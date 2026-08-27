# Using the tools on your computer

The Python tools turn the live FDA + USDA APIs into the dataset, the dashboards,
and the Excel workbook. This is the workflow for running them locally (Windows
examples; macOS/Linux is the same commands).

## Install

1. **Python 3.8+** from python.org (tick "Add Python to PATH").
2. In the repo folder:
   ```powershell
   pip install -r requirements.txt
   ```
   - `curl_cffi` — required for **USDA** (gets past FSIS bot protection).
   - `pillow` — the phone home-screen icon (optional).
   - `openpyxl`, `pandas` — only for the Excel workbook.

## Update the data

```powershell
python fetch_recalls.py --year 2026     # current year
python fetch_recalls.py --year 2025     # repeat per year to backfill history
```

- Merges into `data/recalls_master.json` (+ `.csv`) — existing records are kept,
  new ones added, statuses refreshed. Safe to re-run.
- **USDA note:** if you see `USDA: fetch failed (HTTP Error 403: Forbidden)`,
  install `curl_cffi` (`pip install curl_cffi`) and re-run. FDA is unaffected.

Useful flags: `--since 2026-01-01`, `--fda-only`, `--usda-only`, `--replace`
(rebuild from scratch), `--sample` (write labeled demo rows, no network),
`--api-key KEY` (optional FDA key for higher rate limits).

## Build the outputs

```powershell
python build_dashboard.py    # → dashboard.html   (desktop, self-contained)
python build_mobile.py       # → recall_monitor_mobile.html (phone app)
python build_workbook.py     # → Food_Recall_Tracker.xlsx  (8 tabs)
```

To publish the web outputs, copy them into `docs/` and push:

```powershell
copy /Y dashboard.html docs\dashboard.html
copy /Y recall_monitor_mobile.html docs\index.html
git add -A && git commit -m "Update site" && git push
```

## The workbook (`Food_Recall_Tracker.xlsx`)

8 tabs: Read Me, Master Log (filter it and the rest follow), By Region, By Food
Type, By Cause (with hazard → illness), Trends, Policy Timeline, Reference.
Aggregates are live formulas pointing at the Master Log, so filtering or pasting
new rows updates the summaries. The workbook isn't committed to the repo (it's a
local build artifact); regenerate it any time.

## Monthly rhythm

1. `python fetch_recalls.py --year <current year>`
2. `python build_dashboard.py && python build_mobile.py && python build_workbook.py`
3. Copy the two HTML files into `docs/`, commit, push.

(If you set up the daily GitHub Actions job, steps 1–3 for the web outputs happen
on their own — see [`AUTOMATE_DAILY.md`](AUTOMATE_DAILY.md). You'd still build the
Excel workbook locally when you want it.)
