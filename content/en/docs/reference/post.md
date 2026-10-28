---
title: "Posting: pending activities and platform behavior"
description: "What 'pending' means for a queue activity, the one-click rule, and how posting behaves on each platform. Every flag and example is in the CLI reference."
weight: 216
---


Publishes the queue's pending activities and amplifies existing content.
This page covers what the command reference cannot say: what counts
as pending, the one-click rule, and how posting behaves on each
platform. Every flag and example for the command is in
[`blowhorn post` in the CLI reference](/docs/reference/cli/post/); the steps live
in the how-to guides under Related.

## What "pending" means

An activity is pending when "Approved?" says `yes` or `true`, "Date Promoted"
is empty, "Promote On" is due or blank, and the profile and platform
resolve. `--check-queue` lists the pending activities without publishing
anything, opening no browser and hitting no API. `--dry-run` walks the
whole run, printing what would go out, and marks nothing done.

Posting is one click per run. A clicked control with no confirmation
read back is recorded as clicked, outcome not read, counted for
nothing, and never retried by the run. See
[How Blowhorn avoids repeat posts](/docs/explanation/never-twice/).

## Platform behavior

LinkedIn, X, Reddit, and Hacker News drive your Chrome through the
extension. Slack, Bluesky, and GitHub post through their APIs. Reddit
activities need their subreddit as `r/<name>` in "Destination" or "Amplify";
without one the activity is skipped. A "Comment on" activity addressed to a
LinkedIn or Reddit location becomes a comment under `post` as well as
under `comment`; X has no comment flow.

GitHub is amplify-only under `post`: `--platform github` needs an
`--amplify` issue or pull-request URL, or a GitHub activity's "Amplify"
column, and refuses without one.

## Related

- [`blowhorn post` in the CLI reference](/docs/reference/cli/post/) - every flag and example for this command.
- [Preview and publish queued posts](/docs/how-to/publish/post-content/) - the run in practice.
- [Content queue columns and activity states](/docs/reference/content-queue/) - what the activities hold.
- [Platforms](/docs/reference/platforms/) - per-platform actions and limits.
- [CLI reference](/docs/reference/cli/) - every command and flag.
- [How Blowhorn avoids repeat posts](/docs/explanation/never-twice/) - one click per run.
- [You're in control](/docs/explanation/youre-in-control/) - dry run, pace and the built-in limits.
