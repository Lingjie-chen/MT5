@echo off
:: Switch to project root
cd /d "%~dp0.."

echo 🚀 Starting Data Server (FastAPI)...
echo 📡 This server enables real-time data sync to PostgreSQL.

:: Check environment
if not exist venv (
    echo ❌ Virtual environment not found. Please run 'setup_env.bat' first.
    pause
    exit /b
)

:: Activate venv
call venv\Scripts\activate

:: Start Server
echo 🟢 Starting Uvicorn Server on http://0.0.0.0:8000...
echo (Press Ctrl+C to stop)
uvicorn gold.server.main:app --host 0.0.0.0 --port 8000 --reload

pause