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
the next tick. The standing down board shows STANDING DOWN with each
tick-level scope (this computer, the fleet) stated once, and the activities that would post now wait instead of
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

The popover footer holds "stand down this computer" and "stand down the fleet"
(each reads "reenlist" while it holds) and, when an update is
ready, the update card. The update downloads the new version, installs it
and relaunches the app; when it cannot, it opens the release page in your
browser. An installed Blowhorn that finds such a release when it opens also
asks in the console window, before the download, with **Download**, **Later**
and a **?** help icon;
what each does is under [Update](/docs/how-to/set-up/install-the-app/#update).

## The console

The console is the full window, reached from the popover. The Blowhorn logo
at the top of its rail is Home; there is no separate Home item. Below it are
four places: **Activity**, **Profiles**, **Performance** and **Safety**. The
round teal **+** button in the lower right of every screen is **New activity**
(⌘N, or New activity in the File menu). It opens **New order**:

- **Dispatch to** - press one or more platform logos (LinkedIn, X, Reddit,
  Bluesky, Slack, GitHub); press again to drop one.
- **Orders that fit these channels** - **Compose a dispatch** (a post),
  **Answer the line** (a reply to a link) or **Rally the troops** (amplify a
  link). Only the orders every picked platform takes are offered; with GitHub
  picked, that is Rally alone.
- **Signed by** - the profile it goes out as.
- **The message**, and **Attachments**: drop one or more images or videos, or
  paste a link to one. Anything else is turned away with "Wrong intel - image
  or video only", and each attached file has its own **Stand down** to remove
  it. Blowhorn posts media from a link, so a dropped file needs its link
  pasted too.
- **When to march** - one row that reads **On my mark** (out on the next
  check) until you open it and lock in a date and start time. An order goes
  out once; **Advanced standing orders** opens the routine editor for
  something that repeats, and for Hacker News, an organization blog (offered
  only when a profile in your organization is opted in to it, `blowhorn
  schedule destinations`) or a report.

**Deploy** adds one post to the queue for each platform picked, with the same
words, link, media and time, and opens Upcoming. If one is refused part-way,
the order says which went out and keeps only the rest picked, so a second
Deploy never sends one twice. **Stand down** closes it. The **Sounds on**
control is a preview: no sound plays yet. An activity already saved for a
blog still shows and runs. Activity is
one place with three views, switched at the top of the screen: **Upcoming**
(what you want to say), **Routines** (when and where things go out) and
**History** (what Blowhorn did). Safety holds every Risk Profile choice and every
limit Blowhorn keeps; the Risk Profile pill on Home and the menu-bar popover's
**safety ›** link open it.

At the bottom of the rail, once you are signed in, one duty toggle covers this
computer: **On duty** with **Stand down** beside it, or **Standing down** with
**Reenlist**. Its round thumb is the status - teal on duty, amber standing down.
Press it (or ⌘⇧P) to stand this computer down or reenlist it; it never touches
the fleet. Under the fleet's stand down alone it reads **Fleet standing down**
and still offers this computer's own Stand down. When the service is stopped,
not installed or turned off in System Settings it reads **Not on duty**, and
a line above it gives the reason and opens This computer; the same line says
when a check is late or when the fleet's state can't be read. Hover the toggle
for the next scheduled run (for example "Next: Post on X, tomorrow at 9:00 AM")
or when the stand down began. Under the toggle, the
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
[Set up Blowhorn at first muster](/docs/how-to/set-up/first-muster-setup/).

| Screen | Shows | Acts |
|---|---|---|
| Home | Whether Blowhorn is working and whether it needs you, but never what runs next: an activity's next run is on Activity › Routines, and the rail's duty toggle names the next one on hover; the Fleet card: computers known (this one), how many are on duty or standing down, fleet holds, who stood the fleet down and why, and this computer's row; "Your draft was saved" once after setup, until you dismiss it or leave Home | Stand down or Reenlist the entire fleet (reason optional, saved as you type) or this computer; open This computer from this computer's row; reconnect an account; **Connect an account** opens a step for your own profile: each platform, how to sign in to it in your Chrome profile, and **Check again**, with connected ones ticked; finish setting up |
| Activity › Upcoming | Your posts with their status - "ready", "scheduled", "partly sent", "sent", "draft", "needs you" - and clicked-but-unread ones, each with when it goes out: its own time, "next check" when the next run would take it, "not scheduled" when nothing will send it (a draft, or a post that needs you), and "-" once it has gone out; an opened post's editor shows its result: delivery per profile and platform, reception where it was collected, and the follower change since. On the all and scheduled filters, the schedule's routines follow below the posts, each labelled by what it does; a routine names no post, so selecting one opens it on Routines | Add or edit a post; clearing a clicked post's "Date Promoted" queues it again |
| Activity › Routines | Your routines as a day, week or month calendar, or as a list: each item's next time, its last time, and the times that would follow, dashed because they are estimates; a "now" row for items going out or waiting for the next check; a drawer for one item; a preview of sample routines | Add an item with the **+** button or by clicking a free time; move an item's next time by dragging it; edit one item, or Stand down / Reenlist it from the duty switch in its drawer; "do it now"; add the sample routines |
| Activity › History | Everything Blowhorn did, newest first, with each one's detailed log under the log directory's `scheduler/` folder; a picked run's detail shows its activity's result above the log: delivery per profile and platform, reception where it was collected, and the follower change since | "try again" on a failure |
| Profiles | Every profile, its Chrome mapping, its per-platform sessions; for LinkedIn, X and Reddit, which Chrome profile to sign in to - never a password field | Add a profile; map or unmap its Chrome profile; open a platform's sign-in page in that Chrome profile and **Check again**; enter a token or app password for the platforms that take one |
| Performance | Followers, growth, and activity per profile; collection freshness in the header | Collect now; open the HTML report |
| Safety | The Risk Profile for everyone (the slider), which choice wins, one grid of every profile on every platform with where each cell's choice comes from, the limits by platform (pace and daily caps) and the rest (spacing, outreach, how much runs at once, quiet hours, approval, preview only, typing and pointer timing), what happens when a platform pushes back, what the last check held back, where your sign-ins live, and what Blowhorn will never do | Move the slider; choose a preset for one platform for every profile, one profile on every platform, or one cell, or reset any of them to inherit; save limits or reset them to the preset; stand down or stop every computer; run a held activity once with **Do it anyway**; turn the sign-in check, the needs-you note, preview only by default and failure reports on or off |
| This computer (from Home's computer row, or the rail's reason line) | Who registered the background service, whether it is on duty, the last check, the fleet's stand down | "check now" (with "preview only" to see what would go out); "stand down the fleet" / "reenlist the fleet"; open System Settings when the service is turned off there |
| Settings (from the account menu) | Startup, notifications, appearance and shortcuts; the engine defaults Safety does not hold, rendered from the CLI's own option list; the extension card; your account card | Change defaults, check the extension, choose its mode, test your account connection; **open Safety ›** for the Risk Profile and limits |

The routines list keeps every value on one line. When the list is narrow -
the drawer is wide, or the window is small - the browser and recurrence
columns leave first (the drawer still shows both) and a long profile list
is shortened with an ellipsis; the status is never cut.

The Upcoming list opens with its editor folded away, so the list has the
full width and each post's preview is on screen at the default window
size. Selecting a post opens the editor beside it, and **New activity**
opens it on a new entry. A fold you make yourself is remembered, and a
post you select while the editor is folded that way stays in the list
until you open the editor again.

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

The app lists each profile by the name your account holds and reads and
saves it as the lowercase name every command resolves it to.

## Setup

Setup is the engine checklist the app opens on while its engine is not
ready (otherwise the first muster is the guided setup; see
[Set up Blowhorn at first muster](/docs/how-to/set-up/first-muster-setup/)),
five rows read from this computer: the engine rows ("blowhorn engine" and
"bundled engine" in the installed app; "Blowhorn folder" and "helper tools" in
a source build), "organization connection", "chrome profiles", and
"this computer on watch". The first two check the engine bundled in the
app, the only engine the installed app runs
([Install the app](/docs/how-to/set-up/install-the-app/#first-muster)).
Setup itself never clones or installs: a source build with no engine is
told to clone the repository and run `./tools/install.sh` in Terminal.
An app run from its disk image says to move it to Applications
instead. Each row reports ok, warn, or off with the
one fix that clears it. The "map chrome profiles" panel and the
"this computer on watch" row act directly: mapping a profile and
registering the service happen here, not in a terminal.

## Settings

Settings edits the same `.blowhorn.yaml` defaults the CLI reads:
default profile and platform, excluded profiles, notifications, logs, and the
Chrome launch mode. Pace, daily caps, quiet hours, how much runs at once,
approval, preview only and the Risk Profile are on the [Safety](#safety)
screen instead; each Settings card that used to hold one says so and links
there. The engine-defaults card renders from `blowhorn config show`,
so the app can never offer an option the engine does not know. The
extension card reports whether the extension is installed, which
version answers, and whether it says connected, and sets its
[extension mode](/docs/reference/chrome/#extension-mode-classic-or-background), classic or
background, on your Blowhorn account. **guided setup** at the
bottom reopens the first-muster setup, and **run setup again** opens Setup.
Quitting the app leaves
posting to the background service and the keep-running setting; see
[What runs when the app is closed](/docs/explanation/distribution/).

## Safety

Safety opens with "Your pace. Your risk. Your call." and **stand down the fleet**
and **stop everything**, the same controls as the popover's footer.

- **Who runs how carefully.** The slider sets the Risk Profile for everyone. Under
  it, **which choice wins** numbers the levels from everyone to one activity, and
  the grid has a row for each platform's choice for every profile (**Each
  platform**), a column for each profile's choice on every platform (**Every
  platform**), and a cell for one profile on one platform. A filled chip was chosen
  at that spot; a dashed chip is inherited, and the line under it says from where
  ("from LinkedIn", "from this profile", "from everyone"). A profile still warming
  up shows **Warming** and the preset it returns to. Pick any chip to choose a
  preset or **Inherit**; a cell chosen here shows a reset beside it when you point
  at it or tab to it. A platform's choice is kept for every computer; when it could
  only be saved on this computer, the row says "this computer only". The order is
  in [Which choice wins](/docs/reference/configuration/#which-choice-wins).
- **The limits Blowhorn keeps.** One table of the platforms a Risk Profile covers,
  with each platform's pace (a word, or a number as a multiplier) and its daily
  caps, each cap showing the built-in ceiling until you set a lower one. Below it,
  the speed, how-much and when rows, the preset's own values where no option sets
  them, and typing and pointer timing. **save limits** writes every change at
  once; **reset to preset** puts the dials back.
- **When a platform pushes back.** The pause after a challenge, any sign-in that
  needs you (with **open Profiles ›**), how often sign-ins are checked, and the
  needs-you note.
- **Held back.** What the last check held, why, and when it can run, with **Do it
  anyway** for a Risk Profile hold.
- **Where your sign-ins live** and **Blowhorn will never** are the promises, with
  the failure reports switch.

Info buttons stay hidden until you point at their row or tab to them.

## Related

- [Map Blowhorn profiles to Chrome profiles](/docs/how-to/set-up/map-chrome-profiles/) - the Setup panel behind the mapping.
- [Choose your Risk Profile](/docs/how-to/settings/choose-your-risk-profile/) - the Safety screen in practice.
- [Change your defaults](/docs/how-to/settings/defaults/) - exclusions, logs.
- [Settings and configuration](/docs/reference/configuration/) - every option the app edits.
- [How Blowhorn works](/docs/explanation/how-it-works/) - app, engine, extension, and store.
- [You're in control](/docs/explanation/youre-in-control/) - the controls behind pause and Settings.
- [Install the app](/docs/how-to/set-up/install-the-app/) - get the app onto a Mac.
