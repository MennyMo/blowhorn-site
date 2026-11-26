---
title: "YouTube"
linkTitle: "YouTube"
description: "What Blowhorn can do on YouTube, and how each action behaves there."
weight: 241
---

Blowhorn works on YouTube in your own signed-in Google Chrome, through the
extension. The extension reaches YouTube only once you allow it, one Chrome
profile at a time. To grant that permission and sign in to your channel in
the desktop app, open **Profiles**, open the profile, go to its **Browser**
tab, pick the Google Chrome profile that runs YouTube for it, and choose
**Turn on YouTube**. The guided setup's list of Google Chrome profiles has
the same button once Blowhorn is added to that profile. From Terminal:

```bash
blowhorn chrome open-profile <profile> --sign-in youtube
```

Either way, a Blowhorn page opens in that Chrome profile: choose **Allow
YouTube**, then **Allow** when Chrome asks, then sign in to YouTube on the
page it goes on to. Until the permission is granted, a YouTube run is
refused with nothing sent.

The button is on one Google Chrome profile only: the one a YouTube run of
that profile uses, which is the Chrome profile mapped for YouTube, else the
profile's only one, else its default. When a profile has several Chrome
profiles and none of those picks one, or the one they pick is no longer
in Google Chrome (a deleted Chrome profile), no Chrome profile has the
button. Each says so in plain words ("Choose which Chrome profile to use for
YouTube", or "The Chrome profile this person used for YouTube is no longer in
Chrome. Pick another.") and offers **Use this Chrome profile**, which chooses it
for YouTube (see [Google Chrome](/docs/reference/chrome/)). A profile with no Chrome profile
on this computer at all reads "This person isn't set up to use a Chrome profile
on this computer yet." and offers **Choose a Chrome profile**, which takes you to
the list of Chrome profiles on the same tab. When the one they pick has been
renamed or signed in to another account since it was linked, that Chrome profile
reads "This Chrome profile changed since it was linked." and offers **Confirm**
instead of the button. The desktop app never asks you to run a command.

A profile can post to YouTube once it has `YT_CHANNEL_URL` in its credential,
set to the channel's address by ID (`https://www.youtube.com/channel/UC...`,
shown at youtube.com/account_advanced). In the desktop app it is the
**Channel address** field on the same **YouTube** row of the profile's
**Browser** tab; once it is set, the profile's **Accounts** tab lists
YouTube by its channel ID, with **Channel set** (nothing checks a YouTube
sign-in from there), and choosing that row opens the field to change it.
From Terminal it is
`blowhorn profile set <profile> YT_CHANNEL_URL=https://www.youtube.com/channel/UC...`
([Connect platform accounts](/docs/how-to/set-up/platform-accounts/)).
A handle address (`/@name`) is refused by both, with the reason and nothing
saved, because Blowhorn never guesses which channel a handle means. A handle
address saved before that refusal reads **Needs channel ID** on **Accounts**,
and the field shows why until you replace it.
`blowhorn profile status --json` reports the channel as YouTube's account
(its `username`); YouTube is not a column of the status table and
`--check-sessions` does not check it.

## Live checks

Uploads through YouTube Studio, in signed-in Google Chrome, are the
supported path and the default. One hand-supervised private Studio upload
has already been run (2026-11-19): the upload page, the hidden
file input, overwriting the title Studio fills from the file name, three
presses of Next, and choosing Private so the final button reads Save.
Unlisted and Public, the Checks page, the made-for-kids radio, and the
rest of the dialog selectors have not been live-clicked; they are
modeled.

Uploads through the YouTube Data API are experimental and have not been
live-verified. Giving the Data API consent switches uploads, comments,
replies and likes onto that path; there is no fallback to Studio.
Without the consent, uploads use Studio. Analytics, comments, replies
and likes through the Data API have not had a live check either.

Worked examples for each activity are in
[Post to YouTube](/docs/how-to/publish/post-to-youtube/).

## What Blowhorn does on YouTube

- **Uploads a video** with `blowhorn post --platform youtube`. Set the
  activity's `Video URL`, `Title` and `Message Text` (the description).
  Blowhorn walks YouTube Studio's upload dialog: Details, Video elements,
  Checks and Visibility. It answers "made for kids" with No, and stops if
  Studio Checks reports a problem, with nothing published. The channel is
  checked when the upload page shows, once Details opens, and again just
  before the final click; a mismatch stops the activity with nothing
  published. Visibility is chosen explicitly and verified before that
  click: Blowhorn selects the row's setting, reads it back, and clicks
  only when the final button reads Save (private or unlisted) or Publish
  (public). If the button does not match, the click is refused. Nothing
  is read after a successful click, so the activity is recorded as
  *clicked, outcome not read*: check the upload in YouTube Studio.
  Studio's walk does not set a custom thumbnail. When the activity also
  has an `Image URL`, the report says a custom thumbnail is not yet in
  the Studio walk. Set it in YouTube Studio.
- **Visibility** is the activity's `Visibility` setting: `private` (the
  default), `unlisted` or `public`. Any other value is refused. Through
  the Data API, the visibility is read back from YouTube's answer after
  the upload and a different one is reported, not undone; see the Data
  API upload below. **Short**
  set to `yes` marks a Short; the video must be 3 minutes or less and
  vertical or square (not wider than it is tall). That length and shape
  are measured only once the file is on disk, so a plan-only
  `--dry-run` does not catch a Short that is too long or too wide. A live
  run, or a Google Chrome dry fire that downloads the file, refuses it
  before Studio's dialog proceeds (or, on the Data API path, before any
  byte is sent). See [YouTube settings](/docs/reference/content-queue/#youtube-settings).
- **Comments, replies and likes.** `Comment on` set to a video address is a
  comment, and set to a comment's address (its `&lc=` link) is a reply.
  `Amplify` set to a video address with no `Message Text` is a like.
  A comment or reply with an `@name` in it is refused before anything is
  typed. A reply to a reply is refused. If the Like button already reads
  as pressed, Blowhorn leaves it alone and records the like as done.
  That differs from Facebook, where an already-reacted post is left
  unclicked and is not recorded as done.
- **Posts on the Posts tab.** `Community` set to `yes` makes the activity a
  post on your channel's Posts tab instead of an upload. Posts run only in
  signed-in Chrome; there is no Data API call for them. A title, a video,
  `Comment on`, `Amplify` or an `@` tag on a post row is refused by name.
  YouTube states no text length, so none is checked. At most one image
  (`Image URL`) may be attached. That image is the post's picture. It is
  not a custom thumbnail for a video, and Blowhorn does not call
  `thumbnails.set` for a Posts-tab post.
- **Analytics.** `blowhorn analytics --platform youtube` reads your
  channel's and videos' figures through the YouTube Analytics and Data APIs, using the
  profile's own OAuth consent (its `YT_OAUTH_*` keys; see
  [The Data API consent](#the-data-api-consent)). These are read-only
  metrics: Blowhorn never writes or changes figures on YouTube. A profile
  without a consent is skipped. `--platform all` reads YouTube for every
  profile with a YouTube credential and leaves the others out; naming
  `--platform youtube` for a profile with no credential says what is
  missing. How long figures are kept, and what happens when you take the
  consent back, is in [How long YouTube figures are kept](#how-long-youtube-figures-are-kept).
  With that consent in place, uploads, comments, replies and likes go
  through the Data API too, instead of Google Chrome; uploads on that
  path are experimental and have not been live-verified. A failure on
  one path never falls back to the other. Studio remains the supported
  default for uploads when the profile has no Data API consent.

## The Data API consent

Analytics, and uploads, comments, replies and likes through the Data API,
read the profile's own OAuth consent from its YouTube credential.
Uploads through the Data API are experimental and not live-verified;
Studio is the supported default when this consent is not given:

| Key | What it holds |
|---|---|
| `YT_OAUTH_CLIENT_ID`, `YT_OAUTH_CLIENT_SECRET` | Your own Google Cloud OAuth client, type Desktop app. Blowhorn ships none. When the credential holds none, the consent reads `BLOWHORN_YOUTUBE_OAUTH_CLIENT_ID` and `BLOWHORN_YOUTUBE_OAUTH_CLIENT_SECRET` and stores them here. |
| `YT_OAUTH_REFRESH_TOKEN` | Written by the consent. The access token it refreshes is kept in memory for the run and never stored. |
| `YT_OAUTH_SCOPES` | The access Google granted, written by the consent. |

`blowhorn profile auth --platform youtube --profile <profile>` gives the
consent, for exactly one named profile. It opens Google's consent page in
your default browser and waits up to five minutes for the answer on
127.0.0.1. It asks for upload (`youtube.upload`), editing and playlists
(`youtube`), comments, replies and likes (`youtube.force-ssl`), Data API
reads (`youtube.readonly`) and analytics (`yt-analytics.readonly`). A
refused or abandoned consent stores nothing, and a scheduled run never
opens one. The steps, including creating the OAuth client, are in
[Give the YouTube Data API consent](/docs/how-to/set-up/platform-accounts/#give-the-youtube-data-api-consent).

When Google no longer accepts the consent, the next YouTube run that
tries to refresh it deletes only that profile's stored YouTube figures,
forgets the consent, and asks you to give it again. Other profiles'
figures, read under consents that still hold, stay. Details are in
[Taking the Data API consent back](#taking-the-data-api-consent-back).

## Taking the Data API consent back

`blowhorn profile auth --platform youtube --profile <profile> --revoke` takes
the consent back at once: it revokes the refresh token at Google, deletes the
YouTube figures Blowhorn kept for that profile and clears
`YT_OAUTH_REFRESH_TOKEN` and `YT_OAUTH_SCOPES`, keeping the OAuth client. A
revocation Google does not answer, or refuses, deletes and clears nothing.
With no consent held it sends nothing to Google and still deletes the
figures, so a second run is harmless. The steps are in
[Take the YouTube Data API consent back](/docs/how-to/set-up/platform-accounts/#take-the-youtube-data-api-consent-back).
The desktop app gives and takes back the same consent under **Data API
consent** on the YouTube row of a profile's **Browser** tab.

Removing Blowhorn's access at
[myaccount.google.com/permissions](https://myaccount.google.com/permissions),
or Google expiring the consent, works too: the next YouTube run that tries
to refresh the token then deletes the YouTube figures Blowhorn kept for that
profile, forgets the consent, and asks you to give it again. Other profiles
in the organization are not touched.

[YouTube API Services Developer Policies](https://developers.google.com/youtube/terms/developer-policies)
set the deadlines (last updated 2026-11-06, read 2026-11-20):

- **III.D, revocation in the client.** When Blowhorn revokes the consent
  itself, it must delete Authorized Data accessed or stored pursuant to
  that consent as soon as possible and within 7 calendar days, and it
  must revoke the token immediately. `--revoke` does both at once.
- **III.E.4, revocation through Google's security settings page**
  (III.A.2.i). When you remove access at Google's page, Blowhorn must
  delete API data related to that user accessed or stored pursuant to
  that consent within 30 calendar days. It does this on the next run that
  sees the revocation.

If the store is down or refuses the delete, the consent is kept, so
`--revoke` or the next run can try the deletion again. Blowhorn never
forgets the consent first and leaves readings behind. None of the consent,
refresh or revocation path has been live-checked against Google.

## How long YouTube figures are kept

No YouTube reading is kept past 30 days, under
[YouTube API Services Developer Policies](https://developers.google.com/youtube/terms/developer-policies)
III.E.4. A collection deletes expired YouTube readings first, before it
reads anything. The scheduler also does this on its first real pass of
each calendar day, across every profile in the organization, so figures
do not outlive 30 days when nobody collects. A store refusal is tried
again on the next pass.

Revoking one profile's consent is separate: it deletes only that
profile's stored YouTube figures, as described above. The daily 30-day
purge stays organization-wide.

## What Blowhorn does not do on YouTube

- **A scheduled run never comments, replies, likes or posts on the Posts
  tab.** YouTube treats automated engagement as spam, so those activities
  wait for a run you start yourself.
- **No sign-in for you.** You sign in to YouTube by hand. A sign-in page, a
  verification step, a captcha, or YouTube sending the tab off its own site
  (where Blowhorn cannot read the address) stops YouTube for that profile.
- **No cards or end screens** on an upload, and no likes on comments.
- **One channel per profile**: the one `YT_CHANNEL_URL` names. If Studio
  shows another channel, the activity stops with nothing published.

Every profile has daily ceilings of its own on YouTube: 3 uploads, 2
Posts-tab posts, 10 comments, 10 replies, 20 likes and 5 subscribes a
day, counted across every run that day. They are Blowhorn's own. The
table, the pages checked, and how they differ from Posture are under
[Per-profile daily ceilings](#per-profile-daily-ceilings). An activity
past its ceiling waits for the next day. A dry run counts its planned
rows against those ceilings for the rest of the same run, so it holds
what the real run would; it does not stamp the activity, so the count
does not carry into tomorrow.

Without a Data API consent, a [dry fire](/docs/reference/post/) walks Studio's upload
dialog up to the final button and stops there. Studio keeps the upload as
private once the file is attached, so delete it in YouTube Studio
afterward. With a consent, a dry fire goes through the Data API and only
prints the plan: nothing is sent and no draft is left. A dry run does not
spend the Data API project's unit budget, because nothing is sent.

Through the Data API, an upload is experimental and has not been
live-verified. It is a resumable upload under your own OAuth client. The file is sent in chunks (8 MiB by default, in 256 KiB
units). A dropped connection is resumed on the next run of the same row
(same file, channel and metadata) from the last byte YouTube confirmed,
never from a byte it did not. After six failures in a row with no
progress, with exponential backoff capped at 64 seconds, the row is held
and the session is kept. Set `BLOWHORN_YOUTUBE_UPLOAD_MAX_ATTEMPTS` and
`BLOWHORN_YOUTUBE_UPLOAD_MAX_BACKOFF_S` to change those bounds. If the
last chunk went out and nothing could be read after it, or YouTube
answers the upload as done with no video id, the activity is recorded as
sent, outcome not read. Before any byte is sent, the path
reads the channel the consent was given for and refuses a mismatch with
`YT_CHANNEL_URL`. This protocol is implemented and has not been
live-checked.

YouTube may lock uploads from an API project that has not passed
Google's audit to private. Until `BLOWHORN_YOUTUBE_API_PROJECT_UNVERIFIED`
is set to `false`, the project is treated as unaudited and a `public` or
`unlisted` upload says before it starts that it may land private. Every
upload reads the visibility back from YouTube's answer and reports one
other than the row asked for; the upload has already happened, so it is
not undone.

## Data API project quota

The Data API project's quota is a separate budget from the
[per-profile daily ceilings](#per-profile-daily-ceilings) and from
Posture. It is shared by every profile in a run.
Google changes the quota model, so no unit cost and no daily figure is
hard-coded. Read on 2026-11-24, the
[quota calculator](https://developers.google.com/youtube/v3/determine_quota_cost)
and the [getting started](https://developers.google.com/youtube/v3/getting-started)
quota section say a project gets a default of 100 `search.list` calls,
100 `videos.insert` calls, and 10,000 units a day for every other
endpoint. The two methods have their own buckets, at 1 unit per call.
The other costs named there include `comments.insert` 50,
`commentThreads.insert` 50, `videos.rate` 50, `subscriptions.insert` 50
and `thumbnails.set` 50. Daily quotas reset at midnight Pacific Time.

Optionally set `BLOWHORN_YOUTUBE_API_QUOTA_COSTS` (`method=units` pairs,
comma separated) and `BLOWHORN_YOUTUBE_API_DAILY_UNITS`. A call whose
configured cost would take the run past the configured daily units is
not made, and the row is held. That is one pool. A cost you set for
`videos.insert` is counted in it, which mixes Google's separate upload
bucket into the shared units. Blowhorn does not split the buckets and
does not hard-code 100 or 10,000. `search.list` is not called.
`BLOWHORN_YOUTUBE_API_DAILY_UPLOADS` is an optional per-run upload count
you set, not Google's 100-call `videos.insert` bucket. With nothing
configured, nothing is pre-counted and the API's own answer decides.
`quotaExceeded`, `uploadLimitExceeded`, `rateLimitExceeded` and any 429
hold the row and halt the API path for the rest of the run, never fail
it and never retry it.

After a video upload answers with a video id, Blowhorn can set a custom
thumbnail from the activity's `Image URL`. This runs only for a video
upload: `Video URL` holds the video, and `Image URL` holds a different
attached picture. A Posts-tab post, a comment, a reply, a like, and every
other platform are left alone. A picture built from a YouTube link in the
text (the desktop preview's `i.ytimg.com` thumbnail) is never uploaded.

YouTube Help asks for a JPG, GIF, or PNG that stays under 2 MB for a video
([Add a custom thumbnail](https://support.google.com/youtube/answer/72431)).
Blowhorn sends the file only when its contents are one of those and it is
under 2,000,000 bytes. The call is
[`thumbnails.set`](https://developers.google.com/youtube/v3/docs/thumbnails/set).
That page, read 2026-11-24, also allows JPEG and PNG up to 50 MB and says
the quota impact is approximately 50 units. Blowhorn keeps the Help page's
stricter size. The 50 units are not a built-in number: set
`thumbnails.set=50` in `BLOWHORN_YOUTUBE_API_QUOTA_COSTS` when the run
should count them. A GIF is sent as a GIF. If YouTube refuses it, the
video stays and the report says the thumbnail was not set.

If the thumbnail cannot be set (the file, the type, the size, the quota
skip, or YouTube's answer), the video upload still stands. The report
names the miss and says the video stays. Set the thumbnail in YouTube
Studio. The video is not deleted and is not uploaded again. A quota or
rate answer from the thumbnail call still stops further Data API work for
the rest of the run. A thumbnail whose configured cost would take the
run past the daily units is skipped without that halt, and the video
stays recorded as uploaded. This call has not been live-checked.

The engine can also edit a video's title, description or visibility, delete
a video, and add a video to a playlist through the Data API. Blowhorn does
not yet expose a command or a queue action for those calls.

Subscribe outreach can open a channel address and click Subscribe once,
never on a button that already reads Subscribed, and never on the
profile's own channel. It has no command yet (it belongs beside `follow`).
A scheduled run would hold it.

## When a Studio walk stops after the file is attached

As soon as the file input takes the video, Studio saves the upload as
private, including during a dry fire through Chrome. If the Google Chrome session is lost
after that, or the walk stops on Checks or a channel mismatch, the row
fails and the report tells you the draft is still in YouTube Studio.
If attaching the file itself fails after the browser may have sent it,
the report says Studio may have saved a draft; check YouTube Studio.
A retry starts a new upload; it does not resume the leftover draft.

## Per-profile daily ceilings

These are the ceilings the YouTube activities hold at, per profile, per
day. Each one is Blowhorn's own, and unverified. YouTube publishes no
per-account daily integer for any of them. The pages checked on
2026-11-24 are the [Spam Policy](https://support.google.com/youtube/answer/2801973),
[fake engagement](https://support.google.com/youtube/answer/3399767),
[feature access](https://support.google.com/youtube/answer/9890437) and
[upload errors](https://support.google.com/youtube/answer/10383400).
Feature access says only "limited daily limit" or "higher daily limit".
The upload-error page says a channel can upload only so many videos in
24 hours and that the limit may vary. Neither page states a number.
Review these by 2027-02-22.

| Activity | Ceiling a day |
|---|---|
| Upload | 3 |
| Posts-tab post | 2 |
| Comment | 10 |
| Reply | 10 |
| Like | 20 |
| Subscribe | 5 |

Posture reads a different table, the Risk Profile ceilings: 3 posts a
day and 1 an hour, 60 reactions a day and 15 an hour, 20 comments a day
and 5 an hour, 20 outreach a day and 5 an hour. A preset takes a
quarter, a half, or all of those, and a daily cap you set can only
lower them. YouTube stays experimental there, so outreach stays off
under Safety on and Weapons tight and is on under Weapons free. There
is no subscribe command yet, so a subscribe does not run. Uploads are
the only activity whose daily ceiling matches that gate. Likes,
comments, replies, Posts-tab posts and subscribes do not.
The YouTube activities hold at the table above. A scheduled YouTube
activity is also counted as a post on the Risk Profile gate (3 a day,
1 an hour).

YouTube does publish a few numbers that are not these ceilings. Custom
thumbnails have a daily limit with no integer
([Add custom thumbnails](https://support.google.com/youtube/answer/72431),
read 2026-11-24). Live streaming allows 10 active streams per channel
and 3 active streams per stream key at the same time
([Get started with live streaming](https://support.google.com/youtube/answer/2474026),
read 2026-11-24). A daily limit on creating live streams exists and has
no integer
([Avoid live-streaming restrictions](https://support.google.com/youtube/answer/2853834),
read 2026-11-24). Blowhorn does not upload custom thumbnails or live
streams as these activities.

<!-- BEGIN generated limits: release/scripts/capabilities_docs/build.py; do not edit -->

## Limits

The limits Blowhorn knows for YouTube.

| Limit | Value |
|---|---|
| Description | 5000 |
| Title | 100 |
| Video | 256000000000 bytes |
| Short length | 180 s |
| Custom thumbnail | 2000000 bytes |

<!-- END generated limits -->

## Supported actions

{{< supported-actions "youtube" >}}

## Related

- [Post to YouTube](/docs/how-to/publish/post-to-youtube/) - worked examples for each activity.
- [All platforms](/docs/reference/platforms/) - every platform, side by side.
- [Preview and publish queued posts](/docs/how-to/publish/post-content/) - the posting run.
- [Content queue columns and activity states](/docs/reference/content-queue/) - every column and setting each platform reads.
- [Chrome](/docs/reference/chrome/) - `chrome open-profile` and the extension.
- [Set up your platform accounts](/docs/how-to/set-up/platform-accounts/#youtube) - the sign-in and the Data API consent, step by step.
- [Why Blowhorn uses your own browser](/docs/explanation/your-own-chrome/) - browser versus API.
- [You're in control](/docs/explanation/youre-in-control/) - every safety control in one place.
