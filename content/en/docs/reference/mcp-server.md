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
  `analytics activity`, `analytics activities`, `diagnostics reports`,
  and `report`.
- **Meta** - the computer itself: `setup`, `upgrade`, and
  `uninstall`.

A tool's name is its command's operation id, so the
[CLI reference](/docs/reference/cli/) documents exactly what each tool does: find
the command there for its flags, its examples, and its exit codes.

## Starting it

The server runs over stdio. The `blowhorn-mcp` command starts it with
everything it needs, so a client entry is that one command:

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

The Blowhorn app writes the command to `~/.local/bin` (version 1.61.0
or later; see [The blowhorn-mcp command](#the-blowhorn-mcp-command)),
and so does a checkout install (`tools/install.sh`). Any arguments after
the command go to the server unchanged, so
`~/.local/bin/blowhorn-mcp --list-tools` works too. The npm package
`blowhorn-mcp`, run as `npx -y blowhorn-mcp`, is coming soon and not
published yet.

Without the command, run the server from a checkout, with the
checkout's Python environment:

```bash
PYTHONPATH=engine ./venv/bin/python -m blowhorn.mcp_server
```

As a client entry, with the paths filled in for your checkout:

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

The `-P` keeps the client's working directory off Python's import
path, so a file there can never stand in for one of the server's own
modules.

The server reads the bundle from `--schema`, then `BLOWHORN_MCP_OPENAPI`,
then `schemas/dist/openapi.yaml` under the root it runs from (the
directory that holds `engine/`). It runs the first `blowhorn`
executable it finds in this order: `--cli`, then `BLOWHORN_MCP_CLI`,
then `blowhorn` on your PATH, then `tools/bin/blowhorn.sh` under the
same root. It prints nothing but protocol frames to stdout;
diagnostics go to stderr, and tool arguments are never logged,
because an argument can itself be a secret.

### From the installed app

The app carries everything the server needs inside
`Blowhorn.app/Contents/Resources/engine`: its own Python
(`bin/python`), the engine with the server (`engine/blowhorn/`,
`mcp_server` included), and the command bundle
(`schemas/dist/openapi.yaml`). Each time it opens, the app also writes
its commands (`blowhorn`, `blowhorn-axi` and `blowhorn-mcp`) to
`~/.local/bin`, but only where the path is free or already holds the
app's own command, which contains the line
`Managed by Blowhorn installer`. Any other file at that path is left
alone, and `BLOWHORN_MCP_CLI` must then name the `blowhorn` executable
you want instead. The app runs on macOS.

#### The `blowhorn-mcp` command

Blowhorn 1.61.0 and later write `~/.local/bin/blowhorn-mcp` beside the
other two commands. It is the whole configuration: the command
`/Users/<you>/.local/bin/blowhorn-mcp`, with no arguments and no
environment. Write the full path: a client started from the Dock or
Finder does not have `~/.local/bin` on its PATH. The one exception:
when `~/.local/bin/blowhorn` is not the app's (it lacks the line
`Managed by Blowhorn installer`), the entry still needs
`BLOWHORN_MCP_CLI` in its `env`, naming the `blowhorn` executable to
use; `blowhorn-mcp` keeps a value the client sets.

It finds the app again if the app moves, the way `blowhorn` does,
sets `PYTHONPATH` itself, and sets `BLOWHORN_MCP_CLI` to the
`blowhorn` command beside it unless the client already set one. It
prints nothing to stdout before the server starts. With the app in the
Trash, or no app found at all, it starts nothing: it prints one line
to stderr and exits 1, and it never runs the uninstall or the cleanup
that the `blowhorn` command runs in those cases. A checkout install
(`tools/install.sh`) also writes `~/.local/bin/blowhorn-mcp`, which runs
the checkout's venv the way the command above does and sets
`BLOWHORN_MCP_CLI` to the `blowhorn` launcher beside it unless the
client already set one.

#### The app's own Python

An app older than 1.61.0 has no `blowhorn-mcp` command. Point the
client at the app's interpreter instead. With the app in
`/Applications`, and your home directory filled in:

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

`BLOWHORN_MCP_CLI` names the app's `blowhorn` command outright,
because an MCP client may start the server without `~/.local/bin` on
its PATH. Without it, a client started from the Dock or Finder lists
the tools, but every call fails with
`blowhorn executable not found: blowhorn`. Without `PYTHONPATH`, the
server does not start and stderr says `No module named 'blowhorn'`.

| Fact | With the app |
|---|---|
| Client command | `/Users/<you>/.local/bin/blowhorn-mcp` (1.61.0 or later) |
| Interpreter | `/Applications/Blowhorn.app/Contents/Resources/engine/bin/python` |
| `PYTHONPATH` | `/Applications/Blowhorn.app/Contents/Resources/engine/engine` |
| `blowhorn` command | `~/.local/bin/blowhorn`, rewritten by the app each time it opens |
| Config file the tools read | `~/Library/Application Support/Blowhorn/home/.blowhorn.yaml`, the app's own home, not a `.blowhorn.yaml` in the client's working directory |
| Tool list | Follows the app's version; updating the app updates the tools |
| A moved app | The `~/.local/bin` commands find the app again on their own. An entry that names the interpreter has the two `/Applications/...` paths written into it, so an app moved elsewhere, `~/Applications` for one, needs both changed. |

The `blowhorn` command runs through the app's engine record, the same
way the app and the background service do, which is why its config is
the app's home rather than the client's directory.

## Options and environment

| Flag | Environment | What it does |
|---|---|---|
| `--schema PATH` | `BLOWHORN_MCP_OPENAPI` | The OpenAPI bundle to load. |
| `--cli PATH` | `BLOWHORN_MCP_CLI` | The `blowhorn` executable each tool call runs. |
| `--timeout SECONDS` | `BLOWHORN_MCP_TIMEOUT` | How long one tool call may run. Default 600. |
| `--transport stdio` | | The only transport served. `http` refuses at startup. |
| `--list-tools` | | Print the tool list as JSON and exit. |
| `--check-coverage` | | Check the tool list covers the bundle and exit. |
| `--version` | | Print the Blowhorn version and exit. |

The flag wins over its environment variable.

## What a tool call does

A tool call runs the matching `blowhorn` command as a subprocess, with
the tool arguments mapped to its flags and positional arguments, and
returns what the command printed. Commands that support `--json` run
with it, so the result is structured JSON; the rest return their text.
Credentials come the way the CLI takes them, from your existing
Blowhorn config and environment. The stdio transport does not use
OAuth: that belongs to a remote server, not to a process on your own
computer.

`chrome_confirm`, `profile_create` and `profile_update` also take a
`stdin_document` argument: the JSON document the command reads on
stdin. Passing it adds the command's `--payload-stdin` flag. Every
other call runs with stdin closed.

## Safety: dry run first, confirm to act

A tool that only reads runs as asked. A tool that changes anything
runs with `--dry-run` unless the call passes `confirm` as true. With
`confirm` true it performs the real run, and where the command has its
own confirm flag (the Slack send, edit, delete and react commands) it
passes that through too, so the two gates agree. A changing command
with no dry-run path refuses without `confirm` rather than running
for real, and a call that passes both `confirm` and `dry_run` is
refused as contradictory.

Which tools read, which change something, and which may destroy or
overwrite state is recorded in the schema bundle as `x-mcp` on each
operation: `expose`, `readOnly` and `destructive` (shape
`McpOperation`, authored in `schemas/data/mcp-operations.json`). A
tool's annotations follow from it: `readOnlyHint` and `idempotentHint`
are true for a read-only tool, `openWorldHint` is true for a changing
one, and `destructiveHint` is true for a changing tool marked
destructive. An operation with `expose` false is not served at all.
The server refuses to start on a bundle in which any operation has no
`x-mcp`, and names that operation: classify it in
`schemas/data/mcp-operations.json` and rebuild the bundle with
`make schemas-bundle`.

The server also marks its calls as agent calls, so a configured
approval mode sees them for what they are: it sets
`BLOWHORN_ACTOR=agent` for the command it runs, unless you already set
that variable. Under approval mode `agent` or `all`, the queue rules
in [You are in control](/docs/explanation/youre-in-control/) therefore
apply to MCP calls exactly as they apply to any other agent caller.
`content_approve` is a tool like any other, but `content approve`
refuses an agent caller in every approval mode, so a call marked
`agent` cannot approve queued work. Under `off` that refusal protects
little: an agent's content writes keep the `Approved?` value it
sets, and confirmed ad-hoc actions publish, so nothing waits for a
person.

> **Warning:** Do not set `BLOWHORN_ACTOR=human` in an MCP client's
> `env`. The server only sets `BLOWHORN_ACTOR=agent` when the variable
> is unset. If the server's environment sets `BLOWHORN_ACTOR=human`
> and does not set `BLOWHORN_RUN_SOURCE=scheduler`, every MCP call
> counts as a person, so:
>
> - Under approval mode `agent`, content writes keep the `Approved?`
>   value the agent sets and confirmed ad-hoc actions publish.
> - Under `all`, every content write still lands pending and no
>   ad-hoc action publishes.
> - In every mode, `content_approve` lets the agent approve its own
>   work.
>
> With `BLOWHORN_RUN_SOURCE=scheduler`, the calls still count as an
> agent and nothing above changes.

Note the limit of this transport: there is no desktop-app approval
step here. On this server, `confirm` true is the approval. If you want
a person to approve each write in the app, use the queue and the
approval mode, not a confirmed MCP call.

Tool results never carry secrets. Values under secret-named keys are
replaced before the result reaches the client, and secret-shaped
fragments in text output are replaced the same way. A failed run
reports its exit code and its (redacted) error, never the argv it ran.

## Protocol details

| Item | Behavior |
|---|---|
| Methods | `initialize`, `ping`, `tools/list` and `tools/call`. Notifications get no reply. Any other method, `resources/*` and `prompts/*` included, answers `-32601` (method not found). |
| Batches | A JSON-RPC batch (an array) is refused with `-32600` (invalid request). |
| Protocol versions | `2024-11-05`, `2025-03-26`, `2025-06-18` and `2025-11-25`. A client asking for one of these gets it; any other request gets `2025-11-25`. |
| Server info | Name `blowhorn-mcp`; version is the Blowhorn release, or `0.0.0` when it cannot be read. |
| Annotations | Each tool's four hints come from its operation's `x-mcp` in the bundle, never from a list in the server. A tool whose `x-mcp` says `readOnly`: `readOnlyHint` and `idempotentHint` true, `destructiveHint` and `openWorldHint` false. Any other tool: `readOnlyHint` and `idempotentHint` false, `openWorldHint` true, and `destructiveHint` true only when `x-mcp` also says `destructive`. An operation with `expose` false is no tool; one with no `x-mcp`, or one that does not match `McpOperation`, stops the server from starting. |
| Results | One text content item. Tools declare no `outputSchema` and return no `structuredContent`; a `--json` command's output is the JSON text. |
| Errors | A command that exits nonzero returns `isError` true with its exit code and its stderr (or stdout), redacted and cut to 4000 characters. A command that runs past the timeout returns `isError` true with a timed-out message only, no exit code or output. An unknown tool name also returns `isError` true, not a protocol error. |

## What it does not do

It serves stdio only. It does not serve Streamable HTTP, OAuth, or
per-organization scoping. Those belong to the hosted Blowhorn MCP
server, which is coming. Asking this server for HTTP refuses at
startup:

```bash
~/.local/bin/blowhorn-mcp --transport http
```

## Checking it

```bash
make mcp-generate   # verify the tool list covers the bundle
make mcp-test       # run the server's tests
```

Those targets need a checkout. With the app, run
`~/.local/bin/blowhorn-mcp --version` and
`~/.local/bin/blowhorn-mcp --list-tools`.

`--list-tools` prints the tool list as JSON and `--check-coverage`
runs the same coverage check on its own, both without serving. A tool
call may run at most 600 seconds by default
(`BLOWHORN_MCP_TIMEOUT`, or `--timeout`, changes that); see
[Options and environment](#options-and-environment).

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
