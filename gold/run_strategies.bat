@echo off
echo Starting Strategy Servers...

echo Launching GOLD Strategy...
start "Strategy - GOLD" python start.py GOLD
timeout /t 2 /nobreak >nul

echo Launching ETHUSD Strategy...
start "Strategy - ETHUSD" python start.py ETHUSD
timeout /t 2 /nobreak >nul

echo Launching EURUSD Strategy...
start "Strategy - EURUSD" python start.py EURUSD

echo All strategies launched in separate windows.
echo Logs will be saved to:
echo - windows_bot_GOLD.log
echo - windows_bot_ETHUSD.log
echo - windows_bot_EURUSD.log
pause
