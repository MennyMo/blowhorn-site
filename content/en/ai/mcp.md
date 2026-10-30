{
  "title": "Blowhorn MCP server",
  "linkTitle": "MCP server",
  "seo_title": "The Blowhorn MCP server - every Blowhorn action for any AI assistant",
  "description": "The Blowhorn MCP server lets your AI assistant draft and rehearse your marketing, then act only when you give the order. 113 tools, every write a dry run first, all on your own computer.",
  "tool": "MCP",
  "who": "your assistant",
  "mark": "MCP",
  "weight": 20,
  "lead": "Your assistant drafts and rehearses. You give the order. The Blowhorn MCP server gives any MCP assistant a tool for every Blowhorn command, and every write comes back as a dry run until you say go.",
  "hook": "One local command, 113 tools",
  "crumb_label": "AI native",
  "crumb_url": "/ai/",
  "steps": [
    {
      "t": "Open Blowhorn once",
      "b": "Blowhorn desktop 1.61.0 or later writes the blowhorn-mcp command to ~/.local/bin each time the app opens."
    },
    {
      "t": "Add it to your assistant",
      "b": "One line, or one config entry, points your MCP client at that command. It starts the local server over stdio, on your computer."
    },
    {
      "t": "Say what you want",
      "b": "Your assistant calls the tools. Reads run as asked, every write is a dry run first, and you give the order that makes it real."
    }
  ],
  "wire_title": "Plug it into your assistant",
  "wire_body": "Open Blowhorn once so the app writes the command, then point your client at it. For Claude Code, one line does it. Cursor reads the same command from its mcp.json.",
  "wire_file": "terminal",
  "wire_lang": "bash",
  "wire_code": "claude mcp add blowhorn -- ~/.local/bin/blowhorn-mcp",
  "extra_file": ".cursor/mcp.json",
  "extra_lang": "json",
  "extra_code": "{\n  \"mcpServers\": {\n    \"blowhorn\": {\n      \"command\": \"/Users/you/.local/bin/blowhorn-mcp\"\n    }\n  }\n}",
  "wire_note": "Claude Desktop takes the same command in its config file. New to this? [Connect an assistant and send your first post](/docs/tutorials/first-mcp-connection/) walks through it. [Connect an AI assistant over MCP](/docs/how-to/set-up/connect-mcp-client/) has the steps for every client, including [Claude Code](/docs/how-to/set-up/connect-mcp-client/#claude-code), [Claude Desktop](/docs/how-to/set-up/connect-mcp-client/#claude-desktop), [Cursor](/docs/how-to/set-up/connect-mcp-client/#cursor) and [VS Code](/docs/how-to/set-up/connect-mcp-client/#vs-code-with-github-copilot). [Source and listings](https://github.com/blowhorn-ai/blowhorn-mcp): the launcher, plugin manifests and listing files live in the public blowhorn-mcp repo.",
  "prompts": [
    "Draft a release post from my personal profile for Tuesday at 9:00 and queue it. Dry run first, show me what would be queued, and wait for my go before you confirm.",
    "Someone asked whether the new release works offline. Draft a reply from my company profile that answers that one question. Show me the dry run and wait for my go.",
    "Read last week's numbers across my profiles and tell me which post did best. Read only, nothing gets written.",
    "Pause everything, with the reason \"waiting on legal review\". Show me the dry run first, then confirm once I say go."
  ],
  "commands_title": "What your assistant sees",
  "commands_file": "assistant",
  "commands_lang": "text",
  "commands_prompt": false,
  "commands": "# claude mcp list\nblowhorn: /Users/you/.local/bin/blowhorn-mcp - Connected\n\n# the tools it calls, one per Blowhorn command\npost                dry_run: true     (confirm: true after your go)\ncontent_upsert      dry_run: true     (confirm: true after your go)\nanalytics_history   read only, runs as asked\nschedule_pause      dry_run: true     (confirm: true after your go)",
  "uses": [
    {
      "t": "Release day",
      "b": "Have your assistant turn the changelog into queued posts, dry-run each one, and wait for your go. Nothing is queued until you say so."
    },
    {
      "t": "The first hour",
      "b": "Ask what is due, what is queued and what needs your attention. Reads run as asked, so the answer comes straight back."
    },
    {
      "t": "The weekly read-out",
      "b": "Let it read last week's numbers and write Friday's summary. Nothing is written, so there is nothing to confirm."
    }
  ],
  "faq": [
    {
      "q": "Does it run in the cloud?",
      "a": "No. It runs on your own computer, through the blowhorn-mcp command the app writes. A hosted server is coming soon; it is design only today."
    },
    {
      "q": "Can I npx it?",
      "a": "Coming soon. Today, use ~/.local/bin/blowhorn-mcp, which the Blowhorn app writes each time it opens."
    },
    {
      "q": "Can the agent approve or publish on its own?",
      "a": "No. Every write is a dry run until the assistant re-runs it confirmed, and an agent can never approve its own content. With approval mode on, the work it queues waits for you in the app. [How the MCP server keeps you in control](/docs/explanation/mcp-and-safety/) has the whole picture."
    },
    {
      "q": "Where is the MCP server source?",
      "a": "The public [blowhorn-mcp repo](https://github.com/blowhorn-ai/blowhorn-mcp) on GitHub holds the launcher, the Claude Code and Cursor plugin manifests, the Gemini CLI extension, the agent skill and the listing files. The server itself ships inside the Blowhorn desktop app. The npx launcher and catalog listings are coming soon."
    },
    {
      "q": "Is it listed in MCP catalogs?",
      "a": "Coming soon."
    },
    {
      "q": "Does my assistant see my passwords?",
      "a": "No. Tool results never carry secrets. See [how the MCP server keeps you in control](/docs/explanation/mcp-and-safety/)."
    },
    {
      "q": "Which assistants can use it?",
      "a": "Any MCP client that can start a local command: Claude Code, Claude Desktop, Cursor and VS Code, for example. [Connect an AI assistant over MCP](/docs/how-to/set-up/connect-mcp-client/) has the steps for each, and the [first-connection tutorial](/docs/tutorials/first-mcp-connection/) takes you through your first post."
    }
  ],
  "cta_title": "Rehearse first, then give the order",
  "more_title": "Other ways to bring your assistant",
  "major": "Any assistant can report for duty. None of them fires without your orders.",
  "status": "Available now",
  "label": "AI native",
  "layout": "agent",
  "lastmod": "2026-10-30",
  "sitemap": {
    "changefreq": "monthly",
    "priority": 0.5
  }
}
