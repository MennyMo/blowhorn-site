---
title: "Add a profile"
description: "Create a profile from the desktop app or the command line."
weight: 60
draft: true
aliases: [/docs/how-to/add-a-profile/]
---


A profile is one voice you post as: a person in your organization, or a
brand that represents nobody. Create one from the desktop app or from the
command line.

**Early access:** profiles live in your organization in your Blowhorn account, and customer onboarding for that account is not open yet.
This page stays a draft until it is.

A profile has three things you set: its **name**, what you type after
`--profile`; an optional **description**; and **who it represents**. Its
accounts on each platform are not part of the form: Google Chrome profile
discovery finds the ones you are signed in to, and each platform card
connects the rest. What a profile holds is in the
[Profile reference](/docs/reference/profiles/).

## Before you start

- Sign in and choose your organization ([Sign in](/docs/how-to/set-up/sign-in/)). With your
  account unreachable the create is refused (exit 3) and nothing is written.
- The person the profile represents must be a member of your organization.
  Invite them to your organization in Blowhorn first, or create the profile as a brand.

## From the desktop app

1. Open **Profiles** and click **add profile**.
2. Type the **name**: lowercase letters, digits, `-` or `_`. Add a
   **description** if you like.
3. Under **who is this profile?**, choose **you**, **someone in your
   organization** and pick the member, or **nobody · a brand**.
4. Click **create profile**.

Then give the profile its accounts: open **chrome profiles** to map the
Chrome profile it posts from and attach the accounts signed in there, and
use a platform card for anything else, such as a GitHub token.

A profile you create for someone else is listed for them too, so their own
Blowhorn shows it once they sign in to your organization. They can read it
but not change it: editing a profile takes its ownership or the Edit Profile
permission in your organization. The accounts linked to it are read only by
its owner and by people who can view your organization's profiles, so the
person it represents sees the profile without its accounts unless they hold
that permission.

Your organization's profiles and members are read from your Blowhorn account. When
either read fails, the screen names the failure where it would have listed
them, rather than show an empty list. The Add form's member picker says
`can't read your organization's members`. Every other profile picker says
`can't read your organization's profiles`: the routine and post editors in
Activity, the LinkedIn admin picker in Performance, the excluded profiles in
Settings, and Diagnostics.

## Edit a profile

Select the profile on **Profiles**. Its name, description and **who is this
profile?** are editable; the represented person's name and email are shown
from their member record and are changed in your Blowhorn account, not here. Click
**save**. Renaming a profile changes what you type after `--profile`, and
any routine or excluded-profiles entry that names the old name needs the new
one. Its Chrome mapping and its content items follow the profile, because
they hold its id.

## From the command line

List the members a profile can represent:

```bash
blowhorn org members
```

Create the profile from a JSON document on stdin:

```bash
echo '{"name": "sam", "description": "Sam'\''s posts", "userId": "<a member id from org members>"}' \
  | blowhorn profile create --payload-stdin
```

Leave `userId` out for a brand. The document takes only `name`,
`description` and `userId`: an email, a handle or a credential is refused,
and so is a name another profile already uses. Rehearse with `--dry-run`,
which makes every check and sends nothing.

Edit it the same way, naming it by its name or its id:

```bash
echo '{"name": "sam", "description": "Sam'\''s posts and talks"}' \
  | blowhorn profile update sam --payload-stdin
```

The document is the whole of the fields you set: a description left out is
cleared, and a `userId` left out makes the profile a brand.

## Delete a profile

From the desktop app, select the profile and click **delete profile**. From
a terminal:

```bash
blowhorn profile delete sam --yes
```

Name it by its id instead when two profiles in your organization share a
name, as `blowhorn profile list` prints it. Only the profile with that id is
deleted:

```bash
blowhorn profile delete 3f2b8c1e-5a7d-4e2f-9b1c-6d4a2e8f0c17 --yes
```

The profile is deleted in your organization and unlinked from its
accounts; the accounts themselves are kept. With your account unreachable
the delete is refused and nothing changes.

## Related

- [Sign in](/docs/how-to/set-up/sign-in/) - sign in before profiles mean anything.
- [Map Blowhorn profiles to Chrome profiles](/docs/how-to/set-up/map-chrome-profiles/) - give
  the profile its Chrome and the accounts signed in there.
- [Sign a profile in to each platform](/docs/how-to/set-up/platform-accounts/) - the sessions
  and credentials each platform needs.
- [Profile reference](/docs/reference/profiles/) - what a profile holds.
