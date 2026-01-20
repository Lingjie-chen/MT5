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

:: 3. Auto Data Migration (One-time check on startup)
echo 🔄 Checking for local SQLite data to migrate...
:: This will upload any existing .db files to PostgreSQL
python migrate_sqlite_to_postgres.py

:: 4. Start Background Sync Service (in a separate window)
echo 🔄 Starting Background Sync & Cleanup Service...
:: This script handles:
::   - Periodic DB Checkpoints (WAL merge)
::   - Git Auto-Sync (Pull/Push)
::   - Auto-Cleanup of local DBs after successful sync
start "Background Sync Service" cmd /c "python scripts/checkpoint_dbs.py --loop --cleanup --interval 60"

:: 5. Start Data Server (Blocking Process)
echo 🟢 Starting Data Server (FastAPI)...
echo 📡 This server enables real-time data sync to PostgreSQL.
echo (Press Ctrl+C to stop the server)
echo.

uvicorn gold.server.main:app --host 0.0.0.0 --port 8000 --reload

:: If server stops, we pause
pause