#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 开始一键安装和配置 Quant Trading 环境 (ARM64/Apple Silicon 适配版)...${NC}"

# 获取脚本所在目录的上一级目录（项目根目录）
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"
cd "$PROJECT_ROOT" || exit 1

echo -e "${BLUE}📂 项目根目录: $PROJECT_ROOT${NC}"

# 1. 检测操作系统
OS="$(uname -s)"
ARCH="$(uname -m)"

echo -e "${BLUE}🖥️  检测系统: $OS ($ARCH)${NC}"

if [[ "$ARCH" != "arm64" && "$ARCH" != "aarch64" ]]; then
    echo -e "${YELLOW}⚠️  警告: 检测到非 ARM 架构 ($ARCH)。本脚本主要针对 ARM64/Apple Silicon 优化，但仍将尝试继续。${NC}"
fi

# 2. 安装系统依赖 (PostgreSQL & Python)
install_system_deps() {
    if [[ "$OS" == "Darwin" ]]; then
        # macOS
        if ! command -v brew &> /dev/null; then
            echo -e "${RED}❌ 未检测到 Homebrew。请先安装 Homebrew: https://brew.sh/${NC}"
            exit 1
        fi
        
        echo -e "${GREEN}🍏 macOS 检测到。使用 Homebrew 安装依赖...${NC}"
        brew update
        
        # 安装 Python
        if ! command -v python3 &> /dev/null; then
            brew install python@3.11
        fi
        
        # 安装 PostgreSQL
        if ! command -v postgres &> /dev/null; then
            echo -e "${BLUE}📥 安装 PostgreSQL...${NC}"
            brew install postgresql@14
            brew services start postgresql@14
            # 等待启动
            sleep 5
        else
            echo -e "${GREEN}✅ PostgreSQL 已安装。${NC}"
            # 确服务已启动
            brew services start postgresql@14 || brew services start postgresql
        fi
        
    elif [[ "$OS" == "Linux" ]]; then
        # Linux (Debian/Ubuntu)
        if command -v apt-get &> /dev/null; then
            echo -e "${GREEN}🐧 Linux (Debian/Ubuntu) 检测到。使用 apt 安装依赖...${NC}"
            sudo apt-get update
            sudo apt-get install -y python3 python3-venv python3-pip postgresql postgresql-contrib libpq-dev build-essential
            
            # 启动 PostgreSQL 服务
            sudo service postgresql start
        else
            echo -e "${RED}❌ 不支持的 Linux 发行版。请手动安装 Python 3 和 PostgreSQL。${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ 不支持的操作系统: $OS${NC}"
        exit 1
    fi
}

install_system_deps

# 3. 配置 PostgreSQL 用户和数据库
configure_postgres() {
    echo -e "${BLUE}🐘 配置 PostgreSQL 数据库...${NC}"
    
    DB_USER="chenlingjie"
    DB_PASS="clj568741230"
    DB_NAME="trading_bot"
    
    # 检查数据库用户是否存在，不存在则创建
    if ! psql -U postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
        echo -e "${YELLOW}👤 创建数据库用户 '$DB_USER'...${NC}"
        if [[ "$OS" == "Darwin" ]]; then
            psql postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
            psql postgres -c "ALTER USER $DB_USER CREATEDB;"
        else
            sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
            sudo -u postgres psql -c "ALTER USER $DB_USER CREATEDB;"
        fi
    else
        echo -e "${GREEN}✅ 数据库用户 '$DB_USER' 已存在。${NC}"
    fi
    
    # 检查数据库是否存在，不存在则创建
    if ! psql -U postgres -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
        echo -e "${YELLOW}🗄️  创建数据库 '$DB_NAME'...${NC}"
        if [[ "$OS" == "Darwin" ]]; then
            createdb -U postgres -O $DB_USER $DB_NAME
        else
            sudo -u postgres createdb -O $DB_USER $DB_NAME
        fi
    else
        echo -e "${GREEN}✅ 数据库 '$DB_NAME' 已存在。${NC}"
    fi
}

# 尝试配置 Postgres，如果失败则提示用户
if command -v psql &> /dev/null; then
    # 在 macOS 上，当前用户通常可以直接访问 postgres 数据库如果安装正确
    # 在 Linux 上，通常需要 sudo -u postgres
    configure_postgres || echo -e "${RED}⚠️  自动配置数据库失败。您可能需要手动创建用户和数据库。${NC}"
else
    echo -e "${RED}⚠️  未找到 psql 命令。跳过数据库自动配置。${NC}"
fi

# 4. Python 环境设置
echo -e "${BLUE}🐍 设置 Python 环境...${NC}"

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 创建虚拟环境 (venv)...${NC}"
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装依赖
if [ -f "requirements.txt" ]; then
    echo -e "${BLUE}📥 安装 Python 依赖...${NC}"
    # 针对 ARM mac 可能需要特殊处理 psycopg2
    if [[ "$OS" == "Darwin" && "$ARCH" == "arm64" ]]; then
        # 有时二进制包在 M1 上有问题，尝试从源码构建或使用 binary
        pip install -r requirements.txt
    else
        pip install -r requirements.txt
    fi
else
    echo -e "${RED}❌ 未找到 requirements.txt${NC}"
fi

# 5. 生成 .env 文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📝 创建默认 .env 文件...${NC}"
    cat > .env <<EOL
POSTGRES_CONNECTION_STRING=postgresql://chenlingjie:clj568741230@localhost:5432/trading_bot
SERVER_API_KEY=my_secret_key
POSTGRES_API_URL=http://127.0.0.1:8000/api
SILICONFLOW_API_KEY=your_key_here
TELEGRAM_CHAT_ID=
EOL
    echo -e "${GREEN}✅ .env 文件已创建。请稍后编辑它以填入您的 API Key。${NC}"
else
    echo -e "${GREEN}✅ .env 文件已存在。${NC}"
fi

# 6. 启动服务选项
echo -e "\n${GREEN}🎉 安装完成！${NC}"
echo -e "${YELLOW}您现在可以启动服务了。${NC}"

echo -e "${YELLOW}注意: 交易机器人主程序 (gold/start.py) 依赖 MetaTrader5，仅支持 Windows 环境。${NC}"
echo -e "${YELLOW}在 macOS/Linux ARM 上，您可以运行 API 服务器和 Dashboard 面板。${NC}"

read -p "是否启动 API 服务器和 Dashboard? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}🚀 启动 API 服务器 (后台运行)...${NC}"
    
    # 启动 API Server
    nohup uvicorn gold.server.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
    SERVER_PID=$!
    echo -e "${GREEN}✅ API 服务器已启动 (PID: $SERVER_PID)。日志在 server.log${NC}"
    
    echo -e "${BLUE}🚀 启动 Dashboard...${NC}"
    streamlit run dashboard.py
else
    echo -e "您可以手动运行以下命令启动:"
    echo -e "1. 激活环境: ${YELLOW}source venv/bin/activate${NC}"
    echo -e "2. 启动服务器: ${YELLOW}uvicorn gold.server.main:app --host 0.0.0.0 --port 8000${NC}"
    echo -e "3. 启动面板: ${YELLOW}streamlit run dashboard.py${NC}"
    echo -e "4. (仅Windows) 启动机器人: ${YELLOW}python gold/start.py${NC}"
fi
