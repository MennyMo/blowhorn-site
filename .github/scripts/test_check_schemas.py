#!/usr/bin/env python3
"""Shared line/text/card types: a bad card fails for role, use-case and
solution data; a use case without title fails; a solution's compare list
takes only /compare/ pages.

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

ROOT = Path(__file__).resolve().parents[2]
REFS = ["-r", str(ROOT / "schemas/defs/cast-page.schema.json")]
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
    ] + REFS + ["-d", str(data_path)]
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


class CastPageSchemaTest(unittest.TestCase):
    def test_bad_card_fails_roles_and_use_cases(self):
        cases = (
            ("schemas/roles.schema.json", "data/roles.json", "roles"),
            ("schemas/use_cases.schema.json", "data/use_cases.json", "use_cases"),
            ("schemas/solutions.schema.json", "data/solutions.json", "solutions"),
        )
        for schema, data, key in cases:
            with self.subTest(data=data):
                payload = json.loads((ROOT / data).read_text(encoding="utf-8"))
                broken = copy.deepcopy(payload)
                broken[key][0]["pains"][0]["t"] = "A title with an em dash — here"
                tmp_path = write_tmp(broken)
                try:
                    result = ajv(ROOT / schema, tmp_path)
                    self.assertNotEqual(
                        result.returncode,
                        0,
                        f"{data}: em-dash card title should fail validation",
                    )
                    combined = result.stderr + result.stdout
                    self.assertTrue(
                        combined.strip(),
                        f"{data}: ajv should report why the card failed",
                    )
                finally:
                    tmp_path.unlink(missing_ok=True)

    def test_solution_data_passes(self):
        result = ajv(ROOT / "schemas/solutions.schema.json", ROOT / "data/solutions.json")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_solution_compare_takes_only_compare_pages(self):
        payload = json.loads((ROOT / "data/solutions.json").read_text(encoding="utf-8"))
        for bad in ([], ["/for/devrel"], ["/compare/buffer", "/compare/buffer"]):
            with self.subTest(compare=bad):
                broken = copy.deepcopy(payload)
                broken["solutions"][0]["compare"] = bad
                tmp_path = write_tmp(broken)
                try:
                    result = ajv(ROOT / "schemas/solutions.schema.json", tmp_path)
                    self.assertNotEqual(
                        result.returncode,
                        0,
                        f"compare {bad!r} should fail validation",
                    )
                finally:
                    tmp_path.unlink(missing_ok=True)

    def test_use_case_missing_title_fails(self):
        payload = json.loads((ROOT / "data/use_cases.json").read_text(encoding="utf-8"))
        broken = copy.deepcopy(payload)
        del broken["use_cases"][0]["title"]
        tmp_path = write_tmp(broken)
        try:
            result = ajv(ROOT / "schemas/use_cases.schema.json", tmp_path)
            self.assertNotEqual(
                result.returncode,
                0,
                "a use case without title should fail validation",
            )
            combined = result.stderr + result.stdout
            self.assertTrue(
                combined.strip(),
                "ajv should report that title is required",
            )
        finally:
            tmp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
