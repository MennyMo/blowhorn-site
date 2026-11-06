# Public API reference (/docs/reference/api/)

**Status: enabled.** Public operations from `schemas/dist/openapi.yaml` are exported to `api/openapi.public.json` and rendered at `/docs/reference/api/`. Re-export after schema changes with `make api-reference-export API_SPEC_SRC=...`. Automated fetch from the private product repo is still a follow-up.

Blowhorn ships a CLI and an MCP server today. It does **not** run an HTTP REST listener. The reference documents the operation contracts (request fields, response shape) and says so on the page: the viewer always renders a "Not an HTTP API" notice, never shows a server URL or a "try it" control, and `make check-api-reference` fails a page that loses the notice.

## How it fits together

```
product schema (private)  --local file-->  openapi_export.py  -->  api/openapi.public.json  -->  layout rest-apis  -->  /docs/reference/api/
```

| Piece | Where | Job |
|---|---|---|
| Exporter | `.github/scripts/openapi_export.py` (`make api-reference-export API_SPEC_SRC=...`) | Reads a **local** OpenAPI 3.x file (YAML or JSON), keeps only operations whose `x-internal` lists `public`, rebuilds each object from an allow-list, writes deterministic JSON. Fails closed (below). |
| Site param | `[params.apiReference] spec` in `hugo.toml` | Project-relative path of that JSON. Empty means off. `HUGO_PARAMS_APIREFERENCE_SPEC` overrides it for one build, and `check-api-reference` honours the override too. |
| Layout and partials | `layouts/docs/rest-apis.html`, `layouts/_partials/rest-apis/` | Adapted from layer5io/docs (see `THIRD-PARTY-NOTICES.md`). One native `<details>` per operation, grouped by tag. |
| Script and stylesheet | `assets/js/api-reference.js`, `assets/css/api-reference.css` | Filter, expand all, open the operation a `#fragment` names. Brand tokens only. Both load only on this layout. |
| Build check | `make check-api-reference` (part of `site-check`) | Once the param is set: the page holds exactly the spec's operations, keeps the notice, names nothing private. A no-op while the param is empty. |
| Tests | `test_openapi_export.py`, `test_check_api_reference.py`, `test_api_reference_viewer.py` (`make test-scripts`) | Use `tests/openapi/fixtures/synthetic.openapi.yaml`, which says on every line that it is not the Blowhorn API. |

### What the exporter does and refuses

- **Audience.** An operation is exported only when `x-internal` is `"public"` or a list containing `"public"`. `cloud` alone, a missing key, `Public`, `true` and every other shape are excluded. A path item with `x-internal` must list `public` too.
- **Allow-lists.** `servers`, `externalDocs`, `webhooks`, `callbacks`, `links`, OAuth and OpenID URLs, contact and licence blocks, response headers and every `x-` extension except `x-order`, `x-displayName`, `x-tagGroups` and the normalised `x-internal` are dropped. Unknown schema keywords are dropped too.
- **Refs.** Path-level parameters, `$ref` parameters, request bodies, responses and examples are inlined; the effective security requirement is written into each operation. Only `components.schemas` and `components.securitySchemes` survive, and only what the exported operations reach. Any `$ref` that is not a local `#/components/...` pointer is an error.
- **Private mentions.** The result must not match `blowhorn-ai/blowhorn` (the private product repository; `blowhorn-site` is fine), `internal.blowhorn.ai` or `file://` (a fixed list, `DENY_PATTERNS` in the exporter; `check_api_reference.py` enforces the same list on the built page). A match is an error naming the JSON path, and nothing is written.
- **Descriptions are plain text.** The viewer shows every `description` as paragraphs of escaped text, not Markdown (`layouts/_partials/rest-apis/prose.html`). The site renders goldmark with raw HTML on, so Markdown would let a spec inject markup, and escaping before Markdown double-escapes code spans. Markdown syntax therefore appears as written; `<id>` in a description shows as `<id>`.
- **YAML 1.2 behaviour.** `on`, `off`, `yes`, `no` stay strings, dates stay strings, duplicate keys are an error.
- The output is a fixed point: exporting it again changes nothing.

The viewer filters on `public` again and never reads servers or external docs, so a raw spec dropped in by mistake still cannot publish a non-public operation. `check-api-reference` also fails a file that is not already in the exporter's canonical form.

## Enabling it (once the product schema is available)

1. Get a local copy of the product's `schemas/dist/openapi.yaml`. Fetching it from the private repository (a read-only token such as the `DMG_SOURCE_TOKEN` that `sync-docs.yml` uses, then a make target and a workflow step, as for `docs-sync`) is **not wired yet**.
2. `make api-reference-export API_SPEC_SRC=path/to/openapi.yaml` writes `api/openapi.public.json`. If it fails on a private mention, fix the source description or the operation's `x-internal`; do not edit the output.
3. Set `spec = "api/openapi.public.json"` under `[params.apiReference]` in `hugo.toml`.
4. Add the page below as `content/en/docs/reference/api/_index.md`. It must be an `_index.md`: `sync-docs.py` removes any other Markdown page under `content/en/docs/` that the product does not have, and keeps a site-only `_index.md`.
5. Run `make check`, then the screenshot checklist in [deploy.md](deploy.md) (390, 820 and 1440 px, light and dark, no horizontal scroll from 320 px).
6. Review the points under "Decide before publishing", then land it.

### The page (draft, not published)

```markdown
---
title: "API reference"
description: "The operations Blowhorn defines, with their request fields and responses."
layout: rest-apis
---

Blowhorn is used through its [command-line interface](/docs/reference/cli/) and its [MCP server](/docs/reference/mcp-server/). These are the operations behind them, listed with the fields each one takes and returns.
```

The viewer adds the "Not an HTTP API" notice, the operation count and the resource list under that paragraph. Keep the paragraph to the facts the schema supports; do not describe a base URL, a port or an HTTP client.

## Decide before publishing

- **Authorization lines.** The viewer prints each operation's `security` ("Bearer token", "No authentication"). For CLI operations that may be meaningless or misleading; if so, drop `auth-summary.html` from `viewer.html` rather than explain it.
- **The `x-internal` audit.** About 117 operations are reported. Someone who owns the schema should confirm each `public` mark is deliberate, since opt-in is the only gate.
- **Operation paths.** They are rendered as `POST /cli/...` identifiers. Confirm that is clear next to the notice, or relabel them.
- **Names.** The site says Blowhorn only. A schema mentioning Layer5 Cloud or Blowhorn Cloud is caught by `check-naming`; fix it in the schema.

## Verifying a change to the viewer

Rendering is verified by hand, not in CI (a faithful render needs the whole site):

1. `python3 .github/scripts/openapi_export.py tests/openapi/fixtures/synthetic.openapi.yaml /tmp/synthetic.public.json` and copy the result inside the project (the param is project-relative), for example `tests/openapi/fixtures/synthetic.public.json`.
2. Add a **temporary** `content/en/docs/reference/zz-fixture-test/_index.md` with `layout: rest-apis` and a title that says it is synthetic.
3. `HUGO_PARAMS_APIREFERENCE_SPEC=tests/openapi/fixtures/synthetic.public.json node_modules/.bin/hugo --cleanDestinationDir --destination /tmp/api-out`, then html-validate and the screenshot checklist against `/tmp/api-out`.
4. Delete the temporary page and the generated JSON. Never commit them, and never publish synthetic data.

`hugo server` does not watch the spec file (it is read with `os.ReadFile`); restart it after re-exporting.
