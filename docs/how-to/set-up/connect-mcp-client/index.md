# Connect an AI assistant over MCP


> Point Claude, ChatGPT, Codex, Cursor, VS Code, Windsurf, Gemini CLI, Zed, Cline, Goose, Muse, Grok, Grok Bot, or Arcade at https://mcp.blowhorn.ai/mcp.


Connect an MCP client to Blowhorn's hosted MCP server at
`https://mcp.blowhorn.ai/mcp`. The server is Streamable HTTP. It serves
seven read-only tools: `listContentItems`, `getContentItem`, `getEvents`,
`getConnections`, `listSchedules`, `getScheduleById` and
`getPlatformSessions`. It does not
post, schedule, or change anything, and it serves tools only: no
prompts, resources, or sampling. Where a tool needs an organization,
pass it as the `organizationId` argument.

Sign in with OAuth when the client can. A client that supports MCP
OAuth 2.1 needs only the URL. Dynamic client registration and PKCE are
on. The resource is `https://mcp.blowhorn.ai/mcp`. The authorization
server is the one advertised in
`https://mcp.blowhorn.ai/.well-known/oauth-protected-resource`. A
client that cannot finish that sign-in sends a Blowhorn API token as
`Authorization: Bearer <token>`. Create the token in
[Get a Blowhorn API token](#get-a-blowhorn-api-token). Put no other
secret in a client config.

What the hosted server is, and how it relates to the desktop app's own
process, is in the [MCP server reference](/docs/reference/mcp-server/).
New to this? Follow [Connect an assistant and read your
queue](/docs/tutorials/first-mcp-connection/) first.

## The server URL

Every client uses the same URL.

```json
{
  "mcpServers": {
    "blowhorn": {
      "type": "http",
      "url": "https://mcp.blowhorn.ai/mcp"
    }
  }
}
```

When the client cannot finish OAuth, add the token header:

```json
{
  "mcpServers": {
    "blowhorn": {
      "type": "http",
      "url": "https://mcp.blowhorn.ai/mcp",
      "headers": {
        "Authorization": "Bearer <token>"
      }
    }
  }
}
```

Replace `<token>` with the token from
[Get a Blowhorn API token](#get-a-blowhorn-api-token). Restart the
client after you save the config. Most clients only pick up a new
server on restart.

## Connect your client

### Claude Desktop

Open **Settings**, then **Developer**, then **Edit Config**, and add the
entry above to `claude_desktop_config.json`. Save and restart Claude
Desktop. If it offers an OAuth sign-in for this URL, use that and omit
the header.

### Claude Code

```bash
claude mcp add --transport http blowhorn https://mcp.blowhorn.ai/mcp
```

If sign-in does not complete, add the header:

```bash
claude mcp add --transport http blowhorn https://mcp.blowhorn.ai/mcp \
  --header "Authorization: Bearer <token>"
```

Check it with `claude mcp list`.

### ChatGPT

ChatGPT on the web connects only to remote servers. Add a custom
connector with the URL `https://mcp.blowhorn.ai/mcp`. Sign in with
OAuth if ChatGPT offers it. Otherwise send the Bearer token where it
asks for an authorization header.

### OpenAI Codex CLI

```bash
codex mcp add blowhorn --url https://mcp.blowhorn.ai/mcp
```

If the CLI asks for a bearer token, give it the Blowhorn API token.

### Cursor

In **Settings**, then **MCP**, add a server with the URL
`https://mcp.blowhorn.ai/mcp`. Or write `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "blowhorn": {
      "url": "https://mcp.blowhorn.ai/mcp"
    }
  }
}
```

Add the `headers` object from above when Cursor does not complete
OAuth sign-in.

### VS Code with GitHub Copilot

In `.vscode/mcp.json`:

```json
{
  "servers": {
    "blowhorn": {
      "type": "http",
      "url": "https://mcp.blowhorn.ai/mcp"
    }
  }
}
```

Add `"headers": { "Authorization": "Bearer <token>" }` when sign-in
does not complete.

### Windsurf (Devin Desktop)

Add an MCP server with the URL `https://mcp.blowhorn.ai/mcp`. Use the
same JSON entry as [The server URL](#the-server-url), including the
Bearer header when Windsurf does not finish OAuth.

### Gemini CLI

```bash
gemini mcp add --transport http blowhorn https://mcp.blowhorn.ai/mcp
```

If it cannot finish OAuth, pass the Bearer header the same way Claude
Code does.

### Zed

In Zed's settings, add an MCP server whose URL is
`https://mcp.blowhorn.ai/mcp`. Add the Bearer header when Zed does not
finish OAuth.

### Cline

In Cline's MCP settings, set the server URL to
`https://mcp.blowhorn.ai/mcp`. Add the Bearer header when Cline does
not finish OAuth.

### Goose

Add an extension of type **streamable HTTP** with the URI
`https://mcp.blowhorn.ai/mcp`. Add the Bearer header when Goose does
not finish OAuth.

### Muse

A Muse bot connects as a custom MCP connector. Set the server URL to
`https://mcp.blowhorn.ai/mcp` and send the Blowhorn API token as a
Bearer token.

### Grok

Grok Build connects over HTTP. If it completes the OAuth sign-in from
the URL alone, add the server with no header:

```bash
grok mcp add --transport http blowhorn https://mcp.blowhorn.ai/mcp
```

If it cannot finish OAuth, pass a Blowhorn API token instead:

```bash
grok mcp add --transport http blowhorn https://mcp.blowhorn.ai/mcp \
  --header "Authorization: Bearer <token>"
```

Check it with `grok mcp list`.
[Vendor docs](https://docs.x.ai/build/features/mcp-servers).

Grok on the web can use the same URL as a custom connector and
complete the Blowhorn OAuth sign-in. If it cannot finish OAuth, send a
Blowhorn API token as a Bearer token instead.
[Vendor docs](https://docs.x.ai/grok/connectors).

### Grok Bot

Blowhorn is not in Grok Bot's connector catalog yet. Add it as a
custom MCP server. Grok Bot runs in the cloud, so it cannot start
Blowhorn's local server on your Mac. It connects to the hosted server
at `https://mcp.blowhorn.ai/mcp`. No token or header is needed for the
add step: you sign in with OAuth.

The hosted server is read-only. It has the seven tools named at the top
of this page, so your bot can read your queue, a post, your activity,
your connections, where your social accounts are signed in and your
schedules. It cannot post, schedule or
change anything. To post, use the [CLI](/docs/how-to/publish/post-content/) or
[blowhorn-axi](/docs/reference/cli/blowhorn-axi/) on the Mac where
Blowhorn runs, or the desktop app's own process described in the
[MCP server reference](/docs/reference/mcp-server/).

1. In a chat with your bot, ask it to add a custom MCP server. Say
   "custom" so the bot does not look in the catalog:

   > Add a custom MCP server named blowhorn at
   > https://mcp.blowhorn.ai/mcp.

2. The bot shows the name and the URL and asks you to confirm. Check
   that the URL is exactly `https://mcp.blowhorn.ai/mcp`, then confirm.
3. The bot shows a connect card. Open it. You land on the Blowhorn
   sign-in page at [cloud.blowhorn.ai](https://cloud.blowhorn.ai). Sign
   in, or create a new Blowhorn account there. Approve access.
4. Back in the chat, check it in your next message. Ask:

   > Which Blowhorn tools do you have? Then list my Blowhorn
   > connections.

   The bot should list the seven read-only tools above and answer from
   `getConnections`. Where a tool needs an organization, it is passed
   as the `organizationId` argument.

If a client cannot finish OAuth, send a Blowhorn API token as
`Authorization: Bearer <token>` instead. The steps are in
[Get a Blowhorn API token](#get-a-blowhorn-api-token).

If the bot reports `401 Unauthorized` when it connects, the OAuth
sign-in did not finish, or a Bearer header is missing or malformed.
Sign in again, or use the header `Authorization: Bearer <token>` with
a current token. If it connects but a tool call fails with a `401`,
the sign-in expired or the token was revoked: sign in again, or get a
new token and update the header. If you connected before 20 November
2026, sign in once more: the sign-in address changed, so the client
registers again and completes sign-in once. If you opened the URL in a
browser and saw a JSON error, that is expected: see
[Opening the gateway URL in a browser](#opening-the-gateway-url-in-a-browser).

### Arcade

Arcade connects to the hosted server. Do not create a new Arcade
server or deploy one. Register the existing hosted server as a Remote
MCP.

1. Open the [Arcade servers dashboard](https://app.arcade.dev/servers).
2. Choose **Add Server**, then **Remote MCP**.
3. Set the ID to `blowhorn` and the URI to `https://mcp.blowhorn.ai/mcp`.
4. Under **Advanced settings**, choose **OAuth2 authorization**. Leave
   Client ID, Client Secret, Authorization URL, and Token URL empty so
   Arcade can use dynamic client registration. That is the same pattern
   as Arcade's Atlassian remote MCP guide.
5. Save, then complete the Blowhorn OAuth sign-in.
6. Pick the tools in an MCP Gateway.

The tools are the seven read-only tools named at the top of this page.
This is a connection in your Arcade account. Blowhorn is not listed in
Arcade's public catalog.

[Arcade Remote MCP docs](https://docs.arcade.dev/en/operate/governance/remote-mcp-servers).

## Authentication

### Get a Blowhorn API token

Use this when the client cannot finish OAuth. The Blowhorn desktop app
has no screen for creating a token. Create it on your Blowhorn
account's web page:

1. Open [cloud.blowhorn.ai/security/tokens](https://cloud.blowhorn.ai/security/tokens)
   and sign in with your Blowhorn account. This is the **Tokens** tab
   under **Security**.
2. Click **Create**.
3. Enter a **Token Name** that says where the token is used, such as
   `grok-bot-mcp`, and a **Token Purpose**, then click **Create**. The
   new token appears in the list.
4. In that token's row, click the **Download** icon. The download saves
   a file named `token_<id>.json`.
5. Open the file. The value of its `"token"` field is the API token.
   Give a client that value, and nothing else, where it asks for the
   Bearer token; the client sends it as `Authorization: Bearer <token>`.

Make one token per client, so you can revoke one without breaking the
others, and delete the downloaded file once the token is in the
client. To stop using a token, delete it from the same page with the
**Delete** icon in its row, or see
[Revoke a leaked token](#revoke-a-leaked-token).

### Opening the gateway URL in a browser

`https://mcp.blowhorn.ai/mcp` is an endpoint for MCP clients, not a web
page. A client sends each request as a JSON-RPC `POST`. A browser
sends a plain `GET` without a token, so it gets a short JSON error
instead of a page, such as:

```json
{"error":"unauthorized","error_description":"Bearer token required. Discover the authorization server via the resource_metadata URL in WWW-Authenticate."}
```

or:

```json
{"jsonrpc":"2.0","error":{"code":-32000,"message":"Method not allowed: this stateless gateway answers POST only."},"id":null}
```

That is the server working as designed, not a fault. It keeps no
session between requests, so it answers MCP messages sent as `POST`
only. To check from a browser that the server is up, open
[mcp.blowhorn.ai/healthz](https://mcp.blowhorn.ai/healthz) instead,
which answers `{"ok":true,...}`. To check your token, connect a
client and ask it which Blowhorn tools it has.

### Revoke a leaked token

If an API token for your Blowhorn account leaks, revoke it at once.
Having the token is enough; no sign-in is needed:

```bash
read -rs TOKEN   # paste the token, then press Enter
printf '{"token": "%s"}' "$TOKEN" | curl -sS -X POST https://cloud.blowhorn.ai/revoke \
  -H 'Content-Type: application/json' --data-binary @- -w 'HTTP %{http_code}\n'
```

A 200 response means the token no longer works, if it existed. A 200
does not confirm the token existed. A 503 response means nothing was
revoked, so run the call again.

While you are still signed in with a token you trust, you can delete
the token by ID instead. List your tokens with
`GET https://cloud.blowhorn.ai/api/identity/tokens`, then send
`DELETE https://cloud.blowhorn.ai/api/identity/tokens?tokenId=<id>`
with `Authorization: Bearer <token>`.

## Example prompts

The server can read. Ask for a read, and read the result before you
ask for another:

> List my content items.

> Show me one content item and tell me its status.

> What events do you see, and which connections are set up?

A request to post, schedule, or change anything has no tool on this
server. The assistant should say so.

## Troubleshooting

- **The client shows no Blowhorn server.** The URL must be exactly
  `https://mcp.blowhorn.ai/mcp`. Restart the client after saving the
  config. Claude Desktop only reads its config at startup.
- **The client reports 401.** The OAuth sign-in did not finish, or the
  Bearer header is missing or malformed. Use the header
  `Authorization: Bearer <token>` with a current token, or sign in
  again. If you connected before 20 November 2026, sign in once more:
  the sign-in address changed, so the client registers again and
  completes sign-in once.
- **A tool call returns 401 after the client connected.** The sign-in
  expired, or the token was revoked. Sign in again, or create a new
  token and update the header.
- **The tool list is not the seven read tools.** The client is pointed
  at a different server. Set the URL to `https://mcp.blowhorn.ai/mcp`
  and remove any command that starts a local process.
- **A browser shows a JSON error at `/mcp`.** That is expected. See
  [Opening the gateway URL in a browser](#opening-the-gateway-url-in-a-browser).

## Related

- [MCP server reference](/docs/reference/mcp-server/) - the hosted
  server and the desktop app's own process
- [How the MCP server keeps you in control](/docs/explanation/mcp-and-safety/) -
  how the server, the CLI and approvals fit together
- [You are in control](/docs/explanation/youre-in-control/) -
  approval modes, pauses, and every safety control in one place
- [blowhorn-axi](/docs/reference/cli/blowhorn-axi/) - the agent
  CLI, for an assistant that runs shell commands instead of MCP

