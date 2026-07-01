---
name: m365-cost-advisor
description: |
  Cost gatekeeper, run at the START of every request. Routes work-data questions
  AND broad cross-source retrieve-and-list tasks to the INCLUDED AI — M365 Copilot
  Chat + Work IQ (reads mail, calendar, Teams, SharePoint, OneDrive; licence-covered,
  no per-run billing) — and reserves the metered Cowork run for what only Cowork can
  do: multi-step automation, continuous actions, or multi-source work that TRANSFORMS
  the data into a produced artifact (not mere listing). It is "use the included AI",
  never "don't use AI".
  Use when the user starts any request or asks "Cowork or Copilot Chat", "cheaper
  way", "save money", "用 Cowork 還是內建", "省錢", "Work IQ 問得到嗎".
  Do NOT use once Cowork is chosen ("go ahead"), for browser automation (use
  agent-browser), or to PRODUCE the artifact — hand off to docx, xlsx, pptx,
  slide-template-creator, work-report-slide, teams-customer-dashboard,
  weekly-meeting-notes, or deep-research.
cowork:
  category: analysis
  icon: Lightbulb
---

## What this does

Cowork runs are metered (**> 1 USD even for the simplest task**). The user's M365
licence already includes **Copilot Chat + Work IQ**, which reads their work data
(mail, calendar, Teams, SharePoint, OneDrive, people) at **no per-run cost**. So
for questions and simple retrieve/list/summarize tasks, surface the *included* AI
route **before** any work begins and let the user decide. Reserve Cowork for
automation / transformation only Cowork can do.

**Skip the gate when:** the user already chose Cowork ("go ahead") — proceed
silently; the task genuinely needs Cowork — one-line note, proceed; it's a pure
greeting / general-knowledge question with no work data. (A routine work-data
lookup is NOT exempt — gate it *before* running, never tip afterward.)

## Delegation (after Cowork is chosen — this skill never builds the artifact)

Prose doc → `docx` · Spreadsheet → `xlsx` · PDF → `pdf` · Slides → `pptx` ·
Branded slides → `slide-template-creator` · Weekly work-report deck →
`work-report-slide` · Teams customer dashboard → `teams-customer-dashboard` ·
Weekly meeting notes → `weekly-meeting-notes` · Browser automation →
`agent-browser` · Deep research → `deep-research`.

## Rules

- **Gate before you act.** Classify (Phase 1) on the first request of each turn.
  For a Chat-/Built-in-capable task, surface the tip and **STOP** — don't look up,
  draft, build, or send until the user decides. Advising afterward wastes the spend.
- **Never say "don't use AI."** The cheaper route IS AI (Copilot Chat + Work IQ).
- **Pause, don't refuse.** The user can always choose Cowork. Respect a prior
  Cowork choice and proceed silently. Surface the tip at most once per task; never
  fabricate cost numbers (use the Cost reference or user-supplied figures).

### Phase 0 — Always-on enrollment (once per session)

A skill only loads when triggered; to run on **every** task it must be required by
the user's personal instructions. Once per session, before the first tip: read
`copilot-instructions.md` (primary: `/mnt/user-config/.claude/copilot-instructions.md`).
If it already requires this cost check → continue. If not → ask (via
`AskUserQuestion`) whether to append the directive below; if yes, append it; if
declined, don't ask again. Never block the task on this.

> ## Cost check before every task
> At the start of every task, before acting, apply `m365-cost-advisor`: for a
> work-data question or simple one-off task, recommend **M365 Copilot Chat (Work
> IQ)** and stop for my decision; go straight to Cowork only for multi-step
> automation / transformation that only Cowork can do.

### Phase 1 — Classify

| Signal | Bucket | Action |
|--------|--------|--------|
| Work-data question, or simple lookup/summary — **incl. broad cross-source retrieve-and-list** ("find all X across mail+Teams+files, list by date with source & owner") | **Chat-capable** | Recommend **Copilot Chat (Work IQ)**, STOP & ask |
| A single artifact one desktop app makes (a doc, sheet, few slides) | **Built-in-capable** | Recommend the app + in-app Copilot, STOP & ask |
| Multi-step automation, continuous actions, or multi-source work that **transforms/synthesizes into a produced artifact** (analysis, comparison, deck, model) — *not* mere retrieve-and-list | **Cowork-worthy** | One-line note, proceed |
| User already said "use Cowork" / "go ahead" | **Pre-confirmed** | Proceed silently |

> 🧪 **Verb test.** *Find / list / summarize / annotate* → **Chat**. *Analyze /
> compare / synthesize / build / produce / automate* → **Cowork**. Source count is
> NOT the deciding factor — Work IQ already reads all work sources together; what
> tips a task to Cowork is whether the data must be *worked on*, not just *listed*.
> (Verified: a 30-day "find & list Cowork items across 4 sources" task came back
> fuller AND cheaper on Chat/Work IQ than on a metered Cowork run.)

### Phase 2 — The included route

- **Work-data question / retrieve / summarize** → **Copilot Chat + Work IQ**
  (licence-covered, no per-run billing).
- **A single artifact a desktop app makes** (+ in-app Copilot):

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

### Phase 3 — Recommend, then STOP

Give one short tip (see Output), then wait in the same turn — don't run tools or
start the task. If the user replies "go ahead" / "in Cowork", proceed and hand off
(Delegation). Exception: a **Cowork-worthy** task — one-line note, then proceed.
Default bias to the included route, but **never refuse** — the user can always
choose Cowork.

**Cowork is the right (and only) tool for:** automation / continuous sequential
actions across apps; multi-source work that *transforms/synthesizes* the data into
a produced artifact (deck, report, comparison, model); complex multi-step tasks a
single chat answer can't complete. Merely *retrieving and listing* across sources
is NOT this — Work IQ does that faster, fuller, and at no per-run cost.

## Output

Keep it to 1–3 lines, friendly, non-blocking.

**Chat-capable task (work-data question / simple one-off):**

> 💡 **省錢小提醒**：這看起來是一個 *[task type]* — 直接問 **M365 Copilot Chat
> (Work IQ)** 就能讀你的工作資料回答，已含在授權內、不另計費；Cowork 則是每次
> 執行都計費（最簡單的任務每次 > 1 USD）。要我直接在 Cowork 幫你做，還是先用
> Copilot Chat (Work IQ) 問就好？
> *(回覆「在 Cowork 做」或「go ahead」我就繼續。)*

**Built-in-capable task (single artifact):** swap the recommended route for the
matching desktop app + its in-app Copilot.

**Cowork-worthy task — one line, then proceed:**

> ✅ 這需要多步驟自動化／連續性動作，只有 Cowork 能做 — 直接幫你進行。

## Cost reference (never fabricate; use these or user-supplied figures)

- Simplest Cowork task: **> 1 USD per run**, billed each time.
- M365 Copilot (Chat + Work IQ): ~**30 USD/mo fixed**, licence-covered, no
  per-task charge — far cheaper for repeated work-data questions.
- Single one-off task: Cowork ≈ other AI agents (~7% lower on average).
- Work IQ / Deep Research in Cowork costs **more** (pulls lots of work data); Work
  IQ can be turned off to cut cost, but that reduces completeness.
