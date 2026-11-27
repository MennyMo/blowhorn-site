#!/usr/bin/env python3
"""Does the Blowhorn Chrome extension reach its native host on Windows? Run on the Windows runner.

Installs a published preview installer silently into a throwaway folder, registers the native host
for the runner's user (`chrome extension-install`), starts installed Google Chrome on a throwaway
`--user-data-dir` with the unpacked extension folder the installer ships, and looks for the host
program Chrome starts when the extension's worker connects (`chrome.runtime.connectNative`). Then it
stops Chrome, removes the registry entry and uninstalls.

Chrome 137+ only takes an unpacked extension over `--remote-debugging-pipe` with
`--enable-unsafe-extension-debugging` (`Extensions.loadUnpacked`), so this speaks the DevTools pipe
protocol itself: UTF-8 JSON messages, each ended by a NUL byte, over two inheritable handles named
by `--remote-debugging-io-pipes=<read>,<write>`, the Windows form of Linux's fds 3 and 4.

This site is public and the product is private: each check prints a fixed label and ok or failed, and
at most Chrome's own one-line DevTools error. Nothing the product prints is echoed. It never opens
or signs in to any website: Chrome stays on about:blank in a profile that is deleted afterwards.

Usage: chrome_lab.py <installer.exe>
"""

import json
import msvcrt
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

CHROME = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Google" / "Chrome" / "Application" / "chrome.exe"
HOST_KEY = r"HKCU\Software\Google\Chrome\NativeMessagingHosts\com.blowhorn.chrome_extension"
HOST_PROGRAM = "blowhorn-host.exe"
TIMEOUT = 300
HOST_WAIT_S = 45


def say(label, ok, why=""):
    print(f"lab: {label}: {'ok' if ok else 'failed'}{f' ({why})' if why and not ok else ''}", flush=True)
    return ok


def run(argv, env=None):
    try:
        return subprocess.run(argv, env=env, capture_output=True, text=True, timeout=TIMEOUT, check=False, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired):
        return None


class Pipe:
    """The DevTools pipe to a Chrome started by `start`."""

    def __init__(self, argv):
        to_chrome_r, self.to_chrome_w = os.pipe()
        self.from_chrome_r, from_chrome_w = os.pipe()
        theirs = [msvcrt.get_osfhandle(to_chrome_r), msvcrt.get_osfhandle(from_chrome_w)]
        for handle in theirs:
            os.set_handle_inheritable(handle, True)
        startup = subprocess.STARTUPINFO(lpAttributeList={"handle_list": theirs})
        self.proc = subprocess.Popen(
            argv + [f"--remote-debugging-io-pipes={theirs[0]},{theirs[1]}"],
            startupinfo=startup,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        os.close(to_chrome_r)
        os.close(from_chrome_w)
        self.buffer = b""
        self.next_id = 0

    def call(self, method, params=None, timeout=30):
        self.next_id += 1
        want = self.next_id
        os.write(self.to_chrome_w, json.dumps({"id": want, "method": method, "params": params or {}}).encode() + b"\0")
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            while b"\0" in self.buffer:
                raw, self.buffer = self.buffer.split(b"\0", 1)
                try:
                    message = json.loads(raw)
                except ValueError:
                    continue
                if message.get("id") == want:
                    return message
            chunk = os.read(self.from_chrome_r, 65536)
            if not chunk:
                return None
            self.buffer += chunk
        return None

    def stop(self):
        run(["taskkill", "/F", "/T", "/PID", str(self.proc.pid)])
        for fd in (self.to_chrome_w, self.from_chrome_r):
            try:
                os.close(fd)
            except OSError:
                pass


def host_running():
    done = run(["tasklist", "/FI", f"IMAGENAME eq {HOST_PROGRAM}", "/NH"])
    return bool(done and HOST_PROGRAM.lower() in done.stdout.lower())


def main(installer):
    root = Path(tempfile.mkdtemp(prefix="blowhorn-lab-"))
    app = root / "app"
    profile = root / "chrome-profile"
    app.mkdir()
    profile.mkdir()
    ok = say("chrome installed", CHROME.is_file())
    ok &= say("install", (run([installer, "/S", f"/D={app}"]) or type("r", (), {"returncode": 1})).returncode == 0)
    engine = app / "resources" / "engine" / "bin" / "blowhorn.exe"
    extension = app / "resources" / "engine" / "extension"
    ok &= say("extension folder shipped", (extension / "manifest.json").is_file())
    if not (ok and engine.is_file()):
        return 1
    registered = run([str(engine), "chrome", "extension-install", "--json"])
    ok &= say("host registration", bool(registered and registered.returncode == 0))
    pipe = None
    try:
        pipe = Pipe(
            [
                str(CHROME),
                f"--user-data-dir={profile}",
                "--no-first-run",
                "--no-default-browser-check",
                "--mute-audio",
                "--enable-unsafe-extension-debugging",
                "--remote-debugging-pipe",
                "about:blank",
            ]
        )
        loaded = pipe.call("Extensions.loadUnpacked", {"path": str(extension)})
        error = (loaded or {}).get("error", {}).get("message", "") if loaded else "no answer"
        ok &= say("extension loaded", bool(loaded and "result" in loaded), re.sub(r"[^A-Za-z0-9 .,:'()_-]", "", error)[:160])
        deadline = time.monotonic() + HOST_WAIT_S
        seen = False
        while time.monotonic() < deadline and not seen:
            seen = host_running()
            if not seen:
                time.sleep(2)
        ok &= say("chrome started the native host", seen)
    except OSError as error:
        ok &= say("chrome driven over the pipe", False, type(error).__name__)
    finally:
        if pipe:
            pipe.stop()
        run(["reg", "delete", HOST_KEY, "/f"])
        uninstaller = next(iter(sorted(app.glob("Uninstall*.exe"))), None)
        if uninstaller:
            run([str(uninstaller), "/S", f"_?={app}"])
    print(f"lab: {'all ok' if ok else 'something failed'}")
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: chrome_lab.py <installer.exe>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
