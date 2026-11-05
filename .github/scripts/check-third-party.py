#!/usr/bin/env python3
"""Fail if the built site makes the browser load anything from another host.

The privacy page promises that blowhorn.ai loads no fonts, images, styles or
scripts from third parties other than the ones it discloses: Google Analytics
4 and the download page's release lookup. This check holds the build to it:

- HTML: deny by default. Every attribute value on every element that is an
  absolute http(s) or protocol-relative URL is treated as a fetch; srcset,
  imagesrcset and ping are split into their URLs, style attributes and <style>
  are read as CSS, and inline scripts and on* event-handler attributes are
  scanned for absolute URLs (JSON data blocks such as application/ld+json are
  data, not requests). Only attributes that never make the browser request
  anything are exempt: href and xlink:href on <a> and <area> (navigation),
  <link href> whose rel values all name without fetching (canonical,
  alternate, ...), cite, itemtype, itemid, itemprop, xmlns and xmlns:*, and
  <meta content>, except the url= of <meta http-equiv="refresh">.
  One reviewed exception: <form action> may name a host in FORM_ACTION_HOSTS.
  A form loads nothing; it sends only what the reader types, and only when
  they submit it. The footer's newsletter signup posts to Blowhorn's own
  signup service at api.blowhorn.ai, and the privacy page discloses it.
  Every other form host fails.
  A second: <meta http-equiv="refresh"> may navigate to the Blowhorn host
  named by params.cloud_url in hugo.toml (the /signup, /login and /early-access
  redirects).
  A refresh is a top-level navigation the reader asked for by opening that
  path, not a subresource load; every other refresh host fails.
  A third: Google's gtag.js may come from a host in ANALYTICS_SCRIPT_HOSTS,
  either as a <script src> or named in a script a page loads. Today
  layouts/_partials/analytics.html loads it directly on every production
  page. The privacy page discloses Google
  Analytics 4. Every other attribute naming that host still fails.
- CSS: every url(...) and @import in each stylesheet a page loads.
- JavaScript: every absolute URL in each script a page loads. The Download section's script
  (assets/js/download.js) asks GitHub's public API for the newest release, a
  request the privacy page discloses, and links to github.com; those two hosts
  are the only ones a script may name (SCRIPT_HOSTS).

A stylesheet or script a page loads by an absolute first-party URL
(https://blowhorn.ai/...) is read from the build and checked like a local one.
Files no page loads (Docsy ships a few in its static/ directory) are not
checked either: they are never requested.
Usage: check-third-party.py BUILD_DIR [FIRST_PARTY_HOST]
"""

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

FIRST_PARTY = "blowhorn.ai"
# Hosts a script may name. Each one must be disclosed on the privacy page.
SCRIPT_HOSTS = {"api.github.com", "github.com"}
# Hosts a <script src> may load Google Analytics 4 (gtag.js) from. Disclosed on the privacy page.
ANALYTICS_SCRIPT_HOSTS = {"www.googletagmanager.com"}
# Hosts a <form action> may post to. Each one must be disclosed on the privacy page.
# api.blowhorn.ai is Blowhorn's own signup service (a Cloudflare Worker), not
# a third party: the coming-soon and newsletter forms post there.
FORM_ACTION_HOSTS = {"calcotestudios.us15.list-manage.com", "api.blowhorn.ai"}

def _cloud_host() -> str:
    """Host of params.cloud_url in hugo.toml, the one allowed refresh target."""
    toml = Path(__file__).resolve().parents[2] / "hugo.toml"
    match = re.search(r'^\s*cloud_url\s*=\s*"([^"]+)"', toml.read_text(encoding="utf-8"), re.M)
    return urlparse(match.group(1)).hostname or "" if match else ""


# Hosts a <meta http-equiv="refresh"> may navigate to (params.cloud_url).
REFRESH_HOSTS = {h for h in {_cloud_host()} if h}
# <link rel> values that name a URL without the browser fetching it.
NON_FETCHING_RELS = {"canonical", "alternate", "author", "license", "me", "help"}
# <script type> values that hold data, not code the browser runs.
DATA_SCRIPT_TYPES = {"application/ld+json", "application/json"}
# Attributes that name a URL without the browser fetching it, on any element.
NON_FETCHING_ATTRS = {"cite", "itemtype", "itemid", "itemprop", "xmlns"}
# Elements whose href is navigation, not a request.
NAVIGATION_TAGS = {"a", "area"}
# (tag, attribute) pairs that load a stylesheet or script, read from the build and
# checked in turn. Every other collected value is only host-checked: under deny by
# default it may be any attribute text (an SVG path, a class), not a file path.
FILE_LOADS = {("link", "href"), ("script", "src"), ("script", "href"), ("script", "xlink:href"), ("style", "css")}

CSS_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
CSS_URL = re.compile(r"""url\(\s*(?:"([^"]*)"|'([^']*)'|([^"')\s]*))\s*\)""")
# @import "x.css"; the url("x.css") form is already matched by CSS_URL.
CSS_IMPORT = re.compile(r"""@import\s+["']([^"']+)["']""")
JS_URL = re.compile(r"""(?:https?:)?//[A-Za-z0-9.-]+\.[A-Za-z]{2,}""")


def host_of(ref: str) -> str:
    ref = ref.strip()
    if ref.startswith("//"):
        ref = "https:" + ref
    parsed = urlparse(ref)
    if parsed.scheme in ("http", "https"):
        return (parsed.hostname or "").lower()
    return ""


def css_refs(text: str) -> list:
    text = CSS_COMMENT.sub("", text)
    refs = [next(g for g in m.groups() if g is not None) for m in CSS_URL.finditer(text)]
    refs += [m.group(1) for m in CSS_IMPORT.finditer(text)]
    return refs


class FetchCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
        self.inline_js = []
        self._in_style = False
        self._in_script = False

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        rels = set((values.get("rel") or "").lower().split())
        for name, value in attrs:
            if not value or name in NON_FETCHING_ATTRS or name.startswith("xmlns:"):
                continue
            if name in ("href", "xlink:href") and (
                tag in NAVIGATION_TAGS or (tag == "link" and rels and rels <= NON_FETCHING_RELS)
            ):
                continue
            if tag == "form" and name == "action" and host_of(value) in FORM_ACTION_HOSTS:
                continue
            if name == "style":
                self.refs += [(tag, "style", ref) for ref in css_refs(value)]
            elif name.startswith("on"):
                self.inline_js.append((f"<{tag} {name}>", value))
            elif tag == "meta" and name == "content":
                if (values.get("http-equiv") or "").lower() == "refresh":
                    match = re.search(r"url\s*=\s*(\S+)", value, re.IGNORECASE)
                    if match:
                        self.refs.append((tag, "refresh", match.group(1).strip("'\"")))
            elif name in ("srcset", "imagesrcset"):
                for candidate in value.split(","):
                    candidate = candidate.strip()
                    if candidate:
                        self.refs.append((tag, name, candidate.split()[0]))
            elif name == "ping":
                self.refs += [(tag, name, url) for url in value.split()]
            else:
                self.refs.append((tag, name, value))
        self._in_style = tag == "style"
        script_type = (values.get("type") or "").lower().split(";")[0].strip()
        self._in_script = tag == "script" and not values.get("src") and script_type not in DATA_SCRIPT_TYPES

    def handle_endtag(self, tag):
        if tag == "style":
            self._in_style = False
        if tag == "script":
            self._in_script = False

    def handle_data(self, data):
        if self._in_style:
            self.refs += [("style", "css", ref) for ref in css_refs(data)]
        if self._in_script:
            self.inline_js.append(("<script>", data))


def local_file(root: Path, source: Path, ref: str, first_party: set):
    """The built file a same-site reference resolves to, or None for another host.

    An absolute URL on a first-party host resolves against the build root."""
    host = host_of(ref)
    if (host and host not in first_party) or ref.startswith(("data:", "#", "mailto:")):
        return None
    path = urlparse(ref if not ref.startswith("//") else "https:" + ref).path
    if not path:
        return None
    base = root if host or path.startswith("/") else source.parent
    target = (base / path.lstrip("/")).resolve()
    return target if target.is_file() else None


def main(root: Path, first_party: str) -> int:
    root = root.resolve()
    allowed = {first_party, "www." + first_party}
    problems = []
    pages = sorted(root.rglob("*.html"))
    if not pages:
        print(f"no HTML pages found under {root}", file=sys.stderr)
        return 1
    sheets, scripts = set(), set()
    for page in pages:
        collector = FetchCollector()
        collector.feed(page.read_text(encoding="utf-8"))
        for tag, attr, ref in collector.refs:
            host = host_of(ref)
            if attr == "refresh" and host in REFRESH_HOSTS:
                continue
            if tag == "script" and attr == "src" and host in ANALYTICS_SCRIPT_HOSTS:
                continue
            if host and host not in allowed:
                problems.append(f"{page.relative_to(root)}: <{tag} {attr}> loads {ref}")
            if (tag, attr) not in FILE_LOADS:
                continue
            target = local_file(root, page, ref, allowed)
            if target and target.suffix == ".css":
                sheets.add(target)
            elif target and target.suffix in (".js", ".mjs"):
                scripts.add(target)
        for where, code in collector.inline_js:
            for match in JS_URL.finditer(code):
                host = host_of(match.group(0))
                if host and host not in allowed | SCRIPT_HOSTS:
                    problems.append(f"{page.relative_to(root)}: inline {where} names {match.group(0)}")
    pending = list(sheets)
    while pending:
        sheet = pending.pop()
        for ref in css_refs(sheet.read_text(encoding="utf-8")):
            host = host_of(ref)
            if host and host not in allowed:
                problems.append(f"{sheet.relative_to(root)}: loads {ref}")
            target = local_file(root, sheet, ref, allowed)
            if target and target.suffix == ".css" and target not in sheets:
                sheets.add(target)
                pending.append(target)
    for script in sorted(scripts):
        for match in JS_URL.finditer(script.read_text(encoding="utf-8")):
            host = host_of(match.group(0))
            if host and host not in allowed | SCRIPT_HOSTS | ANALYTICS_SCRIPT_HOSTS:
                problems.append(f"{script.relative_to(root)}: names {match.group(0)}")
    for item in problems:
        print(f"third-party request: {item}", file=sys.stderr)
    print(
        f"checked {len(pages)} page(s), {len(sheets)} stylesheet(s) and {len(scripts)} script(s) they load, "
        f"{len(problems)} third-party reference(s)"
    )
    return 1 if problems else 0


if __name__ == "__main__":
    build = Path(sys.argv[1] if len(sys.argv) > 1 else "public")
    sys.exit(main(build, sys.argv[2] if len(sys.argv) > 2 else FIRST_PARTY))
