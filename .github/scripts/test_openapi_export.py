"""Tests for openapi_export.py, against tests/openapi/fixtures/synthetic.openapi.yaml.

The fixture is synthetic by design (every name says so); no real Blowhorn
operation is used or implied. Run with `make test-scripts`.
"""

import copy
import io
import json
import tempfile
import unittest
from unittest import mock
from contextlib import redirect_stderr
from pathlib import Path

import openapi_export as ox

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "openapi" / "fixtures" / "synthetic.openapi.yaml"


def op(audience=None, **extra):
    body = {"summary": "s", "responses": {"200": {"description": "ok"}}, **extra}
    if audience is not None:
        body["x-internal"] = audience
    return body


def doc(**paths):
    return {"openapi": "3.2.1", "info": {"title": "T", "version": "1"},
            "paths": {p: {"post": o} for p, o in paths.items()}}


class Fixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = ox.load_document(FIXTURE)
        cls.out, cls.report = ox.export_public(cls.source)
        cls.text = ox.render(cls.out)

    def ops(self):
        return {(m.upper(), p): o for p, item in self.out["paths"].items()
                for m, o in item.items()}


class TestAudienceFilter(Fixture):
    def test_only_public_operations_survive(self):
        self.assertEqual(
            sorted(p for _, p in self.ops()),
            ["/synthetic-fixture/gadgets", "/synthetic-fixture/widgets",
             "/synthetic-fixture/widgets/{widgetId}"])
        self.assertEqual(self.report["operations"], 7)
        self.assertEqual(self.report["exported"], 3)

    def test_is_public_fails_closed(self):
        for value in (["cloud"], [], None, True, False, 1, {"public": True},
                      "cloud", "Public", ["Public"], [None], [["public"]], "public,cloud"):
            self.assertFalse(ox.is_public({"x-internal": value}), repr(value))
        self.assertFalse(ox.is_public({}))
        self.assertFalse(ox.is_public(None))

    def test_is_public_accepts_public_alone_or_with_others(self):
        for value in ("public", ["public"], ["cloud", "public"], ["public", "cloud"]):
            self.assertTrue(ox.is_public({"x-internal": value}), repr(value))

    def test_cloud_only_is_not_public(self):
        d = doc(**{"/a": op(["cloud"]), "/b": op(["public"])})
        out, _ = ox.export_public(d)
        self.assertEqual(list(out["paths"]), ["/b"])

    def test_path_level_audience_must_include_public_too(self):
        d = doc(**{"/a": op(["public"])})
        d["paths"]["/a"]["x-internal"] = ["cloud"]
        out, _ = ox.export_public(d)
        self.assertEqual(out["paths"], {})
        d["paths"]["/a"]["x-internal"] = ["public", "cloud"]
        out, _ = ox.export_public(d)
        self.assertIn("/a", out["paths"])

    def test_exported_audience_is_normalised_to_public(self):
        for o in self.ops().values():
            self.assertEqual(o["x-internal"], ["public"])

    def test_cloud_only_tag_and_group_vanish(self):
        self.assertNotIn("Synthetic_CloudOnly", self.text)
        self.assertEqual([t["name"] for t in self.out["tags"]],
                         ["Synthetic_Widgets", "Synthetic_Gadgets"])
        self.assertEqual(self.out["x-tagGroups"],
                         [{"name": "Synthetic group",
                           "tags": ["Synthetic_Widgets", "Synthetic_Gadgets"]}])


class TestStripping(Fixture):
    def test_nothing_that_advertises_a_listener_or_links_out(self):
        for needle in ("synthetic-fixture.invalid", "servers",
                       "webhooks", "callbacks", "x-vendor-secret", "x-go-type",
                       "authorizationUrl", "tokenUrl", "contact", "license",
                       "externalValue", "headers", "X-Synthetic", "syntheticHook"):
            self.assertNotIn(needle, self.text, needle)

    def test_top_level_keys_are_an_allow_list(self):
        self.assertEqual(sorted(self.out), ["components", "info", "openapi", "paths",
                                            "tags", "x-tagGroups"])
        self.assertEqual(sorted(self.out["info"]), ["description", "title", "version"])

    def test_property_names_that_look_like_keywords_survive(self):
        props = self.out["components"]["schemas"]["Widget"]["properties"]
        self.assertIn("x-weird", props)
        self.assertIn("externalDocs", props)

    def test_oauth_scheme_not_used_by_an_exported_operation_is_dropped(self):
        self.assertEqual(list(self.out["components"]["securitySchemes"]), ["synthetic_bearer"])


class TestRefsAndReachability(Fixture):
    def test_only_reachable_schemas_are_kept(self):
        # Widget (response), WidgetInput (request), Owner (via Widget), Node (recursive).
        self.assertEqual(sorted(self.out["components"]["schemas"]),
                         ["Node", "Owner", "Widget", "WidgetInput"])
        self.assertNotIn("CloudOnlySchema", self.text)
        self.assertNotIn("UnusedSchema", self.text)

    def test_recursive_schema_terminates(self):
        node = self.out["components"]["schemas"]["Node"]
        self.assertEqual(node["properties"]["children"]["items"],
                         {"$ref": "#/components/schemas/Node"})

    def test_every_ref_in_the_output_resolves(self):
        names = set(self.out["components"]["schemas"])
        refs = set()

        def walk(node):
            if isinstance(node, dict):
                for k, v in node.items():
                    if k == "$ref":
                        refs.add(v)
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)

        walk(self.out)
        self.assertTrue(refs)
        for ref in refs:
            self.assertTrue(ref.startswith("#/components/schemas/"), ref)
            self.assertIn(ref.rsplit("/", 1)[1], names)

    def test_non_schema_components_are_inlined(self):
        update = self.out["paths"]["/synthetic-fixture/widgets/{widgetId}"]["post"]
        self.assertEqual(update["requestBody"]["description"], "Synthetic request body.")
        self.assertEqual(update["responses"]["200"]["description"], "The updated synthetic widget")
        self.assertNotIn("requestBodies", self.out["components"])
        self.assertNotIn("parameters", self.out["components"])

    def test_operation_parameter_replaces_path_level_one(self):
        update = self.out["paths"]["/synthetic-fixture/widgets/{widgetId}"]["post"]
        by_name = {p["name"]: p for p in update["parameters"]}
        self.assertEqual(list(by_name), ["widgetId", "verbose", "mode"])
        self.assertEqual(by_name["widgetId"]["schema"]["type"], "integer")
        self.assertIn("Operation-level", by_name["widgetId"]["description"])
        self.assertEqual(by_name["verbose"]["description"], "Synthetic shared parameter.")

    def test_security_is_materialised_and_explicit_empty_is_kept(self):
        ops = self.ops()
        self.assertEqual(ops[("POST", "/synthetic-fixture/gadgets")]["security"],
                         [{"synthetic_bearer": []}])
        self.assertEqual(ops[("POST", "/synthetic-fixture/widgets")]["security"], [])

    def test_unresolvable_or_external_refs_are_errors(self):
        bad = ("#/components/schemas/Missing", "other.yaml#/Foo", "https://x.invalid/s.json",
               "#/paths/~1a/post", "#/components/links/L")
        for ref in bad:
            d = doc(**{"/a": op(["public"], requestBody={
                "content": {"application/json": {"schema": {"$ref": ref}}}})})
            with self.assertRaises(ox.ExportError, msg=ref):
                ox.export_public(d)

    def test_parameter_ref_cycle_is_an_error(self):
        d = doc(**{"/a": op(["public"], parameters=[{"$ref": "#/components/parameters/A"}])})
        d["components"] = {"parameters": {"A": {"$ref": "#/components/parameters/B"},
                                          "B": {"$ref": "#/components/parameters/A"}}}
        with self.assertRaises(ox.ExportError):
            ox.export_public(d)

    def test_a_ref_in_a_dropped_operation_is_not_followed(self):
        d = doc(**{"/a": op(["cloud"], requestBody={
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Gone"}}}}),
            "/b": op(["public"])})
        out, _ = ox.export_public(d)  # Gone is undefined, but only a cloud operation uses it
        self.assertNotIn("components", out)


class TestPrivateMentions(unittest.TestCase):
    def export(self, **kw):
        return ox.export_public(doc(**{"/a": op(["public"], **kw)}))

    def test_private_repository_urls_and_references_are_errors(self):
        for text in ("see https://github.com/blowhorn-ai/blowhorn/blob/master/x.md",
                     "https://raw.githubusercontent.com/blowhorn-ai/blowhorn/x",
                     "git@github.com:blowhorn-ai/blowhorn.git",
                     "tracked in blowhorn-ai/blowhorn#2163",
                     "BLOWHORN-AI/BLOWHORN",
                     "https://internal.blowhorn.ai/strategy/",
                     "file:///Users/x/openapi.yaml"):
            with self.assertRaises(ox.ExportError, msg=text):
                self.export(description=text)

    def test_the_public_site_repository_is_fine(self):
        self.export(description="https://github.com/blowhorn-ai/blowhorn-site/issues/1")

    def test_error_names_the_json_path_and_writes_nothing(self):
        with self.assertRaises(ox.ExportError) as caught:
            self.export(description="blowhorn-ai/blowhorn")
        self.assertIn("paths./a.post.description", str(caught.exception))

    def test_keys_and_examples_are_scanned_too(self):
        with self.assertRaises(ox.ExportError):
            self.export(requestBody={"content": {"application/json": {
                "example": {"note": "internal.blowhorn.ai"}}}})
        with self.assertRaises(ox.ExportError):
            self.export(requestBody={"content": {"application/json": {
                "schema": {"properties": {"blowhorn-ai/blowhorn": {"type": "string"}}}}}})

    def test_there_is_no_deny_option(self):
        with self.assertRaises(SystemExit):
            with mock.patch("sys.stderr"):
                ox.main(["in.yaml", "out.json", "--deny", "x"])
        with self.assertRaises(TypeError):
            ox.export_public(doc(), deny=["x"])

    def test_private_text_on_a_dropped_operation_does_not_matter(self):
        d = doc(**{"/a": op(["cloud"], description="blowhorn-ai/blowhorn"),
                   "/b": op(["public"])})
        ox.export_public(d)


class TestRejectedDocuments(unittest.TestCase):
    def test_not_openapi_3(self):
        for d in ({}, {"openapi": "2.0", "paths": {}}, {"openapi": 3, "paths": {}},
                  {"openapi": "3.2.1"}, [], None):
            with self.assertRaises(ox.ExportError):
                ox.export_public(d)

    def test_exported_operation_needs_responses(self):
        d = doc(**{"/a": {"x-internal": ["public"], "summary": "s"}})
        with self.assertRaises(ox.ExportError):
            ox.export_public(d)

    def test_duplicate_operation_ids(self):
        d = doc(**{"/a": op(["public"], operationId="x"), "/b": op(["public"], operationId="x")})
        with self.assertRaises(ox.ExportError):
            ox.export_public(d)

    def test_path_item_ref_is_unsupported(self):
        d = {"openapi": "3.2.1", "paths": {"/a": {"$ref": "#/components/pathItems/A"}}}
        with self.assertRaises(ox.ExportError):
            ox.export_public(d)

    def test_security_scheme_must_exist(self):
        d = doc(**{"/a": op(["public"], security=[{"nope": []}])})
        with self.assertRaises(ox.ExportError):
            ox.export_public(d)


class TestOutput(Fixture):
    def test_deterministic(self):
        again, _ = ox.export_public(ox.load_document(FIXTURE))
        self.assertEqual(ox.render(again), self.text)

    def test_key_order_of_the_input_does_not_matter(self):
        shuffled = json.loads(json.dumps(self.source))
        shuffled["paths"] = dict(reversed(list(shuffled["paths"].items())))
        shuffled["components"]["schemas"] = dict(reversed(list(shuffled["components"]["schemas"].items())))
        out, _ = ox.export_public(shuffled)
        self.assertEqual(ox.render(out), self.text)

    def test_idempotent(self):
        again, report = ox.export_public(json.loads(self.text))
        self.assertEqual(ox.render(again), self.text)
        self.assertEqual(report["exported"], report["operations"])

    def test_format_is_stable_json(self):
        self.assertTrue(self.text.endswith("}\n"))
        self.assertEqual(json.loads(self.text), self.out)
        self.assertIn('\n  "openapi": "3.2.1"', self.text)

    def test_does_not_mutate_the_input(self):
        before = copy.deepcopy(self.source)
        ox.export_public(self.source)
        self.assertEqual(self.source, before)

    def test_nan_is_rejected(self):
        d = doc(**{"/a": op(["public"], description="x")})
        d["paths"]["/a"]["post"]["parameters"] = [
            {"name": "n", "in": "query", "schema": {"type": "number", "default": float("nan")}}]
        out, _ = ox.export_public(d)
        with self.assertRaises(ValueError):
            ox.render(out)


class TestYamlQuirks(Fixture):
    def test_yes_no_on_off_stay_strings(self):
        update = self.out["paths"]["/synthetic-fixture/widgets/{widgetId}"]["post"]
        mode = [p for p in update["parameters"] if p["name"] == "mode"][0]
        self.assertEqual(mode["schema"]["enum"], ["on", "off", "no", "yes"])

    def test_dates_stay_strings(self):
        listing = self.out["paths"]["/synthetic-fixture/widgets"]["post"]
        value = listing["responses"]["200"]["content"]["application/json"]["examples"]["first"]["value"]
        self.assertEqual(value[0]["released"], "2026-01-01")

    def test_true_false_are_still_booleans(self):
        update = self.out["paths"]["/synthetic-fixture/widgets/{widgetId}"]["post"]
        self.assertIs(update["requestBody"]["required"], True)

    def test_duplicate_keys_are_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dup.yaml"
            path.write_text("openapi: 3.2.1\npaths: {}\npaths: {}\n")
            with self.assertRaises(ox.ExportError):
                ox.load_document(path)

    def test_unknown_extension_and_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ox.ExportError):
                ox.load_document(Path(tmp) / "nope.yaml")
            other = Path(tmp) / "spec.txt"
            other.write_text("{}")
            with self.assertRaises(ox.ExportError):
                ox.load_document(other)

    def test_json_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.json"
            path.write_text(json.dumps(self.source))
            out, _ = ox.export_public(ox.load_document(path))
            self.assertEqual(ox.render(out), self.text)


class TestCommandLine(unittest.TestCase):
    def run_cli(self, *args):
        err = io.StringIO()
        with redirect_stderr(err):
            code = ox.main(list(args))
        return code, err.getvalue()

    def test_writes_the_output_and_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "nested" / "public.json"
            code, err = self.run_cli(str(FIXTURE), str(out))
            self.assertEqual(code, 0)
            self.assertIn("exported 3 of 7", err)
            self.assertEqual(json.loads(out.read_text())["openapi"], "3.2.1")

    def test_failure_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "leaky.json"
            src.write_text(json.dumps(doc(**{"/a": op(["public"], description="blowhorn-ai/blowhorn")})))
            out = Path(tmp) / "public.json"
            code, err = self.run_cli(str(src), str(out))
            self.assertEqual(code, 1)
            self.assertIn("private", err)
            self.assertFalse(out.exists())

    def test_missing_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, _ = self.run_cli(str(Path(tmp) / "none.yaml"), str(Path(tmp) / "o.json"))
            self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
