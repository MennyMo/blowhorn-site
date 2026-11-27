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
    if not yaml_path.is_file():
        return []
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
class PlatformLabelGuardTest(unittest.TestCase):
    """The theme check must fail a platform-availability "Coming soon"
    label on a platform surface, and must not trip on the out-of-scope
    "coming soon" copy in the action-example tabs."""

    def setUp(self):
        import shutil

        import check_theme as check

        self.check = check
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / "repo"
        self.build = self.tmp / "public"
        shutil.copytree(ROOT / "data", self.root / "data")
        self.pages = [
            "integrations/index.html",
            "integrations/actions/index.html",
            "docs/index.html",
            "docs/reference/platforms/index.html",
            "docs/reference/platforms/actions/index.html",
        ]
        data = json.loads((self.root / "data/integrations.json").read_text(encoding="utf-8"))
        for item in data["platforms"]:
            self.pages.append(f"docs/reference/platforms/{item['id']}/index.html")
        for rel in self.pages:
            path = self.build / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("<html><body>Every platform.</body></html>", encoding="utf-8")

    def tearDown(self):
        import shutil

        shutil.rmtree(self.tmp)

    def problems(self):
        return self.check.check_platform_labels(self.build, self.root)

    def test_clean_platform_pages_pass(self):
        self.assertEqual(self.problems(), [])

    def test_returned_caption_fails(self):
        page = self.build / "integrations/index.html"
        page.write_text(
            '<html><body><span class="caption">Coming soon</span></body></html>',
            encoding="utf-8",
        )
        found = self.problems()
        self.assertTrue(any("Coming soon" in p for p in found), found)

    def test_example_tab_placeholder_passes(self):
        page = self.build / "docs/reference/platforms/linkedin/index.html"
        page.write_text(
            '<html><body><div class="tabs-soon"><p class="ui">Coming soon</p>'
            '<p class="caption muted">The Blowhorn REST API is coming soon.</p>'
            "</div></body></html>",
            encoding="utf-8",
        )
        self.assertEqual(self.problems(), [])


class CountedNetworksTest(unittest.TestCase):
    """Blowhorn's networks are never counted in site copy."""

    def setUp(self):
        import check_theme as check

        self.check = check
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "content/en/compare").mkdir(parents=True)
        (self.tmp / "content/en/docs").mkdir(parents=True)
        (self.tmp / "data").mkdir()
        (self.tmp / "layouts").mkdir()

    def tearDown(self):
        import shutil

        shutil.rmtree(self.tmp)

    def write(self, rel, text):
        (self.tmp / rel).write_text(text, encoding="utf-8")

    def test_checked_in_copy_passes(self):
        self.assertEqual(self.check.check_countable_network_copy(ROOT), [])

    def test_counted_phrases_fail(self):
        for phrase in ("Blowhorn covers eight networks", "Seven fronts, one desk", "on 8 networks"):
            self.write("content/en/compare/acme.md", phrase + "\n")
            found = self.check.check_countable_network_copy(self.tmp)
            self.assertEqual(len(found), 1, (phrase, found))

    def test_data_and_layouts_are_scanned_but_docs_are_not(self):
        self.write("data/x.json", '{"a": "across seven networks"}\n')
        self.write("layouts/x.html", "<p>eight fronts</p>\n")
        self.write("content/en/docs/x.md", "nine networks\n")
        found = self.check.check_countable_network_copy(self.tmp)
        self.assertEqual(len(found), 2, found)

    def test_seven_tabs_and_all_seven_pass(self):
        self.write("data/x.json", '{"a": "seven tabs and a prayer", "b": "all seven", "c": "seven-tabs"}\n')
        self.assertEqual(self.check.check_countable_network_copy(self.tmp), [])


class OpenNetworkListsTest(unittest.TestCase):
    """A sentence listing all of Blowhorn's networks, or all but one, must
    read as open ("and more"), so it never goes stale when one ships."""

    PLATFORMS = {
        "hacker-news": "Hacker News",
        "linkedin": "LinkedIn",
        "x": "X (Twitter)",
        "youtube": "YouTube",
    }
    ALL = "LinkedIn, X, Hacker News and YouTube"

    def setUp(self):
        import check_theme as check

        self.check = check
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "data/platforms").mkdir(parents=True)
        for pid, name in self.PLATFORMS.items():
            self.write(f"data/platforms/{pid}.yaml", f"id: {pid}\nname: {name}\n")
        (self.tmp / "content/en/compare").mkdir(parents=True)
        (self.tmp / "content/en/docs").mkdir(parents=True)
        (self.tmp / "layouts").mkdir()

    def tearDown(self):
        import shutil

        shutil.rmtree(self.tmp)

    def write(self, rel, text):
        (self.tmp / rel).write_text(text, encoding="utf-8")

    def found(self):
        return self.check.check_open_network_lists(self.tmp)

    def test_checked_in_copy_passes(self):
        self.assertEqual(self.check.check_open_network_lists(ROOT), [])

    def test_names_come_from_the_platform_yaml_without_parentheticals(self):
        self.assertEqual(
            self.check.supported_network_names(self.tmp),
            ["Hacker News", "LinkedIn", "X", "YouTube"],
        )

    def test_closed_list_of_every_network_fails(self):
        self.write("content/en/compare/acme.md", f"Posts to {self.ALL}.\n")
        found = self.found()
        self.assertEqual(len(found), 1, found)
        self.assertNotIn("leaves out", found[0])

    def test_closed_list_missing_one_network_names_it(self):
        self.write(
            "data/x.json",
            '{"a": "Hacker News joins LinkedIn and X in one queue."}\n',
        )
        found = self.found()
        self.assertEqual(len(found), 1, found)
        self.assertIn("leaves out YouTube", found[0])

    def test_open_lists_pass(self):
        for text in (
            "Posts to LinkedIn, X, Hacker News, YouTube and more.",
            "You also speak on X, Hacker News, YouTube and more",
            "Your audience is on LinkedIn, X, YouTube and more, and you message Hacker News.",
            "Accounts you configure, such as LinkedIn, X and Hacker News.",
            "Every network: LinkedIn, X, Hacker News, YouTube + many more",
            "Posts to LinkedIn, X, Hacker News, [YouTube](/field-manual/youtube/) and more.",
            "Posts to LinkedIn, X, Hacker News, **YouTube** and more.",
            "Posts to LinkedIn, X, _Hacker News_, <b>YouTube</b> and more.",
        ):
            self.write("content/en/compare/acme.md", text + "\n")
            self.assertEqual(self.found(), [], text)

    def test_open_marker_away_from_the_list_does_not_open_it(self):
        for text in (
            "Blowhorn posts to LinkedIn, X and Hacker News from one or more computers.",
            "Post, follow and more on LinkedIn, X and Hacker News.",
            "Accounts such as yours post to LinkedIn, X and Hacker News.",
        ):
            self.write("content/en/compare/acme.md", text + "\n")
            found = self.found()
            self.assertEqual(len(found), 1, (text, found))
            self.assertIn("leaves out YouTube", found[0])

    def test_curated_lists_pass(self):
        self.write(
            "data/x.yaml",
            "a: Analytics cover LinkedIn and YouTube.\n"
            "b: Hacker News and X.\n",
        )
        self.assertEqual(self.found(), [])

    def test_layouts_are_scanned_through_their_tags(self):
        self.write("layouts/x.html", f"<p>One queue for <b>{self.ALL}</b>.</p>\n")
        self.assertEqual(len(self.found()), 1)
        self.write("layouts/x.html", "<p>One queue for <b>LinkedIn, X, Hacker News</b> and more.</p>\n")
        self.assertEqual(self.found(), [])

    def test_synced_docs_are_not_scanned(self):
        self.write("content/en/docs/x.md", f"Blowhorn posts to {self.ALL}.\n")
        self.assertEqual(self.found(), [])

    def test_recorded_film_captions_are_allowed(self):
        (self.tmp / "content/en/resources/videos/getting-started").mkdir(parents=True)
        self.write(
            "content/en/resources/videos/getting-started/battalion-thunder.md",
            "Major Blowhorn's one call lands on LinkedIn, X and Hacker News.\n",
        )
        self.assertEqual(self.found(), [])


class HomeSoonSplitTest(unittest.TestCase):
    """Issue #720: the built home page must not bring back a Coming soon split
    (a group heading, or a label on a listed platform), while its out-of-scope
    "coming soon" copy (team invites, the REST API) stays allowed."""

    def setUp(self):
        import shutil

        import check_theme as check

        self.check = check
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / "repo"
        self.build = self.tmp / "public"
        shutil.copytree(ROOT / "data", self.root / "data")
        self.build.mkdir()

    def tearDown(self):
        import shutil

        shutil.rmtree(self.tmp)

    def problems(self, body, page="index.html"):
        path = self.build / page
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"<html><body><main>{body}</main></body></html>", encoding="utf-8")
        return self.check.check_home_soon_split(self.build, self.root)

    def test_missing_pages_are_skipped(self):
        self.assertEqual(self.check.check_home_soon_split(self.build, self.root), [])

    def test_clean_home_passes(self):
        self.assertEqual(self.problems("<h2>Every platform</h2><p>Instagram, YouTube and X.</p>"), [])

    def test_out_of_scope_coming_soon_copy_passes(self):
        body = (
            '<p class="machines-footnote">Each profile posts as itself. Team invites are coming soon.</p>'
            '<li><h3>REST API</h3><p class="label">Coming soon</p>'
            "<p>Planned: every action over HTTP. Until it lands, use the CLI or MCP.</p></li>"
        )
        self.assertEqual(self.problems(body), [])

    def test_coming_soon_group_heading_fails(self):
        found = self.problems("<h2>Coming soon</h2><ul><li>Something</li></ul>")
        self.assertEqual(len(found), 1, found)
        self.assertIn("Coming soon group heading", found[0])

    def test_heading_with_inner_markup_fails(self):
        found = self.problems('<h3 class="h3"><span>Coming</span> soon</h3>')
        self.assertTrue(any("group heading" in p for p in found), found)

    def test_sentence_calling_a_platform_coming_soon_fails(self):
        found = self.problems("<p>Instagram is coming soon.</p>")
        self.assertEqual(len(found), 1, found)
        self.assertIn("calls a listed platform coming soon", found[0])

    def test_label_beside_a_platform_fails(self):
        found = self.problems('<h3>Instagram</h3><p class="label">Coming soon</p>')
        self.assertEqual(len(found), 1, found)
        self.assertIn("label beside a listed platform", found[0])

    def test_label_before_a_platform_fails(self):
        found = self.problems('<p class="label">Coming soon</p><h3>YouTube</h3>')
        self.assertEqual(len(found), 1, found)

    def test_a_label_two_blocks_away_from_a_platform_passes(self):
        self.assertEqual(self.problems("<h3>Instagram</h3><p>Posts as itself.</p><p>Coming soon</p><p>More.</p>"), [])

    def test_example_tab_placeholder_passes(self):
        body = '<div class="tabs-soon"><p>Coming soon</p></div><h3>Instagram</h3>'
        self.assertEqual(self.problems(body), [])

    def test_script_and_style_text_is_ignored(self):
        self.assertEqual(self.problems("<script>var s='Instagram coming soon'</script><style>.a{}</style>"), [])

    def test_reveille_preview_is_scanned_when_built(self):
        found = self.problems("<h2>Coming soon</h2>", page="home-reveille/index.html")
        self.assertEqual(len(found), 1, found)
        self.assertIn("/home-reveille/index.html", found[0])

    def test_other_pages_are_not_scanned_here(self):
        found = self.problems("<h2>Coming soon</h2>", page="pricing/index.html")
        self.assertEqual(found, [])

    def test_main_reports_the_failure(self):
        self.problems("<h2>Coming soon</h2>")
        self.assertTrue(self.check.check_home_soon_split(self.build, self.root))


class PlatformSoonCopyTest(unittest.TestCase):
    """The site's own copy must never call a listed platform coming soon,
    while "coming soon" copy that names no platform stays allowed and the
    synced docs are left to the built-page guard."""

    def setUp(self):
        import shutil

        import check_theme as check

        self.check = check
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / "repo"
        shutil.copytree(ROOT / "data", self.root / "data")
        (self.root / "content/en/compare").mkdir(parents=True)
        (self.root / "content/en/docs").mkdir(parents=True)

    def tearDown(self):
        import shutil

        shutil.rmtree(self.tmp)

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_checked_in_copy_passes(self):
        self.assertEqual(self.check.check_platform_soon_copy(ROOT), [])

    def test_names_come_from_yaml_and_catalog(self):
        names = self.check.platform_names(ROOT)
        for name in ("YouTube", "Instagram", "X (Twitter)", "X", "Hacker News"):
            self.assertIn(name, names)

    def test_compare_networks_row_fails(self):
        self.write(
            "content/en/compare/acme.md",
            '{"rows":[{"f":"Networks","b":"LinkedIn, X. Instagram and YouTube coming soon"}]}\n',
        )
        found = self.check.check_platform_soon_copy(self.root)
        self.assertEqual(len(found), 1, found)
        self.assertIn("content/en/compare/acme.md", found[0])

    def test_compare_hub_row_split_across_fields_fails(self):
        # The compare hub's Networks row before YouTube shipped: the platforms
        # are the row's feature and the status is its Blowhorn cell.
        self.write(
            "content/en/compare/_index.md",
            "---\n"
            "title: Compare\n"
            "rows:\n"
            "  - feature: Instagram, TikTok, Facebook and YouTube\n"
            '    blowhorn: { level: partial, text: "Coming soon" }\n'
            '    schedulers: { level: yes, text: "Yes" }\n'
            "  - feature: Posts with every laptop closed\n"
            '    blowhorn: { level: partial, text: "As long as one computer is awake" }\n'
            "---\n\nBody.\n",
        )
        found = self.check.check_platform_soon_copy(self.root)
        self.assertEqual(len(found), 1, found)
        self.assertIn("YouTube", found[0])

    def test_faq_answer_split_from_its_question_fails(self):
        self.write(
            "content/en/ai/mcp.md",
            '{"faq": [{"q": "Does it post to YouTube?", "a": "Coming soon. Today, use the CLI."}]}\n',
        )
        found = self.check.check_platform_soon_copy(self.root)
        self.assertEqual(len(found), 1, found)
        self.assertIn("content/en/ai/mcp.md", found[0])

    def test_bare_soon_row_without_a_platform_passes(self):
        self.write(
            "content/en/compare/_index.md",
            "---\n"
            "intro: Works on LinkedIn, X and YouTube.\n"
            "rows:\n"
            "  - feature: Team invites\n"
            '    blowhorn: { level: partial, text: "Coming soon" }\n'
            "  - feature: LinkedIn, X and YouTube\n"
            '    blowhorn: { level: yes, text: "Yes" }\n'
            "---\n",
        )
        self.write(
            "content/en/ai/mcp.md",
            '{"faq": [{"q": "Can I npx it?", "a": "Coming soon. Today, use the CLI on LinkedIn."}]}\n',
        )
        self.assertEqual(self.check.check_platform_soon_copy(self.root), [])

    def test_data_faq_fails(self):
        faq = self.root / "data/solutions.json"
        faq.write_text(
            faq.read_text(encoding="utf-8").replace(
                '"solutions"', '"note": "TikTok is Coming soon.", "solutions"', 1
            ),
            encoding="utf-8",
        )
        found = self.check.check_platform_soon_copy(self.root)
        self.assertTrue(any("data/solutions.json" in p for p in found), found)

    def test_soon_copy_without_a_platform_passes(self):
        self.write(
            "content/en/compare/acme.md",
            '{"rows":[{"b":"Sound wave from every profile. Team invites coming soon"}]}\n',
        )
        self.write("content/en/download.md", "Blowhorn for Windows, coming soon.\n")
        self.assertEqual(self.check.check_platform_soon_copy(self.root), [])

    def test_synced_docs_are_not_scanned(self):
        self.write("content/en/docs/reference/platforms/tiktok.md", "TikTok is coming soon.\n")
        self.assertEqual(self.check.check_platform_soon_copy(self.root), [])


class IntegrationsCatalogOnceTest(unittest.TestCase):
    """Issue #784: /integrations/ showed the "Your browser" heading and its
    platforms twice, once in the map's By type panel and once in the catalog.
    Each category heading and each catalog card must appear once."""

    def setUp(self):
        import check_theme as check

        self.check = check
        payload = json.loads((ROOT / "data/integrations.json").read_text(encoding="utf-8"))
        self.categories = payload["categories"]

    def catalog(self, categories):
        """The catalog sections as layouts/integrations.html renders them."""
        parts = []
        for group in categories:
            parts.append(f'<section class="section" aria-labelledby="cat-{group["id"]}" data-action-catalog>')
            parts.append(f'<h2 id="cat-{group["id"]}" class="h2">{group["name"]}</h2>')
            parts.append(f'<p class="muted">{group["summary"]}</p><ul class="grid grid-3 section-body">')
            for pid in group["platforms"]:
                parts.append(
                    f'<li class="card integration-card card-a" data-action-card data-actions="post" '
                    f'data-plat-id="{pid}"><a class="integration-card-main" href="/docs/{pid}/">'
                    f'<h3 class="h3">{pid}</h3><p>Your browser</p></a></li>'
                )
            parts.append("</ul></section>")
        return "".join(parts)

    def by_type_index(self, categories):
        """The By type panel as it is now: links to the catalog's sections."""
        links = "".join(
            f'<li><a class="platform" href="#cat-{g["id"]}"><span class="ui">{g["name"]}</span>'
            '<span class="caption">See the list</span></a></li>'
            for g in categories
        )
        return f'<div class="plat-panel is-on" id="plat-panel-category"><ul class="plat-row">{links}</ul></div>'

    def by_type_repeat(self, categories):
        """The By type panel before the fix: every heading and platform again."""
        parts = ['<div class="plat-panel is-on" id="plat-panel-category"><ul class="plat-cats">']
        for group in categories:
            parts.append(f'<li class="plat-cat"><h3 class="h3">{group["name"]}</h3><ul class="plat-row">')
            for pid in group["platforms"]:
                parts.append(f'<li><a class="platform" href="/docs/{pid}/"><span class="ui">{pid}</span></a></li>')
            parts.append("</ul></li>")
        parts.append("</ul></div>")
        return "".join(parts)

    def page(self, panel, catalog):
        return f"<html><body><main>{panel}{catalog}</main></body></html>"

    def test_index_panel_and_catalog_pass(self):
        html = self.page(self.by_type_index(self.categories), self.catalog(self.categories))
        self.assertEqual(self.check.catalog_duplicate_problems(html, self.categories), [])

    def test_repeated_by_type_panel_fails(self):
        html = self.page(self.by_type_repeat(self.categories), self.catalog(self.categories))
        found = self.check.catalog_duplicate_problems(html, self.categories)
        self.assertIn("/integrations/index.html has 2 'Your browser' headings, want 1", found)
        self.assertEqual(len(found), len(self.categories), found)

    def test_category_listed_twice_in_data_fails(self):
        chrome = next(g for g in self.categories if g["id"] == "chrome")
        doubled = self.categories + [chrome]
        html = self.page(self.by_type_index(self.categories), self.catalog(doubled))
        found = self.check.catalog_duplicate_problems(html, self.categories)
        self.assertIn("/integrations/index.html has 2 'Your browser' headings, want 1", found)
        self.assertIn("/integrations/index.html has 2 'linkedin' catalog cards, want 1", found)

    def test_missing_catalog_section_fails(self):
        rest = [g for g in self.categories if g["id"] != "chrome"]
        html = self.page(self.by_type_index(rest), self.catalog(rest))
        found = self.check.catalog_duplicate_problems(html, self.categories)
        self.assertIn("/integrations/index.html has 0 'Your browser' headings, want 1", found)

    def test_heading_text_in_script_is_ignored(self):
        html = self.page(
            "<script>var h='<h2>Your browser</h2>'</script>" + self.by_type_index(self.categories),
            self.catalog(self.categories),
        )
        self.assertEqual(self.check.catalog_duplicate_problems(html, self.categories), [])


if __name__ == "__main__":
    unittest.main()
