@echo off
REM ===========================================================================
REM  US Food Recall Monitor - local update (backup to the self-hosted runner)
REM  Fetches FDA + USDA from your home IP, rebuilds the site, and pushes.
REM  Use it any time you want to force an update, or if the runner is off.
REM ===========================================================================

REM --- EDIT THIS to the full path of your local clone of the repo ----------
set "REPO=D:\path\to\recall-monitor"
REM ------------------------------------------------------------------------

setlocal enabledelayedexpansion
cd /d "%REPO%" || (echo Could not find repo folder: %REPO% & pause & exit /b 1)

echo Syncing with GitHub...
git pull --rebase --autostash

for /f %%y in ('powershell -NoProfile -Command "(Get-Date).Year"') do set "YEAR=%%y"
set /a PREV=%YEAR%-1

echo Fetching recalls for %YEAR% and %PREV% ...
python fetch_recalls.py --year %YEAR%
python fetch_recalls.py --year %PREV%

echo Rebuilding site...
python build_dashboard.py
python build_mobile.py
if not exist docs mkdir docs
copy /Y dashboard.html docs\dashboard.html >nul
copy /Y recall_monitor_mobile.html docs\index.html >nul
type nul > docs\.nojekyll

echo Publishing...
git add -A
git commit -m "Local update %YEAR%-%date%" || echo No changes to commit.
git push

echo.
echo Done.
pause
endlocal
