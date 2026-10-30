---
title: "Change your defaults"
description: "Set pace, excluded profiles, dry-run default, notifications and logs, in the app or the config file."
weight: 170
aliases: [/docs/how-to/configure-blowhorn/]
---


Set the defaults every run starts from: pace, excluded profiles, dry-run,
notifications and logs. Change them in the app, or with `blowhorn config set`
for the whole checkout. In the app, pace, daily caps, quiet hours, how much
runs at once, approval and dry fire are on the Posture screen; the rest
are on Settings' **Advanced** page.

## See what is in effect

```bash
blowhorn config show
blowhorn config show --json
```

## Change a default

```bash
blowhorn config set defaults.pace slow
blowhorn config set defaults.exclude ada,kate
blowhorn config set defaults.dry_run true
```

A flag beats an environment variable, which beats `.blowhorn.yaml` in the
directory you run from, which beats the built-in. Every option and its
environment variable is listed in the configuration reference.

## Slow one platform down

Pace is per platform when you want it to be: X and LinkedIn can run slow
while Slack and GitHub run at the normal pace.

```bash
blowhorn config set defaults.pace_by_platform.x slow
blowhorn config set defaults.pace_by_platform.linkedin slow
blowhorn config set defaults.pace normal
```

or, in `.blowhorn.yaml`:

```yaml
defaults:
  pace: normal
  pace_by_platform:
    x: slow
    linkedin: slow
    hn: 1.5
```

A platform with no entry runs at `defaults.pace`. A `--pace` flag (or
`BLOWHORN_PACE`) covers every platform for that run, so a one-off run can
override the standing per-platform paces. `blowhorn config show --json`
reports the effective pace for every platform and which setting supplied
it.

In the app, the **by platform** table on the Posture screen shows the same
per-platform paces: pick a pace for one platform there (or **a number…** for
a multiplier such as 1.5), or press × to run at the pace again, then **save
limits**. While `BLOWHORN_PACE` is set, the table says that pace is in effect
on every platform.

## Cap a day's actions

Every platform and action has a built-in daily ceiling. The **by platform**
table on the Posture screen shows each one as the empty box's placeholder:
type a lower cap of your own there, or press × to go back to the ceiling,
then **save limits**. A cap of your own can only lower the ceiling, never
raise it.

```bash
blowhorn config set defaults.caps.x.post_per_day 3
```

To read one option and learn which document holds it:

```bash
blowhorn config get defaults.profile
```

Blowhorn reaches your account through `blowhorn auth login`, not through an
option. The one store option is `defaults.store.organization`, which picks the
organization Blowhorn uses when the sign-in did not choose one.

## Choose where output is written

```bash
blowhorn post --profile ada --log-dir ./logs      # this run only
export BLOWHORN_LOG_DIR=./logs                    # this shell
blowhorn config set defaults.logs.directory ./logs
```

## Choose how long the daily logs are kept

```bash
blowhorn config set defaults.logs.retention_days 7     # keep a week
blowhorn config set defaults.logs.retention_days 0     # keep every daily log
export BLOWHORN_LOG_RETENTION_DAYS=7                   # this shell
```

Every run deletes daily logs older than that (30 days if you set nothing),
judged by the date in the file name. Nothing else in the directory is pruned.

## Related

- [Choose how Blowhorn reaches Chrome](/docs/how-to/settings/launch-mode/) - the launch and driver settings these defaults sit above
- [Schedule a job](/docs/how-to/schedule/schedule-a-job/) - per-job parameters that beat these defaults
- [Review what ran](/docs/how-to/measure/review-runs/) - read the logs these settings keep
- [Choose your rules of engagement](/docs/how-to/settings/choose-your-rules-of-engagement/) - the preset these dials start from, and the Posture screen
- [You're in control](/docs/explanation/youre-in-control/) - how pace and dry run fit with the built-in limits
