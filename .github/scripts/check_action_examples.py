#!/usr/bin/env python3
"""Fail if action examples, vocabulary, or YAML actions drift apart.

Every supported action on every supported platform must have an
data/action_examples.json entry (placeholders allowed). CLI commands marked
available must name a subcommand whose CLI reference page matches, and each
flag must belong to that subcommand's section (plus shared flags when the
section says it takes them), not merely appear somewhere on the page.

Usage: check_action_examples.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FLAG_RE = re.compile(r"--[a-z][a-z0-9-]*")
FLAG_CELL_RE = re.compile(r"`(--[a-z][a-z0-9-]*)`")
HEADING_RE = re.compile(r"^## blowhorn (.+)$", re.M)
# A command's own section has no h2 when it would repeat the page title
# (the product's CLI reference renders it as the title page); the page's
# front matter title names it instead.
TITLE_RE = re.compile(r'^title:\s*"?blowhorn ([^"\n]+?)"?\s*$', re.M)
EM_DASH = "\u2014"


def yaml_action_ids(platform_id: str, root: Path = ROOT) -> list[str]:
    path = root / "data" / "platforms" / f"{platform_id}.yaml"
    return [
        line.split("id:", 1)[1].strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.startswith("  - id:")
    ]


def supported_pairs() -> list[tuple[str, str]]:
    data = json.loads((ROOT / "data/integrations.json").read_text(encoding="utf-8"))
    pairs = []
    for item in data["platforms"]:
        if item["status"] != "supported":
            continue
        for action in yaml_action_ids(item["id"]):
            pairs.append((item["id"], action))
    return pairs


def cli_page(cli_ref: str) -> Path:
    slug = cli_ref.strip("/").rsplit("/", 1)[-1]
    return ROOT / "content" / "en" / "docs" / "reference" / "cli" / f"{slug}.md"


def split_command(command: str) -> tuple[list[str], list[str]]:
    """Return (subcommand words, flags) from a blowhorn command string."""
    body = command.strip()
    if not body.startswith("blowhorn "):
        return [], FLAG_RE.findall(command)
    words = []
    for token in body.split()[1:]:
        if token.startswith("-"):
            break
        words.append(token)
    return words, FLAG_RE.findall(command)


def shared_flag_ids(text: str | None = None) -> set[str]:
    raw = text
    if raw is None:
        raw = (ROOT / "content/en/docs/reference/cli/shared-flags.md").read_text(
            encoding="utf-8"
        )
    return set(FLAG_CELL_RE.findall(raw))


def cli_sections(text: str) -> dict[str, str]:
    parts = HEADING_RE.split(text)
    sections = {}
    title = TITLE_RE.search(parts[0])
    if title:
        sections[title.group(1).strip()] = parts[0]
    # split keeps captures: preamble, heading1, body1, heading2, body2, ...
    i = 1
    while i + 1 < len(parts):
        sections[parts[i].strip()] = parts[i + 1]
        i += 2
    return sections


def flags_in_section(section: str) -> set[str]:
    """Flags from that section's Flag table, not from Examples bash blocks."""
    flags: set[str] = set()
    in_table = False
    for line in section.splitlines():
        if line.startswith("| Flag"):
            in_table = True
            continue
        if in_table:
            if line.startswith("| ---"):
                continue
            if not line.startswith("|"):
                in_table = False
                continue
            flags.update(FLAG_CELL_RE.findall(line))
    return flags


def allowed_flags(page_text: str, heading: str) -> set[str]:
    sections = cli_sections(page_text)
    if heading not in sections:
        return set()
    body = sections[heading]
    flags = flags_in_section(body)
    if "shared flags" in body.lower():
        flags |= shared_flag_ids()
    return flags


def check_cli_available(platform: str, action: str, cli: dict) -> list[str]:
    problems: list[str] = []
    label = f"{platform} {action}"
    command = cli.get("command") or ""
    ref = cli.get("cliRef") or ""
    if not command.startswith("blowhorn "):
        problems.append(f"{label} CLI command does not start with blowhorn")
        return problems
    words, flags = split_command(command)
    if not words:
        problems.append(f"{label} CLI command has no subcommand")
        return problems
    page = cli_page(ref)
    slug = ref.strip("/").rsplit("/", 1)[-1]
    if words[0] != slug:
        problems.append(
            f"{label} subcommand {words[0]!r} does not match cliRef {ref}"
        )
    if not page.is_file():
        problems.append(f"{label} cliRef {ref} has no {page.relative_to(ROOT)}")
        return problems
    heading = " ".join(words)
    text = page.read_text(encoding="utf-8")
    allowed = allowed_flags(text, heading)
    if heading not in cli_sections(text):
        problems.append(
            f"{label} has no {heading!r} section on {page.relative_to(ROOT)}"
        )
        return problems
    for flag in flags:
        if flag not in allowed:
            problems.append(
                f"{label} uses {flag} which is not a {heading} flag "
                f"on {page.relative_to(ROOT)}"
            )
    return problems


def main() -> int:
    problems: list[str] = []
    vocab = json.loads((ROOT / "data/actions.json").read_text(encoding="utf-8"))
    examples = json.loads((ROOT / "data/action_examples.json").read_text(encoding="utf-8"))
    vocab_ids = [a["id"] for a in vocab["actions"]]
    vocab_set = set(vocab_ids)
    if len(vocab_ids) != len(vocab_set):
        problems.append("data/actions.json repeats an action id")

    order = examples.get("surfaces") or []
    if order != ["app", "cli", "rest", "mcp", "skill"]:
        problems.append(
            f"action_examples.surfaces is {order!r}, want ['app', 'cli', 'rest', 'mcp', 'skill']"
        )

    pairs = supported_pairs()
    pair_set = set(pairs)
    seen = set()
    for ex in examples["examples"]:
        key = (ex["platform"], ex["action"])
        if key in seen:
            problems.append(f"duplicate example for {key[0]} {key[1]}")
        seen.add(key)
        if ex["action"] not in vocab_set:
            problems.append(
                f"example {key[0]} {key[1]} uses an action id not in data/actions.json"
            )
        if key not in pair_set:
            problems.append(
                f"example {key[0]} {key[1]} is not a supported platform action"
            )
        blob = json.dumps(ex, ensure_ascii=False)
        if EM_DASH in blob:
            problems.append(f"example {key[0]} {key[1]} contains an em dash")
        cli = ex["surfaces"]["cli"]
        if cli["status"] == "available":
            problems.extend(check_cli_available(key[0], key[1], cli))
        shot = ex["surfaces"]["app"].get("screenshot") or ""
        expected = f"assets/docs/actions/{ex['platform']}/{ex['action']}.png"
        if shot != expected:
            problems.append(
                f"{key[0]} {key[1]} screenshot is {shot!r}, want {expected}"
            )

    for platform, action in pairs:
        if action not in vocab_set:
            problems.append(
                f"data/platforms/{platform}.yaml action {action} is not in data/actions.json"
            )
        if (platform, action) not in seen:
            problems.append(
                f"missing action_examples entry for {platform} {action}"
            )

    for item in problems:
        print(f"actions: {item}", file=sys.stderr)
    print(f"checked {len(pairs)} supported action(s), {len(problems)} broken")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
