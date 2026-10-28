# Project agent memory

This file is the project's committed home for project-intrinsic agent knowledge: build, test, release, architecture, and sharp-edge notes that should travel with the code.

- Add durable project-specific notes here as they are discovered through real work.

## Building the site locally

blowhorn.ai is Hugo with Docsy as a Hugo module, built like layer5io/docs. Run
`make setup` once (npm install) for the pinned toolchain (the dependency check
also accepts system `hugo` and `postcss`), then `make site`
(live reload, http://localhost:1313) or `make site-build` (writes `public/`).
`make check` is exactly what CI runs. Go must be on PATH: Hugo fetches Docsy through it.

The marketing and legal pages do not use Docsy's templates: they render through
`layouts/home.html`, `layouts/trust-center.html` (the Trust Center hub at `/legal/`),
`layouts/legal.html` (each policy at `/legal/<name>/`), `layouts/brand.html` (the Brand page at `/brand/`) and `layouts/404.html` inside
`layouts/baseof.html`, with the header, footer and icon sprite in `layouts/_partials/`.

Themes are schema-driven (`data/themes.json`, `schemas/themes.schema.json`). A
theme is tokens, CSS and layout partials over the same data and content.
Reveille copy is approved; do not add a per-theme content file (`check_theme.py`
fails those except `content/en/home-reveille.md`). Site default is Reveille
(today's look: light, dark follows the OS). The public home page sets front
matter `theme: signal`. Docs, legal, pricing and download stay Reveille.
`?theme=` swaps the token layer only, not homepage layout. Homepage variants
live in `layouts/_partials/home/`. Platform counts and the platforms section
treatments come from `data/integrations.json` plus `data/platforms/*.yaml`;
the By role treatment and the "Who it's for" cards list every role in
`data/roles.json` by weight, and each role's `platforms` decides what it
highlights, so a new role appears on the home page without another edit.
The action vocabulary is `data/actions.json`; YAML rows use those ids.
Examples live in `data/action_examples.json` ([docs/action-examples.md](docs/action-examples.md)).
Platform docs pages render actions through `{{< supported-actions "id" >}}` (`layouts/_partials/supported-actions.html`); `make check-platform-docs` fails a missing page, a skipped table, or a hand-written action list.
The central action matrix (`/integrations/actions/`, `layouts/action-matrix.html`) and the docs all-actions table (`{{< all-actions >}}`, `layouts/_partials/action-table.html`) both render from `layouts/_partials/action-matrix.html`: rows are `data/actions.json` (grouped by its `groups`), columns are `data/integrations.json` platforms, page copy is `data/integrations.json` `matrix`. Status is shown by exception: no "Supported" label or check anywhere; a supported cell is a neutral dot, a coming-soon platform gets one clock on its logo. `make check-action-matrix` fails drift or a dead `#action-<id>` link.
The Signal hero demo is `data/hero_demo.json`.

Role pages (`/for/<slug>/`), use-case pages (`/use-cases/<slug>/`) and
solution pages (`/solutions/<slug>/`, one per category of tool replaced) are
schema-driven from `data/roles.json`, `data/use_cases.json` and
`data/solutions.json`. Shared `line`/`text`/`card` types live in
`schemas/defs/cast-page.schema.json` (`make check-schemas` loads it with ajv
`-r`). Kind labels live in `cast-kind.html`; lookups go through
`role-data.html` / `role-list.html`. Pages share
`layouts/_partials/cast-page.html` and the role-page CSS. A solution's
`compare` list renders the `/compare/` tiles (`versus-grid.html` `pages`)
instead of repeating their tables. `/solutions/` is the hub for all three
kinds (`solution-groups.html`, in the Solutions menu's order). Do not
duplicate those.

The `/compare/<slug>/` pages are edited here, in `content/en/compare/<slug>.md`
(JSON front matter). The product repository's `marketing/compare/data.py` is only
the seed they were first generated from; its generator is gone, so never
regenerate them. Claims on every page come from the product repository's
`marketing/brand/differentiators.md` in its wording rules.

## Rules the site holds

- **No third parties beyond the disclosed ones.** The privacy page discloses exactly three:
  Google Analytics 4 (`[services.googleAnalytics]` in `hugo.toml`;
  `layouts/_partials/analytics.html` loads gtag.js on every production page with
  analytics storage enabled and advertising storage denied), the download
  page's release lookup on api.github.com, and the footer newsletter form, which posts to
  Blowhorn's own signup service at `api.blowhorn.ai`, an allowed host in `FORM_ACTION_HOSTS`. Never add another analytics or tracking tag, a
  CDN script or stylesheet, or web fonts from elsewhere, and never copy layer5io/docs' head,
  navbar or footer (Docsy's head would add a second, consent-less gtag). A new outside host needs a privacy
  page update first. `.github/scripts/check-third-party.py` fails the build.
- **Brand tokens only.** Every colour, type style, radius and shadow in
  `assets/css/site.css` is a token from `static/assets/brand/tokens.json`. Light is the
  default; dark follows the OS with no JavaScript. Brand SVGs are used as files, never
  recoloured. Platform logos are the owners' own files in `static/assets/platforms/`, unmodified, on white
  tiles (sources in `static/assets/brand/LICENSES.md`).
- **The brand kit is built, not edited.** `static/brand/blowhorn-brand-kit.zip` and
  `data/brand_colors.json` come from the product repository's brand build
  (`scripts/brand/build-brand-kit.py`, output in `marketing/brand/kit/`); copy them over unchanged.
- **The product name is Blowhorn.** "Outbox" is the product's old internal name; never put
  it on a public page.
- **Browser wording depends on the page.** Marketing and value pages (home, `/for`, `/ai`,
  `/agents`, `/pricing`, `/major`, `/welcome`, `/integrations`, their data files, and compare
  pages' descriptions of Blowhorn) stay general: "your own browser", "browser profile", "browser
  extension", never Mac or Google Chrome; a requirement note links to System requirements.
  Download and install pages (`/download`, `/download/thanks`, `docs/reference/requirements`,
  `docs/how-to/set-up/`) state the exact requirement: "Requires macOS 13 or newer and Google
  Chrome 142 or newer" (142 is the engine's `MINIMUM_CHROME_MAJOR`), never "for now". Docs about
  using the app or CLI name Google Chrome and "Chrome profile", matching the app's labels ("Add to
  Chrome", "Show my Chrome profiles"). Competitor facts, Chrome Web Store, code, commands and URLs
  stay as they are. `check_naming.py` fails a "for now" requirement and "browser profile" or
  "browser extension" in the docs. Docs copy is synced from the product repository's `docs/`:
  change it there, then sync.
- **The product repository is private.** Never link its files, issues or pull requests
  from a page; every reader would get a 404.
- **Every Hugo run cleans its destination.** Each `hugo` invocation in `package.json`
  and the `Makefile` passes `--cleanDestinationDir`, builds and servers alike, so a
  stale file from an earlier build can never linger in `public/` or `public-internal/`
  and pass for current output. Hugo has no config-level default for this; the flag
  rides on the command line, so keep it on any new invocation.

## CI runs through make

Every CI step that runs repository logic is a Makefile target and the workflow calls it
(`site.yml`, and the `dmg-*` steps of `publish-dmg.yml` backed by `.github/scripts/publish-dmg/`).
When you add or change a CI step, put the logic behind a make target, call the target from
the workflow, and list it in the README's target table. `make ci` reproduces site.yml's check job.

## Keeping URLs and anchors alive

`/`, `/legal/`, `/legal/privacy/`, `/legal/terms/`, `/assets/brand/...` and the home
page's anchors (`#platforms`, `#how`, `#trust`, `#download`) are linked from outside this
repo, and the old `/privacy.html` and `/terms.html` must keep redirecting to their
`/legal/` pages. `.github/scripts/check-site-contract.py` lists every one and fails the
build when one disappears. When a page moves, add the dead path to the page's `aliases:`
front matter rather than leaving a 404 (GitHub Pages has no server redirects, so an alias
is a meta refresh with a canonical link) and list it in the script's `REDIRECTS`, and keep a renamed heading's old anchor with
`### New Wording {#old-anchor-slug}`. To prove nothing was lost, build master and your
branch to separate directories and diff the `id=` attributes across both trees.

Do not give a page in `content/en/` a `url:` ending in `.html`: `url` names one path for
every output format, so the page's Markdown output (`index.md` format) overwrites its HTML.
New pages go in a section (such as `content/en/legal/`), which gets pretty URLs; `uglyURLs`
in `hugo.toml` applies only to top-level pages, and the home page's public URL comes from
`layouts/_partials/canonical.html`.

The Trust Center's summaries (front matter of `content/en/legal/_index.md`) restate what
the policies and public docs already say. Never add a certification, sub-processor,
retention period, encryption detail or compliance claim that a policy does not make.

## Verifying a change

Check the built HTML in `public/`, not the source. Goldmark's typographer is off so quotes
stay straight; HTML is not minified so html-validate can check what ships. For a visual
change, follow the screenshot checklist in `docs/deploy.md` (390, 820 and 1440 px, light
and dark, no horizontal scroll from 320 px).

## Worktrees and landing a change

- **Work in a treehouse worktree, never in the main clone.** Other agent sessions and the
  no-mistakes pipeline share the main clone. Take a worktree with
  `treehouse get --lease -b <branch>` (it prints the path; `--base <branch>` starts it from
  another branch), work there, and release it with `treehouse return <path>` once the change
  has merged. `treehouse status` lists the pool. Never make one with `git worktree add` or a
  second clone.
- **Land every change through no-mistakes, at most three runs per pull request.** Commit in
  the worktree, then run `no-mistakes axi run --intent "<goal>"` (a clone without a
  `no-mistakes` remote needs `no-mistakes init` once). `no-mistakes axi status` shows the step
  and its findings, and `no-mistakes axi respond` answers a review gate. The pipeline reviews,
  tests, pushes and opens the pull request. After the third run, merge the pull request as it
  stands and open an issue for anything still flagged. A run that stopped on a usage limit
  counts; one cancelled before it did anything does not.

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.

## Design rules

Before any layout or copy change, follow [DESIGN.md](DESIGN.md) (whitespace tokens, concision rules and the PR checklist).
