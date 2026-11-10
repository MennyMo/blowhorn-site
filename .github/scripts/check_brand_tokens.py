#!/usr/bin/env python3
"""Keep the site's brand tokens in sync with the product's tokens.

The site keeps a hand-made copy of the product's marketing/brand/tokens.json
at static/assets/brand/tokens.json. The copy drifted (it missed
blowhorn-ai/blowhorn#1865: caption 13/18, ui 15/22, and five colour usage
notes) and was only fixed by hand in #435. This script has two modes:

validate (default): assert each product group is an exact prefix of the
    matching site group, that only named site-only colours follow
    (video-matte, on-matte, on-teal-deep, teal-glow, status-bg, status-ink,
    mark-claude, mark-deepseek, mark-openai, proof-flag-bg, proof-flag-ink,
    print-ink, ai-soon-ink), and that .ui, .caption and .label in
    assets/css/site.css match the token font sizes. Runs in make check when a
    product checkout is present at BLOWHORN_DIR (default ../blowhorn).

generate: write static/assets/brand/tokens.json as the product file plus the
    site-only extension list from data/brand-token-extensions.json (schema
    validated in schemas/brand-token-extensions.schema.json). Runs in the docs
    sync PR when a product checkout is present.

Usage:
  check_brand_tokens.py [BLOWHORN_DIR] [MODE] [SITE_TOKENS]
    BLOWHORN_DIR  default ../blowhorn
    MODE          validate (default) or generate
    SITE_TOKENS   default static/assets/brand/tokens.json
"""

import copy
import json
import re
import sys
from pathlib import Path

SITE_ONLY_COLOURS = frozenset({
    "video-matte", "on-matte", "on-teal-deep", "teal-glow",
    "status-bg", "status-ink", "mark-claude", "mark-deepseek",
    "mark-openai", "proof-flag-bg", "proof-flag-ink", "print-ink",
    "ai-soon-ink",
})

# .class { font-size: Npx; line-height: Mpx; } captured in declaration order.
CSS_SIZE_RE = re.compile(
    r"\.(ui|caption|label)\s*\{\s*font-size:\s*(\d+)px\s*;\s*line-height:\s*(\d+)px\s*;"
)

EXTENSIONS_PATH = Path("data/brand-token-extensions.json")
SITE_CSS_PATH = Path("assets/css/site.css")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def product_path(blowhorn_dir: Path) -> Path:
    return blowhorn_dir / "marketing" / "brand" / "tokens.json"


def group_prefix_problems(product, site, label):
    """Return problems if product is not an exact prefix of site.

    Entries are compared as whole JSON objects so usage notes, values and
    names must all match exactly.
    """
    problems = []
    if len(product) > len(site):
        problems.append(
            f"{label}: product has {len(product)} entries, site has "
            f"{len(site)}; product group is not a prefix of the site group"
        )
        return problems
    for i, (p, s) in enumerate(zip(product, site)):
        if p != s:
            pname = p.get("name") if isinstance(p, dict) else p
            sname = s.get("name") if isinstance(s, dict) else s
            problems.append(
                f"{label}: entry {i} differs: product {pname!r}, site {sname!r}"
            )
    return problems


def colour_problems(product_colours, site_colours, site_only_names):
    """Return problems: product colours exact prefix; only named site-only
    colours follow; every named site-only colour is present."""
    problems = group_prefix_problems(product_colours, site_colours, "color.tokens")
    if problems:
        return problems
    extra = site_colours[len(product_colours):]
    present = {t.get("name") for t in extra if isinstance(t, dict)}
    for name in sorted(present - site_only_names):
        problems.append(
            f"color.tokens: site-only colour {name!r} is not in the named "
            f"site-only list: {sorted(site_only_names)}"
        )
    missing = site_only_names - present
    if missing:
        problems.append(
            f"color.tokens: named site-only colours missing from site: "
            f"{sorted(missing)}"
        )
    return problems


def css_size_problems(site_css_path: Path, product_type_groups):
    """Return problems: .ui, .caption, .label in CSS match token sizes."""
    problems = []
    css = site_css_path.read_text(encoding="utf-8")

    want = {}
    for group in product_type_groups:
        family = group.get("family")
        for style in group.get("styles", []):
            sname = style.get("name")
            if sname in ("ui", "caption") and family == "sans":
                want[sname] = (style["fontSize"], style["lineHeight"])
            if sname == "label" and family == "mono":
                want[sname] = (style["fontSize"], style["lineHeight"])

    found = set()
    for m in CSS_SIZE_RE.finditer(css):
        name = m.group(1)
        size = int(m.group(2))
        line = int(m.group(3))
        found.add(name)
        if name in want:
            want_size = int(str(want[name][0]).rstrip("px"))
            want_line = int(str(want[name][1]).rstrip("px"))
            if size != want_size or line != want_line:
                problems.append(
                    f"assets/css/site.css: .{name} is {size}px/{line}px, "
                    f"want {want_size}px/{want_line}px from tokens"
                )
    for name in want:
        if name not in found:
            want_size = int(str(want[name][0]).rstrip("px"))
            want_line = int(str(want[name][1]).rstrip("px"))
            problems.append(
                f"assets/css/site.css: .{name} not found, want "
                f"{want_size}px/{want_line}px from tokens"
            )
    return problems


def validate(blowhorn_dir: Path, site_tokens_path: Path, site_css_path: Path,
             extensions_path: Path):
    problems = []
    product = load_json(product_path(blowhorn_dir))
    site = load_json(site_tokens_path)
    ext = load_json(extensions_path)

    site_only_names = set(ext.get("color", {}).keys())

    # color.tokens: product exact prefix; only named site-only colours follow
    problems += colour_problems(
        product["color"]["tokens"], site["color"]["tokens"], site_only_names
    )

    # type.groups styles: each product group's styles is prefix of site's
    product_groups = {g["name"]: g for g in product["type"]["groups"]}
    site_groups = {g["name"]: g for g in site["type"]["groups"]}
    for gname, pgroup in product_groups.items():
        if gname not in site_groups:
            problems.append(
                f"type.groups: product group {gname!r} missing from site"
            )
            continue
        problems += group_prefix_problems(
            pgroup["styles"], site_groups[gname]["styles"],
            f"type.groups[{gname!r}].styles"
        )

    # spacing, radius, shadow, stroke: product exact prefix of site
    for section in ("spacing", "radius", "shadow", "stroke"):
        problems += group_prefix_problems(
            product[section]["tokens"], site[section]["tokens"],
            f"{section}.tokens"
        )

    # CSS .ui/.caption/.label sizes match tokens
    problems += css_size_problems(site_css_path, product["type"]["groups"])

    return problems


def generate(blowhorn_dir: Path, site_tokens_path: Path,
             extensions_path: Path):
    product = load_json(product_path(blowhorn_dir))
    ext = load_json(extensions_path)

    site = copy.deepcopy(product)
    site_colours = site["color"]["tokens"]
    site_only = ext.get("color", {})
    for name in sorted(site_only):
        token = site_only[name]
        site_colours.append({
            "name": name,
            "value": token["value"],
            "usage": token["usage"],
        })

    site_tokens_path.write_text(
        json.dumps(site, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"brand tokens: wrote {site_tokens_path} with "
        f"{len(site_colours)} colour tokens"
    )
    return 0


def main(argv):
    if len(argv) < 2 or len(argv) > 4:
        print(__doc__, file=sys.stderr)
        return 2
    blowhorn_dir = Path(argv[1])
    mode = argv[2] if len(argv) > 2 else "validate"
    site_tokens_path = (
        Path(argv[3]) if len(argv) > 3
        else Path("static/assets/brand/tokens.json")
    )

    if not blowhorn_dir.is_dir():
        print(
            f"brand tokens: blowhorn checkout not found at {blowhorn_dir}",
            file=sys.stderr,
        )
        return 2
    if not product_path(blowhorn_dir).is_file():
        print(
            f"brand tokens: product tokens not found at "
            f"{product_path(blowhorn_dir)}",
            file=sys.stderr,
        )
        return 2
    if not extensions_path.is_file():
        print(
            f"brand tokens: extensions file not found at {extensions_path}",
            file=sys.stderr,
        )
        return 2

    if mode == "generate":
        return generate(blowhorn_dir, site_tokens_path, extensions_path)
    if mode == "validate":
        problems = validate(
            blowhorn_dir, site_tokens_path, SITE_CSS_PATH, extensions_path
        )
        for p in problems:
            print(f"brand tokens: {p}", file=sys.stderr)
        print(f"brand tokens: {len(problems)} problem(s)")
        return 1 if problems else 0
    print(
        f"brand tokens: unknown mode {mode!r} (use validate or generate)",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
