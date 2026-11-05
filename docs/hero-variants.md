# Home page hero variants

The home page hero's headline, tagline and illustration come from [`data/hero.json`](../data/hero.json),
which must validate against [`schemas/hero.schema.json`](../schemas/hero.schema.json)
(`make check-schemas`, part of `make site-check` and so of CI). Each variant has an `id`,
a `headline` (up to 80 characters), an optional `art` (`stage` or `fan`, default `stage`),
the numbers of the canonical differentiators it rests on and an optional reviewer `note`.
Copy may only state what those differentiators allow, in their wording rules.

## The tagline

`tagline` is one top-level line, the plain description of what Blowhorn is, shown
under the headline for every hero:

> Social media management for you and your AI agents.

It is sentence case, up to 80 characters, and sits on one line on desktop; on phones
it wraps in balanced lines (`.hero-tagline` in `assets/css/site.css`). It is rendered
once, not per hero, so switching heroes never changes it.

A variant may still carry a `subhead` (a longer plain-words description) and an
`identification` line ("If this is you: ..."). Both are optional and neither is rendered
in the hero anymore; they stay in the data for reference and for the issue #254 heroes.
The `default` variant's `subhead`, when it has one, still feeds the meta, Open Graph,
Twitter and JSON-LD descriptions (the tagline stands in when it does not).

## The rotation

`rotation` is the config object. `rotation.mode` is `utc-day` (production) or
`interval`. `rotation.ids` lists the heroes that take turns, in order. Omit `ids`
to rotate every variant. Variants not listed never rotate, but still render after the
rotating ones, so `?hero=<id>` reaches them for review (`?hero=<n>` counts rotating heroes only).

Production rotates 23 heroes, one per UTC day: the five AI hybrid heroes first (Yi,
2026-10-20), then the 18 round 2 heroes. With 23 ids a given hero comes back every 23
days. The five AI hybrid heroes:

1. `plug-in-ai`: "Automate your social voice. Plug in AI anytime."
2. `scripted-ai-ready`: "Scripted where it counts. AI where it helps." Default and fallback (Yi, 2026-10-20).
3. `same-rules`: "You post. Your agent posts. Same rules."
4. `ai-optional`: "Your voice, automated. AI optional, never in charge."
5. `human-or-ai`: "One queue. Every profile. Human or AI."

The 18 round 2 heroes (Blowhorn Marketing, 2026-10-27, approved by Lee), in rotation
order, have a headline only, no subhead and no `cta`, so their secondary button is
"See how it works":

| id | Headline |
| --- | --- |
| `r2-sound-wave` | Make a sound wave, not a ripple. |
| `r2-advocacy` | Employee advocacy, minus the enterprise invoice. |
| `r2-whisper` | The algorithm can't hear a whisper. |
| `r2-ovation` | Your launch deserves an ovation, not a pity like. |
| `r2-password` | Your password called. It wants to stay home. |
| `r2-scarecrows` | Bought likes are scarecrows with thumbs up. |
| `r2-manners` | Automation with manners. |
| `r2-backup` | Not a bot. Just you, with backup. |
| `r2-every-computer` | Every computer you own, reporting for duty. |
| `r2-army-marches` | Close your laptop. The army keeps marching. |
| `r2-halt` | Second thoughts? One button halts the whole army. |
| `r2-juggling` | Juggling clients? Put the balls down. |
| `r2-agency-name` | Your agency's name on it. Our army behind it. |
| `r2-remote-team` | Remote team. One battle plan. Everyone keeps their own keys. |
| `r2-no-meter` | No meter. No credits. No rationing. |
| `r2-per-breath` | Social tools charge per seat, per post, per breath. |
| `r2-crickets` | Built by a tiny team that got tired of crickets. |
| `r2-ai-orders` | Let your AI give the orders. Blowhorn follows them. |

Hero copy says computer, never Mac, and browser, never Chrome (Lee, 2026-10-28).
`make check-naming` enforces the Mac half, with no exceptions.

`r2-remote-team` is the longest headline: check it at 1440 and 390 px wide after any
hero type or layout change (four lines on both, no overflow).

The earlier five (`not-a-bot`, `real-you`, `your-fleet`, `sound-wave`,
`own-your-voice`) stay in the file outside the rotation, so their `?hero=` links
still work.

Each variant may set `cta` (`label` and `href`, a site path or an on-page
anchor): its secondary button beside Download. Without it the button reads
"See how it works" and goes to `#how`. A path that is not a page fails the build.

The platforms section headline lives in `data/integrations.json` (`headline`).
It is not a hero. The old line "Say it once. Say it everywhere." stays on the
Reveille homepage only.

At page load each visitor gets one of

```
rotation.ids[floor(UTC days since the epoch) % length]   # mode: utc-day
rotation.ids[floor(now / intervalSeconds) % length]      # mode: interval
```

`utc-day` is whole UTC days since the Unix epoch, so every visitor sees the same
hero on the same day and the turn happens at 00:00 UTC. `interval` needs
`rotation.intervalSeconds` (a positive integer). The pick happens once: the hero
never changes while someone is reading the page.

## How it renders

- [`layouts/_partials/hero-rotation.html`](../layouts/_partials/hero-rotation.html) reads
  the data file and fails the build if `rotation.ids` names an unknown variant
  or if `default` is not in the rotating ids. Mode and `intervalSeconds` are
  schema-checked (`make check-schemas`).
- [`layouts/home.html`](../layouts/home.html) renders the hero once: one `h1` with a
  `<span data-hero-only="<id>">` per hero inside it, the one tagline, the shared label,
  buttons and social proof, and one figure per art used by the rotation, each from its own
  partial in [`layouts/_partials/hero-art/`](../layouts/_partials/hero-art/).
- [`layouts/_partials/hero-rotation-head.html`](../layouts/_partials/hero-rotation-head.html),
  in the page's `head`, carries a few lines of CSS that hide every span and figure except
  the picked one, and a few lines of inline script that pick the hero and set
  `data-hero` and `data-hero-art` on `<html>`. It runs before the body is parsed, so the
  first paint already shows the right hero: no flash and no layout shift.
- Hidden copy and art are `display: none`, so screen readers get only the visible hero
  and the page has one `h1`.
- Without JavaScript the attributes are never set and the CSS shows `default`.
  `default` also feeds the meta, Open Graph, Twitter and JSON-LD descriptions
  ([`layouts/_partials/hero-variant.html`](../layouts/_partials/hero-variant.html)), so
  crawlers and social previews always get it. `content/en/_index.md`'s `description` is
  front matter and does not follow the data file: update it by hand when the default
  changes.
- While the fan is the hero, the Platforms section hides its own copy of the fan
  (`.platforms-fan` in `assets/css/site.css`), so it never appears twice.
- Each art keeps its own motion and `prefers-reduced-motion` rules. Switching heroes adds
  no transition.

## Hero media

The hero visual comes from `media` in `data/hero.json`
(schema: `schemas/hero.schema.json`). `media.default` names it for every
hero: `video` (the hero film) or `demo` (the interactive pseudo-app demo
from `data/hero_demo.json`). A hero can set its own `"media": "demo"` or
`"media": "video"` to override it, and `?hero=<id>` picks the hero and so
its media. The pre-paint picker sets `data-hero-media` on `<html>` and only
the matching `[data-hero-media-only]` visual shows; no-JS visitors get the
default hero's.

`media.video` holds the film: `mp4` (H.264, faststart) and `webm` (VP9) under
`static/assets/video/`, a `poster`, its `width` and `height`, and an
accessible `label` and `description`. Captions are burned into the picture.
The default is the Battalion Thunder film (source:
blowhorn `marketing/videos/blowhorn-battalion-thunder`), 1080p,
about 2.1 MB MP4 and 2.2 MB WebM.

`media.video.placement` is `inline-expand` (the only placement): the film
sits small in the hero beside the headline, tagline and calls to action
(below them on phones), on its poster with a Play the film button.
`?hero=<id>` still swaps the copy. `assets/js/hero-video.js` then:

- grows the frame in one FLIP motion from its spot to 90% of the window
  width (all of it at 640 px and under), centered and fitted to the window
  height, as a modal dialog (`role="dialog"`, `aria-modal`) over a dimmed
  backdrop, and plays it once it has grown;
- traps focus in the dialog (Sound, Pause, Close) and locks page scroll;
- closes on Escape, a backdrop click or Close: it pauses the film, shrinks
  it back to exactly its spot and returns focus to the Play button (now
  Resume the film).

Under `prefers-reduced-motion: reduce` it opens and closes without the
motion. Without JavaScript the native video controls show inline.

`media.video.playback` (schema-checked): `autoplay` is always `false`;
`loop` replays it from the start; `sound` starts it with sound on Play (the
click is the user gesture browsers need for audio); `end` is `poster` or
`last-frame` when it ends without looping, with a Watch again button in
the dialog. Production is no loop, sound on, `end: poster`.

To re-encode after a new render:

```sh
ffmpeg -i film.mp4 -c:v libx264 -profile:v high -crf 25 -tune animation -preset slow -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 64k -ac 1 static/assets/video/battalion-thunder.mp4
ffmpeg -i film.mp4 -c:v libvpx-vp9 -crf 38 -b:v 0 -row-mt 1 -c:a libopus -b:a 48k -ac 1 static/assets/video/battalion-thunder.webm
```

The poster is a still, not a frame of the film:
`static/assets/video/battalion-thunder-poster-megaphone.webp`, 1920 x 1080,
in the Locked-6 cartoon style. Major Blowhorn sounds off from a rock while the
General, Recruit Chicks on a MacBook and an iMac, and the Sleeper Cell fall in.
The chicks' screens carry the Blowhorn icon. Keep the middle of any poster
clear, since the Play the film button sits there.

## Adding a hero

1. Add the variant to `variants` (with `art` if it is not the stage).
2. Add its id to `rotation.ids`.
3. For a new illustration, add `layouts/_partials/hero-art/<art>.html` (a `figure` with
   `class="hero-art"` and `data-hero-art-only="<art>"`, every id in it unique on the
   page) and add `<art>` to the `art` enum in the schema.

## Review URLs

`?hero=<n>` (1-based position in `rotation.ids`) or `?hero=<id>` (any id in
`rotation.ids`) forces a hero, for example `https://blowhorn.ai/?hero=2` or
`http://localhost:1313/?hero=real-you` on a local `make site`. Anything else is
ignored and the time rule applies.

## Cycling heroes by keyboard

On the home page and on `/home-reveille/`, type the letters `cycle`, in
order, to move to the next hero in place, without reloading. The order
is the full hero list (rotating heroes first, then the rest), wrapping
from the last hero back to the first. The URL is updated in place to
`?hero=<id>`, so a reload or a shared link shows the same hero.

The sequence ignores modifier keys and any typing inside a form field,
a text box, or an editable area, and it resets if more than 2 seconds
pass between letters. It is implemented in `assets/js/hero-cycle.js`,
loaded by `layouts/home.html` and `layouts/home-reveille.html`, using
the hero list the pre-paint picker exposes as `window.blowhornHeroes`
in `layouts/_partials/hero-rotation-head.html`.

## The 12 heroes from issue #254

The 12 quippy, sarcastic heroes from blowhorn-ai/blowhorn-site issue #254 are
in `data/hero.json`, outside the production rotation, so the daily rotation and
the default hero are unchanged. Their ids, in issue order, are `copy-paste`,
`seven-tabs`, `congratulations-posted`, `password-cookie-2fa`, `not-a-vendor`,
`not-rental`, `nine-likes`, `no-begging`, `say-it-like-you-mean-it`,
`hundred-seats`, `298-stack` and `too-small-for-demo`. Each carries its
plain-words subhead and its self-identification line (`identification` in the
data file). Neither is rendered: like every hero, they show the tagline.
To promote one to production, add its id to `rotation.ids`; do not change
`default` unless the no-JavaScript, crawler and social-preview hero should
change with it.

## Easter egg hotkey

Press `h` on the home page to advance to the next rendered hero, in render
order (rotating heroes first, then the rest, including the 12 from issue
#254). Press Shift+h to go back one. The hotkey is in
`layouts/_partials/hero-rotation-head.html`, so it works on the Signal home
page and the Reveille preview page, and it swaps headline, secondary button, art and media together,
because they all key off the same `data-hero` attribute. It updates
`?hero=<id>` in the address bar, so the shown hero survives a reload and can
be shared. It does nothing while typing in a form field, while a dialog is
open, or with Ctrl, Cmd or Alt held, and it announces the new headline
through a polite live region for screen readers. There is no on-page hint:
this is a reviewer tool, not part of the visitor experience. It sits
alongside the `cycle` sequence above: `h` advances and Shift+h goes back,
while `cycle` only advances.

No analytics or third-party script may be added to measure heroes (`check-third-party`).
