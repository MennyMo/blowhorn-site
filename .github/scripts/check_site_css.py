#!/usr/bin/env python3
"""Fail if the site's own stylesheets break the flat Signal rules (#421).

Reads the source stylesheets (assets/css/*.css and assets/scss/*.scss), not
the built output, so a finding names the file and line to fix. Four rules:

- Type floor: a font-size under 13px fails, unless the same rule also sets
  text-transform: uppercase (small uppercase mono labels and numerals only).
  Sizes in px, rem (16px root) and pt are read, in font-size and in the font
  shorthand; var() and calc() are not.
- No coloured edge: a single-side border (left, right, top, bottom, or the
  inline and block start and end) in an accent colour fails. Neutral 1px
  rules (--line, --line-strong, ink, surface, grey rgba, transparent, none)
  are structure and pass. The selected-tab mark and a checkmark are structure
  too (see structural_mark).
- No single-edge inset shadow: an inset box-shadow with a non-zero x or y
  offset is a stripe down one side. An even ring (inset 0 0 0 1px) passes.
- No glass material: backdrop-filter fails outside the none value.

Each failure prints file:line, the rule and the declaration. The exit code
is 1 when anything fails, so `make check-site-css` stops the build.

Usage: check_site_css.py [ROOT]   (ROOT defaults to the repository root)
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

MIN_FONT_PX = 13.0
ROOT_PX = 16.0

# Files the check reads, relative to the repository root.
GLOBS = ("assets/css/*.css", "assets/scss/*.scss")

# Files that are not yet checked, with the reason. Empty unless a file is
# owned by another change that has not landed.
ALLOWLIST: dict[str, str] = {
    "assets/css/home-signal.css": "home CSS is rebuilt by #418; remove this entry when that lands",
}

# Selectors whose text is a picture of the product, not reader copy: the
# miniature interface art (ia-*, iface-art) is aria-hidden and drawn at about
# 7 to 9px so a whole app window fits in a menu row. Their type is exempt from
# the floor only; every other rule still has to pass.
MINIATURE_SELECTOR_RE = re.compile(r"(^|[\s,>+~])\.(ia-|iface-art)")

# A colour is an accent when it is chromatic: a brand token (teal, coral,
# gold...) or a hex or rgb() literal that is not grey. Ink, line, surface and
# white-or-black alphas are structure.
ACCENT_TOKEN_RE = re.compile(
    r"teal|coral|gold|mint|green|red|amber|warn|yellow|blue|pink|purple|orange|accent|brand|cta|keppel|caribbean",
    re.I,
)
HEX_RE = re.compile(r"^#([0-9a-f]{3,8})$", re.I)
RGB_RE = re.compile(r"^rgba?\((\d+)[ ,]+(\d+)[ ,]+(\d+)", re.I)
SIDE_BORDER_PROPS = {
    "border-left", "border-right", "border-top", "border-bottom",
    "border-inline-start", "border-inline-end",
    "border-block-start", "border-block-end",
    "border-left-color", "border-right-color", "border-top-color",
    "border-bottom-color", "border-inline-start-color", "border-inline-end-color",
    "border-block-start-color", "border-block-end-color",
}
STYLE_KEYWORDS = {"solid", "dashed", "dotted", "double", "groove", "ridge", "inset",
                  "outset", "hidden", "thin", "medium", "thick", "!important"}
FONT_SIZE_RE = re.compile(r"^(-?[\d.]+)(px|rem|pt)$", re.I)
INSET_RE = re.compile(r"\binset\s+(-?[\d.]+)(?:px)?\s+(-?[\d.]+)(?:px)?", re.I)
BACKDROP_RE = re.compile(r"^(-webkit-)?backdrop-filter$", re.I)
DECL_RE = re.compile(r"^\s*(-?[a-z][a-z-]*)\s*:\s*(.+?)\s*$", re.I | re.S)
TOKEN_RE = re.compile(r"[{};]")


@dataclass
class Decl:
    path: str
    line: int
    prop: str
    value: str
    block: int
    selector: str


@dataclass
class Finding:
    path: str
    line: int
    rule: str
    text: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.rule}: {self.text}"


def strip_comments(text: str) -> str:
    """Blank out /* */ and // comments, keeping offsets (and so line numbers)."""
    text = re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), text, flags=re.S)
    return re.sub(r"(?m)(^|[^:\"'])//[^\n]*", lambda m: m.group(1) + " " * (len(m.group(0)) - len(m.group(1))), text)


def parse(text: str, path: str) -> list[Decl]:
    """Return every declaration with the block (rule body) it sits in."""
    text = strip_comments(text)
    decls: list[Decl] = []
    stack: list[int] = [0]
    selectors: dict[int, str] = {0: ""}
    next_block = 1
    start = 0
    for m in TOKEN_RE.finditer(text):
        segment = text[start:m.start()]
        delim = m.group(0)
        seg_line = text.count("\n", 0, start + (len(segment) - len(segment.lstrip()))) + 1
        d = DECL_RE.match(segment)
        if delim in ";}" and d and not segment.lstrip().startswith(("@", "&", ".", "#")):
            prop = d.group(1).lower()
            if not prop.startswith("$"):
                decls.append(Decl(path, seg_line, prop, d.group(2).strip(), stack[-1], selectors[stack[-1]]))
        if delim == "{":
            selectors[next_block] = segment.strip()
            stack.append(next_block)
            next_block += 1
        elif delim == "}" and len(stack) > 1:
            stack.pop()
        start = m.end()
    return decls


SHORTHAND_SIZE_RE = re.compile(r"(?<![\w.-])(\d*\.?\d+)(px|rem|pt)(?!\w)", re.I)


def font_px(value: str, shorthand: bool = False) -> float | None:
    """The size of a font-size value, or of the size token in a font shorthand."""
    if shorthand:
        found = SHORTHAND_SIZE_RE.search(value)
        if not found:
            return None
        value = found.group(0)
    m = FONT_SIZE_RE.match(value.strip().split("!")[0].strip())
    if not m:
        return None
    n, unit = float(m.group(1)), m.group(2).lower()
    if unit == "px":
        return n
    if unit == "rem":
        return n * ROOT_PX
    return n * 4 / 3  # pt


def is_coloured_edge(value: str) -> bool:
    """True when a side border's colour is an accent, not a neutral rule."""
    tokens = re.findall(r"var\([^)]*\)|rgba?\([^)]*\)|\S+", value.strip(), re.I)
    colours = [t for t in tokens
               if not re.match(r"^-?[\d.]+(px|rem|em|pt)?$", t, re.I)
               and t.lower() not in STYLE_KEYWORDS]
    return any(is_accent(c) for c in colours)


def is_accent(colour: str) -> bool:
    if colour.lower() in ("transparent", "none", "inherit", "currentcolor", "initial", "unset"):
        return False
    if colour.startswith("var("):
        return bool(ACCENT_TOKEN_RE.search(colour))
    rgb = None
    hexm = HEX_RE.match(colour)
    if hexm:
        h = hexm.group(1)
        h = "".join(c * 2 for c in h) if len(h) == 3 else h
        rgb = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    rgbm = RGB_RE.match(colour)
    if rgbm:
        rgb = tuple(int(rgbm.group(i)) for i in (1, 2, 3))
    if rgb is not None:
        return max(rgb) - min(rgb) > 16
    return bool(ACCENT_TOKEN_RE.search(colour))


def structural_mark(d: Decl, checkmarks: set[int]) -> bool:
    """A one-edge mark the design keeps: the selected-tab underline or a checkmark.

    DESIGN.md (Cards) names both as structure, not stripes: a tab's selected mark
    sits on a tab rule, and a checkmark is a bordered box turned -45 degrees.
    """
    if d.block in checkmarks:
        return True
    is_tab = re.search(r"[.-]tabs?\b", d.selector, re.I) is not None
    return is_tab and d.prop in {"border-bottom", "border-bottom-color", "box-shadow"}


def check_decls(decls: list[Decl]) -> list[Finding]:
    uppercase_blocks = {d.block for d in decls if d.prop == "text-transform" and d.value.lower().startswith("uppercase")}
    checkmarks = {d.block for d in decls if d.prop == "transform" and "rotate(-45deg)" in d.value.replace(" ", "")}
    findings: list[Finding] = []
    for d in decls:
        if d.prop in ("font-size", "font"):
            px = font_px(d.value, shorthand=d.prop == "font")
            miniature = bool(MINIATURE_SELECTOR_RE.search(d.selector))
            if px is not None and px < MIN_FONT_PX and d.block not in uppercase_blocks and not miniature:
                findings.append(Finding(d.path, d.line, "font-size-floor",
                                        f"font-size: {d.value} is under {MIN_FONT_PX:g}px on mixed-case text"))
        elif d.prop in SIDE_BORDER_PROPS and is_coloured_edge(d.value) and not structural_mark(d, checkmarks):
            findings.append(Finding(d.path, d.line, "coloured-edge",
                                    f"{d.prop}: {d.value} is a coloured stripe on one edge"))
        elif d.prop == "box-shadow" and not structural_mark(d, checkmarks):
            for m in INSET_RE.finditer(d.value):
                x, y = float(m.group(1)), float(m.group(2))
                if x != 0 or y != 0:
                    findings.append(Finding(d.path, d.line, "single-edge-inset",
                                            f"box-shadow: {d.value} draws an inset stripe down one edge"))
                    break
        elif BACKDROP_RE.match(d.prop) and d.value.strip().lower() != "none":
            findings.append(Finding(d.path, d.line, "glass-material",
                                    f"{d.prop}: {d.value} is glass material (flat Signal only)"))
    return findings


def check_files(paths: list[Path], root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in paths:
        rel = path.relative_to(root).as_posix()
        if rel in ALLOWLIST:
            continue
        findings.extend(check_decls(parse(path.read_text(encoding="utf-8"), rel)))
    return findings


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path(__file__).resolve().parents[2]
    paths = sorted(p for pattern in GLOBS for p in root.glob(pattern))
    if not paths:
        print(f"check_site_css: no stylesheets under {root}", file=sys.stderr)
        return 1
    findings = check_files(paths, root)
    for f in findings:
        print(f)
    if findings:
        print(f"check_site_css: {len(findings)} finding(s). Flat Signal: 13px floor, no coloured edge, no glass.", file=sys.stderr)
        return 1
    print(f"check_site_css: {len(paths)} stylesheet(s) pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
