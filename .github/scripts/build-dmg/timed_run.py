"""Run one build-dmg phase with a hard time limit and a private log.

The child's output goes only to the log, which is never printed or cached; a
failed job uploads it only as age ciphertext with staged secrets removed
(encrypt_logs.py). Stdout gets fixed labels: the phase start and end with UTC timestamps
and the elapsed time, and the few progress lines that `progress_line` lets
through (release phase headers, notarization submission id and status, and on
a failure which build sub-step failed, its exit code and the failing test file
names; never the tool output, a path or a value).
On timeout the whole process group is killed and the phase fails with a clear
message instead of running into the job's timeout.

Children start with the default SIGPIPE handler (subprocess restores it), so
a `producer | head` pipeline in a product script exits as it would in a
terminal rather than spinning under the runner's ignored SIGPIPE.

Usage: timed_run.py --label NAME --timeout-minutes N --log FILE -- CMD...
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

# Lines safe to echo from the private log. Each pattern matches the whole
# line and captures only fixed vocabulary, a UUID, or a phase name, so no
# path, identifier, key or tool output can pass.
_PROGRESS = (
    (re.compile(r"==> ([a-z][a-z0-9-]{0,40})"), "phase {0}"),
    (re.compile(r"Submission ID received"), "notarization: submitted"),
    (re.compile(r"\s*id: ([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"), "notarization: submission id {0}"),
    (re.compile(r"\s*(?:Current )?status: (Accepted|Invalid|Rejected|In Progress)\.*"), "notarization: status {0}"),
    (re.compile(r"Processing complete"), "notarization: processing complete"),
)


ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

#: The build phase's sub-steps: a fixed fragment of the step's own label or
#: command in the private log, and the public name it gets. First match wins.
#: Only the public name is echoed, never the matched text, so a quoted command
#: line with paths or flags cannot leak through.
SUBSTEPS = (
    ("checkout's Rust binaries", "checkout rust build"),
    ("verify linkedin-accept", "fixture check linkedin-accept"),
    ("verify reconcile", "fixture check reconcile"),
    ("(fixture)", "fixture check"),
    ("bundled engine", "bundled engine build"),
    ("electron-builder", "electron-builder"),
    ("adhoc-sign-mac-app", "ad-hoc signing"),
    ("signing the DMG", "codesign"),
    ("codesign", "codesign"),
    ("notarytool", "notarytool"),
    ("stapler", "stapler"),
    ("create-dmg", "create-dmg"),
    ("verify-mac-dmg", "DMG verify"),
    ("install --frozen-lockfile", "pnpm install"),
)
#: A pnpm script, as a label ("pnpm test") or a quoted argv ('/x/pnpm' 'test').
_PNPM_SCRIPT = re.compile(r"(?:^|[\s/'\"])pnpm['\"]?\s+['\"]?(typecheck|lint|test|build)(?=['\"]?(?:\s|$))")
PNPM_SCRIPTS = {"typecheck": "typecheck", "lint": "lint", "test": "pnpm test", "build": "pnpm build"}
#: A check beside packaging ends with "--- end of <label> (failed|stopped) ---".
_STEP_END = re.compile(r"\s*--- end of (.{1,300}) \((failed|stopped)\) ---")
#: release-mac's headline on exit: "release-mac: <step> failed (exit N)".
_HEADLINE = re.compile(r"release-mac: (.{1,2000}?) failed(?: \((?:exit (\d{1,3})|[^)]*)\))?(?:[:.].*)?")
#: Vitest's failing-test line. The path is echoed only when it is one of the
#: product's own test files (see test_files), so the line cannot carry
#: anything else out of the private log.
_VITEST_FAIL = re.compile(r"\s*FAIL\s+(tests/\S{1,160})(?:\s.*)?")
TEST_FILE_SUFFIXES = (".ts", ".tsx", ".js", ".jsx", ".mts", ".cts", ".mjs", ".cjs")
MAX_TEST_PATH = 160
FAILING_FILE = "failing test file: "
MAX_FAILING_FILES = 20


def test_files(desktop: Path) -> frozenset[str]:
    """The product's vitest files as vitest prints them ("tests/x.test.ts"), the only names a FAIL line may echo."""
    root = desktop / "tests"
    if not root.is_dir():
        return frozenset()
    found = set()
    for path in root.rglob("*"):
        rel = "tests/" + path.relative_to(root).as_posix()
        if path.is_file() and rel.endswith(TEST_FILE_SUFFIXES) and len(rel) <= MAX_TEST_PATH:
            found.add(rel)
    return frozenset(found)


def substep(text: str) -> str:
    """The public name of the sub-step *text* names; 'unrecognized step' when none matches."""
    script = _PNPM_SCRIPT.search(text)
    if script and "electron-builder" not in text:
        return PNPM_SCRIPTS[script.group(1)]
    for fragment, name in SUBSTEPS:
        if fragment in text:
            return name
    return "unrecognized step"


def failure_line(line: str, known_tests: frozenset[str] = frozenset()) -> str | None:
    """The public form of a failure marker in *line*, or None.

    A failing test file is named only when it is in *known_tests*.
    """
    match = _STEP_END.fullmatch(line)
    if match:
        return f"step {match.group(2)}: {substep(match.group(1))}"
    match = _HEADLINE.fullmatch(line)
    if match:
        code = f"exit {match.group(2)}" if match.group(2) else "no exit code"
        return f"failed step: {substep(match.group(1))} ({code})"
    match = _VITEST_FAIL.fullmatch(line)
    if match and match.group(1) in known_tests:
        return FAILING_FILE + match.group(1)
    return None


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def progress_line(line: str, known_tests: frozenset[str] = frozenset()) -> str | None:
    """The public form of *line*, or None when it must stay in the log."""
    line = ANSI.sub("", line).rstrip()
    for pattern, template in _PROGRESS:
        match = pattern.fullmatch(line)
        if match:
            return template.format(*match.groups())
    return failure_line(line, known_tests)


def say(label: str, message: str) -> None:
    print(f"build-dmg: [{stamp()}] {label}: {message}", flush=True)


def resolve_program(cmd: list[str]) -> list[str]:
    """On Windows, CreateProcess finds only .exe, so a .cmd shim such as pnpm is looked up on PATH.

    Elsewhere the command is returned unchanged.
    """
    if os.name != "nt" or not cmd:
        return cmd
    found = shutil.which(cmd[0])
    return [found, *cmd[1:]] if found else cmd


def kill_tree(proc: subprocess.Popen) -> None:
    """End *proc* and its children: the process group where there is one, taskkill on Windows."""
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], check=False, capture_output=True)
        return
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        proc.kill()


def run_logged(
    cmd: list[str],
    *,
    label: str,
    log: Path,
    timeout_s: float,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    popen: Callable[..., subprocess.Popen] | None = None,
    known_tests: frozenset[str] = frozenset(),
) -> tuple[int, int, bool]:
    """Run *cmd* with output to *log*; return (exit status, seconds, timed out)."""
    log.parent.mkdir(parents=True, exist_ok=True)
    say(label, f"start (limit {timeout_s / 60:g} min)")
    started = time.monotonic()
    timed_out = threading.Event()
    last = None
    failing_files: set[str] = set()
    with log.open("wb") as sink:
        proc = (popen or subprocess.Popen)(resolve_program(cmd), cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, start_new_session=os.name != "nt")

        def expire() -> None:
            timed_out.set()
            kill_tree(proc)

        timer = threading.Timer(timeout_s, expire)
        timer.daemon = True
        timer.start()
        try:
            for raw in proc.stdout:
                sink.write(raw)
                sink.flush()
                # notarytool redraws its status line with carriage returns.
                for part in raw.decode("utf-8", "replace").replace("\r", "\n").split("\n"):
                    public = progress_line(part, known_tests)
                    if public and public.startswith(FAILING_FILE):
                        if public in failing_files or len(failing_files) >= MAX_FAILING_FILES:
                            continue
                        failing_files.add(public)
                    if public and public != last:
                        last = public
                        say(label, public)
            status = proc.wait()
        finally:
            timer.cancel()
            proc.stdout.close()
    elapsed = int(time.monotonic() - started)
    if timed_out.is_set():
        say(label, f"timed out after {elapsed}s (limit {timeout_s / 60:g} min); the process group was killed. The private log has the output.")
        return 124, elapsed, True
    say(label, f"end (exit {status}, {elapsed}s)")
    return status, elapsed, False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--label", required=True)
    parser.add_argument("--timeout-minutes", required=True, type=float)
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("cmd", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    cmd = args.cmd[1:] if args.cmd[:1] == ["--"] else args.cmd
    if not cmd:
        parser.error("a command is required after --")
    status, _, _ = run_logged(cmd, label=args.label, log=args.log, timeout_s=args.timeout_minutes * 60)
    return status


if __name__ == "__main__":
    sys.exit(main())
