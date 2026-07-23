# Cowork Plugin — Manifest Cheatsheet & Gotchas

Deep reference for the `cowork-plugin-builder` skill. Load when you need exact schema,
connector shape, auth details, limits, or the full validation-rule list.

Source: [Build plugins for Copilot Cowork](https://learn.microsoft.com/microsoft-365/copilot/cowork/cowork-plugin-development)
· [Manage plugins for Copilot Cowork](https://learn.microsoft.com/microsoft-365/copilot/cowork/cowork-manage-plugins)

## Package anatomy

```
my-plugin.zip                 # all entries at ROOT, forward-slash paths
├── manifest.json             # M365 unified app manifest
├── color.png                 # 192×192 full-color icon
├── outline.png               # 32×32 single-color icon, transparent bg
└── skills/
    └── <skill-name>/
        ├── SKILL.md
        ├── references/       # optional companion files (loaded on demand)
        └── scripts/          # optional executables (run, not loaded)
```

## Manifest schema version — IMPORTANT (doc drift, 2026-07-23)

- **Tested-working (2026-05-17 admin-center sideload):** `devPreview`
  ```json
  "$schema": "https://developer.microsoft.com/json-schemas/teams/vDevPreview/MicrosoftTeams.schema.json",
  "manifestVersion": "devPreview"
  ```
  Using a non-existent schema URL (e.g. `.../copilot/plugin/mos3/v1.0/...`) returns **500**.
- **Official docs now show** `v1.28` (`.../teams/v1.28/...`, `"manifestVersion": "1.28"`).
- **Rule of thumb:** ship `devPreview` until you personally re-test that the upload
  validator accepts `v1.28`. The platform may be migrating devPreview → 1.28.

## agentSkills

```json
"agentSkills": [ { "folder": "./skills/<skill-name>" } ]
```

- Use the `folder` key (not `path` — older docs used `path`; validator rejects it).
- Up to 20 entries. Each folder must contain a `SKILL.md`.
- `folder` path ≤ 256 chars. No duplicate `folder` values.

## agentConnectors (remote MCP server)

```json
"agentConnectors": [
  {
    "id": "my-mcp",
    "displayName": "My MCP",
    "description": "What this server exposes.",
    "toolSource": {
      "remoteMcpServer": {
        "mcpServerUrl": "https://example.com/api/mcp",
        "authorization": { "type": "None" }
      }
    }
  }
]
```

- `toolSource` takes **exactly one** of `remoteMcpServer` or `plugin` (legacy OpenAPI).
- The field is `displayName`, not `name`. `id` + `displayName` are required and `id`
  must be unique within the manifest.
- `mcpServerUrl` must be a valid **HTTPS** URL.
- Up to 10 connectors per package. A single skill may use tools from any/all of them.
- REST-only backends: wrap in an MCP server first (Node/Python/.NET → any HTTPS host).

### Connector technical requirements

| Requirement | Spec |
| --- | --- |
| Transport | Streamable HTTP (HTTPS, TLS 1.2+) |
| Messages | JSON-RPC 2.0 |
| Required RPC | `initialize`, `tools/list`, `tools/call`, `notifications/initialized` |
| Response time | < 30 s per tool call |
| Availability | 99.9% SLA (store-published) |

### Authorization types

| Type | When | Secret storage |
| --- | --- | --- |
| `None` | Public/anonymous or internal | — (no `referenceId`) |
| `OAuthPluginVault` | OAuth 2.0 (prod default) | Enterprise Token Store `referenceId` |
| `ApiKeyPluginVault` | API-key services | Enterprise Token Store `referenceId` |
| `DynamicClientRegistration` | RFC 7591 DCR — omit `authorization`; Cowork creates the OAuth client | — |

Rule: `referenceId` is **required** unless `type` is `None`, and must be **absent** when
`type` is `None`. Secrets never appear in the manifest or skill files.

## SKILL.md frontmatter — 5-field whitelist

| Field | Required | Notes |
| --- | --- | --- |
| `name` | ✅ | kebab-case, 1–64 chars, == folder name |
| `description` | ✅ | 1–1024 chars, list trigger phrases |
| `license` | — | e.g. MIT |
| `compatibility` | — | free text |
| `metadata` | — | free-form key/value (validator ignores contents) |

Fields some docs list as "optional" (`allowed-tools`, `cowork.category`, `cowork.icon`)
are **not** on the whitelist and will be rejected — put them under `metadata`.

kebab-case: lowercase alphanumerics + hyphens; no leading/trailing/consecutive hyphens.

## Limits

| Scope | Limit |
| --- | --- |
| Skills per package | 20 |
| Connectors per package | 10 |
| Companion files per skill | 20 |
| Companion file size | ≤ 5 MB each; ≤ 10 MB total/skill |
| Companion download timeout | 15 s |

## Validation rules (fix before upload)

Manifest: `ASKILL-M001` folder required · `ASKILL-M002` ≤ 20 skills · `ASKILL-M003`
folder ≤ 256 chars.
Package: `ASKILL-P001` folder exists in zip · `P002` folder has SKILL.md · `P003` valid
YAML frontmatter · `P004` has `name` · `P005` has `description` · `P006` name == folder
· `P007` name is kebab-case · `P008` no duplicate folders.
Connector: `id`+`displayName` required · unique `id` · exactly one of `plugin`/
`remoteMcpServer` · `mcpServerUrl` valid HTTPS · `referenceId` required unless
`type=None` (and absent when `None`).
Companion files: relative paths only · no `..` traversal · no backslashes/null bytes ·
no hidden (dot) files · no Windows reserved names (`CON`,`PRN`,`AUX`,`NUL`,`COM1-9`,`LPT1-9`).

## Top gotchas (learned the hard way)

1. **Backslash zip entries** — Windows `Compress-Archive` writes `skills\x\SKILL.md`;
   Cowork rejects backslashes. Build the zip with .NET `ZipArchive` (forward slashes) —
   see `scripts/package-plugin.ps1`.
2. **Folder ≠ name** — the single most common failure.
3. **Extra frontmatter fields** — anything outside the 5-field whitelist → reject.
4. **`path` vs `folder`** — use `folder`.
5. **Connector shape** — nest under `toolSource.remoteMcpServer`; use `displayName`.
6. **`None` + `referenceId`** — must not coexist.
7. **Files not at zip root** — everything sits at the top level, not inside a parent folder.
8. **Unstable GUID** — keep `id` constant across versions or it registers as a new app.

## Sideload

M365 Admin Center → Integrated apps → **Upload custom apps** → App type **Teams app**
→ choose the zip. On failure: F12 → Network → `uploadCustomApp` POST → **Response** →
read `errorMessage`. After success, wait 5–15 min for Copilot Control System sync, then
check **Copilot → Agents → Tools**.
