{
  "tool": "Grok",
  "mark": "Gk",
  "logo": "grok",
  "weight": 50,
  "description": "Use Grok as your marketing agent with Blowhorn: plain-language prompts turned into blowhorn commands for scheduling, queueing and team amplification.",
  "lead": "Grok in your terminal can run commands. Hand it the Blowhorn CLI and it turns a sentence into a launch plan you approve.",
  "hook": "Prompts in, blowhorn commands out",
  "wire_title": "One instructions file, any Grok agent",
  "wire_body": "However you run Grok, it needs blowhorn on the PATH and a short instructions file. Use AGENTS.md if your setup reads it; otherwise paste the block into its project instructions.",
  "wire_file": "AGENTS.md",
  "wire_lang": "markdown",
  "wire_code": "## Blowhorn\n\nYou can run the blowhorn CLI. Prefer --json.\n- What is due: blowhorn schedule list --due-only --json\n- What is queued: blowhorn content list --pending --json\n- Amplify a live post: blowhorn post --platform <p> --amplify <url> --profile all --dry-run\nAsk me before any command without --dry-run that publishes.",
  "extra_file": "",
  "extra_lang": "",
  "extra_code": "",
  "prompts": [
    "Our launch post is live on X. Dry-run a repost from every profile on this computer.",
    "Find the latest posts mentioning our project since Monday and list the ones worth a reply.",
    "Write tomorrow's X row in my voice from this changelog and leave it unapproved."
  ],
  "commands": "blowhorn post --platform x --profile all --amplify \"https://x.com/<handle>/status/<id>\" --dry-run\nblowhorn find --platform x --query \"blowhorn\" --since 2026-10-12 --limit 25\nblowhorn content list --pending --json",
  "commands_lang": "bash",
  "uses": [
    {
      "t": "The sound wave",
      "b": "One post goes out, then every profile you and your team run repeats it from their own computers. Grok fires the amplify; Blowhorn coordinates who does what."
    },
    {
      "t": "Listening",
      "b": "blowhorn find searches posts with filters for author, mentions, language and dates, so Grok can bring you the conversations worth joining."
    },
    {
      "t": "In your voice",
      "b": "Posts go out from your own accounts in your own browser, not from a bot account."
    }
  ],
  "faq": [
    {
      "q": "Which Grok tool do I need?",
      "a": "Any Grok setup that can run shell commands on your computer. Blowhorn only needs a CLI call."
    },
    {
      "q": "Is amplifying everyone at once a good idea?",
      "a": "Use --dry-run first, then let it go. Blowhorn paces actions and coordinates the fleet so the same post isn't sent from two computers."
    },
    {
      "q": "Does my agent see my social passwords?",
      "a": "No. Blowhorn posts through your own signed-in browser; the agent only runs commands and reads their output. Review what you allow it to run, as with any tool that acts on your accounts."
    }
  ],
  "major": "A post with no amplification is a bugle in an empty barracks. Grok, sound the call.",
  "title": "Blowhorn for Grok",
  "linkTitle": "Grok",
  "layout": "agent",
  "lastmod": "2026-10-12",
  "sitemap": {
    "changefreq": "monthly",
    "priority": 0.5
  }
}
