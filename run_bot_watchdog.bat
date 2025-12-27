@echo off
title AI Trading Bot Watchdog
color 0a

cd /d "%~dp0"

:loop
echo [%DATE% %TIME%] Starting Trading Bot...
echo ---------------------------------------------------
:: 使用 python 直接运行脚本，确保 python 在环境变量中
:: 传递所有命令行参数给 start.py (例如: run_bot_watchdog.bat EURUSD)
python start.py %*

echo ---------------------------------------------------
echo [%DATE% %TIME%] Bot crashed or stopped. Restarting in 5 seconds...
timeout /t 5
goto loop
