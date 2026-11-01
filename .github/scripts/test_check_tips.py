import tempfile
import unittest
from pathlib import Path

import check_tips as check

TIP = """---
title: "A tip"
summary: "Summary."
date: 2026-10-26
author: "Blowhorn team"
layout: article
tags: ["tips"]
column: "boot-camp"
tipOrder: 1
video:
  mp4: "assets/video/tips/x.mp4"
  webm: "assets/video/tips/x.webm"
  poster: "assets/video/tips/x-poster.webp"
  duration: "0:20"
---

Body.
"""

ARTICLE = """---
title: "An article"
summary: "Summary."
date: 2026-10-14
author: "Blowhorn team"
layout: article
tags: ["in-product-intelligence"]
column: "from-the-field"
---

Body.
"""


class CheckTipsTest(unittest.TestCase):
    def run_on(self, files):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, body in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(body)
            return check.main(["check", str(root)])

    def base(self):
        return {
            "content/en/resources/articles/tip-x.md": TIP,
            "content/en/resources/articles/article-y.md": ARTICLE,
            "static/assets/video/tips/x.mp4": "",
            "static/assets/video/tips/x.webm": "",
            "static/assets/video/tips/x-poster.webp": "",
        }

    def test_valid_content_passes(self):
        self.assertEqual(self.run_on(self.base()), 0)

    def test_tip_without_video_fails(self):
        files = self.base()
        files["content/en/resources/articles/tip-x.md"] = TIP.split("video:")[0] + "\n---\n\nBody.\n"
        self.assertEqual(self.run_on(files), 1)

    def test_tip_with_missing_video_file_fails(self):
        files = self.base()
        del files["static/assets/video/tips/x.webm"]
        self.assertEqual(self.run_on(files), 1)

    def test_article_without_column_fails(self):
        files = self.base()
        files["content/en/resources/articles/article-y.md"] = ARTICLE.replace('column: "from-the-field"\n', "")
        self.assertEqual(self.run_on(files), 1)

    def test_tip_with_unknown_column_fails(self):
        files = self.base()
        files["content/en/resources/articles/tip-x.md"] = TIP.replace("boot-camp", "barracks")
        self.assertEqual(self.run_on(files), 1)

    def test_duplicate_tip_order_fails(self):
        files = self.base()
        files["content/en/resources/articles/tip-z.md"] = TIP.replace('"A tip"', '"Another tip"')
        self.assertEqual(self.run_on(files), 1)

    def test_draft_tip_is_skipped(self):
        files = self.base()
        files["content/en/resources/articles/tip-x.md"] = "---\ndraft: true\ntags: [\"tips\"]\n---\n\nBody.\n"
        self.assertEqual(self.run_on(files), 0)


if __name__ == "__main__":
    unittest.main()
