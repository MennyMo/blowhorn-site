#!/usr/bin/env python3
"""Fail if a platform product page drifts from its data or its contract.

Platform pages (docs/platform-pages.md) render one record of
data/platform_pages.json (schemas/platform_page.schema.json, which make
check-schemas validates with ajv) through layouts/platform-page.html.

--source checks the data alone (run by make check-schemas), the references
JSON Schema cannot express:

- each record's platform is a supported row of data/integrations.json with a
  data/platforms/<id>.yaml, and its route is /preview/platforms/<id>/;
- each activity type names an action that YAML lists, ids are unique and no two
  types share an action; examples use a declared type, ids are unique, no four
  neighbours share a card variant (the rail shows up to four) and paper, the
  featured variant, is used at most once; breakdown kinds are unique and a limits
  item needs an action with limits;
- each record has exactly one content page (content/en/preview-platform-<id>.md)
  with layout platform-page, the same platform and url, noindex, exclude_search,
  sitemap disabled and build list never, and no other page uses the layout;
- hugo.toml keeps /preview/** out of llms.txt; no em dash anywhere in the data.

With a build directory it also checks each built page and runs its script:

- the page exists, is noindex, and its route is in no sitemap, llms.txt,
  llms-full.txt or search index, and no other built page links to it;
- <main> holds exactly one primary button, Start, to the download page; one
  radio per activity type in order, the first checked; one illustration, intent
  and Start context per type; the examples in order with their card variants;
  the breakdown collapsed, its rows the platform's actions in YAML order and its
  limits exactly the limited actions; no em dash and no browser brand in it;
- assets/js/platform-page.js, run through platform_page_harness.js against the
  built <main>: picking each type swaps every [data-pp-for] element and marks
  the bound rows; an example's preview selects its type, shows its sample and
  moves focus to the illustration; the rail pages by hand with aria-disabled
  ends, and under reduced motion nothing scrolls smoothly.

Usage: check_platform_pages.py --source
       check_platform_pages.py [BUILD_DIR]
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

from check_action_examples import yaml_action_ids

ROOT = Path(__file__).resolve().parents[2]
HARNESS = Path(__file__).resolve().parent / "platform_page_harness.js"
SCRIPT = Path("assets/js/platform-page.js")
EM_DASH = "—"
BRAND_RE = re.compile(r"Chrome|Safari|Firefox|\bMac\b|macOS|Outbox")
VARIANTS = {"paper": "card-paper", "field": "card-field", "plain": "card-plain", "stamp": "card-stamp"}
RAIL_WINDOW = 4
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
LLMS_EXCLUDE = "/preview/**"


# ---------- source ----------

def load_json(root: Path, rel: str) -> dict:
    return json.loads((root / rel).read_text(encoding="utf-8"))


def yaml_actions(root: Path, platform_id: str) -> list[dict] | None:
    """The action rows of data/platforms/<id>.yaml: id (from the shared
    yaml_action_ids) and the text of its limits, empty when it lists none."""
    path = root / "data" / "platforms" / f"{platform_id}.yaml"
    if not path.is_file():
        return None
    limits: dict[str, str] = {}
    current = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("  - id:"):
            current = line.split("id:", 1)[1].strip()
        elif line.startswith("    limits:") and current:
            limits[current] = line.split("limits:", 1)[1].strip()
    return [{"id": i, "limits": limits.get(i, "")} for i in yaml_action_ids(platform_id, root)]


def links_to(html: str, route: str) -> bool:
    """Whether html has an href to the route: absolute, with a host or a base
    path in front, relative, with or without the trailing slash, with or
    without a fragment or query."""
    path = re.escape(route.strip("/"))
    return bool(re.search(
        rf"""href=["'](?:[^"'#?]*/)?{path}/?(?:[#?][^"']*)?["']""", html, re.I))


def front_matter(path: Path) -> dict:
    """The flat keys of a page's YAML front matter, plus sitemap.disable and build.list."""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    out: dict = {}
    parent = ""
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, _, value = line.strip().partition(":")
        value = value.strip().strip("\"'")
        if line.startswith((" ", "\t")):
            out[f"{parent}.{key}"] = value
        else:
            parent = key
            out[key] = value
    return out


def platform_pages(root: Path) -> list[Path]:
    return sorted(
        p for p in (root / "content" / "en").rglob("*.md")
        if front_matter(p).get("layout") == "platform-page"
    )


def check_source(root: Path) -> list[str]:
    problems: list[str] = []
    raw = (root / "data" / "platform_pages.json").read_text(encoding="utf-8")
    if EM_DASH in raw:
        problems.append("data/platform_pages.json carries an em dash; use a hyphen")
    data = json.loads(raw)
    integrations = {p["id"]: p for p in load_json(root, "data/integrations.json")["platforms"]}
    vocab = {a["id"] for a in load_json(root, "data/actions.json")["actions"]}

    seen_platforms: set[str] = set()
    for rec in data.get("pages", []):
        pid = rec.get("platform", "")
        where = f"page {pid!r}"
        if pid in seen_platforms:
            problems.append(f"{where} appears twice")
        seen_platforms.add(pid)
        row = integrations.get(pid)
        if row is None:
            problems.append(f"{where}: {pid!r} is not in data/integrations.json")
            continue
        if row.get("status") != "supported":
            problems.append(f"{where}: {pid!r} is {row.get('status')!r}; only a supported platform gets a page")
        actions = yaml_actions(root, pid)
        if actions is None:
            problems.append(f"{where}: data/platforms/{pid}.yaml is missing")
            continue
        listed = [a["id"] for a in actions]
        if rec.get("route") != f"/preview/platforms/{pid}/":
            problems.append(f"{where}: route {rec.get('route')!r} must be /preview/platforms/{pid}/")

        type_ids: list[str] = []
        bound: list[str] = []
        for act in rec.get("activities", []):
            if act["id"] in type_ids:
                problems.append(f"{where}: activity id {act['id']!r} repeats")
            type_ids.append(act["id"])
            if act["action"] not in vocab:
                problems.append(f"{where}: activity {act['id']!r} names {act['action']!r}, not in data/actions.json")
            elif act["action"] not in listed:
                problems.append(f"{where}: activity {act['id']!r} names {act['action']!r}, which data/platforms/{pid}.yaml does not list")
            if act["action"] in bound:
                problems.append(f"{where}: two activities bind action {act['action']!r}")
            bound.append(act["action"])

        items = rec.get("examples", {}).get("items", [])
        example_ids: list[str] = []
        for i, ex in enumerate(items):
            if ex["activity"] not in type_ids:
                problems.append(f"{where}: example {ex['id']!r} uses undeclared activity {ex['activity']!r}")
            if ex["id"] in example_ids:
                problems.append(f"{where}: example id {ex['id']!r} repeats")
            example_ids.append(ex["id"])
            for other in items[i + 1:i + RAIL_WINDOW]:
                if other["variant"] == ex["variant"]:
                    problems.append(
                        f"{where}: examples {ex['id']!r} and {other['id']!r} are within {RAIL_WINDOW} of each other "
                        f"and share the {ex['variant']!r} card variant"
                    )
        papers = [ex["id"] for ex in items if ex.get("variant") == "paper"]
        if len(papers) > 1:
            problems.append(f"{where}: {len(papers)} paper examples ({', '.join(papers)}); paper is the one featured example")

        kinds: list[str] = []
        for item in rec.get("breakdown", {}).get("items", []):
            if item["kind"] in kinds:
                problems.append(f"{where}: breakdown kind {item['kind']!r} repeats")
            kinds.append(item["kind"])
            if item["kind"] == "limits" and not any(a["limits"] for a in actions):
                problems.append(f"{where}: a limits breakdown, but data/platforms/{pid}.yaml lists no limits")

        page = root / "content" / "en" / f"preview-platform-{pid}.md"
        if not page.is_file():
            problems.append(f"{where}: content/en/preview-platform-{pid}.md is missing")
            continue
        fm = front_matter(page)
        rel = page.relative_to(root)
        want = {
            "layout": "platform-page",
            "platform": pid,
            "url": rec.get("route"),
            "noindex": "true",
            "exclude_search": "true",
            "sitemap.disable": "true",
            "build.list": "never",
        }
        for key, value in want.items():
            if fm.get(key) != value:
                problems.append(f"{rel}: front matter {key} is {fm.get(key)!r}, want {value!r}")

    for page in platform_pages(root):
        pid = front_matter(page).get("platform", "")
        if pid not in seen_platforms:
            problems.append(f"{page.relative_to(root)} uses layout platform-page for {pid!r}, which has no record")

    hugo = (root / "hugo.toml").read_text(encoding="utf-8")
    if f'"{LLMS_EXCLUDE}"' not in hugo:
        problems.append(f'hugo.toml [params.llms] exclude must list "{LLMS_EXCLUDE}"')
    return problems


# ---------- built ----------

class Tree(HTMLParser):
    """The element tree of <main>, plus a few page-wide facts."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.main: dict | None = None
        self.stack: list[dict] = []
        self.robots = ""
        self.hrefs: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = {k: (v if v is not None else "") for k, v in attrs}
        if tag == "meta" and a.get("name") == "robots":
            self.robots = a.get("content", "")
        if "href" in a:
            self.hrefs.append(a["href"])
        if self.main is None and tag == "main":
            self.main = {"tag": tag, "attrs": a, "children": []}
            self.stack = [self.main]
            return
        if not self.stack:
            return
        el = {"tag": tag, "attrs": a, "children": []}
        self.stack[-1]["children"].append(el)
        if tag not in VOID:
            self.stack.append(el)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self.stack and tag not in VOID and self.stack[-1]["tag"] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        if not self.stack:
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]["tag"] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if self.stack:
            self.stack[-1]["children"].append(data)


def parse(path: Path) -> Tree:
    t = Tree()
    t.feed(path.read_text(encoding="utf-8"))
    t.close()
    return t


def walk(el: dict):
    yield el
    for c in el["children"]:
        if isinstance(c, dict):
            yield from walk(c)


def text(el: dict) -> str:
    return "".join(c if isinstance(c, str) else text(c) for c in el["children"])


def find(el: dict, attr: str, value: str | None = None) -> list[dict]:
    return [
        e for e in walk(el)
        if attr in e["attrs"] and (value is None or e["attrs"][attr] == value)
    ]


def classes(el: dict) -> list[str]:
    return el["attrs"].get("class", "").split()


def run_harness(tree: dict, scenario: dict, root: Path) -> list[dict]:
    node = shutil.which("node")
    if not node:
        raise RuntimeError("node is not on PATH; the platform page behaviour check needs it")
    out = subprocess.run(
        [node, str(HARNESS), str(root / SCRIPT)],
        input=json.dumps({"tree": tree, "scenario": scenario}),
        capture_output=True, text=True, check=False,
    )
    if out.returncode != 0:
        raise RuntimeError(f"platform_page_harness.js failed: {out.stderr.strip()}")
    return json.loads(out.stdout)


def check_behaviour(label: str, main: dict, rec: dict, actions: list[dict], root: Path) -> list[str]:
    problems: list[str] = []
    types = [a["id"] for a in rec["activities"]]
    action_of = {a["id"]: a["action"] for a in rec["activities"]}
    intents = {a["id"]: a["intent"] for a in rec["activities"]}
    examples = rec["examples"]["items"]
    # The stylesheet shows a whole number of cards (3 on desktop): 3 slides and 2 gaps fill the width.
    rail = {"width": 1000, "slide": 312, "gap": 32}
    edges = {i * (rail["slide"] + rail["gap"]) for i in range(len(examples))}

    steps = [{"choose": t} for t in types[1:]] + [{"choose": types[0]}]
    states = run_harness(main, {"rail": rail, "steps": steps}, root)
    first = states[0]
    if not first["enhanced"]:
        problems.append(f"{label}: the script did not enhance the page")
    for state, want in zip(states, [types[0]] + types[1:] + [types[0]]):
        if state["type"] != want or state["checked"] != [want]:
            problems.append(f"{label}: after choosing {want!r} the page shows {state['type']!r}, checked {state['checked']}")
        if set(state["shown"]) != {want}:
            problems.append(f"{label}: choosing {want!r} shows elements for {sorted(state['shown'])}")
        if set(state["hidden"]) != set(types) - {want}:
            problems.append(f"{label}: choosing {want!r} leaves {sorted(set(types) - {want} - set(state['hidden']))} visible")
        want_picked = [a["id"] for a in actions if a["id"] == action_of[want]]
        if sorted(set(state["picked"])) != want_picked:
            problems.append(f"{label}: choosing {want!r} marks rows {state['picked']}, want {want_picked}")
    for state, want in zip(states[1:], types[1:]):
        if state["announce"] != f"{next(a['label'] for a in rec['activities'] if a['id'] == want)}. {intents[want]}":
            problems.append(f"{label}: choosing {want!r} announces {state['announce']!r}")
    if first["tryShown"] != len(examples):
        problems.append(f"{label}: {first['tryShown']} of {len(examples)} example preview buttons shown")

    # An example's preview: its type, its sample, focus on the illustration.
    ex = examples[-1]
    for reduce, behaviour in ((False, "smooth"), (True, "auto")):
        s = run_harness(main, {"rail": rail, "reduce": reduce, "steps": [{"try": ex["id"]}]}, root)[-1]
        sample = s["samples"].get(ex["activity"], {})
        if s["type"] != ex["activity"]:
            problems.append(f"{label}: previewing {ex['id']!r} selects {s['type']!r}, want {ex['activity']!r}")
        if not sample.get("sampleShown") or sample.get("sampleText") != ex["sample"] or sample.get("originalsShown"):
            problems.append(f"{label}: previewing {ex['id']!r} does not put its sample in the illustration: {sample}")
        if "data-pp-stage" not in s["focus"].split():
            problems.append(f"{label}: previewing {ex['id']!r} leaves focus on {s['focus']!r}, not the illustration")
        if s["intoView"] != [behaviour]:
            problems.append(f"{label}: previewing with reduce={reduce} scrolls {s['intoView']}, want [{behaviour!r}]")

    # Picking a type by hand after a preview returns the default illustration.
    originals = {a["id"]: len(a["scene"]["text"]) for a in rec["activities"]}
    back = run_harness(main, {"rail": rail, "steps": [{"try": ex["id"]}, {"choose": ex["activity"]}]}, root)[-1]
    for t_id, want_count in originals.items():
        sample = back["samples"].get(t_id, {})
        if sample.get("sampleShown") or sample.get("sampleText") or sample.get("originalsShown") != want_count:
            problems.append(f"{label}: choosing {ex['activity']!r} after a preview leaves {t_id!r} showing {sample}, want its {want_count} original lines")

    # The same radio (already checked after the preview) fires click but no change
    # event; it must still restore the default scene, announce once, and a radio
    # chosen by pointer or by arrow key must do the same through change, once.
    other = next(t for t in types if t != ex["activity"])
    want_say = f"{next(a['label'] for a in rec['activities'] if a['id'] == ex['activity'])}. {intents[ex['activity']]}"
    for how, step in (("clicking", {"choose": ex["activity"]}),):
        runs = run_harness(main, {"rail": rail, "steps": [{"try": ex["id"]}, step]}, root)
        if runs[-1]["announceWrites"] - runs[-2]["announceWrites"] != 1 or runs[-1]["announce"] != want_say:
            problems.append(f"{label}: {how} the checked {ex['activity']!r} radio after a preview announced {runs[-1]['announceWrites'] - runs[-2]['announceWrites']} time(s), {runs[-1]['announce']!r}; want once, {want_say!r}")
    for how, key in (("clicking", "choose"), ("arrowing to", "key")):
        runs = run_harness(main, {"rail": rail, "steps": [{"try": ex["id"]}, {key: other}, {"try": ex["id"]}, {key: ex["activity"]}]}, root)
        for i, want in ((2, other), (4, ex["activity"])):
            s = runs[i]
            says = f"{next(a['label'] for a in rec['activities'] if a['id'] == want)}. {intents[want]}"
            if s["type"] != want or s["checked"] != [want] or s["announce"] != says or s["announceWrites"] - runs[i - 1]["announceWrites"] != 1:
                problems.append(f"{label}: {how} {want!r} after a preview shows {s['type']!r}, checked {s['checked']}, announced {s['announceWrites'] - runs[i - 1]['announceWrites']} time(s) {s['announce']!r}")
            for t_id, want_count in originals.items():
                sample = s["samples"].get(t_id, {})
                if sample.get("sampleShown") or sample.get("sampleText") or sample.get("originalsShown") != want_count:
                    problems.append(f"{label}: {how} {want!r} after a preview leaves {t_id!r} showing {sample}, want its {want_count} original lines")
    # With no preview showing, clicking the checked radio changes and announces nothing.
    idle = run_harness(main, {"rail": rail, "steps": [{"choose": types[0]}]}, root)
    if idle[-1]["announceWrites"] != idle[0]["announceWrites"] or idle[-1]["type"] != types[0]:
        problems.append(f"{label}: clicking the checked radio with no preview showing announced or changed the page")

    # The rail, paged by hand.
    n = len(examples)
    wide = run_harness(main, {"rail": {"width": n * rail["slide"] + (n - 1) * rail["gap"] + 50, "slide": rail["slide"], "gap": rail["gap"]}}, root)[0]
    if wide["controlsShown"]:
        problems.append(f"{label}: rail controls show although every example fits")
    pages = run_harness(main, {"rail": rail, "steps": [{"click": "next"}] * n + [{"click": "prev"}] * n}, root)
    start = pages[0]
    if not start["controlsShown"] or start["prevDisabled"] != "true" or start["nextDisabled"] != "false":
        problems.append(f"{label}: rail at load shows controls={start['controlsShown']}, prev={start['prevDisabled']}, next={start['nextDisabled']}")
    if start["count"] != f"1-3 of {n}":
        problems.append(f"{label}: rail count at load is {start['count']!r}, want '1-3 of {n}'")
    end = pages[n]
    if end["nextDisabled"] != "true" or end["prevDisabled"] != "false" or end["scrollLeft"] <= 0:
        problems.append(f"{label}: rail after paging forward: next={end['nextDisabled']}, prev={end['prevDisabled']}, left={end['scrollLeft']}")
    if any(p["prevDisabledAttr"] for p in pages) or "data-pp-next" not in end["focus"].split():
        problems.append(f"{label}: a rail button lost focus at the end (it must use aria-disabled, not disabled)")
    # Every stop of a button press is a card's own left edge, never mid-card.
    stray = [p["scrollLeft"] for p in pages if p["scrollLeft"] not in edges]
    if stray:
        problems.append(f"{label}: the rail stops mid-card at {stray}; card edges are {sorted(edges)}")
    if pages[-1]["scrollLeft"] != 0 or pages[-1]["prevDisabled"] != "true":
        problems.append(f"{label}: rail did not page back to the start: left={pages[-1]['scrollLeft']}")
    if set(end["scrolls"]) != {"smooth"}:
        problems.append(f"{label}: rail scrolls {sorted(set(end['scrolls']))}, want smooth")
    # Scrolling by any means keeps the count current but announces nothing; a
    # button press announces the range it lands on, once.
    farthest = n * rail["slide"] + (n - 1) * rail["gap"] - rail["width"]
    swipes = run_harness(main, {"rail": rail, "steps": [{"scroll": farthest}, {"scroll": 0}]}, root)
    if swipes[1]["count"] != end["count"] or swipes[2]["count"] != start["count"]:
        problems.append(f"{label}: the rail count while scrolling is {[s['count'] for s in swipes]}, want {end['count']!r} at the far end and {start['count']!r} back at the start")
    if any(s["railAnnounce"] != "" for s in swipes):
        problems.append(f"{label}: scrolling the rail announced {[s['railAnnounce'] for s in swipes]}; only a button press may")
    if end["railAnnounce"] != f"Showing examples {end['count']}":
        problems.append(f"{label}: paging forward announced {end['railAnnounce']!r}, want 'Showing examples {end['count']}'")
    calm = run_harness(main, {"rail": rail, "reduce": True, "steps": [{"click": "next"}]}, root)[-1]
    if calm["scrolls"] != ["auto"]:
        problems.append(f"{label}: under reduced motion the rail scrolls {calm['scrolls']}, want ['auto']")
    return problems


def built_file(build_dir: Path, route: str) -> Path:
    return build_dir / route.strip("/") / "index.html"


def check_built(build_dir: Path, root: Path) -> list[str]:
    problems: list[str] = []
    data = load_json(root, "data/platform_pages.json")
    vocab = {a["id"]: a for a in load_json(root, "data/actions.json")["actions"]}
    indexes = [build_dir / "sitemap.xml", build_dir / "llms.txt", build_dir / "llms-full.txt",
               *sorted(build_dir.glob("offline-search-index*.json"))]
    pages_html = sorted(build_dir.rglob("*.html"))

    for rec in data["pages"]:
        route = rec["route"]
        label = route
        path = built_file(build_dir, route)
        if not path.is_file():
            problems.append(f"{label} was not built")
            continue
        t = parse(path)
        main = t.main
        if main is None:
            problems.append(f"{label} has no <main>")
            continue
        if "noindex" not in t.robots:
            problems.append(f"{label} is not noindex")
        for idx in indexes:
            if idx.is_file() and route in idx.read_text(encoding="utf-8"):
                problems.append(f"{label} is listed in {idx.name}")
        for other in pages_html:
            if other == path:
                continue
            body = other.read_text(encoding="utf-8")
            if links_to(body, route):
                problems.append(f"{label} is linked from {other.relative_to(build_dir)}")

        body = text(main)
        if EM_DASH in body:
            problems.append(f"{label}: an em dash in the page")
        if BRAND_RE.search(body):
            problems.append(f"{label}: a browser or operating system brand in marketing copy: {BRAND_RE.search(body).group(0)!r}")
        if any("style" in e["attrs"] for e in walk(main)):
            problems.append(f"{label}: an inline style attribute")

        primary = [e for e in walk(main) if "button-primary" in classes(e)]
        if len(primary) != 1 or not primary[0]["attrs"].get("href", "").endswith("/download/") or "data-pp-start" not in primary[0]["attrs"]:
            problems.append(f"{label}: needs exactly one primary button, Start, to the download page; found {len(primary)}")

        order = [e["attrs"] for e in walk(main)]
        where = {k: next((i for i, a in enumerate(order) if k in a), -1) for k in ("data-pp-choice", "data-pp-start", "data-pp-stage")}
        if not 0 <= where["data-pp-choice"] < where["data-pp-start"] < where["data-pp-stage"]:
            problems.append(f"{label}: source order must be selector, Start, illustration so Start is in a phone's first screen; got {where}")

        types = [a["id"] for a in rec["activities"]]
        radios = find(main, "data-pp-choice")
        if [r["attrs"].get("value") for r in radios] != types:
            problems.append(f"{label}: radios {[r['attrs'].get('value') for r in radios]}, want {types}")
        if [("checked" in r["attrs"]) for r in radios] != [i == 0 for i in range(len(types))]:
            problems.append(f"{label}: only the first activity type is checked at load")
        for t_id in types:
            scenes = [e for e in find(main, "data-pp-for", t_id) if "pp-scene" in classes(e)]
            intents = [e for e in find(main, "data-pp-for", t_id) if "data-pp-intent" in e["attrs"]]
            if len(scenes) != 1 or len(intents) != 1:
                problems.append(f"{label}: type {t_id!r} has {len(scenes)} illustrations and {len(intents)} intents, want one each")
        if not find(main, "data-pp-stage") or not find(main, "data-pp-announce"):
            problems.append(f"{label}: the illustration or the announcement region is missing")

        cards = find(main, "data-pp-example")
        want_cards = [(e["id"], VARIANTS[e["variant"]]) for e in rec["examples"]["items"]]
        got_cards = [(c["attrs"]["data-pp-example"], next((k for k in classes(c) if k in VARIANTS.values()), "")) for c in cards]
        if got_cards != want_cards:
            problems.append(f"{label}: examples {got_cards}, want {want_cards}")

        details = [e for e in walk(main) if e["tag"] == "details"]
        if [d["attrs"].get("data-pp-kind") for d in details] != [i["kind"] for i in rec["breakdown"]["items"]]:
            problems.append(f"{label}: breakdowns {[d['attrs'].get('data-pp-kind') for d in details]} do not match the record")
        if any("open" in d["attrs"] for d in details):
            problems.append(f"{label}: a breakdown is open at load; all start collapsed")
        actions = yaml_actions(root, rec["platform"]) or []
        ids = [a["id"] for a in actions]
        for block, want in (("data-pp-actions", ids), ("data-pp-behavior", ids), ("data-pp-limits", [a["id"] for a in actions if a["limits"]])):
            regions = find(main, block)
            if not regions:
                continue
            got = [e["attrs"]["data-action"] for e in walk(regions[0]) if "data-action" in e["attrs"]]
            if got != want:
                problems.append(f"{label}: {block} rows {got}, want {want}")
        for el in find(main, "data-pp-limits"):
            shown = {
                row["attrs"]["data-action"]: " ".join(text(next(d for d in walk(row) if d["tag"] == "dd")).split())
                for row in walk(el) if "data-action" in row["attrs"]
            }
            want_text = {a["id"]: a["limits"] for a in actions if a["limits"]}
            if shown != want_text:
                problems.append(f"{label}: limits text {shown}, want the YAML's {want_text}")
        counts = find(main, "data-pp-rail-count")
        announcers = find(main, "data-pp-rail-announce")
        if any("aria-live" in c["attrs"] for c in counts):
            problems.append(f"{label}: the rail count is a live region; scrolling would announce every frame")
        if len(announcers) != 1 or announcers[0]["attrs"].get("aria-live") != "polite":
            problems.append(f"{label}: needs one polite live region for rail button presses")
        for el in find(main, "data-pp-actions"):
            names = [text(n).strip() for n in walk(el) if "pp-fact-name" in classes(n)]
            want_names = [vocab[i]["name"] for i in ids if i in vocab]
            if names != want_names:
                problems.append(f"{label}: supported actions named {names}, want {want_names}")

        try:
            problems.extend(check_behaviour(label, main, rec, actions, root))
        except RuntimeError as err:
            problems.append(f"{label}: {err}")
    return problems


def run(root: Path, build_dir: Path | None) -> list[str]:
    problems = check_source(root)
    if build_dir is not None:
        problems.extend(check_built(build_dir, root))
    return problems


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["--source"]:
        problems = check_source(ROOT)
        what = "platform page data"
    else:
        build_dir = Path(argv[0]) if argv else ROOT / "public"
        if build_dir.is_dir():
            problems = run(ROOT, build_dir)
        else:
            problems = check_source(ROOT) + [f"build dir {build_dir} is missing; run make site-build first"]
        what = "platform pages"
    for item in problems:
        print(f"platform-pages: {item}", file=sys.stderr)
    print(f"checked {what}, {len(problems)} broken")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
