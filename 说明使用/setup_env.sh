#!/bin/bash

# Ensure we are in the project root
cd "$(dirname "$0")/.." || exit 1

echo "🚀 Setting up Quant Trading Environment..."

# ARM64/Apple Silicon 检测提示
ARCH="$(uname -m)"
if [[ "$ARCH" == "arm64" || "$ARCH" == "aarch64" ]]; then
    echo -e "\033[1;33m⚠️  检测到 ARM64 架构 (Apple Silicon/Linux ARM)。\033[0m"
    echo -e "\033[1;32m推荐使用专为 ARM 优化的安装脚本：\033[0m"
    echo -e "   Run: \033[1m./说明使用/install_and_run.sh\033[0m"
    echo -e "   或者: \033[1mbash install_and_run.sh\033[0m (如果在说明使用目录下)"
    echo -e "按任意键继续使用当前旧脚本 (可能缺少 PostgreSQL 配置)，或 Ctrl+C 退出切换脚本..."
    read -n 1 -s -r -t 10
    echo
fi

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
    echo "POSTGRES_CONNECTION_STRING=postgresql://chenlingjie:clj568741230@localhost:5432/trading_bot" > .env
    echo "SERVER_API_KEY=my_secret_key" >> .env
    echo "POSTGRES_API_URL=http://127.0.0.1:8000/api" >> .env
    echo "SILICONFLOW_API_KEY=your_key_here" >> .env
    echo "⚠️  Please edit .env with your actual SILICONFLOW_API_KEY!"
else
    echo "✅ .env file exists."
fi

echo "✨ Setup complete! To activate: source venv/bin/activate"
