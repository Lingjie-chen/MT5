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
                support_levels.append(float(round(level, 4)))
        
        # 阻力位（高于当前价格）
        for i in range(1, 4):
            level = current_price + (price_range * 0.1 * i)
            if level < recent_high:
                resistance_levels.append(float(round(level, 4)))
        
        # 确保至少有一个支撑阻力位
        if not support_levels:
            support_levels = [float(round(recent_low, 4))]
        if not resistance_levels:
            resistance_levels = [float(round(recent_high, 4))]
        
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
    
    def analyze_crt_strategy(self, df: pd.DataFrame, range_period: int = 15, confirm_period: int = 1, min_manipulation_pct: float = 5.0) -> Dict[str, any]:
        """
        基于 CRT (Candle Range Theory) 的策略分析
        逻辑来源: CRT蜡烛区间理论EA.mq5
        
        Args:
            df: OHLCV DataFrame (通常是较高时间周期的，如 M15)
            range_period: 定义区间的周期数
            confirm_period: 确认突破的周期数
            min_manipulation_pct: 最小操纵深度百分比
            
        Returns:
            策略信号和区间信息
        """
        if len(df) < range_period + confirm_period + 5:
            return {"signal": "hold", "strength": 0, "reasons": []}
            
        # 1. 识别区间 (Accumulation Phase)
        # 假设当前时间点为 t，区间定义为 t-1 的 High/Low
        # MQL5逻辑: Range High/Low based on PREVIOUS candle of Range Timeframe
        
        prev_candle = df.iloc[-2] # 前一根已完成 K 线
        range_high = prev_candle['high']
        range_low = prev_candle['low']
        range_open = prev_candle['open']
        range_close = prev_candle['close']
        
        # 判断区间方向 (Sentiment)
        is_bullish_range = range_close > range_open
        
        # 2. 检测突破和操纵 (Manipulation Phase)
        # 当前正在形成的 K 线 (或最近几根) 是否突破了区间
        current_candle = df.iloc[-1]
        current_high = current_candle['high']
        current_low = current_candle['low']
        current_close = current_candle['close']
        
        breakout = False
        manipulation = False
        manipulation_depth = 0.0
        
        range_size = range_high - range_low
        if range_size == 0: range_size = 0.0001
        
        # 操纵逻辑: 
        # 如果是看涨区间 (预期向上)，操纵通常是先向下假突破 (Run Stops below Low)
        # 如果是看跌区间 (预期向下)，操纵通常是先向上假突破 (Run Stops above High)
        
        signal = "hold"
        strength = 0
        reasons = []
        
        if is_bullish_range:
            # 预期向上，检查下方操纵
            if current_low < range_low:
                breakout = True
                manipulation_depth = range_low - current_low
                pct = (manipulation_depth / range_size) * 100
                
                # 检查是否收回 (Distribution Phase Start)
                # 价格重新回到区间内或收盘价高于 range_low
                if current_close > range_low:
                    manipulation = True
                    if pct >= min_manipulation_pct:
                        signal = "buy"
                        strength = 80
                        reasons.append(f"CRT Bullish: Downward Manipulation ({pct:.1f}%) & Reclaim")
                        
        else: # Bearish Range
            # 预期向下，检查上方操纵
            if current_high > range_high:
                breakout = True
                manipulation_depth = current_high - range_high
                pct = (manipulation_depth / range_size) * 100
                
                # 检查是否收回
                if current_close < range_high:
                    manipulation = True
                    if pct >= min_manipulation_pct:
                        signal = "sell"
                        strength = 80
                        reasons.append(f"CRT Bearish: Upward Manipulation ({pct:.1f}%) & Reclaim")
        
        return {
            "signal": signal,
            "strength": strength,
            "reasons": reasons,
            "range_info": {
                "high": range_high,
                "low": range_low,
                "direction": "bullish" if is_bullish_range else "bearish",
                "manipulation_pct": (manipulation_depth / range_size * 100) if breakout else 0
            }
        }
    def analyze_rvgi_cci_strategy(self, df: pd.DataFrame, sma_period: int = 30, cci_period: int = 14, rvi_smooth: int = 4) -> Dict[str, any]:
        """
        基于 RVGI + CCI + SMA 的复合策略分析
        逻辑来源: RVGI_CCI_SMA_Panel_EA.mq5
        
        Args:
            df: OHLCV DataFrame
            sma_period: SMA 周期
            cci_period: CCI 周期
            rvi_smooth: RVI 平滑周期
            
        Returns:
            策略信号和指标值
        """
        if len(df) < max(sma_period, cci_period) + 5:
            return {"signal": "hold", "strength": 0, "reasons": []}
            
        closes = df['close']
        highs = df['high']
        lows = df['low']
        opens = df['open']
        
        # 1. 计算指标
        
        # SMA
        sma = closes.rolling(window=sma_period).mean()
        
        # CCI (Commodity Channel Index)
        tp = (highs + lows + closes) / 3
        sma_tp = tp.rolling(window=cci_period).mean()
        mad = tp.rolling(window=cci_period).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True)
        # 避免除以零
        mad = mad.replace(0, 0.000001)
        cci = (tp - sma_tp) / (0.015 * mad)
        
        # RVI (Relative Vigor Index) - 完整版计算
        # 逻辑来源: MQL5 RVI 计算公式
        
        # 1. 计算 Numerator (Value1) 和 Denominator (Value2) 的基础值
        # Value1 = ((Close - Open) + 2*(Close[1]-Open[1]) + 2*(Close[2]-Open[2]) + (Close[3]-Open[3])) / 6
        # Value2 = ((High - Low) + 2*(High[1]-Low[1]) + 2*(High[2]-Low[2]) + (High[3]-Low[3])) / 6
        
        co = closes - opens
        hl = highs - lows
        
        # 使用 shift 获取前 N 根 K 线的数据
        # 注意: rolling 的 window 包含当前行，shift(1) 是上一行
        
        # 计算 Numerator (Value1)
        num_val = (co + 2 * co.shift(1) + 2 * co.shift(2) + co.shift(3)) / 6
        
        # 计算 Denominator (Value2)
        den_val = (hl + 2 * hl.shift(1) + 2 * hl.shift(2) + hl.shift(3)) / 6
        
        # 2. 对 Num 和 Den 进行 SMA 平滑 (通常周期为 10)
        # 注意: 这里使用传入的 rvi_smooth 还是固定周期? MQL5 标准 RVI 指标通常 Period=10
        # 但这里的函数参数是 rvi_smooth，通常指 Signal 线的平滑?
        # 让我们假设 rvi_smooth 用于 Signal 线，而 RVI 主线的 SMA 周期通常是 10
        # 为了灵活，我们可以引入 rvi_period 参数，默认为 10
        rvi_period = 10 
        
        rvi_num = num_val.rolling(window=rvi_period).mean()
        rvi_den = den_val.rolling(window=rvi_period).mean()
        
        # 避免除以零
        rvi_den = rvi_den.replace(0, 0.000001)
        
        rvi_main = rvi_num / rvi_den
        
        # 3. 计算 Signal Line
        # Signal = (RVI + 2*RVI[1] + 2*RVI[2] + RVI[3]) / 6
        rvi_signal = (rvi_main + 2 * rvi_main.shift(1) + 2 * rvi_main.shift(2) + rvi_main.shift(3)) / 6
        
        # 处理可能的 NaN (由于 shift 和 rolling 导致的前面数据缺失)
        rvi_main = rvi_main.fillna(0)
        rvi_signal = rvi_signal.fillna(0)
        
        # 2. 获取当前值 (最新的已完成 K 线，即 iloc[-2] 或 iloc[-1] 取决于是否包含当前 K)
        # 假设 df 包含当前正在形成的 K 线，我们通常看上一根 K 线的收盘确认信号
        curr = -1 
        prev = -2
        
        price = closes.iloc[curr]
        sma_val = sma.iloc[curr]
        
        cci_now = cci.iloc[curr]
        
        rvi_m_now = rvi_main.iloc[curr]
        rvi_s_now = rvi_signal.iloc[curr]
        rvi_m_prev = rvi_main.iloc[prev]
        rvi_s_prev = rvi_signal.iloc[prev]
        
        # 3. 信号逻辑
        
        # 价格位置
        price_above_sma = price > sma_val
        price_below_sma = price < sma_val
        
        # RVI 交叉
        # 金叉: Main 上穿 Signal
        rvi_cross_up = (rvi_m_prev <= rvi_s_prev) and (rvi_m_now > rvi_s_now)
        # 死叉: Main 下穿 Signal
        rvi_cross_down = (rvi_m_prev >= rvi_s_prev) and (rvi_m_now < rvi_s_now)
        
        # CCI 状态
        cci_buy = cci_now <= -100 # 超卖
        cci_sell = cci_now >= 100 # 超买
        
        signal = "hold"
        strength = 0
        reasons = []
        
        # Sell Signal: Price > SMA + CCI >= 100 + RVI Cross Down
        if price_above_sma and cci_sell and rvi_cross_down:
            signal = "sell"
            strength = 75
            reasons.append("RVGI 死叉 + CCI 超买 + 价格在 SMA 之上")
            
        # Buy Signal: Price < SMA + CCI <= -100 + RVI Cross Up
        elif price_below_sma and cci_buy and rvi_cross_up:
            signal = "buy"
            strength = 75
            reasons.append("RVGI 金叉 + CCI 超卖 + 价格在 SMA 之下")
            
        return {
            "signal": signal,
            "strength": strength,
            "reasons": reasons,
            "indicators": {
                "sma": sma_val,
                "cci": cci_now,
                "rvi_main": rvi_m_now,
                "rvi_signal": rvi_s_now
            }
        }
    def analyze_ifvg(self, df: pd.DataFrame, min_gap_points: int = 100) -> Dict[str, any]:
        """
        分析 IFVG (Inverse Fair Value Gap) - 基于 MQL5 策略逻辑移植
        
        Args:
            df: OHLC DataFrame
            min_gap_points: 最小跳空点数 (默认100点 = 1.0对于黄金)
            
        Returns:
            包含信号和活跃区域的字典
        """
        if len(df) < 5:
            return {"signal": "hold", "strength": 0, "reasons": [], "active_zones": []}

        # 数据准备
        opens = df['open'].values
        highs = df['high'].values
        lows = df['low'].values
        closes = df['close'].values
        times = df.index
        
        # 点值估算 (假设是黄金/外汇，0.01)
        point = 0.01 
        min_gap = min_gap_points * point

        fvgs = [] 
        # 结构: {'type': 'bullish'/'bearish', 'top': float, 'bottom': float, 'start_time': datetime, 
        #       'mitigated': bool, 'inverted': bool, 'inverted_time': datetime}

        # 遍历历史数据检测 FVG
        # 从第3根K线开始 (索引2)
        for i in range(2, len(df)):
            # 1. 检测新 FVG
            
            # Bullish FVG (Gap Up): Low[i] > High[i-2]
            if lows[i] > highs[i-2] and (lows[i] - highs[i-2]) > min_gap:
                fvgs.append({
                    'id': f"bull_{i}",
                    'type': 'bullish', # 原始方向
                    'top': lows[i],
                    'bottom': highs[i-2],
                    'start_time': times[i],
                    'mitigated': False,
                    'inverted': False,
                    'inverted_time': None
                })
                
            # Bearish FVG (Gap Down): Low[i-2] > High[i]
            elif lows[i-2] > highs[i] and (lows[i-2] - highs[i]) > min_gap:
                fvgs.append({
                    'id': f"bear_{i}",
                    'type': 'bearish', # 原始方向
                    'top': lows[i-2],
                    'bottom': highs[i],
                    'start_time': times[i],
                    'mitigated': False,
                    'inverted': False,
                    'inverted_time': None
                })

            # 2. 更新现有 FVG 状态 (基于当前 K 线 i)
            current_low = lows[i]
            current_high = highs[i]
            current_close = closes[i]
            
            for fvg in fvgs:
                # 如果已经反转，暂不需要进一步状态更新(除非失效，这里暂不处理失效)
                if fvg['inverted']:
                    continue

                # 检查 Mitigation (缓解/触碰)
                # MQL5逻辑: breakFar check
                if not fvg['mitigated']:
                    if fvg['type'] == 'bullish':
                        if current_low < fvg['bottom']: # 价格跌破缺口下沿
                            fvg['mitigated'] = True
                    else: # bearish
                        if current_high > fvg['top']: # 价格突破缺口上沿
                            fvg['mitigated'] = True
                
                # 检查 Inversion (反转信号)
                # 必须先被 Mitigated，然后收盘价完全突破
                if fvg['mitigated']:
                    if fvg['type'] == 'bullish':
                        # 原本是看涨缺口，被跌破并收盘在下方 -> 变为看跌阻力 (Bearish Inverted FVG)
                        if current_close < fvg['bottom']:
                            fvg['inverted'] = True
                            fvg['inverted_time'] = times[i]
                    else: # bearish
                        # 原本是看跌缺口，被突破并收盘在上方 -> 变为看涨支撑 (Bullish Inverted FVG)
                        if current_close > fvg['top']:
                            fvg['inverted'] = True
                            fvg['inverted_time'] = times[i]
                            
        # 3. 生成最新信号
        # 检查最后一根 K 线是否触发了新的反转
        last_time = times[-1]
        signal = "hold"
        strength = 0
        reasons = []
        
        latest_inversions = [f for f in fvgs if f['inverted'] and f['inverted_time'] == last_time]
        
        for inv in latest_inversions:
            if inv['type'] == 'bearish': 
                # Bearish FVG Inverted -> Bullish Signal (Buy)
                signal = "buy"
                strength = 80 # IFVG 是强信号
                reasons.append(f"IFVG Bullish Inversion (原看跌缺口被突破)")
            elif inv['type'] == 'bullish':
                # Bullish FVG Inverted -> Bearish Signal (Sell)
                signal = "sell"
                strength = 80
                reasons.append(f"IFVG Bearish Inversion (原看涨缺口被跌破)")
        
        # 过滤出最近的活跃区域用于可视化
        active_zones = [f for f in fvgs if f['start_time'] > times[-50]] # 仅保留最近50根K线的
        
        return {
            "signal": signal,
            "strength": strength,
            "reasons": reasons,
            "active_zones": active_zones
        }

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
    
    def generate_analysis_summary(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        生成综合分析摘要
        
        Args:
            df: 价格数据DataFrame
            
        Returns:
            分析摘要字典
        """
        if len(df) < 20:
            return {
                "summary": "数据不足，无法生成分析摘要",
                "recommendation": "hold",
                "confidence": 0.0
            }
        
        # 计算各种分析指标
        indicators = self.calculate_technical_indicators(df)
        market_regime = self.detect_market_regime(df)
        risk_metrics = self.calculate_risk_metrics(df)
        support_resistance = self.generate_support_resistance(df)
        signal_info = self.generate_signal_from_indicators(indicators)
        
        # 生成综合分析摘要
        current_price = df['close'].iloc[-1]
        price_change_1d = (df['close'].iloc[-1] / df['close'].iloc[-2] - 1) * 100
        price_change_5d = (df['close'].iloc[-1] / df['close'].iloc[-6] - 1) * 100
        
        # 生成交易建议
        if signal_info['signal'] == 'buy' and signal_info['strength'] > 60:
            recommendation = "强烈买入"
        elif signal_info['signal'] == 'buy':
            recommendation = "买入"
        elif signal_info['signal'] == 'sell' and signal_info['strength'] > 60:
            recommendation = "强烈卖出"
        elif signal_info['signal'] == 'sell':
            recommendation = "卖出"
        else:
            recommendation = "持有"
        
        # 生成市场状态描述
        regime_descriptions = {
            "trending": "市场处于趋势状态，适合趋势跟踪策略",
            "ranging": "市场处于震荡状态，适合区间交易策略",
            "high_volatility": "市场波动性较高，注意风险管理",
            "unknown": "市场状态不明确，建议谨慎操作"
        }
        
        regime_desc = regime_descriptions.get(market_regime['regime'], "市场状态分析中")
        
        # 构建摘要
        summary = {
            "summary": f"当前价格: {current_price:.4f} ({price_change_1d:+.2f}% 1日, {price_change_5d:+.2f}% 5日)",
            "market_regime": market_regime['description'],
            "regime_analysis": regime_desc,
            "recommendation": recommendation,
            "confidence": signal_info['confidence'],
            "risk_level": "高" if risk_metrics['volatility'] > 0.3 else "中" if risk_metrics['volatility'] > 0.15 else "低",
            "key_indicators": {
                "RSI": f"{indicators['rsi']:.1f}",
                "MACD": f"{indicators['macd']:.4f}",
                "ATR": f"{indicators['atr']:.4f}",
                "波动率": f"{risk_metrics['volatility']:.2%}"
            },
            "support_levels": support_resistance['support_levels'],
            "resistance_levels": support_resistance['resistance_levels'],
            "timestamp": pd.Timestamp.now().isoformat()
        }
        
        return summary

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