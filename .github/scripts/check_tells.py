#!/usr/bin/env python3
"""Fail if a Blowhorn Tells placement disappears or a Tells link loses its tracking.

The site points readers at Blowhorn Tells, the free "Am I a Bot?" check, from
fixed places (data/tells.json "placements"), and every one of those links is
built by layouts/_partials/tells-link.html with the same UTM parameters, so
referral reports can tell the placements apart. This check reads the built
site and fails when:

- a link to the Tells host carries UTM parameters other than the ones in
  data/tells.json, or a utm_content that is not a listed placement;
- a placement is missing from a page that must carry it (REQUIRED below):
  the header, bar and footer on the home page, the home band, the callout on
  every /compare/<slug>/ page, /ai/ and /agents/, the thanks card, the card on
  every docs page and the 404 line.

Links without any UTM parameter pass: the docs (synced from the product
repository) and data-driven FAQ copy link to Tells in prose, by design.

Usage: check_tells.py [BUILD_DIR] [DATA_FILE]
"""

from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA = ROOT / "data" / "tells.json"

# Page (relative to the build) -> placements whose links it must carry.
REQUIRED = {
    "index.html": {"nav", "bar", "footer", "home"},
    "ai/index.html": {"ai"},
    "agents/index.html": {"agents"},
    "download/thanks/index.html": {"thanks"},
    "404.html": {"404", "bar"},
}
# Every page (index.html) under a prefix must carry the placement. The
# /compare/ hub is a matrix page, not a comparison, so only its children
# count there; the docs landing page is a docs page like the rest.
REQUIRED_UNDER = {
    "compare/": ("compare", False),
    "docs/": ("docs", True),
}


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hrefs: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.hrefs.append(href)


def is_redirect(html: str) -> bool:
    return 'http-equiv="refresh"' in html or "http-equiv=refresh" in html


def page_placements(rel: str, html: str, data: dict) -> tuple[set[str], list[str]]:
    """The placements a page links with, and its malformed Tells links."""
    host = urlsplit(data["url"]).netloc
    expected = {
        "utm_source": data["utm"]["source"],
        "utm_medium": data["utm"]["medium"],
        "utm_campaign": data["utm"]["campaign"],
    }
    parser = Links()
    parser.feed(html)
    found: set[str] = set()
    problems: list[str] = []
    for href in parser.hrefs:
        url = urlsplit(href)
        if url.netloc != host:
            continue
        query = parse_qs(url.query)
        utm = {k: v for k, v in query.items() if k.startswith("utm_")}
        if not utm:
            continue
        for key, value in expected.items():
            if utm.get(key) != [value]:
                problems.append(f"{rel}: {href} has {key}={utm.get(key)}, want {value}")
        extra = set(utm) - set(expected) - {"utm_content"}
        if extra:
            problems.append(f"{rel}: {href} has unexpected {', '.join(sorted(extra))}")
        content = utm.get("utm_content", [])
        if len(content) != 1 or content[0] not in data["placements"]:
            problems.append(f"{rel}: {href} has utm_content={content}, not one of data/tells.json placements")
            continue
        found.add(content[0])
    return found, problems


def check(build: Path, data: dict) -> list[str]:
    failures: list[str] = []
    seen: dict[str, set[str]] = {}
    for path in sorted(build.rglob("*.html")):
        rel = path.relative_to(build).as_posix()
        html = path.read_text(encoding="utf-8", errors="replace")
        if is_redirect(html):
            continue
        found, problems = page_placements(rel, html, data)
        failures.extend(problems)
        seen[rel] = found

    for rel, placements in REQUIRED.items():
        if rel not in seen:
            failures.append(f"{rel}: page is missing from the build")
            continue
        for placement in sorted(placements - seen[rel]):
            failures.append(f"{rel}: no Tells link with utm_content={placement}")

    for prefix, (placement, with_hub) in REQUIRED_UNDER.items():
        hub = prefix + "index.html"
        pages = [rel for rel in seen
                 if rel.startswith(prefix) and rel.endswith("index.html") and (with_hub or rel != hub)]
        if not pages:
            failures.append(f"{prefix}: no pages in the build")
        for rel in sorted(pages):
            if placement not in seen[rel]:
                failures.append(f"{rel}: no Tells link with utm_content={placement}")
    return failures


def main(argv: list[str]) -> int:
    build = Path(argv[1]) if len(argv) > 1 else ROOT / "public"
    data_file = Path(argv[2]) if len(argv) > 2 else DEFAULT_DATA
    data = json.loads(data_file.read_text(encoding="utf-8"))
    failures = check(build, data)
    for failure in failures:
        print(failure, file=sys.stderr)
    if failures:
        print(f"check_tells: {len(failures)} problem(s)", file=sys.stderr)
        return 1
    print("check_tells: every Tells placement is present and tagged")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
