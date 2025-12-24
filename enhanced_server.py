#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版Python服务器 - 集成DeepSeek/Qwen大模型和高级分析功能
实现与MT5平台的实时联动，支持大模型驱动的交易决策
"""

import os
import json
import time
import logging
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入自定义模块
# 确保python目录在路径中
sys.path.append(os.path.join(os.path.dirname(__file__), 'python'))

try:
    from python.advanced_analysis import AdvancedMarketAnalysis
    from python.data_processor import MT5DataProcessor
    from python.ai_client_factory import AIClientFactory
    from python.deepseek_client import DeepSeekClient
    from python.qwen_client import QwenClient
except ImportError as e:
    # 如果直接运行server，路径可能需要调整
    sys.path.append(os.path.dirname(__file__))
    from python.advanced_analysis import AdvancedMarketAnalysis
    from python.data_processor import MT5DataProcessor
    from python.ai_client_factory import AIClientFactory
    from python.deepseek_client import DeepSeekClient
    from python.qwen_client import QwenClient

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 服务器启动时间
app_start_time = time.time()

# 全局组件实例
data_processor = MT5DataProcessor()
analysis_tool = AdvancedMarketAnalysis()
ai_factory = AIClientFactory()

# 初始化AI客户端
deepseek_client: Optional[DeepSeekClient] = None
qwen_client: Optional[QwenClient] = None

try:
    clients = ai_factory.initialize_all_clients()
    deepseek_client = clients.get('deepseek')
    qwen_client = clients.get('qwen')
    
    if not deepseek_client or not qwen_client:
        logger.warning("AI客户端初始化不完整，将使用本地分析作为降级方案")
        logger.warning("请检查环境变量 SILICONFLOW_API_KEY 是否正确配置")
except Exception as e:
    logger.error(f"AI客户端初始化失败: {e}")

# 请求统计
request_stats = {
    'total_requests': 0,
    'successful_requests': 0,
    'failed_requests': 0,
    'ai_calls': 0,
    'local_analysis': 0
}

def convert_numpy_types(obj):
    """将numpy类型转换为原生Python类型"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(v) for v in obj]
    elif isinstance(obj, np.bool_):
        return bool(obj)
    else:
        return obj

def validate_request_data(data: Dict[str, Any]) -> Tuple[bool, str]:
    """验证请求数据的安全性和完整性"""
    try:
        required_fields = ['symbol', 'timeframe', 'rates']
        for field in required_fields:
            if field not in data:
                return False, f"缺少必需字段: {field}"
        
        rates = data['rates']
        if not isinstance(rates, list) or len(rates) < 10:
            return False, "rates数据无效或长度不足(最少10条)"
            
        return True, "验证通过"
    except Exception as e:
        return False, f"验证过程发生异常: {str(e)}"

def generate_ai_signal(df: pd.DataFrame, symbol: str, timeframe: str) -> Dict[str, Any]:
    """
    使用大模型生成交易信号
    结合DeepSeek的市场结构分析和Qwen的策略优化
    """
    # 1. 准备市场数据
    current_price = df.iloc[-1]
    
    # 计算技术指标作为上下文
    df_features = data_processor.generate_features(df)
    latest_features = df_features.iloc[-1].to_dict()
    
    # 构建发送给AI的市场快照
    market_snapshot = {
        "symbol": symbol,
        "timeframe": timeframe,
        "prices": {
            "open": float(current_price['open']),
            "high": float(current_price['high']),
            "low": float(current_price['low']),
            "close": float(current_price['close']),
            "volume": int(current_price['volume'])
        },
        "indicators": {
            "rsi": float(latest_features.get('rsi', 50)),
            "atr": float(latest_features.get('atr', 0)),
            "ema_fast": float(latest_features.get('ema_fast', 0)),
            "ema_slow": float(latest_features.get('ema_slow', 0)),
            "volatility": float(latest_features.get('volatility', 0))
        },
        "trend": "bullish" if latest_features.get('ema_fast', 0) > latest_features.get('ema_slow', 0) else "bearish"
    }
    
    # 2. DeepSeek分析市场结构
    structure_analysis = {
        "market_state": "unknown",
        "structure_score": 50,
        "short_term_prediction": "neutral",
        "indicator_analysis": "AI分析跳过"
    }
    
    if deepseek_client:
        try:
            logger.info(f"调用DeepSeek分析 {symbol}...")
            structure_analysis = deepseek_client.analyze_market_structure(market_snapshot)
            request_stats['ai_calls'] += 1
        except Exception as e:
            logger.error(f"DeepSeek调用失败: {e}")
    
    # 3. Qwen优化策略并生成信号
    signal_result = {
        "signal": "hold",
        "strength": 0,
        "analysis": "等待AI分析"
    }
    
    if qwen_client:
        try:
            logger.info(f"调用Qwen生成策略 {symbol}...")
            # 获取策略建议
            strategy = qwen_client.optimize_strategy_logic(structure_analysis, market_snapshot)
            request_stats['ai_calls'] += 1
            
            # 二次验证信号强度
            deepseek_prelim_signal = {
                "signal": "buy" if structure_analysis.get("short_term_prediction") == "bullish" else 
                          "sell" if structure_analysis.get("short_term_prediction") == "bearish" else "hold",
                "confidence": structure_analysis.get("structure_score", 50) / 100.0
            }
            
            final_strength = qwen_client.judge_signal_strength(deepseek_prelim_signal, market_snapshot['indicators'])
            
            # 综合决策
            base_signal = deepseek_prelim_signal['signal']
            
            # 只有当强度足够时才确认信号
            if final_strength >= 60:
                final_signal = base_signal
            else:
                final_signal = "hold"
                
            analysis_text = (
                f"AI分析 ({structure_analysis.get('market_state', 'N/A')}): "
                f"{structure_analysis.get('indicator_analysis', 'N/A')}. "
                f"Qwen策略: 信号强度 {final_strength}, "
                f"建议 {final_signal.upper()}."
            )
            
            signal_result = {
                "signal": final_signal,
                "strength": final_strength,
                "analysis": analysis_text,
                "sl_tp": strategy.get("exit_conditions", {}),
                "risk": strategy.get("risk_management", {})
            }
            
        except Exception as e:
            logger.error(f"Qwen调用失败: {e}")
            signal_result["analysis"] = f"AI策略生成失败: {str(e)}"
    else:
        # 如果没有AI客户端，使用本地规则
        signal_result = generate_local_signal(df_features)
        signal_result["analysis"] = "AI未启用，使用本地技术分析"
        request_stats['local_analysis'] += 1
        
    return signal_result

def generate_local_signal(df: pd.DataFrame) -> Dict[str, Any]:
    """
    当AI不可用时的本地降级分析方案
    """
    latest = df.iloc[-1]
    rsi = latest.get('rsi', 50)
    ema_cross = latest.get('ema_crossover', 0)
    
    signal = "hold"
    strength = 0
    analysis = "本地分析: 市场中性"
    
    if rsi < 30 and ema_cross > 0:
        signal = "buy"
        strength = 70
        analysis = f"本地分析: RSI超卖({rsi:.1f})且EMA金叉"
    elif rsi > 70 and ema_cross < 0:
        signal = "sell"
        strength = 70
        analysis = f"本地分析: RSI超买({rsi:.1f})且EMA死叉"
    elif ema_cross != 0:
        signal = "buy" if ema_cross > 0 else "sell"
        strength = 50
        analysis = f"本地分析: EMA趋势跟踪 ({'看涨' if ema_cross > 0 else '看跌'})"
        
    return {
        "signal": signal,
        "strength": strength,
        "analysis": analysis
    }

@app.route('/')
def index():
    """主页"""
    return jsonify({
        "status": "online",
        "service": "AI Quant Trading Server",
        "models": {
            "deepseek": "available" if deepseek_client else "unavailable",
            "qwen": "available" if qwen_client else "unavailable"
        },
        "time": datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'uptime': time.time() - app_start_time,
        'stats': request_stats
    })

@app.route('/get_signal', methods=['POST'])
def get_signal():
    """获取交易信号 - 大模型驱动"""
    request_stats['total_requests'] += 1
    start_time = time.time()
    
    try:
        # 1. 解析请求
        # 增强的JSON解析逻辑，处理MT5可能发送的异常字符
        raw_data = request.data
        try:
            data = request.get_json(silent=True)
            if data is None:
                # 尝试手动清洗和解析
                decoded = raw_data.decode('utf-8', errors='ignore').strip()
                # 移除空字符
                decoded = decoded.replace('\x00', '')
                # 尝试找到最后一个闭合括号
                last_brace = decoded.rfind('}')
                if last_brace != -1:
                    decoded = decoded[:last_brace+1]
                data = json.loads(decoded)
        except Exception as e:
            logger.error(f"JSON解析严重失败: {e}")
            return jsonify({'error': 'Invalid JSON format', 'details': str(e)}), 400

        if not data:
            return jsonify({'error': 'Empty request body'}), 400

        # 2. 验证数据
        is_valid, msg = validate_request_data(data)
        if not is_valid:
            logger.warning(f"数据验证失败: {msg}")
            return jsonify({'error': msg}), 400

        symbol = data['symbol']
        timeframe = data['timeframe']
        rates = data['rates']
        
        logger.info(f"收到信号请求: {symbol} {timeframe}, 数据条数: {len(rates)}")

        # 3. 转换为DataFrame
        df = data_processor.convert_to_dataframe(rates)
        
        if df.empty:
            return jsonify({'error': '无法处理K线数据'}), 400

        # 4. 生成信号 (AI或本地)
        result = generate_ai_signal(df, symbol, timeframe)
        
        # 5. 格式化响应
        response = {
            "signal": result['signal'],
            "strength": result['strength'],
            "analysis": result['analysis'],
            "timestamp": datetime.now().isoformat(),
            "server_time": time.time()
        }
        
        # 确保JSON序列化兼容性
        response = convert_numpy_types(response)
        
        logger.info(f"生成信号: {response['signal']} (强度: {response['strength']}) - {response['analysis'][:50]}...")
        request_stats['successful_requests'] += 1
        
        return jsonify(response)

    except Exception as e:
        logger.error(f"处理请求异常: {e}", exc_info=True)
        request_stats['failed_requests'] += 1
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """获取详细统计"""
    return jsonify({
        'request_stats': request_stats,
        'system': {
            'python': sys.version,
            'platform': sys.platform
        },
        'ai_status': {
            'deepseek_enabled': deepseek_client is not None,
            'qwen_enabled': qwen_client is not None
        }
    })

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 5002
    
    logger.info(f"启动AI量化交易服务器 - http://{host}:{port}")
    logger.info("集成模型: DeepSeek-V3, Qwen-Max")
    logger.info("等待MT5连接...")
    
    app.run(host=host, port=port, debug=False, threaded=True)
