---
title: "Sign in"
description: "Sign in to your organization from the app or the command line."
weight: 32
draft: true
---


Sign in to your organization so Blowhorn knows your plan: how many profiles
you can run and which platforms you can post to.

**Early access:** sign in from the command line or from the desktop app.
Both go through your browser, and the command line keeps a Blowhorn API
token in the macOS Keychain.

## From the command line

```bash
blowhorn auth login
```

The command opens [Blowhorn](https://cloud.blowhorn.ai) in your browser. Sign in there, or create an
account with the page's Sign up link (`blowhorn auth login --sign-up` opens
the sign-up page directly). There is no page asking you to allow the app:
once you sign in, or confirm your email after signing up, the browser comes
back to Blowhorn and the command:

1. keeps a Blowhorn API token: Blowhorn issues it for this sign-in, and
   it is separate from your browser session. It is listed, named Blowhorn,
   among your tokens in Blowhorn, where you can revoke it. The command
   keeps it in the macOS Keychain, or elsewhere in a `cloud-token` file only
   you can read, beside `cloud.yaml`, and never prints it. Signing in again
   revokes the token the previous sign-in kept; if that fails, the command
   says so and you can revoke it in Blowhorn's token list.
2. writes your organization and name to `cloud.yaml`, replacing those of
   whoever signed in before.
3. reads your plan once. If your account does not include Blowhorn yet, it
   opens [Blowhorn](https://cloud.blowhorn.ai) in your browser to start
   using the Blowhorn beta. There is no form to fill in.

If no answer comes back within five minutes, the command stops; run it
again. A sign-up waits ten minutes instead, because email verification
comes first: if that wait runs out, verify your email, then sign in with
`blowhorn auth login`. Your account is kept, so do not create it again.
If your browser shows an update page, update Blowhorn. If it shows
a Blowhorn error page instead of coming back, Blowhorn refused the
sign-in; if it happens again, send us the page's message. `blowhorn auth login --dry-run` prints where it would sign you in and
opens, waits for and saves nothing.

Then check what the plan says:

```bash
blowhorn auth status
```

`auth status` reports the token as configured (never its value), the
organization id, and the plan it read. It writes nothing.

A token you export as `BLOWHORN_CLOUD_TOKEN` wins over the saved one.

The saved token is not renewed. When Blowhorn stops accepting it, a
publishing run asks you to sign in: run `blowhorn auth login` again.

On a Mac, after Python is upgraded or Blowhorn's environment is rebuilt, the
Keychain asks once whether `python` may use the saved sign-in. Choose
**Always Allow**; a scheduled run cannot answer that prompt for you.

## From the app

Open `blowhorn://signin`, the link offered by **Sign in** in the Blowhorn extension in
Google Chrome. The app opens [Blowhorn](https://cloud.blowhorn.ai) in your browser; sign in there, or create
an account, then choose **Allow**. `blowhorn://signup` starts the same sign-in for a new account
(see [Create a Blowhorn account](/docs/how-to/set-up/create-an-account/)). The sign-in sends its
answer to the command line on this computer (`127.0.0.1`), and the app comes
forward with the sign-in finished. The browser tab says **Authorization complete**
and usually stays open: close it, or choose **Return to Blowhorn** to bring the app
forward. Now and then the tab closes on its own. The token is kept by Blowhorn's command line, never by
the app. If the browser stays on an update page, update Blowhorn. If it stays on a Blowhorn error page instead, the sign-in was refused: no answer comes back. If Blowhorn cannot be reached at all, the app says it could not reach cloud.blowhorn.ai: check your connection, then try again. In guided setup, **Cancel** on the
waiting screen stops the wait at once; left alone, the app tells you
you're not signed in once the wait runs out. Try again, and if that page
comes back, send us its message.

The sign-in opens one browser tab, the sign-in page, and nothing after it: the app
does not open a second tab once the sign-in answer arrives. If your account has no
Blowhorn plan yet, open [Blowhorn](https://cloud.blowhorn.ai) yourself, or choose
**Your account and plan** in the app's account menu, to start the beta there.

## Sign out

In the app, open the account menu at the bottom of the rail and choose **Sign
out**. The app takes you to the sign-in screen, where **Sign in with your
browser** signs you back in, as the same account or another. From Terminal:

```bash
blowhorn auth logout
```

Signing out removes this computer from Blowhorn first. That revokes the
saved Blowhorn API token. Blowhorn then removes the token, the organization
and name in `cloud.yaml`, and the cached plan check on this computer. If the
token is already gone, sign-out still finishes. If Blowhorn cannot be reached
to revoke it, the command says so; revoke it in Blowhorn's token list. If you exported
`BLOWHORN_CLOUD_TOKEN`, unset it in the shell too. Queued posts and profiles
stay where they are. `blowhorn auth logout --dry-run` lists what it would
remove and removes nothing.

## Related

- [Install the app](/docs/how-to/set-up/install-the-app/) - download and first muster.
- [Add a profile](/docs/how-to/set-up/add-a-profile/) - create a profile once you are signed in.
- [The Blowhorn app, screen by screen](/docs/reference/use-the-desktop-app/) -
  the Setup screen.
