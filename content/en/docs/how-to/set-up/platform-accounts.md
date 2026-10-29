---
title: "Sign a profile in to each platform"
description: "Browser sign-ins, tokens, and app passwords each profile needs before it can post."
weight: 65
---


One section per platform. LinkedIn, X, and Reddit sign in by hand in your
Google Chrome; Bluesky takes a handle and an app password; GitHub takes a token;
Hacker News takes a username and password, or a confirmed Chrome session;
Slack takes a captured session.

Do the mapping first
([Map Blowhorn profiles to Chrome profiles](/docs/how-to/set-up/map-chrome-profiles/)):
every browser sign-in below opens in the profile's mapped Chrome.

## LinkedIn, X, Reddit

Blowhorn never asks for these passwords. The account is your own sign-in,
in the Chrome profile your Blowhorn profile is mapped to.

In the desktop app, open **Profiles**, pick the profile, and find the
platform's card. It says which Chrome profile to use ("Sign in to LinkedIn
in the Chrome profile Work"). Choose **Open LinkedIn sign-in** to open that
Chrome profile on LinkedIn's sign-in page, sign in there, then choose
**Check again**. Once Blowhorn sees the sign-in, it records it as the
profile's account in your Blowhorn account, and the card says
**Connected**. Home's **Connect an account** button opens the same steps
for your own profile. The card holds only that guidance, **Open LinkedIn
sign-in** and **Check again**: it has no fields to fill in and never asks
for a password. An account Blowhorn should sign in to for you with a stored
username and password is set up from Terminal only (below).

**Check again** reads **Checking…** while Blowhorn reads your Chrome
profiles, then says what it found: the platforms it found in each Chrome
profile, which are new since your last check and which are no longer
signed in (Blowhorn then marks that account disconnected), **Nothing new
found**, or why it couldn't read Chrome. Setup's Chrome profiles step and **Profiles ›
chrome profiles** answer the same way. Chrome saves a new sign-in to disk
about 30 seconds after you sign in, so if you signed in a moment ago and
see **Nothing new found**, wait a little and check again.

From Terminal, the same two steps:

```bash
blowhorn chrome open-profile ada --sign-in linkedin   # sign in in the Chrome window that opens
blowhorn chrome discover                              # records the sign-in as ada's account
```

Each keeps a persistent Chrome session. Refresh it with `profile auth`.
With a username and password stored in the profile's credential in your
account (`LI_USERNAME` and `LI_PASSWORD`, `X_USERNAME` and `X_PASSWORD`,
`RDDT_USERNAME` and `RDDT_PASSWORD`, written with `blowhorn profile set`;
the app never asks for them), the login is attempted for you; otherwise
the browser opens and you sign in by hand.

```bash
blowhorn profile auth --platform linkedin --profile ada
blowhorn profile auth --platform x --profile ada
blowhorn profile auth --platform reddit --profile ada
```

With `--headless` the browser still opens as a background window and only
the automated login is attempted; the manual fallback is skipped. A
CAPTCHA or second-factor challenge always hands back to you: unattended
runs never wait for a person.

LinkedIn can also work from a **confirmed Chrome session** instead of a
stored password: when setup's Confirm troops step found you signed in to
LinkedIn in a Chrome profile and you confirmed it, the profile holds
`LI_CHROME_SESSION` naming that Chrome profile, and runs use the session
in the mapped Chrome profile. If that session signs out, sign in again in
Chrome; there is no password for Blowhorn to fall back to unless you store
one too.

### Record your LinkedIn page

Blowhorn finds your LinkedIn sign-in, which is an email, never your
`/in/` name. Without that name it cannot tell your own posts from anyone
else's, so it skips any `Amplify` row on LinkedIn for the profile and says
why. Record the page once, on the LinkedIn account already mapped to the
profile:

```bash
blowhorn profile accounts ada --page https://www.linkedin.com/in/ada-example
```

Do the same with your `https://x.com/<handle>` page when your saved X
login is an email.

## Bluesky

Log in with a handle and an app password. The pair is stored only when
Bluesky accepts it, so a refused credential is never saved.

```bash
blowhorn profile auth --platform bluesky --profile ada
```

In a terminal it asks for both (the stored handle is the default; a blank
app password keeps the stored one). Supply them without a prompt with
`--handle` and `--app-password-stdin`. Otherwise the stored pair is logged
in with and nothing is written. Make the app password in your Bluesky
account settings; your main password never goes here.

## GitHub

Store a personal access token as the profile's `GH_TOKEN`. It lands in the
profile's GitHub credential in your account:

```bash
blowhorn profile set ada GH_TOKEN=<token>
```

Then validate it without following or reacting to anything:

```bash
blowhorn profile status --profile ada --check-platform github
```

The check reports the login the token signs in as and its scopes. A
classic token needs `user:follow` to follow and `repo` to react; a
fine-grained token needs read and write on Followers to follow, and on
Issues (and Pull requests for PR targets) to react.

## Hacker News

Store the login with `profile set`. Both keys are needed; the password is
read from your account:

```bash
blowhorn profile set ada HN_USERNAME=<account> HN_PASSWORD=<password>
```

Or work from a **confirmed Chrome session**: if setup's Confirm troops
step found you signed in to Hacker News in a Chrome profile and you
confirmed it, the profile holds `HN_CHROME_SESSION` naming that Chrome
profile instead of a password, and runs use that session. If it signs
out, sign back in in Chrome, or store a password as above.

Check it landed, with the password shown only as set or not set:

```bash
blowhorn profile get ada
```

## Slack

Capture your signed-in web session into the profile's Slack credential in
your account:

```bash
blowhorn profile auth --platform slack --profile ada
```

A browser window opens; sign in to Slack, and the session is extracted. No
Slack app install is needed. To capture a new workspace, name it:

```bash
blowhorn profile auth --platform slack --profile ada --workspace acme.slack.com
```

Omit `--workspace` to refresh every workspace already listed under
`slack_workspaces` in that credential.

## Related

- [Map Blowhorn profiles to Chrome profiles](/docs/how-to/set-up/map-chrome-profiles/) - the
  mapping every browser sign-in opens in.
- [Post content](/docs/how-to/publish/post-content/) - publish once every platform
  is signed in.
- [Profile reference](/docs/reference/profiles/) - where each credential
  is stored.
- [Eligibility](/docs/explanation/eligibility/) - a credential is
  permission.
- [Requirements](/docs/reference/requirements/) - what each computer needs
