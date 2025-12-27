@echo off
title AI Crypto Trading Bot Watchdog
color 0a

:: 切换到脚本所在目录
cd /d "%~dp0"

:loop
echo [%DATE% %TIME%] Starting Crypto Trading Bot...
echo ---------------------------------------------------
:: 运行 Python 交易机器人脚本
python crypto/trading_bot.py %*

echo ---------------------------------------------------
echo [%DATE% %TIME%] Bot crashed or stopped. Restarting in 5 seconds...
timeout /t 5
goto loop