"""Tests for check_api_reference.py. Synthetic fixture only; see test_openapi_export.py."""

import os
import tempfile
import unittest
from unittest import mock
from pathlib import Path

import check_api_reference as car
import openapi_export as ox

FIXTURE = Path(__file__).resolve().parents[2] / "tests" / "openapi" / "fixtures" / "synthetic.openapi.yaml"


def page(ops=3, notice=True, extra=""):
    body = "".join('<details class="api-op" data-api-op></details>' for _ in range(ops))
    return f'<div data-api-ref>{"Not an HTTP API" if notice else ""}{body}{extra}</div>'


class Case(unittest.TestCase):
    def setUp(self):
        env = mock.patch.dict(os.environ)
        env.start()
        self.addCleanup(env.stop)
        os.environ.pop(car.ENV_SPEC, None)
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.build = self.root / "public"
        (self.build / "docs" / "api").mkdir(parents=True)
        self.out, _ = ox.export_public(ox.load_document(FIXTURE))
        self.write_spec(ox.render(self.out))
        self.config = self.root / "hugo.toml"
        self.set_param("spec/public.json")

    def write_spec(self, text):
        (self.root / "spec").mkdir(exist_ok=True)
        (self.root / "spec" / "public.json").write_text(text, encoding="utf-8")

    def set_param(self, value):
        self.config.write_text(f'[params.apiReference]\n  spec = "{value}"\n', encoding="utf-8")

    def write_page(self, html):
        (self.build / "docs" / "api" / "index.html").write_text(html, encoding="utf-8")

    def problems(self):
        return car.check(self.build, self.config, self.root)


class TestCheck(Case):
    def test_disabled_passes_without_a_spec_or_a_page(self):
        self.set_param("")
        self.assertEqual(self.problems(), [])
        self.assertEqual(car.main([str(self.build), "--config", str(self.config), "--root", str(self.root)]), 0)

    def test_matching_page_passes(self):
        self.write_page(page())
        self.assertEqual(self.problems(), [])

    def test_enabled_but_no_page(self):
        self.assertTrue(any("no built page" in p for p in self.problems()))

    def test_operation_count_must_match(self):
        self.write_page(page(ops=2))
        self.assertTrue(any("renders 2" in p for p in self.problems()))

    def test_notice_is_required(self):
        self.write_page(page(notice=False))
        self.assertTrue(any("notice is missing" in p for p in self.problems()))

    def test_private_mentions_in_the_page(self):
        self.write_page(page(extra="see github.com/blowhorn-ai/blowhorn/blob/master/x"))
        self.assertTrue(any("private" in p for p in self.problems()))
        self.write_page(page(extra="https://github.com/blowhorn-ai/blowhorn-site"))
        self.assertEqual(self.problems(), [])

    def test_the_notice_wording_is_not_a_listener_ad(self):
        self.write_page(page(extra="there is no server URL to send these requests to"))
        self.assertEqual(self.problems(), [])

    def test_listener_wording_in_the_page(self):
        self.write_page(page(extra="<h3>Try this endpoint</h3>"))
        self.assertTrue(any("try it" in p for p in self.problems()))

    def test_reformatted_spec_fails(self):
        import json
        self.write_page(page())
        self.write_spec(json.dumps(self.out, indent=4))
        self.assertTrue(any("canonical public form" in p for p in self.problems()))

    def test_listener_added_by_hand_fails(self):
        import json
        self.write_page(page())
        edited = dict(self.out, servers=[{"url": "https://x.invalid"}])
        self.write_spec(json.dumps(edited, sort_keys=True, indent=2) + "\n")
        self.assertTrue(any("canonical public form" in p for p in self.problems()))

    def test_spec_with_a_non_public_operation_fails(self):
        raw = ox.load_document(FIXTURE)  # unfiltered: not a fixed point
        import json
        self.write_spec(json.dumps(raw))
        self.write_page(page())
        self.assertTrue(self.problems())

    def test_env_override_enables_the_check_when_the_toml_is_disabled(self):
        self.set_param("")
        os.environ[car.ENV_SPEC] = "spec/public.json"
        self.assertTrue(any("no built page" in p for p in self.problems()))
        self.assertEqual(car.main([str(self.build), "--config", str(self.config), "--root", str(self.root)]), 1)
        self.write_page(page())
        self.assertEqual(car.main([str(self.build), "--config", str(self.config), "--root", str(self.root)]), 0)

    def test_env_override_wins_over_the_toml_even_when_empty(self):
        os.environ[car.ENV_SPEC] = ""
        self.assertEqual(self.problems(), [])
        self.assertEqual(car.main([str(self.build), "--config", str(self.config), "--root", str(self.root)]), 0)

    def test_env_override_points_at_its_own_spec(self):
        os.environ[car.ENV_SPEC] = "spec/missing.json"
        self.assertTrue(any("missing.json" in p for p in self.problems()))

    def test_missing_spec_file(self):
        self.set_param("spec/missing.json")
        self.assertTrue(any("missing.json" in p for p in self.problems()))


if __name__ == "__main__":
    unittest.main()
