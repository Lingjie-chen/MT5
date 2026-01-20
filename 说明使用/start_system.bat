@echo off
title Quant Trading System (Data Server & Auto-Sync)
color 0b

:: Switch to project root
cd /d "%~dp0.."

echo 🚀 Starting Quant Trading System...
echo ===================================================

:: 1. Environment Check
if not exist venv (
    echo ❌ Virtual environment not found. Please run 'setup_env.bat' first.
    pause
    exit /b
)

:: 2. Activate Virtual Environment
echo 🟢 Activating virtual environment...
call venv\Scripts\activate

:: 2.5 Fix Git State (Auto-Commit & Lock Removal)
echo 🛠️ Ensuring clean Git state...
:: Kill any stale git processes that might be locking files
taskkill /F /IM git.exe >nul 2>&1
:: Remove lock file if it exists
if exist .git\index.lock (
    echo 🗑️ Removing stale .git/index.lock...
    del /F /Q .git\index.lock
)
:: Auto-commit to prevent overwrite errors
echo 💾 Auto-saving local DB changes...
git add gold/trading_data.db
git commit -m "Auto-save trading_data.db on startup"

:: 2.6 Sync Code (Pull & Push)
echo 🔄 Syncing with GitHub (Pull & Push)...

:: PULL: Get remote updates
echo ⬇️ Pulling latest code...
git pull origin master
if %errorlevel% neq 0 (
    echo ⚠️ Standard pull failed. Attempting auto-resolve (Strategy: ours)...
    git pull --no-edit -s recursive -X ours origin master
    if %errorlevel% neq 0 echo ❌ Auto-resolve failed. Please resolve conflicts manually.
)

:: PUSH: Upload local changes
echo ⬆️ Pushing local changes...
git push origin master
if %errorlevel% equ 0 (
    echo ✅ Push successful.
) else (
    echo ⚠️ Push failed. Will retry in background service.
)

:: 3. Secure Cleanup (Sync -> Verify -> Delete)
echo 🧹 Starting Secure Cleanup...
:: This will upload local DBs to Postgres, verify them, and safely delete local files
python scripts/checkpoint_dbs.py --cleanup --no-git

:: 4. Start Background Sync Service (in a separate window)
echo 🔄 Starting Background Sync & Cleanup Service...
:: This script handles:
::   - Periodic DB Checkpoints (WAL merge)
::   - Git Auto-Sync (Pull/Push) - automatically enabled
::   - Auto-Cleanup of local DBs (Safe Mode: Syncs to Postgres -> Verifies -> Deletes)
start "Background Sync Service" cmd /c "python scripts/checkpoint_dbs.py --loop --cleanup --interval 60"

:: 5. Start Data Server (Blocking Process)
echo 🟢 Starting Data Server (FastAPI)...
echo 📡 This server enables real-time data sync to PostgreSQL.
echo (Press Ctrl+C to stop the server)
echo.

uvicorn gold.server.main:app --host 0.0.0.0 --port 8000 --reload

:: If server stops, we pause
pause