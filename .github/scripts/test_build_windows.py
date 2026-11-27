#!/usr/bin/env python3
"""Pins the rules build-windows.yml must keep: dispatch only, private output withheld,
signing secrets only on the build step, one short-lived artifact."""

import unittest
from pathlib import Path

import yaml

WORKFLOW = Path(__file__).resolve().parents[1] / "workflows" / "build-windows.yml"


class BuildWindowsWorkflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = yaml.safe_load(WORKFLOW.read_text())
        cls.job = cls.doc["jobs"]["build-windows"]

    def test_only_a_manual_dispatch_starts_it(self):
        triggers = self.doc.get(True) or self.doc.get("on")
        self.assertEqual(set(triggers), {"workflow_dispatch"})

    def test_signing_secrets_reach_only_the_build_step(self):
        self.assertNotIn("env", self.job)
        carrying = [s["name"] for s in self.job["steps"] if "WINDOWS_PREVIEW" in str(s.get("env", {}))]
        self.assertEqual(len(carrying), 1)
        self.assertIn("Build and sign", carrying[0])
        self.assertEqual(self.job["environment"], "windows-preview-signing")

    def test_the_product_token_goes_only_to_checkout_product(self):
        holders = [s for s in self.job["steps"] if "DMG_SOURCE_TOKEN" in str(s)]
        self.assertEqual([s["uses"] for s in holders], ["./.github/actions/checkout-product"])

    def test_one_artifact_kept_one_day(self):
        uploads = [s for s in self.job["steps"] if str(s.get("uses", "")).startswith("actions/upload-artifact")]
        self.assertEqual(len(uploads), 1)
        self.assertEqual(uploads[0]["with"]["retention-days"], 1)
        self.assertEqual(uploads[0]["with"]["path"], "dist/")

    def test_the_smoke_job_holds_no_secret_and_no_product_checkout(self):
        smoke = self.doc["jobs"]["smoke-windows"]
        self.assertEqual(smoke["needs"], "build-windows")
        self.assertNotIn("environment", smoke)
        self.assertNotIn("env", smoke)
        text = str(smoke)
        for forbidden in ("secrets.", "checkout-product", "DMG_SOURCE_TOKEN", "WINDOWS_PREVIEW"):
            self.assertNotIn(forbidden, text)

    def test_the_smoke_script_prints_labels_never_program_output(self):
        script = (WORKFLOW.parents[1] / "scripts" / "build-windows" / "smoke.py").read_text()
        self.assertIn("capture_output=True", script)
        self.assertNotIn("done.stdout)", script.replace("json.loads(done.stdout)", ""))
        # The program's stderr is read only through the strict handover filter, and never printed whole.
        self.assertEqual(script.count("done.stderr"), script.count("handover_line(done.stderr)"))
        self.assertNotIn("print(done", script)

    def test_build_output_goes_to_a_log_never_printed(self):
        text = WORKFLOW.read_text()
        self.assertIn("timed_run.py", text)
        self.assertIn('--log "$RUNNER_TEMP/build-windows/build.log"', text)


if __name__ == "__main__":
    unittest.main()
