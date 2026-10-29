---
title: "Chrome extension permissions"
description: "Each permission the Blowhorn extension asks for, the sites it runs on, and why."
weight: 220
---


What the Blowhorn extension may do, and why each capability exists.
The extension acts only on requests from the Blowhorn app on your computer;
it makes no requests of its own to any server, sells no data, and
injects no ads. Its single purpose is carrying out the posting,
engagement, outreach, export and session-check actions you queue or
start in Blowhorn, inside the Google Chrome profile you already use. Its
toolbar button shows status only; every change happens in the Blowhorn
app.

## Sites

The extension runs content only on the sites Blowhorn acts on, and
reads a workspace session only from its sign-in pages:

- `x.com`, `twitter.com`
- `linkedin.com`, `www.linkedin.com`
- `reddit.com`, `www.reddit.com`
- `facebook.com`, `www.facebook.com`
- `news.ycombinator.com`
- `mentorship.lfx.linuxfoundation.org`, `sso.linuxfoundation.org`
- `*.slack.com`

No other site is touched. You remain responsible for each destination's
terms and acceptable-use rules; Blowhorn gives you the controls, not
permission to ignore them.

## Permissions

| Permission | Why |
|---|---|
| `nativeMessaging` | Talks to the Blowhorn app on this computer. Every action is a request from that app |
| `alarms` | A one-minute alarm re-opens the connection to the app after Chrome suspends the worker, so a scheduled run finds the extension ready |
| `tabs` | Opens one background tab on a supported site, or reuses the one it opened earlier, so the action runs where you are signed in. It looks only among tabs on the sites above, only to find its own, and never navigates, drives or closes any other tab |
| `tabGroups` | In both [classic and background mode](/docs/reference/chrome/#extension-mode-classic-or-background), puts the tab it opened in a tab group named Blowhorn, right after the tab you were on, collapsed by default, so you can see which tab the app is driving and get back to yours. The group is a label: it never moves, selects or closes your other tabs, and a Chrome that cannot group still gets the tab. A screenshot is taken through the debugger and does not select the tab. Nothing brings the tab or the window forward; when Blowhorn needs you it renames the group "Blowhorn needs you", turns it red and opens it, posts a notification when "Tell me when something needs me" is on in Safety, then waits for you to click the tab |
| `cookies` | Reads cookies on the supported sites only when the app asks, to reuse a sign-in you already have. A cookie goes to the local app; the one the app keeps beyond your computer is your Slack workspace session, kept in your account as that profile's Slack credential |
| `debugger` | Delivers some of your queued clicks and key presses as real input (the rest, and all typing, go through the extension's own script on the page), watches the page's own requests to tell when an action finished, and takes a screenshot when the app asks for one. Attached only to the tab the extension opened. In classic mode it attaches when an action needs it and is released when the run ends or after a short idle period; in [background mode](/docs/reference/chrome/#extension-mode-classic-or-background) it attaches as soon as the extension opens or reuses its tab, before the site loads, and stays attached until the run ends. Chrome shows its debugging bar while it is attached; closing that bar, opening developer tools on the tab or closing the tab stops the extension using the debugger until the next run |
| `storage` | Keeps the pairing token `blowhorn chrome map` hands it in this Chrome profile, which tells the app which Chrome profile the extension is in so a run for another Blowhorn profile is refused before it does anything. It also keeps, in session storage that Chrome clears when it closes, the id of the tab and tab group the extension opened and whether you cancelled Chrome's debugging banner, so if Chrome restarts the extension's worker it reuses that tab instead of opening another one, and it does not attach the debugger again after a cancellation until the run ends. Nothing leaves your computer. Chrome shows no warning for this permission |
| `downloads` | Catches the one export you asked for (an analytics or connections export) for the app, then cancels and clears it. A finished file stays where it is; the extension never starts a download on its own |

## Related

- [Chrome reference](/docs/reference/chrome/) - install, status, and connection checks.
- [Platforms](/docs/reference/platforms/) - the sites above, per platform.
- [Where your data lives](/docs/explanation/your-data/) - what the extension reads and where it goes.
- [Install the Chrome extension](/docs/how-to/set-up/install-the-chrome-extension/) - install it.
