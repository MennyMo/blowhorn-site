---
title: "LinkedIn"
linkTitle: "LinkedIn"
description: "What Blowhorn can do on LinkedIn, and how each action behaves there."
weight: 225
---

Blowhorn works on LinkedIn in your own signed-in Google Chrome, through the Blowhorn extension, in the Chrome profile you mapped. Sign in to LinkedIn there once, by hand. The credential Blowhorn checks is `LI_USERNAME` with `LI_PASSWORD`, kept in your account.

Posts to the feed from an activity; comments on a post when the activity's "Comment on"
holds its address; amplifies by reposting.

## Supported actions

{{< supported-actions "linkedin" >}}

## LinkedIn comments

An activity with "Comment on" set to a `linkedin.com` post address and a
"Message Text" becomes a comment on that post instead of a new post.
The same activity is also picked up by `blowhorn comment`. An activity whose
"Comment on" names anything else stays a normal post.

## Related

- [All platforms](/docs/reference/platforms/) - every platform, side by side.
- [Preview and publish queued posts](/docs/how-to/publish/post-content/) - the posting run.
- [Content queue columns and activity states](/docs/reference/content-queue/) - every column each platform reads.
- [Messages and exit codes](/docs/reference/messages/) - what a refusal means.
- [Who can post as whom](/docs/explanation/eligibility/) - why a credential is permission.
- [Why Blowhorn uses your own browser](/docs/explanation/your-own-chrome/) - browser versus API.
- [You're in control](/docs/explanation/youre-in-control/) - every safety control in one place.
- [Field Manual: LinkedIn](https://blowhorn.ai/field-manual/linkedin/) - what the LinkedIn feed rewards and what it penalizes.
- [Platform action matrix](https://blowhorn.ai/field-manual/action-matrix/) - safe versus risky actions, per platform.
