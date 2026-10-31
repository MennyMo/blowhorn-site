---
name: ux-audit
description: Audit a blowhorn.ai page, layout or section (home sections, product, download, solutions, roles, use cases, AI and agents pages, pricing, compare, resources, docs) against the Blowhorn design language and report findings in one table. Use when asked to audit, review or check the site's UI, UX, layout, visual hierarchy, card or section treatments, design-system or brand adherence, whitespace, copy, the mascot on a page, accessibility or contrast, and before merging any change to layouts/, assets/css/site.css or a page's data file. For the desktop app use the ux-audit skill in blowhorn-ai/blowhorn instead.
---

# UX audit (site)

An audit answers one question per layout: **does the eye land where the page needs it, and does every piece obey the design language?** It is evidence, not taste: each finding cites the rule it breaks by file and section, plus a screenshot or a line of code.

## The sources (cite them; never restate a value in a finding)

| Rule family | Authority |
|---|---|
| Whitespace, rhythm, concision, interface art, speech bubbles | `DESIGN.md` here |
| Brand-wide language: principles, colour, type, liquid glass, platform logos, cards, mascot | `internal/DESIGN.md` in the product repository (private: cite it in an issue, never link it from a page) |
| Tokens | `static/assets/brand/tokens.json`; `assets/css/site.css` implements them |
| Site rules (browser wording, brand tokens only, product name, third parties) | `AGENTS.md` here |
| Designs | Figma file `mM9B4Zv9ON3pIyh3IvB4Il` (the site pages and landing concepts) |

## Scope by layout, not by page

Pages that share a layout share its faults. Audit one representative page per layout in `layouts/*.html` (and each `layouts/_partials/home/*` section on its own), then list the other pages that inherit the result. Record each layout as `audited`, `skipped (why)` or `unreachable`.

## Capture the evidence

```bash
make site                                   # http://localhost:1313, live reload
chrome-devtools-axi open http://localhost:1313/<path>/
chrome-devtools-axi emulate --viewport "1280x900" --color-scheme light
chrome-devtools-axi screenshot "$TMPDIR/ux-audit/<layout>--1280--light.png"
chrome-devtools-axi emulate --viewport "390x844x3,mobile,touch" --color-scheme dark
chrome-devtools-axi screenshot "$TMPDIR/ux-audit/<layout>--390--dark.png"
```

- Every layout at 1280, 390 and 320 px, light and dark (`DESIGN.md`, Whitespace and rhythm). That is six shots; fewer is a partial audit and the report says which are missing.
- Full-page shots hide the fold. Also take the first viewport at 1280 and 390: that is what decides where the eye lands.
- Keep captures outside the checkout (`$TMPDIR/ux-audit/`): `data/` is Hugo's data directory, and anything under `static/` or `content/` is published.
- Compare with Figma (`get_screenshot` on the page's node). A layout with no Figma design is a finding (`no-design`), not a pass.

## Run the guards before judging by eye

`make check` is exactly what CI runs (links, third parties, theme, platform docs, action matrix, download links, brand kits, feeds, Tells links, naming, no internal content). Run it once; a failure is a finding with the target as evidence, and a passing target's rule is not re-checked by eye.

Candidates the guards do not catch (judge each hit):

```bash
git grep -n -E "[\"'\`]#[0-9a-fA-F]{3,8}[\"'\`;]|rgba?\(" -- layouts/ content/   # colour outside the token layer
git grep -n -E '(margin|padding)[a-z-]*: *[0-9]+px' -- 'assets/css/*.css' layouts/   # hard-coded spacing
git grep -n -E 'style="' -- layouts/                                     # inline styles on a template
```

## Judge what no guard can

Walk each layout's first viewport, then the full page, with these questions in order.

1. **Where does the eye land first, and is that the page's one job?** Name the focal element. If you cannot, or if three elements compete, that is a `major` finding.
2. **Inventory the treatments.** List every section and card treatment on the page (gradient card, glass card, plain section, white logo tile, bubble, Major card, `shadow-pop` card, list) and count each. One treatment carrying most of the page, or two neighbouring sections in the same treatment, flattens the hierarchy: the eye has no gradient of importance to follow.
3. **Does each treatment have one job?** A treatment means something: the focal card is used once, supporting cards are quieter, proof and lists are quieter still. A loud treatment (gradient, `shadow-pop`, a background shift) on something that is not the page's focus is a finding. `shadow-pop` belongs to the Major card and the hero's primary button only; background shifts only to a distinct moment (the CTA, the Major).
4. **Cards:** one `<a>` around the whole card, a title and one short line at most, no underlined card text, no links inside a linked card.
5. **Whitespace:** a title never touches its content (`--head-gap`); sections separate by whitespace first; paragraphs within `--text-measure`; no hard-coded spacing.
6. **Platform logos:** owners' files on opaque white tiles in both themes, never on glass, teal or yellow, never recoloured.
7. **The mascot:** one character per page; only Major and the General speak; the line is real text, never inside the art.
8. **Copy:** concise (intros of two sentences or fewer, card bodies about 30 words), hyphens never em dashes, the page's browser wording (`AGENTS.md`), "your account" never "Blowhorn Cloud", no Coming soon feature unlabelled.
9. **Glass and contrast:** text on glass or the ambient field holds 4.5:1 in both themes against the worst pixel behind it; reduced transparency and `prefers-contrast: more` fall back to solid.

## Severity

| Severity | Meaning |
|---|---|
| `blocker` | Contrast under AA, a broken guard, a forbidden claim, a private-repository link, a logo misuse |
| `major` | The eye has no clear landing point, one treatment dominates, a loud treatment on a minor element, no Figma design |
| `minor` | Spacing or token drift, copy polish |
| `figma-drift` | The page and Figma disagree; name which is right |

## Report

```markdown
| # | Layout (page / width / theme) | Severity | Rule (file § section) | Evidence | Fix |
|---|---|---|---|---|---|

**Treatment inventory:** <layout - treatment x count, ...>
**No Figma design:** <layouts>
**Not audited:** <layout - why>
```

A fix names the class, token or partial to use. Group one cause across layouts into one row.

## NEVER

- **Never propose a new card style as the fix for sameness.** Variety comes from giving the existing treatments distinct jobs and quieting most of them; a sixth decorative card adds noise, not hierarchy.
- **Never restate a token value in a finding or in a doc.** Cite the section. This file's own `DESIGN.md` is a partial copy of the brand language and already has to be kept in sync by hand.
- **Never audit one width or one theme and call it done.** Dark mode and 320 px are where contrast and wrapping break.
- **Never fix a finding with a page-specific margin, colour or inline style.** Fix the shared class or token so every page using it improves.
- **Never link the product repository from a page**, even when citing its rules: every reader gets a 404.
