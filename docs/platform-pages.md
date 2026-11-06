# Platform pages

A platform product page (blowhorn-site#466) shows what you can do on one platform:
pick an activity type, see it illustrated, try on a draft, scan every action and its
limits, see the rules of engagement, and copy a real setup. X is the first, at the
noindex preview route **`/preview/platforms/x/`**. Design: Figma
`mM9B4Zv9ON3pIyh3IvB4Il`, node `902:114` (the X frame) on `902:111` (the shared
contract). The matrix, playground, rules of engagement, Field Manual and setups
sections (PR #491) were built to the site's design rules (`DESIGN.md`) and have no
X-specific Figma frame yet: they need a Figma review before the page leaves preview.

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

- **The contract** (`contract` in the data file): the reviewer note, the three
  stages (Write, Review, Track), the illustration label and the closing Activities
  illustration. Once and recurring activities share one Activities model in which
  the platform is a filter, not a separate Upcoming or History destination, so
  that visual is the same on every page.
- **Facts.** Name, logo, docs link and reach come from `data/platforms/<id>.yaml`;
  each action's name from `data/actions.json`, its behavior and limits from that
  YAML, its CLI line from `data/action_examples.json`. The matrix is computed from
  them, so it cannot drift from the docs.
- **Layout and behavior**: the template, CSS, script and checks.

X-specific, in its record: the headline and lede, the activity types (Post,
Respond, Amplify, each bound to one action the YAML lists: `post`, `reply`,
`amplify`), each type's illustrated scene, the playground's starter drafts, and the
sourced facts and setups below.

### Sourced facts and setups

The rules-of-engagement presets and notes, the Field Manual facts and the setups
rail are page copy that restates a public page, so each carries its `source` (a
site path with an anchor) and a verbatim `quote`; a setup's `code` is its own
quote. `check_platform_pages.py --source` reads the source's Markdown under
`content/en/` (and the JSON front matter of agent pages) and fails a quote or
snippet that page does not carry, or a number the page shows that its quote does
not hold. The built check fails a source anchor that no longer exists. Never cite
the product repository: it is private.

For X today:

| Section | Facts | Source |
|---|---|---|
| Rules of engagement | 12, 25 and 50 posts a day on X under Safety on, Weapons tight (the default) and Weapons free; nothing goes past a limit X publishes; a new profile or computer runs Safety on for its first 14 days | `/docs/how-to/settings/choose-your-rules-of-engagement/` |
| Matrix limits (YAML) | 50 original posts and 200 replies a day for an account without a checkmark (X's published limits); 400 follows per profile a day and 15 in any 15 minutes; analytics read-only | `data/platforms/x.yaml` |
| Field Manual | 2023 weights: an engaged reply 75, a like 0.5; each post after an author's first decays to a floor | `/field-manual/x/` |
| Setups | the `npx -y blowhorn-mcp` MCP entry; `blowhorn risk show --profile personal --platform x --json`; the Claude Code skill `.claude/skills/blowhorn/SKILL.md` | `/docs/how-to/set-up/connect-mcp-client/`, `/docs/reference/cli/risk/`, `/agents/claude-code/` |

## Behavior

- **Selector.** A native radio group. Picking a type swaps every `[data-pp-for]`
  element (the illustration, the intent line, the playground's preview title and
  post-only controls, the Activities chips) and tints the matrix rows bound to it.
  No row or fact is ever hidden. The change is announced in a polite live region.
  Arrow keys move between types natively.
- **Source order is copy, selector, call to action, illustration** (Figma 902:111:
  a narrow screen stacks the visual below the intent and keeps the call to action
  in the first screen). The desktop grid puts it under the selector beside the
  illustration. The build check fails an illustration placed before it.
- **One primary call to action: Get the browser extension.** It links to the
  extension's Chrome Web Store listing, the same link the download page's
  extension card uses (the check fails the build when the two differ). The link is
  built in the data partial (`extensionHref`), never in the record, and the schema
  allows only that label. Nothing sits under it: no note and no caption (the check
  fails anything beside it in `.pp-go` or an `aria-describedby` on it).
- **Annotations, not captions.** Reviewer-facing text is removed rather than
  explained in captions. The one that remains, `contract.reviewerNote` ("Preview:
  not final, and not linked from the site"), is drawn as an annotation: the
  alternate (coral) colour, mono type, a dashed edge on every side and the
  explicit mark "Reviewer note". It is never a standard caption (the check fails
  one). Remove it with the preview. True illustration labels stay as captions:
  "Interactive preview", "Illustration, not a recording", "Local preview" and the
  Activities illustration caption. Roadmap text uses the same mark pattern:
  "Planned" in the playground.
- **Illustration, not footage.** The hero is a switchable storyboard with no play
  button, scrubber or timestamp. No recording exists; when one does, extend
  `media` in the schema, template and checks together.
- **Playground ("Try on a draft")**, local only. The visitor types a draft, or
  picks a starter (which selects its type and fills the draft), and may choose an
  image from their own computer. The preview mirrors the draft as text, never
  markup. For the type bound to `post`, a counter shows the length against
  `playground.thread.at` (274, which must match the YAML's "longer than 274
  characters" or the build fails) and flags "Goes out as a thread" past it,
  announced once each way (and cleared when the type moves off Post, so it is never read as a reply's state). The counter, its `aria-describedby` on the draft, the
  flag and its announcement apply only while the post type is selected, and
  refresh on a type change. The image is shown through an object URL and released
  when removed or replaced (and on `pagehide` only when the page is not kept in
  the back/forward cache). A non-image is refused with a short announced message
  (`playground.fields.notImage`), and an image the browser cannot decode (for
  instance HEIC) is dropped, the picker cleared and `fields.unreadable` announced.
  A starter replaces the draft, with no undo. There is no form and no named
  field, and `platform-page.js` makes no request and touches no storage, cookie,
  credential or extension API (`--source` fails one). Nothing is published or
  submitted. The length is counted in code points, which can differ slightly from
  Blowhorn's own count; the preview is an illustration.
- **Action matrix**, visible at load (never in a `<details>`): one row per YAML
  action, in YAML order. Columns: Action (linked to its `#action-<id>` on the docs
  page, with the type label when it differs, Respond for Reply), What it does,
  Limits and notes ("None listed" when the YAML gives none), In the CLI (the
  example command with its inline copy button, or the example's placeholder note).
  A command wraps only between whole tokens. It is a real, native two-axis table at
  every width (no `display` change, no ARIA roles, no stacked cell labels), inside a
  focusable group (`role="group"`, `tabindex="0"`, `aria-labelledby` the section
  heading; a `region` would duplicate the section's own landmark name) that scrolls sideways on a narrow screen, so the page never overflows.
- **Rules of engagement.** One Stamp card holds the three presets as one stat row
  split by neutral rules (no two cards in a row share a variant), each linked to
  its section of the rules-of-engagement docs, then the sourced notes.
- **Field Manual teaser.** Two linked cards (paper, then field), each to the
  section it quotes, and a link to the whole briefing.
- **Setups rail** ("Run it from your tools"). Terminal code cards
  (`code-card.html`, copied by `code-card.js`) on a native scroll area with snap
  points: one card and a peek on a phone, two on a wide screen, so every stop is a
  card's own edge. The script adds previous and next buttons that page it by hand
  (no autoplay) and a plain-text count; only a button press is announced. The
  buttons use `aria-disabled`, so a focused button keeps focus at either end.
- **Cards** are picked by content (`DESIGN.md`, Cards). Glass is used for the
  storyboard only; it goes solid under `prefers-contrast: more`. Type uses the
  site's styles (`.h3`, `.ui`, `.body`, `.label`), no literal sizes.
- **Motion** is CSS transform and opacity: a swapped scene and a picked image
  settle in. Under `prefers-reduced-motion: reduce` nothing animates and nothing
  scrolls smoothly.
- **Without script** every type's intent is listed, the first type's illustration
  shows, the playground shows the first starter as a static preview with its
  controls hidden, the matrix is a plain table and the rail scrolls natively.

No library is loaded. Embla Carousel and Motion were considered: a native scroller
already gives touch, trackpad and keyboard scrolling, and CSS covers the motion.

## Preview route rules

The page file sets `layout: platform-page`, `platform: <id>`,
`url: /preview/platforms/<id>/`, `noindex: true`, `exclude_search: true`,
`sitemap: {disable: true}` and `build: {list: never}`; `hugo.toml` excludes
`/preview/**` from llms.txt. Nothing in the navigation links to it.
`make check-platform-pages` fails if the built page is indexed, listed in the
sitemap, llms.txt, llms-full.txt or the search index, or linked from another page
(absolute, base-prefixed, relative, with or without the trailing slash).

## Add the next platform

1. Confirm the platform is `supported` in `data/integrations.json`, its
   `data/platforms/<id>.yaml` lists the actions you want as types, and each has a
   `data/action_examples.json` entry.
2. Add a record to `pages` in `data/platform_pages.json`: route
   `/preview/platforms/<id>/`, two to four activity types bound to listed actions,
   their scenes, starter drafts, the matrix copy, and sourced rules of engagement,
   Field Manual facts and setups, each quoting its public page. Leave the contract
   alone.
3. Add `content/en/preview-platform-<id>.md` with the front matter above.
4. Run `make check-schemas`, `make check-platform-pages` and `make test-scripts`,
   then check 1280 and 390 px in light and dark, and 320 px for overflow
   (`DESIGN.md`, `docs/deploy.md`).

Promoting a page out of preview is a deliberate change, not a data edit: the
schema's `route` pattern is preview-only, and a promoted page needs a new route, a
navigation entry, sitemap and search inclusion, removal of the reviewer note, and
an update to these rules.

## Known limits and planned work

- **The call to action installs the extension only.** The extension works with the
  Blowhorn desktop app; its side panel offers "Download the Blowhorn app" when the
  app is missing (`/docs/how-to/set-up/install-the-chrome-extension/`). No link
  installs both, or carries the picked platform and type: the app's only web link,
  `blowhorn://content/new`, takes a URL, title and text. When one exists, change
  the label, `extensionHref` and the check together.
- **The Web Store link is written in several templates** (`layouts/download.html`,
  `download-thanks.html`, `_partials/header.html`, `footer.html`,
  `home/ways-in.html`, this page's data partial, and `content/en/legal/terms.md`).
  The platform page check ties this page to the download page's copy; the fix is
  one `data/extension.json` (not `data/download.json`, which the release pin job
  rewrites) read by every template, done as its own change.
- **Planned, not shipped: a dry run from the extension.** Today Dry fire lives in
  the desktop app's New order: it rehearses a post per platform and desk, signs in,
  stops before composing, and saves nothing
  (`/docs/reference/use-the-desktop-app/`). The planned flow is New order from the
  extension, then an anonymous dry fire of the visitor's draft after the extension
  is installed. The playground says so only under its "Planned" mark. Product
  tracking: the private product repository's issue
  https://github.com/blowhorn-ai/blowhorn/issues/2178 ("Anonymous dry-fire free
  tier: try New Order in the extension without deploy"). This doc only; never link
  it from a rendered page. When it ships, replace the Planned line with the real
  flow and its docs link.
- **The Activities illustration shows the contract's model.** Today the app's
  Activity place switches between Upcoming, Routines and History views; the
  closing illustration draws the shared model of `902:111`, and its caption says it
  is an illustration. Recheck it when the app's Activity place changes.
- **No recording exists yet**, so the hero is an illustration (see Behavior).
- **The starter drafts and scenes are invented** sample text.
- **One platform so far.** The schema allows more records; only X has one.
