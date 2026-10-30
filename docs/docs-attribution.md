# Docs attribution events

The MCP connection guides send three Google Analytics 4 events so an install can be traced back to the guide, the client section and the campaign that led to it. They ride on the GA4 tag the site already loads after consent (`layouts/_partials/analytics.html`): no Google Tag Manager container, no new host, no new cookie.

## Where it runs

- Pages: events run on every path prefix in `pages` in `data/docs_events.json` (today the connect guide, the MCP server and Python client references, the first MCP connection tutorial, the MCP and safety explanation, and `/ai/mcp/`). A prefix for a page that does not exist yet simply matches nothing. Every other page with analytics runs the same script for the first-touch capture only (below): it stores attribution after consent and sends nothing.
- Builds: production only, the same gate as analytics (`analytics-enabled.html`). `layouts/_partials/docs-attribution.html` emits the config as `<script type="application/json" id="docs-events">` (the whole config on every page) plus `assets/js/docs-attribution.js`, from `layouts/baseof.html` and `layouts/_partials/docs-scripts.html`.
- Consent: nothing is sent, stored or listened for until localStorage `blowhorn-consent` is `granted`. If the reader accepts on the page, `assets/js/consent.js` dispatches `blowhorn:consent` and the capture and events start from that moment; nothing is queued before it. Withdrawing consent removes the stored attribution.

No markup goes into content. The script finds code cards (`figure.term`, copy button `.term-copy`) and links with delegated listeners, and reads the client from the nearest enclosing h2 or h3 whose id is in `clients`. Without one it uses the page's `mcp_client` front matter (a client heading id from `clients`), then `default_client` (`general`). A heading renamed in the product repository's docs changes its id: add the new id to `clients`.

## Events

Every event also carries the attribution parameters below.

| Event | Parameters | When |
|---|---|---|
| `docs_guide_view` | `page_path`, `guide` (page slug), `client` (from the URL hash when it names a client heading) | once per page load, after consent |
| `docs_snippet_copy` | `page_path`, `client`, `snippet_kind` (`json`, `toml`, `yaml`, `shell`, `text`, `other`, from the card's `data-lang`), `snippet_title` (the card's label) | a code card's copy button is pressed |
| `docs_outbound_click` | `page_path`, `client`, `link_kind` (`npm`, `registry`, `download`), `link_url` (scheme, host and path only) | a click or middle-click on a link matching an `outbound` rule |

Attribution, captured once per browser session into sessionStorage `blowhorn-docs-attribution` (only after consent) from the first page with analytics, tracked or not; the first touch wins: `first_source`, `first_medium`, `first_campaign`, `first_content`, `first_term` (that page's `utm_*`), `first_referrer_host` (the referrer's host only, `(none)` for this site or no referrer), `landing_page` (that page's path, no query string) and `landing_guide` (the first tracked guide seen in the session). A missing value is `(none)`. A reader who consents on a later page is captured from that page: nothing is kept before consent.

Never sent: query strings, fragments, full referrer URLs, copied text, or anything a reader types. Values are cut to GA4's 100 characters.

## Changing it

- Config: `data/docs_events.json`, validated by `schemas/docs_events.schema.json`. Payload shapes: `schemas/defs/docs-event.schema.json`. `make check-schemas` validates the config.
- Tests: `.github/scripts/test_docs_attribution.py` (run by `make test-scripts`) drives the script through `docs_attribution_harness.js`, checks the consent gate, the sitewide first-touch capture, clearing on withdrawal (`consent.js`), client lookup, link kinds and stripping, and validates every payload with ajv.
- Reports: register the parameters as GA4 custom dimensions (event scope) to see them in reports. A Google Tag Manager container would be another tracking tag, which the site's rules forbid without a privacy page update first.
