@echo off
echo Starting Strategy Servers...

:: 切换到当前脚本所在目录 (gold/)
cd /d "%~dp0"

:: -----------------------------------------------------------------------------
:: Launch Strategies
:: 我们直接调用 run_bot_watchdog.bat 来处理具体的启动和重启逻辑
:: 这样避免了在 start 命令中编写复杂的单行循环代码导致的语法错误
:: -----------------------------------------------------------------------------

echo Launching Account 1 Strategy (GOLD, ETHUSD, EURUSD)...
start "Strategy - Account 1 (Ava)" run_bot_watchdog.bat GOLD,ETHUSD,EURUSD --account 1
timeout /t 2 /nobreak >nul

echo Launching Account 2 Strategy (XAUUSDm, ETHUSDm, EURUSDm)...
start "Strategy - Account 2 (Exness)" run_bot_watchdog.bat XAUUSDm,ETHUSDm,EURUSDm --account 2

echo.
echo ========================================================
echo  All strategies have been launched in 2 main windows.
echo  Account 1: Ava (GOLD, ETHUSD, EURUSD)
echo  Account 2: Exness (XAUUSDm, ETHUSDm, EURUSDm)
echo ========================================================
echo.
pause