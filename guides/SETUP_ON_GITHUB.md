# Host it on GitHub Pages

This publishes the app at a real `https://…` address so it works on your iPhone
(live FDA fetch and Add-to-Home-Screen both need a hosted URL — neither works
from a local file). The published site lives in the **`docs/`** folder.

Time: about 5 minutes.

---

## 1. Put this repo on GitHub

**If you're replacing an existing repo,** you can either delete the old one and
create a fresh one, or push these files over it. Either way you want the repo to
contain this whole folder structure (code at the root, `docs/`, `.github/`).

**Web upload (no tools):**
1. Create a repository (**+ → New repository**), name it e.g. `recall-monitor`,
   set it **Public** (free GitHub Pages needs a public repo), and create it.
2. **Add file → Upload files**, then drag in everything from this repo. Drag the
   **folders** (`data`, `docs`, `guides`, `.github`) so the structure is kept.
3. Commit.

**Git (keeps folders automatically):**
```bash
cd recall-monitor
git init
git add -A
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<username>/recall-monitor.git
git push -u origin main
```

> `.github/` and `.nojekyll` start with a dot and can look "missing" in the web
> uploader — the Git method avoids that fiddliness.

## 2. Turn on GitHub Pages (serve the `docs/` folder)

1. Repo **Settings → Pages**.
2. **Build and deployment → Source:** *Deploy from a branch*.
3. **Branch:** `main`, **Folder:** `/docs`. **Save**.
4. Wait ~1 minute, refresh. It shows **"Your site is live at
   https://<username>.github.io/recall-monitor/"**.

## 3. Open it on your iPhone

- Mobile app: `https://<username>.github.io/recall-monitor/`
- Desktop dashboard (nice on a computer): add `dashboard.html` to that URL.

In Safari, tap **Share → Add to Home Screen**. It launches full-screen and
re-fetches FDA when opened.

---

## Put your real data in it

The repo ships with the small **sample** dataset so the site renders immediately.
To publish your real recalls, replace **`data/recalls_master.json`** with your
backfilled copy (the one you built on your PC with USDA included), then rebuild
and push:

```bash
python build_dashboard.py
python build_mobile.py
cp dashboard.html docs/dashboard.html
cp recall_monitor_mobile.html docs/index.html
git add -A && git commit -m "Publish real data" && git push
```

Or skip this and let the daily workflow populate it — see
[`AUTOMATE_DAILY.md`](AUTOMATE_DAILY.md). (Pushing your real master first is still
best, so USDA is present even if GitHub can't fetch it.)

## Troubleshooting

- **404 after enabling Pages.** Give it a minute; confirm Source = *Deploy from a
  branch*, Branch = `main`, Folder = `/docs`, and that `docs/index.html` exists.
- **Old data after an update.** It's cached. Close and reopen the home-screen app,
  or hard-refresh in Safari; GitHub's CDN can lag a couple of minutes.
- **`USDA ▲ blocked` pill on the phone.** Expected — browsers can't fetch USDA
  (CORS). USDA comes from the embedded snapshot, so rebuild after backfilling
  USDA on your computer. `FDA ● N` means FDA came in live.
