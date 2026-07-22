---
name: ai-finops-report
description: >
  AI FinOps insight builder for M365 Copilot Cowork / Neptune credit-consumption
  exports. Turns the CSV logs you download from the admin cost-management view
  (per-user, per-group, per-service consumption + Cowork task details) into a
  polished insight report: ONE Word narrative (.docx) plus ONE Excel workbook
  (.xlsx) with data tables, charts, and a quantified cost-optimization action
  plan. Centerpiece is cost optimization — how to right-size limits, reclaim
  wasted licences, tame concentration risk, and cap ungoverned spend.
  Use when the user says "AI FinOps report", "分析 Copilot 消耗", "credit 用量分析",
  "cost management log 做成報告", "Cowork 成本報告", "optimize Copilot cost",
  "Word 加 Excel 的成本洞察報告", or drops the neptuneconsumption* / CoworkUserDetails
  CSV exports and asks for insight.
  Companion to copilot-cost-advisor (that one PREVENTS spend at task time; this one
  ANALYZES spend after the fact).
license: MIT
compatibility: Cowork (Frontier), Claude Code, VS Code / GitHub Copilot, Cursor
metadata:
  author: Dennis Li
  version: 1.0.0
  category: analysis
  icon: ChartMultiple
---

# AI FinOps Report

## Purpose

Take the raw **credit-consumption CSV exports** from the M365 Copilot Cowork /
Neptune cost-management admin view and produce a two-part **insight report**:

1. **Word (.docx)** — a zh-TW narrative for internal FinOps review: executive
   summary, consumption/utilization/adoption findings, anomalies, and a
   prioritized **cost-optimization action plan**.
2. **Excel (.xlsx)** — the working data: cleaned per-user / per-group / per-service
   tables, a summary dashboard with charts, and a recommendations sheet.

Everything is measured in **credits** (never fabricate a USD figure). Pass an
optional `--credit-cost` only if the user supplies a real credit→currency rate.

## When to use

- User exports the `neptuneconsumptionusers`, `neptuneconsumptiongroups`,
  `neptuneconsumptionservices`, and/or `CoworkUserDetails` CSVs and wants insight.
- "把 cost management 的 log 做成 Word + Excel 報告"
- "分析 Copilot Cowork credit 用量 / 怎麼優化成本"
- Any recurring monthly Copilot/Cowork consumption review.

## When NOT to use

- Task-time "should I use Cowork or Chat to save money?" → use **copilot-cost-advisor**.
- Building the report artifact from arbitrary non-Copilot data → use plain `xlsx` / `docx`.
- Azure resource cost (not Copilot credits) → use the Azure cost skills.

## Instructions

1. **Collect the exports.** Ask the user for the folder holding the CSV(s), or use
   the files they attached. The script auto-detects each file by its header
   signature, so filenames and download suffixes don't matter. Any subset of the
   four export types works; missing types are skipped gracefully.

2. **Confirm two things (one line each):**
   - Reporting period label (e.g. `2026-07`) — defaults to today's month.
   - Whether they have a real **credit→currency rate**. If not, keep it in credits.

3. **Run the generator:**
   ```bash
   python3 scripts/generate_finops_report.py \
     --input-dir "<folder with the CSVs>" \
     --output-dir "<where to write the report>" \
     --period "2026-07" \
     --org "<tenant / customer name>"
     # optional: --credit-cost 0.01 --currency USD
   ```
   Dependencies: `python-docx`, `openpyxl` (install with
   `pip install python-docx openpyxl` if missing).

   **Excel output is a Power BI-style dashboard.** The first sheet (`📊 Dashboard`)
   has 6 KPI cards + 8 charts (top spenders, service doughnut, concentration
   Pareto, credits-by-group, utilization %, licence-status doughnut,
   sessions-vs-credits scatter, automation split). Raw tables live on the
   `使用者 / 群組 / 服務 / 任務明細` sheets; the action plan on `最佳化建議`.

4. **No data yet? Try it on fake data first.** Generate realistic demo exports
   (with seeded anomalies — whales, unlimited accounts, idle licences, dormant
   groups) and run the report on them to feel the dashboard:
   ```bash
   python3 scripts/make_fake_data.py --output-dir "/tmp/fake" --users 45 --seed 7
   python3 scripts/generate_finops_report.py --input-dir "/tmp/fake" \
     --output-dir "/tmp/out" --period "DEMO" --org "Demo Tenant" --credit-cost 0.01
   ```

   **Want true interactive slicers?** Excel can't do real slicers without a
   PivotTable, so for a live-filter experience generate the **HTML dashboard**
   instead (Chart.js + Clawpilot theme, self-contained single file). It has
   slicers (licence / flag / min-credits / search) that live-update the KPIs,
   all charts, and the data table:
   ```bash
   python3 scripts/generate_html_dashboard.py --input-dir "<csvs>" \
     --output-dir "<out>" --period "2026-07" --org "<tenant>"
   ```
   Opens in any browser; no server needed. (Uses the Chart.js CDN — for a fully
   offline/OneDrive-shareable file, inline the library.)

5. **Review the console summary** the script prints (totals, top spender share,
   flagged wastage). Sanity-check the headline numbers before handing off.

6. **Deliver both files** and paste the top 3 optimization actions into chat so the
   user gets value without opening anything. Point out any **governance gaps**
   (unlimited users, inactive licences, single-user concentration) explicitly —
   that is the optimization payload.

7. **For trend/forecast**, ask the user to keep monthly exports; pass several months
   via repeated `--input-dir` is not supported yet — instead re-run per month and
   compare. A single export = a snapshot; say so in the report.

## What the report measures

See [`references/finops-playbook.md`](references/finops-playbook.md) for the full
metric definitions, thresholds, and the optimization heuristics the recommendation
engine applies. See [`references/data-schema.md`](references/data-schema.md) for the
exact CSV export columns and how each field maps into the report.

## References

- [`scripts/generate_finops_report.py`](scripts/generate_finops_report.py) — the generator.
- [`references/data-schema.md`](references/data-schema.md) — CSV export schema.
- [`references/finops-playbook.md`](references/finops-playbook.md) — metrics + optimization rules.
