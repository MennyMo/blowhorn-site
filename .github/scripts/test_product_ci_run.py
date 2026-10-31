#!/usr/bin/env python3
"""Tests for product-ci/run.py: a private suite's output never reaches the public log.

Run with `make test-scripts` (CI runs it too).
"""

import importlib.util
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SPEC = importlib.util.spec_from_file_location("product_ci_run", HERE / "product-ci" / "run.py")
run = importlib.util.module_from_spec(SPEC)
sys.modules["product_ci_run"] = run
SPEC.loader.exec_module(run)

SECRET = "tests/test_private_module.py::test_secret_branch assert token == 'hunter2'"


def _py(code):
    return (sys.executable, "-c", code)


class RunStepsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.product = Path(self.tmp.name) / "product"
        self.product.mkdir()
        self.log = Path(self.tmp.name) / "private" / "suite.log"

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, steps):
        out = io.StringIO()
        status = run.run_steps(steps, self.product, self.log, out=out)
        return status, out.getvalue()

    def test_a_passing_suite_prints_counts_and_none_of_its_output(self):
        code = f"import sys; print({SECRET!r}); print({SECRET!r}, file=sys.stderr); print('=== 12 passed, 3 skipped, 1 xfailed in 4.20s ===')"
        status, out = self._run([run.Step("test suite", _py(code), counts="pytest")])
        self.assertEqual(status, 0)
        self.assertNotIn("hunter2", out)
        self.assertNotIn("test_private_module", out)
        self.assertIn("test suite: ok", out)
        self.assertIn("[12 passed, 3 skipped, 1 xfailed]", out)
        self.assertIn("hunter2", self.log.read_text())

    def test_a_failing_step_stops_the_run_and_withholds_its_output(self):
        fail = f"import sys; print({SECRET!r}); print('1 failed, 4 passed in 1s'); sys.exit(3)"
        status, out = self._run([
            run.Step("lint", _py(fail), counts="pytest"),
            run.Step("never runs", _py("open('ran', 'w').write('x')")),
        ])
        self.assertEqual(status, 3)
        self.assertNotIn("hunter2", out)
        self.assertIn("lint: failed (exit 3)", out)
        self.assertIn("[1 failed, 4 passed]", out)
        self.assertIn("withheld", out)
        self.assertFalse((self.product / "ran").exists())
        self.assertNotIn("never runs", out)

    def test_a_summary_line_cannot_smuggle_text_through(self):
        code = f"print('7 passed ' + {SECRET!r} + ' 2 failed in 1.00s')"
        status, out = self._run([run.Step("test suite", _py(code), counts="pytest")])
        self.assertEqual(status, 0)
        self.assertNotIn("hunter2", out)
        self.assertIn("[7 passed, 2 failed]", out)

    def test_pytest_counts_come_from_its_summary_line_only(self):
        code = ("print('== 5 passed in 312.40s (0:05:12) ==');"
                "print('found 3 errors in the fixture');"
                "print('Fatal Python error: Aborted')")
        _status, out = self._run([run.Step("test suite", _py(code), counts="pytest")])
        self.assertIn("[5 passed]", out)
        self.assertNotIn("3 errors", out)

    def test_no_pytest_summary_prints_no_counts(self):
        code = "import sys; print('found 3 errors'); print('2 failed checks'); sys.exit(134)"
        _status, out = self._run([run.Step("test suite", _py(code), counts="pytest")])
        self.assertIn("test suite: failed (exit 134)", out)
        self.assertNotIn("[", out)

    def test_vitest_counts_come_from_its_summary_lines_only(self):
        code = ("print('\\x1b[32m✓\\x1b[0m tests/private-file.test.ts (3)');"
                "print(' Test Files  \\x1b[1m98 passed\\x1b[0m (98)');"
                "print('      Tests  1367 passed | 2 skipped (1369)')")
        _status, out = self._run([run.Step("test", _py(code), counts="vitest")])
        self.assertNotIn("private-file", out)
        self.assertIn("[files: 98 passed; tests: 1367 passed, 2 skipped]", out)

    def test_a_hung_step_times_out_and_fails(self):
        status, out = self._run([run.Step("hang", _py("import time; time.sleep(30)"), timeout_s=1)])
        self.assertEqual(status, 124)
        self.assertIn("hang: failed (timed out after 1 s)", out)

    def test_a_missing_command_fails_without_a_traceback(self):
        status, out = self._run([run.Step("missing", ("definitely-not-a-command-xyz",))])
        self.assertEqual(status, 127)
        self.assertIn("missing: failed (could not start", out)
        self.assertNotIn("Traceback", out)

    def test_a_step_cannot_write_to_the_runner_file_commands(self):
        files = {name: Path(self.tmp.name) / name.lower() for name in sorted(run.FILE_COMMANDS)}
        for path in files.values():
            path.write_text("")
        write_all = ("import os\n"
                     f"for name in {sorted(files)!r}:\n"
                     "    if os.environ.get(name):\n"
                     f"        open(os.environ[name], 'a').write({SECRET!r})\n"
                     "print('KEEP=' + os.environ.get('KEEP', ''))")
        with mock.patch.dict("os.environ", {**{k: str(v) for k, v in files.items()}, "KEEP": "kept"}):
            status, _out = self._run([run.Step("summary", _py(write_all))])
        self.assertEqual(status, 0)
        for name, path in files.items():
            self.assertEqual(path.read_text(), "", name)
        self.assertIn("KEEP=kept", self.log.read_text())

    def test_a_step_does_not_inherit_the_calling_make(self):
        show = "import os; print('MAKE_STATE=' + repr([os.environ.get(n) for n in ('MAKEFLAGS', 'MAKELEVEL', 'MFLAGS', 'MAKEOVERRIDES')]))"
        calling_make = {"MAKEFLAGS": " -- SUITE=python PRODUCT_DIR=product", "MAKELEVEL": "1", "MFLAGS": "-s",
                        "MAKEOVERRIDES": "${-*-command-variables-*-}"}
        with mock.patch.dict("os.environ", calling_make):
            status, _out = self._run([run.Step("make state", _py(show))])
        self.assertEqual(status, 0)
        self.assertIn("MAKE_STATE=[None, None, None, None]", self.log.read_text())

    def test_steps_run_in_their_own_directory_of_the_product(self):
        (self.product / "desktop").mkdir()
        status, _out = self._run([run.Step("here", _py("open('marker', 'w').write('x')"), cwd="desktop")])
        self.assertEqual(status, 0)
        self.assertTrue((self.product / "desktop" / "marker").exists())


class MakeTargetTest(unittest.TestCase):
    def test_make_product_ci_runs_the_suite_and_prints_only_its_summary(self):
        # Resolve `make` from the host PATH instead of assuming where it lives, and
        # fail with a clear message when it is not installed at all.
        host_path = os.environ.get("PATH", "")
        make_bin = shutil.which("make")
        if make_bin is None:
            self.fail(f"`make` was not found on PATH ({host_path!r}); "
                      "install make to run this test (`make test-scripts` needs it).")

        with tempfile.TemporaryDirectory() as tmp:
            product = Path(tmp) / "product"
            (product / "desktop").mkdir(parents=True)
            fake_bin = Path(tmp) / "bin"
            fake_bin.mkdir()
            pnpm = fake_bin / "pnpm"
            pnpm.write_text(f"#!/bin/sh\necho {SECRET!r}\n[ \"$1\" = test ] && echo '      Tests  5 passed (5)'\nexit 0\n")
            pnpm.chmod(0o755)
            log = Path(tmp) / "desktop.log"
            # fake pnpm first, then the host PATH (empty entries dropped: they mean "current dir").
            path = os.pathsep.join(p for p in (str(fake_bin), *host_path.split(os.pathsep)) if p)
            env = {"PATH": path, "HOME": tmp}
            done = subprocess.run([make_bin, "-s", "product-ci", "SUITE=desktop", f"PRODUCT_DIR={product}",
                                   f"PRODUCT_CI_LOG={log}"], cwd=ROOT, env=env, capture_output=True, text=True,
                                  timeout=60)
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertNotIn("hunter2", done.stdout + done.stderr)
            for label in ("install", "typecheck", "lint", "test", "build"):
                self.assertIn(f"{label}: ok", done.stdout)
            self.assertIn("[tests: 5 passed]", done.stdout)
            self.assertIn("hunter2", log.read_text())


if __name__ == "__main__":
    unittest.main()
