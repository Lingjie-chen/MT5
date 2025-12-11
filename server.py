import sys
import os
import time
# 将python目录添加到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'python'))

from flask import Flask, request, jsonify
from data_processor import MT5DataProcessor
from deepseek_client import DeepSeekClient
from qwen_client import QwenClient
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

# 信号缓存，格式: {cache_key: {"signal": str, "signal_strength": int, "timestamp": float}}
# cache_key = f"{symbol}_{timeframe}_{hash_data}"
signal_cache = {}
CACHE_EXPIRY = 300  # 缓存过期时间，单位秒（5分钟）

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})

@app.route('/get_signal', methods=['POST'])
def get_signal():
    data = request.json
    symbol = data.get('symbol', 'GOLD')
    timeframe = data.get('timeframe', 'H1')
    rates = data.get('rates', [])
    
    # 生成缓存键，使用symbol、timeframe和rates的哈希值
    import hashlib
    rates_str = str(rates) if rates else "no_rates"
    cache_key = f"{symbol}_{timeframe}_{hashlib.md5(rates_str.encode()).hexdigest()}"
    
    # 检查缓存是否有效
    current_time = time.time()
    if cache_key in signal_cache:
        cached_data = signal_cache[cache_key]
        if current_time - cached_data["timestamp"] < CACHE_EXPIRY:
            # 返回缓存的信号
            return jsonify({
                "signal": cached_data["signal"], 
                "signal_strength": cached_data["signal_strength"],
                "from_cache": True
            })
    
    # 生成模拟数据（如果没有提供）
    if not rates:
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        df = processor.get_historical_data(symbol, None, start_date, end_date)
    else:
        # 将请求数据转换为DataFrame
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'])
        df.set_index('time', inplace=True)
    
    # 生成特征
    df = processor.generate_features(df)
    
    # 准备模型输入
    # 将DataFrame转换为字典，确保索引是字符串类型
    df_tail = df.tail(20)
    df_tail_reset = df_tail.reset_index()
    df_tail_reset['time'] = df_tail_reset['time'].astype(str)
    model_input = df_tail_reset.to_dict(orient='records')
    
    # 使用DeepSeek分析市场结构
    deepseek_analysis = deepseek_client.analyze_market_structure(model_input)
    
    # 使用Qwen3优化策略
    optimized_strategy = qwen_client.optimize_strategy_logic(deepseek_analysis, model_input)
    
    # 生成信号
    signal = "none"
    if optimized_strategy["signal_strength"] > 70:
        # 根据策略逻辑生成信号
        if df['ema_fast'].iloc[-1] > df['ema_slow'].iloc[-1]:
            signal = "buy"
        else:
            signal = "sell"
    
    # 缓存信号
    signal_cache[cache_key] = {
        "signal": signal,
        "signal_strength": optimized_strategy["signal_strength"],
        "timestamp": current_time
    }
    
    # 清理过期缓存
    expired_keys = [key for key, value in signal_cache.items() if current_time - value["timestamp"] >= CACHE_EXPIRY]
    for key in expired_keys:
        del signal_cache[key]
    
    # 返回信号
    return jsonify({"signal": signal, "signal_strength": optimized_strategy["signal_strength"], "from_cache": False})

if __name__ == '__main__':
    # 支持多品种交易的服务器配置
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", 5001))
    
    print(f"AI交易信号服务器启动在 {host}:{port}")
    print("支持多品种交易，可同时处理多个交易品种的信号请求")
    print(f"信号缓存过期时间: {CACHE_EXPIRY}秒")
    
    app.run(
        host=host,
        port=port,
        debug=True
    )
