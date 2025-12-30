#!/bin/bash

# 切换到脚本所在目录
cd "$(dirname "$0")"


# 切换到上级目录(项目根目录)，以便作为模块运行
cd ..

while true; do
    echo "[$(date)] Starting Crypto Trading Bot..."
    echo "---------------------------------------------------"
    
    # 以模块方式运行，确保包导入正确
    python -m crypto.trading_bot "$@"
    
    echo "---------------------------------------------------"
    echo "[$(date)] Bot crashed or stopped. Restarting in 5 seconds..."
    sleep 5
done