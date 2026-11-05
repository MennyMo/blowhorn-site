---
name: brand-identity-review
version: 1.0.0
description: >-
  Use for brand-facing writing or changes to user-visible strings, marketing,
  marks, mascots, or design tokens, and targeted final reviews or requested
  audits. Skip unrelated code; this is not an every-PR CI requirement.
---
# Brand identity review

## When to invoke
Use during brand-facing authoring and once at meaningful final review of relevant changed content. Also use for an explicitly requested release sweep, manual review, or scheduled audit. Do not invoke after every command, commit, or unrelated PR; rerun only for materially changed brand-facing content. This skill does not create a CI job, merge gate, workflow, or schedule.

Project coding/reviewer instructions should point to this skill and a small set of relevant current paths. Treat paths as candidate selection, not proof of brand impact: inspect the actual diff, including visible text embedded in code. Avoid invoking a full review just because a large UI directory changed. Skip unrelated backend, tests, and mechanical changes silently, without a mandatory brand checkbox or N/A line on every PR. If explicitly asked to classify an unrelated change, explain why it is out of scope.

## Inputs and authority
Determine the project, changed artifacts, audience, and surface. Locate current approved brand guidance, voice rules, positioning and claims, logo/mascot assets, design tokens, terminology, design system, and review instructions. Use current default-branch or live sources and record commit/revision or observation date. Reuse project copy and UX skills rather than duplicating their rules.

Do not create another guide, invent missing rules, or transfer another business's rules. Distinguish approved guidance, proposals, and implementations; neither code nor a design file automatically overrides approved guidance. Report source conflicts and their ownership instead of silently choosing one. Missing guidance or access is a gap, not a pass.

## Scope the review
Brand-facing changes include visible wording and names, marketing claims, UI states, illustrations, marks, mascots, public assets, design tokens, store listings, and the guide itself. Select only applicable checks. Review the changed content and enough surrounding context to judge it, not the whole repository.

If localization exists, use actual source and locale catalogs as the primary voice-review inputs. Check meaning, tone, terminology, interpolation/pluralization, context, and visible length. Do not force English phrasing or punctuation conventions onto other languages or claim native-language validation without evidence. Catalog-only review cannot cover visual identity or visible strings outside catalogs; retain relevant asset/token/UI checks. Do not assume localization exists until verified.

## Voice and messaging
- Match approved audience, tone, terminology, sentence style, and brevity.
- Keep alternate voice modes coherent and avoid accidental character voice in sensitive flows.
- Distinguish general marketing wording from precise compatibility, installation, and in-product language.
- Check claims against evidence; flag unsupported guarantees and misleading descriptions.
- Cite approved examples/do-and-don't rules and offer short replacements without inventing policy.

## Visual identity
- Verify approved marks, variants, clear space, minimum sizes, and backgrounds.
- Compare color and typography with canonical tokens; flag duplicated or drifting values.
- Check mascot/illustration style and approved variants; do not present invented expressions or lockups as approved identity.
- Inspect representative changed screens/assets when visuals are in scope. Check readability, contrast, focus, and states against the project's accessibility standard. If none exists, flag the gap and identify any external standard used.
- Check kit/download mirrors and design-system references when affected.

## Findings
Report actionable findings as `severity | location | violated source | user impact | smallest fix`. Use the project's severity scale; otherwise separate critical misuse or misleading claims, substantive inconsistencies, and optional polish. Cite evidence; do not turn taste into a violation. Distinguish source conflicts from implementation defects.

For a requested targeted review, report findings or a short pass with sources and scope. State any unverified portion explicitly. Avoid duplicate PR comments and boilerplate on unrelated changes. A skill reference is advisory guidance, not proof that every tool loaded it. Do not claim enforcement or universal invocation without testing it.

## Adoption and audit backstop
Link from existing versioned authoring/reviewer entrypoints, using supported path-scoping features only after verifying the actual tools. Otherwise use a concise conditional instruction plus semantic diff review. Record a project owner and canonical source pointers. Validate with a relevant edit that invokes the skill, an unrelated edit that skips it, and an embedded visible-string edit that is not missed. Do not add a CI gate unless separately requested.

A periodic audit is optional and requires an authorized schedule. If requested, inspect only relevant changes since the last successful reviewed commit, preserve the baseline on failures, group findings, and stay quiet when there is nothing actionable. A public-repository audit must not copy private source/assets or expose private findings. Restrict it to public inputs unless private access and output handling are separately authorized. Keep private product review in its existing private environment. Do not publish or send findings without authorization.

When only proposing an audit, describe its scope and tradeoffs; do not silently schedule it.

## blowhorn.ai project configuration

Public sources in this repository. Cite these files. Do not invent rules, and do not copy material from outside this public repo.

| What | Path |
|---|---|
| Layout and copy rules | `DESIGN.md` |
| Brand page layout | `layouts/brand.html`, `layouts/brand.md`, `layouts/_partials/brand-css.html` |
| Brand page content | `content/en/brand/_index.md` |
| Brand color data | `data/brand_colors.json` |
| Logos, mascot, fonts, token file | `static/assets/brand/` (`tokens.json`, `logo/`, `mascot/`, `fonts/`) |
| Downloadable kits | `static/brand/blowhorn-brand-kit.zip`, `static/brand/blowhorn-logo-kit.zip` |
| CSS tokens | `assets/css/site.css` (values from `static/assets/brand/tokens.json`) |
| Brand page script | `assets/js/brand.js` |

Reuse the `ux-audit` skill (`.agents/skills/ux-audit/`) for layout audits. Do not restate its rules here.

Candidate paths: `content/`, `data/`, `layouts/`, and brand assets under `static/assets/brand/` and `static/brand/`. Treat a path as a selection hint. Inspect the actual diff, including visible text in code.

No CI job or PR checkbox; skip unrelated diffs silently.
