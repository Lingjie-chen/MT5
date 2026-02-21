import numpy as np
import pandas as pd
from collections import deque
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MicrostructureAnalyzer:
    """
    市场微观结构分析器
    实现Tick级数据分析，识别订单流、买卖压力、流动性空洞及机构行为。
    """
    
    def __init__(self, tick_history_size: int = 1000, large_order_threshold_std: float = 3.0):
        self.tick_history = deque(maxlen=tick_history_size)
        self.large_order_threshold_std = large_order_threshold_std
        
        # 缓存指标
        self.current_metrics = {
            'buy_pressure': 0.0,
            'sell_pressure': 0.0,
            'liquidity': 0.0,
            'institutional_activity': 'neutral'
        }
        
    def analyze_tick(self, tick: Dict) -> Dict:
        """
        分析单个Tick数据
        tick格式: {'price': float, 'volume': float, 'time': timestamp, 'bid': float, 'ask': float}
        """
        # 1. 更新历史
        self._update_tick_history(tick)
        
        if len(self.tick_history) < 10:
            return self.current_metrics
            
        # 2. 计算基本指标
        basic_metrics = self._calculate_basic_metrics()
        
        # 3. 订单流分析
        order_flow = self._analyze_order_flow()
        
        # 4. 买卖压力
        pressure = self._analyze_buy_sell_pressure()
        
        # 5. 价格冲击分析
        impact = self._analyze_price_impact()
        
        # 6. 大单检测
        large_orders = self._detect_large_order(tick)
        
        # 7. 流动性分析
        liquidity = self._analyze_liquidity(tick)
        
        # 8. 机构行为识别
        inst_activity = self._detect_institutional_activity()
        
        # 9. 微观结构模式识别
        patterns = self._identify_microstructure_patterns()
        
        self.current_metrics.update({
            'order_flow': order_flow,
            'pressure': pressure,
            'impact': impact,
            'large_orders': large_orders,
            'liquidity': liquidity,
            'institutional_activity': inst_activity,
            'patterns': patterns
        })
        
        return self.current_metrics

    def _update_tick_history(self, tick: Dict):
        self.tick_history.append(tick)

    def _calculate_basic_metrics(self) -> Dict:
        """计算基本统计指标"""
        df = pd.DataFrame(list(self.tick_history))
        df['return'] = df['price'].pct_change()
        
        return {
            'volatility': df['return'].std(),
            'avg_volume': df['volume'].mean(),
            'tick_speed': len(df) / 60  # 假设每分钟频率
        }

    def _analyze_order_flow(self) -> Dict:
        """分析订单流 (基于涨跌判断主动买卖方向)"""
        df = pd.DataFrame(list(self.tick_history))
        
        # 简化：价格上涨归为买入流，下跌归为卖出流
        buy_volume = df[df['price'] > df['price'].shift(1)]['volume'].sum()
        sell_volume = df[df['price'] < df['price'].shift(1)]['volume'].sum()
        total_volume = buy_volume + sell_volume + 1e-6
        
        imbalance = (buy_volume - sell_volume) / total_volume
        
        return {
            'buy_volume': buy_volume,
            'sell_volume': sell_volume,
            'imbalance': imbalance
        }

    def _analyze_buy_sell_pressure(self) -> Dict:
        """计算买卖压力指数"""
        recent_ticks = list(self.tick_history)[-20:] # 最近20笔
        prices = [t['price'] for t in recent_ticks]
        volumes = [t['volume'] for t in recent_ticks]
        
        # 加权价格变化
        price_changes = np.diff(prices)
        weighted_pressure = np.sum(price_changes * volumes[1:]) # 简化模型
        
        # 归一化
        norm_pressure = weighted_pressure / (np.mean(volumes) * np.mean(np.abs(price_changes)) + 1e-6)
        
        return {
            'pressure_index': norm_pressure,
            'trend': 'bullish' if norm_pressure > 0.5 else ('bearish' if norm_pressure < -0.5 else 'neutral')
        }

    def _analyze_price_impact(self) -> Dict:
        """分析价格冲击"""
        df = pd.DataFrame(list(self.tick_history))
        if len(df) < 2: return {'impact_coefficient': 0}
        
        # Amihud非流动性指标简化
        ret = np.abs(df['price'].pct_change())
        vol = df['volume']
        
        # 价格冲击 = 收益率 / 成交量
        impact_series = ret / (vol + 1e-6)
        avg_impact = impact_series.mean()
        
        return {
            'impact_coefficient': avg_impact,
            'elasticity': 1 / (avg_impact + 1e-6) # 价格弹性
        }

    def _detect_large_order(self, tick: Dict) -> Dict:
        """Z-score大单检测"""
        volumes = [t['volume'] for t in self.tick_history]
        mean_vol = np.mean(volumes)
        std_vol = np.std(volumes)
        
        if std_vol == 0: return {'is_large': False}
        
        z_score = (tick['volume'] - mean_vol) / std_vol
        
        return {
            'is_large': z_score > self.large_order_threshold_std,
            'z_score': z_score,
            'volume_ratio': tick['volume'] / (mean_vol + 1e-6)
        }

    def _analyze_liquidity(self, tick: Dict) -> Dict:
        """流动性分析，检测流动性空洞"""
        # 基于买卖价差
        spread = tick.get('ask', tick['price']) - tick.get('bid', tick['price'])
        spread_pct = spread / tick['price']
        
        # 检测Tick频率突降 (流动性空洞特征)
        timestamps = [t['time'] for t in list(self.tick_history)[-10:]]
        time_diffs = np.diff(timestamps).astype(float) / 1e9 # 转秒
        is_hole = np.mean(time_diffs) > (2 * np.mean(list(self.tick_history)[-100:])) # 简化逻辑
        
        return {
            'spread': spread,
            'spread_pct': spread_pct,
            'liquidity_hole': bool(is_hole),
            'depth_imbalance': 0.5 # 模拟深度失衡
        }

    def _detect_institutional_activity(self) -> str:
        """检测机构行为"""
        metrics = self.current_metrics
        flow = metrics.get('order_flow', {})
        imb = flow.get('imbalance', 0)
        liq = metrics.get('liquidity', {})
        hole = liq.get('liquidity_hole', False)
        
        # 逻辑规则
        if imb > 0.6 and not hole:
            return 'accumulation' # 持续买入，流动性正常
        elif imb < -0.6 and not hole:
            return 'distribution' # 持续卖出
        elif hole and abs(imb) > 0.4:
            return 'aggressive_move' # 流动性缺失伴随大单方向
        else:
            return 'mixed'

    def _identify_microstructure_patterns(self) -> List[str]:
        """识别微观结构模式"""
        patterns = []
        
        if self.current_metrics['liquidity'].get('liquidity_hole'):
            patterns.append('liquidity_void')
            
        if self.current_metrics['large_orders'].get('is_large'):
            patterns.append('large_order_impact')
            
        pressure = self.current_metrics.get('pressure', {}).get('pressure_index', 0)
        if abs(pressure) > 2.0:
            patterns.append('extreme_pressure')
            
        # 订单块堆积检测 (简化：连续同向大单)
        # ... 实现细节省略
        
        return patterns

    def get_microstructure_summary(self) -> Dict:
        return self.current_metrics

    def export_microstructure_data(self) -> pd.DataFrame:
        return pd.DataFrame(list(self.tick_history))
