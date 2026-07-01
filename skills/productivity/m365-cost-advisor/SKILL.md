---
name: m365-cost-advisor
description: |
  Runs at the START of every conversation: classifies the request and, when it is
  a work-data question or a simple one-off task, steers the user to the cheaper
  INCLUDED AI route — M365 Copilot Chat with Work IQ (reads mail, calendar, Teams,
  files; covered by the licence, no per-run billing) — instead of a metered Cowork
  session. This is NOT "don't use AI": it routes simple Q&A to the included AI and
  reserves Cowork for what only Cowork can do (multi-step automation, continuous /
  sequential actions, multi-source orchestration, complex tasks).
  Use when the user kicks off any request, or asks "should I do this in Cowork or
  Copilot Chat", "is there a cheaper way", "can I do this for free", "save money",
  "用 Cowork 還是內建 / Copilot Chat", "省錢", "Work IQ 問得到嗎".
  Do NOT use once the user has already chosen Cowork ("just do it in Cowork",
  "go ahead"); for browser/web automation (use agent-browser); or to PRODUCE the
  artifact — once Cowork is chosen, hand off to docx, xlsx, pptx,
  slide-template-creator, work-report-slide, teams-customer-dashboard,
  weekly-meeting-notes, or deep-research instead.
cowork:
  category: analysis
  icon: Lightbulb
---

## Overview

This skill is a **cost gatekeeper** that runs at the **start of every
conversation**. Cowork sessions are metered/billed compute — even the simplest
task costs **> 1 USD per run**. Meanwhile the user's M365 licence already
includes **Copilot Chat with Work IQ**, an AI that can read their work data
(mail, calendar, Teams, files, people) to answer questions at **no per-task
cost**.

So the cheaper route for *questions about work data* and *simple one-off tasks*
is not "do it by hand" and it is **not** "don't use AI" — it is **use the
included AI** (Copilot Chat + Work IQ) instead of paying for a Cowork run. This
skill surfaces that route *before* any work begins and lets the user decide.

Cowork is still the right — and only — tool for **automation, continuous /
sequential actions, multi-source orchestration, and complex multi-step tasks**
that Copilot Chat cannot perform. For those, this skill says so in one line and
proceeds.

## When to Use

- **At the start of every conversation / first request of a turn** — run the
  Phase 1 classification before acting.
- The user explicitly asks whether a task is cheaper via Copilot Chat / Work IQ,
  or how to avoid a billed Cowork run.

## When NOT to Use

- **The user already chose Cowork** ("do it in Cowork", "go ahead", "I know,
  just run it here") — skip the check entirely and proceed. Never re-prompt.
- **Genuinely agentic, multi-step, cross-source work** that only Cowork can do
  (see *When Cowork IS the right tool*) — note it briefly and proceed; do not
  steer to Copilot Chat.
- **Producing the artifact** — this skill only advises. Once Cowork is chosen,
  hand off to the right creation skill (see Delegation).
- **Browser/web automation** — use `agent-browser` instead.
- Pure greetings or general-knowledge questions with **no work-data and no
  artifact** at all. (A routine work-data lookup the included Copilot Chat can
  answer — e.g. "what meetings do I have today" — is *not* exempt: apply the gate
  *before* running it; never run it first and tip afterward.)

## Delegation

This skill never builds anything itself. After the user picks Cowork, route to
the specialist and stop:

| If the task is… | Hand off to |
|-----------------|-------------|
| A prose document, memo, letter | `docx` |
| A spreadsheet, table, model | `xlsx` |
| A PDF | `pdf` |
| Generic slides / a deck | `pptx` |
| Branded company slides | `slide-template-creator` |
| Dennis's weekly work-report deck | `work-report-slide` |
| A Teams-activity customer dashboard | `teams-customer-dashboard` |
| Weekly meeting notes | `weekly-meeting-notes` |
| Browser / web automation | `agent-browser` |
| Deep multi-source research | `deep-research` |

## Core Instructions

> 🔁 **Run at the start of every conversation.** Before acting on the user's first
> request of a turn, run the Phase 1 classification *first*. This assessment is the
> entry point of every task, not an afterthought.

> ⛔ **Pre-execution gate — judge BEFORE you act.** For a Chat-capable or
> built-in-capable task, surface the tip and **STOP** — do not look anything up,
> draft, build, or send until the user has decided. Advising *after* the work is
> done defeats the purpose: the user can only save the spend if asked *before* the
> run begins.

> 🙅 **Never frame this as "don't use AI."** The recommended cheaper route IS an AI
> — M365 Copilot Chat with Work IQ. Steer the user to the *included* AI for simple
> work-data questions; never tell them to do it manually or to avoid AI.

### Phase 0 — Ensure always-on enrollment (once per session)

A skill only loads when triggered; to truly run on **every** task it must be
required by the user's personal instructions. Before the first tip of a session,
check that this is wired up:

1. Read the user's personal instructions file **`copilot-instructions.md`**
   (primary path: `/mnt/user-config/.claude/copilot-instructions.md`).
2. **If it already contains a directive that requires running this cost check /
   `m365-cost-advisor` at the start of every task** → do nothing; continue to
   Phase 1.
3. **If no such directive exists** → *actively ask* the user (via
   `AskUserQuestion`) whether to add one, so the cost check runs automatically at
   the start of every task. Explain briefly why (a skill otherwise only loads when
   triggered). If they agree, **append the directive below** to
   `copilot-instructions.md`. If they decline, respect it and do not ask again
   this session.

Ask **at most once per session**, and **never block the actual task** on it —
surface the cost tip / proceed regardless of the answer.

Directive to append when the user agrees:

> ## Cost check before every task
> At the start of every task, before acting, apply the `m365-cost-advisor` skill:
> if it is a work-data question or a simple one-off task, recommend **M365 Copilot
> Chat (Work IQ)** and stop for my decision; only go straight to Cowork for
> multi-step automation / continuous actions / complex orchestration that only
> Cowork can do.

### Phase 1 — Classify the request (1 quick judgment)

| Signal | Bucket | Action |
|--------|--------|--------|
| A question about work data, or a simple one-off lookup / summary | **Chat-capable** | Recommend **M365 Copilot Chat (Work IQ)** (Phase 2), then STOP and ask |
| A single artifact one desktop app makes (a doc, a sheet, a few slides) | **Built-in-capable** | Recommend the built-in app + in-app Copilot (Phase 2), then STOP and ask |
| Multi-step automation, continuous / sequential actions, multi-source orchestration, or a complex task | **Cowork-worthy** | One-line note that only Cowork can do it, proceed |
| User already said "use Cowork" / "go ahead" | **Pre-confirmed** | Proceed silently |

### Phase 2 — Map to the cheaper included route

**For a question about work data, or a simple summary / lookup (the most common
case):**
→ **M365 Copilot Chat with Work IQ.** Included in the licence; reads the user's
mail, calendar, Teams, files, and people to answer. No per-run billing. This is
*using AI* — just the included one.

**For a single artifact a desktop app makes** (+ in-app Copilot, covered by
licence):

| Task type | Built-in M365 feature |
|-----------|------------------------|
| Write / format a document, letter, memo | **Word** (+ Copilot in Word) |
| Table, list, budget, calc, simple chart | **Excel** (+ Copilot in Excel) |
| A few slides / quick deck | **PowerPoint** (+ Copilot, Designer) |
| Draft / reply to an email | **Outlook** (+ Copilot in Outlook) |
| Meeting recap, transcript summary, action items | **Teams Intelligent Recap / Copilot in Teams** |
| Notes, lightweight tracking, task list | **OneNote, Loop, Planner, To Do** |
| Survey, quiz, intake form | **Microsoft Forms** |
| Simple workflow / approval / notification | **Power Automate** |
| Dashboard / report from existing data | **Power BI** |
| Diagram / flowchart | **Visio** |

### Phase 3 — Recommend, then STOP and let the user decide

Lead with the cheaper option in **one short tip** (see Output), then **stop and
wait in the same turn** — do not run tools, gather data, or start the task. Then:
- Wait for the user to choose; **or**
- If the user replies "continue in Cowork" / "go ahead", proceed and hand off to
  the right creation skill.

The only exception is a **Cowork-worthy** task: note in one line that only Cowork
can do it and proceed without waiting.

Default bias: recommend the included route for Chat-/Built-in-capable tasks, but
**never refuse** — the user can always choose Cowork.

## When Cowork IS the right (and only) tool

Only Cowork can do these. Recommend it without hesitation (one-line note, then
proceed) — Copilot Chat (Work IQ) cannot perform them:

- **Automation & continuous / sequential actions** — chained steps with
  follow-through, acting across several apps in one flow.
- **Multi-source orchestration** — pulling email + Teams + calendar + files
  together, synthesizing, and producing an artifact.
- **Complex, multi-step tasks** a single chat answer cannot complete.

Copilot Chat answers questions; it does not execute multi-step automation.

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

## Cost Reference

Figures from Dennis's "Cowork billing compare" analysis (user-supplied):

- **Simplest one-off task in Cowork:** **> 1 USD per run**, billed each time.
- **M365 Copilot (incl. Copilot Chat + Work IQ):** ~**30 USD fixed** monthly fee,
  already covered by the licence — no per-task charge. For simple, repeated
  work-data questions this is far cheaper than paying > 1 USD every Cowork run.
- **Single one-off task:** Cowork is roughly comparable to other general-purpose
  AI agents (≈ **7% lower** on average in the analysis).
- **Work IQ / Deep Research tasks:** cost **more** in Cowork, because Cowork pulls
  a large amount of work data through Work IQ for a more precise analysis. Work IQ
  can be **turned off** in Cowork to cut cost — but that reduces data completeness.

## Guardrails

- **Run at the start of every conversation**, surface the tip **at most once per
  task**. Do not nag or repeat it on follow-ups within the same task.
- **Enrollment ask (Phase 0) is once per session.** Only ask to add the directive
  to `copilot-instructions.md` when it is genuinely missing; if it is already
  there, or the user has declined this session, never ask again. Never block the
  task on this.
- **Never frame the recommendation as "don't use AI."** It is "use the included
  AI (Copilot Chat + Work IQ) instead of a billed Cowork run."
- **Pause, don't refuse.** For a Chat-/Built-in-capable task, pausing for the
  user's decision *before* executing is the intended behavior — that is the gate,
  not a refusal. Never decline the task outright; the user can always choose Cowork.
- **Respect a prior Cowork choice** — if the user signalled Cowork (this turn or
  earlier), proceed without asking.
- **Don't slow down agentic work.** If the task genuinely needs Cowork
  (automation / continuous actions / orchestration), say so in one line and
  proceed — don't force a false "use Copilot Chat" suggestion.
- **Never fabricate cost numbers.** Use only the figures in Cost Reference (or
  newer ones the user supplies); otherwise speak qualitatively ("billed per run"
  vs "included in licence").
- Once Cowork is chosen, hand off to the correct creation skill — this skill does
  not produce the artifact.
