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
| [remotion-video-lab](skills/remotion-video-lab/SKILL.md) | Portable Remotion + ffmpeg pipeline that turns a raw screen recording into a focused, captioned, scored final cut (trim dead time, speed up slow parts, add captions/music/narration/blur). Ships its own scaffold and enforces an agenda-first confirm workflow. |
| [slide-template-creator](skills/slide-template-creator/SKILL.md) | Builds a branded `.pptx` deck by reading the brand palette/fonts from a template, generating content slides with pptxgenjs, then merging the template's branded cover and closing slides onto the front and back via python-pptx. |

## Plugin packages

Prebuilt M365 Copilot Cowork plugin bundles (manifest + icons + skills), ready to
sideload. Publisher: **TW MS Dennis**.

| Toolkit | Skill | Download |
| ------- | ----- | -------- |
| **Org User Toolkit** | [copilot-cost-advisor](skills/AI%20Implement/skills/copilot-cost-advisor/SKILL.md) — routes each task to the cheapest capable option before Cowork credits are spent | [org-user-toolkit-1.0.0.zip](https://github.com/dennis175168/Dennis-Agent-Skills/raw/main/skills/AI%20Implement/plugin/org-user-toolkit/dist/org-user-toolkit-1.0.0.zip) |
| **Org IT Toolkit** | [ai-finops-report](skills/AI%20Implement/skills/ai-finops-report/SKILL.md) — turns Cowork/Neptune consumption CSV exports into Word + Excel + HTML FinOps insight reports | [org-it-toolkit-1.0.0.zip](https://github.com/dennis175168/Dennis-Agent-Skills/raw/main/skills/AI%20Implement/plugin/org-it-toolkit/dist/org-it-toolkit-1.0.0.zip) |
