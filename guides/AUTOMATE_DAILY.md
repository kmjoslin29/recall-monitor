# Auto-update once a day (GitHub Actions)

>
> **Update:** it's now confirmed that USDA can't be fetched from GitHub's cloud
> runners (they're IP-blocked). The daily workflow therefore runs on a
> **self-hosted runner** — see [`SELF_HOSTED_RUNNER.md`](SELF_HOSTED_RUNNER.md)
> for the setup. The **Task Scheduler / `.bat`** section below is still valid as
> the backup method, and the honest picture below still explains *why*.
>


This repo already includes the workflow — `.github/workflows/update-recalls.yml`.
Once a day it fetches fresh recalls, rebuilds the site into `docs/`, and commits,
which makes GitHub Pages redeploy. No computer needed.

## First, the honest picture

- **FDA is already live.** The hosted app fetches openFDA in the browser every
  time you open it, so FDA is current without any automation.
- **The daily job is really for USDA.** The browser can't fetch USDA (a CORS
  block), so USDA lives as a snapshot baked into the file; the job refreshes it.
- **The catch:** USDA's server (Akamai) blocks non-browser requests and tends to
  distrust **datacenter IPs**. On your home PC, `curl_cffi` gets past it. From
  **GitHub's servers, USDA may still return 403** even with `curl_cffi`, because
  the request comes from a cloud IP. You'll find out on the first run.
- **It degrades gracefully.** A USDA block is treated as a non-error: the job
  keeps the USDA data already in the repo and continues.
  - **Best case:** GitHub can reach USDA → fully automated daily FDA + USDA.
  - **Worst case:** GitHub can't → FDA still updates daily; USDA holds at
    whatever you last pushed from home.

For *guaranteed* USDA automation, run the fetch on your own PC on a schedule (it
runs from your home IP). See the last section.

---

## Setup

Almost all of this is done already — the workflow ships in the repo.

1. **Host the repo and enable Pages from `/docs`** — see
   [`SETUP_ON_GITHUB.md`](SETUP_ON_GITHUB.md). The daily commit triggers the
   Pages redeploy.
2. **Push your real `data/recalls_master.json`** (with USDA backfilled from your
   PC) before the first run, so your good USDA data is present even if GitHub
   can't fetch it.
3. **Enable Actions if prompted.** Open the **Actions** tab; if it asks, enable
   workflows. The workflow already grants itself write access
   (`permissions: contents: write`). If a push ever fails, set **Settings →
   Actions → General → Workflow permissions → Read and write**.
4. **Test it now.** Actions tab → **Update recall data → Run workflow**. Watch the
   **Fetch recalls** step:
   - `USDA: fetched N records … (via curl_cffi)` → GitHub can reach USDA. 🎉
   - `USDA: blocked with 403 …` → FDA-only automation (still fine).
   If it commits, your Pages site updates in a minute or two.

After that it runs daily on the `cron` schedule (08:17 UTC — edit if you like).

## Things worth knowing

- **Timing isn't exact.** GitHub can delay scheduled runs; expect "once a day,
  roughly."
- **A commit appears daily even with no new recalls** — each fetch restamps a
  timestamp, so the file changes. Normal.
- **Inactive repos pause schedules** after ~60 days with no activity; a daily
  commit keeps it alive. If it ever stops, re-enable it from the Actions tab.

---

## Alternative: schedule it on your own PC (guaranteed USDA)

Run the update from home, where `curl_cffi` already works, and push the result.

1. Create `daily_update.bat` in your local repo folder:

   ```bat
   cd /d "D:\path\to\recall-monitor"
   python fetch_recalls.py --year %date:~-4%
   python build_dashboard.py
   python build_mobile.py
   copy /Y dashboard.html docs\dashboard.html
   copy /Y recall_monitor_mobile.html docs\index.html
   git add -A
   git commit -m "Daily update"
   git push
   ```

2. **Task Scheduler → Create Basic Task → Daily → Start a program →** point it at
   `daily_update.bat`.

Runs from your home IP (USDA reachable) but only when your PC is on. Use it
instead of, or alongside, the GitHub job.
