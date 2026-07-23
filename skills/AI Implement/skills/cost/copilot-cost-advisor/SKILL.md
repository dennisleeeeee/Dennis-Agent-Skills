---
name: copilot-cost-advisor
description: |
  Cost-aware router for M365 Copilot Cowork. Apply at the start of a task (or via
  /copilot-cost-advisor) to pick the cheapest route: a metered Cowork run burns credits,
  but the licence-included Copilot Chat + Work IQ (mail, Teams, SharePoint, OneDrive)
  and built-in Office apps + Copilot cost nothing per run. Judge in one pass: if the
  included tools CAN'T do it (automation / orchestration only Cowork can do) → proceed
  silently; if they CAN and it's a CHEAP lookup / list / summary → do it, then add a
  one-line "use Chat next time" nudge; if they CAN but it's EXPENSIVE (a deck, data
  analysis, a report, a spreadsheet model) → STOP first and suggest PowerPoint / Excel /
  Word + Copilot before spending Cowork credits. Near-zero cost: no tool calls, no file
  reads, no deliberation.
  Use at the start of a task, on /copilot-cost-advisor, or on "Cowork or Chat", "cheaper
  way", "save money", "省錢", "用 Cowork 還是內建".
  Do NOT interrupt a task only Cowork can do; once the user says "go ahead", proceed.
license: MIT
compatibility: Cowork (Frontier), Claude Code, VS Code / GitHub Copilot, Cursor
metadata:
  author: Dennis Li
  version: 1.0.0
  category: analysis
  icon: Lightbulb
---

⚡ **Keep it cheap.** Judge in ONE quick pass — no deliberation, no tool calls, no
multi-step reasoning. Don't read `references/reference.md` on the common path (only if
the user asks for the app map, cost figures, or setup).

## Route by "can the included tools do it?" + "cheap or expensive?"

1. **Can the licence-included tools do it?**
   - **Copilot Chat + Work IQ** → work-data questions and retrieve / list / summarize
     (even across mail + Teams + SharePoint + OneDrive — Work IQ reads them all).
   - **A built-in Office app + its in-app Copilot** → a single artifact
     (Word / Excel / PowerPoint / Outlook…), including drafting a deck, analysing
     data, or writing a report.
   - **No** → it needs Cowork's multi-step automation / cross-app orchestration / a
     complex chained job Chat & Office can't do → **proceed silently, no message.**

2. **If the included tools CAN do it, is it cheap or expensive?**
   - **Cheap** (a quick lookup / list / short summary / short draft) → **do it now**,
     then append ONE post-task nudge (Output A). Don't interrupt — the tip would cost
     more than the task itself.
   - **Expensive** (a full deck, data analysis, a report, a large spreadsheet model —
     big enough that a Cowork run really burns credits) → **STOP first**, give the
     pre-tip (Output B), and wait. This is where interrupting saves real money.

Already told "go ahead" / "use Cowork" → proceed silently.

## Output

**A. Cheap — do the task, then append one line:**

> 💡 **下次更省**：這種小任務直接在 **M365 Copilot Chat (Work IQ)** 問就免費（已含授權），
> Cowork 每跑一次都燒 credits。

**B. Expensive & divertible — STOP before doing it:**

> 💡 **省錢提醒**：這個 *[簡報／報表／資料分析]* 用 **[PowerPoint / Excel / Word] + Copilot**
> 就能做、已含在授權內；在 Cowork 做這種大任務會燒不少 credits。要先去那邊做，還是直接在
> Cowork 幫你？*(回「go ahead」我就直接在這做。)*

**C. Needs Cowork:** no message — just do it.

Only surface a tip once per task. App map / cost figures / delegation live in
`references/reference.md` — read only if the user asks.
