@echo off
echo Starting Strategy Servers (Account 2 - Exness)...

:: Switch to current script directory (scripts/run/)
cd /d "%~dp0"

:: -----------------------------------------------------------------------------
:: Launch Strategies for Account 2
:: -----------------------------------------------------------------------------

echo Launching XAUUSD Strategy (Exness - Acc2)...
:: Exness usually uses XAUUSD or XAUUSDm
start "Strategy - XAUUSD (Exness)" "%~dp0run_bot_watchdog.bat" XAUUSD 2

echo Launching BTCUSD Strategy (Exness - Acc2)...
start "Strategy - BTCUSD (Exness)" "%~dp0run_bot_watchdog.bat" BTCUSD 2

timeout /t 1 /nobreak >nul

echo.
echo ========================================================
echo  Account 2 Strategies Launched!
echo ========================================================
echo.
pause
