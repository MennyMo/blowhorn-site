# Hero activity feed

The home hero shows a small activity card: one recent line, who it was for, and Previous / Next. It asks the Blowhorn account service for the public event feed and shows what comes back while it is fresh. When the feed is empty, the request fails or the payload is invalid, it rotates a bundled example collection instead, labelled "Examples". The hero is never blank, and the first bundled example is in the HTML so the card reads with no JavaScript.

Public copy on the card says the fallback lines are examples. It does not name a cloud service, a price, or a browser.

## The contract

The feed is `GET <cloud_url>/api/events/feed` on the account service (`params.cloud_url` in `hugo.toml`, `https://cloud.blowhorn.ai`). No auth. The response shape is `EventFeedPage` and its items are `EventFeedItem`, both defined in meshery/schemas v1.3.116 (`schemas/constructs/v1beta3/event/api.yml`). That repository is the source of truth; nothing here redefines the contract.

| Piece | Value |
|---|---|
| Query | `page` (from 0), `pagesize` (default 20, max 50), optional `category`, `action`. The card asks for `page=0&pagesize=20&category=schedule&action=completed`. |
| Envelope | `{ page, pageSize, totalCount, data: EventFeedItem[] }`, newest first. |
| Required item fields | `id`, `userId` (UUIDs), `category`, `action`, `createdAt`, `visibility` (`public`), `platform` (one of the seven supported ids), `role` (3 to 40 characters), `line` (10 to 120). |
| Optional item fields | `networks`, `displayName`, `avatarUrl`, `organizationName`, `publicProfileUrl` (https), present only for a public profile. |
| Caching | `Cache-Control: public, max-age=N`, N at most 30. Over the limit the service answers 429 with `Retry-After`. |
| Empty feed | `{ "page": 0, "pageSize": 20, "totalCount": 0, "data": [] }`. This is valid and is what the card sees until public events exist. |

`/api/public/activity-feed` is not the public feed (it answers 401); do not use it.

## What is wired

| Piece | Role |
|---|---|
| `schemas/event_feed_page.schema.json` | JSON Schema projection of `EventFeedPage` and `EventFeedItem` from meshery/schemas v1.3.116. Re-project it when the pinned version changes. |
| `schemas/activity_feed.examples.schema.json` | Local schema for the bundled file only: `{ example: true, data }`, each item a `$ref` to `EventFeedItem`. |
| `data/activity_feed.examples.json` | The collection baked into the home page. The envelope's `example: true` marks every item an example. |
| `layouts/_partials/activity-feed.html` | Static card (first example, Examples label), the `data-feed-url` attribute built from `params.cloud_url`, and a `script type="application/json"` block holding the examples. Loads the script fingerprinted and deferred, only where the card is rendered. |
| `layouts/_partials/home/signal.html`, `home/reveille.html` | Where the card sits in the hero. |
| `assets/js/activity-feed.js` | Validation (a JS mirror of `EventFeedItem`, run on every live payload), the transport, rotation and `createFeedSource`. |
| `assets/css/site.css` | Card layout, under "Hero activity card". Glass variant, tokens only. |

Live payloads are checked by the JS validator, since the browser carries no JSON Schema engine; `make test-activity-feed` pins it to the contract (including the empty page). `make check-schemas` validates the bundled file against the local schema and the projected `EventFeedItem`.

## Example collection

75 items, all `category: schedule`, `action: completed`. Each line is one supported action on a platform that `data/integrations.json` marks supported and that `data/platforms/<id>.yaml` lists for that action. Ids and user ids are fixed UUIDs (v5) so the file satisfies the `uuid` format.

Actions used: post, comment, reply, amplify, react, follow, unfollow, accept, withdraw, find. Analytics is left out: this card shows no performance stats, counts, or outcomes.

Roles are generic personas. There is no display name, avatar, or profile URL. `createdAt` is a fixed date in October 2026. The card does not turn those into "just now" or "2 min ago". Example rows show the label "Example activity".

The static HTML shows the first item and a visible Examples badge: "Illustrative examples, not real customer activity." With script off, that first item stays. Previous and Next keep their space and stay hidden until the script is running, so the card does not jump.

## Runtime behaviour

`boot` reads the JSON block and the card's `data-feed-url`, and calls `createFeedSource({ transport, fallback })`. The transport is `fetch` with `credentials: "omit"` and no referrer, accepted only for an https URL. No URL (for example a build with no `cloud_url`) means a null transport: the bundled examples, with no request and no timer. No feed URL lives in the script.

Rotation is 7 seconds, a short opacity crossfade. It pauses while the pointer is over the card or focus is inside it, and while `document.hidden` is true. `prefers-reduced-motion: reduce` skips the timer and the fade; Previous and Next still move one row. The rotating line is not an `aria-live` region. The card's accessible name is the static "Recent activity" label. `destroy` clears every timer and removes the listeners.

A page is accepted only if it is an `EventFeedPage`: `page`, `pageSize` (1 to 50) and `totalCount` are integers in range, `data` is an array of at most 50 items, and there are no other top-level fields. Items are checked field by field: known fields only, UUIDs, the platform list, length limits, a valid `createdAt`, `https` URLs, no `javascript:` or `data:` URLs. Text is written with `textContent`. A live item's profile link uses `rel="noopener noreferrer nofollow"` and `target="_blank"`. Example rows do not render it. Avatar URLs are not requested. Invalid items are dropped.

The fallback to the bundled examples, with the Examples label, covers: an empty `data` array, a body that is not JSON or not an `EventFeedPage`, no valid items, a timeout (8 seconds), a thrown network error (including a blocked cross-origin request), any non-success status, and a response with no `max-age`. HTTP 429 also sets a wait from `Retry-After` (delta-seconds or an HTTP date) before the transport is called again; a missing or unreadable value waits 60 seconds.

Live items are held only for the response `max-age`, capped at 30 seconds. When it ends, the card asks once more. If that refresh fails, the live rows are dropped and the bundled examples take their place, labelled. Expired live rows are never the offline fallback. Nothing in this script writes `localStorage`, `sessionStorage`, `IndexedDB`, or a service-worker cache.

## Disclosure

The card's request goes to `cloud.blowhorn.ai`, Blowhorn's own account service, from the reader's browser. The privacy page lists it with the other requests the site makes. Change the privacy page first if the request changes.

## Open items outside this repository

- CORS. As of 2026-11-09 the feed answers `Vary: Origin` but sends no `Access-Control-Allow-Origin` for `https://blowhorn.ai`, so a browser blocks the response and the card shows the examples. The account service needs to allow `https://blowhorn.ai` (and `https://www.blowhorn.ai`) on `GET /api/events/feed`. Until then the live path cannot be seen in a browser.
- Seed events. Cloud reported about 100 seed events from 25 fake accounts. EventFeedItem has no seed or example marker, so a seed event in the live feed would render as real activity. Cloud must keep seed events out of the public feed, or add a marker to the schema.
