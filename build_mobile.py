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
    d.rounded_rectangle([0, 0, S, S], radius=112, fill=(0, 103, 124, 255))   # M3 primary #00677c
    d.rounded_rectangle([70, 60, 120, S - 60], radius=22, fill=(255, 218, 212, 255))  # sev-c1 container
    # magnifier lens
    cx, cy, r = 300, 232, 120
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255, 255), width=34)
    d.line([cx + r - 24, cy + r - 24, 430, 372], fill=(255, 255, 255, 255), width=40)
    # teal check inside lens
    d.line([cx - 52, cy + 6, cx - 14, cy + 46], fill=(178, 235, 255, 255), width=30)
    d.line([cx - 14, cy + 46, cx + 60, cy - 44], fill=(178, 235, 255, 255), width=30)
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
<meta name="theme-color" media="(prefers-color-scheme: light)" content="#f5fafd">
<meta name="theme-color" media="(prefers-color-scheme: dark)" content="#0f1416">
<meta name="color-scheme" content="light dark">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Recalls">
<link rel="apple-touch-icon" href="__ICON__">
<link rel="icon" href="__ICON__">
<link rel="manifest" href='data:application/json,{"name":"US Food Recall Monitor","short_name":"Recalls","display":"standalone","background_color":"%23f5fafd","theme_color":"%2300677c","icons":[{"src":"__ICON__","sizes":"512x512","type":"image/png"}]}'>
<style>
/* ===== Material Design 3 system tokens =====================================
   Color: generated with Google's material-color-utilities (SchemeTonalSpot),
   seed #0F5C6E. Shape/state/type/motion values from material-web
   tokens/versions/latest. Severity colors are data-viz roles built as M3 tonal
   palettes (tone 45 light / 75 dark), deliberately NOT harmonized to the seed
   so their red/amber/teal/violet meaning is preserved. */
:root{
  color-scheme:light dark;
  --md-primary:#00677c;--md-on-primary:#ffffff;
  --md-primary-container:#b2ebff;--md-on-primary-container:#004e5e;
  --md-secondary:#4b626a;--md-secondary-container:#cee7f0;--md-on-secondary-container:#344a51;
  --md-tertiary-container:#dfe0ff;--md-on-tertiary-container:#404465;
  --md-error:#ba1a1a;--md-error-container:#ffdad6;--md-on-error-container:#93000a;
  --md-surface:#f5fafd;--md-on-surface:#171c1e;--md-on-surface-variant:#40484b;
  --md-surface-container-lowest:#ffffff;--md-surface-container-low:#eff4f7;
  --md-surface-container:#eaeff1;--md-surface-container-high:#e4e9eb;
  --md-surface-container-highest:#dee3e6;
  --md-outline:#70787c;--md-outline-variant:#bfc8cc;
  --sev-c1:#c6341e;--sev-c2:#9b5c00;--sev-c3:#417183;--sev-pha:#7a5ca6;
  --sev-c1-container:#ffdad4;--warn-container:#ffdcbd;--on-warn-container:#693c00;
  /* shape */
  --md-shape-xs:4px;--md-shape-sm:8px;--md-shape-md:12px;--md-shape-lg:16px;
  --md-shape-xl:28px;--md-shape-full:9999px;
  /* state layers */
  --md-state-hover:.08;--md-state-focus:.10;--md-state-pressed:.10;
  /* motion */
  --md-ease-standard:cubic-bezier(0.2,0,0,1);--md-dur-short4:200ms;
  /* type — Roboto is the M3 baseline typeface; system fallbacks keep the
     file offline/self-contained (no webfont download). */
  --md-font:Roboto,"Google Sans Text",system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;
  --md-font-mono:"Roboto Mono",ui-monospace,"Cascadia Mono",Consolas,Menlo,monospace;
}
@media (prefers-color-scheme:dark){:root{
  --md-primary:#86d1e9;--md-on-primary:#003642;
  --md-primary-container:#004e5e;--md-on-primary-container:#b2ebff;
  --md-secondary:#b2cad3;--md-secondary-container:#344a51;--md-on-secondary-container:#cee7f0;
  --md-tertiary-container:#404465;--md-on-tertiary-container:#dfe0ff;
  --md-error:#ffb4ab;--md-error-container:#93000a;--md-on-error-container:#ffdad6;
  --md-surface:#0f1416;--md-on-surface:#dee3e6;--md-on-surface-variant:#bfc8cc;
  --md-surface-container-lowest:#090f11;--md-surface-container-low:#171c1e;
  --md-surface-container:#1b2022;--md-surface-container-high:#252b2d;
  --md-surface-container-highest:#303638;
  --md-outline:#899296;--md-outline-variant:#40484b;
  --sev-c1:#ffa08e;--sev-c2:#ffa53a;--sev-c3:#90c0d4;--sev-pha:#cbaafa;
  --sev-c1-container:#900e00;--warn-container:#693c00;--on-warn-container:#ffdcbd;
}}

/* ===== type scale (material-web tokens, rem) ============================== */
.t-headline-s{font-size:1.5rem;line-height:2rem;font-weight:400}
.t-headline-m{font-size:1.75rem;line-height:2.25rem;font-weight:400}
.t-title-l{font-size:1.375rem;line-height:1.75rem;font-weight:400}
.t-title-m{font-size:1rem;line-height:1.5rem;font-weight:500;letter-spacing:.009375rem}
.t-title-s{font-size:.875rem;line-height:1.25rem;font-weight:500;letter-spacing:.00625rem}
.t-label-l{font-size:.875rem;line-height:1.25rem;font-weight:500;letter-spacing:.00625rem}
.t-label-m{font-size:.75rem;line-height:1rem;font-weight:500;letter-spacing:.03125rem}
.t-label-s{font-size:.6875rem;line-height:1rem;font-weight:500;letter-spacing:.03125rem}
.t-body-l{font-size:1rem;line-height:1.5rem;letter-spacing:.03125rem}
.t-body-m{font-size:.875rem;line-height:1.25rem;letter-spacing:.015625rem}
.t-body-s{font-size:.75rem;line-height:1rem;letter-spacing:.025rem}

/* ===== base =============================================================== */
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--md-surface);color:var(--md-on-surface);
  font-family:var(--md-font);font-size:.875rem;line-height:1.25rem;
  letter-spacing:.015625rem;-webkit-font-smoothing:antialiased}
a{color:var(--md-primary)}
code{font-family:var(--md-font-mono);font-size:.8125rem}
.num{font-variant-numeric:tabular-nums}

/* focus indicator: 3px ring, 2px outer offset, secondary (md.sys.state.focus-indicator) */
:focus-visible{outline:3px solid var(--md-secondary);outline-offset:2px}

/* state layer: currentColor overlay at M3 opacities */
.sl{position:relative;isolation:isolate}
.sl::before{content:"";position:absolute;inset:0;border-radius:inherit;
  background:currentColor;opacity:0;pointer-events:none;z-index:-1;
  transition:opacity var(--md-dur-short4) var(--md-ease-standard)}
.sl:hover::before{opacity:var(--md-state-hover)}
.sl:focus-visible::before{opacity:var(--md-state-focus)}
.sl:active::before{opacity:var(--md-state-pressed)}

/* ===== buttons (button-small: 40px container, full corner, 48px target) === */
.btn{font:inherit;font-size:.875rem;line-height:1.25rem;font-weight:500;
  letter-spacing:.00625rem;height:40px;padding:0 16px;border-radius:var(--md-shape-full);
  border:0;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;
  gap:8px;white-space:nowrap}
.btn::after{content:"";position:absolute;left:0;right:0;top:-4px;bottom:-4px}  /* 48px target */
.btn.filled{background:var(--md-primary);color:var(--md-on-primary)}
.btn.tonal{background:var(--md-secondary-container);color:var(--md-on-secondary-container)}
.btn.outlined{background:transparent;color:var(--md-primary);border:1px solid var(--md-outline-variant)}
.btn.text{background:transparent;color:var(--md-primary);padding:0 12px}
.btn[disabled]{opacity:.38;cursor:default}
.btn svg{width:20px;height:20px;fill:currentColor}

/* ===== filter chip (32px, small corner, 48px target) ====================== */
.fchip{position:relative;display:inline-flex;cursor:pointer}
.fchip input{position:absolute;opacity:0;width:1px;height:1px}
.fchip-body{display:inline-flex;align-items:center;gap:8px;height:32px;padding:0 16px;
  border-radius:var(--md-shape-sm);border:1px solid var(--md-outline-variant);
  color:var(--md-on-surface-variant);font-size:.875rem;font-weight:500;letter-spacing:.00625rem}
.fchip-body::after{content:"";position:absolute;left:0;right:0;top:-8px;bottom:-8px}
.fchip-body svg{width:18px;height:18px;fill:currentColor;display:none}
.fchip input:checked + .fchip-body{background:var(--md-secondary-container);
  color:var(--md-on-secondary-container);border-color:transparent;padding-left:8px}
.fchip input:checked + .fchip-body svg{display:block}
.fchip input:focus-visible + .fchip-body{outline:3px solid var(--md-secondary);outline-offset:2px}

/* ===== outlined select / search bar ======================================= */
.fld{display:flex;flex-direction:column;gap:4px;min-width:0}
.fld > label{font-size:.75rem;line-height:1rem;font-weight:500;letter-spacing:.03125rem;
  color:var(--md-on-surface-variant);padding-left:4px}
.select{font:inherit;font-size:1rem;line-height:1.5rem;height:56px;padding:0 40px 0 16px;
  border:1px solid var(--md-outline);border-radius:var(--md-shape-xs);
  background:var(--md-surface) no-repeat right 12px center/24px 24px;
  color:var(--md-on-surface);cursor:pointer;appearance:none;-webkit-appearance:none;width:100%;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2370787c' d='M7 10l5 5 5-5z'/%3E%3C/svg%3E")}
.select:hover{border-color:var(--md-on-surface)}
.select:focus-visible{outline:none;border:2px solid var(--md-primary);padding-left:15px}
.search{display:flex;align-items:center;gap:4px;height:56px;padding:0 16px 0 16px;
  border-radius:var(--md-shape-full);background:var(--md-surface-container-high);
  color:var(--md-on-surface-variant)}
.search svg{width:24px;height:24px;fill:currentColor;flex:0 0 auto}
.search input{flex:1;min-width:0;height:100%;border:0;background:transparent;
  font:inherit;font-size:1rem;line-height:1.5rem;color:var(--md-on-surface);padding:0 8px}
.search input::placeholder{color:var(--md-on-surface-variant)}
.search input:focus-visible{outline:none}
.search:focus-within{outline:3px solid var(--md-secondary);outline-offset:2px}

/* ===== cards (outlined: medium corner, 1px outline-variant) =============== */
.card{background:var(--md-surface);border:1px solid var(--md-outline-variant);
  border-radius:var(--md-shape-md);padding:16px;min-width:0}
.card-filled{background:var(--md-surface-container-highest);border-radius:var(--md-shape-md);padding:16px}
.card h2{margin:0 0 12px;font-size:1rem;line-height:1.5rem;font-weight:500;
  letter-spacing:.009375rem;color:var(--md-on-surface)}
.card h2 .sub{display:block;font-size:.75rem;line-height:1rem;font-weight:400;
  letter-spacing:.025rem;color:var(--md-on-surface-variant)}

/* static labels (non-interactive; chip-shaped — see README M3 deviations) */
.tag{display:inline-flex;align-items:center;height:24px;padding:0 8px;
  border-radius:var(--md-shape-sm);font-size:.6875rem;line-height:1rem;font-weight:500;
  letter-spacing:.03125rem;white-space:nowrap}
.tag.fda{background:var(--md-primary-container);color:var(--md-on-primary-container)}
.tag.usda{background:var(--md-tertiary-container);color:var(--md-on-tertiary-container)}
.tag.warn{background:var(--warn-container);color:var(--on-warn-container)}
.tag.outline{border:1px solid var(--md-outline-variant);color:var(--md-on-surface-variant)}
.tag.on{background:var(--warn-container);color:var(--on-warn-container)}
.tag.live{background:var(--md-primary-container);color:var(--md-on-primary-container)}
.tag.sample{background:var(--md-error-container);color:var(--md-on-error-container)}

/* notice (filled card in error/secondary containers; M3 has no banner) */
.notice{border-radius:var(--md-shape-md);padding:12px 16px;font-size:.875rem;line-height:1.25rem}
.notice.error{background:var(--md-error-container);color:var(--md-on-error-container)}
.notice.warn{background:var(--warn-container);color:var(--on-warn-container)}
.notice.info{background:var(--md-secondary-container);color:var(--md-on-secondary-container)}

/* ===== data viz =========================================================== */
.legend{display:flex;gap:4px 16px;flex-wrap:wrap;font-size:.75rem;line-height:1rem;
  color:var(--md-on-surface-variant);margin-top:12px}
.legend i{display:inline-block;width:12px;height:12px;border-radius:var(--md-shape-xs);
  margin-right:6px;vertical-align:-2px}
.bars{display:flex;flex-direction:column;gap:8px}
.bar-row{display:grid;grid-template-columns:132px 1fr 40px;align-items:center;gap:12px}
.bar-row .name{font-size:.875rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar-track{background:var(--md-surface-container-highest);border-radius:var(--md-shape-xs);
  height:16px;overflow:hidden}
.stack{height:100%;display:flex;overflow:hidden;border-radius:var(--md-shape-xs)}
.stack i{display:block;height:100%}
.stack i + i{box-shadow:-1px 0 0 var(--md-surface)}
.bar-row .v{font-variant-numeric:tabular-nums;font-size:.875rem;text-align:right;
  color:var(--md-on-surface-variant)}
.trend-scroll-wrap{display:flex;align-items:flex-start}
.trend-axis{flex:0 0 auto}
.trend-scroll{overflow-x:auto;overflow-y:hidden;flex:1 1 auto;min-width:0;
  -webkit-overflow-scrolling:touch;scrollbar-width:thin}
.trend-scroll svg{display:block}
svg text{font-family:var(--md-font);font-size:11px;fill:var(--md-on-surface-variant);
  font-variant-numeric:tabular-nums}
.axis{stroke:var(--md-outline-variant)}
.empty{padding:40px 16px;text-align:center;color:var(--md-on-surface-variant)}

/* ===== expandable list ==================================================== */
.list{background:var(--md-surface);border:1px solid var(--md-outline-variant);
  border-radius:var(--md-shape-lg);overflow:hidden}
.row{border-bottom:1px solid var(--md-outline-variant)}
.row:last-child{border-bottom:0}
.rtop{cursor:pointer;color:var(--md-on-surface)}
.spine{width:4px;align-self:stretch;border-radius:var(--md-shape-full);min-height:40px}
.firm{font-size:1rem;line-height:1.5rem;letter-spacing:.03125rem;white-space:nowrap;
  overflow:hidden;text-overflow:ellipsis}
.prod{font-size:.875rem;line-height:1.25rem;color:var(--md-on-surface-variant);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.cls{font-size:.75rem;line-height:1rem;font-weight:500;letter-spacing:.03125rem;white-space:nowrap}
.chev{width:24px;height:24px;fill:var(--md-on-surface-variant);flex:0 0 auto;
  transition:transform var(--md-dur-short4) var(--md-ease-standard)}
.row.open .chev{transform:rotate(180deg)}
.detail{display:none;padding:8px 16px 16px 36px;background:var(--md-surface-container-low)}
.row.open .detail{display:block}
.detail dl{display:grid;grid-template-columns:140px 1fr;gap:8px 16px;margin:8px 0}
.detail dt{font-size:.75rem;line-height:1rem;font-weight:500;letter-spacing:.03125rem;
  color:var(--md-on-surface-variant);padding-top:2px}
.detail dd{margin:0;font-size:.875rem;line-height:1.25rem}
.illness{background:var(--md-surface);border:1px solid var(--md-outline-variant);
  border-radius:var(--md-shape-md);padding:12px 16px;margin-top:8px}
.illness .h{font-size:.75rem;line-height:1rem;font-weight:500;letter-spacing:.03125rem;
  color:var(--sev-c1);margin-bottom:4px}
.listfoot{display:flex;gap:8px;align-items:center;padding:16px;flex-wrap:wrap;
  border-top:1px solid var(--md-outline-variant)}
.listfoot:empty{display:none}
.count{font-size:.875rem;color:var(--md-on-surface-variant);margin:24px 4px 8px}

/* ===== policy list ======================================================== */
.pol-item{display:grid;grid-template-columns:104px 1fr;gap:16px;padding:12px 0;
  border-top:1px solid var(--md-outline-variant)}
.pol-item:first-child{border-top:0}
.pol-date{font-variant-numeric:tabular-nums;font-size:.875rem;font-weight:500;color:var(--md-primary)}
.pol-title{font-size:1rem;line-height:1.5rem;font-weight:500}
.pol-sum{font-size:.875rem;color:var(--md-on-surface-variant);margin-top:2px}
.pol-eff{font-size:.875rem;margin-top:8px;display:flex;gap:8px;align-items:flex-start;flex-wrap:wrap}
.conf{font-size:.75rem;line-height:1rem;color:var(--md-on-surface-variant);margin-top:4px}
footer{margin-top:32px;padding-top:16px;border-top:1px solid var(--md-outline-variant);
  font-size:.875rem;color:var(--md-on-surface-variant)}
footer ul{margin:8px 0 0;padding-left:20px}
footer strong{color:var(--md-on-surface)}

@media (prefers-reduced-motion:reduce){*{transition:none!important}html{scroll-behavior:auto}}

/* ===== mobile layout (M3 compact window: 16dp margins) ==================== */
body{padding:env(safe-area-inset-top) env(safe-area-inset-right) 0 env(safe-area-inset-left)}
.wrap{max-width:840px;margin:0 auto;padding:0 16px 72px}
header.mast{padding:16px 0 8px}
.overline{margin:0 0 4px;color:var(--md-primary)}
h1{margin:0}
.srcline{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px;align-items:center}
.updated{font-size:.75rem;line-height:1rem;color:var(--md-on-surface-variant);margin-left:auto}
.notice{margin:8px 0 16px;display:none}.notice.show{display:block}
.controls{display:grid;grid-template-columns:minmax(96px,1fr) auto auto;gap:8px;align-items:end;margin:8px 0 16px}
.controls .btn{margin-bottom:8px}   /* centers 40dp buttons on the 56dp field */
.filters{display:none;background:var(--md-surface-container-low);border-radius:var(--md-shape-lg);
  padding:16px;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px}
.filters.open{display:grid}
.filters .full{grid-column:1/-1}
.rowbtns{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.kpis{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:16px}
.kpi .n{font-size:1.75rem;line-height:2.25rem;font-variant-numeric:tabular-nums}
.kpi .l{font-size:.75rem;line-height:1rem;color:var(--md-on-surface-variant);margin-top:4px}
.kpi.sev .n{color:var(--sev-c1)}
.card{margin-bottom:16px}
.bar-row{grid-template-columns:96px 1fr 36px;gap:8px}
.rowc{border-bottom:1px solid var(--md-outline-variant)}
.rowc:last-child{border-bottom:0}
.rtop{display:grid;grid-template-columns:4px minmax(0,1fr) auto 24px;gap:12px;align-items:center;
  padding:12px 16px;min-height:88px;cursor:pointer}                   /* three-line list item */
.rmeta{display:flex;gap:8px;align-items:center;font-size:.75rem;line-height:1rem;
  color:var(--md-on-surface-variant);margin-bottom:2px;min-width:0}
.rmeta span:last-child{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.rowc.open .detail{display:block}
.rowc.open .chev{transform:rotate(180deg)}
.detail dl{grid-template-columns:104px 1fr}
.detail{padding-left:16px}
.pol-item{grid-template-columns:88px 1fr;gap:12px}
.a2hs{display:none;margin-bottom:16px}.a2hs.show{display:block}
@media (min-width:600px){.wrap{padding:0 24px 72px}.kpis{grid-template-columns:repeat(4,1fr)}
  .filters{grid-template-columns:repeat(3,1fr)}}                     /* medium: 24dp */
@media (max-width:379px){.detail dl{grid-template-columns:1fr}
  .controls{grid-template-columns:1fr 1fr}.controls .fld{grid-column:1/-1}.controls .btn{margin-bottom:0}}
</style>
</head>
<body>
<div class="wrap">
  <header class="mast">
    <p class="overline t-label-l">Food safety surveillance &middot; FDA + USDA</p>
    <h1 class="t-headline-s">US Food Recall Monitor</h1>
    <div class="srcline" id="srcline">
      <span class="tag outline" id="pill-fda">FDA —</span>
      <span class="tag outline" id="pill-usda">USDA —</span>
      <span class="updated" id="updated"></span>
    </div>
  </header>

  <div class="notice info a2hs" id="a2hs">Tip: tap <b>Share → Add to Home Screen</b> to keep this as an app that refreshes on open.</div>
  <div class="notice" id="banner" role="status"></div>

  <div class="controls">
    <div class="fld"><label for="year">Year</label><select class="select" id="year"></select></div>
    <button type="button" class="btn tonal sl" id="btn-filters" aria-expanded="false" aria-controls="filters"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10 18h4v-2h-4v2zM3 6v2h18V6H3zm3 7h12v-2H6v2z"/></svg>Filters</button>
    <button type="button" class="btn filled sl" id="btn-refresh"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M17.65 6.35A7.96 7.96 0 0 0 12 4a8 8 0 1 0 7.73 10h-2.08A6 6 0 1 1 12 6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg>Refresh</button>
  </div>

  <section class="filters" id="filters" aria-label="Filters">
    <div class="full"><div class="search"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15.5 14h-.79l-.28-.27A6.47 6.47 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
      <input type="search" id="f-q" placeholder="Search firm, product, pathogen" aria-label="Search firm, product, or pathogen"></div></div>
    <div class="fld"><label for="f-agency">Agency</label><select class="select" id="f-agency"></select></div>
    <div class="fld"><label for="f-region">Region</label><select class="select" id="f-region"></select></div>
    <div class="fld"><label for="f-food">Food type</label><select class="select" id="f-food"></select></div>
    <div class="fld"><label for="f-hazard">Hazard</label><select class="select" id="f-hazard"></select></div>
    <div class="fld"><label for="f-class">Class</label><select class="select" id="f-class"></select></div>
    <div class="full rowbtns">
      <label class="fchip"><input type="checkbox" id="btn-sample" checked><span class="fchip-body sl"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 16.17 4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>Sample rows</span></label>
      <button type="button" class="btn text sl" id="btn-reset">Reset</button>
      <button type="button" class="btn outlined sl" id="btn-export">Export CSV</button>
      <button type="button" class="btn outlined sl" id="btn-load">Load file</button>
      <input type="file" id="file" accept=".json,.csv" hidden>
    </div>
  </section>

  <section class="kpis" id="kpis" aria-label="Summary"></section>

  <section class="card">
    <h2>Recalls per month<span class="sub">By severity class &middot; dashed lines mark policy events</span></h2>
    <div id="trend"></div>
    <div class="legend" id="trend-legend"></div>
  </section>
  <section class="card">
    <h2>By region<span class="sub">Where distributed; multi-region recalls count in each</span></h2>
    <div class="bars" id="region-bars"></div>
    <h2 style="margin-top:24px">By hazard</h2>
    <div class="bars" id="hazard-bars"></div>
    <div class="legend" id="bars-legend"></div>
  </section>

  <div class="count" id="count" aria-live="polite"></div>
  <section class="list" aria-label="Recalls"><div id="rows"></div><div class="listfoot" id="tablefoot"></div></section>

  <section class="card" style="margin-top:16px">
    <h2>Policy &amp; regulatory timeline<span class="sub">Items tagged <b>confounder</b> can change reported counts independent of actual food safety</span></h2>
    <div id="policy"></div>
  </section>

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
const CLASS_COLOR={"Class I":"var(--sev-c1)","Class II":"var(--sev-c2)","Class III":"var(--sev-c3)","Public Health Alert (USDA)":"var(--sev-pha)"};
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
function setPill(id,cls,txt){ const el=$(id); el.className="tag "+({live:"live",warnp:"warn",sample:"sample"}[cls]||"outline"); el.textContent=txt; }
function banner(kind,html){ const b=$("#banner"); if(!kind){b.className="notice";b.innerHTML="";return;}
  b.className="notice show "+({sample:"error",warn:"warn"}[kind]||"info"); b.innerHTML=html; }

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
  $("#kpis").innerHTML=cards.map(([c,n,l])=>`<div class="card kpi ${c}" style="margin:0"><div class="n">${n}</div><div class="l">${l}</div></div>`).join("");
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
      years+=`<line x1="${lx}" x2="${lx}" y1="${padT}" y2="${padT+plotH+6}" style="stroke:var(--md-outline)"/><text x="${lx+3}" y="${H-padB+31}" text-anchor="start" style="fill:var(--md-on-surface);font-weight:500">${yr}</text>`;
      lastYear=yr;}
    let acc=0;
    CLASS_ORDER.forEach(cl=>{const v=c[cl];if(!v)return;
      const h=plotH*v/maxV,yy=padT+plotH*(1-(acc+v)/maxV);
      bars+=`<rect x="${x(i)-bw/2}" y="${yy}" width="${bw}" height="${h}" style="fill:${CLASS_COLOR[cl]}"><title>${c.m} · ${cl}: ${v}</title></rect>`;acc+=v;});
    bars+=`<text x="${x(i)}" y="${H-padB+14}" text-anchor="middle">${c.m.slice(5)}</text>`;
    if(c.total) bars+=`<text x="${x(i)}" y="${y(c.total)-4}" text-anchor="middle" style="fill:var(--md-on-surface)">${c.total}</text>`;});
  let marks="";
  POLICY.forEach(p=>{const idx=months.indexOf((p.date||"").slice(0,7)); if(idx>=0){const xx=x(idx);
    marks+=`<line x1="${xx}" x2="${xx}" y1="${padT}" y2="${padT+plotH}" style="stroke:var(--md-on-surface)" stroke-dasharray="3 3" opacity=".5"/><polygon points="${xx-4},${padT} ${xx+4},${padT} ${xx},${padT+7}" style="fill:var(--md-on-surface)"><title>${p.date} — ${p.title}</title></polygon>`;}});
  host.innerHTML=`<div class="trend-scroll-wrap"><svg class="trend-axis" width="${AX}" height="${H}" aria-hidden="true">${axis}</svg>`
    +`<div class="trend-scroll"><svg width="${W}" height="${H}" role="img" aria-label="Recalls per month by class">${grid}${years}${bars}${marks}</svg></div></div>`;
  $("#trend-legend").innerHTML=CLASS_ORDER.map(c=>`<span><i style="background:${CLASS_COLOR[c]}"></i>${c}</span>`).join("")+`<span><i style="background:var(--md-on-surface)"></i>policy event</span>`+(W>avail-AX?`<span style="color:var(--md-primary);font-weight:500">Scroll for more →</span>`:"");
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
    const col=CLASS_COLOR[r.classification]||"var(--md-outline)", agc=r.agency==="FDA"?"fda":"usda";
    const ill=illnessFor(r), ongoing=/ongoing|active|open|progress/i.test(r.status);
    const days=r.days_open!==""&&r.days_open!=null?`${r.days_open} days${r.date_closed?"":" (open)"}`:"—";
    const illB=ill?`<div class="illness"><div class="h">If ${esc(r.agent||r.hazard_category)} — what it can cause</div><b>${esc(ill.illness)}.</b> ${esc(ill.symptoms)}<div style="margin-top:4px;color:var(--md-on-surface-variant)">Onset ${esc(ill.onset)} · Higher risk: ${esc(ill.higher_risk)}</div></div>`:"";
    return `<div class="rowc"><div class="rtop sl" tabindex="0" role="button" aria-expanded="false">
      <div class="spine" style="background:${col}"></div>
      <div class="rmid">
        <div class="rmeta"><span class="tag ${agc}">${r.agency}</span><span>${r.date_reported||"—"}</span><span>${esc(r.regions)}</span></div>
        <div class="firm">${esc(r.firm)||"—"}</div>
        <div class="prod">${esc(r.product_description)}</div>
      </div>
      <div class="cls" style="color:${col}">${(r.classification||"—").replace(" (USDA)","")}</div>
      <svg class="chev" viewBox="0 0 24 24" aria-hidden="true"><path d="M16.59 8.59 12 13.17 7.41 8.59 6 10l6 6 6-6z"/></svg>
    </div>
    <div class="detail">
      <dl>
        <dt>Recall #</dt><dd>${esc(r.recall_number)||"—"} ${r.is_sample==="Yes"?'<span class="tag sample">Sample</span>':""}</dd>
        <dt>Reason</dt><dd>${esc(r.reason)||"—"}</dd>
        <dt>Hazard</dt><dd>${esc(r.hazard_category)}${r.agent?" · "+esc(r.agent):""}</dd>
        <dt>Status</dt><dd><span class="tag ${ongoing?"on":"outline"}">${esc(r.status)||"—"}</span> &nbsp;${days}</dd>
        <dt>Distribution</dt><dd>${esc(r.distribution_pattern)||"—"}${r.nationwide==="Yes"?" · Nationwide":""}</dd>
        <dt>Quantity</dt><dd>${esc(r.quantity_raw)||"—"}</dd>
        ${r.url?`<dt>Source</dt><dd><a href="${r.url}" target="_blank" rel="noopener">Agency recall page ↗</a></dd>`:""}
      </dl>${illB}
    </div></div>`;}).join("");
  const remaining=rows.length-shown;
  $("#tablefoot").innerHTML = remaining>0 ?
    `<button type="button" class="btn tonal sl" id="more-btn">Show ${Math.min(PAGE,remaining)} more</button>`
    +`<button type="button" class="btn text sl" id="all-btn">Show all ${rows.length.toLocaleString()}</button>` : "";
  if(remaining>0){$("#more-btn").onclick=()=>{shown+=PAGE;table();};$("#all-btn").onclick=()=>{shown=rows.length;table();};}
}
function policy(){
  $("#policy").innerHTML=POLICY.map(p=>{const conf=(p.effect_on_recalls||"").includes("CONFOUNDER");
    return `<div class="pol-item"><div class="pol-date">${p.date}</div><div><div class="pol-title">${esc(p.title)}</div><div class="pol-sum">${esc(p.summary)}</div><div class="pol-eff">${conf?'<span class="tag warn">Confounder</span>':""}<span>${esc((p.effect_on_recalls||"").replace(/^CONFOUNDER:\s*/,""))}</span></div><div class="conf">confidence: ${esc(p.confidence)} · ${esc(p.source)}</div></div></div>`;}).join("");
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
$("#btn-filters").addEventListener("click",e=>{const o=$("#filters").classList.toggle("open");e.currentTarget.setAttribute("aria-expanded",o);});
function toggleRow(t){const row=t.closest(".rowc");const o=row.classList.toggle("open");t.setAttribute("aria-expanded",o);}
$("#rows").addEventListener("click",e=>{const t=e.target.closest(".rtop");if(t)toggleRow(t);});
$("#rows").addEventListener("keydown",e=>{const t=e.target.closest(".rtop");if(t&&(e.key==="Enter"||e.key===" ")){e.preventDefault();toggleRow(t);}});
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
