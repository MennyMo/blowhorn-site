#!/usr/bin/env python3
"""Every Blowhorn Tells placement stays on its page, and every tagged Tells
link carries the UTM parameters in data/tells.json with a known placement.

Run with `make test-scripts` (CI runs it too).
"""

import json
import tempfile
import unittest
from pathlib import Path

import check_tells as check

DATA = json.loads(check.DEFAULT_DATA.read_text(encoding="utf-8"))
BASE = DATA["url"]


def link(placement, path="", **override):
    params = {
        "utm_source": DATA["utm"]["source"],
        "utm_medium": DATA["utm"]["medium"],
        "utm_campaign": DATA["utm"]["campaign"],
        "utm_content": placement,
    }
    params.update(override)
    query = "&amp;".join(f"{k}={v}" for k, v in params.items() if v is not None)
    return f'<a href="{BASE}{path}?{query}">Am I a Bot?</a>'


def page(*placements):
    return "<html><body>" + "".join(link(p) for p in placements) + "</body></html>"


def complete_site():
    return {
        "index.html": page("nav", "bar", "footer", "home"),
        "ai/index.html": page("ai"),
        "agents/index.html": page("agents"),
        "download/thanks/index.html": page("thanks"),
        "404.html": page("404", "bar"),
        "compare/index.html": page(),
        "compare/phantombuster/index.html": page("compare"),
        "docs/index.html": page("docs"),
        "docs/explanation/your-own-chrome/index.html": page("docs"),
    }


class TellsPlacements(unittest.TestCase):
    def run_check(self, pages):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        for rel, html in pages.items():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(html, encoding="utf-8")
        return check.check(root, DATA)

    def test_every_placement_present_passes(self):
        self.assertEqual(self.run_check(complete_site()), [])

    def test_a_missing_placement_fails(self):
        pages = complete_site()
        pages["index.html"] = page("nav", "bar", "footer")
        failures = self.run_check(pages)
        self.assertEqual(len(failures), 1)
        self.assertIn("utm_content=home", failures[0])

    def test_a_compare_page_without_the_callout_fails(self):
        pages = complete_site()
        pages["compare/gologin/index.html"] = page()
        failures = self.run_check(pages)
        self.assertEqual(len(failures), 1)
        self.assertIn("compare/gologin/index.html", failures[0])

    def test_the_compare_hub_needs_no_callout(self):
        pages = complete_site()
        pages["compare/index.html"] = "<html><body></body></html>"
        self.assertEqual(self.run_check(pages), [])

    def test_a_docs_page_without_the_card_fails(self):
        pages = complete_site()
        pages["docs/reference/support/index.html"] = page()
        failures = self.run_check(pages)
        self.assertEqual(len(failures), 1)
        self.assertIn("docs/reference/support/index.html", failures[0])

    def test_an_unknown_placement_fails(self):
        pages = complete_site()
        pages["ai/index.html"] = page("ai", "sidebar")
        failures = self.run_check(pages)
        self.assertEqual(len(failures), 1)
        self.assertIn("utm_content=['sidebar']", failures[0])

    def test_a_wrong_utm_value_fails(self):
        pages = complete_site()
        pages["agents/index.html"] = "<html><body>" + link("agents", utm_medium="email") + "</body></html>"
        failures = self.run_check(pages)
        self.assertTrue(any("utm_medium" in f for f in failures))

    def test_a_missing_utm_parameter_fails(self):
        pages = complete_site()
        pages["agents/index.html"] = "<html><body>" + link("agents", utm_campaign=None) + "</body></html>"
        failures = self.run_check(pages)
        self.assertTrue(any("utm_campaign" in f for f in failures))

    def test_an_extra_utm_parameter_fails(self):
        pages = complete_site()
        pages["agents/index.html"] = "<html><body>" + link("agents", utm_term="bots") + "</body></html>"
        failures = self.run_check(pages)
        self.assertTrue(any("utm_term" in f for f in failures))

    def test_untagged_prose_links_pass(self):
        pages = complete_site()
        pages["field-manual/index.html"] = f'<html><body><a href="{BASE}">Blowhorn Tells</a></body></html>'
        self.assertEqual(self.run_check(pages), [])

    def test_tells_subpages_count_for_their_placement(self):
        pages = complete_site()
        pages["agents/index.html"] = "<html><body>" + link("agents", "agents/") + "</body></html>"
        self.assertEqual(self.run_check(pages), [])

    def test_redirect_pages_are_skipped(self):
        pages = complete_site()
        pages["docs/old/index.html"] = '<html><head><meta http-equiv="refresh" content="0; url=/docs/"></head></html>'
        self.assertEqual(self.run_check(pages), [])

    def test_a_missing_required_page_fails(self):
        pages = complete_site()
        del pages["download/thanks/index.html"]
        failures = self.run_check(pages)
        self.assertEqual(failures, ["download/thanks/index.html: page is missing from the build"])


if __name__ == "__main__":
    unittest.main()
