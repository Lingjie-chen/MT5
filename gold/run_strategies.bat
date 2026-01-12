@echo off
echo Starting Strategy Servers with Auto-Restart Watchdogs...

:: 切换到脚本所在目录的上一级目录（项目根目录）
cd /d "%~dp0\.."

:: -----------------------------------------------------------------------------
:: GOLD Strategy Launcher
:: -----------------------------------------------------------------------------
echo Launching GOLD Strategy...
:: 使用 cmd /k 替代 cmd /c 以保持窗口打开，方便查看报错
:: 移除 cd .. 因为主脚本已经切换到了根目录，start 会继承当前目录
start "Strategy - GOLD" cmd /k "title Strategy - GOLD & :loop & echo [%DATE% %TIME%] Starting GOLD Bot... & python -m gold.start GOLD & echo. & echo [%DATE% %TIME%] Bot Stopped/Crashed! Restarting in 5s... & timeout /t 5 & goto loop"
timeout /t 1 /nobreak >nul

:: -----------------------------------------------------------------------------
:: ETHUSD Strategy Launcher
:: -----------------------------------------------------------------------------
echo Launching ETHUSD Strategy...
start "Strategy - ETHUSD" cmd /k "title Strategy - ETHUSD & :loop & echo [%DATE% %TIME%] Starting ETHUSD Bot... & python -m gold.start ETHUSD & echo. & echo [%DATE% %TIME%] Bot Stopped/Crashed! Restarting in 5s... & timeout /t 5 & goto loop"
timeout /t 1 /nobreak >nul

:: -----------------------------------------------------------------------------
:: EURUSD Strategy Launcher
:: -----------------------------------------------------------------------------
echo Launching EURUSD Strategy...
start "Strategy - EURUSD" cmd /k "title Strategy - EURUSD & :loop & echo [%DATE% %TIME%] Starting EURUSD Bot... & python -m gold.start EURUSD & echo. & echo [%DATE% %TIME%] Bot Stopped/Crashed! Restarting in 5s... & timeout /t 5 & goto loop"

echo.
echo ========================================================
echo  All 3 strategies have been launched in separate windows.
echo  You can now close this launcher window.
echo  The strategy windows will stay open and auto-restart.
echo ========================================================
echo.
pause
