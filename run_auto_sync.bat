@echo off
title MT5 Data Auto-Sync Service
echo Starting MT5 Data Auto-Sync Service...
echo Press Ctrl+C to stop.
echo Logs are saved to auto_sync.log

python auto_sync_db.py

pause
