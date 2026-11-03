---
title: "The Blowhorn app, screen by screen"
description: "The menu-bar popover, the console screens, Setup, Settings, and what each one does."
weight: 211
---


What each part of the Blowhorn desktop app shows and does. This page
describes; the steps live in the how-to guides linked under Related.

## The menu bar and the popover

Blowhorn lives in the menu bar. Opening it shows the popover, top to bottom:

- **The header:** the Blowhorn mark and wordmark (not a link), a `?` that says what the popover is for, **Settings** and **Quit**.
- **Three stats:** how many items need you (gold above zero), runs done in the last seven days, and the success share over the same week. A dash means no runs or no reading.
- **The create button:** **New order**, or **New activity** when Major Blowhorn is off. Under it, one line says you can drop a link, image or video anywhere on the popover.
- **NEXT UP:** the next three due items. **open ›** opens one in Activity. When nothing is due, the popover says so.
- **RECENTLY DONE:** the last three finished items. **↗** opens the item's proof link in Google Chrome. An item with no proof link opens in Content.
- **Duty:** **This computer ›** and **Fleet ›**, each with its switch. A switch shows its state by its knob alone. The name opens that screen.
- **Open console**, and, when there is one, an update card.

A notice line sits under the header when something needs you: a store outage, a fleet state that cannot be read, or a refused pause. The popover never offers Check now, a countdown or a timer. Its stats and lists refresh when the popover opens and when main pushes a change.

Stop everything is not on the popover. Use the console or `blowhorn stop --all` for it.

### Drop a link, image or video

Drop anything on the popover, with no prompt. What you drop decides the sheet:

- **A link to a post or comment** on LinkedIn, X, Reddit, Bluesky, Slack or GitHub opens the engage sheet for it. The sheet offers the verbs that platform takes: Respond and Amplify on LinkedIn, Reddit and Bluesky, Amplify alone on X and GitHub, and Respond alone on Slack. A verb the platform cannot do is left out.
- **Only profiles with an active account on that platform** are offered. The one you used last on that platform is selected, and that choice is remembered on this computer. A platform with no active profile says so in one line and links to Profiles.
- **Any other link,** including a Hacker News item, starts a new order that uses the page's title and summary.
- **An image or video** starts a new order.
- **Anything else** is refused with the line "Links, images or video only" (in the military voice, "Wrong intel").

Respond or Amplify writes an approved item, due now, for each profile you select. For 10 seconds afterwards the sheet offers **Undo**, which removes what it wrote. After that the order is final.

**New order** looks at the Chrome tab in front of you first. An open post opens the engage sheet, and an open page starts a new order from that page. The first time you press New order while Chrome is running, macOS asks whether Blowhorn may control Google Chrome. Blowhorn asks only then, when you start a post from a page, never at launch.

When an update is ready, the update card at the bottom of the popover offers **Update**. The update downloads the new version, installs it
and relaunches the app; when it cannot, it says why and offers the release
page. In the console, an update shows its progress over the whole window
until Blowhorn reopens. An installed Blowhorn that finds such a release when it opens also
asks in the console window, before the download, with **Update now**, **Later**
and a **?** help icon;
what each does is under [Update](/docs/how-to/set-up/install-the-app/#update).
With **UI sounds** on in Settings, a new version gets a short announcement when the prompt
first shows, the update plays quiet music while it downloads and installs, and a finished
update plays a short chime: on the new version's first launch when Blowhorn relaunched to
finish. Turning UI sounds off silences all three. The update dialog itself carries a
speaker toggle at the top right beside its title; it is the same **UI sounds** setting
as in Settings, so switching it off mid-update silences the update music at once, and
switching it on again restores it.

## The console

The console is the full window, reached from the popover. The Blowhorn logo
at the top of its rail is Home; there is no separate Home item. Below it are
four places: **Activity**, **Profiles**, **Performance** and **Posture**. The
round **+** button in the lower right of every screen, teal glass unless you
change the material, is **New order** (⌘N, or New order in the File menu), or **New activity** when Major Blowhorn is off. It opens a field order you fill in
one step at a time. Only the open step shows its fields; a
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
5. **When to march** - **On my mark** (out on the next run), or a date and a
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
are read once when Performance opens, never on the screen's 60-second poll. If any platform refuses, the card is an **after-action report**
instead: **Mission failure**, how many platforms deployed, each refusal in its
own words, and per platform **Re-engage** (try only what did not land) or
**Stand down** (leave it unsent). What landed is never written twice.
An action deploys the same way, as one scheduled run per platform and desk
that runs once, at the time you picked or on the next run; its debrief rows
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

At the bottom of the rail, once you are signed in, one duty switch covers this
computer: **On duty**, or **Standing down** while it is held. Its position and
colour show the state, and it never names the action. Press it (or ⌘⇧P) to change
it; it never touches the fleet. Under the fleet's stand down alone it reads
**Standing down** and is held: the fleet's switch on Home's Fleet card is the one
that changes it. When the service is stopped, not installed or turned off in
System Settings it still reads **On duty**, and a line above it gives the reason
and opens This computer; the same line says when a check is late or when the
fleet's state can't be read. Hover the switch for the next scheduled run (for
example "Next: Post on X, tomorrow at 9:00 AM") or when the stand down began. When the service runs from another copy of
Blowhorn (a dev checkout, or a moved or older app), the line above the switch
says so, and This computer names that copy in one sentence with its one fix,
**Register the service**, which registers the service to this app. Under the switch, the
account button (desktop v1.27.2) shows who is signed in: your Blowhorn profile photo, or
your initials, your name, and your organization and plan (for example "Acme ·
Free plan"). The organization is the one your Blowhorn session has
selected, the same one [cloud.blowhorn.ai](https://cloud.blowhorn.ai) shows, unless
`BLOWHORN_CLOUD_ORGANIZATION` names another; the plan is that organization's.
Every organization is on the Free plan unless an active subscription names another. It opens the
account menu: your name, email, organization and plan, then **Your account and
plan** (your Blowhorn account page at cloud.blowhorn.ai, in your browser), **Team** (coming
soon), **Switch organization** when you belong to more than one (it lists them
inline in this menu with yours checked, and pointing at one, or moving to it with the
arrow keys, shows its description and its ID, so two organizations with the same name
can be told apart; picking one switches your account to it right here, the same
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
| Home (two tabs: **Today** and **Resources**) | Today: whether Blowhorn is working and whether it needs you, but never what runs next: an activity's next run is on Activity › Routines, and the rail's duty toggle names the next one on hover; the Fleet card: computers known (this one and every other computer that has run here or reported lately), how many are on duty or standing down, fleet holds, who stood the fleet down and why, this computer's row, and a row for each other computer saying **On duty**, **Standing down** or **Not on duty** from the last pass its background service reported, or **Not reporting** when it has reported nothing in the last half hour; a computer that is not reporting is never counted on duty, and the card says **2 of 3 reporting** while any one is not; "Your draft was saved" once after setup, until you dismiss it or leave Home; beside them your results, and one card with **Recent activity** and **What went wrong** (it opens on what went wrong while something failed). Resources: ideas worth a try, the latest from Blowhorn - each piece labelled with its column, From the Desk of the General, From Boot Camp or From the Field - and the tips as a taught sequence: the next tip you have not seen yet, with its video, one at a time; opening a tip or choosing **Another tip** moves you on, a tip you have seen never comes back, and when you have seen them all the card says so and points to Resources. A newer release is offered on a card at the top of the results column, **Update to Blowhorn** and the version | the entire fleet's switch (reason optional, saved as you type) or this computer's switch, on the Fleet card; open This computer from this computer's row; reconnect a signed-out account from the **Needs you** section at the top of Today: one full-row button per signed-out account, its platform's mark and **Reconnect** (naming the profile, **Reconnect @handle**, only where two signed-out accounts share a platform), which signs that account in again and reads **Reconnecting…** while it runs, and the **?** beside the title says which computer they are signed out on and how many scheduled posts wait (a Bluesky app password or a GitHub token opens Profiles instead); a sign-in that does not finish leaves the row with a note underneath saying so; open an item's details from a row in **Recent activity** or **What went wrong**; start the update from its card (Blowhorn restarts to finish); **Connect an account** opens a step for your own profile: each platform, how to sign in to it in your Google Chrome profile, and **Check again**, with connected ones ticked; finish setting up |
| Activity › Upcoming | Your posts with their status - "ready", "scheduled", "partly sent", "sent", "draft", "needs you" - and clicked-but-unread ones, each with when it goes out: its own time, "next run" when the next run would take it, "not scheduled" when nothing will send it (a draft, or a post that needs you), and "-" once it has gone out; an opened post shows its result: delivery per profile and platform, reception where it was collected, and the follower change since. On the all and scheduled filters, the schedule's routines follow below the posts, each labelled by what it does; a routine names no post, so clicking one opens that routine's details on Routines | Click a post to open it in a dialog (a box over the screen), or add one; edit it there; clearing a clicked post's "Date Promoted" queues it again |
| Activity › Routines | Your routines as a day, week or month calendar, or as a list: each item's next time, its last time, and the times that would follow, dashed because they are estimates; a "now" row for items going out or waiting for the service to take them up; a dialog for one item, opened by clicking it in the list or on the calendar; a chooser of sample routines, each one ticked on only once its platform is connected | Add an item with the **+** button or by clicking a free time (**Schedule** saves it); move an item's next time by dragging it; edit one item (its changes save as you make them, and **Do it now** runs it), or switch it between on duty and standing down from its duty switch on its row, on its calendar chip or in its dialog; "do it now", "disable" or "delete" it there; turn **dry fire** on in the header to rehearse up to the final click and post nothing (the dry run, `--dry-run`); add the sample routines you tick |
| Activity › History | Everything Blowhorn did, newest first, with each one's detailed log under the log directory's `scheduler/` folder; clicking a run opens it in a dialog over the full-width list: when it started, how it ended and why it stopped, its activity's result (delivery per profile and platform, reception where it was collected, and the follower change since), and the log and its file behind **more details** | open a run; "try again" on a failure |
| Profiles | Every profile, its accounts and their state, and the Google Chrome profiles on this computer each one uses. Clicking a profile opens its window over the list: the header says what Blowhorn does for the person and what needs you, and three tabs hold the rest. **Accounts** lists each connected account, and an account that needs you reads **Reconnect**. **Browser** lists the Google Chrome profiles on this computer beside the accounts in the one you pick; each is switched on or off for Blowhorn, and **Discover** finds signed-in sessions again. **About** holds the name, the description, who the profile is for, and delete. Nothing has a Save button: switches and fields save as you change them | Add a profile (in its own form); reconnect an account on **Accounts**; on **Browser**, turn a Google Chrome profile on or off, set up an account, or add a token or app password; change the name, description or who it is for, or delete the profile, on **About**; **check all profiles** on the list |
| Performance | Followers, growth, and activity per profile; collection freshness in the header. Under the filters, three tabs that all read them: **Activity** (runs by platform, activity per profile), **History** (the figures, followers over time, new versus unfollowed per month) and **Report** (your LinkedIn pages and the health of each profile and page) | Collect now; open the HTML report |
| Posture (three tabs: **Rules**, **Limits**, **Protection**; the fleet's stand down and stop sit on the tabs' line) | Rules: the rules of engagement for everyone (the slider: Safety on, Weapons tight or Weapons free), which choice wins, one grid of every profile on every platform with where each cell's choice comes from. Limits, one row per section: by platform (pace and daily caps), speed and amount (spacing, outreach, how much runs at once), when and who says yes (quiet hours, approval, dry fire), typing, and pointer timing; each row opens its settings in a window. Protection, one row per section: what happens when a platform pushes back, what the last check held back, where your sign-ins live and what Blowhorn will never do | Move the slider; choose a preset for one platform for every profile, one profile on every platform, or one cell, or reset any of them to inherit; reset them to the preset; each limit saves as you change it; stand down or stop every computer; run a held activity once with **Do it anyway**; turn the sign-in check, the needs-you note, dry fire by default and failure reports on or off |
| This computer (from Home's computer row, or the rail's reason line) | Whether this computer is on duty and, when it is not, the one sentence on what is wrong, the owner of the background service once something holds it, the last pass, the fleet's stand down | Its one fix under the banner: "register the service" when the service is not registered or runs from another copy of Blowhorn, "start the service" when it is registered but not running, "open Login Items" when it is turned off in System Settings (only those states offer one); "check now" (with "dry fire" to rehearse up to the final click, posting nothing); "stand down the fleet", and the fleet's switch while the fleet holds |
| Settings (from the account menu; its pages are listed in the left rail under the places while it is open) | **General**: appearance (theme, material, spacing), notifications and usage data. **Background & updates**: startup, keeping this computer on watch after quit, the pause shortcut, the update channel, uninstall. **Setup**: setup and the guided setup, the extension card. **Advanced**: app paths and the engine defaults Posture does not hold, rendered from the CLI's own option list | Change defaults, check the extension, choose its mode; run setup again or quit or uninstall; **open Posture ›** for the rules of engagement and limits. Your account is not in Settings: the account menu holds **Your account and plan**, **Switch organization** and **Sign out** |

The routines list keeps every value on one line, and it has the whole width of
the screen: an item's details open in a dialog, not beside it. When the window is
small, the browser and recurrence columns leave first (an item's dialog still
shows both) and a long profile list is shortened with an ellipsis; the status is
never cut. In the narrowest window the number leaves too, and each routine's duty switch
shrinks to its track (its words stay in its name). Every row carries that switch beside its status:
click it to stand the routine down or put it back on duty, without opening the row. A
list longer than the screen is shown a page at a time, as many rows as fit, with
previous and next at its foot.

Clicking an item, in the list or on the calendar, opens its details in a
dialog (a box over the screen). It shows the item's number, its status as
plain text, platform, what it does and who for, and the duty switch on the
right of that heading (a routine only: a post or a run has none), then when it
goes and when it last did, the last error, and **do it now**, **disable**,
**edit** and **delete**. The driver, the rules of engagement, the retries, the lock, the
edit check and the log sit behind **more details**, which is already open
while the item is running. **edit** swaps the dialog for the editor, one box at
a time. Esc, the **X** or a click outside closes it, and it asks first when
you typed a reason you have not sent; focus goes back to the item you clicked.
A routine or post on Home, a routine under Upcoming's posts and a row in the
menu-bar popover open the same dialog over its own screen; a run on Home opens
its run dialog where you are.

The day and week calendars show all 24 hours at once, an hour a row; the
rows grow when the window gives them room. The **now** lane shows three
items and a "+N more".

The Upcoming list keeps each value on one line too, and the preview gives
way first: in a small window "goes out" leaves the list (the post's dialog
shows it), and below that the number and the preview.

The Upcoming list has the full width of the screen, so each post's preview is
on screen at the default window size. Clicking a post opens it in a dialog, a
box over the screen, with its words, when it goes out, whether it is approved,
and what came of it; **New order** opens the same dialog on a new entry.
The columns nobody reads daily sit behind **more details**. If you typed
something and close the dialog, it asks before it throws your changes away.

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

The Performance screen states how fresh its numbers are behind the `?` in its
header and has no refresh control of its own (the debrief's rows are read once,
when the screen opens on them). Its activity heatmap has one row per
profile; attempts recorded for several profiles at once (`all`, or a comma
list) name no one profile, so they are counted beside it rather than shown
as a row. The History view reaches each item's detailed log through the
log directory listing, which includes each capture file and its rollover.
The this computer screen is the visible face of `blowhorn service`: it reports the
service the app registered and never installs, updates or uninstalls one.

The app lists each profile by the name your account holds and reads and
saves it as the lowercase name every command resolves it to.

An empty screen says what it is for and what to do next, with one member of
the cast beside the note. Every empty screen has one, including a filter that
hides everything, a table, a form, a dropdown and the menu bar's queue. Two
empty areas on one screen merge into one. Where the next step is a button on
that screen, the button is there, and an info button beside it links the docs
page for it. Where the next step is the **+** button or a button in the
header, such as **collect now** on Performance, the note names it rather than
repeating it. With **Cast characters** off in Settings, the same note and
action show without the art, and Major's line goes with them. A tab with nothing on it says what goes there and offers one
button: Upcoming's points at the tab where your posts are, with its count
(**show drafts (1)**), and History's at today or all, or at the **+** button
when nothing has run yet. A filter that hides everything on a tab offers **clear
filter**.

Upcoming opens on the first tab that holds a post - ready, needs you, drafts,
scheduled, then sent - so right after guided setup it opens on your first
post, often a draft. A tab you pick, or one a link opens, stays put.

On the guided setup's steps, Major Blowhorn's portrait in the left rail is
alive. His eyes and head follow your pointer, and now and then he looks
around, pulls a face, polishes his bugle or gives a thumbs up. Click him and
he sounds his bugle, double-click him and he lets Old Thunderlung rip; he only
makes a sound when you click him, and only with **UI sounds** on. Leave him
alone and he points at the step's button, then turns into one of his oil
paintings until you come back. With **Cast characters** off in Settings the
rail shows no portrait, and with **Reduce motion** on in your Mac's
accessibility settings he holds still. The same setting hides the periscope
picture on the Chrome side panel's idle screen; the line under it stays. The
side panel follows the setting within a few seconds: no reload, and you do not
need to close and open it again.

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
Chrome launch mode. Nothing has a Save button: a switch saves as you flip it,
and a text, number or path field saves when you leave it, with one saved
indicator on the card. Its **appearance** card is the app's own: the theme, the
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
background, the Blowhorn tab group (collapsed or open) and where Blowhorn works
(beside your tabs or in its own window, mostly behind yours), on your Blowhorn account. **guided setup** at the
bottom reopens the first-muster setup, and **run setup again** opens Setup.
Quitting the app leaves
posting to the background service and the keep-running setting; see
[What runs when the app is closed](/docs/explanation/distribution/).

## Posture

Posture opens on its tabs, with **Stand down the fleet** and **Stop everything**
beside them; the rail names the screen, so it has no visible title.

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
  one row per section (by platform, speed and amount, when and who says yes, typing,
  pointer timing). Each row opens its settings in a window: a choice saves as you
  make it, a typed value saves when you leave the field or close the window, and
  **Reset to preset** puts the dials back.
- **When a platform pushes back.** Each row opens a window holding the pause after a challenge, any sign-in that
  needs you (with **open Profiles ›**), how often sign-ins are checked, and the
  needs-you note.
- **Held back.** What the last check held, why, and when it can run, with **Do it
  anyway** for a rules-of-engagement hold.
- **Where your sign-ins live** and **Blowhorn will never** are the promises, each one
  row that opens its details in a window; the failure reports switch is in the sign-ins window.

Info buttons stay hidden until you point at their row or tab to them.

## Related

- [Map Blowhorn profiles to Chrome profiles](/docs/how-to/set-up/map-chrome-profiles/) - the Setup panel behind the mapping.
- [Choose your rules of engagement](/docs/how-to/settings/choose-your-rules-of-engagement/) - the Posture screen in practice.
- [Change your defaults](/docs/how-to/settings/defaults/) - exclusions, logs.
- [Settings and configuration](/docs/reference/configuration/) - every option the app edits.
- [How Blowhorn works](/docs/explanation/how-it-works/) - app, engine, extension, and store.
- [You're in control](/docs/explanation/youre-in-control/) - the controls behind pause and Settings.
- [Install the app](/docs/how-to/set-up/install-the-app/) - get the app onto a Mac.
