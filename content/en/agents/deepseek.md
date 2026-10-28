{
  "tool": "DeepSeek",
  "mark": "DS",
  "logo": "deepseek",
  "weight": 60,
  "description": "Run Blowhorn from a DeepSeek-powered agent harness: the same CLI, the same JSON, whichever terminal agent you point at DeepSeek.",
  "lead": "DeepSeek is a model, and the harness around it decides how it runs commands. Blowhorn fits any harness with a shell tool.",
  "hook": "Any harness, one CLI",
  "wire_title": "Bring the model, keep the commands",
  "wire_body": "Whether DeepSeek sits behind OpenCode, Claude Code with a compatible endpoint, or a harness of your own, the setup is the same: blowhorn on the PATH, a rules block and JSON output. Long context turns a big changelog into a week of rows.",
  "wire_file": "AGENTS.md",
  "wire_lang": "markdown",
  "wire_code": "## Blowhorn rules\n\n- Always add --json and parse it; never scrape human output\n- One content row per platform per message\n- Writes: blowhorn content upsert --row N --expected-fingerprint <fp>\n- Stop everything: blowhorn schedule pause --all --reason \"<why>\"",
  "extra_file": "",
  "extra_lang": "",
  "extra_code": "",
  "prompts": [
    "Read CHANGELOG.md and plan a week of posts: one row per platform per day, unapproved, with Promote On times at 09:00.",
    "Compare this month's analytics to last month's and tell me which platform earned its keep.",
    "List every queue row in state invalid and say why."
  ],
  "commands": "blowhorn content list --json\nblowhorn analytics history --since 60d --json\nblowhorn schedule validate --json\nblowhorn schedule get 9 --json",
  "commands_lang": "bash",
  "uses": [
    {
      "t": "Planning a campaign",
      "b": "Feed it the release notes and get a week of queue rows back, each one a reviewable payload."
    },
    {
      "t": "Cost-aware runs",
      "b": "Reads are cheap and repeatable. Let the model poll status often and save the expensive thinking for copy."
    },
    {
      "t": "Swap models freely",
      "b": "Change the model behind your harness tomorrow and nothing in Blowhorn changes."
    }
  ],
  "faq": [
    {
      "q": "Is there a DeepSeek-specific integration?",
      "a": "No, and it does not need one. The harness runs the commands; Blowhorn answers in JSON."
    },
    {
      "q": "Where does my data live?",
      "a": "Your queue, schedule and results stay in sync in your account; the work happens on your computers."
    },
    {
      "q": "Does my agent see my social passwords?",
      "a": "No. Blowhorn posts through your own signed-in browser; the agent only runs commands and reads their output. Review what you allow it to run, as with any tool that acts on your accounts."
    }
  ],
  "major": "I do not care whose brain is in the helmet. I care that the post goes out on time.",
  "title": "Blowhorn for DeepSeek",
  "linkTitle": "DeepSeek",
  "layout": "agent",
  "lastmod": "2026-10-12",
  "sitemap": {
    "changefreq": "monthly",
    "priority": 0.5
  }
}
