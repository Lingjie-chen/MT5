@echo off
title AI Trading Dashboard
color 0d

:: Navigate to the project root directory (one level up from scripts)
cd /d "%~dp0\.."

echo [%DATE% %TIME%] Starting AI Trading Dashboard...
echo ---------------------------------------------------
echo Access the dashboard at http://localhost:8501
echo ---------------------------------------------------

:loop
:: Run Streamlit
streamlit run dashboard.py --server.port 8501 --server.address localhost --server.headless true

:: If Streamlit exits, restart it
echo [%DATE% %TIME%] Dashboard process ended. Restarting in 5 seconds...
timeout /t 5
goto loop
