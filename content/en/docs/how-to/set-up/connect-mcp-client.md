---
title: "Connect an AI assistant over MCP"
description: "Point Claude Code, Claude Desktop, Cursor, or VS Code at the Blowhorn MCP server and let an assistant drive Blowhorn from your computer."
weight: 70
---

Connect an MCP client to the Blowhorn MCP server and an assistant can
use every Blowhorn command: it reads your queue and analytics, drafts
and queues posts, amplifies what went out, and manages profiles. The
server runs on your own computer, from a Blowhorn checkout or from
the installed app, and the assistant
only ever acts through the commands you already run. What the server
is, how it groups its tools, and how it keeps writes safe are in the
[MCP server reference](/docs/reference/mcp-server/).

Before you connect anything, finish Blowhorn's own setup: [install
the app](/docs/how-to/set-up/install-the-app/), [sign a profile in to each
platform](/docs/how-to/set-up/platform-accounts/), and [map each profile to its Chrome
profile](/docs/how-to/set-up/map-chrome-profiles/). The server takes its credentials the way the CLI takes them,
from your existing Blowhorn config and environment, so there is no
second sign-in and nothing new to paste into a client config. If a
profile is not signed in, its runs fail the way a CLI run would.

## Start the server

The steps below run the server from a Blowhorn checkout, with the
checkout's Python environment. If you only installed the app, see
[Use the installed app instead](#use-the-installed-app-instead).
From the checkout root:

```bash
PYTHONPATH=engine ./venv/bin/python -m blowhorn.mcp_server
```

It reads the command bundle from `schemas/dist/openapi.yaml` in the
same checkout and runs the `blowhorn` executable from your PATH. If
you installed the launcher with `make cli-install`, that is already
the case. Otherwise set `BLOWHORN_MCP_CLI` to the executable, or pass
`--cli`, and the server uses that instead. The server prints nothing
but protocol frames to stdout; diagnostics go to stderr, and tool
arguments are never logged, because an argument can itself be a
secret.

Check the server on its own before pointing a client at it. These
targets need the checkout; the app has its own check in
[Use the installed app instead](#use-the-installed-app-instead).

```bash
make mcp-generate   # verify the tool list covers the bundle
make mcp-test       # run the server's tests
```

`--list-tools` prints the tool list as JSON and `--check-coverage`
runs the coverage check, both without serving.

### Use the installed app instead

The app ships its own Python, the server and the command bundle, so
no checkout is needed. This path is verified on Blowhorn.app 1.44.1
on an Intel Mac with macOS 15.

1. Open the app once, so it writes the `blowhorn` command to
   `~/.local/bin`. The app writes that file only when the path is free
   or already holds the app's own command, and leaves any other file
   there alone.
2. Check that `~/.local/bin/blowhorn` contains the line
   `Managed by Blowhorn installer`. If it does not, set
   `BLOWHORN_MCP_CLI` below to the `blowhorn` executable you want
   instead.
3. If `~/.local/bin/blowhorn-mcp` also exists (newer versions of the
   app write it), use it as the whole client entry: the command
   `/Users/<you>/.local/bin/blowhorn-mcp`, no arguments, no `env`. It
   finds the app again if you move it and sets `PYTHONPATH` and
   `BLOWHORN_MCP_CLI` itself. If step 2 found no marker, the entry
   still needs `BLOWHORN_MCP_CLI` in its `env`, naming the `blowhorn`
   executable to use; the command keeps a value the client sets. For
   Claude Code:

   ```bash
   claude mcp add blowhorn -- $HOME/.local/bin/blowhorn-mcp
   ```

4. Otherwise, use the app's interpreter with two environment values,
   filling in your home directory. For Claude Code:

   ```bash
   claude mcp add blowhorn -e PYTHONPATH=/Applications/Blowhorn.app/Contents/Resources/engine/engine -e BLOWHORN_MCP_CLI=$HOME/.local/bin/blowhorn -- /Applications/Blowhorn.app/Contents/Resources/engine/bin/python -m blowhorn.mcp_server
   ```

   For a client that reads a JSON file, the entry is:

   ```json
   {
     "mcpServers": {
       "blowhorn": {
         "command": "/Applications/Blowhorn.app/Contents/Resources/engine/bin/python",
         "args": ["-m", "blowhorn.mcp_server"],
         "env": {
           "PYTHONPATH": "/Applications/Blowhorn.app/Contents/Resources/engine/engine",
           "BLOWHORN_MCP_CLI": "/Users/<you>/.local/bin/blowhorn"
         }
       }
     }
   }
   ```

   Put it in the client's file from [Connect a client](#connect-a-client)
   (VS Code takes it under `servers`, with `"type": "stdio"`). Both
   values are needed: without `BLOWHORN_MCP_CLI`, a client started
   from the Dock or Finder, whose PATH lacks `~/.local/bin`, lists the
   tools but every call fails with
   `blowhorn executable not found: blowhorn`. These paths assume the
   app is in `/Applications`; if you moved it, `~/Applications` for
   one, change both paths to match.

To check the server on its own, without a client, run the app's
interpreter with `PYTHONPATH` set:

```bash
PYTHONPATH=/Applications/Blowhorn.app/Contents/Resources/engine/engine /Applications/Blowhorn.app/Contents/Resources/engine/bin/python -m blowhorn.mcp_server --version
PYTHONPATH=/Applications/Blowhorn.app/Contents/Resources/engine/engine /Applications/Blowhorn.app/Contents/Resources/engine/bin/python -m blowhorn.mcp_server --list-tools
```

With the app, each tool runs the app's `blowhorn` command, which reads
the app's own settings in
`~/Library/Application Support/Blowhorn/home/.blowhorn.yaml`, not a
`./.blowhorn.yaml` in the client's working directory. The full set of
app paths is in the
[MCP server reference](/docs/reference/mcp-server/#from-the-installed-app).

## Connect a client

Every client below runs the same command; only the config file and
its top-level key differ. The examples are for a checkout: fill in
its real paths, where they use `/path/to/blowhorn` as a placeholder.
From a checkout, the only environment value the server needs is
`PYTHONPATH`, pointing at the checkout's `engine` directory. With the
app, use the entry from
[Use the installed app instead](#use-the-installed-app-instead) in the
same files. Put no secrets in these files.

### Claude Code

From a terminal, with the checkout's paths filled in:

```bash
claude mcp add blowhorn -e PYTHONPATH=/path/to/blowhorn/engine -- /path/to/blowhorn/venv/bin/python -m blowhorn.mcp_server
```

The same entry as a project file, `.mcp.json` at the project root,
under the `mcpServers` key:

```json
{
  "mcpServers": {
    "blowhorn": {
      "command": "/path/to/blowhorn/venv/bin/python",
      "args": ["-m", "blowhorn.mcp_server"],
      "env": {"PYTHONPATH": "/path/to/blowhorn/engine"}
    }
  }
}
```

Check it with `claude mcp list`, or `/mcp` inside a session, which
shows whether the server connected.

### Claude Desktop

Edit the Desktop config file, `~/Library/Application Support/Claude/claude_desktop_config.json`
on macOS, and add the same entry under the `mcpServers` key:

```json
{
  "mcpServers": {
    "blowhorn": {
      "command": "/path/to/blowhorn/venv/bin/python",
      "args": ["-m", "blowhorn.mcp_server"],
      "env": {"PYTHONPATH": "/path/to/blowhorn/engine"}
    }
  }
}
```

Quit and reopen Claude Desktop after editing: it only reads the file
at startup.

### Cursor

Create `.cursor/mcp.json` in the project, or `~/.cursor/mcp.json`
for every project, with the entry under the `mcpServers` key:

```json
{
  "mcpServers": {
    "blowhorn": {
      "command": "/path/to/blowhorn/venv/bin/python",
      "args": ["-m", "blowhorn.mcp_server"],
      "env": {"PYTHONPATH": "/path/to/blowhorn/engine"}
    }
  }
}
```

### VS Code

VS Code is the one client here whose file uses a different top-level
key. Create `.vscode/mcp.json` in the workspace with the entry under
`servers`, and a `type` of `stdio`:

```json
{
  "servers": {
    "blowhorn": {
      "type": "stdio",
      "command": "/path/to/blowhorn/venv/bin/python",
      "args": ["-m", "blowhorn.mcp_server"],
      "env": {"PYTHONPATH": "/path/to/blowhorn/engine"}
    }
  }
}
```

## Authentication

There is no OAuth step for this server and no token to create. The
stdio transport does not use OAuth: that belongs to a remote server,
not to a process on your own computer. A client that offers you an
OAuth login for this server is pointed at the wrong thing; the local
server takes its credentials from your Blowhorn config and
environment, exactly as the CLI does.

The server also serves stdio only. Asking it for Streamable HTTP
refuses at startup:

```bash
PYTHONPATH=engine ./venv/bin/python -m blowhorn.mcp_server --transport http
```

A hosted server over HTTP, with its own identity and per-organization
scoping, is separate work and owns that transport, so there is
exactly one remote server. This page covers the local server only.

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

> This post just went live at this URL. Dry-run an amplify from every
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

Tool results never carry secrets. Values under secret-named keys are
replaced before the result reaches the client, and secret-shaped
fragments in text output are replaced the same way. A failed run
reports its exit code and its (redacted) error, never the arguments
it ran.

## Troubleshooting

- **The client shows no Blowhorn server.** Check the command path
  first. From a checkout, the venv Python must exist at the path in
  the config, and `PYTHONPATH` must point at the checkout's `engine`
  directory. With the app,
  `/Applications/Blowhorn.app/Contents/Resources/engine/bin/python`
  must exist (change the path if you moved the app), and `PYTHONPATH`
  must be `/Applications/Blowhorn.app/Contents/Resources/engine/engine`;
  a missing `PYTHONPATH` shows `No module named 'blowhorn'` in the
  server's stderr. Then restart the client: Claude Desktop only reads its config at
  startup, and most clients only pick up a new server on restart.
- **The server starts but lists no tools, or the tools look stale.**
  From a checkout, run `make mcp-generate`: it fails if the tool list
  ever stops matching the command bundle. Restart the server after
  any change to the CLI or the bundle; a command added to the CLI
  appears as a tool the next time the server starts. With the app,
  the tool list follows the app's version: update the app, then
  restart the client.
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
- **A tool call fails with `blowhorn executable not found`.** From a
  checkout, install the launcher with `make cli-install`, or set
  `BLOWHORN_MCP_CLI` to the executable in the client's `env`. With the
  app, open the app once so it rewrites `~/.local/bin/blowhorn`, and
  set `BLOWHORN_MCP_CLI` to `/Users/<you>/.local/bin/blowhorn` in the
  client's `env` (the `blowhorn-mcp` command sets it for you).

## Related

- [MCP server reference](/docs/reference/mcp-server/) - what the
  server is, the tour of its tools, and the safety rules in full
- [Command reference](/docs/reference/cli/) - every command the
  tools wrap, generated from the app itself
- [You are in control](/docs/explanation/youre-in-control/) -
  approval modes, pauses, and every safety control in one place
- [blowhorn-axi](/docs/reference/cli/blowhorn-axi/) - the agent
  CLI: the same commands through a command line instead of MCP
