# Fully-automatic USDA: self-hosted runner (+ a backup script)

USDA's server blocks GitHub's cloud servers, so the daily job can't fetch USDA
from GitHub's own runners. The fix is to run the job on **your PC** instead —
GitHub calls this a *self-hosted runner*. It runs from your home IP, where
`curl_cffi` gets past the block, so FDA **and** USDA update automatically.

The included workflow (`.github/workflows/update-recalls.yml`) is already set to
use a self-hosted Windows runner (`runs-on: [self-hosted, Windows, X64]`). You
just need to register one.

---

## ⚠ Read first: security on a public repo

GitHub recommends **not** using self-hosted runners on **public** repositories,
because a malicious pull request could run code on your machine. Two things make
this safe enough here, but do both:

1. **This workflow never runs on pull requests** — only on a schedule and manual
   runs. So a fork PR cannot trigger it on your runner. (Don't add a
   `pull_request:` trigger to it.)
2. **Lock down fork PRs anyway:** repo **Settings → Actions → General →**
   - *Fork pull request workflows from outside collaborators* → **Require
     approval for all external contributors**.
   - Leave *Actions permissions* as-is; you don't need PRs building here.

If you'd rather not run a self-hosted runner on a public repo at all, skip to
[**Backup: scheduled script**](#backup-scheduled-script) — it does the same job
with none of this risk. (Or, with GitHub Pro, make the repo **private**; Pages
then works privately and the runner risk drops.)

---

## Prerequisites

- Python, `git`, and `pip` installed and on your PATH (you already have these —
  you've been running the tools and pushing).
- The repo pushed to GitHub with Pages serving `/docs` (see
  [`SETUP_ON_GITHUB.md`](SETUP_ON_GITHUB.md)).

## 1. Register the runner

1. In your repo: **Settings → Actions → Runners → New self-hosted runner**.
2. Choose **Windows** / **x64**. GitHub shows a short script with a **token that
   expires in ~1 hour** — copy the commands from *that page* (they include your
   token). They look like this:

   ```powershell
   # Create a folder and download the runner
   mkdir C:\actions-runner ; cd C:\actions-runner
   Invoke-WebRequest -Uri https://github.com/actions/runner/releases/download/vX.Y.Z/actions-runner-win-x64-X.Y.Z.zip -OutFile runner.zip
   Add-Type -AssemblyName System.IO.Compression.FileSystem ;
   [System.IO.Compression.ZipFile]::ExtractToDirectory("$PWD/runner.zip", "$PWD")

   # Register it with your repo (token is from the GitHub page)
   ./config.cmd --url https://github.com/<username>/recall-monitor --token <TOKEN>
   ```

3. During `config.cmd`, press **Enter** to accept the defaults (runner group,
   name, and the default labels `self-hosted`, `Windows`, `X64` — the workflow
   relies on these). When it asks **"Run as service?"**, answer **Y** so it
   starts automatically on boot.

## 2. Make sure the service can find Python

If the runner runs as a Windows service under the wrong account, it may not see
`python`/`git`. If a run fails with "python not found":

- Open **services.msc**, find **"GitHub Actions Runner (recall-monitor)"** →
  **Properties → Log On → This account**, and enter your Windows username and
  password → OK → restart the service.

(Alternatively, instead of the service, run `./run.cmd` in a PowerShell window
under your own account — it runs only while that window is open.)

## 3. Confirm it's connected

Back on **Settings → Actions → Runners**, your runner should show a green
**Idle** dot. The workflow is already pointed at it — nothing to change.

## 4. Test it

**Actions → Update recall data → Run workflow.** Watch the run happen *on your
machine*. In the **Fetch recalls** step, the USDA line should read
`USDA: fetched N records … (via curl_cffi)`. If it commits, your Pages site
updates in a minute or two.

After that it runs daily on the schedule, whenever your PC (and the runner) are
on. If the PC is off at 08:17 UTC, that day's run waits for the runner or is
skipped — which is fine: the phone app still fetches FDA live on every open, and
USDA is low-volume, so an occasional missed day doesn't matter.

## Managing the runner

- **Status / start / stop:** services.msc → the "GitHub Actions Runner" service.
- **Remove it:** in the runner folder, `./config.cmd remove --token <TOKEN>`
  (get a fresh remove-token from the Runners page).
- **Keep it updated:** the runner self-updates; no action needed usually.

---

## Backup: scheduled script

`update_recalls.bat` (in the repo root) does the same fetch-build-push from your
home IP, on demand or on a schedule — a safety net if the runner is off, and the
zero-risk alternative if you prefer not to run a runner on a public repo.

1. **Edit the path** at the top of `update_recalls.bat` to your local clone, e.g.
   `set "REPO=D:\...\recall-monitor"`.
2. Double-click it any time to force an update (it pulls first, so it won't
   clash with the runner's commits).
3. **To schedule it:** open **Task Scheduler → Create Basic Task →** choose a
   cadence (weekly is plenty for USDA) **→ Start a program →** point it at
   `update_recalls.bat`.

You can run the runner and the script together; both `git pull --rebase` first,
so they won't step on each other.

---

## Which should I rely on?

- **Runner** — most automatic (no PC scheduling), but has the public-repo caveat
  above and only runs when your PC is on.
- **Script + Task Scheduler** — no security caveat, dead simple, but only runs
  when your PC is on and you've scheduled it.

Either keeps USDA current; together they're belt-and-suspenders. FDA stays fresh
regardless, since the phone app fetches it live on every open.
