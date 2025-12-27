@echo off
title MT5 Data Auto-Sync Service
color 0b

cd /d "%~dp0"

:loop
echo [%DATE% %TIME%] Starting MT5 Data Auto-Sync Service...
echo ---------------------------------------------------
python auto_sync_db.py
echo ---------------------------------------------------
echo [%DATE% %TIME%] Service stopped. Restarting in 10 seconds...
timeout /t 10
goto loop
