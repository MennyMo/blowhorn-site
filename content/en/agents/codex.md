{
  "tool": "Codex",
  "mark": "Cx",
  "logo": "openai",
  "weight": 40,
  "description": "Use Codex with Blowhorn: AGENTS.md rules, codex exec for unattended checks, and approval settings that keep publishing in your hands.",
  "lead": "Codex follows AGENTS.md and asks before it acts outside its lane. Point it at Blowhorn and keep your finger on approve.",
  "hook": "AGENTS.md, codex exec and approvals",
  "wire_title": "Rules in AGENTS.md, approvals in Codex",
  "wire_body": "Codex reads AGENTS.md from your repo. Blowhorn needs the network and your browser, so sandboxed Codex asks before running it. That's a feature: approve reads, think twice before publishing.",
  "wire_file": "AGENTS.md",
  "wire_lang": "markdown",
  "wire_code": "## Social posting\n\nTool: blowhorn (on PATH). JSON output: add --json.\n1. Read: blowhorn schedule list --json, blowhorn content list --pending --json\n2. Propose changes as a payload and show me\n3. Write with --expected-fingerprint so you never overwrite a newer edit\n4. Stop switch: blowhorn schedule pause --all --reason \"<why>\"",
  "extra_file": "",
  "extra_lang": "",
  "extra_code": "",
  "prompts": [
    "Read the last 30 days of operations grouped by host and tell me which computer is doing the work.",
    "Schedule a daily report row at 08:00 for all profiles. Show the payload before you run it.",
    "Validate every schedule row and fix the ones that fail, one upsert per row."
  ],
  "commands": "blowhorn analytics operations --group-by host --since 30d --json\nblowhorn schedule upsert --payload '{\"Command\":\"report\",\"Profile\":\"all\",\"Run At\":\"2026-10-13 08:00:00\",\"Recurrence\":\"daily\"}' --json\nblowhorn schedule validate --json",
  "commands_lang": "bash",
  "uses": [
    {
      "t": "Unattended checks",
      "b": "codex exec runs a task without the interactive UI, which suits a morning \"what is due, what failed\" pass."
    },
    {
      "t": "Safe edits",
      "b": "Every schedule and content write takes --expected-fingerprint, so a Codex edit is rejected if you changed the row first."
    },
    {
      "t": "Fleet health",
      "b": "analytics operations --group-by host shows which computer ran what, so Codex can spot the one that went quiet."
    }
  ],
  "faq": [
    {
      "q": "Why does Codex ask before running blowhorn?",
      "a": "Blowhorn reaches the network and your browser. Approving it per command is the sensible default."
    },
    {
      "q": "Will two computers post the same row?",
      "a": "Rows are claimed with a lease, coordinated so the same post isn't sent from two computers."
    },
    {
      "q": "Does my agent see my social passwords?",
      "a": "No. Blowhorn posts through your own signed-in browser; the agent only runs commands and reads their output. Review what you allow it to run, as with any tool that acts on your accounts."
    }
  ],
  "major": "Codex asks permission before it fires. Good. The last recruit who did not is still explaining himself to LinkedIn.",
  "title": "Blowhorn for Codex",
  "linkTitle": "Codex",
  "layout": "agent",
  "lastmod": "2026-10-12",
  "sitemap": {
    "changefreq": "monthly",
    "priority": 0.5
  }
}
