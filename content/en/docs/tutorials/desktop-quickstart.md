---
title: "Getting started with the desktop app"
description: "Install the app, connect Chrome, and preview your first post without publishing."
weight: 20
draft: true
---


In this tutorial you will install the Blowhorn menu-bar console and use it
to inspect a run - without letting it publish anything. It takes about
fifteen minutes.

You need macOS 13 or newer and a browser signed in to GitHub. The app
carries its own engine, so you need no checkout of this repository and no
Python.

## 1. Install the app {#section-1-install-the-app}

The app ships as one universal DMG that runs on Apple silicon and Intel Macs.

1. Open the [download page at blowhorn.ai](https://blowhorn.ai/download/)
   in your browser.
2. Download `Blowhorn-mac.dmg`, the newest release.
3. Open the DMG and drag `Blowhorn.app` to `/Applications`.

The release is Developer ID signed and notarized, so the first time you open
it macOS asks once whether to open an app downloaded from the internet. Choose
**Open**.

## 2. Open it and meet the Setup screen {#section-2-open-it-and-meet-the-setup-screen}

Launch `Blowhorn.app`. It runs the engine it carries and never looks for a
checkout of this repository. If that engine can't start, it opens on
**Setup**. Otherwise the guided setup opens
first: finish it ([Set up Blowhorn at first muster](/docs/how-to/set-up/first-muster-setup/)),
then choose **run setup again** at the bottom of Settings. Setup shows four
checks, each either `ok` or offering the action that fixes it.

Work down the activities:

1. **Blowhorn folder** - `bundled in the app`. If it asks you to move
   Blowhorn to Applications, do that and open it again; see
   [Fix Blowhorn when its engine won't start](/docs/how-to/troubleshoot/engine-wont-start/).
2. **helper tools** - its Python ships in the app, so this activity has
   nothing to install.
3. **organization connection** - the connection to your account. When it warns, it
   shows why (for example `Not signed in to Blowhorn. Sign in to continue.`) and a **test connection**
   button; sign in from the app, then click **test connection** to check again.
4. **this computer on watch** - nothing to do here: once the activities above are ok
   the app registers the service itself, and this activity only reports it. You do
   not need it to finish this tutorial.

Each probe is bounded by a 20-second timeout (60 s for your account's full **test
connection**), so an activity that cannot answer will tell you rather than hang.

## 3. Turn on dry-run before anything else {#section-3-turn-on-dry-run-before-anything-else}

Still on the Setup screen, find the **preview only by default** switch below the
four activities and turn it **on**.

This is the important step of this tutorial. With it on, runs you start from
the app rehearse instead of publishing. Turn it off later, deliberately, when
you want the app to post for real.

Now click **open console**.

## 4. Look at the queue {#section-4-look-at-the-queue}

The console's "posts" screen reads the same content queue the CLI does - it
runs `blowhorn content list --json` once and its "ready" tab shows the activities that
are due, each with who would post it (the same selection
`blowhorn post --check-queue` prints).

Nothing here publishes on its own. The screen reads on no timer - it shows you
what it read when it read it.

## 5. Find the app in your menu bar {#section-5-find-the-app-in-your-menu-bar}

Close the console window. The app is still running: its icon sits in the menu
bar, and clicking it opens the popover with the service state, the next
scheduled tick, and the content about to post: **ready to post** lists the activities
some profile would post on its next run - its count is the `pending` beside
content in the console's rail - and **scheduled to post** lists what waits for
a later `Promote On`.

Installing the app is what installed the background service, and quitting the
app does **not** stop it - the switch **keep this computer on watch after
quit**, on by default, is the one thing that decides that. With it off,
quitting stops the service (asking you first if a pass is in flight), and the
next launch starts it again. See
[What runs when the app is closed](/docs/explanation/distribution/).

## What you did

You installed the console from its DMG, made every run from the app a rehearsal by
default, and read the queue.

## Next

- [The Blowhorn app, screen by screen](/docs/reference/use-the-desktop-app/) -
  every screen you just used.
- [Schedule a job](/docs/how-to/schedule/schedule-a-job/) - when you want the
  scheduler the Setup screen offered.
- [What runs when the app is closed](/docs/explanation/distribution/) - the
  background service, quitting, and updates.
