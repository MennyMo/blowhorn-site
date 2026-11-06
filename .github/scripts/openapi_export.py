#!/usr/bin/env python3
"""Export the public subset of an OpenAPI document for the docs API reference.

Usage: openapi_export.py INPUT OUTPUT

  INPUT   a local OpenAPI 3.x file (.yaml, .yml or .json); nothing is fetched
  OUTPUT  the JSON the reference page renders (the Hugo site param
          params.apiReference.spec names it; docs/api-reference.md)

The reference page is public, so this is the one place that decides what may
reach it, and every rule fails closed:

- An operation is exported only when its x-internal audience list contains
  "public" (exactly; "cloud" alone, a missing key or any other shape is not
  enough). A path item that carries x-internal must list "public" too.
- Each exported object is rebuilt from an allow-list of keys. Servers
  (a listener the product does not ship), externalDocs, webhooks, callbacks,
  links, OAuth flow URLs, contact and licence blocks and every x- extension
  but x-order, x-displayName and x-tagGroups are dropped.
- Path-level parameters, $ref parameters, request bodies, responses and
  examples are inlined into each operation, and the effective security
  requirement (the operation's own, else the document's) is written into it.
  Only components.schemas and components.securitySchemes survive, and only the
  ones the exported operations can reach. Any $ref that is not a local
  #/components/... pointer is an error.
- The result must not mention the private product repository or the internal
  site (the fixed DENY_PATTERNS below, which check_api_reference.py also enforces). A match is an error that
  names the JSON path; nothing is written.

Output is deterministic (sorted keys, two-space indent, trailing newline) and
a fixed point: exporting the output gives the same bytes. check_api_reference.py
relies on that to catch an unfiltered or reformatted file (not a stale one).

Needs PyYAML for YAML input (already used by check_platform_docs.py).
"""

import argparse
import copy
import json
import re
import sys
from pathlib import Path

AUDIENCE = "public"

METHODS = ("get", "put", "post", "delete", "options", "head", "patch", "trace", "query")

# Private product repository (blowhorn-ai/blowhorn, not blowhorn-site), its
# issue references and the internal hostname. Every reader of a public page
# would get a 404 or learn something private.
DENY_PATTERNS = (
    r"blowhorn-ai/blowhorn(?![\w-])",
    r"internal\.blowhorn\.ai",
    r"file://",
)

# Site naming (check_naming.py): never publish "Blowhorn Cloud" / "Layer5 Cloud".
SITE_CLOUD_RE = re.compile(r"\b(?:Layer\s?5|Blowhorn)\s+Cloud\b", re.I)


def _site_name_string(value: str) -> str:
    return SITE_CLOUD_RE.sub("Blowhorn", value)


def apply_site_naming(node):
    """Rewrite Cloud product names in every string for the public site."""
    if isinstance(node, dict):
        return {k: apply_site_naming(v) for k, v in node.items()}
    if isinstance(node, list):
        return [apply_site_naming(v) for v in node]
    if isinstance(node, str):
        return _site_name_string(node)
    return node


KEEP_EXTENSIONS = ("x-order", "x-displayName")

SCHEMA_SCALARS = (
    "type", "format", "title", "description", "enum", "const", "default",
    "example", "examples", "nullable", "readOnly", "writeOnly", "deprecated",
    "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf",
    "minLength", "maxLength", "pattern", "minItems", "maxItems", "uniqueItems",
    "minProperties", "maxProperties", "required", "contentMediaType",
    "contentEncoding", "x-order",
)
SCHEMA_ONE = ("items", "not", "contains", "propertyNames", "if", "then", "else",
              "additionalProperties", "unevaluatedItems", "unevaluatedProperties")
SCHEMA_LIST = ("allOf", "anyOf", "oneOf", "prefixItems")
SCHEMA_MAP = ("properties", "patternProperties")

SCHEMA_REF_RE = re.compile(r"^#/components/schemas/([^/]+)$")
COMPONENT_REF_RE = re.compile(r"^#/components/(parameters|requestBodies|responses|examples)/([^/]+)$")


class ExportError(Exception):
    """The document cannot be exported safely."""


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def _strict_loader():
    """A PyYAML loader with the YAML 1.2 core behaviour OpenAPI authors expect:
    only true/false are booleans (not yes/no/on/off), no implicit timestamps,
    and a duplicate mapping key is an error rather than a silent overwrite."""
    import yaml

    class Loader(yaml.SafeLoader):
        pass

    Loader.yaml_implicit_resolvers = {
        key: [(tag, regexp) for tag, regexp in resolvers
              if tag not in ("tag:yaml.org,2002:timestamp",)]
        for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
    }
    bool_re = re.compile(r"^(?:true|True|TRUE|false|False|FALSE)$")
    for key, resolvers in list(Loader.yaml_implicit_resolvers.items()):
        Loader.yaml_implicit_resolvers[key] = [
            (tag, bool_re if tag == "tag:yaml.org,2002:bool" else regexp)
            for tag, regexp in resolvers]

    def construct_mapping(loader, node, deep=False):
        seen = set()
        for key_node, _ in node.value:
            key = loader.construct_object(key_node, deep=True)
            if key in seen:
                raise ExportError(f"duplicate mapping key {key!r} "
                                  f"(line {key_node.start_mark.line + 1})")
            seen.add(key)
        return yaml.SafeLoader.construct_mapping(loader, node, deep)

    Loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)
    return Loader


def load_document(path):
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ExportError(f"cannot read {path}: {exc}") from exc
    try:
        if path.suffix.lower() == ".json":
            return json.loads(text)
        if path.suffix.lower() in (".yaml", ".yml"):
            import yaml
            return yaml.load(text, Loader=_strict_loader())
    except ExportError:
        raise
    except Exception as exc:  # parser errors differ by format
        raise ExportError(f"cannot parse {path}: {exc}") from exc
    raise ExportError(f"{path}: expected a .yaml, .yml or .json file")


# ---------------------------------------------------------------------------
# Audience
# ---------------------------------------------------------------------------

def is_public(node):
    """True only when node['x-internal'] is "public" or a list containing the
    string "public". Everything else, including an absent key, is False."""
    if not isinstance(node, dict) or "x-internal" not in node:
        return False
    value = node["x-internal"]
    if isinstance(value, str):
        return value == AUDIENCE
    if isinstance(value, list):
        return AUDIENCE in [v for v in value if isinstance(v, str)]
    return False


# ---------------------------------------------------------------------------
# Reference resolution and rebuilding
# ---------------------------------------------------------------------------

class Exporter:
    def __init__(self, doc):
        self.doc = doc
        self.components = doc.get("components") or {}
        if not isinstance(self.components, dict):
            raise ExportError("components must be an object")
        self.schema_refs = set()      # schema names reachable from exported operations
        self.security_names = set()   # securitySchemes named by exported operations

    # -- refs -------------------------------------------------------------

    def _component(self, ref, where):
        match = COMPONENT_REF_RE.match(ref)
        if not match:
            raise ExportError(f"{where}: unsupported $ref {ref!r} "
                              "(only local #/components/... references are exported)")
        kind, name = match.groups()
        found = (self.components.get(kind) or {}).get(name)
        if not isinstance(found, dict):
            raise ExportError(f"{where}: $ref {ref!r} does not resolve")
        return found

    def deref(self, node, where, seen=()):
        """Follow $ref chains to a non-schema component and merge the
        referencing object's own summary/description over it."""
        if not isinstance(node, dict) or "$ref" not in node:
            return node
        ref = node["$ref"]
        if ref in seen:
            raise ExportError(f"{where}: $ref cycle through {ref!r}")
        target = self.deref(self._component(ref, where), where, seen + (ref,))
        merged = dict(target)
        for key in ("summary", "description"):
            if key in node:
                merged[key] = node[key]
        return merged

    # -- schemas ----------------------------------------------------------

    def schema(self, node, where):
        if node is True or node is False:
            return node
        if not isinstance(node, dict):
            raise ExportError(f"{where}: a schema must be an object")
        if "$ref" in node:
            match = SCHEMA_REF_RE.match(str(node["$ref"]))
            if not match:
                raise ExportError(f"{where}: unsupported $ref {node['$ref']!r} "
                                  "(only #/components/schemas/<name> is exported)")
            self.schema_refs.add(match.group(1))
            out = {"$ref": node["$ref"]}
            if isinstance(node.get("description"), str):
                out["description"] = node["description"]
            return out
        out = {key: copy.deepcopy(node[key]) for key in SCHEMA_SCALARS if key in node}
        for key in SCHEMA_ONE:
            if key in node:
                out[key] = self.schema(node[key], f"{where}.{key}")
        for key in SCHEMA_LIST:
            if key in node:
                if not isinstance(node[key], list):
                    raise ExportError(f"{where}.{key}: expected a list")
                out[key] = [self.schema(item, f"{where}.{key}[{i}]")
                            for i, item in enumerate(node[key])]
        for key in SCHEMA_MAP:
            if key in node:
                if not isinstance(node[key], dict):
                    raise ExportError(f"{where}.{key}: expected an object")
                out[key] = {name: self.schema(sub, f"{where}.{key}.{name}")
                            for name, sub in node[key].items()}
        discriminator = node.get("discriminator")
        if isinstance(discriminator, dict) and isinstance(discriminator.get("propertyName"), str):
            out["discriminator"] = {"propertyName": discriminator["propertyName"]}
        return out

    # -- operation parts --------------------------------------------------

    def example(self, node, where):
        node = self.deref(node, where)
        if not isinstance(node, dict):
            return {"value": node}
        out = {key: node[key] for key in ("summary", "description", "value") if key in node}
        # externalValue is a URL to somewhere else: dropped.
        return out if "value" in out else None

    def media(self, node, where):
        if not isinstance(node, dict):
            raise ExportError(f"{where}: media type must be an object")
        out = {}
        if "schema" in node:
            out["schema"] = self.schema(node["schema"], f"{where}.schema")
        if "example" in node:
            out["example"] = copy.deepcopy(node["example"])
        examples = self.examples(node.get("examples"), where)
        if examples:
            out["examples"] = examples
        return out

    def examples(self, node, where):
        if not isinstance(node, dict):
            return {}
        found = {name: self.example(item, f"{where}.examples.{name}")
                 for name, item in node.items()}
        return {name: item for name, item in found.items() if item is not None}

    def content(self, node, where):
        if not isinstance(node, dict):
            raise ExportError(f"{where}: content must be an object")
        return {ctype: self.media(media, f"{where}.{ctype}") for ctype, media in node.items()}

    def parameter(self, node, where):
        node = self.deref(node, where)
        if not isinstance(node, dict) or "name" not in node or "in" not in node:
            raise ExportError(f"{where}: a parameter needs name and in")
        out = {key: node[key] for key in ("name", "in", "description", "required",
                                          "deprecated", "style", "explode",
                                          "allowEmptyValue", "example") if key in node}
        if "schema" in node:
            out["schema"] = self.schema(node["schema"], f"{where}.schema")
        if "content" in node:
            out["content"] = self.content(node["content"], f"{where}.content")
        examples = self.examples(node.get("examples"), where)
        if examples:
            out["examples"] = examples
        return out

    def request_body(self, node, where):
        node = self.deref(node, where)
        if not isinstance(node, dict):
            raise ExportError(f"{where}: requestBody must be an object")
        out = {key: node[key] for key in ("description", "required") if key in node}
        out["content"] = self.content(node.get("content") or {}, f"{where}.content")
        return out

    def response(self, node, where):
        node = self.deref(node, where)
        if not isinstance(node, dict):
            raise ExportError(f"{where}: a response must be an object")
        out = {"description": node.get("description", "")}
        if "content" in node:
            out["content"] = self.content(node["content"], f"{where}.content")
        return out

    def security(self, requirement, where):
        if not isinstance(requirement, list):
            raise ExportError(f"{where}: security must be a list")
        out = []
        for i, alternative in enumerate(requirement):
            if not isinstance(alternative, dict):
                raise ExportError(f"{where}[{i}]: a security requirement must be an object")
            for name, scopes in alternative.items():
                if not isinstance(scopes, list):
                    raise ExportError(f"{where}[{i}].{name}: scopes must be a list")
                self.security_names.add(name)
            out.append({name: list(scopes) for name, scopes in alternative.items()})
        return out

    def parameters(self, path_level, op_level, where):
        """Path-level parameters first; an operation parameter with the same
        name and location replaces it."""
        merged = {}
        order = []
        for source, items in (("path", path_level or []), ("operation", op_level or [])):
            if not isinstance(items, list):
                raise ExportError(f"{where}: parameters must be a list")
            for i, item in enumerate(items):
                param = self.parameter(item, f"{where}.parameters[{source}:{i}]")
                key = (param["in"], param["name"])
                if key not in merged:
                    order.append(key)
                merged[key] = param
        return [merged[key] for key in order]

    def operation(self, op, path_item, global_security, where):
        out = {key: op[key] for key in ("summary", "description", "operationId", "deprecated")
               if key in op}
        out["x-internal"] = [AUDIENCE]
        if isinstance(op.get("tags"), list):
            out["tags"] = [t for t in op["tags"] if isinstance(t, str)]
        params = self.parameters(path_item.get("parameters"), op.get("parameters"), where)
        if params:
            out["parameters"] = params
        if "requestBody" in op:
            out["requestBody"] = self.request_body(op["requestBody"], f"{where}.requestBody")
        responses = op.get("responses")
        if not isinstance(responses, dict) or not responses:
            raise ExportError(f"{where}: an exported operation needs responses")
        out["responses"] = {str(code): self.response(resp, f"{where}.responses.{code}")
                            for code, resp in responses.items()}
        requirement = op["security"] if "security" in op else global_security
        if requirement is not None:
            out["security"] = self.security(requirement, f"{where}.security")
        return out


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

def export_public(doc):
    """Return (public_document, report). Raises ExportError."""
    if not isinstance(doc, dict):
        raise ExportError("the document must be an object")
    version = doc.get("openapi")
    if not isinstance(version, str) or not version.startswith("3."):
        raise ExportError(f"expected an OpenAPI 3.x document, got openapi: {version!r}")
    paths = doc.get("paths")
    if not isinstance(paths, dict):
        raise ExportError("the document has no paths object")

    ex = Exporter(doc)
    global_security = doc.get("security") if isinstance(doc.get("security"), list) else None

    out_paths = {}
    total = kept = 0
    seen_ids = {}
    for path in sorted(paths):
        item = paths[path]
        if not isinstance(item, dict):
            raise ExportError(f"paths.{path}: a path item must be an object")
        if "$ref" in item:
            raise ExportError(f"paths.{path}: a path item $ref is not supported")
        path_ok = ("x-internal" not in item) or is_public(item)
        out_item = {}
        for method in METHODS:
            op = item.get(method)
            if op is None:
                continue
            total += 1
            if not isinstance(op, dict):
                raise ExportError(f"paths.{path}.{method}: an operation must be an object")
            if not (path_ok and is_public(op)):
                continue
            kept += 1
            out_item[method] = ex.operation(op, item, global_security, f"paths.{path}.{method}")
            op_id = out_item[method].get("operationId")
            if op_id:
                if op_id in seen_ids:
                    raise ExportError(f"operationId {op_id!r} is used by both "
                                      f"{seen_ids[op_id]} and {method.upper()} {path}")
                seen_ids[op_id] = f"{method.upper()} {path}"
        if out_item:
            out_paths[path] = out_item

    # Reachable schemas, transitively.
    schemas_in = ex.components.get("schemas") or {}
    out_schemas = {}
    pending = sorted(ex.schema_refs)
    while pending:
        name = pending.pop()
        if name in out_schemas:
            continue
        if name not in schemas_in:
            raise ExportError(f"$ref #/components/schemas/{name} does not resolve")
        before = set(ex.schema_refs)
        out_schemas[name] = ex.schema(schemas_in[name], f"components.schemas.{name}")
        pending.extend(sorted(ex.schema_refs - before))

    out_schemes = {}
    schemes_in = ex.components.get("securitySchemes") or {}
    for name in sorted(ex.security_names):
        scheme = schemes_in.get(name)
        if not isinstance(scheme, dict):
            raise ExportError(f"security scheme {name!r} is used but not defined")
        # OAuth flow and OpenID URLs are dropped on purpose.
        out_schemes[name] = {key: scheme[key] for key in
                             ("type", "scheme", "bearerFormat", "name", "in", "description")
                             if key in scheme}

    used_tags = {t for item in out_paths.values() for op in item.values()
                 for t in op.get("tags", [])}
    out_tags = []
    for tag in doc.get("tags") or []:
        if isinstance(tag, dict) and tag.get("name") in used_tags:
            out_tags.append({key: tag[key] for key in ("name", "description", "x-displayName")
                             if key in tag})
    known = {t["name"] for t in out_tags}
    for name in sorted(used_tags - known):
        out_tags.append({"name": name})

    out_groups = []
    for group in doc.get("x-tagGroups") or []:
        if isinstance(group, dict) and isinstance(group.get("tags"), list):
            tags = [t for t in group["tags"] if t in used_tags]
            if tags:
                out_groups.append({"name": group.get("name", ""), "tags": tags})

    info = doc.get("info") if isinstance(doc.get("info"), dict) else {}
    out = {
        "openapi": version,
        "info": {key: info[key] for key in ("title", "version", "summary", "description")
                 if key in info},
        "paths": out_paths,
    }
    if out_tags:
        out["tags"] = out_tags
    if out_groups:
        out["x-tagGroups"] = out_groups
    components = {}
    if out_schemas:
        components["schemas"] = out_schemas
    if out_schemes:
        components["securitySchemes"] = out_schemes
    if components:
        out["components"] = components

    leaks = find_leaks(out)
    if leaks:
        shown = "\n".join(f"  {where}: matches {pattern!r}" for where, pattern in leaks[:20])
        more = f"\n  ... and {len(leaks) - 20} more" if len(leaks) > 20 else ""
        raise ExportError("the public output mentions something private "
                          f"({len(leaks)} place(s)); fix the source or the operation's "
                          f"x-internal:\n{shown}{more}")

    report = {"operations": total, "exported": kept, "excluded": total - kept,
              "tags": len(out_tags), "schemas": len(out_schemas)}
    return apply_site_naming(out), report


def find_leaks(node, where="$"):
    """(json path, pattern) for every string, key included, that matches a
    deny pattern."""
    patterns = [re.compile(p, re.IGNORECASE) for p in DENY_PATTERNS]
    found = []

    def visit(value, path):
        if isinstance(value, str):
            for pattern in patterns:
                if pattern.search(value):
                    found.append((path, pattern.pattern))
        elif isinstance(value, dict):
            for key, sub in value.items():
                visit(str(key), f"{path}.<key {key}>")
                visit(sub, f"{path}.{key}")
        elif isinstance(value, list):
            for i, sub in enumerate(value):
                visit(sub, f"{path}[{i}]")

    visit(node, where)
    return found


def render(document):
    return json.dumps(document, sort_keys=True, indent=2, ensure_ascii=False,
                      allow_nan=False) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args(argv)
    try:
        public, report = export_public(load_document(args.input))
        text = render(public)
    except ExportError as exc:
        print(f"openapi-export: {exc}", file=sys.stderr)
        return 1
    except (TypeError, ValueError) as exc:
        print(f"openapi-export: cannot serialise the result: {exc}", file=sys.stderr)
        return 1
    out = Path(args.output)
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    except OSError as exc:
        print(f"openapi-export: cannot write {out}: {exc}", file=sys.stderr)
        return 1
    print(f"openapi-export: exported {report['exported']} of {report['operations']} "
          f"operation(s), {report['tags']} tag(s), {report['schemas']} schema(s) -> {out}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
