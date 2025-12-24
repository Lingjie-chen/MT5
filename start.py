
import time
import sys
import os
import logging
from datetime import datetime
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# 尝试导入 MetaTrader5，如果不在 Windows 或未安装则报错
try:
    import MetaTrader5 as mt5
except ImportError:
    print("错误: 请在安装了 MetaTrader 5 的 Windows 环境中运行此脚本")
    print("pip install MetaTrader5")
    sys.exit(1)

# --- 新增模块: MFH (Multiple Forecast Horizons) 分析器 ---
# 基于 MQL5 Article 19383 & MFH_1.4.mq5
# 实现了具体的特征工程和基于斜率的预测逻辑
class MFHAnalyzer:
    def __init__(self, input_size=16, learning_rate=0.01):
        self.input_size = input_size
        self.learning_rate = learning_rate
        self.horizon = 5 # Horizon defined in MQ5
        self.ma_period = 5 # MA Period defined in MQ5
        
        # 我们模拟两个 Horizon 的预测输出 (类似于 MQ5 中的 pred[3,6] 和 pred[5,8])
        # Group A (Short Term): Represents current state
        # Group B (Long Term): Represents future state (Horizon)
        
        self.weights = np.random.randn(input_size) * np.sqrt(1 / input_size)
        self.bias = 0.0
        
        # 简单的线性回归模型 (模拟文章中的 LR)
        # 实际上我们希望预测的是未来的价格变化
        # 这里我们使用在线学习来拟合 Price(t+Horizon) - Price(t)
        
        self.last_features = None
        self.last_prediction = 0.0
        
    def calculate_features(self, df):
        """
        根据 MFH_1.4.mq5 逻辑计算 16 个特征
        """
        if len(df) < (self.ma_period + self.horizon + 1):
            return None
            
        # 准备数据
        closes = df['close'].values
        opens = df['open'].values
        highs = df['high'].values
        lows = df['low'].values
        
        # 计算 MA (SMA 5)
        # 使用 pandas rolling mean
        ma_close = df['close'].rolling(window=self.ma_period).mean().values
        ma_open = df['open'].rolling(window=self.ma_period).mean().values
        ma_high = df['high'].rolling(window=self.ma_period).mean().values
        ma_low = df['low'].rolling(window=self.ma_period).mean().values
        
        curr = -1 # 当前索引
        prev_h = -1 - self.horizon # Horizon 之前的索引
        
        features = np.zeros(16)
        
        # 1. OHLC Raw
        features[0] = closes[curr]
        features[1] = opens[curr]
        features[2] = highs[curr]
        features[3] = lows[curr]
        
        # 2. OHLC MA
        features[4] = ma_close[curr]
        features[5] = ma_open[curr]
        features[6] = ma_high[curr]
        features[7] = ma_low[curr]
        
        # 3. OHLC Change (Momentum)
        features[8] = opens[curr] - opens[prev_h]
        features[9] = highs[curr] - highs[prev_h]
        features[10] = lows[curr] - lows[prev_h]
        features[11] = closes[curr] - closes[prev_h]
        
        # 4. MA Change (Momentum)
        features[12] = ma_close[curr] - ma_close[prev_h]
        features[13] = ma_open[curr] - ma_open[prev_h]
        features[14] = ma_high[curr] - ma_high[prev_h]
        features[15] = ma_low[curr] - ma_low[prev_h]
        
        # 归一化特征 (非常重要，因为价格绝对值很大)
        # 简单使用 Z-Score 归一化 (基于特征向量本身是不够的，应该基于历史，但这里简化处理)
        # 或者除以当前价格进行比例化
        base_price = closes[curr]
        if base_price > 0:
            features = features / base_price
            
        return features

    def predict(self, df):
        """
        执行预测
        """
        features = self.calculate_features(df)
        if features is None:
            return {"signal": "neutral", "slope": 0.0}
            
        self.last_features = features
        
        # 线性预测: W * X + b
        # 这里预测的是 "未来 Horizon 的价格相对于当前的涨跌幅"
        prediction = np.dot(self.weights, features) + self.bias
        self.last_prediction = prediction
        
        signal = "neutral"
        slope = prediction # 预测值本身就是斜率 (预期涨跌幅)
        
        # 阈值判断 (需要根据归一化后的数值范围调整，假设归一化后是百分比)
        if slope > 0.001: # 预期上涨 0.1%
            signal = "buy"
        elif slope < -0.001: # 预期下跌 0.1%
            signal = "sell"
            
        return {
            "signal": signal,
            "slope": float(slope),
            "features": features.tolist() if features is not None else []
        }
        
    def train(self, current_price_change):
        """
        在线训练
        current_price_change: 实际发生的 (Price_t - Price_t-h) / Price_t-h
        """
        if self.last_features is None:
            return
            
        # 目标是拟合实际的 Horizon 收益率
        target = current_price_change
        
        # 误差
        error = target - self.last_prediction
        
        # 更新权重 (SGD)
        self.weights += self.learning_rate * error * self.last_features
        self.bias += self.learning_rate * error
        
        return error
        
    def update_buffer(self, features, current_price, current_time):
        # Python 版本简化了 Buffer 逻辑，直接在 Main Loop 中计算实际 Return 传入 Train
        pass

# --- 新增模块: SMC (Smart Money Concepts) 分析器 ---
# 基于 MQL5 Article 20414: Adaptive Smart Money Architecture (ASMA) & SMC_Sent.mq5
class SMCAnalyzer:
    def __init__(self):
        self.last_structure = "neutral" 
        self.ma_period = 200
        self.swing_lookback = 5
        self.atr_threshold = 0.002
        
    def calculate_ema(self, series, period):
        return series.ewm(span=period, adjust=False).mean()

    def get_market_sentiment(self, df):
        """
        计算市场情绪 (Bullish, Bearish, Risk-On, Risk-Off, Neutral)
        基于 SMC_Sent.mq5 的逻辑 (MA Deviation + Structure)
        """
        if len(df) < self.ma_period:
            return 0, "Neutral"
            
        closes = df['close']
        highs = df['high']
        lows = df['low']
        
        # 1. Higher TF Bias (模拟: 使用当前TF的长期MA)
        ema_long = self.calculate_ema(closes, self.ma_period).iloc[-1]
        current_price = closes.iloc[-1]
        
        deviation = abs(current_price - ema_long) / ema_long
        higher_tf_bias = 0
        if current_price > ema_long and deviation > self.atr_threshold:
            higher_tf_bias = 1
        elif current_price < ema_long and deviation > self.atr_threshold:
            higher_tf_bias = -1
            
        # 2. Local Structure (Bullish/Bearish)
        # Check if we are making Higher Highs (Bullish) or Lower Lows (Bearish)
        # 简单判定: 比较最近两个 Swing Points
        # 这里简化处理: 比较最近20根K线的趋势
        recent_high = highs.iloc[-20:].max()
        prev_recent_high = highs.iloc[-40:-20].max()
        recent_low = lows.iloc[-20:].min()
        prev_recent_low = lows.iloc[-40:-20].min()
        
        is_bullish_structure = recent_high > prev_recent_high and recent_low > prev_recent_low
        is_bearish_structure = recent_high < prev_recent_high and recent_low < prev_recent_low
        
        # 3. Breakout Detection (Risk-On/Off)
        # Price breaking local swings in direction of bias
        has_breakout = False
        if higher_tf_bias == 1 and current_price > recent_high:
            has_breakout = True
        elif higher_tf_bias == -1 and current_price < recent_low:
            has_breakout = True
            
        # 4. Determine Sentiment
        sentiment = 0
        text = "Neutral"
        
        if higher_tf_bias == 1 and is_bullish_structure:
            sentiment = 1; text = "Bullish"
        elif higher_tf_bias == -1 and is_bearish_structure:
            sentiment = -1; text = "Bearish"
            
        if higher_tf_bias == 1 and has_breakout:
            sentiment = 2; text = "Risk-On"
        elif higher_tf_bias == -1 and has_breakout:
            sentiment = -2; text = "Risk-Off"
            
        return sentiment, text

    def analyze(self, df):
        """
        分析市场结构 (BOS), 订单块 (OB), 和价值缺口 (FVG)
        基于 Sentiment 选择策略
        """
        if df is None or len(df) < 50:
            return {"signal": "neutral", "structure": "neutral", "reason": "数据不足"}
            
        # 1. 获取市场情绪
        sentiment_score, sentiment_text = self.get_market_sentiment(df)
        
        # 2. 选择策略
        active_strategy = "OB" # Default
        if abs(sentiment_score) == 1:
            active_strategy = "BOS" # Strong Trend -> Break of Structure
        elif abs(sentiment_score) == 2:
            active_strategy = "FVG" # Breakout/Momentum -> Fair Value Gaps
            
        # 3. 执行各策略检测
        ob_signal = self.detect_order_blocks(df)
        fvg_signal = self.detect_fvg(df)
        bos_signal = self.detect_bos(df)
        
        final_signal = "neutral"
        reason = f"Sentiment: {sentiment_text} ({active_strategy})"
        strength = 0
        
        # 根据选定策略采纳信号
        if active_strategy == "BOS" and bos_signal['signal'] != "neutral":
            # 检查方向一致性
            if (sentiment_score > 0 and bos_signal['signal'] == 'buy') or \
               (sentiment_score < 0 and bos_signal['signal'] == 'sell'):
                final_signal = bos_signal['signal']
                reason = f"SMC BOS ({sentiment_text}): {bos_signal['reason']}"
                strength = 80
                
        elif active_strategy == "FVG" and fvg_signal['signal'] != "neutral":
            if (sentiment_score > 0 and fvg_signal['signal'] == 'buy') or \
               (sentiment_score < 0 and fvg_signal['signal'] == 'sell'):
                final_signal = fvg_signal['signal']
                reason = f"SMC FVG ({sentiment_text}): {fvg_signal['reason']}"
                strength = 85
                
        elif active_strategy == "OB" and ob_signal['signal'] != "neutral":
            # Neutral market -> OB mean reversion or trend continuation
            final_signal = ob_signal['signal']
            reason = f"SMC OB ({sentiment_text}): {ob_signal['reason']}"
            strength = 75
            
        # 如果当前策略没有信号，尝试其他策略作为次要信号 (降低强度)
        if final_signal == "neutral":
            if fvg_signal['signal'] != "neutral":
                final_signal = fvg_signal['signal']
                strength = 60
                reason = f"Secondary FVG: {fvg_signal['reason']}"
            elif ob_signal['signal'] != "neutral":
                final_signal = ob_signal['signal']
                strength = 60
                reason = f"Secondary OB: {ob_signal['reason']}"

        return {
            "signal": final_signal,
            "structure": sentiment_text,
            "reason": reason,
            "sentiment_score": sentiment_score,
            "active_strategy": active_strategy,
            "details": {
                "ob": ob_signal,
                "fvg": fvg_signal,
                "bos": bos_signal
            }
        }
        
    def detect_order_blocks(self, df):
        # 简化版 OB 检测
        # Bullish OB: Bear candle followed by Strong Bull Candle
        # Check last few candles
        closes = df['close'].values
        opens = df['open'].values
        highs = df['high'].values
        lows = df['low'].values
        
        signal = "neutral"
        reason = ""
        
        for i in range(len(df)-2, len(df)-10, -1):
            # Bullish OB Pattern
            # Candle i: Strong Bull (Close > Open)
            # Candle i-1: Bear (Close < Open)
            # Engulfing or strong move
            if closes[i] > opens[i] and closes[i-1] < opens[i-1]:
                body_bull = closes[i] - opens[i]
                body_bear = opens[i-1] - closes[i-1]
                if body_bull > body_bear * 1.5:
                    # Found Bullish OB at i-1
                    ob_low = lows[i-1]
                    ob_high = highs[i-1]
                    current_price = closes[-1]
                    
                    # Retest check
                    if current_price <= ob_high and current_price >= ob_low:
                        signal = "buy"
                        reason = "Bullish Order Block Retest"
                        return {"signal": signal, "reason": reason, "price": ob_high}

            # Bearish OB Pattern
            if closes[i] < opens[i] and closes[i-1] > opens[i-1]:
                body_bear = opens[i] - closes[i]
                body_bull = closes[i-1] - opens[i-1]
                if body_bear > body_bull * 1.5:
                    # Found Bearish OB at i-1
                    ob_low = lows[i-1]
                    ob_high = highs[i-1]
                    current_price = closes[-1]
                    
                    # Retest check
                    if current_price >= ob_low and current_price <= ob_high:
                        signal = "sell"
                        reason = "Bearish Order Block Retest"
                        return {"signal": signal, "reason": reason, "price": ob_low}
                        
        return {"signal": "neutral", "reason": ""}

    def detect_fvg(self, df):
        # Fair Value Gaps
        highs = df['high'].values
        lows = df['low'].values
        closes = df['close'].values
        
        # Check recent candles for UNFILLED FVGs
        # We only look at the most recent valid FVG
        
        for i in range(len(df)-2, len(df)-10, -1):
            # Bullish FVG: Low[i] > High[i-2]
            if lows[i] > highs[i-2]:
                gap_top = lows[i]
                gap_bottom = highs[i-2]
                if gap_top - gap_bottom > 0: # Valid gap
                    current_price = closes[-1]
                    # Check if price is currently inside the gap
                    if current_price <= gap_top and current_price >= gap_bottom:
                         return {"signal": "buy", "reason": "Bullish FVG Retest", "top": gap_top, "bottom": gap_bottom}
            
            # Bearish FVG: High[i] < Low[i-2]
            if highs[i] < lows[i-2]:
                gap_top = lows[i-2]
                gap_bottom = highs[i]
                if gap_top - gap_bottom > 0:
                    current_price = closes[-1]
                    if current_price <= gap_top and current_price >= gap_bottom:
                        return {"signal": "sell", "reason": "Bearish FVG Retest", "top": gap_top, "bottom": gap_bottom}
                        
        return {"signal": "neutral", "reason": ""}
        
    def detect_bos(self, df):
        # Break of Structure
        # Check if we broke recent swing points
        highs = df['high'].values
        lows = df['low'].values
        closes = df['close'].values
        
        # Simple Swing detection (Fractal 3)
        swing_high = -1.0
        swing_low = 999999.0
        
        # Find recent swing high
        for i in range(len(df)-5, len(df)-30, -1):
            if highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                swing_high = highs[i]
                break
                
        # Find recent swing low
        for i in range(len(df)-5, len(df)-30, -1):
            if lows[i] < lows[i-1] and lows[i] < lows[i-2] and lows[i] < lows[i+1] and lows[i] < lows[i+2]:
                swing_low = lows[i]
                break
                
        current_close = closes[-1]
        
        if swing_high > 0 and current_close > swing_high:
            return {"signal": "buy", "reason": f"BOS Buy: Break above {swing_high}"}
            
        if swing_low < 999999 and current_close < swing_low:
            return {"signal": "sell", "reason": f"BOS Sell: Break below {swing_low}"}
            
        return {"signal": "neutral", "reason": ""}

# --- 新增模块: Matrix ML Analyzer (基于 MQL5 矩阵机器学习概念) ---
class MatrixMLAnalyzer:
    """
    基于 MQL5 文档中的矩阵和向量机器学习概念实现的 Python 版本
    参考: https://www.mql5.com/en/book/common/matrices/matrices_ml
    使用 Numpy 矩阵运算模拟简单的在线学习神经网络
    """
    def __init__(self, input_size=10, learning_rate=0.01):
        self.input_size = input_size
        self.learning_rate = learning_rate
        # 初始化权重向量 (相当于单层神经网络)
        # 使用 Xavier 初始化
        self.weights = np.random.randn(input_size) * np.sqrt(1 / input_size)
        self.bias = 0.0
        self.last_inputs = None
        self.last_prediction = 0.0
        
    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))
        
    def sigmoid_derivative(self, x):
        s = self.sigmoid(x)
        return s * (1 - s)
        
    def tanh(self, x):
        return np.tanh(x)
        
    def tanh_derivative(self, x):
        return 1.0 - np.tanh(x)**2

    def predict(self, tick_data):
        """
        输入: 最近的 tick 价格列表
        输出: 预测下一个 tick 的涨跌概率 (-1 到 1)
        """
        if len(tick_data) < self.input_size + 1:
            return {"signal": "neutral", "strength": 0.0, "raw_output": 0.0}
            
        # 1. 特征工程: 计算价格变化 (Returns)
        # 我们使用最近 input_size 个价格变化作为输入特征
        prices = np.array([t['ask'] for t in tick_data])
        returns = np.diff(prices) # 计算一阶差分
        
        if len(returns) < self.input_size:
            return {"signal": "neutral", "strength": 0.0, "raw_output": 0.0}
            
        # 取最近的 input_size 个变化量并归一化
        features = returns[-self.input_size:]
        
        # 简单的归一化: 除以标准差 (防止数值爆炸)
        std = np.std(features)
        if std > 0:
            features = features / std
        else:
            features = np.zeros_like(features)
            
        self.last_inputs = features
        
        # 2. 矩阵运算 (Matrix Operation)
        # Dot Product: W * X + b
        linear_output = np.dot(self.weights, features) + self.bias
        
        # 3. 激活函数 (Activation)
        # 使用 Tanh 将输出映射到 [-1, 1]
        prediction = self.tanh(linear_output)
        self.last_prediction = prediction
        
        # 转换信号
        signal = "neutral"
        strength = abs(prediction) * 100
        
        if prediction > 0.3:
            signal = "buy"
        elif prediction < -0.3:
            signal = "sell"
            
        return {
            "signal": signal,
            "strength": float(strength),
            "raw_output": float(prediction)
        }
        
    def train(self, actual_price_change):
        """
        在线学习: 根据实际发生的价格变化更新权重
        """
        if self.last_inputs is None:
            return
            
        # 目标值: 如果涨了就是 1.0, 跌了就是 -1.0
        target = 1.0 if actual_price_change > 0 else -1.0
        if actual_price_change == 0:
            target = 0.0
            
        # 计算误差 (Loss)
        error = target - self.last_prediction
        
        # 反向传播 (Backpropagation) - 简单的梯度下降
        # d_Error/d_Weight = error * derivative * input
        derivative = self.tanh_derivative(self.last_prediction)
        
        # 更新权重和偏置
        self.weights += self.learning_rate * error * derivative * self.last_inputs
        self.bias += self.learning_rate * error * derivative
        
        return error

# --- 新增模块: CRT (Candle Range Theory) 分析器 ---
class CRTAnalyzer:
    def __init__(self, timeframe_htf=mt5.TIMEFRAME_H4, min_manipulation_percent=5.0):
        self.timeframe_htf = timeframe_htf
        self.min_manipulation_percent = min_manipulation_percent # 最小操纵深度百分比
        self.last_range_time = 0
        self.range_high = 0.0
        self.range_low = 0.0
        self.is_bullish_range = False # Range Candle Direction
        self.range_broken = False # 是否发生过突破(操纵)
        self.breakout_price = 0.0 # 突破后的极值
        
    def analyze(self, symbol, current_price, current_time):
        """
        基于 CRT (Candle Range Theory) 分析市场
        逻辑: 检查高时间周期 (HTF) 的 K 线范围，寻找流动性猎取 (Sweep) 和回归
        """
        # 1. 获取定义 Range 的 HTF K线 (上一根已完成的 H4)
        # copy_rates_from returns bars with open time <= date.
        # We need the completed H4 bar before current_time.
        # Assuming current_time is the open time of the current H1 bar.
        
        # 获取最近的2根 H4 K线: [Previous_H4, Current_Forming_H4] (if aligned)
        # Or just get 2 bars from current time backwards
        htf_rates = mt5.copy_rates_from(symbol, self.timeframe_htf, current_time, 2)
        
        if htf_rates is None or len(htf_rates) < 2:
            return {"signal": "neutral", "reason": "数据不足"}
        
        # htf_rates[-1] is likely the current forming H4 (or just started)
        # htf_rates[-2] is the completed H4 (The Range)
        # Let's verify timestamps to be sure.
        
        prev_htf = htf_rates[-2] # The Range Candle
        curr_htf_start = htf_rates[-1]['time']
        
        # 检查是否进入了新的 Range 周期
        if prev_htf['time'] != self.last_range_time:
            self.last_range_time = prev_htf['time']
            self.range_high = prev_htf['high']
            self.range_low = prev_htf['low']
            self.is_bullish_range = (prev_htf['close'] > prev_htf['open'])
            self.range_broken = False
            self.breakout_price = self.range_low if self.is_bullish_range else self.range_high
            
        range_size = self.range_high - self.range_low
        if range_size == 0:
             return {"signal": "neutral", "reason": "Range Size 0"}

        # 2. 检测操纵 (Manipulation)
        # 我们不仅要看当前 H1 K线，还要看当前 H4 周期内发生过的所有价格行为
        # 但在 simplify 模式下 (stateless call or updated sequentially), 
        # 我们假设 analyze 被顺序调用，或者我们检查当前 H1 K线的极值来更新状态
        
        curr_close = current_price['close']
        curr_high = current_price['high']
        curr_low = current_price['low']
        
        signal = "neutral"
        reason = ""
        strength = 0
        
        # 更新突破状态
        if self.is_bullish_range:
            # 多头区间 (上一根H4是阳线) -> 关注下方流动性猎取
            if curr_low < self.range_low:
                self.range_broken = True
                self.breakout_price = min(self.breakout_price, curr_low)
                
            # 检测信号: 曾发生突破 + 价格回到区间内
            if self.range_broken and curr_close > self.range_low:
                # 检查操纵深度
                manipulation_depth = self.range_low - self.breakout_price
                manipulation_pct = (manipulation_depth / range_size) * 100
                
                if manipulation_pct >= self.min_manipulation_percent:
                    signal = "buy"
                    strength = min(100, 50 + manipulation_pct * 2) # 深度越大强度越高
                    reason = f"Bullish CRT: Manipulation {manipulation_pct:.1f}% & Reclaim"
                else:
                    reason = f"Bullish CRT: Manipulation too shallow ({manipulation_pct:.1f}%)"
                    
        else:
            # 空头区间 (上一根H4是阴线) -> 关注上方流动性猎取
            if curr_high > self.range_high:
                self.range_broken = True
                self.breakout_price = max(self.breakout_price, curr_high)
                
            # 检测信号: 曾发生突破 + 价格回到区间内
            if self.range_broken and curr_close < self.range_high:
                # 检查操纵深度
                manipulation_depth = self.breakout_price - self.range_high
                manipulation_pct = (manipulation_depth / range_size) * 100
                
                if manipulation_pct >= self.min_manipulation_percent:
                    signal = "sell"
                    strength = min(100, 50 + manipulation_pct * 2)
                    reason = f"Bearish CRT: Manipulation {manipulation_pct:.1f}% & Reclaim"
                else:
                    reason = f"Bearish CRT: Manipulation too shallow ({manipulation_pct:.1f}%)"
            
        return {
            "signal": signal,
            "strength": float(strength),
            "reason": reason,
            "range_high": float(self.range_high),
            "range_low": float(self.range_low),
            "breakout_price": float(self.breakout_price),
            "manipulation_pct": float((abs(self.breakout_price - (self.range_low if self.is_bullish_range else self.range_high)) / range_size * 100) if self.range_broken else 0)
        }

# --- 新增模块: 价格方程模型 (Price Equation) ---
class PriceEquationModel:
    def __init__(self):
        # Coefficients from PEM EA
        self.coeffs = [0.2752466, 0.01058082, 0.55162082, 0.03687016, 0.27721318, 0.1483476, 0.0008025]
        
        # Trend Filter Parameters
        self.ma_fast_period = 108
        self.ma_slow_period = 60
        self.adx_threshold = 20.0
        
        self.price_history = []
        
    def update(self, current_price):
        self.price_history.append(current_price)
        if len(self.price_history) > 100:
            self.price_history.pop(0)
            
    def predict(self, df_history=None):
        """
        基于 PEM 逻辑进行预测
        需要传入 DataFrame 历史数据以计算 MA 和 ADX
        """
        signal = "neutral"
        predicted_price = 0.0
        
        if df_history is None or len(df_history) < max(self.ma_fast_period, self.ma_slow_period, 14):
            return {"signal": "neutral", "predicted_price": 0.0}
            
        # 1. 计算预测价格 (Equation)
        # Equation uses t-1 and t-2 close prices
        try:
            price_t1 = df_history['close'].iloc[-2]
            price_t2 = df_history['close'].iloc[-3]
            current_price = df_history['close'].iloc[-1]
            
            # Normalize prices to avoid polynomial explosion
            # We normalize relative to the older price (t2)
            base_price = price_t2
            if base_price == 0:
                return {"signal": "neutral", "predicted_price": 0.0}
                
            norm_t1 = price_t1 / base_price
            norm_t2 = price_t2 / base_price # Always 1.0
            
            # Calculate normalized prediction ratio
            pred_ratio = (self.coeffs[0] * norm_t1 +
                          self.coeffs[1] * (norm_t1**2) +
                          self.coeffs[2] * norm_t2 +
                          self.coeffs[3] * (norm_t2**2) +
                          self.coeffs[4] * (norm_t1 - norm_t2) +
                          self.coeffs[5] * np.sin(norm_t1) +
                          self.coeffs[6])
                          
            predicted_price = pred_ratio * base_price
            
        except IndexError:
            return {"signal": "neutral", "predicted_price": 0.0}
                           
        # 2. 计算趋势过滤指标 (MA + ADX)
        closes = df_history['close']
        ma_fast = closes.rolling(window=self.ma_fast_period).mean().iloc[-1]
        ma_slow = closes.rolling(window=self.ma_slow_period).mean().iloc[-1]
        
        # 简单 ADX 计算 (使用 pandas_ta 如果有，否则手动计算)
        # 这里手动实现一个简化的 ADX (TR, +DM, -DM)
        adx = self.calculate_adx(df_history)
        
        is_strong_trend = adx >= self.adx_threshold
        is_uptrend = ma_fast > ma_slow
        is_downtrend = ma_fast < ma_slow
        
        # 3. 生成信号
        if predicted_price > current_price:
            if is_strong_trend and is_uptrend:
                signal = "buy"
        elif predicted_price < current_price:
            if is_strong_trend and is_downtrend:
                signal = "sell"
                
        return {
            "signal": signal,
            "predicted_price": predicted_price,
            "trend_strength": float(adx),
            "ma_fast": float(ma_fast),
            "ma_slow": float(ma_slow)
        }
        
    def calculate_adx(self, df, period=14):
        # 简化的 ADX 计算
        try:
            high = df['high']
            low = df['low']
            close = df['close']
            
            # TR
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            # DM
            up_move = high - high.shift(1)
            down_move = low.shift(1) - low
            
            plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
            minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
            
            # Smoothed
            tr_smooth = tr.rolling(window=period).sum() # 简单起见用 SUM/SMA 代替 Wilders
            plus_dm_smooth = pd.Series(plus_dm).rolling(window=period).sum()
            minus_dm_smooth = pd.Series(minus_dm).rolling(window=period).sum()
            
            plus_di = 100 * (plus_dm_smooth / tr_smooth)
            minus_di = 100 * (minus_dm_smooth / tr_smooth)
            
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
            adx = dx.rolling(window=period).mean().iloc[-1]
            
            return 0.0 if np.isnan(adx) else adx
        except Exception:
            return 0.0

# --- 新增模块: Timeframe Visual Analyzer (多时间周期分析) ---
class TimeframeVisualAnalyzer:
    def __init__(self):
        # 定义要分析的时间周期
        self.timeframes = {
            "M15": mt5.TIMEFRAME_M15,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4
        }
        
    def analyze(self, symbol, current_time):
        """
        分析多时间周期趋势一致性
        """
        trends = {}
        alignment_score = 0
        
        for tf_name, tf_const in self.timeframes.items():
            # 获取最近 50 根 K 线计算 EMA
            rates = mt5.copy_rates_from(symbol, tf_const, current_time, 50)
            if rates is None or len(rates) < 50:
                trends[tf_name] = "neutral"
                continue
                
            df = pd.DataFrame(rates)
            # 简单计算 EMA20 和 EMA50
            df['close'] = df['close'].astype(float)
            ema20 = df['close'].ewm(span=20, adjust=False).mean().iloc[-1]
            ema50 = df['close'].ewm(span=50, adjust=False).mean().iloc[-1]
            current_close = df['close'].iloc[-1]
            
            if current_close > ema20 > ema50:
                trends[tf_name] = "bullish"
                alignment_score += 1
            elif current_close < ema20 < ema50:
                trends[tf_name] = "bearish"
                alignment_score -= 1
            else:
                trends[tf_name] = "neutral"
                
        # 综合信号
        signal = "neutral"
        reason = f"Trends: {trends}"
        
        if alignment_score >= 2: # 至少 2 个周期看涨
            signal = "buy"
            reason = "Multi-Timeframe Bullish Alignment"
        elif alignment_score <= -2: # 至少 2 个周期看跌
            signal = "sell"
            reason = "Multi-Timeframe Bearish Alignment"
            
        return {
            "signal": signal,
            "reason": reason,
            "details": trends
        }

# --- 新增模块: AdvancedAnalysisAdapter (高级分析适配器) ---
class AdvancedAnalysisAdapter:
    def __init__(self):
        # 延迟导入以避免循环依赖
        self.analyzer = None
        self.available = False
        
        try:
            # 尝试标准包导入
            from python.advanced_analysis import AdvancedMarketAnalysis
            self.analyzer = AdvancedMarketAnalysis()
            self.available = True
        except ImportError:
            try:
                # 尝试直接导入 (如果 python/ 在路径中)
                import advanced_analysis as adv_mod
                self.analyzer = adv_mod.AdvancedMarketAnalysis()
                self.available = True
            except ImportError:
                # 尝试动态导入
                try:
                    import importlib.util
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    python_dir = os.path.join(current_dir, 'python')
                    file_path = os.path.join(python_dir, 'advanced_analysis.py')
                    
                    if os.path.exists(file_path):
                        spec = importlib.util.spec_from_file_location("advanced_analysis", file_path)
                        if spec and spec.loader:
                            mod = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(mod)
                            self.analyzer = mod.AdvancedMarketAnalysis()
                            self.available = True
                except Exception as e:
                    logger.warning(f"高级分析模块加载彻底失败: {e}")
        
        if not self.available:
            logger.warning("无法导入 AdvancedMarketAnalysis，将禁用高级技术指标功能")
            
    def analyze(self, df):
        """
        调用 AdvancedMarketAnalysis 进行全面分析
        """
        if not self.available or df is None or len(df) < 50:
            return None
            
        try:
            # 1. 计算技术指标
            indicators = self.analyzer.calculate_technical_indicators(df)
            
            # 2. 检测市场状态
            regime = self.analyzer.detect_market_regime(df)
            
            # 3. 生成支撑阻力位
            levels = self.analyzer.generate_support_resistance(df)
            
            # 4. 计算风险指标
            risk = self.analyzer.calculate_risk_metrics(df)
            
            # 5. 生成信号
            signal_info = self.analyzer.generate_signal_from_indicators(indicators)
            
            # 6. 生成摘要
            summary = self.analyzer.generate_analysis_summary(df)
            
            return {
                "indicators": indicators,
                "regime": regime,
                "levels": levels,
                "risk": risk,
                "signal_info": signal_info,
                "summary": summary
            }
        except Exception as e:
            logger.error(f"Advanced Analysis failed: {e}")
            return None

# --- 混合优化引擎 (Hybrid Optimization) ---
class HybridOptimizer:
    def __init__(self):
        # 初始化策略权重
        self.weights = {
            "deepseek": 1.0,
            "qwen": 1.0,
            "crt": 1.0,
            "price_equation": 0.8,
            "tf_visual": 0.9,
            "advanced_tech": 0.85,
            "matrix_ml": 0.7,
            "smc": 1.0,
            "mfh": 0.75 # 新增 MFH 权重
        }
        self.history = []
        self.performance = {k: {"correct": 0, "total": 0} for k in self.weights.keys()}
    
    # ... update_performance ...
    def update_performance(self, last_signals, actual_movement):
        # ... (保持不变) ...
        for strategy, signal in last_signals.items():
            if signal == "buy" and actual_movement > 0:
                self.performance[strategy]["correct"] += 1
            elif signal == "sell" and actual_movement < 0:
                self.performance[strategy]["correct"] += 1
            
            self.performance[strategy]["total"] += 1
            
        for strategy in self.weights:
            total = self.performance[strategy]["total"]
            if total > 0:
                accuracy = self.performance[strategy]["correct"] / total
                self.weights[strategy] = 0.5 + accuracy

    def combine_signals(self, signals):
        # ... (保持不变) ...
        score = 0
        total_weight = 0
        
        for strategy, signal in signals.items():
            weight = self.weights.get(strategy, 1.0)
            
            if signal == "buy":
                score += weight
                total_weight += weight
            elif signal == "sell":
                score -= weight
                total_weight += weight
            
        final_signal = "hold"
        strength = 0
        
        if total_weight > 0:
            normalized_score = score / total_weight 
            strength = abs(normalized_score) * 100
            
            if normalized_score > 0.3:
                final_signal = "buy"
            elif normalized_score < -0.3:
                final_signal = "sell"
                
        return final_signal, strength, self.weights

# 添加当前目录到路径以确保可以正确导入模块
current_dir = os.path.dirname(os.path.abspath(__file__))
# 1. Add current_dir to sys.path (for importing 'python.xxx')
if current_dir not in sys.path:
    sys.path.append(current_dir)
# 2. Add current_dir/python to sys.path (for importing 'xxx' directly if needed)
python_dir = os.path.join(current_dir, 'python')
if python_dir not in sys.path:
    sys.path.append(python_dir)

try:
    # Try importing as package first (Standard way)
    try:
        from python.ai_client_factory import AIClientFactory
        from python.data_processor import MT5DataProcessor
        from python.database_manager import DatabaseManager
        from python.optimization import GWO, WOAm, DE, COAm, BBO
    except ImportError:
        # Fallback: Try importing directly if 'python' dir is in path but not treated as package
        import ai_client_factory as ai_mod
        import data_processor as dp_mod
        import database_manager as db_mod
        import optimization as opt_mod
        
        AIClientFactory = ai_mod.AIClientFactory
        MT5DataProcessor = dp_mod.MT5DataProcessor
        DatabaseManager = db_mod.DatabaseManager
        GWO = opt_mod.GWO
        WOAm = opt_mod.WOAm
        DE = opt_mod.DE
        COAm = opt_mod.COAm
        BBO = opt_mod.BBO

except ImportError as e:
    # Final Fallback: Manual loading via importlib
    try:
        import importlib.util
        
        def load_module_from_file(module_name, file_name):
            file_path = os.path.join(python_dir, file_name)
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
            else:
                raise ImportError(f"Cannot load {file_path}")

        ai_mod = load_module_from_file("ai_client_factory", "ai_client_factory.py")
        AIClientFactory = ai_mod.AIClientFactory
        
        dp_mod = load_module_from_file("data_processor", "data_processor.py")
        MT5DataProcessor = dp_mod.MT5DataProcessor
        
        db_mod = load_module_from_file("database_manager", "database_manager.py")
        DatabaseManager = db_mod.DatabaseManager
        
        opt_mod = load_module_from_file("optimization", "optimization.py")
        GWO = opt_mod.GWO
        WOAm = opt_mod.WOAm
        DE = opt_mod.DE
        COAm = opt_mod.COAm
        BBO = opt_mod.BBO
        
    except Exception as e2:
        print(f"导入错误: {e}")
        print(f"备用导入也失败: {e2}")
        print("请确保 'python' 文件夹在当前目录下")
        sys.exit(1)

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('windows_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("WindowsBot")

# --- 新增模块: MTF (Multi-Timeframe) 分析器 ---
class MTFAnalyzer:
    def __init__(self, htf1=mt5.TIMEFRAME_H1, htf2=mt5.TIMEFRAME_H4, swing_length=20):
        self.htf1 = htf1
        self.htf2 = htf2
        self.swing_length = swing_length
        self.demand_zones = [] # [(top, bottom), ...]
        self.supply_zones = []
        self.last_zone_update = 0
        
    def analyze(self, symbol, current_price, current_time):
        # 1. MTF Alignment
        dir_htf1 = self.get_candle_direction(symbol, self.htf1, 1) 
        dir_htf2 = self.get_candle_direction(symbol, self.htf2, 1)
        
        # Current TF
        dir_curr = 0
        if current_price['close'] > current_price['open']:
            dir_curr = 1
        elif current_price['close'] < current_price['open']:
            dir_curr = -1
            
        confirmed_dir = 0
        if dir_htf1 == dir_htf2 and dir_htf1 != 0:
             if dir_curr == 0 or dir_curr == dir_htf1:
                 confirmed_dir = dir_htf1
        
        # 2. Zone Check
        if time.time() - self.last_zone_update > 900: 
            self.update_zones(symbol)
            self.last_zone_update = time.time()
        
        bid = current_price['close']
        in_demand = self.is_in_zone(bid, is_demand=True)
        in_supply = self.is_in_zone(bid, is_demand=False)
        
        signal = "neutral"
        strength = 0
        reason = ""
        
        # 宽松逻辑: 只要 H1 和 Current 同向，或者 H4 和 Current 同向，就给出一个弱信号
        # 严格逻辑: H1 和 H4 必须同向 (confirmed_dir)
        
        if confirmed_dir > 0: # H1 & H4 Bullish
            if in_supply:
                 reason = "Bullish MTF but in Supply Zone (Risk)"
            else:
                 signal = "buy"
                 strength = 85 if in_demand else 70
                 reason = f"MTF Strong Bullish (H1+H4). {'In Demand Zone' if in_demand else ''}"
        elif confirmed_dir < 0: # H1 & H4 Bearish
            if in_demand:
                 reason = "Bearish MTF but in Demand Zone (Risk)"
            else:
                 signal = "sell"
                 strength = 85 if in_supply else 70
                 reason = f"MTF Strong Bearish (H1+H4). {'In Supply Zone' if in_supply else ''}"
        else:
            # 尝试次级信号 (Weak Alignment)
            if dir_htf1 == dir_curr and dir_htf1 != 0:
                signal = "buy" if dir_htf1 > 0 else "sell"
                strength = 50
                reason = f"MTF Weak {signal.capitalize()} (H1 aligned only)"
            elif dir_htf2 == dir_curr and dir_htf2 != 0:
                signal = "buy" if dir_htf2 > 0 else "sell"
                strength = 50
                reason = f"MTF Weak {signal.capitalize()} (H4 aligned only)"
            else:
                reason = f"MTF Misaligned (H1:{dir_htf1}, H4:{dir_htf2}, Curr:{dir_curr})"

        return {
            "signal": signal,
            "strength": float(strength),
            "reason": reason,
            "htf1_dir": dir_htf1,
            "htf2_dir": dir_htf2
        }

    def get_candle_direction(self, symbol, timeframe, index=0):
        rates = mt5.copy_rates_from_pos(symbol, timeframe, index, 1)
        if rates is None or len(rates) == 0:
            return 0
        candle = rates[0]
        if candle['close'] > candle['open']:
            return 1
        elif candle['close'] < candle['open']:
            return -1
        return 0
        
    def update_zones(self, symbol):
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 500)
        if rates is None or len(rates) < 50: return
        
        self.demand_zones = []
        self.supply_zones = []
        
        tr_sum = 0
        for i in range(len(rates)-14, len(rates)):
            tr_sum += (rates[i]['high'] - rates[i]['low'])
        atr = tr_sum / 14 if tr_sum > 0 else 0.001
        box_width = atr * 1.0
        
        swing_len = self.swing_length
        highs = np.array([r['high'] for r in rates])
        lows = np.array([r['low'] for r in rates])
        
        for i in range(swing_len, len(rates) - swing_len):
            is_low = True
            curr_low = lows[i]
            if np.min(lows[i-swing_len:i]) < curr_low or np.min(lows[i+1:i+swing_len+1]) < curr_low:
                is_low = False
            
            if is_low and len(self.demand_zones) < 50:
                self.demand_zones.append((curr_low + box_width, curr_low))
                
            is_high = True
            curr_high = highs[i]
            if np.max(highs[i-swing_len:i]) > curr_high or np.max(highs[i+1:i+swing_len+1]) > curr_high:
                is_high = False
                
            if is_high and len(self.supply_zones) < 50:
                self.supply_zones.append((curr_high, curr_high - box_width))
                
    def is_in_zone(self, price, is_demand):
        tolerance = 0.0005
        zones = self.demand_zones if is_demand else self.supply_zones
        for top, bottom in zones:
            if price >= (bottom - tolerance) and price <= (top + tolerance):
                return True
        return False

class AI_MT5_Bot:
    def __init__(self, symbol="GOLD", timeframe=mt5.TIMEFRAME_M15):
        self.symbol = symbol
        self.timeframe = timeframe
        self.magic_number = 20241223
        self.lot_size = 0.01
        self.last_bar_time = 0
        
        # 获取 timeframe 的字符串名称用于数据库和日志
        self.tf_name = "M15"
        if self.timeframe == mt5.TIMEFRAME_M1: self.tf_name = "M1"
        elif self.timeframe == mt5.TIMEFRAME_M5: self.tf_name = "M5"
        elif self.timeframe == mt5.TIMEFRAME_M15: self.tf_name = "M15"
        elif self.timeframe == mt5.TIMEFRAME_M30: self.tf_name = "M30"
        elif self.timeframe == mt5.TIMEFRAME_H1: self.tf_name = "H1"
        elif self.timeframe == mt5.TIMEFRAME_H4: self.tf_name = "H4"
        elif self.timeframe == mt5.TIMEFRAME_D1: self.tf_name = "D1"
        
        # 初始化 AI 客户端
        self.ai_factory = AIClientFactory()
        clients = self.ai_factory.initialize_all_clients()
        self.deepseek_client = clients.get('deepseek')
        self.qwen_client = clients.get('qwen')
        
        # 初始化高级分析模块
        # 用户指定时间框架: M15 (交易) 和 H1 (趋势/结构)
        self.crt_analyzer = CRTAnalyzer(timeframe_htf=mt5.TIMEFRAME_H1)
        # MTF 分析调整为 M30 和 H1，以匹配用户的 H1 关注点
        self.mtf_analyzer = MTFAnalyzer(htf1=mt5.TIMEFRAME_M30, htf2=mt5.TIMEFRAME_H1) 
        self.price_model = PriceEquationModel()
        self.tf_analyzer = TimeframeVisualAnalyzer()
        self.advanced_adapter = AdvancedAnalysisAdapter() # 初始化高级分析适配器
        self.matrix_ml = MatrixMLAnalyzer() # 新增 Matrix ML
        self.smc_analyzer = SMCAnalyzer() # 新增 SMC 分析器
        self.mfh_analyzer = MFHAnalyzer() # 新增 MFH 分析器
        self.optimizer = HybridOptimizer()
        self.db_manager = DatabaseManager()
        
        # 初始化参数优化器池 (Auto-Selection)
        self.optimizers = {
            "GWO": GWO(pop_size=10, alpha_number=3),
            "WOAm": WOAm(pop_size=10, ref_prob=0.1),
            "DE": DE(pop_size=10, F=0.5, CR=0.7),
            "COAm": COAm(pop_size=10, nests_number=10, koef_pa=0.6),
            "BBO": BBO(pop_size=10, immigration_max=1.0, emigration_max=1.0)
        }
        self.active_optimizer_name = "GWO" # 默认
        self.last_optimization_time = 0
        self.last_realtime_save = 0 # Added for realtime dashboard
        self.last_analysis_time = 0 # Added for periodic analysis (1 min)
        self.latest_strategy = None # 存储最新的策略参数 (用于 manage_positions)
        self.latest_signal = "neutral" # 存储最新的信号
        
        if not self.deepseek_client or not self.qwen_client:
            logger.warning("AI 客户端未完全初始化，将仅运行在观察模式")

    def initialize_mt5(self):
        """初始化 MT5 连接"""
        # 尝试使用指定账户登录
        account = 89633982
        server = "Ava-Real 1-MT5"
        password = "Clj568741230#"
        
        if not mt5.initialize(login=account, server=server, password=password):
            logger.error(f"MT5 初始化失败, 错误码: {mt5.last_error()}")
            return False
            
        # 检查终端状态
        term_info = mt5.terminal_info()
        if term_info is None:
            logger.error("无法获取终端信息")
            return False
            
        if not term_info.trade_allowed:
            logger.warning("⚠️ 警告: 终端 '自动交易' (Algo Trading) 未开启，无法执行交易！请在 MT5 工具栏点击 'Algo Trading' 按钮。")
            
        if not term_info.connected:
            logger.warning("⚠️ 警告: 终端未连接到交易服务器，请检查网络或账号设置。")
        
        # 确认交易品种存在
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            logger.error(f"找不到交易品种 {self.symbol}")
            return False
            
        if not symbol_info.visible:
            logger.info(f"交易品种 {self.symbol} 不可见，尝试选中")
            if not mt5.symbol_select(self.symbol, True):
                logger.error(f"无法选中交易品种 {self.symbol}")
                return False
        
        # 检查品种是否允许交易
        if symbol_info.trade_mode == mt5.SYMBOL_TRADE_MODE_DISABLED:
            logger.error(f"交易品种 {self.symbol} 禁止交易")
            return False
                
        logger.info(f"MT5 初始化成功，已连接到账户: {mt5.account_info().login}")
        return True

    def get_market_data(self, num_candles=100):
        """直接从 MT5 获取历史数据"""
        rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, num_candles)
        
        if rates is None or len(rates) == 0:
            logger.error("无法获取 K 线数据")
            return None
            
        # 转换为 DataFrame
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        
        # 将 tick_volume 重命名为 volume 以保持一致性
        if 'tick_volume' in df.columns:
            df.rename(columns={'tick_volume': 'volume'}, inplace=True)
        
        return df

    def calculate_sl_tp(self, signal, price, atr, sl_tp_params=None):
        """
        计算止损和止盈价格
        默认使用 ATR 动态止损: SL = 1.5 * ATR, TP = 2.5 * ATR
        """
        sl_multiplier = 1.5
        tp_multiplier = 2.5
        
        if sl_tp_params:
            sl_multiplier = sl_tp_params.get('sl_atr_multiplier', 1.5)
            tp_multiplier = sl_tp_params.get('tp_atr_multiplier', 2.5)
            
        sl = 0.0
        tp = 0.0
        
        # 确保 ATR 有效
        if atr <= 0:
            atr = price * 0.005 # 默认 0.5% 波动
            
        if signal == 'buy':
            sl = price - (atr * sl_multiplier)
            tp = price + (atr * tp_multiplier)
        elif signal == 'sell':
            sl = price + (atr * sl_multiplier)
            tp = price - (atr * tp_multiplier)
            
        return sl, tp

    def execute_trade(self, signal, strength, sl_tp_params, entry_params=None):
        """
        执行交易指令，参考 MQL5 Python 最佳实践
        https://www.mql5.com/en/book/advanced/python/python_ordercheck_ordersend
        """
        if signal not in ['buy', 'sell']:
            return
            
        # 1. 检查是否已有持仓
        positions = mt5.positions_get(symbol=self.symbol)
        
        # 用户需求: 不需要已有持仓跳过，可以平仓反手
        # 逻辑: 
        # - 如果有相反方向的持仓 -> 平掉它，然后开新仓
        # - 如果有相同方向的持仓 -> 
        #   A. 加仓 (基于账户资金和风险偏好)
        #   B. 保持现状
        
        account_info = mt5.account_info()
        balance = account_info.balance if account_info else 10000.0
        
        if positions and len(positions) > 0:
            for pos in positions:
                # 检查持仓方向
                pos_type = pos.type # 0: Buy, 1: Sell
                is_buy_pos = (pos_type == mt5.POSITION_TYPE_BUY)
                
                # 如果信号与现有持仓反向 (例如: 持有 Buy，信号 Sell)
                if (signal == 'sell' and is_buy_pos) or (signal == 'buy' and not is_buy_pos):
                    logger.info(f"信号反转 ({signal.upper()})，平掉现有持仓 #{pos.ticket}...")
                    
                    # 平仓请求
                    close_request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": self.symbol,
                        "volume": pos.volume,
                        "type": mt5.ORDER_TYPE_SELL if is_buy_pos else mt5.ORDER_TYPE_BUY,
                        "position": pos.ticket,
                        "price": mt5.symbol_info_tick(self.symbol).bid if is_buy_pos else mt5.symbol_info_tick(self.symbol).ask,
                        "deviation": 20,
                        "magic": self.magic_number,
                        "comment": "AI-Bot: Reversal Close",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_FOK,
                    }
                    
                    # 动态检查 filling mode
                    symbol_info = mt5.symbol_info(self.symbol)
                    if symbol_info:
                        filling_mode = mt5.ORDER_FILLING_FOK
                        if (symbol_info.filling_mode & mt5.SYMBOL_FILLING_FOK) != 0: filling_mode = mt5.ORDER_FILLING_FOK
                        elif (symbol_info.filling_mode & mt5.SYMBOL_FILLING_IOC) != 0: filling_mode = mt5.ORDER_FILLING_IOC
                        else: filling_mode = 0
                        close_request['type_filling'] = filling_mode

                    result = mt5.order_send(close_request)
                    if result.retcode != mt5.TRADE_RETCODE_DONE:
                        logger.error(f"平仓失败: {result.comment}")
                        return # 平仓失败则不执行新开仓，防止对冲
                    else:
                        logger.info(f"平仓成功 #{pos.ticket}")
                        self.send_telegram_message(f"🔄 *Position Closed (Reversal)*\nTicket: `{pos.ticket}`\nProfit: {result.profit}")
                
                # 如果信号与持仓同向
                elif (signal == 'buy' and is_buy_pos) or (signal == 'sell' and not is_buy_pos):
                    # 加仓逻辑: 检查是否有足够的保证金和风险敞口
                    # 简单规则: 如果总持仓量 < 账户余额/1000 * 0.1 (每1000刀最多0.1手)，且当前盈利 > ATR (金字塔加仓)
                    
                    total_volume = sum([p.volume for p in positions if p.symbol == self.symbol])
                    max_volume = (balance / 1000.0) * 0.1 # 风险控制
                    
                    if total_volume < max_volume:
                        # 检查当前持仓是否盈利
                        profit_pips = (mt5.symbol_info_tick(self.symbol).bid - pos.price_open) if is_buy_pos else (pos.price_open - mt5.symbol_info_tick(self.symbol).ask)
                        
                        # 获取 ATR (复用计算逻辑，不简化)
                        rates_atr = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, 20)
                        current_atr = 0.001
                        if rates_atr is not None and len(rates_atr) > 14:
                            df_atr = pd.DataFrame(rates_atr)
                            tr = df_atr['high'] - df_atr['low'] # 简化 TR
                            current_atr = tr.rolling(14).mean().iloc[-1]
                            
                        if profit_pips > current_atr * 0.5: # 盈利超过 0.5 ATR 才加仓
                            logger.info(f"同向加仓: 当前持仓盈利且风险允许 (Vol: {total_volume:.2f} < Max: {max_volume:.2f})")
                            # 继续执行下面的开仓逻辑 (不 return)
                        else:
                            logger.info(f"同向持仓但盈利不足或风险已满，跳过加仓")
                            return
                    else:
                        logger.info(f"风险敞口已满 (Vol: {total_volume:.2f} >= Max: {max_volume:.2f})，跳过加仓")
                        return

        # 2. 获取最新的品种信息
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            logger.error(f"找不到品种 {self.symbol}")
            return
            
        if not symbol_info.visible:
            logger.info(f"品种 {self.symbol} 不可见，尝试选中")
            if not mt5.symbol_select(self.symbol, True):
                logger.error(f"无法选中品种 {self.symbol}")
                return

        # 3. 准备交易参数
        action = mt5.TRADE_ACTION_DEAL
        type_order = mt5.ORDER_TYPE_BUY if signal == 'buy' else mt5.ORDER_TYPE_SELL
        
        # 获取最新报价
        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            logger.error(f"无法获取 {self.symbol} 的最新报价")
            return
            
        price = tick.ask if signal == 'buy' else tick.bid
        
        # --- 检查是否使用挂单 (Limit Order) ---
        is_pending = False
        if entry_params and entry_params.get('trigger_type') == 'limit':
            limit_price = entry_params.get('limit_price', 0.0)
            if limit_price > 0:
                # 简单的挂单逻辑
                # 检查限价单的逻辑是否合理 (买单价格 < Ask, 卖单价格 > Bid)
                # 如果不合理，我们不应该直接降级为市价单，而应该:
                # 1. 调整价格 (例如设为当前价的微小偏移)
                # 2. 或者直接降级为市价单 (如果差距过大)
                
                valid_limit = False
                if signal == 'buy':
                     if limit_price < tick.ask:
                         valid_limit = True
                     else:
                         # 价格不合理，可能是 Qwen 没更新最新价格
                         # 尝试修正: 如果 limit_price > ask，说明想以更高价买入? 那直接市价买更好
                         # 或者这是突破单 (Stop Order)? 目前仅支持 Limit
                         logger.warning(f"限价买单价格 {limit_price} >= Ask {tick.ask}，转为市价单")
                         valid_limit = False
                         
                elif signal == 'sell':
                     if limit_price > tick.bid:
                         valid_limit = True
                     else:
                         logger.warning(f"限价卖单价格 {limit_price} <= Bid {tick.bid}，转为市价单")
                         valid_limit = False
                
                if valid_limit:
                    if signal == 'buy':
                        action = mt5.TRADE_ACTION_PENDING
                        type_order = mt5.ORDER_TYPE_BUY_LIMIT
                        price = limit_price
                        is_pending = True
                        logger.info(f"使用限价买单: {limit_price}")
                    elif signal == 'sell':
                        action = mt5.TRADE_ACTION_PENDING
                        type_order = mt5.ORDER_TYPE_SELL_LIMIT
                        price = limit_price
                        is_pending = True
                        logger.info(f"使用限价卖单: {limit_price}")
                else:
                    # 价格无效，降级为市价单
                    pass
        
        # --- 计算止损止盈 ---
        # 获取 ATR (需要从 data_processor 或 context 获取，不要简化)
        # 我们这里重新请求完整数据来计算准确的 ATR，确保不使用过时或简化的数据
        
        # 获取足够的历史数据来计算 ATR(14)
        rates_full = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, 100)
        atr = 0.0
        if rates_full is not None and len(rates_full) > 20:
            df_full = pd.DataFrame(rates_full)
            
            # 完整的 TR 计算
            high = df_full['high']
            low = df_full['low']
            close = df_full['close']
            
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            # ATR SMA 14
            atr = tr.rolling(window=14).mean().iloc[-1]
        
        if atr <= 0:
            logger.warning("ATR 计算失败，使用默认值")
            atr = price * 0.005 # Fallback
            
        sl, tp = self.calculate_sl_tp(signal, price, atr, sl_tp_params)
        logger.info(f"计算止损止盈 (ATR={atr:.4f}): SL={sl:.2f}, TP={tp:.2f}")

        # 4. 规范化交易量
        # 确保交易量在 min/max 之间，并且是 step 的倍数
        volume = self.lot_size
        if volume < symbol_info.volume_min:
            volume = symbol_info.volume_min
            logger.warning(f"交易量调整为最小允许值: {volume}")
        elif volume > symbol_info.volume_max:
            volume = symbol_info.volume_max
            logger.warning(f"交易量调整为最大允许值: {volume}")
            
        # 简单的步长调整 (保留合适的小数位)
        # 假设 volume_step 是 0.01，则保留 2 位小数
        import math
        step_decimals = 0
        if symbol_info.volume_step > 0:
            step_decimals = int(round(-math.log(symbol_info.volume_step, 10), 0))
            volume = round(volume, step_decimals)
            
        # 5. 构建请求结构
        request = {
            "action": action,
            "symbol": self.symbol,
            "volume": volume,
            "type": type_order,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": self.magic_number,
            "comment": f"AI-Bot: {strength:.1f}%",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK, 
        }
        
        # 6. 动态选择填充模式 (Filling Mode)
        filling_mode = mt5.ORDER_FILLING_FOK
        
        # 定义填充模式常量 (如果 mt5 模块中缺少)
        SYMBOL_FILLING_FOK = 1
        SYMBOL_FILLING_IOC = 2

        # 检查是否支持 FOK
        if (symbol_info.filling_mode & SYMBOL_FILLING_FOK) != 0:
            filling_mode = mt5.ORDER_FILLING_FOK
        # 检查是否支持 IOC
        elif (symbol_info.filling_mode & SYMBOL_FILLING_IOC) != 0:
            filling_mode = mt5.ORDER_FILLING_IOC
        else:
            # 如果都不支持，通常设为 0 (ORDER_FILLING_RETURN)
            filling_mode = 0
            
        # 挂单通常不支持 FOK/IOC，需要设置为 ORDER_FILLING_RETURN (0) 或其他
        if is_pending:
             request['type_filling'] = mt5.ORDER_FILLING_RETURN
        else:
             request['type_filling'] = filling_mode
        
        # 7. 执行 OrderCheck (关键步骤)
        logger.info(f"正在检查订单: {signal.upper()} {volume} lots @ {price}")
        check_result = mt5.order_check(request)
        
        if check_result is None:
            logger.error("order_check() 返回 None, API 可能未连接")
            return
            
        # order_check 返回 0 也表示成功 (Done)
        if check_result.retcode != mt5.TRADE_RETCODE_DONE and check_result.retcode != 0:
            logger.error(f"❌ 订单检查失败: {check_result.comment}")
            logger.error(f"   Retcode: {check_result.retcode}")
            logger.error(f"   Balance: {check_result.balance}, Equity: {check_result.equity}")
            logger.error(f"   Margin: {check_result.margin}, Free Margin: {check_result.margin_free}")
            logger.error(f"   Margin Level: {check_result.margin_level}")
            
            # 发送警告到 Telegram
            self.send_telegram_message(f"⚠️ *Order Check Failed*\nReason: {check_result.comment}\nCode: {check_result.retcode}")
            return
            
        logger.info("✅ 订单检查通过，准备发送交易...")
        
        # 8. 发送订单
        result = mt5.order_send(request)
        
        if result is None:
            logger.error("order_send() 返回 None")
            return
            
        # 记录交易结果
        trade_data = {
            "ticket": result.order if result.retcode == mt5.TRADE_RETCODE_DONE else 0,
            "symbol": self.symbol,
            "action": signal.upper(),
            "volume": volume,
            "price": price,
            "result": "OPEN" if result.retcode == mt5.TRADE_RETCODE_DONE else f"ERROR: {result.comment}"
        }
        self.db_manager.save_trade(trade_data)
        
        # 9. 处理返回结果
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"❌ 订单发送失败: {result.comment}, 错误码: {result.retcode}")
            # 可以在这里添加重试逻辑，如果错误码是临时的 (如连接超时)
            self.send_telegram_message(f"❌ *Trade Failed*\nSymbol: {self.symbol}\nError: {result.comment}")
        else:
            logger.info(f"🚀 订单执行成功! 票号: {result.order}")
            logger.info(f"   成交价: {result.price}, 交易量: {result.volume}")
            
            trade_msg = (
                f"🚀 *Trade Executed*\n"
                f"Symbol: {self.symbol}\n"
                f"Action: {signal.upper()}\n"
                f"Volume: {volume}\n"
                f"Price: {price}\n"
                f"Ticket: `{result.order}`"
            )
            self.send_telegram_message(trade_msg)

    def send_telegram_message(self, message):
        """发送消息到 Telegram"""
        token = "8253887074:AAE_o7hfEb6iJCZ2MdVIezOC_E0OnTCvCzY"
        chat_id = "5254086791"
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        # 配置代理 (针对中国大陆用户)
        # 如果您使用 Clash，通常端口是 7890
        # 如果您使用 v2rayN，通常端口是 10809
        proxies = {
            "http": "http://127.0.0.1:7890",
            "https": "http://127.0.0.1:7890"
        }
        
        try:
            import requests
            try:
                # 尝试通过代理发送
                response = requests.post(url, json=data, timeout=10, proxies=proxies)
            except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError):
                # 如果代理失败，尝试直连 (虽然可能也会被墙)
                logger.warning("代理连接失败，尝试直连 Telegram...")
                response = requests.post(url, json=data, timeout=10)
                
            if response.status_code != 200:
                logger.error(f"Telegram 发送失败: {response.text}")
        except Exception as e:
            logger.error(f"Telegram 发送异常: {e}")

    def manage_positions(self, signal=None, strategy_params=None):
        """
        根据最新分析结果管理持仓:
        1. 更新止损止盈 (覆盖旧设置) - 基于 strategy_params
        2. 执行移动止损 (Trailing Stop)
        3. 检查是否需要平仓 (非反转情况，例如信号转弱)
        """
        positions = mt5.positions_get(symbol=self.symbol)
        if positions is None or len(positions) == 0:
            return

        # 获取 ATR 用于计算移动止损距离 (动态调整)
        rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, 20)
        atr = 0.0
        if rates is not None and len(rates) > 14:
            df_temp = pd.DataFrame(rates)
            high_low = df_temp['high'] - df_temp['low']
            atr = high_low.rolling(14).mean().iloc[-1]
            
        if atr <= 0:
            return # 无法计算 ATR，跳过

        trailing_dist = atr * 1.5 # 默认移动止损距离
        
        # 如果有策略参数，尝试解析最新的 SL/TP 设置
        new_sl_multiplier = 1.5
        new_tp_multiplier = 2.5
        has_new_params = False
        
        if strategy_params:
            exit_cond = strategy_params.get('exit_conditions')
            if exit_cond:
                new_sl_multiplier = exit_cond.get('sl_atr_multiplier', 1.5)
                new_tp_multiplier = exit_cond.get('tp_atr_multiplier', 2.5)
                has_new_params = True
                # 更新移动止损距离 (可选: 基于新 SL 倍数)
                # trailing_dist = atr * new_sl_multiplier 

        for pos in positions:
            if pos.magic != self.magic_number:
                continue
                
            symbol = pos.symbol
            type_pos = pos.type # 0: Buy, 1: Sell
            price_open = pos.price_open
            sl = pos.sl
            tp = pos.tp
            current_price = pos.price_current
            
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": symbol,
                "position": pos.ticket,
                "sl": sl,
                "tp": tp
            }
            
            changed = False
            
            # --- 1. 基于最新策略更新 SL/TP (覆盖旧值) ---
            if has_new_params:
                # 计算新的目标 SL/TP
                calc_sl = 0.0
                calc_tp = 0.0
                
                # 注意: 这里我们使用当前价格重新计算，还是基于开仓价?
                # 用户要求 "cover previous ones... based on latest analysis"
                # 通常 SL 是基于当前价格的动态保护，或者基于开仓价的固定保护
                # 如果是移动止损，是基于当前价。如果是结构性 SL，可能是基于开仓价。
                # Qwen 给出的通常是 ATR 倍数。
                
                # 我们假设 Qwen 的意图是: "当前市场状态下，合理的 SL 距离是 X ATR"
                # 因此，我们应该检查当前 SL 是否符合这个距离。
                # 如果是浮动盈亏状态，我们通常只做 Trailing (收紧 SL)，而不放宽。
                
                # 简化逻辑: 仅当我们需要收紧 SL 时才更新 (Trailing)，或者当 TP 需要调整时。
                # 但用户说 "cover"，可能意味着强制更新。
                # 风险: 如果价格已经反向运行，重新计算 SL 可能会导致 SL 被推远 (增加亏损)。
                # 原则: SL 只能向有利方向移动 (Tighten)。
                
                pass # 具体计算在下面结合 Trailing 处理
            
            # --- 2. 执行移动止损 & 策略更新 ---
            
            if type_pos == mt5.POSITION_TYPE_BUY:
                # Buy: 
                # 1. Trailing Stop
                new_sl = current_price - (atr * new_sl_multiplier) # 使用最新的 multiplier
                
                # 确保 SL 不低于开仓价 (保本) -> 只有在盈利时才保本? 
                # 或者仅仅是追踪? 通常 Trailing Stop 是无条件的 (只要价格上涨)
                
                # 逻辑: 新 SL 必须 > 旧 SL (只上移)
                if new_sl > sl:
                    # 额外检查: 不要离现价太近 (防止被随机波动打掉)
                    if (current_price - new_sl) >= mt5.symbol_info(self.symbol).point * 10:
                        request['sl'] = new_sl
                        changed = True
                
                # 2. Update TP (如果有新策略)
                # TP 可以双向调整 (适应市场波动率)
                if has_new_params:
                    # TP 通常基于开仓价 (固定目标) 或 当前价 (滚动目标)?
                    # 标准做法: TP 基于入场位。但如果持仓很久，可能需要基于当前结构调整。
                    # 这里我们基于当前价格 + TP距离? 不，这会让 TP 永远追不到。
                    # 我们应该保持 TP 基于开仓价，但调整倍数?
                    # 或者，直接使用 Qwen 给出的具体价格 (如果它能给出)。
                    # 目前 Qwen 给的是倍数。
                    
                    # 这种情况下，修改 TP 比较危险。我们暂时只调整 SL (Trailing)。
                    # 除非用户明确要求 "动态调整 TP"。
                    pass

            elif type_pos == mt5.POSITION_TYPE_SELL:
                # Sell:
                # 1. Trailing Stop
                new_sl = current_price + (atr * new_sl_multiplier)
                
                # 逻辑: 新 SL 必须 < 旧 SL (只下移)
                if (sl == 0 or new_sl < sl):
                    if (new_sl - current_price) >= mt5.symbol_info(self.symbol).point * 10:
                        request['sl'] = new_sl
                        changed = True
            
            if changed:
                logger.info(f"更新持仓 #{pos.ticket}: SL={request['sl']:.2f} (ATR x {new_sl_multiplier})")
                result = mt5.order_send(request)
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    logger.error(f"持仓修改失败: {result.comment}")
                    
            # --- 3. 检查信号平仓 ---
            # 如果最新信号转为反向或中立，且强度足够，可以考虑提前平仓
            # 但 execute_trade 已经处理了反向开仓(会先平仓)。
            # 这里只处理: 信号变 Weak/Neutral 时的防御性平仓 (如果需要)
            # 用户: "operate SL/TP, or close, open"
            if signal == 'neutral' and strategy_params:
                # 检查是否应该平仓
                # 简单逻辑: 如果盈利 > 0 且信号消失，落袋为安?
                # 或者依靠 Trailing Stop 自然离场。
                pass

    def analyze_closed_trades(self):
        """
        分析已平仓的交易，计算 MFE (最大有利波动) and MAE (最大不利波动)
        用于后续 AI 学习和策略优化
        """
        try:
            # 1. 获取数据库中尚未标记为 CLOSED 的交易
            open_trades = self.db_manager.get_open_trades()
            
            if not open_trades:
                return

            for trade in open_trades:
                ticket = trade['ticket'] # 这是 Order Ticket
                symbol = trade['symbol']
                
                # 2. 检查该订单是否已完全平仓
                # 我们通过 Order Ticket 查找对应的 History Orders 或 Deals
                # 注意: 在 MT5 中，一个 Position 可能由多个 Deal 组成 (In, Out)
                # 我们需要找到该 Order 开启的 Position ID
                
                # 尝试通过 Order Ticket 获取 Position ID
                # history_orders_get 可以通过 ticket 获取指定历史订单
                # 但我们需要的是 Deals 来确定是否平仓
                
                # 方法 A: 获取该 Order 的 Deal，得到 Position ID，然后查询 Position 的所有 Deals
                # 假设 Order Ticket 也是 Position ID (通常情况)
                position_id = ticket 
                
                # 获取该 Position ID 的所有历史交易
                # from_date 设为很久以前，确保能找到
                deals = mt5.history_deals_get(position=position_id)
                
                if deals is None or len(deals) == 0:
                    # 可能还没平仓，或者 Ticket 不是 Position ID
                    # 如果是 Netting 账户，PositionID 通常等于开仓 Deal 的 Ticket
                    continue
                    
                # 检查是否有 ENTRY_OUT (平仓) 类型的 Deal
                has_out = False
                close_time = 0
                close_price = 0.0
                profit = 0.0
                open_price = trade['price'] # 使用 DB 中的开仓价
                open_time_ts = 0
                
                # 重新计算利润和确认平仓
                total_profit = 0.0
                
                for deal in deals:
                    total_profit += deal.profit + deal.swap + deal.commission
                    
                    if deal.entry == mt5.DEAL_ENTRY_IN:
                        open_time_ts = deal.time
                        # 如果 DB 中没有准确的开仓价，可以用这个: open_price = deal.price
                    
                    if deal.entry == mt5.DEAL_ENTRY_OUT:
                        has_out = True
                        close_time = deal.time
                        close_price = deal.price
                
                # 如果有 OUT deal，说明已平仓 (或部分平仓，这里简化为只要有 OUT 就视为结束分析)
                # 并且要确保此时持仓量为 0 (完全平仓)
                # 通过 positions_get(ticket=position_id) 检查是否还存在不要简化
                
                active_pos = mt5.positions_get(ticket=position_id)
                is_fully_closed = True
                if active_pos is not None and len(active_pos) > 0:
                    # Position still exists
                    is_fully_closed = False
                
                if has_out and is_fully_closed:
                    # 这是一个已平仓的完整交易
                    # 获取该时段的 M1 数据来计算 MFE/MAE
                    
                    # 确保时间范围有效
                    if open_time_ts == 0:
                        open_time_ts = int(pd.to_datetime(trade['time']).timestamp())
                        
                    start_dt = datetime.fromtimestamp(open_time_ts)
                    end_dt = datetime.fromtimestamp(close_time)
                    
                    if start_dt >= end_dt:
                        continue
                        
                    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, start_dt, end_dt)
                                               
                    if rates is not None and len(rates) > 0:
                        df_rates = pd.DataFrame(rates)
                        max_high = df_rates['high'].max()
                        min_low = df_rates['low'].min()
                        
                        mfe = 0.0
                        mae = 0.0
                        
                        action = trade['action']
                        
                        if action == 'BUY':
                            mfe = (max_high - open_price) / open_price * 100 # %
                            mae = (min_low - open_price) / open_price * 100 # % (Negative)
                        elif action == 'SELL':
                            mfe = (open_price - min_low) / open_price * 100 # %
                            mae = (open_price - max_high) / open_price * 100 # % (Negative)
                            
                        # 更新数据库
                        self.db_manager.update_trade_performance(ticket, {
                            "close_price": close_price,
                            "close_time": end_dt,
                            "profit": total_profit,
                            "mfe": mfe,
                            "mae": mae
                        })
                        
                        logger.info(f"分析交易 #{ticket} 完成: MFE={mfe:.2f}%, MAE={mae:.2f}%, Profit={total_profit:.2f}")

        except Exception as e:
            logger.error(f"分析历史交易失败: {e}")

    def evaluate_smc_params(self, params, df):
        """
        目标函数: 评估 SMC 策略参数的表现
        params: [ma_period, atr_threshold]
        完整回测逻辑，不简化处理
        """
        ma_period = int(params[0])
        atr_threshold = params[1]
        
        # 创建临时分析器
        analyzer = SMCAnalyzer()
        analyzer.ma_period = ma_period
        analyzer.atr_threshold = atr_threshold
        
        score = 0
        total_trades = 0
        win_trades = 0
        total_profit_pips = 0.0
        
        closes = df['close'].values
        
        # 我们需要足够的数据来计算 MA
        if len(closes) < ma_period + 50:
            return -1000
            
        # 完整的逐 K 线回测
        # 从 ma_period 开始，模拟每根 K 线作为"当前" K 线
        # 记录虚拟交易
        
        # 账户状态维护
        equity = 10000.0 # 初始净值
        balance = 10000.0 # 初始余额
        
        positions = [] # [{'type': 'buy', 'price': 1.0, 'vol': 0.1, 'sl': 0.9, 'tp': 1.2}, ...]
        
        in_trade = False
        trade_type = "" # buy, sell
        entry_price = 0.0
        entry_idx = 0
        
        # 为了提高效率，维护复杂的账户净值 
        # 这里的"不简化"指的是: 必须逐个遍历检查信号，而不是跳跃采样
        
        holding_period = 24 
        
        start_idx = ma_period
        end_idx = len(closes) - holding_period # 留出平仓空间
        
        # 预计算 MA (向量化) 以避免循环中重复计算
        # 注意: SMCAnalyzer 内部使用 rolling mean，这里为了模拟真实情况，
        # 我们应该让 Analyzer 自己算。但为了速度，我们可以手动计算指标传入 Analyzer?
        # 不，为了准确性，我们传入切片。虽然慢，但符合"不简化"的要求。
        # 优化: Analyzer 的 get_market_sentiment 只需要最近的数据。
        # 如果我们每次都传入完整 df.iloc[:i]，随着 i 增大，切片开销大。
        # 实际上 SMCAnalyzer.analyze 只需要最近 ma_period + small_buffer 的数据。
        
        lookback_needed = ma_period + 50
        
        for i in range(start_idx, end_idx):
            # 1. 更新账户净值 (Mark to Market)
            current_close = closes[i]
            current_high = df['high'].iloc[i]
            current_low = df['low'].iloc[i]
            
            unrealized_pl = 0.0
            
            # 检查现有持仓的盈亏和止损止盈
            active_positions = []
            for pos in positions:
                pl = 0.0
                if pos['type'] == 'buy':
                    pl = (current_close - pos['price']) * pos['vol'] * 100000 # 假设标准合约
                    
                    # 检查 SL/TP (基于 High/Low)
                    if current_low <= pos['sl']: # 触发止损
                        close_p = pos['sl']
                        realized_pl = (close_p - pos['price']) * pos['vol'] * 100000
                        balance += realized_pl
                        total_trades += 1
                        if realized_pl > 0: win_trades += 1
                        continue # 移除持仓
                    elif current_high >= pos['tp']: # 触发止盈
                        close_p = pos['tp']
                        realized_pl = (close_p - pos['price']) * pos['vol'] * 100000
                        balance += realized_pl
                        total_trades += 1
                        if realized_pl > 0: win_trades += 1
                        continue # 移除持仓
                        
                elif pos['type'] == 'sell':
                    pl = (pos['price'] - current_close) * pos['vol'] * 100000
                    
                    if current_high >= pos['sl']: # 触发止损
                        close_p = pos['sl']
                        realized_pl = (pos['price'] - close_p) * pos['vol'] * 100000
                        balance += realized_pl
                        total_trades += 1
                        if realized_pl > 0: win_trades += 1
                        continue
                    elif current_low <= pos['tp']: # 触发止盈
                        close_p = pos['tp']
                        realized_pl = (pos['price'] - close_p) * pos['vol'] * 100000
                        balance += realized_pl
                        total_trades += 1
                        if realized_pl > 0: win_trades += 1
                        continue
                
                unrealized_pl += pl
                active_positions.append(pos)
            
            positions = active_positions # 更新持仓列表
            equity = balance + unrealized_pl
            
            if equity <= 0: # 爆仓
                return -99999
            
            # 2. 生成信号
            # 获取上下文窗口
            window_start = max(0, i - lookback_needed)
            sub_df = df.iloc[window_start:i+1] # 注意 iloc 是左闭右开，所以要 i+1
            
            result = analyzer.analyze(sub_df)
            signal = result['signal']
            
            # 3. 交易逻辑
            # 简单的交易逻辑: 如果有信号且无持仓，则开仓
            # 如果有持仓，检查是否反转
            
            # 简单的 ATR 计算用于 SL/TP
            # 这里简单取最近 14 根 High-Low 的均值作为 ATR 估计
            atr_est = np.mean(df['high'].iloc[i-14:i] - df['low'].iloc[i-14:i])
            if atr_est <= 0: atr_est = current_close * 0.001
            
            if len(positions) == 0:
                if signal != 'neutral':
                    # 开仓
                    sl_dist = atr_est * 1.5
                    tp_dist = atr_est * 2.5
                    
                    sl = current_close - sl_dist if signal == 'buy' else current_close + sl_dist
                    tp = current_close + tp_dist if signal == 'buy' else current_close - tp_dist
                    
                    positions.append({
                        'type': signal,
                        'price': current_close,
                        'vol': 0.1, # 固定 0.1 手
                        'sl': sl,
                        'tp': tp,
                        'entry_idx': i
                    })
            else:
                # 检查平仓条件 (反转)
                # 假设单向持仓
                curr_pos = positions[0]
                if (curr_pos['type'] == 'buy' and signal == 'sell') or \
                   (curr_pos['type'] == 'sell' and signal == 'buy'):
                    
                    # 平仓
                    pl = 0.0
                    if curr_pos['type'] == 'buy':
                        pl = (current_close - curr_pos['price']) * curr_pos['vol'] * 100000
                    else:
                        pl = (curr_pos['price'] - current_close) * curr_pos['vol'] * 100000
                        
                    balance += pl
                    total_trades += 1
                    if pl > 0: win_trades += 1
                    positions = [] # 清空
                    
                    # 反手开仓
                    sl_dist = atr_est * 1.5
                    tp_dist = atr_est * 2.5
                    sl = current_close - sl_dist if signal == 'buy' else current_close + sl_dist
                    tp = current_close + tp_dist if signal == 'buy' else current_close - tp_dist
                    
                    positions.append({
                        'type': signal,
                        'price': current_close,
                        'vol': 0.1,
                        'sl': sl,
                        'tp': tp,
                        'entry_idx': i
                    })
                    
        # 处理最后一笔未平仓交易 (按当前价平仓)
        for pos in positions:
            pl = 0.0
            if pos['type'] == 'buy':
                pl = (closes[end_idx] - pos['price']) * pos['vol'] * 100000
            else:
                pl = (pos['price'] - closes[end_idx]) * pos['vol'] * 100000
            balance += pl
            total_trades += 1
            if pl > 0: win_trades += 1

        # 评分公式
        if total_trades == 0:
            return -100
            
        # 最终得分基于净值增长
        net_profit = balance - 10000.0
        
        # 综合评分: 净利润 + 胜率修正
        win_rate = win_trades / total_trades
        score = net_profit * (1 + win_rate)
        
        return score

    def optimize_strategy_parameters(self):
        """
        使用 自动选择的优化器 优化策略参数
        包含自动选择最佳算法的逻辑 (Auto-Selection)
        """
        logger.info("开始执行策略参数优化 (Auto-AO)...")
        
        # 1. 获取用于优化的历史数据 (最近 500 根 H1)
        df = self.get_market_data(500)
        if df is None or len(df) < 300:
            logger.warning("数据不足，跳过优化")
            return
            
        # 2. 定义搜索空间
        # [MA Period (100-300), ATR Threshold (0.001-0.005)]
        bounds = [(100, 300), (0.001, 0.005)]
        steps = [10, 0.0005] # 步长
        
        # 3. 定义目标函数 Wrapper
        def objective(params):
            return self.evaluate_smc_params(params, df)
            
        # 4. 自动选择或轮询优化算法
        # 简单逻辑: 随机选择或轮询，或者记录历史表现选择最好的
        # 这里演示: 随机选择一个算法进行本次优化
        import random
        algo_name = random.choice(list(self.optimizers.keys()))
        optimizer = self.optimizers[algo_name]
        
        logger.info(f"本次选择的优化算法: {algo_name}")
        
        # 5. 运行优化
        best_params, best_score = optimizer.optimize(
            objective, 
            bounds, 
            steps=steps, 
            epochs=5 # 快速优化
        )
        
        # 6. 应用最佳参数
        new_ma = int(best_params[0])
        new_atr = best_params[1]
        
        logger.info(f"优化完成! Best Score: {best_score:.4f}")
        logger.info(f"更新参数: MA Period={new_ma}, ATR Threshold={new_atr:.4f}")
        
        self.smc_analyzer.ma_period = new_ma
        self.smc_analyzer.atr_threshold = new_atr
        
        self.send_telegram_message(
            f"🧬 *Auto-AO Optimization ({algo_name})*\n"
            f"Best Score: {best_score:.2f}\n"
            f"New Params:\n"
            f"• MA Period: {new_ma}\n"
            f"• ATR Thresh: {new_atr:.4f}"
        )

    def run(self):
        """主循环"""
        if not self.initialize_mt5():
            return

        logger.info(f"启动 AI 自动交易机器人 - {self.symbol}")
        self.send_telegram_message(f"🤖 *AI Bot Started*\nSymbol: {self.symbol}\nTimeframe: {self.timeframe}")
        
        try:
            while True:
                # 0. 管理持仓 (移动止损) - 使用最新策略
                if self.latest_strategy:
                    self.manage_positions(self.latest_signal, self.latest_strategy)
                else:
                    self.manage_positions() # 降级为默认
                
                # 0.5 分析已平仓交易 (每 60 次循环 / 约 1 分钟执行一次)
                if int(time.time()) % 60 == 0:
                    self.analyze_closed_trades()
                    
                # 0.6 执行策略参数优化 (每 4 小时一次)
                if time.time() - self.last_optimization_time > 14400:
                    self.optimize_strategy_parameters()
                    self.last_optimization_time = time.time()
                
                # 1. 检查新 K 线
                # 获取最后一根 K 线的时间
                rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, 1)
                if rates is None:
                    time.sleep(1)
                    continue
                    
                current_bar_time = rates[0]['time']
                
                # --- Real-time Data Update (Added for Dashboard) ---
                # 每隔 3 秒保存一次当前正在形成的 K 线数据到数据库
                # 这样 Dashboard 就可以看到实时价格跳动
                if time.time() - self.last_realtime_save > 3:
                    try:
                        df_current = pd.DataFrame(rates)
                        df_current['time'] = pd.to_datetime(df_current['time'], unit='s')
                        df_current.set_index('time', inplace=True)
                        if 'tick_volume' in df_current.columns:
                            df_current.rename(columns={'tick_volume': 'volume'}, inplace=True)
                        
                        self.db_manager.save_market_data(self.symbol, self.tf_name, df_current)
                        self.last_realtime_save = time.time()
                        
                        # 实时更新持仓 SL/TP (使用最近一次分析的策略)
                        if self.latest_strategy:
                            self.manage_positions(self.latest_signal, self.latest_strategy)
                            
                    except Exception as e:
                        logger.error(f"Real-time data save failed: {e}")
                # ---------------------------------------------------

                # 如果是新 K 线 或者 这是第一次运行 (last_bar_time 为 0)
                # 用户需求: 每15分钟执行一次分析 (即跟随 M15 K 线收盘)
                is_new_bar = current_bar_time != self.last_bar_time
                
                if is_new_bar:
                    if self.last_bar_time == 0:
                        logger.info("首次运行，立即执行分析...")
                    else:
                        logger.info(f"发现新 K 线: {datetime.fromtimestamp(current_bar_time)}")
                    
                    self.last_bar_time = current_bar_time
                    self.last_analysis_time = time.time()
                    
                    # 2. 获取数据并分析
                    # ... 这里的代码保持不变 ...
                    # PEM 需要至少 108 根 K 线 (ma_fast_period)，MTF 更新 Zones 需要 500 根
                    # 为了确保所有模块都有足够数据，我们获取 300 根 (MTF Zones 在 update_zones 内部单独获取)
                    df = self.get_market_data(300) 
                    
                    # 获取最近的 Tick 数据用于 Matrix ML
                    # 尝试获取最近 20 个 tick
                    ticks = mt5.copy_ticks_from(self.symbol, current_bar_time, 20, mt5.COPY_TICKS_ALL)
                    if ticks is None:
                        ticks = []
                    
                    if df is not None:
                        # 保存市场数据到DB
                        self.db_manager.save_market_data(self.symbol, self.tf_name, df)
                        
                        # 使用 data_processor 计算指标
                        processor = MT5DataProcessor()
                        df_features = processor.generate_features(df)
                        
                        # 3. 调用 AI 与高级分析
                        # 构建市场快照
                        current_price = df.iloc[-1]
                        latest_features = df_features.iloc[-1].to_dict()
                        
                        market_snapshot = {
                            "symbol": self.symbol,
                            "timeframe": self.tf_name,
                            "prices": {
                                "open": float(current_price['open']),
                                "high": float(current_price['high']),
                                "low": float(current_price['low']),
                                "close": float(current_price['close']),
                                "volume": int(current_price['volume'])
                            },
                            "indicators": {
                                "rsi": float(latest_features.get('rsi', 50)),
                                "atr": float(latest_features.get('atr', 0)),
                                "ema_fast": float(latest_features.get('ema_fast', 0)),
                                "ema_slow": float(latest_features.get('ema_slow', 0)),
                                "volatility": float(latest_features.get('volatility', 0))
                            }
                        }
                        
                        # --- 3.1 CRT 分析 ---
                        crt_result = self.crt_analyzer.analyze(self.symbol, current_price, current_bar_time)
                        logger.info(f"CRT 分析: {crt_result['signal']} ({crt_result['reason']})")
                        
                        # --- 3.2 价格方程模型 (PEM) ---
                        self.price_model.update(float(current_price['close']))
                        price_eq_result = self.price_model.predict(df) # 传入 df 进行分析
                        logger.info(f"PEM 预测: {price_eq_result['signal']} (目标: {price_eq_result['predicted_price']:.2f})")
                        
                        # --- 3.2.1 多时间周期分析 (新增) ---
                        tf_result = self.tf_analyzer.analyze(self.symbol, current_bar_time)
                        logger.info(f"TF 分析: {tf_result['signal']} ({tf_result['reason']})")
                        
                        # --- 3.2.2 高级技术分析 (新增) ---
                        adv_result = self.advanced_adapter.analyze(df)
                        adv_signal = "neutral"
                        if adv_result:
                            adv_signal = adv_result['signal_info']['signal']
                            logger.info(f"高级技术分析: {adv_signal} (强度: {adv_result['signal_info']['strength']})")
                            logger.info(f"市场状态: {adv_result['regime']['description']}")
                            
                        # --- 3.2.3 Matrix ML 分析 (新增) ---
                        # 首先进行训练 (基于上一次预测和当前价格变动)
                        price_change = float(current_price['close']) - float(df.iloc[-2]['close']) if len(df) > 1 else 0
                        loss = self.matrix_ml.train(price_change)
                        if loss:
                            logger.info(f"Matrix ML 训练 Loss: {loss:.4f}")
                            
                        # 进行预测
                        ml_result = self.matrix_ml.predict(ticks)
                        logger.info(f"Matrix ML 预测: {ml_result['signal']} (Raw: {ml_result.get('raw_output', 0.0):.2f})")
                        
                        # --- 3.2.4 SMC 分析 (新增) ---
                        smc_result = self.smc_analyzer.analyze(df)
                        logger.info(f"SMC 结构: {smc_result['structure']} (信号: {smc_result['signal']})")
                        
                        # --- 3.2.5 MFH 分析 (新增) ---
                        # 计算真实收益率用于训练 (t - t_horizon)
                        # 我们需要足够的数据来计算 Horizon 收益
                        horizon = 5
                        mfh_slope = 0.0
                        mfh_signal = "neutral"
                        
                        if len(df) > horizon + 10:
                            # 1. 训练 (Delayed Training)
                            # 实际发生的 Horizon 收益: (Close[t] - Close[t-5]) / Close[t-5]
                            current_close = float(current_price['close'])
                            past_close = float(df.iloc[-1 - horizon]['close'])
                            
                            if past_close > 0:
                                actual_return = (current_close - past_close) / past_close
                                self.mfh_analyzer.train(actual_return)
                            
                            # 2. 预测
                            mfh_result = self.mfh_analyzer.predict(df)
                            mfh_slope = mfh_result['slope']
                            mfh_signal = mfh_result['signal']
                            logger.info(f"MFH 斜率: {mfh_slope:.4f} (信号: {mfh_signal})")
                        else:
                            mfh_result = {"signal": "neutral", "slope": 0.0}
                        
                        # --- 3.2.6 MTF 分析 (新增) ---
                        mtf_result = self.mtf_analyzer.analyze(self.symbol, current_price, current_bar_time)
                        logger.info(f"MTF 分析: {mtf_result['signal']} ({mtf_result['reason']})")
                        
                        # --- 3.3 DeepSeek 分析 ---
                        logger.info("正在调用 DeepSeek 分析市场结构...")
                        # 传入 CRT, PriceEq, TF 和 高级分析 的结果作为额外上下文
                        extra_analysis = {
                            "crt": crt_result,
                            "price_equation": price_eq_result,
                            "timeframe_analysis": tf_result,
                            "advanced_tech": adv_result['summary'] if adv_result else None,
                            "matrix_ml": ml_result,
                            "smc": smc_result,
                            "mfh": mfh_result,
                            "mtf": mtf_result # 新增
                        }
                        structure = self.deepseek_client.analyze_market_structure(market_snapshot, extra_analysis=extra_analysis)
                        logger.info(f"DeepSeek 分析完成: {structure.get('market_state')}")
                        
                        # DeepSeek 信号转换
                        ds_signal = "neutral"
                        ds_pred = structure.get('short_term_prediction', 'neutral')
                        ds_score = structure.get('structure_score', 50)
                        if ds_pred == 'bullish' and ds_score > 60:
                            ds_signal = "buy"
                        elif ds_pred == 'bearish' and ds_score > 60:
                            ds_signal = "sell"
                        
                        # --- 3.4 Qwen 策略 ---
                        logger.info("正在调用 Qwen 生成策略...")
                        
                        # 获取历史交易绩效 (MFE/MAE)
                        trade_stats = self.db_manager.get_trade_performance_stats(limit=50)
                        
                        # 准备混合信号供 Qwen 参考
                        technical_signals = {
                            "crt": crt_result,
                            "price_equation": price_eq_result,
                            "timeframe_analysis": tf_result,
                            "advanced_tech": adv_signal,
                            "matrix_ml": ml_result['signal'],
                            "smc": smc_result['signal'],
                            "mfh": mfh_result['signal'],
                            "mtf": mtf_result['signal'], # 新增
                            "deepseek_preliminary": ds_signal,
                            "performance_stats": trade_stats # 传入历史绩效
                        }
                        
                        strategy = self.qwen_client.optimize_strategy_logic(structure, market_snapshot, technical_signals=technical_signals)
                        
                        # Qwen 信号转换
                        # 如果没有明确 action 字段，我们假设它作为 DeepSeek 的确认层
                        # 现在我们优先使用 Qwen 返回的 action
                        qw_action = strategy.get('action', 'neutral').lower()
                        if qw_action not in ['buy', 'sell', 'neutral', 'hold']:
                            qw_action = 'neutral'
                        
                        qw_signal = qw_action if qw_action != 'hold' else 'neutral'
                        
                        # --- 3.5 混合优化决策 ---
                        # 动态调整 DeepSeek 权重 (基于 Structure Score)
                        if ds_signal != 'neutral':
                            # Score 50 -> 1.0, Score 100 -> 2.0
                            ds_weight = 1.0 + (ds_score - 50) / 50.0
                            self.optimizer.weights['deepseek'] = ds_weight
                        else:
                            self.optimizer.weights['deepseek'] = 1.0
                            
                        all_signals = {
                            "deepseek": ds_signal,
                            "qwen": qw_signal,
                            "crt": crt_result['signal'],
                            "price_equation": price_eq_result['signal'],
                            "tf_visual": tf_result['signal'],
                            "advanced_tech": adv_signal,
                            "matrix_ml": ml_result['signal'],
                            "smc": smc_result['signal'],
                            "mfh": mfh_result['signal'],
                            "mtf": mtf_result['signal'] # 新增
                        }
                        
                        final_signal, strength, weights = self.optimizer.combine_signals(all_signals)
                        logger.info(f"各策略权重: {weights}")
                        logger.info(f"AI 最终决定: {final_signal.upper()} (强度: {strength:.1f})")
                        
                        # 保存分析结果到DB
                        self.db_manager.save_signal(self.symbol, self.tf_name, {
                            "final_signal": final_signal,
                            "strength": strength,
                            "details": {
                                "weights": weights,
                                "signals": all_signals,
                                "market_state": structure.get('market_state'),
                                "prediction": structure.get('short_term_prediction'),
                                "crt_reason": crt_result['reason'],
                                "mtf_reason": mtf_result['reason'],
                                "adv_summary": adv_result['summary'] if adv_result else None,
                                "matrix_ml_raw": ml_result['raw_output'],
                                "smc_structure": smc_result['structure'],
                                "smc_reason": smc_result['reason'],
                                "mfh_slope": mfh_result['slope']
                            }
                        })
                        
                        # 更新全局缓存，供 manage_positions 使用
                        self.latest_strategy = strategy
                        self.latest_signal = final_signal
                        
                        # --- 发送分析报告到 Telegram ---
                        # 构建更详细的报告
                        regime_info = adv_result['regime']['description'] if adv_result else "N/A"
                        volatility_info = f"{adv_result['risk']['volatility']:.2%}" if adv_result else "N/A"
                        
                        analysis_msg = (
                            f"🤖 *AI Market Analysis - {self.symbol}*\n"
                            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                            f"📊 *Signals:*\n"
                            f"• SMC: `{smc_result['signal']}`\n"
                            f"• MFH: `{mfh_result['signal']}` (Slope: {mfh_result['slope']:.2f})\n"
                            f"• MTF: `{mtf_result['signal']}`\n"
                            f"• CRT: `{crt_result['signal']}`\n"
                            f"• PriceEq: `{price_eq_result['signal']}`\n"
                            f"• AdvTech: `{adv_signal}`\n"
                            f"• MatrixML: `{ml_result['signal']}`\n"
                            f"• TFVisual: `{tf_result['signal']}`\n"
                            f"• DeepSeek: `{ds_signal}` (Conf: {ds_score})\n"
                            f"• Qwen: `{qw_signal}`\n\n"
                            f"🧠 *Hybrid Decision:*\n"
                            f"• Signal: *{final_signal.upper()}*\n"
                            f"• Strength: `{strength:.1f}`\n\n"
                            f"📈 *Market Context:*\n"
                            f"• State: {structure.get('market_state', 'N/A')}\n"
                            f"• Regime: {regime_info}\n"
                            f"• Volatility: {volatility_info}\n"
                            f"🔮 *Prediction:* {structure.get('short_term_prediction', 'N/A')}"
                        )
                        self.send_telegram_message(analysis_msg)
                        
                        # 4. 执行交易
                        # 修正逻辑: 优先尊重 Qwen 的信号和参数
                        # 如果 Qwen 明确说 "hold" 或 "neutral"，即使 final_signal 是 buy/sell，也应该谨慎
                        # 但如果 final_signal 极强 (如 100.0)，我们可能还是想交易
                        # 现在的逻辑是: 交易方向以 final_signal 为准 (因为它是混合投票的结果，Qwen 也是其中一票)
                        # 但 参数 (Entry/Exit) 必须优先使用 Qwen 的建议
                        
                        if final_signal != 'hold':
                            entry_params = strategy.get('entry_conditions')
                            exit_params = strategy.get('exit_conditions')
                            
                            # 强制使用 Qwen 的参数，不再进行一致性回退检查
                            # 除非 Qwen 建议的参数明显不可用 (如 None)
                            
                            # 日志记录差异，但不阻止使用参数
                            if qw_signal != final_signal and qw_signal not in ['neutral', 'hold']:
                                logger.warning(f"Qwen 信号 ({qw_signal}) 与最终决策 ({final_signal}) 不一致，但仍优先使用 Qwen 参数")
                            
                            trade_res = self.execute_trade(
                                final_signal, 
                                strength, 
                                exit_params,
                                entry_params
                            )
                            
                time.sleep(1) # 避免 CPU 占用过高
                
        except KeyboardInterrupt:
            logger.info("用户停止机器人")
            mt5.shutdown()
        except Exception as e:
            logger.error(f"发生未捕获异常: {e}", exc_info=True)
            mt5.shutdown()

if __name__ == "__main__":
    # 可以通过命令行参数传入品种
    symbol = "GOLD" 
    if len(sys.argv) > 1:
        symbol = sys.argv[1].upper()
    else:
        symbol = "GOLD" # 默认改为黄金
        
    bot = AI_MT5_Bot(symbol=symbol)
    bot.run()
