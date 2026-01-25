@echo off
echo Starting Strategy Servers for Exness (Account 2)...

:: Switch to current script directory (scripts/run/)
cd /d "%~dp0"

:: -----------------------------------------------------------------------------
:: Launch Strategies for Exness
:: Using Account 2 credentials from .env
:: -----------------------------------------------------------------------------

echo Launching Exness GOLD Strategy...
start "Exness - GOLD" run_bot_watchdog.bat GOLD --account 2
timeout /t 1 /nobreak >nul

echo Launching Exness ETHUSD Strategy...
start "Exness - ETHUSD" run_bot_watchdog.bat ETHUSD --account 2
timeout /t 1 /nobreak >nul

echo Launching Exness EURUSD Strategy...
start "Exness - EURUSD" run_bot_watchdog.bat EURUSD --account 2

echo.
echo ========================================================
echo  Exness strategies have been launched in separate windows.
echo  Account: 2 (Exness)
echo ========================================================
echo.
pause
