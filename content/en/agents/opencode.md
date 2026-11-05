{
  "tool": "OpenCode",
  "mark": "OC",
  "logo": "opencode",
  "weight": 20,
  "description": "Use OpenCode with Blowhorn: AGENTS.md instructions, per-command bash permissions and opencode run for marketing jobs across every computer.",
  "lead": "OpenCode reads AGENTS.md and lets you set bash permissions per command. That is exactly the leash a marketing agent needs.",
  "hook": "AGENTS.md and per-command permissions",
  "wire_title": "Write the rules where OpenCode looks",
  "wire_body": "OpenCode reads AGENTS.md. Put the Blowhorn rules there, then set the bash permission map in opencode.json: reads run freely, writes ask, pause is always allowed.",
  "wire_file": "AGENTS.md",
  "wire_lang": "markdown",
  "wire_code": "## Marketing with Blowhorn\n\n- Read state with --json: blowhorn schedule list, blowhorn content list --pending\n- Edit queue rows with blowhorn content upsert and pass --expected-fingerprint\n- Preview publishing with --dry-run; never trigger without asking\n- Emergency stop: blowhorn schedule pause --all --reason \"<why>\"",
  "extra_file": "opencode.json",
  "extra_lang": "json",
  "extra_code": "{\n  \"permission\": {\n    \"bash\": {\n      \"blowhorn schedule list*\": \"allow\",\n      \"blowhorn content list*\": \"allow\",\n      \"blowhorn schedule pause*\": \"allow\",\n      \"blowhorn post*\": \"ask\",\n      \"*\": \"ask\"\n    }\n  }\n}",
  "prompts": [
    "List every scheduled row that is due this week and the computer that will claim it.",
    "Draft three Bluesky rows for profile team-dev from docs/launch.md, unapproved, so I can edit them.",
    "Explain why row 7 did not run.",
    "Pause row 12 only, the rest of the schedule keeps going."
  ],
  "commands": "blowhorn schedule list --due-only --profile all --json\nblowhorn schedule why 7 --json\nblowhorn schedule pause --row 12 --reason \"copy under review\"\nblowhorn schedule resume --row 12",
  "commands_lang": "bash",
  "uses": [
    {
      "t": "Model of your choice",
      "b": "OpenCode talks to many model providers. Blowhorn does not care which one is driving; the CLI and its JSON stay the same."
    },
    {
      "t": "Scripted checks",
      "b": "opencode run takes a prompt from the command line, so a nightly \"what is owed tomorrow\" check fits in a cron line."
    },
    {
      "t": "One row at a time",
      "b": "schedule pause --row N parks a single job on every computer while the rest of the launch keeps moving."
    }
  ],
  "faq": [
    {
      "q": "Why not let it run everything?",
      "a": "You can. We suggest ask for anything that publishes because a post is public the moment it lands, and within a run Blowhorn doesn't retry a failed post."
    },
    {
      "q": "Does it work with OpenCode's other agents?",
      "a": "Any agent in OpenCode that can run bash can run blowhorn. The permission map applies to all of them."
    },
    {
      "q": "Does my agent see my social passwords?",
      "a": "No. Blowhorn posts through your own signed-in browser; the agent only runs commands and reads their output. Review what you allow it to run, as with any tool that acts on your accounts."
    }
  ],
  "major": "Permissions per command. Finally, a recruit who reads the rules of engagement.",
  "title": "Blowhorn for OpenCode",
  "linkTitle": "OpenCode",
  "layout": "agent",
  "lastmod": "2026-10-12",
  "sitemap": {
    "changefreq": "monthly",
    "priority": 0.5
  }
}
