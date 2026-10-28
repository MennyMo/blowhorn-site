---
title: "Bluesky"
linkTitle: "Bluesky"
description: "What Blowhorn can do on Bluesky, and how each action behaves there."
weight: 230
---

Blowhorn works on Bluesky through Bluesky's API, never the browser. It uses `BLUESKY_HANDLE` with `BLUESKY_APP_PASSWORD`, kept in the profile's credential in your account: an app password, not your main password.

Posts up to 300 characters per post; longer messages split into
threads. Reposts for amplify activities. Follows with `blowhorn follow`,
unfollows one account with `blowhorn unfollow`, searches posts with
`blowhorn find`. Analytics appends a follower and following trend activity
per run.

## Supported actions

{{< supported-actions "bluesky" >}}

## Related

- [All platforms](/docs/reference/platforms/) - every platform, side by side.
- [Preview and publish queued posts](/docs/how-to/publish/post-content/) - the posting run.
- [Content queue columns and activity states](/docs/reference/content-queue/) - every column each platform reads.
- [Messages and exit codes](/docs/reference/messages/) - what a refusal means.
- [Who can post as whom](/docs/explanation/eligibility/) - why a credential is permission.
- [Why Blowhorn uses your own browser](/docs/explanation/your-own-chrome/) - browser versus API.
- [You're in control](/docs/explanation/youre-in-control/) - every safety control in one place.
- [Field Manual: Bluesky](https://blowhorn.ai/field-manual/bluesky/) - what the Bluesky feed rewards and what it penalizes.
- [Platform action matrix](https://blowhorn.ai/field-manual/action-matrix/) - safe versus risky actions, per platform.
