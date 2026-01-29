@echo off
title AI Trading Dashboard
color 0d

:: Navigate to the project root directory (two levels up from scripts/run)
cd /d "%~dp0\..\.."

echo [%DATE% %TIME%] Starting AI Trading Dashboard...
echo ---------------------------------------------------
echo Access the dashboard at http://localhost:8501
echo ---------------------------------------------------

:: Activate Virtual Environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found at venv\Scripts\activate.bat
)

:loop
:: Run Streamlit pointing to the correct location in src
python -m streamlit run src/trading_bot/analysis/dashboard.py --server.port 8501 --server.address localhost --server.headless true

:: If Streamlit exits, restart it
echo [%DATE% %TIME%] Dashboard process ended. Restarting in 5 seconds...
timeout /t 5
goto loop
