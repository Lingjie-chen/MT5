@echo off
echo Starting Generic Strategy Launcher...
echo.
echo Usage: run_generic_strategy.bat [SYMBOL] [ACCOUNT_INDEX]
echo Example: run_generic_strategy.bat GBPUSD 1
echo.

set /p SYMBOL="Enter Symbol (e.g. GOLD, EURUSD, BTCUSD): "
set /p ACCOUNT="Enter Account Index (1, 2, or 3): "

if "%SYMBOL%"=="" set SYMBOL=GOLD
if "%ACCOUNT%"=="" set ACCOUNT=1

:: Switch to current script directory (scripts/run/)
cd /d "%~dp0"

echo.
echo Launching %SYMBOL% Strategy (Account %ACCOUNT%)...
start "Strategy - %SYMBOL% (Acc %ACCOUNT%)" "%~dp0run_bot_watchdog.bat" %SYMBOL% %ACCOUNT%

echo.
echo Strategy launched in new window.
echo.
pause
