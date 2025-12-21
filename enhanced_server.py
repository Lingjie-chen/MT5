#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版Python服务器 - 集成机器学习和高级分析功能
基于MQL5-Python集成最佳实践
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
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

try:
    import psutil
except ImportError:
    psutil = None

# 导入自定义模块
from python.advanced_analysis import AdvancedMarketAnalysis
from python.data_processor import MT5DataProcessor

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

# 请求统计
request_stats = {
    'total_requests': 0,
    'successful_requests': 0,
    'failed_requests': 0,
    'last_request_time': None,
    'average_response_time': 0.0
}

# 性能监控
performance_stats = {
    'ml_predictions': 0,
    'technical_analysis': 0,
    'market_regime_detections': 0,
    'cache_hits': 0,
    'cache_misses': 0
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
        # 检查必需字段
        required_fields = ['symbol', 'timeframe', 'count', 'rates']
        for field in required_fields:
            if field not in data:
                return False, f"缺少必需字段: {field}"
        
        # 验证symbol格式
        symbol = str(data['symbol']).strip()
        if len(symbol) == 0 or len(symbol) > 20:
            return False, f"无效的交易品种格式: '{symbol}' (长度: {len(symbol)})"
        
        # 验证时间周期格式
        timeframe = str(data['timeframe']).strip()
        valid_timeframes = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1', 'W1', 'MN1']
        if timeframe not in valid_timeframes:
            return False, f"无效的时间周期: {timeframe} (有效值: {valid_timeframes})"
        
        # 验证数据条数
        count = int(data['count'])
        if count < 10 or count > 1000:
            return False, f"数据条数超出范围: {count} (有效范围: 10-1000)"
        
        # 验证rates数组
        rates = data['rates']
        if not isinstance(rates, list):
            return False, f"rates不是数组类型，实际类型: {type(rates)} (值: {rates})"
        if len(rates) != count:
            return False, f"rates数组长度({len(rates)})与指定的count({count})不匹配"
        
        # 验证每个rate条目的完整性
        for i, rate in enumerate(rates):
            if not isinstance(rate, dict):
                return False, f"第{i}个rate条目格式错误，不是字典类型，实际类型: {type(rate)} (值: {rate})"
            
            required_rate_fields = ['time', 'open', 'high', 'low', 'close', 'tick_volume']
            for field in required_rate_fields:
                if field not in rate:
                    return False, f"第{i}个rate条目缺少字段: {field} (当前字段: {list(rate.keys())})"
            
            # 验证数值范围
            time_val = int(rate['time'])
            if time_val < 0 or time_val > 2000000000:  # 合理的时间戳范围
                return False, f"第{i}个rate条目的时间戳无效: {time_val} (有效范围: 0-2000000000)"
            
            open_val = float(rate['open'])
            high_val = float(rate['high'])
            low_val = float(rate['low'])
            close_val = float(rate['close'])
            
            if not (0 < open_val < 1000000 and 0 < high_val < 1000000 and 
                    0 < low_val < 1000000 and 0 < close_val < 1000000):
                return False, f"第{i}个rate条目的价格值超出合理范围: open={open_val}, high={high_val}, low={low_val}, close={close_val} (有效范围: 0-1000000)"
            
            if not (low_val <= open_val <= high_val and low_val <= close_val <= high_val):
                return False, f"第{i}个rate条目的价格逻辑错误: open={open_val}, high={high_val}, low={low_val}, close={close_val} (应满足: low <= open <= high 且 low <= close <= high)"
            
            volume_val = int(rate['tick_volume'])
            if volume_val < 0 or volume_val > 1000000000:
                return False, f"第{i}个rate条目的成交量无效: {volume_val} (有效范围: 0-1000000000)"
        
        return True, "数据验证通过"
        
    except (ValueError, TypeError) as e:
        return False, f"数据验证异常: {e} (数据类型错误)"
    except Exception as e:
        return False, f"未知验证错误: {e} (其他错误)"

def sanitize_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """清理和标准化输入数据"""
    sanitized = {}
    
    # 清理symbol
    if 'symbol' in data:
        sanitized['symbol'] = str(data['symbol']).strip().upper()
    
    # 清理timeframe
    if 'timeframe' in data:
        sanitized['timeframe'] = str(data['timeframe']).strip().upper()
    
    # 清理count
    if 'count' in data:
        try:
            sanitized['count'] = max(10, min(1000, int(data['count'])))
        except (ValueError, TypeError):
            sanitized['count'] = 100
    
    # 清理rates数据
    if 'rates' in data and isinstance(data['rates'], list):
        sanitized_rates = []
        for rate in data['rates']:
            if isinstance(rate, dict):
                sanitized_rate = {}
                for key in ['time', 'open', 'high', 'low', 'close', 'tick_volume']:
                    if key in rate:
                        try:
                            if key == 'time' or key == 'tick_volume':
                                sanitized_rate[key] = int(rate[key])
                            else:
                                sanitized_rate[key] = float(rate[key])
                        except (ValueError, TypeError):
                            # 使用默认值
                            if key == 'time':
                                sanitized_rate[key] = 0
                            elif key == 'tick_volume':
                                sanitized_rate[key] = 0
                            else:
                                sanitized_rate[key] = 0.0
                
                # 确保价格逻辑正确
                if all(k in sanitized_rate for k in ['open', 'high', 'low', 'close']):
                    sanitized_rate['low'] = min(sanitized_rate['low'], sanitized_rate['open'], sanitized_rate['close'])
                    sanitized_rate['high'] = max(sanitized_rate['high'], sanitized_rate['open'], sanitized_rate['close'])
                
                sanitized_rates.append(sanitized_rate)
        
        sanitized['rates'] = sanitized_rates
    
    return sanitized

def monitor_request(func):
    """请求监控装饰器"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        request_stats['total_requests'] += 1
        request_stats['last_request_time'] = datetime.now().isoformat()
        
        try:
            result = func(*args, **kwargs)
            request_stats['successful_requests'] += 1
            
            # 更新平均响应时间
            response_time = time.time() - start_time
            if request_stats['average_response_time'] == 0:
                request_stats['average_response_time'] = response_time
            else:
                request_stats['average_response_time'] = (
                    request_stats['average_response_time'] * 0.9 + response_time * 0.1
                )
            
            logger.info(f"请求处理成功: {func.__name__}, 耗时: {response_time:.3f}s")
            return result
            
        except Exception as e:
            request_stats['failed_requests'] += 1
            logger.error(f"请求处理失败: {func.__name__}, 错误: {e}")
            raise
    
    wrapper.__name__ = func.__name__
    return wrapper

class MLSignalGenerator:
    """机器学习信号生成器"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.training_data = []
        self.last_training_time = 0
        
    def extract_features(self, df: pd.DataFrame) -> np.ndarray:
        """从价格数据中提取特征"""
        features = []
        
        # 价格相关特征
        features.extend([
            df['close'].pct_change().iloc[-1],  # 最新价格变化率
            df['close'].pct_change().rolling(5).mean().iloc[-1],  # 5周期平均变化率
            df['close'].pct_change().rolling(10).mean().iloc[-1],  # 10周期平均变化率
            df['close'].pct_change().rolling(20).mean().iloc[-1],  # 20周期平均变化率
        ])
        
        # 波动率特征
        returns = df['close'].pct_change()
        features.extend([
            returns.rolling(5).std().iloc[-1],  # 5周期波动率
            returns.rolling(10).std().iloc[-1],  # 10周期波动率
            returns.rolling(20).std().iloc[-1],  # 20周期波动率
        ])
        
        # 技术指标特征
        features.extend([
            (df['close'] - df['close'].rolling(5).mean()).iloc[-1] / df['close'].rolling(5).std().iloc[-1],  # 5周期Z-score
            (df['close'] - df['close'].rolling(10).mean()).iloc[-1] / df['close'].rolling(10).std().iloc[-1],  # 10周期Z-score
            (df['close'] - df['close'].rolling(20).mean()).iloc[-1] / df['close'].rolling(20).std().iloc[-1],  # 20周期Z-score
        ])
        
        # 成交量特征
        features.extend([
            df['volume'].pct_change().iloc[-1],  # 成交量变化率
            df['volume'].rolling(5).mean().iloc[-1],  # 5周期平均成交量
        ])
        
        return np.array(features).reshape(1, -1)
    
    def create_label(self, df: pd.DataFrame, future_periods: int = 3) -> int:
        """创建标签（未来价格方向）"""
        current_price = df['close'].iloc[-1]
        future_price = df['close'].shift(-future_periods).iloc[-future_periods]
        
        if future_price > current_price * 1.002:  # 上涨超过0.2%
            return 1  # 买入信号
        elif future_price < current_price * 0.998:  # 下跌超过0.2%
            return -1  # 卖出信号
        else:
            return 0  # 持有信号
    
    def add_training_sample(self, df: pd.DataFrame, actual_signal: str):
        """添加训练样本"""
        try:
            features = self.extract_features(df)
            
            # 将实际信号转换为标签
            if actual_signal == "buy":
                label = 1
            elif actual_signal == "sell":
                label = -1
            else:
                label = 0
            
            self.training_data.append({
                'features': features.flatten(),
                'label': label,
                'timestamp': time.time()
            })
            
            # 限制训练数据大小
            if len(self.training_data) > 1000:
                self.training_data = self.training_data[-1000:]
                
        except Exception as e:
            logger.warning(f"添加训练样本失败: {e}")
    
    def train_model(self):
        """训练机器学习模型"""
        if len(self.training_data) < 100:
            logger.info("训练数据不足，跳过训练")
            return
        
        try:
            # 准备训练数据
            X = np.array([sample['features'] for sample in self.training_data])
            y = np.array([sample['label'] for sample in self.training_data])
            
            # 数据标准化
            X_scaled = self.scaler.fit_transform(X)
            
            # 训练模型
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            self.model.fit(X_scaled, y)
            self.is_trained = True
            self.last_training_time = time.time()
            
            # 评估模型性能
            accuracy = self.model.score(X_scaled, y)
            logger.info(f"模型训练完成，准确率: {accuracy:.3f}")
            
        except Exception as e:
            logger.error(f"模型训练失败: {e}")
    
    def predict_signal(self, df: pd.DataFrame) -> Dict[str, Any]:
        """使用机器学习模型预测信号"""
        if not self.is_trained:
            return {
                'signal': 'hold',
                'confidence': 0.0,
                'method': 'ml',
                'reason': '模型未训练'
            }
        
        try:
            features = self.extract_features(df)
            features_scaled = self.scaler.transform(features)
            
            prediction = self.model.predict(features_scaled)[0]
            probabilities = self.model.predict_proba(features_scaled)[0]
            
            # 根据预测结果生成信号
            if prediction == 1:
                signal = 'buy'
                confidence = probabilities[2] if len(probabilities) == 3 else 0.5  # 买入类概率
            elif prediction == -1:
                signal = 'sell'
                confidence = probabilities[0] if len(probabilities) == 3 else 0.5  # 卖出类概率
            else:
                signal = 'hold'
                confidence = probabilities[1] if len(probabilities) == 3 else 0.5  # 持有类概率
            
            return {
                'signal': signal,
                'confidence': float(confidence),
                'method': 'ml',
                'reason': '机器学习模型预测'
            }
            
        except Exception as e:
            logger.error(f"机器学习预测失败: {e}")
            return {
                'signal': 'hold',
                'confidence': 0.0,
                'method': 'ml',
                'reason': f'预测失败: {e}'
            }

class EnhancedSignalGenerator:
    """增强版信号生成器，集成多种分析方法"""
    
    def __init__(self):
        self.analysis_tool = AdvancedMarketAnalysis()
        self.data_processor = MT5DataProcessor()
        self.ml_generator = MLSignalGenerator()
        
        # 信号缓存
        self.signal_cache = {}
        self.cache_expiry = 300  # 5分钟
        
        # 性能跟踪
        self.signal_history = []
        self.max_history_size = 1000
    
    def _timeframe_to_int(self, timeframe: str) -> int:
        """将时间周期字符串转换为整数表示"""
        timeframe_map = {
            'M1': 1, 'M5': 5, 'M15': 15, 'M30': 30,
            'H1': 60, 'H4': 240, 'D1': 1440, 'W1': 10080, 'MN1': 43200
        }
        return timeframe_map.get(timeframe.upper(), 60)  # 默认H1
    
    def _perform_technical_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """执行技术分析"""
        try:
            indicators = self.analysis_tool.calculate_technical_indicators(df)
            
            # 生成技术分析信号
            signal_info = self.analysis_tool.generate_signal_from_indicators(indicators)
            
            return {
                'signal': signal_info.get('signal', 'hold'),
                'strength': signal_info.get('strength', 50),
                'indicators': indicators,
                'method': 'technical'
            }
            
        except Exception as e:
            logger.error(f"技术分析失败: {e}")
            return {
                'signal': 'hold',
                'strength': 0,
                'indicators': {},
                'method': 'technical',
                'error': str(e)
            }
    
    def _perform_ml_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """执行机器学习分析"""
        return self.ml_generator.predict_signal(df)
    
    def _perform_market_regime_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """执行市场状态分析"""
        try:
            regime_info = self.analysis_tool.detect_market_regime(df)
            
            # 根据市场状态调整信号权重
            regime_weights = {
                'trending': 1.2,      # 趋势市场增加权重
                'ranging': 0.8,       # 震荡市场降低权重
                'high_volatility': 0.6  # 高波动市场大幅降低权重
            }
            
            weight = regime_weights.get(regime_info['regime'], 1.0)
            
            return {
                'regime': regime_info['regime'],
                'confidence': regime_info['confidence'],
                'weight': weight,
                'description': regime_info['description']
            }
            
        except Exception as e:
            logger.error(f"市场状态分析失败: {e}")
            return {
                'regime': 'unknown',
                'confidence': 0.0,
                'weight': 1.0,
                'description': '分析失败'
            }
    
    def _generate_final_signal(self, 
                             technical_analysis: Dict[str, Any],
                             ml_analysis: Dict[str, Any],
                             regime_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成最终交易信号"""
        
        # 收集所有信号
        signals = []
        weights = []
        confidences = []
        
        # 技术分析信号
        if technical_analysis.get('signal') != 'hold':
            signals.append(technical_analysis['signal'])
            weights.append(0.4)  # 技术分析权重
            confidences.append(technical_analysis.get('strength', 50) / 100)
        
        # 机器学习信号
        if ml_analysis.get('signal') != 'hold' and ml_analysis.get('confidence', 0) > 0.6:
            signals.append(ml_analysis['signal'])
            weights.append(0.6)  # 机器学习权重
            confidences.append(ml_analysis.get('confidence', 0))
        
        # 如果没有有效信号，返回持有
        if not signals:
            return {
                'signal': 'hold',
                'strength': 0,
                'confidence': 0.0,
                'reason': '所有分析方法均建议持有',
                'components': {
                    'technical': technical_analysis,
                    'ml': ml_analysis,
                    'regime': regime_analysis
                }
            }
        
        # 加权投票
        buy_score = 0.0
        sell_score = 0.0
        total_weight = 0.0
        
        for i, signal in enumerate(signals):
            weight = weights[i] * regime_analysis.get('weight', 1.0)
            confidence = confidences[i]
            
            if signal == 'buy':
                buy_score += weight * confidence
            elif signal == 'sell':
                sell_score += weight * confidence
            
            total_weight += weight
        
        # 归一化得分
        if total_weight > 0:
            buy_score /= total_weight
            sell_score /= total_weight
        
        # 生成最终信号
        if buy_score > sell_score and buy_score > 0.6:
            final_signal = 'buy'
            final_strength = int(buy_score * 100)
            reason = f"买入信号强烈 (得分: {buy_score:.3f})"
        elif sell_score > buy_score and sell_score > 0.6:
            final_signal = 'sell'
            final_strength = int(sell_score * 100)
            reason = f"卖出信号强烈 (得分: {sell_score:.3f})"
        else:
            final_signal = 'hold'
            final_strength = 0
            reason = f"信号不明确 (买入: {buy_score:.3f}, 卖出: {sell_score:.3f})"
        
        return {
            'signal': final_signal,
            'strength': final_strength,
            'confidence': max(buy_score, sell_score),
            'reason': reason,
            'components': {
                'technical': technical_analysis,
                'ml': ml_analysis,
                'regime': regime_analysis
            }
        }
    
    def generate_comprehensive_signal(self, symbol: str, timeframe: str, rates_data: List[Dict]) -> Dict[str, Any]:
        """生成综合交易信号"""
        
        # 检查缓存
        cache_key = f"{symbol}_{timeframe}_{int(time.time() // 60)}"  # 每分钟缓存
        if cache_key in self.signal_cache:
            cached_signal = self.signal_cache[cache_key]
            if time.time() - cached_signal['timestamp'] < self.cache_expiry:
                cached_signal['cached'] = True
                return cached_signal
        
        try:
            # 转换为DataFrame
            df = self.data_processor.convert_to_dataframe(rates_data)
            
            if df.empty or len(df) < 20:
                return {
                    'signal': 'hold',
                    'strength': 0,
                    'confidence': 0.0,
                    'reason': '数据不足，无法分析',
                    'timestamp': time.time()
                }
            
            # 执行各种分析
            technical_analysis = self._perform_technical_analysis(df)
            ml_analysis = self._perform_ml_analysis(df)
            regime_analysis = self._perform_market_regime_analysis(df)
            
            # 生成最终信号
            final_signal = self._generate_final_signal(technical_analysis, ml_analysis, regime_analysis)
            final_signal.update({
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': time.time(),
                'cached': False
            })
            
            # 缓存信号
            self.signal_cache[cache_key] = final_signal
            
            # 记录信号历史
            self.signal_history.append(final_signal)
            if len(self.signal_history) > self.max_history_size:
                self.signal_history = self.signal_history[-self.max_history_size:]
            
            logger.info(f"生成信号: {final_signal['signal']} (强度: {final_signal['strength']})")
            return final_signal
            
        except Exception as e:
            logger.error(f"生成综合信号失败: {e}")
            return {
                'signal': 'hold',
                'strength': 0,
                'confidence': 0.0,
                'reason': f'分析失败: {e}',
                'timestamp': time.time()
            }
    
    def get_detailed_analysis(self, symbol: str, timeframe: str, rates_data: List[Dict]) -> Dict[str, Any]:
        """获取详细分析报告"""
        try:
            df = self.data_processor.convert_to_dataframe(rates_data)
            
            if df.empty or len(df) < 20:
                return {
                    'error': '数据不足，无法进行详细分析',
                    'timestamp': time.time()
                }
            
            # 技术指标分析
            technical_indicators = self.analysis_tool.calculate_technical_indicators(df)
            
            # 市场状态分析
            market_regime = self.analysis_tool.detect_market_regime(df)
            
            # 支撑阻力分析
            support_resistance = self.analysis_tool.generate_support_resistance(df)
            
            # 风险指标分析
            risk_metrics = self.analysis_tool.calculate_risk_metrics(df)
            
            # 机器学习分析
            ml_signal = self.ml_generator.predict_signal(df)
            
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': time.time(),
                'technical_analysis': technical_indicators,
                'market_regime': market_regime,
                'support_resistance': support_resistance,
                'risk_metrics': risk_metrics,
                'ml_analysis': ml_signal,
                'current_price': float(df['close'].iloc[-1]),
                'price_change_24h': float((df['close'].iloc[-1] - df['close'].iloc[-24]) / df['close'].iloc[-24] * 100) if len(df) >= 24 else 0.0
            }
            
        except Exception as e:
            logger.error(f"生成详细分析失败: {e}")
            return {
                'error': f'详细分析失败: {e}',
                'timestamp': time.time()
            }

# 全局信号生成器实例
signal_generator = EnhancedSignalGenerator()

@app.route('/health', methods=['GET'])
@monitor_request
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'request_stats': request_stats,
        'performance_stats': performance_stats,
        'uptime': time.time() - app_start_time if 'app_start_time' in globals() else 0
    })

@app.route('/stats', methods=['GET'])
@monitor_request
def get_stats():
    """获取详细统计信息"""
    return jsonify({
        'request_stats': request_stats,
        'performance_stats': performance_stats,
        'system_info': {
            'python_version': sys.version,
            'platform': sys.platform,
            'memory_usage': psutil.Process().memory_info().rss / 1024 / 1024 if 'psutil' in sys.modules else 'N/A'
        }
    })

@app.route('/get_signal', methods=['POST'])
@app.route('/signal', methods=['POST'])  # 添加兼容性端点
@monitor_request
def get_signal():
    """获取交易信号端点"""
    try:
        # 增强JSON解析容错性
        if not request.data:
            return jsonify({
                'error': '请求体为空',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        try:
            data = request.get_json()
            logger.info(f"JSON解析成功，数据类型: {type(data)}")
            if data:
                logger.info(f"解析后的数据: symbol={data.get('symbol', 'N/A')}, timeframe={data.get('timeframe', 'N/A')}, count={data.get('count', 'N/A')}")
        except Exception as json_error:
            logger.warning(f"JSON解析失败 (request.get_json()): {json_error}")
            logger.warning(f"请求头: {request.headers}")
            logger.warning(f"请求体前200字符: {request.data.decode('utf-8')[:200]}...")
            # 尝试手动解析JSON
            try:
                data = json.loads(request.data.decode('utf-8'))
                logger.info(f"手动JSON解析成功")
                if data:
                    logger.info(f"手动解析后的数据: symbol={data.get('symbol', 'N/A')}, timeframe={data.get('timeframe', 'N/A')}, count={data.get('count', 'N/A')}")
            except Exception as manual_error:
                logger.error(f"手动JSON解析失败: {manual_error}")
                logger.error(f"完整请求体: {request.data.decode('utf-8')}")
                return jsonify({
                    'error': f'无效的JSON格式: {str(manual_error)}',
                    'timestamp': datetime.now().isoformat()
                }), 400
        
        if not data:
            logger.warning("解析后的数据为空")
            return jsonify({
                'error': '无效的请求数据',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # 数据验证
        is_valid, validation_message = validate_request_data(data)
        if not is_valid:
            logger.warning(f"数据验证失败: {validation_message}")
            logger.warning(f"验证失败的数据结构: symbol={data.get('symbol', 'N/A')}, timeframe={data.get('timeframe', 'N/A')}, count={data.get('count', 'N/A')}")
            logger.warning(f"rates数组长度: {len(data.get('rates', [])) if isinstance(data.get('rates'), list) else 'N/A'}")
            if data.get('rates') and isinstance(data.get('rates'), list) and len(data.get('rates')) > 0:
                first_rate = data['rates'][0]
                logger.warning(f"第一个rate条目: {first_rate}")
            # 添加更多调试信息
            logger.warning(f"完整数据结构: {data}")
            # 特别记录原始请求数据用于调试
            raw_data_str = request.data.decode('utf-8') if request.data else "无原始数据"
            logger.warning(f"原始请求数据: {raw_data_str[:500]}...")  # 只记录前500个字符
            return jsonify({
                'error': f'数据验证失败: {validation_message}',
                'timestamp': datetime.now().isoformat(),
                'details': {
                    'symbol': data.get('symbol', 'N/A'),
                    'timeframe': data.get('timeframe', 'N/A'),
                    'count': data.get('count', 'N/A'),
                    'rates_length': len(data.get('rates', [])) if isinstance(data.get('rates'), list) else 'N/A'
                }
            }), 400
        
        # 数据清理和标准化
        sanitized_data = sanitize_input(data)
        
        symbol = sanitized_data.get('symbol', 'EURUSD')
        timeframe = sanitized_data.get('timeframe', 'H1')
        count = sanitized_data.get('count', 100)
        rates = sanitized_data.get('rates', [])
        
        # 如果没有提供rates数据，则自动生成或从MT5获取
        if not rates:
            # 尝试从MT5获取数据，如果失败则使用模拟数据
            from datetime import datetime as dt, timedelta
            end_date = dt.now()
            start_date = end_date - timedelta(days=30)  # 默认30天数据
            
            # 使用数据处理器获取数据
            df = signal_generator.data_processor.get_historical_data(
                symbol, 
                signal_generator._timeframe_to_int(timeframe), 
                start_date, 
                end_date
            )
            
            # 转换为rates格式
            rates = df.reset_index().to_dict('records')
        
        # 生成交易信号
        signal = signal_generator.generate_comprehensive_signal(symbol, timeframe, rates)
        
        # 转换numpy类型为原生Python类型，解决"Object of type int64 is not JSON serializable"错误
        signal = convert_numpy_types(signal)
        
        # 添加安全审计信息
        signal['security_audit'] = {
            'data_validated': True,
            'data_sanitized': True,
            'validation_message': validation_message,
            'request_timestamp': datetime.now().isoformat()
        }
        
        return jsonify(signal)
        
    except Exception as e:
        logger.error(f"获取信号失败: {e}")
        return jsonify({
            'error': f'内部服务器错误: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/analysis', methods=['POST'])
def get_detailed_analysis():
    """获取详细分析报告端点"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': '无效的请求数据',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        symbol = data.get('symbol', 'GOLD')
        timeframe = data.get('timeframe', 'H1')
        rates = data.get('rates', [])
        
        # 如果没有提供rates数据，则自动生成或从MT5获取
        if not rates:
            # 尝试从MT5获取数据，如果失败则使用模拟数据
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)  # 默认30天数据
            
            # 使用数据处理器获取数据
            df = signal_generator.data_processor.get_historical_data(
                symbol, 
                signal_generator._timeframe_to_int(timeframe), 
                start_date, 
                end_date
            )
            
            # 转换为rates格式
            rates = df.reset_index().to_dict('records')
        
        # 生成详细分析报告
        analysis = signal_generator.get_detailed_analysis(symbol, timeframe, rates)
        
        # 转换numpy类型为原生Python类型
        analysis = convert_numpy_types(analysis)
        
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"获取详细分析失败: {e}")
        return jsonify({
            'error': f'服务器内部错误: {e}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/train_model', methods=['POST'])
def train_model():
    """手动触发模型训练"""
    try:
        signal_generator.ml_generator.train_model()
        
        return jsonify({
            'status': 'training_started',
            'timestamp': datetime.now().isoformat(),
            'message': '模型训练已开始'
        })
        
    except Exception as e:
        logger.error(f"模型训练失败: {e}")
        return jsonify({
            'error': f'模型训练失败: {e}',
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    logger.info("启动增强版Python服务器...")
    
    # 配置服务器参数
    host = '0.0.0.0'
    port = 5002
    debug = False
    
    logger.info(f"服务器运行在: http://{host}:{port}")
    logger.info("可用端点:")
    logger.info("  GET  /health - 健康检查")
    logger.info("  POST /get_signal - 获取交易信号")
    logger.info("  POST /analysis - 获取详细分析")
    logger.info("  POST /train_model - 手动训练模型")
    logger.info("  GET  /stats - 获取统计信息")
    
    app.run(host=host, port=port, debug=debug, threaded=True)