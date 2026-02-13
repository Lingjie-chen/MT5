@echo off
echo Starting Strategy Servers (Account 3 - Ava Demo)...

:: Switch to current script directory (scripts/run/)
cd /d "%~dp0"

:: -----------------------------------------------------------------------------
:: Launch Strategies for Account 3
:: -----------------------------------------------------------------------------

echo Launching GOLD Strategy (Ava Demo - Acc3)...
start "Strategy - GOLD (Ava Demo)" "%~dp0run_bot_watchdog.bat" GOLD 3


timeout /t 1 /nobreak >nul

echo.
echo ========================================================
echo  Account 3 Strategies Launched!
echo ========================================================
echo.
pause
