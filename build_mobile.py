"""
build_mobile.py  --  self-updating iPhone dashboard (option 2)
--------------------------------------------------------------
Writes recall_monitor_mobile.html: a single self-contained page that fetches
FDA (openFDA) and USDA (FSIS) recalls DIRECTLY in the browser — no Python, no
computer needed to refresh. Add it to the iPhone home screen and tap Refresh.

Design notes
  * FDA openFDA is built for browser use and allows cross-origin requests, so
    live fetch works. USDA FSIS may block cross-origin browser requests (CORS);
    if it does, the app keeps FDA live, shows a clear note, and lets you load
    USDA from a file. It never just breaks.
  * Ships with the labeled sample as an offline fallback, so it is never empty.
  * The region / food-type / hazard logic from reference_data.py is ported to
    JavaScript here so live records get the same treatment as the desktop tool.

Run once to (re)generate the file:  python build_mobile.py
After that the .html is standalone. Best hosted at a URL (GitHub Pages / Netlify)
so live fetch + "Add to Home Screen" work cleanly; opening the local file works
for a quick look too.
"""

import base64
import io
import json
import os
import sys

import reference_data as ref

OUT = "recall_monitor_mobile.html"
SAMPLE_JSON = os.path.join("data", "recalls_master.json")


def make_icon():
    """A small app icon: slate tile, teal magnifier lens, red severity spine."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return ""
    S = 512
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, S, S], radius=112, fill=(22, 32, 42, 255))   # slate
    d.rounded_rectangle([70, 60, 120, S - 60], radius=22, fill=(200, 53, 31, 255))  # red spine
    # magnifier lens
    cx, cy, r = 300, 232, 120
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255, 255), width=34)
    d.line([cx + r - 24, cy + r - 24, 430, 372], fill=(255, 255, 255, 255), width=40)
    # teal check inside lens
    d.line([cx - 52, cy + 6, cx - 14, cy + 46], fill=(18, 121, 143, 255), width=30)
    d.line([cx - 14, cy + 46, cx + 60, cy - 44], fill=(18, 121, 143, 255), width=30)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def load_sample():
    if os.path.exists(SAMPLE_JSON):
        with open(SAMPLE_JSON, encoding="utf-8") as f:
            return json.load(f)
    return []


# The JS port of the classifiers lives in the template as a static block so the
# app can enrich LIVE API records client-side. Data tables come from Python.
JS_REF = {
    "REGION_OF": ref.REGION_OF,
    "STATE_ABBR": ref.STATE_ABBR,
    "FOOD_TYPE_RULES": ref.FOOD_TYPE_RULES,
    "PATHOGENS": ref.PATHOGENS,
    "ALLERGENS": ref.ALLERGENS,
}

TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Recall Monitor</title>
<meta name="theme-color" content="#16202A">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Recalls">
<link rel="apple-touch-icon" href="__ICON__">
<link rel="icon" href="__ICON__">
<link rel="manifest" href='data:application/json,{"name":"US Food Recall Monitor","short_name":"Recalls","display":"standalone","background_color":"%23EEF1F4","theme_color":"%2316202A","icons":[{"src":"__ICON__","sizes":"512x512","type":"image/png"}]}'>
<style>
:root{
  --paper:#EEF1F4;--panel:#FFF;--ink:#16202A;--muted:#5A6B7B;--line:#D6DEE5;
  --line2:#E7ECF1;--c1:#C8351F;--c2:#DE8A1E;--c3:#4A7A8C;--pha:#7A5CA6;
  --accent:#0F5C6E;--ok:#1c7d53;--warn:#8a5a12;
  --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
  --sans:-apple-system,system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);
  font-size:15px;line-height:1.45;-webkit-text-size-adjust:100%;
  padding:env(safe-area-inset-top) env(safe-area-inset-right) 0 env(safe-area-inset-left)}
.wrap{max-width:760px;margin:0 auto;padding:0 14px 72px}
a{color:var(--accent)}

header.mast{padding:16px 0 12px;border-bottom:2px solid var(--ink);margin-bottom:14px}
.eyebrow{font-family:var(--mono);font-size:10.5px;letter-spacing:.2em;
  text-transform:uppercase;color:var(--accent);margin:0 0 5px}
h1{font-size:24px;line-height:1.05;margin:0;font-weight:800;letter-spacing:-.01em}
.srcline{display:flex;flex-wrap:wrap;gap:6px 10px;margin-top:10px;align-items:center}
.pill{font-family:var(--mono);font-size:11px;padding:3px 8px;border-radius:20px;
  border:1px solid var(--line);color:var(--muted);white-space:nowrap}
.pill.live{color:var(--ok);border-color:#accdb9;background:#eef7f1}
.pill.warnp{color:var(--warn);border-color:#e3c38a;background:#fdf6e9}
.pill.sample{color:#7d1c10;border-color:#e6a79c;background:#fdecea}
.updated{font-family:var(--mono);font-size:11px;color:var(--muted);margin-left:auto}

.banner{border-radius:8px;padding:9px 12px;font-size:12.5px;margin-bottom:12px;display:none}
.banner.show{display:block}
.banner.warn{background:#fdf6e9;border:1px solid #e3c38a;color:#6b4708}
.banner.sample{background:#fdecea;border:1px solid var(--c1);color:#7d1c10}

.controls{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px;align-items:center}
.controls .grow{flex:1 1 100%}
button{font-family:var(--sans);font-size:14px;font-weight:600;cursor:pointer;
  border:1px solid var(--accent);background:var(--accent);color:#fff;
  padding:10px 14px;border-radius:9px;min-height:44px}
button.ghost{background:#fff;color:var(--accent)}
button:active{transform:translateY(1px)}
select,input[type=search]{font-family:var(--sans);font-size:15px;padding:9px 10px;
  border:1px solid var(--line);border-radius:9px;background:#fff;color:var(--ink);
  min-height:44px;width:100%}
input:focus,select:focus,button:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
.filt-toggle{background:#fff;color:var(--ink);border:1px solid var(--line)}
.filters{display:none;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px}
.filters.open{display:grid}
.filters .full{grid-column:1/-1}
.fld{display:flex;flex-direction:column;gap:3px}
.fld label{font-size:10px;text-transform:uppercase;letter-spacing:.07em;
  color:var(--muted);font-weight:700}
.rowbtns{display:flex;gap:8px;flex-wrap:wrap}
.toggle{display:flex;align-items:center;gap:7px;font-size:13px;color:var(--muted);
  min-height:44px}
.toggle input{width:20px;height:20px}

.kpis{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:10px;
  padding:11px 13px;position:relative;overflow:hidden}
.kpi .n{font-family:var(--mono);font-size:23px;font-weight:700;line-height:1}
.kpi .l{font-size:11px;color:var(--muted);text-transform:uppercase;
  letter-spacing:.06em;margin-top:5px}
.kpi.sev::before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--c1)}

.panel{background:var(--panel);border:1px solid var(--line);border-radius:10px;
  padding:14px;margin-bottom:14px;min-width:0}
.panel h2{font-size:11.5px;text-transform:uppercase;letter-spacing:.08em;
  color:var(--muted);margin:0 0 10px;font-weight:700}
.legend{display:flex;gap:12px;flex-wrap:wrap;font-family:var(--mono);font-size:10.5px;
  color:var(--muted);margin-top:8px}
.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:4px}
.bars{display:flex;flex-direction:column;gap:7px}
.bar-row{display:grid;grid-template-columns:96px 1fr 30px;align-items:center;gap:8px}
.bar-row .name{font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar-track{background:var(--line2);border-radius:3px;height:15px;overflow:hidden}
.stack{height:100%;display:flex;border-radius:3px;overflow:hidden}
.stack i{display:block;height:100%}
.tablefoot{display:flex;gap:8px;align-items:center;padding:12px;border-top:1px solid var(--line2);flex-wrap:wrap}
.tablefoot:empty{display:none}
.bar-fill{height:100%;background:var(--accent);border-radius:3px}
.bar-row .v{font-family:var(--mono);font-size:12px;text-align:right;color:var(--muted)}

.tablewrap{background:var(--panel);border:1px solid var(--line);border-radius:10px;
  overflow:hidden;margin-bottom:14px}
.rowc{border-bottom:1px solid var(--line2)}
.rtop{display:grid;grid-template-columns:6px 1fr auto;gap:10px;padding:11px 12px;
  align-items:center;cursor:pointer}
.rowc:active{background:#f5f8fa}
.spine{width:6px;height:38px;border-radius:2px;background:var(--muted)}
.rmid{min-width:0}
.rmeta{font-family:var(--mono);font-size:10.5px;color:var(--muted);
  display:flex;gap:8px;margin-bottom:2px}
.chip{font-weight:700;padding:1px 5px;border-radius:4px}
.chip.fda{background:#e4f0f3;color:#0d4f5e}.chip.usda{background:#efe9f6;color:#5a3f86}
.firm{font-weight:700;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.prod{font-size:12.5px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.cls{font-family:var(--mono);font-size:10.5px;font-weight:700;text-align:right;white-space:nowrap}
.detail{display:none;padding:0 12px 14px 28px;background:#fbfcfd}
.rowc.open .detail{display:block}
.detail dl{display:grid;grid-template-columns:104px 1fr;gap:4px 10px;margin:8px 0}
.detail dt{font-size:10.5px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);font-weight:700}
.detail dd{margin:0;font-size:13.5px}
.illness{background:#fff;border:1px solid var(--line);border-left:3px solid var(--c1);
  border-radius:8px;padding:9px 11px;margin-top:8px}
.illness .h{font-family:var(--mono);font-size:10.5px;text-transform:uppercase;
  letter-spacing:.06em;color:var(--c1);font-weight:700;margin-bottom:3px}
.spill{font-family:var(--mono);font-size:10px;padding:2px 7px;border-radius:10px;
  border:1px solid var(--line)}
.spill.on{color:#8a5a12;border-color:#e3c38a;background:#fdf6e9}
.empty{padding:34px 14px;text-align:center;color:var(--muted)}
.count{font-family:var(--mono);font-size:11px;color:var(--muted);margin:2px 2px 8px}

svg text{font-family:var(--mono);font-size:10px;fill:var(--muted)}
.axis line{stroke:var(--line)}
.trend-scroll-wrap{display:flex;align-items:flex-start}
.trend-axis{flex:0 0 auto}
.trend-scroll{overflow-x:auto;overflow-y:hidden;flex:1 1 auto;min-width:0;
  -webkit-overflow-scrolling:touch;scrollbar-width:thin}
.trend-scroll svg{display:block}

.pol-item{display:grid;grid-template-columns:92px 1fr;gap:10px;padding:9px 0;border-top:1px solid var(--line2)}
.pol-date{font-family:var(--mono);font-size:11.5px;color:var(--accent);font-weight:700}
.pol-title{font-weight:700;font-size:13px}
.pol-sum{font-size:12px;color:var(--muted);margin-top:2px}
.pol-eff{font-size:12px;margin-top:3px}
.flag{display:inline-block;font-family:var(--mono);font-size:9.5px;font-weight:700;
  color:#8a5a12;background:#fdf6e9;border:1px solid #e3c38a;border-radius:4px;padding:1px 5px;margin-right:5px}
.conf{font-family:var(--mono);font-size:10px;color:var(--muted);margin-top:2px}

.a2hs{display:none;background:#fff;border:1px dashed var(--accent);border-radius:9px;
  padding:9px 12px;font-size:12.5px;color:var(--accent);margin-bottom:14px}
.a2hs.show{display:block}
footer{margin-top:20px;padding-top:14px;border-top:1px solid var(--line);font-size:12px;color:var(--muted)}
footer ul{margin:8px 0 0;padding-left:18px}
@media(min-width:560px){.kpis{grid-template-columns:repeat(4,1fr)}.filters{grid-template-columns:repeat(3,1fr)}}
@media(prefers-reduced-motion:reduce){button:active{transform:none}}
</style>
</head>
<body>
<div class="wrap">
  <header class="mast">
    <p class="eyebrow">Food safety surveillance &middot; FDA + USDA</p>
    <h1>US Food Recall Monitor</h1>
    <div class="srcline" id="srcline">
      <span class="pill" id="pill-fda">FDA —</span>
      <span class="pill" id="pill-usda">USDA —</span>
      <span class="updated" id="updated"></span>
    </div>
  </header>

  <div class="a2hs" id="a2hs">Tip: tap <b>Share → Add to Home Screen</b> to keep this as an app that refreshes on open.</div>
  <div class="banner" id="banner"></div>

  <div class="controls">
    <button id="btn-refresh">↻ Refresh live data</button>
    <div class="fld" style="width:120px"><label>Year</label><select id="year"></select></div>
    <button class="filt-toggle" id="btn-filters">Filters</button>
  </div>

  <div class="filters" id="filters">
    <div class="fld full"><label>Search firm / product</label>
      <input type="search" id="f-q" placeholder="e.g. cheese, Listeria"></div>
    <div class="fld"><label>Agency</label><select id="f-agency"></select></div>
    <div class="fld"><label>Region</label><select id="f-region"></select></div>
    <div class="fld"><label>Food type</label><select id="f-food"></select></div>
    <div class="fld"><label>Hazard</label><select id="f-hazard"></select></div>
    <div class="fld"><label>Class</label><select id="f-class"></select></div>
    <div class="full rowbtns">
      <button class="ghost" id="btn-reset">Reset</button>
      <button class="ghost" id="btn-export">Export CSV</button>
      <button class="ghost" id="btn-load">Load file…</button>
      <input type="file" id="file" accept=".json,.csv" style="display:none">
      <label class="toggle"><input type="checkbox" id="btn-sample" checked> Show sample rows</label>
    </div>
  </div>

  <section class="kpis" id="kpis"></section>

  <div class="panel">
    <h2>Recalls per month &middot; by severity class</h2>
    <div id="trend"></div>
    <div class="legend" id="trend-legend"></div>
  </div>
  <div class="panel">
    <h2>By region <span class="conf" style="text-transform:none">(where distributed; multi-region counted each)</span></h2>
    <div class="bars" id="region-bars"></div>
    <h2 style="margin-top:16px">By hazard</h2>
    <div class="bars" id="hazard-bars"></div>
    <div class="legend" id="bars-legend" style="margin-top:10px"></div>
  </div>

  <div class="count" id="count"></div>
  <div class="tablewrap"><div id="rows"></div><div class="tablefoot" id="tablefoot"></div></div>

  <div class="panel">
    <h2>Policy &amp; regulatory timeline &middot; <span class="flag">flag</span> = trend confounder</h2>
    <div id="policy"></div>
  </div>

  <footer>
    <strong>Reading the data honestly.</strong>
    <ul>
      <li>A change in recall counts is not the same as a change in food safety —
        staffing cuts or a shutdown can lower reported recalls (see timeline).</li>
      <li>Region is derived from distribution text; multi-region recalls count in each.</li>
      <li>Quantities aren't standardized across agencies; the raw quantity is the source of truth.</li>
      <li>Hazard→illness notes are general CDC/FDA/USDA info, not medical advice.</li>
    </ul>
    <p>Live sources: openFDA Food Enforcement API &middot; USDA FSIS Recall API.</p>
  </footer>
</div>

<script>
const SAMPLE  = __SAMPLE_JSON__;
const POLICY  = __POLICY_JSON__;
const ILLNESS = __ILLNESS_JSON__;
const REGION_OF = __REGION_OF__;
const STATE_ABBR = __STATE_ABBR__;
const FOOD_RULES = __FOOD_RULES__;
const PATHOGENS = __PATHOGENS__;
const ALLERGENS = __ALLERGENS__;

const CLASS_ORDER=["Class I","Class II","Class III","Public Health Alert (USDA)"];
const CLASS_COLOR={"Class I":"#C8351F","Class II":"#DE8A1E","Class III":"#4A7A8C","Public Health Alert (USDA)":"#7A5CA6"};
const REGION_ORDER=["Northeast","Midwest","South","West","Territories","Nationwide","Unknown"];
const ABBR_SET=new Set(Object.values(STATE_ABBR));
const $=s=>document.querySelector(s), uniq=a=>[...new Set(a.filter(Boolean))];
let DATA=SAMPLE.slice(), sortKey="date_reported", sortDir=-1;
const PAGE=50; let shown=PAGE, tableRows=[];

/* ---------- ported classifiers (mirror reference_data.py) ---------- */
function parseStates(text){
  if(!text) return [new Set(),false];
  const low=text.toLowerCase();
  const nation=["nationwide","nation wide","national distribution",
    "throughout the united states","all 50 states","throughout the u.s","throughout the us"]
    .some(k=>low.includes(k));
  const found=new Set();
  for(const name in STATE_ABBR){ if(low.includes(name)) found.add(STATE_ABBR[name]); }
  (text.match(/\b[A-Z]{2}\b/g)||[]).forEach(t=>{ if(ABBR_SET.has(t)) found.add(t); });
  return [found,nation];
}
function regionsFor(states,nation){
  if(nation) return ["Nationwide"];
  const r=[...new Set([...states].map(s=>REGION_OF[s]||"Unknown"))].sort();
  return r.length?r:["Unknown"];
}
function categorizeFood(desc){
  if(!desc) return "Uncategorized";
  const low=desc.toLowerCase();
  for(const [label,keys] of FOOD_RULES){ if(keys.some(k=>low.includes(k))) return label; }
  return "Other / Multiple";
}
function classifyHazard(reason){
  if(!reason) return ["Unspecified",""];
  const low=reason.toLowerCase();
  for(const agent in PATHOGENS){ if(PATHOGENS[agent].some(k=>low.includes(k))) return ["Biological (pathogen)",agent]; }
  if(low.includes("allerg")||low.includes("undeclared")||low.includes("unreported")||low.includes("misbrand")){
    for(const a of ALLERGENS){ if(low.includes(a)) return ["Undeclared allergen",a.replace(/\b\w/,c=>c.toUpperCase())]; }
    if(low.includes("allerg")) return ["Undeclared allergen","Unspecified allergen"];
  }
  if(["foreign material","foreign matter","metal","plastic","glass","wood","rubber","bone","extraneous"].some(k=>low.includes(k))) return ["Foreign material",""];
  if(["chemical","benzene","lead","arsenic","cadmium","heavy metal","pesticide","toxin","aflatoxin","cleaning","sanitizer","melamine","pfas"].some(k=>low.includes(k))) return ["Chemical / contaminant",""];
  if(["without benefit of inspection","without the benefit of inspection","not presented for import","import violation","underprocess","undercook","temperature abuse","insanitary","unsanitary","adulterat"].some(k=>low.includes(k))) return ["Processing / production",""];
  if(["mislabel","label","spoil","mold","off-odor","quality","expired","date","packaging"].some(k=>low.includes(k))) return ["Labeling / quality",""];
  return ["Other / Unspecified",""];
}
const QUNITS=/([\d][\d,\.]*)\s*(lb|lbs|pound|pounds|case|cases|unit|units|bottle|bottles|bag|bags|box|boxes|carton|cartons|container|containers|jar|jars|package|packages|can|cans|oz|ounce|ounces|kg|count|pouch|pouches|tray|trays)\b/i;
function parseQty(){ for(const t of arguments){ if(!t) continue; const m=(""+t).match(QUNITS);
  if(m){let u=m[2].toLowerCase(); u=({lb:"lbs",pound:"lbs",pounds:"lbs"})[u]||u; return [m[1].replace(/,/g,""),u];}} return ["",""]; }
function iso(s){ if(!s) return ""; s=(""+s).trim();
  if(/^\d{8}$/.test(s)) return s.slice(0,4)+"-"+s.slice(4,6)+"-"+s.slice(6,8);
  const m=s.match(/(\d{4})-(\d{2})-(\d{2})/); return m?m[0]:""; }
function daysBetween(a,b){ if(!a||!b) return ""; const d=(new Date(b)-new Date(a))/86400000; return isFinite(d)?Math.round(d):""; }
function enrich(r){
  const [states,nation]=parseStates(r.distribution_pattern||"");
  r.distribution_states=[...states].sort().join(", ");
  r.nationwide=nation?"Yes":"No";
  r.regions=regionsFor(states,nation).join(", ");
  r.food_type=categorizeFood(r.product_description||"");
  const [cat,agent]=classifyHazard(r.reason||"");
  r.hazard_category=cat; r.agent=agent;
  const ref=r.date_closed||new Date().toISOString().slice(0,10);
  r.days_open=r.date_initiated?daysBetween(r.date_initiated,ref):"";
  const basis=r.date_reported||r.date_initiated||"";
  r.year=basis.slice(0,4); r.month=basis.slice(5,7);
  const [qv,qu]=parseQty(r.quantity_raw); r.quantity_value=qv; r.quantity_unit=qu;
  return r;
}

/* ---------- live fetch ---------- */
async function tfetch(url,ms){ ms=ms||15000;
  const ctl=new AbortController(), t=setTimeout(()=>ctl.abort(),ms);
  try{ return await fetch(url,{signal:ctl.signal}); }
  finally{ clearTimeout(t); }
}
function normFDA(r){
  return enrich({
    agency:"FDA", recall_number:r.recall_number||"", event_id:r.event_id||"",
    firm:r.recalling_firm||"", firm_city:r.city||"", firm_state:r.state||"",
    product_description:(r.product_description||"").slice(0,500),
    reason:r.reason_for_recall||"", classification:r.classification||"",
    status:r.status||"", distribution_pattern:r.distribution_pattern||"",
    quantity_raw:r.product_quantity||"",
    date_initiated:iso(r.recall_initiation_date), date_reported:iso(r.report_date),
    date_closed:iso(r.termination_date), voluntary_mandated:r.voluntary_mandated||"",
    url:"https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts",
    is_sample:"No",
    recall_id:"FDA:"+(r.recall_number||r.event_id||Math.random())
  });
}
function fsisClass(rk){ if(!rk) return ""; const m=(""+rk).match(/Class\s+I{1,3}/);
  if(m) return m[0]; if((""+rk).toLowerCase().includes("alert")) return "Public Health Alert (USDA)"; return rk; }
function normFSIS(r){
  const num=(r.field_recall_number||"").trim();
  const reason=(r.field_recall_reason||r.field_summary||"").replace(/\s+/g," ").trim();
  const prod=(r.field_product_items||r.field_title||"").replace(/\s+/g," ").trim();
  const rec=enrich({
    agency:"USDA-FSIS", recall_number:num, event_id:"",
    firm:(r.field_establishment||"").replace(/\s+/g," ").trim(), firm_city:"", firm_state:"",
    product_description:prod.slice(0,500), reason:reason,
    classification:fsisClass(r.field_risk_level),
    status:(""+r.field_active_notice).toLowerCase()==="true"?"Active":"Closed",
    distribution_pattern:(r.field_states||"").replace(/\s+/g," ").trim(),
    quantity_raw:(r.field_summary||"").replace(/\s+/g," ").trim().slice(0,300),
    date_initiated:iso(r.field_recall_date||r.field_last_modified_date),
    date_reported:iso(r.field_recall_date||r.field_last_modified_date),
    date_closed:iso(r.field_closed_date), voluntary_mandated:"",
    url:"https://www.fsis.usda.gov/recalls", is_sample:"No",
    recall_id:"USDA:"+(num||prod.slice(0,24))
  });
  const [qv,qu]=parseQty(r.field_summary,prod,r.field_title); rec.quantity_value=qv; rec.quantity_unit=qu;
  return rec;
}
async function fetchFDA(year){
  let out=[], skip=0;
  for(let page=0; page<5; page++){
    const url=`https://api.fda.gov/food/enforcement.json?search=report_date:[${year}0101+TO+${year}1231]&limit=1000&skip=${skip}`;
    const res=await tfetch(url);
    if(res.status===404) break;
    if(!res.ok) throw new Error("FDA HTTP "+res.status);
    const j=await res.json(); const results=j.results||[];
    if(!results.length) break;
    out=out.concat(results.map(normFDA)); skip+=results.length;
    if(results.length<1000) break;
  }
  return out;
}
async function fetchFSIS(year){
  const res=await tfetch("https://www.fsis.usda.gov/fsis/api/recall/v/1");
  if(!res.ok) throw new Error("FSIS HTTP "+res.status);
  let data=await res.json(); if(data&&data.results) data=data.results;
  return (data||[]).filter(r=>{
    const num=(""+(r.field_recall_number||"")); const suff=num.includes("-")?num.split("-").pop():"";
    return String(year)===String(r.field_year)||String(year)===suff;
  }).map(normFSIS);
}
function setPill(id,cls,txt){ const el=$(id); el.className="pill "+cls; el.textContent=txt; }
function banner(kind,html){ const b=$("#banner"); if(!kind){b.className="banner";b.innerHTML="";return;}
  b.className="banner show "+kind; b.innerHTML=html; }

async function refresh(){
  const year=$("#year").value;
  setPill("#pill-fda","","FDA …"); setPill("#pill-usda","","USDA …");
  $("#btn-refresh").disabled=true;
  const [fda,usda]=await Promise.allSettled([fetchFDA(year),fetchFSIS(year)]);
  let live=[], notes=[];
  if(fda.status==="fulfilled"){ live=live.concat(fda.value);
    setPill("#pill-fda","live",`FDA ● ${fda.value.length}`); }
  else { setPill("#pill-fda","warnp","FDA ▲ blocked");
    notes.push("FDA live fetch failed ("+(fda.reason&&fda.reason.message||"network/CORS")+")."); }
  if(usda.status==="fulfilled"){ live=live.concat(usda.value);
    setPill("#pill-usda","live",`USDA ● ${usda.value.length}`); }
  else { setPill("#pill-usda","warnp","USDA ▲ blocked");
    notes.push("USDA doesn't allow in-browser fetch here — use <b>Load file…</b> with a USDA CSV/JSON, or refresh USDA from the desktop tool."); }

  if(live.length){
    const m=new Map(); live.forEach(r=>m.set(r.recall_id,r)); DATA=[...m.values()];
    $("#btn-sample").checked=false;
    $("#updated").textContent="updated "+new Date().toLocaleString();
    if(notes.length) banner("warn",notes.join(" ")); else banner();
  } else {
    setPill("#pill-fda","sample","FDA — sample"); setPill("#pill-usda","sample","USDA — sample");
    banner("sample","Couldn't reach the live APIs from this browser, so this is <b>sample</b> data. "
      +"This is expected if you opened the file locally — host it at a URL (or add to Home Screen) and tap Refresh. "
      +notes.join(" "));
  }
  $("#btn-refresh").disabled=false;
  populate(); render();
}

/* ---------- filtering + views (shared with desktop) ---------- */
function opts(sel,vals,all="All"){ sel.innerHTML=`<option value="">${all}</option>`+vals.map(v=>`<option>${v}</option>`).join(""); }
function populate(){
  opts($("#f-agency"),uniq(DATA.map(r=>r.agency)).sort());
  opts($("#f-region"),REGION_ORDER.filter(r=>DATA.some(d=>(d.regions||"").includes(r))));
  opts($("#f-food"),uniq(DATA.map(r=>r.food_type)).sort());
  opts($("#f-hazard"),uniq(DATA.map(r=>r.hazard_category)).sort());
  opts($("#f-class"),CLASS_ORDER.filter(c=>DATA.some(d=>d.classification===c)));
}
function filtered(){
  const a=$("#f-agency").value,rg=$("#f-region").value,fd=$("#f-food").value,
    hz=$("#f-hazard").value,cl=$("#f-class").value,q=$("#f-q").value.trim().toLowerCase(),
    ss=$("#btn-sample").checked;
  let rows=DATA.filter(r=>{
    if(!ss&&r.is_sample==="Yes") return false;
    if(a&&r.agency!==a) return false;
    if(rg&&!(r.regions||"").includes(rg)) return false;
    if(fd&&r.food_type!==fd) return false;
    if(hz&&r.hazard_category!==hz) return false;
    if(cl&&r.classification!==cl) return false;
    if(q){const h=(r.firm+" "+r.product_description+" "+r.reason+" "+r.agent).toLowerCase(); if(!h.includes(q)) return false;}
    return true;
  });
  rows.sort((x,y)=>{const vx=x[sortKey]||"",vy=y[sortKey]||"";return (vx<vy?-1:vx>vy?1:0)*sortDir;});
  return rows;
}
function kpis(rows){
  const c1=rows.filter(r=>r.classification==="Class I").length;
  const ongoing=rows.filter(r=>/ongoing|active|open|progress/i.test(r.status)).length;
  const fda=rows.filter(r=>r.agency==="FDA").length;
  const hz={}; rows.forEach(r=>hz[r.hazard_category]=(hz[r.hazard_category]||0)+1);
  const top=Object.entries(hz).sort((a,b)=>b[1]-a[1])[0];
  const cards=[["",rows.length,"Recalls (filtered)"],["sev",c1,"Class I (serious)"],
    ["",ongoing,"Ongoing / active"],["",fda+" / "+(rows.length-fda),"FDA / USDA"]];
  $("#kpis").innerHTML=cards.map(([c,n,l])=>`<div class="kpi ${c}"><div class="n">${n}</div><div class="l">${l}</div></div>`).join("");
}
function monthsIn(rows){ return uniq(rows.map(r=>r.year&&r.month?`${r.year}-${r.month}`:"")).sort(); }
function trend(rows){
  const months=monthsIn(rows), host=$("#trend");
  if(!months.length){host.innerHTML='<div class="empty">No dated recalls in view.</div>';$("#trend-legend").innerHTML="";return;}
  const counts=months.map(m=>{const o={m};CLASS_ORDER.forEach(c=>o[c]=0);
    rows.forEach(r=>{if(`${r.year}-${r.month}`===m&&(r.classification in o))o[r.classification]++;});
    o.total=CLASS_ORDER.reduce((s,c)=>s+o[c],0);return o;});
  const maxV=Math.max(1,...counts.map(c=>c.total));
  const AX=40,H=280,padT=14,padB=48;
  const avail=Math.max(240,(host.clientWidth||340));
  const colW=Math.max(42,Math.floor((avail-AX-4)/months.length));
  const W=colW*months.length, plotH=H-padT-padB, bw=Math.min(28,colW*0.6);
  const x=i=>i*colW+colW/2, y=v=>padT+plotH*(1-v/maxV);
  const ticks=Math.min(maxV,5);
  let axis="";
  for(let t=0;t<=ticks;t++){const v=Math.round(maxV*t/ticks);
    axis+=`<line x1="${AX-4}" x2="${AX}" y1="${y(v)}" y2="${y(v)}" class="axis"/><text x="${AX-7}" y="${y(v)+3}" text-anchor="end">${v}</text>`;}
  let grid="";
  for(let t=0;t<=ticks;t++){const v=Math.round(maxV*t/ticks); grid+=`<line x1="0" x2="${W}" y1="${y(v)}" y2="${y(v)}" class="axis"/>`;}
  let bars="",years="",lastYear=null;
  counts.forEach((c,i)=>{
    const yr=c.m.slice(0,4);
    if(yr!==lastYear){const lx=x(i)-colW/2;
      years+=`<line x1="${lx}" x2="${lx}" y1="${padT}" y2="${padT+plotH+6}" stroke="#C7D0D8"/><text x="${lx+3}" y="${H-padB+31}" text-anchor="start" fill="#16202A" style="font-weight:600">${yr}</text>`;
      lastYear=yr;}
    let acc=0;
    CLASS_ORDER.forEach(cl=>{const v=c[cl];if(!v)return;
      const h=plotH*v/maxV,yy=padT+plotH*(1-(acc+v)/maxV);
      bars+=`<rect x="${x(i)-bw/2}" y="${yy}" width="${bw}" height="${h}" fill="${CLASS_COLOR[cl]}"><title>${c.m} · ${cl}: ${v}</title></rect>`;acc+=v;});
    bars+=`<text x="${x(i)}" y="${H-padB+14}" text-anchor="middle">${c.m.slice(5)}</text>`;
    if(c.total) bars+=`<text x="${x(i)}" y="${y(c.total)-4}" text-anchor="middle" fill="#16202A">${c.total}</text>`;});
  let marks="";
  POLICY.forEach(p=>{const idx=months.indexOf((p.date||"").slice(0,7)); if(idx>=0){const xx=x(idx);
    marks+=`<line x1="${xx}" x2="${xx}" y1="${padT}" y2="${padT+plotH}" stroke="#16202A" stroke-dasharray="3 3" opacity=".5"/><polygon points="${xx-4},${padT} ${xx+4},${padT} ${xx},${padT+7}" fill="#16202A"><title>${p.date} — ${p.title}</title></polygon>`;}});
  host.innerHTML=`<div class="trend-scroll-wrap"><svg class="trend-axis" width="${AX}" height="${H}" aria-hidden="true">${axis}</svg>`
    +`<div class="trend-scroll"><svg width="${W}" height="${H}" role="img" aria-label="Recalls per month by class">${grid}${years}${bars}${marks}</svg></div></div>`;
  $("#trend-legend").innerHTML=CLASS_ORDER.map(c=>`<span><i style="background:${CLASS_COLOR[c]}"></i>${c}</span>`).join("")+`<span><i style="background:#16202A"></i>policy event</span>`+(W>avail-AX?`<span style="color:#0F5C6E">scroll →</span>`:"");
}
function stackedBars(host,entries,max){
  host.innerHTML=entries.map(e=>{
    const segs=CLASS_ORDER.map(c=>{const v=e.seg[c]||0;
      return v?`<i style="width:${100*v/e.total}%;background:${CLASS_COLOR[c]}" title="${c}: ${v}"></i>`:"";}).join("");
    return `<div class="bar-row"><div class="name" title="${e.name}">${e.name}</div><div class="bar-track"><div class="stack" style="width:${100*e.total/max}%">${segs}</div></div><div class="v">${e.total}</div></div>`;
  }).join("")||'<div class="empty" style="padding:12px">None</div>';
}
function regionBars(rows){const m={};REGION_ORDER.forEach(r=>m[r]={name:r,total:0,seg:{}});
  rows.forEach(r=>{const cls=r.classification;(r.regions||"").split(",").map(s=>s.trim()).forEach(s=>{if(!(s in m))return;m[s].total++;m[s].seg[cls]=(m[s].seg[cls]||0)+1;});});
  const arr=REGION_ORDER.map(r=>m[r]).filter(e=>e.total);
  stackedBars($("#region-bars"),arr,Math.max(1,...arr.map(e=>e.total)));}
function hazardBars(rows){const m={};rows.forEach(r=>{const h=r.hazard_category||"Unspecified";(m[h]=m[h]||{name:h,total:0,seg:{}});m[h].total++;m[h].seg[r.classification]=(m[h].seg[r.classification]||0)+1;});
  const arr=Object.values(m).sort((a,b)=>b.total-a.total);
  stackedBars($("#hazard-bars"),arr,Math.max(1,...arr.map(e=>e.total)));}
function drawBarsLegend(){$("#bars-legend").innerHTML=CLASS_ORDER.map(c=>`<span><i style="background:${CLASS_COLOR[c]}"></i>${c}</span>`).join("");}
function illnessFor(r){return ILLNESS[r.agent]||(r.hazard_category==="Undeclared allergen"?ILLNESS["Undeclared allergen"]:null)||(r.hazard_category==="Foreign material"?ILLNESS["Foreign material"]:null);}
function esc(s){return (s||"").replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));}
function table(){
  const rows=tableRows, host=$("#rows");
  $("#count").textContent=rows.length? `Showing ${Math.min(shown,rows.length).toLocaleString()} of ${rows.length.toLocaleString()} recalls`:"0 recalls";
  if(!rows.length){host.innerHTML='<div class="empty">No recalls match these filters.</div>';$("#tablefoot").innerHTML="";return;}
  host.innerHTML=rows.slice(0,shown).map(r=>{
    const col=CLASS_COLOR[r.classification]||"#5A6B7B", agc=r.agency==="FDA"?"fda":"usda";
    const ill=illnessFor(r), ongoing=/ongoing|active|open|progress/i.test(r.status);
    const days=r.days_open!==""&&r.days_open!=null?`${r.days_open} days${r.date_closed?"":" (open)"}`:"—";
    const illB=ill?`<div class="illness"><div class="h">If ${esc(r.agent||r.hazard_category)} — what it can cause</div><b>${esc(ill.illness)}.</b> ${esc(ill.symptoms)}<div style="margin-top:4px;color:var(--muted)">Onset ${esc(ill.onset)} · Higher risk: ${esc(ill.higher_risk)}</div></div>`:"";
    return `<div class="rowc"><div class="rtop" onclick="this.parentNode.classList.toggle('open')">
      <div class="spine" style="background:${col}"></div>
      <div class="rmid">
        <div class="rmeta"><span class="chip ${agc}">${r.agency}</span><span>${r.date_reported||"—"}</span><span>${esc(r.regions)}</span></div>
        <div class="firm">${esc(r.firm)||"—"}</div>
        <div class="prod">${esc(r.product_description)}</div>
      </div>
      <div class="cls" style="color:${col}">${(r.classification||"—").replace(" (USDA)","")}</div>
    </div>
    <div class="detail">
      <dl>
        <dt>Recall #</dt><dd>${esc(r.recall_number)||"—"} ${r.is_sample==="Yes"?'<span class="flag">sample</span>':""}</dd>
        <dt>Reason</dt><dd>${esc(r.reason)||"—"}</dd>
        <dt>Hazard</dt><dd>${esc(r.hazard_category)}${r.agent?" · "+esc(r.agent):""}</dd>
        <dt>Status</dt><dd><span class="spill ${ongoing?"on":""}">${esc(r.status)||"—"}</span> &nbsp;${days}</dd>
        <dt>Distribution</dt><dd>${esc(r.distribution_pattern)||"—"}${r.nationwide==="Yes"?" · Nationwide":""}</dd>
        <dt>Quantity</dt><dd>${esc(r.quantity_raw)||"—"}</dd>
        ${r.url?`<dt>Source</dt><dd><a href="${r.url}" target="_blank" rel="noopener">Agency recall page ↗</a></dd>`:""}
      </dl>${illB}
    </div></div>`;}).join("");
  const remaining=rows.length-shown;
  $("#tablefoot").innerHTML = remaining>0 ?
    `<button class="ghost" id="more-btn">Show ${Math.min(PAGE,remaining)} more</button>`
    +`<button class="ghost" id="all-btn">Show all ${rows.length.toLocaleString()}</button>` : "";
  if(remaining>0){$("#more-btn").onclick=()=>{shown+=PAGE;table();};$("#all-btn").onclick=()=>{shown=rows.length;table();};}
}
function policy(){
  $("#policy").innerHTML=POLICY.map(p=>{const conf=(p.effect_on_recalls||"").includes("CONFOUNDER");
    return `<div class="pol-item"><div class="pol-date">${p.date}</div><div><div class="pol-title">${esc(p.title)}</div><div class="pol-sum">${esc(p.summary)}</div><div class="pol-eff">${conf?'<span class="flag">confounder</span>':""}${esc(p.effect_on_recalls)}</div><div class="conf">confidence: ${esc(p.confidence)} · ${esc(p.source)}</div></div></div>`;}).join("");
}
function render(){const rows=filtered();tableRows=rows;shown=PAGE;kpis(rows);trend(rows);regionBars(rows);hazardBars(rows);table();}

/* ---------- wire up ---------- */
(function initYears(){const now=new Date().getFullYear();const sel=$("#year");
  for(let y=now;y>=2022;y--){const o=document.createElement("option");o.value=y;o.textContent=y;sel.appendChild(o);} sel.value=now;})();
["f-agency","f-region","f-food","f-hazard","f-class"].forEach(id=>$("#"+id).addEventListener("change",render));
$("#f-q").addEventListener("input",render);
$("#btn-sample").addEventListener("change",render);
$("#year").addEventListener("change",refresh);
$("#btn-refresh").addEventListener("click",refresh);
$("#btn-filters").addEventListener("click",()=>$("#filters").classList.toggle("open"));
$("#btn-reset").addEventListener("click",()=>{["f-agency","f-region","f-food","f-hazard","f-class"].forEach(id=>$("#"+id).value="");$("#f-q").value="";$("#btn-sample").checked=true;render();});
$("#btn-export").addEventListener("click",()=>{const rows=filtered();const cols=Object.keys(DATA[0]||{recall_id:1});
  const csv=[cols.join(",")].concat(rows.map(r=>cols.map(c=>{let v=(r[c]??"").toString().replace(/"/g,'""');return /[",\n]/.test(v)?`"${v}"`:v;}).join(","))).join("\n");
  const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([csv],{type:"text/csv"}));a.download="recalls_filtered.csv";a.click();});
$("#btn-load").addEventListener("click",()=>$("#file").click());
$("#file").addEventListener("change",e=>{const f=e.target.files[0];if(!f)return;const rd=new FileReader();
  rd.onload=()=>{try{let arr=f.name.endsWith(".json")?JSON.parse(rd.result):parseCSV(rd.result);
    if(!Array.isArray(arr)||!arr.length)throw new Error("empty");DATA=arr;$("#btn-sample").checked=true;
    banner();populate();render();alert("Loaded "+arr.length+" records from "+f.name);}
    catch(err){alert("Could not read that file: "+err.message);}};rd.readAsText(f);});
function parseCSV(text){const rows=[];let i=0,f="",row=[],q=false;
  while(i<text.length){const c=text[i];
    if(q){if(c==='"'){if(text[i+1]==='"'){f+='"';i++;}else q=false;}else f+=c;}
    else{if(c==='"')q=true;else if(c===","){row.push(f);f="";}
      else if(c==="\n"||c==="\r"){if(f!==""||row.length){row.push(f);f="";rows.push(row);row=[];}if(c==="\r"&&text[i+1]==="\n")i++;}
      else f+=c;}i++;}
  if(f!==""||row.length){row.push(f);rows.push(row);}
  const head=rows.shift();return rows.map(r=>Object.fromEntries(head.map((h,j)=>[h,r[j]??""])));}

// show Add-to-Home hint on iOS Safari tabs (not already installed)
if(/iP(hone|ad|od)/.test(navigator.userAgent) && !navigator.standalone) $("#a2hs").classList.add("show");

populate(); policy(); drawBarsLegend(); render();
refresh();   // attempt live data on open; falls back to sample if blocked
</script>
</body>
</html>"""


def main():
    sample = load_sample()
    illness = {r["agent"]: r for r in ref.HAZARD_ILLNESS}
    icon = make_icon()
    html = (TEMPLATE
            .replace("__SAMPLE_JSON__", json.dumps(sample, ensure_ascii=False))
            .replace("__POLICY_JSON__", json.dumps(ref.POLICY_TIMELINE, ensure_ascii=False))
            .replace("__ILLNESS_JSON__", json.dumps(illness, ensure_ascii=False))
            .replace("__REGION_OF__", json.dumps(ref.REGION_OF))
            .replace("__STATE_ABBR__", json.dumps(ref.STATE_ABBR))
            .replace("__FOOD_RULES__", json.dumps(ref.FOOD_TYPE_RULES))
            .replace("__PATHOGENS__", json.dumps(ref.PATHOGENS))
            .replace("__ALLERGENS__", json.dumps(ref.ALLERGENS))
            .replace("__ICON__", icon))
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {OUT}  ({len(sample)} sample rows embedded, icon={'yes' if icon else 'no'})")


if __name__ == "__main__":
    main()
