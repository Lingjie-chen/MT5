import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import warnings
import logging
warnings.filterwarnings('ignore')

class PEMAnalyzer:
    """
    Price Equation Model (PEM) Analyzer
    Based on PulseEquation EA logic: Polynomial Prediction + Trend Filter
    """
    def __init__(self):
        # Coefficients from MQL5 (g_coeffs)
        self.coeffs = [0.2752466, 0.01058082, 0.55162082, 0.03687016, 0.27721318, 0.1483476, 0.0008025]
        
    def predict_price(self, price_t1, price_t2):
        """
        Calculate predicted price using the polynomial equation
        """
        c = self.coeffs
        prediction = (c[0] * price_t1 +                    # Linear t-1
                      c[1] * (price_t1 ** 2) +             # Quadratic t-1
                      c[2] * price_t2 +                    # Linear t-2
                      c[3] * (price_t2 ** 2) +             # Quadratic t-2
                      c[4] * (price_t1 - price_t2) +       # Price change
                      c[5] * np.sin(price_t1) +            # Cyclic
                      c[6])                                # Constant
        return prediction

    def analyze(self, df: pd.DataFrame, ma_fast_period=108, ma_slow_period=60, adx_threshold=20) -> Dict[str, any]:
        if len(df) < max(ma_fast_period, ma_slow_period) + 5:
            return {"signal": "neutral", "strength": 0, "reason": "Insufficient Data"}
            
        # 1. Price Prediction
        # Get prices t-1 and t-2 (assuming df.iloc[-1] is current forming candle, so t-1 is -2)
        price_t1 = df['close'].iloc[-2]
        price_t2 = df['close'].iloc[-3]
        current_price = df['close'].iloc[-1] # Approximation of current Ask/Bid
        
        predicted_price = self.predict_price(price_t1, price_t2)
        
        # Raw Signal
        raw_signal = "neutral"
        if predicted_price > current_price:
            raw_signal = "buy"
        elif predicted_price < current_price:
            raw_signal = "sell"
            
        # 2. Trend Filter (ADX + MA)
        # Calculate MAs
        ma_fast = df['close'].rolling(window=ma_fast_period).mean().iloc[-2] # Completed candle
        ma_slow = df['close'].rolling(window=ma_slow_period).mean().iloc[-2]
        
        # Calculate ADX (simplified or reuse existing)
        adx = self._calculate_adx(df).iloc[-2]
        
        is_strong_trend = adx >= adx_threshold
        is_uptrend = ma_fast > ma_slow
        is_downtrend = ma_fast < ma_slow
        
        final_signal = "neutral"
        strength = 0
        reason = []
        
        if raw_signal == "buy":
            if is_strong_trend and is_uptrend:
                final_signal = "buy"
                strength = 85
                reason.append(f"PEM: Predicted {predicted_price:.4f} > Curr {current_price:.4f} + Strong Uptrend (ADX={adx:.1f})")
            else:
                reason.append(f"PEM: Raw Buy filtered (Trend mismatch)")
                
        elif raw_signal == "sell":
            if is_strong_trend and is_downtrend:
                final_signal = "sell"
                strength = 85
                reason.append(f"PEM: Predicted {predicted_price:.4f} < Curr {current_price:.4f} + Strong Downtrend (ADX={adx:.1f})")
            else:
                reason.append(f"PEM: Raw Sell filtered (Trend mismatch)")
                
        return {
            "signal": final_signal,
            "strength": strength,
            "reason": "; ".join(reason),
            "prediction": predicted_price,
            "adx": adx,
            "trend": "bullish" if is_uptrend else "bearish"
        }

    def _calculate_adx(self, df, period=14):
        highs = df['high']
        lows = df['low']
        closes = df['close']
        
        plus_dm = highs.diff()
        minus_dm = -lows.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        tr1 = highs - lows
        tr2 = abs(highs - closes.shift())
        tr3 = abs(lows - closes.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        atr = tr.rolling(period).mean()
        plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(period).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(period).mean()
        return adx

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
        point = 1.0; min_gap = min_gap_points * point # For Crypto, points are different. Assuming 1.0 for now or passed value
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

    def analyze_crt_strategy(self, df: pd.DataFrame, range_period: int = 15, confirm_period: int = 1, min_manipulation_pct: float = 5.0) -> Dict[str, any]:
        if len(df) < range_period + confirm_period + 5: return {"signal": "hold", "strength": 0, "reasons": []}
        prev_candle = df.iloc[-2]
        range_high = prev_candle['high']; range_low = prev_candle['low']
        range_open = prev_candle['open']; range_close = prev_candle['close']
        is_bullish_range = range_close > range_open
        
        current_candle = df.iloc[-1]
        current_high = current_candle['high']; current_low = current_candle['low']; current_close = current_candle['close']
        breakout = False; manipulation = False; manipulation_depth = 0.0
        range_size = range_high - range_low
        if range_size == 0: range_size = 0.0001
        
        signal = "hold"; strength = 0; reasons = []
        if is_bullish_range:
            if current_low < range_low:
                breakout = True; manipulation_depth = range_low - current_low
                pct = (manipulation_depth / range_size) * 100
                if current_close > range_low:
                    manipulation = True
                    if pct >= min_manipulation_pct: signal = "buy"; strength = 80; reasons.append(f"CRT Bullish: Downward Manipulation ({pct:.1f}%) & Reclaim")
        else:
            if current_high > range_high:
                breakout = True; manipulation_depth = current_high - range_high
                pct = (manipulation_depth / range_size) * 100
                if current_close < range_high:
                    manipulation = True
                    if pct >= min_manipulation_pct: signal = "sell"; strength = 80; reasons.append(f"CRT Bearish: Upward Manipulation ({pct:.1f}%) & Reclaim")
        
        return {"signal": signal, "strength": strength, "reasons": reasons, "range_info": {"high": range_high, "low": range_low, "direction": "bullish" if is_bullish_range else "bearish", "manipulation_pct": (manipulation_depth / range_size * 100) if breakout else 0}}

class SMCAnalyzer:
    def __init__(self):
        self.last_structure = "neutral" 
        self.ma_period = 200
        self.swing_lookback = 5
        self.atr_threshold = 0.002
        self.allow_bos = True; self.allow_ob = True; self.allow_fvg = True; self.use_sentiment = True

    def analyze(self, df: pd.DataFrame) -> Dict[str, any]:
        if len(df) < 50: return {"signal": "neutral", "structure": "neutral", "reason": "Insufficient Data"}
        
        swings = self._detect_swings(df)
        structure = self._analyze_structure(df, swings)
        ob_info = self._detect_order_blocks(df)
        fvg_info = self._detect_fvg(df)
        sweeps = self._detect_liquidity_sweeps(df, swings)
        pd_info = self._analyze_premium_discount(df, swings)
        
        signal = "neutral"; strength = 0; reasons = []
        is_bullish = structure['trend'] == 'bullish'
        is_bearish = structure['trend'] == 'bearish'
        in_discount = pd_info['zone'] == 'discount'
        in_premium = pd_info['zone'] == 'premium'
        
        if is_bullish and in_discount:
            if ob_info['signal'] == 'buy': signal = 'buy'; strength += 40; reasons.append(f"Bullish OB in Discount: {ob_info['reason']}")
            if sweeps['signal'] == 'buy': signal = 'buy'; strength += 30; reasons.append(f"Liquidity Sweep (Sell-side): {sweeps['reason']}")
            if fvg_info['signal'] == 'buy': signal = 'buy'; strength += 20; reasons.append(f"Bullish FVG Retest: {fvg_info['reason']}")
        elif is_bearish and in_premium:
            if ob_info['signal'] == 'sell': signal = 'sell'; strength += 40; reasons.append(f"Bearish OB in Premium: {ob_info['reason']}")
            if sweeps['signal'] == 'sell': signal = 'sell'; strength += 30; reasons.append(f"Liquidity Sweep (Buy-side): {sweeps['reason']}")
            if fvg_info['signal'] == 'sell': signal = 'sell'; strength += 20; reasons.append(f"Bearish FVG Retest: {fvg_info['reason']}")
                
        return {"signal": signal, "strength": strength, "structure": structure['trend'], "reason": "; ".join(reasons), "details": {"swings": swings, "ob": ob_info, "fvg": fvg_info, "sweeps": sweeps, "premium_discount": pd_info}}

    def _detect_swings(self, df):
        highs = df['high'].values; lows = df['low'].values; n = len(df)
        swing_highs = []; swing_lows = []
        for i in range(5, n-5):
            if all(highs[i] >= highs[i-j] for j in range(1, 6)) and all(highs[i] > highs[i+j] for j in range(1, 6)): swing_highs.append((i, highs[i]))
            if all(lows[i] <= lows[i-j] for j in range(1, 6)) and all(lows[i] < lows[i+j] for j in range(1, 6)): swing_lows.append((i, lows[i]))
        return {"highs": swing_highs, "lows": swing_lows}

    def _analyze_structure(self, df, swings):
        if not swings['highs'] or not swings['lows']: return {"trend": "neutral"}
        last_high = swings['highs'][-1][1]; prev_high = swings['highs'][-2][1] if len(swings['highs']) > 1 else last_high
        last_low = swings['lows'][-1][1]; prev_low = swings['lows'][-2][1] if len(swings['lows']) > 1 else last_low
        current_close = df['close'].iloc[-1]
        trend = "neutral"
        if last_high > prev_high and last_low > prev_low: trend = "bullish"
        elif last_high < prev_high and last_low < prev_low: trend = "bearish"
        if trend == "bullish" and current_close < last_low: trend = "bearish_change"
        elif trend == "bearish" and current_close > last_high: trend = "bullish_change"
        return {"trend": trend}

    def _detect_order_blocks(self, df):
        closes = df['close'].values; opens = df['open'].values; highs = df['high'].values; lows = df['low'].values; current_price = closes[-1]
        for i in range(len(df)-3, len(df)-50, -1):
            if opens[i-1] > closes[i-1]:
                if closes[i] > opens[i] and (closes[i] - opens[i]) > (opens[i-1] - closes[i-1]):
                    ob_high = highs[i-1]; ob_low = lows[i-1]; violated = False
                    for k in range(i+1, len(df)):
                        if closes[k] < ob_low: violated = True; break
                    if not violated and ob_low <= current_price <= ob_high * 1.01: return {"signal": "buy", "reason": f"Retesting Bullish OB from index {i-1}", "level": [ob_low, ob_high]}
            if opens[i-1] < closes[i-1]:
                if closes[i] < opens[i] and (opens[i] - closes[i]) > (closes[i-1] - opens[i-1]):
                    ob_high = highs[i-1]; ob_low = lows[i-1]; violated = False
                    for k in range(i+1, len(df)):
                        if closes[k] > ob_high: violated = True; break
                    if not violated and ob_low * 0.99 <= current_price <= ob_high: return {"signal": "sell", "reason": f"Retesting Bearish OB from index {i-1}", "level": [ob_low, ob_high]}
        return {"signal": "neutral", "reason": "", "level": []}

    def _detect_fvg(self, df):
        highs = df['high'].values; lows = df['low'].values; closes = df['close'].values; current_price = closes[-1]; point = 0.00001
        for i in range(len(df)-1, len(df)-20, -1):
            if lows[i] > highs[i-2]:
                gap_top = lows[i]; gap_bot = highs[i-2]; mitigated = False
                for k in range(i+1, len(df)):
                    if lows[k] < gap_top: mitigated = True
                if (not mitigated or (mitigated and current_price >= gap_bot)) and gap_bot <= current_price <= gap_top: return {"signal": "buy", "reason": f"In Bullish FVG {i}", "zone": [gap_bot, gap_top]}
            if highs[i] < lows[i-2]:
                gap_top = lows[i-2]; gap_bot = highs[i]; mitigated = False
                for k in range(i+1, len(df)):
                    if highs[k] > gap_bot: mitigated = True
                if (not mitigated or (mitigated and current_price <= gap_top)) and gap_bot <= current_price <= gap_top: return {"signal": "sell", "reason": f"In Bearish FVG {i}", "zone": [gap_bot, gap_top]}
        return {"signal": "neutral", "reason": "", "zone": []}

    def _detect_liquidity_sweeps(self, df, swings):
        if not swings['highs'] or not swings['lows']: return {"signal": "neutral"}
        current_high = df['high'].iloc[-1]; current_low = df['low'].iloc[-1]; current_close = df['close'].iloc[-1]
        last_swing_high = swings['highs'][-1][1]; last_swing_low = swings['lows'][-1][1]
        if current_high > last_swing_high and current_close < last_swing_high: return {"signal": "sell", "reason": "Buy-side Liquidity Sweep"}
        if current_low < last_swing_low and current_close > last_swing_low: return {"signal": "buy", "reason": "Sell-side Liquidity Sweep"}
        return {"signal": "neutral", "reason": ""}

    def _analyze_premium_discount(self, df, swings):
        if not swings['highs'] or not swings['lows']: return {"zone": "equilibrium"}
        recent_range_high = max(x[1] for x in swings['highs'][-3:]); recent_range_low = min(x[1] for x in swings['lows'][-3:])
        current_price = df['close'].iloc[-1]; mid_point = (recent_range_high + recent_range_low) / 2
        zone = "equilibrium"
        if current_price > mid_point: zone = "premium"
        elif current_price < mid_point: zone = "discount"
        return {"zone": zone, "range_high": recent_range_high, "range_low": recent_range_low, "equilibrium": mid_point}

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

class TimeframeVisualAnalyzer:
    """
    Multi-timeframe trend visualization analyzer
    """
    def __init__(self):
        pass
    
    def analyze(self, symbol, current_time):
        # Placeholder for visual analysis logic
        # In a real scenario, this would check trend alignment across M5, M15, H1, H4
        return {"signal": "neutral", "strength": 0, "reason": "Not implemented"}

class CRTAnalyzer:
    """
    Candle Range Theory (CRT) Analyzer
    Based on identifying manipulation of previous ranges
    """
    def __init__(self, timeframe_htf='1h'):
        self.timeframe_htf = timeframe_htf
        
    def analyze(self, symbol, current_candle, current_time):
        # Simplified CRT logic without fetching HTF data inside
        # Requires passing HTF candle or dataframe
        return {"signal": "neutral", "reason": "CRT requires HTF context"}

class PriceEquationModel(PEMAnalyzer):
    """
    Alias for PEMAnalyzer to match Gold strategy naming
    """
    def update(self, price):
        pass # PEMAnalyzer is stateless for now
        
    def predict(self, df):
        return self.analyze(df)

class MTFAnalyzer:
    """
    Multi-Timeframe Analyzer
    """
    def __init__(self, htf1='1h', htf2='4h'):
        self.htf1 = htf1
        self.htf2 = htf2
        
    def analyze(self, current_df, htf1_df, htf2_df=None):
        curr_trend = self._get_trend(current_df)
        htf1_trend = self._get_trend(htf1_df)
        
        signal = "neutral"; strength = 0; reason = ""
        
        if curr_trend == htf1_trend and curr_trend != 0: 
            signal = "buy" if curr_trend > 0 else "sell"
            strength = 70
            reason = "MTF Alignment (Curr + HTF1)"
            
            if htf2_df is not None:
                htf2_trend = self._get_trend(htf2_df)
                if htf2_trend == curr_trend:
                    strength = 90
                    reason = "Strong MTF Alignment (Curr + HTF1 + HTF2)"
                elif htf2_trend != 0:
                    strength = 50
                    reason = "Partial MTF Alignment (HTF2 Divergence)"
                    
        elif htf1_trend != 0: 
            reason = f"MTF Divergence: HTF {htf1_trend}, Curr {curr_trend}"
            
        return {"signal": signal, "strength": strength, "reason": reason, "htf_trend": htf1_trend, "curr_trend": curr_trend}
        
    def _get_trend(self, df):
        if df is None or len(df) < 50: return 0
        ema20 = df['close'].ewm(span=20).mean().iloc[-1]
        ema50 = df['close'].ewm(span=50).mean().iloc[-1]
        close = df['close'].iloc[-1]
        if close > ema20 > ema50: return 1
        if close < ema20 < ema50: return -1
        return 0

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

    def predict(self, tick_data_or_returns):
        # Compatible with both tick list (Gold) and direct returns array (Crypto)
        if isinstance(tick_data_or_returns, list) and len(tick_data_or_returns) > 0 and isinstance(tick_data_or_returns[0], dict):
             prices = np.array([t['ask'] for t in tick_data_or_returns])
             returns = np.diff(prices)
        elif isinstance(tick_data_or_returns, (np.ndarray, list, pd.Series)):
             returns = np.array(tick_data_or_returns)
        else:
             return {"signal": "neutral", "strength": 0.0, "raw_output": 0.0}

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
            return {
                "indicators": indicators,
                "regime": regime,
                "levels": levels,
                "risk": risk,
                "signal_info": signal_info,
                "summary": summary,
                "ifvg": ifvg,
                "rvgi_cci": rvgi_cci
            }
        except Exception as e:
            logging.error(f"Full Analysis failed: {e}")
            return None
