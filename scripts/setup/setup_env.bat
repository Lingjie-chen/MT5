@echo off
:: Switch to project root
cd /d "%~dp0..\.."

echo 🚀 Setting up Quant Trading Environment...

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH.
    pause
    exit /b
)

:: 2. Create Virtual Environment
if not exist venv (
    echo 📦 Creating virtual environment...
    python -m venv venv
) else (
    echo ✅ Virtual environment exists.
)

:: 3. Activate and Install Deps
echo 📥 Installing dependencies...
call venv\Scripts\activate

:: Fix for JSONDecodeError/Network issues: Use Tsinghua Mirror & No Cache
echo 🔄 Upgrading pip (using Tsinghua mirror)...
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

echo 📦 Installing requirements (using Tsinghua mirror & no-cache)...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir --default-timeout=100

:: 4. .env setup
if not exist .env (
    echo 📝 Creating .env template...
    (
        echo POSTGRES_CONNECTION_STRING=postgresql://chenlingjie:clj568741230@localhost:5432/trading_bot
        echo SERVER_API_KEY=clj568741230
        echo POSTGRES_API_URL=http://127.0.0.1:8000/api
        echo SILICONFLOW_API_KEY=your_key_here
    ) > .env
    echo ⚠️  Please edit .env with your actual SILICONFLOW_API_KEY!
) else (
    echo ✅ .env file exists.
)

:: 5. Check PostgreSQL
echo 🐘 Checking PostgreSQL status...
powershell -Command "if (Test-NetConnection -ComputerName localhost -Port 5432 -InformationLevel Quiet) { Write-Host '✅ PostgreSQL is running on port 5432.' -ForegroundColor Green } else { Write-Host '⚠️  PostgreSQL is NOT detected on port 5432.' -ForegroundColor Yellow }"

echo ✨ Setup complete! To activate: venv\Scripts\activate
pause
