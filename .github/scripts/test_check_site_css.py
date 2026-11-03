"""Unit tests for check_site_css.py (the flat Signal rules, #421)."""

import tempfile
import unittest
from pathlib import Path

import check_site_css as check


def rules(css: str) -> list[str]:
    """Rule names the checker reports for a stylesheet snippet."""
    return [f.rule for f in check.check_decls(check.parse(css, "t.css"))]


class FontFloor(unittest.TestCase):
    def test_mixed_case_under_13px_fails(self):
        self.assertEqual(rules(".a { font-size: 12px; }"), ["font-size-floor"])

    def test_rem_under_13px_fails(self):
        self.assertEqual(rules(".a { font-size: 0.8rem; }"), ["font-size-floor"])
        self.assertEqual(rules(".a { font-size: 0.8125rem; }"), [])

    def test_font_shorthand_size_is_read(self):
        self.assertEqual(rules(".a { font: 500 11px var(--font-mono); }"), ["font-size-floor"])
        self.assertEqual(rules(".a { font: 500 12px/1 var(--font-sans); }"), ["font-size-floor"])
        self.assertEqual(rules(".a { font: 600 14.5px var(--font-sans); }"), [])
        self.assertEqual(rules(".a { font: 500 11px var(--font-mono); text-transform: uppercase; }"), [])

    def test_13px_passes(self):
        self.assertEqual(rules(".a { font-size: 13px; }"), [])

    def test_uppercase_label_under_13px_passes(self):
        self.assertEqual(rules(".a { font-size: 11px; text-transform: uppercase; }"), [])

    def test_uppercase_must_be_in_the_same_rule(self):
        css = ".a { text-transform: uppercase; }\n.b { font-size: 11px; }"
        self.assertEqual(rules(css), ["font-size-floor"])

    def test_miniature_interface_art_is_exempt(self):
        self.assertEqual(rules(".ia-panel { font-size: 9px; }"), [])
        self.assertEqual(rules(".iface-art .ia-chip-name { font-size: 7px; }"), [])

    def test_nested_scss_block_keeps_its_own_uppercase(self):
        scss = ".a {\n  text-transform: uppercase;\n  .b { font-size: 11px; }\n}"
        self.assertEqual(rules(scss), ["font-size-floor"])


class EdgesAndInsets(unittest.TestCase):
    def test_coloured_left_border_fails(self):
        self.assertEqual(rules(".a { border-left: 2px solid var(--teal); }"), ["coloured-edge"])

    def test_coloured_border_colour_fails(self):
        self.assertEqual(rules(".a { border-left-color: var(--teal); }"), ["coloured-edge"])

    def test_neutral_column_rule_passes(self):
        self.assertEqual(rules(".a { border-left: var(--stroke-hairline) solid var(--line); }"), [])
        self.assertEqual(rules(".a { border-left: 1px solid rgba(255, 255, 255, 0.14); }"), [])
        self.assertEqual(rules(".a { border-left: 0; }"), [])

    def test_hex_accent_fails_and_grey_passes(self):
        self.assertEqual(rules(".a { border-right: 1px solid #00B39F; }"), ["coloured-edge"])
        self.assertEqual(rules(".a { border-right: 1px solid #D5DEDD; }"), [])

    def test_selected_tab_mark_is_structure(self):
        self.assertEqual(rules('.tabs-tab[aria-selected="true"] { border-bottom-color: var(--teal); }'), [])
        self.assertEqual(rules(".category-tab { border-bottom-color: var(--teal); }"), [])
        self.assertEqual(rules(".table td { border-bottom-color: var(--teal); }"), ["coloured-edge"])

    def test_checkmark_is_structure(self):
        css = ".li::before { border-left: 2px solid var(--teal); border-bottom: 2px solid var(--teal); transform: rotate(-45deg); }"
        self.assertEqual(rules(css), [])

    def test_single_edge_inset_fails(self):
        self.assertEqual(rules(".a { box-shadow: inset 0 1px 0 0 var(--white); }"), ["single-edge-inset"])
        self.assertEqual(rules(".a { box-shadow: inset 0 -1px 0 var(--line); }"), ["single-edge-inset"])

    def test_even_inset_ring_passes(self):
        self.assertEqual(rules(".a { box-shadow: inset 0 0 0 1px var(--line); }"), [])


class Glass(unittest.TestCase):
    def test_backdrop_blur_fails(self):
        self.assertEqual(rules(".a { backdrop-filter: blur(12px); }"), ["glass-material"])
        self.assertEqual(rules(".a { -webkit-backdrop-filter: var(--card-blur, none); }"), ["glass-material"])

    def test_backdrop_none_passes(self):
        self.assertEqual(rules(".a { backdrop-filter: none; }"), [])


class Parsing(unittest.TestCase):
    def test_comments_are_ignored(self):
        self.assertEqual(rules("/* .a { font-size: 9px; } */ .b { color: red; }"), [])
        self.assertEqual(rules("// border-left: 2px solid var(--teal);\n.b { color: red; }"), [])

    def test_check_files_reads_every_site_stylesheet(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "assets" / "css").mkdir(parents=True)
            (root / "assets" / "css" / "site.css").write_text(".a { font-size: 9px; }\n", encoding="utf-8")
            (root / "assets" / "css" / "home-signal.css").write_text(".a { font-size: 9px; }\n", encoding="utf-8")
            paths = sorted((root / "assets" / "css").glob("*.css"))
            findings = check.check_files(paths, root)
            self.assertEqual(sorted(f.path for f in findings), ["assets/css/home-signal.css", "assets/css/site.css"])
            self.assertEqual(findings[0].line, 1)


if __name__ == "__main__":
    unittest.main()
