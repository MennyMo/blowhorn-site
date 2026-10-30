---
title: "X (Twitter)"
linkTitle: "X (Twitter)"
description: "What Blowhorn can do on X (Twitter), and how each action behaves there."
weight: 226
---

Blowhorn works on X in your own signed-in Google Chrome, through the Blowhorn extension. Sign in to X there once, by hand. The credential Blowhorn checks is `X_USERNAME`, kept in your account.

Posts from an activity; a message past 274 characters goes out as a thread.
Replies go through a post activity that targets the conversation. Amplifies
by retweet or quote. Follows accounts with `blowhorn follow`. Analytics
appends a follower and following trend activity per run.

Follows: at most 400 per profile a day and 15 in any 15 minutes,
counted from that profile's follow log on this computer. The 400 is X's
own published follow limit; the 15 is Blowhorn's spacing. X also
publishes 50 original posts and 200 replies a day for an account without
a checkmark, and no setting in Blowhorn goes past any of the three
([the one hard stop](/docs/how-to/settings/choose-your-rules-of-engagement/#a-limit-the-platform-publishes-is-the-one-hard-stop)).

## Supported actions

{{< supported-actions "x" >}}

## X (Twitter) replies

Replying is a post activity addressed at the conversation, not a separate
command. There is no comment flow for X under `blowhorn comment`.

## Related

- [All platforms](/docs/reference/platforms/) - every platform, side by side.
- [Preview and publish queued posts](/docs/how-to/publish/post-content/) - the posting run.
- [Content queue columns and activity states](/docs/reference/content-queue/) - every column each platform reads.
- [Messages and exit codes](/docs/reference/messages/) - what a refusal means.
- [Who can post as whom](/docs/explanation/eligibility/) - why a credential is permission.
- [Why Blowhorn uses your own browser](/docs/explanation/your-own-chrome/) - browser versus API.
- [You're in control](/docs/explanation/youre-in-control/) - every safety control in one place.
- [Field Manual: X](https://blowhorn.ai/field-manual/x/) - what the X feed rewards and what it penalizes.
- [Platform action matrix](https://blowhorn.ai/field-manual/action-matrix/) - safe versus risky actions, per platform.
