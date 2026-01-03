@echo off
title DB Checkpoint & Auto-Update Service
color 0b

:: 检查是否运行在 macOS (通过检查 uname 命令是否存在)
where uname >nul 2>nul
if %errorlevel%==0 (
    echo Detected Unix-like environment (possibly Mac/Linux under simulation).
    echo Switching to Shell Script Loop Mode...
    sh "%~dp0\auto_push.sh" --loop
    exit /b
)

cd /d "%~dp0\.."

echo [%DATE% %TIME%] Starting Database Checkpoint & Sync Service (Windows)...
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
