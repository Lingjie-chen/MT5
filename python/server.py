from flask import Flask, request, jsonify
from data_processor import MT5DataProcessor
from deepseek_client import DeepSeekClient
from qwen_client import QwenClient
import os
from dotenv import load_dotenv
import pandas as pd

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# 初始化客户端
deepseek_client = DeepSeekClient(
    api_key=os.getenv("DEEPSEEK_API_KEY", "your_deepseek_api_key"),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
)

qwen_client = QwenClient(
    api_key=os.getenv("QWEN_API_KEY", "your_qwen_api_key"),
    base_url=os.getenv("QWEN_BASE_URL", "https://api.qwen.com/v1")
)

processor = MT5DataProcessor()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})

@app.route('/get_signal', methods=['POST'])
def get_signal():
    data = request.json
    symbol = data.get('symbol', 'GOLD')
    timeframe = data.get('timeframe', 'H1')
    rates = data.get('rates', [])
    
    # 生成信号（简化版，实际项目中需要更复杂的逻辑）
    signal = "none"
    
    # 这里可以添加更复杂的信号生成逻辑
    # 例如：根据EMA交叉、RSI等指标生成信号
    
    # 返回信号
    return jsonify({"signal": signal, "signal_strength": 50})

if __name__ == '__main__':
    app.run(
        host=os.getenv("SERVER_HOST", "0.0.0.0"),
        port=int(os.getenv("SERVER_PORT", 5000)),
        debug=True
    )
