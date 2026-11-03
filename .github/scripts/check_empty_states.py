#!/usr/bin/env python3
"""Fail if a built empty state shows text without its cast character.

Every empty state on the site is the cast empty state
(layouts/_partials/cast-empty-state.html): one character on a dark stage,
one line of copy, at most one action. Each known empty-state line must sit
inside a .cast-empty block that also holds the character's art, and the
docs search's no-results template (assets/js/offline-search.js) must carry
the art and the query slot.

Read from every built HTML page. A new empty state gets its copy added to
EMPTY_COPY, or the layout that renders it gets a test here.

Run with `make check-empty-states`; `make test-scripts` runs its unit tests.
"""

import re
import sys
from pathlib import Path

# The one-line copy of each empty state. A page that shows one of these
# lines must show it inside a cast-empty block with art.
EMPTY_COPY = [
    "No page matches",
    "This example is coming soon.",
    "Not in the CLI yet.",
    "Screenshot coming soon.",
    "No actions match.",
]

BLOCK = re.compile(r'<div class="cast-empty(?:\s[^"]*)?">(.*?)</div>', re.S)
ART = re.compile(r'<img class="cast-empty-art"')
SEARCH_TEMPLATE = re.compile(r'<template id="cast-empty-search">(.*?)</template>', re.S)
QUERY_SLOT = 'data-cast-query'
# The copy the search and the sidebar shipped before the cast state.
RETIRED_COPY = ["No results found for query", "Drop a PNG at"]


def problems_in(path, html):
    found = []
    blocks = BLOCK.findall(html)
    for copy in EMPTY_COPY:
        if copy not in html:
            continue
        inside = [b for b in blocks if copy in b]
        if not inside:
            found.append(f"{path}: {copy!r} is shown outside a cast-empty block")
        elif not any(ART.search(b) for b in inside):
            found.append(f"{path}: {copy!r} is shown without its cast character")
    for copy in RETIRED_COPY:
        if copy in html:
            found.append(f"{path}: retired empty-state copy {copy!r}")
    for template in SEARCH_TEMPLATE.findall(html):
        if not ART.search(template):
            found.append(f"{path}: the search no-results template has no cast character")
        if QUERY_SLOT not in template:
            found.append(f"{path}: the search no-results template has no query slot")
    return found


def main(build_dir):
    problems = []
    pages = sorted(Path(build_dir).rglob("*.html"))
    for page in pages:
        problems += problems_in(page, page.read_text(encoding="utf-8"))
    if not any(SEARCH_TEMPLATE.search(p.read_text(encoding="utf-8")) for p in pages):
        problems.append("no page carries the search no-results template")
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        return 1
    print(f"check-empty-states: {len(pages)} pages, every empty state has its cast character")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "public"))
