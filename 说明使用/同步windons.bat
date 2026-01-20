@echo off
:: One-Click Start for Auto Sync Engine (Windows)

:: Ensure we are in the project root
:: Because this script is in "说明使用", we need to go up one level to project root
cd /d "%~dp0\.."

:: 0. Check Environment
if not exist venv (
    echo ⚠️  Virtual environment not found!
    echo 🚀 Launching Setup Script first...
    call "说明使用\setup_env.bat"
)

:: 1. Activate Virtual Environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

:: Add current directory to PYTHONPATH so python can find modules
set PYTHONPATH=%PYTHONPATH%;%cd%

echo 🚀 Starting Auto Sync Engine...
echo Logs will be written to auto_sync_engine.log

:: Basic check for Postgres port (optional)
netstat -an | find "5432" >nul
if errorlevel 1 (
    echo ⚠️  Warning: PostgreSQL port 5432 not detected.
    echo    Please ensure your remote DB tunnel or local DB is active.
)

:: Run the engine
python scripts\checkpoint_dbs.py

pause