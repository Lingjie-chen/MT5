@echo off
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
python -m pip install --upgrade pip
pip install -r requirements.txt

:: 4. .env setup
if not exist .env (
    echo 📝 Creating .env template...
    echo POSTGRES_CONNECTION_STRING=postgresql://user:pass@localhost:5432/trading_bot> .env
    echo SERVER_API_KEY=my_secret_key>> .env
    echo SILICONFLOW_API_KEY=your_key_here>> .env
    echo ⚠️  Please edit .env with your actual credentials!
) else (
    echo ✅ .env file exists.
)

echo ✨ Setup complete! To activate: venv\Scripts\activate
pause
