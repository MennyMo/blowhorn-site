---
title: Blowhorn MCP server
seo_title: The Blowhorn MCP server - every Blowhorn action for any AI assistant
description: The Blowhorn MCP server lets AI assistants find and use every Blowhorn action, with your approval rules and risk limits applied to every step, and every action running on your own computer.
label: AI native
lead: Every Blowhorn action, ready for any AI assistant
intro: MCP is a common standard that lets AI assistants plug into apps. The Blowhorn MCP server lets an assistant see everything Blowhorn can do and use it, while you stay in command.
status: Available now
layout: ai
weight: 20
lastmod: 2026-10-30
code:
  - title: terminal
    code: "claude mcp add blowhorn -- ~/.local/bin/blowhorn-mcp\n"
    prompt: true
code_note: "Open Blowhorn 1.61 or later once so it writes ~/.local/bin/blowhorn-mcp. Other clients: [Connect an AI assistant over MCP](/docs/how-to/set-up/connect-mcp-client/)."
cards_title: Standard issue
cards:
  - t: Every action, described
    b: Everything the Blowhorn command line can do is described in a form assistants understand, so they know what each action needs before they ask.
  - t: Works where your assistant works
    b: "It runs on your own computer through the `blowhorn-mcp` command the app installs, for any MCP client: Claude Code, Claude Desktop, Cursor, VS Code. A hosted server is coming soon."
  - t: Easy to find
    b: Clear docs and a setup guide for each client. Catalog listings coming soon.
rules_title: You stay in charge
rules:
  - t: Approve before it posts
    b: With approval mode on, anything an agent queues waits for your OK in the app, and an agent can never approve its own content. Every write is a dry run until confirmed.
  - t: Risk limits on every action
    b: The limits you set for each profile apply to everything an agent does, every time.
  - t: Runs on your computer
    b: Every action runs locally on your own computer, just like the app.
major: Any assistant can report for duty. None of them fires without your orders.
---
