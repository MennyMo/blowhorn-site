#!/usr/bin/env python3
"""Fail if a built heading, button or nav link is in Title Case (#421).

The casing rule (Yi, 2026-11-02): small uppercase is for section and field
labels only (eyebrows such as "HOW IT WORKS"); everything else is sentence
case. So "Frequently Asked Questions" becomes "Questions", and "Get Started
Free" becomes "Get started free".

Read from every built HTML page except the two that are not site copy:

- /docs/ (synced from the product repository: fixed there, not here);
- /compare/<slug>/ (every heading names a competitor, a proper noun).

Read the text of:

- h1, h2 and h3;
- every button (and role="button");
- every link inside a nav element, and every link styled as a button.

A text is Title Case when a word that is not the first of its sentence starts
with a capital letter. Sentence starts (after a full stop, colon, question or
exclamation mark, semicolon or pipe) pass, as the first word does. Acronyms
(CLI, APIs), single letters (I), brand names with a capital inside (AdsPower,
DevRel), and the words in PROPER_NOUNS pass, as do the exact phrases in
PROPER_PHRASES. Text inside <code>, <pre>, <script> and <style>, and anything
with aria-hidden, is not read. A nav link stops at its first block or
description child, so a menu card reads as its title only.

Usage: check_casing.py [BUILD_DIR]
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

# Names and product words that keep their capitals wherever they appear.
PROPER_NOUNS = {
    # Blowhorn and its characters (the cast's names are proper nouns).
    "Blowhorn", "Major", "Tells", "Crowhorn", "General", "Sleeper", "Cell",
    "Trench", "Trooper", "Robo", "Recruit", "Mouse", "Marine", "Drill",
    "Instructor", "Platoon", "Private", "Keyboard", "Warrior", "Donkey",
    "Chick", "Battalion",
    # Platforms, companies and tools a reader would know by name.
    "Chrome", "Google", "Mac", "Windows", "Linux", "Apple", "LinkedIn",
    "Hacker", "News", "Facebook", "Instagram", "YouTube", "TikTok", "Reddit",
    "Threads", "Bluesky", "Mastodon", "GitHub", "Slack", "Teams", "Discord",
    "Claude", "Anthropic", "OpenAI", "Codex", "Cursor", "Copilot", "Gemini",
    "Zapier", "Notion", "Jira", "Trello", "Asana", "Gmail", "Outlook", "Excel",
    "Sheets", "Drive", "Hugo", "Docsy", "Layer5", "Chrome Web Store", "Safari",
    "Firefox", "Edge", "Pinterest", "Medium", "Substack", "Shopify", "WordPress",
    "Stripe", "Salesforce", "HubSpot", "Canva", "Figma", "Vimeo", "Dropbox",
    "Grok", "Pi", "Solo", "Pro", "Team", "Analytics", "Twitter", "Sans",
    "Algorithm", "Captain", "Bot", "Rhonda", "Peddler", "Follower", "Blowhard",
    "Thunderlung",
    "Atlassian", "Microsoft", "Amazon", "Meta", "Signal", "Intercom", "Linear",
    "Datadog", "Wix", "Squarespace", "Framer", "Webflow", "Bricolage",
    "Grotesque", "Instrument", "JetBrains",
}
# Exact phrases that are names, matched case-sensitively in the text.
PROPER_PHRASES = ("Am I a Bot?", "Field Manual", "Early Access", "Blowhorn Tells",
                  "Claude Code", "Chrome Web Store", "Google Analytics", "JetBrains Mono",
                  "Rate Limit Rhonda")
ACRONYM_RE = re.compile(r"^[A-Z0-9]{2,}s?$")
# Pages that are not read: synced docs and competitor comparisons.
SKIPPED_PREFIXES = ("docs/", "compare/")
# A child of a nav link that holds its description, not its label.
DESCRIPTION_CLASS_RE = re.compile(r"(^|[\s_-])(desc|description|sub|meta|intro|summary)($|[\s_-])", re.I)
# Characters after which a word starts a sentence or a label: full stops and the
# like, and the quotes, brackets and marks a label puts before its first word.
SENTENCE_STARTS = set(".!?:;|()\"'\u201c\u201d\u2018\u2019+\u00b7\u2022/")
BLOCK_TAGS = {"p", "div", "ul", "ol", "li", "figure", "section", "article", "table"}
WORD_RE = re.compile(r"[A-Za-z][A-Za-z-]*")
SKIP_TAGS = {"code", "pre", "script", "style", "kbd", "samp"}
HEADING_TAGS = {"h1", "h2", "h3"}


@dataclass
class Text:
    path: str
    line: int
    kind: str
    text: str


@dataclass
class Finding:
    path: str
    line: int
    kind: str
    text: str
    words: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        return (f"{self.path}:{self.line}: {self.kind} is Title Case ({', '.join(self.words)}): "
                f"{self.text!r}")


class Collector(HTMLParser):
    """Collects the text of headings, buttons and nav links with their line numbers."""

    def __init__(self, path: str) -> None:
        super().__init__(convert_charrefs=True)
        self.path = path
        self.texts: list[Text] = []
        self.stack: list[dict] = []  # open elements we care about
        self.skip_depth = 0
        self.nav_depth = 0

    def _open(self, tag, attrs):
        a = dict(attrs)
        if tag in SKIP_TAGS:
            self.skip_depth += 1
        if a.get("aria-hidden") == "true":
            self.stack.append({"tag": tag, "hidden": True})
            return
        # A nav link's description (or any block inside it) closes its label.
        if DESCRIPTION_CLASS_RE.search(a.get("class") or "") or tag in BLOCK_TAGS:
            for node in self.stack:
                if node.get("kind") == "nav link":
                    node["closed"] = True
        kind = None
        if tag in HEADING_TAGS:
            kind = tag
        elif tag == "button" or a.get("role") == "button":
            kind = "button"
        elif tag == "a" and self.nav_depth and "button" not in (a.get("class") or ""):
            kind = "nav link"
        elif tag == "a" and "button" in (a.get("class") or "").split():
            kind = "button"
        if tag == "nav":
            self.nav_depth += 1
        if kind:
            self.stack.append({"tag": tag, "kind": kind, "line": self.getpos()[0], "text": []})
        else:
            self.stack.append({"tag": tag})

    def handle_starttag(self, tag, attrs):
        if tag in ("br", "img", "input", "meta", "link", "hr", "source", "wbr"):
            return
        self._open(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        return

    def handle_endtag(self, tag):
        if tag in ("br", "img", "input", "meta", "link", "hr", "source", "wbr"):
            return
        # Pop to the matching open element.
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i].get("tag") == tag:
                node = self.stack[i]
                del self.stack[i:]
                if tag in SKIP_TAGS:
                    self.skip_depth = max(0, self.skip_depth - 1)
                if tag == "nav":
                    self.nav_depth = max(0, self.nav_depth - 1)
                if "kind" in node:
                    text = " ".join("".join(node["text"]).split())
                    if text:
                        self.texts.append(Text(self.path, node["line"], node["kind"], text))
                break

    def handle_data(self, data):
        if self.skip_depth or any(node.get("hidden") for node in self.stack):
            return
        for node in self.stack:
            if "text" in node and not node.get("closed"):
                node["text"].append(data)


def title_case_words(text: str) -> list[str]:
    """The capitalised words that are not the first of a sentence and are not names."""
    for phrase in PROPER_PHRASES:
        text = text.replace(phrase, " " * len(phrase))
    flagged = []
    for m in WORD_RE.finditer(text):
        word = m.group(0)
        before = text[:m.start()].rstrip()
        if not before or before[-1] in SENTENCE_STARTS:
            continue
        for part in word.split("-"):
            if not part or not part[0].isupper():
                continue
            if len(part) == 1 or ACRONYM_RE.match(part) or any(c.isupper() for c in part[1:]):
                continue
            if part in PROPER_NOUNS:
                continue
            flagged.append(word)
            break
    return flagged


def check_html(path: str, html: str) -> list[Finding]:
    collector = Collector(path)
    collector.feed(html)
    findings = []
    for t in collector.texts:
        words = title_case_words(t.text)
        if words:
            findings.append(Finding(t.path, t.line, t.kind, t.text, words))
    return findings


def main(argv: list[str]) -> int:
    build = Path(argv[1]) if len(argv) > 1 else Path("public")
    if not build.is_dir():
        print(f"check_casing: build dir {build} is missing; run make site-build first", file=sys.stderr)
        return 1
    findings: list[Finding] = []
    pages = sorted(build.rglob("*.html"))
    for page in pages:
        rel = page.relative_to(build).as_posix()
        if rel.startswith(SKIPPED_PREFIXES):
            continue
        findings.extend(check_html(rel, page.read_text(encoding="utf-8")))
    for f in findings:
        print(f)
    if findings:
        print(f"check_casing: {len(findings)} Title Case heading, button or nav link(s). "
              "Sentence case everywhere except section and field labels.", file=sys.stderr)
        return 1
    print(f"check_casing: {len(pages)} page(s) pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
