#!/usr/bin/env python3
"""Generate realistic FAKE Copilot Cowork / Neptune consumption exports.

Produces the same 4 CSV types the real admin view exports, with plausible
distributions AND deliberately seeded FinOps anomalies (whales, unlimited
accounts, idle licences, over-limit users, dormant groups) so the report and
dashboard have something interesting to show.

Usage:
    python3 make_fake_data.py --output-dir "/path/to/fake_csvs" [--users 45] [--seed 7]
"""

from __future__ import annotations

import argparse
import csv
import os
import random
import uuid
from datetime import datetime, timedelta

FIRST = ["Dennis", "Amy", "Jason", "Wei", "Ling", "Kevin", "Sophia", "Marcus",
         "Yuki", "Chen", "Priya", "Diego", "Hana", "Omar", "Nadia", "Leon",
         "Grace", "Victor", "Mei", "Ravi", "Elena", "Tom", "Ivy", "Carlos",
         "Sara", "Ken", "Lily", "Adam", "Nina", "Paul", "Rosa", "Sam",
         "Tina", "Umar", "Vera", "Will", "Xena", "Yara", "Zack", "Bella",
         "Cody", "Dana", "Ewan", "Faye", "Gino"]
LAST = ["Lee", "Wang", "Chen", "Lin", "Huang", "Wu", "Chang", "Liu", "Yang",
        "Tsai", "Nguyen", "Patel", "Kim", "Sato", "Garcia", "Silva", "Khan",
        "Ali", "Brown", "Davis", "Evans", "Ford", "Green", "Hill", "Ito",
        "Jones", "Kaur", "Lopez", "Moore", "Novak", "Ortiz", "Price", "Reed"]

GROUPS = ["MCS SG01", "Sales APAC", "Engineering", "Marketing", "IT Ops",
          "Finance", "HR", "Customer Success"]
SERVICES = ["Copilot Cowork", "Work IQ API", "Researcher Agent",
            "Analyst Agent", "Facilitator Agent"]

DOMAIN = "M365CPI99346242.onmicrosoft.com"


def rand_date(days_back_max=6) -> str:
    base = datetime(2026, 7, 20, 8, 30, 0)
    d = base - timedelta(days=random.randint(0, days_back_max),
                         hours=random.randint(0, 12),
                         minutes=random.randint(0, 59))
    return d.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--users", type=int, default=45)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    random.seed(args.seed)
    os.makedirs(args.output_dir, exist_ok=True)

    n = args.users
    users = []
    used_names = set()
    for i in range(n):
        while True:
            fn, ln = random.choice(FIRST), random.choice(LAST)
            name = f"{fn} {ln}"
            if name not in used_names:
                used_names.add(name)
                break
        upn = f"{fn.lower()}.{ln.lower()}{i}@{DOMAIN}"
        group = random.choices(GROUPS, weights=[6, 5, 5, 3, 3, 2, 2, 3])[0]

        # base persona
        roll = random.random()
        if roll < 0.10:          # whale — huge usage
            used = random.randint(4000, 9000)
        elif roll < 0.45:        # regular active
            used = random.randint(300, 2500)
        elif roll < 0.70:        # light
            used = random.randint(20, 300)
        else:                    # idle
            used = 0

        licensed = random.random() < 0.85
        # limit: some unlimited (0), some capped
        if random.random() < 0.30:
            limit = 0                      # unlimited (governance gap)
        else:
            # cap set around a plausible level; occasionally too tight or too loose
            base_cap = random.choice([1000, 2000, 3000, 5000])
            limit = base_cap
        # seed a few over-limit breaches
        if limit > 0 and random.random() < 0.12:
            used = int(limit * random.uniform(1.02, 1.4))

        sessions = 0 if used == 0 else max(1, int(used / random.uniform(60, 220)))
        last = "" if used == 0 and random.random() < 0.5 else rand_date()

        users.append({
            "Display Name": name,
            "User Principal Name": upn,
            "Monthly credit limit": limit,
            "Monthly credits used": used,
            "User ID": str(uuid.uuid4()),
            "Microsoft 365 Copilot license": "Yes" if licensed else "No",
            "Last activity date": last,
            "Session Count": sessions,
            "% Used": round(used / limit * 100, 2) if limit > 0 else 0,
            "_group": group,
        })

    # Force a clear concentration whale so the dashboard shows a Pareto tail
    users[0]["Monthly credits used"] = max(users[0]["Monthly credits used"], 12000)
    users[0]["Monthly credit limit"] = 0
    users[0]["Session Count"] = 95
    users[0]["Last activity date"] = rand_date(1)

    # --- users csv ---
    ucols = ["Display Name", "User Principal Name", "Monthly credit limit",
             "Monthly credits used", "User ID", "Microsoft 365 Copilot license",
             "Last activity date", "Session Count", "% Used"]
    with open(os.path.join(args.output_dir, "neptuneconsumptionusers_fake.csv"),
              "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=ucols)
        w.writeheader()
        for u in users:
            w.writerow({k: u[k] for k in ucols})

    # --- groups csv (rollup, incl. one dormant + the default ungrouped) ---
    gcols = ["Display Name", "Total Users", "Monthly credits used",
             "Members that used credits", "Avg credits per user per day",
             "Group ID", "Session Count", "Last activity date"]
    grows = []
    for g in GROUPS:
        members = [u for u in users if u["_group"] == g]
        if not members:
            continue
        gused = sum(u["Monthly credits used"] for u in members)
        active = sum(1 for u in members if u["Monthly credits used"] > 0)
        gsess = sum(u["Session Count"] for u in members)
        grows.append({
            "Display Name": g,
            "Total Users": len(members),
            "Monthly credits used": gused,
            "Members that used credits": active,
            "Avg credits per user per day": round(gused / max(1, len(members)) / 30, 1),
            "Group ID": str(uuid.uuid4()),
            "Session Count": gsess,
            "Last activity date": rand_date(),
        })
    # dormant group (members, zero usage)
    grows.append({
        "Display Name": "Legacy Pilot", "Total Users": 6, "Monthly credits used": 0,
        "Members that used credits": 0, "Avg credits per user per day": 0,
        "Group ID": str(uuid.uuid4()), "Session Count": 0, "Last activity date": "",
    })
    # default ungrouped bucket (all-zero id)
    ungrouped = sum(u["Monthly credits used"] for u in users) // 6
    grows.append({
        "Display Name": "", "Total Users": 0, "Monthly credits used": ungrouped,
        "Members that used credits": 1, "Avg credits per user per day": 105,
        "Group ID": "00000000-0000-0000-0000-000000000000",
        "Session Count": 22, "Last activity date": rand_date(),
    })
    with open(os.path.join(args.output_dir, "neptuneconsumptiongroups_fake.csv"),
              "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=gcols)
        w.writeheader()
        w.writerows(grows)

    # --- services csv ---
    total_used = sum(u["Monthly credits used"] for u in users)
    weights = [0.62, 0.14, 0.10, 0.09, 0.05]
    scols = ["Service Name", "Active users", "Monthly credits used", "Last activity date"]
    srows = []
    for svc, wt in zip(SERVICES, weights):
        srows.append({
            "Service Name": svc,
            "Active users": max(1, int(sum(1 for u in users if u["Monthly credits used"] > 0) * wt)),
            "Monthly credits used": int(total_used * wt),
            "Last activity date": rand_date(),
        })
    with open(os.path.join(args.output_dir, "neptuneconsumptionservices_fake.csv"),
              "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=scols)
        w.writeheader()
        w.writerows(srows)

    # --- Cowork task details csv (only active users) ---
    tcols = ["UserPrincipalName", "DisplayName", "TotalTasks", "ScheduledTasks",
             "UserInitiatedTasks", "ActiveDays", "LastActivityDate"]
    trows = []
    for u in users:
        if u["Monthly credits used"] <= 0:
            continue
        total = max(1, u["Session Count"] + random.randint(0, 20))
        # automation maturity varies; some very low (mostly manual)
        auto_ratio = random.choices([0.05, 0.2, 0.4, 0.6], weights=[4, 3, 2, 1])[0]
        scheduled = int(total * auto_ratio)
        trows.append({
            "UserPrincipalName": u["User Principal Name"],
            "DisplayName": u["Display Name"],
            "TotalTasks": total,
            "ScheduledTasks": scheduled,
            "UserInitiatedTasks": total - scheduled,
            "ActiveDays": random.randint(1, 22),
            "LastActivityDate": u["Last activity date"] or rand_date(),
        })
    with open(os.path.join(args.output_dir, "CoworkUserDetails_fake.csv"),
              "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=tcols)
        w.writeheader()
        w.writerows(trows)

    print(f"Wrote fake exports to {args.output_dir}")
    print(f"  users={n}  total_credits={total_used:,}  "
          f"top_user={users[0]['Display Name']} ({users[0]['Monthly credits used']:,})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
