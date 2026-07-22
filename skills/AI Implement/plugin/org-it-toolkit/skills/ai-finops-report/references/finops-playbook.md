# AI FinOps — metrics & optimization playbook

The generator computes these metrics and runs the optimization heuristics below.
Cost is measured in **credits**; a USD/other figure appears only if the user
supplies a real `--credit-cost` rate (never fabricate one).

## Metric groups

### A. Consumption summary
- **Total credits used** = Σ user `Monthly credits used`.
- **Active users** = users with credits used > 0.
- **Avg credits / active user**.
- **Top spenders** (ranked) and each one's **share of total**.
- **Service split** (Cowork vs Work IQ API vs …).

### B. Utilization vs. limits
- For users with `Monthly credit limit > 0`: **real % used** = used / limit.
- **Near-limit** users: % used ≥ 80%.
- **Over-limit** users: % used > 100%.
- **Unlimited** users: limit = 0 → no cap → governance risk.

### C. Anomaly / outlier detection
- **Concentration risk**: top user's share of total credits.
- **Single-user dominance**: one user ≥ 60% of all spend.
- **High intensity**: credits ÷ session much higher than peer median.
- **Over-limit breaches**.

### D. Adoption & engagement (needs CoworkUserDetails)
- **Automation ratio** = scheduled ÷ total tasks (higher = more mature automation).
- **Active days**, **session counts**.
- **Scheduled vs user-initiated** split.

### E. Licence waste
- **Inactive licensed users**: `Microsoft 365 Copilot license = Yes` AND credits used
  = 0 AND session count = 0 → paying for a licence nobody uses.

## Optimization heuristics (recommendation engine)

Each fired rule emits: **priority · theme · finding (quantified) · action · benefit**.

| Rule | Trigger | Recommended action | Benefit |
|---|---|---|---|
| Cap ungoverned spend | any user with limit = 0 | Set a monthly credit limit sized to ~1.2× their observed usage | Prevents runaway spend; makes cost predictable |
| Break concentration risk | top user ≥ 60% of total | Review that user's workload; move repetitive jobs to licence-included Chat/Work IQ (see copilot-cost-advisor) | Cuts the single biggest cost driver |
| Reclaim wasted licences | licensed but 0 usage | Reassign or drop the licence | Direct licence-cost saving |
| Right-size over-caps | limit set but < 40% used | Lower the limit toward actual usage | Tighter budgeting, no impact on users |
| Address near/over-limit | % used ≥ 80% (or > 100%) | Confirm whether legitimate; raise limit deliberately or coach usage | Avoids surprise throttling / overruns |
| Raise automation maturity | automation ratio < 20% | Promote scheduled tasks over ad-hoc runs | More output per credit |
| Retire dormant groups | group with 0 active members | Clean up / reassign | Reduces sprawl |

## Report structure the script produces

**Word (.docx)** — zh-TW:
1. 封面 + 報告範圍（期間、租戶、資料來源）
2. 執行摘要（Executive Summary，含關鍵數字）
3. 消耗總覽（Consumption Summary + top spenders 表）
4. 額度使用率（Utilization vs limits）
5. 採用與參與（Adoption & engagement）
6. 異常與風險（Anomalies / concentration / licence waste）
7. **成本最佳化行動計畫（Optimization Action Plan）** ← 重點，依優先級排序
8. 附註與方法（credits-only、單月快照等免責）

**Excel (.xlsx)**:
- `總覽 Summary` — headline KPIs + top-spender bar chart + service pie chart
- `使用者 Users` — cleaned per-user table with recomputed % used + flags
- `群組 Groups`
- `服務 Services`
- `任務明細 Tasks` (if present)
- `最佳化建議 Recommendations` — the action plan as a filterable table
