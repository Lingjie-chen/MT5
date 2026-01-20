#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# 切换到项目根目录（脚本父目录）
cd "$SCRIPT_DIR/.." || exit 1

echo -e "${BLUE}🚀 启动 Quant Trading 服务...${NC}"

# 检查 venv
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  未找到虚拟环境，请先运行 install_and_run.sh${NC}"
    exit 1
fi

source venv/bin/activate

# 启动 API Server
echo -e "${BLUE}📡 启动 API 服务器 (Port 8000)...${NC}"
if pgrep -f "uvicorn gold.server.main:app" > /dev/null; then
    echo -e "${YELLOW}API 服务器已在运行。${NC}"
else
    nohup uvicorn gold.server.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
    echo -e "${GREEN}API 服务器已后台启动。${NC}"
fi

# 启动 Dashboard
echo -e "${BLUE}📊 启动 Dashboard...${NC}"
streamlit run dashboard.py
