#!/usr/bin/env python3
"""Themes, integrations catalog and hero demo: schema, counts, and the
per-page override hook.

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


def yaml_action_ids(platform_id):
    yaml_path = ROOT / "data" / "platforms" / f"{platform_id}.yaml"
    return [
        line.split("id:", 1)[1].strip()
        for line in yaml_path.read_text(encoding="utf-8").splitlines()
        if line.startswith("  - id:")
    ]


def counts_from(payload):
    platforms = 0
    activities = 0
    for item in payload["platforms"]:
        if item["status"] == "supported":
            platforms += 1
            activities += len(yaml_action_ids(item["id"]))
    return platforms, activities


class ThemeSchemaTest(unittest.TestCase):
    def test_checked_in_themes_pass(self):
        result = ajv(ROOT / "schemas/themes.schema.json", ROOT / "data/themes.json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unknown_theme_id_fails(self):
        payload = json.loads((ROOT / "data/themes.json").read_text(encoding="utf-8"))
        broken = copy.deepcopy(payload)
        broken["themes"][0]["id"] = "full-volume"
        tmp = write_tmp(broken)
        try:
            result = ajv(ROOT / "schemas/themes.schema.json", tmp)
            self.assertNotEqual(result.returncode, 0)
        finally:
            tmp.unlink(missing_ok=True)

    def test_em_dash_theme_name_fails(self):
        payload = json.loads((ROOT / "data/themes.json").read_text(encoding="utf-8"))
        broken = copy.deepcopy(payload)
        broken["themes"][0]["name"] = "Signal \u2014 dark"
        tmp = write_tmp(broken)
        try:
            result = ajv(ROOT / "schemas/themes.schema.json", tmp)
            self.assertNotEqual(result.returncode, 0)
        finally:
            tmp.unlink(missing_ok=True)


class IntegrationsSchemaTest(unittest.TestCase):
    def test_checked_in_integrations_pass(self):
        result = ajv(
            ROOT / "schemas/integrations.schema.json",
            ROOT / "data/integrations.json",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_counts_are_derived_from_supported_rows(self):
        payload = json.loads((ROOT / "data/integrations.json").read_text(encoding="utf-8"))
        platforms, activities = counts_from(payload)
        self.assertGreaterEqual(platforms, 1)
        self.assertGreaterEqual(activities, platforms)
        github = next(p for p in payload["platforms"] if p["id"] == "github")
        self.assertFalse(github["posts"])
        self.assertNotIn("post", yaml_action_ids("github"))
        ids = {t["id"] for t in payload["treatments"]}
        self.assertIn("action", ids)

    def test_github_cannot_claim_to_post(self):
        payload = json.loads((ROOT / "data/integrations.json").read_text(encoding="utf-8"))
        broken = copy.deepcopy(payload)
        for item in broken["platforms"]:
            if item["id"] == "github":
                item["posts"] = True
        tmp = write_tmp(broken)
        try:
            result = ajv(ROOT / "schemas/integrations.schema.json", tmp)
            self.assertNotEqual(result.returncode, 0)
        finally:
            tmp.unlink(missing_ok=True)

    def test_role_and_category_ids_exist(self):
        payload = json.loads((ROOT / "data/integrations.json").read_text(encoding="utf-8"))
        ids = {p["id"] for p in payload["platforms"]}
        for group in payload["categories"]:
            for pid in group["platforms"]:
                self.assertIn(pid, ids, f"{group['id']} names unknown platform {pid}")
        roles = json.loads((ROOT / "data/roles.json").read_text(encoding="utf-8"))["roles"]
        for role in roles:
            for pid in role["platforms"]:
                self.assertIn(pid, ids, f"role {role['slug']} names unknown platform {pid}")

    def test_em_dash_headline_fails(self):
        payload = json.loads((ROOT / "data/integrations.json").read_text(encoding="utf-8"))
        broken = copy.deepcopy(payload)
        broken["headline"] = "Say it once \u2014 everywhere"
        tmp = write_tmp(broken)
        try:
            result = ajv(ROOT / "schemas/integrations.schema.json", tmp)
            self.assertNotEqual(result.returncode, 0)
        finally:
            tmp.unlink(missing_ok=True)


class ThemeContentSplitTest(unittest.TestCase):
    def test_only_approved_theme_content_file(self):
        import check_theme

        self.assertEqual(check_theme.extra_theme_content(), [])
        self.assertIn("content/en/home-reveille.md", check_theme.APPROVED_THEME_CONTENT)

    def test_home_signal_content_would_fail(self):
        import check_theme

        self.assertIn("signal", check_theme.theme_ids())
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "content" / "en" / "home-signal.md"
            path.parent.mkdir(parents=True)
            path.write_text("---\ntitle: Signal home\n---\n", encoding="utf-8")
            extras = check_theme.extra_theme_content(root)
        self.assertIn("content/en/home-signal.md", extras)



class HomeSignalPlatformsBehaviorTest(unittest.TestCase):
    """Run assets/js/home-signal.js in a fake DOM and check what it shows."""

    def run_js(self, **extra):
        import check_theme

        return check_theme.run_platforms_js(check_theme.platforms_scenario(**extra))

    def visible(self, got):
        return sorted(k for k, v in got["panels"].items() if v)

    def test_no_hash_shows_only_the_default_treatment(self):
        import check_theme

        want = check_theme.platforms_scenario()["on"]
        got = self.run_js()
        self.assertEqual(got["tab"], want)
        self.assertEqual(got["ariaSelected"], [want])
        self.assertEqual(self.visible(got), [want])
        self.assertTrue(got["enhanced"])
        self.assertEqual(check_theme.platforms_default_problems(), [])

    def test_no_marked_tab_falls_back_to_the_first(self):
        tabs = self.run_js()["panels"].keys()
        got = self.run_js(on="")
        self.assertEqual(self.visible(got), [list(tabs)[0]])

    def test_panel_hash_opens_that_panel(self):
        got = self.run_js(hash="#plat-panel-action")
        self.assertEqual(got["tab"], "action")
        self.assertEqual(self.visible(got), ["action"])

    def test_action_hash_opens_the_action_panel(self):
        got = self.run_js(hash="#action-post")
        self.assertEqual(self.visible(got), ["action"])

    def test_unknown_panel_hash_falls_back_to_default(self):
        import check_theme

        want = check_theme.platforms_scenario()["on"]
        got = self.run_js(hash="#plat-panel-nope")
        self.assertEqual(self.visible(got), [want])

    def test_click_and_arrow_keys_switch_panels(self):
        import check_theme

        tabs = check_theme.platforms_scenario()["tabs"]
        got = self.run_js(click=tabs[-1])
        self.assertEqual(self.visible(got), [tabs[-1]])
        got = self.run_js(on=tabs[0], key="ArrowRight")
        self.assertEqual(self.visible(got), [tabs[1]])

    def test_script_that_skips_the_default_fails_the_check(self):
        import check_theme

        src = (ROOT / "assets/js/home-signal.js").read_text(encoding="utf-8")
        broken = src.replace("selectTab(section, initial);", "")
        self.assertNotEqual(src, broken)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "home-signal.js"
            path.write_text(broken, encoding="utf-8")
            problems = check_theme.platforms_default_problems(path)
        self.assertTrue(problems, "a script that never selects a panel must fail")


class HeroDemoSchemaTest(unittest.TestCase):
    def test_checked_in_demo_pass(self):
        result = ajv(ROOT / "schemas/hero_demo.schema.json", ROOT / "data/hero_demo.json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_status_steps_are_the_three_states(self):
        data = json.loads((ROOT / "data/hero_demo.json").read_text(encoding="utf-8"))
        self.assertEqual(data["statusSteps"], ["Queued", "Posting as you", "Went out"])
        self.assertIn("Demo", data["label"])
        self.assertIn("Example", data["exampleLabel"])

    def test_video_mode_is_gone(self):
        # The hero film lives in data/hero.json media.video; hero_demo.json
        # is the interactive demo only.
        payload = json.loads((ROOT / "data/hero_demo.json").read_text(encoding="utf-8"))
        broken = copy.deepcopy(payload)
        broken["video"] = {"src": "", "poster": "", "alt": "A video"}
        tmp = write_tmp(broken)
        try:
            result = ajv(ROOT / "schemas/hero_demo.schema.json", tmp)
            self.assertNotEqual(result.returncode, 0)
        finally:
            tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
