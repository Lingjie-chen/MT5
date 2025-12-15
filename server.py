import sys
import os
import time
import socket
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

# Add the python directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

from flask import Flask, request, jsonify
from flask_cors import CORS  # 添加CORS支持
from data_processor import MT5DataProcessor
from deepseek_client import DeepSeekClient
from qwen_client import QwenClient
from dotenv import load_dotenv
import pandas as pd
import hashlib
import warnings

# 过滤警告
warnings.filterwarnings('ignore')

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)
# 启用CORS，允许所有域名访问（生产环境应限制）
CORS(app, resources={r"/*": {"origins": "*"}})

def get_local_ip() -> str:
    """获取本机局域网IP地址"""
    try:
        # 方法1: 连接到外部DNS服务器获取本地IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        try:
            # 方法2: 通过主机名获取IP
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return local_ip
        except:
            return "127.0.0.1"

def get_public_ip() -> str:
    """获取公网IP（如果需要从外部访问）"""
    try:
        import requests
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        return response.json()['ip']
    except:
        return ""

class SignalCache:
    """信号缓存管理器"""
    def __init__(self, expiry_seconds: int = 300):
        self.cache: Dict[str, dict] = {}
        self.expiry = expiry_seconds
    
    def get_key(self, symbol: str, timeframe: str, rates: list) -> str:
        """生成缓存键"""
        rates_str = json.dumps(rates, sort_keys=True) if rates else "no_rates"
        content = f"{symbol}_{timeframe}_{rates_str}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[dict]:
        """获取缓存"""
        if key in self.cache:
            cached_data = self.cache[key]
            if time.time() - cached_data["timestamp"] < self.expiry:
                return cached_data
            else:
                # 清理过期缓存
                del self.cache[key]
        return None
    
    def set(self, key: str, signal: str, signal_strength: int, metadata: dict = None):
        """设置缓存"""
        self.cache[key] = {
            "signal": signal,
            "signal_strength": signal_strength,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
    
    def cleanup(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = [
            key for key, value in self.cache.items() 
            if current_time - value["timestamp"] >= self.expiry
        ]
        for key in expired_keys:
            del self.cache[key]

# 初始化全局变量
local_ip = get_local_ip()
public_ip = get_public_ip()

print("=" * 60)
print("AI交易信号服务器 v2.0")
print("=" * 60)
print(f"本地IP地址: {local_ip}")
if public_ip:
    print(f"公网IP地址: {public_ip}")
print(f"服务器时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("-" * 60)

# 初始化AI客户端，遵循ValueCell的模型工厂模式
def initialize_ai_clients():
    """
    初始化AI客户端，遵循ValueCell的模型工厂模式，支持多模型提供商和故障恢复
    """
    siliconflow_api_key = os.getenv("SILICONFLOW_API_KEY", "")
    if not siliconflow_api_key:
        print("⚠ 未配置SILICONFLOW_API_KEY，AI功能将不可用")
        return None, None
    
    # 获取统一的SiliconFlow API URL
    siliconflow_api_url = os.getenv("SILICONFLOW_API_URL", "https://api.siliconflow.cn/v1")
    
    # DeepSeek客户端初始化
    deepseek_client = None
    try:
        deepseek_model = os.getenv("DEEPSEEK_MODEL", "deepseek-ai/DeepSeek-V3.1-Terminus")
        deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL", siliconflow_api_url)
        
        deepseek_client = DeepSeekClient(
            api_key=siliconflow_api_key,
            base_url=deepseek_base_url,
            model=deepseek_model
        )
        print(f"✓ DeepSeek客户端初始化成功 (模型: {deepseek_model}, API: {deepseek_base_url})")
    except Exception as e:
        print(f"✗ DeepSeek客户端初始化失败: {e}")
    
    # Qwen客户端初始化
    qwen_client = None
    try:
        qwen_model = os.getenv("QWEN_MODEL", "Qwen/Qwen3-VL-235B-A22B-Thinking")
        qwen_base_url = os.getenv("QWEN_BASE_URL", siliconflow_api_url)
        
        qwen_client = QwenClient(
            api_key=siliconflow_api_key,
            base_url=qwen_base_url,
            model=qwen_model
        )
        print(f"✓ Qwen客户端初始化成功 (模型: {qwen_model}, API: {qwen_base_url})")
    except Exception as e:
        print(f"✗ Qwen客户端初始化失败: {e}")
    
    return deepseek_client, qwen_client

# 初始化AI客户端
deepseek_client, qwen_client = initialize_ai_clients()

# 初始化处理器和缓存
processor = MT5DataProcessor()
signal_cache = SignalCache(expiry_seconds=int(os.getenv("CACHE_EXPIRY", 300)))
print(f"✓ 信号缓存已启用，过期时间: {signal_cache.expiry}秒")
print("-" * 60)

@app.route('/', methods=['GET'])
def index():
    """服务器主页"""
    server_info = {
        "server_name": "AI Trading Signal Server",
        "version": "2.0",
        "status": "running",
        "local_ip": local_ip,
        "public_ip": public_ip,
        "time": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "get_signal": "/get_signal (POST)",
            "cache_info": "/cache_info",
            "server_info": "/server_info"
        },
        "ai_enabled": bool(deepseek_client and qwen_client),
        "cache_size": len(signal_cache.cache)
    }
    return jsonify(server_info)

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache_size": len(signal_cache.cache)
    })

@app.route('/server_info', methods=['GET'])
def server_info():
    """服务器信息"""
    return jsonify({
        "local_ip": local_ip,
        "public_ip": public_ip,
        "mt5_connection_urls": [
            f"http://{local_ip}:{port}/get_signal",
            f"http://{public_ip}:{port}/get_signal" if public_ip else None
        ],
        "ai_enabled": bool(deepseek_client and qwen_client),
        "cache_enabled": True,
        "cache_expiry_seconds": signal_cache.expiry,
        "python_version": sys.version
    })

@app.route('/cache_info', methods=['GET'])
def cache_info():
    """缓存信息"""
    cache_items = []
    current_time = time.time()
    
    for key, value in signal_cache.cache.items():
        age = current_time - value["timestamp"]
        cache_items.append({
            "key": key[:20] + "...",  # 显示部分key
            "signal": value["signal"],
            "strength": value["signal_strength"],
            "age_seconds": int(age),
            "expires_in": max(0, int(signal_cache.expiry - age))
        })
    
    return jsonify({
        "total_items": len(signal_cache.cache),
        "expiry_seconds": signal_cache.expiry,
        "items": cache_items
    })

@app.route('/get_signal', methods=['POST', 'GET'])
def get_signal():
    """获取交易信号的主端点"""
    start_time = time.time()
    
    try:
        # 清理过期缓存
        signal_cache.cleanup()
        
        # 处理GET请求（用于测试）
        if request.method == 'GET':
            symbol = request.args.get('symbol', 'GOLD')
            timeframe = request.args.get('timeframe', 'H1')
            rates = []
            print(f"[GET] 收到请求: symbol={symbol}, timeframe={timeframe}")
        else:
            # 处理POST请求
            if not request.is_json:
                return jsonify({
                    "error": "Request must be JSON",
                    "signal": "none",
                    "signal_strength": 0,
                    "processing_time_ms": 0
                }), 400
            
            try:
                data = request.get_json(silent=True)  # 使用silent模式避免抛出异常
                if data is None:
                    # 尝试获取原始请求数据进行调试
                    raw_data = request.get_data(as_text=True)
                    print(f"[DEBUG] 无法解析JSON数据: {raw_data[:200]}...")
                    return jsonify({
                        "error": "Invalid JSON format",
                        "signal": "none",
                        "signal_strength": 0,
                        "processing_time_ms": 0
                    }), 400
            except Exception as e:
                raw_data = request.get_data(as_text=True)
                print(f"[DEBUG] JSON解析错误: {e}, 原始数据: {raw_data[:200]}...")
                return jsonify({
                    "error": f"JSON parsing error: {e}",
                    "signal": "none",
                    "signal_strength": 0,
                    "processing_time_ms": 0
                }), 400
            
            symbol = data.get('symbol', 'GOLD')
            timeframe = data.get('timeframe', 'H1')
            rates = data.get('rates', [])
            
            print(f"[POST] 收到请求: symbol={symbol}, timeframe={timeframe}, rates_count={len(rates)}")
        
        # 生成缓存键
        cache_key = signal_cache.get_key(symbol, timeframe, rates)
        
        # 检查缓存
        cached_result = signal_cache.get(cache_key)
        if cached_result:
            print(f"✓ 使用缓存结果: {cached_result['signal']} (强度: {cached_result['signal_strength']})")
            return jsonify({
                "symbol": symbol,
                "timeframe": timeframe,
                "signal": cached_result["signal"],
                "signal_strength": cached_result["signal_strength"],
                "from_cache": True,
                "cache_age_seconds": int(time.time() - cached_result["timestamp"]),
                "processing_time_ms": int((time.time() - start_time) * 1000),
                "timestamp": datetime.now().isoformat()
            })
        
        # 处理数据
        if not rates or len(rates) == 0:
            # 生成模拟数据
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            df = processor.get_historical_data(symbol, None, start_date, end_date)
            if df is None or len(df) == 0:
                return jsonify({
                    "error": f"无法获取{symbol}的历史数据",
                    "signal": "none",
                    "signal_strength": 0,
                    "processing_time_ms": int((time.time() - start_time) * 1000)
                }), 400
        else:
            # 转换请求数据
            df = pd.DataFrame(rates)
            
            # 标准化列名
            column_mapping = {
                'time': ['time', 'Time', 'datetime', 'Date'],
                'open': ['open', 'Open'],
                'high': ['high', 'High'],
                'low': ['low', 'Low'],
                'close': ['close', 'Close'],
                'volume': ['volume', 'Volume', 'tick_volume', 'TickVolume']
            }
            
            for standard_name, possible_names in column_mapping.items():
                for name in possible_names:
                    if name in df.columns and standard_name not in df.columns:
                        df[standard_name] = df[name]
                        break
            
            # 确保必要的列存在
            required_columns = ['time', 'open', 'high', 'low', 'close']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return jsonify({
                    "error": f"缺少必要的列: {missing_columns}",
                    "signal": "none",
                    "signal_strength": 0,
                    "processing_time_ms": int((time.time() - start_time) * 1000)
                }), 400
            
            # 处理时间列
            try:
                if df['time'].dtype == 'object' or 'int' in str(df['time'].dtype):
                    # 尝试转换为datetime
                    df['time'] = pd.to_datetime(df['time'], errors='coerce', unit='s')
            except:
                pass
            
            df.set_index('time', inplace=True)
        
        # 生成技术指标
        original_length = len(df)
        df = processor.generate_features(df)
        feature_length = len(df)
        
        print(f"[DEBUG] 数据点统计: 原始={original_length}, 生成特征后={feature_length}")
        
        if len(df) < 5:
            return jsonify({
                "error": "数据不足，至少需要5个数据点",
                "signal": "none",
                "signal_strength": 0,
                "processing_time_ms": int((time.time() - start_time) * 1000),
                "debug_info": {
                    "original_data_points": original_length,
                    "after_features_data_points": feature_length
                }
            }), 400
        
        # 准备AI分析数据
        ai_analysis = None
        if deepseek_client and qwen_client:
            try:
                df_tail = df.tail(20).reset_index()
                df_tail['time'] = df_tail['time'].astype(str)
                model_input = df_tail.to_dict(orient='records')
                
                # DeepSeek分析
                deepseek_result = deepseek_client.analyze_market_structure(model_input)
                
                # Qwen优化
                qwen_result = qwen_client.optimize_strategy_logic(deepseek_result, model_input)
                
                ai_analysis = {
                    "deepseek": deepseek_result,
                    "qwen": qwen_result
                }
                print("✓ AI分析完成")
            except Exception as e:
                print(f"⚠ AI分析失败: {e}")
                ai_analysis = None
        
        # 生成交易信号
        signal = "none"
        signal_strength = 50
        indicators = {}
        
        try:
            # EMA交叉策略
            if 'ema_fast' in df.columns and 'ema_slow' in df.columns:
                last_ema_fast = df['ema_fast'].iloc[-1]
                last_ema_slow = df['ema_slow'].iloc[-1]
                prev_ema_fast = df['ema_fast'].iloc[-2]
                prev_ema_slow = df['ema_slow'].iloc[-2]
                
                indicators['ema_fast'] = float(last_ema_fast)
                indicators['ema_slow'] = float(last_ema_slow)
                indicators['ema_cross'] = "golden" if last_ema_fast > last_ema_slow else "death"
            
            # RSI指标
            if 'rsi' in df.columns:
                rsi = df['rsi'].iloc[-1]
                indicators['rsi'] = float(rsi)
                
                # 根据AI分析调整信号强度
                if ai_analysis and 'signal_strength' in ai_analysis['qwen']:
                    signal_strength = min(100, max(0, ai_analysis['qwen']['signal_strength']))
                else:
                    # 传统信号生成逻辑
                    if 'ema_fast' in df.columns and 'ema_slow' in df.columns:
                        if prev_ema_fast < prev_ema_slow and last_ema_fast > last_ema_slow and rsi < 70:
                            signal = "buy"
                            signal_strength = min(90, int(rsi * 1.2))
                        elif prev_ema_fast > prev_ema_slow and last_ema_fast < last_ema_slow and rsi > 30:
                            signal = "sell"
                            signal_strength = min(90, int((100 - rsi) * 1.2))
            
            # MACD指标
            if 'macd' in df.columns and 'macd_signal' in df.columns:
                macd = df['macd'].iloc[-1]
                macd_signal = df['macd_signal'].iloc[-1]
                indicators['macd'] = float(macd)
                indicators['macd_signal'] = float(macd_signal)
                indicators['macd_histogram'] = float(macd - macd_signal)
            
            # 价格信息
            indicators['current_price'] = float(df['close'].iloc[-1])
            indicators['price_change'] = float((df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2] * 100)
            
        except Exception as e:
            print(f"⚠ 指标计算失败: {e}")
        
        # 缓存结果
        signal_cache.set(
            key=cache_key,
            signal=signal,
            signal_strength=signal_strength,
            metadata={
                "symbol": symbol,
                "timeframe": timeframe,
                "indicators": indicators,
                "ai_used": bool(ai_analysis)
            }
        )
        
        # 构建响应
        response = {
            "symbol": symbol,
            "timeframe": timeframe,
            "signal": signal,
            "signal_strength": signal_strength,
            "indicators": indicators,
            "from_cache": False,
            "ai_analysis_used": bool(ai_analysis),
            "processing_time_ms": int((time.time() - start_time) * 1000),
            "timestamp": datetime.now().isoformat(),
            "cache_key": cache_key,
            "data_points": len(df)
        }
        
        print(f"✓ 生成信号: {signal} (强度: {signal_strength})")
        return jsonify(response)
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"✗ 处理请求时出错: {e}")
        print(f"详细错误:\n{error_trace}")
        
        return jsonify({
            "error": str(e),
            "signal": "none",
            "signal_strength": 0,
            "processing_time_ms": int((time.time() - start_time) * 1000),
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    # 配置服务器
    host = os.getenv("SERVER_HOST", "0.0.0.0")  # 监听所有网络接口
    port = int(os.getenv("SERVER_PORT", 5001))
    
    print("服务器配置:")
    print(f"  监听地址: {host}")
    print(f"  端口: {port}")
    print(f"  本地访问: http://localhost:{port}")
    print(f"  局域网访问: http://{local_ip}:{port}")
    if public_ip:
        print(f"  公网访问: http://{public_ip}:{port}")
    print("-" * 60)
    print("MT5连接配置:")
    print(f"  在MT5中使用: http://{local_ip}:{port}/get_signal")
    print("-" * 60)
    print("按 Ctrl+C 停止服务器")
    print("=" * 60)
    
    # 运行服务器
    try:
        app.run(
            host=host,
            port=port,
            debug=False,  # 生产环境设置为False
            threaded=True  # 启用多线程处理请求
        )
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"服务器启动失败: {e}")