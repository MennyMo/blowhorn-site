#!/usr/bin/env python3
"""Fail if the published API reference could mislead or leak.

Usage: check_api_reference.py BUILD_DIR [--config hugo.toml] [--root DIR]

Does nothing (and passes) while params.apiReference.spec is empty (hugo.toml,
or HUGO_PARAMS_APIREFERENCE_SPEC, which overrides it as it does for Hugo), which is the
shipped state: no page uses the rest-apis layout and there is no spec file.
Once a spec path is set, the build must hold:

- a spec file that is already in the exporter's canonical, fully filtered form
  (.github/scripts/openapi_export.py run on it changes nothing), so an
  unfiltered or reformatted file fails. It cannot tell whether the file is
  current with the product schema: that is the sync step's job;
- at least one built page rendered by the layout, whose operation count equals
  the spec's, and which carries the "Not an HTTP API" notice (the product ships
  no HTTP listener);
- no private-repository or internal-site mention in that page (the exporter's
  deny patterns), and no "try it" control (the notice itself says there is no server URL).

See docs/api-reference.md. Run by `make check-api-reference`.
"""

import argparse
import json
import os
import re
import sys
import tomllib
from pathlib import Path

import openapi_export as ox

ROOT = Path(__file__).resolve().parents[2]
NOTICE = "Not an HTTP API"
OP_RE = re.compile(r"<details\b[^>]*\bdata-api-op\b")
LISTENER_RE = re.compile(r"Try this endpoint|Try it out|api-try", re.IGNORECASE)


ENV_SPEC = "HUGO_PARAMS_APIREFERENCE_SPEC"


def configured_spec(config):
    """The spec path Hugo will use: the environment override (it wins, even to
    an empty value, exactly as Hugo applies it), else hugo.toml."""
    if ENV_SPEC in os.environ:
        return os.environ[ENV_SPEC].strip()
    data = tomllib.loads(Path(config).read_text(encoding="utf-8"))
    return ((data.get("params") or {}).get("apiReference") or {}).get("spec") or ""


def check(build_dir, config, root=ROOT):
    """Return a list of problems (empty when fine or disabled)."""
    spec_rel = configured_spec(config)
    if not spec_rel:
        return []
    problems = []
    spec_path = Path(root) / spec_rel
    try:
        text = spec_path.read_text(encoding="utf-8")
        exported, _ = ox.export_public(json.loads(text))
    except (OSError, ValueError, ox.ExportError) as exc:
        return [f"{spec_rel}: {exc}"]
    if ox.render(exported) != text:
        problems.append(f"{spec_rel}: not in the exporter's canonical public form (unfiltered or reformatted); "
                        "re-run .github/scripts/openapi_export.py")
    expected = sum(len(item) for item in exported["paths"].values())

    pages = [p for p in Path(build_dir).rglob("index.html")
             if "data-api-ref" in p.read_text(encoding="utf-8")]
    if not pages:
        problems.append(f"params.apiReference.spec is set but no built page uses the "
                        f"rest-apis layout under {build_dir}")
    for page in pages:
        html = page.read_text(encoding="utf-8")
        rel = page.relative_to(build_dir)
        found = len(OP_RE.findall(html))
        if found != expected:
            problems.append(f"{rel}: renders {found} operation(s), the spec has {expected}")
        if NOTICE not in html:
            problems.append(f'{rel}: the "{NOTICE}" notice is missing')
        for where, pattern in ox.find_leaks(html):
            problems.append(f"{rel}: mentions something private (matches {pattern!r})")
        if LISTENER_RE.search(html):
            problems.append(f"{rel}: offers a 'try it' control")
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("build_dir")
    parser.add_argument("--config", default=str(ROOT / "hugo.toml"))
    parser.add_argument("--root", default=str(ROOT), help="project root the spec path is relative to")
    args = parser.parse_args(argv)
    if not configured_spec(args.config):
        print("check-api-reference: params.apiReference.spec is empty; nothing to check")
        return 0
    problems = check(args.build_dir, args.config, args.root)
    for problem in problems:
        print(f"check-api-reference: {problem}", file=sys.stderr)
    if problems:
        return 1
    print("check-api-reference: the API reference matches its spec")
    return 0


if __name__ == "__main__":
    sys.exit(main())
