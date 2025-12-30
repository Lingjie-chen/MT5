@echo off
title DB Checkpoint Service
color 0b

cd /d "%~dp0\.."

echo [%DATE% %TIME%] Starting Database Checkpoint Service...
echo Intervals: Every 60 seconds
echo ---------------------------------------------------

:loop
:: Run the python script in loop mode
python scripts/checkpoint_dbs.py --loop --interval 60

:: If the python script exits for some reason, restart it
echo [%DATE% %TIME%] Service stopped unexpectedly. Restarting in 5 seconds...
timeout /t 5
goto loop
