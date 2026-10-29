---
title: "GitHub"
linkTitle: "GitHub"
description: "What Blowhorn can do on GitHub, and how each action behaves there."
weight: 231
---

Blowhorn works on GitHub through GitHub's API, never the browser, with the `GH_TOKEN` in your account.

Follows accounts with `blowhorn follow` and lists an audience with
`blowhorn source --platform github --repo`. Under `post`, GitHub
amplifies only: it adds all five uplifting reactions (+1, laugh,
hooray, heart, rocket) to the issue or pull request the `--amplify`
flag or the activity's "Amplify" column names, from every selected profile
under its own token. Re-running adds none of them twice.

## Supported actions

{{< supported-actions "github" >}}

## Related

- [All platforms](/docs/reference/platforms/) - every platform, side by side.
- [Preview and publish queued posts](/docs/how-to/publish/post-content/) - the posting run.
- [Content queue columns and activity states](/docs/reference/content-queue/) - every column each platform reads.
- [Messages and exit codes](/docs/reference/messages/) - what a refusal means.
- [Who can post as whom](/docs/explanation/eligibility/) - why a credential is permission.
- [Why Blowhorn uses your own browser](/docs/explanation/your-own-chrome/) - browser versus API.
- [You're in control](/docs/explanation/youre-in-control/) - every safety control in one place.
- [Platform action matrix](https://blowhorn.ai/field-manual/action-matrix/) - safe versus risky actions, per platform.
- [Developer distribution](https://blowhorn.ai/solutions/developer-distribution/) - GitHub reactions beside the other developer channels, for a launch.
