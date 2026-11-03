# Blowhorn site design rules

The brand-wide design language (principles, colour, type, liquid glass, platform logos, the mascot) lives in `internal/DESIGN.md` in the product repository (private, so it is named rather than linked). This file is the one written source for the site's own rules below; the product page links here and does not repeat them.

## Whitespace and rhythm

Whitespace separates ideas. A title never touches its content, and sections never run together. On the site these rules live in one token block at the end of `assets/css/site.css` ("Whitespace and rhythm"); shared classes (`.section`, `.agent-section`, `.compare-section`, `.brand-section`, `.section-head`, `.page-head`, `.section-body`, `.grid`, `.card`) read the tokens, so spacing is structural, never a per-page patch.

| Token | Mobile | Desktop (>= 900px) | Use |
|---|---|---|---|
| `--section-y` | 64px | 112px | Section padding-block |
| `--head-gap` | 32px | 40px | Section head (or bare h2) to its content, minimum |
| `--eyebrow-gap` | 12px | 12px | Label to heading |
| `--intro-gap` | 16px | 16px | Heading to its intro paragraph |
| `--grid-gap` | 24px | 32px | Card grid gutters |
| `--stack-gap` | 16px | 16px | Stacked items (FAQ, lists) |
| `--card-pad` | 24px | 32px | Card padding |
| `--text-measure` | 64ch | 64ch | Paragraph line length |

Rules:

- Never let a title touch its content: heading-to-content is at least `--head-gap` (32px mobile, 40px desktop). Wrap the title and intro in `.section-head`; whatever follows gets the gap automatically.
- Separate sections with whitespace first (`--section-y` on both sides). Neighboring sections get a faded hairline divider; glass panels that are their own section float with half a section of air instead. Use background shifts only where a section is a distinct moment (CTA, the Major).
- Keep paragraphs at or under `--text-measure` (about 60-68 characters). Section heads max out at 44rem.
- Cards get `--card-pad` on every side and `--grid-gap` between them. Don't shrink either to fit more in; cut copy instead.
- Never hard-code a margin or padding in px on a page template. Add or reuse a token.
- Check 1280, 390 and 320 widths, light and dark, before merging.

## Cards

Two rules, from the owner's order of 2 Nov 2026:

1. **No stripe on one edge.** A card, callout, quote, table row or panel never carries a coloured stripe on one side: no `border-left` or `border-right` (or inline start or end) in a colour, no inset shadow down one side, no `::before` bar, and no hard offset shadow (an outer shadow with no blur pushed off one or two edges, the retired `shadow-pop` sticker that the Download button and the Major card wore; Lee, 2 Nov 2026). Depth is the soft `--glass-shadow`. A card keeps an even border on all sides, or none. Emphasis comes from the eyebrow label, the type and the fill. Neutral 1px column rules, the selected-tab mark and checkmarks are structure, not stripes.
2. **No single generic card.** Pick the variant by what the content is. No two cards in the same row share a variant, and no card shares one with the card directly above it, at any width the grid is shown at: a 3-column grid that drops to 2 columns on a tablet and 1 on a phone has to hold at all three.

The variants live once, in `assets/css/cards.css`. The same file is published unminified at `/assets/brand/cards.css` for tells.blowhorn.ai. `.card` (padding, radius, gaps) stays the structural base in `site.css`; a variant only sets the look.

How a grid gets its variants:

- **A loop** calls `layouts/_partials/card-variant.html` with the card's index, the grid (`"grid" "grid-3"`, or `"cols"` with every column count it shows), the number of cards (`"n"`, required) and, if the default does not fit the content, the variants in order of preference. `card-deal.html` deals them card by card: each card takes the first variant that no card in its row and not the card above it holds, at any of those widths, and the build fails when the variants run out. A grid that shows 3 or 4 across needs four variants once it has a second row.
- **A grid class** that holds cards lists its column counts in `card-deal.html`, so keep that map in step with the CSS. Card grids use fixed breakpoints, not `auto-fill`, so the counts are known.
- **A filter** that hides cards (`resources.js`, `action-filter.js`) hands the variants out again: the grid prints its deal as `data-card-deal`, and `assets/js/card-deal.js` gives its first k entries to the k visible cards after each change (the deal for fewer cards is always the start of the deal for more). Load the filter through `layouts/_partials/filter-script.html`.
- **Docs cards** come from the synced Markdown without a variant; `layouts/_partials/docs-content.html` deals each grid of them for the columns its container shows.
- **A hand-written grid** names each card's variant; or, better, calls the helper with literal indexes; check it at every width the grid shows. Count only the cards drawn: collect a filtered list first, then range over it.

Paper and Dispatch keep one palette in both themes, so they also set `--ink`, `--ink-muted`, `--link`, `--line` and `--surface-tint` for everything inside them. A component rule that reads those tokens stays legible inside either card without a per-variant override. A card link's round arrow chip fills with `--card-chip`, which defaults to `--surface-tint`; Field, whose own fill is that tint, sets it to `--surface` so the chip still shows.

| Class | Name | Use for | Fill | Edge | Text (light / dark) | Contrast |
|---|---|---|---|---|---|---|
| `card-paper` | Field order | Major's voice, testimonials, the one featured item in a section | cream in both themes | 1.5px near-black, no shadow | near-black ink, charcoal muted | ink 15.2:1, muted 8.6:1 in both themes |
| `card-dispatch` | Dispatch | developer notes, API and JSON facts, commands | near-black in both themes | 1px dashed teal-shade (#008F80) | cream ink, mint muted, teal-bright mono `>` label | ink 15.2:1, muted 12.1:1, label 8.5:1 |
| `card-stamp` | Stamp | facts, stats, guarantees, proof points, compliance | none (the page shows through) | 2px ink (1px border plus a 1px inset ring, so the box matches the other variants); label boxed in mono caps | ink, ink-muted | 16.3:1 and 5.6 / 7.2:1 for muted; edge 16.3:1 |
| `card-field` | Field | feature and explanation grids, the common case | surface-tint | none; the hover edge is line-strong | ink, ink-muted | 14.2 / 12.4:1 ink; 4.9 / 5.5:1 muted |
| `card-plain` | Plain | secondary lists, link lists, low emphasis | none | 1px line-strong on all sides | ink, ink-muted | 16.3 / 16.3:1 ink; 5.6 / 7.2:1 muted; edge 3.7 / 4.4:1 |
| `card-glass` | Glass | one floating surface over content: a menu, the header, a hero. Also the `.glass` panel class. Never on a grid | solid `--surface` (flat, no blur) | even 1px `--glass-edge` on all sides, soft shadow | ink, ink-muted | 16.0 / 15.0:1 ink; 5.5 / 6.6:1 muted |
| `card-cream` | Signal feature | a feature with its art (How it works span 7) | cream (surface-raised in dark) | none | near-black ink, charcoal muted (page ink in dark) | as Paper, without the outline |
| `card-raised` | Signal mockup | a mock sitting on the page as a card (How it works, span 12) | surface-raised | none | ink, ink-muted | as Field |

Ratios are WCAG 2.1 for the pair named, computed for light and dark. Two edges are deliberate:

- **Paper in dark mode** keeps a near-black outline on a near-black page, so the edge you see is the cream fill against the page (15.2:1).
- **Plain uses line-strong, not `--line`.** `--line` is 1.4:1 on white, under the 3:1 a UI boundary needs.

Do:

- Pick the variant by content, then check every card in its row and the card above it at 390, 820 and 1440px.
- Give every card link the same hover: a 2px lift and a stronger edge, no glow. Nothing moves under reduced motion.
- Let a featured item be paper, and let one stat row be stamps.
- Let a featured item stand out by fill and type, never by a stripe.

Don't:

- Draw a stripe on one edge, on a card, a quote, a table row or a callout.
- Give a button, card or tile a hard offset shadow (`4px 4px 0 0`); a primary button stands out by its teal fill.
- Put the same variant on two cards in a row or on a card and the one above it, or make a whole grid one variant.
- Put glass on a grid of cards, or on anything that is not a floating surface.
- Hard-code a card's colours in a template: add a variant, or use an existing one.

Live specimen: /brand/#cards.

## Install call to action

- Every install link says "Download" and comes from `layouts/_partials/download-button.html` (kind primary, secondary or text). The header's is always secondary.
- A view has one teal primary (`.button-primary`) in its main content. A free check is a text link; a second action is an outline button.
- `make check-install-cta` (in `make check`) fails a second primary or an old label. Docs are skipped; the home page is pending its rebuild (#418).
- `/download/`: the Mac button is the only primary. The extension, the command and the bookmarklet are outline buttons. Windows is a plain line.

## Flat Signal

The site is flat. Surfaces are solid, edges are even and depth is one soft shadow on a floating surface. Three rules, enforced by `make check-site-css` over `assets/css` and `assets/scss` (`.github/scripts/check_site_css.py`):

- **13px floor.** No text under 13px in mixed case. Only uppercase mono labels and numerals may go smaller (11px). The miniature interface art (`.ia-*`, `.iface-art`) is a picture of the app, aria-hidden, and is exempt.
- **No edge stripes.** No border-left, border-right or inset shadow in an accent colour down one side. The docs sidebar's active page is a tint fill with teal text, not a bar. Neutral 1px rules and the selected-tab mark stay.
- **No glass.** No `backdrop-filter`, no inset highlight, no sheen or ambient gradient. A panel that floats is a solid surface with an even border.

## Casing

Yi's rule (2 Nov 2026): **small uppercase is for section and field labels only** (eyebrows such as "HOW IT WORKS", form field labels). Everything else is sentence case: headings, buttons, menu and nav items, titles and body. Proper nouns and product names keep their capitals ("Blowhorn", "Major Blowhorn", "Chrome", "LinkedIn", "Am I a Bot?"). Examples: "Questions", not "Frequently Asked Questions"; "Get started free", not "Get Started Free".

`make check-casing` fails a Title Case heading, button or nav link in the built site. Its allowlist of names is in `.github/scripts/check_casing.py`; the synced docs (`/docs/`) and the competitor pages (`/compare/`) are not read by it. Add a name to the allowlist rather than capitalising a common word.

## Concision

Say less, more clearly. Turn the verbosity dial down a notch from your first draft.

- One idea per sentence. Cut a sentence before you add one.
- Section intros are 2 sentences or fewer. Card bodies are about 30 words or fewer.
- Cut redundant clauses, filler ("that is what lets you", "as many as you need"), and doubled examples. One example beats three.
- Keep facts, guardrail wording and SEO terms; cut the padding around them. Don't shorten legal text substantively.
- No em dashes. No period at the end of a section title.

## PR checklist: whitespace, cards and concision

- [ ] Every heading has at least `--head-gap` before its content; nothing touches
- [ ] New sections use the shared section and `.section-head` classes, not page-specific spacing
- [ ] Sections are clearly separated (whitespace, then divider or background shift if needed)
- [ ] Paragraphs stay within `--text-measure`; cards use `--card-pad` and `--grid-gap`
- [ ] Type is 13px or more in mixed case; no border-left accent, inset stripe or backdrop blur (`make check-site-css`)
- [ ] Headings, buttons and nav are sentence case; section and field labels are the only uppercase (`make check-casing`)
- [ ] No coloured stripe on one edge of a card, callout, quote, table row or panel, and no hard offset shadow; no two cards in a row, and no card and the one above it, share a card variant, at any width the grid shows
- [ ] Checked at 1280, 390 and 320 px, light and dark
- [ ] One teal primary per view; install links come from `download-button.html` and say "Download"
- [ ] Intros <= 2 sentences, card bodies <= ~30 words, one idea per sentence
- [ ] No em dashes; no trailing periods on section titles

## Code and commands

Rule (Lee, 12 Oct 2026): **anywhere the site shows a command a reader might run, it can be copied in one click.** Source: `layouts/_partials/code-card.html`, `layouts/_markup/render-codeblock.html`, `assets/js/code-card.js` and the "Terminal code card" section of `assets/css/site.css`.

1. **Every code block is a terminal code card:** title bar with three dots, a file or `terminal` label, a language pill and a Copy button, in a window that is light in light mode and near-black in dark mode (a window, not a card variant; see Cards). Docs fences get it through the render hook; layouts call the partial.
2. **Declare the language.** Each card names the language of its actual content (`bash`, `markdown`, `json`, `toml`, `yaml`...) so Chroma highlights it with the brand token colours. Markdown front matter is highlighted as YAML.
3. **Prompts and output are never copied.** Shell cards draw a `$` before each command line (not before comments, blank lines or continuation lines) as an unselectable element that copy drops. Untyped or `text` fences are sample output: labelled `output`, muted, no copy button.
4. **Inline commands in prose** (`blowhorn ...` in backticks) get a small copy button after them. Commands with placeholders such as `<url>` are not copyable; show them in a card with the placeholder explained instead.
5. **Accessible:** the copy button is a real button with an `aria-label`, reachable by keyboard, and "Copied" is announced through an `aria-live` region. Code scrolls horizontally rather than wrapping; it must work at 320px.
6. **No third-party scripts** for highlighting or copy: Hugo's built-in Chroma with class output, and a small local script.

## Interface art

The miniature product UI in the AI page's "Ways in" section is one partial, `layouts/_partials/interface-art.html` (styles under "Interface art" in `assets/css/site.css`). It is drawn from the real surfaces, never invented:

- **Desktop app** copies the console: lights at the top of the left rail (hidden-inset title bar, no URL bar), the Crowhorn and wordmark, "+ New activity", the places (Dashboard, Activity, Profiles, Performance, Posture) and the "on watch" status line, beside Activity's Upcoming list. Sources in the product repository: `desktop/src/renderer/console/ConsoleRail.tsx`, `places.ts` and `desktop/src/ui/PlatformIcon.tsx`. When the app's rail or vocabulary changes, update the art.
- **Web app** and **Chrome extension** share a Chrome-on-Mac frame (`interface-art-browser.html`): lights at the far left of the tab strip, back/forward/reload, the omnibox, a bookmarks bar; the extension adds the pinned Blowhorn icon.
- Platform marks are the app's monoline marks (`interface-art-mark.html`), not filled brand logos. App labels say "activity", never "post".
- The Product menu is cards only (no art, no intro copy). The art appears on the AI page only, and a container query in the same CSS keeps each piece legible at its narrow sizes. Check both widths, light and dark.

## Mascot consistency

Mascot art comes from the product repository's locked style (`marketing/cast/major-blowhorn/STYLE-LOCKED.md` and `consistency.md` there: one locked prompt, reference images, no text in the art). The oil-painting process that used to be described here is historical; never start a new scene from it. On the site:

- Use the official art in `static/assets/brand/mascot/`; one character per page, and only Major and the General speak, in a speech bubble below.
- Lore art for /major/ lives in `static/assets/brand/mascot/lore/` as WebP with alt text.

## Speech bubbles

Every bubble uses `layouts/_partials/bubble.html`; styles are under "Speech bubble" in `assets/css/site.css`. The body and tail are one silhouette with one continuous outline. Never draw a tail as its own stroked shape. Tails: `left`, `right`, `top`, `bottom`, or `auto` (bottom on narrow screens, left from 720px). The live specimen is on /brand/#bubbles.

| Variant | Use for | Fill | Outline | Text | Contrast |
|---|---|---|---|---|---|
| default (neutral) | quotes, lists of lines | surface | near-black, cream in dark | ink-wordmark | 9.3:1 light, 16.3:1 dark |
| `paper` | Major speaking | cream | yellow-shade | charcoal | 8.6:1 |
| `mint` | what a person says to an agent | mint | teal-deep | charcoal | 6.9:1 |
| `command` | Major's orders, calls to action | teal-deep | none | white | 5.6:1 |

Paper, mint and command keep their colours in dark mode so a voice looks the same in both themes; neutral follows the theme. All pass WCAG AA for body text.

- Do pick the variant by who is talking, and use the same variant for the same voice on every page.
- Do keep command to one per section.
- Don't mix variants within one list, put links or buttons inside a bubble, or use teal (#00B39F) as a fill under white text (2.6:1).
- Current assignments: Major's intros and asides (/major/ hero, the home Major card, /brand/) are `paper`; the home "Fall in, profiles" rally and the army demo's yells are `command`; the agent pages' Try saying prompts are `mint`; the /major/ Greatest hits list is neutral.
- The storybook variant is retired: its only page, the /home-alt/ preview, was deleted with the flat storybook art.

## Type

The families are `--font-display` (Bricolage Grotesque, headings), `--font-sans` (Instrument Sans, text and interface) and `--font-mono` (JetBrains Mono, code, commands, IDs and numerals). Section and field labels (eyebrows, `.label`) use the label token, `--font-label`, which is `--font-display` at 600, 11px/16px, 0.08em tracking, uppercase, with optical sizing on. It mirrors the desktop app's `--font-label`. Keep code-like labels (timestamps, kbd, IDs, numerals) and the stamp card's label in mono, set on the element rather than by the `.label` class. The style lives in `static/assets/brand/tokens.json` (Display group, `label`).
