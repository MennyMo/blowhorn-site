#!/usr/bin/env python3
"""Fail if a published Resources piece breaks the column or tip-video rules.

Two standing rules are enforced at the source, before any build:

- Columns (blowhorn #1555): every published article and every published
  video carries exactly one `column` front-matter field, one of
  desk-of-the-general, boot-camp, from-the-field. The feeds carry the
  column as a "column:<slug>" category (check_feeds.py verifies the
  built output); this check verifies the source, including pieces the
  feeds do not carry.
- Tip videos (blowhorn #1554): a published tip (an article tagged
  "tips") never ships without a video. Its front matter carries a
  `video` map - mp4, webm, poster, duration - whose files exist under
  static/, and a unique positive `tipOrder`, its place in the desktop
  app's bundled curriculum.

Usage: check_tips.py [REPO_ROOT]   (default: the repository root)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

COLUMNS = ("desk-of-the-general", "boot-camp", "from-the-field")
ARTICLES = Path("content/en/resources/articles")
VIDEOS = Path("content/en/resources/videos")
DURATION = re.compile(r"^\d+:\d{2}$")


def front_matter(text: str) -> str | None:
    parts = text.split("---", 2)
    if len(parts) < 3 or parts[0].strip():
        return None
    return parts[1]


def field(head: str, name: str) -> str | None:
    match = re.search(rf"(?m)^{name}:\s*\"?([^\"\n]+)\"?\s*$", head)
    return match.group(1).strip() if match else None


def is_draft(head: str) -> bool:
    return (field(head, "draft") or "").lower() == "true"


def tags_of(head: str) -> list[str]:
    match = re.search(r"(?m)^tags:\s*\[([^\]]*)\]", head)
    if not match:
        return []
    return [t.strip().strip('"') for t in match.group(1).split(",") if t.strip()]


def video_block(head: str) -> dict[str, str]:
    block: dict[str, str] = {}
    in_video = False
    for line in head.splitlines():
        if re.match(r"^video:\s*$", line):
            in_video = True
            continue
        if in_video:
            match = re.match(r"^\s+(mp4|webm|poster|duration):\s*\"?([^\"\n]+)\"?\s*$", line)
            if match:
                block[match.group(1)] = match.group(2).strip()
            elif line and not line.startswith((" ", "#")):
                in_video = False
    return block


def check(root: Path) -> list[str]:
    problems: list[str] = []
    tip_orders: dict[int, str] = {}

    def require_column(path: Path, head: str) -> None:
        column = field(head, "column")
        if column not in COLUMNS:
            problems.append(
                f"{path}: published pieces need column, one of {', '.join(COLUMNS)}; found {column!r}"
            )

    articles = root / ARTICLES
    for path in sorted(articles.glob("*.md")):
        head = front_matter(path.read_text())
        if head is None or is_draft(head) or path.name.startswith(("template", "_")):
            continue
        require_column(path.relative_to(root), head)
        if "tips" not in tags_of(head):
            continue
        rel = path.relative_to(root)
        order_raw = field(head, "tipOrder")
        try:
            order = int(order_raw) if order_raw is not None else None
        except ValueError:
            order = None
        if order is None or order < 1:
            problems.append(f"{rel}: a tip needs a positive integer tipOrder; found {order_raw!r}")
        elif order in tip_orders:
            problems.append(f"{rel}: tipOrder {order} is already used by {tip_orders[order]}")
        else:
            tip_orders[order] = str(rel)
        video = video_block(head)
        for key in ("mp4", "webm", "poster", "duration"):
            if not video.get(key):
                problems.append(f"{rel}: a tip never publishes without a video - missing video.{key} (#1554)")
        for key in ("mp4", "webm", "poster"):
            target = video.get(key)
            if target and not (root / "static" / target).is_file():
                problems.append(f"{rel}: video.{key} points at {target}, which is not under static/")
        if video.get("duration") and not DURATION.match(video["duration"]):
            problems.append(f"{rel}: video.duration must be m:ss; found {video['duration']!r}")

    videos = root / VIDEOS
    for path in sorted(videos.rglob("*.md")):
        if path.name == "_index.md" or path.name.startswith("template"):
            continue
        head = front_matter(path.read_text())
        if head is None or is_draft(head):
            continue
        require_column(path.relative_to(root), head)

    return problems


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parents[2]
    if not (root / ARTICLES).is_dir():
        print(f"check_tips: {root / ARTICLES} is not a directory", file=sys.stderr)
        return 2
    problems = check(root)
    for problem in problems:
        print(f"::error::{problem}")
    if problems:
        return 1
    print("check_tips: every published piece has a column, and every tip has a video")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
