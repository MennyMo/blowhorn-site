"""Regression tests for the consent-first Google Analytics template."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class AnalyticsTemplateTests(unittest.TestCase):
    def test_analytics_defaults_to_denied_and_loads_nothing(self):
        template = (ROOT / "layouts/_partials/analytics.html").read_text()

        self.assertIn("analytics_storage: 'denied'", template)
        self.assertIn("ad_storage: 'denied'", template)
        self.assertNotIn("gtag/js", template)
        self.assertIn("consent.js", template)

    def test_cookie_notice_files_exist(self):
        self.assertTrue((ROOT / "assets/js/consent.js").exists())
        self.assertTrue((ROOT / "layouts/_partials/consent.html").exists())

    def test_cookie_choices_control_analytics(self):
        footer = (ROOT / "layouts/_partials/footer.html").read_text()

        self.assertIn("data-consent-open", footer)
        self.assertIn('partial "consent.html"', footer)


if __name__ == "__main__":
    unittest.main()
