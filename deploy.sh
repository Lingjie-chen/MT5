#!/bin/bash

# 部署脚本 - 在阿里云服务器上安装和启动MT5 Python服务

echo "开始部署MT5 Python服务..."

# 更新系统包
echo "更新系统包..."
sudo apt update

# 安装Python 3和pip
echo "安装Python 3和pip..."
sudo apt install -y python3 python3-pip python3-venv

# 创建虚拟环境
echo "创建虚拟环境..."
python3 -m venv venv

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "升级pip..."
pip install --upgrade pip

# 安装依赖
echo "安装依赖..."
# 使用--no-deps选项避免强制安装Windows特定依赖
pip install -r requirements.txt --no-deps

# 安装非平台特定的依赖
pip install flask flask-cors pandas numpy python-dotenv requests scikit-learn

# 尝试安装TA-Lib
echo "安装TA-Lib..."
sudo apt install -y libta-lib0 libta-lib-dev
pip install ta-lib

# 安装MT5（仅在Windows系统上会成功）
echo "尝试安装MT5库（仅Windows系统支持）..."
pip install MetaTrader5 || echo "MT5库仅支持Windows系统，应用将使用模拟数据运行"

# 创建日志目录
echo "创建日志目录..."
mkdir -p logs

# 启动Flask应用
echo "启动Flask应用..."

# 使用nohup在后台运行应用
echo "应用启动中，日志将输出到 logs/server.log..."
nohup python enhanced_server_ml.py > logs/server.log 2>&1 &

echo "部署完成！应用已在后台启动。"
echo "可以通过 http://47.82.116.43:5002 访问应用"
echo "查看日志：tail -f logs/server.log"
