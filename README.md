# Agent Skills

A personal collection of reusable, **agent-agnostic** skills. Each skill packages
domain knowledge and instructions in a portable format that any capable AI agent
(Claude, Copilot, Cursor, etc.) can load and follow.

## What is a skill?

A skill is a self-contained folder under [`skills/`](skills/) that contains a
`SKILL.md` file plus any supporting assets (scripts, templates, reference docs).
The `SKILL.md` front matter tells an agent **when** to use the skill, and its body
tells the agent **how**.

## Repository structure

```
.
├── README.md            # This file
├── TEMPLATE.md          # Copy this when creating a new skill
└── skills/              # One subfolder per skill
    └── <skill-name>/
        ├── SKILL.md     # Required: metadata + instructions
        └── ...          # Optional: scripts, templates, references
```

## Adding a new skill

1. Create a folder: `skills/<skill-name>/` (use a short, kebab-case name).
2. Copy [`TEMPLATE.md`](TEMPLATE.md) into it as `SKILL.md`.
3. Fill in the front matter and instructions.
4. Add any supporting files the skill needs alongside `SKILL.md`.
5. Add a row to the [Skill index](#skill-index) below.

## SKILL.md format

Each `SKILL.md` starts with YAML front matter followed by Markdown instructions:

```markdown
---
name: my-skill
description: >
  One or two sentences describing what the skill does and, crucially, WHEN an
  agent should use it. Include trigger phrases the user might say.
---

# My Skill

Step-by-step instructions, conventions, and references the agent should follow.
```

**Field guidance**

| Field         | Required | Notes                                                        |
| ------------- | -------- | ------------------------------------------------------------ |
| `name`        | Yes      | Kebab-case, matches the folder name.                         |
| `description` | Yes      | Describe purpose **and** trigger conditions. Keep it tight.  |

Keep `SKILL.md` focused. Push long reference material into separate files in the
skill folder and link to them, so agents only load detail when needed.

## Skill index

<!-- Add one row per skill as you create it. -->

| Skill | Description |
| ----- | ----------- |
| [ms-learn-docs](skills/personal%20productivity/skills/advanced-search/ms-learn-docs/SKILL.md) | Grounds Microsoft/Azure/M365 answers in official Microsoft Learn docs via the Microsoft Learn MCP Server. Runs the full workflow in one pass — `microsoft_docs_search` (breadth), `microsoft_docs_fetch` (depth), `microsoft_code_sample_search` (code) — then answers with Learn URL citations and never fabricates APIs, flags, or steps. |
| [cowork-plugin-builder](skills/AI%20Implement/skills/development/cowork-plugin-builder/SKILL.md) | Scaffolds, validates, and packages a M365 Copilot Cowork plugin end-to-end into a sideload-ready zip — 5-field `SKILL.md` frontmatter, devPreview manifest with `agentSkills` + remote MCP `agentConnectors`, icon generation, and forward-slash packaging — with the known validation gotchas baked in. Ships `package-plugin.ps1` + `new-icons.ps1`. |
| [remotion-video-lab](skills/personal%20productivity/skills/media/remotion-video-lab/SKILL.md) | Portable Remotion + ffmpeg pipeline that turns a raw screen recording into a focused, captioned, scored final cut (trim dead time, speed up slow parts, add captions/music/narration/blur). Ships its own scaffold and enforces an agenda-first confirm workflow. |
| [slide-template-creator](skills/personal%20productivity/skills/presentation/slide-template-creator/SKILL.md) | Builds a branded `.pptx` deck by reading the brand palette/fonts from a template, generating content slides with pptxgenjs, then merging the template's branded cover and closing slides onto the front and back via python-pptx. |

## Plugin packages

Prebuilt M365 Copilot Cowork plugin bundles (manifest + icons + skills), ready to
sideload. Publisher: **TW MS Dennis**.

| Toolkit | Skill | Download |
| ------- | ----- | -------- |
| **Org User Toolkit** | [copilot-cost-advisor](skills/AI%20Implement/skills/cost/copilot-cost-advisor/SKILL.md) — routes each task to the cheapest capable option before Cowork credits are spent | [org-user-toolkit-1.0.0.zip](https://github.com/dennis175168/Dennis-Agent-Skills/raw/main/skills/AI%20Implement/plugins/org-user-toolkit/dist/org-user-toolkit-1.0.0.zip) |
| **Org IT Toolkit** | [ai-finops-report](skills/AI%20Implement/skills/cost/ai-finops-report/SKILL.md) — turns Cowork/Neptune consumption CSV exports into Word + Excel + HTML FinOps insight reports · [cowork-plugin-builder](skills/AI%20Implement/skills/development/cowork-plugin-builder/SKILL.md) — scaffolds & packages new Cowork plugins into sideload-ready zips | [org-it-toolkit-1.1.0.zip](https://github.com/dennis175168/Dennis-Agent-Skills/raw/main/skills/AI%20Implement/plugins/org-it-toolkit/dist/org-it-toolkit-1.1.0.zip) |
| **MS Learn Toolkit** | [ms-learn-docs](skills/personal%20productivity/skills/advanced-search/ms-learn-docs/SKILL.md) — grounds Microsoft/Azure/M365 answers in official Learn docs via the Microsoft Learn MCP Server (search + fetch + code sample, always cited) | [manifest + skill](skills/personal%20productivity/plugins/ms-learn-toolkit/) |
