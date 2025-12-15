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
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

# 导入自定义模块
from python.advanced_analysis import AdvancedMarketAnalysis
from python.data_processor import MT5DataProcessor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

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
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })

@app.route('/get_signal', methods=['POST'])
def get_signal():
    """获取交易信号端点"""
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
        
        if not rates:
            return jsonify({
                'error': '缺少K线数据',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # 生成交易信号
        signal = signal_generator.generate_comprehensive_signal(symbol, timeframe, rates)
        
        return jsonify(signal)
        
    except Exception as e:
        logger.error(f"获取信号失败: {e}")
        return jsonify({
            'error': f'服务器内部错误: {e}',
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
        
        if not rates:
            return jsonify({
                'error': '缺少K线数据',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # 生成详细分析报告
        analysis = signal_generator.get_detailed_analysis(symbol, timeframe, rates)
        
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

@app.route('/stats', methods=['GET'])
def get_stats():
    """获取服务器统计信息"""
    return jsonify({
        'signal_history_count': len(signal_generator.signal_history),
        'cache_size': len(signal_generator.signal_cache),
        'ml_model_trained': signal_generator.ml_generator.is_trained,
        'last_training_time': signal_generator.ml_generator.last_training_time,
        'training_data_size': len(signal_generator.ml_generator.training_data),
        'timestamp': datetime.now().isoformat()
    })

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