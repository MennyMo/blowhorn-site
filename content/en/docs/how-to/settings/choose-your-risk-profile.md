---
title: "Choose your Risk Profile"
description: "Your pace. Your risk. Your call. What cautious, standard and brisk change in your day, and which one to pick."
weight: 25
---

Your Risk Profile is one choice for how risky and how fast Blowhorn
runs: cautious, standard (the default) or brisk. It sets pace, pointer
movement, caps, spacing, quiet hours, outreach, the pause after a
sign-in challenge, retries and how much runs at once, together. The
headline is ownership-first - "Your pace. Your risk. Your call." - and
the formal name stays Risk Profile: the tradeoff really is detection
and ban risk against speed, and it is the same term the CLI, the config
file and the reference use.

Choose it in the app with the slider at the top of Settings - a
colour-graded track from cautious (slow end) to brisk (fast end), with
a consequence readout under it, one row per dial, each row's info
button linking to that dial's anchor. The same mode shows on Home as
a pill that opens Settings, and as a mini-slider in the menu-bar
popover; changing it anywhere changes it everywhere. Or use
`blowhorn risk set cautious` (add `--profile` to store it on one
profile, `--platform` for one platform). `blowhorn risk show` says
which preset is in effect and where it came from. Any single dial you set yourself wins over the
preset for that dial, and the rest of the preset still applies around
it; a profile with a dial set outside the preset is a custom profile,
not a fourth preset you can pick.

To adjust the dials yourself, open Customise dials in Settings: start
from the preset, then change the per-platform pace, your daily caps per
platform and action, and the typing and pointer timing. The header
reads "Custom, based on Standard, 3 dials changed" once dials move,
and Reset to preset puts every dial back. No dial may exceed a
built-in ceiling: your own cap can only lower a ceiling, never raise
it. Two dials carry a driver note on the card: pauses and mistakes
run on the Playwright driver only. The extension driver sends one key
per message and runs no pause plan, so on that driver it types with
the shaped delay from the delay band and no pauses or corrections.
The full values are in the
[configuration reference](/docs/reference/configuration/#risk-profile-presets),
with a stable anchor per dial in
[Risk Profile dials](/docs/reference/configuration/#risk-profile-dials).

## Cautious: one thing at a time, nights off

Pick cautious for a new account, a new computer, or an unattended run
you will not be watching.

- **Between actions:** at least 15 minutes, plus a random wait of up to
  15 minutes, between two public actions on one platform for one
  profile. A day of posting is therefore a slow trickle, not a burst.
- **How much per day:** a quarter of each platform's built-in ceiling.
  On LinkedIn that is 2 posts and 10 comments a day (before any cap
  you set yourself); on X it is 12 posts a day. Your own daily caps can
  only take these lower.
- **Nights:** nothing public from 22:00 to 07:00 local time. A due
  activity inside those hours waits until morning; it is not failed.
- **After a challenge:** if a platform shows a CAPTCHA, checkpoint or
  restriction page, that profile on that platform is held for 72 hours
  from the last such record.
- **Outreach:** off entirely - no connects, invites or follows.
- **At once:** at most 1 run, and one profile at a time on a platform.
  A second run is refused and names your Cautious profile; its
  activities stay queued.
- **Retries:** a failed scheduled job is not retried.

## Standard: today's behaviour, with the guardrails on

Standard is the built-in default, and the right choice when an account
is established and you want Blowhorn to behave the way it always has,
with the Risk Profile guardrails explicit rather than new.

- **Between actions:** no minimum spacing; pace still shapes typing
  cadence and the random pauses between actions.
- **How much per day:** the full built-in ceiling. On LinkedIn that is
  10 posts and 40 comments a day; on X it is 50 posts a day, before
  any cap you set yourself or a warmup ramp.
- **Nights:** no preset quiet hours. A quiet window you name yourself
  with `defaults.quiet_hours` still holds scheduled claims.
- **After a challenge:** the profile on that platform is held for 24
  hours.
- **Outreach:** on for established platforms, off on platforms still
  being built (Facebook, Instagram, TikTok, YouTube).
- **At once:** one profile at a time on a platform, and no preset limit
  on runs overall. Setting `defaults.concurrency.max_runs` adds one.
- **Retries:** a failed scheduled job is not retried.

## Brisk: fast, while you watch

Pick brisk for an established account you are watching, when you want
the most throughput and accept the most exposure.

- **Between actions:** no minimum spacing, and the fast pace.
- **How much per day:** the full built-in ceiling, same as standard -
  brisk does not raise any ceiling, it only removes cautious's
  quarter-share, quiet hours, spacing and outreach limits.
- **Nights:** no preset quiet hours.
- **After a challenge:** the profile on that platform is held for 12
  hours - the shortest pause, so a challenge is the place brisk costs
  you the most caution.
- **Outreach:** on everywhere, including platforms still being built.
- **At once:** different profiles may share a platform, and no preset
  limit on runs overall. One profile is still held to one run on a
  platform.
- **Retries:** a failed scheduled job gets one retry. A login is never
  retried, and a retry is never granted for an unknown outcome.

## A new profile warms up cautious, whatever you chose

A new profile or a new Mac runs cautious for scheduled jobs until it
has history - 14 days, whatever preset you picked. Its caps ramp over
those 14 days, from about a quarter of cautious's caps on day one
(about 1 LinkedIn post a day) to cautious's full caps by day 14, and
only then does your chosen preset take over. A profile idle longer
than the 15-day ledger window warms up again. A run you start yourself
is not held by the warmup, only warned about, and it follows your
chosen preset's caps, quiet hours and outreach.

## If you are still unsure

- New account, or you will not watch it: cautious.
- Established account, normal use: standard.
- Established account, you are watching, and you want the most done
  today: brisk.
- One account needs to be slower than the rest: set that profile or
  platform cautious, and leave the rest alone - the choice is per
  profile and per platform, not only computer-wide.

## One activity on its own preset

One recurring activity can run cautious while everything else on the
same profile and platform runs standard: open the activity, set
**Risk profile** (blank means inherit, exactly as before), and save.
From the terminal the same value is `risk_profile=cautious` in the
activity's params. The activity's detail then shows the preset and
where it came from (`Cautious · this activity`, or `Cautious ·
inherits: LinkedIn × work profile`), and while the profile is warming
it also says what the tick enforces (`warming: runs Cautious for
now`). An activity without one profile and one platform names no
single preset; its targets resolve their own. For a single run you
start by hand, `blowhorn --risk-profile cautious post ...` overrides
everything for that run only.

## Related

- [Configuration reference](/docs/reference/configuration/#risk-profile-presets) - every dial, every preset value.
- [Risk Profile dials](/docs/reference/configuration/#risk-profile-dials) - one anchor per dial, for the desktop info buttons.
- [You're in control](/docs/explanation/youre-in-control/#your-risk-profile) - the Risk Profile among every safety control.
- [How Blowhorn paces itself](/docs/explanation/reliability-and-anti-bot-design/) - measured pacing and the no-retry rule.
