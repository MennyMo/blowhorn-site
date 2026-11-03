#!/usr/bin/env python3
"""Fail if a built page breaks the one-install-call rule (issue #420).

Every view has one install call to action, labelled "Download" and rendered
by layouts/_partials/download-button.html, and at most one teal primary
(.button-primary) in its main content. This check reads the built site and
fails when:

- a page's <main> holds more than one .button-primary. A form's own submit
  button (the newsletter and signup forms) is not a page call to action and
  is not counted, and the header, footer and cookie banner sit outside main;
- a link or button carries an old install label ("Download free", "Enlist a
  computer", "Download for Mac", "Get Blowhorn", "Download Blowhorn"), or
  "Install the CLI" as a primary.

Docs pages are synced from the product repository and are skipped. The home
page is exempt from both rules (PENDING_HOME) until its rebuild (#418) lands:
remove it from PENDING_HOME then.

Usage: check_install_cta.py [BUILD_DIR]
"""

from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path

PRIMARY_CLASS = "button-primary"
OLD_LABELS = (
    "Download free",
    "Enlist a computer",
    "Download for Mac",
    "Get Blowhorn",
    "Get Blowhorn for Mac",
    "Download Blowhorn",
    "Download Blowhorn free",
)
OLD_PRIMARY_LABELS = ("Install the CLI",)
SKIP_PREFIXES = ("docs/",)
PENDING_HOME = ("index.html",)


class Controls(HTMLParser):
    """Collect every link and button: its label, whether it is a primary,
    and whether it sits inside <main> and outside any <form>."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.controls: list[dict] = []
        self._open: list[dict] = []
        self._main = 0
        self._form = 0

    def handle_starttag(self, tag, attrs):
        if tag == "main":
            self._main += 1
        elif tag == "form":
            self._form += 1
        elif tag in ("a", "button"):
            classes = (dict(attrs).get("class") or "").split()
            self._open.append({
                "tag": tag,
                "primary": PRIMARY_CLASS in classes,
                "in_main": self._main > 0,
                "in_form": self._form > 0,
                "text": [],
            })

    def handle_endtag(self, tag):
        if tag == "main":
            self._main -= 1
        elif tag == "form":
            self._form -= 1
        elif tag in ("a", "button"):
            for i in range(len(self._open) - 1, -1, -1):
                if self._open[i]["tag"] == tag:
                    entry = self._open.pop(i)
                    entry["label"] = " ".join("".join(entry.pop("text")).split())
                    self.controls.append(entry)
                    break

    def handle_data(self, data):
        for entry in self._open:
            entry["text"].append(data)


def problems_in(rel: str, html: str) -> list[str]:
    parser = Controls()
    parser.feed(html)
    problems = []
    primaries = [c for c in parser.controls if c["primary"] and c["in_main"] and not c["in_form"]]
    if len(primaries) > 1:
        labels = ", ".join(repr(c["label"]) for c in primaries)
        problems.append(f"{rel}: {len(primaries)} primary buttons in main ({labels}); a view has one")
    for control in parser.controls:
        label = control["label"]
        if label in OLD_LABELS or (control["primary"] and label in OLD_PRIMARY_LABELS):
            problems.append(f"{rel}: {control['tag']} reads {label!r}, an old install label; use the Download partial")
    return problems


def check(build_dir: Path) -> list[str]:
    problems = []
    for path in sorted(build_dir.rglob("*.html")):
        rel = path.relative_to(build_dir).as_posix()
        if rel.startswith(SKIP_PREFIXES) or rel in PENDING_HOME:
            continue
        problems.extend(problems_in(rel, path.read_text(encoding="utf-8", errors="replace")))
    return problems


def main(argv: list[str]) -> int:
    build_dir = Path(argv[1] if len(argv) > 1 else "public")
    if not build_dir.is_dir():
        print(f"check_install_cta: {build_dir} is not a directory", file=sys.stderr)
        return 2
    problems = check(build_dir)
    for problem in problems:
        print(f"::error::{problem}")
    if problems:
        return 1
    print("check_install_cta: one primary per view, and no old install label")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
