# Platform pages

A platform product page (blowhorn-site#466) shows what you can start on one platform:
pick an activity type, see it illustrated, press Start. X is the first, at the
noindex preview route **`/preview/platforms/x/`**. Design: Figma
`mM9B4Zv9ON3pIyh3IvB4Il`, node `902:114` (the X frame) on `902:111` (the shared
contract).

## Files

| What | Where |
|---|---|
| Shared contract and one record per page | `data/platform_pages.json` |
| Shape | `schemas/platform_page.schema.json` (`make check-schemas`) |
| Joins and build-time guards | `layouts/_partials/platform-page-data.html` |
| Template | `layouts/platform-page.html` |
| Styles, script | `assets/css/platform-page.css`, `assets/js/platform-page.js` |
| Page file | `content/en/preview-platform-<id>.md` |
| Checks | `.github/scripts/check_platform_pages.py` (`--source` in `check-schemas`; `make check-platform-pages` on the build), `platform_page_harness.js`, `test_platform_pages.py` |

## Reusable versus X-specific

Reusable, and never written per platform:

- **The contract** (`contract` in the data file): the three stages (Write, Review,
  Track), the preview and illustration labels, and the closing Activities
  illustration. Once and recurring activities share one Activities model in which
  the platform is a filter, not a separate Upcoming or History destination, so
  that visual is the same on every page.
- **Facts.** Name, logo, docs link and reach come from `data/platforms/<id>.yaml`;
  each action's name, behavior and limits from `data/actions.json` plus that YAML.
  The breakdown bodies are computed from them, so they cannot drift from the docs.
- **Layout and behavior**: the template, CSS, script and checks.

X-specific, in its record: the headline and lede, the activity types (Post,
Respond, Amplify, each bound to one action the YAML lists: `post`, `reply`,
`amplify`), each type's illustrated scene and stage lines, the examples and the
breakdown titles.

## Behavior

- **Selector.** A native radio group. Picking a type swaps every `[data-pp-for]`
  element: the illustration, the intent line, Start's context, the "Your pick"
  rows in the breakdown and the Activities chips. The change is announced in a
  polite live region. Arrow keys move between types natively. Picking a type by
  hand also returns the illustration to its own scene, whatever an example's
  preview put there.
- **Source order is copy, selector, Start, illustration** (Figma 902:111: a narrow
  screen stacks the visual below the intent and keeps Start in the first screen).
  The desktop grid still puts Start under the selector in the left column beside
  the illustration. There is one Start, never a duplicate; the build check fails an
  illustration placed before it.
- **One primary call to action.** Start goes to `/download/`. The app's only web
  link, `blowhorn://content/new`, takes a URL, title and text (the bookmarklet's
  contract), not a platform or an activity type, so Start cannot pre-select X or
  Post. The note under Start says so: pick the activity again in the app. When the
  app gains a link that takes a platform and a type, build that link in the data
  partial (`startHref`) and update the schema description and the note in the same
  change. The closing Activities copy says the activity starts in the app, never
  on this page.
- **Illustration, not footage.** The hero is a switchable storyboard labelled
  "Interactive preview" and "Illustration, not a recording", with no play button,
  scrubber or timestamp. No recording exists; when one does, extend `media` in the
  schema, template and checks together.
- **Examples rail** (optional content, never core facts). A native scroll area
  with snap points. A phone shows one card and a peek of the next, with a trailing
  spacer so the last card can start at the left edge; a wider rail shows a whole
  number of cards (2, then 3), so every stop is a card's own edge and Next never
  leaves a card cut off at the left. The script adds previous and next buttons that page it by hand
  (no autoplay) and a count of the examples in view. The count is plain text that
  follows any scrolling; only a button press is announced, once, from where the
  rail will land, so a swipe never reads out every frame. The buttons use
  `aria-disabled`, so a focused button keeps focus at either end, and a focused
  example scrolls into view natively. "Preview above" puts an example's sample in
  the hero, selects its type and moves focus to the illustration.
- **Breakdowns.** Native `<details>`, all collapsed at load: what Blowhorn can do,
  limits and notes (a Dispatch card: technical facts), how each action runs. The
  limits item lists whatever `data/platforms/<id>.yaml` gives an action under
  `limits`, so it mixes caps with notes such as analytics' "Read-only." and is
  titled and counted that way, never as caps only. For X, Post and Respond carry
  the daily caps the X docs already state (50 original posts, 200 replies, for an
  account without a checkmark); they are in the YAML, so the docs table and this
  page read the same text.
- **Cards** are picked by content (`DESIGN.md`, Cards): in the rail, paper for the
  featured example, field for an explanation, plain for a secondary one, stamp for
  a recap of facts; Dispatch for the limits. The rail shows up to four at once, so
  any four neighbours differ and paper appears once (`--source` and the build fail
  otherwise). The variant is data, not dealt by `card-deal.html`, because the deal
  picks by preference order and cannot keep a variant bound to what its example is.
  Glass is used for the two floating surfaces only: the storyboard and the
  breakdown panel; both go solid under `prefers-contrast: more`. Type uses the
  site's styles (`.h3`, `.ui`, `.body`), no literal sizes.
- **Motion** is CSS transform and opacity: a swapped scene and an opened breakdown
  settle in, the chevron turns. Under `prefers-reduced-motion: reduce` nothing
  animates and nothing scrolls smoothly.
- **Without script** every type's intent is listed, the first type's illustration
  shows, the rail scrolls natively and the breakdowns still open and close.

No library is loaded. Embla Carousel and Motion were considered: a native scroller
already gives touch, trackpad and keyboard scrolling and brings a focused example
into view, and CSS covers the motion, so neither had a job.

## Preview route rules

The page file sets `layout: platform-page`, `platform: <id>`,
`url: /preview/platforms/<id>/`, `noindex: true`, `exclude_search: true`,
`sitemap: {disable: true}` and `build: {list: never}`; `hugo.toml` excludes
`/preview/**` from llms.txt. Nothing in the navigation links to it.
`make check-platform-pages` fails if the built page is indexed, listed in the
sitemap, llms.txt, llms-full.txt or the search index, or linked from another page
(absolute, base-prefixed, relative, with or without the trailing slash).

## Add the next platform

1. Confirm the platform is `supported` in `data/integrations.json` and its
   `data/platforms/<id>.yaml` lists the actions you want as types.
2. Add a record to `pages` in `data/platform_pages.json`: route
   `/preview/platforms/<id>/`, two to four activity types bound to listed actions,
   their scenes, examples (variants by content, no four neighbours alike) and the
   breakdown titles. Leave the contract alone.
3. Add `content/en/preview-platform-<id>.md` with the front matter above.
4. Run `make check-schemas`, `make check-platform-pages` and `make test-scripts`,
   then check 390, 820 and 1440 px in light and dark, and 320 px for overflow
   (`docs/deploy.md`).

Promoting a page out of preview is a deliberate change, not a data edit: the
schema's `route` pattern is preview-only, and a promoted page needs a new route, a
navigation entry, sitemap and search inclusion, and an update to these rules.

## Known limits

- **Start cannot carry the pick** into the app (see Behavior).
- **The Activities illustration shows the contract's model.** Today the app's
  Activity place switches between Upcoming, Routines and History views; the
  closing illustration draws the shared model of `902:111`, a single list with the
  platform and type as filters, and its caption says it is an illustration. Recheck
  the caption when the app's Activity place changes.
- **No recording exists yet**, so the hero is an illustration (see Behavior).
- **The examples are invented** and labelled "Illustrative example".
- **One platform so far.** The schema allows more records; only X has one.
