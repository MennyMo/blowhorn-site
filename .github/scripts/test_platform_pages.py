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

    def test_an_example_must_use_a_declared_activity(self):
        def fn(rec):
            rec["examples"]["items"][0]["activity"] = "follow"
        self.assertNamed(self.mutate(fn), "uses undeclared activity 'follow'")

    def test_neighbouring_examples_never_share_a_variant(self):
        def fn(rec):
            rec["examples"]["items"][3]["variant"] = "field"
        self.assertNamed(self.mutate(fn), "'reply-with-context' and 'weekly-recap' are within 4", "'field' card variant")

    def test_paper_is_the_one_featured_example(self):
        def fn(rec):
            items = rec["examples"]["items"]
            items.extend([dict(items[1], id="extra-one", variant="field"),
                          dict(items[2], id="extra-two", variant="plain"),
                          dict(items[3], id="extra-three", variant="stamp"),
                          dict(items[0], id="extra-four", variant="paper")])
        self.assertNamed(self.mutate(fn), "2 paper examples")

    def test_a_breakdown_kind_appears_once(self):
        def fn(rec):
            rec["breakdown"]["items"][2]["kind"] = "supported"
        self.assertNamed(self.mutate(fn), "breakdown kind 'supported' repeats")

    def test_a_limits_breakdown_needs_limits(self):
        path = self.fx.root / "data/platforms/x.yaml"
        path.write_text("\n".join(l for l in path.read_text(encoding="utf-8").splitlines() if "limits:" not in l) + "\n", encoding="utf-8")
        self.assertNamed(self.problems(), "a limits breakdown, but data/platforms/x.yaml lists no limits")

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
            rec["examples"]["items"][0]["blurb"] = "A clear update — for your next release."
        self.assertNamed(self.mutate(fn), "carries an em dash")


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
            self.assertGreaterEqual(state["shown"][want], 4)  # scene, intent, Start context, Activities chip

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
        self.edit_page(build, 'class="pp-try ui"', 'class="pp-try ui button-primary"')
        self.assertIn("exactly one primary button", self.problems(build))

    def test_start_comes_before_the_illustration(self):
        """A phone stacks in source order: Start must not sit below the 546px storyboard."""
        build = self.copy()
        path = check.built_file(build, ROUTE)
        html = path.read_text(encoding="utf-8")
        go_start = html.index('<div class="pp-go">')
        go_end = html.index("</div>", html.index('id="pp-start-note"')) + len("</div>")
        stage_end = html.index("</figure>", html.index('data-pp-stage')) + len("</figure>")
        self.assertLess(go_start, html.index("<figure"))
        moved = html[:go_start] + html[html.index("<figure", go_start):stage_end] + html[go_start:go_end] + html[stage_end:]
        path.write_text(moved, encoding="utf-8")
        self.assertIn("source order must be selector, Start, illustration", self.problems(build))

    def test_the_rail_never_stops_mid_card(self):
        fx = Fixture()
        self.addCleanup(fx.close)
        fx.edit(check.SCRIPT, "var left = Math.min(max, slides[i].offsetLeft - origin());",
                "var left = Math.min(max, slides[i].offsetLeft - origin() + 24);")
        self.assertIn("the rail stops mid-card", self.problems(self.build, fx.root))

    def test_breakdowns_start_collapsed(self):
        build = self.copy()
        self.edit_page(build, '<details class="pp-disclosure"', '<details open class="pp-disclosure"')
        self.assertIn("open at load", self.problems(build))

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

    def test_an_example_preview_moves_focus_to_the_illustration(self):
        fx = Fixture()
        self.addCleanup(fx.close)
        fx.edit(check.SCRIPT, "stage.focus({ preventScroll: true });", "")
        self.assertIn("not the illustration", self.problems(self.build, fx.root))

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
        """Post and Respond show X's published daily caps, the same text on the
        preview and on the docs page, because both read data/platforms/x.yaml."""
        preview = " ".join(check.text(check.parse(check.built_file(self.build, ROUTE)).main).split())
        docs = " ".join(check.text(check.parse(check.built_file(self.build, "/docs/reference/platforms/x/")).main).split())
        limited = {a["id"]: a["limits"] for a in check.yaml_actions(ROOT, "x") if a["limits"]}
        for action in ("post", "reply", "follow"):
            self.assertIn(action, limited)
            self.assertIn(limited[action], preview)
            self.assertIn(limited[action], docs)
        self.assertIn("50 original posts", limited["post"])
        self.assertIn("200 replies", limited["reply"])

    def test_limits_name_themselves_honestly(self):
        """The list holds what the YAML lists, caps and notes, so it is titled
        and counted that way: Read-only analytics is a note, not a cap."""
        tree = check.parse(check.built_file(self.build, ROUTE)).main
        details = next(d for d in check.walk(tree) if d["attrs"].get("data-pp-kind") == "limits")
        summary = " ".join(check.text(details).split())
        self.assertIn("Limits and notes", summary)
        self.assertIn("4 of 5 actions", summary)

    def test_a_picked_type_returns_the_default_illustration(self):
        fx = Fixture()
        self.addCleanup(fx.close)
        fx.edit(check.SCRIPT, "        restoreScenes();\n", "")
        self.assertIn("after a preview leaves", self.problems(self.build, fx.root))

    def test_clicking_the_checked_radio_restores_the_default_scene(self):
        """A real browser fires click but no change for the checked radio; the
        harness now does the same, so the change handler alone cannot pass."""
        tree = check.parse(check.built_file(self.build, ROUTE)).main
        rec = json.loads((ROOT / "data/platform_pages.json").read_text(encoding="utf-8"))["pages"][0]
        ex = rec["examples"]["items"][-1]
        other = next(a["id"] for a in rec["activities"] if a["id"] != ex["activity"])
        runs = check.run_harness(tree, {"steps": [{"try": ex["id"]}, {"choose": ex["activity"]}]}, ROOT)
        self.assertTrue(runs[1]["samples"][ex["activity"]]["sampleShown"])
        self.assertFalse(runs[2]["samples"][ex["activity"]]["sampleShown"])
        self.assertEqual(runs[2]["announceWrites"] - runs[1]["announceWrites"], 1)
        # Native selection of another radio, by pointer or arrow key, still works once.
        for step in ({"choose": other}, {"key": other}):
            runs = check.run_harness(tree, {"steps": [{"try": ex["id"]}, step]}, ROOT)
            self.assertEqual(runs[2]["checked"], [other])
            self.assertFalse(runs[2]["samples"][ex["activity"]]["sampleShown"])
            self.assertEqual(runs[2]["announceWrites"] - runs[1]["announceWrites"], 1)
        # The harness fires no change for the checked radio.
        idle = check.run_harness(tree, {"steps": [{"choose": rec["activities"][0]["id"]}]}, ROOT)
        self.assertEqual(idle[1]["announceWrites"], idle[0]["announceWrites"])

    def test_a_script_that_ignores_the_checked_radio_is_caught(self):
        fx = Fixture()
        self.addCleanup(fx.close)
        fx.edit(check.SCRIPT, 'if (!input.checked || root.getAttribute("data-pp-type") !== input.value) return;', "return;")
        self.assertIn("the checked", self.problems(self.build, fx.root))

    def test_a_script_that_announces_twice_is_caught(self):
        fx = Fixture()
        self.addCleanup(fx.close)
        fx.edit(check.SCRIPT, 'if (!input.checked || root.getAttribute("data-pp-type") !== input.value) return;', "if (!input.checked) return;")
        self.assertIn("announced 2 time(s)", self.problems(self.build, fx.root))

    def test_scrolling_the_rail_announces_nothing(self):
        fx = Fixture()
        self.addCleanup(fx.close)
        fx.edit(check.SCRIPT, "if (count) count.textContent = describe(inView());",
                "if (count) count.textContent = describe(inView()); if (announce) announce.textContent = describe(inView());")
        self.assertIn("scrolling the rail announced", self.problems(self.build, fx.root))

    def test_a_button_press_announces_where_the_rail_lands(self):
        fx = Fixture()
        self.addCleanup(fx.close)
        fx.edit(check.SCRIPT, 'if (announce) announce.textContent = "Showing examples " + describe(inView(left));', "")
        self.assertIn("paging forward announced", self.problems(self.build, fx.root))

    def test_the_rail_count_is_never_live(self):
        build = self.copy()
        self.edit_page(build, "data-pp-rail-count>", 'data-pp-rail-count aria-live="polite">')
        self.assertIn("the rail count is a live region", self.problems(build))


if __name__ == "__main__":
    unittest.main()
