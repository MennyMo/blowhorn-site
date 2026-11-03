# Adding a platform action example

Every supported action on every supported platform has a tabbed example on its
docs page (`/docs/reference/platforms/<id>/#action-<id>`). The tabs are App,
CLI, REST API, MCP, then Skill. Content lives in data, not in the Markdown
page. Hyphens, never em dashes.

## Where the data lives

| File | What it is |
|---|---|
| [`data/actions.json`](../data/actions.json) | Action vocabulary: `id`, display `name`, default description. Templates never hand-list action names. |
| [`data/platforms/<id>.yaml`](../data/platforms/) | Which of those ids this platform supports. Optional `behavior` overrides the default description where the platform differs. Optional `limits`. |
| [`data/action_examples.json`](../data/action_examples.json) | One entry per supported platform+action. Each surface is `available` or `placeholder`. |
| [`schemas/actions.schema.json`](../schemas/actions.schema.json) and [`schemas/action_examples.schema.json`](../schemas/action_examples.schema.json) | `make check-schemas` validates both, then [`.github/scripts/check_action_examples.py`](../.github/scripts/check_action_examples.py) fails if coverage dropped. |

Every platform docs page calls `{{< supported-actions "<id>" >}}`. That
shortcode renders the actions table (Action, What it does, Limits / notes)
and the example tabs from this data. Each action name links to its example
section on the same page (`#action-<id>`); there is no separate Example
column. You do not edit the page to add an example or to list the actions.
`make check-platform-docs` fails a hand-written action list, a page that skips
the shortcode, a dead `#action-<id>` link, an action name without one, or an
Example column coming back. A listed action is supported, so the table shows
no Supported label and no check mark (the check fails either); only an
exception, such as a coming-soon platform, shows a status, as an icon with an
accessible name and tooltip and no text label. A Status column with no
exception in it fails too.

When every surface of an example is `placeholder`, its tabs open on
`defaultSurface` (`cli`), which reads "Not in the CLI yet" with the CLI notes.

## Add or fill an example

1. If the action is new to Blowhorn, append it to `data/actions.json` (id, name,
   description). Use a hyphenated lowercase id (`post`, `find`).
2. List that id under `actions:` in `data/platforms/<platform>.yaml`. Set
   `behavior` only when this platform's "what it does" is not the vocabulary
   default. Set `limits` when there is a cap or a read-only note.
3. Add a matching object to `data/action_examples.json`:

   ```json
   {
     "platform": "linkedin",
     "action": "comment",
     "surfaces": {
       "app": {
         "status": "placeholder",
         "screenshot": "assets/docs/actions/linkedin/comment.png"
       },
       "cli": {
         "status": "available",
         "command": "blowhorn comment --platform linkedin --target \"https://www.linkedin.com/feed/update/urn:li:activity:123/\" --message \"Great post!\"",
         "cliRef": "/docs/reference/cli/comment/"
       },
       "rest": {
         "status": "available",
         "notes": "Every Blowhorn action is on the REST API, from the same schema as the CLI. Parameters match the CLI reference."
       },
       "mcp": {
         "status": "available",
         "prompt": "Comment on this LinkedIn post as me: https://www.linkedin.com/feed/update/urn:li:activity:123/ with the message Great post!",
         "notes": "The prompt to give an AI assistant connected to the Blowhorn MCP server."
       },
       "skill": {
         "status": "available",
         "notes": "The Blowhorn skill teaches your agent this action: read first, rehearse, then ask before it fires."
       }
     }
   }
   ```

4. CLI: copy a command from [`content/en/docs/reference/cli/`](../content/en/docs/reference/cli/).
   Do not invent flags. If the action has no CLI command, set `cli.status` to
   `placeholder` and say so in `notes`. The check script requires every
   `--flag` in an available command to appear on the `cliRef` page.
5. App screenshot: keep `status` as `placeholder` until the PNG exists. Put
   the file at `static/assets/docs/actions/<platform>/<action>.png` (the path
   in `screenshot` without the `static/` prefix). The pane fills itself when
   that file is present; you do not have to change the JSON.
6. Run `make check-schemas`, then `make check`.

## Tabs shortcode

For a one-off tabset in Markdown, not an action example:

```
{{< tabs id="unique" group="surface" label="Examples" >}}
{{< tab id="cli" name="CLI" >}}
command here
{{< /tab >}}
{{< /tabs >}}
```

`group="surface"` shares the chosen tab across the page (localStorage), so
switching to CLI switches every grouped set. Without JavaScript every pane
stays visible, stacked. Action examples use this through
`{{< action-examples platform="linkedin" action="comment" >}}`.
