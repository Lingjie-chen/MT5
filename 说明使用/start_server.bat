@echo off
cd /d "%~dp0\.."

:: Check venv
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Please run setup_env.bat first.
    pause
    exit /b
)

:: Set PYTHONPATH
set PYTHONPATH=%PYTHONPATH%;%cd%

echo Starting API Server on port 8000...
python gold/server/main.py
pause
