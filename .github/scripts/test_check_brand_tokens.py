#!/usr/bin/env python3
"""check_brand_tokens.py: validate/generate brand tokens against the product.

Run with `make test-scripts` (CI runs it too).
"""

import copy
import json
import tempfile
import unittest
from pathlib import Path

import check_brand_tokens as check

PRODUCT_TOKENS = {
    "name": "Blowhorn",
    "version": 1,
    "color": {
        "themes": [{"id": "light", "name": "Light"}, {"id": "dark", "name": "Dark"}],
        "tokens": [
            {"name": "teal", "value": "#00B39F", "usage": "primary brand fill"},
            {"name": "teal-bright", "value": "#00D3A9", "usage": "highlights"},
            {"name": "near-black", "value": "#1E2117", "usage": "deepest ink"},
            {"name": "on-yellow", "value": "#1E2117", "usage": "text on yellow"},
        ],
    },
    "type": {
        "fonts": [
            {"family": "Instrument Sans", "file": "f.woff2", "weight": "400", "style": "normal"},
            {"family": "JetBrains Mono", "file": "f.woff2", "weight": "400", "style": "normal"},
        ],
        "families": {
            "display": "\"Instrument Sans\", sans-serif",
            "sans": "\"Instrument Sans\", sans-serif",
            "mono": "\"JetBrains Mono\", monospace",
        },
        "groups": [
            {
                "name": "Display",
                "family": "display",
                "styles": [
                    {"name": "display-xl", "fontSize": "72px", "lineHeight": "72px"},
                    {"name": "h1", "fontSize": "40px", "lineHeight": "46px"},
                ],
            },
            {
                "name": "Text",
                "family": "sans",
                "styles": [
                    {"name": "body-lg", "fontSize": "18px", "lineHeight": "28px"},
                    {"name": "body", "fontSize": "16px", "lineHeight": "24px"},
                    {"name": "ui", "fontSize": "14px", "lineHeight": "20px"},
                    {"name": "caption", "fontSize": "12px", "lineHeight": "16px"},
                ],
            },
            {
                "name": "Mono",
                "family": "mono",
                "styles": [
                    {"name": "code", "fontSize": "13px", "lineHeight": "20px"},
                    {"name": "label", "fontSize": "11px", "lineHeight": "16px"},
                ],
            },
        ],
    },
    "spacing": {
        "tokens": [
            {"name": "space-1", "value": "4px", "usage": "icon gaps"},
            {"name": "space-4", "value": "16px", "usage": "card padding"},
        ],
    },
    "radius": {
        "tokens": [
            {"name": "radius-md", "value": "10px", "usage": "buttons"},
            {"name": "radius-lg", "value": "16px", "usage": "cards"},
        ],
    },
    "shadow": {
        "tokens": [
            {"name": "shadow-soft", "value": {"light": "0 8px 24px rgba(0,0,0,0.12)"}, "usage": "menus"},
        ],
    },
    "stroke": {
        "tokens": [
            {"name": "stroke-hairline", "value": "1px", "usage": "dividers"},
        ],
    },
}

SITE_ONLY = {
    "video-matte": {"value": "#0F172A", "usage": "video background"},
    "on-matte": {"value": "#FFFFFF", "usage": "text on matte"},
    "on-teal-deep": {"value": "#FFFFFF", "usage": "text on teal-deep"},
    "teal-glow": {"value": "#40E0D0", "usage": "glow accent"},
    "status-bg": {"value": "#F4F7F6", "usage": "status background"},
    "status-ink": {"value": "#1E2117", "usage": "text on status"},
    "mark-claude": {"value": "#D97706", "usage": "Claude mark"},
    "mark-deepseek": {"value": "#0066CC", "usage": "DeepSeek mark"},
    "mark-openai": {"value": "#00A86E", "usage": "OpenAI mark"},
    "proof-flag-bg": {"value": "#FFF6E0", "usage": "proof flag bg"},
    "proof-flag-ink": {"value": "#1E2117", "usage": "text on proof flag"},
    "print-ink": {"value": "#1E2117", "usage": "print ink"},
    "ai-soon-ink": {"value": "#5B6A70", "usage": "AI soon muted"},
}

CSS_MATCHING = """
.ui { font-size: 14px; line-height: 20px; font-weight: 500; }
.caption { font-size: 12px; line-height: 16px; font-weight: 500; }
.label { font-size: 11px; line-height: 16px; font-weight: 500; }
"""

CSS_MISMATCH = """
.ui { font-size: 16px; line-height: 24px; font-weight: 500; }
.caption { font-size: 12px; line-height: 16px; font-weight: 500; }
.label { font-size: 11px; line-height: 16px; font-weight: 500; }
"""


def site_with_site_only_colours():
    return {
        "name": "Blowhorn",
        "version": 1,
        "color": {
            "themes": PRODUCT_TOKENS["color"]["themes"],
            "tokens": PRODUCT_TOKENS["color"]["tokens"]
            + [{"name": n, "value": v["value"], "usage": v["usage"]}
               for n, v in SITE_ONLY.items()],
        },
        "type": PRODUCT_TOKENS["type"],
        "spacing": PRODUCT_TOKENS["spacing"],
        "radius": PRODUCT_TOKENS["radius"],
        "shadow": PRODUCT_TOKENS["shadow"],
        "stroke": PRODUCT_TOKENS["stroke"],
    }


def make_tmp(products=None, site_tokens=None, css=None, extensions=None):
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    bh = root / "blowhorn"
    (bh / "marketing" / "brand").mkdir(parents=True)
    if products is not None:
        (bh / "marketing" / "brand" / "tokens.json").write_text(
            json.dumps(products), encoding="utf-8"
        )
    site = root / "site"
    site.mkdir()
    if site_tokens is not None:
        (site / "tokens.json").write_text(json.dumps(site_tokens), encoding="utf-8")
    if css is not None:
        (site / "site.css").write_text(css, encoding="utf-8")
    if extensions is not None:
        (root / "extensions.json").write_text(json.dumps(extensions), encoding="utf-8")
    return tmp, bh, site, root


class ValidatePasses(unittest.TestCase):
    def test_product_prefix_and_css_match(self):
        tmp, bh, site, root = make_tmp(
            products=PRODUCT_TOKENS,
            site_tokens=site_with_site_only_colours(),
            css=CSS_MATCHING,
            extensions={"color": SITE_ONLY},
        )
        try:
            problems = check.validate(bh, site / "tokens.json", site / "site.css", root / "extensions.json")
        finally:
            tmp.cleanup()
        self.assertEqual(problems, [])

    def test_site_only_colours_after_product_prefix_pass(self):
        tmp, bh, site, root = make_tmp(
            products=PRODUCT_TOKENS,
            site_tokens=site_with_site_only_colours(),
            css=CSS_MATCHING,
            extensions={"color": SITE_ONLY},
        )
        try:
            problems = check.validate(bh, site / "tokens.json", site / "site.css", root / "extensions.json")
        finally:
            tmp.cleanup()
        self.assertEqual(problems, [])


class ValidateFails(unittest.TestCase):
    def test_product_drift_fails(self):
        drifted = copy.deepcopy(PRODUCT_TOKENS)
        drifted["color"]["tokens"][0]["usage"] = "changed usage"
        tmp, bh, site, root = make_tmp(
            products=drifted,
            site_tokens=site_with_site_only_colours(),
            css=CSS_MATCHING,
            extensions={"color": SITE_ONLY},
        )
        try:
            problems = check.validate(bh, site / "tokens.json", site / "site.css", root / "extensions.json")
        finally:
            tmp.cleanup()
        self.assertNotEqual(problems, [])
        self.assertTrue(any("entry 0 differs" in p for p in problems))

    def test_unnamed_site_only_colour_fails(self):
        tokens = site_with_site_only_colours()
        tokens["color"]["tokens"].append(
            {"name": "rogue-colour", "value": "#BADA55", "usage": "x"}
        )
        tmp, bh, site, root = make_tmp(
            products=PRODUCT_TOKENS,
            site_tokens=tokens,
            css=CSS_MATCHING,
            extensions={"color": SITE_ONLY},
        )
        try:
            problems = check.validate(bh, site / "tokens.json", site / "site.css", root / "extensions.json")
        finally:
            tmp.cleanup()
        self.assertNotEqual(problems, [])
        self.assertTrue(any("rogue-colour" in p for p in problems))

    def test_missing_site_only_colour_fails(self):
        tokens = site_with_site_only_colours()
        tokens["color"]["tokens"] = [
            t for t in tokens["color"]["tokens"] if t["name"] != "video-matte"
        ]
        tmp, bh, site, root = make_tmp(
            products=PRODUCT_TOKENS,
            site_tokens=tokens,
            css=CSS_MATCHING,
            extensions={"color": SITE_ONLY},
        )
        try:
            problems = check.validate(bh, site / "tokens.json", site / "site.css", root / "extensions.json")
        finally:
            tmp.cleanup()
        self.assertNotEqual(problems, [])
        self.assertTrue(any("video-matte" in p for p in problems))

    def test_css_mismatch_fails(self):
        tmp, bh, site, root = make_tmp(
            products=PRODUCT_TOKENS,
            site_tokens=site_with_site_only_colours(),
            css=CSS_MISMATCH,
            extensions={"color": SITE_ONLY},
        )
        try:
            problems = check.validate(bh, site / "tokens.json", site / "site.css", root / "extensions.json")
        finally:
            tmp.cleanup()
        self.assertNotEqual(problems, [])
        self.assertTrue(any(".ui" in p and "16px" in p for p in problems))


class GenerateWrites(unittest.TestCase):
    def test_generate_merges_product_and_extensions(self):
        tmp, bh, site, root = make_tmp(
            products=PRODUCT_TOKENS,
            extensions={"color": SITE_ONLY},
        )
        try:
            rc = check.generate(bh, site / "tokens.json", root / "extensions.json")
            written = json.loads((site / "tokens.json").read_text(encoding="utf-8"))
        finally:
            tmp.cleanup()
        self.assertEqual(rc, 0)
        names = [t["name"] for t in written["color"]["tokens"]]
        product_names = [t["name"] for t in PRODUCT_TOKENS["color"]["tokens"]]
        self.assertEqual(names[:len(product_names)], product_names)
        for n in SITE_ONLY:
            self.assertIn(n, names)


class NoBlowhornDir(unittest.TestCase):
    def test_missing_blowhorn_dir_fails(self):
        rc = check.main(["/nonexistent/blowhorn", "validate"])
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
