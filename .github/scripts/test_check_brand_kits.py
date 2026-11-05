#!/usr/bin/env python3
"""The Brand page states each kit's real size, and links both kits.

Run with `make test-scripts` (CI runs it too).
"""

import tempfile
import unittest
from pathlib import Path

import check_brand_kits as check

MB = 1024 * 1024


def downloads(full="29 MB", logos="2.0 MB"):
    return (
        '<main><a class="button" href="/brand/blowhorn-brand-kit.zip" download>Download full brand kit</a>'
        f'<p class="caption muted">ZIP, {full}. Logos, colors, type.</p>'
        '<a class="button" href="/brand/blowhorn-logo-kit.zip" download>Download logos only</a>'
        f'<p class="caption muted">ZIP, {logos}. Logos, icons and wordmarks.</p></main>'
    )


class TheKitSizesMatchTheFiles(unittest.TestCase):
    def build(self, html, full_bytes=int(28.7 * MB), logo_bytes=int(1.99 * MB)):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "brand").mkdir()
        (root / "brand" / "index.html").write_text(html, encoding="utf-8")
        if full_bytes is not None:
            (root / "brand" / "blowhorn-brand-kit.zip").write_bytes(b"\0" * full_bytes)
        if logo_bytes is not None:
            (root / "brand" / "blowhorn-logo-kit.zip").write_bytes(b"\0" * logo_bytes)
        return root

    def test_true_sizes_pass(self):
        self.assertEqual(check.check(self.build(downloads())), [])

    def test_a_stale_size_fails(self):
        errors = check.check(self.build(downloads(full="5 MB")))
        self.assertEqual(len(errors), 1)
        self.assertIn("says 5 MB, the file is 29 MB", errors[0])

    def test_a_missing_zip_fails(self):
        errors = check.check(self.build(downloads(), logo_bytes=None))
        self.assertTrue(any("does not publish" in e for e in errors))

    def test_a_kit_without_a_link_fails(self):
        html = downloads().split('<a class="button" href="/brand/blowhorn-logo-kit.zip"')[0] + "</main>"
        errors = check.check(self.build(html))
        self.assertTrue(any("no download link for brand/blowhorn-logo-kit.zip" in e for e in errors))

    def test_a_link_without_a_caption_fails(self):
        html = downloads().replace("ZIP, 2.0 MB.", "Logos.")
        errors = check.check(self.build(html))
        self.assertTrue(any("has no" in e for e in errors))

    def test_labels_round_like_the_page(self):
        self.assertEqual(check.size_label(int(1.99 * MB)), "2.0 MB")
        self.assertEqual(check.size_label(int(9.4 * MB)), "9.4 MB")
        self.assertEqual(check.size_label(int(9.97 * MB)), "10 MB")
        self.assertEqual(check.size_label(int(28.7 * MB)), "29 MB")


if __name__ == "__main__":
    unittest.main()
