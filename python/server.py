from flask import Flask, request, jsonify
from data_processor import MT5DataProcessor
from deepseek_client import DeepSeekClient
from qwen_client import QwenClient
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import logging

# 加载环境变量
load_dotenv()

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 初始化客户端
try:
    deepseek_client = DeepSeekClient(
        api_key=os.getenv("DEEPSEEK_API_KEY", "your_deepseek_api_key"),
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    )
    qwen_client = QwenClient(
        api_key=os.getenv("QWEN_API_KEY", "your_qwen_api_key"),
        base_url=os.getenv("QWEN_BASE_URL", "https://api.qwen.com/v1")
    )
    logger.info("AI clients initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize AI clients: {e}")
    deepseek_client = None
    qwen_client = None

processor = MT5DataProcessor()

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@app.route('/get_signal', methods=['POST'])
def get_signal():
    """获取交易信号端点"""
    try:
        # 解析请求数据
        data = request.json
        symbol = data.get('symbol', 'GOLD')
        timeframe = data.get('timeframe', 'H1')
        rates = data.get('rates', [])
        
        logger.info(f"Received signal request for {symbol} on {timeframe}")
        
        # 准备数据
        df = None
        if rates:
            # 将EA发送的数据转换为DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            logger.info(f"Processed {len(df)} rates from EA")
        else:
            # 生成模拟数据
            end_date = datetime.now()
            start_date = end_date - pd.DateOffset(days=30)
            df = processor.get_historical_data(symbol, None, start_date, end_date)
            logger.info(f"Generated {len(df)} mock rates")
        
        # 生成特征
        df_with_features = processor.generate_features(df)
        logger.info(f"Generated features for {len(df_with_features)} rows")
        
        # 生成信号
        signal = "none"
        signal_strength = 50
        
        # 基于特征生成简单的信号逻辑
        if len(df_with_features) > 0:
            last_row = df_with_features.iloc[-1]
            
            # EMA交叉策略
            if last_row['ema_fast'] > last_row['ema_slow'] and last_row['rsi'] < 70:
                signal = "buy"
                signal_strength = min(90, int((last_row['rsi'] / 70) * 100))
            elif last_row['ema_fast'] < last_row['ema_slow'] and last_row['rsi'] > 30:
                signal = "sell"
                signal_strength = min(90, int(((70 - last_row['rsi']) / 70) * 100))
            
            # 基于ATR的信号强度调整
            volatility = last_row['volatility']
            if volatility > 2.0:
                signal_strength = min(70, signal_strength)
            elif volatility < 0.5:
                signal_strength = min(50, signal_strength)
        
        # 如果AI客户端可用，使用AI增强信号
        if deepseek_client and qwen_client:
            try:
                # 准备模型输入
                model_input = df_with_features.tail(20).to_dict()
                
                # 使用DeepSeek分析市场结构
                deepseek_analysis = deepseek_client.analyze_market_structure(model_input)
                
                # 使用Qwen3优化策略
                optimized_strategy = qwen_client.optimize_strategy_logic(deepseek_analysis, model_input)
                
                # 结合AI分析调整信号
                if optimized_strategy["signal_strength"] > signal_strength:
                    signal = optimized_strategy.get("signal", signal)
                    signal_strength = optimized_strategy["signal_strength"]
                    
                logger.info(f"AI enhanced signal: {signal}, strength: {signal_strength}")
            except Exception as e:
                logger.error(f"Failed to use AI clients: {e}")
        
        # 记录信号
        logger.info(f"Generated signal: {signal}, strength: {signal_strength}")
        
        # 返回信号
        return jsonify({
            "signal": signal,
            "signal_strength": signal_strength,
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "timeframe": timeframe
        })
        
    except Exception as e:
        logger.error(f"Error generating signal: {e}", exc_info=True)
        return jsonify({
            "signal": "none",
            "signal_strength": 0,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    # 获取配置
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", 5001))
    
    logger.info(f"Starting AI Signal Server on {host}:{port}")
    
    app.run(
        host=host,
        port=port,
        debug=True
    )