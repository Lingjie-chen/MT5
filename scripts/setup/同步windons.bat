@echo off
cd /d "%~dp0\.."

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

:: --- Fix Git State (Auto-Unlock) ---
if exist .git\index.lock (
    echo 🗑️ Removing stale .git/index.lock...
    del /F /Q .git\index.lock
)
:: -----------------------------------

echo ===================================================
echo Quant Trading System Startup
echo ===================================================

:: Check PostgreSQL
echo [Checking PostgreSQL...]
powershell -Command "if (Test-NetConnection -ComputerName localhost -Port 5432 -InformationLevel Quiet) { Write-Host '✅ PostgreSQL is running on port 5432.' -ForegroundColor Green } else { Write-Host '❌ PostgreSQL is NOT running on port 5432.' -ForegroundColor Red; Write-Host '   Please ensure local DB or Tunnel is active.' -ForegroundColor Yellow }"

echo.
echo [1/2] Starting API Server...
start "Quant API Server" cmd /k "call venv\Scripts\activate.bat && python -m src.trading_bot.server.main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/2] Starting Auto Sync Engine...
echo Logs will be written to auto_sync_engine.log

:: Auto-resolve Git conflicts
python scripts\maintenance\git_auto_resolve.py

:: Fix "modify/delete" conflicts (Remote deleted, Local modified -> Keep Local)
git status | findstr "deleted by them" > nul
if %errorlevel% equ 0 (
    echo ⚠️ Conflict "deleted by them" detected. Keeping local files...
    git add .
    git commit -m "auto: resolve modify/delete conflict"
)

:: Auto-repair Database
python scripts\maintenance\db_auto_repair.py

:: Merge Archived DBs to Main
echo 📦 Consolidating databases...
python scripts\maintenance\consolidate_dbs.py

:: 3. Backup PostgreSQL to GitHub
echo 📦 Backing up PostgreSQL data to GitHub...
python scripts\maintenance\backup_postgres.py

:: Run the engine
python scripts\maintenance\checkpoint_dbs.py

pause
