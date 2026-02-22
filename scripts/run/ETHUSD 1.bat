@echo off
echo Starting Strategy Servers (Account 1 - Ava Real)...

:: Switch to current script directory (scripts/run/)
cd /d "%~dp0"

:: -----------------------------------------------------------------------------
:: Launch Strategies for Account 1
:: -----------------------------------------------------------------------------

echo Launching ETHUSD Strategy (Ava Real - Acc1)...
start "Strategy - ETHUSD (Ava Real)" "%~dp0run_bot_watchdog.bat" ETHUSD 1

timeout /t 1 /nobreak >nul

echo.
echo ========================================================
echo  Account 1 Strategies Launched!
echo ========================================================
echo.
pause
