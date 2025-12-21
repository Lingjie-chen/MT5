#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Socket版本Python服务器 - 基于底层Socket通信
集成机器学习和高级分析功能
基于MQL5-Python集成最佳实践
"""

import socket
import json
import time
import threading
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# 自定义JSON编码器处理numpy类型
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)

# 硅基流动大模型集成类
class SiliconFlowModel:
    """硅基流动大模型集成类"""
    
    def __init__(self, model_name: str = "silicon_flow"):
        self.model_name = model_name
        self.is_available = False
        self.last_analysis_time = 0
        self.analysis_cache = {}
        self.cache_expiry = 600  # 10分钟缓存
        
        # 初始化大模型连接
        self._initialize_model()
    
    def _initialize_model(self):
        """初始化大模型连接"""
        try:
            # 这里可以集成实际的硅基流动大模型API
            # 目前使用模拟实现
            self.is_available = True
            logger.info(f"硅基流动大模型 {self.model_name} 初始化成功")
        except Exception as e:
            logger.warning(f"硅基流动大模型初始化失败: {e}")
            self.is_available = False
    
    def analyze_market_context(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Dict[str, Any]:
        """使用大模型分析市场上下文"""
        
        # 检查缓存
        cache_key = f"{symbol}_{timeframe}_{int(time.time() // 300)}"  # 5分钟缓存
        if cache_key in self.analysis_cache:
            cached_result = self.analysis_cache[cache_key]
            if time.time() - cached_result['timestamp'] < self.cache_expiry:
                return cached_result
        
        if not self.is_available:
            return self._generate_simulated_analysis(df, symbol, timeframe)
        
        try:
            # 准备分析数据
            analysis_data = self._prepare_analysis_data(df, symbol, timeframe)
            
            # 调用大模型API（模拟实现）
            result = self._call_llm_api(analysis_data)
            
            # 缓存结果
            result['timestamp'] = time.time()
            self.analysis_cache[cache_key] = result
            
            # 清理过期缓存
            self._clean_expired_cache()
            
            return result
            
        except Exception as e:
            logger.error(f"大模型分析失败: {e}")
            return self._generate_simulated_analysis(df, symbol, timeframe)
    
    def _prepare_analysis_data(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Dict[str, Any]:
        """准备分析数据"""
        
        # 计算基本统计指标
        price_stats = {
            'current_price': df['close'].iloc[-1],
            'price_change_1d': (df['close'].iloc[-1] / df['close'].iloc[-2] - 1) * 100 if len(df) >= 2 else 0,
            'price_change_5d': (df['close'].iloc[-1] / df['close'].iloc[-6] - 1) * 100 if len(df) >= 6 else 0,
            'volatility': df['close'].pct_change().std() * 100,
            'volume_trend': df['volume'].pct_change().mean() * 100
        }
        
        # 技术指标
        technical_indicators = {
            'rsi': self._calculate_rsi(df['close']).iloc[-1] if len(df) >= 14 else 50,
            'macd': self._calculate_macd(df['close']).iloc[-1] if len(df) >= 26 else 0,
            'sma_20': df['close'].rolling(20).mean().iloc[-1] if len(df) >= 20 else df['close'].iloc[-1],
            'sma_50': df['close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else df['close'].iloc[-1]
        }
        
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'price_stats': price_stats,
            'technical_indicators': technical_indicators,
            'data_points': len(df),
            'analysis_time': time.time()
        }
    
    def _call_llm_api(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """调用大模型API（增强模拟实现）"""
        
        # 模拟大模型分析逻辑
        symbol = analysis_data['symbol']
        timeframe = analysis_data['timeframe']
        price_stats = analysis_data['price_stats']
        technical_indicators = analysis_data['technical_indicators']
        
        # 基于技术指标生成分析
        rsi = technical_indicators['rsi']
        macd = technical_indicators['macd']
        price_change_1d = price_stats['price_change_1d']
        price_change_5d = price_stats['price_change_5d']
        volatility = price_stats['volatility']
        volume_trend = price_stats['volume_trend']
        
        # 增强分析逻辑
        signal_score = 0
        reasoning_parts = []
        
        # RSI分析
        if rsi < 30:
            signal_score += 2
            reasoning_parts.append("RSI显示超卖区域，存在反弹机会")
        elif rsi > 70:
            signal_score -= 2
            reasoning_parts.append("RSI显示超买区域，存在回调风险")
        
        # MACD分析
        if macd > 0:
            signal_score += 1
            reasoning_parts.append("MACD处于看涨趋势")
        else:
            signal_score -= 1
            reasoning_parts.append("MACD处于看跌趋势")
        
        # 价格动量分析
        if price_change_1d > 0.5:
            signal_score += 1
            reasoning_parts.append("短期价格呈现上涨动能")
        elif price_change_1d < -0.5:
            signal_score -= 1
            reasoning_parts.append("短期价格呈现下跌动能")
        
        # 中长期趋势分析
        if price_change_5d > 2:
            signal_score += 0.5
            reasoning_parts.append("中期趋势向上")
        elif price_change_5d < -2:
            signal_score -= 0.5
            reasoning_parts.append("中期趋势向下")
        
        # 波动率分析
        if volatility > 1.5:
            reasoning_parts.append("市场波动率较高，需谨慎操作")
        
        # 成交量分析
        if volume_trend > 0:
            reasoning_parts.append("成交量呈现上升趋势")
        
        # 生成最终信号
        if signal_score >= 2:
            signal = 'buy'
            confidence = min(0.9, 0.6 + signal_score * 0.1)
        elif signal_score <= -2:
            signal = 'sell'
            confidence = min(0.9, 0.6 + abs(signal_score) * 0.1)
        else:
            signal = 'hold'
            confidence = 0.6
            reasoning_parts.append("市场处于震荡状态，建议观望")
        
        reasoning = "。".join(reasoning_parts) if reasoning_parts else "市场分析无明显趋势"
        
        return {
            'signal': signal,
            'confidence': confidence,
            'reasoning': reasoning,
            'analysis_type': 'silicon_flow_llm',
            'model_used': self.model_name,
            'key_factors': {
                'rsi_analysis': f"RSI: {rsi:.1f} ({'超卖' if rsi < 30 else '超买' if rsi > 70 else '正常'})",
                'macd_trend': f"MACD: {macd:.4f} ({'看涨' if macd > 0 else '看跌'})",
                'price_momentum_1d': f"1日价格动量: {price_change_1d:+.2f}%",
                'price_momentum_5d': f"5日价格动量: {price_change_5d:+.2f}%",
                'volatility': f"波动率: {volatility:.2f}%",
                'volume_trend': f"成交量趋势: {volume_trend:+.2f}%"
            },
            'signal_score': signal_score
        }
    
    def _generate_simulated_analysis(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Dict[str, Any]:
        """生成模拟分析结果"""
        
        return {
            'signal': 'hold',
            'confidence': 0.5,
            'reasoning': '硅基流动大模型暂时不可用，使用模拟分析',
            'analysis_type': 'simulated_llm',
            'model_used': 'simulated_model',
            'key_factors': {
                'status': '模型服务维护中',
                'recommendation': '建议使用技术分析作为主要参考'
            },
            'timestamp': time.time()
        }
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """计算RSI指标"""
        if len(prices) < period:
            return pd.Series([50] * len(prices), index=prices.index)
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)
    
    def _calculate_macd(self, prices: pd.Series) -> pd.Series:
        """计算MACD指标"""
        if len(prices) < 26:
            return pd.Series([0] * len(prices), index=prices.index)
        
        ema_12 = prices.ewm(span=12).mean()
        ema_26 = prices.ewm(span=26).mean()
        macd = ema_12 - ema_26
        return macd
    
    def _clean_expired_cache(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = [
            key for key, value in self.analysis_cache.items()
            if current_time - value['timestamp'] > self.cache_expiry
        ]
        for key in expired_keys:
            del self.analysis_cache[key]

# 导入自定义模块
from python.advanced_analysis import AdvancedMarketAnalysis
from python.data_processor import MT5DataProcessor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
            df['close'].pct_change().iloc[-1],
            df['close'].pct_change().rolling(5).mean().iloc[-1],
            df['close'].pct_change().rolling(10).mean().iloc[-1],
            df['close'].pct_change().rolling(20).mean().iloc[-1],
        ])
        
        # 波动率特征
        returns = df['close'].pct_change()
        features.extend([
            returns.rolling(5).std().iloc[-1],
            returns.rolling(10).std().iloc[-1],
            returns.rolling(20).std().iloc[-1],
        ])
        
        # 技术指标特征
        features.extend([
            (df['close'] - df['close'].rolling(5).mean()).iloc[-1] / df['close'].rolling(5).std().iloc[-1],
            (df['close'] - df['close'].rolling(10).mean()).iloc[-1] / df['close'].rolling(10).std().iloc[-1],
            (df['close'] - df['close'].rolling(20).mean()).iloc[-1] / df['close'].rolling(20).std().iloc[-1],
        ])
        
        # 成交量特征
        features.extend([
            df['volume'].pct_change().iloc[-1],
            df['volume'].rolling(5).mean().iloc[-1],
        ])
        
        return np.array(features).reshape(1, -1)
    
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
            
            confidence = max(probabilities)
            
            if prediction == 1:
                signal = 'buy'
            elif prediction == -1:
                signal = 'sell'
            else:
                signal = 'hold'
            
            return {
                'signal': signal,
                'confidence': float(confidence),
                'method': 'ml',
                'reason': f'机器学习预测 (置信度: {confidence:.2f})'
            }
            
        except Exception as e:
            logger.error(f"机器学习预测失败: {e}")
            return {
                'signal': 'hold',
                'confidence': 0.0,
                'method': 'ml',
                'reason': f'预测错误: {str(e)}'
            }
    
    def train_model(self):
        """训练机器学习模型"""
        if len(self.training_data) < 100:
            logger.warning("训练数据不足，需要至少100个样本")
            return
        
        try:
            X = np.array([sample['features'] for sample in self.training_data])
            y = np.array([sample['label'] for sample in self.training_data])
            
            # 标准化特征
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
            logger.info("机器学习模型训练完成")
            
        except Exception as e:
            logger.error(f"模型训练失败: {e}")

class EnhancedSignalGenerator:
    """增强版信号生成器，集成多种分析方法"""
    
    def __init__(self):
        self.analysis_tool = AdvancedMarketAnalysis()
        self.data_processor = MT5DataProcessor()
        self.ml_generator = MLSignalGenerator()
        self.silicon_flow_model = SiliconFlowModel()  # 硅基流动大模型
        
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
            regime = regime_info.get('regime', 'unknown')
            confidence = regime_info.get('confidence', 0.5)
            
            return {
                'regime': regime,
                'confidence': confidence,
                'description': regime_info.get('description', '未知状态'),
                'weight': 0.8 if confidence > 0.7 else 0.5,
                'method': 'regime'
            }
            
        except Exception as e:
            logger.error(f"市场状态分析失败: {e}")
            return {
                'regime': 'unknown',
                'confidence': 0.0,
                'description': '分析失败',
                'weight': 0.5,
                'method': 'regime',
                'error': str(e)
            }
    
    def _perform_silicon_flow_analysis(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Dict[str, Any]:
        """执行硅基流动大模型分析"""
        try:
            llm_analysis = self.silicon_flow_model.analyze_market_context(df, symbol, timeframe)
            
            # 转换信号格式
            signal_map = {'buy': 'buy', 'sell': 'sell', 'hold': 'hold'}
            signal = signal_map.get(llm_analysis.get('signal', 'hold'), 'hold')
            
            return {
                'signal': signal,
                'confidence': llm_analysis.get('confidence', 0.5),
                'reasoning': llm_analysis.get('reasoning', '大模型分析'),
                'analysis_type': llm_analysis.get('analysis_type', 'silicon_flow'),
                'model_used': llm_analysis.get('model_used', 'unknown'),
                'key_factors': llm_analysis.get('key_factors', {}),
                'weight': 0.9 if llm_analysis.get('confidence', 0) > 0.7 else 0.6,  # 大模型权重较高
                'method': 'silicon_flow'
            }
            
        except Exception as e:
            logger.error(f"硅基流动大模型分析失败: {e}")
            return {
                'signal': 'hold',
                'confidence': 0.0,
                'reasoning': f'大模型分析失败: {str(e)}',
                'analysis_type': 'error',
                'model_used': 'error',
                'key_factors': {'error': str(e)},
                'weight': 0.3,  # 错误时权重较低
                'method': 'silicon_flow',
                'error': str(e)
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
                    'reason': '数据不足',
                    'timestamp': time.time()
                }
            
            # 执行多种分析
            technical_signal = self._perform_technical_analysis(df)
            ml_signal = self._perform_ml_analysis(df)
            regime_signal = self._perform_market_regime_analysis(df)
            silicon_flow_signal = self._perform_silicon_flow_analysis(df, symbol, timeframe)
            
            # 综合信号生成逻辑
            signals = []
            strengths = []
            reasons = []
            weights = []
            
            # 技术分析信号
            if technical_signal.get('signal') != 'hold':
                signals.append(technical_signal['signal'])
                strengths.append(technical_signal.get('strength', 50))
                reasons.append('技术分析')
                weights.append(0.7)  # 技术分析权重
            
            # 机器学习信号
            if ml_signal.get('signal') != 'hold' and ml_signal.get('confidence', 0) > 0.6:
                signals.append(ml_signal['signal'])
                strengths.append(int(ml_signal.get('confidence', 0) * 100))
                reasons.append('机器学习')
                weights.append(0.8)  # 机器学习权重
            
            # 硅基流动大模型信号
            if silicon_flow_signal.get('signal') != 'hold' and silicon_flow_signal.get('confidence', 0) > 0.5:
                signals.append(silicon_flow_signal['signal'])
                strengths.append(int(silicon_flow_signal.get('confidence', 0) * 100))
                reasons.append('大模型分析')
                weights.append(silicon_flow_signal.get('weight', 0.9))  # 大模型权重最高
            
            # 市场状态权重
            regime_weight = regime_signal.get('weight', 0.5)
            
            # 生成最终信号
            if not signals:
                final_signal = 'hold'
                final_strength = 0
                final_reason = '所有分析方法均建议持有'
            else:
                # 加权投票机制
                buy_weighted = 0
                sell_weighted = 0
                
                for signal, strength, weight in zip(signals, strengths, weights):
                    if signal == 'buy':
                        buy_weighted += strength * weight
                    elif signal == 'sell':
                        sell_weighted += strength * weight
                
                # 考虑市场状态权重
                buy_weighted *= regime_weight
                sell_weighted *= regime_weight
                
                if buy_weighted > sell_weighted and buy_weighted > 30:  # 阈值30
                    final_signal = 'buy'
                    final_strength = min(int(buy_weighted), 100)
                    final_reason = f"综合信号 ({', '.join(reasons)})"
                elif sell_weighted > buy_weighted and sell_weighted > 30:
                    final_signal = 'sell'
                    final_strength = min(int(sell_weighted), 100)
                    final_reason = f"综合信号 ({', '.join(reasons)})"
                else:
                    final_signal = 'hold'
                    final_strength = 0
                    final_reason = f"信号强度不足 ({', '.join(reasons)})"
            
            # 构建响应
            result = {
                'symbol': symbol,
                'timeframe': timeframe,
                'signal': final_signal,
                'strength': final_strength,
                'confidence': final_strength / 100.0,
                'reason': final_reason,
                'timestamp': time.time(),
                'cached': False,
                'components': {
                    'technical': technical_signal,
                    'ml': ml_signal,
                    'regime': regime_signal,
                    'silicon_flow': silicon_flow_signal
                },
                'analysis_weights': {
                    'technical': 0.7,
                    'ml': 0.8,
                    'silicon_flow': silicon_flow_signal.get('weight', 0.9),
                    'regime': regime_weight
                }
            }
            
            # 缓存结果
            self.signal_cache[cache_key] = result
            
            # 记录历史
            self.signal_history.append(result)
            if len(self.signal_history) > self.max_history_size:
                self.signal_history = self.signal_history[-self.max_history_size:]
            
            logger.info(f"生成信号: {final_signal} (强度: {final_strength})")
            return result
            
        except Exception as e:
            logger.error(f"信号生成失败: {e}")
            return {
                'signal': 'hold',
                'strength': 0,
                'reason': f'信号生成错误: {str(e)}',
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
            
            # 执行完整分析
            technical_indicators = self.analysis_tool.calculate_technical_indicators(df)
            market_regime = self.analysis_tool.detect_market_regime(df)
            risk_metrics = self.analysis_tool.calculate_risk_metrics(df)
            
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': time.time(),
                'technical_indicators': technical_indicators,
                'market_regime': market_regime,
                'risk_metrics': risk_metrics,
                'summary': self.analysis_tool.generate_analysis_summary(df)
            }
            
        except Exception as e:
            logger.error(f"详细分析失败: {e}")
            return {
                'error': f'详细分析失败: {str(e)}',
                'timestamp': time.time()
            }

class SocketServer:
    """Socket服务器类"""
    
    def __init__(self, host='localhost', port=9090):
        self.host = host
        self.port = port
        self.signal_generator = EnhancedSignalGenerator()
        self.running = False
        
    def _process_request(self, request_data: str) -> str:
        """处理客户端请求"""
        try:
            # 解析JSON请求
            request = json.loads(request_data)
            action = request.get('action', '')
            
            if action == 'get_signal':
                symbol = request.get('symbol', 'EURUSD')
                timeframe = request.get('timeframe', 'H1')
                rates = request.get('rates', [])
                
                # 如果没有提供rates数据，则自动生成
                if not rates:
                    from datetime import datetime, timedelta
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=30)
                    
                    df = self.signal_generator.data_processor.get_historical_data(
                        symbol, 
                        self.signal_generator._timeframe_to_int(timeframe), 
                        start_date, 
                        end_date
                    )
                    rates = df.reset_index().to_dict('records')
                
                signal = self.signal_generator.generate_comprehensive_signal(symbol, timeframe, rates)
                return json.dumps(signal, cls=NumpyEncoder)
                
            elif action == 'get_analysis':
                symbol = request.get('symbol', 'EURUSD')
                timeframe = request.get('timeframe', 'H1')
                rates = request.get('rates', [])
                
                if not rates:
                    from datetime import datetime, timedelta
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=30)
                    
                    df = self.signal_generator.data_processor.get_historical_data(
                        symbol, 
                        self.signal_generator._timeframe_to_int(timeframe), 
                        start_date, 
                        end_date
                    )
                    rates = df.reset_index().to_dict('records')
                
                analysis = self.signal_generator.get_detailed_analysis(symbol, timeframe, rates)
                return json.dumps(analysis, cls=NumpyEncoder)
                
            elif action == 'train_model':
                self.signal_generator.ml_generator.train_model()
                return json.dumps({'status': 'training_started', 'timestamp': time.time()})
                
            elif action == 'get_stats':
                stats = {
                    'cache_size': len(self.signal_generator.signal_cache),
                    'signal_history_count': len(self.signal_generator.signal_history),
                    'training_data_size': len(self.signal_generator.ml_generator.training_data),
                    'ml_model_trained': self.signal_generator.ml_generator.is_trained,
                    'last_training_time': self.signal_generator.ml_generator.last_training_time,
                    'silicon_flow_available': self.signal_generator.silicon_flow_model.is_available,
                    'silicon_flow_cache_size': len(self.signal_generator.silicon_flow_model.analysis_cache),
                    'timestamp': time.time()
                }
                return json.dumps(stats)
            
            elif action == 'silicon_flow_analysis':
                symbol = request.get('symbol', 'EURUSD')
                timeframe = request.get('timeframe', 'H1')
                rates = request.get('rates', [])
                
                if not rates:
                    from datetime import datetime, timedelta
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=30)
                    
                    df = self.signal_generator.data_processor.get_historical_data(
                        symbol, 
                        self.signal_generator._timeframe_to_int(timeframe), 
                        start_date, 
                        end_date
                    )
                    rates = df.reset_index().to_dict('records')
                
                df = self.signal_generator.data_processor.convert_to_dataframe(rates)
                
                if df.empty or len(df) < 20:
                    return json.dumps({'error': '数据不足', 'timestamp': time.time()})
                
                analysis = self.signal_generator.silicon_flow_model.analyze_market_context(df, symbol, timeframe)
                return json.dumps(analysis, cls=NumpyEncoder)
                
            else:
                return json.dumps({'error': '未知操作', 'action': action})
                
        except Exception as e:
            logger.error(f"请求处理失败: {e}")
            return json.dumps({'error': f'处理失败: {str(e)}'})
    
    def _handle_client(self, conn, addr):
        """处理单个客户端连接"""
        logger.info(f"客户端连接: {addr}")
        
        try:
            buffer = b''
            
            while True:
                # 接收数据
                data = conn.recv(4096)
                if not data:
                    break
                
                buffer += data
                
                # 处理所有完整消息
                while True:
                    # 查找消息长度分隔符
                    colon_pos = buffer.find(b':')
                    if colon_pos == -1:
                        break  # 没有找到完整消息头
                    
                    # 解析消息长度
                    try:
                        length_str = buffer[:colon_pos].decode('utf-8')
                        message_length = int(length_str)
                    except (ValueError, UnicodeDecodeError):
                        logger.error(f"无效的消息长度格式: {buffer[:colon_pos]}")
                        break
                    
                    # 检查是否收到完整消息
                    total_length_needed = colon_pos + 1 + message_length
                    if len(buffer) < total_length_needed:
                        break  # 消息不完整，等待更多数据
                    
                    # 提取消息内容
                    message_data = buffer[colon_pos + 1:total_length_needed].decode('utf-8')
                    
                    # 处理消息
                    response = self._process_request(message_data)
                    conn.send((str(len(response)) + ':' + response).encode('utf-8'))
                    
                    # 移除已处理的消息
                    buffer = buffer[total_length_needed:]
        
        except Exception as e:
            logger.error(f"客户端处理错误: {e}")
        
        finally:
            conn.close()
            logger.info(f"客户端断开: {addr}")
    
    def start(self):
        """启动服务器"""
        self.running = True
        
        # 创建Socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            sock.bind((self.host, self.port))
            sock.listen(5)
            
            logger.info(f"Socket服务器启动在 {self.host}:{self.port}")
            logger.info("可用操作:")
            logger.info("  get_signal - 获取交易信号（集成硅基流动大模型）")
            logger.info("  get_analysis - 获取详细分析")
            logger.info("  silicon_flow_analysis - 获取硅基流动大模型独立分析")
            logger.info("  train_model - 手动训练模型")
            logger.info("  get_stats - 获取统计信息")
            
            while self.running:
                try:
                    conn, addr = sock.accept()
                    
                    # 为每个客户端创建新线程
                    client_thread = threading.Thread(
                        target=self._handle_client, 
                        args=(conn, addr)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except Exception as e:
                    if self.running:
                        logger.error(f"接受连接错误: {e}")
        
        except Exception as e:
            logger.error(f"服务器启动失败: {e}")
        
        finally:
            sock.close()
            self.running = False
    
    def stop(self):
        """停止服务器"""
        self.running = False

if __name__ == "__main__":
    # 创建并启动服务器（绑定到所有网络接口，允许外部连接）
    server = SocketServer(host='0.0.0.0', port=9090)
    
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("收到中断信号，停止服务器")
        server.stop()