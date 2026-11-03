import tempfile
import unittest
from pathlib import Path

import check_install_cta as check

PRIMARY = '<a class="button button-primary" href="/download/">Download</a>'
SECONDARY = '<a class="button button-secondary" href="/download/">Download</a>'


def page(main="", outside=""):
    return f"<html><body>{outside}<main id=\"main\">{main}</main></body></html>"


class PrimaryPerViewTest(unittest.TestCase):
    def problems(self, html):
        return check.problems_in("for/marketing/index.html", html)

    def test_one_primary_in_main_passes(self):
        self.assertEqual(self.problems(page(PRIMARY + SECONDARY)), [])

    def test_two_primaries_in_main_fail(self):
        problems = self.problems(page(PRIMARY + '<a class="button button-primary" href="/x/">See it</a>'))
        self.assertEqual(len(problems), 1)
        self.assertIn("2 primary buttons in main", problems[0])
        self.assertIn("'See it'", problems[0])

    def test_header_and_footer_primaries_are_not_counted(self):
        html = page(PRIMARY, outside='<header><a class="button button-primary" href="/download/">Download</a></header>')
        self.assertEqual(self.problems(html), [])

    def test_form_submit_buttons_are_not_counted(self):
        form = '<form><button class="button button-primary" type="submit">Subscribe</button></form>'
        self.assertEqual(self.problems(page(PRIMARY + form)), [])

    def test_a_form_primary_does_not_count_toward_the_limit(self):
        form = '<form><button class="button button-primary" type="submit">Subscribe</button></form>'
        self.assertEqual(self.problems(page(form + PRIMARY + PRIMARY)), [
            "for/marketing/index.html: 2 primary buttons in main ('Download', 'Download'); a view has one"
        ])

    def test_no_primary_passes(self):
        self.assertEqual(self.problems(page(SECONDARY)), [])


class OldLabelTest(unittest.TestCase):
    def problems(self, html):
        return check.problems_in("pricing/index.html", html)

    def test_old_label_on_a_secondary_link_fails(self):
        problems = self.problems(page('<a class="button" href="/download/">Download free</a>'))
        self.assertEqual(len(problems), 1)
        self.assertIn("'Download free'", problems[0])

    def test_old_label_in_the_header_fails(self):
        html = page(outside='<header><a href="/download/">Get Blowhorn</a></header>')
        self.assertIn("'Get Blowhorn'", self.problems(html)[0])

    def test_enlist_a_computer_fails(self):
        problems = self.problems(page('<a class="button" href="/download/">Enlist a computer</a>'))
        self.assertEqual(len(problems), 1)
        self.assertIn("'Enlist a computer'", problems[0])

    def test_install_the_cli_is_fine_as_a_secondary(self):
        self.assertEqual(self.problems(page('<a class="button button-secondary" href="/docs/">Install the CLI</a>')), [])

    def test_install_the_cli_as_a_primary_fails(self):
        problems = self.problems(page('<a class="button button-primary" href="/docs/">Install the CLI</a>'))
        self.assertEqual(len(problems), 1)
        self.assertIn("'Install the CLI'", problems[0])

    def test_label_text_is_whitespace_normalised(self):
        html = page('<a href="/download/">\n    Download   free\n</a>')
        self.assertEqual(len(self.problems(html)), 1)

    def test_the_download_label_passes(self):
        self.assertEqual(self.problems(page(PRIMARY + SECONDARY)), [])


class CheckTreeTest(unittest.TestCase):
    def run_on(self, files):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, body in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(body, encoding="utf-8")
            return check.check(root)

    def test_home_is_checked(self):
        problems = self.run_on({"index.html": page(PRIMARY + PRIMARY)})
        self.assertEqual(len(problems), 1)
        self.assertTrue(problems[0].startswith("index.html:"))

    def test_docs_pages_are_skipped(self):
        self.assertEqual(self.run_on({"docs/reference/cli/index.html": page(PRIMARY + PRIMARY)}), [])

    def test_other_pages_are_checked(self):
        problems = self.run_on({
            "ai/index.html": page(PRIMARY + PRIMARY),
            "download/index.html": page(PRIMARY),
        })
        self.assertEqual(len(problems), 1)
        self.assertTrue(problems[0].startswith("ai/index.html:"))

    def test_main_exits_zero_on_a_clean_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "download").mkdir()
            Path(tmp, "download", "index.html").write_text(page(PRIMARY + SECONDARY), encoding="utf-8")
            self.assertEqual(check.main(["check", tmp]), 0)

    def test_main_exits_one_on_a_violation(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "ai").mkdir()
            Path(tmp, "ai", "index.html").write_text(page(PRIMARY + PRIMARY), encoding="utf-8")
            self.assertEqual(check.main(["check", tmp]), 1)


if __name__ == "__main__":
    unittest.main()
