#!/usr/bin/env python3
"""Platform product pages must match their data and behave (docs/platform-pages.md).

Run with `make test-scripts` (CI runs it too). The source tests copy the data,
the page file and hugo.toml into a fixture, check that check_platform_pages.py
passes them, then break one thing and check that the check names it. The built
tests build the real site once with Hugo, check the generated preview page and
run assets/js/platform-page.js against it through platform_page_harness.js, then
break the generated page or the script and check that the failure is caught.
"""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import check_platform_pages as check

ROOT = Path(__file__).resolve().parents[2]
HUGO = ROOT / "node_modules" / ".bin" / "hugo"
PAGE = "content/en/preview-platform-x.md"
ROUTE = "/preview/platforms/x/"
SOURCES = (
    "content/en/docs/how-to/settings/choose-your-rules-of-engagement.md",
    "content/en/field-manual/x.md",
    "content/en/docs/how-to/set-up/connect-mcp-client.md",
    "content/en/docs/reference/cli/risk.md",
    "content/en/agents/claude-code.md",
)


def hugo_binary():
    return str(HUGO) if HUGO.is_file() else shutil.which("hugo")


class Fixture:
    """A temporary copy of what --source reads, plus the page script."""

    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        shutil.copytree(ROOT / "data", self.root / "data")
        (self.root / "content/en").mkdir(parents=True)
        shutil.copy(ROOT / PAGE, self.root / PAGE)
        # The public pages the record's sourced facts and snippets quote.
        for rel in SOURCES:
            (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / rel, self.root / rel)
        shutil.copy(ROOT / "hugo.toml", self.root / "hugo.toml")
        (self.root / check.SCRIPT).parent.mkdir(parents=True)
        shutil.copy(ROOT / check.SCRIPT, self.root / check.SCRIPT)

    def data(self):
        return json.loads((self.root / "data/platform_pages.json").read_text(encoding="utf-8"))

    def write_data(self, data):
        (self.root / "data/platform_pages.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def edit(self, rel, old, new):
        path = self.root / rel
        text = path.read_text(encoding="utf-8")
        assert old in text, f"{old!r} not in {rel}"
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def close(self):
        self.tmp.cleanup()


class SourceTest(unittest.TestCase):
    def setUp(self):
        self.fx = Fixture()
        self.addCleanup(self.fx.close)

    def problems(self):
        return check.check_source(self.fx.root)

    def mutate(self, fn):
        data = self.fx.data()
        fn(data["pages"][0])
        self.fx.write_data(data)
        return self.problems()

    def assertNamed(self, problems, *fragments):
        joined = "\n".join(problems)
        for fragment in fragments:
            self.assertIn(fragment, joined)

    def test_the_repository_data_passes(self):
        self.assertEqual(check.check_source(ROOT), [])
        self.assertEqual(self.problems(), [])

    def test_a_coming_soon_platform_gets_no_page(self):
        def fn(rec):
            rec["platform"] = "youtube"
        self.assertNamed(self.mutate(fn), "'youtube' is 'coming-soon'")

    def test_an_activity_must_name_an_action_the_platform_lists(self):
        def fn(rec):
            rec["activities"][1]["action"] = "comment"
        self.assertNamed(self.mutate(fn), "names 'comment', which data/platforms/x.yaml does not list")

    def test_an_activity_must_name_a_vocabulary_action(self):
        def fn(rec):
            rec["activities"][1]["action"] = "retweet"
        self.assertNamed(self.mutate(fn), "names 'retweet', not in data/actions.json")

    def test_two_activities_cannot_share_an_action(self):
        def fn(rec):
            rec["activities"][2]["action"] = "post"
        self.assertNamed(self.mutate(fn), "two activities bind action 'post'")

    def test_the_route_follows_the_platform(self):
        def fn(rec):
            rec["route"] = "/preview/platforms/twitter/"
        self.assertNamed(self.mutate(fn), "must be /preview/platforms/x/")

    def test_the_page_stays_out_of_indexes_and_search(self):
        for old, new, key in (
            ("noindex: true", "noindex: false", "noindex"),
            ("exclude_search: true", "exclude_search: false", "exclude_search"),
            ("  disable: true", "  disable: false", "sitemap.disable"),
            ("  list: never", "  list: always", "build.list"),
        ):
            with self.subTest(key=key):
                fx = Fixture()
                self.addCleanup(fx.close)
                fx.edit(PAGE, old, new)
                self.assertIn(f"front matter {key} is", "\n".join(check.check_source(fx.root)))

    def test_llms_txt_keeps_preview_out(self):
        self.fx.edit("hugo.toml", ', "/preview/**"', "")
        self.assertNamed(self.problems(), 'exclude must list "/preview/**"')

    def test_a_record_needs_its_page_and_a_page_its_record(self):
        (self.fx.root / PAGE).rename(self.fx.root / "content/en/preview-platform-bluebird.md")
        self.fx.edit("content/en/preview-platform-bluebird.md", "platform: x", "platform: bluebird")
        self.assertNamed(self.problems(), "preview-platform-x.md is missing", "for 'bluebird', which has no record")

    def test_no_em_dash_in_the_data(self):
        def fn(rec):
            rec["playground"]["intro"] = "Write a post — and preview it here."
        self.assertNamed(self.mutate(fn), "carries an em dash")

    def test_a_starter_must_use_a_declared_activity(self):
        def fn(rec):
            rec["playground"]["starters"]["items"][0]["activity"] = "follow"
        self.assertNamed(self.mutate(fn), "starter 'launch-update' uses undeclared activity 'follow'")

    def test_starter_ids_are_unique(self):
        def fn(rec):
            items = rec["playground"]["starters"]["items"]
            items[1]["id"] = items[0]["id"]
        self.assertNamed(self.mutate(fn), "starter id 'launch-update' repeats")

    def test_the_thread_length_is_the_yaml_one(self):
        def fn(rec):
            rec["playground"]["thread"]["at"] = 280
        self.assertNamed(self.mutate(fn), "thread.at is 280", "'longer than 280 characters'")

    def test_every_action_needs_a_cli_example(self):
        path = self.fx.root / "data/action_examples.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["examples"] = [e for e in data["examples"] if (e["platform"], e["action"]) != ("x", "analytics")]
        path.write_text(json.dumps(data), encoding="utf-8")
        self.assertNamed(self.problems(), "no x example for 'analytics'")

    def test_a_quote_must_be_on_its_source_page(self):
        def fn(rec):
            rec["roe"]["presets"][0]["quote"] = "on X it is 13 posts a day"
            rec["roe"]["presets"][0]["stat"] = "13"
        self.assertNamed(self.mutate(fn), "does not say 'on X it is 13 posts a day'")

    def test_a_number_must_come_from_its_quote(self):
        def fn(rec):
            rec["fieldManual"]["facts"][0]["text"] = "A reply the author engages with scored 90."
        self.assertNamed(self.mutate(fn), "shows ['90'], which the quote")

    def test_a_preset_meaning_is_verbatim(self):
        def fn(rec):
            rec["roe"]["presets"][2]["means"] = "as fast as you like"
        self.assertNamed(self.mutate(fn), "does not say 'as fast as you like'")

    def test_a_snippet_must_be_on_its_source_page(self):
        def fn(rec):
            rec["usage"]["items"][1]["code"] = "blowhorn risk show --platform x --everything"
        self.assertNamed(self.mutate(fn), "usage 'cli'", "does not say")

    def test_the_skill_snippet_is_read_from_json_front_matter(self):
        self.fx.edit("content/en/agents/claude-code.md", "Preview anything that publishes with --dry-run first.", "Preview first.")
        self.assertNamed(self.problems(), "usage 'skill'")

    def test_a_source_must_be_a_page_here(self):
        def fn(rec):
            rec["fieldManual"]["facts"][1]["source"] = "/field-manual/nowhere/"
        self.assertNamed(self.mutate(fn), "is not a page under content/en/")

    def test_the_script_never_makes_a_request(self):
        for call in ("fetch('/x')", "navigator.sendBeacon('/x')", "localStorage.setItem('a', 1)", "document.cookie = 'a'"):
            with self.subTest(call=call):
                fx = Fixture()
                self.addCleanup(fx.close)
                fx.edit(str(check.SCRIPT), "    render();\n    controls.hidden = false;", f"    render();\n    {call};\n    controls.hidden = false;")
                self.assertIn("the playground is local only", "\n".join(check.check_source(fx.root)))


class LinkGuardTest(unittest.TestCase):
    """links_to finds a link to the preview however it is written."""

    def test_every_way_of_writing_the_link_is_found(self):
        for href in (
            "/preview/platforms/x/",
            "/preview/platforms/x",
            "/preview/platforms/x/#examples",
            "/preview/platforms/x?ref=nav",
            "https://blowhorn.ai/preview/platforms/x/",
            "http://localhost:1313/preview/platforms/x",
            "/blowhorn-site/preview/platforms/x/",
            "preview/platforms/x/",
            "../preview/platforms/x/",
        ):
            with self.subTest(href=href):
                self.assertTrue(check.links_to(f'<a class="n" href="{href}">x</a>', ROUTE))
                self.assertTrue(check.links_to(f"<a href='{href}'>x</a>", ROUTE))

    def test_other_pages_are_not_mistaken_for_it(self):
        for href in (
            "/preview/platforms/xylophone/",
            "/preview/platforms/x/other/",
            "/notpreview/platforms/x/",
            "/docs/reference/platforms/x/",
            "https://example.com/?next=/preview/platforms/x/",
        ):
            with self.subTest(href=href):
                self.assertFalse(check.links_to(f'<a href="{href}">x</a>', ROUTE))


@unittest.skipUnless(hugo_binary() and shutil.which("node"), "needs hugo and node")
class BuiltTest(unittest.TestCase):
    """The generated page, and the real script run against it."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.build = Path(cls.tmp.name) / "public"
        run = subprocess.run(
            [hugo_binary(), "--source", str(ROOT), "--destination", str(cls.build),
             "--cleanDestinationDir", "--minify", "--quiet"],
            capture_output=True, text=True, check=False,
        )
        if run.returncode != 0:
            raise RuntimeError(f"hugo failed: {run.stderr}")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def copy(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        out = Path(tmp.name) / "public"
        shutil.copytree(self.build, out)
        return out

    def edit_page(self, build, old, new, count=1):
        path = check.built_file(build, ROUTE)
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, count), encoding="utf-8")

    def problems(self, build, root=ROOT):
        return "\n".join(check.check_built(build, root))

    def test_the_built_page_passes(self):
        self.assertEqual(check.check_built(self.build, ROOT), [])

    def test_every_type_swaps_the_page(self):
        tree = check.parse(check.built_file(self.build, ROUTE)).main
        rec = json.loads((ROOT / "data/platform_pages.json").read_text(encoding="utf-8"))["pages"][0]
        types = [a["id"] for a in rec["activities"]]
        states = check.run_harness(tree, {"steps": [{"choose": t} for t in types]}, ROOT)
        for state, want in zip(states[1:], types):
            self.assertEqual(state["checked"], [want])
            self.assertEqual(set(state["shown"]), {want})
            self.assertGreaterEqual(state["shown"][want], 4)  # scene, intent, playground title, Activities chip

    def test_the_page_must_stay_noindex_and_unlinked(self):
        build = self.copy()
        self.edit_page(build, '<meta name="robots" content="noindex">', "")
        (build / "pricing/index.html").write_text(
            (build / "pricing/index.html").read_text(encoding="utf-8").replace("</main>", f'<a href="{ROUTE}">x</a></main>', 1),
            encoding="utf-8")
        found = self.problems(build)
        self.assertIn("is not noindex", found)
        self.assertIn("is linked from pricing/index.html", found)

    def test_one_primary_call_to_action(self):
        build = self.copy()
        self.edit_page(build, 'class="pp-starter ui"', 'class="pp-starter ui button-primary"')
        self.assertIn("exactly one primary button", self.problems(build))

    def test_the_call_to_action_installs_the_extension(self):
        build = self.copy()
        self.edit_page(build, f'href="{check.EXTENSION_HREF}" data-pp-start', 'href="/download/" data-pp-start')
        self.assertIn(f"to {check.EXTENSION_HREF}", self.problems(build))

    def test_the_download_page_keeps_the_same_install_path(self):
        build = self.copy()
        page = build / "download/index.html"
        page.write_text(page.read_text(encoding="utf-8").replace(check.EXTENSION_HREF, "https://example.com/ext"), encoding="utf-8")
        self.assertIn("/download/ no longer offers", self.problems(build))

    def test_nothing_sits_under_the_call_to_action(self):
        build = self.copy()
        self.edit_page(build, "</a>\n        </div>\n\n        <figure", '</a>\n          <p class="caption">Opens the download page.</p>\n        </div>\n\n        <figure')
        self.assertIn("something sits beside or under the call to action", self.problems(build))

    def test_a_reviewer_note_is_never_a_caption(self):
        build = self.copy()
        self.edit_page(build, 'class="pp-annot ui" data-pp-annotation', 'class="caption" data-pp-annotation')
        self.assertIn("reviewer annotation must be drawn as one", self.problems(build))

    def test_the_call_to_action_comes_before_the_illustration(self):
        """A phone stacks in source order: the call to action must not sit below the storyboard."""
        build = self.copy()
        path = check.built_file(build, ROUTE)
        html = path.read_text(encoding="utf-8")
        go_start = html.index('<div class="pp-go">')
        go_end = html.index("</div>", go_start) + len("</div>")
        stage_end = html.index("</figure>", html.index('data-pp-stage')) + len("</figure>")
        self.assertLess(go_start, html.index("<figure"))
        moved = html[:go_start] + html[html.index("<figure", go_start):stage_end] + html[go_start:go_end] + html[stage_end:]
        path.write_text(moved, encoding="utf-8")
        self.assertIn("source order must be selector, call to action, illustration", self.problems(build))

    def test_the_matrix_is_never_collapsed(self):
        build = self.copy()
        self.edit_page(build, '<table class="pp-matrix" data-pp-matrix>', '<details><summary>Actions</summary><table class="pp-matrix" data-pp-matrix>')
        self.edit_page(build, "</table>", "</table></details>")
        self.assertIn("a <details> on the page", self.problems(build))

    def test_a_matrix_cell_that_drifts_is_caught(self):
        build = self.copy()
        self.edit_page(build, "Read-only.", "Read and write.")
        self.assertIn("matrix 'analytics' limits reads 'Read and write.'", self.problems(build))

    def test_an_action_without_limits_says_so(self):
        tree = check.parse(check.built_file(self.build, ROUTE)).main
        rec = json.loads((ROOT / "data/platform_pages.json").read_text(encoding="utf-8"))["pages"][0]
        row = next(r for r in check.walk(tree) if r["tag"] == "tr" and r["attrs"].get("data-action") == "amplify")
        self.assertIn(rec["matrix"]["none"], " ".join(check.text(row).split()))

    def test_every_setup_can_be_copied(self):
        build = self.copy()
        self.edit_page(build, 'class="term-copy"', 'class="term-nocopy"', count=3)
        self.assertIn("cannot be copied", self.problems(build))

    def test_a_dead_source_anchor_is_caught(self):
        build = self.copy()
        page = build / "field-manual/x/index.html"
        page.write_text(page.read_text(encoding="utf-8").replace('id="what-xs-ranking-rewards"', 'id="gone"'), encoding="utf-8")
        self.assertIn("cites #what-xs-ranking-rewards", self.problems(build))

    def test_the_playground_submits_nothing(self):
        build = self.copy()
        self.edit_page(build, '<textarea id="pp-try-text"', '<textarea name="draft" id="pp-try-text"')
        self.assertIn("a named textarea", self.problems(build))
        build = self.copy()
        self.edit_page(build, '<div class="pp-try-grid">', '<form action="/x"><div class="pp-try-grid">')
        self.assertIn("a <form> in the page", self.problems(build))

    def test_the_preview_mirrors_text_never_markup(self):
        fx = Fixture()
        self.addCleanup(fx.close)
        fx.edit(check.SCRIPT, "out.textContent = value;", "out.textContent = value.replace(/<[^>]*>/g, '');")
        self.assertIn("does not mirror the draft as text", self.problems(self.build, fx.root))

    def test_the_thread_flag_is_announced_once(self):
        fx = Fixture()
        self.addCleanup(fx.close)
        fx.edit(check.SCRIPT, "if (now && thread) say(thread.textContent);", "")
        self.assertIn("crossing 274 characters announced", self.problems(self.build, fx.root))

    def test_a_removed_image_is_released(self):
        fx = Fixture()
        self.addCleanup(fx.close)
        fx.edit(check.SCRIPT, "if (url && window.URL && URL.revokeObjectURL) URL.revokeObjectURL(url);", "")
        found = self.problems(self.build, fx.root)
        self.assertIn("replacing the image keeps", found)
        self.assertIn("removing the image leaves", found)

    def test_a_non_image_is_refused(self):
        fx = Fixture()
        self.addCleanup(fx.close)
        fx.edit(check.SCRIPT, 'if (!/^image\\//.test(picked.type || "")) {', "if (false) {")
        self.assertIn("a non-image file is not refused", self.problems(self.build, fx.root))

    def test_a_starter_fills_the_draft(self):
        fx = Fixture()
        self.addCleanup(fx.close)
        fx.edit(check.SCRIPT, 'text.value = button.getAttribute("data-sample") || "";', "")
        self.assertIn("starter 'weekly-recap' shows", self.problems(self.build, fx.root))

    def test_clicking_the_checked_radio_changes_nothing(self):
        tree = check.parse(check.built_file(self.build, ROUTE)).main
        rec = json.loads((ROOT / "data/platform_pages.json").read_text(encoding="utf-8"))["pages"][0]
        other = rec["activities"][1]["id"]
        for step in ({"choose": other}, {"key": other}):
            runs = check.run_harness(tree, {"steps": [step]}, ROOT)
            self.assertEqual(runs[1]["checked"], [other])
            self.assertEqual(runs[1]["announceWrites"] - runs[0]["announceWrites"], 1)
        idle = check.run_harness(tree, {"steps": [{"choose": rec["activities"][0]["id"]}]}, ROOT)
        self.assertEqual(idle[1]["announceWrites"], idle[0]["announceWrites"])

    def test_an_undecodable_image_is_dropped_and_announced(self):
        fx = Fixture()
        self.addCleanup(fx.close)
        fx.edit(check.SCRIPT, 'img.addEventListener("error", function () {', 'img.addEventListener("load", function () {')
        self.assertIn("cannot decode", self.problems(self.build, fx.root))

    def test_a_refused_file_is_announced(self):
        fx = Fixture()
        self.addCleanup(fx.close)
        fx.edit(check.SCRIPT, 'say(announce ? announce.getAttribute("data-not-image") || "" : "");', "")
        self.assertIn("a non-image file announces", self.problems(self.build, fx.root))

    def test_a_kept_page_keeps_its_image(self):
        fx = Fixture()
        self.addCleanup(fx.close)
        fx.edit(check.SCRIPT, "if (!event.persisted) release();", "release();")
        self.assertIn("persisted=True revoked", self.problems(self.build, fx.root))

    def test_the_thread_flag_belongs_to_the_post_type(self):
        fx = Fixture()
        self.addCleanup(fx.close)
        fx.edit(check.SCRIPT, "var now = postActive() && max > 0 && n > max;", "var now = max > 0 && n > max;")
        self.assertIn("a long draft under", self.problems(self.build, fx.root))

    def test_the_counter_is_described_only_for_the_post_type(self):
        fx = Fixture()
        self.addCleanup(fx.close)
        fx.edit(check.SCRIPT, 'else text.removeAttribute("aria-describedby");', "")
        self.assertIn("describes", self.problems(self.build, fx.root))

    def test_a_type_change_refreshes_the_playground(self):
        fx = Fixture()
        self.addCleanup(fx.close)
        fx.edit(check.SCRIPT, 'input.addEventListener("change", render);', "")
        self.assertIn("back on", self.problems(self.build, fx.root))

    def test_a_starter_button_needs_no_description(self):
        build = self.copy()
        self.edit_page(build, 'data-pp-try-starter="launch-update"', 'data-pp-try-starter="launch-update" aria-describedby="pp-try-title"')
        self.assertIn("a starter button carries aria-describedby", self.problems(build))

    def test_the_matrix_is_a_native_table_in_a_scroll_region(self):
        build = self.copy()
        self.edit_page(build, '<th scope="row"', '<th scope="row" role="rowheader"')
        self.assertIn("a native table", self.problems(build))
        build = self.copy()
        self.edit_page(build, 'class="pp-matrix-scroll" role="group"', 'class="pp-matrix-scroll" role="presentation"')
        self.assertIn("focusable, labelled group", self.problems(build))

    def test_a_stale_thread_message_is_cleared_off_post(self):
        fx = Fixture()
        self.addCleanup(fx.close)
        fx.edit(check.SCRIPT, 'announce.textContent === thread.textContent) say("");', "false) say(\"\");")
        self.assertIn("stale live message", self.problems(self.build, fx.root))

    def test_the_field_manual_claims_stay_in_the_quote(self):
        data = json.loads((ROOT / "data/platform_pages.json").read_text(encoding="utf-8"))
        facts = data["pages"][0]["fieldManual"]["facts"]
        self.assertNotIn("Space them out", " ".join(f["text"] for f in facts))

    def test_the_rail_never_stops_mid_card(self):
        fx = Fixture()
        self.addCleanup(fx.close)
        fx.edit(check.SCRIPT, "var left = Math.min(max, slides[i].offsetLeft - origin());",
                "var left = Math.min(max, slides[i].offsetLeft - origin() + 24);")
        self.assertIn("the rail stops mid-card", self.problems(self.build, fx.root))

    def test_a_script_that_forgets_a_region_is_caught(self):
        fx = Fixture()
        self.addCleanup(fx.close)
        fx.edit(check.SCRIPT, 'all(root, "[data-pp-for]")', 'all(root, "[data-pp-scene-text]")')
        found = self.problems(self.build, fx.root)
        self.assertIn("choosing 'respond' shows elements for", found)

    def test_a_disabled_rail_button_is_caught(self):
        fx = Fixture()
        self.addCleanup(fx.close)
        fx.edit(check.SCRIPT,
                'prev.setAttribute("aria-disabled", atStart() ? "true" : "false");',
                'prev.setAttribute("aria-disabled", atStart() ? "true" : "false"); if (atStart()) prev.setAttribute("disabled", ""); else prev.removeAttribute("disabled");')
        self.assertIn("must use aria-disabled", self.problems(self.build, fx.root))

    def test_reduced_motion_is_honoured(self):
        fx = Fixture()
        self.addCleanup(fx.close)
        fx.edit(check.SCRIPT, 'behavior: reduced() ? "auto" : "smooth" });\n    }', 'behavior: "smooth" });\n    }')
        self.assertIn("under reduced motion the rail scrolls ['smooth']", self.problems(self.build, fx.root))

    def test_a_link_in_any_form_is_caught(self):
        for href in ("https://blowhorn.ai/preview/platforms/x/", "/preview/platforms/x", "/base/preview/platforms/x/#a"):
            with self.subTest(href=href):
                build = self.copy()
                page = build / "pricing/index.html"
                page.write_text(page.read_text(encoding="utf-8").replace("</main>", f'<a href="{href}">x</a></main>', 1), encoding="utf-8")
                self.assertIn("is linked from pricing/index.html", self.problems(build))

    def test_the_activities_intro_starts_in_the_app(self):
        tree = check.parse(check.built_file(self.build, ROUTE)).main
        section = next(e for e in check.walk(tree) if e["attrs"].get("aria-labelledby") == "pp-activities-title")
        intro = " ".join(check.text(section).split())
        self.assertIn("Start in the app", intro)
        self.assertNotIn("Start it here", intro)

    def test_the_limits_are_the_docs_limits(self):
        """Post and Respond show X's published daily caps in the matrix, the same
        text as the docs page, because both read data/platforms/x.yaml."""
        preview = " ".join(check.text(check.parse(check.built_file(self.build, ROUTE)).main).split())
        docs = " ".join(check.text(check.parse(check.built_file(self.build, "/docs/reference/platforms/x/")).main).split())
        limited = {a["id"]: a["limits"] for a in check.yaml_actions(ROOT, "x") if a["limits"]}
        for action in ("post", "reply", "follow"):
            self.assertIn(action, limited)
            self.assertIn(limited[action], preview)
            self.assertIn(limited[action], docs)
        self.assertIn("50 original posts", limited["post"])
        self.assertIn("200 replies", limited["reply"])

    def test_scrolling_the_rail_announces_nothing(self):
        fx = Fixture()
        self.addCleanup(fx.close)
        fx.edit(check.SCRIPT, "if (count) count.textContent = describe(inView());",
                "if (count) count.textContent = describe(inView()); if (announce) announce.textContent = describe(inView());")
        self.assertIn("scrolling the rail announced", self.problems(self.build, fx.root))

    def test_a_button_press_announces_where_the_rail_lands(self):
        fx = Fixture()
        self.addCleanup(fx.close)
        fx.edit(check.SCRIPT, 'if (announce) announce.textContent = "Showing " + describe(inView(left));', "")
        self.assertIn("paging forward announced", self.problems(self.build, fx.root))

    def test_the_rail_count_is_never_live(self):
        build = self.copy()
        self.edit_page(build, "data-pp-rail-count>", 'data-pp-rail-count aria-live="polite">')
        self.assertIn("the rail count is a live region", self.problems(build))


if __name__ == "__main__":
    unittest.main()
