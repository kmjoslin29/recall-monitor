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
│   ├── SETUP_ON_GITHUB.md     host it on GitHub Pages
│   ├── AUTOMATE_DAILY.md      the once-a-day auto-update
│   └── DESKTOP_USAGE.md       run the tools on your computer
├── .github/workflows/
│   └── update-recalls.yml     the daily job
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
- **Automate it:** [`guides/AUTOMATE_DAILY.md`](guides/AUTOMATE_DAILY.md) — the
  included workflow fetches, rebuilds `docs/`, and commits once a day.

One caveat worth reading before you rely on the daily job: the phone app already
fetches **FDA live on every open**, so automation mainly keeps the embedded
**USDA** snapshot current — and USDA may be blocked from GitHub's cloud servers
even though it works from your home machine. The job degrades gracefully (FDA
keeps updating; USDA holds at its last good value). Details and a home-PC
alternative are in the automation guide.

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
