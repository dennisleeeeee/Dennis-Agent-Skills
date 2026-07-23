# MS Learn Docs — Reference

Deep detail for the `ms-learn-docs` skill. Load only when you need the endpoint,
client configuration, tool contracts, or troubleshooting. The common path only needs
`SKILL.md`.

## Microsoft Learn MCP Server

- **Endpoint:** `https://learn.microsoft.com/api/mcp`
- **Transport:** streamable HTTP
- **Authentication:** none (public, unauthenticated)
- **Licensing:** none — free to use, subject to the
  [Microsoft API Terms of Use](https://learn.microsoft.com/legal/microsoft-apis/terms-of-use)
- **Note:** the endpoint is for programmatic MCP clients only. Opening it in a browser
  returns `405 Method Not Allowed`. Don't call it as a plain REST API — the tool list,
  request, and response shapes can change; always go through an agent/MCP client.

Official docs:
- Overview — https://learn.microsoft.com/training/support/mcp
- Developer reference — https://learn.microsoft.com/training/support/mcp-developer-reference
- Best practices — https://learn.microsoft.com/training/support/mcp-best-practices
- Get started (VS Code) — https://learn.microsoft.com/training/support/mcp-get-started
- Get started (Foundry) — https://learn.microsoft.com/training/support/mcp-get-started-foundry
- Release notes — https://learn.microsoft.com/training/support/mcp-release-notes
- FAQ — https://learn.microsoft.com/training/support/mcp-faq

## Tools (from the server's tool list)

On every connection the client calls `tools/list`; the set below is current but may
evolve. Never hardcode request/response schemas — read them from the live tool list.

1. `microsoft_docs_search` — semantic search over official Microsoft Learn content.
   Returns up to 10 chunks (≤500 tokens each), each with article title + URL.
2. `microsoft_docs_fetch` — fetch and convert a full documentation page to markdown.
   Use after search when you need complete step-by-step / prerequisites / full code.
3. `microsoft_code_sample_search` — search official Learn code samples. Returns up to
   20 snippets. Optional `language` filter: `csharp javascript typescript python
   powershell azurecli al sql java kusto cpp go rust ruby php`.

Workflow rule of thumb: **Search gives breadth. Code Sample Search gives practical
examples. Fetch gives depth.**

## Client configuration

### M365 Copilot Cowork (native, in `manifest.json`)

Cowork declares MCP servers natively in the plugin manifest via `agentConnectors` —
no separate config file. Cowork discovers tools at runtime (`initialize` + `tools/list`).

```json
"agentConnectors": [
  {
    "id": "microsoft-learn-mcp",
    "displayName": "Microsoft Learn MCP",
    "description": "Official Microsoft Learn documentation search, article fetch, and code-sample lookup.",
    "toolSource": {
      "remoteMcpServer": {
        "mcpServerUrl": "https://learn.microsoft.com/api/mcp",
        "authorization": { "type": "None" }
      }
    }
  }
]
```

Auth types: `None` (anonymous), `OAuthPluginVault`, `ApiKeyPluginVault`. For `None`,
omit `referenceId`. Docs: https://learn.microsoft.com/microsoft-365/copilot/cowork/cowork-plugin-development

### VS Code / GitHub Copilot (`.vscode/mcp.json` or user `mcp.json`)

```json
{
  "servers": {
    "microsoft.docs.mcp": {
      "type": "http",
      "url": "https://learn.microsoft.com/api/mcp"
    }
  }
}
```

Generic IDE form (same server object):

```json
{
  "microsoft.docs.mcp": {
    "type": "http",
    "url": "https://learn.microsoft.com/api/mcp"
  }
}
```

### Microsoft Foundry agent

1. Build → Agents → Create agent → name it, pick a deployed model, add instructions.
2. Tools → Add → Custom → **MCP** → Create.
3. Name it, endpoint `https://learn.microsoft.com/api/mcp`, Authentication =
   **Unauthenticated** → Connect.
4. Ask a Learn-grounded question, allow the agent to use the MCP server, then **Save**.

### Copilot Studio agent

Tools → Add a tool → New tool → **Model Context Protocol** → fill Server name,
Server description, Server URL `https://learn.microsoft.com/api/mcp`, Authentication
**None** → Create → add to agent. Requires **generative orchestration** turned on.

### MCP Inspector (quick smoke test)

```
npx -y @modelcontextprotocol/inspector https://learn.microsoft.com/api/mcp
```

## Troubleshooting

- **405 in browser** — expected; the endpoint is MCP-only, not a webpage.
- **Tools not listed** — reconnect the server so the client re-runs `tools/list`.
- **Empty/irrelevant search** — refine the query with product + service + task keywords;
  refine once, not repeatedly.
- **Truncated chunk** — that's normal for search; `microsoft_docs_fetch` the page URL
  for the full content instead of re-searching.
- **Rate/terms** — usage is governed by the Microsoft API Terms of Use; don't scrape or
  hammer the endpoint.
