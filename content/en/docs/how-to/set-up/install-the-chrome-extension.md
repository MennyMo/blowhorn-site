---
title: "Install the Chrome extension"
description: "Add the Blowhorn extension in the Blowhorn app or from the Chrome Web Store, or load it unpacked in one profile."
weight: 40
aliases: [/docs/how-to/install-the-chrome-extension/]
---


Requires macOS 13 or newer and Google Chrome 142 or newer. See
[System requirements](/docs/reference/requirements/).

Blowhorn drives Google Chrome through its Chrome extension. Chrome keeps an
extension inside each Chrome profile, and the extension drives only the
profile it is installed in. Install it in every Chrome profile you post
from.

## In the Blowhorn app

The guided setup does this for you. On **Confirm troops** you mark each
Chrome profile in use or not in use, and **Getting ready**, the step
after, adds the extension only to the ones you marked. If that is every
Chrome profile on this computer, it uses Chrome's policy route: macOS
asks for your administrator password once. When more than one profile is
chosen, that one prompt covers every profile you chose. With one profile,
it is one prompt for that profile. The password request is named
**Blowhorn**: it is this install, and it writes Chrome's policy file once
so Chrome installs the extension, turned on, in every profile you chose.
Cancelling it writes nothing, and setup stops there and says why.
Before it asks, Getting ready tells you the request is coming and waits
for your Continue, so the prompt never appears over a screen that has
not warned you about it yet. Chrome
shows **Managed by your organization**; that is the install working, not
a problem. There is nothing to click in each profile.

If you left a profile out, no computer-wide file is written for the
others: both files above reach every profile, so either would put the
extension in the profile you left out. Each profile you chose instead
gets it one at a time, with the **Enable in** steps below - Chrome opens
Blowhorn's store page in that one profile, and your click there installs
it only there. A profile you leave out is never given the extension by
guided setup; if an earlier setup already put it there, setup cannot
remove it from that one profile - see
[Leaving a Chrome profile out](/docs/how-to/set-up/first-muster-setup/#leaving-a-chrome-profile-out).

A computer that already has the extension from an earlier setup - put
there by Chrome's external-extensions file - stays on that route
when you marked only some profiles in use. Chrome adds it turned off
there, so each profile you marked in use needs one click:

1. Next to a profile that says **Turned off** or **Not added yet**, press
   **Enable in** and the profile's name.
2. Chrome opens Blowhorn's store page in that profile. Click
   **Enable now** (or **Add to Chrome** if Chrome was already open).
3. The profile reads **Ready** in the app within a few seconds. A
   manual install during guided setup lands back in the app instead
   of opening the Blowhorn welcome page; outside guided setup, the
   welcome page is what opens.

When every profile is marked in use, guided setup writes the policy
file instead of staying on the external route, so Chrome turns the
extension on everywhere with nothing to click in each profile.

If Getting ready says **This is taking longer than usual**, press
**Start again**: Blowhorn stops the attempt still running and begins a new
one.

One ready profile is enough to carry on. On the external route, if a
profile still says **Not on yet** after a minute and a half, press
**Open** and the profile's name **again**. You can turn it on in more
profiles any time later.

## From the Chrome Web Store

Open the
[Blowhorn listing](https://chromewebstore.google.com/detail/fcflpiagmpcfifgknledeknedfopnapf)
(item `fcflpiagmpcfifgknledeknedfopnapf`) in each Chrome profile you post
from and choose **Add to Chrome**. Write the native host the extension
talks to, then confirm the extension answers:

```bash
blowhorn chrome extension-install
blowhorn chrome extension-status
```

An answered hello means the extension is loaded in some Chrome profile and
talking. The report also lists each Chrome profile with a Web Store
install and its version.

If it says the extension is too old for this Blowhorn, update it: open
`chrome://extensions`, turn on **Developer mode**, and choose **Update**
(or restart Chrome). Do not load it unpacked over a store install.

## Check it from the toolbar

On first install the extension opens the Blowhorn welcome page. Its
toolbar button shows the Blowhorn paw in grey until this Chrome profile
is ready, then in colour; hovering it names what is missing. Click it to
see what is missing, then follow its one button:

- **Download the Blowhorn app** - the app is not installed.
- **Update the Blowhorn app** - the app is too old for this extension.
- **Finish setup in Blowhorn** - Blowhorn changed in a way that needs the
  guided setup again; opens it in the app. Updating alone never asks for
  it again; it appears only when a new version of Blowhorn needs
  something the earlier setup did not do.
- **Sign in** - opens the app's sign-in.
- **Map this profile in Blowhorn** - opens the app's mapping screen for
  this Chrome profile.

When everything is in place the popup names the linked Blowhorn
profile and signed-in account, and offers **Change mapping**. The app
tells the extension which profile by its id as well as its name, so a
profile renamed in your Blowhorn account keeps its link.

After an update from a version that named the profile only, the popup
reads **Map this profile in Blowhorn** even for a Chrome profile that is
mapped. Nothing is lost: the mapping itself is unchanged. The popup
catches up the next time the app reads the mapping: after you sign in or
change a mapping.

## Load it unpacked in one Chrome profile

When only one Chrome profile needs the extension, write the native host and
follow the printed steps. Through the Blowhorn mapping:

```bash
blowhorn chrome extension-install --profile kate
```

By the Chrome profile directory, as `blowhorn chrome profiles` prints it:

```bash
blowhorn chrome extension-install --chrome-profile 'Profile 12'
```

`--chrome-profile` can be given more than once. Either flag with
`--all-profiles` is refused. A `--profile` inherited from
`BLOWHORN_PROFILE` or `defaults.profile` does not count: type it on this
command.

The printed steps are: switch to that Chrome profile, open
`chrome://extensions`, turn on Developer mode, choose **Load unpacked**,
select the `extension/` directory the command names, then check with
`blowhorn chrome extension-status`. There is no file the command can write
that installs an extension in one profile only, so this route always ends
with those clicks.

See the files first, and write nothing:

```bash
blowhorn chrome extension-install --profile kate --dry-run
```

## Every Chrome profile on this computer

**Every profile** (the default) writes Chrome's
`ExtensionInstallForcelist`. Chrome installs the extension the next time
each profile starts, with no click in that profile. That is every Chrome
profile on this computer, including ones no Blowhorn profile uses. Chrome
shows **Managed by your organization**. macOS asks for an administrator
password once. Cancelling that dialog writes nothing. The policy is your
own macOS user's (`/Library/Managed Preferences/<you>/com.google.Chrome.plist`),
never the computer's, so the Chrome of another macOS user on this Mac is
left alone.

macOS names the process that asks, so the name on that dialog depends on
how Blowhorn was started. In the Blowhorn app, the app's bundled
installer asks, and the dialog names **Blowhorn**. From a terminal, the
engine asks through the Mac's own script runner, and the dialog names
**osascript** instead. Both are this install asking - the one write of
Chrome's policy file - and cancelling either writes nothing.

```bash
blowhorn chrome extension-install --all-profiles
```

**Ask in each profile** writes Chrome's external-extensions file instead, so
Chrome offers the install in each profile and you click once there. There is
no managed banner.

```bash
blowhorn chrome extension-install --all-profiles --external
```

On Linux both files live where only root can write. Blowhorn never asks for
root and refuses to run under `sudo`: a write it cannot make is refused
with the file, its exact content, and the one `sudo` command that writes
that file. Write that file, then run the plain install as yourself for the
host.

## See which route is on disk

```bash
blowhorn chrome extension-status
```

The report includes `Install route: policy`, `external`, or `none`. A
policy line ends `not confirmed in chrome`; an external line ends `waiting
for your click`. Those lines say what Chrome was asked to do, never that a
profile's copy was confirmed.

## From the desktop app

Settings has one **chrome extension** card, on its **Setup** page. The segmented control is the
route: **every profile** or **ask in each profile**. The button stays
**install chrome extension** either way. After the command, the card lists
one row per Chrome profile with the same words the terminal prints.

## Move an install made before the extension id changed

Installs made before the current store item used the retired id
`alogghnpabnbkmhgeceffnlcbcnlpoap`, which has no store listing and never
updates on its own. The native host still accepts that id beside the store id
`fcflpiagmpcfifgknledeknedfopnapf`, so an old copy can connect and tell you it
is out of date. Move it to the store install so Chrome keeps it current:

1. Run the install again with the flags you used the first time.
2. In each Chrome profile that loaded the extension unpacked, open
   `chrome://extensions`, remove the old copy, and choose **Load unpacked**
   again with the `extension/` directory.
3. If you used `--all-profiles`, remove the old id's entry by hand: the
   command adds and removes only the current id.
4. Check with `blowhorn chrome extension-status`.

Your profile mappings (`blowhorn chrome map`) do not name the extension id
and do not change.

## Related

- [Map Blowhorn profiles to Chrome profiles](/docs/how-to/set-up/map-chrome-profiles/) - which
  Chrome profile each Blowhorn profile belongs to.
- [Chrome reference](/docs/reference/chrome/) - the flags, the files, and
  the JSON shapes.
- [Requirements](/docs/reference/requirements/) - what each computer needs
