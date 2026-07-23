---
name: cowork-plugin-builder
description: |
  Scaffold, validate, and package a M365 Copilot Cowork plugin end-to-end into a
  sideload-ready .zip. Covers the whole process: pick a packaging pattern
  (skills-only / skills+connector / connector-only), write a valid SKILL.md
  (5-field frontmatter whitelist, folder name = name), build manifest.json
  (devPreview schema, agentSkills + agentConnectors with a remote MCP server),
  generate icons, and package with FORWARD-SLASH zip entries (Windows
  Compress-Archive produces backslashes that fail Cowork validation). Bakes in
  the known validation gotchas so the first sideload upload passes.
  Use when the user says "build a cowork plugin", "make a cowork plugin",
  "package a skill for cowork", "cowork plugin manifest", "sideload plugin",
  "打包 cowork plugin", "做一個 cowork 外掛", "把 skill 包成 plugin".
  Do NOT use for Copilot Studio agents, Teams tabs/bots, or API/OpenAPI plugins.
license: MIT
compatibility: Cowork (Frontier), Claude Code, VS Code / GitHub Copilot, Cursor
metadata:
  author: Dennis Li
  version: 1.0.0
  category: development
  icon: Wrench
---

# Cowork Plugin Builder

Turn one or more skills (and optional remote MCP servers) into a sideload-ready
M365 Copilot Cowork plugin `.zip`. A Cowork plugin is an M365 unified app package
(same family as Teams apps) containing `manifest.json` + icons + a `skills/` folder.

> Reusable assets in this skill:
> - `scripts/package-plugin.ps1` — builds the dist zip with **forward-slash** entries.
> - `scripts/new-icons.ps1` — generates placeholder `color.png` / `outline.png`.
> - `references/manifest-cheatsheet.md` — full manifest schema, connector shape,
>   auth types, and the complete validation-rule / gotcha list.

## Step 0 — Pick the packaging pattern

| Pattern | manifest holds | Use for |
| --- | --- | --- |
| Skills only | `agentSkills` | Prompt workflows, doc analysis, writing help |
| Skills + connector | `agentSkills` + `agentConnectors` | Skill that calls a remote MCP server's tools |
| Connector only | `agentConnectors` | Built-in skills already know how to use the data |

## Step 1 — Write each `SKILL.md`

Folder layout — **the folder name MUST equal the `name` field** (kebab-case). This
mismatch is the #1 cause of skill failures (validation `ASKILL-P006`).

```
skills/<skill-name>/
├── SKILL.md
├── references/   # optional companion docs (loaded on demand)
└── scripts/      # optional executables (run, not loaded into context)
```

Frontmatter is a **5-field whitelist** — anything else is rejected by the production
validator. Put custom keys under `metadata`.

```yaml
---
name: my-skill                 # required, kebab-case, == folder name
description: |                 # required, 1-1024 chars, list trigger phrases
  What it does + "Use when the user asks to ...".
license: MIT                   # optional
compatibility: Cowork (Frontier), Claude Code, VS Code Copilot   # optional
metadata:                      # optional free-form (validator ignores contents)
  author: Dennis Li
  version: 1.0.0
---
```

A vague `description` is why skills don't trigger — always list 5+ concrete trigger
phrases. Keep the body under ~2,000 words; push depth into `references/`.

## Step 2 — Build `manifest.json`

Create it at the package root. Use the **devPreview** schema (see the doc-drift note
in the cheatsheet before changing this).

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/teams/vDevPreview/MicrosoftTeams.schema.json",
  "manifestVersion": "devPreview",
  "version": "1.0.0",
  "id": "STABLE-GUID-HERE",
  "packageName": "com.<org>.<plugin-slug>",
  "developer": { "name": "...", "websiteUrl": "...", "privacyUrl": "...", "termsOfUseUrl": "..." },
  "name": { "short": "...", "full": "..." },
  "description": { "short": "...", "full": "..." },
  "icons": { "color": "color.png", "outline": "outline.png" },
  "accentColor": "#0078D4",
  "agentSkills": [
    { "folder": "./skills/my-skill" }
  ]
}
```

To attach a remote MCP server, add `agentConnectors` (up to 10). The connection is the
**one** `mcpServerUrl` line — Cowork registers it and auto-discovers tools at runtime.

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

Auth types: `None` (public — no `referenceId`), `OAuthPluginVault`, `ApiKeyPluginVault`
(both need a Token Store `referenceId`). REST-only backends need an MCP wrapper first.

## Step 3 — Generate icons

`color.png` 192×192 (full color) and `outline.png` 32×32 (single color, transparent bg).
Run `scripts/new-icons.ps1 -PluginDir <dir> -AccentColor "#0078D4"` for branded
placeholders; replace before store submission.

## Step 4 — Package (forward-slash zip)

Do **not** use `Compress-Archive` on Windows — it writes backslash zip entries that
violate Cowork's "no backslashes in file names" rule. Use the bundled script:

```powershell
./scripts/package-plugin.ps1 -PluginDir <plugin-folder> -Version 1.0.0
```

It emits `<plugin-folder>/dist/<name>-<version>.zip` with all files at the **root**
level and forward-slash paths.

## Step 5 — Sideload & validate

M365 Admin Center → Integrated apps → **Upload custom apps** → App type **Teams app**
→ choose the zip. On failure, open **F12 → Network → `uploadCustomApp` POST →
Response** and read `errorMessage` for the real schema violation.

## Pre-flight checklist

- [ ] Folder name == `SKILL.md` `name` (kebab-case), for every skill
- [ ] Frontmatter only uses the 5 whitelist fields
- [ ] `agentSkills` uses the `folder` key (not `path`)
- [ ] Connector uses `toolSource.remoteMcpServer.mcpServerUrl` + `authorization`; `displayName` (not `name`)
- [ ] `None` auth has **no** `referenceId`; OAuth/ApiKey **has** one
- [ ] `mcpServerUrl` is HTTPS
- [ ] Icons present: `color.png` 192×192, `outline.png` 32×32
- [ ] Zip: files at root, **forward-slash** entries
- [ ] `id` GUID stays stable across versions

## References

- `references/manifest-cheatsheet.md` — schema, connector shape, auth, full validation rules & gotchas.
- `scripts/package-plugin.ps1` — forward-slash zip packager.
- `scripts/new-icons.ps1` — placeholder icon generator.
