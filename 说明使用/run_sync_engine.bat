@echo off
:: One-Click Start for Auto Sync Engine (Windows)

:: Ensure we are in the project root
cd /d "%~dp0"

:: Add current directory to PYTHONPATH so python can find modules
set PYTHONPATH=%PYTHONPATH%;%cd%

echo 🚀 Starting Auto Sync Engine...
echo Logs will be written to auto_sync_engine.log

:: Run the engine
python scripts\checkpoint_dbs.py

pause