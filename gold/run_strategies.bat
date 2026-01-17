@echo off
echo Starting Strategy Servers...

:: 切换到当前脚本所在目录 (gold/)
cd /d "%~dp0"

:: -----------------------------------------------------------------------------
:: Launch Strategies
:: 我们直接调用 run_bot_watchdog.bat 来处理具体的启动和重启逻辑
:: 这样避免了在 start 命令中编写复杂的单行循环代码导致的语法错误
:: -----------------------------------------------------------------------------

echo Launching XAUUSDm Strategy...
start "Strategy - XAUUSDm" run_bot_watchdog.bat XAUUSDm
timeout /t 1 /nobreak >nul

echo Launching ETHUSDm Strategy...
start "Strategy - ETHUSDm" run_bot_watchdog.bat ETHUSDm

echo Launching EURUSDm Strategy...
start "Strategy - EURUSDm" run_bot_watchdog.bat EURUSDm

echo.
echo ========================================================
echo  All strategies have been launched in separate windows.
echo  Each window runs 'run_bot_watchdog.bat' which handles
echo  the auto-restart logic.
echo ========================================================
echo.
pause