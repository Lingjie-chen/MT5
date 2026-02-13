@echo off
title AI Multi-Symbol Trading Bot (Gold/ETH)
color 0a

:: Switch to script directory's parent (project root)
cd /d "%~dp0\..\.."

:: Activate Virtual Environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found at venv\Scripts\activate.bat
)

:loop
echo [%DATE% %TIME%] Starting Multi-Symbol AI Trading Bot...
echo ---------------------------------------------------
echo Supported Symbols: ALL (Auto-Discovery)
echo Usage: run_bot_watchdog.bat [Symbol] [AccountIndex]
echo Default: GOLD, Account 1
echo ---------------------------------------------------

:: Run as module, passing all arguments
:: Ensure python is in your PATH
python -m src.trading_bot.main %*

echo ---------------------------------------------------
echo [%DATE% %TIME%] Bot crashed or stopped. Restarting in 5 seconds...
timeout /t 5
goto loop