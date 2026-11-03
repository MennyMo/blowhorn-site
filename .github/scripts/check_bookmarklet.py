#!/usr/bin/env python3
"""Fail if the download page's bookmarklet differs from the one in the docs.

data/bookmarklet.json feeds the card on /download/; the docs page shows the
same code under "Capture a page from the browser". They must stay identical.

Usage: check_bookmarklet.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "content/en/docs/how-to/publish/manage-the-content-worksheet.md"


def main() -> int:
    code = json.loads((ROOT / "data/bookmarklet.json").read_text(encoding="utf-8"))["code"]
    match = re.search(r"^```\n(javascript:.*)\n```$", DOC.read_text(encoding="utf-8"), re.M)
    if not match:
        print(f"{DOC.relative_to(ROOT)}: no javascript: code block found")
        return 1
    if match.group(1) != code:
        print("data/bookmarklet.json differs from the code block in " + str(DOC.relative_to(ROOT)))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
