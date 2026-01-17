@echo off
title AI Multi-Symbol Trading Bot (Gold/ETH)
color 0a

:: Switch to script directory's parent (project root)
cd /d "%~dp0\.."

:loop
echo [%DATE% %TIME%] Starting Multi-Symbol AI Trading Bot...
echo ---------------------------------------------------
echo Supported Symbols: GOLD, ETHUSD, EURUSD, XAUUSDm, ETHUSDm, EURUSDm
echo Usage: run_bot_watchdog.bat [Symbol1,Symbol2,...] [--account N]
echo Default: GOLD, XAUUSDm, ETHUSD, ETHUSDm, EURUSD, EURUSDm
echo ---------------------------------------------------

:: Run as module, passing all arguments
:: Ensure python is in your PATH
python -m gold.start %*

echo ---------------------------------------------------
echo [%DATE% %TIME%] Bot crashed or stopped. Restarting in 5 seconds...
timeout /t 5
goto loop