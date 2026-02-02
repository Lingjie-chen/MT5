import pandas as pd
import numpy as np
import logging
import time
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

try:
    import MetaTrader5 as mt5
except ImportError:
    pass

class AdvancedMarketAnalysis:
    """
    高级市场分析工具类
    基于MQL5文章中的最佳实践，利用Python的Pandas和NumPy库
    提供更强大的技术分析和机器学习功能
    """
    
    def __init__(self):
        self.indicators_cache = {}
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        if len(df) < 20:
            return self._get_default_indicators()
        
        indicators = {}
        # SMA
        indicators['sma_20'] = df['close'].tail(20).mean()
        indicators['sma_50'] = df['close'].tail(50).mean() if len(df) >= 50 else indicators['sma_20']
        
        # EMA
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
        
        # ATR
        high_low = df['high'] - df['low']
        high_close_prev = abs(df['high'] - df['close'].shift())
        low_close_prev = abs(df['low'] - df['close'].shift())
        true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
        indicators['atr'] = true_range.rolling(window=14).mean().iloc[-1]
        
        # Volume
        indicators['volume_sma'] = df['volume'].tail(20).mean()
        indicators['current_volume'] = df['volume'].iloc[-1]
        indicators['volume_ratio'] = indicators['current_volume'] / indicators['volume_sma'] if indicators['volume_sma'] > 0 else 1
        
        # Momentum
        indicators['momentum_5'] = (df['close'].iloc[-1] / df['close'].iloc[-6] - 1) * 100
        indicators['momentum_10'] = (df['close'].iloc[-1] / df['close'].iloc[-11] - 1) * 100
        
        return indicators
    
    def detect_market_regime(self, df: pd.DataFrame) -> Dict[str, any]:
        if len(df) < 50:
            return {"regime": "unknown", "confidence": 0.5, "description": "数据不足"}
        
        returns = df['close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)
        price_change = (df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100
        
        highs = df['high']
        lows = df['low']
        plus_dm = highs.diff()
        minus_dm = -lows.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        tr = pd.concat([highs - lows, abs(highs - df['close'].shift()), abs(lows - df['close'].shift())], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean()
        plus_di = 100 * (plus_dm.rolling(window=14).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=14).mean() / atr)
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=14).mean()
        current_adx = adx.iloc[-1] if not pd.isna(adx.iloc[-1]) else 0
        
        if volatility > 0.3:
            regime = "high_volatility"
            confidence = min(volatility / 0.5, 0.9)
            description = "高波动市场"
        elif current_adx > 25:
            regime = "trending"
            confidence = min(current_adx / 50, 0.9)
            description = "趋势市场"
        else:
            regime = "ranging"
            confidence = 0.7
            description = "震荡市场"
        
        return {"regime": regime, "confidence": confidence, "description": description, "volatility": volatility, "adx": current_adx, "price_change": price_change}
    
    def calculate_donchian_channels(self, df: pd.DataFrame, period: int = 20) -> Dict[str, float]:
        """
        计算唐奇安通道 (Turtle Trading 核心指标)
        """
        if len(df) < period:
            return {"upper": 0, "lower": 0, "middle": 0}
        
        # Donchian Channel is the Max High / Min Low of the LAST 'period' days (excluding current if used for breakout signal, 
        # but typically calculated on closed candles)
        # We use the window of 'period' size ending at previous candle for signal generation, 
        # or current window for visualization. 
        # Turtle Rule: Buy when price > High of last 20 days.
        
        recent_data = df.tail(period + 1).iloc[:-1] # Exclude current forming candle for strict breakout check
        if len(recent_data) < period:
            recent_data = df.tail(period)

        upper = recent_data['high'].max()
        lower = recent_data['low'].min()
        middle = (upper + lower) / 2
        
        return {"donchian_upper": upper, "donchian_lower": lower, "donchian_middle": middle}

    def detect_strict_supply_demand(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        严格供需区识别 (Strict Supply/Demand Zones)
        结合 动量(Momentum) + 盘整(Base) + 新鲜度(Freshness)
        """
        if len(df) < 50: return {"signal": "neutral", "zones": []}
        
        closes = df['close'].values
        opens = df['open'].values
        highs = df['high'].values
        lows = df['low'].values
        volatilities = (df['high'] - df['low']).values
        avg_vol = np.mean(volatilities[-50:])
        
        zones = []
        
        # Look back for strong impulse moves
        for i in range(len(df)-2, 10, -1):
            body_size = abs(closes[i] - opens[i])
            is_bullish_impulse = closes[i] > opens[i] and body_size > avg_vol * 2.0 # Strong move
            is_bearish_impulse = closes[i] < opens[i] and body_size > avg_vol * 2.0
            
            if is_bullish_impulse:
                # Look for base (consolidation) before impulse
                # Check previous 1-3 candles for small bodies
                is_base = True
                base_high = -1
                base_low = 999999
                base_start_idx = i
                
                for k in range(1, 4):
                    prev_idx = i - k
                    if prev_idx < 0: break
                    prev_body = abs(closes[prev_idx] - opens[prev_idx])
                    if prev_body > avg_vol * 1.0: # Base candles should be small
                        is_base = False
                        break
                    base_high = max(base_high, highs[prev_idx])
                    base_low = min(base_low, lows[prev_idx])
                    base_start_idx = prev_idx
                
                if is_base and base_high > 0:
                    # Demand Zone Found (Rally-Base-Rally or Drop-Base-Rally)
                    # For simplicity, we define the Zone as the Base High/Low
                    zones.append({
                        'type': 'demand',
                        'top': base_high,
                        'bottom': base_low,
                        'index': base_start_idx,
                        'strength': 'strong', # Strict criteria met
                        'tested_count': 0
                    })
            
            elif is_bearish_impulse:
                # Look for base
                is_base = True
                base_high = -1
                base_low = 999999
                base_start_idx = i
                
                for k in range(1, 4):
                    prev_idx = i - k
                    if prev_idx < 0: break
                    prev_body = abs(closes[prev_idx] - opens[prev_idx])
                    if prev_body > avg_vol * 1.0:
                        is_base = False
                        break
                    base_high = max(base_high, highs[prev_idx])
                    base_low = min(base_low, lows[prev_idx])
                    base_start_idx = prev_idx
                    
                if is_base and base_high > 0:
                    # Supply Zone Found
                    zones.append({
                        'type': 'supply',
                        'top': base_high,
                        'bottom': base_low,
                        'index': base_start_idx,
                        'strength': 'strong',
                        'tested_count': 0
                    })
        
        # Check if current price is in any fresh zone
        current_price = closes[-1]
        signal = "neutral"
        reason = ""
        active_zones = []
        
        for zone in zones[:5]: # Check 5 most recent zones
            # Check if price has already mitigated this zone (simple check)
            # In a real strict system, we'd track all price history since zone creation.
            # Here we just check if current price is inside.
            
            is_inside = False
            if zone['type'] == 'demand':
                if zone['bottom'] <= current_price <= zone['top'] * 1.001: # Slight tolerance
                    signal = "buy"
                    reason = "Price in Strict Demand Zone"
                    is_inside = True
            elif zone['type'] == 'supply':
                if zone['bottom'] * 0.999 <= current_price <= zone['top']:
                    signal = "sell"
                    reason = "Price in Strict Supply Zone"
                    is_inside = True
            
            if is_inside:
                active_zones.append(zone)
                break # Priority to most recent
                
        return {"signal": signal, "reason": reason, "active_zones": active_zones}

    def generate_support_resistance(self, df: pd.DataFrame, lookback_period: int = 100) -> Dict[str, List[float]]:
        if len(df) < lookback_period: lookback_period = len(df)
        recent_data = df.tail(lookback_period)
        recent_high = recent_data['high'].max()
        recent_low = recent_data['low'].min()
        price_range = recent_high - recent_low
        current_price = df['close'].iloc[-1]
        
        support_levels = []
        for i in range(1, 4):
            level = current_price - (price_range * 0.1 * i)
            if level > recent_low: support_levels.append(float(round(level, 4)))
            
        resistance_levels = []
        for i in range(1, 4):
            level = current_price + (price_range * 0.1 * i)
            if level < recent_high: resistance_levels.append(float(round(level, 4)))
            
        if not support_levels: support_levels = [float(round(recent_low, 4))]
        if not resistance_levels: resistance_levels = [float(round(recent_high, 4))]
        
        return {"support_levels": sorted(support_levels), "resistance_levels": sorted(resistance_levels), "current_price": current_price}
    
    def calculate_risk_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        if len(df) < 30: return self._get_default_risk_metrics()
        returns = df['close'].pct_change().dropna()
        metrics = {
            "volatility": returns.std() * np.sqrt(252),
            "sharpe_ratio": returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0,
            "max_drawdown": self._calculate_max_drawdown(df['close']),
            "var_95": np.percentile(returns, 5) * 100,
            "expected_shortfall": returns[returns <= np.percentile(returns, 5)].mean() * 100,
            "skewness": returns.skew(),
            "kurtosis": returns.kurtosis()
        }
        return metrics
        
    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        cumulative_returns = (1 + prices.pct_change()).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        return drawdown.min() * 100
    
    def _get_default_indicators(self) -> Dict[str, float]:
        return {"sma_20": 0, "sma_50": 0, "ema_12": 0, "ema_26": 0, "macd": 0, "macd_signal": 0, "macd_histogram": 0, "rsi": 50, "bb_upper": 0, "bb_lower": 0, "bb_middle": 0, "atr": 0, "volume_sma": 0, "current_volume": 0, "volume_ratio": 1, "momentum_5": 0, "momentum_10": 0}
        
    def generate_signal_from_indicators(self, indicators: Dict[str, float]) -> Dict[str, any]:
        signal = "hold"; strength = 0; reasons = []
        if indicators['macd'] > indicators['macd_signal'] and indicators['macd_histogram'] > 0: strength += 25; reasons.append("MACD金叉")
        elif indicators['macd'] < indicators['macd_signal'] and indicators['macd_histogram'] < 0: strength -= 25; reasons.append("MACD死叉")
        if indicators['rsi'] < 30: strength += 20; reasons.append("RSI超卖")
        elif indicators['rsi'] > 70: strength -= 20; reasons.append("RSI超买")
        if indicators['ema_12'] > indicators['ema_26']: strength += 15; reasons.append("EMA金叉")
        elif indicators['ema_12'] < indicators['ema_26']: strength -= 15; reasons.append("EMA死叉")
        current_price = indicators.get('current_price', indicators['sma_20'])
        if current_price < indicators['bb_lower']: strength += 15; reasons.append("价格触及布林带下轨")
        elif current_price > indicators['bb_upper']: strength -= 15; reasons.append("价格触及布林带上轨")
        if indicators['volume_ratio'] > 1.5: strength += 10; reasons.append("成交量放大")
        
        if strength >= 40: signal = "buy"
        elif strength <= -40: signal = "sell"
        return {"signal": signal, "strength": abs(strength), "reasons": reasons, "confidence": min(abs(strength) / 100, 1.0)}

    def _get_default_risk_metrics(self) -> Dict[str, float]:
        return {"volatility": 0.2, "sharpe_ratio": 0, "max_drawdown": 0, "var_95": -2, "expected_shortfall": -3, "skewness": 0, "kurtosis": 0}

    def generate_analysis_summary(self, df: pd.DataFrame) -> Dict[str, any]:
        if len(df) < 20: return {"summary": "数据不足", "recommendation": "hold", "confidence": 0.0}
        indicators = self.calculate_technical_indicators(df)
        market_regime = self.detect_market_regime(df)
        risk_metrics = self.calculate_risk_metrics(df)
        support_resistance = self.generate_support_resistance(df)
        signal_info = self.generate_signal_from_indicators(indicators)
        current_price = df['close'].iloc[-1]
        
        recommendation = "持有"
        if signal_info['signal'] == 'buy': recommendation = "强烈买入" if signal_info['strength'] > 60 else "买入"
        elif signal_info['signal'] == 'sell': recommendation = "强烈卖出" if signal_info['strength'] > 60 else "卖出"
        
        return {
            "summary": f"当前价格: {current_price:.4f}",
            "market_regime": market_regime['description'],
            "recommendation": recommendation,
            "confidence": signal_info['confidence'],
            "risk_level": "高" if risk_metrics['volatility'] > 0.3 else "中",
            "key_indicators": {"RSI": f"{indicators['rsi']:.1f}", "MACD": f"{indicators['macd']:.4f}"},
            "support_levels": support_resistance['support_levels'],
            "resistance_levels": support_resistance['resistance_levels']
        }
    
    def analyze_ifvg(self, df: pd.DataFrame, min_gap_points: int = 100) -> Dict[str, any]:
        if len(df) < 5: return {"signal": "hold", "strength": 0, "reasons": [], "active_zones": []}
        lows = df['low'].values; highs = df['high'].values; closes = df['close'].values; times = df.index
        point = 0.01; min_gap = min_gap_points * point
        fvgs = []
        for i in range(2, len(df)):
            if lows[i] > highs[i-2] and (lows[i] - highs[i-2]) > min_gap:
                fvgs.append({'id': f"bull_{i}", 'type': 'bullish', 'top': lows[i], 'bottom': highs[i-2], 'start_time': times[i], 'mitigated': False, 'inverted': False, 'inverted_time': None})
            elif lows[i-2] > highs[i] and (lows[i-2] - highs[i]) > min_gap:
                fvgs.append({'id': f"bear_{i}", 'type': 'bearish', 'top': lows[i-2], 'bottom': highs[i], 'start_time': times[i], 'mitigated': False, 'inverted': False, 'inverted_time': None})
            
            current_low = lows[i]; current_high = highs[i]; current_close = closes[i]
            for fvg in fvgs:
                if fvg['inverted']: continue
                if not fvg['mitigated']:
                    if fvg['type'] == 'bullish' and current_low < fvg['bottom']: fvg['mitigated'] = True
                    elif fvg['type'] == 'bearish' and current_high > fvg['top']: fvg['mitigated'] = True
                if fvg['mitigated']:
                    if fvg['type'] == 'bullish' and current_close < fvg['bottom']: fvg['inverted'] = True; fvg['inverted_time'] = times[i]
                    elif fvg['type'] == 'bearish' and current_close > fvg['top']: fvg['inverted'] = True; fvg['inverted_time'] = times[i]
        
        last_time = times[-1]; signal = "hold"; strength = 0; reasons = []
        latest_inversions = [f for f in fvgs if f['inverted'] and f['inverted_time'] == last_time]
        for inv in latest_inversions:
            if inv['type'] == 'bearish': signal = "buy"; strength = 80; reasons.append("IFVG Bullish Inversion")
            elif inv['type'] == 'bullish': signal = "sell"; strength = 80; reasons.append("IFVG Bearish Inversion")
        
        return {"signal": signal, "strength": strength, "reasons": reasons, "active_zones": [f for f in fvgs if f['start_time'] > times[-50]]}

    def calculate_rvgi_cci_series(self, df: pd.DataFrame, sma_period: int = 30, cci_period: int = 14) -> pd.Series:
        if len(df) < max(sma_period, cci_period) + 5: return pd.Series(0, index=df.index)
        
        closes = df['close']; highs = df['high']; lows = df['low']; opens = df['open']
        sma = closes.rolling(window=sma_period).mean()
        tp = (highs + lows + closes) / 3
        sma_tp = tp.rolling(window=cci_period).mean()
        mad = tp.rolling(window=cci_period).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True).replace(0, 0.000001)
        cci = (tp - sma_tp) / (0.015 * mad)
        
        co = closes - opens; hl = highs - lows
        num_val = (co + 2 * co.shift(1) + 2 * co.shift(2) + co.shift(3)) / 6
        den_val = (hl + 2 * hl.shift(1) + 2 * hl.shift(2) + hl.shift(3)) / 6
        rvi_period = 10
        rvi_num = num_val.rolling(window=rvi_period).mean()
        rvi_den = den_val.rolling(window=rvi_period).mean().replace(0, 0.000001)
        rvi_main = (rvi_num / rvi_den).fillna(0)
        rvi_signal = ((rvi_main + 2 * rvi_main.shift(1) + 2 * rvi_main.shift(2) + rvi_main.shift(3)) / 6).fillna(0)
        
        # Vectorized Logic
        price_above_sma = closes > sma
        price_below_sma = closes < sma
        
        rvi_cross_up = (rvi_main.shift(1) <= rvi_signal.shift(1)) & (rvi_main > rvi_signal)
        rvi_cross_down = (rvi_main.shift(1) >= rvi_signal.shift(1)) & (rvi_main < rvi_signal)
        
        cci_buy = cci <= -100
        cci_sell = cci >= 100
        
        signals = pd.Series(0, index=df.index)
        
        # Sell Condition: price_above_sma and cci_sell and rvi_cross_down
        sell_cond = price_above_sma & cci_sell & rvi_cross_down
        signals[sell_cond] = -1
        
        # Buy Condition: price_below_sma and cci_buy and rvi_cross_up
        buy_cond = price_below_sma & cci_buy & rvi_cross_up
        signals[buy_cond] = 1
        
        return signals

    def analyze_rvgi_cci_strategy(self, df: pd.DataFrame, sma_period: int = 30, cci_period: int = 14) -> Dict[str, any]:
        if len(df) < max(sma_period, cci_period) + 5: return {"signal": "hold", "strength": 0, "reasons": []}
        closes = df['close']; highs = df['high']; lows = df['low']; opens = df['open']
        sma = closes.rolling(window=sma_period).mean()
        tp = (highs + lows + closes) / 3
        sma_tp = tp.rolling(window=cci_period).mean()
        mad = tp.rolling(window=cci_period).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True).replace(0, 0.000001)
        cci = (tp - sma_tp) / (0.015 * mad)
        
        co = closes - opens; hl = highs - lows
        num_val = (co + 2 * co.shift(1) + 2 * co.shift(2) + co.shift(3)) / 6
        den_val = (hl + 2 * hl.shift(1) + 2 * hl.shift(2) + hl.shift(3)) / 6
        rvi_period = 10
        rvi_num = num_val.rolling(window=rvi_period).mean()
        rvi_den = den_val.rolling(window=rvi_period).mean().replace(0, 0.000001)
        rvi_main = (rvi_num / rvi_den).fillna(0)
        rvi_signal = ((rvi_main + 2 * rvi_main.shift(1) + 2 * rvi_main.shift(2) + rvi_main.shift(3)) / 6).fillna(0)
        
        curr = -1; prev = -2
        price = closes.iloc[curr]; sma_val = sma.iloc[curr]; cci_now = cci.iloc[curr]
        rvi_m_now = rvi_main.iloc[curr]; rvi_s_now = rvi_signal.iloc[curr]
        rvi_m_prev = rvi_main.iloc[prev]; rvi_s_prev = rvi_signal.iloc[prev]
        
        price_above_sma = price > sma_val; price_below_sma = price < sma_val
        rvi_cross_up = (rvi_m_prev <= rvi_s_prev) and (rvi_m_now > rvi_s_now)
        rvi_cross_down = (rvi_m_prev >= rvi_s_prev) and (rvi_m_now < rvi_s_now)
        cci_buy = cci_now <= -100; cci_sell = cci_now >= 100
        
        signal = "hold"; strength = 0; reasons = []
        if price_above_sma and cci_sell and rvi_cross_down: signal = "sell"; strength = 75; reasons.append("RVGI死叉+CCI超买+SMA之上")
        elif price_below_sma and cci_buy and rvi_cross_up: signal = "buy"; strength = 75; reasons.append("RVGI金叉+CCI超卖+SMA之下")
        
        return {"signal": signal, "strength": strength, "reasons": reasons, "indicators": {"sma": sma_val, "cci": cci_now}}

class MFHAnalyzer:
    def __init__(self, input_size=16, learning_rate=0.01):
        self.input_size = input_size
        self.learning_rate = learning_rate
        self.horizon = 5 
        self.ma_period = 5 
        self.weights = np.random.randn(input_size) * np.sqrt(1 / input_size)
        self.bias = 0.0
        self.last_features = None
        self.last_prediction = 0.0
        self.count = 0
        self.mean = np.zeros(input_size)
        self.m2 = np.zeros(input_size)
        
    def calculate_features(self, df):
        if len(df) < (self.ma_period + self.horizon + 1): return None
        closes = df['close'].values; opens = df['open'].values; highs = df['high'].values; lows = df['low'].values
        ma_close = df['close'].rolling(window=self.ma_period).mean().values
        ma_open = df['open'].rolling(window=self.ma_period).mean().values
        ma_high = df['high'].rolling(window=self.ma_period).mean().values
        ma_low = df['low'].rolling(window=self.ma_period).mean().values
        curr = -1; prev_h = -1 - self.horizon
        features = np.zeros(16)
        features[0] = closes[curr]; features[1] = opens[curr]; features[2] = highs[curr]; features[3] = lows[curr]
        features[4] = ma_close[curr]; features[5] = ma_open[curr]; features[6] = ma_high[curr]; features[7] = ma_low[curr]
        features[8] = opens[curr] - opens[prev_h]; features[9] = highs[curr] - highs[prev_h]
        features[10] = lows[curr] - lows[prev_h]; features[11] = closes[curr] - closes[prev_h]
        features[12] = ma_close[curr] - ma_close[prev_h]; features[13] = ma_open[curr] - ma_open[prev_h]
        features[14] = ma_high[curr] - ma_high[prev_h]; features[15] = ma_low[curr] - ma_low[prev_h]
        
        if self.count == 0: self.mean = features.copy(); self.m2 = np.zeros_like(features)
        else:
            delta = features - self.mean; self.mean += delta / (self.count + 1)
            delta2 = features - self.mean; self.m2 += delta * delta2
        self.count += 1
        if self.count < 2: std = np.ones_like(features)
        else: variance = self.m2 / (self.count - 1); std = np.sqrt(variance); std[std == 0] = 1.0
        return (features - self.mean) / std

    def prepare_features_batch(self, df):
        """Pre-calculate features for the entire dataframe for optimization speedup"""
        if len(df) < (self.ma_period + self.horizon + 1): return None
        
        # Calculate rolling means vectorially
        ma_close = df['close'].rolling(window=self.ma_period).mean()
        ma_open = df['open'].rolling(window=self.ma_period).mean()
        ma_high = df['high'].rolling(window=self.ma_period).mean()
        ma_low = df['low'].rolling(window=self.ma_period).mean()
        
        closes = df['close'].values; opens = df['open'].values; highs = df['high'].values; lows = df['low'].values
        ma_c_vals = ma_close.values; ma_o_vals = ma_open.values; ma_h_vals = ma_high.values; ma_l_vals = ma_low.values
        
        n = len(df)
        feature_matrix = np.zeros((n, 16))
        
        # Shifted arrays for previous values (horizon)
        # prev_idx = i - self.horizon
        # We can use pandas shift
        closes_prev = df['close'].shift(self.horizon).values
        opens_prev = df['open'].shift(self.horizon).values
        highs_prev = df['high'].shift(self.horizon).values
        lows_prev = df['low'].shift(self.horizon).values
        
        ma_c_prev = ma_close.shift(self.horizon).values
        ma_o_prev = ma_open.shift(self.horizon).values
        ma_h_prev = ma_high.shift(self.horizon).values
        ma_l_prev = ma_low.shift(self.horizon).values
        
        # Fill Matrix
        # Indices where valid
        start = self.ma_period + self.horizon
        
        feature_matrix[:, 0] = closes
        feature_matrix[:, 1] = opens
        feature_matrix[:, 2] = highs
        feature_matrix[:, 3] = lows
        feature_matrix[:, 4] = ma_c_vals
        feature_matrix[:, 5] = ma_o_vals
        feature_matrix[:, 6] = ma_h_vals
        feature_matrix[:, 7] = ma_l_vals
        
        feature_matrix[:, 8] = opens - opens_prev
        feature_matrix[:, 9] = highs - highs_prev
        feature_matrix[:, 10] = lows - lows_prev
        feature_matrix[:, 11] = closes - closes_prev
        feature_matrix[:, 12] = ma_c_vals - ma_c_prev
        feature_matrix[:, 13] = ma_o_vals - ma_o_prev
        feature_matrix[:, 14] = ma_h_vals - ma_h_prev
        feature_matrix[:, 15] = ma_l_vals - ma_l_prev
        
        # Normalize incrementally? 
        # For batch optimization, we can just normalize standardly or simulate online normalization.
        # Simulating online normalization in batch is slow (loop).
        # We will use simple batch normalization for optimization speed.
        # It's a slight deviation but acceptable for parameter tuning.
        
        mean = np.nanmean(feature_matrix[start:], axis=0)
        std = np.nanstd(feature_matrix[start:], axis=0)
        std[std == 0] = 1.0
        
        normalized = (feature_matrix - mean) / std
        return normalized

    def predict(self, df):
        features = self.calculate_features(df)
        if features is None: return {"signal": "neutral", "slope": 0.0}
        self.last_features = features
        prediction = np.dot(self.weights, features) + self.bias
        self.last_prediction = prediction
        slope = prediction
        signal = "buy" if slope > 0.001 else "sell" if slope < -0.001 else "neutral"
        return {"signal": signal, "slope": float(slope), "features": features.tolist() if features is not None else []}
        
    def train(self, current_price_change):
        if self.last_features is None: return
        target = current_price_change
        error = target - self.last_prediction
        self.weights += self.learning_rate * error * self.last_features
        self.bias += self.learning_rate * error
        return error

class SMCAnalyzer:
    def __init__(self):
        self.last_structure = "neutral" 
        self.ma_period = 200
        self.swing_lookback = 5
        self.atr_threshold = 0.002
        self.allow_bos = True; self.allow_ob = True; self.allow_fvg = True; self.use_sentiment = True

    def calculate_ema(self, series, period):
        return series.ewm(span=period, adjust=False).mean()

    def get_mtf_data(self, symbol, timeframe, count=250):
        try:
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
            if rates is None or len(rates) == 0: return None
            return pd.DataFrame(rates)
        except: return None

    def get_market_sentiment(self, df_current, symbol):
        # User Request: Analysis H1 -> M15 as HTF
        df_htf = self.get_mtf_data(symbol, mt5.TIMEFRAME_M15, 300)
        if df_htf is None: return 0, "Neutral"
        ema_long = self.calculate_ema(df_htf['close'], self.ma_period).iloc[-1]
        current_price_htf = df_htf['close'].iloc[-1]
        deviation = abs(current_price_htf - ema_long) / ema_long
        higher_tf_bias = 0
        if current_price_htf > ema_long and deviation > self.atr_threshold: higher_tf_bias = 1
        elif current_price_htf < ema_long and deviation > self.atr_threshold: higher_tf_bias = -1
        
        def check_structure(df):
            highs = df['high'].values; lows = df['low'].values; n = len(df)
            swing_highs = []; swing_lows = []
            for i in range(n - 3, 2, -1):
                if len(swing_highs) < 2:
                    if (highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i+1] and highs[i] > highs[i+2]): swing_highs.append(highs[i])
                if len(swing_lows) < 2:
                    if (lows[i] < lows[i-1] and lows[i] < lows[i-2] and lows[i] < lows[i+1] and lows[i] < lows[i+2]): swing_lows.append(lows[i])
                if len(swing_highs) >= 2 and len(swing_lows) >= 2: break
            is_bull = False; is_bear = False
            if len(swing_highs) >= 2 and len(swing_lows) >= 2:
                if swing_highs[0] > swing_highs[1] and swing_lows[0] > swing_lows[1]: is_bull = True
                if swing_highs[0] < swing_highs[1] and swing_lows[0] < swing_lows[1]: is_bear = True
            has_break = False; curr_close = df['close'].iloc[-1]
            rec_high = swing_highs[0] if swing_highs else highs[-20:].max()
            rec_low = swing_lows[0] if swing_lows else lows[-20:].min()
            if higher_tf_bias == 1 and curr_close > rec_high: has_break = True
            elif higher_tf_bias == -1 and curr_close < rec_low: has_break = True
            return is_bull, is_bear, has_break

        tf1_bull, tf1_bear, tf1_break = check_structure(df_htf)
        tf2_bull, tf2_bear, tf2_break = check_structure(df_current)
        sentiment = 0; text = "Neutral"
        if higher_tf_bias == 1 and tf1_bull and tf2_bull: sentiment = 1; text = "Bullish"
        elif higher_tf_bias == -1 and tf1_bear and tf2_bear: sentiment = -1; text = "Bearish"
        elif higher_tf_bias == 1 and (tf1_break or tf2_break): sentiment = 2; text = "Risk-On"
        elif higher_tf_bias == -1 and (tf1_break or tf2_break): sentiment = -2; text = "Risk-Off"
        return sentiment, text

    def analyze(self, df, symbol=None):
        if df is None or len(df) < 50: return {"signal": "neutral", "structure": "neutral", "reason": "数据不足"}
        sentiment_score = 0; sentiment_text = "Neutral"
        if symbol:
            try: sentiment_score, sentiment_text = self.get_market_sentiment(df, symbol)
            except: pass
        active_strategy = "OB"
        if self.use_sentiment:
            if abs(sentiment_score) == 1: active_strategy = "BOS"
            elif abs(sentiment_score) == 2: active_strategy = "FVG"
        else: active_strategy = "ALL"
        
        ob_signal = self.detect_order_blocks(df)
        fvg_signal = self.detect_fvg(df)
        bos_signal = self.detect_bos(df)
        smart_structure = self.detect_smart_structure(df, sentiment_score) # [NEW] Integrated Smart Structure (BOS/CHoCH)
        pd_info = self.detect_premium_discount(df)
        final_signal = "neutral"; reason = f"Sentiment: {sentiment_text} ({active_strategy})"; strength = 0
        in_premium = pd_info['zone'] == 'premium'; in_discount = pd_info['zone'] == 'discount'
        
        # Integrate Smart Structure Signal
        if smart_structure['signal'] != 'neutral':
             # Smart Structure (BOS/CHoCH) has high priority
             if active_strategy == "ALL" or active_strategy == "BOS":
                 final_signal = smart_structure['signal']
                 reason = f"SMC {smart_structure.get('type', 'Structure')}: {smart_structure['reason']}"
                 strength = 85
        
        if (active_strategy == "ALL" or active_strategy == "BOS") and self.allow_bos and final_signal == "neutral":
            if bos_signal['signal'] != "neutral":
                aligned = False
                # BOS typically means continuation, so it must align with trend
                if (bos_signal['signal'] == 'buy' and sentiment_score >= 0): aligned = True
                if (bos_signal['signal'] == 'sell' and sentiment_score <= 0): aligned = True
                
                # Special Case: CHoCH (Change of Character) - Reversal
                # If sentiment is opposite but we have a strong structure break, it might be CHoCH
                # For now, we strictly follow user's "Trend Trading" request, so we prioritize alignment.
                
                if aligned: 
                    final_signal = bos_signal['signal']
                    reason = f"SMC BOS (Structure Break): {bos_signal['reason']}"
                    strength = 90 # Increased strength for strict execution
                    is_strict_trigger = True # User Requirement: Strictly execute on structure break
                else:
                    is_strict_trigger = False

        if final_signal == "neutral" and (active_strategy == "ALL" or active_strategy == "FVG") and self.allow_fvg:
            if fvg_signal['signal'] != "neutral":
                valid_zone = True
                if fvg_signal['signal'] == 'buy' and not in_discount: valid_zone = False 
                if fvg_signal['signal'] == 'sell' and not in_premium: valid_zone = False 
                aligned = False
                if (fvg_signal['signal'] == 'buy' and sentiment_score >= 0): aligned = True
                if (fvg_signal['signal'] == 'sell' and sentiment_score <= 0): aligned = True
                if aligned and valid_zone: final_signal = fvg_signal['signal']; reason = f"SMC FVG: {fvg_signal['reason']}"; strength = 85

        if final_signal == "neutral" and (active_strategy == "ALL" or active_strategy == "OB") and self.allow_ob:
            if ob_signal['signal'] != "neutral":
                aligned = False
                if (ob_signal['signal'] == 'buy' and sentiment_score >= 0 and in_discount): aligned = True
                if (ob_signal['signal'] == 'sell' and sentiment_score <= 0 and in_premium): aligned = True
                if aligned: final_signal = ob_signal['signal']; reason = f"SMC OB: {ob_signal['reason']}"; strength = 75

        return {"signal": final_signal, "structure": sentiment_text, "reason": reason, "sentiment_score": sentiment_score, "active_strategy": active_strategy, "details": {"ob": ob_signal, "fvg": fvg_signal, "bos": bos_signal, "smart_structure": smart_structure, "premium_discount": pd_info}}

    def detect_premium_discount(self, df):
        highs = df['high'].values; lows = df['low'].values
        range_high = max(highs[-50:]); range_low = min(lows[-50:]); mid_point = (range_high + range_low) / 2
        current_price = df['close'].iloc[-1]
        zone = "equilibrium"
        if current_price > mid_point: zone = "premium"
        elif current_price < mid_point: zone = "discount"
        return {"zone": zone, "range_high": range_high, "range_low": range_low}

    def detect_order_blocks(self, df):
        closes = df['close'].values; opens = df['open'].values; highs = df['high'].values; lows = df['low'].values; current_ask = closes[-1]
        active_obs = []
        for i in range(len(df)-2, len(df)-30, -1):
            if (opens[i-1] > closes[i-1] and opens[i] < closes[i] and (closes[i] - opens[i]) > (opens[i-1] - closes[i-1]) * 1.5):
                ob_high = highs[i-1]; ob_low = lows[i-1]
                active_obs.append({'type': 'bullish', 'top': ob_high, 'bottom': ob_low, 'index': i})
            if (opens[i-1] < closes[i-1] and opens[i] > closes[i] and (opens[i] - closes[i]) > (closes[i-1] - opens[i-1]) * 1.5):
                ob_high = highs[i-1]; ob_low = lows[i-1]
                active_obs.append({'type': 'bearish', 'top': ob_high, 'bottom': ob_low, 'index': i})
        
        # Determine signal based on active OBs
        signal = "neutral"; reason = ""; price = 0
        for ob in active_obs:
            if ob['type'] == 'bullish' and current_ask >= ob['bottom'] and current_ask <= ob['top']:
                signal = "buy"; reason = "Bullish OB Retest"; price = ob['top']
                break
            if ob['type'] == 'bearish' and current_ask <= ob['top'] and current_ask >= ob['bottom']:
                signal = "sell"; reason = "Bearish OB Retest"; price = ob['bottom']
                break
                
        return {"signal": signal, "reason": reason, "price": price, "active_obs": active_obs}

    def detect_fvg(self, df):
        highs = df['high'].values; lows = df['low'].values; closes = df['close'].values; point = 0.00001
        active_fvgs = []
        for i in range(len(df)-1, 2, -1):
            if lows[i-2] > highs[i] + (3*point):
                gap_top = lows[i-2]; gap_bot = highs[i]
                active_fvgs.append({'type': 'bullish', 'top': gap_top, 'bottom': gap_bot, 'index': i})
            if highs[i-2] < lows[i] - (3*point):
                gap_top = lows[i]; gap_bot = highs[i-2]
                active_fvgs.append({'type': 'bearish', 'top': gap_top, 'bottom': gap_bot, 'index': i})
        
        # Determine signal based on active FVGs
        signal = "neutral"; reason = ""; top = 0; bottom = 0
        for fvg in active_fvgs:
            curr = closes[-1]
            if fvg['type'] == 'bullish' and curr <= fvg['top'] and curr >= fvg['bottom']:
                signal = "buy"; reason = "Bullish FVG (Gap Fill)"; top = fvg['top']; bottom = fvg['bottom']
                break
            if fvg['type'] == 'bearish' and curr <= fvg['top'] and curr >= fvg['bottom']:
                signal = "sell"; reason = "Bearish FVG (Gap Fill)"; top = fvg['top']; bottom = fvg['bottom']
                break
                
        return {"signal": signal, "reason": reason, "top": top, "bottom": bottom, "active_fvgs": active_fvgs}

    def detect_structure_points(self, df):
        """
        识别最近的市场结构点 (Swing Highs / Swing Lows)
        返回: 结构列表, 包含价格、索引、类型(SH/SL)
        """
        highs = df['high'].values; lows = df['low'].values
        n = len(df)
        points = []
        
        # 使用动态回溯，寻找分形点
        # Fractal: High[i] > High[i-2...i+2]
        for i in range(n-3, 2, -1):
            is_sh = True
            is_sl = True
            
            # Check Swing High
            for k in range(1, 4): # Look left and right 3 bars
                if i-k >= 0 and highs[i] <= highs[i-k]: is_sh = False
                if i+k < n and highs[i] <= highs[i+k]: is_sh = False
            
            # Check Swing Low
            for k in range(1, 4):
                if i-k >= 0 and lows[i] >= lows[i-k]: is_sl = False
                if i+k < n and lows[i] >= lows[i+k]: is_sl = False
                
            if is_sh: points.append({'type': 'SH', 'price': highs[i], 'index': i, 'time': df.index[i]})
            if is_sl: points.append({'type': 'SL', 'price': lows[i], 'index': i, 'time': df.index[i]})
            
            if len(points) >= 10: break # 只找最近的10个点
            
        return sorted(points, key=lambda x: x['index']) # 按时间正序排列

    def detect_smart_structure(self, df, sentiment_score):
        """
        综合检测 BOS 和 CHoCH
        基于最近的 Swing Points 和 宏观趋势 (sentiment_score)
        """
        points = self.detect_structure_points(df)
        if not points: return {"signal": "neutral", "reason": "No Structure Points"}
        
        current_close = df['close'].iloc[-1]
        
        # 1. 确定当前微观结构趋势 (基于最近两个同类点)
        last_sh = [p for p in points if p['type'] == 'SH']
        last_sl = [p for p in points if p['type'] == 'SL']
        
        if len(last_sh) < 2 or len(last_sl) < 2: return {"signal": "neutral", "reason": "Insufficient Structure"}
        
        # 最近的一个 SH 和 SL
        recent_sh = last_sh[-1]
        recent_sl = last_sl[-1]
        prev_sh = last_sh[-2]
        prev_sl = last_sl[-2]
        
        micro_trend = "neutral"
        if recent_sh['price'] > prev_sh['price'] and recent_sl['price'] > prev_sl['price']: micro_trend = "bullish"
        elif recent_sh['price'] < prev_sh['price'] and recent_sl['price'] < prev_sl['price']: micro_trend = "bearish"
        
        signal = "neutral"
        reason = ""
        pattern_type = "none"
        
        # --- BOS (Break of Structure) - 顺势突破 ---
        # Uptrend: Break above recent SH
        if (micro_trend == "bullish" or sentiment_score >= 0) and current_close > recent_sh['price']:
            # 确认是有效突破 (Close > SH)
            # 增加回踩确认 (Pullback Confirmation) 逻辑
            # BOS 发生后，理想情况是价格回调测试了之前的阻力(现支撑)或 OB，然后再上涨
            # 这里我们只标记 BOS 发生，具体的入场时机由主逻辑控制
            signal = "buy"
            reason = f"BOS Bullish: Closed above SH ({recent_sh['price']})"
            pattern_type = "BOS"
            
        # Downtrend: Break below recent SL
        elif (micro_trend == "bearish" or sentiment_score <= 0) and current_close < recent_sl['price']:
            signal = "sell"
            reason = f"BOS Bearish: Closed below SL ({recent_sl['price']})"
            pattern_type = "BOS"
            
        # --- CHoCH (Change of Character) - 反转破坏 ---
        # 如果当前是看涨结构/趋势，但价格跌破了最近的 "Strong Low" (导致这一波上涨的起点 SL)
        # 简化: 跌破最近的 SL
        elif (micro_trend == "bullish" or sentiment_score > 0) and current_close < recent_sl['price']:
             # 这可能是一个反转信号
             signal = "sell"
             reason = f"CHoCH Bearish: Structure Broken (SL {recent_sl['price']} violated)"
             pattern_type = "CHoCH"
             
        # 如果当前是看跌结构/趋势，但价格突破了最近的 "Strong High"
        elif (micro_trend == "bearish" or sentiment_score < 0) and current_close > recent_sh['price']:
             signal = "buy"
             reason = f"CHoCH Bullish: Structure Broken (SH {recent_sh['price']} violated)"
             pattern_type = "CHoCH"
             
        return {"signal": signal, "reason": reason, "type": pattern_type, "price": current_close, "recent_sh": recent_sh['price'], "recent_sl": recent_sl['price']}

    def detect_bos(self, df):
        # Legacy method kept for compatibility, redirected to new logic internally if needed
        # Or we can keep it simple as a 'Sweep' detector.
        # Let's keep the original Sweep logic but rename reason to distinguish.
        highs = df['high'].values; lows = df['low'].values; closes = df['close'].values
        swing_high = -1; swing_low = -1
        for i in range(len(df)-4, len(df)-30, -1):
            if (highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i-3] and highs[i] > highs[i+1] and highs[i] > highs[i+2] and highs[i] > highs[i+3]): swing_high = highs[i]; break
        for i in range(len(df)-4, len(df)-30, -1):
            if (lows[i] < lows[i-1] and lows[i] < lows[i-2] and lows[i] < lows[i-3] and lows[i] < lows[i+1] and lows[i] < lows[i+2] and lows[i] < lows[i+3]): swing_low = lows[i]; break
        current_bid = closes[-1]
        if swing_high > 0 and current_bid > swing_high: return {"signal": "sell", "reason": "Liquidity Sweep (High)", "price": swing_high}
        if swing_low > 0 and current_bid < swing_low: return {"signal": "buy", "reason": "Liquidity Sweep (Low)", "price": swing_low}
        return {"signal": "neutral", "reason": ""}

class MatrixMLAnalyzer:
    def __init__(self, input_size=10, learning_rate=0.01):
        self.input_size = input_size
        self.learning_rate = learning_rate
        self.weights = np.random.randn(input_size) * np.sqrt(1 / input_size)
        self.bias = 0.0
        self.last_inputs = None
        self.last_prediction = 0.0
        
    def sigmoid(self, x): return 1 / (1 + np.exp(-x))
    def sigmoid_derivative(self, x): s = self.sigmoid(x); return s * (1 - s)
    def tanh(self, x): return np.tanh(x)
    def tanh_derivative(self, x): return 1.0 - np.tanh(x)**2

    def predict(self, tick_data):
        if len(tick_data) < self.input_size + 1: return {"signal": "neutral", "strength": 0.0, "raw_output": 0.0}
        prices = np.array([t['ask'] for t in tick_data])
        returns = np.diff(prices)
        if len(returns) < self.input_size: return {"signal": "neutral", "strength": 0.0, "raw_output": 0.0}
        features = returns[-self.input_size:]
        std = np.std(features)
        if std > 0: features = features / std
        else: features = np.zeros_like(features)
        self.last_inputs = features
        linear_output = np.dot(self.weights, features) + self.bias
        prediction = self.tanh(linear_output)
        self.last_prediction = prediction
        signal = "neutral"; strength = abs(prediction) * 100
        if prediction > 0.1: signal = "buy"
        elif prediction < -0.1: signal = "sell"
        return {"signal": signal, "strength": float(strength), "raw_output": float(prediction)}
        
    def train(self, actual_price_change):
        if self.last_inputs is None: return
        target = 1.0 if actual_price_change > 0 else -1.0
        if actual_price_change == 0: target = 0.0
        error = target - self.last_prediction
        derivative = self.tanh_derivative(self.last_prediction)
        self.weights += self.learning_rate * error * derivative * self.last_inputs
        self.bias += self.learning_rate * error * derivative
        return error

class CRTAnalyzer:
    """
    Candle Range Theory (CRT) Analyzer
    Based on identifying manipulation of previous ranges using HTF data
    """
    def __init__(self, timeframe_htf=mt5.TIMEFRAME_H1, min_manipulation_percent=5.0):
        self.timeframe_htf = timeframe_htf
        self.min_manipulation_percent = min_manipulation_percent 
        
    def analyze(self, symbol, current_price, current_time):
        try:
            # Fetch completed HTF candles (index 1 is previous completed)
            htf_rates = mt5.copy_rates_from_pos(symbol, self.timeframe_htf, 1, 2)
            if htf_rates is None or len(htf_rates) < 1: return {"signal": "neutral", "reason": "Insufficient Data"}
            
            prev_htf = htf_rates[-1] # The most recent COMPLETED candle
            range_high = prev_htf['high']
            range_low = prev_htf['low']
            range_open = prev_htf['open']
            range_close = prev_htf['close']
            
            is_bullish_range = range_close > range_open
            range_size = range_high - range_low
            if range_size == 0: return {"signal": "neutral", "reason": "Range Size 0"}
            
            curr_close = current_price['close']
            curr_high = current_price['high']
            curr_low = current_price['low']
            
            signal = "neutral"; reason = ""; strength = 0
            
            # CRT Logic: Sweep & Reclaim
            # Bullish: Price sweeps below Range Low but closes/is currently above it
            if curr_low < range_low and curr_close > range_low:
                manipulation_depth = range_low - curr_low
                manipulation_pct = (manipulation_depth / range_size) * 100
                if manipulation_pct >= self.min_manipulation_percent:
                    signal = "buy"
                    strength = min(100, 60 + manipulation_pct * 2)
                    reason = f"CRT Bullish: Swept Range Low ({range_low}) & Reclaimed (Manip: {manipulation_pct:.1f}%)"
            
            # Bearish: Price sweeps above Range High but closes/is currently below it
            elif curr_high > range_high and curr_close < range_high:
                manipulation_depth = curr_high - range_high
                manipulation_pct = (manipulation_depth / range_size) * 100
                if manipulation_pct >= self.min_manipulation_percent:
                    signal = "sell"
                    strength = min(100, 60 + manipulation_pct * 2)
                    reason = f"CRT Bearish: Swept Range High ({range_high}) & Reclaimed (Manip: {manipulation_pct:.1f}%)"
            
            if signal == "neutral":
                # Range Continuation Bias
                range_mid = (range_high + range_low) / 2
                if is_bullish_range:
                    if curr_close < range_mid: # Discount
                        signal = "buy"; strength = 40; reason = "Bullish Range (Price in Discount)"
                else:
                    if curr_close > range_mid: # Premium
                        signal = "sell"; strength = 40; reason = "Bearish Range (Price in Premium)"
                        
            return {
                "signal": signal, 
                "strength": float(strength), 
                "reason": reason, 
                "range_high": float(range_high), 
                "range_low": float(range_low),
                "manipulation_pct": float(manipulation_pct if signal in ['buy', 'sell'] and strength > 50 else 0)
            }
        except Exception as e:
            logging.error(f"CRT Error: {e}")
            return {"signal": "neutral", "reason": "CRT Analysis Error"}

class PriceEquationModel:
    def __init__(self):
        self.coeffs = [0.2752466, 0.01058082, 0.55162082, 0.03687016, 0.27721318, 0.1483476, 0.0008025]
        self.ma_fast_period = 25; self.ma_slow_period = 200; self.adx_threshold = 20.0
        self.price_history = []
    def update(self, current_price):
        self.price_history.append(current_price)
        if len(self.price_history) > 100: self.price_history.pop(0)
    def predict(self, df_history=None):
        signal = "neutral"; predicted_price = 0.0
        if df_history is None or len(df_history) < max(self.ma_fast_period, self.ma_slow_period, 14): return {"signal": "neutral", "predicted_price": 0.0}
        try:
            price_t1 = df_history['close'].iloc[-2]; price_t2 = df_history['close'].iloc[-3]; current_price = df_history['close'].iloc[-1]
            
            # Normalize inputs relative to mean of last two prices to handle scale
            scale_factor = (price_t1 + price_t2) / 2.0
            if scale_factor == 0: scale_factor = 1.0
            
            p1_norm = price_t1 / scale_factor
            p2_norm = price_t2 / scale_factor
            
            c = self.coeffs
            # Apply equation on normalized values
            pred_norm = (c[0] * p1_norm +                    
                         c[1] * (p1_norm ** 2) +             
                         c[2] * p2_norm +                    
                         c[3] * (p2_norm ** 2) +             
                         c[4] * (p1_norm - p2_norm) +       
                         c[5] * np.sin(p1_norm) +            
                         c[6])
                         
            predicted_price = pred_norm * scale_factor
            
        except IndexError: return {"signal": "neutral", "predicted_price": 0.0}
        
        closes = df_history['close']
        ma_fast = closes.rolling(window=self.ma_fast_period).mean().iloc[-1]
        ma_slow = closes.rolling(window=self.ma_slow_period).mean().iloc[-1]
        adx = self.calculate_adx(df_history)
        is_strong_trend = adx >= self.adx_threshold; is_uptrend = ma_fast > ma_slow; is_downtrend = ma_fast < ma_slow
        
        if predicted_price > current_price:
            if is_uptrend:
                if is_strong_trend: signal = "buy"
                else: signal = "buy"
            else:
                if (predicted_price - current_price) / current_price > 0.005: signal = "buy"
                else: signal = "neutral"
        elif predicted_price < current_price:
            if is_downtrend:
                if is_strong_trend: signal = "sell"
                else: signal = "sell"
            else:
                if (current_price - predicted_price) / current_price > 0.005: signal = "sell"
                else: signal = "neutral"
                
        return {"signal": signal, "predicted_price": predicted_price, "trend_strength": float(adx), "ma_fast": float(ma_fast), "ma_slow": float(ma_slow)}
    def calculate_adx(self, df, period=14):
        try:
            high = df['high']; low = df['low']; close = df['close']
            tr1 = high - low; tr2 = abs(high - close.shift(1)); tr3 = abs(low - close.shift(1))
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            up_move = high - high.shift(1); down_move = low.shift(1) - low
            plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
            minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
            tr_smooth = tr.rolling(window=period).sum()
            plus_dm_smooth = pd.Series(plus_dm).rolling(window=period).sum()
            minus_dm_smooth = pd.Series(minus_dm).rolling(window=period).sum()
            plus_di = 100 * (plus_dm_smooth / tr_smooth); minus_di = 100 * (minus_dm_smooth / tr_smooth)
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
            adx = dx.rolling(window=period).mean().iloc[-1]
            return 0.0 if np.isnan(adx) else adx
        except Exception: return 0.0

class TimeframeVisualAnalyzer:
    """
    Multi-timeframe trend visualization analyzer
    Uses Moving Averages alignment to simulate visual trend confirmation
    """
    def __init__(self):
        # M6 removed, only H1 and M15 kept as per user request
        self.timeframes = {"M15": mt5.TIMEFRAME_M15, "H1": mt5.TIMEFRAME_H1}
        
    def analyze(self, symbol, current_time):
        trends = {}; alignment_score = 0
        for tf_name, tf_const in self.timeframes.items():
            try:
                rates = mt5.copy_rates_from(symbol, tf_const, current_time, 250)
                if rates is None or len(rates) < 50: trends[tf_name] = "neutral"; continue
                df = pd.DataFrame(rates); df['close'] = df['close'].astype(float)
                
                # Use standard 20/50/200 MA for visual alignment
                ema20 = df['close'].ewm(span=20, adjust=False).mean().iloc[-1]
                ema50 = df['close'].ewm(span=50, adjust=False).mean().iloc[-1]
                ema200 = df['close'].ewm(span=200, adjust=False).mean().iloc[-1]
                
                current_close = df['close'].iloc[-1]
                
                if current_close > ema20 > ema50 > ema200: trends[tf_name] = "bullish"; alignment_score += 1
                elif current_close < ema20 < ema50 < ema200: trends[tf_name] = "bearish"; alignment_score -= 1
                elif current_close > ema20 > ema50: trends[tf_name] = "weak_bullish"; alignment_score += 0.5
                elif current_close < ema20 < ema50: trends[tf_name] = "weak_bearish"; alignment_score -= 0.5
                else: trends[tf_name] = "neutral"
            except: trends[tf_name] = "neutral"
            
        signal = "neutral"; reason = f"Trends: {trends}"
        strength = 0
        
        if alignment_score >= 2.5: 
            signal = "buy"; strength = 90; reason = f"Strong Bullish Alignment (Score {alignment_score}/3)"
        elif alignment_score >= 1.5: 
            signal = "buy"; strength = 70; reason = "Bullish Bias"
        elif alignment_score <= -2.5: 
            signal = "sell"; strength = 90; reason = f"Strong Bearish Alignment (Score {alignment_score}/3)"
        elif alignment_score <= -1.5: 
            signal = "sell"; strength = 70; reason = "Bearish Bias"
            
        return {"signal": signal, "strength": strength, "reason": reason, "details": trends}

class MTFAnalyzer:
    def __init__(self, htf1=mt5.TIMEFRAME_M15, htf2=mt5.TIMEFRAME_H1, swing_length=20):
        self.htf1 = htf1; self.htf2 = htf2; self.swing_length = swing_length
        self.demand_zones = []; self.supply_zones = []; self.last_zone_update = 0
    def analyze(self, symbol, current_price, current_time):
        dir_htf1 = self.get_candle_direction(symbol, self.htf1, 1) 
        dir_htf2 = self.get_candle_direction(symbol, self.htf2, 1)
        dir_curr = 0
        if current_price['close'] > current_price['open']: dir_curr = 1
        elif current_price['close'] < current_price['open']: dir_curr = -1
        confirmed_dir = 0
        if dir_htf1 == dir_htf2 and dir_htf1 != 0:
             if dir_curr == 0 or dir_curr == dir_htf1: confirmed_dir = dir_htf1
        if time.time() - self.last_zone_update > 900: 
            self.update_zones(symbol); self.last_zone_update = time.time()
        bid = current_price['close']
        in_demand = self.is_in_zone(bid, is_demand=True); in_supply = self.is_in_zone(bid, is_demand=False)
        signal = "neutral"; strength = 0; reason = ""
        if confirmed_dir > 0:
            if in_supply: reason = "Bullish MTF but in Supply Zone (Risk)"
            else: signal = "buy"; strength = 85 if in_demand else 70; reason = f"MTF Strong Bullish (M15+H1). {'In Demand Zone' if in_demand else ''}"
        elif confirmed_dir < 0:
            if in_demand: reason = "Bearish MTF but in Demand Zone (Risk)"
            else: signal = "sell"; strength = 85 if in_supply else 70; reason = f"MTF Strong Bearish (M15+H1). {'In Supply Zone' if in_supply else ''}"
        else:
            if dir_htf1 == dir_curr and dir_htf1 != 0: signal = "buy" if dir_htf1 > 0 else "sell"; strength = 50; reason = f"MTF Weak {signal.capitalize()} (M15 aligned only)"
            elif dir_htf2 == dir_curr and dir_htf2 != 0: signal = "buy" if dir_htf2 > 0 else "sell"; strength = 50; reason = f"MTF Weak {signal.capitalize()} (H1 aligned only)"
            else: reason = f"MTF Misaligned (M15:{dir_htf1}, H1:{dir_htf2}, Curr:{dir_curr})"
        return {"signal": signal, "strength": float(strength), "reason": reason, "htf1_dir": dir_htf1, "htf2_dir": dir_htf2}
    def get_candle_direction(self, symbol, timeframe, index=0):
        try:
            rates = mt5.copy_rates_from_pos(symbol, timeframe, index, 1)
            if rates is None or len(rates) == 0: return 0
            candle = rates[0]
            if candle['close'] > candle['open']: return 1
            elif candle['close'] < candle['open']: return -1
            return 0
        except: return 0
    def update_zones(self, symbol):
        try:
            # Changed from M6 to M15 for zone update as per user request
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 500)
            if rates is None or len(rates) < 50: return
            self.demand_zones = []; self.supply_zones = []
            tr_sum = 0
            for i in range(len(rates)-14, len(rates)): tr_sum += (rates[i]['high'] - rates[i]['low'])
            atr = tr_sum / 14 if tr_sum > 0 else 0.001
            box_width = atr * 1.0; swing_len = self.swing_length
            highs = np.array([r['high'] for r in rates]); lows = np.array([r['low'] for r in rates])
            for i in range(swing_len, len(rates) - swing_len):
                is_low = True; curr_low = lows[i]
                if np.min(lows[i-swing_len:i]) < curr_low or np.min(lows[i+1:i+swing_len+1]) < curr_low: is_low = False
                if is_low and len(self.demand_zones) < 50: self.demand_zones.append((curr_low + box_width, curr_low))
                is_high = True; curr_high = highs[i]
                if np.max(highs[i-swing_len:i]) > curr_high or np.max(highs[i+1:i+swing_len+1]) > curr_high: is_high = False
                if is_high and len(self.supply_zones) < 50: self.supply_zones.append((curr_high, curr_high - box_width))
        except: pass
    def is_in_zone(self, price, is_demand):
        tolerance = 0.0005
        zones = self.demand_zones if is_demand else self.supply_zones
        for top, bottom in zones:
            if price >= (bottom - tolerance) and price <= (top + tolerance): return True
        return False

class AdvancedMarketAnalysisAdapter(AdvancedMarketAnalysis):
    def analyze_full(self, df: pd.DataFrame, params: Dict[str, any] = None) -> Dict[str, any]:
        if df is None or len(df) < 50: return None
        params = params or {}
        try:
            indicators = self.calculate_technical_indicators(df)
            regime = self.detect_market_regime(df)
            levels = self.generate_support_resistance(df)
            risk = self.calculate_risk_metrics(df)
            signal_info = self.generate_signal_from_indicators(indicators)
            summary = self.generate_analysis_summary(df)
            ifvg = self.analyze_ifvg(df, min_gap_points=params.get('ifvg_gap', 10))
            rvgi_cci = self.analyze_rvgi_cci_strategy(df, sma_period=params.get('rvgi_sma', 10), cci_period=params.get('rvgi_cci', 14))
            
            # New Indicators
            donchian = self.calculate_donchian_channels(df, period=20)
            strict_sd = self.detect_strict_supply_demand(df)
            
            return {
                "indicators": indicators,
                "regime": regime,
                "levels": levels,
                "risk": risk,
                "signal_info": signal_info,
                "summary": summary,
                "ifvg": ifvg,
                "rvgi_cci": rvgi_cci,
                "donchian": donchian,
                "strict_supply_demand": strict_sd
            }
        except Exception as e:
            logging.error(f"Full Analysis failed: {e}")
            return None
