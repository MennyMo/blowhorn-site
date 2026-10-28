#!/usr/bin/env python3
"""Users see Blowhorn: never Layer5 Cloud or Blowhorn Cloud, and Layer5 only
in the footer and on the legal pages. Every page says computers, never
machines; marketing copy never says Macs or your Mac. The Google Chrome
requirement is stated with versions, never "for now", and the docs say
Chrome profile and Chrome extension.

Run with `make test-scripts` (CI runs it too).
"""

import tempfile
import unittest
from pathlib import Path

import check_naming as check

PAGE = "<html><head>{head}</head><body><main>{main}</main><footer>{footer}</footer></body></html>"


def page(main="", footer="", head=""):
    return PAGE.format(main=main, footer=footer, head=head)


class TheServiceIsBlowhorn(unittest.TestCase):
    def build(self, pages):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        for rel, html in pages.items():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(html, encoding="utf-8")
        return check.check(root)

    def test_blowhorn_and_its_sign_in_url_pass(self):
        failures = self.build({"index.html": page(
            '<p>Sign in to your Blowhorn account at <a href="https://cloud.blowhorn.ai">cloud.blowhorn.ai</a>.</p>')})
        self.assertEqual(failures, [])

    def test_layer5_cloud_fails_even_in_the_footer(self):
        failures = self.build({"index.html": page(footer="<p>Layer5 Cloud status</p>")})
        self.assertEqual(len(failures), 1)
        self.assertIn("Layer5 Cloud", failures[0])

    def test_blowhorn_cloud_fails_in_any_case(self):
        failures = self.build({"docs/index.html": page("<p>Open blowhorn cloud.</p>")})
        self.assertEqual(len(failures), 1)

    def test_layer5_cloud_in_an_attribute_or_meta_fails(self):
        failures = self.build({
            "a/index.html": page('<img src="x.png" alt="Layer5 Cloud">'),
            "b/index.html": page(head='<meta name="description" content="Built on Blowhorn Cloud">'),
        })
        self.assertEqual(len(failures), 2)

    def test_layer5_outside_the_footer_fails(self):
        failures = self.build({"brand/index.html": page("<p>Marks of Layer5, Inc.</p>")})
        self.assertEqual(len(failures), 1)
        self.assertIn("outside the footer", failures[0])

    def test_layer5_in_the_footer_and_legal_pages_passes(self):
        failures = self.build({
            "index.html": page(footer='<img src="l.svg" alt="Layer5 Blowhorn"><p>© Layer5, Inc.</p>'),
            "legal/terms/index.html": page("<p>An agreement with Layer5, Inc.</p>"),
            "legal/privacy/index.html": page("<p>Layer5 keeps the list.</p>"),
            "legal/index.html": page("<p>Policies of Layer5, Inc.</p>"),
        })
        self.assertEqual(failures, [])

    def test_repository_urls_ids_scripts_and_comments_pass(self):
        failures = self.build({"index.html": page(
            '<!-- Layer5 green --><p id="on-layer5-cloud">'
            '<a href="https://github.com/blowhorn-ai/blowhorn-site">blowhorn-ai/blowhorn-site</a></p>'
            '<script>var x = "Layer5 Cloud";</script>')})
        self.assertEqual(failures, [])

    def test_layer5_in_a_command_sample_passes_but_layer5_cloud_does_not(self):
        failures = self.build({"docs/reference/cli/analytics/index.html": page(
            "<pre><code>blowhorn analytics history --subject Layer5</code></pre>"
            "<p>Run <code>blowhorn auth login</code> for Layer5 Cloud.</p>")})
        self.assertEqual(len(failures), 1)
        self.assertIn("Layer5 Cloud", failures[0])

    def test_layer5_in_prose_beside_code_still_fails(self):
        failures = self.build({"docs/index.html": page("<p>Use <code>x</code> with Layer5 today.</p>")})
        self.assertEqual(len(failures), 1)

    def test_the_generated_cli_reference_gets_no_allowance(self):
        failures = self.build({"docs/reference/cli/auth/index.html": page("<p>Sign in to Layer5 Cloud.</p>")})
        self.assertEqual(len(failures), 1)
        self.assertIn("docs/reference/cli/auth/index.html", failures[0])

    def test_macs_in_marketing_copy_fails(self):
        failures = self.build({
            "index.html": page("<h2>You give the orders. Your Macs carry them out.</h2>"),
            "major/index.html": page("<p>He keeps them on your own Mac.</p>"),
            "download/index.html": page(head='<meta name="description" content="Install Blowhorn on your Mac">'),
            "home-oil/index.html": page(footer="<p>Runs on every Mac you own.</p>"),
            "compare/x/index.html": page('<img src="a.png" alt="Two MACS">'),
        })
        self.assertEqual(len(failures), 5)
        self.assertTrue(all("say computers" in f for f in failures))

    def test_computers_macos_and_the_download_button_pass(self):
        failures = self.build({"index.html": page(
            "<h2>You give the orders. Your computers carry them out.</h2>"
            "<p>One macOS disk image for Apple silicon and Intel.</p>"
            '<a href="/download/">Download for Mac</a><p>Blowhorn-mac.dmg, Computer 1, machinery</p>')})
        self.assertEqual(failures, [])

    def test_macs_in_docs_home_reveille_and_code_pass(self):
        failures = self.build({
            "docs/reference/requirements/index.html": page("<p>What your Mac needs. Intel Macs work.</p>"),
            "home-reveille/index.html": page("<h2>Your Macs carry them out.</h2>"),
            "index.html": page("<pre><code>echo your Mac</code></pre>"),
        })
        self.assertEqual(failures, [])

    def test_macs_in_prose_beside_code_still_fails(self):
        failures = self.build({"index.html": page("<p>Run <code>blowhorn</code> on all your Macs.</p>")})
        self.assertEqual(len(failures), 1)

    def test_machines_fail_everywhere_docs_included(self):
        failures = self.build({
            "index.html": page("<h2>Your machines carry them out.</h2>"),
            "docs/reference/x/index.html": page("<p>Install it on each machine.</p>"),
            "legal/index.html": page(footer="<p>One Machine at a time.</p>"),
            "compare/x/index.html": page('<img src="a.png" alt="Two MACHINES">'),
        })
        self.assertEqual(len(failures), 4)
        self.assertTrue(all("say computer" in f for f in failures))

    def test_machine_idioms_code_and_identifiers_pass(self):
        failures = self.build({"docs/index.html": page(
            "<p>Bluesky feeds can use machine learning. The output is machine-readable."
            " A state machine. Expandi is a serious outbound machine.</p>"
            '<p class="machines-pill" data-machines="1"><a href="/x/#on-your-machine">On your computer</a></p>'
            "<pre><code>blowhorn store machines</code></pre><p>Run <code>--machine a</code>.</p>")})
        self.assertEqual(failures, [])

    def test_the_generated_cli_reference_passes(self):
        failures = self.build({"docs/reference/cli/store/index.html": page(
            "<p>Report whether this machine can reach the Blowhorn database.</p>")})
        self.assertEqual(failures, [])

    def test_a_vague_chrome_requirement_fails_on_every_page(self):
        failures = self.build({
            "download/index.html": page("<p>Google Chrome is required for now. Support for more browsers is planned.</p>"),
            "index.html": page("<p><span>Google Chrome, for now</span></p>"),
        })
        self.assertEqual(len(failures), 3)
        self.assertTrue(all("with versions" in f for f in failures))

    def test_the_exact_chrome_requirement_and_skip_for_now_pass(self):
        failures = self.build({
            "download/index.html": page("<p>Requires macOS 13 or newer and Google Chrome 142 or newer.</p>"),
            "docs/how-to/set-up/first-muster-setup/index.html": page(
                "<p><strong>Skip for now</strong> finishes guided setup.</p>"),
        })
        self.assertEqual(failures, [])

    def test_docs_say_chrome_profile_and_chrome_extension(self):
        failures = self.build({"docs/how-to/set-up/map-chrome-profiles/index.html": page(
            "<p>Map each browser profile.</p><p>Install the browser extension.</p>"
            "<p>Sign-in opens your browser.</p><p>Run <code>blowhorn chrome profiles</code>.</p>")})
        self.assertEqual(len(failures), 2)
        self.assertIn("Chrome profile or Chrome extension", failures[0])

    def test_marketing_and_the_cli_reference_may_say_browser_extension(self):
        failures = self.build({
            "index.html": page("<p>Add the browser extension to each browser profile.</p>"),
            "docs/reference/cli/chrome/index.html": page("<p>Checks the browser profile.</p>"),
        })
        self.assertEqual(failures, [])

    def test_main_fails_on_macs(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "index.html").write_text(page("<p>Your Macs share one queue.</p>"), encoding="utf-8")
            self.assertEqual(check.main(["check_naming.py", tmp]), 1)

    def test_main_fails_on_a_problem(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "index.html").write_text(page("<p>Layer5 Cloud keeps it in sync.</p>"), encoding="utf-8")
            self.assertEqual(check.main(["check_naming.py", tmp]), 1)


if __name__ == "__main__":
    unittest.main()
