---
title: "Connect an AI assistant over MCP"
description: "Point Claude Code, Claude Desktop, Cursor, or VS Code at the Blowhorn MCP server and let an assistant drive Blowhorn from your computer."
weight: 70
---

Connect an MCP client to the Blowhorn MCP server and an assistant can
use every Blowhorn command: it reads your queue and analytics, drafts
and queues posts, amplifies what went out, and manages profiles. The
server runs on your own computer, from a Blowhorn checkout, and the
assistant only ever acts through the commands you already run. What
the server is, how it groups its tools, and how it keeps writes safe
are in the [MCP server reference](/docs/reference/mcp-server/).

Before you connect anything, finish Blowhorn's own setup: [install
the app](/docs/how-to/set-up/install-the-app/), [sign a profile in to each
platform](/docs/how-to/set-up/platform-accounts/), and [map each profile to its Chrome
profile](/docs/how-to/set-up/map-chrome-profiles/). The server takes its credentials the way the CLI takes them,
from your existing Blowhorn config and environment, so there is no
second sign-in and nothing new to paste into a client config. If a
profile is not signed in, its runs fail the way a CLI run would.

## Start the server

Today the server runs from a Blowhorn checkout, with the checkout's
Python environment. From the checkout root:

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

Check the server on its own before pointing a client at it:

```bash
make mcp-generate   # verify the tool list covers the bundle
make mcp-test       # run the server's tests
```

`--list-tools` prints the tool list as JSON and `--check-coverage`
runs the coverage check, both without serving.

## Connect a client

Every client below runs the same command; only the config file and
its top-level key differ. Fill in your checkout's real paths: the
examples use `/path/to/blowhorn` as a placeholder. Put no secrets in
these files. The only environment value the server needs is
`PYTHONPATH`, pointing at the checkout's `engine` directory.

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

A hosted server over HTTP, with its own identity and per-profile
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
agent caller, including the rule that an agent cannot approve its own
work. Note the limit of this transport: there is no desktop-app
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
  first: the venv Python must exist at the path in the config, and
  `PYTHONPATH` must point at the checkout's `engine` directory.
  Then restart the client: Claude Desktop only reads its config at
  startup, and most clients only pick up a new server on restart.
- **The server starts but lists no tools, or the tools look stale.**
  Run `make mcp-generate` in the checkout: it fails if the tool list
  ever stops matching the command bundle. Restart the server after
  any change to the CLI or the bundle; a command added to the CLI
  appears as a tool the next time the server starts.
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
- **A tool call fails with the `blowhorn` executable missing.**
  Install the launcher with `make cli-install`, or set
  `BLOWHORN_MCP_CLI` to the executable in the client's `env`.

## Related

- [MCP server reference](/docs/reference/mcp-server/) - what the
  server is, the tour of its tools, and the safety rules in full
- [Command reference](/docs/reference/cli/) - every command the
  tools wrap, generated from the app itself
- [You are in control](/docs/explanation/youre-in-control/) -
  approval modes, pauses, and every safety control in one place
- [blowhorn-axi](/docs/reference/cli/blowhorn-axi/) - the agent
  CLI: the same commands through a command line instead of MCP
