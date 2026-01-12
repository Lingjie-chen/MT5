@echo off
echo Starting Strategy Servers with Auto-Restart Watchdogs...

:: -----------------------------------------------------------------------------
:: GOLD Strategy Launcher
:: -----------------------------------------------------------------------------
echo Launching GOLD Strategy...
start "Strategy - GOLD" cmd /c "title Strategy - GOLD && :loop && echo [%DATE% %TIME%] Starting GOLD Bot... && python start.py GOLD && echo [%DATE% %TIME%] Bot Crashed! Restarting in 5s... && timeout /t 5 >nul && goto loop"
timeout /t 2 /nobreak >nul

:: -----------------------------------------------------------------------------
:: ETHUSD Strategy Launcher
:: -----------------------------------------------------------------------------
echo Launching ETHUSD Strategy...
start "Strategy - ETHUSD" cmd /c "title Strategy - ETHUSD && :loop && echo [%DATE% %TIME%] Starting ETHUSD Bot... && python start.py ETHUSD && echo [%DATE% %TIME%] Bot Crashed! Restarting in 5s... && timeout /t 5 >nul && goto loop"
timeout /t 2 /nobreak >nul

:: -----------------------------------------------------------------------------
:: EURUSD Strategy Launcher
:: -----------------------------------------------------------------------------
echo Launching EURUSD Strategy...
start "Strategy - EURUSD" cmd /c "title Strategy - EURUSD && :loop && echo [%DATE% %TIME%] Starting EURUSD Bot... && python start.py EURUSD && echo [%DATE% %TIME%] Bot Crashed! Restarting in 5s... && timeout /t 5 >nul && goto loop"

echo.
echo All strategies launched in separate watchdog windows.
echo Each window will automatically restart if the bot crashes.
echo.
echo Logs will be saved to:
echo - windows_bot_GOLD.log
echo - windows_bot_ETHUSD.log
echo - windows_bot_EURUSD.log
pause
