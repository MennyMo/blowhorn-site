# Sign a profile in to each platform


> Browser sign-ins, tokens, and app passwords each profile needs before it can post.



One section per platform. LinkedIn, X, and Reddit sign in by hand in your
Google Chrome; Bluesky takes a handle and an app password; GitHub takes a token;
Hacker News takes a username and password, or a confirmed Chrome session;
Slack takes a captured session; YouTube takes a Chrome sign-in, the
channel's address and, for analytics and the Data API, your own OAuth consent.

Do the mapping first
([Map Blowhorn profiles to Chrome profiles](/docs/how-to/set-up/map-chrome-profiles/)):
every browser sign-in below opens in the profile's mapped Chrome.

## LinkedIn, X, Reddit

Blowhorn never asks for these passwords. The account is your own sign-in,
in the Chrome profile your Blowhorn profile is mapped to.

In the desktop app, open **Profiles**, open the profile, and go to its **Browser**
tab. Pick the Google Chrome profile on the left and find LinkedIn on the right. Choose
**Set up**: it says which Chrome profile to use ("Open the Work Chrome profile and
sign in to LinkedIn there"). Choose **Open in Chrome** to open that Chrome profile on
LinkedIn's sign-in page, sign in there, then choose **Discover** at the top of the
list. Once Blowhorn sees the sign-in, it records it as the profile's account in your
Blowhorn account, and the row says it found you signed in. Home's **Connect an account**
button opens the same steps for your own profile. The set-up steps hold only that
guidance and **Open in Chrome**: they have no fields to fill in and never ask for a
password. An account Blowhorn should sign in to for you with a stored
username and password is set up from Terminal only (below).

**Discover** reads **Checking…** while Blowhorn reads your Chrome
profiles, then says what it found: the platforms it found in each Chrome
profile, which are new since your last check and which are no longer
signed in (Blowhorn then marks that account disconnected), **Nothing new
found**, or why it couldn't read Chrome. Setup's Confirm troops step and the **Browser** tab of any profile answer the
same way. Chrome saves a new sign-in to disk
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

LinkedIn, X, Reddit and Hacker News can also work from a **confirmed
Chrome session** instead of a stored password or typed username: when
setup's Confirm step found you signed in to one of them in a Chrome
profile and you confirmed it, the profile holds a session key naming that
Chrome profile (`LI_CHROME_SESSION`, `X_CHROME_SESSION`,
`RDDT_CHROME_SESSION`, `HN_CHROME_SESSION`), and runs use the session in
the mapped Chrome profile. Setup does not ask for your username: the
session is the account, and a background session check reads the account
name off the signed-in page and records it when the profile has none yet.
If that session signs out, sign in again in Chrome; there is no password
for Blowhorn to fall back to unless you store one too.

### Record your LinkedIn page

Blowhorn finds your LinkedIn sign-in, which is an email, never your
`/in/` name. Without that name it cannot tell your own posts from anyone
else's, so it skips any `Amplify` row on LinkedIn for the profile and says
why. A session check (`blowhorn profile status --check-sessions`, which
the app runs in the background) reads the name off your signed-in LinkedIn
feed and records it when the profile has none yet; it never replaces a page
you recorded. To record the page yourself, once, on the LinkedIn account
already mapped to the profile:

```bash
blowhorn profile accounts ada --page https://www.linkedin.com/in/ada-example
```

The same session check reads your X handle and Reddit username off their
signed-in pages when a saved login did not name them; recording your
`https://x.com/<handle>` page yourself is the fallback when the read has
not landed yet.

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

Store the login with `profile set`. The password is read from your
account; the username is only needed when you sign in with a password:

```bash
blowhorn profile set ada HN_USERNAME=<account> HN_PASSWORD=<password>
```

Or work from a **confirmed Chrome session**: if setup's Confirm step
found you signed in to Hacker News in a Chrome profile and you confirmed
it, the profile holds `HN_CHROME_SESSION` naming that Chrome profile
instead of a password, and runs use that session. Setup does not ask for
your username: a background session check reads it off the signed-in
page's header and records it when the profile has none yet. If the
session signs out, sign back in in Chrome, or store a password as above.

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

## YouTube

Let the extension reach YouTube in the profile's mapped Chrome, and sign in
to the channel there by hand. In the desktop app, open **Profiles**, open the
profile, go to its **Browser** tab, pick the Google Chrome profile that has
**Turn on YouTube**, and choose it. From Terminal:

```bash
blowhorn chrome open-profile ada --sign-in youtube
```

A Blowhorn page opens in that Chrome profile: choose **Allow YouTube**, then
**Allow** when Chrome asks, then sign in to YouTube on the page it goes on
to. If Chrome says the page is blocked, the Blowhorn extension is not in
that Chrome profile yet: add it there first. **Discover** does not look for
a YouTube sign-in, so there is nothing to check afterward.

Only the Google Chrome profile a YouTube run would use has the button. If the
profile has several Chrome profiles and none is chosen for YouTube, choose one
first: in the desktop app, choose **Use this Chrome profile** on the one you
want. From Terminal:

```bash
blowhorn chrome map ada 'Profile 2' --for youtube
```

Then give the profile its channel: the channel's address by ID, like
`https://www.youtube.com/channel/UC...`. YouTube shows the ID at
[youtube.com/account_advanced](https://www.youtube.com/account_advanced)
while you are signed in to the channel.

In the desktop app, paste it into **Channel address** on the same
**YouTube** row of the profile's **Browser** tab (**Find your channel ID**
opens that YouTube page). It saves when you leave the field. To change it
later, choose the profile's **YouTube** row on its **Accounts** tab, which
opens that field; empty the field to remove the channel. From Terminal:

```bash
blowhorn profile set ada YT_CHANNEL_URL=https://www.youtube.com/channel/UC...
```

A handle address (`https://www.youtube.com/@name`) is refused with the
reason, in the app and by `profile set`, and nothing is saved: it names no
channel ID, and Blowhorn never guesses which channel a handle means. A
profile that already holds a handle address reads **Needs channel ID** on its
**Accounts** tab; choose that row and paste the address by ID. Until the
profile has a channel, its YouTube activities are not eligible.

### Give the YouTube Data API consent

Analytics, and uploads, comments, replies and likes through the Data API
instead of Google Chrome, need the profile's own OAuth consent. Uploads
through the Data API are experimental and have not been live-verified;
Studio in signed-in Google Chrome is the supported default when this
consent is not given. The consent is given to your own Google Cloud
OAuth client: Blowhorn ships none.

1. In the [Google Cloud console](https://console.cloud.google.com/), in a
   project of your own, enable the **YouTube Data API v3** and the
   **YouTube Analytics API**.
2. Set up the project's OAuth consent screen. While its publishing status
   is "Testing", add the Google account that owns the channel as a test
   user; Google then expires the consent after 7 days, so publish the app
   to keep it.
3. Create an OAuth client ID of type **Desktop app**, and store its ID and
   secret in the profile's credential:

   ```bash
   blowhorn profile set ada YT_OAUTH_CLIENT_ID=1234-abc.apps.googleusercontent.com YT_OAUTH_CLIENT_SECRET=GOCSPX-...
   ```

   Or set `BLOWHORN_YOUTUBE_OAUTH_CLIENT_ID` and
   `BLOWHORN_YOUTUBE_OAUTH_CLIENT_SECRET` in the environment for the next
   step; the consent stores them in the credential either way, because a
   consent refreshes only with the client that issued it.
4. Check that the client is found, opening nothing:

   ```bash
   blowhorn profile auth --platform youtube --profile ada --dry-run
   ```

5. Give the consent:

   ```bash
   blowhorn profile auth --platform youtube --profile ada
   ```

   Google's consent page opens in your default browser. Sign in, choose
   the channel and allow access. Blowhorn waits up to five minutes for the
   answer on 127.0.0.1, then stores `YT_OAUTH_REFRESH_TOKEN` and
   `YT_OAUTH_SCOPES` in the profile's YouTube credential, with the client
   from step 3 when it came from the environment. If you refuse, close the
   page or let the five minutes pass, nothing is stored; run the command
   again. If your Blowhorn account does not accept YouTube connections yet,
   the summary says so and nothing is stored, and running the command again
   does not help until it does. In the rare case Blowhorn also cannot remove
   the credential it saved for that account, the summary names that
   credential instead; delete it from the Credentials page of your Blowhorn
   account. If Google grants only some of the access
   asked for, the summary names what is missing, and the calls that need it
   are refused.

In the desktop app, the same consent is **Give consent** under **Data API
consent** on the YouTube row of the profile's **Browser** tab. It runs the
command above, so Google's page opens in your default browser the same way,
and the row says what Google granted or why nothing was stored. Once a
consent is given, **Give again** runs the same consent and replaces the one
stored, for example to grant the access Google left out; it deletes nothing.

The consent is given for one profile at a time, and a scheduled run never
opens it.

### Take the YouTube Data API consent back

To stop Blowhorn using a profile's YouTube consent and delete what it read
with it:

1. Preview what would go, sending and deleting nothing:

   ```bash
   blowhorn profile auth --platform youtube --profile ada --revoke --dry-run
   ```

2. Take the consent back:

   ```bash
   blowhorn profile auth --platform youtube --profile ada --revoke
   ```

   Blowhorn revokes the refresh token at Google, deletes the YouTube channel
   and video figures it kept for that profile, and clears
   `YT_OAUTH_REFRESH_TOKEN` and `YT_OAUTH_SCOPES`. The summary counts the
   figures deleted. Other profiles' figures stay, and so does the OAuth
   client, so giving the consent again needs no setup.

In the desktop app, choose **Take back** under **Data API consent** on the
YouTube row of the profile's **Browser** tab, then **Take back consent**.

If Google cannot be reached or refuses, nothing is deleted or cleared; run
the command again. If the profile holds no consent, nothing is sent to
Google and any figures still kept for it are deleted, so running the command
twice is harmless. Removing Blowhorn's access at
[myaccount.google.com/permissions](https://myaccount.google.com/permissions)
also works: the next YouTube run that tries to refresh the token then
deletes the figures and forgets the consent.

[YouTube API Services Developer Policies](https://developers.google.com/youtube/terms/developer-policies)
set the deadlines (last updated 2026-11-06, read 2026-11-20). When Blowhorn
revokes the consent itself, III.D requires deletion as soon as possible and
within 7 calendar days, and the token to be revoked immediately; the command
above does both at once. When you revoke through Google's security settings
page, III.E.4 (via III.A.2.i) allows 30 calendar days to delete API data
accessed or stored pursuant to that consent; Blowhorn does this on the next
run that sees the revocation.

If the store is down or refuses the delete, the consent is kept, so the
command or the next run can try the deletion again. Blowhorn never forgets
the consent first and leaves readings behind. None of the consent, refresh or
revocation path has been live-checked against Google.

The daily deletion of YouTube figures older than 30 days is separate,
and runs across the organization; see
[How long YouTube figures are kept](/docs/reference/platforms/youtube/#how-long-youtube-figures-are-kept).

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

