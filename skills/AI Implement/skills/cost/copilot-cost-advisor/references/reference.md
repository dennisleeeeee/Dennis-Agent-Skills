# copilot-cost-advisor — reference (load ONLY when needed)

Read this **only** after the gate has fired and you actually need a detail: the
built-in app map, delegation targets, cost figures, one-time enrollment, or the
rationale. Do **not** read it on the common "tip → STOP" path — reading it costs
tokens/credits and defeats the point of a cheap gate.

## Built-in app map (single-artifact tasks)

| Task | Built-in |
|------|----------|
| Document, letter, memo | **Word** |
| Table, budget, calc, chart | **Excel** |
| A few slides | **PowerPoint** (+ Designer) |
| Draft / reply email | **Outlook** |
| Meeting recap, action items | **Teams Intelligent Recap** |
| Notes, tracking, tasks | **OneNote / Loop / Planner / To Do** |
| Survey, quiz, form | **Forms** |
| Simple workflow / approval | **Power Automate** |
| Dashboard from existing data | **Power BI** |
| Diagram / flowchart | **Visio** |

## Delegation (after Cowork is chosen — this skill never builds the artifact)

Prose doc → `docx` · Spreadsheet → `xlsx` · PDF → `pdf` · Slides → `pptx` ·
Branded slides → `slide-template-creator` · Weekly work-report deck →
`work-report-slide` · Teams customer dashboard → `teams-customer-dashboard` ·
Weekly meeting notes → `weekly-meeting-notes` · Browser automation →
`agent-browser` · Deep research → `deep-research`.

## Chat vs Cowork — the rule

- *Find / list / summarize / annotate* → **Chat (Work IQ)**. Source count is NOT the
  deciding factor — Work IQ reads mail, Teams, SharePoint, OneDrive together.
- *Analyze / compare / synthesize / build / produce / automate* → **Cowork**.
- Tipping point: must the data be *worked on* (transformed into an artifact), or just
  *listed*?
- Verified: a 30-day "find & list Cowork items across 4 sources" task came back fuller
  AND cheaper on Chat/Work IQ than on a metered Cowork run.

## Cost figures (never fabricate; use these or user-supplied)

- Simplest Cowork task: **> 1 USD per run**, billed each time.
- M365 Copilot (Chat + Work IQ): ~**30 USD/mo fixed**, licence-covered, no per-task
  charge — far cheaper for repeated work-data questions.
- Single one-off task: Cowork ≈ other AI agents (~7% lower on average).
- Work IQ / Deep Research in Cowork costs **more** (pulls lots of work data); Work IQ
  can be turned off to cut cost, but that reduces completeness.
- ⚠️ **Gate overhead matters.** The gate's own turn must stay far below a task turn —
  otherwise a cheap task diverted to Chat saves nothing (a real run showed the tip
  turn costing ~71 credits vs ~65 to just do the task). Keep the gate to one
  immediate reply: no tool calls, no file reads, no multi-step reasoning.

## One-time enrollment (at most once per session, only when asked)

To make the check run on every task it must be required by the user's personal
instructions. If not already present, offer to append to `copilot-instructions.md`
(primary: `/mnt/user-config/.claude/copilot-instructions.md`):

> ## Cost check before every task
> At the start of every task, before acting, apply `copilot-cost-advisor`: for a
> work-data question or simple one-off task, recommend **M365 Copilot Chat (Work IQ)**
> in one line and stop for my decision; go straight to Cowork only for multi-step
> automation / transformation that only Cowork can do.

Never block a task on this; ask at most once per session; if declined, don't ask again.
