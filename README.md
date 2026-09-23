# US Food Recall Monitor

An open, self-updating tracker of United States food recalls from both federal
agencies — **FDA** (openFDA Food Enforcement) and **USDA FSIS** — organized by
region, food type, and hazard, with a severity-class trend over time and a
policy timeline. One dataset drives three outputs: an interactive **web
dashboard**, a phone **home-screen app**, and a multi-tab **Excel workbook**.

> **Reading the data honestly.** A change in the number of recalls is *not* the
> same as a change in food safety. Reduced inspection staffing or a government
> shutdown can lower the number of recalls that get *reported* without food
> actually becoming safer. The Policy Timeline flags these confounders, and each
> policy item carries a confidence label. Treat trends as a starting point for
> questions, not a verdict.

---

## What it does

- Pulls every FDA- and USDA-regulated food recall for a given year from the
  official APIs and merges them into one running dataset.
- Derives **region** (from where each recall was distributed), **food type**,
  and **hazard** (pathogen, allergen, foreign material, etc.), and links each
  biological hazard to what it can cause.
- Produces:
  - `docs/index.html` — a mobile app that fetches FDA live in the browser and
    can be added to an iPhone home screen.
  - `docs/dashboard.html` — a full desktop dashboard (filters, severity-class
    trend, region/hazard breakdowns, expandable detail).
  - `Food_Recall_Tracker.xlsx` — an 8-tab workbook (built locally).
- Can **update itself once a day** via GitHub Actions.

## Live site

Once hosted (see [`guides/SETUP_ON_GITHUB.md`](guides/SETUP_ON_GITHUB.md)):

- Mobile app: `https://<username>.github.io/<repo>/`
- Desktop dashboard: `https://<username>.github.io/<repo>/dashboard.html`

## Repository layout

```
recall-monitor/
├── reference_data.py          shared lookups: regions, hazards, hazard→illness,
│                              policy timeline
├── fetch_recalls.py           the updater — fetches FDA + USDA, writes data/
├── build_dashboard.py         data → docs/dashboard.html (desktop)
├── build_mobile.py            data → docs/index.html (phone app)
├── build_workbook.py          data → Food_Recall_Tracker.xlsx (local)
├── data/
│   └── recalls_master.json    the running dataset (+ .csv); source of truth
├── docs/                      ← GitHub Pages serves this folder
│   ├── index.html             mobile app
│   ├── dashboard.html         desktop dashboard
│   └── .nojekyll
├── guides/
│   ├── SETUP_ON_GITHUB.md      host it on GitHub Pages
│   ├── SELF_HOSTED_RUNNER.md   fully-automatic daily updates (incl. USDA)
│   ├── AUTOMATE_DAILY.md       background on the daily job + Task Scheduler
│   ├── DESIGN_SYSTEM.md        Material Design 3 basis, checks, deviations
│   └── DESKTOP_USAGE.md        run the tools on your computer
├── update_recalls.bat          backup local updater (fetch → build → push)
├── .github/workflows/
│   └── update-recalls.yml      the daily job (runs on a self-hosted runner)
├── requirements.txt
└── LICENSE
```

## Quick start (local)

```bash
pip install -r requirements.txt

python fetch_recalls.py --year 2026     # fetch (repeat per year to backfill)
python build_dashboard.py               # → dashboard.html
python build_mobile.py                  # → recall_monitor_mobile.html
python build_workbook.py                # → Food_Recall_Tracker.xlsx
```

`fetch_recalls.py` **merges** into `data/recalls_master.json`, so running it for
several years accumulates history. See
[`guides/DESKTOP_USAGE.md`](guides/DESKTOP_USAGE.md) for the full workflow.

> **USDA needs `curl_cffi`.** USDA's server blocks ordinary Python requests; a
> `403 Forbidden` on USDA means `curl_cffi` isn't installed. `pip install
> curl_cffi` and re-run. FDA works without it.

## Hosting + daily updates

- **Host it:** [`guides/SETUP_ON_GITHUB.md`](guides/SETUP_ON_GITHUB.md) — push
  the repo and set **Pages → Deploy from a branch → `main` / `docs`**.
- **Automate it:** [`guides/SELF_HOSTED_RUNNER.md`](guides/SELF_HOSTED_RUNNER.md)
  — the included workflow fetches, rebuilds `docs/`, and commits once a day.

Important reality about USDA and automation: USDA's server blocks requests from
GitHub's cloud IPs, so the daily job **can't fetch USDA from GitHub's own
runners** (confirmed — even third-party mirrors that tried this went stale). It
*can* be fetched from a residential IP with `curl_cffi`. So the daily workflow is
set to run on a **self-hosted runner on your PC**, which updates FDA **and**
USDA. A `update_recalls.bat` + Task Scheduler backup does the same on demand. The
phone app also fetches **FDA live on every open**, so FDA is current regardless.
See the runner guide for setup and the security notes.

## Design

Both web outputs follow Google's **Material Design 3**: tokenized color roles
with automatic light/dark themes, the M3 shape, type, and state-layer scales,
48dp touch targets, and M3 window-size breakpoints. They pass an axe-core
WCAG 2.2 AA audit with no violations. Sources, verification, and intentional
deviations are documented in
[`guides/DESIGN_SYSTEM.md`](guides/DESIGN_SYSTEM.md).

## Data sources

- **FDA** — openFDA Food Enforcement API (FDA-regulated foods).
- **USDA** — FSIS Recall API (meat, poultry, egg).
- **Hazard → illness reference** — general CDC / FDA / USDA consumer information.

## How the data is derived, and its limits

- **Region** is parsed from free-text distribution info; a recall reaching
  several regions is counted in each, so region totals exceed the number of
  distinct recalls.
- **Food type** and **hazard** are inferred by keyword from the product and
  reason text — accurate for most records, but skim the source when a category
  looks off.
- **Quantities** are not standardized across agencies (FDA free text vs USDA
  pounds); the parsed value is best-effort and the raw quantity is authoritative.
- **Hazard → illness** notes are general educational information, **not medical
  advice**.
- Confidence on policy items uses four tiers: *well-established*,
  *supported-but-contested*, *low-confidence*, *speculative*.

## License

Code is released under the MIT License (see [`LICENSE`](LICENSE)) — replace
`<Your Name>` with yours, or swap in a different license. The underlying recall
data is public U.S. government information. This note is not legal advice.
