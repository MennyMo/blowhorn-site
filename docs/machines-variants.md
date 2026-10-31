# Home page computers section variants

The home page's How it works section (the orders section, `#how`) shows one of
four designs for how computers join the fleet. The designs, their headlines and
subheads come from [`data/machines.json`](../data/machines.json), which must
validate against [`schemas/machines.schema.json`](../schemas/machines.schema.json)
(`make check-schemas`, part of `make site-check` and so of CI). Each variant has
an `id`, a `headline`, a `subhead` and an optional reviewer `note`. The designs
were brainstormed on the Landing concepts page of the Blowhorn Figma file.

## The rotation

`rotation` is the config object. `rotation.mode` is `interval` (production) or
`utc-day`. `rotation.ids` lists the designs that take turns, in order. Omit
`ids` to rotate every variant. Variants not listed stay in the file for later.

Production rotates these four, one per hour:

1. `muster`: "Every computer you own is a recruit." Roll call beside the
   formation. Default and fallback.
2. `battalion-map`: "Your squad, on one map." The fleet as units around
   HQ, a teammate's computer included, with a reports feed.
3. `one-thunder`: "Many voices. One thunder." Teammates and computers wired
   into the Major's single call out to every platform.
4. `call-to-arms`: "From one recruit to a full squad." The four-beat
   storyboard (Enlist, Muster, Rally, Thunder); the beats play in
   sequence, with a Replay button.

At page load each visitor gets one of

```
rotation.ids[floor(now / intervalSeconds) % length]        # mode: interval
rotation.ids[floor(UTC days since the epoch) % length]    # mode: utc-day
```

`interval` needs `rotation.intervalSeconds` (a positive integer); production
uses 3600, so every visitor in the same hour sees the same design and the
turn happens on the hour. The pick happens once: the design never changes
while someone is reading the page.

## How it renders

- [`layouts/_partials/machines-rotation.html`](../layouts/_partials/machines-rotation.html)
  reads the data file and fails the build if `rotation.ids` names an unknown
  variant or if `default` is not in the rotating ids. Mode and
  `intervalSeconds` are schema-checked (`make check-schemas`).
- [`layouts/_partials/home/signal.html`](../layouts/_partials/home/signal.html)
  renders the section once: one `h2` and one intro paragraph, each holding a
  `<span data-machines-only="<id>">` per rotating design, then one panel per
  design from [`layouts/_partials/home/machines/`](../layouts/_partials/home/machines/).
- [`layouts/_partials/machines-rotation-head.html`](../layouts/_partials/machines-rotation-head.html),
  in the page's `head`, carries a few lines of CSS that hide every span and
  panel except the picked one, and a few lines of inline script that pick the
  design and set `data-machines` on `<html>`. It runs before the body is
  parsed, so the first paint already shows the right design: no flash and no
  layout shift.
- Hidden copy and panels are `display: none`, so screen readers get only the
  visible design and the page keeps one `#how` heading.
- Without JavaScript the attribute is never set and the CSS shows `default`.

## Animations

[`assets/js/machines.js`](../assets/js/machines.js) (bundled into the home
page's `home-signal.js`) animates only the design the rotation picked, in the
spirit of the Reveille army board ([`assets/js/army.js`](../assets/js/army.js)).
Styles are under "Machines animations" in `assets/css/home-signal.css` and
reuse the Reveille keyframes in `assets/css/site.css`: `army-enlist` (the
enlist pop), `wave-pulse` (rings), `stage-bark` (the Major) and `army-shout`
(his bubble).

- **Muster:** recruits fall into the formation, the roll call fills, and the
  strength counts up. The two Enlist buttons (the `+` tile and the roll call's
  `+ Enlist`) add a recruit on the page, up to 23, and the Major answers in
  his bubble. The "Enlist a computer" button still goes to the download page.
- **Battalion Map:** units ping in, reports run the dashed lines to HQ, HQ
  rings, and the reports feed ticks a new report every 2.6 s.
- **One Thunder:** dotted voice lines flow from every teammate and computer
  into the Major, rings leave the bullhorn, and each platform tile lights as
  the call lands. The logos themselves never move (Bluesky's and X's brand
  rules).
- **Call to Arms:** the four beats play once along the timeline when the
  section comes into view; Replay plays them again.

The panel gets `is-armed` (start state) when the script runs and `is-live`
once a quarter of it (or 40% of the screen) is in view. Looping motion
pauses (`is-paused`) when the panel leaves the screen. Under
`prefers-reduced-motion` nothing is armed: every design rests fully drawn,
and Muster's Enlist buttons still work, without motion. Without JavaScript
the static designs show, with no buttons that do nothing.

## Adding a design

1. Add the variant to `variants` in `data/machines.json`.
2. Add its id to `rotation.ids`.
3. Add its panel as `layouts/_partials/home/machines/<id>.html` (a `div` with
   `data-machines-only="<id>"`) and include it in the `#how` section of
   `layouts/_partials/home/signal.html`. Panel styles live under "How it
   works" in `assets/css/home-signal.css`; use the shared tokens and the
   official cast art in `static/assets/brand/cast/`, never a redrawn Major.

## Review URLs

`?machines=<n>` (1-based position in `rotation.ids`) or `?machines=<id>`
forces a design, for example `https://blowhorn.ai/?machines=2` or
`http://localhost:1313/?machines=one-thunder` on a local `make site`.
Anything else is ignored and the time rule applies.

No analytics or third-party script may be added to measure the designs
(`check-third-party`).
