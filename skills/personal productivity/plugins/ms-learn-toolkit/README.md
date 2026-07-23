# MS Learn Toolkit

A M365 Copilot Cowork plugin bundle that grounds Microsoft / Azure / M365 answers in
**official Microsoft Learn documentation** via the Microsoft Learn MCP Server.

Publisher: **TW MS Dennis**

## What's inside

| File / folder | Purpose |
| --- | --- |
| `manifest.json` | Cowork plugin manifest (schema **devPreview**): registers the `ms-learn-docs` skill **and** declares the Microsoft Learn MCP server as an `agentConnectors` entry. |
| `skills/ms-learn-docs/` | The skill: search → fetch → code-sample workflow + grounding rules. |
| `color.png` / `outline.png` | Plugin icons (add before packaging). |

## How the MCP server is wired

Cowork declares MCP servers **natively in `manifest.json`** via `agentConnectors` — no
separate `mcp.json` is needed. Cowork performs dynamic tool discovery at runtime
(`initialize` + `tools/list`), so the manifest doesn't list individual tools.

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

- **Endpoint:** `https://learn.microsoft.com/api/mcp`
- **Transport:** streamable HTTP (HTTPS, TLS 1.2+)
- **Auth:** `None` (public, unauthenticated — so no `referenceId` is set)
- **Discovered tools:** `microsoft_docs_search`, `microsoft_docs_fetch`, `microsoft_code_sample_search`

For non-Cowork hosts (VS Code / Copilot / Foundry / Copilot Studio), the same endpoint
can be registered directly — see
[`skills/ms-learn-docs/references/reference.md`](skills/ms-learn-docs/references/reference.md).

## Packaging

Zip the manifest, icons, and `skills/` folder at the **root level** (not inside a
parent folder), then sideload into Copilot Cowork or upload via the M365 admin center:

```powershell
Compress-Archive -Path manifest.json, color.png, outline.png, skills -DestinationPath dist/ms-learn-toolkit-1.0.0.zip
```

Validation notes (Cowork):
- The skill folder name (`ms-learn-docs`) must equal the `name` in its `SKILL.md`.
- `mcpServerUrl` must be a valid HTTPS URL.
- With `authorization.type = "None"`, do **not** include a `referenceId`.

> Icons are not included yet — drop in `color.png` (192×192) and `outline.png` (32×32,
> transparent) before zipping, or reuse a placeholder from another toolkit.
