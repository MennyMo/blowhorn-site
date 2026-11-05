#!/usr/bin/env python3
"""Copy the Blowhorn product docs into the site's Docsy section.

The user docs live in the private blowhorn repository under
docs/{tutorials,how-to,reference,explanation} and docs/README.md. This
script mirrors them into the site's content/en/docs/ so the normal site
checks (make site-check) hold the synced pages to the same contract as
every hand-written page. Run it through make (see the docs-sync target);
sync-docs.yml calls the same target.

What is copied: every Markdown page under the four public sections,
including each section landing (_index.md), the docs landing
(docs/_index.md, which becomes content/en/docs/_index.md), plus any local
non-Markdown file those pages reference (images and the like). The product
docs are the only source: nothing under content/en/docs/ is written by hand.
What is never copied: docs/internal/, docs/gtm/, and any path listed in
the product's internal-paths.txt (release/internal-paths.txt since the
product's layout move, then docs/internal-paths.txt, then internal-paths.txt
at the product root), dotfiles, and docs/README.md
itself, the product's GitHub index (the site landing comes from
docs/_index.md instead).

Per-page conversions (the product docs themselves are never edited):

- Relative ".md" links become root-relative site URLs, e.g.
  ../reference/cli.md becomes /docs/reference/cli/, keeping any
  #anchor or query. Links that escape the published tree (internal/,
  gtm/, excluded or missing paths) are left alone and reported: fixing
  them belongs to the product docs, and the sync PR lists them.
- reference/cli.md becomes the reference/cli/ section index
  (reference/cli/_index.md): the product keeps a single CLI page while
  the site reserves cli/ for per-command pages, and the two cannot both
  claim /docs/reference/cli/.
- Pages keep their front matter untouched, except that a missing title
  is derived from the first H1 (else the file name) and aliases that
  collide with a URL the synced tree itself publishes are dropped: a
  colliding alias would replace a section index with a redirect and
  break the site contract check.
- "Blowhorn Cloud" and "Layer5 Cloud" in prose and front matter become
  "Blowhorn", the one name the site says (check_naming.py fails the
  build on either). Fenced code is left as the product writes it. Each
  rename is reported, so the product copy gets fixed upstream too.
- Headings whose auto id would not begin with a letter (which
  html-validate rejects) get an explicit {#anchor} pinning a valid one.
- Pages carrying draft: true stay drafts, so Hugo leaves them
  unpublished until the product ungates them.

Mirror bookkeeping: site _index.md landing pages with no product
counterpart are kept byte-identical (and reported, since every landing now
has a product source); other Markdown pages under the docs
directory with no product counterpart are removed as stale; newly empty
directories are pruned.

Usage: sync-docs.py SOURCE_DIR DOCS_DIR --ref REF

  SOURCE_DIR  root of a blowhorn checkout (reads SOURCE_DIR/docs)
  DOCS_DIR    site directory the pages sync into (content/en/docs)
  --ref       tag, branch or SHA of the product repo being synced; recorded
              in the report only
"""

import argparse
import posixpath
import re
import sys
from pathlib import Path

# The site's naming rule, shared with the build check (sibling script,
# importable because this file's directory is on sys.path when run).
from check_naming import CLOUD_RE

SECTIONS = ("tutorials", "how-to", "reference", "explanation")
# Product paths that are never published, relative to docs/ (the sync root).
ALWAYS_EXCLUDED = ("internal", "gtm")
# File names that address a section rather than a page.
INDEX_NAMES = ("_index.md", "index.md", "README.md")
# Links to the private product repository must never ship: every reader
# would get a 404.
PRIVATE_REPO_MARK = "github.com/blowhorn-ai/blowhorn"

LINK = re.compile(r"(!?)\[([^\]]*)\]\(([^)]*)\)")
AUTOLINK = re.compile(r"<([A-Za-z][A-Za-z0-9+.-]*:[^<>\s]*)>")
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def warn(message, warnings):
    warnings.append(message)
    print(f"sync-docs warning: {message}", file=sys.stderr)


def read_internal_paths(product_root, product_docs):
    """Docs-relative exclusion paths from the product's internal-paths.txt.

    Entries are written repo-relative (docs/how-to/x.md); a leading docs/
    is stripped so they compare against docs-relative paths.
    """
    excluded = set(ALWAYS_EXCLUDED)
    # The product moved the list to release/ (blowhorn #636); a
    # missed home means no exclusion at all, so every known home is tried.
    for candidate in (product_root / "release" / "internal-paths.txt",
                      product_docs / "internal-paths.txt",
                      product_root / "internal-paths.txt"):
        if not candidate.is_file():
            continue
        for line in candidate.read_text(encoding="utf-8").splitlines():
            line = line.strip().strip("/")
            if not line or line.startswith("#"):
                continue
            if line == "docs" or line.startswith("docs/"):
                line = line[len("docs"):].strip("/")
            if line:
                excluded.add(line)
        break
    return excluded


def is_excluded(docs_rel, excluded):
    parts = docs_rel.split("/")
    for i in range(1, len(parts) + 1):
        if "/".join(parts[:i]) in excluded:
            return True
    return False


def map_path(docs_rel):
    """Map a product docs-relative path to a site docs-relative path."""
    if docs_rel == "README.md":
        # The product's GitHub index; the site landing comes from _index.md.
        return None
    if docs_rel == "_index.md":
        # The docs landing (content/en/docs/_index.md) lives in the product.
        return "_index.md"
    if docs_rel == "reference/cli.md":
        # The product keeps a single CLI page where the site reserves cli/
        # for per-command pages; it becomes the section index.
        return "reference/cli/_index.md"
    section = docs_rel.split("/", 1)[0]
    if section not in SECTIONS:
        return None
    if posixpath.basename(docs_rel) in INDEX_NAMES:
        directory = posixpath.dirname(docs_rel)
        return directory + "/_index.md" if directory else "_index.md"
    return docs_rel


def split_front_matter(text):
    """Return (front_matter or None, body). The fences must be --- lines."""
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return None, text
    lines = text.split("\n")
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1:])
    return None, text


def front_matter_title(front):
    for line in front.split("\n"):
        match = re.match(r"^title:\s*(.*)$", line)
        if match:
            value = match.group(1).strip()
            if (len(value) >= 2 and value[0] == value[-1]
                    and value[0] in ("'", '"')):
                value = value[1:-1]
            return value
    return None


def first_h1(body):
    in_fence = False
    for line in body.split("\n"):
        if line.startswith("```"):
            in_fence = not in_fence
        elif not in_fence and line.startswith("# "):
            heading = line[2:].strip()
            heading = re.sub(r"\{#[^}]*\}\s*$", "", heading).strip()
            return heading.strip("`\"'")
    return None


def parse_aliases(front):
    """Parse an aliases: key; return (style, items, span) or None.

    style is "flow" for `aliases: [/a/, /b/]` or "block" for a following
    list of `- /a/` lines; span is the (start, end) line range to replace.
    """
    lines = front.split("\n")
    for i, line in enumerate(lines):
        match = re.match(r"^aliases:\s*(.*)$", line)
        if not match:
            continue
        rest = match.group(1).strip()
        if rest.startswith("["):
            inner = rest[1:rest.index("]")] if "]" in rest else rest[1:]
            items = [item.strip().strip("\"'") for item in inner.split(",")]
            return ("flow", [item for item in items if item], (i, i + 1))
        if rest:
            return None
        items, j = [], i + 1
        while j < len(lines) and re.match(r"^\s+-\s+\S", lines[j]):
            items.append(lines[j].split("-", 1)[1].strip().strip("\"'"))
            j += 1
        if j == i + 1:
            return None
        return ("block", items, (i, j))
    return None


def render_aliases(style, items, span, lines):
    kept = [f'"{item}"' if "," in item else item for item in items]
    if style == "flow":
        lines[span[0]] = f"aliases: [{', '.join(kept)}]"
    else:
        lines[span[0]:span[1]] = [lines[span[0]]] + [f"  - {item}" for item in kept]
    return "\n".join(lines)


def site_url_for(docs_rel):
    """Site URL path for a product docs-relative page or section path."""
    if posixpath.basename(docs_rel) in INDEX_NAMES:
        docs_rel = posixpath.dirname(docs_rel)
    elif docs_rel.endswith(".md"):
        docs_rel = docs_rel[:-len(".md")]
    return "/docs/" + docs_rel + "/" if docs_rel else "/docs/"


def classify_target(raw, src_dir, product_docs, excluded, published_urls, warnings, src_label):
    """Decide what a link target becomes: ("page", url), ("asset", rel), or None."""
    target = raw.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    title = ""
    path, space, rest = target.partition(" ")
    if space:
        # URLs never contain a raw space; the rest is a "title".
        title = " " + rest.strip()
        target = path
    lowered = target.lower()
    if PRIVATE_REPO_MARK in lowered:
        warn(f"{src_label}: links the private product repository: {raw.strip()}", warnings)
    if (not target or target.startswith("#") or target.startswith("mailto:")
            or "://" in target or target.startswith("//") or SCHEME.match(target)):
        return None
    if target.startswith("/"):
        if target.startswith("/docs/"):
            page = target[len("/docs/"):].strip("/")
            if page and f"/docs/{page}/" not in published_urls:
                warn(f"{src_label}: links a docs URL the sync does not publish: {raw.strip()}",
                     warnings)
        return None
    path, hash_mark, anchor = target.partition("#")
    query = ""
    if "?" in path:
        path, _, query = path.partition("?")
        query = "?" + query
    if not path:
        return None
    resolved = posixpath.normpath(posixpath.join(src_dir, path))
    if resolved.startswith(".."):
        warn(f"{src_label}: links outside the published docs: {raw.strip()}", warnings)
        return None
    suffix = ""
    if resolved.endswith(".md") and (product_docs / resolved).is_file():
        suffix = "page"
    elif (product_docs / (resolved + ".md")).is_file():
        resolved = resolved + ".md"
        suffix = "page"
    elif (product_docs / resolved).is_dir():
        suffix = "dir"
    elif (product_docs / resolved).is_file():
        suffix = "asset"
    else:
        warn(f"{src_label}: links outside the published docs: {raw.strip()}", warnings)
        return None
    candidates = [resolved]
    if suffix == "page":
        candidates.append(resolved[:-len(".md")])
    if any(is_excluded(candidate, excluded) for candidate in candidates):
        warn(f"{src_label}: links a page that is never published: {raw.strip()}", warnings)
        return None
    if suffix == "asset":
        url = "/docs/" + resolved + query
    else:
        url = site_url_for(resolved) + query
    if anchor:
        url += "#" + anchor
    return (suffix, url, title)


def anchorize_heading(text):
    """Approximate Hugo's auto heading id: formatting stripped, lowercased."""
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[*_~]+", "", text)
    text = re.sub(r"\{[^}]*\}\s*$", "", text).strip()
    text = text.lower()
    return re.sub(r"[^\w\- ]", "", text, flags=re.UNICODE).replace(" ", "-")


def fix_heading_ids(body, warnings, src_label):
    """Give headings with invalid auto ids an explicit {#anchor}.

    Hugo anchors `### --profile ...` as --profile-..., which html-validate
    rejects (an id must begin with a letter). The explicit anchor overrides
    the auto one; product links never address these anchors today.
    """
    used = set(re.findall(r"\{#([^}]+)\}", body))
    fixed = []

    def fix_line(line):
        match = re.match(r"^(#{1,6}\s+)(.*?)(\s*)$", line)
        if not match or "{#" in line:
            return line
        candidate = anchorize_heading(match.group(2))
        if candidate and re.match(r"^[A-Za-z]", candidate):
            return line
        base = "section-" + candidate.lstrip("-") if candidate.lstrip("-") else "section"
        anchor, suffix = base, 2
        while anchor in used:
            anchor, suffix = f"{base}-{suffix}", suffix + 1
        used.add(anchor)
        fixed.append((match.group(2), anchor))
        return f"{match.group(1)}{match.group(2)} {{#{anchor}}}{match.group(3)}"

    in_fence = False
    lines = []
    for line in body.split("\n"):
        if line.startswith("```"):
            in_fence = not in_fence
        if not in_fence and line.startswith("#"):
            line = fix_line(line)
        lines.append(line)
    for heading, anchor in fixed:
        warn(f"{src_label}: heading {heading!r} would anchor as an invalid id; "
             f"pinning {{#{anchor}}}", warnings)
    return "\n".join(lines)


def rewrite_links(body, src_dir, product_docs, excluded, published_urls, warnings, src_label):
    assets = []

    def replace(match):
        bang, text, raw = match.groups()
        outcome = classify_target(raw, src_dir, product_docs, excluded,
                                  published_urls, warnings, src_label)
        if outcome is None:
            return match.group(0)
        kind, url, title = outcome
        if kind == "asset":
            assets.append(url[len("/docs/"):].split("?")[0].split("#")[0])
        return f"{bang}[{text}]({url}{title})"

    body = LINK.sub(replace, body)

    def flag_autolink(match):
        if PRIVATE_REPO_MARK in match.group(1).lower():
            warn(f"{src_label}: links the private product repository: <{match.group(1)}>",
                 warnings)
        return match.group(0)

    return AUTOLINK.sub(flag_autolink, body), assets


def rename_cloud(text):
    """Return text with "Blowhorn Cloud" and "Layer5 Cloud" said as "Blowhorn", and the count.

    Fenced code is left alone: a command or printed line is quoted as the
    software writes it, and check_naming.py exempts code too.
    """
    count = 0
    lines = []
    in_fence = False
    for line in text.split("\n"):
        if line.startswith("```"):
            in_fence = not in_fence
        if not in_fence:
            line, n = CLOUD_RE.subn("Blowhorn", line)
            count += n
        lines.append(line)
    return "\n".join(lines), count


def convert_page(text, src_dir, product_docs, excluded, published_urls, warnings, src_label):
    front, body = split_front_matter(text)
    if front is None:
        front, body = "", text
    if front_matter_title(front) is None:
        heading = first_h1(body)
        if heading is None:
            heading = posixpath.basename(src_label)[:-len(".md")].replace("-", " ")
            warn(f"{src_label}: no title or H1; using file name", warnings)
        else:
            warn(f"{src_label}: no title front matter; using H1", warnings)
        title = heading.replace('"', '\\"')
        front = f'title: "{title}"\n{front}' if front else f'title: "{title}"'
    parsed = parse_aliases(front)
    if parsed is not None:
        style, items, span = parsed
        colliding = [item for item in items
                     if item in published_urls or item.rstrip("/") in published_urls]
        for item in colliding:
            warn(f"{src_label}: alias {item} collides with a published URL; dropping it",
                 warnings)
        kept = [item for item in items if item not in colliding]
        if len(kept) != len(items):
            lines = front.split("\n")
            if kept:
                front = render_aliases(style, kept, span, lines)
            else:
                del lines[span[0]:span[1]]
                front = "\n".join(lines)
    elif re.search(r"^aliases:", front, re.MULTILINE):
        warn(f"{src_label}: aliases not in flow or block form; kept unchecked", warnings)
    front, front_renames = rename_cloud(front)
    body, body_renames = rename_cloud(body)
    if front_renames + body_renames:
        warn(f"{src_label}: said \"Blowhorn Cloud\" or \"Layer5 Cloud\" {front_renames + body_renames} "
             "time(s); said \"Blowhorn\" instead (fix the product copy)", warnings)
    body = fix_heading_ids(body, warnings, src_label)
    body, assets = rewrite_links(body, src_dir, product_docs, excluded,
                                 published_urls, warnings, src_label)
    if front or text.startswith("---"):
        return f"---\n{front}\n---\n{body}", assets
    return body, assets


def sync(source_dir, docs_dir, ref):
    warnings = []
    source_dir = Path(source_dir)
    docs_dir = Path(docs_dir)
    product_docs = source_dir / "docs"
    if not product_docs.is_dir():
        print(f"sync-docs: {product_docs} is not a directory: "
              "SOURCE_DIR must be the root of a blowhorn checkout",
              file=sys.stderr)
        return 2
    excluded = read_internal_paths(source_dir, product_docs)

    pages = {}
    # The docs landing sits at the product docs root, outside the sections.
    if (product_docs / "_index.md").is_file():
        pages["_index.md"] = "_index.md"
    for section in SECTIONS:
        section_dir = product_docs / section
        if not section_dir.is_dir():
            warn(f"product section docs/{section}/ is missing at {ref}; "
                 "its site pages go stale", warnings)
            continue
        for path in sorted(section_dir.rglob("*")):
            if not path.is_file() or path.name.startswith("."):
                continue
            docs_rel = path.relative_to(product_docs).as_posix()
            if is_excluded(docs_rel, excluded):
                continue
            if path.suffix != ".md":
                continue
            site_rel = map_path(docs_rel)
            if site_rel is None:
                continue
            pages[site_rel] = docs_rel

    # Published URLs for alias-collision filtering: every synced page plus
    # every section the tree publishes (kept site landings included).
    published_urls = {"/docs/"}
    for site_rel in pages:
        if site_rel == "_index.md":
            continue
        if site_rel.endswith("/_index.md"):
            section = site_rel[:-len("/_index.md")]
            published_urls.add("/docs/" + section + "/" if section else "/docs/")
        else:
            published_urls.add("/docs/" + site_rel[:-len(".md")] + "/")
    if docs_dir.is_dir():
        for path in sorted(docs_dir.rglob("_index.md")):
            rel = path.relative_to(docs_dir).as_posix()
            if rel != "_index.md":
                published_urls.add("/docs/" + rel[:-len("/_index.md")] + "/")

    synced, assets_copied, kept = 0, 0, 0
    for site_rel in sorted(pages):
        docs_rel = pages[site_rel]
        text = (product_docs / docs_rel).read_text(encoding="utf-8")
        converted, assets = convert_page(
            text, posixpath.dirname(docs_rel), product_docs, excluded,
            published_urls, warnings, docs_rel)
        dest = docs_dir / site_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.is_file() or dest.read_text(encoding="utf-8") != converted:
            dest.write_text(converted, encoding="utf-8")
        synced += 1
        for asset_rel in assets:
            data = (product_docs / asset_rel).read_bytes()
            asset_dest = docs_dir / asset_rel
            asset_dest.parent.mkdir(parents=True, exist_ok=True)
            if not asset_dest.is_file() or asset_dest.read_bytes() != data:
                asset_dest.write_bytes(data)
            assets_copied += 1

    removed = 0
    if docs_dir.is_dir():
        for path in sorted(docs_dir.rglob("*.md")):
            rel = path.relative_to(docs_dir).as_posix()
            if path.name == "_index.md":
                if rel not in pages:
                    kept += 1
                    warn(f"{rel}: site landing has no product source "
                         f"(docs/{rel}); kept as is", warnings)
                continue
            if rel not in pages:
                path.unlink()
                removed += 1
        for path in sorted(docs_dir.rglob("*"), reverse=True):
            if path.is_dir() and path != docs_dir and not any(path.iterdir()):
                path.rmdir()

    print(f"sync-docs: synced {synced} page(s) from {ref} "
          f"(+{assets_copied} asset(s)); kept {kept} site landing(s); "
          f"removed {removed} stale page(s)")
    return 0


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("source_dir")
    parser.add_argument("docs_dir")
    parser.add_argument("--ref", required=True)
    args = parser.parse_args(argv)
    return sync(args.source_dir, args.docs_dir, args.ref)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
