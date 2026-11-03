"""Unit tests for check_casing.py (sentence case for headings, buttons and nav, #421)."""

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import check_casing as check


def flagged(html: str, path: str = "page/index.html") -> list[str]:
    return [f"{f.kind}: {f.text}" for f in check.check_html(path, html)]


class Headings(unittest.TestCase):
    def test_title_case_heading_fails(self):
        self.assertEqual(flagged("<h2>Frequently Asked Questions</h2>"),
                         ["h2: Frequently Asked Questions"])

    def test_sentence_case_passes(self):
        self.assertEqual(flagged("<h2>Questions</h2>"), [])
        self.assertEqual(flagged("<h1>This page went out of range.</h1>"), [])

    def test_a_sentence_start_after_a_stop_passes(self):
        self.assertEqual(flagged("<h2>Not a bot. You, at full volume.</h2>"), [])
        self.assertEqual(flagged("<h3>Step 1: Open Blowhorn once</h3>"), [])

    def test_quoted_and_bracketed_starts_pass(self):
        self.assertEqual(flagged('<h3>"Bypass the limits"</h3>'), [])
        self.assertEqual(flagged("<h3>(Recommended) Set up profiles</h3>"), [])

    def test_aria_hidden_text_is_not_read(self):
        self.assertEqual(flagged('<h2><span aria-hidden="true">Big Title Here</span>Questions</h2>'), [])

    def test_code_is_not_read(self):
        self.assertEqual(flagged("<h3>Run <code>Do This Thing</code></h3>"), [])


class Names(unittest.TestCase):
    def test_brand_and_product_names_keep_their_capitals(self):
        self.assertEqual(flagged("<h2>Sign in to Blowhorn</h2>"), [])
        self.assertEqual(flagged("<h2>What Claude Code runs</h2>"), [])
        self.assertEqual(flagged("<h3>Google Analytics</h3>"), [])
        self.assertEqual(flagged("<h2>Blowhorn for DevRel</h2>"), [])

    def test_acronyms_and_single_letters_pass(self):
        self.assertEqual(flagged("<h3>Official APIs</h3>"), [])
        self.assertEqual(flagged("<h2>Use the CLI</h2>"), [])
        self.assertEqual(flagged("<h3>Am I a Bot?</h3>"), [])

    def test_a_word_with_a_capital_inside_is_a_brand(self):
        self.assertEqual(flagged("<h3>Choose AdsPower if</h3>"), [])


class Buttons(unittest.TestCase):
    def test_title_case_button_fails(self):
        self.assertEqual(flagged("<button>Get Started Free</button>"), ["button: Get Started Free"])

    def test_button_class_link_is_a_button(self):
        self.assertEqual(flagged('<a class="button button-primary" href="/">Start Free Trial</a>'),
                         ["button: Start Free Trial"])

    def test_sentence_case_button_passes(self):
        self.assertEqual(flagged("<button>Add to Chrome</button>"), [])
        self.assertEqual(flagged("<button>Back to the home page</button>"), [])


class NavLinks(unittest.TestCase):
    def test_title_case_nav_link_fails(self):
        self.assertEqual(flagged('<nav><a href="/legal/">Trust Center</a></nav>'), ["nav link: Trust Center"])

    def test_menu_card_reads_as_its_title(self):
        html = ('<nav><a class="mm-link" href="/major/"><span class="mm-link-title">Meet major</span>'
                '<span class="mm-link-desc">Our Mascot and his troops</span></a></nav>')
        self.assertEqual(flagged(html), [])

    def test_text_outside_nav_is_not_a_nav_link(self):
        self.assertEqual(flagged('<p><a href="/x/">Trust Center</a></p>'), [])


class Scope(unittest.TestCase):
    def test_docs_and_compare_pages_are_not_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in ("docs/guide/index.html", "compare/buffer/index.html", "pricing/index.html"):
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_text("<h2>Frequently Asked Questions</h2>", encoding="utf-8")
            out = io.StringIO()
            with redirect_stdout(out), redirect_stderr(io.StringIO()):
                status = check.main(["check_casing.py", str(root)])
            self.assertEqual(status, 1)
            self.assertIn("pricing/index.html:1: h2 is Title Case", out.getvalue())
            self.assertNotIn("docs/", out.getvalue())
            self.assertNotIn("compare/", out.getvalue())

    def test_missing_build_dir_fails(self):
        with redirect_stderr(io.StringIO()):
            self.assertEqual(check.main(["check_casing.py", "/nonexistent-build-dir"]), 1)


if __name__ == "__main__":
    unittest.main()
