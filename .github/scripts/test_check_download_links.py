import tempfile
import unittest
from pathlib import Path

import check_download_links as check

LATEST = "https://github.com/blowhorn-ai/blowhorn-site/releases/latest/download/Blowhorn-mac.dmg"
ALIAS = "https://github.com/blowhorn-ai/blowhorn-site/releases/download/v1.27.3/Blowhorn-mac.dmg"
PINNED = "https://github.com/blowhorn-ai/blowhorn-site/releases/download/v1.27.3/Blowhorn-1.27.3-mac-universal.dmg"


class CheckDownloadLinksTest(unittest.TestCase):
    def run_on(self, files):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, body in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(body)
            return check.main(["check", str(root)])

    def test_pinned_links_pass(self):
        self.assertEqual(self.run_on({"download/index.html": f'<a href="{PINNED}">Download</a>'}), 0)

    def test_unversioned_alias_link_fails(self):
        self.assertEqual(self.run_on({"download/index.html": f'<a href="{ALIAS}">Download</a>'}), 1)

    def test_latest_link_in_a_page_fails(self):
        self.assertEqual(self.run_on({"docs/install/index.html": f'<a href="{LATEST}">dmg</a>'}), 1)

    def test_latest_url_in_json_ld_fails(self):
        self.assertEqual(self.run_on({"index.html": f'<script type="application/ld+json">{{"downloadUrl":"{LATEST}"}}</script>'}), 1)

    def test_latest_url_in_a_script_fails(self):
        self.assertEqual(self.run_on({"js/main.js": f'location.href = "{LATEST}";'}), 1)

    def test_prose_about_the_hazard_passes(self):
        self.assertEqual(self.run_on({"docs/index.html": "<p>/releases/latest/download resolves to an axi release.</p>"}), 0)


if __name__ == "__main__":
    unittest.main()
