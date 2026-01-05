@echo off
title AI Crypto Trading Bot Watchdog
color 0a

:: 切换到脚本所在目录
cd /d "%~dp0"

:: 切换到上级目录(项目根目录)，以便作为模块运行
cd ..

:loop
echo [%DATE% %TIME%] Starting Crypto Trading Bot...
echo ---------------------------------------------------
:: 以模块方式运行，确保包导入正确
python -m crypto.trading_bot %*

echo ---------------------------------------------------
echo [%DATE% %TIME%] Bot crashed or stopped. Restarting in 5 seconds...
timeout /t 5
goto loop