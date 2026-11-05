#!/usr/bin/env python3
"""Action vocabulary and examples: schema, coverage, no invented CLI flags.

Run with `make test-scripts` (CI runs it too).
"""

import copy
import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

import check_action_examples as check

ROOT = Path(__file__).resolve().parents[2]
AJV_VERSION_RE = re.compile(r"^AJV_CLI_VERSION\s*\??=\s*(\S+)\s*$")


def ajv_cli_version():
    env = os.environ.get("AJV_CLI_VERSION")
    if env:
        return env
    for line in (ROOT / "Makefile").read_text(encoding="utf-8").splitlines():
        match = AJV_VERSION_RE.match(line)
        if match:
            return match.group(1)
    raise RuntimeError("AJV_CLI_VERSION not set in the environment or Makefile")


def ajv(schema, data_path):
    cmd = [
        "npx",
        "--yes",
        f"ajv-cli@{ajv_cli_version()}",
        "validate",
        "--strict=false",
        "-s",
        str(schema),
        "-d",
        str(data_path),
    ]
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )


def write_tmp(payload):
    tmp = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        encoding="utf-8",
        delete=False,
    )
    json.dump(payload, tmp)
    tmp.close()
    return Path(tmp.name)


class ActionsSchemaTest(unittest.TestCase):
    def test_checked_in_actions_pass(self):
        result = ajv(ROOT / "schemas/actions.schema.json", ROOT / "data/actions.json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_em_dash_description_fails(self):
        payload = json.loads((ROOT / "data/actions.json").read_text(encoding="utf-8"))
        broken = copy.deepcopy(payload)
        broken["actions"][0]["description"] = "Publish — as you"
        tmp = write_tmp(broken)
        try:
            result = ajv(ROOT / "schemas/actions.schema.json", tmp)
            self.assertNotEqual(result.returncode, 0)
        finally:
            tmp.unlink(missing_ok=True)


class ActionExamplesSchemaTest(unittest.TestCase):
    def test_checked_in_examples_pass(self):
        result = ajv(
            ROOT / "schemas/action_examples.schema.json",
            ROOT / "data/action_examples.json",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_coverage_matches_yaml(self):
        self.assertEqual(check.main(), 0)

    def test_yaml_ids_are_in_vocabulary(self):
        vocab = {
            a["id"]
            for a in json.loads((ROOT / "data/actions.json").read_text(encoding="utf-8"))[
                "actions"
            ]
        }
        for platform, action in check.supported_pairs():
            self.assertIn(action, vocab, f"{platform} {action}")

    def test_comment_page_does_not_leak_post_example_flags(self):
        comment = (
            ROOT / "content/en/docs/reference/cli/comment.md"
        ).read_text(encoding="utf-8")
        flags = check.allowed_flags(comment, "comment")
        self.assertIn("--platform", flags)
        self.assertIn("--target", flags)
        self.assertIn("--profile", flags)
        self.assertNotIn("--check-queue", flags)
        self.assertNotIn("--amplify", flags)

    def test_title_page_section_has_no_h2(self):
        page = (
            '---\ntitle: "blowhorn comment"\n---\n\n'
            "| Flag | Type |\n| --- | --- |\n| `--platform` | string |\n\n"
            "## blowhorn comment queue\n\n"
            "| Flag | Type |\n| --- | --- |\n| `--check-queue` | boolean |\n"
        )
        sections = check.cli_sections(page)
        self.assertIn("comment", sections)
        self.assertIn("--platform", check.allowed_flags(page, "comment"))
        self.assertNotIn("--check-queue", check.allowed_flags(page, "comment"))
        self.assertIn("--check-queue", check.allowed_flags(page, "comment queue"))

    def test_subcommand_must_match_cliref(self):
        problems = check.check_cli_available(
            "x",
            "reply",
            {
                "command": "blowhorn post --platform x --profile alex",
                "cliRef": "/docs/reference/cli/comment/",
            },
        )
        self.assertTrue(any("does not match cliRef" in p for p in problems), problems)

    def test_flag_must_belong_to_heading_section(self):
        problems = check.check_cli_available(
            "linkedin",
            "comment",
            {
                "command": "blowhorn comment --check-queue --platform linkedin",
                "cliRef": "/docs/reference/cli/comment/",
            },
        )
        self.assertTrue(any("not a comment flag" in p for p in problems), problems)

    def test_analytics_history_since_is_in_its_section(self):
        problems = check.check_cli_available(
            "linkedin",
            "analytics",
            {
                "command": "blowhorn analytics history --platform linkedin --json --since 12m",
                "cliRef": "/docs/reference/cli/analytics/",
            },
        )
        self.assertEqual(problems, [])

    def test_missing_surface_fails_schema(self):
        payload = json.loads(
            (ROOT / "data/action_examples.json").read_text(encoding="utf-8")
        )
        broken = copy.deepcopy(payload)
        del broken["examples"][0]["surfaces"]["cli"]
        tmp = write_tmp(broken)
        try:
            result = ajv(ROOT / "schemas/action_examples.schema.json", tmp)
            self.assertNotEqual(result.returncode, 0)
        finally:
            tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
