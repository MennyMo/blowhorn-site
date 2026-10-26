---
title: "Set up Blowhorn the first time"
description: "What each step of the desktop app's first-run setup does, and what it never does."
weight: 33
---


The guided setup opens by itself the first time you open Blowhorn, and every
time after that until you finish it. If you quit partway and you are still
signed in, it picks up at the step you left. If you are not signed in, it
starts at Sign in. Uninstalling removes that progress with the sign-in, so
the next open is a first run. If you set Blowhorn up before this setup
existed and you are still signed in, it doesn't open by itself. Updating
alone never opens it again; it reopens by itself, from the first step, only
when a new version of Blowhorn needs something your earlier setup did not do.

- **Sign in:** one screen does the welcoming and the signing in: Major
  Blowhorn says hello and asks for your papers. Sign in to your Blowhorn
  account, or choose **Create account**.
  Both open your browser and bring you straight back to the app. Create
  account opens the sign-up page, and once you confirm your email the
  app moves on by itself. There is no extra page asking you to allow it. If the browser attempt fails, or you close it before
  finishing, **Cancel** on
  the waiting screen stops the wait right away - you never have to wait
  it out - and **Open it again** ends the old attempt and starts a fresh
  one. See [Create a Blowhorn account](/docs/how-to/set-up/create-an-account/).
- **Blowhorn's Chrome profile:** before the list of Chrome profiles, one
  screen explains how Blowhorn works in Chrome. It works in a Chrome
  profile set aside for it, never the one you browse in, so your own
  windows, tabs and sign-ins stay as you left them while it posts, likes
  and connects for you. Chrome's main profile, the one Chrome made first,
  stays yours: Blowhorn can't work from it. If it is the only profile you
  have, the next screen asks you to add one for Blowhorn in Chrome (your
  profile picture, then **Add**), sign in there to the sites Blowhorn
  should use, then choose **Check again**. Nothing is read or saved on
  this screen; **Show my Chrome profiles** moves on.
- **Assign troops:** Blowhorn shows what it found in each Chrome
  profile: the Google account, and the platform accounts signed in or
  saved there. Mark each Chrome profile and each account **in use** or
  **not in use**. For a profile that isn't in Blowhorn yet, confirm the
  name it will be created under. The profiles you mark in use are the ones
  the next step installs into, and a profile you mark not in use is left
  alone. Chrome's main profile is listed as yours, with no **Use with
  Blowhorn** switch; a main profile an earlier setup already mapped keeps
  its switch. On **Confirm**, Blowhorn creates the profiles you marked in use,
  saves the handles (and a GitHub token or Bluesky app password you type
  on the activity), and maps each of those Chrome profiles. A profile you mark
  not in use is recorded that way: its mapping on this computer is
  removed, and a run of every profile skips it. A profile you had already
  excluded stays excluded. Marking it in use again removes that skip only
  when this screen added it. The Blowhorn profile and its saved sign-in
  stay. An account you mark not in use is skipped on this computer, and
  its saved sign-in stays too. Nothing is created or
  installed until you confirm. See
  [Map Chrome profiles](/docs/how-to/set-up/map-chrome-profiles/).
- **Getting ready:** Blowhorn finds your Chrome profiles and adds its
  extension only to the ones you marked in use on Confirm troops. If that
  is all of them, it uses Chrome's policy route: macOS asks for your
  administrator password once, and Chrome turns the extension on in every
  profile and shows it as **Managed by your organization**. If you left
  some profiles out, there is no administrator prompt; each profile you
  chose gets an **Enable in** button instead: one click there, then
  **Enable now** (or **Add to Chrome**) in Chrome. Each step shows as it
  runs, with the time left, and **Start again** appears if it takes
  longer than usual. A computer that already has the extension from an
  earlier setup keeps that setup's route; there, each profile you chose
  gets an **Enable in** button the same way. One ready profile you chose
  is enough to go on. See
  [Install the Chrome extension](/docs/how-to/set-up/install-the-chrome-extension/).
- **First post:** write a post and pick where it goes. It lands in your queue
  as a draft, and nothing is posted until you approve it in Content. You can
  also skip this. See [Post content](/docs/how-to/publish/post-content/).
- **Home:** you're done. Connect your platform accounts any time. See
  [Platform accounts](/docs/how-to/set-up/platform-accounts/).

## Leaving a Chrome profile out

A Chrome profile you leave unchecked on Confirm troops is not in use, and
guided setup leaves it alone: it gets no extension from this setup, no
Blowhorn profile and no mapping.

If you run guided setup again and leave out a profile that an earlier
setup already put the extension in, this setup cannot take the extension
out of that one profile. Both routes Chrome gives Blowhorn for adding an
extension - the policy file and the external-extensions file - are one
file for all your Chrome profiles, never one per Chrome profile, so neither can
be removed for a single profile. The extension stays in that profile
until you remove it there yourself (in that profile, open
`chrome://extensions` and remove Blowhorn). This setup never adds it
again, never maps that profile, and its being ready there counts for
nothing here.

## The rest of the app stays limited until Getting ready

- **Limited until then:** the rail's places other than Home, and New activity,
  stay locked until you're signed in and the extension is ready. Home, and
  any place you already opened, stay on screen, and anything that would
  take you somewhere else - a rail item, the menu bar's buttons, a capture
  link - brings you back to Home instead. There is no separate training
  page. While the guided setup is open it fills the window, with no rail
  beside it; sign in from the sign-in step. The
  rail does not add another Sign in, and it hides this computer's status
  until you are signed in. After setup, if you are signed out, Home's
  **Finish setting up** opens the guided setup again. The menu bar shows
  **Welcome to Blowhorn** and one **Open Blowhorn** button, which opens the
  console, instead of a pause or an error; signed in with the extension not
  ready yet, it shows **Finish setting up** and the same one button. When you are
  signed in, the account button stays usable, so you can still sign out or
  open the docs.
- **It checks for real:** the lock reads your actual sign-in and extension
  state each time you come back to the window, so signing out later locks it
  again until you sign back in. The extension counts as ready once it's
  turned on in at least one Chrome profile, set to install by your
  organization's policy, or answering. Getting ready never adds the
  extension twice: once Chrome is set to add it, it writes nothing again.
- **Open it again any time:** choose **guided setup** at the bottom of
  Settings.
- **Missing tools come first:** if Blowhorn's own tools aren't set up on this
  computer yet, the Setup screen shows first. See
  [Install the app](/docs/how-to/set-up/install-the-app/).

## Going back and forward is safe

- **Next checks first:** each step checks that its work is really done (you're
  signed in, the extension is ready in at least one Chrome profile you marked
  in use, your choices are saved) before it lets you go on. If it isn't, the
  step says why, right under the button.
- **Back never redoes harmful work:** going back and forward again skips what's
  already done. The extension is never added twice, sign-in is not repeated
  while you're signed in, and your first post is never added to the queue
  twice.
- **Re-checking is fine:** finding profiles again and changing a choice are
  safe to repeat.
- **No pop-ups:** every status and every reason shows on the step itself,
  including when your progress couldn't be saved.
