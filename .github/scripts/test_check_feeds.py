import tempfile
import unittest
from pathlib import Path

import check_feeds as check

ITEM = """<item><title>Post</title><link>https://blowhorn.ai/resources/articles/x/</link>
<guid>https://blowhorn.ai/resources/articles/x/</guid>
<pubDate>Wed, 28 Oct 2026 05:00:00 +0000</pubDate>
<description>A summary.</description><category>{cat}</category><category>column:boot-camp</category></item>"""


BASE = "https://blowhorn.ai/"


def feed(items, cat="in-product-intelligence", path="resources/feed.xml", link="resources/", self_href=None):
    body = "".join(ITEM.format(cat=c) for c in items) if isinstance(items, list) else ITEM.format(cat=cat)
    return (
        '<?xml version="1.0" encoding="utf-8"?><rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">'
        f'<channel><title>t</title><link>{BASE}{link}</link>'
        f'<atom:link href="{self_href or BASE + path}" rel="self" type="application/rss+xml"/>{body}</channel></rss>'
    )


VALID = {
    "resources/feed.xml": feed(1),
    "resources/tags/in-product-intelligence/feed.xml": feed(
        1, path="resources/tags/in-product-intelligence/feed.xml", link="tags/in-product-intelligence/"
    ),
    "resources/index.html": "",
    "tags/in-product-intelligence/index.html": "",
}


class CheckFeedsTest(unittest.TestCase):
    def run_on(self, files):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, body in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(body)
            return check.main(["check", str(root)])

    def test_valid_feeds_pass(self):
        self.assertEqual(self.run_on(VALID), 0)

    def test_missing_contract_feed_fails(self):
        files = {"resources/feed.xml": feed(1)}
        self.assertEqual(self.run_on(files), 1)

    def test_missing_resources_feed_fails(self):
        files = {"resources/tags/in-product-intelligence/feed.xml": feed(1)}
        self.assertEqual(self.run_on(files), 1)

    def test_malformed_xml_fails(self):
        files = dict(VALID)
        files["resources/feed.xml"] = "<rss><channel><item>"
        self.assertEqual(self.run_on(files), 1)

    def test_item_missing_pubdate_fails(self):
        bad = feed(1).replace("<pubDate>Wed, 28 Oct 2026 05:00:00 +0000</pubDate>", "")
        files = dict(VALID)
        files["resources/feed.xml"] = bad
        self.assertEqual(self.run_on(files), 1)

    def test_contract_feed_rejects_other_tags(self):
        files = dict(VALID)
        files["resources/tags/in-product-intelligence/feed.xml"] = feed(["tips"])
        self.assertEqual(self.run_on(files), 1)

    def test_unparseable_pubdate_fails(self):
        bad = feed(1).replace("Wed, 28 Oct 2026 05:00:00 +0000", "last Tuesday-ish")
        files = dict(VALID)
        files["resources/tags/in-product-intelligence/feed.xml"] = bad
        self.assertEqual(self.run_on(files), 1)

    def test_wrong_self_link_fails(self):
        files = dict(VALID)
        tag = "resources/tags/in-product-intelligence/feed.xml"
        files[tag] = feed(1, link="tags/in-product-intelligence/", self_href=BASE + tag + "feed.xml")
        self.assertEqual(self.run_on(files), 1)

    def test_missing_channel_page_fails(self):
        files = dict(VALID)
        del files["tags/in-product-intelligence/index.html"]
        self.assertEqual(self.run_on(files), 1)


if __name__ == "__main__":
    unittest.main()


    def test_item_without_column_fails(self):
        files = dict(VALID)
        files["resources/feed.xml"] = feed(1).replace("<category>column:boot-camp</category>", "")
        self.assertEqual(self.run_on(files), 1)

    def test_item_with_unknown_column_fails(self):
        files = dict(VALID)
        files["resources/feed.xml"] = feed(1).replace("column:boot-camp", "column:barracks")
        self.assertEqual(self.run_on(files), 1)

    def test_item_with_two_columns_fails(self):
        files = dict(VALID)
        files["resources/feed.xml"] = feed(1).replace(
            "<category>column:boot-camp</category>",
            "<category>column:boot-camp</category><category>column:from-the-field</category>",
        )
        self.assertEqual(self.run_on(files), 1)
