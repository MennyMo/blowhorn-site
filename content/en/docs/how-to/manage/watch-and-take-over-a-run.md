---
title: "Watch, pause or take over a run in Chrome"
description: "Open the Blowhorn side panel to see what Blowhorn is doing in Chrome, pause or stop it, and take over for a sign-in or a check."
weight: 185
---


When Blowhorn works in your Google Chrome through the extension, the Blowhorn side
panel shows what it is doing and lets you stop it, pause it, or take the tab
over for a sign-in or an are-you-human check. Nothing is added to the pages
Blowhorn works on: the panel is part of Chrome, beside the page.

## Open the panel

Click the Blowhorn button in Chrome's toolbar. The side panel opens on the
right of the window. If you do not see the button, open the extensions menu
(the puzzle piece) and pin Blowhorn.

With nothing running the panel says so. Below the run, **This Chrome
profile** shows whether this profile is linked and ready, as the toolbar
button did before (see [Install the Chrome extension](/docs/how-to/set-up/install-the-chrome-extension/#check-it-from-the-toolbar)).

## Watch a run

While a run works, the panel shows:

- the task, such as **Post the queue**, and the site it is on;
- the address of the Blowhorn tab;
- each step as a short line: done, in progress, or failed. Typing is one
  line; the panel never shows what was typed.

## Pause and resume

Click **Pause**. Blowhorn finishes the step it is on, then does nothing at all,
in any tab, until you click **Resume**. A paused run is not timed out and is
not counted as a failure.

## Stop a run

Click **Stop**. Blowhorn finishes recording the post it is on, then does
nothing more in any tab and lets go of the tab. The run is recorded as stopped
by you, never as failed or as a crash; a scheduled activity that was not yet
posted goes back to the queue for its next turn.

If Blowhorn had already clicked Post, it records that post as clicked but not
confirmed and does not post it again. Check the profile on the site before you
retry it. Stop between steps when you can.

Known limit: the panel does not remember its state when Chrome restarts the
extension's background worker.

## When Blowhorn needs you

When a site asks for a sign-in, a two-step code or an are-you-human check,
Blowhorn waits. The Blowhorn button shows **!**, the Blowhorn tab group turns
red and reads **Blowhorn needs you**, and the panel says what is needed.

1. Click **Take over**. Chrome brings the Blowhorn tab and its window to the
   front. Blowhorn does nothing while you have the tab.
2. Sign in or finish the check in that tab.
3. Click **Give back**. Blowhorn carries on from the page you leave it on; it
   reads the page again rather than repeating what it did.

You can also sign in in the red tab without opening the panel, as before:
Blowhorn notices when you are done.

You can take over at any time, not only when Blowhorn asks, and give back the
same way.

## Related

- [Chrome extension permissions](/docs/reference/extension-permissions/) - what
  the side panel permission allows.
- [Fix the Chrome extension connection](/docs/how-to/troubleshoot/extension-connection/)
