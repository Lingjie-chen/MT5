@echo off
cd /d "%~dp0"

echo Starting System...

:: Start Server in a new window
start "Quant Server" cmd /c "start_server.bat"

:: Start Sync Engine in a new window
start "Auto Sync Engine" cmd /c "同步windons.bat"

echo System started. 
echo Please check the other windows for logs.
pause
