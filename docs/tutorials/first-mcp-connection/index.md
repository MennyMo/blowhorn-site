# Connect an assistant and read your queue


> Add Blowhorn's hosted MCP server to Claude Desktop and ask it to read your content items.


In this tutorial you connect Claude Desktop to Blowhorn's hosted MCP
server. You ask it which tools it has, then you ask it to read your
content items. Nothing is posted or changed. It takes a few minutes.

## Before you start

You need:

- A Blowhorn account.
- Claude Desktop, installed and signed in.
- A Blowhorn API token, if Claude Desktop does not finish the OAuth
  sign-in. The steps are in [Get a Blowhorn API
  token](/docs/how-to/set-up/connect-mcp-client/#get-a-blowhorn-api-token).

## 1. Add the hosted server {#section-1-add-the-hosted-server}

1. In Claude Desktop, open **Settings**, then **Developer**, then
   **Edit Config**.
2. Add this entry to `claude_desktop_config.json`. If Claude Desktop
   completes OAuth for the URL, omit the `headers` object. Otherwise
   replace `<token>` with your Blowhorn API token.

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

3. Save the file and restart Claude Desktop.

The other clients, and what to do when sign-in fails, are in
[Connect an AI assistant over
MCP](/docs/how-to/set-up/connect-mcp-client/).

## 2. Ask which tools it has {#section-2-ask-which-tools-it-has}

In a new chat, ask:

> Which Blowhorn tools do you have?

You should see six: `listContentItems`, `getContentItem`,
`getEvents`, `getConnections`, `listSchedules`, `getScheduleById` and
`getPlatformSessions`.
If the list is empty, or the client says it cannot connect, check the
URL and the token, then restart Claude Desktop. A `401` means the
header is missing, the token is no longer valid, or you need to sign
in again.

## 3. Read your content {#section-3-read-your-content}

Ask:

> List my content items and tell me the status of each one you can see.

The assistant calls `listContentItems` and answers from that result.
It cannot post, schedule, or edit. If you ask it to publish something,
it should tell you this server has no write tool.

## Related

- [Connect an AI assistant over MCP](/docs/how-to/set-up/connect-mcp-client/) -
  the same hosted URL in every other client
- [MCP server reference](/docs/reference/mcp-server/) - what the hosted
  server serves

