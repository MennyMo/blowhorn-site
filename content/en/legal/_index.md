---
title: Trust Center
heading: Blowhorn Trust Center
description: How Blowhorn handles your data, sessions and accounts, in plain language, and every policy that covers the Blowhorn website, the Blowhorn app for macOS and the Blowhorn Chrome extension.
lead: Many public voices, one coordinated queue, every action on your own computer. Every policy for the Blowhorn website, desktop app and Chrome extension, each with a plain-language summary. Where a summary differs from its policy, the policy decides.
layout: trust-center
lastmod: 2026-10-25
sitemap:
  changefreq: monthly
  priority: 0.5
# The plain-language summaries. Each one restates what the linked policy
# already says; add a card only for a promise a policy or a public doc makes.
glance:
  - title: Every action happens on your own computer
    text: Blowhorn never acts for you from a server. Every post, comment and reaction is made by the Blowhorn app on one of your computers; the Chrome extension acts only when that app asks.
    link: /legal/privacy/#on-your-machine
    linkText: What stays on your computer
  - title: The extension reports to no server
    text: The extension talks only to the Blowhorn app on your computer, over Chrome's native messaging. It acts only on supported sites, only in the Chrome profiles you install it in, and keeps nothing itself.
    link: /legal/privacy/#in-chrome-through-the-blowhorn-extension
    linkText: What the extension reads
  - title: No analytics in the app
    text: The app carries no analytics or crash-reporting library. The one thing it sends about itself is failure reports, described on the privacy page. This website uses Google Analytics to count visits only if you accept its cookie notice, and those cookies are the only ones the site sets. You can change your choice under Cookie preferences. Its other outside request is the release lookup on GitHub. The newsletter form sends your email address to Blowhorn's own signup service only when you submit it. The privacy page describes all three.
    link: /legal/privacy/#this-website
    linkText: What this website does
  - title: One account for your queue, analytics and credentials
    text: Your account keeps your queue, schedule, profiles, run history, analytics and platform credentials in sync, so any number of computers, yours or your teammates', run as one fleet. They share one queue, coordinated so the same post isn't sent from two of them. The account privacy policy governs that data.
    link: /legal/privacy/#in-your-blowhorn-account
    linkText: What your account keeps
  - title: You approve what goes out
    text: Blowhorn publishes the rows you approve and the commands you run, from the accounts you configure. A dry run publishes nothing, and on Hacker News Blowhorn submits and comments only; it never votes.
    link: /legal/terms/#your-accounts
    linkText: Your accounts and your content
  - title: Releases you can check
    text: The official downloads are signed disk images published with a SHA256SUMS.txt file to check them against, and a release is never replaced in place. The Blowhorn software is licensed under the AGPL-3.0.
    link: /legal/terms/#downloads
    linkText: Official downloads
# The policies, as cards. `status` marks a policy the reader must know is not final.
policies:
  - title: Privacy
    summary: What the Blowhorn website, the app and the extension store, where they store it, and what the app sends.
    url: /legal/privacy/
  - title: Terms of service
    summary: The agreement between you and us for the website, the app and the extension, from early access and downloads to acceptable use.
    url: /legal/terms/
    status: Draft, pending legal review
  - title: Chrome extension permissions
    summary: Each permission the Blowhorn extension asks for, the sites it runs on, and why.
    url: /docs/reference/extension-permissions/
  - title: Where your data lives
    summary: What stays on your computer, what your account keeps in sync, and what the extension reads.
    url: /docs/explanation/your-data/
  - title: Account policies
    summary: The privacy policy, terms of service and other policies of Layer5, Inc. that cover your account.
    url: https://layer5.io/company/legal/
---

## See what sites can see {#tells}

Curious what websites can read about your browser? [Blowhorn Tells](https://tells.blowhorn.ai/) is our free "Am I a Bot?" check. It shows the bot-detection and fingerprint signals a site can see, in plain words. The site keeps no copy, and its own page says exactly which outside services see your IP address.

## Report a security issue

If you think you have found a security vulnerability in Blowhorn, send the details privately to [security@blowhorn.ai](mailto:security@blowhorn.ai) rather than opening a public issue. We acknowledge and analyze each report within 10 working days and keep the reporter updated while it is addressed. The [security policy](https://github.com/blowhorn-ai/blowhorn-site/blob/master/SECURITY.md) explains what to report and how fixes are disclosed.

## Frequently Asked Questions {#questions}

- About privacy: open an issue on the [site repository](https://github.com/blowhorn-ai/blowhorn-site/issues), or use the contact channels in the account [privacy policy](https://layer5.io/company/legal/privacy/).
- About the terms: email [legal@blowhorn.ai](mailto:legal@blowhorn.ai).

## Changes to these policies

Each policy shows the date it last changed at the top of its page, and every edit to these pages is recorded in the [site repository's history](https://github.com/blowhorn-ai/blowhorn-site/commits/master/content/en/legal).
