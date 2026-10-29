---
title: "Keep posting when the app is closed"
description: "Run scheduled passes from the background service, and quit cleanly."
weight: 153
---


Scheduled passes keep running with no window open. One background service owns
the timer and runs a pass every ten minutes, starting with one as soon as it
starts.

## Check the service

```bash
blowhorn service status
blowhorn service tick-now --follow
```

`service status` names the owner, whether the service is running, the last
pass and the pass in flight. `tick-now` asks the running service for a pass
now and watches it. In the app, the "this computer" screen shows the same state.

When this install is signed in to a Blowhorn account, one tick runs at a time. A
second `blowhorn schedule tick` or `blowhorn schedule trigger-now` while that
tick is running stops, and Blowhorn says it is already running a tick on this
install.

The owner tells you who manages it: the desktop app registered it itself, or
the command line installed it from a file. When the app owns it, the app's
setting "keep this computer on watch after quit" (on by default)
decides whether quitting stops it. Quitting with a pass in flight asks what to
do, in a small prompt in the Blowhorn window that lists what is running:

- **finish, then stop** lets the service end the pass, then stops it.
- **cancel and stop** ends the pass after the step in progress - the post being
  published, or a run that can't be interrupted safely - and the rest goes back
  to the queue. It resumes the next time Blowhorn or the service starts, and
  nothing is marked failed.
- **stay open** (or closing the prompt) changes nothing.

However the app is quit - the menu, Cmd-Q, the menu-bar icon's Quit, a quit
from another app, or a `SIGTERM`, `SIGINT` or `SIGHUP` - it stops the commands
it started, removes its menu-bar icon and exits within a few seconds. A quit by
signal (logging out, for example) has nobody to answer the prompt, so with the
setting off and a pass in flight it takes **finish, then stop**. With the
setting on, no quit of any kind touches the service.

## A separate data folder

A run that sets `BLOWHORN_USER_DATA_DIR` (a test, a packaged check, or a second
copy of the app's data) does not register, re-register, or remove the shared
background service. Scheduling on this computer runs from the normal install.
That run also leaves `~/.zshrc`, `~/.local/bin`, the app's open-at-login item,
the `blowhorn://` link handler and the installed app in `/Applications` alone.
It never reads the account you signed in with in your login Keychain, and it
keeps its own sign-in and Google Chrome folders inside its data folder. Its menu bar
icon reads `test`, and its tooltip says `Blowhorn (test)`.
It still reads the service's state, so Setup shows it, and when it quits it
stops any Chrome it started on a throwaway folder under the system temp
directory.

The normal install registers the service only after it has written `engine.json`.
Until that file exists, it waits and tries again quietly, so the service does
not start, fail, and start again.

## Install it without the app

On a computer without the desktop app:

```bash
blowhorn service install
```

`service test` validates the schedule and previews a pass the way the service
would run it. `service stop` drains the pass in flight before it stops; the
definition stays, and `service start` loads it again. `service update` brings
a file-installed definition up to date with the checkout, and only reloads
when it differs.

Every verb takes `--dry-run` to print what it would do, and `--json` for the
shape the app reads.

## Cancel a pass in flight

```bash
blowhorn service cancel
```

Cancelling stops at the next safe point, never mid-post: the activity the pass was
on returns to the queue exactly as claimed, with no retry counted, and the
next pass takes it up again. The run ledger records the pass as cancelled,
never failed.

## Related

- [Schedule a job](/docs/how-to/schedule/schedule-a-job/) - create the activities the passes run
- [Pause and resume posting](/docs/how-to/schedule/pause/) - hold claims without stopping the service
- [Find out why a job did not run](/docs/how-to/schedule/why-not-run/) - read one activity's state
- [Uninstall Blowhorn](/docs/how-to/manage/uninstall/) - remove the service for good
- [You're in control](/docs/explanation/youre-in-control/) - what an unattended run will and won't do
