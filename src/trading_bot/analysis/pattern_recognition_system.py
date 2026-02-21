import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import logging

# 引入各子模块
# 实际环境中需确保路径正确: from .pattern_discovery import PatternDiscovery ...
# 此处假设类已在内存中或同目录
# from pattern_discovery import PatternDiscovery
# from microstructure_analyzer import MicrostructureAnalyzer
# from multi_pattern_recognizer import MultiPatternRecognizer
# from hidden_pattern_miner import HiddenPatternMiner
# from pattern_validator import PatternValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PatternRecognitionSystem:
    """
    模式识别统一接口
    整合微观结构、统计模式、机器学习模型与关联规则挖掘。
    提供全面的市场分析能力。
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # 初始化各模块
        logger.info("Initializing Pattern Recognition System...")
        
        self.discovery = PatternDiscovery(
            n_clusters=self.config.get('n_clusters', 5)
        )
        
        self.microstructure = MicrostructureAnalyzer()
        
        self.recognizer = MultiPatternRecognizer()
        
        self.miner = HiddenPatternMiner()
        
        self.validator = PatternValidator()
        
    def analyze_market(self, ohlcv_df: pd.DataFrame, tick_data: Optional[List[Dict]] = None) -> Dict:
        """
        综合市场分析入口
        """
        results = {}
        
        # 1. 市场微观结构分析 (如果有Tick数据)
        if tick_data:
            micro_summary = []
            for tick in tick_data[-100:]: # 仅分析最近100个tick作为示例
                res = self.microstructure.analyze_tick(tick)
                micro_summary.append(res)
            
            if micro_summary:
                results['microstructure'] = self.microstructure.get_microstructure_summary()
        
        # 2. 无监督模式发现
        logger.info("Running unsupervised pattern discovery...")
        results['discovery'] = self.discovery.discover_patterns(ohlcv_df)
        
        # 3. 多模式识别 (有监督/规则)
        logger.info("Running multi-pattern recognition...")
        results['recognition'] = self.recognizer.recognize_patterns(ohlcv_df)
        
        # 4. 隐含模式挖掘
        logger.info("Mining hidden association rules...")
        transactions = self.miner.extract_events(ohlcv_df)
        results['hidden_rules'] = self.miner.mine_association_rules(transactions[:1000]) # 限制数据量
        
        # 5. 生成综合分析与交易信号
        comprehensive = self._generate_comprehensive_analysis(results)
        results['comprehensive_analysis'] = comprehensive
        
        return results

    def _generate_comprehensive_analysis(self, results: Dict) -> Dict:
        """
        融合各模块结果，生成统一观点
        """
        signal = 'neutral'
        confidence = 0.0
        reasons = []
        
        # 1. 检查微观结构
        micro = results.get('microstructure', {})
        if micro.get('institutional_activity') == 'accumulation':
            reasons.append("Microstructure: Institutional Accumulation Detected")
            signal = 'buy'
            confidence += 0.2
        
        # 2. 检查模式识别
        recog = results.get('recognition', {})
        pattern = recog.get('current_pattern')
        if pattern in ['trend_up', 'breakout_up']:
            reasons.append(f"Pattern: {pattern} detected")
            signal = 'buy'
            confidence += 0.3
        elif pattern in ['trend_down', 'breakout_down']:
            reasons.append(f"Pattern: {pattern} detected")
            signal = 'sell'
            confidence += 0.3
            
        # 3. 检查关联规则
        hidden = results.get('hidden_rules', [])
        # 检查是否有强规则支持当前方向 (简化逻辑)
        strong_rules = [r for r in hidden if r['lift'] > 1.5]
        if strong_rules:
            reasons.append(f"Hidden Rules: {len(strong_rules)} strong confirmation rules found")
            confidence += 0.2
            
        return {
            'signal': signal,
            'confidence': min(confidence, 1.0),
            'reasoning': reasons,
            'risk_warning': "High volatility" if results['discovery']['scores']['silhouette'] < 0.3 else "Normal"
        }

    def get_trading_signals(self, analysis_result: Dict) -> List[Dict]:
        """提取标准化交易信号"""
        comp = analysis_result.get('comprehensive_analysis', {})
        return [{
            'action': comp.get('signal'),
            'strength': comp.get('confidence'),
            'notes': "; ".join(comp.get('reasoning', []))
        }]

    def train_system(self, historical_data: pd.DataFrame, labels: Optional[pd.Series] = None):
        """
        训练系统中的有监督学习组件
        """
        logger.info("Training system models...")
        
        # 提取特征用于训练
        features = self.recognizer.extract_pattern_features(historical_data)
        
        # 如果有标签，训练分类器
        if labels is not None:
            # 对齐索引
            common_idx = historical_data.index.intersection(labels.index)
            X = features[-len(common_idx):] # 简化索引对齐
            y = labels.loc[common_idx].values
            
            self.recognizer.train_models(X, y)
            logger.info("Recognizer models trained.")
        else:
            logger.warning("No labels provided, skipping supervised training.")

    def export_all_data(self, filepath: str):
        """导出模型状态"""
        self.discovery.export_patterns(f"{filepath}_discovery.pkl")
        # 其他模块导出逻辑...
        logger.info(f"System state exported to {filepath}")
