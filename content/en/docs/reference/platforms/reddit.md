---
title: "Reddit"
linkTitle: "Reddit"
description: "What Blowhorn can do on Reddit, and how each action behaves there."
weight: 227
---

Blowhorn works on Reddit in your own signed-in Google Chrome, through the Blowhorn extension. Sign in to Reddit there once, by hand. The credential Blowhorn checks is `RDDT_USERNAME`, kept in your account.

Posts to the subreddit the activity's "Destination" names as `r/<name>`; with
no subreddit the activity is skipped, never guessed. Comments when "Comment
on" holds a Reddit post or comment address. Amplifies with an upvote.

## Supported actions

{{< supported-actions "reddit" >}}

## Reddit posts and comments

Posting needs the subreddit in "Destination" or, for an upvote, in
"Amplify". Commenting needs a Reddit address in "Comment on" plus a
"Message Text". Both `post` and `comment` act on comment activities; an activity
already marked done is never acted on twice.

## Related

- [All platforms](/docs/reference/platforms/) - every platform, side by side.
- [Preview and publish queued posts](/docs/how-to/publish/post-content/) - the posting run.
- [Content queue columns and activity states](/docs/reference/content-queue/) - every column each platform reads.
- [Messages and exit codes](/docs/reference/messages/) - what a refusal means.
- [Who can post as whom](/docs/explanation/eligibility/) - why a credential is permission.
- [Why Blowhorn uses your own browser](/docs/explanation/your-own-chrome/) - browser versus API.
- [You're in control](/docs/explanation/youre-in-control/) - every safety control in one place.
- [Field Manual: Reddit](https://blowhorn.ai/field-manual/reddit/) - what the Reddit feed rewards and what it penalizes.
- [Platform action matrix](https://blowhorn.ai/field-manual/action-matrix/) - safe versus risky actions, per platform.
- [Developer distribution](https://blowhorn.ai/solutions/developer-distribution/) - Reddit beside the other developer channels, for a launch.
