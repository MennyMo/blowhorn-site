#!/usr/bin/env python3
"""Docs attribution events (assets/js/docs-attribution.js, data/docs_events.json).

Runs the script's pure builders and its DOM wiring through
docs_attribution_harness.js, then checks: nothing is sent or stored before
consent, consent given on the page starts it, every other analytics page
captures the first touch and sends nothing, withdrawing consent clears it
(assets/js/consent.js), the client comes from the nearest enclosing client
heading, links classify by kind, query strings and
full referrers never leave the page, and every payload validates against
schemas/defs/docs-event.schema.json (ajv, as make check-schemas runs it).

Run with `make test-scripts` (CI runs it too).
"""

import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / ".github/scripts/docs_attribution_harness.js"
DEFS = ROOT / "schemas/defs/docs-event.schema.json"
DEFS_ID = "https://blowhorn.ai/schemas/defs/docs-event.schema.json"
CONFIG = json.loads((ROOT / "data/docs_events.json").read_text(encoding="utf-8"))
AJV_VERSION_RE = re.compile(r"^AJV_CLI_VERSION\s*\??=\s*(\S+)\s*$")

GUIDE = "https://blowhorn.ai/docs/how-to/set-up/connect-mcp-client/"
OFF_GUIDES = "https://blowhorn.ai/pricing/"
NODES = [
    {"h": 2, "id": "connect-a-client"},
    {"h": 3, "id": "claude-code"},
    {"card": "json", "title": "settings.json", "name": "card"},
    {"a": "https://www.npmjs.com/package/blowhorn?activeTab=readme#install", "name": "npm"},
    {"a": "/docs/reference/mcp-server/", "name": "internal"},
    {"h": 2, "id": "authentication"},
    {"card": "bash", "title": "terminal", "name": "shell"},
    {"a": "https://github.com/blowhorn-ai/blowhorn-site/releases/download/v1.0.0/Blowhorn.dmg?x=1", "name": "dmg"},
]


def ajv_cli_version():
    env = os.environ.get("AJV_CLI_VERSION")
    if env:
        return env
    for line in (ROOT / "Makefile").read_text(encoding="utf-8").splitlines():
        match = AJV_VERSION_RE.match(line)
        if match:
            return match.group(1)
    raise RuntimeError("AJV_CLI_VERSION not set in the environment or Makefile")


def harness(mode, payload):
    out = subprocess.run(
        ["node", str(HARNESS), mode, json.dumps(payload)],
        capture_output=True, text=True, cwd=ROOT, check=True,
    )
    return json.loads(out.stdout)


def pure(*calls):
    return harness("pure", [{"fn": fn, "args": list(args)} for fn, *args in calls])


def page(**scenario):
    scenario.setdefault("url", GUIDE)
    scenario.setdefault("nodes", NODES)
    return harness("page", scenario)


def events(calls):
    return [(c[1], c[2]) for c in calls if c[0] == "event"]


def stored(result):
    return json.loads(result["session"][CONFIG["storage_key"]])


class ConsentTests(unittest.TestCase):
    STEPS = [{"click": "card"}, {"click": "npm"}, {"aux": "dmg", "button": 1}]

    def assert_silent(self, result):
        self.assertTrue(all(step == [] for step in result["after"]), result["after"])
        self.assertEqual(result["session"], {})
        self.assertEqual(result["localWrites"], [])

    def test_nothing_before_consent(self):
        self.assert_silent(page(consent=None, steps=self.STEPS, url=GUIDE + "?utm_source=x"))

    def test_nothing_when_declined(self):
        self.assert_silent(page(consent="denied", steps=self.STEPS))

    def test_nothing_without_the_partial(self):
        self.assert_silent(page(consent="granted", partial=False, steps=self.STEPS))

    def test_off_the_guides_nothing_is_sent(self):
        result = page(consent="granted", url=OFF_GUIDES, steps=self.STEPS)
        self.assertTrue(all(step == [] for step in result["after"]), result["after"])
        self.assertIn(CONFIG["storage_key"], result["session"])
        self.assertEqual(result["localWrites"], [])

    def test_consent_on_the_page_starts_from_that_point(self):
        result = page(consent=None, steps=[{"click": "card"}, {"grant": True}, {"click": "card"}])
        self.assertEqual(result["after"][1], [])
        self.assertEqual([n for n, _ in events(result["after"][2])], ["docs_guide_view"])
        self.assertEqual([n for n, _ in events(result["after"][3])], ["docs_guide_view", "docs_snippet_copy"])
        self.assertIn(CONFIG["storage_key"], result["session"])
        self.assertEqual(result["localWrites"], [])

    def test_granted_reader_gets_guide_view_on_load(self):
        result = page(consent="granted", url=GUIDE + "#cursor")
        (name, params), = events(result["after"][0])
        self.assertEqual(name, "docs_guide_view")
        self.assertEqual(params["client"], "Cursor")
        self.assertEqual(params["guide"], "connect-mcp-client")


class AttributionTests(unittest.TestCase):
    def test_utm_and_external_referrer_host(self):
        result = page(
            consent="granted",
            url=GUIDE + "?utm_source=newsletter&utm_medium=email&utm_campaign=mcp&utm_content=hero&utm_term=claude&email=a@b.c",
            referrer="https://news.example.com/item?id=42&user=someone",
        )
        (_, params), = events(result["after"][0])
        self.assertEqual(
            {k: params[k] for k in CONFIG["attribution_params"]},
            {
                "first_source": "newsletter",
                "first_medium": "email",
                "first_campaign": "mcp",
                "first_content": "hero",
                "first_term": "claude",
                "first_referrer_host": "news.example.com",
                "landing_guide": "connect-mcp-client",
                "landing_page": "/docs/how-to/set-up/connect-mcp-client/",
            },
        )
        stored = result["session"][CONFIG["storage_key"]]
        self.assertNotIn("id=42", stored)
        self.assertNotIn("a@b.c", stored)

    def test_internal_referrers_are_ignored(self):
        for ref in ["https://blowhorn.ai/docs/", "https://www.blowhorn.ai/", ""]:
            result = page(consent="granted", referrer=ref)
            (_, params), = events(result["after"][0])
            self.assertEqual(params["first_referrer_host"], "(none)", ref)
        self.assertEqual(
            pure(("referrerHost", "http://localhost:1313/ai/", "localhost:1313"), ("referrerHost", "not a url", "blowhorn.ai")),
            ["(none)", "(none)"],
        )

    def test_first_touch_is_kept_for_the_session(self):
        first = {k: "(none)" for k in CONFIG["attribution_params"]}
        first.update(first_source="launch", landing_guide="mcp")
        result = page(consent="granted", session=first, url=GUIDE + "?utm_source=later")
        (_, params), = events(result["after"][0])
        self.assertEqual(params["first_source"], "launch")
        self.assertEqual(params["landing_guide"], "mcp")


class SitewideCaptureTests(unittest.TestCase):
    def test_untracked_landing_carries_to_a_guide(self):
        landing = page(
            consent="granted", url=OFF_GUIDES + "?utm_source=launch&utm_medium=social&email=a@b.c",
            referrer="https://news.example.com/item?id=42",
        )
        self.assertEqual(landing["after"], [[]])
        first = stored(landing)
        self.assertEqual(
            {k: first[k] for k in ("first_source", "first_medium", "first_referrer_host", "landing_page", "landing_guide")},
            {"first_source": "launch", "first_medium": "social", "first_referrer_host": "news.example.com",
             "landing_page": "/pricing/", "landing_guide": "(none)"},
        )
        self.assertNotIn("a@b.c", landing["session"][CONFIG["storage_key"]])

        guide = page(consent="granted", session=first, url=GUIDE + "?utm_source=later",
                     referrer="https://blowhorn.ai/pricing/")
        (name, params), = events(guide["after"][0])
        self.assertEqual(name, "docs_guide_view")
        self.assertEqual(params["first_source"], "launch")
        self.assertEqual(params["first_referrer_host"], "news.example.com")
        self.assertEqual(params["landing_page"], "/pricing/")
        self.assertEqual(params["landing_guide"], "connect-mcp-client")

        later = page(consent="granted", session=stored(guide), url="https://blowhorn.ai/ai/mcp/")
        (_, params), = events(later["after"][0])
        self.assertEqual((params["landing_guide"], params["landing_page"]), ("connect-mcp-client", "/pricing/"))

    def test_internal_referrer_is_ignored_on_untracked_pages(self):
        for ref in ["https://blowhorn.ai/", "https://www.blowhorn.ai/docs/", ""]:
            result = page(consent="granted", url=OFF_GUIDES, referrer=ref)
            self.assertEqual(stored(result)["first_referrer_host"], "(none)", ref)

    def test_nothing_stored_before_consent_on_untracked_pages(self):
        for consent in (None, "denied"):
            result = page(consent=consent, url=OFF_GUIDES + "?utm_source=x", referrer="https://news.example.com/")
            self.assertEqual(result["session"], {}, consent)
            self.assertEqual(result["localWrites"], [], consent)
            self.assertEqual(result["after"], [[]], consent)

    def test_capture_when_consent_is_granted_on_the_page(self):
        result = page(consent=None, url=OFF_GUIDES + "?utm_campaign=mcp", steps=[{"grant": True}])
        self.assertEqual(result["after"], [[], []])
        first = stored(result)
        self.assertEqual((first["first_campaign"], first["landing_page"]), ("mcp", "/pricing/"))

    def test_first_touch_wins_and_only_fills_a_missing_guide(self):
        fresh, guide = pure(
            ("captureAttribution", "?utm_source=b", "", "blowhorn.ai", "/ai/mcp/", True),
            ("firstTouch", {"first_source": "a", "landing_guide": "(none)", "landing_page": "/"},
             {"first_source": "b", "landing_guide": "mcp", "landing_page": "/ai/mcp/"}),
        )
        self.assertEqual((fresh["landing_guide"], fresh["landing_page"]), ("mcp", "/ai/mcp/"))
        self.assertEqual(guide, {"first_source": "a", "landing_guide": "mcp", "landing_page": "/"})


class WithdrawalTests(unittest.TestCase):
    FIRST = {"first_source": "launch", "landing_page": "/pricing/"}

    def test_withdrawing_consent_clears_the_first_touch(self):
        result = harness("consent", {"consent": "granted", "session": self.FIRST, "choose": "denied"})
        self.assertEqual(result["consent"], "denied")
        self.assertNotIn(CONFIG["storage_key"], result["session"])

    def test_declining_clears_and_accepting_keeps(self):
        declined = harness("consent", {"consent": None, "session": self.FIRST, "choose": "denied"})
        self.assertNotIn(CONFIG["storage_key"], declined["session"])
        kept = harness("consent", {"consent": "granted", "session": self.FIRST, "choose": "granted"})
        self.assertEqual(json.loads(kept["session"][CONFIG["storage_key"]]), self.FIRST)


class ClientTests(unittest.TestCase):
    def test_nearest_enclosing_client_heading(self):
        h = lambda level, id_: {"level": level, "id": id_}
        self.assertEqual(
            pure(
                ("clientFor", [h(2, "connect-a-client"), h(3, "claude-code")], ""),
                ("clientFor", [h(2, "connect-a-client"), h(3, "claude-code"), h(2, "authentication")], ""),
                ("clientFor", [h(2, "zed"), h(3, "settings")], ""),
                ("clientFor", [h(3, "cursor"), h(3, "troubleshooting")], ""),
                ("clientFor", [h(3, "claude-desktop-1")], ""),
                ("clientFor", [h(3, "vs-code")], ""),
                ("clientFor", [h(2, "start-the-server")], "goose"),
                ("clientFor", [], "Gemini CLI"),
                ("clientFor", [], "nope"),
                ("hashClient", "#windsurf-devin-desktop", ""),
                ("hashClient", "#authentication", "cline"),
                ("hashClient", "", ""),
            ),
            [
                "Claude Code", "general", "Zed", "general", "Claude Desktop",
                "VS Code with GitHub Copilot", "Goose", "Gemini CLI", "general",
                "Windsurf (Devin Desktop)", "Cline", "general",
            ],
        )

    def test_dom_reads_the_heading_before_the_card(self):
        result = page(consent="granted", steps=[{"click": "card"}, {"click": "shell"}])
        copies = [p for n, p in events(result["after"][-1]) if n == "docs_snippet_copy"]
        self.assertEqual([(p["client"], p["snippet_kind"], p["snippet_title"]) for p in copies],
                         [("Claude Code", "json", "settings.json"), ("general", "shell", "terminal")])

    def test_front_matter_client_is_the_fallback(self):
        result = page(consent="granted", mcpClient="chatgpt", steps=[{"click": "shell"}])
        (_, view), (_, copy) = events(result["after"][-1])
        self.assertEqual(view["client"], "ChatGPT")
        self.assertEqual(copy["client"], "ChatGPT")

    def test_snippet_kinds(self):
        self.assertEqual(
            pure(*[("snippetKind", lang) for lang in ["json", "toml", "yaml", "bash", "text", "python", ""]]),
            ["json", "toml", "yaml", "shell", "text", "other", "other"],
        )


class OutboundTests(unittest.TestCase):
    def test_link_kinds(self):
        cases = {
            "https://www.npmjs.com/package/@blowhorn/mcp": "npm",
            "https://npmjs.com/package/blowhorn": "npm",
            "https://registry.npmjs.org/blowhorn": "npm",
            "https://registry.modelcontextprotocol.io/v0/servers?search=blowhorn": "registry",
            "https://github.com/mcp": "registry",
            "https://github.com/mcp/blowhorn-ai/blowhorn": "registry",
            "https://github.com/mcpx": None,
            "https://github.com/blowhorn-ai/blowhorn-site/releases": "download",
            "https://github.com/blowhorn-ai/blowhorn-site/releases/download/v1.61.0/Blowhorn-1.61.0-mac-universal.dmg": "download",
            "https://github.com/blowhorn-ai/blowhorn-site": None,
            "https://blowhorn.ai/download/": "download",
            "https://blowhorn.ai/download/thanks/": "download",
            "http://localhost:1313/download/": "download",
            "https://blowhorn.ai/docs/": None,
            "https://evil.example/download/": None,
            "https://npmjs.com.evil.example/x": None,
            "mailto:hello@blowhorn.ai": None,
        }
        got = pure(*[("linkKind", url, "localhost") for url in cases])
        self.assertEqual(dict(zip(cases, got)), cases)

    def test_query_strings_and_fragments_are_stripped(self):
        self.assertEqual(
            pure(
                ("cleanUrl", "https://user:pw@www.npmjs.com/package/x?token=secret#readme"),
                ("cleanUrl", "https://blowhorn.ai/download/?utm_source=docs"),
            ),
            ["https://www.npmjs.com/package/x", "https://blowhorn.ai/download/"],
        )

    def test_dom_clicks(self):
        result = page(consent="granted", steps=[
            {"click": "npm"}, {"click": "internal"}, {"aux": "dmg", "button": 2}, {"aux": "dmg", "button": 1},
        ])
        clicks = [p for n, p in events(result["after"][-1]) if n == "docs_outbound_click"]
        self.assertEqual(
            [(p["link_kind"], p["link_url"], p["client"]) for p in clicks],
            [
                ("npm", "https://www.npmjs.com/package/blowhorn", "Claude Code"),
                ("download", "https://github.com/blowhorn-ai/blowhorn-site/releases/download/v1.0.0/Blowhorn.dmg", "general"),
            ],
        )


@unittest.skipUnless(shutil.which("npx"), "npx is required to run ajv")
class PayloadSchemaTests(unittest.TestCase):
    def ajv(self, event, files):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        wrapper = tmp / "wrapper.schema.json"
        wrapper.write_text(json.dumps({"$ref": f"{DEFS_ID}#/definitions/{event}"}), encoding="utf-8")
        cmd = ["npx", "--yes", f"ajv-cli@{ajv_cli_version()}", "validate", "--strict=false",
               "-s", str(wrapper), "-r", str(DEFS)]
        for i, payload in enumerate(files):
            path = tmp / f"{event}-{i}.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            cmd += ["-d", str(path)]
        return subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, check=False)

    def produced(self):
        long = "x" * 300
        ctx = {"path": "/ai/mcp/", "hash": "#zed", "host": "blowhorn.ai", "pageClient": "",
               "attribution": {"first_source": long, "landing_guide": "mcp"}}
        built = pure(
            ("guideView", ctx),
            ("snippetCopy", ctx, {"lang": "toml", "title": long, "headings": []}),
            ("outboundClick", ctx, {"url": "https://registry.modelcontextprotocol.io/v0/servers?q=1", "headings": []}),
            ("outboundClick", {**ctx, "attribution": None}, {"url": "https://blowhorn.ai/download/?a=b", "headings": []}),
        )
        result = page(
            consent=None, url=GUIDE + "?utm_source=x#claude-desktop", referrer="https://www.google.com/search?q=blowhorn",
            steps=[{"grant": True}, {"click": "card"}, {"click": "shell"}, {"click": "npm"}, {"click": "dmg"}],
        )
        return [(e["name"], e["params"]) for e in built] + events(result["after"][-1])

    def test_every_payload_matches_its_schema_and_config(self):
        produced = self.produced()
        self.assertEqual({n for n, _ in produced}, set(CONFIG["events"]))
        for name, params in produced:
            self.assertEqual(list(params), CONFIG["events"][name]["params"] + CONFIG["attribution_params"], name)
            for value in params.values():
                self.assertLessEqual(len(value), 100)
                self.assertNotIn("?", value)
        for name in CONFIG["events"]:
            files = [p for n, p in produced if n == name]
            result = self.ajv(name, files)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_schema_rejects_query_strings_and_full_referrers(self):
        _, good = self.produced()[2]
        for key, bad in [("link_url", "https://www.npmjs.com/x?token=1"),
                         ("first_referrer_host", "https://news.example.com/a"),
                         ("page_path", "/ai/mcp/?utm_source=x")]:
            result = self.ajv("docs_outbound_click", [{**good, key: bad}])
            self.assertNotEqual(result.returncode, 0, key)


class WiringTests(unittest.TestCase):
    def test_partial_is_analytics_gated_and_included(self):
        partial = (ROOT / "layouts/_partials/docs-attribution.html").read_text(encoding="utf-8")
        self.assertIn('partial "analytics-enabled.html"', partial)
        self.assertIn("site.Data.docs_events", partial)
        for layout in ["layouts/baseof.html", "layouts/_partials/docs-scripts.html"]:
            self.assertIn('partial "docs-attribution.html"', (ROOT / layout).read_text(encoding="utf-8"), layout)

    def test_consent_js_announces_the_grant(self):
        consent = (ROOT / "assets/js/consent.js").read_text(encoding="utf-8")
        self.assertIn(f"new CustomEvent('{CONFIG['consent_event']}'", consent)
        self.assertEqual(CONFIG["consent_key"], re.search(r"var KEY = '([^']+)'", consent).group(1))
        self.assertEqual(CONFIG["storage_key"], re.search(r"var ATTRIBUTION = '([^']+)'", consent).group(1))

    def test_partial_emits_the_capture_keys_off_the_guides(self):
        partial = (ROOT / "layouts/_partials/docs-attribution.html").read_text(encoding="utf-8")
        keys = json.loads(re.search(r"const CAPTURE_KEYS = (\[[^\]]*\]);", HARNESS.read_text(encoding="utf-8")).group(1))
        emitted = re.findall(r'"([a-z_]+)" \$cfg\.([a-z_]+)', partial)
        self.assertEqual([k for k, v in emitted if k == v], keys)

    def test_script_names_no_host(self):
        script = (ROOT / "assets/js/docs-attribution.js").read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"https?://", script))

    def test_synced_content_carries_no_hooks(self):
        files = [ROOT / "content/en/ai/mcp.md", *sorted((ROOT / "content/en/docs").rglob("*.md"))]
        for path in files:
            text = path.read_text(encoding="utf-8")
            for hook in ("docs-attribution", "docs-events", "data-mcp-client", "docs_snippet_copy"):
                self.assertNotIn(hook, text, path)


if __name__ == "__main__":
    unittest.main()
