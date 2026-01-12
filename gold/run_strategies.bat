@echo off
echo Starting Strategy Servers with Auto-Restart Watchdogs...

:: -----------------------------------------------------------------------------
:: GOLD Strategy Launcher
:: -----------------------------------------------------------------------------
echo Launching GOLD Strategy...
:: 使用 & 替代 &&，确保即使 python 报错也会执行后续的重启逻辑
:: Run as module: python -m gold.start
start "Strategy - GOLD" cmd /c "title Strategy - GOLD & cd .. & :loop & echo [%DATE% %TIME%] Starting GOLD Bot... & python -m gold.start GOLD & echo. & echo [%DATE% %TIME%] Bot Stopped/Crashed! Restarting in 5s... & timeout /t 5 & goto loop"
timeout /t 1 /nobreak >nul

:: -----------------------------------------------------------------------------
:: ETHUSD Strategy Launcher
:: -----------------------------------------------------------------------------
echo Launching ETHUSD Strategy...
start "Strategy - ETHUSD" cmd /c "title Strategy - ETHUSD & cd .. & :loop & echo [%DATE% %TIME%] Starting ETHUSD Bot... & python -m gold.start ETHUSD & echo. & echo [%DATE% %TIME%] Bot Stopped/Crashed! Restarting in 5s... & timeout /t 5 & goto loop"
timeout /t 1 /nobreak >nul

:: -----------------------------------------------------------------------------
:: EURUSD Strategy Launcher
:: -----------------------------------------------------------------------------
echo Launching EURUSD Strategy...
start "Strategy - EURUSD" cmd /c "title Strategy - EURUSD & cd .. & :loop & echo [%DATE% %TIME%] Starting EURUSD Bot... & python -m gold.start EURUSD & echo. & echo [%DATE% %TIME%] Bot Stopped/Crashed! Restarting in 5s... & timeout /t 5 & goto loop"

echo.
echo ========================================================
echo  All 3 strategies have been launched in separate windows.
echo  You can now close this launcher window.
echo  The strategy windows will stay open and auto-restart.
echo ========================================================
echo.
pause
