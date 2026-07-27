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

### F. Task cost profile（相對權重，不用絕對數字）

絕對 credit 數值會隨模型改版而失效，**一律以相對權重判斷**，門檻取自該租戶自己的
分佈（credits/task 的中位數與百分位）：

| 權重 | 行為 |
|---|---|
| **很重** | 深度研究——比其他任務高一個數量級 |
| **重** | 文件生成（簡報、試算表、網頁）與跨 App 連續任務 |
| **一般** | 單次查詢、讀檔、產生圖表 |

intensity 一律以「相對租戶中位數的倍數」表達，**絕不引用固定的每任務 credit 值**。

### G. Tier allocation（成本結構分層）— the headline insight

將每位使用者的工作負載分到三層，並報告**目前的成本結構**。

> **不得預設或強制任何目標比例**。任何提到的比例都只是示意，每家企業依自己的
> 工作型態設定。只有使用者主動提供目標時，才做現況 vs 目標的比對。

Per-user signals（需要 CoworkUserDetails）：
- **repeatability** = `ScheduledTasks ÷ TotalTasks` → 可流程化程度（最強訊號，直接量測）
- **intensity** = `credits ÷ TotalTasks` → 單位任務成本，對應上方成本權重
- **frequency** = `TotalTasks ÷ ActiveDays` → 使用密度

**三層 = 三個使用面（surface）**：

| 層級 | 對應使用面 | 判定條件 | 典型任務 |
|---|---|---|---|
| **Fixed** | Copilot Chat / Copilot in Apps（included，不耗 credit） | 單次、無遠端執行，intensity 落在一般區間 | 找答案、摘要整理、草擬內容、研究分析、單步驟文件生成 |
| **Semi-fixed** | Custom Agent（MCS / Power Platform / Foundry） | repeatability ≥ 0.5，或 frequency 高且 intensity 穩定 | 固定專業問答（HR/IT/產品）、重複 SOP（週報、案件分類）、企業流程串接（CRM/ERP/核准） |
| **Dynamic** | Cowork / UBB | intensity 落在重以上，或需要排程遠端執行 | 多步驟、跨 App 執行、長時間任務——**沒有 Chat 替代方案，計量計費是合理的** |

重點：**深度研究與文件生成若在 Cowork 跑，是最大的可避免成本**（這些在 Chat /
Office app 本來就含在授權內）。

#### 信心度（必填）

分層是從**用量形狀與成本特徵**推論而來，**不是從任務內容**（取不到）。每筆分類必須
標註 **高 / 中 / 低**：只有 repeatability、intensity 與成本權重三者一致時才能標高。
並須明講：intensity **分不出「任務複雜」與「輸入很大」**，因此每個分層都是**待驗證的
假設，不是定論**。

輸出：三層現況佔比、**分層分類表**（使用者 / 目前 credits / repeatability /
建議層級 / 理由 / 信心度）。並針對 Fixed 層做 **seat 右調**：依 licence 指派 vs
實際活躍，算出建議 seat 數與可回收數。若缺少任務明細，明講並退回只用 intensity。

## IT actions（每個發現都要可執行）

> 「把這位使用者搬到 Fixed」**不是一個行動**——他本來就有 licence，卻還是選了 Cowork。
> 行為改變需要槓桿。所有建議只能落在下列五種。

| # | 槓桿 | 內容 |
|---|---|---|
| 1 | **情境確認** | 點名該訪談的使用者（約 15 分鐘）與要問的問題：這任務實際在做什麼 / 多久跑一次 / 輸入輸出是否固定 / Copilot Chat 做不做得到。依 credits 規模排序。**信心度為中或低時，一律先做這一步** |
| 2 | **額度政策** | 設定或下調 per-user / per-group 月上限，附建議數值。**IT 唯一的直接控制權** |
| 3 | **使用引導** | 公告哪些任務類型該回 Chat / Office app，以相對租戶中位數量化可避免的消耗 |
| 4 | **建 Custom Agent** | 點名候選工作負載、其 repeatability，以及可從 dynamic 轉成 semi-fixed 的 credits |
| 5 | **授權調整** | 回收閒置 licence；為搬下層的使用者補 seat |

行動表欄位：**行動 / 對象（UPN 或群組）/ 負責人 / 驗證方式 / 預估影響 / 信心度**，
依影響排序。

## Trigger rules（每條觸發一列行動）

| Rule | Trigger | Action |
|---|---|---|
| Cap ungoverned spend | limit = 0 | 設定約 1.2× 實際用量的月上限 |
| Break concentration risk | top user ≥ 60% | 優先檢視該工作負載 |
| Reclaim wasted licences | licensed 但 0 usage | 回收或重新指派 |
| Right-size over-caps | 有 limit 但 < 40% used | 下調 limit |
| Address near/over-limit | % used ≥ 80% | 確認合理性，再刻意調高或輔導 |
| Raise automation maturity | automation ratio < 20% | 推廣排程任務 |
| Divert heavy workloads | intensity 落在重 / 很重區間 | 最高價值的可避免成本，該回 Chat 或 Office app |
| Retire dormant groups | group 無活躍成員 | 清理或重新指派 |
| Rebalance tier mix | Dynamic 層佔比遠高於其工作型態應有的水準 | 將 repeatability ≥ 0.5 的工作負載做成 Custom Agent |
| Right-size Fixed seats | licence 指派 ≠ 實際活躍 | 回收閒置 seat，為搬下層者補 seat |

## Canonical output spec（兩種部署方式必須一致）

The skill (`scripts/`) and the Agent Builder variant
(`agent-builder-instructions.txt`) must produce the **same structure**. Any change
here must be applied to both.

**HTML dashboard — 版面順序（insight 在前，數字在後）**：

1. Header（標題 + 一行報告範圍）
2. **篩選列**（sticky）：授權狀態 / 分層 / 旗標 / 最低 credits / 姓名搜尋
3. **AI 最佳化建議**（全寬一張卡）：3–5 條白話分析 + TOP 5 行動
4. **KPI 卡 × 6**：`總消耗 / 活躍 / 平均 / 最大佔比 / 無上限 / 閒置授權`
5. **圖表（兩欄 grid，1fr 1fr，gap 16px，每張約 260px 高）**：
   Top Spenders（長條）/ 服務拆分（圓環）/ 額度使用率 / 授權狀態（圓環）/
   Sessions vs Credits（散布）/ 自動化拆分，之後全寬：各群組消耗、成本結構分層
6. **全寬表格**：分層分類表（含信心度）→ 使用者明細表 → 完整 IT 行動表

Flags 一律使用同一組值：`Unlimited / IdleLicence / OverLimit / NearLimit / Normal`。

> **圖表實作**：兩邊都用 **Chart.js 4（CDN）+ `<canvas>`**。檔案是下載後用瀏覽器開，
> CDN 載得到；手刻 SVG 反而會爆版。每個 canvas 設 `max-height:260px` 與
> `maintainAspectRatio:false`。
> **互動必須真的接上**：每個篩選器都要 `addEventListener`，重新篩選內嵌 JSON 後
> 呼叫單一 `render()` 同步更新 KPI、所有圖表與表格。表格一律自己寫
> `<table><tr><td>`，**不得使用 pandas `to_html`**（會產生巢狀表格而破版）。

## Report structure the script produces

**Word (.docx)** — zh-TW:
1. 封面 + 報告範圍（期間、租戶、資料來源、列數）
2. 執行摘要（開頭 3–5 條可行動的 bullet）
3. 消耗總覽（+ top 10 spenders 表）
4. 額度使用率
5. 採用與參與
6. **成本結構分層** ← 三層現況 + 分層分類表（含信心度）
7. 異常與風險
8. **IT 行動計畫** ← 重點，依優先級排序，只能落在五個槓桿
9. 附註與方法（credits-only、單期快照、缺少的資料、分層為推論需驗證）

每個章節至少 2–3 段實質分析，每條發現都要帶實際數字。

**Excel (.xlsx)**:
- `總覽` — KPI + top-spender 長條 + 服務圓餅
- `使用者` — 含重算 % used、旗標、分層
- `群組` / `服務` / `任務明細`（有資料才建）
- `分層分類` — 含信心度
- `IT 行動表` — 可篩選
