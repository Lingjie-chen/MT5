@echo off
chcp 65001 >nul
cd /d "%~dp0\..\.."

:: Check venv
if not exist venv\Scripts\activate.bat (
    echo [ERROR] venv not found. Run setup_env.bat first.
    pause
    exit /b
)

:: Activate venv
call venv\Scripts\activate.bat

:: Add current dir to PYTHONPATH
set PYTHONPATH=%PYTHONPATH%;%cd%

:: --- Fix Git State (Auto-Unlock & Sync) ---
if exist .git\index.lock (
    echo [INFO] Removing stale .git/index.lock...
    del /F /Q .git\index.lock
)

echo [INFO] Ensuring Git Consistency...
:: 1. Handle Detached HEAD / Ensure master
git symbolic-ref -q HEAD >nul
if %errorlevel% neq 0 (
    echo [WARN] Detached HEAD detected. Checking out master...
    git checkout master
)

:: 2. Save local state
git add .
git commit -m "auto: save before sync" >nul 2>&1

:: 3. Pull Remote (Rebase strategy: Apply local changes ON TOP of remote)
:: -X theirs means: In case of conflict, keep OUR local changes
echo [INFO] Pulling remote updates...
git pull origin master --rebase -X theirs
if %errorlevel% neq 0 (
    echo [WARN] Rebase failed. Trying standard merge (keeping local data)...
    git rebase --abort >nul 2>&1
    git pull origin master --strategy-option=ours --no-edit
)
:: -----------------------------------

echo ===================================================
echo Quant Trading System Startup
echo ===================================================

:: Check PostgreSQL
echo [Checking PostgreSQL...]
powershell -Command "if (Test-NetConnection -ComputerName localhost -Port 5432 -InformationLevel Quiet) { Write-Host '[OK] PostgreSQL is running on port 5432.' -ForegroundColor Green } else { Write-Host '[ERROR] PostgreSQL is NOT running on port 5432.' -ForegroundColor Red; Write-Host '   Please ensure local DB or Tunnel is active.' -ForegroundColor Yellow }"

echo.
echo [1/2] Starting API Server...
start "Quant API Server" cmd /k "call venv\Scripts\activate.bat && python -m uvicorn src.trading_bot.server.main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/2] Starting Auto Sync Engine...
echo Logs will be written to auto_sync_engine.log

:: Auto-resolve Git conflicts
python scripts\maintenance\git_auto_resolve.py

:: Fix "modify/delete" conflicts (Remote deleted, Local modified -> Keep Local)
git status | findstr "deleted by them" > nul
if %errorlevel% equ 0 (
    echo [WARN] Conflict "deleted by them" detected. Keeping local files...
    git add .
    git commit -m "auto: resolve modify/delete conflict"
)

:: Auto-repair Database
python scripts\maintenance\db_auto_repair.py

:: Merge Archived DBs to Main
echo [INFO] Consolidating databases...
python scripts\maintenance\consolidate_dbs.py

:: 3. Backup PostgreSQL to GitHub
echo [INFO] Backing up PostgreSQL data to GitHub...
python scripts\maintenance\backup_postgres.py

:: Run the engine
python scripts\maintenance\checkpoint_dbs.py

pause
