#!/bin/bash

# Ensure we are in the project root
cd "$(dirname "$0")/../.." || exit 1

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
    cat > .env << EOL
POSTGRES_CONNECTION_STRING=postgresql://chenlingjie:clj568741230@localhost:5432/trading_bot
SERVER_API_KEY=my_secret_key
POSTGRES_API_URL=http://127.0.0.1:8000/api
SILICONFLOW_API_KEY=your_key_here
EOL
    echo "⚠️  Please edit .env with your actual SILICONFLOW_API_KEY!"
else
    echo "✅ .env file exists."
fi

# 5. Check PostgreSQL Status
echo "🐘 Checking PostgreSQL status..."
if nc -z localhost 5432 2>/dev/null; then
    echo "✅ PostgreSQL is running on port 5432."
else
    echo "⚠️  PostgreSQL is NOT detected on port 5432."
    echo "    Please ensure PostgreSQL is installed and running."
fi

echo "✨ Setup complete! To activate: source venv/bin/activate"
