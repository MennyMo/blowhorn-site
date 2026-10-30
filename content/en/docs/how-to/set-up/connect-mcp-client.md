---
title: "Connect an AI assistant over MCP"
description: "Point Claude, ChatGPT, Codex, Cursor, VS Code, Windsurf, Gemini CLI, Zed, Cline, or Goose at the Blowhorn MCP server and let an assistant drive Blowhorn from your computer."
weight: 70
---

Connect an MCP client to the Blowhorn MCP server and an assistant can
use every Blowhorn command: it reads your queue and analytics, drafts
and queues posts, amplifies what went out, and manages profiles. The
server runs on your own computer, and the assistant only ever acts
through the commands you already run. What the server is, how it
groups its tools, and how it keeps writes safe are in the
[MCP server reference](/docs/reference/mcp-server/). New to this?
Follow [Connect an assistant and send your first
post](/docs/tutorials/first-mcp-connection/) first.

Before you connect anything, finish Blowhorn's own setup: [install
the app](/docs/how-to/set-up/install-the-app/), [sign a profile in to each
platform](/docs/how-to/set-up/platform-accounts/), and [map each profile to its Google
Chrome profile](/docs/how-to/set-up/map-chrome-profiles/). The server takes its
credentials the way the CLI takes them, from your existing Blowhorn
config and environment, so there is no second sign-in and nothing new
to paste into a client config. Put no secrets in a client config. If a
profile is not signed in, its runs fail the way a CLI run would.

The Blowhorn app runs on macOS, and a checkout also runs on Linux.
The paths below are the macOS ones. On Linux, your home directory is
`/home/<you>` instead of `/Users/<you>`.

## Choose how to start the server

Every client starts the same server. Use the first route that fits.

### Use the blowhorn-mcp command

This is the route to use. It needs Blowhorn 1.61.0 or later.

1. Open the Blowhorn app once. It writes the `blowhorn-mcp` command to
   `~/.local/bin`.
2. Check that `~/.local/bin/blowhorn` contains the line
   `Managed by Blowhorn installer`.
3. Use `/Users/<you>/.local/bin/blowhorn-mcp` as the client's command,
   with no arguments and no `env`.

As a JSON entry, it looks like this:

```json
{
  "mcpServers": {
    "blowhorn": {
      "command": "/Users/<you>/.local/bin/blowhorn-mcp",
      "args": []
    }
  }
}
```

Write the full path in a client's file. A client started from the
Dock or Finder does not have `~/.local/bin` on its PATH. A client you
set up from a terminal command can take `$HOME/.local/bin/blowhorn-mcp`,
because your shell fills in the path.

The command finds the app again if you move it, and sets
`PYTHONPATH` and `BLOWHORN_MCP_CLI` itself. If step 2 found no marker
line, another `blowhorn` sits at that path. Then add `BLOWHORN_MCP_CLI`
to the entry's environment, naming the `blowhorn` executable to use.
`blowhorn-mcp` keeps a value the client sets. In JSON that is
`"env": {"BLOWHORN_MCP_CLI": "/path/to/blowhorn"}`, in TOML a
`[mcp_servers.blowhorn.env]` table, in Goose's YAML the `envs` map, and
on a client's command line its `--env` or `-e` option.

A checkout install (`./tools/install.sh`) writes the same
`~/.local/bin/blowhorn-mcp` command, so the same entry works there.

Check the command on its own before you point a client at it:

```bash
~/.local/bin/blowhorn-mcp --version
~/.local/bin/blowhorn-mcp --list-tools
```

The first prints the Blowhorn version. The second prints the tool
list as JSON. Neither starts serving.

### Coming soon: start it with npx

The `blowhorn-mcp` npm package is coming soon. It is not published
yet, so this route does not work today. Once it is, swap the command in
any entry on this page for `npx` with the arguments `-y blowhorn-mcp`:

```json
{
  "mcpServers": {
    "blowhorn": {
      "command": "npx",
      "args": ["-y", "blowhorn-mcp"]
    }
  }
}
```

On a client's command line, the same swap is `-- npx -y blowhorn-mcp`.
It will still need the Blowhorn app installed and opened once.

### Fallback: the app's own Python

Use this only if your app is older than 1.61.0 and has no
`blowhorn-mcp` command. It assumes the app is in `/Applications`; if
you moved it, `~/Applications` for one, change both paths to match.

```json
{
  "mcpServers": {
    "blowhorn": {
      "command": "/Applications/Blowhorn.app/Contents/Resources/engine/bin/python",
      "args": ["-P", "-m", "blowhorn.mcp_server"],
      "env": {
        "PYTHONPATH": "/Applications/Blowhorn.app/Contents/Resources/engine/engine",
        "BLOWHORN_MCP_CLI": "/Users/<you>/.local/bin/blowhorn"
      }
    }
  }
}
```

Both `env` values are needed. Without `PYTHONPATH` the server does not
start. Without `BLOWHORN_MCP_CLI`, a client started from the Dock or
Finder lists the tools, but every call fails with
`blowhorn executable not found: blowhorn`. The `-P` keeps the client's
working directory off Python's import path, so a file there can never
stand in for one of the server's own modules.

### Fallback: a checkout

Use this from a Blowhorn checkout that has no `blowhorn-mcp` command.
Fill in the checkout's real path for `/path/to/blowhorn`:

```json
{
  "mcpServers": {
    "blowhorn": {
      "command": "/path/to/blowhorn/venv/bin/python",
      "args": ["-P", "-m", "blowhorn.mcp_server"],
      "env": {"PYTHONPATH": "/path/to/blowhorn/engine"}
    }
  }
}
```

The server runs the `blowhorn` executable on your PATH. If you have
not run `make cli-install`, add `BLOWHORN_MCP_CLI` to `env`, naming the
executable. From the checkout root, `make mcp-generate` checks that the
tool list covers every command, and `make mcp-test` runs the server's
tests.

To use either fallback in a client, keep the client's file and
top-level key from its section below. Swap in this `command`, `args`
and `env`.

## Connect your client

Each section below uses the `blowhorn-mcp` command. Fill in your own
home directory for `<you>`.

### Claude Desktop

1. In Claude Desktop, open Settings > Developer > Edit Config. It opens
   `~/Library/Application Support/Claude/claude_desktop_config.json`.
2. Add the entry under `mcpServers`:

   ```json
   {
     "mcpServers": {
       "blowhorn": {
         "command": "/Users/<you>/.local/bin/blowhorn-mcp",
         "args": []
       }
     }
   }
   ```

3. Quit Claude Desktop fully, then reopen it. It reads the file only at
   startup.

To check it, ask Claude which Blowhorn tools it has. If none show up,
read the logs in `~/Library/Logs/Claude/mcp*.log`.
[Vendor docs](https://modelcontextprotocol.io/docs/develop/connect-local-servers).

### Claude Code

Add the server for every project:

```bash
claude mcp add --scope user blowhorn -- $HOME/.local/bin/blowhorn-mcp
```

Without `--scope user`, the server is added for the current project
only. To share it with a project, put the entry in `.mcp.json` at the
project root instead:

```json
{
  "mcpServers": {
    "blowhorn": {
      "command": "/Users/<you>/.local/bin/blowhorn-mcp",
      "args": []
    }
  }
}
```

Check it with `claude mcp list`, or `/mcp` inside a session.
[Vendor docs](https://code.claude.com/docs/en/mcp).

### ChatGPT

The ChatGPT desktop app can run this server. ChatGPT on the web
cannot: it connects only to remote servers over HTTPS, and this server
runs on your computer. The web needs the hosted Blowhorn MCP server,
which is coming.

In the ChatGPT desktop app:

1. Open Settings > MCP servers > Add server.
2. Choose STDIO.
3. Enter the command `/Users/<you>/.local/bin/blowhorn-mcp`.
4. Restart ChatGPT.

The desktop app shares its MCP config with the Codex CLI, in
`~/.codex/config.toml`. A server you add in one shows up in the other.
To check it, ask ChatGPT which Blowhorn tools it has.
[Vendor docs](https://developers.openai.com/codex/mcp).

### OpenAI Codex CLI

Add the server from a terminal:

```bash
codex mcp add blowhorn -- $HOME/.local/bin/blowhorn-mcp
```

Or add it to `~/.codex/config.toml`, or to a trusted project's
`.codex/config.toml`:

```toml
[mcp_servers.blowhorn]
command = "/Users/<you>/.local/bin/blowhorn-mcp"
args = []
```

Check it with `codex mcp list`, or `/mcp` inside a session. The ChatGPT
desktop app reads the same file.
[Vendor docs](https://developers.openai.com/codex/mcp).

### Cursor

Create `~/.cursor/mcp.json` for every project, or `.cursor/mcp.json`
in one project, with the entry under `mcpServers`:

```json
{
  "mcpServers": {
    "blowhorn": {
      "type": "stdio",
      "command": "/Users/<you>/.local/bin/blowhorn-mcp",
      "args": []
    }
  }
}
```

The `type` line is optional. If the server does not connect, open the
Output panel and choose MCP Logs.
[Vendor docs](https://cursor.com/docs/context/mcp).

### VS Code with GitHub Copilot

The quickest route is the Command Palette:

1. Run MCP: Add Server.
2. Choose Command (stdio).
3. Enter the command `/Users/<you>/.local/bin/blowhorn-mcp`.
4. Enter the server ID `blowhorn`.

To write the file yourself, use the portable format. Put the entry in
`~/.copilot/mcp-config.json` for every workspace, or `.mcp.json` at a
workspace root, under `mcpServers`:

```json
{
  "mcpServers": {
    "blowhorn": {
      "command": "/Users/<you>/.local/bin/blowhorn-mcp",
      "args": []
    }
  }
}
```

VS Code's own format also works: `.vscode/mcp.json` in a workspace, or
the `mcp.json` in your user profile. That file's top-level key is
`servers`, and the entry needs a `type` of `stdio`:

```json
{
  "servers": {
    "blowhorn": {
      "type": "stdio",
      "command": "/Users/<you>/.local/bin/blowhorn-mcp",
      "args": []
    }
  }
}
```

Do not mix the two keys. A file under `.vscode/` takes `servers`; the
portable files take `mcpServers`.
[Vendor docs](https://code.visualstudio.com/docs/copilot/customization/mcp-servers).

### Windsurf (Devin Desktop)

Windsurf is now Devin Desktop. Add the server for your user from a
terminal:

```bash
devin mcp add -s user blowhorn -- $HOME/.local/bin/blowhorn-mcp
```

Or put the entry in `~/.config/devin/mcp_config.json`, or
`.devin/mcp_config.json` in a project, under `mcpServers`:

```json
{
  "mcpServers": {
    "blowhorn": {
      "command": "/Users/<you>/.local/bin/blowhorn-mcp",
      "args": []
    }
  }
}
```

Older Windsurf builds read `~/.codeium/windsurf/mcp_config.json`, with
the same `mcpServers` shape. Devin Desktop imports that file.
[Vendor docs](https://docs.devin.ai/desktop/devin-local/customizations).

### Gemini CLI

Add the server for your user:

```bash
gemini mcp add -s user blowhorn $HOME/.local/bin/blowhorn-mcp
```

Without `-s user`, it is added to the current project only. Or put the
entry in `~/.gemini/settings.json`, or `.gemini/settings.json` in a
project, under `mcpServers`:

```json
{
  "mcpServers": {
    "blowhorn": {
      "command": "/Users/<you>/.local/bin/blowhorn-mcp",
      "args": []
    }
  }
}
```

Gemini CLI starts a local server only in a trusted folder. Run
`gemini trust` in the folder you work from. Keep the name `blowhorn`:
server names may not contain underscores. Check it with `/mcp` inside a
session.
[Vendor docs](https://geminicli.com/docs/tools/mcp-server/).

### Zed

In Zed, open Settings > AI > MCP Servers > Add Server, then choose Add
Local Server. Or run `zed: open settings file` and add the entry under
`context_servers`:

```json
{
  "context_servers": {
    "blowhorn": {
      "command": "/Users/<you>/.local/bin/blowhorn-mcp",
      "args": [],
      "env": {}
    }
  }
}
```

A green dot next to the server, with "Server is active", means it
connected. Zed asks before each tool call by default. Keep that
setting.
[Vendor docs](https://zed.dev/docs/ai/mcp).

### Cline

In the editor:

1. Click the MCP Servers icon.
2. Open the Configure tab.
3. Click Configure MCP Servers.
4. Add the entry under `mcpServers`:

   ```json
   {
     "mcpServers": {
       "blowhorn": {
         "command": "/Users/<you>/.local/bin/blowhorn-mcp",
         "args": [],
         "env": {},
         "disabled": false,
         "autoApprove": []
       }
     }
   }
   ```

Leave `autoApprove` empty, so Cline asks you before each tool call.

For the Cline CLI, add the server from a terminal. It writes
`~/.cline/data/settings/cline_mcp_settings.json`:

```bash
cline mcp add blowhorn --yes -- $HOME/.local/bin/blowhorn-mcp
```

[Vendor docs](https://docs.cline.bot/mcp/configuring-mcp-servers).

### Goose

Run `goose configure`, choose Add Extension, then Command-line
Extension, and enter the command. Or add it under `extensions` in
Goose's YAML config file, in the `~/.config/goose/` folder:

```yaml
extensions:
  blowhorn:
    type: stdio
    name: blowhorn
    enabled: true
    cmd: /Users/<you>/.local/bin/blowhorn-mcp
    args: []
    envs: {}
    timeout: 300
```

Goose calls the command `cmd`, not `command`. To try the server in one
session without saving it:

```bash
goose session --with-extension "$HOME/.local/bin/blowhorn-mcp"
```

[Vendor docs](https://github.com/block/goose/blob/main/documentation/docs/guides/config-files.md).

## Authentication

There is no OAuth step for this server and no token to create. The
stdio transport does not use OAuth: that belongs to a remote server,
not to a process on your own computer. A client that offers you an
OAuth login for this server is pointed at the wrong thing. The local
server takes its credentials from your Blowhorn config and
environment, exactly as the CLI does.

With the app, each tool runs the app's `blowhorn` command. It reads
the app's own settings in
`~/Library/Application Support/Blowhorn/home/.blowhorn.yaml`, not a
`./.blowhorn.yaml` in the client's working directory.

The server serves stdio only. Asking it for HTTP refuses at startup:

```bash
~/.local/bin/blowhorn-mcp --transport http
```

A hosted Blowhorn MCP server, with its own sign-in, is coming. This
page covers the local server only.

## Example prompts and workflows

The assistant picks the tools; you approve the writes. These prompts
are written so the dry run comes first and nothing goes out on the
first pass.

### Draft and queue a post

> Draft a LinkedIn post for profile alex announcing the v2.4 release,
> queue it for Tuesday 09:00, and show me the dry run before you
> confirm anything.

The assistant drafts with the content tools and queues the row. A
changing tool runs with `--dry-run` unless the call confirms it, so
the first pass shows what would be queued and queues nothing. Say
go, and the assistant re-runs it confirmed.

### Check analytics

> How did last week's posts do on LinkedIn, and which profile drove
> the most engagement?

Read-only tools run as asked. The assistant reads the analytics
tools and reports back; nothing is written, so there is nothing to
confirm.

### Amplify a post

> This post went live at this URL. Dry-run an amplify from every
> profile on this computer, then wait for my go.

The amplify runs as a rehearsal first, naming what each profile
would do. Confirm it and the real run follows. The same shape works
for a GitHub issue or pull request: the assistant amplifies from
each profile's own credential, and re-running adds no reaction twice.

### Manage profiles

> Which profiles are signed in and ready, and which ones need
> attention?

The assistant reads the profile tools and reports each profile's
state. Changing a profile, switching the current one, or setting a
risk limit is a write: dry run first, confirm to act, same as every
other write. `profile status` and `chrome discover` count as writes
too, because each records the sign-ins it reads as the profile's
accounts in your Blowhorn account.

## Safety

Writes need confirmation, and dry run is the default. A tool that
only reads runs as asked. A tool that changes anything runs with
`--dry-run` unless the call passes `confirm` as true. A call that
passes both `confirm` and `dry_run` is refused as contradictory, and
a changing command with no dry-run path refuses without `confirm`
rather than running for real.

The server also marks its calls as agent calls, so a configured
approval mode sees them for what they are: it sets
`BLOWHORN_ACTOR=agent` for the command it runs, unless you already
set that variable. Under approval mode `agent` or `all`, the queue
rules in [You are in control](/docs/explanation/youre-in-control/)
therefore apply to MCP calls exactly as they apply to any other
agent caller. `content_approve` is one of the tools, but
`content approve` refuses an agent caller in every mode, so an MCP
call cannot approve queued work. That only holds work back under
`agent` or `all`: under `off`, the agent's own writes keep the
`Approved?` value it sets, and a confirmed ad-hoc action publishes.
Do not set `BLOWHORN_ACTOR=human` in a client's `env`: the server
leaves an existing value alone. If the server's environment sets
`BLOWHORN_ACTOR=human` and does not set
`BLOWHORN_RUN_SOURCE=scheduler`, every MCP call counts as a person,
so under `agent` the agent's writes and confirmed ad-hoc actions go
through unheld, under `all` writes still land pending, and in any
mode the agent can approve its own work. With
`BLOWHORN_RUN_SOURCE=scheduler`, the calls still count as an agent
and nothing changes.
Note the limit of this transport: there is no desktop-app
approval step here. On this server, `confirm` true is the approval.
If you want a person to approve each write in the app, use the queue
and the approval mode, not a confirmed MCP call.

Keep your client's own approval prompt on, too. Zed, Cline and most
other clients ask before each tool call unless you turn that off.

Tool results never carry secrets. Values under secret-named keys are
replaced before the result reaches the client, and secret-shaped
fragments in text output are replaced the same way. A failed run
reports its exit code and its (redacted) error, never the arguments
it ran.

How these rules fit together is in
[How the MCP server keeps you in control](/docs/explanation/mcp-and-safety/).

## Troubleshooting

- **The client shows no Blowhorn server.** Run
  `~/.local/bin/blowhorn-mcp --version` in a terminal. If the file is
  missing, open the Blowhorn app once, or update it to 1.61.0 or later.
  If it says the app is in the Trash or was not found, put the app back
  or reinstall it. Check that the client's entry uses the full path,
  not `~`. Then restart the client: most clients only pick up a new
  server on restart, and Claude Desktop only reads its config at
  startup.
- **A tool call fails with `blowhorn executable not found`.** Open the
  app once, so it rewrites `~/.local/bin/blowhorn`. If that file lacks
  the line `Managed by Blowhorn installer`, set `BLOWHORN_MCP_CLI` in the
  entry's environment to the `blowhorn` executable you want. With a
  fallback entry, set `BLOWHORN_MCP_CLI` to
  `/Users/<you>/.local/bin/blowhorn`.
- **A fallback entry shows `No module named 'blowhorn'`.** Its
  `PYTHONPATH` is missing or wrong. With the app it must be
  `/Applications/Blowhorn.app/Contents/Resources/engine/engine`; from a
  checkout, the checkout's `engine` directory. Better, switch to the
  `blowhorn-mcp` command.
- **The server starts but lists no tools, or the tools look stale.**
  The tool list follows the app's version. Update the app, then
  restart the client. From a checkout, run `make mcp-generate` and
  restart the server after any change to the CLI.
- **A write only produced a dry run.** That is the default, not a
  failure. The assistant must re-run the call with `confirm` true
  for the real run. If you did not mean to confirm, the dry run is
  the whole result: nothing was written.
- **A call is refused as contradictory.** It passed both `confirm`
  and `dry_run`. Drop one: `confirm` true for the real run, or
  `dry_run` for the rehearsal.
- **A changing call is refused without running.** It has no dry-run
  path, so it refuses rather than running for real without
  `confirm`. Confirm it, or leave it refused.
- **The server exits when asked for HTTP.** That is deliberate: this
  server is local stdio only, and `--transport http` refuses with
  the reason. Use `--transport stdio`, the default.
- **ChatGPT on the web cannot find the server.** It connects only to
  remote servers. Use the ChatGPT desktop app.

## Related

- [MCP server reference](/docs/reference/mcp-server/) - what the
  server is, the tour of its tools, and the safety rules in full
- [How the MCP server keeps you in control](/docs/explanation/mcp-and-safety/) -
  how the server, the CLI and approvals fit together
- [Command reference](/docs/reference/cli/) - every command the
  tools wrap, generated from the app itself
- [You are in control](/docs/explanation/youre-in-control/) -
  approval modes, pauses, and every safety control in one place
- [blowhorn-axi](/docs/reference/cli/blowhorn-axi/) - the agent
  CLI: the same commands through a command line instead of MCP
