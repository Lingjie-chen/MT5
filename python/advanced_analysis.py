import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

class AdvancedMarketAnalysis:
    """
    高级市场分析工具类
    基于MQL5文章中的最佳实践，利用Python的Pandas和NumPy库
    提供更强大的技术分析和机器学习功能
    """
    
    def __init__(self):
        self.indicators_cache = {}
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        计算综合技术指标
        
        Args:
            df: 包含OHLCV数据的DataFrame
            
        Returns:
            技术指标字典
        """
        if len(df) < 20:
            return self._get_default_indicators()
        
        indicators = {}
        
        # 移动平均线
        indicators['sma_20'] = df['close'].tail(20).mean()
        indicators['sma_50'] = df['close'].tail(50).mean() if len(df) >= 50 else indicators['sma_20']
        
        # 指数移动平均线
        indicators['ema_12'] = df['close'].ewm(span=12).mean().iloc[-1]
        indicators['ema_26'] = df['close'].ewm(span=26).mean().iloc[-1]
        
        # MACD
        ema_12 = df['close'].ewm(span=12).mean()
        ema_26 = df['close'].ewm(span=26).mean()
        macd_line = ema_12 - ema_26
        macd_signal = macd_line.ewm(span=9).mean()
        indicators['macd'] = macd_line.iloc[-1]
        indicators['macd_signal'] = macd_signal.iloc[-1]
        indicators['macd_histogram'] = indicators['macd'] - indicators['macd_signal']
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        indicators['rsi'] = 100 - (100 / (1 + rs.iloc[-1])) if not pd.isna(loss.iloc[-1]) and loss.iloc[-1] != 0 else 50
        
        # Bollinger Bands
        bb_period = 20
        bb_std = 2
        sma = df['close'].rolling(window=bb_period).mean()
        std = df['close'].rolling(window=bb_period).std()
        indicators['bb_upper'] = sma.iloc[-1] + (std.iloc[-1] * bb_std)
        indicators['bb_lower'] = sma.iloc[-1] - (std.iloc[-1] * bb_std)
        indicators['bb_middle'] = sma.iloc[-1]
        
        # ATR (平均真实波幅)
        high_low = df['high'] - df['low']
        high_close_prev = abs(df['high'] - df['close'].shift())
        low_close_prev = abs(df['low'] - df['close'].shift())
        true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
        indicators['atr'] = true_range.rolling(window=14).mean().iloc[-1]
        
        # 成交量分析
        indicators['volume_sma'] = df['volume'].tail(20).mean()
        indicators['current_volume'] = df['volume'].iloc[-1]
        indicators['volume_ratio'] = indicators['current_volume'] / indicators['volume_sma'] if indicators['volume_sma'] > 0 else 1
        
        # 价格动量
        indicators['momentum_5'] = (df['close'].iloc[-1] / df['close'].iloc[-6] - 1) * 100
        indicators['momentum_10'] = (df['close'].iloc[-1] / df['close'].iloc[-11] - 1) * 100
        
        return indicators
    
    def detect_market_regime(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        检测市场状态（趋势/震荡/高波动）
        
        Args:
            df: 价格数据DataFrame
            
        Returns:
            市场状态分析结果
        """
        if len(df) < 50:
            return {"regime": "unknown", "confidence": 0.5, "description": "数据不足"}
        
        # 计算波动率
        returns = df['close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)  # 年化波动率
        
        # 计算趋势强度
        price_change = (df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100
        
        # 使用ADX判断趋势强度
        highs = df['high']
        lows = df['low']
        
        # 计算+DI和-DI
        plus_dm = highs.diff()
        minus_dm = -lows.diff()
        
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        tr = pd.concat([
            highs - lows,
            abs(highs - df['close'].shift()),
            abs(lows - df['close'].shift())
        ], axis=1).max(axis=1)
        
        atr = tr.rolling(window=14).mean()
        plus_di = 100 * (plus_dm.rolling(window=14).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=14).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=14).mean()
        
        current_adx = adx.iloc[-1] if not pd.isna(adx.iloc[-1]) else 0
        
        # 判断市场状态
        if volatility > 0.3:  # 高波动
            regime = "high_volatility"
            confidence = min(volatility / 0.5, 0.9)
            description = "高波动市场"
        elif current_adx > 25:  # 强趋势
            regime = "trending"
            confidence = min(current_adx / 50, 0.9)
            description = "趋势市场"
        else:  # 震荡
            regime = "ranging"
            confidence = 0.7
            description = "震荡市场"
        
        return {
            "regime": regime,
            "confidence": confidence,
            "description": description,
            "volatility": volatility,
            "adx": current_adx,
            "price_change": price_change
        }
    
    def generate_support_resistance(self, df: pd.DataFrame, lookback_period: int = 100) -> Dict[str, List[float]]:
        """
        生成支撑阻力位
        
        Args:
            df: 价格数据DataFrame
            lookback_period: 回溯周期
            
        Returns:
            支撑阻力位字典
        """
        if len(df) < lookback_period:
            lookback_period = len(df)
        
        recent_data = df.tail(lookback_period)
        
        # 使用局部极值点识别支撑阻力
        highs = recent_data['high']
        lows = recent_data['low']
        
        # 寻找局部高点和低点
        support_levels = []
        resistance_levels = []
        
        # 简单方法：使用近期高点和低点
        recent_high = highs.max()
        recent_low = lows.min()
        
        # 生成多个支撑阻力位
        price_range = recent_high - recent_low
        
        # 支撑位（低于当前价格）
        current_price = df['close'].iloc[-1]
        for i in range(1, 4):
            level = current_price - (price_range * 0.1 * i)
            if level > recent_low:
                support_levels.append(round(level, 4))
        
        # 阻力位（高于当前价格）
        for i in range(1, 4):
            level = current_price + (price_range * 0.1 * i)
            if level < recent_high:
                resistance_levels.append(round(level, 4))
        
        # 确保至少有一个支撑阻力位
        if not support_levels:
            support_levels = [round(recent_low, 4)]
        if not resistance_levels:
            resistance_levels = [round(recent_high, 4)]
        
        return {
            "support_levels": sorted(support_levels),
            "resistance_levels": sorted(resistance_levels),
            "current_price": current_price
        }
    
    def calculate_risk_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        计算风险指标
        
        Args:
            df: 价格数据DataFrame
            
        Returns:
            风险指标字典
        """
        if len(df) < 30:
            return self._get_default_risk_metrics()
        
        returns = df['close'].pct_change().dropna()
        
        metrics = {
            "volatility": returns.std() * np.sqrt(252),  # 年化波动率
            "sharpe_ratio": returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0,
            "max_drawdown": self._calculate_max_drawdown(df['close']),
            "var_95": np.percentile(returns, 5) * 100,  # 95% VaR
            "expected_shortfall": returns[returns <= np.percentile(returns, 5)].mean() * 100,
            "skewness": returns.skew(),
            "kurtosis": returns.kurtosis()
        }
        
        return metrics
    
    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        """计算最大回撤"""
        cumulative_returns = (1 + prices.pct_change()).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        return drawdown.min() * 100
    
    def _get_default_indicators(self) -> Dict[str, float]:
        """获取默认技术指标"""
        return {
            "sma_20": 0, "sma_50": 0, "ema_12": 0, "ema_26": 0,
            "macd": 0, "macd_signal": 0, "macd_histogram": 0,
            "rsi": 50, "bb_upper": 0, "bb_lower": 0, "bb_middle": 0,
            "atr": 0, "volume_sma": 0, "current_volume": 0, "volume_ratio": 1,
            "momentum_5": 0, "momentum_10": 0
        }
    
    def generate_signal_from_indicators(self, indicators: Dict[str, float]) -> Dict[str, any]:
        """根据技术指标生成交易信号
        
        Args:
            indicators: 技术指标字典
            
        Returns:
            交易信号信息
        """
        signal = "hold"
        strength = 0
        reasons = []
        
        # MACD信号
        if indicators['macd'] > indicators['macd_signal'] and indicators['macd_histogram'] > 0:
            strength += 25
            reasons.append("MACD金叉")
        elif indicators['macd'] < indicators['macd_signal'] and indicators['macd_histogram'] < 0:
            strength -= 25
            reasons.append("MACD死叉")
        
        # RSI信号
        if indicators['rsi'] < 30:
            strength += 20
            reasons.append("RSI超卖")
        elif indicators['rsi'] > 70:
            strength -= 20
            reasons.append("RSI超买")
        
        # 移动平均线信号
        if indicators['ema_12'] > indicators['ema_26']:
            strength += 15
            reasons.append("EMA金叉")
        elif indicators['ema_12'] < indicators['ema_26']:
            strength -= 15
            reasons.append("EMA死叉")
        
        # 布林带信号
        current_price = indicators.get('current_price', indicators['sma_20'])
        if current_price < indicators['bb_lower']:
            strength += 15
            reasons.append("价格触及布林带下轨")
        elif current_price > indicators['bb_upper']:
            strength -= 15
            reasons.append("价格触及布林带上轨")
        
        # 成交量确认
        if indicators['volume_ratio'] > 1.5:
            strength += 10
            reasons.append("成交量放大")
        
        # 确定最终信号
        if strength >= 40:
            signal = "buy"
        elif strength <= -40:
            signal = "sell"
        else:
            signal = "hold"
            strength = 0
        
        return {
            "signal": signal,
            "strength": abs(strength),
            "reasons": reasons,
            "confidence": min(abs(strength) / 100, 1.0)
        }

    def _get_default_risk_metrics(self) -> Dict[str, float]:
        """获取默认风险指标"""
        return {
            "volatility": 0.2, "sharpe_ratio": 0, "max_drawdown": 0,
            "var_95": -2, "expected_shortfall": -3, "skewness": 0, "kurtosis": 0
        }

# 使用示例
def create_sample_data():
    """创建示例数据用于测试"""
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    # 生成随机价格数据
    returns = np.random.normal(0.001, 0.02, 100)
    prices = 100 * (1 + returns).cumprod()
    
    df = pd.DataFrame({
        'open': prices * 0.999,
        'high': prices * 1.005,
        'low': prices * 0.995,
        'close': prices,
        'volume': np.random.randint(100000, 1000000, 100)
    }, index=dates)
    
    return df

if __name__ == "__main__":
    # 测试功能
    analyzer = AdvancedMarketAnalysis()
    sample_data = create_sample_data()
    
    print("技术指标:")
    indicators = analyzer.calculate_technical_indicators(sample_data)
    for key, value in indicators.items():
        print(f"{key}: {value:.4f}")
    
    print("\n市场状态:")
    regime = analyzer.detect_market_regime(sample_data)
    for key, value in regime.items():
        print(f"{key}: {value}")
    
    print("\n支撑阻力位:")
    levels = analyzer.generate_support_resistance(sample_data)
    for key, value in levels.items():
        print(f"{key}: {value}")
    
    print("\n风险指标:")
    risk = analyzer.calculate_risk_metrics(sample_data)
    for key, value in risk.items():
        print(f"{key}: {value:.4f}")