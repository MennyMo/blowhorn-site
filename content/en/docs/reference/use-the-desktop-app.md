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
posting; it lists the first three waiting items and how many more, which
**N more ›** opens in Activity › Routines. Until you are signed in and the extension is ready, those boards
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
and relaunches the app; when it cannot, it says why and offers the release
page. In the console, an update shows its progress over the whole window
until Blowhorn reopens. An installed Blowhorn that finds such a release when it opens also
asks in the console window, before the download, with **Update now**, **Later**
and a **?** help icon;
what each does is under [Update](/docs/how-to/set-up/install-the-app/#update).

## The console

The console is the full window, reached from the popover. The Blowhorn logo
at the top of its rail is Home; there is no separate Home item. Below it are
four places: **Activity**, **Profiles**, **Performance** and **Posture**. The
round **+** button in the lower right of every screen, teal glass unless you
change the material, is **New activity** (⌘N, or New activity in the File
menu). It opens **New order**, a field
order you fill in one step at a time. Only the open step shows its fields; a
finished step folds to a one-line summary (press it to change it), and the
steps ahead wait as dim rows. A step that holds what it asks for takes a teal
check; one you passed empty, such as a skipped landing zone, takes a dashed
"-". Each step's **Next** moves on.

1. **Dispatch to** - press one or more platform tiles (LinkedIn, X, Reddit,
   Bluesky, Slack, GitHub), each showing that platform's mark in its own
   colour; a picked tile lifts and rings in that colour. Press again to drop
   one. Then **Orders that fit**: **Compose a dispatch** (a post), **Answer the
   line** (a reply to a link) or **Rally the troops** (amplify a link). Only
   the orders every picked platform takes are offered; with GitHub picked, that
   is Rally alone. Each order has an info button on its top-right corner, shown when you point at the order: its tip says what the order
   does on each platform picked, and links to that platform's supported
   actions and to the action-by-platform matrix (the platforms page).
   Beside them, **Or run** lists every other action the picked platforms can
   run once, in one select: on LinkedIn **Invite to a page**, **Accept
   invitations**, **Withdraw stale invitations** and **Collect analytics**; on X and Bluesky **Follow accounts** and **Collect
   analytics**; on GitHub **Follow accounts**. With several platforms picked it
   lists the actions all of them run. The list is the same catalog the command
   line schedules from, so an action Blowhorn can schedule is never missing
   here. Its info button describes every action until you choose one, then the
   one you chose.
2. **From the desk of** - one or more profiles. Each desk sends its own copy to
   every platform, so two platforms from two desks is four posts.
3. **The message**, with its character count (and, for a reply or a rally, the
   link it answers or amplifies). Type `@` to tag a person, company, page or
   community: a note says what the tag means, and the tags found show as chips.
   Each platform may know them by a different name, so **Next** first opens
   **Who's who**: for each tag, one line per platform picked, prefilled with a
   *guess* in that platform's form - `@handle` on X, `@name.bsky.social` on
   Bluesky, `u/` or `r/` on Reddit, a member id (`U0…`) on Slack. LinkedIn
   can't carry tags yet, and the order says so: its copy names each one as
   plain text, without the `@`, and nothing on LinkedIn is tagged. Blowhorn looks none of them up here, so check each one,
   edit any that are wrong, and leave a line empty to send that platform the
   name as plain text. **Looks right** moves on; change the message or the
   platforms afterwards and the order asks again before it can deploy. Each
   platform's post carries the message with its own form of each tag. Your
   answers are not remembered for the next order yet.
   A composed dispatch also offers **Single
   dispatch | Radio net**. A radio net is a conversation between profiles: the
   first transmission opens the net, and each one after it is a reply from one
   of the profiles you picked to the transmission above it, with its own words
   and character count, closed with "Over." **+ Add a reply** offers the next
   profile, each reply's profile can be switched, and a reply's **×** stands it
   down. Replies go out a random number of minutes apart within the window you
   pick (2-6 by default), never seconds apart; GitHub only rallies, so it sits
   a net out. The manifest shows the chain (K › L › K) and Deploy counts
   platforms x transmissions. **A radio net cannot go out yet:** each reply has
   to answer the post the transmission above it actually produced, read back
   from the platform, and your Blowhorn account cannot yet keep which item a
   reply answers. Until it can, Deploy, Hold in reserve and Dry fire wait, and
   the line above them says why. Switching back to Single dispatch keeps the
   opening transmission's words as the message.
   For an action this step is **The details**:
   the options that action takes, such as how many days old an invitation must
   be, how many to withdraw and **apply** for **Withdraw stale invitations**
   (without apply, the run only previews). A box left empty takes the
   command's own default, shown in it. An option a run cannot do without,
   such as the account to start from for **Follow accounts**, is marked
   required, and the order cannot go out until it is filled. Each option
   has an info button with what it means and the command's own help for it.
4. **Landing zone** - drop one or more images or videos, or paste a link to
   one. Anything else is turned away with "Wrong intel - image or video only",
   and each landed file has its own **Stand down** to remove it. Blowhorn posts
   media from a link, so a dropped file needs its link pasted too. **LZ clear**
   moves on with no media. A rally or an action carries no media.
5. **When to march** - **On my mark** (out on the next check), or a date and a
   start time from the pickers. Time is read the military way ("1430 HRS"),
   with the day's bugle calls (Reveille 0600, Mess call 1200, Retreat 1700,
   Taps 2200) as quick picks; **Roger ✓** closes the clock and **Lock it in**
   folds the order. An order goes out once: **Repeat it?** lists the standing
   orders (every day, weekday, week or month), and picking one opens the
   routine editor on the platform and desks you picked. A routine runs on one
   platform, so with more than one picked it asks you to pick one instead.
   The routine editor is where a repeating order lives, as do Hacker News, an
   organization blog (offered only when a profile in your organization is
   opted in to it, `blowhorn schedule destinations`) and a report.

On a wide enough window a narrow **manifest** slides out beside the order
the first time there is something to show: the platforms and desks stacked
like cards, the message's length (never its words), what landed, and when it
goes: a field watch shows a set time, and a jump light stands for **On my mark**. On a narrow window the folded summaries say the same. The line above the
buttons says what is still missing, or when the order goes out.

**Deploy** (it names the count, for example **Deploy 4**; a single post is just
**Deploy**) adds one post to the queue for each platform and desk, with the same
words, link, media and time. The steps fold away and the debrief takes the window: **Orders deployed**, one
row per platform with how many were queued and when, and "link pending" until
Blowhorn reads each post's own link back - never a guess. **Debrief** opens
Performance filtered to just the posts this order wrote: a **these dispatches**
chip in place of the filters, counting the posts the order wrote (its **×** puts
the whole screen back), and one row per post with its profile, platform, status
and when it is due or was sent (on your computer's clock, as "Mon, Jul 27, 2026 ·
10:00 AM"). A post deleted from the queue since is counted under the rows ("1 of
4 dispatches is no longer in your queue"), so the rows and that line add up to
the chip. Once its link is read back and
the platform reports on it, its engagement and reach, labelled measured with
the date it was read. A post whose link is not read back yet says **link
pending** - there is nothing to measure, so it never shows a zero. The rows
are read once when Performance opens and again when you press **read again**,
never on the screen's 60-second poll. If any platform refuses, the card is an **after-action report**
instead: **Mission failure**, how many platforms deployed, each refusal in its
own words, and per platform **Re-engage** (try only what did not land) or
**Stand down** (leave it unsent). What landed is never written twice.
An action deploys the same way, as one scheduled run per platform and desk
that runs once, at the time you picked or on the next check; its debrief rows
have no link to wait for and no Debrief link, since an action is not a post
with engagement to measure. The app checks an action in the window and again
before it is saved, so one missing a required option or naming an option the command
does not take is refused with the reason, never saved to fail later.
**Close** then opens Upcoming for a post, or Routines on the first action
saved. **Dry fire** rehearses the order before you
save it: for each platform and desk in turn it opens that profile's browser,
checks the sign-in and stops before composing (Slack, Bluesky and GitHub post
over their APIs, so they open no browser and stop before sending), listing
each as it goes and ending "Nothing was posted." It saves nothing - no post,
routine or record - and a platform it cannot walk says why on its own row.
Hacker News is not offered, because even its dry run signs in.
Dry fire is offered for posts only: an action has no post to rehearse.
**Hold in reserve** saves the same posts
unapproved instead, so nothing goes out until someone approves them in
Upcoming (an action is saved turned off on Routines, and runs only once
someone turns it on); **Cancel** closes the order without saving. The speaker button
in the header beside the title starts in your **UI sounds** setting; turning it off
mutes this order's sounds, and those of every post it saves. An activity already saved for a
blog still shows and runs. Activity is
one place with three views, switched at the top of the screen: **Upcoming**
(what you want to say), **Routines** (when and where things go out) and
**History** (what Blowhorn did). Posture holds every rules-of-engagement choice
and every limit Blowhorn keeps; the menu-bar
popover's **posture ›** link opens it.

At the bottom of the rail, once you are signed in, one duty toggle covers this
computer: **On duty** with **Stand down** under it, or **Standing down** with
**Reenlist** - always in full, never cut short. Its round thumb is the status - teal on duty, amber standing down.
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
inline in this menu with yours checked; picking one switches your account to it right here, the same
switch cloud.blowhorn.ai makes, so your browser follows too; `blowhorn auth
switch-organization` does it from Terminal), **Settings** (⌘,), **Help and docs**, and
**Sign out**. With many organizations the list scrolls on its own, so your name at
the top and **Sign out** at the bottom stay in view, and with more than eight a
**Filter organizations** box above the list narrows it as you type (press the
down arrow to move from the box into the list, and the up arrow on the list's first
organization to go back to the box). The menu works from the keyboard:
the up and down arrows move through it and wrap around at the ends, Home and End
jump to the first and last item, typing a name's first letters jumps to it, Return
or Space chooses the highlighted item, and Esc closes the menu. **Sign out** signs
you out and takes you straight to the sign-in screen; if it can't, the menu's error
line says why and you stay where you were. Opening the menu refreshes your name, photo, organizations and
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
| Home (two tabs: **Today** and **Resources**) | Today: whether Blowhorn is working and whether it needs you, but never what runs next: an activity's next run is on Activity › Routines, and the rail's duty toggle names the next one on hover; the Fleet card: computers known (this one), how many are on duty or standing down, fleet holds, who stood the fleet down and why, and this computer's row; "Your draft was saved" once after setup, until you dismiss it or leave Home; beside them your results, and one card with **Recent activity** and **What went wrong** (it opens on what went wrong while something failed). Resources: ideas worth a try, the latest from Blowhorn, and a tip. A newer release is offered on the top line, beside the tabs | Stand down or Reenlist the entire fleet (reason optional, saved as you type) or this computer; open This computer from this computer's row; reconnect an account; **Connect an account** opens a step for your own profile: each platform, how to sign in to it in your Google Chrome profile, and **Check again**, with connected ones ticked; finish setting up |
| Activity › Upcoming | Your posts with their status - "ready", "scheduled", "partly sent", "sent", "draft", "needs you" - and clicked-but-unread ones, each with when it goes out: its own time, "next check" when the next run would take it, "not scheduled" when nothing will send it (a draft, or a post that needs you), and "-" once it has gone out; an opened post's editor shows its result: delivery per profile and platform, reception where it was collected, and the follower change since. On the all and scheduled filters, the schedule's routines follow below the posts, each labelled by what it does; a routine names no post, so selecting one opens it on Routines | Add or edit a post; clearing a clicked post's "Date Promoted" queues it again |
| Activity › Routines | Your routines as a day, week or month calendar, or as a list: each item's next time, its last time, and the times that would follow, dashed because they are estimates; a "now" row for items going out or waiting for the next check; a drawer for one item; a chooser of sample routines, each one ticked on only once its platform is connected | Add an item with the **+** button or by clicking a free time; move an item's next time by dragging it; edit one item, or Stand down / Reenlist it from the duty switch in its drawer; "do it now"; turn **dry fire** on in the header to rehearse up to the final click and post nothing (the dry run, `--dry-run`); add the sample routines you tick |
| Activity › History | Everything Blowhorn did, newest first, with each one's detailed log under the log directory's `scheduler/` folder; a picked run's detail shows its activity's result above the log: delivery per profile and platform, reception where it was collected, and the follower change since | "try again" on a failure |
| Profiles | Every profile, its Chrome mapping, its per-platform sessions; for LinkedIn, X and Reddit, which Chrome profile to sign in to - never a password field. An open profile keeps its name and **check sessions** on top, over three tabs: **Details** (name, description, who it is), **Platforms** (one platform's card at a time, picked by its mark, each mark showing that session's state) and **Chrome** (its Chrome profile) | Add a profile; map or unmap its Chrome profile; open a platform's sign-in page in that Chrome profile and **Check again**; enter a token or app password for the platforms that take one |
| Performance | Followers, growth, and activity per profile; collection freshness in the header. Under the filters, three tabs that all read them: **Activity** (runs by platform, activity per profile), **History** (the figures, followers over time, new versus unfollowed per month) and **Report** (your LinkedIn pages and the health of each profile and page) | Collect now; open the HTML report |
| Posture (three tabs: **Rules**, **Limits**, **Protection**; the fleet's stand down and stop sit on the tabs' line) | Rules: the rules of engagement for everyone (the slider: Safety on, Weapons tight or Weapons free), which choice wins, one grid of every profile on every platform with where each cell's choice comes from. Limits, one section at a time: by platform (pace and daily caps), speed and amount (spacing, outreach, how much runs at once), when and who says yes (quiet hours, approval, dry fire), typing, and pointer timing. Protection: what happens when a platform pushes back and what the last check held back, beside where your sign-ins live and what Blowhorn will never do | Move the slider; choose a preset for one platform for every profile, one profile on every platform, or one cell, or reset any of them to inherit; save limits or reset them to the preset; stand down or stop every computer; run a held activity once with **Do it anyway**; turn the sign-in check, the needs-you note, dry fire by default and failure reports on or off |
| This computer (from Home's computer row, or the rail's reason line) | Who registered the background service, whether it is on duty, the last check, the fleet's stand down | "check now" (with "dry fire" to rehearse up to the final click, posting nothing); "stand down the fleet" / "reenlist the fleet"; open System Settings when the service is turned off there |
| Settings (from the account menu; its pages are listed in the left rail under the places while it is open) | **General**: appearance (theme, material, spacing), notifications and usage data. **Background & updates**: startup, keeping this computer on watch after quit, the pause shortcut, the update channel, uninstall. **Setup**: setup and the guided setup, the extension card. **Advanced**: app paths and the engine defaults Posture does not hold, rendered from the CLI's own option list; your account card | Change defaults, check the extension, choose its mode, test your account connection; run setup again or quit or uninstall; **open Posture ›** for the rules of engagement and limits |

The routines list keeps every value on one line. When the list is narrow -
the drawer is wide, or the window is small - the browser and recurrence
columns leave first (the drawer still shows both) and a long profile list
is shortened with an ellipsis; the status is never cut. With a routine
open at the default window size the number leaves too, and a routine that
is standing down shows an amber dot beside its status (hover it for the
words). A list longer than the pane is shown a page at a time, as many
rows as fit, with previous and next at its foot.

The day and week calendars show all 24 hours at once, an hour a row; the
rows grow when the window gives them room. The **now** lane shows three
items and a "+N more".

The Upcoming list keeps each value on one line too, and the preview gives
way first. With a post open beside it, "goes out" leaves the list (the
editor's Promote On shows it), and below that the number and the preview.

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
has no refresh control of its own (the debrief's **read again** reads only
those posts). Its activity heatmap has one row per
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
Chrome launch mode. Its **appearance** card is the app's own: the theme, the
material of the side rail and the **+** button (Solid, Teal glass, Ink glass or
Clear glass, with tint strength, see-through and reduce transparency, which is
on by default), and spacing; see [Change how the app looks](/docs/how-to/settings/appearance/).
Pace, daily caps, quiet hours, how much runs at once,
approval, dry fire and the rules of engagement are on the [Posture](#posture)
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

## Posture

Posture opens with "Your pace. Your risk. Your call." and **stand down the fleet**
and **stop everything**, the same controls as the popover's footer.

- **Who runs how carefully.** The slider sets the rules of engagement for
  everyone: **Safety on** (slow and careful, in teal blue), **Weapons tight**
  (normal pace, in teal) or **Weapons free** (fast, in the warn colour); the CLI
  and the config file keep `cautious`, `standard` and `brisk`. Under
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
- **The limits Blowhorn keeps.** One table of the platforms the rules of engagement cover,
  with each platform's pace (a word, or a number as a multiplier) and its daily
  caps, each cap showing the built-in ceiling until you set a lower one. Below it,
  the speed, how-much and when rows, the preset's own values where no option sets
  them, and typing and pointer timing. **save limits** writes every change at
  once; **reset to preset** puts the dials back.
- **When a platform pushes back.** The pause after a challenge, any sign-in that
  needs you (with **open Profiles ›**), how often sign-ins are checked, and the
  needs-you note.
- **Held back.** What the last check held, why, and when it can run, with **Do it
  anyway** for a rules-of-engagement hold.
- **Where your sign-ins live** and **Blowhorn will never** are the promises, with
  the failure reports switch.

Info buttons stay hidden until you point at their row or tab to them.

## Related

- [Map Blowhorn profiles to Chrome profiles](/docs/how-to/set-up/map-chrome-profiles/) - the Setup panel behind the mapping.
- [Choose your rules of engagement](/docs/how-to/settings/choose-your-rules-of-engagement/) - the Posture screen in practice.
- [Change your defaults](/docs/how-to/settings/defaults/) - exclusions, logs.
- [Settings and configuration](/docs/reference/configuration/) - every option the app edits.
- [How Blowhorn works](/docs/explanation/how-it-works/) - app, engine, extension, and store.
- [You're in control](/docs/explanation/youre-in-control/) - the controls behind pause and Settings.
- [Install the app](/docs/how-to/set-up/install-the-app/) - get the app onto a Mac.
