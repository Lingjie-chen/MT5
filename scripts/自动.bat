@echo off
title DB Checkpoint & Auto-Update Service
color 0b

:: Switch to project root
cd /d "%~dp0\.."

echo [%DATE% %TIME%] Starting Database Checkpoint & Sync Service (Windows)...
echo Intervals: Every 60 seconds
echo ---------------------------------------------------

:: ===================================================
:: NETWORK PROXY SETTINGS (Optional / Network Fix)
:: If you see "Failed to connect to github.com", uncomment the line below:
set "https_proxy=http://127.0.0.1:7897"
:: ===================================================

:: Check and Configure Git Identity if missing
git config user.email >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Configuring default Git user...
    git config user.email "bot@quant.trading"
    git config user.name "QuantTradingBot"
)

:loop
echo.
echo ===================================================
echo [%DATE% %TIME%] Starting Sync Cycle...

:: 1. Run Checkpoint Script
:: This script handles DB WAL checkpointing to ensure data integrity
python scripts/checkpoint_dbs.py

:: 2. Pull Remote Changes (Robust Sync)
echo [%DATE% %TIME%] Checking for remote updates...
git pull --no-edit origin master
if %ERRORLEVEL% EQU 0 goto commit_step

echo [WARNING] Pull failed or conflict detected.
echo [INFO] Attempting auto-resolve using 'ours' strategy...
:: Strategy: recursive -X ours (Keep local changes in case of conflict)
git pull --no-edit -s recursive -X ours origin master

if %ERRORLEVEL% EQU 0 (
    echo [INFO] Conflict resolved automatically.
    goto commit_step
)

echo [ERROR] Auto-resolve failed. Aborting merge...
git merge --abort 2>nul

:commit_step
:: 3. Commit Local Changes
:: We try to add and commit. If nothing to commit, git will just exit with non-zero, which we ignore.
echo [%DATE% %TIME%] Checking local changes...
git add .
git commit -m "auto: sync updates %DATE% %TIME%" >nul 2>&1

:: 4. Push to Remote
echo [%DATE% %TIME%] Pushing to GitHub...
git push origin master
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Push complete.
) else (
    echo [ERROR] Push failed. Will retry next cycle.
)

echo [%DATE% %TIME%] Cycle Complete.
echo ===================================================
echo Waiting 60 seconds...
timeout /t 60 >nul
goto loop
