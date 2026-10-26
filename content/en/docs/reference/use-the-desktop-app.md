---
title: "The Blowhorn app, screen by screen"
description: "The menu-bar popover, the console screens, Setup, Settings, and what each one does."
weight: 211
---


What each part of the Blowhorn desktop app shows and does. This page
describes; the steps live in the how-to guides linked under Related.

## The menu bar and the popover

Blowhorn lives in the menu bar. Opening it shows the popover, which has
two boards. The running board shows the scheduler, what is due now, what
is running, what needs you, and the content queue with a countdown to
the next tick. The paused board shows PAUSED with each tick-level pause
scope stated once, and the activities that would post now wait instead of
posting. Until you are signed in and the extension is ready, those boards
stay hidden, and so does any can't-reach or unknown line. Signed out, the
popover then shows the mark, the wordmark
and Quit, the recruit, Welcome to Blowhorn, the line "Open Blowhorn to sign
in and get set up. It takes about five minutes.", and one Open Blowhorn
button, which opens the console. Signed in but the extension not ready
yet, it shows Finish setting up and the same one Open Blowhorn button
instead. It shows no pause, counts, countdown,
update card or error. A store outage puts its line above the board once
the boards show. The line is the last check's word, so while it shows, the app keeps checking the store in
the background - soon after the line appears, then every two minutes -
and again whenever you open the popover, bring the console forward, or
wake the computer. When the store answers, the line clears on its own and
the next check runs straight away; you never have to relaunch the app to
clear it. **try again** on the line checks at once instead of waiting.
The console shows the same line, with the same **try again**.

The popover footer holds the pause controls and, when an update is
ready, the update card. The update downloads the new version, installs it
and relaunches the app; when it cannot, it opens the release page in your
browser. An installed Blowhorn that finds such a release when it opens also
asks in the console window, before the download, with **Download**, **Later**
and a **?** help icon;
what each does is under [Update](/docs/how-to/set-up/install-the-app/#update).

## The console

The console is the full window, reached from the popover. At the top of its
rail, **New activity** (⌘N) opens Activity with a new entry. Its list of what
an activity can do offers a blog (an organization blog) only when a
profile in your organization is opted in to it (`blowhorn schedule
destinations`); an activity already saved for one still shows and runs. Below it are four
places: **Home**, **Activity**, **Profiles** and **Performance**. Activity is
one place with three views, switched at the top of the screen: **Upcoming**
(what you want to say), **Routines** (when and where things go out) and
**History** (what Blowhorn did).

At the bottom of the rail, once you are signed in, the status line says whether
this computer is on watch. It reads "Paused since" when the pause began (the time for a pause from
today, the weekday and time within the past week, otherwise the date) with
"Nothing goes out"; "This computer isn't on watch" with the reason when its
service is stopped, not installed or turned off in System Settings; "Check
overdue on this computer" when a check is late; and "This computer is on watch"
only when none of those hold. On watch, the line under it names the next scheduled
run of an activity that is on and not paused, worded as Home words it (for example
"Next: Post on X, tomorrow at 9:00 AM"; hover for the whole line when the rail cuts it
short), or "Nothing scheduled" when no activity is due again. The countdown to the
next check is on This computer. Click the status line to open This computer. Beside it, **Pause** is one toggle: press it to pause, press it
again to turn the pause off (⌘⇧P does the same). Under the status line, the
account button (desktop v1.27.2) shows who is signed in: your Blowhorn profile photo, or
your initials, your name, and your organization and plan (for example "Acme ·
Free plan"). The organization is the one your Blowhorn session has
selected, the same one [cloud.blowhorn.ai](https://cloud.blowhorn.ai) shows, unless
`BLOWHORN_CLOUD_ORGANIZATION` names another; the plan is that organization's.
Every organization is on the Free plan unless an active subscription names another. It opens the
account menu: your name, email, organization and plan, then **Your account and
plan** (your Blowhorn account page at cloud.blowhorn.ai, in your browser), **Team** (coming
soon), **Switch organization** when you belong to more than one (it lists them
with yours checked; picking one switches your account to it right here, the same
switch cloud.blowhorn.ai makes, so your browser follows too; `blowhorn auth
switch-organization` does it from Terminal), **Settings** (⌘,), **Help and docs**, and
**Sign out**. Opening the menu refreshes your name, photo, organizations and
plan from your Blowhorn account. Signed out, the rail shows no sign-in button
and no account placeholder: the guided setup's own sign-in buttons are the way
in, and this computer's status line stays hidden. While
Blowhorn checks your account it shows a spinner; when it can't reach
Blowhorn it shows a warning dot, and its menu offers **Try again**. If
Blowhorn refuses your sign-in, the error where it appears offers
**sign in again**, which signs you back in from the app.

Each screen reads live state on open. Nothing here edits on a timer. Until
you're signed in and the extension is ready, every place but Home, and New
activity, is locked. Once you are signed in, the account button stays usable. See
[Set up Blowhorn the first time](/docs/how-to/set-up/first-run-setup/).

| Screen | Shows | Acts |
|---|---|---|
| Home | Whether Blowhorn is working, what runs next ("Next: Accept LinkedIn invitations, tomorrow at 9:00 AM", from your enabled routines, and nothing while a pause holds), and whether it needs you; a pause names which pause holds - this computer, all computers, or both; "Your draft was saved" once after setup, until you dismiss it or leave Home | Turn off the pause it names (one button per pause while both hold); reconnect an account; **Connect an account** opens a step for your own profile: each platform, how to sign in to it in your Chrome profile, and **Check again**, with connected ones ticked; finish setting up |
| Activity › Upcoming | Your posts with their status - "ready", "scheduled", "partly sent", "sent", "draft", "needs you" - and clicked-but-unread ones; an opened post's editor shows its result: delivery per profile and platform, reception where it was collected, and the follower change since. On the all and scheduled filters, the schedule's routines follow below the posts, each labelled by what it does; a routine names no post, so selecting one opens it on Routines | Add or edit a post; clearing a clicked post's "Date Promoted" queues it again |
| Activity › Routines | Your routines as a day, week or month calendar, or as a list: each item's next time, its last time, and the times that would follow, dashed because they are estimates; a "now" row for items going out or waiting for the next check; a drawer for one item; a preview of sample routines | Add an item, from "schedule something" or by clicking a free time; move an item's next time by dragging it; edit, pause or resume one item; "do it now"; add the sample routines |
| Activity › History | Everything Blowhorn did, newest first, with each one's detailed log under the log directory's `scheduler/` folder; a picked run's detail shows its activity's result above the log: delivery per profile and platform, reception where it was collected, and the follower change since | "try again" on a failure |
| Profiles | Every profile, its Chrome mapping, its per-platform sessions; for LinkedIn, X and Reddit, which Chrome profile to sign in to - never a password field | Add a profile; map or unmap its Chrome profile; open a platform's sign-in page in that Chrome profile and **Check again**; enter a token or app password for the platforms that take one |
| Performance | Followers, growth, and activity per profile; collection freshness in the header | Collect now; open the HTML report |
| This computer (from the status line) | Who registered the background service, whether it is on watch, the last check, the pause for all computers | "check now" (with "preview only" to see what would go out); the "pause all computers" toggle; open System Settings when the service is turned off there |
| Settings (from the account menu) | Engine defaults rendered from the CLI's own option list, the extension card, your account card | Change defaults, check the extension, choose its mode, test your account connection |

The routines list keeps every value on one line. When the list is narrow -
the drawer is wide, or the window is small - the browser and recurrence
columns leave first (the drawer still shows both) and a long profile list
is shortened with an ellipsis; the status is never cut.

The Routines view opens on the week calendar and remembers the layout you
pick; opening a day from the month makes the day view the remembered one.
The tabs ("coming up", "due now", "going out", "failed", "all") and the
filter box choose which items it shows, in every layout. An item's next time
is a fact; the times after it are drawn dashed, because Blowhorn schedules
each one from when the last one finished, so they drift. An item that repeats
more often than every hour shows its next time only (the month shows daily
and slower). Moving one asks your account first and refuses if someone else
changed that item since you loaded it. A finished item (it happened once, or
gave up after its retries) shows its last time and no next one; giving it a
new "when" in its editor schedules it again, with its full set of retries.

The Performance screen states how fresh its numbers are in the header and
has no refresh control of its own. Its activity heatmap has one row per
profile; attempts recorded for several profiles at once (`all`, or a comma
list) name no one profile, so they are counted beside it rather than shown
as a row. The History view reaches each item's detailed log through the
log directory listing, which includes each capture file and its rollover.
The this computer screen is the visible face of `blowhorn service`: it reports the
service the app registered and never installs, updates or uninstalls one.

Profiles made before profile names were lowercase keep their capitalised
folder (`data/profiles/Alex`). The app lists them as they are spelled and
reads and saves them as the lowercase name every command resolves them to.

## Setup

Setup is the engine checklist the app opens on while its engine is not
ready (otherwise the first run is the guided setup; see
[Set up Blowhorn the first time](/docs/how-to/set-up/first-run-setup/)),
five rows read from this computer: the engine rows ("blowhorn engine" and
"bundled engine" in the installed app; "Blowhorn folder" and "helper tools" in
a source build), "organization connection", "chrome profiles", and
"this computer on watch". The first two check the engine bundled in the
app, the only engine the installed app runs
([Install the app](/docs/how-to/set-up/install-the-app/#first-run)).
Setup itself never clones or installs: a source build with no engine is
told to clone the repository and run `./tools/install.sh` in Terminal.
An app run from its disk image says to move it to Applications
instead. Each row reports ok, warn, or off with the
one fix that clears it. The "map chrome profiles" panel and the
"this computer on watch" row act directly: mapping a profile and
registering the service happen here, not in a terminal.

## Settings

Settings edits the same `.blowhorn.yaml` defaults the CLI reads: pace,
excluded profiles, dry run, notifications, logs, and the Chrome launch
mode. The engine-defaults card renders from `blowhorn config show`,
so the app can never offer an option the engine does not know. The
extension card reports whether the extension is installed, which
version answers, and whether it says connected, and sets its
[extension mode](/docs/reference/chrome/#extension-mode-classic-or-background), classic or
background, on your Blowhorn account. **guided setup** at the
bottom reopens the first-run setup, and **run setup again** opens Setup.
Quitting the app leaves
posting to the background service and the keep-running setting; see
[What runs when the app is closed](/docs/explanation/distribution/).

## Related

- [Map Blowhorn profiles to Chrome profiles](/docs/how-to/set-up/map-chrome-profiles/) - the Setup panel behind the mapping.
- [Change your defaults](/docs/how-to/settings/defaults/) - pace, exclusions, logs.
- [Settings and configuration](/docs/reference/configuration/) - every option the app edits.
- [How Blowhorn works](/docs/explanation/how-it-works/) - app, engine, extension, and store.
- [You're in control](/docs/explanation/youre-in-control/) - the controls behind pause and Settings.
- [Install the app](/docs/how-to/set-up/install-the-app/) - get the app onto a Mac.
