@echo off
title DB Checkpoint & Auto-Update Service
color 0b

cd /d "%~dp0\.."

echo [%DATE% %TIME%] Starting Database Checkpoint & Sync Service...
echo Intervals: Every 60 seconds
echo ---------------------------------------------------

:loop
echo.
echo ===================================================
echo [%DATE% %TIME%] Starting Sync Cycle...

:: 1. Run Checkpoint Script (Commits local changes if any)
:: Removed --loop to allow batch file to handle the loop and git operations
python scripts/checkpoint_dbs.py

:: 2. Pull Remote Changes (Auto-Update Code)
echo [%DATE% %TIME%] Checking for remote updates...
git pull origin master

:: 3. Push Any Pending Commits (Retry push if python script failed or after merge)
echo [%DATE% %TIME%] Pushing local changes...
git push origin master

echo [%DATE% %TIME%] Cycle Complete.
echo ===================================================
echo Waiting 60 seconds...
timeout /t 60 >nul
goto loop
