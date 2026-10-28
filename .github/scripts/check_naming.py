#!/usr/bin/env python3
"""Fail if the built site names the service anything but Blowhorn, says machines or Macs,
or blurs the Google Chrome requirement.

Users see one product, Blowhorn: they sign in at cloud.blowhorn.ai and
there is no "Layer5 Cloud" or "Blowhorn Cloud" (Yi, 2026-10-20). Layer5,
the company, is named only in the footer and on the legal pages
(privacy, terms and the legal index).

Read from every built HTML page: text, plus the alt, title, aria-label
and placeholder attributes and the description and social meta tags.
Script and style bodies, HTML comments, URLs and ids are not read, so
layer5io/... repository links and file names pass.

- "Layer5 Cloud" or "Blowhorn Cloud" (any case) fails on every page,
  footer included.
- "Layer5" or "Layer 5" (as written, capital L) fails outside a <footer>
  element and outside the legal pages. Literal command samples in <code>
  or <pre> (an org or subject named Layer5) pass this rule, not the one
  above.
- "machine" or "machines" (any case) fails on every page, docs included.
  The things Blowhorn runs on are computers (Lee, 2026-10-21, replacing
  "machines, never Macs"). Idioms that are not the reader's computer pass:
  "machine learning", "machine-readable", "state machine" and a tool
  described as a "posting" or "outbound machine". Class names, ids and
  URLs are never read. The CLI reference (docs/reference/cli/) is written
  from the CLI's own --help text, so it passes until that text changes.
- "Macs" or "your Mac" (also "my", "this" or "every" Mac, and "own
  Mac") fails outside the docs and the archived /home-reveille/ page.
  Blowhorn runs on any number of your computers, so marketing copy says
  computers (or soldiers, recruits, battalion), never Macs (Yi,
  2026-10-20). "macOS", "for Mac" on a download button and the
  Blowhorn-mac.dmg file name pass; docs keep macOS-specific detail.
- A vague browser requirement ("Google Chrome is required for now",
  "Google Chrome, for now", "Support for more browsers is planned")
  fails on every page. Download and install pages state the exact
  requirement with versions ("Requires macOS 13 or newer and Google
  Chrome 142 or newer"); marketing pages link to System requirements
  (Lee, 2026-10-28, replacing #288's "for now" note).
- "browser profile" or "browser extension" fails in the docs. Docs about
  using the app or the CLI name Google Chrome and Chrome profiles, as the
  app's own labels do, because the reader must use Chrome there. The CLI
  reference (docs/reference/cli/) comes from --help text and passes.
- Text in <code> or <pre> passes these rules: a command, flag or printed
  line is quoted as the software writes it.

Usage: check_naming.py [BUILD_DIR]
"""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

CLOUD_RE = re.compile(r"\b(?:Layer\s?5|Blowhorn)\s+Cloud\b", re.I)
COMPANY_RE = re.compile(r"\bLayer\s?5\b")
MACHINE_RE = re.compile(r"\bmachines?\b", re.I)
# "machine" that is not the reader's computer.
MACHINE_IDIOM_RE = re.compile(
    r"\bmachines?(?:\s+learning|-readable|\s+readable)\b|\bstate\s+machines?\b"
    r"|\b(?:posting|outbound)\s+machines?\b", re.I)
MACS_RE = re.compile(r"\bMacs\b|\b(?:your|my|this|every)\s+(?:own\s+)?Mac\b|\bown\s+Mac\b", re.I)
VAGUE_BROWSER_RE = re.compile(
    r"\bChrome(?: is required)?,? for now\b|\bsupport for more browsers\b|\bmore browsers (?:is|are) planned\b", re.I)
CHROME_WORD_RE = re.compile(r"\bbrowser[- ](?:profiles?|extensions?)\b", re.I)
# Pages that must say Chrome profile and Chrome extension: the docs, minus the CLI's --help text.
CHROME_WORDS_PREFIX = "docs/"
# Pages where "machine" may stay: generated from the CLI's --help text.
MACHINE_ALLOWED_PREFIXES = ("docs/reference/cli/",)
# Pages where "Macs" may stay: macOS-specific docs and the archived original home.
MACS_ALLOWED_PREFIXES = ("docs/", "home-reveille/")
# Pages that may name Layer5 (the company). Paths relative to BUILD_DIR.
COMPANY_ALLOWED = ("legal/index.html", "legal/privacy/index.html", "legal/terms/index.html")
TEXT_ATTRS = {"alt", "title", "aria-label", "placeholder"}
META_NAMES = {"description", "og:title", "og:description", "og:site_name",
              "twitter:title", "twitter:description", "application-name"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "source", "track", "wbr"}


class Reader(HTMLParser):
    """Collect (text, company_ok, in_code) triples a reader of the page sees.

    company_ok is true in a <footer>, and for text in <code> or <pre>.
    in_code is true only for text in <code> or <pre>.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.footer = 0
        self.code = 0
        self.skip = 0
        self.out: list[tuple[str, bool, bool]] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for name in TEXT_ATTRS:
            if a.get(name):
                self.out.append((a[name], self.footer > 0, False))
        if tag == "meta":
            key = (a.get("name") or a.get("property") or "").lower()
            if key in META_NAMES and a.get("content"):
                self.out.append((a["content"], False, False))
        if tag in VOID:
            return
        self.stack.append(tag)
        if tag == "footer":
            self.footer += 1
        if tag in ("code", "pre"):
            self.code += 1
        if tag in ("script", "style", "template"):
            self.skip += 1

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.stack and self.stack[-1] == tag:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag not in self.stack:
            return
        while self.stack:
            t = self.stack.pop()
            if t == "footer":
                self.footer -= 1
            if t in ("code", "pre"):
                self.code -= 1
            if t in ("script", "style", "template"):
                self.skip -= 1
            if t == tag:
                break

    def handle_data(self, data):
        if not self.skip and data.strip():
            self.out.append((data, self.footer > 0 or self.code > 0, self.code > 0))


def page_problems(rel: str, html: str) -> list[str]:
    reader = Reader()
    reader.feed(html)
    reader.close()
    found: list[str] = []
    company_ok = rel in COMPANY_ALLOWED
    macs_ok = rel.startswith(MACS_ALLOWED_PREFIXES)
    machine_ok = rel.startswith(MACHINE_ALLOWED_PREFIXES)
    chrome_words = rel.startswith(CHROME_WORDS_PREFIX) and not machine_ok
    for text, company_here, in_code in reader.out:
        text = " ".join(text.split())
        for m in CLOUD_RE.finditer(text):
            found.append(f'{rel}: says "{m.group(0)}" (say Blowhorn): ...{snippet(text, m)}...')
        if not in_code and not machine_ok:
            idioms = [i.span() for i in MACHINE_IDIOM_RE.finditer(text)]
            for m in MACHINE_RE.finditer(text):
                if any(a <= m.start() < b for a, b in idioms):
                    continue
                found.append(f'{rel}: says "{m.group(0)}" (say computer): ...{snippet(text, m)}...')
        if not macs_ok and not in_code:
            for m in MACS_RE.finditer(text):
                found.append(f'{rel}: says "{m.group(0)}" (say computers): ...{snippet(text, m)}...')
        if not in_code:
            for m in VAGUE_BROWSER_RE.finditer(text):
                found.append(f'{rel}: says "{m.group(0)}" (state the requirement with versions): ...{snippet(text, m)}...')
            if chrome_words:
                for m in CHROME_WORD_RE.finditer(text):
                    found.append(f'{rel}: says "{m.group(0)}" (say Chrome profile or Chrome extension in the docs): ...{snippet(text, m)}...')
        if company_ok or company_here:
            continue
        for m in COMPANY_RE.finditer(text):
            if CLOUD_RE.match(text, m.start()):
                continue
            found.append(f'{rel}: names "{m.group(0)}" outside the footer and legal pages: ...{snippet(text, m)}...')
    return found


def snippet(text: str, m: re.Match) -> str:
    return text[max(0, m.start() - 40): m.end() + 40]


def check(build: Path) -> list[str]:
    failures: list[str] = []
    for path in sorted(build.rglob("*.html")):
        rel = path.relative_to(build).as_posix()
        if rel.startswith("internal/"):
            continue
        failures.extend(page_problems(rel, path.read_text(encoding="utf-8", errors="replace")))
    return failures


def main(argv: list[str]) -> int:
    build = Path(argv[1] if len(argv) > 1 else "public")
    if not build.is_dir():
        print(f"check_naming: no build at {build}; run make site-build first", file=sys.stderr)
        return 2
    failures = check(build)
    for line in failures:
        print(f"check_naming: {line}", file=sys.stderr)
    if failures:
        print(f"check_naming: {len(failures)} naming problem(s). Users see Blowhorn (sign in at cloud.blowhorn.ai); Layer5 only in the footer and legal pages; computers, never machines or Macs; the Google Chrome requirement stated with versions.", file=sys.stderr)
        return 1
    print("check_naming: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
