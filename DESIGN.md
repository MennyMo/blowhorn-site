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

## Concision

Say less, more clearly. Turn the verbosity dial down a notch from your first draft.

- One idea per sentence. Cut a sentence before you add one.
- Section intros are 2 sentences or fewer. Card bodies are about 30 words or fewer.
- Cut redundant clauses, filler ("that is what lets you", "as many as you need"), and doubled examples. One example beats three.
- Keep facts, guardrail wording and SEO terms; cut the padding around them. Don't shorten legal text substantively.
- No em dashes. No period at the end of a section title.

## PR checklist: whitespace and concision

- [ ] Every heading has at least `--head-gap` before its content; nothing touches
- [ ] New sections use the shared section and `.section-head` classes, not page-specific spacing
- [ ] Sections are clearly separated (whitespace, then divider or background shift if needed)
- [ ] Paragraphs stay within `--text-measure`; cards use `--card-pad` and `--grid-gap`
- [ ] Checked at 1280, 390 and 320 px, light and dark
- [ ] Intros <= 2 sentences, card bodies <= ~30 words, one idea per sentence
- [ ] No em dashes; no trailing periods on section titles

## Code and commands

Rule (Lee, 12 Oct 2026): **anywhere the site shows a command a reader might run, it can be copied in one click.** Source: `layouts/_partials/code-card.html`, `layouts/_markup/render-codeblock.html`, `assets/js/code-card.js` and the "Terminal code card" section of `assets/css/site.css`.

1. **Every code block is a terminal code card:** title bar with three dots, a file or `terminal` label, a language pill and a Copy button, on a glass window that is light in light mode and near-black in dark mode. Docs fences get it through the render hook; layouts call the partial.
2. **Declare the language.** Each card names the language of its actual content (`bash`, `markdown`, `json`, `toml`, `yaml`...) so Chroma highlights it with the brand token colours. Markdown front matter is highlighted as YAML.
3. **Prompts and output are never copied.** Shell cards draw a `$` before each command line (not before comments, blank lines or continuation lines) as an unselectable element that copy drops. Untyped or `text` fences are sample output: labelled `output`, muted, no copy button.
4. **Inline commands in prose** (`blowhorn ...` in backticks) get a small copy button after them. Commands with placeholders such as `<url>` are not copyable; show them in a card with the placeholder explained instead.
5. **Accessible:** the copy button is a real button with an `aria-label`, reachable by keyboard, and "Copied" is announced through an `aria-live` region. Code scrolls horizontally rather than wrapping; it must work at 320px.
6. **No third-party scripts** for highlighting or copy: Hugo's built-in Chroma with class output, and a small local script.

## Interface art

The miniature product UI in the Product menu and the homepage "Ways in" section is one partial, `layouts/_partials/interface-art.html` (styles under "Interface art" in `assets/css/site.css`). It is drawn from the real surfaces, never invented:

- **Desktop app** copies the console: lights at the top of the left rail (hidden-inset title bar, no URL bar), the Crowhorn and wordmark, "+ New activity", the five places (Home, Activity, Profiles, Performance, Safety) and the "on watch" status line, beside Activity's Upcoming list. Sources in the product repository: `desktop/src/renderer/console/ConsoleRail.tsx`, `places.ts` and `desktop/src/ui/PlatformIcon.tsx`. When the app's rail or vocabulary changes, update the art.
- **Web app** and **Chrome extension** share a Chrome-on-Mac frame (`interface-art-browser.html`): lights at the far left of the tab strip, back/forward/reload, the omnibox, a bookmarks bar; the extension adds the pinned Blowhorn icon.
- Platform marks are the app's monoline marks (`interface-art-mark.html`), not filled brand logos. App labels say "activity", never "post".
- The menu's narrow rows draw the art at 92px; a container query in the same CSS keeps each piece legible there. Check both widths, light and dark.

## Mascot consistency

Mascot art comes from the product repository's locked style (`marketing/brand/major-blowhorn/STYLE-LOCKED.md` and `consistency.md` there: one locked prompt, reference images, no text in the art). The oil-painting process that used to be described here is historical; never start a new scene from it. On the site:

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
- Current assignments: Major's intros and asides (/major/ hero, the home Major card, /brand/, the 404) are `paper`; the home "Fall in, profiles" rally and the army demo's yells are `command`; the agent pages' Try saying prompts are `mint`; the /major/ Greatest hits list is neutral.
- The storybook variant is retired: its only page, the /home-alt/ preview, was deleted with the flat storybook art.

