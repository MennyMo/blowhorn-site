# Post to YouTube


> Upload a video, post on the Posts tab, comment, reply, like, and collect analytics, with the behavior of each activity.



Upload a video to YouTube, post on your channel's Posts tab, comment, reply
or like, and collect analytics, from a content activity.

> **The Major says:** "Studio is the supported upload path, and the default. Studio starts on Public. We don't. Private is the default visibility, and a dry fire through Google Chrome still leaves a private draft the moment the file attaches. Uploads through the Data API are experimental."


Uploads through YouTube Studio, in signed-in Google Chrome, are the
supported path and the default. One hand-supervised private Studio upload
has already been run (2026-11-19). Unlisted and Public, Checks,
the made-for-kids choice, and many dialog selectors have not been
live-clicked; they are modeled from YouTube's pages and docs.

Uploads through the YouTube Data API are experimental and have not been
live-verified. Giving the Data API consent switches uploads, comments,
replies and likes onto that path; there is no fallback to Studio.
Without the consent, uploads use Studio. Analytics also need that
consent. Comments, replies, likes and analytics through the Data API
have not had a live check either. What each activity does, including
that caveat, is also on the
[YouTube reference page](/docs/reference/platforms/youtube/).

## Before the first run

1. **Let the extension reach YouTube** in the Google Chrome profile this
   Blowhorn profile uses, and sign in to the channel by hand. In the
   desktop app, open **Profiles**, open the profile, go to its **Browser**
   tab, and choose **Turn on YouTube**. From Terminal:

   ```bash
   blowhorn chrome open-profile your-profile --sign-in youtube
   ```

   Allow YouTube when the Blowhorn page and Chrome ask, then sign in on
   the YouTube page it goes on to. Until that permission is granted, a
   YouTube run is refused with nothing sent. **Discover** does not look
   for a YouTube sign-in. The full procedure is in
   [Set up your platform accounts](/docs/how-to/set-up/platform-accounts/#youtube).

2. **Store the channel's address by ID**, shown at
   youtube.com/account_advanced. A handle address (`/@name`) is refused,
   because Blowhorn never guesses which channel a handle means.

   ```bash
   blowhorn profile set your-profile YT_CHANNEL_URL=https://www.youtube.com/channel/UC...
   ```

3. **Optional: give the Data API consent** if you want analytics, or if
   you want comments, replies and likes to go through the YouTube Data
   API instead of Google Chrome. Uploads through the Data API are
   experimental and not live-verified; Studio remains the supported
   default. The consent uses your own Google Cloud OAuth client (type
   Desktop app); Blowhorn ships none. The steps are in
   [Give the YouTube Data API consent](/docs/how-to/set-up/platform-accounts/#give-the-youtube-data-api-consent).

   ```bash
   blowhorn profile auth --platform youtube --profile your-profile
   ```

   With that consent in place, uploads, comments, replies and likes use
   the Data API (uploads on that path are experimental). Without it,
   those activities use signed-in Google Chrome, which is the supported
   default for uploads, and analytics skips the profile. A failure on
   one path never falls back to the other.

If the profile has no YouTube credential, `blowhorn post --profile
your-profile --platform youtube` exits non-zero and says the profile has
no credential for youtube, so nothing can be selected for posting, and
to add one with `blowhorn profile set your-profile <KEY>=<value>`. That
message does not name `YT_CHANNEL_URL`. Set the key as shown above. A
handle address is refused by name, with the ID form to use. Nothing
opens Google Chrome in either case.

## Upload a video

Set `Video URL`, `Title` and `Message Text` (the description). Leave
`Comment on`, `Amplify` and `Community` blank. A blank `Visibility` is
private.

```bash
blowhorn content upsert --payload '{"Platform":"YouTube","Profile":"your-profile","Title":"Launch day","Message Text":"What we shipped and why it matters.","Video URL":"https://example.com/launch.mp4","Approved?":"yes"}'
```

Then preview, and publish:

```bash
blowhorn post --platform youtube --profile your-profile --dry-run
blowhorn post --platform youtube --profile your-profile
```

Through Google Chrome, Blowhorn opens Studio's upload page at the
channel ID in `YT_CHANNEL_URL`, attaches the file, and walks Details,
Video elements, Checks and Visibility. It answers "made for kids" with
No, and stops if Studio Checks reports a problem, with nothing
published. The channel is checked when the upload page shows, once
Details opens, and again just before the final click, because Studio can
switch channels after the upload page first showed. If the address is
not the channel `YT_CHANNEL_URL` names, the activity stops with nothing
published.

Visibility is chosen explicitly and verified before that click. Studio's
Visibility page starts on Public, with the final button reading Publish.
Blowhorn selects the row's setting (`private` when `Visibility` is
blank), reads the choice back, and clicks only when the button reads
Save (private or unlisted) or Publish (public). If the button does not
read what that setting requires, the click is refused and nothing is
published. Unlisted and Public have not been live-clicked.

Nothing is read after a successful click, so the activity is recorded as
*clicked, outcome not read*: check the upload in YouTube Studio.

The title may be at most 100 characters and the description at most
5,000. A longer value is refused before the file is fetched and before
Studio opens, not shortened. `<` and `>` are refused in both.

Once the file is attached, Studio has already saved the upload as
private, including during a dry fire through Google Chrome or a walk
that later stops. Delete that draft in YouTube Studio if you do not want
it. A retry starts a new upload; it does not resume the leftover draft.

Through the Data API, which is experimental for uploads and has not
been live-verified, the same row is sent as a resumable upload under
your own OAuth client. The file goes in chunks (8 MiB by default, in
256 KiB units). If the connection drops, the next run of the same row
(same file, channel and metadata) resumes from the last byte YouTube
confirmed, never from a byte it did not. After six failures in a row
with no progress (with exponential backoff capped at 64 seconds), the
row is held and the session is kept for the next run. If the last chunk
went out and nothing could be read after it, the activity is recorded as
sent, outcome not read, and is not blindly retried. A quota,
`uploadLimitExceeded`, rate-limit or 429 answer holds the row instead of
failing it, and stops further Data API work for the rest of the run.
This path has not been live-checked.

On the Data API path no Visibility page is walked. The visibility is
sent with the upload and read back from YouTube's answer; a different
visibility, or none, is reported but does not undo the upload, which
has already happened. YouTube may lock uploads from an API project that
has not passed Google's audit to private, so a `public` or `unlisted`
upload says so before it starts. Set
`BLOWHORN_YOUTUBE_API_PROJECT_UNVERIFIED=false` once your project has
passed the audit to stop that warning.

Each profile may upload 3 videos a day, counted across every run that
day. That ceiling is Blowhorn's own. YouTube publishes no daily upload
count (read 2026-11-24; the pages are on the
[YouTube reference](/docs/reference/platforms/youtube/#per-profile-daily-ceilings)).
An activity past that ceiling waits for the next day. A dry run
counts its planned rows against that ceiling for the rest of the same
run, so it holds what the real run would; it does not stamp the
activity, so the count does not carry into tomorrow.

## Set a custom thumbnail

On a video upload, set `Image URL` to a picture as well as `Video URL`
to the video. Through the Data API, Blowhorn uploads that picture as the
video's custom thumbnail after the upload answers with a video id. The
video itself still comes from `Video URL`.

```bash
blowhorn content upsert --payload '{"Platform":"YouTube","Profile":"your-profile","Title":"Launch day","Message Text":"What we shipped and why it matters.","Video URL":"https://example.com/launch.mp4","Image URL":"https://example.com/launch-thumb.jpg","Approved?":"yes"}'
```

YouTube Help asks for a JPG, GIF, or PNG under 2 MB for a video
([Add a custom thumbnail](https://support.google.com/youtube/answer/72431)).
Blowhorn sends the picture only when the file is one of those and under
2,000,000 bytes. The Data API call is
[`thumbnails.set`](https://developers.google.com/youtube/v3/docs/thumbnails/set).
That page also allows a larger JPEG or PNG, up to 50 MB, and says the
call costs about 50 quota units. Blowhorn keeps the Help page's stricter
limit. The 50 units are counted only when you set `thumbnails.set=50` in
`BLOWHORN_YOUTUBE_API_QUOTA_COSTS`.

If the thumbnail cannot be set, the video upload still stands. The report
says the thumbnail was not set and that the video stays. Set the
thumbnail in YouTube Studio. Blowhorn does not delete the video and does
not upload it again.

Through Google Chrome, Studio's upload walk does not set a custom
thumbnail yet. The report says so. Set it in YouTube Studio after the
upload.

`Image URL` on a Posts-tab post is the post's image, not a video
thumbnail. A comment, a reply, or a like does not get one either. A
picture Blowhorn builds from a YouTube link in the text, for the desktop
preview, is never uploaded.

## Choose visibility

Set `Visibility` to `private` (the default), `unlisted` or `public`. Any
other value is refused. These settings belong only to YouTube: a
LinkedIn, X or other activity that sets `Visibility`, `Short` or
`Community` is refused by name (leave the setting blank).

```bash
blowhorn content upsert --payload '{"Platform":"YouTube","Profile":"your-profile","Title":"Launch day","Message Text":"What we shipped and why it matters.","Video URL":"https://example.com/launch.mp4","Visibility":"unlisted","Approved?":"yes"}'
```

Through Google Chrome, the choice is verified on Studio's Visibility
page before the final click, as described above. Unlisted and Public
have not been live-clicked. Through the Data API, the visibility is only
read back from YouTube's answer after the upload, and a `public` or
`unlisted` upload may land private on an unaudited API project, as
described above.

## Upload a Short

Set `Short` to `yes`. The video must be 3 minutes or less, and vertical
or square (not wider than it is tall). A row that fails either check is
refused once the file has been downloaded, before Studio's dialog
proceeds (or, on the Data API path, before any byte is sent). A
plan-only `--dry-run` does not download the file, so it does not measure
length or shape and will not catch a Short that is too long or too wide.

```bash
blowhorn content upsert --payload '{"Platform":"YouTube","Profile":"your-profile","Title":"Launch in 30 seconds","Message Text":"A quick look at what shipped.","Video URL":"https://example.com/short.mp4","Short":"yes","Approved?":"yes"}'
```

A blank `Short` means the video is not a Short. Use `yes` or `no`; a JSON
`true` or `false` is stored as `yes` or `no`. The string `"true"` is
refused.

## Post on the Posts tab

Set `Community` to `yes` and put the text in `Message Text`. Optionally
set `Image URL` to one image. That image is the post's picture. It is not
a custom thumbnail for a video. Leave `Title`, `Video URL`, `Comment on`
and `Amplify` blank: any of those, or an `@` tag in the text, is refused
by name. YouTube states no text length, so Blowhorn does not check one.

```bash
blowhorn content upsert --payload '{"Platform":"YouTube","Profile":"your-profile","Message Text":"The launch stream starts at 15:00 CT.","Community":"yes","Approved?":"yes"}'
```

A Posts-tab post runs only in signed-in Chrome. There is no Data API call
for it. A scheduled run holds the activity for a run you start yourself.
Each profile may publish 2 Posts-tab posts a day.

## Comment, reply or like

A comment puts the video's address in `Comment on` and the text in
`Message Text`. A reply uses the comment's own address, the watch URL
with `&lc=`. A like puts the video's address in `Amplify` and leaves
`Message Text` blank.

```bash
blowhorn content upsert --payload '{"Platform":"YouTube","Profile":"your-profile","Comment on":"https://www.youtube.com/watch?v=VIDEO_ID","Message Text":"The 2:15 mark is the part we would start with.","Approved?":"yes"}'
```

```bash
blowhorn content upsert --payload '{"Platform":"YouTube","Profile":"your-profile","Comment on":"https://www.youtube.com/watch?v=VIDEO_ID&lc=COMMENT_ID","Message Text":"Agreed; that is the cut we kept.","Approved?":"yes"}'
```

```bash
blowhorn content upsert --payload '{"Platform":"YouTube","Profile":"your-profile","Amplify":"https://www.youtube.com/watch?v=VIDEO_ID","Approved?":"yes"}'
```

An `@name` in a comment or reply is refused before anything is typed. A
reply to a reply is refused. A like that carries text is refused. A
scheduled run holds every comment, reply and like for a run you start
yourself: YouTube treats automated engagement as spam.

If the Like button already reads as pressed (`aria-pressed=true`),
Blowhorn leaves it alone and records the like as done. That differs from
Facebook, where an already-reacted post is left unclicked and is not
recorded as done.

Each profile may send 10 comments, 10 replies and 20 likes a day, and
may publish 2 Posts-tab posts and make 5 subscribes. Those ceilings are
Blowhorn's own. YouTube publishes no daily count for any of them (read
2026-11-24; the pages are on the
[YouTube reference](/docs/reference/platforms/youtube/#per-profile-daily-ceilings)).
They are not the Risk Profile ceilings Posture uses, and they are not
the Data API project quota. A dry run counts its planned rows against
those ceilings for the rest of the same run, so it holds what the real
run would; it does not stamp the activity. With a Data API consent
these go through the API; without one they go through the signed-in
watch page. A Data API quota, rate-limit or 429 answer holds the row
and stops further API work for the rest of the run. The project's quota
budget is shared by every profile in the run, because the quota belongs
to your API project, not to one profile. Posture does not set that
budget. Set `BLOWHORN_YOUTUBE_API_QUOTA_COSTS` and
`BLOWHORN_YOUTUBE_API_DAILY_UNITS` if you want a count before the API
answers. Google gives `videos.insert` its own bucket of 100 calls a
day, separate from the 10,000 units for other methods (quota calculator,
read 2026-11-24). Blowhorn's configured unit pool does not split that
bucket out, and it does not hard-code either number.

## Collect analytics

```bash
blowhorn analytics --platform youtube --profile your-profile
```

Analytics are read-only metrics, collected through the profile's own
Data API consent (your own OAuth client). A profile without a consent is
skipped. Blowhorn never writes or changes figures on YouTube.

Figures are kept for 30 days, as
[YouTube API Services Developer Policies](https://developers.google.com/youtube/terms/developer-policies)
III.E.4 require. A collection deletes expired YouTube readings first,
before it reads anything. The scheduler also does this on its first real
pass of each calendar day, across every profile in the organization, so
figures do not outlive 30 days when nobody collects.

If you take the consent back, only that profile's stored YouTube
figures are deleted. Other profiles' figures stay. How to take the
consent back, and what happens if the store is down, is in
[Give the YouTube Data API consent](/docs/how-to/set-up/platform-accounts/#give-the-youtube-data-api-consent).
The steps and the history commands are in
[Collect and read your analytics](/docs/how-to/measure/analytics/).

## Preview without publishing

A plan-only dry run validates the row and prints the plan. It never
opens Studio or sends to the API:

```bash
blowhorn post --platform youtube --profile your-profile --dry-run
```

Without a Data API consent, a dry fire (`blowhorn post --dry-run
--payload-stdin`) walks Studio's dialog as far as Visibility, chooses the
row's setting, reads the final button back, and does not click it. Studio
has already saved a private draft once the file was attached; delete it in
YouTube Studio afterward. With a consent, the same dry fire goes through
the Data API and is plan-only: it prints the plan, opens no Studio page,
sends nothing and leaves no draft.

```bash
cat youtube-order.json | blowhorn post --dry-run --payload-stdin --json
```

A dry run still counts planned YouTube rows against the profile's daily
ceilings for the rest of that run, as described above. It does not spend
the Data API project's unit budget, because nothing is sent.

## Related

- [YouTube](/docs/reference/platforms/youtube/) - what each activity
  does, the Data API consent, ceilings and limits.
- [Set up your platform accounts](/docs/how-to/set-up/platform-accounts/#youtube) -
  the sign-in and the Data API consent, step by step.
- [Preview and publish queued posts](/docs/how-to/publish/post-content/) - the posting run
  for every platform.
- [Content queue columns and activity states](/docs/reference/content-queue/#youtube-settings) -
  Visibility, Short and Community.
- [Collect and read your analytics](/docs/how-to/measure/analytics/) - history and
  the HTML report.

