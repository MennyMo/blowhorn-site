---
title: "MCP server"
description: "The local MCP server: one tool per CLI command, over stdio, with dry run as the default for anything that changes state."
weight: 225
---

Blowhorn ships a local MCP server so an AI agent can drive the same
commands you run, through the Model Context Protocol, instead of
learning a second surface. It is generated, not hand-written: at
startup it reads `schemas/dist/openapi.yaml` and builds one tool per
operation in that bundle, named by the operation id
(`post`, `schedule_trigger_now`, `profile_list`, and so on). A command
added to the CLI appears as a tool the next time the server starts,
and `make mcp-generate` fails if the tool list ever stops matching the
bundle. The tool inputs are the command's flags and arguments, taken
from the same schemas the CLI reference is built from.

## How it relates to the CLI and to blowhorn-axi

There are two agent doors into the same commands, and they differ in
how the agent talks, not in what it can do. The MCP server is the
standard plug: any MCP client can discover one tool per command and
call it over the protocol. [blowhorn-axi](/docs/reference/cli/blowhorn-axi/) is the
agent command line: an agent runs it directly and reads compact,
agent-shaped answers, with every write a dry run until `--confirm`.
Both drive the same `blowhorn` commands, both rehearse before they
act, and both run on your own computer. If your assistant speaks MCP,
connect it here; if it runs shell commands, give it `blowhorn-axi`
or the CLI itself. The steps for connecting a client are in
[Connect an AI assistant over MCP](/docs/how-to/set-up/connect-mcp-client/).

## Tour of the tools

The tools are grouped the way the command bundle groups them, and a
group's tools cover the commands in it, no more and no less:

- **Act** - the outward actions: `post`, `comment`, `follow`,
  `unfollow`, `accept`, `withdraw`, `find`, and `source`, plus the
  connection, invitation, and reconciliation actions.
- **Manage** - profiles, content, schedules, risk, and config:
  `profile list`, `profile status`, `content list`, `content upsert`,
  `schedule list`, `schedule trigger-now`, `risk show`, and
  `config show`, among others.
- **Connect** - the sign-ins and the browser: `auth status`,
  `chrome profiles`, `chrome map`, `slack send`, and `slack whoami`,
  among others.
- **Run** - the service, the desktop app, and the store:
  `service status`, `service tick-now`, `desktop status`, and
  `store`.
- **Observe** - what happened: `analytics history`,
  `analytics activity`, `diagnostics reports`, and `report`.
- **Meta** - the computer itself: `setup`, `upgrade`, and
  `uninstall`.

A tool's name is its command's operation id, so the
[CLI reference](/docs/reference/cli/) documents exactly what each tool does: find
the command there for its flags, its examples, and its exit codes.

## Starting it

The server runs over stdio, from the checkout, with the checkout's
Python environment:

```bash
PYTHONPATH=engine ./venv/bin/python -m blowhorn.mcp_server
```

Point an MCP client at that command. A client configuration looks like
this, with the paths filled in for your checkout:

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

The server reads the bundle from `schemas/dist/openapi.yaml` in the
same checkout, unless `--schema` names another bundle, and it runs the
`blowhorn` executable from your PATH, unless `--cli` names one
(`BLOWHORN_MCP_CLI` does the same from the environment). It prints
nothing but protocol frames to stdout; diagnostics go to stderr, and
tool arguments are never logged, because an argument can itself be a
secret.

## What a tool call does

A tool call runs the matching `blowhorn` command as a subprocess, with
the tool arguments mapped to its flags and positional arguments, and
returns what the command printed. Commands that support `--json` run
with it, so the result is structured JSON; the rest return their text.
Credentials come the way the CLI takes them, from your existing
Blowhorn config and environment. The stdio transport does not use
OAuth: that belongs to a remote server, not to a process on your own
computer.

## Safety: dry run first, confirm to act

A tool that only reads runs as asked. A tool that changes anything
runs with `--dry-run` unless the call passes `confirm` as true. With
`confirm` true it performs the real run, and where the command has its
own confirm flag (the Slack send, edit, delete and react commands) it
passes that through too, so the two gates agree. A changing command
with no dry-run path refuses without `confirm` rather than running
for real, and a call that passes both `confirm` and `dry_run` is
refused as contradictory.

The server also marks its calls as agent calls, so a configured
approval mode sees them for what they are: it sets
`BLOWHORN_ACTOR=agent` for the command it runs, unless you already set
that variable. Under approval mode `agent` or `all`, the queue rules
in [You are in control](/docs/explanation/youre-in-control/) therefore
apply to MCP calls exactly as they apply to any other agent caller.
Note the limit of this transport: there is no desktop-app approval
step here. On this server, `confirm` true is the approval. If you want
a person to approve each write in the app, use the queue and the
approval mode, not a confirmed MCP call.

Tool results never carry secrets. Values under secret-named keys are
replaced before the result reaches the client, and secret-shaped
fragments in text output are replaced the same way. A failed run
reports its exit code and its (redacted) error, never the argv it ran.

## What it does not do

It serves stdio only. It does not serve Streamable HTTP, OAuth, or
per-organization scoping: the remote, hosted server is a separate
piece of work and owns that transport, so there is exactly one remote
server. Asking this server for HTTP refuses at startup:

```bash
PYTHONPATH=engine ./venv/bin/python -m blowhorn.mcp_server --transport http
```

## Checking it

```bash
make mcp-generate   # verify the tool list covers the bundle
make mcp-test       # run the server's tests
```

`--list-tools` prints the tool list as JSON and `--check-coverage`
runs the same coverage check on its own, both without serving. A tool
call may run at most 600 seconds by default
(`BLOWHORN_MCP_TIMEOUT`, or `--timeout`, changes that).

## Catalog listings

The server is not listed in the official MCP Registry or other catalogs
yet. The listing input, `server.json` at the repository root, names the
server for the registry and pins its version to the Blowhorn release;
publication waits on the catalog description's approval and on the
server being packaged for distribution.

See also the [CLI reference](/docs/reference/cli/) for the commands themselves,
[Connect an AI assistant over MCP](/docs/how-to/set-up/connect-mcp-client/)
for the client-by-client setup steps, and
[Settings and configuration](/docs/reference/configuration/) for the config and
environment the server's subprocesses inherit.
