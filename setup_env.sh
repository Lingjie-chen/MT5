#!/bin/bash

echo "🚀 Setting up Quant Trading Environment..."

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10+"
    exit 1
fi

# 2. Create Virtual Environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment exists."
fi

# 3. Activate and Install Deps
echo "📥 Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. .env setup
if [ ! -f ".env" ]; then
    echo "📝 Creating .env template..."
    echo "POSTGRES_CONNECTION_STRING=postgresql://user:pass@localhost:5432/trading_bot" > .env
    echo "SERVER_API_KEY=my_secret_key" >> .env
    echo "SILICONFLOW_API_KEY=your_key_here" >> .env
    echo "⚠️  Please edit .env with your actual credentials!"
else
    echo "✅ .env file exists."
fi

echo "✨ Setup complete! To activate: source venv/bin/activate"
