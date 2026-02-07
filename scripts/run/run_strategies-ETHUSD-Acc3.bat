@echo off
echo Starting Strategy Servers (Account 3)...

:: Switch to current script directory (scripts/run/)
cd /d "%~dp0"

:: -----------------------------------------------------------------------------
:: Launch Strategies
:: 我们直接调用 run_bot_watchdog.bat 来处理具体的启动和重启逻辑
:: -----------------------------------------------------------------------------

echo Launching ETHUSD Strategy (Ava Demo - Acc3)...
start "Strategy - ETHUSD (Ava Demo)" run_bot_watchdog.bat ETHUSD --account 3
timeout /t 1 /nobreak >nul

echo.
echo ========================================================
echo  All strategies have been launched in separate windows.
echo  Each window runs 'run_bot_watchdog.bat' which handles
echo  the auto-restart logic.
echo ========================================================
echo.
pause
