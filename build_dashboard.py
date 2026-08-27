"""
build_dashboard.py  --  master data -> dashboard.html
-----------------------------------------------------
Writes a single self-contained HTML file (no internet, no dependencies) that
reads the current recall data embedded inside it. Filters, KPIs, an SVG trend
chart annotated with the policy timeline, region/hazard breakdowns, and an
expandable recall table. A "Load updated data" button lets you point it at a
fresh recalls_master.json / .csv without regenerating.

Run:  python build_dashboard.py
"""

import datetime as dt
import json
import os
import sys

import reference_data as ref

MASTER_JSON = os.path.join("data", "recalls_master.json")
OUT = "dashboard.html"


def load():
    if not os.path.exists(MASTER_JSON):
        sys.exit("Missing data/recalls_master.json. Run fetch_recalls.py first.")
    with open(MASTER_JSON, encoding="utf-8") as f:
        return json.load(f)


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>US Food Recall Monitor</title>
<style>
:root{
  --paper:#EEF1F4; --panel:#FFFFFF; --ink:#16202A; --muted:#5A6B7B;
  --line:#D6DEE5; --line2:#E7ECF1;
  --c1:#C8351F; --c2:#DE8A1E; --c3:#4A7A8C; --pha:#7A5CA6;
  --accent:#0F5C6E; --accent2:#12798f;
  --mono:ui-monospace,"Cascadia Code","Cascadia Mono",Consolas,Menlo,monospace;
  --sans:system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);
  font-size:14px;line-height:1.45;-webkit-font-smoothing:antialiased}
a{color:var(--accent)}
.wrap{max-width:1200px;margin:0 auto;padding:0 18px 64px}

/* masthead */
header.mast{border-bottom:2px solid var(--ink);padding:22px 0 14px;margin-bottom:18px}
.eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.22em;
  text-transform:uppercase;color:var(--accent);margin:0 0 6px}
h1{font-size:30px;line-height:1.02;letter-spacing:-.01em;margin:0;font-weight:800}
.status{font-family:var(--mono);font-size:12px;color:var(--muted);margin-top:8px;
  display:flex;flex-wrap:wrap;gap:6px 18px}
.status b{color:var(--ink);font-weight:600}
.sample-banner{background:#FDECEA;border:1px solid var(--c1);color:#7d1c10;
  font-family:var(--mono);font-size:12px;padding:8px 12px;border-radius:6px;
  margin-top:12px}

/* kpi readout */
.kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin:18px 0}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:8px;
  padding:12px 14px;position:relative;overflow:hidden}
.kpi .n{font-family:var(--mono);font-size:26px;font-weight:700;line-height:1}
.kpi .l{font-size:11px;color:var(--muted);text-transform:uppercase;
  letter-spacing:.08em;margin-top:6px}
.kpi.sev::before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;
  background:var(--c1)}

/* controls */
.controls{background:var(--panel);border:1px solid var(--line);border-radius:8px;
  padding:14px;display:grid;grid-template-columns:repeat(6,1fr);gap:10px;
  align-items:end;margin-bottom:18px}
.controls .full{grid-column:1/-1}
.fld{display:flex;flex-direction:column;gap:4px}
.fld label{font-size:10px;text-transform:uppercase;letter-spacing:.08em;
  color:var(--muted);font-weight:600}
select,input[type=search]{font-family:var(--sans);font-size:13px;padding:7px 8px;
  border:1px solid var(--line);border-radius:6px;background:#fff;color:var(--ink)}
select:focus,input:focus,button:focus-visible{outline:2px solid var(--accent);
  outline-offset:1px}
.btns{display:flex;gap:8px;flex-wrap:wrap}
button{font-family:var(--sans);font-size:12.5px;font-weight:600;cursor:pointer;
  border:1px solid var(--accent);background:var(--accent);color:#fff;
  padding:8px 12px;border-radius:6px}
button.ghost{background:#fff;color:var(--accent)}
button.ghost:hover{background:#eef7f9}
.toggle{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--muted)}

/* panels grid */
.grid{display:grid;grid-template-columns:1.55fr 1fr;gap:16px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:8px;
  padding:16px;min-width:0}
.panel h2{font-size:12px;text-transform:uppercase;letter-spacing:.1em;
  color:var(--muted);margin:0 0 12px;font-weight:700}
.legend{display:flex;gap:14px;flex-wrap:wrap;font-family:var(--mono);
  font-size:11px;color:var(--muted);margin-top:6px}
.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;
  margin-right:5px;vertical-align:-1px}

/* bars */
.bars{display:flex;flex-direction:column;gap:7px}
.bar-row{display:grid;grid-template-columns:120px 1fr 34px;align-items:center;gap:8px}
.bar-row .name{font-size:12px;color:var(--ink);white-space:nowrap;overflow:hidden;
  text-overflow:ellipsis}
.bar-track{background:var(--line2);border-radius:3px;height:16px;overflow:hidden}
.bar-fill{height:100%;background:var(--accent);border-radius:3px}
.stack{height:100%;display:flex;border-radius:3px;overflow:hidden}
.stack i{display:block;height:100%}
.count{font-family:var(--mono);font-size:12px;color:var(--muted);margin:0 2px 8px}
.tablefoot{display:flex;gap:8px;align-items:center;padding:12px 14px;
  border-top:1px solid var(--line2);flex-wrap:wrap}
.tablefoot:empty{display:none}
.foot-note{font-family:var(--mono);font-size:11px;color:var(--muted)}
.bar-row .v{font-family:var(--mono);font-size:12px;text-align:right;color:var(--muted)}

/* table */
.tablewrap{margin-top:16px;background:var(--panel);border:1px solid var(--line);
  border-radius:8px;overflow:hidden}
.tbl-head{display:grid;grid-template-columns:6px 92px 78px 1.4fr 1.6fr 96px 90px;
  gap:10px;padding:10px 14px;border-bottom:1px solid var(--line);
  font-size:10px;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);
  font-weight:700;cursor:default}
.tbl-head span{cursor:pointer;user-select:none}
.row{border-bottom:1px solid var(--line2)}
.row .rtop{display:grid;grid-template-columns:6px 92px 78px 1.4fr 1.6fr 96px 90px;
  gap:10px;padding:10px 14px;align-items:center;cursor:pointer}
.row:hover{background:#f7f9fb}
.spine{width:6px;height:34px;border-radius:2px;background:var(--muted)}
.chip{font-family:var(--mono);font-size:10.5px;font-weight:700;padding:2px 6px;
  border-radius:4px;text-align:center;white-space:nowrap}
.chip.fda{background:#e4f0f3;color:#0d4f5e}
.chip.usda{background:#efe9f6;color:#5a3f86}
.dt{font-family:var(--mono);font-size:11.5px;color:var(--muted)}
.firm{font-weight:600;font-size:13px;overflow:hidden;text-overflow:ellipsis;
  white-space:nowrap}
.prod{font-size:12.5px;color:var(--muted);overflow:hidden;text-overflow:ellipsis;
  white-space:nowrap}
.cls{font-family:var(--mono);font-size:11px;font-weight:700}
.reg{font-size:11.5px;color:var(--muted);white-space:nowrap;overflow:hidden;
  text-overflow:ellipsis}
.detail{padding:2px 14px 16px 30px;display:none;background:#fbfcfd}
.row.open .detail{display:block}
.detail dl{display:grid;grid-template-columns:150px 1fr;gap:4px 14px;margin:8px 0}
.detail dt{font-size:11px;text-transform:uppercase;letter-spacing:.05em;
  color:var(--muted);font-weight:700}
.detail dd{margin:0;font-size:13px}
.illness{background:#fff;border:1px solid var(--line);border-left:3px solid var(--c1);
  border-radius:6px;padding:10px 12px;margin-top:8px}
.illness .h{font-family:var(--mono);font-size:11px;text-transform:uppercase;
  letter-spacing:.08em;color:var(--c1);font-weight:700;margin-bottom:4px}
.status-pill{font-family:var(--mono);font-size:10.5px;padding:2px 7px;border-radius:10px;
  border:1px solid var(--line)}
.status-pill.on{color:#8a5a12;border-color:#e3c38a;background:#fdf6e9}
.empty{padding:40px;text-align:center;color:var(--muted)}

/* policy */
.policy{margin-top:16px}
.pol-item{display:grid;grid-template-columns:110px 1fr;gap:14px;padding:10px 0;
  border-top:1px solid var(--line2)}
.pol-date{font-family:var(--mono);font-size:12px;color:var(--accent);font-weight:700}
.pol-title{font-weight:700;font-size:13px}
.pol-sum{font-size:12.5px;color:var(--muted);margin-top:2px}
.pol-eff{font-size:12px;margin-top:4px}
.flag{display:inline-block;font-family:var(--mono);font-size:10px;font-weight:700;
  color:#8a5a12;background:#fdf6e9;border:1px solid #e3c38a;border-radius:4px;
  padding:1px 6px;margin-right:6px}
.conf{font-family:var(--mono);font-size:10.5px;color:var(--muted)}
footer{margin-top:30px;padding-top:16px;border-top:1px solid var(--line);
  font-size:12px;color:var(--muted)}
footer ul{margin:8px 0 0;padding-left:18px}

/* chart */
.trend-scroll-wrap{display:flex;align-items:flex-start}
.trend-axis{flex:0 0 auto}
.trend-scroll{overflow-x:auto;overflow-y:hidden;flex:1 1 auto;min-width:0;scrollbar-width:thin}
.trend-scroll svg{display:block}
svg text{font-family:var(--mono);font-size:10px;fill:var(--muted)}
.axis line{stroke:var(--line)}
.pol-marker{cursor:help}

@media (max-width:900px){
  .kpis{grid-template-columns:repeat(2,1fr)}
  .controls{grid-template-columns:repeat(2,1fr)}
  .grid{grid-template-columns:1fr}
  .tbl-head{display:none}
  .row .rtop{grid-template-columns:6px 1fr auto;grid-auto-rows:auto}
  .row .rtop .dt,.row .rtop .prod,.row .rtop .reg{display:none}
}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
</style>
</head>
<body>
<div class="wrap">
  <header class="mast">
    <p class="eyebrow">Food safety surveillance &middot; FDA + USDA</p>
    <h1>US Food Recall Monitor</h1>
    <div class="status">
      <span>Generated <b>__GENERATED__</b></span>
      <span>Records <b id="st-count">0</b></span>
      <span>Sources <b>openFDA Food Enforcement &middot; USDA FSIS Recall API</b></span>
    </div>
    __SAMPLE_BANNER__
  </header>

  <section class="kpis" id="kpis"></section>

  <div class="controls">
    <div class="fld"><label>Agency</label><select id="f-agency"></select></div>
    <div class="fld"><label>Region</label><select id="f-region"></select></div>
    <div class="fld"><label>Food type</label><select id="f-food"></select></div>
    <div class="fld"><label>Hazard</label><select id="f-hazard"></select></div>
    <div class="fld"><label>Class</label><select id="f-class"></select></div>
    <div class="fld"><label>Search firm/product</label>
      <input type="search" id="f-q" placeholder="e.g. cheese, Listeria"></div>
    <div class="full btns">
      <button class="ghost" id="btn-reset">Reset filters</button>
      <button class="ghost" id="btn-export">Export filtered CSV</button>
      <label class="toggle"><input type="checkbox" id="btn-sample" checked>
        Show sample rows</label>
      <span style="flex:1"></span>
      <button id="btn-load">Load updated data…</button>
      <input type="file" id="file" accept=".json,.csv" style="display:none">
    </div>
  </div>

  <div class="grid">
    <div class="panel">
      <h2>Recalls per month &middot; stacked by severity class</h2>
      <div id="trend"></div>
      <div class="legend" id="trend-legend"></div>
    </div>
    <div class="panel">
      <h2>By region <span class="conf">(distribution-based; multi-region counted each)</span></h2>
      <div class="bars" id="region-bars"></div>
      <h2 style="margin-top:18px">By hazard</h2>
      <div class="bars" id="hazard-bars"></div>
      <div class="legend" id="bars-legend" style="margin-top:12px"></div>
    </div>
  </div>

  <div class="count" id="count"></div>
  <div class="tablewrap">
    <div class="tbl-head">
      <span></span>
      <span data-sort="agency">Agency</span>
      <span data-sort="date_reported">Reported</span>
      <span data-sort="firm">Firm</span>
      <span data-sort="product_description">Product</span>
      <span data-sort="classification">Class</span>
      <span data-sort="regions">Region</span>
    </div>
    <div id="rows"></div>
    <div class="tablefoot" id="tablefoot"></div>
  </div>

  <div class="panel policy">
    <h2>Policy &amp; regulatory timeline &middot; <span class="flag">flag</span> = trend confounder</h2>
    <div id="policy"></div>
  </div>

  <footer>
    <strong>Reading the data honestly.</strong>
    <ul>
      <li>A change in recall counts is not the same as a change in food safety —
        staffing cuts or a government shutdown can lower reported recalls
        (see the timeline).</li>
      <li>Region is derived from distribution text; a recall reaching several
        regions is counted in each.</li>
      <li>Quantities are not standardized (FDA free text vs USDA pounds); the raw
        quantity is the source of truth.</li>
      <li>The hazard→illness notes are general CDC/FDA/USDA information, not
        medical advice.</li>
    </ul>
    <p>Data: openFDA Food Enforcement API (FDA-regulated foods) and USDA FSIS
      Recall API (meat, poultry, egg). Rebuild anytime with
      <code>fetch_recalls.py → build_dashboard.py</code>.</p>
  </footer>
</div>

<script>
const RECALLS = __RECALLS_JSON__;
const POLICY  = __POLICY_JSON__;
const ILLNESS = __ILLNESS_JSON__;
let DATA = RECALLS.slice();

const CLASS_ORDER = ["Class I","Class II","Class III","Public Health Alert (USDA)"];
const CLASS_COLOR = {"Class I":"#C8351F","Class II":"#DE8A1E",
  "Class III":"#4A7A8C","Public Health Alert (USDA)":"#7A5CA6"};
const REGION_ORDER = ["Northeast","Midwest","South","West","Territories","Nationwide","Unknown"];
const $ = s => document.querySelector(s);
const uniq = (arr) => [...new Set(arr.filter(Boolean))];

let sortKey="date_reported", sortDir=-1;
const PAGE=50; let shown=PAGE, tableRows=[];

function opts(sel, values, all="All"){
  sel.innerHTML = `<option value="">${all}</option>` +
    values.map(v=>`<option>${v}</option>`).join("");
}
function populate(){
  opts($("#f-agency"), uniq(DATA.map(r=>r.agency)).sort());
  opts($("#f-region"), REGION_ORDER.filter(r=>DATA.some(d=>(d.regions||"").includes(r))));
  opts($("#f-food"), uniq(DATA.map(r=>r.food_type)).sort());
  opts($("#f-hazard"), uniq(DATA.map(r=>r.hazard_category)).sort());
  opts($("#f-class"), CLASS_ORDER.filter(c=>DATA.some(d=>d.classification===c)));
}

function filtered(){
  const a=$("#f-agency").value, rg=$("#f-region").value, fd=$("#f-food").value,
    hz=$("#f-hazard").value, cl=$("#f-class").value,
    q=$("#f-q").value.trim().toLowerCase(),
    showSample=$("#btn-sample").checked;
  let rows = DATA.filter(r=>{
    if(!showSample && r.is_sample==="Yes") return false;
    if(a && r.agency!==a) return false;
    if(rg && !(r.regions||"").includes(rg)) return false;
    if(fd && r.food_type!==fd) return false;
    if(hz && r.hazard_category!==hz) return false;
    if(cl && r.classification!==cl) return false;
    if(q){
      const hay=(r.firm+" "+r.product_description+" "+r.reason+" "+r.agent).toLowerCase();
      if(!hay.includes(q)) return false;
    }
    return true;
  });
  rows.sort((x,y)=>{
    const vx=(x[sortKey]||""), vy=(y[sortKey]||"");
    return (vx<vy?-1:vx>vy?1:0)*sortDir;
  });
  return rows;
}

function kpis(rows){
  const total=rows.length;
  const c1=rows.filter(r=>r.classification==="Class I").length;
  const ongoing=rows.filter(r=>/ongoing|active|open|progress/i.test(r.status)).length;
  const fda=rows.filter(r=>r.agency==="FDA").length;
  const usda=total-fda;
  const hz={}; rows.forEach(r=>hz[r.hazard_category]=(hz[r.hazard_category]||0)+1);
  const top=Object.entries(hz).sort((a,b)=>b[1]-a[1])[0];
  const cards=[
    ["",total,"Recalls (filtered)"],
    ["sev",c1,"Class I (serious)"],
    ["",ongoing,"Ongoing / active"],
    ["",fda+" / "+usda,"FDA / USDA"],
    ["",top?top[0].replace(" (pathogen)",""):"—","Top hazard"],
  ];
  $("#kpis").innerHTML = cards.map(([c,n,l])=>
    `<div class="kpi ${c}"><div class="n">${n}</div><div class="l">${l}</div></div>`).join("");
  $("#st-count").textContent = DATA.length;
}

function monthsIn(rows){
  return uniq(rows.map(r=>r.year&&r.month?`${r.year}-${r.month}`:"")).sort();
}

function trend(rows){
  const host=$("#trend");
  const months=monthsIn(rows);
  if(!months.length){host.innerHTML='<div class="empty">No dated recalls in view.</div>';$("#trend-legend").innerHTML="";return;}
  const counts=months.map(m=>{
    const o={m}; CLASS_ORDER.forEach(c=>o[c]=0);
    rows.forEach(r=>{ if(`${r.year}-${r.month}`===m && (r.classification in o)) o[r.classification]++; });
    o.total=CLASS_ORDER.reduce((s,c)=>s+o[c],0); return o;
  });
  const maxV=Math.max(1,...counts.map(c=>c.total));
  // fixed tall height; each month gets a real column. When there are few
  // months the columns widen to fill the panel; when there are many the plot
  // grows past the panel and scrolls horizontally (y-axis stays pinned).
  const AX=46, H=320, padT=16, padB=50;
  const avail=Math.max(280,(host.clientWidth||640));
  const colW=Math.max(46, Math.floor((avail-AX-4)/months.length));
  const W=colW*months.length, plotH=H-padT-padB, bw=Math.min(30, colW*0.62);
  const x=i=>i*colW + colW/2;
  const y=v=>padT + plotH*(1 - v/maxV);
  const ticks=Math.min(maxV,5);
  let axis="";                                   // pinned y-axis (own svg)
  for(let t=0;t<=ticks;t++){const v=Math.round(maxV*t/ticks);
    axis+=`<line x1="${AX-4}" x2="${AX}" y1="${y(v)}" y2="${y(v)}" class="axis"/>`
      +`<text x="${AX-7}" y="${y(v)+3}" text-anchor="end">${v}</text>`;}
  let grid="";
  for(let t=0;t<=ticks;t++){const v=Math.round(maxV*t/ticks);
    grid+=`<line x1="0" x2="${W}" y1="${y(v)}" y2="${y(v)}" class="axis"/>`;}
  let bars="", years="", lastYear=null;
  counts.forEach((c,i)=>{
    const yr=c.m.slice(0,4);
    if(yr!==lastYear){                           // year separator + label
      const lx=x(i)-colW/2;
      years+=`<line x1="${lx}" x2="${lx}" y1="${padT}" y2="${padT+plotH+6}" stroke="#C7D0D8"/>`
        +`<text x="${lx+4}" y="${H-padB+32}" text-anchor="start" fill="#16202A" style="font-weight:600">${yr}</text>`;
      lastYear=yr;
    }
    let acc=0;
    CLASS_ORDER.forEach(cls=>{
      const v=c[cls]; if(!v) return;
      const h=plotH*v/maxV, yy=padT+plotH*(1-(acc+v)/maxV);
      bars+=`<rect x="${x(i)-bw/2}" y="${yy}" width="${bw}" height="${h}"
        fill="${CLASS_COLOR[cls]}"><title>${c.m} · ${cls}: ${v}</title></rect>`;
      acc+=v;
    });
    bars+=`<text x="${x(i)}" y="${H-padB+14}" text-anchor="middle">${c.m.slice(5)}</text>`;
    if(c.total) bars+=`<text x="${x(i)}" y="${y(c.total)-4}" text-anchor="middle" fill="#16202A">${c.total}</text>`;
  });
  let marks="";
  POLICY.forEach(p=>{
    const idx=months.indexOf((p.date||"").slice(0,7));
    if(idx>=0){const xx=x(idx);
      marks+=`<line x1="${xx}" x2="${xx}" y1="${padT}" y2="${padT+plotH}"
        stroke="#16202A" stroke-dasharray="3 3" opacity=".5"/>
        <polygon class="pol-marker" points="${xx-4},${padT} ${xx+4},${padT} ${xx},${padT+7}"
        fill="#16202A"><title>${p.date} — ${p.title}</title></polygon>`;}
  });
  host.innerHTML=`<div class="trend-scroll-wrap">`
    +`<svg class="trend-axis" width="${AX}" height="${H}" aria-hidden="true">${axis}</svg>`
    +`<div class="trend-scroll"><svg width="${W}" height="${H}" role="img"`
    +` aria-label="Recalls per month by class">${grid}${years}${bars}${marks}</svg></div></div>`;
  $("#trend-legend").innerHTML = CLASS_ORDER.map(c=>
    `<span><i style="background:${CLASS_COLOR[c]}"></i>${c}</span>`).join("")
    + `<span><i style="background:#16202A"></i>policy event</span>`
    + (W>avail-AX ? `<span style="color:#0F5C6E">scroll →</span>` : "");
}

function stackedBars(host, entries, max){
  host.innerHTML = entries.map(e=>{
    const segs = CLASS_ORDER.map(c=>{const v=e.seg[c]||0;
      return v?`<i style="width:${100*v/e.total}%;background:${CLASS_COLOR[c]}" title="${c}: ${v}"></i>`:"";}).join("");
    return `<div class="bar-row"><div class="name" title="${e.name}">${e.name}</div>`
      +`<div class="bar-track"><div class="stack" style="width:${100*e.total/max}%">${segs}</div></div>`
      +`<div class="v">${e.total}</div></div>`;
  }).join("") || '<div class="empty" style="padding:14px">None</div>';
}
function regionBars(rows){
  const m={}; REGION_ORDER.forEach(r=>m[r]={name:r,total:0,seg:{}});
  rows.forEach(r=>{const cls=r.classification;
    (r.regions||"").split(",").map(s=>s.trim()).forEach(s=>{
      if(!(s in m))return; m[s].total++; m[s].seg[cls]=(m[s].seg[cls]||0)+1;});});
  const arr=REGION_ORDER.map(r=>m[r]).filter(e=>e.total);
  stackedBars($("#region-bars"), arr, Math.max(1,...arr.map(e=>e.total)));
}
function hazardBars(rows){
  const m={}; rows.forEach(r=>{const h=r.hazard_category||"Unspecified";
    (m[h]=m[h]||{name:h,total:0,seg:{}}); m[h].total++;
    m[h].seg[r.classification]=(m[h].seg[r.classification]||0)+1;});
  const arr=Object.values(m).sort((a,b)=>b.total-a.total);
  stackedBars($("#hazard-bars"), arr, Math.max(1,...arr.map(e=>e.total)));
}

function illnessFor(r){
  return ILLNESS[r.agent] ||
    (r.hazard_category==="Undeclared allergen" ? ILLNESS["Undeclared allergen"] : null) ||
    (r.hazard_category==="Foreign material" ? ILLNESS["Foreign material"] : null);
}
function esc(s){return (s||"").replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));}

function table(){
  const rows=tableRows, host=$("#rows");
  $("#count").textContent = rows.length ?
    `Showing ${Math.min(shown,rows.length).toLocaleString()} of ${rows.length.toLocaleString()} recalls` : "";
  if(!rows.length){host.innerHTML='<div class="empty">No recalls match these filters.</div>';
    $("#tablefoot").innerHTML=""; $("#count").textContent="0 recalls"; return;}
  const slice=rows.slice(0,shown);
  host.innerHTML = slice.map((r,i)=>{
    const col=CLASS_COLOR[r.classification]||"#5A6B7B";
    const agc=r.agency==="FDA"?"fda":"usda";
    const ill=illnessFor(r);
    const ongoing=/ongoing|active|open|progress/i.test(r.status);
    const daysTxt = r.days_open!==""&&r.days_open!=null ?
      `${r.days_open} days${r.date_closed?"":" (open)"}` : "—";
    const illBlock = ill ? `<div class="illness">
        <div class="h">If ${esc(r.agent||r.hazard_category)} — what it can cause</div>
        <b>${esc(ill.illness)}.</b> ${esc(ill.symptoms)}
        <div style="margin-top:5px;color:var(--muted)">Onset ${esc(ill.onset)} ·
        Higher risk: ${esc(ill.higher_risk)}</div></div>` : "";
    return `<div class="row" data-i="${i}">
      <div class="rtop">
        <div class="spine" style="background:${col}"></div>
        <div><span class="chip ${agc}">${r.agency}</span></div>
        <div class="dt">${r.date_reported||"—"}</div>
        <div class="firm" title="${esc(r.firm)}">${esc(r.firm)||"—"}</div>
        <div class="prod" title="${esc(r.product_description)}">${esc(r.product_description)}</div>
        <div class="cls" style="color:${col}">${r.classification||"—"}</div>
        <div class="reg" title="${esc(r.regions)}">${esc(r.regions)}</div>
      </div>
      <div class="detail">
        <dl>
          <dt>Recall #</dt><dd>${esc(r.recall_number)||"—"}
            ${r.is_sample==="Yes"?'<span class="flag">sample</span>':""}</dd>
          <dt>Reason</dt><dd>${esc(r.reason)||"—"}</dd>
          <dt>Hazard</dt><dd>${esc(r.hazard_category)}${r.agent?` · ${esc(r.agent)}`:""}</dd>
          <dt>Status</dt><dd><span class="status-pill ${ongoing?"on":""}">${esc(r.status)||"—"}</span>
            &nbsp; ${daysTxt}</dd>
          <dt>Distribution</dt><dd>${esc(r.distribution_pattern)||"—"}
            ${r.nationwide==="Yes"?" · Nationwide":""}</dd>
          <dt>Quantity</dt><dd>${esc(r.quantity_raw)||"—"}</dd>
          <dt>Firm location</dt><dd>${esc([r.firm_city,r.firm_state].filter(Boolean).join(", "))||"—"}</dd>
          ${r.url?`<dt>Source</dt><dd><a href="${r.url}" target="_blank" rel="noopener">Agency recall page ↗</a></dd>`:""}
        </dl>
        ${illBlock}
      </div></div>`;
  }).join("");
  host.querySelectorAll(".row").forEach(row=>{
    row.querySelector(".rtop").addEventListener("click",()=>row.classList.toggle("open"));
  });
  const remaining=rows.length-shown;
  $("#tablefoot").innerHTML = remaining>0 ?
    `<button class="ghost" id="more-btn">Show ${Math.min(PAGE,remaining)} more</button>`
    +`<button class="ghost" id="all-btn">Show all ${rows.length.toLocaleString()}</button>`
    +`<span class="foot-note">${remaining.toLocaleString()} more below</span>` : "";
  if(remaining>0){
    $("#more-btn").onclick=()=>{shown+=PAGE; table();};
    $("#all-btn").onclick=()=>{shown=rows.length; table();};
  }
}

function policy(){
  $("#policy").innerHTML = POLICY.map(p=>{
    const conf=(p.effect_on_recalls||"").includes("CONFOUNDER");
    return `<div class="pol-item">
      <div class="pol-date">${p.date}</div>
      <div><div class="pol-title">${esc(p.title)}</div>
      <div class="pol-sum">${esc(p.summary)}</div>
      <div class="pol-eff">${conf?'<span class="flag">confounder</span>':""}${esc(p.effect_on_recalls)}</div>
      <div class="conf">confidence: ${esc(p.confidence)} · ${esc(p.source)}</div></div></div>`;
  }).join("");
}

function render(){
  const rows=filtered();
  tableRows=rows; shown=PAGE;
  kpis(rows); trend(rows); regionBars(rows); hazardBars(rows); table();
}
function drawBarsLegend(){
  $("#bars-legend").innerHTML = CLASS_ORDER.map(c=>
    `<span><i style="background:${CLASS_COLOR[c]}"></i>${c}</span>`).join("");
}

// controls
["f-agency","f-region","f-food","f-hazard","f-class"].forEach(id=>
  $("#"+id).addEventListener("change",render));
$("#f-q").addEventListener("input",render);
$("#btn-sample").addEventListener("change",render);
$("#btn-reset").addEventListener("click",()=>{
  ["f-agency","f-region","f-food","f-hazard","f-class"].forEach(id=>$("#"+id).value="");
  $("#f-q").value=""; $("#btn-sample").checked=true; render();
});
document.querySelectorAll(".tbl-head [data-sort]").forEach(h=>
  h.addEventListener("click",()=>{
    const k=h.dataset.sort; sortDir=(sortKey===k)?-sortDir:1; sortKey=k; render();
  }));
$("#btn-export").addEventListener("click",()=>{
  const rows=filtered();
  const cols=Object.keys(RECALLS[0]||{recall_id:1});
  const csv=[cols.join(",")].concat(rows.map(r=>cols.map(c=>{
    let v=(r[c]??"").toString().replace(/"/g,'""');
    return /[",\n]/.test(v)?`"${v}"`:v;
  }).join(","))).join("\n");
  const a=document.createElement("a");
  a.href=URL.createObjectURL(new Blob([csv],{type:"text/csv"}));
  a.download="recalls_filtered.csv"; a.click();
});
// load updated data
$("#btn-load").addEventListener("click",()=>$("#file").click());
$("#file").addEventListener("change",e=>{
  const f=e.target.files[0]; if(!f) return;
  const rd=new FileReader();
  rd.onload=()=>{
    try{
      let arr;
      if(f.name.endsWith(".json")) arr=JSON.parse(rd.result);
      else arr=parseCSV(rd.result);
      if(!Array.isArray(arr)||!arr.length) throw new Error("empty");
      DATA=arr; populate(); render();
      alert("Loaded "+arr.length+" records from "+f.name);
    }catch(err){alert("Could not read that file: "+err.message);}
  };
  rd.readAsText(f);
});
function parseCSV(text){
  const rows=[]; let i=0,f="",row=[],q=false;
  while(i<text.length){const c=text[i];
    if(q){ if(c==='"'){ if(text[i+1]==='"'){f+='"';i++;} else q=false;} else f+=c;}
    else{ if(c==='"')q=true; else if(c===","){row.push(f);f="";}
      else if(c==="\n"||c==="\r"){ if(f!==""||row.length){row.push(f);f="";
        rows.push(row);row=[];} if(c==="\r"&&text[i+1]==="\n")i++;}
      else f+=c;}
    i++;}
  if(f!==""||row.length){row.push(f);rows.push(row);}
  const head=rows.shift(); return rows.map(r=>Object.fromEntries(head.map((h,j)=>[h,r[j]??""])));
}

populate(); policy(); drawBarsLegend(); render();
</script>
</body>
</html>"""


def main():
    rows = load()
    illness = {r["agent"]: r for r in ref.HAZARD_ILLNESS}
    has_sample = any(r.get("is_sample") == "Yes" for r in rows)
    banner = ("" if not has_sample else
              '<div class="sample-banner">⚠ Showing SAMPLE data so you can see '
              'the layout. Run <code>fetch_recalls.py</code> (without --sample) '
              'for live FDA + USDA records, then <code>build_dashboard.py</code>.'
              '</div>')
    html = (TEMPLATE
            .replace("__RECALLS_JSON__", json.dumps(rows, ensure_ascii=False))
            .replace("__POLICY_JSON__", json.dumps(ref.POLICY_TIMELINE, ensure_ascii=False))
            .replace("__ILLNESS_JSON__", json.dumps(illness, ensure_ascii=False))
            .replace("__GENERATED__", dt.date.today().isoformat())
            .replace("__SAMPLE_BANNER__", banner))
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {OUT}  ({len(rows)} recalls embedded)")


if __name__ == "__main__":
    main()
