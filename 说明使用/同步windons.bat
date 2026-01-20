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

echo ===================================================
echo Quant Trading System Startup
echo ===================================================

echo [1/3] Starting API Server...
start "Quant API Server" cmd /k "call venv\Scripts\activate.bat && python -m uvicorn gold.server.main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/3] Starting Dashboard...
start "Quant Dashboard" cmd /k "call venv\Scripts\activate.bat && streamlit run dashboard.py"

echo [3/3] Starting Auto Sync Engine...
python scripts\checkpoint_dbs.py

pause