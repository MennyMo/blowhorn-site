---
title: blowhorn-axi
seo_title: blowhorn-axi - the agent interface to Blowhorn
description: blowhorn-axi lets AI agents use Blowhorn. Compact answers built for agents, rehearsal before every action and clear next steps when something goes wrong. Runs on your computer with Node 18 or later.
label: AI native
lead: The agent interface to Blowhorn
intro: blowhorn-axi is a small command your AI agent runs to use Blowhorn for you. It speaks the agent's language, rehearses before it acts and always says what to do next.
status: Version 0.2.0
layout: ai
weight: 10
lastmod: 2026-10-13
code:
  - title: terminal
    code: "npx blowhorn-axi\n"
    prompt: true
  - title: example output
    lang: text
    copy: false
    code: "count: 2\nprofiles[2]{name,ready}:\n  ana,yes\n  sam,no\nhelp[1]:\n  Run `blowhorn-axi profile status --profile sam`\n"
code_note: Needs Node.js 18 or later and the Blowhorn app. Run it once with npx, nothing to install first.
cards_title: What makes it agent friendly
cards:
  - t: Short answers agents can read
    b: Results come back as TOON, a compact text format made for AI agents. Less to read means faster, cheaper and fewer mix-ups.
  - t: A dry run by default
    b: Every action is a rehearsal unless the agent adds --confirm. It shows what would be sent, then waits.
  - t: Clear next steps
    b: Every answer, and every error, ends with a help list of the commands to try next. Agents don't get stuck guessing.
  - t: Your computer, your limits
    b: It runs on your own computer and follows the risk limits you set for each profile. Nothing secret is printed in its answers.
major: Dry run first. Nobody fires live rounds on my range without a rehearsal.
---
