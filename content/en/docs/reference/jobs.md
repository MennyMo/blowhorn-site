---
title: "Job options and schedules"
description: "Schedule activities, recurrence words, driver mode, and the three pause scopes."
weight: 214
---


What a schedule activity holds, when it runs, and what keeps it from
running. This page describes; the steps live in the how-to guides
linked under Related.

A pass runs every ten minutes and claims the activities that are due. Several
computers sharing one store share the queue: a running activity carries a lease,
and an activity whose lease lapsed is reclaimable by the next pass.

## The activity

| Field | Means |
|---|---|
| Command | What the pass runs: `post` and the other schedulable commands (`source` is not schedulable) |
| Platforms | Activity filter, not a posting target: which activities the command reads |
| Profiles | Which profiles the run acts as |
| Recurrence | When the activity comes due again |
| Driver mode | How the run reaches Google Chrome: `default`, `extension`, `extension-classic`, `extension-background`, `cdp`, or `persistent` |
| Status | Where the activity stands; `running` is a lease, never a lock |

`blowhorn schedule list` shows each activity and whether it is due.
`blowhorn schedule get` returns one activity with all fields.
`blowhorn schedule upsert` creates or updates an activity from a JSON
payload (`--activity` names the activity; `--expected-fingerprint` rejects the
write when the activity changed underneath you). An update that gives a
completed or failed activity a new `Next Run At`, or changes its `Run At`,
schedules it again on the same activity: `Status` becomes `scheduled` and
`Retry Count` 0, so it gets its full `Max Retries` again, and its last run
and last error are kept. Raising `Max Retries` alone does not (see
[Schedule a job](/docs/how-to/schedule/schedule-a-job/)). `blowhorn schedule delete`
removes an activity by number. `blowhorn schedule validate` checks every activity
against the schema. `blowhorn schedule bootstrap` previews or writes a
starter set. `blowhorn schedule trigger-now` forces one activity to run
immediately instead of waiting for the pass.

## Recurrence

| Word | Means |
|---|---|
| `once`, `none`, or blank | Runs one time, then never again |
| `hourly` | Every hour |
| `daily` | Every day |
| `weekly` | Every week |
| `monthly` | Every 30 days |
| `every:N` | Every N minutes |

Anything else is refused as an unsupported recurrence.

## Driver mode

`default` follows the same precedence every run follows: the
`--chrome-launch` flag, then the job's own mode, then the configured
default, which is the extension. Naming `extension`, `cdp`, or
`persistent` pins the job to that driver. `extension-classic` and
`extension-background` pin the job to the extension and set its
[extension mode](/docs/reference/chrome/#extension-mode-classic-or-background) for that
job, outranking your account setting; a tick forced to `extension` with
`--chrome-launch` keeps that mode. A job pinned to a driver that
cannot do the work is refused by name before anything opens.

## Risk Profile

An activity may carry its own Risk Profile: set the `Risk Profile`
column to `cautious`, `standard` or `brisk` (or write
`risk_profile=cautious` in its Params), and that activity runs that
preset end to end (pace, caps, quiet hours and the pause after a
sign-in challenge) while the same profile on the same platform runs
its usual preset everywhere else. Leave it blank and the activity
inherits the profile's preset, exactly as before. A hold or a run
report names the source as `schedule` when the activity's own setting
decided it. `blowhorn schedule list` shows each activity's own setting,
the preset it effectively runs and where that preset came from. The
app's activity editor and drawer show the same column as **rules of
engagement**, with `cautious` as Safety on, `standard` as Weapons tight
and `brisk` as Weapons free; the stored value does not change.

## Pause scopes

An activity is claimed only when none of the three scopes says paused:

| Scope | Pauses | Lifted by |
|---|---|---|
| `machine` | This computer only, in `.blowhorn.pause.json` | `blowhorn schedule resume` on this computer |
| `all` | Every computer sharing your account | Resuming the organization-wide pause |
| `activity` | One scheduled activity, everywhere | Resuming that activity |

`blowhorn schedule pause` pauses; `blowhorn schedule resume` resumes.
`blowhorn schedule status` shows whether processing is paused and the
last tick's heartbeat. `blowhorn schedule why <activity>` explains why one
activity has or has not run on this computer. Quitting the app pauses
nothing: the file, the organization-wide pause, and the activity pauses keep
exactly what they said.

## Related

- [Schedule a job](/docs/how-to/schedule/schedule-a-job/) - create, pause, and resume jobs.
- [The Blowhorn app, screen by screen](/docs/reference/use-the-desktop-app/) - the Routines view of Activity and the popover boards.
- [Settings and configuration](/docs/reference/configuration/) - the launch-mode default a job inherits.
- [How scheduling works](/docs/explanation/scheduling/) - passes, leases, and why an activity waited.
- [CLI reference](/docs/reference/cli/) - the schedule commands.
