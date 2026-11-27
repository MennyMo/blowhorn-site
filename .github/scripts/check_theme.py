#!/usr/bin/env python3
"""Fail if the built site dropped the theme contract.

The public homepage theme is data/themes.json default, overridden by
content/en/_index.md front matter theme: when set. Reveille is a look kept
as a preview (front matter theme: reveille) and via ?theme=, which swaps the
token layer only, not homepage layout. /home-reveille/ is no longer built
(build: render: never, #410); when it is built again, its page is checked.

A theme is tokens, CSS and layout partials that read the same data and
content. Reveille copy is the site's copy. The only approved per-theme
content file is content/en/home-reveille.md (today's homepage, kept as a
preview). A new home-signal.md or other theme-named page fails this check.

Activity and platform counts in copy must match supported rows in
data/integrations.json plus actions in data/platforms/<id>.yaml, and each
figure must be wrapped in a data-count-* span. The home page and
/integrations/ show the action count only and never a coming-soon count. The
home page links to /integrations/, which holds the platform map. That section
must ship JS that calls selectTab with defaultPlatTab when the URL has no
matching hash, so JS enhancement cannot leave all four panels stacked.
/integrations/ shows each category heading and each of its platform cards
once (catalog_duplicate_problems, #784): the map's By type panel points at
the catalog's sections instead of listing them again.

No platform-availability "Coming soon" label may return: the catalog, the
action matrix, the docs platform pages and the docs all-actions table are
scanned for it (check_platform_labels), and the showcase page's "Where it
works" section is scanned too. The built home page (and the Reveille preview)
is scanned for a returned split as well (check_home_soon_split): no "Coming
soon" group heading, and no "Coming soon" label on a listed platform or right
beside one. The home page keeps its out-of-scope "coming soon" copy, so it is
not scanned with the blanket match the platform pages get. The site's own copy
is scanned at the source
as well (check_platform_soon_copy): no sentence in content/en/ outside the
synced docs, or in data/, may name a platform data/integrations.json lists
and call it coming soon, and no data or front matter record (a table row,
an FAQ entry) may name one in one field and say "Coming soon" in another,
so a compare page's Networks row or an FAQ answer cannot keep one after the
platform ships. Other "coming soon" copy stays out
of scope: team invites, the Windows waitlist and /coming-soon/thanks/, the
REST API and Risk Profile, which name no platform.

Blowhorn's networks are never counted either (check_countable_network_copy):
"eight networks" or "seven fronts" in site copy fails, so a new platform
never leaves a stale count. Nor are they listed as a closed set
(check_open_network_lists): a sentence naming all of them, or all but one,
must end the list with "and more", so it stays true when one ships.

Usage: check_theme.py BUILD_DIR
"""

import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]

COUNT_ATTRS = ("platforms", "activities", "soon")
APPROVED_THEME_CONTENT = frozenset({"content/en/home-reveille.md"})


def front_matter_theme(path: Path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    for line in text[3:end].splitlines():
        stripped = line.strip()
        if stripped.startswith("theme:"):
            return stripped.split(":", 1)[1].strip().strip("\"'")
    return None


def expected_home_theme():
    themes = json.loads((ROOT / "data/themes.json").read_text(encoding="utf-8"))
    override = front_matter_theme(ROOT / "content/en/_index.md")
    return override or themes["default"]


def yaml_action_ids(platform_id: str):
    yaml_path = ROOT / "data" / "platforms" / f"{platform_id}.yaml"
    return [
        line.split("id:", 1)[1].strip()
        for line in yaml_path.read_text(encoding="utf-8").splitlines()
        if line.startswith("  - id:")
    ]


def theme_ids():
    data = json.loads((ROOT / "data/themes.json").read_text(encoding="utf-8"))
    return [theme["id"] for theme in data["themes"]]


HOME_SIGNAL_JS = ROOT / "assets/js/home-signal.js"
HOME_SIGNAL_HARNESS = Path(__file__).resolve().parent / "home_signal_harness.js"


def run_platforms_js(scenario: dict, script: Path = HOME_SIGNAL_JS) -> dict:
    """Run home-signal.js in home_signal_harness.js's fake DOM and return what
    the platforms section shows: selected tab, visible panels, aria-selected."""
    result = subprocess.run(
        ["node", str(HOME_SIGNAL_HARNESS), str(script), json.dumps(scenario)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"home-signal.js harness failed: {result.stderr.strip()}")
    return json.loads(result.stdout)


def platforms_scenario(**extra) -> dict:
    """The platforms tabs as data/integrations.json renders them."""
    data = json.loads((ROOT / "data/integrations.json").read_text(encoding="utf-8"))
    scenario = {
        "tabs": [t["id"] for t in data["treatments"]],
        "on": data["defaultTreatment"],
    }
    scenario.update(extra)
    return scenario


def platforms_default_problems(script: Path = HOME_SIGNAL_JS) -> list:
    """With no hash, the script must show exactly the default treatment's panel."""
    scenario = platforms_scenario()
    want = scenario["on"]
    try:
        got = run_platforms_js(scenario, script)
    except (OSError, RuntimeError) as err:
        return [str(err)]
    visible = sorted(k for k, v in got["panels"].items() if v)
    problems = []
    if got["tab"] != want or got["ariaSelected"] != [want]:
        problems.append(f"home-signal.js selects {got['tab']!r} with no hash, want {want!r}")
    if visible != [want]:
        problems.append(f"home-signal.js shows panels {visible} with no hash, want [{want!r}]")
    return problems


def extra_theme_content(root=ROOT):
    """Content files named for a theme, other than the approved Reveille preview."""
    ids = theme_ids()
    extras = []
    content = root / "content"
    if not content.is_dir():
        return extras
    for path in content.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel in APPROVED_THEME_CONTENT:
            continue
        stem = path.stem
        parts = path.relative_to(content).parts
        for tid in ids:
            if stem == f"home-{tid}" or stem.endswith(f"-{tid}") or tid in parts:
                extras.append(rel)
                break
    return extras


def counts():
    data = json.loads((ROOT / "data/integrations.json").read_text(encoding="utf-8"))
    platforms = 0
    activities = 0
    for item in data["platforms"]:
        if item["status"] == "supported":
            platforms += 1
            yaml_path = ROOT / "data" / "platforms" / f"{item['id']}.yaml"
            if yaml_path.is_file():
                activities += len(yaml_action_ids(item["id"]))
    return platforms, activities


class AttrCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.html_theme = None
        self.ids = set()
        self.text = []
        self.counts = {name: [] for name in COUNT_ATTRS}
        self._count_key = None
        self._count_depth = 0
        self._count_buf = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.html_theme = attrs.get("data-theme")
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        key = None
        for name in COUNT_ATTRS:
            if f"data-count-{name}" in attrs:
                key = name
                break
        if key is not None:
            self._count_key = key
            self._count_depth = 1
            self._count_buf = []
        elif self._count_key is not None:
            self._count_depth += 1

    def handle_endtag(self, tag):
        if self._count_key is None:
            return
        self._count_depth -= 1
        if self._count_depth <= 0:
            self.counts[self._count_key].append("".join(self._count_buf).strip())
            self._count_key = None
            self._count_buf = []

    def handle_data(self, data):
        self.text.append(data)
        if self._count_key is not None:
            self._count_buf.append(data)


def parse(path: Path) -> AttrCollector:
    collector = AttrCollector()
    collector.feed(path.read_text(encoding="utf-8"))
    return collector


def check_counts(page: AttrCollector, want, label, problems, names=COUNT_ATTRS):
    platforms, activities = want
    expected = {
        "platforms": str(platforms),
        "activities": str(activities),
    }
    for name, value in expected.items():
        if name not in names:
            continue
        found = page.counts[name]
        if not found:
            problems.append(f"{label} is missing data-count-{name}")
            continue
        for text in found:
            if text != value:
                problems.append(
                    f"{label} data-count-{name} is {text!r}, want {value}"
                )


PLATFORM_LABEL_RE = re.compile(r"coming[ -]soon", re.I)
# The action-example tabs carry out-of-scope "coming soon" placeholders
# (the REST API note, "Screenshot coming soon"); strip them before
# scanning, so the guard only sees platform-availability labels.
TABS_SOON_RE = re.compile(r'<div class="tabs-soon">.*?</div>', re.S)


def without_example_placeholders(html: str) -> str:
    return TABS_SOON_RE.sub("", html)


def check_platform_labels(build_dir: Path, root: Path) -> list[str]:
    """Fail if a platform-availability "Coming soon" label returns on a
    platform surface. Scoped to the pages that list platforms, so the
    out-of-scope "coming soon" copy (team invites, the Windows waitlist,
    the REST API, compare pages) does not trip it."""
    problems: list[str] = []
    data = json.loads((root / "data/integrations.json").read_text(encoding="utf-8"))
    pages = [
        "integrations/index.html",
        "integrations/actions/index.html",
        "docs/index.html",
        "docs/reference/platforms/index.html",
        "docs/reference/platforms/actions/index.html",
    ]
    for item in data["platforms"]:
        pages.append(f"docs/reference/platforms/{item['id']}/index.html")
    for rel in pages:
        path = build_dir / rel
        if not path.is_file():
            problems.append(f"platform label guard: {rel} was not built")
            continue
        if PLATFORM_LABEL_RE.search(without_example_placeholders(path.read_text(encoding="utf-8"))):
            problems.append(f"/{rel} shows a platform-availability 'Coming soon' label")
    showcase = build_dir / "showcase/index.html"
    if showcase.is_file():
        html = showcase.read_text(encoding="utf-8")
        match = re.search(
            r'<section[^>]*aria-labelledby="works-title"[^>]*>(.*?)</section>',
            html,
            re.S,
        )
        if match is None:
            problems.append("/showcase/index.html lost its Where it works section")
        elif PLATFORM_LABEL_RE.search(match.group(1)):
            problems.append("/showcase/index.html splits supported from coming-soon platforms")
    return problems


# One sentence of copy: a line break or a full stop ends it.
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n")
# A status with no subject of its own, such as a table cell's "Coming soon".
BARE_SOON_RE = re.compile(r"\W*coming[ -]soon\W*", re.I)


def platform_names(root: Path) -> list[str]:
    """Every name a listed platform goes by in copy: its YAML or catalog
    name, and that name without a parenthetical ("X (Twitter)" is also X)."""
    data = json.loads((root / "data/integrations.json").read_text(encoding="utf-8"))
    names: set[str] = set()
    for item in data["platforms"]:
        name = item.get("name")
        yaml_path = root / "data" / "platforms" / f"{item['id']}.yaml"
        if yaml_path.is_file():
            name = yaml.safe_load(yaml_path.read_text(encoding="utf-8")).get("name") or name
        if not name:
            continue
        names.add(name)
        names.add(re.sub(r"\s*\(.*?\)", "", name).strip())
    return sorted(names)


def copy_documents(path: Path) -> tuple[list, str]:
    """A source file as its structured documents (JSON or YAML data, a
    page's JSON or YAML front matter) and its Markdown body prose."""
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return [json.loads(text)], ""
    if path.suffix == ".yaml":
        return [yaml.safe_load(text)], ""
    if text.startswith("{"):
        front, end = json.JSONDecoder().raw_decode(text)
        return [front], text[end:]
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end >= 0:
            return [yaml.safe_load(text[3:end])], text[end + 4 :]
    return [], text


def record_parts(node, strings: list[str], nested: list) -> None:
    """A record's strings are its own fields and those of the mappings it
    holds; each item of a list it holds is a record of its own."""
    if isinstance(node, str):
        strings.append(node)
    elif isinstance(node, dict):
        for value in node.values():
            record_parts(value, strings, nested)
    elif isinstance(node, list):
        nested.extend(node)


def soon_records(document, names_platform) -> list[str]:
    """Judge each record (the document, and every list item in it) as one
    unit: fail a sentence that names a platform and calls it coming soon,
    and a bare "Coming soon" when another field of its record names a
    platform, such as a compare row whose feature lists the platforms and
    whose Blowhorn cell says "Coming soon"."""
    found: list[str] = []
    pending = [document]
    while pending:
        strings: list[str] = []
        record_parts(pending.pop(0), strings, pending)
        statuses, subjects = [], []
        for text in strings:
            sentences = [s.strip() for s in SENTENCE_SPLIT_RE.split(text)]
            found += [s for s in sentences if PLATFORM_LABEL_RE.search(s) and names_platform(s)]
            bare = any(BARE_SOON_RE.fullmatch(s) for s in sentences)
            (statuses if bare else subjects).append(text)
        named = [text for text in subjects if names_platform(text)]
        if statuses and named:
            found.append(f"{named[0].strip()} / {statuses[0].strip()}")
    return found


def check_platform_soon_copy(root: Path) -> list[str]:
    """Fail site copy that names a listed platform and calls it coming
    soon. Scans content/en/ (the synced docs are the product's and are
    guarded on the built pages by check_platform_labels) and every JSON and
    YAML file under data/. Structured data and front matter are judged a
    record at a time (soon_records); Markdown body prose a sentence at a
    time."""
    names = platform_names(root)
    name_res = [re.compile(rf"(?<![\w-]){re.escape(n)}(?![\w-])") for n in names]

    def names_platform(text: str) -> bool:
        return any(rx.search(text) for rx in name_res)

    content = root / "content" / "en"
    docs = content / "docs"
    files = [
        path
        for path in sorted(content.rglob("*.md"))
        if docs not in path.parents
    ]
    data = root / "data"
    files += sorted(data.rglob("*.json")) + sorted(data.rglob("*.yaml"))
    problems: list[str] = []
    for path in files:
        documents, body = copy_documents(path)
        found = [hit for document in documents for hit in soon_records(document, names_platform)]
        found += [
            s.strip()
            for s in SENTENCE_SPLIT_RE.split(body)
            if PLATFORM_LABEL_RE.search(s) and names_platform(s)
        ]
        rel = path.relative_to(root)
        problems += [
            f"{rel} calls a listed platform coming soon: {hit[:160]!r}" for hit in found
        ]
    return problems



# The home page is scanned on its built HTML for a returned Coming soon split.
# It cannot use check_platform_labels' blanket match: the home page rightly
# says "coming soon" about team invites and the REST API, which are not
# platform availability. So it fails only a Coming soon group heading, and a
# Coming soon label that names a listed platform or sits right beside one.
HOME_PAGES = ("index.html", "home-reveille/index.html")
SCRIPT_STYLE_RE = re.compile(r"<(script|style)\b.*?</\1>", re.S | re.I)
HEADING_RE = re.compile(r"<h([1-6])\b[^>]*>(.*?)</h\1>", re.S | re.I)
BLOCK_BREAK_RE = re.compile(
    r"</?(?:p|li|ul|ol|h[1-6]|div|section|article|header|footer|tr|td|th|dd|dt|figcaption|br)\b[^>]*>",
    re.I,
)


def home_blocks(html: str) -> list[str]:
    """The built page's copy as a reader sees it, one entry per block."""
    html = SCRIPT_STYLE_RE.sub("", without_example_placeholders(html))
    return [b for b in (" ".join(plain_text(b).split()) for b in BLOCK_BREAK_RE.split(html)) if b]


def home_soon_problems(rel: str, html: str, names_platform) -> list[str]:
    problems = []
    cleaned = SCRIPT_STYLE_RE.sub("", without_example_placeholders(html))
    for match in HEADING_RE.finditer(cleaned):
        heading = " ".join(plain_text(match.group(2)).split())
        if PLATFORM_LABEL_RE.search(heading):
            problems.append(f"/{rel} has a Coming soon group heading: {heading[:120]!r}")
    blocks = home_blocks(html)
    for i, block in enumerate(blocks):
        if not PLATFORM_LABEL_RE.search(block):
            continue
        for sentence in SENTENCE_SPLIT_RE.split(block):
            if PLATFORM_LABEL_RE.search(sentence) and names_platform(sentence):
                problems.append(f"/{rel} calls a listed platform coming soon: {sentence.strip()[:120]!r}")
        if BARE_SOON_RE.fullmatch(block):
            beside = blocks[max(i - 1, 0):i] + blocks[i + 1:i + 2]
            for neighbour in beside:
                if names_platform(neighbour) and not PLATFORM_LABEL_RE.search(neighbour):
                    problems.append(
                        f"/{rel} has a Coming soon label beside a listed platform: {neighbour[:120]!r}"
                    )
    return problems


def check_home_soon_split(build_dir: Path, root: Path) -> list[str]:
    """Fail a Coming soon split on the built home page: a group heading, or a
    label on a listed platform. Out-of-scope copy (team invites, the REST API)
    that names no platform stays allowed."""
    name_res = [
        re.compile(rf"(?<![\w-]){re.escape(n)}(?![\w-])") for n in platform_names(root)
    ]

    def names_platform(text: str) -> bool:
        return any(rx.search(text) for rx in name_res)

    problems: list[str] = []
    for rel in HOME_PAGES:
        path = build_dir / rel
        if not path.is_file():
            continue
        problems.extend(home_soon_problems(rel, path.read_text(encoding="utf-8"), names_platform))
    return problems


CATALOG_CARD_RE = re.compile(
    r'<li\b[^>]*\bclass="card integration-card\b[^"]*"[^>]*\bdata-plat-id="([^"]+)"', re.I
)


def catalog_duplicate_problems(html: str, categories: list) -> list[str]:
    """Issue #784: /integrations/ shows each category heading ("Your
    browser") and each of its platform cards once. The map's By type panel
    points at the catalog's sections; it must not list them a second time,
    and data/integrations.json must not list a category or platform twice."""
    problems = []
    cleaned = SCRIPT_STYLE_RE.sub("", html)
    headings = [" ".join(plain_text(m.group(2)).split()) for m in HEADING_RE.finditer(cleaned)]
    cards = CATALOG_CARD_RE.findall(cleaned)
    for group in categories:
        found = headings.count(group["name"])
        if found != 1:
            problems.append(
                f"/integrations/index.html has {found} {group['name']!r} headings, want 1"
            )
        for pid in group["platforms"]:
            found = cards.count(pid)
            if found != 1:
                problems.append(
                    f"/integrations/index.html has {found} {pid!r} catalog cards, want 1"
                )
    return problems


NUMBER_WORDS = (
    "two three four five six seven eight nine ten eleven twelve thirteen "
    "fourteen fifteen sixteen"
).split()
# Blowhorn's networks are never counted: "seven networks", "8 fronts" go stale
# the day a platform ships. "seven tabs" and "all seven" are not matches.
COUNTED_NETWORKS_RE = re.compile(
    rf"\b(?:{'|'.join(NUMBER_WORDS)}|\d+)\s+(?:networks|fronts)\b", re.I
)


# Counts that are not Blowhorn's: a competitor's own figure, and the demo
# page's four-act scene. Each is (path, phrase).
COUNTED_NETWORKS_ALLOWED = {
    ("content/en/compare/blotato.md", "9 networks"),
    ("content/en/compare/publer.md", "13 networks"),
    ("content/en/compare/buffer.md", "four networks"),
    ("layouts/demo.html", "four fronts"),
}


def check_countable_network_copy(root: Path) -> list[str]:
    """Fail marketing copy that counts networks ("eight networks", "seven
    fronts"). Scans content/en/ outside the synced docs, data/*.json and
    *.yaml, and layouts/."""
    content = root / "content" / "en"
    docs = content / "docs"
    files = [p for p in sorted(content.rglob("*.md")) if docs not in p.parents]
    data = root / "data"
    files += sorted(data.rglob("*.json")) + sorted(data.rglob("*.yaml"))
    files += sorted((root / "layouts").rglob("*.html"))
    problems: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(root).as_posix()
        for m in COUNTED_NETWORKS_RE.finditer(text):
            if (rel, m.group(0).lower()) in COUNTED_NETWORKS_ALLOWED:
                continue
            line = text.count("\n", 0, m.start()) + 1
            problems.append(
                f"{rel}:{line} counts networks ({m.group(0)!r}); "
                "never count them, say 'every network you post on' or 'and more' "
                "(docs/action-examples.md)"
            )
    return problems


# What makes a list of networks read as open, attached to a network name:
# right after one, "Slack, YouTube and more", "... plus many more",
# "+ many more"; or right before one, "such as LinkedIn, X ...".
OPEN_LIST_END_RE = re.compile(
    r",?\s*(?:(?:and|or|plus)\s+(?:many\s+)?more|\+\s*many\s+more)\b",
    re.I,
)
OPEN_LIST_START_RE = re.compile(r"\bsuch\s+as\s*$", re.I)
TAG_RE = re.compile(r"<[^>]*>")
MD_LINK_RE = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
MD_MARK_RE = re.compile(r"\*+|`+|(?<!\w)_+|_+(?!\w)")

# Sentences that name the networks as a record of something fixed, not as
# Blowhorn's reach: a film's own captions and the logo loop's frames. Each is
# (path, a phrase from the sentence).
ALL_NETWORK_LISTS_ALLOWED = {
    ("data/hero.json", "Major Blowhorn's one call lands on"),
    (
        "content/en/resources/videos/getting-started/battalion-thunder.md",
        "Major Blowhorn's one call lands on",
    ),
    ("data/integrations.json", "A row of platform logos slides by"),
}


def supported_network_names(root: Path) -> list[str]:
    """The networks Blowhorn acts on: every data/platforms/<id>.yaml, by its
    name without a parenthetical ("X (Twitter)" is X in copy)."""
    names = []
    for path in sorted((root / "data" / "platforms").glob("*.yaml")):
        name = yaml.safe_load(path.read_text(encoding="utf-8")).get("name")
        if name:
            names.append(re.sub(r"\s*\(.*?\)", "", name).strip())
    return names


def plain_text(text: str) -> str:
    """Copy as a reader sees it: HTML tags, Markdown links and emphasis
    reduced to their text."""
    return MD_MARK_RE.sub("", MD_LINK_RE.sub(r"\1", TAG_RE.sub(" ", text)))


def copy_sentences(path: Path) -> list[str]:
    """Every sentence of a source file's copy, as plain text: the strings of
    its structured data or front matter, its Markdown body, or a layout's
    text."""
    if path.suffix == ".html":
        strings = [path.read_text(encoding="utf-8")]
    else:
        documents, body = copy_documents(path)
        strings = [body]
        pending = list(documents)
        while pending:
            node = pending.pop()
            if isinstance(node, str):
                strings.append(node)
            elif isinstance(node, dict):
                pending.extend(node.values())
            elif isinstance(node, list):
                pending.extend(node)
    return [s.strip() for text in strings for s in SENTENCE_SPLIT_RE.split(plain_text(text)) if s.strip()]


def check_open_network_lists(root: Path) -> list[str]:
    """Fail a sentence that lists all of Blowhorn's networks, or all but one,
    as a closed set. Such a list is stale the day a platform ships (it was
    how YouTube went missing from "plus LinkedIn, X, Reddit and Bluesky"), so
    it must read as open: "..., YouTube and more" (docs/action-examples.md
    step 3). Curated lists, such as the developer networks or the analytics
    networks, name fewer and are not matched. Scans what
    check_countable_network_copy scans."""
    names = supported_network_names(root)
    name_res = {n: re.compile(rf"(?<![\w-]){re.escape(n)}(?![\w-])") for n in names}
    content = root / "content" / "en"
    docs = content / "docs"
    files = [p for p in sorted(content.rglob("*.md")) if docs not in p.parents]
    data = root / "data"
    files += sorted(data.rglob("*.json")) + sorted(data.rglob("*.yaml"))
    files += sorted((root / "layouts").rglob("*.html"))
    problems: list[str] = []
    for path in files:
        rel = path.relative_to(root).as_posix()
        allowed = [phrase for (p, phrase) in ALL_NETWORK_LISTS_ALLOWED if p == rel]
        for sentence in copy_sentences(path):
            spans = {n: [m.span() for m in name_res[n].finditer(sentence)] for n in names}
            missing = [n for n in names if not spans[n]]
            if len(missing) > 1:
                continue
            if any(
                OPEN_LIST_END_RE.match(sentence, end) or OPEN_LIST_START_RE.search(sentence, 0, start)
                for found in spans.values()
                for start, end in found
            ):
                continue
            if any(phrase in sentence for phrase in allowed):
                continue
            gap = f" and leaves out {missing[0]}" if missing else ""
            problems.append(
                f"{rel} lists Blowhorn's networks as a closed set{gap}: "
                f"{sentence[:160]!r}; name every network and end the list "
                "with 'and more' (docs/action-examples.md)"
            )
    return problems


def main(root: Path) -> int:
    problems = []
    want_theme = expected_home_theme()
    want_counts = counts()
    for rel in extra_theme_content():
        problems.append(
            f"theme-specific content file {rel}; themes differ by tokens, "
            "CSS and layout partials only. Approved exception: content/en/home-reveille.md"
        )

    index = root / "index.html"
    if not index.is_file():
        problems.append("/index.html is not published")
    else:
        page = parse(index)
        html = index.read_text(encoding="utf-8")
        if page.html_theme != want_theme:
            problems.append(
                f"/index.html data-theme is {page.html_theme!r}, want {want_theme}"
            )
        if "Priced per voice, not per channel." not in html:
            problems.append("/index.html is missing the pricing headline")
        # The home page never splits supported from planned platforms: it
        # shows the action count only, and no coming-soon figure.
        check_counts(page, want_counts, "/index.html", problems, names=("activities",))
        if page.counts["soon"]:
            problems.append("/index.html shows a coming-soon count (data-count-soon)")
        if 'data-demo-card="github"' in html:
            problems.append("/index.html demo posts to GitHub")
        if ">Say it once. Say it everywhere.<" in html:
            problems.append("/index.html still uses the old platforms headline")
        if "Write it once. Deploy to every front." not in html:
            problems.append("/index.html lost the Major card headline")
        if "Tab after tab. One post. Somebody call a medic." in html:
            problems.append("/index.html still uses the old Major card line")
        # The interactive platform map lives on /integrations/; the home
        # page keeps the clip and links there.
        if 'data-plat-panel="' in html:
            problems.append("/index.html still carries the platform map; it lives on /integrations/")
        if 'href="/integrations/"' not in html:
            problems.append("/index.html does not link to /integrations/")

    # The preview is unpublished (build: render: never); check it only when built.
    reveille = root / "home-reveille/index.html"
    if reveille.is_file():
        page = parse(reveille)
        html = reveille.read_text(encoding="utf-8")
        if page.html_theme != "reveille":
            problems.append(
                f"/home-reveille/index.html data-theme is {page.html_theme!r}, want reveille"
            )
        if "Say it once. Say it everywhere." not in html:
            problems.append("/home-reveille/index.html lost today's platforms headline")
        if 'id="how"' not in html or "army" not in html:
            problems.append("/home-reveille/index.html lost the army / how section")

    catalog = root / "integrations/index.html"
    if not catalog.is_file():
        problems.append("/integrations/index.html is not published")
    else:
        page = parse(catalog)
        if "integrations-title" not in page.ids:
            problems.append("/integrations/index.html#integrations-title is gone")
        if "action-filter" not in page.ids:
            problems.append("/integrations/index.html#action-filter is gone")
        html = catalog.read_text(encoding="utf-8")
        check_counts(page, want_counts, "/integrations/index.html", problems, names=("activities",))
        if page.counts["soon"]:
            problems.append("/integrations/index.html shows a coming-soon count (data-count-soon)")
        panels = html.count('data-plat-panel="')
        if panels != 4:
            problems.append(f"/integrations/index.html has {panels} platform panels, want 4")
        integrations = json.loads((ROOT / "data/integrations.json").read_text(encoding="utf-8"))
        problems.extend(catalog_duplicate_problems(html, integrations["categories"]))
        problems.extend(platforms_default_problems())

    problems.extend(check_platform_labels(root, ROOT))
    problems.extend(check_home_soon_split(root, ROOT))
    problems.extend(check_platform_soon_copy(ROOT))
    problems.extend(check_countable_network_copy(ROOT))
    problems.extend(check_open_network_lists(ROOT))

    for item in problems:
        print(f"theme: {item}", file=sys.stderr)
    print(f"checked theme contract, {len(problems)} broken")
    return 1 if problems else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: check_theme.py BUILD_DIR", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(Path(sys.argv[1])))
