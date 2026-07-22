#!/usr/bin/env python3
"""Generate a self-contained interactive HTML FinOps dashboard.

Reuses the CSV parsing + insight logic from generate_finops_report.py, embeds
the data as `const DATA = {...}`, and renders an interactive dashboard with
slicers (licence / flag / min-credits / search) that live-filter KPIs, charts,
and the data table. Uses Chart.js (CDN) + the Clawpilot theme.

Usage:
    python3 generate_html_dashboard.py --input-dir "<csvs>" --output-dir "<out>" \
        --period "2026-07" --org "Contoso"
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_finops_report import load_csvs, compute_insights, OVER_LIMIT, NEAR_LIMIT  # noqa: E402


def build_payload(ins: dict, meta: dict) -> dict:
    users = []
    for u in ins["users"]:
        flags = []
        if u["limit"] == 0 and u["used"] > 0:
            flags.append("Unlimited")
        if u["licensed"] and u["used"] == 0 and u["sessions"] == 0:
            flags.append("IdleLicence")
        if u["pct"] is not None and u["pct"] > OVER_LIMIT:
            flags.append("OverLimit")
        elif u["pct"] is not None and u["pct"] >= NEAR_LIMIT:
            flags.append("NearLimit")
        if not flags:
            flags.append("Normal")
        users.append({
            "name": u["name"] or u["upn"],
            "upn": u["upn"],
            "limit": u["limit"],
            "used": u["used"],
            "sessions": u["sessions"],
            "licensed": u["licensed"],
            "pct": None if u["pct"] is None else round(u["pct"] * 100, 1),
            "flags": flags,
        })
    services = [{"name": s["name"], "users": s["active_users"], "used": s["used"]}
                for s in sorted(ins["services"], key=lambda x: x["used"], reverse=True)]
    groups = [{"name": g["name"], "users": g["total_users"], "used": g["used"],
               "active": g["active_members"]}
              for g in sorted(ins["groups"], key=lambda x: x["used"], reverse=True)]
    tasks = [{"upn": t["upn"], "name": t["name"] or t["upn"],
              "scheduled": int(t["scheduled"]), "manual": int(t["user_initiated"]),
              "total": int(t["total"])}
             for t in ins["tasks"]]
    from generate_finops_report import build_recommendations
    recs = build_recommendations(ins)
    return {
        "meta": meta,
        "users": users,
        "services": services,
        "groups": groups,
        "tasks": tasks,
        "recs": recs,
    }


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<script>
  (() => {
    const param = new URLSearchParams(window.location.search).get("scoutTheme");
    const theme = param || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    document.documentElement.setAttribute("data-theme", theme);
  })();
</script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
:root{
  color-scheme:light;
  --cp-bg:#f7f4ef;--cp-bg-elevated:#fcfbf8;--cp-surface:#ffffff;--cp-surface-soft:#f5f5f5;
  --cp-border:#dedede;--cp-border-strong:#919191;--cp-text:#242424;--cp-text-muted:#5c5c5c;
  --cp-text-soft:#6f6f6f;--cp-accent:#b11f4b;--cp-accent-hover:#9a1a41;--cp-accent-soft:rgba(177,31,75,.08);
  --cp-accent-fg:#ffffff;--cp-success:#16a34a;--cp-danger:#dc2626;--cp-warning:#f59e0b;--cp-link:#0078d4;
  --cp-shadow:0 18px 48px rgba(0,0,0,.12);--cp-highlight:rgba(177,31,75,.12);
}
html[data-theme="dark"]{
  color-scheme:dark;
  --cp-bg:#3d3b3a;--cp-bg-elevated:#343231;--cp-surface:#292929;--cp-surface-soft:#2e2e2e;
  --cp-border:#474747;--cp-border-strong:#5f5f5f;--cp-text:#dedede;--cp-text-muted:#919191;
  --cp-text-soft:#b0b0b0;--cp-accent:#fd8ea1;--cp-accent-hover:#fb7b91;--cp-accent-soft:rgba(253,142,161,.14);
  --cp-accent-fg:#1a1a1a;--cp-success:#4ade80;--cp-danger:#f87171;--cp-warning:#fbbf24;--cp-link:#4da6ff;
  --cp-shadow:0 18px 48px rgba(0,0,0,.32);--cp-highlight:rgba(253,142,161,.12);
}
*{box-sizing:border-box}
body{margin:0;background:var(--cp-bg);color:var(--cp-text);
  font-family:"Segoe UI",Aptos,Calibri,-apple-system,BlinkMacSystemFont,sans-serif;}
.wrap{max-width:1280px;margin:0 auto;padding:24px}
h1{font-size:22px;margin:0 0 2px}
.sub{color:var(--cp-text-muted);font-size:13px;margin-bottom:18px}
.toolbar{display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end;background:var(--cp-surface);
  border:1px solid var(--cp-border);border-radius:16px;padding:14px 16px;margin-bottom:18px;
  box-shadow:0 0 2px rgba(0,0,0,.12),0 1px 2px rgba(0,0,0,.14)}
.field{display:flex;flex-direction:column;gap:4px}
.field label{font-size:11px;color:var(--cp-text-soft);font-weight:600;text-transform:uppercase;letter-spacing:.04em}
select,input[type=search],input[type=range]{font:inherit;padding:7px 10px;border:1px solid var(--cp-border);
  border-radius:10px;background:var(--cp-bg-elevated);color:var(--cp-text);min-width:140px}
input[type=range]{padding:0;min-width:160px}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.chip{border:1px solid var(--cp-border);background:var(--cp-bg-elevated);color:var(--cp-text-muted);
  border-radius:999px;padding:6px 12px;font-size:12px;cursor:pointer;user-select:none}
.chip.active{background:var(--cp-accent);color:var(--cp-accent-fg);border-color:var(--cp-accent)}
.reset{margin-left:auto;border:1px solid var(--cp-border);background:var(--cp-bg-elevated);color:var(--cp-text);
  border-radius:10px;padding:8px 14px;cursor:pointer;font:inherit}
.reset:hover{border-color:var(--cp-accent);color:var(--cp-accent)}
.kpis{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin-bottom:18px}
.kpi{background:var(--cp-surface);border:1px solid var(--cp-border);border-radius:16px;padding:14px;
  box-shadow:0 0 2px rgba(0,0,0,.12),0 1px 2px rgba(0,0,0,.14)}
.kpi .k{font-size:11px;color:var(--cp-text-soft);font-weight:600}
.kpi .v{font-size:24px;font-weight:700;margin-top:6px}
.kpi .v.warn{color:var(--cp-warning)}.kpi .v.bad{color:var(--cp-danger)}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.card{background:var(--cp-surface);border:1px solid var(--cp-border);border-radius:16px;padding:16px;
  box-shadow:0 0 2px rgba(0,0,0,.12),0 1px 2px rgba(0,0,0,.14)}
.card h3{margin:0 0 12px;font-size:14px}
.card canvas{max-height:260px}
.full{grid-column:1/3}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{text-align:left;padding:7px 8px;border-bottom:1px solid var(--cp-border)}
th{color:var(--cp-text-soft);font-size:11px;text-transform:uppercase;letter-spacing:.03em;cursor:pointer}
tbody tr:hover{background:var(--cp-accent-soft)}
.tag{display:inline-block;font-size:11px;padding:2px 7px;border-radius:999px;margin:1px;
  background:var(--cp-surface-soft);border:1px solid var(--cp-border);color:var(--cp-text-muted)}
.tag.Unlimited{color:var(--cp-danger);border-color:var(--cp-danger)}
.tag.OverLimit{color:var(--cp-danger);border-color:var(--cp-danger)}
.tag.NearLimit{color:var(--cp-warning);border-color:var(--cp-warning)}
.tag.IdleLicence{color:var(--cp-link);border-color:var(--cp-link)}
.rec{border-left:4px solid var(--cp-border);padding:8px 12px;margin-bottom:8px;background:var(--cp-bg-elevated);border-radius:0 10px 10px 0}
.rec.High{border-left-color:var(--cp-danger)}.rec.Medium{border-left-color:var(--cp-warning)}.rec.Low{border-left-color:var(--cp-success)}
.rec b{font-size:13px}.rec p{margin:4px 0 0;font-size:12px;color:var(--cp-text-muted)}
.count{color:var(--cp-text-soft);font-size:12px;font-weight:400}
@media(max-width:900px){.kpis{grid-template-columns:repeat(2,1fr)}.grid{grid-template-columns:1fr}.full{grid-column:1}}
</style>
</head>
<body>
<div class="wrap">
  <h1>AI FinOps 儀表板 — <span id="org"></span></h1>
  <div class="sub" id="meta"></div>

  <div class="toolbar">
    <div class="field"><label>授權 Licence</label>
      <select id="fLic"><option value="all">全部</option><option value="yes">有授權</option><option value="no">無授權</option></select></div>
    <div class="field"><label>最低消耗 Min credits：<span id="minv">0</span></label>
      <input type="range" id="fMin" min="0" max="0" step="50" value="0"></div>
    <div class="field" style="flex:1;min-width:200px"><label>搜尋 Search</label>
      <input type="search" id="fSearch" placeholder="使用者 / UPN…"></div>
    <div class="field" style="width:100%"><label>旗標 Flag（切片器）</label>
      <div class="chips" id="fFlags"></div></div>
    <button class="reset" id="reset">重設 Reset</button>
  </div>

  <div class="kpis" id="kpis"></div>

  <div class="grid">
    <div class="card"><h3>🏆 Top Spenders <span class="count" id="cTop"></span></h3><canvas id="topChart"></canvas></div>
    <div class="card"><h3>🧩 服務拆分 Service split</h3><canvas id="svcChart"></canvas></div>
    <div class="card"><h3>📏 額度使用率 Utilization %</h3><canvas id="utilChart"></canvas></div>
    <div class="card"><h3>🪪 授權狀態 Licence status</h3><canvas id="licChart"></canvas></div>
    <div class="card"><h3>🔬 Sessions vs Credits</h3><canvas id="scatterChart"></canvas></div>
    <div class="card"><h3>🤖 自動化拆分 Automation</h3><canvas id="autoChart"></canvas></div>
    <div class="card full"><h3>👥 各群組消耗 Credits by group</h3><canvas id="grpChart" style="max-height:220px"></canvas></div>
    <div class="card full"><h3>📋 使用者明細 <span class="count" id="cTbl"></span></h3>
      <div style="max-height:360px;overflow:auto"><table id="tbl"></table></div></div>
    <div class="card full"><h3>💡 最佳化建議 Optimization</h3><div id="recs"></div></div>
  </div>
</div>

<script>
const DATA = /*__DATA__*/{};
const css = (n)=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const PALETTE = ()=>[css('--cp-accent'),css('--cp-link'),css('--cp-success'),css('--cp-warning'),
  css('--cp-danger'),css('--cp-text-muted'),css('--cp-border-strong'),css('--cp-accent-hover')];
const fmt=(n)=>Math.round(n).toLocaleString();
const pct=(n)=>(n*100).toFixed(1)+'%';

let state={lic:'all',min:0,search:'',flag:'all'};
const FLAGS=['all','Unlimited','IdleLicence','OverLimit','NearLimit','Normal'];
const FLAG_LABEL={all:'全部',Unlimited:'無上限',IdleLicence:'閒置授權',OverLimit:'超額',NearLimit:'接近上限',Normal:'正常'};

function filtered(){
  return DATA.users.filter(u=>{
    if(state.lic==='yes'&&!u.licensed)return false;
    if(state.lic==='no'&&u.licensed)return false;
    if(u.used<state.min)return false;
    if(state.flag!=='all'&&!u.flags.includes(state.flag))return false;
    if(state.search){const s=state.search.toLowerCase();
      if(!(u.name.toLowerCase().includes(s)||u.upn.toLowerCase().includes(s)))return false;}
    return true;
  });
}

let charts={};
function mkChart(id,cfg){charts[id]=new Chart(document.getElementById(id),cfg);}
function baseOpts(extra){return Object.assign({responsive:true,maintainAspectRatio:false,
  plugins:{legend:{labels:{color:css('--cp-text-muted'),font:{size:11}}}},
  scales:{x:{ticks:{color:css('--cp-text-muted'),font:{size:10}},grid:{color:css('--cp-border')}},
          y:{ticks:{color:css('--cp-text-muted'),font:{size:10}},grid:{color:css('--cp-border')}}}},extra||{});}

function initCharts(){
  const p=PALETTE();
  mkChart('topChart',{type:'bar',data:{labels:[],datasets:[{data:[],backgroundColor:p[0]}]},
    options:baseOpts({indexAxis:'y',plugins:{legend:{display:false}}})});
  mkChart('utilChart',{type:'bar',data:{labels:[],datasets:[{data:[],backgroundColor:p[3]}]},
    options:baseOpts({plugins:{legend:{display:false}}})});
  mkChart('scatterChart',{type:'scatter',data:{datasets:[{data:[],backgroundColor:p[2],pointRadius:5}]},
    options:baseOpts({plugins:{legend:{display:false}},scales:{x:{title:{display:true,text:'Sessions',color:css('--cp-text-soft')},ticks:{color:css('--cp-text-muted')},grid:{color:css('--cp-border')}},y:{title:{display:true,text:'Credits',color:css('--cp-text-soft')},ticks:{color:css('--cp-text-muted')},grid:{color:css('--cp-border')}}}})});
  mkChart('licChart',{type:'doughnut',data:{labels:[],datasets:[{data:[],backgroundColor:p}]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{color:css('--cp-text-muted'),font:{size:11}}}}}});
  mkChart('autoChart',{type:'bar',data:{labels:[],datasets:[
    {label:'排程 Scheduled',data:[],backgroundColor:p[2]},
    {label:'手動 Manual',data:[],backgroundColor:p[3]}]},
    options:baseOpts({scales:{x:{stacked:true,ticks:{color:css('--cp-text-muted'),font:{size:10}},grid:{color:css('--cp-border')}},y:{stacked:true,ticks:{color:css('--cp-text-muted')},grid:{color:css('--cp-border')}}}})});
  // static charts
  mkChart('svcChart',{type:'doughnut',data:{labels:DATA.services.map(s=>s.name),
    datasets:[{data:DATA.services.map(s=>s.used),backgroundColor:p}]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{color:css('--cp-text-muted'),font:{size:11}}}}}});
  mkChart('grpChart',{type:'bar',data:{labels:DATA.groups.filter(g=>g.used>0).map(g=>g.name),
    datasets:[{data:DATA.groups.filter(g=>g.used>0).map(g=>g.used),backgroundColor:p[1]}]},
    options:baseOpts({plugins:{legend:{display:false}}})});
}

function refresh(){
  const f=filtered();
  const total=f.reduce((a,u)=>a+u.used,0);
  const active=f.filter(u=>u.used>0);
  const top=[...active].sort((a,b)=>b.used-a.used);
  const share=total?top[0].used/total:0;
  const unlimited=f.filter(u=>u.flags.includes('Unlimited')).length;
  const idle=f.filter(u=>u.flags.includes('IdleLicence')).length;
  const cards=[
    ['總消耗 Total',fmt(total),''],
    ['活躍 Active',active.length+'/'+f.length,''],
    ['平均 Avg',active.length?fmt(total/active.length):'0',''],
    ['最大佔比 Top',total?pct(share):'0%',share>=0.6?'bad':''],
    ['無上限 Unlimited',unlimited,unlimited?'warn':''],
    ['閒置授權 Idle',idle,idle?'warn':''],
  ];
  document.getElementById('kpis').innerHTML=cards.map(c=>
    `<div class="kpi"><div class="k">${c[0]}</div><div class="v ${c[2]}">${c[1]}</div></div>`).join('');

  const t12=top.slice(0,12);
  charts.topChart.data.labels=t12.map(u=>u.name);
  charts.topChart.data.datasets[0].data=t12.map(u=>u.used);
  charts.topChart.update();
  document.getElementById('cTop').textContent='('+active.length+' active)';

  const util=active.filter(u=>u.pct!=null).sort((a,b)=>b.pct-a.pct).slice(0,12);
  charts.utilChart.data.labels=util.map(u=>u.name);
  charts.utilChart.data.datasets[0].data=util.map(u=>u.pct);
  charts.utilChart.update();

  charts.scatterChart.data.datasets[0].data=active.map(u=>({x:u.sessions,y:u.used}));
  charts.scatterChart.update();

  const la=f.filter(u=>u.licensed&&u.used>0).length;
  const li=f.filter(u=>u.licensed&&u.used===0&&u.sessions===0).length;
  const lu=f.filter(u=>!u.licensed).length;
  charts.licChart.data.labels=['Active licensed','Idle licensed','Unlicensed'];
  charts.licChart.data.datasets[0].data=[la,li,lu];
  charts.licChart.update();

  const upns=new Set(f.map(u=>u.upn));
  const at=DATA.tasks.filter(t=>upns.has(t.upn)).sort((a,b)=>b.total-a.total).slice(0,12);
  charts.autoChart.data.labels=at.map(t=>t.name);
  charts.autoChart.data.datasets[0].data=at.map(t=>t.scheduled);
  charts.autoChart.data.datasets[1].data=at.map(t=>t.manual);
  charts.autoChart.update();

  // table
  const rows=top.concat(f.filter(u=>u.used===0)).slice(0,200);
  document.getElementById('tbl').innerHTML=
    '<thead><tr><th>使用者</th><th>Credits</th><th>額度</th><th>% Used</th><th>Sessions</th><th>授權</th><th>Flags</th></tr></thead><tbody>'+
    rows.map(u=>`<tr><td>${u.name}</td><td>${fmt(u.used)}</td>`+
      `<td>${u.limit===0?'無上限':fmt(u.limit)}</td>`+
      `<td>${u.pct==null?'-':u.pct+'%'}</td>`+
      `<td>${fmt(u.sessions)}</td><td>${u.licensed?'Yes':'No'}</td>`+
      `<td>${u.flags.filter(x=>x!=='Normal').map(x=>`<span class="tag ${x}">${x}</span>`).join('')||'<span class="tag">—</span>'}</td></tr>`).join('')+
    '</tbody>';
  document.getElementById('cTbl').textContent='('+f.length+' 位)';
}

function initUI(){
  document.getElementById('org').textContent=DATA.meta.org;
  document.getElementById('meta').textContent=`期間 ${DATA.meta.period}｜產出 ${DATA.meta.generated}｜單位 credits`;
  const maxU=Math.max(0,...DATA.users.map(u=>u.used));
  const fMin=document.getElementById('fMin');fMin.max=Math.ceil(maxU/100)*100;
  fMin.oninput=()=>{state.min=+fMin.value;document.getElementById('minv').textContent=fmt(state.min);refresh();};
  document.getElementById('fLic').onchange=(e)=>{state.lic=e.target.value;refresh();};
  document.getElementById('fSearch').oninput=(e)=>{state.search=e.target.value;refresh();};
  const fc=document.getElementById('fFlags');
  fc.innerHTML=FLAGS.map(f=>`<span class="chip${f==='all'?' active':''}" data-f="${f}">${FLAG_LABEL[f]}</span>`).join('');
  fc.querySelectorAll('.chip').forEach(c=>c.onclick=()=>{
    state.flag=c.dataset.f;fc.querySelectorAll('.chip').forEach(x=>x.classList.remove('active'));
    c.classList.add('active');refresh();});
  document.getElementById('reset').onclick=()=>{
    state={lic:'all',min:0,search:'',flag:'all'};
    document.getElementById('fLic').value='all';document.getElementById('fSearch').value='';
    fMin.value=0;document.getElementById('minv').textContent='0';
    fc.querySelectorAll('.chip').forEach(x=>x.classList.remove('active'));
    fc.querySelector('[data-f=all]').classList.add('active');refresh();};

  document.getElementById('recs').innerHTML=DATA.recs.map(r=>
    `<div class="rec ${r.priority}"><b>[${r.priority}] ${r.theme}</b>`+
    `<p>🔍 ${r.finding}</p><p>✅ ${r.action}</p><p>📈 ${r.benefit}</p></div>`).join('')||'<p>無重大最佳化項目。</p>';
}

initUI();initCharts();refresh();
</script>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--period", default=datetime.now().strftime("%Y-%m"))
    ap.add_argument("--org", default="M365 Copilot Cowork")
    ap.add_argument("--credit-cost", type=float, default=None)
    ap.add_argument("--currency", default="USD")
    args = ap.parse_args()

    if not os.path.isdir(args.input_dir):
        print(f"ERROR: input dir not found: {args.input_dir}", file=sys.stderr)
        return 2
    os.makedirs(args.output_dir, exist_ok=True)

    data, found = load_csvs(args.input_dir)
    if not any(data.values()):
        print("ERROR: no recognizable Copilot consumption CSVs found.", file=sys.stderr)
        return 3
    ins = compute_insights(data, args.credit_cost)
    meta = {"org": args.org, "period": args.period,
            "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "currency": args.currency}
    payload = build_payload(ins, meta)

    html = HTML_TEMPLATE.replace("__TITLE__", f"AI FinOps 儀表板 — {args.org}")
    html = html.replace("/*__DATA__*/{}", json.dumps(payload, ensure_ascii=False))

    safe = args.period.replace("/", "-")
    out = os.path.join(args.output_dir, f"AI-FinOps-Dashboard_{safe}.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
