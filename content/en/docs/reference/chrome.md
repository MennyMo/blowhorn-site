---
title: "Chrome reference"
description: "The mapping commands, the two launch modes, the extension default, and Linux differences."
weight: 224
---


How Blowhorn finds and reaches your Google Chrome. Every browser run
reads the profile mapping first and refuses a profile without one,
before anything opens. This page describes; the steps live in the
how-to guides under Related.

## What it reads, and what it never reads

`blowhorn chrome` reads two files under Chrome's data directory,
`Local State` and `DevToolsActivePort`, and nothing else: never
cookies, saved passwords, storage, or the keychain. It writes nothing
there and opens no browser, DevTools, or network connection. Whether
Chrome is running is one bounded process lookup. There are four
exceptions. `blowhorn chrome extension-status` also reads each Chrome
profile's `Secure Preferences` and `Preferences` for the extension's
entry alone (see [its section](#blowhorn-chrome-extension-status)).
`blowhorn chrome discover` reads an allowlisted set of identity fields
for setup's confirm step (see [its section](#blowhorn-chrome-discover));
nothing outside that list, and never a saved password or a cookie's
value beyond the one named there.
`blowhorn chrome map` also asks Chrome to open a window on the
extension's pairing page in the mapped Chrome profile, and creates this
computer's pairing key outside Chrome's directory (see [Pairing](#pairing)).
`blowhorn chrome extension-enable` asks Chrome to open a window on the
extension's Chrome Web Store page in each Chrome profile you name (see
[its section](#blowhorn-chrome-extension-enable)).
`blowhorn chrome open-profile` asks Chrome to open a window in the
Chrome profile a Blowhorn profile is mapped to (see
[its section](#blowhorn-chrome-open-profile)). When no Chrome is
running, any of them starts Chrome to open that window and leaves it
running; none drives anything in it.

## What it never opens, and when it never starts Chrome {#what-it-never-opens-and-when-it-never-starts-chrome}

Blowhorn never opens a real Chrome profile folder directly. The Chrome
it launches itself runs on Blowhorn's own folders (its automation
folder, or the dedicated attach Chrome's folder); your profiles are
reached through the Blowhorn extension in your own Chrome, or by asking
your running Chrome to open a tab. A launch aimed at a real profile
folder is refused by name, with no fallback.

And Blowhorn never starts Chrome from a session that cannot reach your
login keychain -- an SSH session, a CI runner, or a shell with no
desktop session behind it. Chrome keeps its sign-in keys in the
keychain; started without it, Chrome cannot read them and signs the
profile out. A command that would have to start Chrome from such a
session refuses and says why; run it from a terminal on this computer
instead. Asking a Chrome that is already running to open a tab starts
nothing and is not refused.

A test or check run that points Blowhorn's Chrome folders at a throwaway
folder under the system temp directory (`BLOWHORN_USER_DATA_DIR`,
`BLOWHORN_CHROME_DATA_DIR`, `BLOWHORN_CHROME_AUTOMATION_DATA_DIR` or
`BLOWHORN_ATTACH_CHROME_DATA_DIR`) starts Chrome on that folder with
`--use-mock-keychain` and `--password-store=basic`, so macOS never asks
for a keychain. Your own Chrome, and any folder outside the temp
directory, never gets those switches: its cookies were encrypted with
your keychain's key.

The extension's native host reads one more thing, only to answer the
toolbar popup: it looks for the extension's own random identifier in
the extension's own IndexedDB files,
`<profile>/IndexedDB/chrome-extension_<extension id>_0.indexeddb.leveldb/`
under the data directory of the Chrome that started it (its
`--user-data-dir`, else Chrome's default), to learn which Chrome profile
is asking. It
reads no other extension's files and nothing else in the profile, and
writes nothing there.

## The mapping

Each Blowhorn profile maps to one real Chrome profile on this computer,
kept in your account and keyed by hostname. The mapping does not follow
you to another computer.

`blowhorn chrome profiles` lists every profile Chrome knows, with the
directory name and the display identity. Chrome does not have to be
running. `blowhorn chrome suggest` prints a proposed mapping for every
Blowhorn profile your account knows. `blowhorn chrome map <profile>
<directory>` writes one mapping; it checks the directory exists in
Chrome and refuses a name Chrome no longer has. `blowhorn chrome unmap
<profile>` removes one mapping. A mapping is identity, never
permission: it says where the run acts, not what it may do, and there
is never a fallback to another profile.

### Pairing

The Chrome extension drives whichever Chrome profile it is installed in, so a
mapping alone cannot stop a run from acting in the wrong one. `blowhorn chrome
map` therefore also pairs the profile: it opens the extension's pairing page in
the mapped Chrome profile, and the page keeps a token tied to this computer, the
Blowhorn profile and the Chrome directory. The token is derived from a random
key Blowhorn keeps on this computer (`chrome_pairing.key`, readable only by you);
it carries no account data. The extension keeps it in its own storage (the
`storage` permission, which shows no install warning) and reports it when a run
connects.

Before any action, a run checks the token. It refuses with one sentence when
the Chrome profile is not paired, is paired to another Blowhorn profile (the
sentence names both and the Chrome directory to switch to), or is paired to a
mapping this computer no longer has.

The same key also guards the bridge between a run and the extension. The
socket the run connects to (`chrome_extension.sock`, beside the key) is
readable and writable only by you, and the native host forwards nothing a
run sends until that run's first message proves it knows a secret made
from the key. The secret is per install, not per profile, and the host
keeps it to itself: it is checked and removed before anything reaches the
extension, so a program on this computer that cannot read the key cannot
drive your Chrome through the bridge, however its messages are shaped.

To pair, or to pair again after the
extension was reinstalled, map the profile to the directory it already has:

```bash
blowhorn chrome map ada 'Profile 2'
```

On the desktop app, the Chrome card on a profile has a pair again button that
does the same. An extension older than pairing cannot report a token; the run
says so once on stderr and goes ahead. The check starts once Chrome updates the
extension to a version that pairs and you re-run `blowhorn chrome map` for each
profile.

## Launch modes

How the run reaches Chrome once the mapping holds:

- The extension default: the run drives your signed-in Chrome through
  the Blowhorn extension. No second browser, no Allow dialog in the
  happy path.
- Attach (`cdp`): the run attaches to the Chrome you have open over the
  debugging protocol. Needs a window open and the Allow dialog
  approved; a scheduled pass gets a short Allow window. Attach is never
  the default (the extension driver is). It is also the one mode that
  interrupts once per profile: opening Blowhorn's tab hands the running
  Chrome a new window through `open -na`, which brings Chrome forward
  once per profile, and the refocus afterwards is best effort, because
  since macOS 14 activation is a request the system may refuse. A
  scheduled `cdp` pass pays that interrupt once per profile too.
- Launch (`persistent`): the run launches Blowhorn's own Chrome from
  the automation directory, in a normal window placed off to the side
  (2500,60), never minimized and never hidden, with the previous app
  re-activated so it takes no focus. A minimized or app-hidden window
  puts the page into `visibilityState: 'hidden'` with timers throttled to
  about one second; the visible
  posture is what keeps a flow's waits running at pace.

Chrome is never launched headless and never replaced with bundled
Chromium: a headless run would announce itself to every site.

### The extension default

The extension driver starts no Chrome and launches no Playwright. One
mapped profile holds the bridge per run; a second run that wants it
while it is held stops with `another blowhorn run holds the Chrome
extension bridge (pid <pid>)`, naming the run that holds it, and does
nothing. The holding run sends a heartbeat every 5 seconds, and a
holder that sends nothing -- no request, no heartbeat -- for
30 seconds is stale: the native host closes its bridge socket, a
waiting run may take the bridge, and any request the stale run left
unanswered is failed rather than handed to the next run, so a hung
run cannot wedge the runs behind it. A hello that omits the run's
version, or an installed extension older than the run needs, stops as
`extension_outdated` naming both versions. Anything the extension
cannot do is refused by name.

Under the extension default, `blowhorn profile auth` is a sign-in by
hand: it opens the platform's sign-in page once in your mapped Chrome
profile, types nothing, and waits a bounded time for you to finish
signing in, then confirms the session once.

## `blowhorn chrome status`

Whether Google Chrome is installed, whether it is running, and whether
its debugging switch is on. On macOS the installed path is
`/Applications/Google Chrome.app`, then `~/Applications/Google Chrome.app`
(the first one there wins); on Linux the `PATH` names and
`/opt/google/chrome/chrome`. A missing Chrome stops the run with
`ChromeNotInstalled` before any driver starts.

## Flags

`--profile` and `--chrome-profile` pin one Chrome profile for one run.
`--chrome-launch` pins the launch mode for one run. `--pace`,
`--headless`, and `--dry-run` behave as they do everywhere.

## Linux

The `extension` and `persistent` drivers run on Linux as on macOS; the
`cdp` attach driver is macOS only. Chrome is found by its `PATH` names
and `/opt/google/chrome/chrome`. Everything else on this page reads
the same.

## A dedicated attach Chrome (no Allow dialog) {#a-dedicated-attach-chrome-no-allow-dialog}

`blowhorn chrome attach-chrome` starts a second Chrome on a tree of
its own (`~/.blowhorn/attach-chrome`), open to remote debugging, so
`--chrome-launch cdp` can attach unattended with no Allow dialog.
Chrome 136 and later ignore the debugging switch on the default data
directory, which is why this is never your daily Chrome.

The port is bound to `127.0.0.1` and has no password, and `127.0.0.1`
is shared by every macOS user on this Mac: any program running as you,
or as any other user signed in here, can drive that Chrome and read its
cookies. So the route is off by default: `start` and `install-agent`
refuse unless you pass `--allow-other-users`, and print that warning
when they run. Sign it in only to the accounts Blowhorn posts from. The
desktop app does not offer it. The tree and every folder Blowhorn
creates under `~/.blowhorn` are owner-only (`0700`).

A debugging port, and Playwright's `--remote-debugging-pipe`, each make
Chrome report `navigator.webdriver` as `true`. `start` and launch mode
both pass `--disable-blink-features=AutomationControlled` and
`--test-type`, which keeps the flag `false` and leaves the
unsupported-flag infobar off.

| action | what it does |
| --- | --- |
| `status` (default) | reads the tree's `Local State`, `DevToolsActivePort` and `SingletonLock`; opens nothing |
| `signin` | opens the tree with no debugging switch, for the one-time sign-in; quit it after |
| `start --allow-other-users` | launches Chrome detached with `--remote-debugging-port=0 --remote-debugging-address=127.0.0.1 --disable-blink-features=AutomationControlled --test-type`, then prints the setup steps |
| `stop` | DevTools `Browser.close`, waits, then `SIGTERM`; signals only the tree's own Chrome, never `SIGKILL` |
| `install-agent --allow-other-users` | writes and loads `~/Library/LaunchAgents/ai.blowhorn.attach-chrome.plist`, which runs `start` at each login and logs to `data/logs/attach-chrome-agent.*.log` (or `--log-dir`) |
| `uninstall-agent` | unloads and removes that LaunchAgent; Chrome keeps running |

Off macOS every action but `status` is refused by name, and nothing is
started, signalled or written.

It writes no configuration: pointing `chrome.data_dir` at the tree,
and `chrome.launch_mode` at `cdp` for scheduled jobs, stay your
explicit steps. A recorded port counts only while a live Chrome holds
the tree, and it is evidence, not proof. Before a `cdp` run attaches
to this tree, it checks with `lsof` that the recorded port is
listened on by the pid holding the tree, on loopback only, and
refuses otherwise. `--json` on `status` adds `holder_pid`,
`stale_port` and `held_without_debugging`.

## `blowhorn chrome extension-install`

Writes the native-messaging host file Chrome launches to reach the
local Blowhorn app. Re-run it after moving the checkout or
reinstalling the app; without a current host file the extension cannot
talk to the engine.

When a run needs the extension and finds it missing, stale, or outdated
in the run's mapped Chrome profile, it ensures it on demand instead of
failing with a manual step: it repairs the native host manifest and
launcher when missing or stale, registers the extension for that
profile's data directory when nothing is there yet, and re-probes hello
once. If the socket is still missing, the run fails naming what was
repaired and the one remaining step, usually to launch or relaunch
Chrome with that profile. A profile already carrying a Chrome Web Store
install is left alone: Chrome's updater owns it, and Blowhorn never
forces a store update. While another run holds the bridge, no ensure
runs. The same ensure runs ahead of a run with
`blowhorn chrome extension-install --profile <name> --ensure`
(or `--chrome-profile <directory>`); `--dry-run` writes nothing and
reports what it would do. The ensure never starts, restarts, or kills
Chrome, never touches an unmapped profile, and runs once per failure,
never in a loop. Note the registration file is per data directory, not
per profile: it offers the extension to every profile in that one data
directory. A missing native host manifest does not stop a run before the
ensure: the run goes straight to the ensure, and only says the manifest
is missing when the ensure could not write it. When the ensure repaired
or registered something and the extension then connects, the run says
so once on stderr, for example `repaired the native host manifest and
registered the extension; the Blowhorn extension (1.36.6) is connected`.

### The minimum extension version, both ways

The minimum is checked from both sides. A run refuses an extension older
than the oldest version this Blowhorn accepts (`extension_outdated`, or
the version-skew sentence) and ensures it as above. The app also tells
the extension that minimum: the native host's `host_status` answer
carries `min_extension_version` (host protocol 4). An extension older
than that minimum never shows "You're all set". Its popup says the
extension needs an update and offers **Upgrade** and **Check for
update**, and the extension asks Chrome for an update on its own, at
most once every ten minutes. An older host that sends no minimum sets
no floor.

Both buttons use Chrome's own update calls
(`chrome.runtime.requestUpdateCheck`), never `chrome://extensions`, and
the popup says what Chrome answered: an update downloading, up to date,
checked too recently (try again in a few minutes), or the check failed.
Chrome installs a downloaded update only while the extension is idle,
and the extension is rarely idle while the Blowhorn app runs, so the
extension restarts itself into a downloaded update as soon as no run is
at work: never while a run holds a tab or has not yet released its
input, however long it waits on you. The
ready popup keeps a quiet **Check for update** (or **Upgrade to** the
downloaded version once Chrome has one), so you can take an update
before you fall behind. A store update still needs the Chrome Web Store
to publish it first: Blowhorn never claims an update Chrome did not
report. An unpacked install gets nothing from the store; the popup says
so, and the ensure plus a Chrome relaunch is the way forward there.

The extension logs every check, every deferred update and every update
it applies (`upgrading from <old> to <new>`), and logs `updated from
<old> to <new>` when Chrome reports the update installed, in its service
worker's console.

## What a site sees: the user agent by driver

Your own user agent, on every driver. The extension and attach drivers
run inside your installed Chrome, so sites see the same agent string
your ordinary browsing sends. The launch driver starts that same
installed Chrome, never bundled Chromium, which would announce itself
as HeadlessChrome. A `--headless` request becomes the visible
background window for exactly this reason: headless Chrome sends
`HeadlessChrome` in every request while its hints still claim Google
Chrome. Visible, not minimized: a minimized window puts the page into
`visibilityState: 'hidden'` with timers throttled.

The launched window emulates nothing: the page reads the real screen, the real GPU and
your own permission state. A viewport override, a GPU switch or a blanket permission grant
each gave a reading no real Chrome gives, so the launch passes none of them (measured
2026-10-15).

To see it from the site's side, open the free check at
[Blowhorn Tells](https://tells.blowhorn.ai/) in the Chrome profile a run
uses. It lists the user agent, the automation flags and the other signals
a page can read.

## Extension mode: classic or background

With the extension driver, a run uses one of two behaviors:

| | classic | background |
| --- | --- | --- |
| Blowhorn's tab | opens inactive beside the tab you are on, in a Blowhorn group that is collapsed by default | opens inactive beside the tab you are on, in a Blowhorn group that is collapsed by default |
| focus emulation | from the first action that takes the debugger | from the first page load |
| Chrome's debugging bar | while an action holds the debugger, gone after a short idle period | for the whole run, from before the site loads |
| visible screenshot | captured through the debugger, without selecting the tab | captured through the debugger, without selecting the tab |
| input | synthetic unless `BLOWHORN_EXTENSION_INPUT=trusted` | trusted unless `BLOWHORN_EXTENSION_INPUT=synthetic` |
| bringing the tab forward | never. When Blowhorn needs you it turns the Blowhorn group red and opens it, posts a notification when "Tell me when something needs me" is on in Safety, and waits for you to click the tab | the same |
| no Chrome window open | that profile stops and you are asked to open a Chrome window. Opening one itself would bring Chrome in front of what you are doing. A post moves on to the next profile; other commands end there, and nothing that did not happen is recorded | the same |

background is the default. classic keeps the input and debugger behavior of
the Chrome Web Store build 1.12.10 (synthetic input, the debugger only while
an action holds it) with the same tab placement as background, and
`BLOWHORN_EXTENSION_ROLLBACK=classic` forces it on a computer.
Where the mode comes from, top wins:

| layer | spelling |
| --- | --- |
| this computer | `BLOWHORN_EXTENSION_ROLLBACK=classic` forces classic |
| one scheduled job | its `Driver Mode`: `extension-classic` or `extension-background` |
| your account | the extension mode on Settings, Chrome extension (saved as `extensionMode` in your Blowhorn preferences, so it follows you to every computer) |
| nothing set | background |

How the Blowhorn tab group sits beside your tabs between steps is one more
account setting: collapsed (the default) or open, saved as `chromeGroup` in
the same Blowhorn preferences, so it follows you to every computer. Set it on
Settings, Chrome extension, or with `blowhorn chrome extension-mode --group
open` (`default` clears it). A run reads it once when it starts.

## Blowhorn's desktop (Spaces)

If Blowhorn's Chrome work lives on its own macOS desktop instead of beside
your tabs, setup finds or makes that desktop for you, so you never have to
open Mission Control and create one yourself. Setup runs only when you
start it, never during a run, and it works in this order:

1. **Reuse.** If a second desktop or display already exists, setup
   offers it. This is a read-only check and asks nothing of you.
2. **One-click create.** With Accessibility granted at that click, the
   helper opens Mission Control, presses its "+" button for the display
   you chose, closes Mission Control, and confirms exactly one new
   desktop. Mission Control is on screen for a moment, and the desktop
   you were on and the app in front stay unchanged. It refuses when
   Mission Control is busy or the display already has 16 desktops.
3. **Guided click.** If Accessibility is declined or the press fails,
   Blowhorn opens Mission Control and points at "+". You click once,
   and Blowhorn detects the new desktop. It gives up quietly after
   60 seconds with no click.
4. **Beside.** Otherwise, the background tab next to your tabs, as
   always.

You can also set setup to guided-only (never touch Accessibility) or to
never (never create, never open Mission Control). If the desktop is
later deleted, runs never recreate it: they fall back to beside and
post one notification whose button re-runs setup. Where setup's choice
lives is per computer, not per account: a desktop belongs to the
computer it was made on, so it is recorded there and never synced.

Automatic creation needs one Accessibility grant, which System Settings
lists as Blowhorn (Privacy & Security, Accessibility). Blowhorn asks for
it only when you start setup, never during a run. Without it, the floor
is one click by you in a Mission Control Blowhorn opens for you. A
window on a desktop you are not looking at still reads as hidden to
the page, so a desktop is a place to keep the work, not a way to hide
it from detection.

`BLOWHORN_EXTENSION_ROLLBACK=1` still swaps the driver for Blowhorn's own
Chrome as before; it says nothing about the mode. `0`, `false` and `off` read
as unset; any other value is refused before the run starts. On Settings the
selector is your account setting; the description under it is the mode this
computer runs, and the card says when the variable overrides the account or
holds a refused value. The features a
mode sets are `placement`, `first_page`, `lease_at_goto`, `quiet_screenshot`,
`checkpoint_front` and `trusted_input`. `first_page` is background only: a new
Blowhorn tab first loads a blank page that belongs to the extension, then the
site, so the site is the tab's second page. A site loaded as a tab's first page
reads its window size as zero while it loads; as the second page it often reads
the real size, but not always (about half the time when measured on
2026-10-17). An extension too old for a background feature runs that feature
the classic way, and the run says so once on stderr and carries on, so the
store build 1.12.10 keeps working in background mode. A run whose mode is not
the default names it once on stderr: `extension mode: classic, from the
account setting`.

Typing follows the input row. In background mode each character is sent
through Chrome's debugger as a real key event, one character at a time on the
same shaped cadence as classic typing, and the field is read back after the
last character; a character with no key on a US keyboard (an emoji, an
accented letter) is inserted as text instead, which the page still reads as
real input. That is what lets X posting, threads, replies and X credential
sign-in run under the extension in background mode: X's editor and sign-in
form read their own input handling, which a written field value never
reaches. In classic mode typing writes the field's value or text with no
input event, and those X flows refuse by name there. Clearing a field
before typing stays a page-side clear in both modes.

In background mode Chrome's "started debugging this browser" bar stays up for
the whole run, and it goes away when the run ends. Closing it, opening
developer tools on Blowhorn's tab, or closing that tab takes the debugger away:
for the rest of that run every click, key press or quiet screenshot that needs
it fails as `input_revoked`, and the error names which of the three happened.
Run it again and leave the tab and the bar alone.

## `blowhorn chrome extension-mode`

```bash
blowhorn chrome extension-mode              # the mode a run would use, and why
blowhorn chrome extension-mode classic      # save classic to your account
blowhorn chrome extension-mode default      # clear it, so runs use background
```

With no mode it reads your account setting from Blowhorn and writes
nothing; when it cannot be read it says why (`account_error`) and shows
the cached setting a run would fall back to. With one it saves `extensionMode` to Blowhorn; sign in
first with `blowhorn auth login`. `--dry-run`, with a mode or `--group`, reads that stored account,
reports it with the change on top, and writes nothing; when the account cannot be read it says why
and changes nothing. `--json` prints one object: `mode`,
`source` (`rollback`, `account` or `default`), `account`, `account_error`,
`rollback`, `rollback_error`, `features` and `written`.

## `blowhorn chrome extension-status`

Whether the extension is installed, which version answers, and whether
it says connected. A version older than the run needs is the
`extension_outdated` refusal above.

It also reads each Chrome profile's `Secure Preferences`, then
`Preferences`, under the Chrome data directory for the extension's entry,
and lists every profile whose entry came from the Chrome Web Store
(`from_webstore`, or location `INTERNAL`) with its version, as
`webstore_profiles` in `--json`. A loaded-unpacked entry is not listed.
For a store install the report never says Load unpacked: a version too
old for this Blowhorn is told to update in `chrome://extensions`, and a
missing native host is told to run `blowhorn chrome extension-install`.
It writes nothing in that directory. A run itself does not stop there:
when it needs the extension it ensures it on demand, as
`blowhorn chrome extension-install` describes.

`--json` also carries `profile_states`: one item per Chrome profile
directory (`Default` and `Profile N` with a `Preferences` file), each
`{profile, state, version}`, read from the same two files. `state` is:

- `enabled` - the extension is in that profile and turned on.
- `disabled` - it is in that profile and turned off. The external route
  always adds it this way until you turn it on there.
- `removed` - Chrome added it from the external-extensions file and you
  removed it. Chrome does not add it again by itself; the store page can.
- `absent` - nothing is recorded there yet: Chrome has not opened that
  profile since the file was written, or no install route is on.

## `blowhorn chrome extension-enable`

```bash
blowhorn chrome extension-enable --chrome-profile 'Profile 1'
blowhorn chrome extension-enable --chrome-profile Default --chrome-profile 'Profile 1' --json
```

Asks Chrome to open the extension's Chrome Web Store page in each
Chrome profile you name, so you can turn the extension on there with one
click: **Enable now** where Chrome already added it turned off, **Add to
Chrome** where Chrome has not picked it up yet. Name a profile with
`--chrome-profile`, the directory `blowhorn chrome profiles` prints, more
than once for several. Each directory must be in Chrome's `Local State`,
the one file it reads; a directory Chrome does not have, or a blank one,
is refused before anything opens. It writes nothing, and whether you then turned the extension on
is read by `blowhorn chrome extension-status` (`profile_states`), never
by this command. `--dry-run` opens nothing.

`--json` prints `ok`, `dry_run`, `url` (the store page) and `profiles`,
one `{directory, display_name, opened, detail}` per profile, where
`detail` says why the page did not open (`chrome could not open the Chrome Web Store page: <reason>`). When it opened in no
profile, `ok` is `false` and the command exits 1.

## `blowhorn chrome open-profile`

```bash
blowhorn chrome open-profile kate
blowhorn chrome open-profile kate --sign-in linkedin
```

Opens a window in the Chrome profile the named Blowhorn profile is
mapped to on this computer, so you can look at it or sign in to a
platform there yourself. The mapping chooses the Chrome profile by the
same rule a run uses: with `--sign-in <platform>`, the mapping chosen
for that platform; without it, the profile's only mapping or its
default one. The window opens on that platform's sign-in page, or on a
new tab when no platform is named. Chrome shows the profile's own name
and picture in the window, so it cannot be mistaken for another Chrome
profile.

A profile with no mapping here, several mappings with none chosen, a
mapped directory Chrome no longer has, or a name or account that
drifted since the mapping was made is refused by name and nothing
opens: a mapping is identity, never a guess at another profile, and no
other Chrome profile is opened, read, or changed. Blowhorn asks Chrome
to open the window and steps back -- it drives nothing in it, attaches
nothing to it, and never restarts or closes Chrome, so a Chrome already
running just gains the window. It writes nothing. `--dry-run` opens
nothing.

`--json` prints `ok`, `dry_run`, `profile`, `platform` (the `--sign-in`
platform, or null), `url`, `directory`, `display_name`, `account`,
`opened`, and `detail`, which says why the window did not open
(`chrome could not open that chrome profile: <reason>`). When Chrome
could not be asked, `ok` is `false` and the command exits 1.
The Chrome that opens is the same handoff as `extension-enable`'s, so
on a throwaway Chrome folder under the system temp directory it carries
`--use-mock-keychain` and `--password-store=basic`, and on your own
Chrome it never does.

LinkedIn, X and Reddit work through your own Chrome, so `--sign-in`
with one of them is how you connect it: Blowhorn never asks for the
password. After you sign in, `blowhorn chrome discover` (the desktop's
**Check again**) sees the sign-in and records it as the profile's
account in your Blowhorn account.

## `blowhorn chrome create-profile`

```bash
blowhorn chrome create-profile
blowhorn chrome create-profile --json
```

Gives Blowhorn a Google Chrome profile of its own, for a Chrome that has
only its main profile. It asks Google Chrome to open a new window in the
profile directory `Blowhorn`, with the same handoff as `open-profile`
(`open -na "Google Chrome" --args --profile-directory=Blowhorn
--new-window chrome://newtab/` on macOS). Chrome is expected to make that
profile the first time and open the same one every time after, so running
it again should never make a second profile. Neither that, nor the name
Chrome gives the new profile, has been confirmed by a recorded check yet:
Chrome picks the name, often a generic one such as `Person 2`, and the
desktop then shows the profile as **Blowhorn's profile**. It maps nothing, reads no store and drives
nothing in the window: you sign in there to the sites Blowhorn should
use, then `blowhorn chrome discover` (the desktop's **Check again**)
finds the profile and its accounts. Setup's **Set up Blowhorn's
profile** runs it.

With `--json` it prints `ok`, `dry_run`, `directory` (`Blowhorn`),
`already_listed` (whether `Local State` listed the directory before this
run; `null` when that file could not be read), `url`, `opened`, and
`detail`, which says why the window did not open. Nothing after the open
is read back, so it never claims Chrome made the profile. No Google
Chrome is refused before anything opens, and a window Chrome could not be
asked to open exits 1.

## `blowhorn chrome discover`

```bash
blowhorn chrome discover
blowhorn chrome discover --json
```

The survey behind setup's Confirm troops step: for every Chrome profile,
who it is and which platform accounts it holds, with nothing applied.
It reads only this allowlist, and nothing else in Chrome's directory:

- `Local State` and each profile's `Preferences`: the profile's
  directory, display name and Google account identity fields (`name`,
  `user_name`, `gaia_name`) - no other `account_info` field.
- Each profile's `Login Data` (read-only): the saved-login **username**
  for an allowlist of hosts only - LinkedIn, X, Reddit, Hacker News,
  GitHub, Bluesky and Slack. Never the password column, never form data.
- Each profile's `Cookies`: the **value** of GitHub's `dotcom_user`
  cookie alone (the signed-in GitHub account), and for LinkedIn, X,
  Reddit and Slack only whether a session cookie is **present** -
  never its value, and never the encrypted value of anything. Hacker
  News's session cookie is not read at all.

No history, no LevelDB, no other profile file. A database Chrome has
locked or that does not parse reads as "not found", never as an error.

The text form prints one activity per profile: its identity, its mapping, and
one line per platform (`username`, `signed in`, or `-`). With `--json`
each profile also carries `resolution` - how its Google email resolves
against your account's users, under the same rule as profile creation:
`one` (with the user, and their account's social links for display
only), `several` (with the candidates), `none` (with the refusal's
sentence) or `no-email` - plus `proposed_slug` and `slug_state` (`free`,
`own`, `taken`, `invalid`) for the profile a confirm would create.
Discovery writes nothing to Chrome, and the social links it shows are
never treated as permission to post.

For LinkedIn, X and Reddit the account is the browser sign-in, so
discovery records it in your Blowhorn account. For each Chrome profile
mapped on this computer, in use, whose identity still reads `ok`, and
for each of those platforms that is in use there and that the mapping
picks this Chrome profile for:

- a sign-in registers the profile's account for that platform (a
  connection of that kind, `connected`, with no credential) and maps it
  to the profile, or reuses the one it already maps;
- a sign-in that ended marks that account `disconnected`. Nothing is
  deleted or unmapped;
- an account the profile turned off (`ignored`) is left as it is.

`--json` lists what was recorded in `accounts` (`profile`, `platform`,
`outcome` - `created`, `reconnected`, `disconnected`, `unchanged` or
`none` - and the `account`), and names each refusal in `account_errors`.
`--local` and `--dry-run` record nothing. The desktop app's Check again
runs this survey, which is how Home's Connect an account step and every
other computer learn the account is connected. `blowhorn profile status
--check-sessions` records its LinkedIn, X and Reddit verdicts the same
way.

## `blowhorn chrome confirm`

```bash
cat assignments.json | blowhorn chrome confirm --payload-stdin [--dry-run] --json
```

Applies a confirmed assignments document - what setup's Confirm troops
step sends. The document is read from stdin (`--payload-stdin` is
required), so a GitHub token or Bluesky app password inside it reaches
neither the command line nor the log:

```json
{"assignments": [{"directory": "Profile 2", "profile": "ada", "create": true,
  "platforms": {"linkedin": {"attach": true, "session": true},
                "github": {"attach": true, "token": "..."}}}]}
```

Per assignment, in order: resolve the target profile (the directory's
existing mapping, an existing profile named by `profileId` or `profile`,
or, with `"create": true`, a new profile in your Blowhorn account representing
the member `userId` names, or nobody for a brand; `email` and `subject`
are refused by name); store the attached platforms' credentials in
your Blowhorn account (usernames; `LI_CHROME_SESSION` / `HN_CHROME_SESSION`
naming the directory when `session` is set; `GH_TOKEN`; `BLUESKY_HANDLE`
with `BLUESKY_APP_PASSWORD`), never in a file on this computer; then write
the mapping with `chrome map`'s own checks; then record each attached
platform's username as the profile's account there; then record the
attached LinkedIn, X and Reddit sign-ins, as `chrome discover` does. Both
land in each result's `accounts`. A LinkedIn sign-in with no saved
username still becomes the account. Slack writes no key - its note says to
capture the session with `blowhorn profile auth --platform slack <profile>`.
A username omitted from the document is re-read from discovery.

An account is a connection in your Blowhorn account linked to the profile with
`addConnectionToProfile`, the only way an account becomes a profile's. Its
name is the username, and its `metadata.url` is the account page
(`https://x.com/<handle>`, `https://github.com/<handle>`,
`https://www.reddit.com/user/<handle>`,
`https://bsky.app/profile/<handle>`) when the username has that
platform's handle shape, else the platform's home. The profile's handles
(the ones a post is attributed to and a self-amplify check compares) are
read from those pages and from nothing else: a sign-in email names no
page, so it is never taken for a handle. LinkedIn's sign-in is always an
email, so a LinkedIn account found here names no handle until you record
its page with `blowhorn profile accounts <profile> --page
https://www.linkedin.com/in/<name>`; until then an `Amplify` row on
LinkedIn for that profile is skipped by name. The same command records an
X page when the saved X login is an email. `blowhorn profile accounts
<profile> --map <id>` links an account you already have.

`in_use: false` on an assignment records that Chrome profile as not in
use: this computer's mapping for the directory is removed, the Blowhorn
profile is added to `defaults.exclude`, and the profile and its
credentials are kept. `attach: false` on a platform records that account
not in use in `.blowhorn.chrome-not-in-use.json` beside the config file.
The credential is kept, and a later run on this computer skips that
account. Marking the profile in use again removes the name from
`defaults.exclude`. Deleting the Blowhorn profile removes its recorded
per-platform choices with it, so an account it had marked not in use is
not skipped for a different profile later mapped to the same Chrome
profile; a Chrome profile recorded not in use as a whole stays recorded
that way, because that mark is about the Chrome profile itself.
Omitting `in_use` applies only the attached activities, as
an older document does. `chrome discover` reports `in_use` on the profile
and on each platform, so the next confirm screen can start a recorded
choice unchecked.

Each assignment answers for itself in `results` (`written` names keys,
never values), so a partial confirm is a successful confirm: the exit
code is 0 when at least one assignment landed, 1 when none did, and 3
on a store outage. A profile recorded not in use has `mapped` null.
`--dry-run` runs every check and writes nothing. No pairing page is
opened; pairing happens on the first run or through `blowhorn chrome map`.

## One run per profile and platform

A profile's session on a browser platform (LinkedIn, X, Reddit, Hacker
News) belongs to one Blowhorn process at a time on a computer. Before a run
opens the session it takes a lock keyed by profile and platform, under
every launch mode. A second run that wants the same profile on the same
platform is refused with "profile `<name>` on `<platform>` is in use by
another blowhorn process; wait for it to finish or stop it": that profile
is skipped, its activities stay queued, and a scheduled job leaves it for the
next pass. Different profiles, or different platforms of one profile,
can run side by side. See [You're in control](/docs/explanation/youre-in-control/).

## Related

- [You're in control](/docs/explanation/youre-in-control/) - every safety control in one place.
- [Install the Chrome extension](/docs/how-to/set-up/install-the-chrome-extension/) - install it.

- [Map Blowhorn profiles to Chrome profiles](/docs/how-to/set-up/map-chrome-profiles/) - write the mapping.
- [Choose how Blowhorn reaches Chrome](/docs/how-to/settings/launch-mode/) - when to leave the default.
- [Chrome extension permissions](/docs/reference/extension-permissions/) - what the extension may do.
- [Messages and exit codes](/docs/reference/messages/) - every refusal sentence.
- [Why Blowhorn uses your own Chrome](/docs/explanation/your-own-chrome/) - why your Chrome and not a bundled one.
