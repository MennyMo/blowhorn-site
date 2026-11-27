#!/usr/bin/env python3
"""Smoke for a built Windows preview installer, run on the Windows runner.

Installs the per-user NSIS installer silently into a throwaway folder, runs the packaged
Rust-only engine with every user folder pointed at throwaway ones, and removes it again.
This site is public and the product is private, so nothing the product prints is ever echoed:
each check reports only a fixed label and ok or failed, and its output is discarded.

What it proves: the installer installs with no prompt, the engine answers `--version`,
`config show` and `platforms capabilities --json` (parsable JSON), and the uninstaller runs.
Not yet here (tracked in the product's Windows gaps list): the native host registration in
HKCU and Chrome connecting to the extension over a throwaway profile.

Usage: smoke.py <installer.exe>
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

TIMEOUT = 300


def run(label, argv, env=None, want_json=False):
    """Run one check; print its label and ok/failed; never print what the program said."""
    try:
        done = subprocess.run(
            argv, env=env, capture_output=True, text=True, timeout=TIMEOUT, check=False, stdin=subprocess.DEVNULL
        )
        ok = done.returncode == 0
        why = f"exit {done.returncode & 0xFFFFFFFF:#x}"
        if ok and want_json:
            json.loads(done.stdout)
    except (OSError, subprocess.TimeoutExpired, ValueError) as error:
        ok = False
        why = type(error).__name__
    # Only the exit status or the exception's class: never what the program printed.
    print(f"smoke: {label}: {'ok' if ok else f'failed ({why})'}")
    return ok


def main(installer):
    root = Path(tempfile.mkdtemp(prefix="blowhorn-smoke-"))
    app = root / "app"
    home = root / "home"
    for folder in (app, home / "AppData" / "Roaming", home / "AppData" / "Local"):
        folder.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env.update(
        USERPROFILE=str(home),
        HOME=str(home),
        APPDATA=str(home / "AppData" / "Roaming"),
        LOCALAPPDATA=str(home / "AppData" / "Local"),
        BLOWHORN_CLOUD_CONFIG_DIR=str(home / "cloud"),
    )
    results = []
    # NSIS: /S is silent and /D= (last, unquoted) is the install folder.
    results.append(run("install", [installer, "/S", f"/D={app}"], env))
    engine = app / "resources" / "engine" / "bin" / "blowhorn.exe"
    present = engine.is_file() and (app / "resources" / "engine" / "RUST_ENGINE").is_file()
    print(f"smoke: engine present: {'ok' if present else 'failed'}")
    results.append(present)
    if present:
        results.append(run("engine --version", [str(engine), "--version"], env))
        results.append(run("config show", [str(engine), "config", "show"], env))
        results.append(run("platforms capabilities", [str(engine), "platforms", "capabilities", "--json"], env, True))
    uninstaller = next(iter(sorted(app.glob("Uninstall*.exe"))), None)
    if uninstaller is None:
        print("smoke: uninstall: failed")
        results.append(False)
    else:
        results.append(run("uninstall", [str(uninstaller), "/S", f"_?={app}"], env))
    failed = results.count(False)
    print(f"smoke: {len(results) - failed} ok, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: smoke.py <installer.exe>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
