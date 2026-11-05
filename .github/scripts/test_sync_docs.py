#!/usr/bin/env python3
"""Tests for sync-docs.py: run it on fixture product checkouts and read the site tree.

Run with `make test-scripts` (CI runs it too).
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("sync-docs.py")

LANDING = """---
title: "How-to guides"
linkTitle: "How-to guides"
description: "Reach one goal."
weight: 20
---

Each guide solves one real problem.
"""

PAGE = """---
title: "{title}"
description: "A test page."
weight: 10
---

# {title}

See [the other]({link}).
"""


def product(files):
    """A product checkout layout from docs-relative path -> text."""
    tree = {}
    for name, text in files.items():
        tree[f"docs/{name}"] = text
    return tree


class SyncDocsTest(unittest.TestCase):
    def run_sync(self, tree, ref="test-ref", docs_seed=None):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, text in tree.items():
                path = root / "product" / name
                path.parent.mkdir(parents=True, exist_ok=True)
                if isinstance(text, bytes):
                    path.write_bytes(text)
                else:
                    path.write_text(text, encoding="utf-8")
            docs = root / "site-docs"
            for name, text in (docs_seed or {}).items():
                path = docs / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(root / "product"), str(docs),
                 "--ref", ref],
                capture_output=True, text=True, check=False,
            )
            site = {}
            if docs.is_dir():
                for path in sorted(docs.rglob("*")):
                    if path.is_file():
                        site[path.relative_to(docs).as_posix()] = path.read_text(
                            encoding="utf-8")
            return result, site

    def assert_synced(self, tree, docs_seed=None):
        result, site = self.run_sync(tree, docs_seed=docs_seed)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result, site

    def test_copies_only_public_sections(self):
        _, site = self.assert_synced(product({
            "README.md": "---\ntitle: docs\n---\n# docs\n",
            "tutorials/first.md": PAGE.format(title="First", link="other.md"),
            "tutorials/other.md": PAGE.format(title="Other", link="first.md"),
            "internal/secret.md": PAGE.format(title="Secret", link="x.md"),
            "gtm/plan.md": PAGE.format(title="Plan", link="x.md"),
        }))
        self.assertIn("tutorials/first.md", site)
        self.assertIn("tutorials/other.md", site)
        self.assertNotIn("README.md", site)
        self.assertFalse(any(name.startswith("internal/") for name in site))
        self.assertFalse(any(name.startswith("gtm/") for name in site))

    def test_dotfiles_and_unreferenced_files_are_skipped(self):
        result, site = self.run_sync(product({
            "reference/cli/.gitkeep": "",
            "reference/notes.txt": "not a page",
            "reference/cli.md": PAGE.format(title="CLI", link="x.md"),
        }), docs_seed={"reference/cli/_index.md": LANDING})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(any(Path(name).name.startswith(".") for name in site))
        self.assertNotIn("reference/notes.txt", site)

    def test_site_landing_kept_when_product_has_no_counterpart(self):
        result, site = self.assert_synced(
            product({"how-to/publish/post.md": PAGE.format(title="Post", link="x.md")}),
            docs_seed={"how-to/publish/_index.md": LANDING},
        )
        self.assertEqual(site["how-to/publish/_index.md"], LANDING)
        self.assertIn("sync-docs: synced 1 page(s)", result.stdout)

    def test_docs_and_section_landings_come_from_the_product(self):
        root = "---\ntitle: \"Docs\"\nlayout: \"landing\"\n---\n\n# Docs\n\n<a href=\"how-to/\">How-to</a>\n"
        result, site = self.assert_synced(
            product({
                "README.md": "---\ntitle: docs\n---\n# docs\n",
                "_index.md": root,
                "how-to/_index.md": LANDING,
                "how-to/post.md": PAGE.format(title="Post", link="x.md"),
            }),
            docs_seed={"_index.md": "old landing\n", "how-to/_index.md": "old\n"},
        )
        self.assertEqual(site["_index.md"], root)
        self.assertEqual(site["how-to/_index.md"], LANDING)
        self.assertNotIn("site landing has no product source", result.stderr)

    def test_unsourced_site_landing_is_reported(self):
        result, _ = self.assert_synced(
            product({"how-to/publish/post.md": PAGE.format(title="Post", link="x.md")}),
            docs_seed={"how-to/publish/_index.md": LANDING},
        )
        self.assertIn("how-to/publish/_index.md: site landing has no product source", result.stderr)

    def test_cli_page_becomes_section_index(self):
        _, site = self.assert_synced(product({
            "reference/cli.md": PAGE.format(title="CLI", link="platforms.md"),
            "reference/platforms.md": PAGE.format(title="Platforms", link="cli.md"),
        }))
        self.assertIn("reference/cli/_index.md", site)
        self.assertNotIn("reference/cli.md", site)
        self.assertIn("(/docs/reference/cli/)", site["reference/platforms.md"])
        self.assertIn("(/docs/reference/platforms/)", site["reference/cli/_index.md"])

    def test_relative_links_become_root_relative(self):
        _, site = self.assert_synced(product({
            "how-to/publish/post.md": (
                "---\ntitle: Post\n---\n\n"
                "[sibling](reply.md)\n"
                "[cousin](../schedule/jobs.md)\n"
                "[cross](../../reference/platforms.md#limits)\n"
                "[same-page](#a-section)\n"
                "[mail](mailto:team@example.com)\n"
                "[web](https://example.com/x.md)\n"),
            "how-to/publish/reply.md": "---\ntitle: Reply\n---\n\n# Reply\n",
            "reference/note.md": "---\ntitle: Note\n---\n\n[guide](../how-to/publish/reply.md)\n",
            "how-to/schedule/jobs.md": "---\ntitle: Jobs\n---\n\n# Jobs\n",
            "reference/platforms.md": "---\ntitle: Platforms\n---\n\n# Platforms\n",
        }))
        body = site["how-to/publish/post.md"]
        self.assertIn("(/docs/how-to/publish/reply/)", body)
        self.assertIn("(/docs/how-to/schedule/jobs/)", body)
        self.assertIn("(/docs/reference/platforms/#limits)", body)
        self.assertIn("(/docs/how-to/publish/reply/)", site["reference/note.md"])
        self.assertIn("(#a-section)", body)
        self.assertIn("(mailto:team@example.com)", body)
        self.assertIn("(https://example.com/x.md)", body)
        for leftover in ("](reply.md)", "](jobs.md)", "](platforms.md#limits)"):
            self.assertNotIn(leftover, body)

    def test_out_of_scope_links_are_kept_and_reported(self):
        result, site = self.assert_synced(product({
            "how-to/manage/pack.md": (
                "---\ntitle: Pack\ndraft: true\n---\n\n"
                "[assets](../../../store-assets/x/)\n"
                "[secret](../../internal/y.md)\n"
                "[gone](missing.md)\n"),
            "internal/y.md": "---\ntitle: Y\n---\n\n# Y\n",
        }))
        body = site["how-to/manage/pack.md"]
        self.assertIn("](../../../store-assets/x/)", body)
        self.assertIn("](../../internal/y.md)", body)
        self.assertIn("](missing.md)", body)
        self.assertIn("outside the published docs", result.stderr)
        self.assertIn("never published", result.stderr)

    def test_private_repository_links_are_flagged(self):
        result, site = self.assert_synced(product({
            "tutorials/quick.md": (
                "---\ntitle: Quick\ndraft: true\n---\n\n"
                "Open <https://github.com/blowhorn-ai/blowhorn/releases>.\n"
                "See [code](https://github.com/blowhorn-ai/blowhorn/blob/master/x).\n"),
        }))
        body = site["tutorials/quick.md"]
        self.assertIn("https://github.com/blowhorn-ai/blowhorn/releases", body)
        self.assertIn("private product repository", result.stderr)

    def test_draft_pages_stay_draft(self):
        _, site = self.assert_synced(product({
            "tutorials/gated.md": "---\ntitle: G\ndraft: true\n---\n\n# G\n",
        }))
        self.assertIn("draft: true", site["tutorials/gated.md"])

    def test_colliding_alias_is_dropped_and_others_kept(self):
        _, site = self.assert_synced(
            product({
                "how-to/troubleshoot/fix.md": (
                    "---\ntitle: Fix\naliases: [/docs/how-to/troubleshoot/, /docs/how-to/old-fix/]\n"
                    "---\n\n# Fix\n"),
            }),
            docs_seed={"how-to/troubleshoot/_index.md": LANDING},
        )
        body = site["how-to/troubleshoot/fix.md"]
        self.assertNotIn("/docs/how-to/troubleshoot/", body)
        self.assertIn("/docs/how-to/old-fix/", body)

    def test_invalid_heading_id_is_pinned(self):
        result, site = self.assert_synced(product({
            "reference/flags.md": (
                "---\ntitle: Flags\n---\n\n"
                "### `--profile` and `--exclude`\n\n"
                "## 1. Install\n\n"
                "```\n# not a heading\n```\n\n"
                "## Kept {#custom}\n"),
        }))
        body = site["reference/flags.md"]
        self.assertIn("{#section-profile-and---exclude}", body)
        self.assertIn("{#section-1-install}", body)
        self.assertIn("# not a heading", body)
        self.assertNotIn("{#section-not-a-heading}", body)
        self.assertIn("## Kept {#custom}", body)
        self.assertIn("invalid id", result.stderr)

    def test_cloud_name_is_said_as_blowhorn_outside_code(self):
        result, site = self.assert_synced(product({
            "reference/org.md": (
                "---\ntitle: Blowhorn Cloud org\n---\n\n"
                "# Blowhorn Cloud org\n\n"
                "List the members on Blowhorn Cloud. Layer5 Cloud is retired.\n\n"
                "```\nblowhorn org members  # Blowhorn Cloud\n```\n"),
        }))
        body = site["reference/org.md"]
        self.assertIn('title: Blowhorn org', body)
        self.assertIn("# Blowhorn org", body)
        self.assertIn("List the members on Blowhorn. Blowhorn is retired.", body)
        self.assertIn("# Blowhorn Cloud", body.split("```")[1])
        self.assertNotIn("Blowhorn Cloud", body.split("```")[0])
        self.assertIn("said \"Blowhorn Cloud\" or \"Layer5 Cloud\" 4 time(s)", result.stderr)

    def test_missing_title_is_derived_from_h1(self):
        result, site = self.assert_synced(product({
            "explanation/why.md": "# Why things work\n\nBody.\n",
            "explanation/plain.md": "Just body.\n",
        }))
        self.assertIn('title: "Why things work"', site["explanation/why.md"])
        self.assertIn('title: "plain"', site["explanation/plain.md"])
        self.assertIn("no title front matter", result.stderr)

    def test_stale_pages_removed_but_landings_kept(self):
        _, site = self.assert_synced(
            product({"tutorials/first.md": PAGE.format(title="First", link="x.md")}),
            docs_seed={
                "tutorials/_index.md": LANDING,
                "tutorials/gone.md": "old",
                "tutorials/empty/_index.md": LANDING,
            },
        )
        self.assertNotIn("tutorials/gone.md", site)
        self.assertEqual(site["tutorials/_index.md"], LANDING)
        self.assertEqual(site["tutorials/empty/_index.md"], LANDING)

    def test_internal_paths_txt_excludes_listed_paths(self):
        result, site = self.assert_synced(product({
            "internal-paths.txt": "# keep lists\ndocs/reference/draft-api.md\nhow-to/beta/\n",
            "reference/draft-api.md": PAGE.format(title="API", link="x.md"),
            "reference/ok.md": (
                "---\ntitle: OK\n---\n\n[api](draft-api.md)\n[beta](../how-to/beta/soon.md)\n"),
            "how-to/beta/soon.md": PAGE.format(title="Soon", link="x.md"),
        }))
        self.assertNotIn("reference/draft-api.md", site)
        self.assertNotIn("how-to/beta/soon.md", site)
        body = site["reference/ok.md"]
        self.assertIn("](draft-api.md)", body)
        self.assertIn("](../how-to/beta/soon.md)", body)
        self.assertIn("never published", result.stderr)

    def test_internal_paths_txt_under_release_excludes_listed_paths(self):
        # The product keeps the list at release/internal-paths.txt; missing it
        # would publish every page it lists.
        tree = product({
            "reference/draft-api.md": PAGE.format(title="API", link="x.md"),
            "reference/ok.md": PAGE.format(title="OK", link="x.md"),
        })
        tree["release/internal-paths.txt"] = "# the one list\ndocs/internal/\ndocs/reference/draft-api.md\n"
        _, site = self.assert_synced(tree)
        self.assertNotIn("reference/draft-api.md", site)
        self.assertIn("reference/ok.md", site)

    def test_referenced_assets_are_copied(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            product_dir = root / "product" / "docs" / "tutorials"
            product_dir.mkdir(parents=True)
            (product_dir / "shot.md").write_text(
                "---\ntitle: Shot\n---\n\n![shot](img/app.png)\n", encoding="utf-8")
            (product_dir / "img").mkdir()
            (product_dir / "img" / "app.png").write_bytes(b"\x89PNG\r\n")
            docs = root / "site-docs"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(root / "product"), str(docs),
                 "--ref", "test-ref"],
                capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((docs / "tutorials" / "img" / "app.png").read_bytes(),
                             b"\x89PNG\r\n")
            body = (docs / "tutorials" / "shot.md").read_text(encoding="utf-8")
            self.assertIn("(/docs/tutorials/img/app.png)", body)

    def test_second_run_changes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, text in product({
                "how-to/publish/post.md": PAGE.format(title="Post", link="reply.md"),
                "how-to/publish/reply.md": PAGE.format(title="Reply", link="post.md"),
            }).items():
                path = root / "product" / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            docs = root / "site-docs"
            (docs / "how-to" / "publish").mkdir(parents=True)
            (docs / "how-to" / "publish" / "_index.md").write_text(LANDING, encoding="utf-8")
            args = [sys.executable, str(SCRIPT), str(root / "product"), str(docs),
                    "--ref", "test-ref"]
            one = subprocess.run(args, capture_output=True, text=True, check=False)
            before = {p.relative_to(docs).as_posix(): p.read_bytes()
                      for p in docs.rglob("*") if p.is_file()}
            two = subprocess.run(args, capture_output=True, text=True, check=False)
            after = {p.relative_to(docs).as_posix(): p.read_bytes()
                     for p in docs.rglob("*") if p.is_file()}
            self.assertEqual(one.returncode, 0, one.stderr)
            self.assertEqual(two.returncode, 0, two.stderr)
            self.assertEqual(before, after)
            self.assertEqual(one.stdout, two.stdout)

    def test_missing_product_docs_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "product").mkdir()
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(root / "product"), str(root / "docs"),
                 "--ref", "test-ref"],
                capture_output=True, text=True, check=False)
            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
