#!/usr/bin/env python3
"""Fail if the built Resources RSS feeds are missing or malformed.

The Resources center publishes two kinds of feeds (issue #253, Part D):

- public/resources/feed.xml - everything in Resources, newest first.
- public/resources/tags/<tag>/feed.xml - one feed per tag.

The in-product-intelligence tag feed is a published contract: the
desktop homepage reads https://blowhorn.ai/resources/tags/in-product-intelligence/feed.xml.
Every item in every feed must carry the fields the contract promises -
title, link, description (the summary, not a teaser), pubDate, and the
item's tags as category elements - and the contract feed may contain
only items tagged in-product-intelligence.

Usage: check_feeds.py [BUILD_DIR]
"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path

REQUIRED_FIELDS = ("title", "link", "description", "pubDate")
CONTRACT_TAG = "in-product-intelligence"
CONTRACT_FEED = Path("resources/tags") / CONTRACT_TAG / "feed.xml"
RESOURCES_FEED = Path("resources/feed.xml")
ATOM = "{http://www.w3.org/2005/Atom}"
HUGO_TOML = Path(__file__).resolve().parents[2] / "hugo.toml"


def base_url() -> str:
    """The site's baseURL from hugo.toml, with exactly one trailing slash."""
    match = re.search(r'^baseURL\s*=\s*"([^"]+)"', HUGO_TOML.read_text(), re.M)
    if not match:
        raise SystemExit(f"check_feeds: no baseURL in {HUGO_TOML}")
    return match.group(1).rstrip("/") + "/"


def check_feed(
    path: Path, problems: list[str], label: str, contract: bool = False,
    build_dir: Path | None = None, base: str | None = None,
) -> None:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        problems.append(f"{label}: not well-formed XML ({exc})")
        return
    if root.tag != "rss":
        problems.append(f"{label}: root element is <{root.tag}>, expected <rss>")
        return
    channel = root.find("channel")
    if channel is None:
        problems.append(f"{label}: no <channel>")
        return
    if build_dir is not None and base is not None:
        check_channel_links(channel, path.relative_to(build_dir), build_dir, base, problems, label)
    items = channel.findall("item")
    if not items:
        problems.append(f"{label}: no <item> elements")
        return
    for i, item in enumerate(items, 1):
        for field in REQUIRED_FIELDS:
            el = item.find(field)
            if el is None or not (el.text or "").strip():
                problems.append(f"{label}: item {i} is missing a non-empty <{field}>")
        pub = item.find("pubDate")
        if pub is not None and (pub.text or "").strip():
            try:
                parsedate_to_datetime(pub.text.strip())
            except (TypeError, ValueError):
                problems.append(f"{label}: item {i} has an unparseable <pubDate>: {pub.text.strip()!r}")
        if contract:
            cats = [(c.text or "").strip() for c in item.findall("category")]
            if CONTRACT_TAG not in cats:
                problems.append(
                    f"{label}: item {i} lacks <category>{CONTRACT_TAG}</category>;"
                    " the contract feed may only carry that tag's items"
                )


def check_channel_links(
    channel: ET.Element, rel: Path, build_dir: Path, base: str, problems: list[str], label: str
) -> None:
    served_at = base + rel.as_posix()
    self_links = [a.get("href", "") for a in channel.findall(f"{ATOM}link") if a.get("rel") == "self"]
    if served_at not in self_links:
        problems.append(
            f"{label}: channel atom:link rel=self is {self_links[0] if self_links else 'missing'!r},"
            f" expected the URL the feed is served at, {served_at!r}"
        )
    link = (channel.findtext("link") or "").strip()
    if not link.startswith(base):
        problems.append(f"{label}: channel <link> {link!r} is not under {base}")
        return
    page = build_dir / link[len(base):].strip("/") / "index.html"
    if not page.is_file():
        problems.append(
            f"{label}: channel <link> {link!r} points at no page in the build"
            f" (expected {page.relative_to(build_dir)})"
        )


def find(build_dir: Path) -> list[str]:
    problems: list[str] = []
    base = base_url()
    resources_feed = build_dir / RESOURCES_FEED
    if not resources_feed.is_file():
        problems.append(f"{RESOURCES_FEED}: missing")
    else:
        check_feed(resources_feed, problems, str(RESOURCES_FEED), build_dir=build_dir, base=base)
    tags_dir = build_dir / "resources" / "tags"
    tag_feeds = sorted(tags_dir.glob("*/feed.xml")) if tags_dir.is_dir() else []
    if (build_dir / CONTRACT_FEED) not in tag_feeds:
        problems.append(f"{CONTRACT_FEED}: missing (the desktop contract feed)")
    for feed in tag_feeds:
        rel = feed.relative_to(build_dir)
        check_feed(feed, problems, str(rel), contract=(rel == CONTRACT_FEED), build_dir=build_dir, base=base)
    return problems


def main(argv: list[str]) -> int:
    build_dir = Path(argv[1] if len(argv) > 1 else "public")
    if not build_dir.is_dir():
        print(f"check_feeds: {build_dir} is not a directory", file=sys.stderr)
        return 2
    problems = find(build_dir)
    for problem in problems:
        print(f"::error::{problem}")
    if problems:
        return 1
    print("check_feeds: resources feeds are well-formed and carry the required fields")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
