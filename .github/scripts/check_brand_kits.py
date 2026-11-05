#!/usr/bin/env python3
"""Fail if the Brand page offers a kit zip that isn't there, or states its size wrong.

The two kits in static/brand/ are copied from the product repository's build, and
their sizes are typed into content/en/brand/_index.md by hand. This reads the
built page, pairs each .zip download with the "ZIP, <size>." caption after it, and
checks the size against the file the build published: one decimal under 10 MB,
whole MB above, in MB of 1024 x 1024 bytes.

Usage: check_brand_kits.py BUILD_DIR
"""

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

PAGE = "brand/index.html"
KITS = ("brand/blowhorn-brand-kit.zip", "brand/blowhorn-logo-kit.zip")
CAPTION = re.compile(r"^ZIP, (\d+(?:\.\d)? MB)\.")


def size_label(size_bytes):
    mb = size_bytes / (1024 * 1024)
    if round(mb, 1) < 10:
        return f"{mb:.1f} MB"
    return f"{round(mb)} MB"


class Downloads(HTMLParser):
    """Each .zip link on the page, with the size its following caption states."""

    def __init__(self):
        super().__init__()
        self.found = []  # [href, size or None]
        self._in_p = False
        self._text = ""

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href") or ""
            if href.endswith(".zip"):
                self.found.append([href, None])
        elif tag == "p":
            self._in_p, self._text = True, ""

    def handle_data(self, data):
        if self._in_p:
            self._text += data

    def handle_endtag(self, tag):
        if tag != "p" or not self._in_p:
            return
        self._in_p = False
        match = CAPTION.match(" ".join(self._text.split()))
        if match and self.found and self.found[-1][1] is None:
            self.found[-1][1] = match.group(1)


def check(build_dir):
    build_dir = Path(build_dir)
    errors = []
    page = build_dir / PAGE
    if not page.is_file():
        return [f"{PAGE}: not built"]
    parser = Downloads()
    parser.feed(page.read_text(encoding="utf-8"))
    offered = set()
    for href, stated in parser.found:
        rel = re.sub(r"^(?:https?://[^/]+)?/", "", href)
        offered.add(rel)
        path = build_dir / rel
        if not path.is_file():
            errors.append(f"{PAGE}: links {href}, which the build does not publish")
            continue
        if stated is None:
            errors.append(f"{PAGE}: {href} has no \"ZIP, <size>.\" caption after it")
            continue
        actual = size_label(path.stat().st_size)
        if stated != actual:
            errors.append(f"{PAGE}: {href} says {stated}, the file is {actual}; update `kits:` in content/en/brand/_index.md")
    for kit in KITS:
        if kit not in offered:
            errors.append(f"{PAGE}: no download link for {kit}")
    return errors


def main(argv):
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    errors = check(argv[1])
    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
