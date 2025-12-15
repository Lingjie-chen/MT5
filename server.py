import sys
import os
import time

# Add the python directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

from flask import Flask, request, jsonify
from data_processor import MT5DataProcessor
from deepseek_client import DeepSeekClient
from qwen_client import QwenClient
from dotenv import load_dotenv
import pandas as pd

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# 初始化客户端 - 使用硅基流动API服务
siliconflow_api_key = os.getenv("SILICONFLOW_API_KEY", "your_siliconflow_api_key")
deepseek_model = os.getenv("DEEPSEEK_MODEL", "deepseek-ai/DeepSeek-V3.1-Terminus")
qwen_model = os.getenv("QWEN_MODEL", "Qwen/Qwen3-VL-235B-A22B-Thinking")

deepseek_client = DeepSeekClient(
    api_key=siliconflow_api_key,
    model=deepseek_model
)

qwen_client = QwenClient(
    api_key=siliconflow_api_key,
    model=qwen_model
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
    try:
        # Validate request format
        if not request.is_json:
            return jsonify({"error": "Request must be JSON", "signal": "none", "signal_strength": 0}), 400
        
        data = request.json
        symbol = data.get('symbol', 'GOLD')
        timeframe = data.get('timeframe', 'H1')
        rates = data.get('rates', [])
        
        # Validate rates format if provided
        if rates and not isinstance(rates, list):
            return jsonify({"error": "Rates must be a list", "signal": "none", "signal_strength": 0}), 400
        
        # Log the request for debugging
        print(f"Received request: symbol={symbol}, timeframe={timeframe}, rates_count={len(rates) if rates else 0}")
        if rates and len(rates) > 0:
            print(f"First rate: {rates[0]}")
        
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
        if not rates or len(rates) == 0:
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            df = processor.get_historical_data(symbol, None, start_date, end_date)
        else:
            # 将请求数据转换为DataFrame
            df = pd.DataFrame(rates)
            
            # 处理不同的时间格式和字段名称
            if 'time' in df.columns:
                # 确保时间列是数值类型
                df['time'] = pd.to_numeric(df['time'], errors='coerce')
                # 转换为datetime
                df['time'] = pd.to_datetime(df['time'], unit='s')
            elif 'Time' in df.columns:
                df['time'] = pd.to_numeric(df['Time'], errors='coerce')
                df['time'] = pd.to_datetime(df['time'], unit='s')
            
            # 处理不同的成交量字段名称
            if 'tick_volume' in df.columns and 'volume' not in df.columns:
                df['volume'] = df['tick_volume']
            elif 'TickVolume' in df.columns and 'volume' not in df.columns:
                df['volume'] = df['TickVolume']
            
            df.set_index('time', inplace=True)
        
        # 生成特征
        df = processor.generate_features(df)
        
        # 准备模型输入
        # 将DataFrame转换为字典，确保索引是字符串类型
        df_tail = df.tail(20)
        df_tail_reset = df_tail.reset_index()
        df_tail_reset['time'] = df_tail_reset['time'].astype(str)
        model_input = df_tail_reset.to_dict(orient='records')
        
        # 初始化信号和强度
        signal = "none"
        signal_strength = 50
        
        # 尝试使用AI增强信号（如果可用）
        if deepseek_client and qwen_client:
            try:
                # 使用DeepSeek分析市场结构
                deepseek_analysis = deepseek_client.analyze_market_structure(model_input)
                
                # 使用Qwen3优化策略
                optimized_strategy = qwen_client.optimize_strategy_logic(deepseek_analysis, model_input)
                
                # 获取AI生成的信号强度
                signal_strength = optimized_strategy.get("signal_strength", 50)
            except Exception as e:
                print(f"AI信号生成失败，使用传统方法: {e}")
        
        # 使用传统技术分析生成信号
        if len(df) > 2:
            # EMA交叉策略
            last_ema_fast = df['ema_fast'].iloc[-1]
            last_ema_slow = df['ema_slow'].iloc[-1]
            prev_ema_fast = df['ema_fast'].iloc[-2]
            prev_ema_slow = df['ema_slow'].iloc[-2]
            
            # 计算RSI
            rsi = df['rsi'].iloc[-1]
            
            # 生成信号
            if prev_ema_fast < prev_ema_slow and last_ema_fast > last_ema_slow and rsi < 70:
                # 金叉，买入信号
                signal = "buy"
                signal_strength = min(90, int(rsi * 1.2))
            elif prev_ema_fast > prev_ema_slow and last_ema_fast < last_ema_slow and rsi > 30:
                # 死叉，卖出信号
                signal = "sell"
                signal_strength = min(90, int((100 - rsi) * 1.2))
        
        # 保存策略信息
        optimized_strategy = {"signal_strength": signal_strength}
        
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
    except Exception as e:
        # Log the error with traceback
        import traceback
        print(f"Error processing request: {e}")
        traceback.print_exc()
        
        # Return a meaningful error response
        return jsonify({"error": f"Internal server error: {str(e)}", "signal": "none", "signal_strength": 0}), 500

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