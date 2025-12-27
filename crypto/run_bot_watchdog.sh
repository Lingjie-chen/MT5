#!/bin/bash

# 切换到脚本所在目录
cd "$(dirname "$0")"

while true; do
    echo "[$(date)] Starting Crypto Trading Bot..."
    echo "---------------------------------------------------"
    
    # 运行 Python 交易机器人脚本
    # 确保在 crypto 目录中执行，以便正确解析相对导入
    python trading_bot.py "$@"
    
    echo "---------------------------------------------------"
    echo "[$(date)] Bot crashed or stopped. Restarting in 5 seconds..."
    sleep 5
done