# Blowhorn signup worker

The API behind the coming-soon waitlist forms and the newsletter signup:
`POST /api/waitlist`, `POST /api/subscribe`, `GET /api/unsubscribe` (confirmation page), `POST /api/unsubscribe`.
No confirmation step: a signup is live as soon as it is stored. Every
ship email and newsletter email carries an unsubscribe link built from
the row token.

## Hosting

- Worker: `blowhorn-signups`, served at `https://api.blowhorn.ai`
  (custom domain). A `blowhorn.ai/api/*` route was dropped: the apex is
  DNS-only, so such a route can never serve traffic, and creating it
  failed the deploy (the Cloudflare API refused the routes update).
  If the apex is ever proxied, the route can be re-added then.
- Store: Cloudflare D1 database `blowhorn-signups`, bound as
  `SIGNUPS_DB`. The same database is bound to the internal worker,
  which serves the Access-gated admin page and CSV export at
  `https://internal.blowhorn.ai/internal/signups/`.
- CORS: only `https://blowhorn.ai` may call the API from a browser.

## Deploy

`.github/workflows/signup-worker.yml` deploys on pushes to master
that touch `signup-worker/`, and on manual dispatch. It runs the
node tests, then `.github/scripts/resolve-d1.sh` (creates the D1
database if it is missing and writes its id into `wrangler.json`),
applies `migrations/`, and deploys with wrangler. The
`database_id` committed here is a placeholder on purpose: never
deploy this worker by hand without running `resolve-d1.sh` first,
or wrangler will fail on the placeholder.

## Tests

`node --test signup-worker/worker.test.mjs` (also run by the
deploy workflow). The tests inject an in-memory fake for the six
db methods, so no D1 instance is needed.
