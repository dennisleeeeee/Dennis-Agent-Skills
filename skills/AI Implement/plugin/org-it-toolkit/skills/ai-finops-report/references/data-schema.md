# AI FinOps — CSV export schema

The M365 Copilot Cowork / Neptune cost-management admin view exports up to four
CSV types. The generator auto-detects each file by its **header signature**, so
the download filename/suffix is irrelevant. Any subset works; missing types are
skipped.

## 1. Users — `neptuneconsumptionusers*.csv`

Per-user credit consumption. **Header signature:** contains `User Principal Name`
+ `Monthly credit limit`.

| Column | Meaning | Used for |
|---|---|---|
| `Display Name` | User display name | labels |
| `User Principal Name` | UPN (unique key) | join key |
| `Monthly credit limit` | Credit cap; **0 = no limit (unlimited)** | governance / right-sizing |
| `Monthly credits used` | Credits consumed this period | core spend metric |
| `User ID` | AAD object id | join key |
| `Microsoft 365 Copilot license` | `Yes`/`No` | licence-waste detection |
| `Last activity date` | Last activity timestamp | inactivity detection |
| `Session Count` | Sessions this period | engagement |
| `% Used` | limit utilization (0 when limit=0) | recomputed by the script when limit>0 |

## 2. Groups — `neptuneconsumptiongroups*.csv`

Per-group rollup. **Header signature:** contains `Group ID`.

| Column | Meaning |
|---|---|
| `Display Name` | Group name (blank + all-zero `Group ID` = ungrouped/default) |
| `Total Users` | Members in group |
| `Monthly credits used` | Group total credits |
| `Members that used credits` | Active members |
| `Avg credits per user per day` | Intensity |
| `Group ID` | Group object id |
| `Session Count` | Sessions |
| `Last activity date` | Last activity |

## 3. Services — `neptuneconsumptionservices*.csv`

Per-service split. **Header signature:** contains `Service Name`.

| Column | Meaning |
|---|---|
| `Service Name` | e.g. `Copilot Cowork`, `Work IQ API` |
| `Active users` | Distinct users |
| `Monthly credits used` | Service total credits |
| `Last activity date` | Last activity |

## 4. Cowork task details — `CoworkUserDetails*.csv`

Per-user task/automation breakdown. **Header signature:** contains `TotalTasks`.

| Column | Meaning | Used for |
|---|---|---|
| `UserPrincipalName` | UPN (join key) | join |
| `DisplayName` | User display name | labels |
| `TotalTasks` | All tasks | adoption |
| `ScheduledTasks` | Automated/scheduled tasks | automation-maturity ratio |
| `UserInitiatedTasks` | Manual tasks | automation-maturity ratio |
| `ActiveDays` | Days active | engagement |
| `LastActivityDate` | Last activity | inactivity |

## Notes on data quirks

- Numeric fields may contain thousands separators (`8,264`) — the parser strips them.
- Timestamps are ISO 8601 (`2026-07-20T08:30:55.777`); only the date is shown.
- `Monthly credit limit = 0` means **unlimited**, NOT "zero budget" → flagged as a
  governance gap, not as a maxed-out user.
- `% Used` in the raw file is 0 whenever the limit is 0; the script recomputes real
  utilization only where a positive limit exists.
