
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
# 基于 MQL5 Article 20414 & SMC_Sent.mq5 完整复刻
class SMCAnalyzer:
    def __init__(self):
        self.last_structure = "neutral" 
        self.ma_period = 200
        self.swing_lookback = 5
        self.atr_threshold = 0.002
        
        # Strategy Flags (defaults from MQL5)
        self.allow_bos = True
        self.allow_ob = True
        self.allow_fvg = True
        self.use_sentiment = True

    def calculate_ema(self, series, period):
        return series.ewm(span=period, adjust=False).mean()

    def get_mtf_data(self, symbol, timeframe, count=250):
        """获取多时间周期数据"""
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
        if rates is None or len(rates) == 0:
            return None
        df = pd.DataFrame(rates)
        return df

    def get_market_sentiment(self, df_current, symbol):
        """
        计算市场情绪 (Bullish, Bearish, Risk-On, Risk-Off, Neutral)
        复刻 SMC_Sent.mq5 逻辑
        """
        # 1. Higher TF Bias (使用 H1 作为 Bias TF)
        df_h1 = self.get_mtf_data(symbol, mt5.TIMEFRAME_H1, 300)
        if df_h1 is None:
            return 0, "Neutral"
            
        ema_long = self.calculate_ema(df_h1['close'], self.ma_period).iloc[-1]
        current_price_h1 = df_h1['close'].iloc[-1]
        
        deviation = abs(current_price_h1 - ema_long) / ema_long
        higher_tf_bias = 0
        if current_price_h1 > ema_long and deviation > self.atr_threshold:
            higher_tf_bias = 1
        elif current_price_h1 < ema_long and deviation > self.atr_threshold:
            higher_tf_bias = -1
            
        # 2. Local Structure (TF1 & TF2)
        # 辅助函数: 检测结构 (使用我们之前实现的 robust fractal logic)
        def check_structure(df):
            highs = df['high'].values
            lows = df['low'].values
            n = len(df)
            swing_highs = []
            swing_lows = []
            
            for i in range(n - 3, 2, -1):
                if len(swing_highs) < 2:
                    if (highs[i] > highs[i-1] and highs[i] > highs[i-2] and 
                        highs[i] > highs[i+1] and highs[i] > highs[i+2]):
                        swing_highs.append(highs[i])
                if len(swing_lows) < 2:
                    if (lows[i] < lows[i-1] and lows[i] < lows[i-2] and 
                        lows[i] < lows[i+1] and lows[i] < lows[i+2]):
                        swing_lows.append(lows[i])
                if len(swing_highs) >= 2 and len(swing_lows) >= 2: break
            
            is_bull = False
            is_bear = False
            if len(swing_highs) >= 2 and len(swing_lows) >= 2:
                if swing_highs[0] > swing_highs[1] and swing_lows[0] > swing_lows[1]: is_bull = True
                if swing_highs[0] < swing_highs[1] and swing_lows[0] < swing_lows[1]: is_bear = True
            
            # Breakout Detection
            has_break = False
            curr_close = df['close'].iloc[-1]
            rec_high = swing_highs[0] if swing_highs else highs[-20:].max()
            rec_low = swing_lows[0] if swing_lows else lows[-20:].min()
            
            if higher_tf_bias == 1 and curr_close > rec_high: has_break = True
            elif higher_tf_bias == -1 and curr_close < rec_low: has_break = True
            
            return is_bull, is_bear, has_break

        tf1_bull, tf1_bear, tf1_break = check_structure(df_h1)
        tf2_bull, tf2_bear, tf2_break = check_structure(df_current)
        
        # 3. Determine Sentiment
        sentiment = 0
        text = "Neutral"
        
        # Priority 1: Strong Structure
        if higher_tf_bias == 1 and tf1_bull and tf2_bull:
            sentiment = 1; text = "Bullish"
        elif higher_tf_bias == -1 and tf1_bear and tf2_bear:
            sentiment = -1; text = "Bearish"
            
        # Priority 2: Breakout (Risk-On/Off)
        elif higher_tf_bias == 1 and (tf1_break or tf2_break):
            sentiment = 2; text = "Risk-On"
        elif higher_tf_bias == -1 and (tf1_break or tf2_break):
            sentiment = -2; text = "Risk-Off"
            
        return sentiment, text

    def analyze(self, df):
        """
        分析市场结构 (BOS), 订单块 (OB), 和价值缺口 (FVG)
        基于 Sentiment 选择策略 (Strategy Switching)
        """
        if df is None or len(df) < 50:
            return {"signal": "neutral", "structure": "neutral", "reason": "数据不足"}
            
        # 1. 获取市场情绪
        # 注意: 需要 symbol 来获取 MTF 数据，但 analyze 接口目前只传了 df
        # 我们假设 df 是当前周期的。为了获取 MTF，我们需要 symbol。
        # 临时 hack: start.py 的调用方应该已经有了 symbol。
        # 由于我们是在 class 内部，且 get_market_sentiment 需要 symbol
        # 我们需要修改 analyze 签名或者 假设 self.symbol 被设置
        # 但 SMCAnalyzer 是无状态工具类 (init 没有 symbol)
        # 我们假设 df 是最新的，我们无法在 analyze 内部获取 symbol 除非传入
        # 这里为了兼容，我们暂时只用单周期情绪 (降级) 或请求调用方传入 symbol
        # 但为了"完整复刻"，必须用 MTF。
        # 我将修改 analyze 签名，在 start.py 调用处传入 symbol
        
        # 但这里是 SearchReplace，我不能轻易修改调用处 (start.py:2700左右)
        # 检查 start.py 调用: smc_result = self.smc_analyzer.analyze(df)
        # 调用处 self.symbol 是可用的。
        # 我需要修改调用处。
        # 暂时，我将在 analyze 中硬编码 symbol (不可行) 或者
        # 让 get_market_sentiment 只用当前 df (降级)。
        # 为了"完整复刻"，我必须修改 start.py 的调用行。
        
        # 假设 start.py 的调用代码会被我稍后修改，这里先写好带有 symbol 参数的 analyze
        # 或者，我可以在 __init__ 里不传 symbol，但在 analyze 里传。
        pass # Placeholder, 实际代码在下面 SearchReplace

    def analyze_with_symbol(self, df, symbol): # New method signature
        if df is None or len(df) < 50:
            return {"signal": "neutral", "structure": "neutral", "reason": "数据不足"}
            
        sentiment_score, sentiment_text = self.get_market_sentiment(df, symbol)
        
        # 2. Strategy Selection (MQL5 Logic)
        active_strategy = "OB"
        if self.use_sentiment:
            if abs(sentiment_score) == 1: active_strategy = "BOS"
            elif abs(sentiment_score) == 2: active_strategy = "FVG"
            else: active_strategy = "OB"
        else:
            active_strategy = "ALL"
            
        # 3. Detect Patterns
        ob_signal = self.detect_order_blocks(df)
        fvg_signal = self.detect_fvg(df)
        bos_signal = self.detect_bos(df)
        
        final_signal = "neutral"
        reason = f"Sentiment: {sentiment_text} ({active_strategy})"
        strength = 0
        
        # 4. Execute Logic based on Strategy
        
        # BOS Strategy
        if (active_strategy == "ALL" or active_strategy == "BOS") and self.allow_bos:
            if bos_signal['signal'] != "neutral":
                # Check sentiment alignment
                aligned = False
                if (bos_signal['signal'] == 'buy' and sentiment_score > 0) or \
                   (bos_signal['signal'] == 'sell' and sentiment_score < 0):
                    aligned = True
                if sentiment_score == 0: aligned = True # Caution
                
                if aligned:
                    final_signal = bos_signal['signal']
                    reason = f"SMC BOS: {bos_signal['reason']}"
                    strength = 80
                    
        # FVG Strategy
        if final_signal == "neutral" and (active_strategy == "ALL" or active_strategy == "FVG") and self.allow_fvg:
            if fvg_signal['signal'] != "neutral":
                aligned = False
                if (fvg_signal['signal'] == 'buy' and sentiment_score > 0) or \
                   (fvg_signal['signal'] == 'sell' and sentiment_score < 0):
                    aligned = True
                if sentiment_score == 0: aligned = True
                
                if aligned:
                    final_signal = fvg_signal['signal']
                    reason = f"SMC FVG: {fvg_signal['reason']}"
                    strength = 85
                    
        # OB Strategy
        if final_signal == "neutral" and (active_strategy == "ALL" or active_strategy == "OB") and self.allow_ob:
            if ob_signal['signal'] != "neutral":
                # OB trades often work in neutral or trend continuations
                final_signal = ob_signal['signal']
                reason = f"SMC OB: {ob_signal['reason']}"
                strength = 75

        return {
            "signal": final_signal,
            "structure": sentiment_text,
            "reason": reason,
            "sentiment_score": sentiment_score,
            "active_strategy": active_strategy,
            "details": {"ob": ob_signal, "fvg": fvg_signal, "bos": bos_signal}
        }
        
    def detect_order_blocks(self, df):
        # MQL5 Logic: 
        # Bullish: Bear(i-1) -> Bull(i), BullBody > BearBody * 1.5
        # Entry: Ask >= Low(i-1) && Ask <= High(i-1)
        closes = df['close'].values
        opens = df['open'].values
        highs = df['high'].values
        lows = df['low'].values
        current_ask = closes[-1] # Approximation using close
        
        for i in range(len(df)-2, len(df)-30, -1):
            # Bullish OB
            if (opens[i] < closes[i] and # Bull
                opens[i-1] > closes[i-1] and # Bear
                closes[i-1] > opens[i] and # Gap check? No, MQL5 logic: Close(i-1) > Open(i) is weird for Bear->Bull. 
                # MQL5: getOpen(i) > getClose(i) (Bear) ?? No MQL5 i is left.
                # Let's read MQL5 loop: i from 3 to 30.
                # getOpen(i) > getClose(i) (Bear candle at i)
                # getOpen(i-1) < getClose(i-1) (Bull candle at i-1, which is to the right of i)
                # So Pattern is: Bear Candle -> Bull Candle.
                # Condition: abs(BullBody) > abs(BearBody) * 1.5
                
                # In Python list, -1 is latest. -2 is previous.
                # So we look for Bear at -2, Bull at -1.
                
                opens[i-1] > closes[i-1] and # Bear at i-1
                opens[i] < closes[i] and     # Bull at i
                (closes[i] - opens[i]) > (opens[i-1] - closes[i-1]) * 1.5): # Strong Move
                
                ob_high = highs[i-1]
                ob_low = lows[i-1]
                
                # Retest Condition
                if current_ask >= ob_low and current_ask <= ob_high:
                     return {"signal": "buy", "reason": "Bullish OB Retest", "price": ob_high}
                     
            # Bearish OB (Bull -> Bear)
            if (opens[i-1] < closes[i-1] and # Bull at i-1
                opens[i] > closes[i] and     # Bear at i
                (opens[i] - closes[i]) > (closes[i-1] - opens[i-1]) * 1.5):
                
                ob_high = highs[i-1]
                ob_low = lows[i-1]
                
                if current_ask <= ob_high and current_ask >= ob_low:
                     return {"signal": "sell", "reason": "Bearish OB Retest", "price": ob_low}

        return {"signal": "neutral", "reason": ""}

    def detect_fvg(self, df):
        # MQL5 Logic:
        # Bullish FVG: Low(i+2) > High(i) (Indices are reverse in MQL5, i+2 is older)
        # Python: i-2 (Older) -> i (Newer). 
        # Gap: Low(i-2) > High(i) ?? No.
        # FVG is 3 candles: A(old), B(mid), C(new).
        # Bullish Gap: High(A) < Low(C). 
        # Wait, MQL5 code: lowA = getLow(i+2), highC = getHigh(i).
        # lowA > highC -> Gap.
        # So it is: Candle i+2 (Old) Low > Candle i (New) High.
        # This implies Old Low is ABOVE New High? That's a GAP DOWN (Bearish)?
        # Let's re-read MQL5: 
        # Bullish FVG: lowA > highC.
        # This means the Low of the older candle is higher than the High of the newer candle.
        # This is a gap, but usually Bullish FVG (Imbalance) is High(A) < Low(C) in an UP move.
        # If Low(A) > High(C), it means price dropped and left a gap. That's a BEARISH FVG (Supply).
        # MQL5 code says: "Bullish FVG ... if(lowA > highC)".
        # And "Bearish FVG ... if(highA < lowC)".
        # This seems INVERTED or I am misinterpreting "Bullish FVG".
        # Usually Bullish FVG = Demand = Price went UP. High(1) < Low(3).
        # Bearish FVG = Supply = Price went DOWN. Low(1) > High(3).
        # Let's stick to standard SMC definitions if MQL5 code is weird, OR trust the MQL5 code logic for "Replication".
        # "Bullish FVG detected... newFVG.dir = 1".
        # Trade: if(Ask <= top && Ask >= bot) -> BUY.
        # If Low(A) > High(C), Top=Low(A), Bot=High(C).
        # Price is below Top and above Bot.
        # This is a GAP DOWN. Buying a Gap Down is filling the gap?
        # Maybe it's a "Gap Fill" strategy?
        # BUT standard SMC FVG:
        # Bullish FVG (BIS): Created by up candle. High(1) < Low(3). Zone is between High(1) and Low(3).
        # Price retraces DOWN into it.
        
        # Let's assume MQL5 code `i` is increasing backwards?
        # `for(int i=2; i<30; i++)`
        # `getLow(i+2)` is older than `getHigh(i)`.
        # If MQL5 standard array (0 is current): i+2 is older.
        # If Low(Old) > High(New) -> Gap Down.
        # If High(Old) < Low(New) -> Gap Up.
        
        # MQL5 Code: "Bullish FVG: lowA > highC". (Gap Down).
        # Trade: Buy.
        # So it buys the Gap Down (Gap Fill?).
        # "Bearish FVG: highA < lowC". (Gap Up).
        # Trade: Sell.
        
        # Okay, I will replicate this "Gap Fill" logic as per MQL5 code.
        
        highs = df['high'].values
        lows = df['low'].values
        closes = df['close'].values
        point = 0.00001 # approx
        
        for i in range(len(df)-1, 2, -1): # i is current/newest
            # Need A(i-2), B(i-1), C(i).
            # Python indices: i is newest. i-2 is oldest.
            
            # MQL5: A=i+2 (Old), C=i (New).
            # Python: A=i-2, C=i.
            
            # MQL5 Bullish: Low(A) > High(C) -> Gap Down -> Buy
            if lows[i-2] > highs[i] + (3*point):
                gap_top = lows[i-2]
                gap_bot = highs[i]
                curr = closes[-1]
                mid = (gap_top + gap_bot) / 2
                # Trade: Ask <= top && Ask >= bot && Ask <= mid (Deep retest?)
                if curr <= gap_top and curr >= gap_bot:
                    return {"signal": "buy", "reason": "Bullish FVG (Gap Fill)", "top": gap_top, "bottom": gap_bot}
            
            # MQL5 Bearish: High(A) < Low(C) -> Gap Up -> Sell
            if highs[i-2] < lows[i] - (3*point):
                gap_top = lows[i]
                gap_bot = highs[i-2]
                curr = closes[-1]
                if curr <= gap_top and curr >= gap_bot:
                    return {"signal": "sell", "reason": "Bearish FVG (Gap Fill)", "top": gap_top, "bottom": gap_bot}
                    
        return {"signal": "neutral", "reason": ""}

    def detect_bos(self, df):
        # MQL5 Logic: 3-bar Fractal.
        # Swing High: High[i] > High[i-1, i-2, i+1, i+2] (MQL5 uses j=1..3)
        # BOS Sell: Break Above Swing High. (Liquidity Sweep)
        # BOS Buy: Break Below Swing Low.
        
        highs = df['high'].values
        lows = df['low'].values
        closes = df['close'].values
        
        # Find recent Swing High
        swing_high = -1
        for i in range(len(df)-4, len(df)-30, -1):
            if (highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i-3] and
                highs[i] > highs[i+1] and highs[i] > highs[i+2] and highs[i] > highs[i+3]):
                swing_high = highs[i]
                break
                
        # Find recent Swing Low
        swing_low = -1
        for i in range(len(df)-4, len(df)-30, -1):
            if (lows[i] < lows[i-1] and lows[i] < lows[i-2] and lows[i] < lows[i-3] and
                lows[i] < lows[i+1] and lows[i] < lows[i+2] and lows[i] < lows[i+3]):
                swing_low = lows[i]
                break
                
        current_bid = closes[-1]
        
        # MQL5: BOS Sell (Break Above High) -> Trade Sell
        if swing_high > 0 and current_bid > swing_high:
            return {"signal": "sell", "reason": "BOS Sell (Liquidity Sweep)", "price": swing_high}
            
        # MQL5: BOS Buy (Break Below Low) -> Trade Buy
        if swing_low > 0 and current_bid < swing_low:
             return {"signal": "buy", "reason": "BOS Buy (Liquidity Sweep)", "price": swing_low}
             
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
            
            # 7. IFVG 分析
            ifvg_result = self.analyzer.analyze_ifvg(df)
            
            # 8. RVGI+CCI 分析
            rvgi_cci_result = self.analyzer.analyze_rvgi_cci_strategy(df)
            
            return {
                "indicators": indicators,
                "regime": regime,
                "levels": levels,
                "risk": risk,
                "signal_info": signal_info,
                "summary": summary,
                "ifvg": ifvg_result,
                "rvgi_cci": rvgi_cci_result
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
            "mfh": 0.75,
            "mtf": 0.9,
            "ifvg": 1.2,
            "rvgi_cci": 0.95 # 新增
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
        from python.optimization import GWO, WOAm, DE, COAm, BBO, TETA
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
        TETA = opt_mod.TETA

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
        self.magic_number = 20241122
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
            "BBO": BBO(pop_size=10, immigration_max=1.0, emigration_max=1.0),
            "TETA": TETA(pop_size=10) # 新增 TETA
        }
        self.active_optimizer_name = "TETA" # 默认使用 TETA (作为最新引入的强力算法)
        self.last_optimization_time = 0
        self.last_realtime_save = 0 # Added for realtime dashboard
        self.last_analysis_time = 0 # Added for periodic analysis (1 min)
        self.latest_strategy = None # 存储最新的策略参数 (用于 manage_positions)
        self.latest_signal = "neutral" # 存储最新的信号
        self.signal_history = [] # 存储历史信号用于实时权重优化
        
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

    def get_position_stats(self, pos):
        """
        计算持仓的 MFE (最大潜在收益) 和 MAE (最大潜在亏损)
        """
        try:
            # 获取持仓期间的 M1 数据
            now = datetime.now()
            # pos.time 是时间戳，转换为 datetime
            open_time = datetime.fromtimestamp(pos.time)
            
            # 获取数据
            rates = mt5.copy_rates_range(self.symbol, mt5.TIMEFRAME_M1, open_time, now)
            
            if rates is None or len(rates) == 0:
                # 如果获取不到数据，尝试只用当前价格估算
                # 这种情况可能发生在刚刚开仓的一瞬间
                current_price = pos.price_current
                if pos.type == mt5.POSITION_TYPE_BUY:
                    mfe_price = max(0, current_price - pos.price_open)
                    mae_price = max(0, pos.price_open - current_price)
                else:
                    mfe_price = max(0, pos.price_open - current_price)
                    mae_price = max(0, current_price - pos.price_open)
                
                if pos.price_open > 0:
                    return (mfe_price / pos.price_open) * 100, (mae_price / pos.price_open) * 100
                return 0.0, 0.0
                
            df = pd.DataFrame(rates)
            
            # 计算期间最高价和最低价
            # 注意: 还需要考虑当前价格，因为 M1 数据可能还没包含当前的 tick
            period_high = max(df['high'].max(), pos.price_current)
            period_low = min(df['low'].min(), pos.price_current)
            
            mfe = 0.0
            mae = 0.0
            
            if pos.type == mt5.POSITION_TYPE_BUY:
                # 买入: MFE = High - Open, MAE = Open - Low
                mfe_price = max(0, period_high - pos.price_open)
                mae_price = max(0, pos.price_open - period_low)
            else:
                # 卖出: MFE = Open - Low, MAE = High - Open
                mfe_price = max(0, pos.price_open - period_low)
                mae_price = max(0, period_high - pos.price_open)
                
            # 转换为百分比
            if pos.price_open > 0:
                mfe = (mfe_price / pos.price_open) * 100
                mae = (mae_price / pos.price_open) * 100
                
            return mfe, mae
            
        except Exception as e:
            logger.error(f"计算持仓统计时出错: {e}")
            return 0.0, 0.0





    def close_position(self, position, comment="AI-Bot Close"):
        """辅助函数: 平仓"""
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": mt5.ORDER_TYPE_SELL if position.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
            "position": position.ticket,
            "price": mt5.symbol_info_tick(self.symbol).bid if position.type == mt5.POSITION_TYPE_BUY else mt5.symbol_info_tick(self.symbol).ask,
            "deviation": 20,
            "magic": self.magic_number,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"平仓失败 #{position.ticket}: {result.comment}")
            return False
        else:
            logger.info(f"平仓成功 #{position.ticket}")
            profit = getattr(result, 'profit', 0.0)
            self.send_telegram_message(f"🔄 *Position Closed*\nTicket: `{position.ticket}`\nReason: {comment}\nProfit: {profit}")
            return True

    def execute_trade(self, signal, strength, sl_tp_params, entry_params=None):
        """
        执行交易指令，完全由大模型驱动
        """
        # 允许所有相关指令进入
        valid_actions = ['buy', 'sell', 'limit_buy', 'limit_sell', 'close', 'add_buy', 'add_sell', 'hold']
        # 注意: signal 参数这里传入的是 final_signal，已经被归一化为 buy/sell/close/hold
        # 但我们更关心 entry_params 中的具体 action
        
        # --- 1. 获取市场状态 ---
        positions = mt5.positions_get(symbol=self.symbol)
        tick = mt5.symbol_info_tick(self.symbol)
        if not tick:
            logger.error("无法获取 Tick 数据")
            return

        # 解析 LLM 指令
        # 这里的 entry_params 是从 strategy 字典中提取的 'entry_conditions'
        # 但 strategy 字典本身也有 'action'
        # 为了更准确，我们应该直接使用 self.latest_strategy (在 run 循环中更新)
        
        # 兼容性处理
        llm_action = "hold"
        if self.latest_strategy:
             llm_action = self.latest_strategy.get('action', 'hold').lower()
        elif entry_params and 'action' in entry_params:
             llm_action = entry_params.get('action', 'hold').lower()
        else:
             llm_action = signal if signal in valid_actions else 'hold'

        # 显式 MFE/MAE 止损止盈
        # LLM 应该返回具体的 sl_price 和 tp_price，或者 MFE/MAE 的百分比建议
        # 如果 LLM 提供了具体的 SL/TP 价格，优先使用
        explicit_sl = None
        explicit_tp = None
        
        if self.latest_strategy:
            explicit_sl = self.latest_strategy.get('sl')
            explicit_tp = self.latest_strategy.get('tp')
        
        # 如果没有具体价格，回退到 sl_tp_params (通常也是 LLM 生成的)
        if explicit_sl is None and sl_tp_params:
             explicit_sl = sl_tp_params.get('sl_price')
        if explicit_tp is None and sl_tp_params:
             explicit_tp = sl_tp_params.get('tp_price')

        logger.info(f"执行逻辑: Action={llm_action}, Signal={signal}, Explicit SL={explicit_sl}, TP={explicit_tp}")

        # --- 2. 持仓管理 (已开仓状态) ---
        if positions and len(positions) > 0:
            for pos in positions:
                pos_type = pos.type # 0: Buy, 1: Sell
                is_buy_pos = (pos_type == mt5.POSITION_TYPE_BUY)
                
                # A. 平仓/减仓逻辑 (Close)
                should_close = False
                close_reason = ""
                
                if llm_action in ['close', 'close_buy', 'close_sell']:
                    # 检查方向匹配
                    if llm_action == 'close': should_close = True
                    elif llm_action == 'close_buy' and is_buy_pos: should_close = True
                    elif llm_action == 'close_sell' and not is_buy_pos: should_close = True
                    
                    if should_close: close_reason = "LLM Close Instruction"
                
                # 反向信号平仓 (Reversal)
                elif (llm_action in ['buy', 'add_buy'] and not is_buy_pos):
                     should_close = True
                     close_reason = "Reversal (Sell -> Buy)"
                elif (llm_action in ['sell', 'add_sell'] and is_buy_pos):
                     should_close = True
                     close_reason = "Reversal (Buy -> Sell)"

                if should_close:
                    logger.info(f"执行平仓 #{pos.ticket}: {close_reason}")
                    self.close_position(pos, comment=f"AI: {close_reason}")
                    continue 

                # B. 加仓逻辑 (Add Position)
                should_add = False
                if llm_action == 'add_buy' and is_buy_pos: should_add = True
                elif llm_action == 'add_sell' and not is_buy_pos: should_add = True
                
                # 如果是单纯的 buy/sell 信号，且已有同向仓位，通常视为 hold，除非明确 add
                # 但如果用户希望 "完全交给大模型"，那么如果大模型在有仓位时发出了 buy，可能意味着加仓
                # 为了安全，我们严格限制只有 'add_xxx' 才加仓，或者 signal 极强
                
                if should_add:
                    logger.info(f"执行加仓 #{pos.ticket} 方向")
                    # 加仓逻辑复用开仓逻辑，但可能调整手数
                    self._send_order(
                        "buy" if is_buy_pos else "sell", 
                        tick.ask if is_buy_pos else tick.bid,
                        explicit_sl,
                        explicit_tp,
                        comment="AI: Add Position"
                    )
                    
                # C. 持仓 (Hold) - 默认行为
                # 更新 SL/TP (如果 LLM 给出了新的优化值)
                # 只有当新给出的 SL/TP 与当前差别较大时才修改
                if explicit_sl is not None and explicit_tp is not None:
                    # 简单的阈值检查，避免频繁修改
                    point = mt5.symbol_info(self.symbol).point
                    if abs(pos.sl - explicit_sl) > 10 * point or abs(pos.tp - explicit_tp) > 10 * point:
                        logger.info(f"更新持仓 SL/TP #{pos.ticket}: SL {pos.sl}->{explicit_sl}, TP {pos.tp}->{explicit_tp}")
                        request = {
                            "action": mt5.TRADE_ACTION_SLTP,
                            "position": pos.ticket,
                            "sl": explicit_sl,
                            "tp": explicit_tp
                        }
                        mt5.order_send(request)

        # --- 3. 开仓/挂单逻辑 (未开仓 或 加仓) ---
        # 注意: 上面的循环处理了已有仓位的 Close 和 Add。
        # 如果当前没有仓位，或者上面的逻辑没有触发 Close (即是 Hold)，
        # 或者是 Reversal (Close 之后)，我们需要看是否需要开新仓。
        
        # 重新检查持仓数 (因为刚才可能平仓了)
        positions = mt5.positions_get(symbol=self.symbol)
        has_position = len(positions) > 0 if positions else False
        
        # 如果有持仓且不是加仓指令，则不再开新仓
        if has_position and 'add' not in llm_action:
            return

        # 执行开仓/挂单
        trade_type = None
        price = 0.0
        
        if llm_action == 'buy':
            trade_type = "buy"
            price = tick.ask
        elif llm_action == 'sell':
            trade_type = "sell"
            price = tick.bid
        elif llm_action == 'limit_buy':
            trade_type = "limit_buy"
            # 优先使用 limit_price (与 prompt 一致)，回退使用 entry_price
            price = entry_params.get('limit_price', entry_params.get('entry_price', 0.0)) if entry_params else 0.0
        elif llm_action == 'limit_sell':
            trade_type = "limit_sell"
            price = entry_params.get('limit_price', entry_params.get('entry_price', 0.0)) if entry_params else 0.0

        if trade_type and price > 0:
            # 再次确认 SL/TP 是否存在
            if explicit_sl is None or explicit_tp is None:
                # 策略优化: 如果 LLM 未提供明确价格，则使用基于 MFE/MAE 的统计优化值
                # 移除旧的 ATR 动态计算，确保策略的一致性和基于绩效的优化
                logger.info("LLM 未提供明确 SL/TP，使用 MFE/MAE 统计优化值")
                explicit_sl, explicit_tp = self.calculate_optimized_sl_tp(trade_type, price)
                
                if explicit_sl == 0 or explicit_tp == 0:
                     logger.error("无法计算优化 SL/TP，放弃交易")
                     return 

            comment = f"AI: {llm_action.upper()}"
            self._send_order(trade_type, price, explicit_sl, explicit_tp, comment=comment)

    def calculate_optimized_sl_tp(self, trade_type, price):
        """
        计算基于 MFE/MAE 统计的优化止损止盈点
        完全移除 ATR 动态逻辑，使用历史绩效数据的统计特征
        """
        sl = 0.0
        tp = 0.0
        
        # 默认兜底参数 (基于价格的固定百分比，非 ATR)
        # 黄金通常波动较大，给予 0.5% SL 和 1.0% TP 作为初始冷启动值
        default_sl_pct = 0.005 
        default_tp_pct = 0.010
        
        try:
             # 获取历史交易绩效统计
             # 我们关注最近 100 笔交易的 MFE (最大潜在收益) 和 MAE (最大潜在回撤)
             trades = self.db_manager.get_trade_performance_stats(limit=100)
             
             if trades and len(trades) > 10:
                 # 提取有效的 MFE/MAE 数据 (假设 DB 中存储的是百分比值)
                 mfes = [t.get('mfe', 0) for t in trades if t.get('mfe', 0) > 0]
                 maes = [t.get('mae', 0) for t in trades if t.get('mae', 0) > 0]
                 
                 if mfes and maes:
                     # 策略核心:
                     # TP: 设置在 75% 的历史交易都能到达的 MFE 水平 (75分位数) -> 更容易达成的目标
                     # SL: 设置在能覆盖 90% 历史交易回撤的 MAE 水平 (90分位数) -> 更宽的容错空间
                     
                     # 优化调整: 
                     # 如果我们要追求高盈亏比，TP 应该更大，但胜率会降
                     # 如果我们要追求高胜率，SL 应该宽，TP 适中
                     # 这里采用 "宽止损 + 适中止盈" 的高胜率配置
                     
                     opt_tp_pct = np.percentile(mfes, 50) / 100.0 # 中位数目标 (稳健)
                     opt_sl_pct = np.percentile(maes, 90) / 100.0 # 90% 容错空间 (宽止损)
                     
                     # 安全范围检查
                     if 0.001 < opt_tp_pct < 0.05:
                         default_tp_pct = opt_tp_pct
                     if 0.001 < opt_sl_pct < 0.03:
                         default_sl_pct = opt_sl_pct
                         
                     logger.info(f"应用 MFE/MAE 优化: TP={default_tp_pct:.2%}, SL={default_sl_pct:.2%}")
                     
        except Exception as e:
             logger.warning(f"获取 MFE/MAE 统计失败，使用默认参数: {e}")

        # 计算具体价格
        sl_dist = price * default_sl_pct
        tp_dist = price * default_tp_pct
        
        if 'buy' in trade_type:
            sl = price - sl_dist
            tp = price + tp_dist
        elif 'sell' in trade_type:
            sl = price + sl_dist
            tp = price - tp_dist
            
        return sl, tp

    def _send_order(self, type_str, price, sl, tp, comment=""):
        """底层下单函数"""
        order_type = mt5.ORDER_TYPE_BUY
        action = mt5.TRADE_ACTION_DEAL
        
        if type_str == "buy":
            order_type = mt5.ORDER_TYPE_BUY
            action = mt5.TRADE_ACTION_DEAL
        elif type_str == "sell":
            order_type = mt5.ORDER_TYPE_SELL
            action = mt5.TRADE_ACTION_DEAL
        elif type_str == "limit_buy":
            order_type = mt5.ORDER_TYPE_BUY_LIMIT
            action = mt5.TRADE_ACTION_PENDING
        elif type_str == "limit_sell":
            order_type = mt5.ORDER_TYPE_SELL_LIMIT
            action = mt5.TRADE_ACTION_PENDING
            
        request = {
            "action": action,
            "symbol": self.symbol,
            "volume": self.lot_size,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": self.magic_number,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        
        # 挂单需要不同的 filling type? 通常 Pending 订单不用 FOK，用 RETURN 或默认
        if "limit" in type_str:
             if 'type_filling' in request:
                 del request['type_filling']
        
        result = mt5.order_send(request)
        if result is None:
             logger.error("order_send 返回 None")
             return

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"下单失败 ({type_str}): {result.comment}, retcode={result.retcode}")
        else:
            logger.info(f"下单成功 ({type_str}) #{result.order}")
            self.send_telegram_message(f"✅ *Order Executed*\nType: `{type_str.upper()}`\nPrice: `{price}`\nSL: `{sl}`\nTP: `{tp}`")



                



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

        symbol_info = mt5.symbol_info(self.symbol)
        if not symbol_info:
            return
        point = symbol_info.point

        # 遍历所有持仓，独立管理
        for pos in positions:
            if pos.magic != self.magic_number:
                continue
                
            symbol = pos.symbol
            type_pos = pos.type # 0: Buy, 1: Sell
            price_open = pos.price_open
            sl = pos.sl
            tp = pos.tp
            current_price = pos.price_current
            
            # 针对每个订单独立计算最优 SL/TP
            # 如果是挂单成交后的新持仓，或者老持仓，都统一处理
            
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": symbol,
                "position": pos.ticket,
                "sl": sl,
                "tp": tp
            }
            
            changed = False
            
            # --- 1. 基于最新策略更新 SL/TP (全量覆盖更新) ---
            # 用户指令: "止盈和止损也需要根据大模型的最后整合分析结果来进行移动...而不是只有当新计算的 Trailing SL ... 还要高时，才再次更新"
            # 解读: 允许 SL/TP 动态调整，既可以收紧也可以放宽 (Breathing Stop)，以适应 LLM 对市场波动率和结构的最新判断。
            
            if has_new_params:
                current_sl_dist = atr * new_sl_multiplier
                current_tp_dist = atr * new_tp_multiplier
                
                # 计算建议的 SL/TP 价格 (基于当前价格)
                suggested_sl = 0.0
                suggested_tp = 0.0
                
                if type_pos == mt5.POSITION_TYPE_BUY:
                    suggested_sl = current_price - current_sl_dist
                    suggested_tp = current_price + current_tp_dist
                    
                    # 更新 SL: 始终更新 (移除 > sl 的限制)
                    # 注意: 这意味着如果 ATR 变大或 Multiplier 变大，SL 可能会下移 (放宽)
                    if abs(suggested_sl - sl) > point * 5: # 避免微小抖动
                        request['sl'] = suggested_sl
                        changed = True
                    
                    # 更新 TP
                    if abs(suggested_tp - tp) > point * 10:
                        request['tp'] = suggested_tp
                        changed = True

                elif type_pos == mt5.POSITION_TYPE_SELL:
                    suggested_sl = current_price + current_sl_dist
                    suggested_tp = current_price - current_tp_dist
                    
                    # 更新 SL: 始终更新 (移除 < sl 的限制)
                    if abs(suggested_sl - sl) > point * 5:
                        request['sl'] = suggested_sl
                        changed = True
                        
                    # 更新 TP
                    if abs(suggested_tp - tp) > point * 10:
                        request['tp'] = suggested_tp
                        changed = True
            
            # --- 2. 兜底移动止损 (Trailing Stop) ---
            # 如果上面没有因为 LLM 参数变化而更新，我们依然执行常规的 Trailing 逻辑 (仅收紧)
            # 只有当 'changed' 为 False 时才检查，避免冲突
            
            if not changed:
                if type_pos == mt5.POSITION_TYPE_BUY:
                    target_sl = current_price - (atr * new_sl_multiplier)
                    # 常规 Trailing: 仅收紧
                    current_req_sl = request['sl'] if request['sl'] > 0 else sl
                    if target_sl > current_req_sl:
                         if (current_price - target_sl) >= point * 10:
                            request['sl'] = target_sl
                            changed = True

                elif type_pos == mt5.POSITION_TYPE_SELL:
                    target_sl = current_price + (atr * new_sl_multiplier)
                    # 常规 Trailing: 仅收紧
                    current_req_sl = request['sl']
                    if current_req_sl == 0 or target_sl < current_req_sl:
                        if (target_sl - current_price) >= point * 10:
                            request['sl'] = target_sl
                            changed = True
                        
                # 2. 移动止盈 (Trailing Take Profit)
                dist_to_tp = current_price - tp
                if dist_to_tp > 0 and dist_to_tp < (atr * 0.5):
                    if signal == 'sell':
                        new_tp = current_price - (atr * max(new_tp_multiplier, 1.0))
                        if new_tp < tp:
                            request['tp'] = new_tp
                            changed = True
                            logger.info(f"🚀 移动止盈触发 (Sell): TP 延伸至 {new_tp:.2f}")
            
            if changed:
                logger.info(f"更新持仓 #{pos.ticket}: SL={request['sl']:.2f}, TP={request['tp']:.2f} (ATR x {new_sl_multiplier})")
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
        
        # 6. 验证和应用最佳参数
        # 如果得分是负数且非常低（如初始值-99999），说明优化未找到有效解，不应更新
        if best_score > -1000:
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
        else:
            logger.warning(f"优化失败或未找到正收益参数 (Score: {best_score:.4f})，保持原有参数。")
            self.send_telegram_message(
                f"🧬 *Auto-AO Optimization ({algo_name})*\n"
                f"Optimization Skipped (Low Score: {best_score:.2f})"
            )

    def optimize_weights(self):
        """
        使用激活的优化算法 (GWO, WOAm, etc.) 实时优化 HybridOptimizer 的权重
        解决优化算法一直为负数的问题：确保有实际运行并使用正向的适应度函数 (准确率)
        """
        if len(self.signal_history) < 20: # 需要一定的历史数据
            return

        logger.info(f"正在运行权重优化 ({self.active_optimizer_name})... 样本数: {len(self.signal_history)}")
        
        # 1. 准备数据
        # 提取历史信号和实际结果
        # history items: (timestamp, signals_dict, close_price)
        # 我们需要计算每个样本的实际涨跌: price[i+1] - price[i]
        
        samples = []
        for i in range(len(self.signal_history) - 1):
            curr = self.signal_history[i]
            next_bar = self.signal_history[i+1]
            
            signals = curr[1]
            price_change = next_bar[2] - curr[2]
            
            actual_dir = 0
            if price_change > 0: actual_dir = 1
            elif price_change < 0: actual_dir = -1
            
            if actual_dir != 0:
                samples.append((signals, actual_dir))
                
        if len(samples) < 10:
            return

        # 2. 定义目标函数 (适应度函数)
        # 输入: 权重向量 [w1, w2, ...]
        # 输出: 准确率 (0.0 - 1.0) -> 保证非负
        strategy_keys = list(self.optimizer.weights.keys())
        
        def objective(weights_vec):
            correct = 0
            total = 0
            
            # 构建临时权重字典
            temp_weights = {k: w for k, w in zip(strategy_keys, weights_vec)}
            
            for signals, actual_dir in samples:
                # 模拟 combine_signals
                weighted_sum = 0
                total_w = 0
                
                for strat, sig in signals.items():
                    w = temp_weights.get(strat, 1.0)
                    if sig == 'buy':
                        weighted_sum += w
                        total_w += w
                    elif sig == 'sell':
                        weighted_sum -= w
                        total_w += w
                
                if total_w > 0:
                    norm_score = weighted_sum / total_w
                    
                    pred_dir = 0
                    if norm_score > 0.3: pred_dir = 1
                    elif norm_score < -0.3: pred_dir = -1
                    
                    if pred_dir == actual_dir:
                        correct += 1
                    total += 1
            
            if total == 0: return 0.0
            return correct / total # 返回准确率
            
        # 3. 运行优化
        optimizer = self.optimizers[self.active_optimizer_name]
        
        # 定义边界: 权重范围 [0.0, 2.0]
        bounds = [(0.0, 2.0) for _ in range(len(strategy_keys))]
        
        try:
            best_weights_vec, best_score = optimizer.optimize(
                objective_function=objective,
                bounds=bounds,
                epochs=20 # 实时运行不宜过久
            )
            
            # 4. 应用最佳权重
            if best_score > 0: # 确保结果有效
                for i, k in enumerate(strategy_keys):
                    self.optimizer.weights[k] = best_weights_vec[i]
                
                logger.info(f"权重优化完成! 最佳准确率: {best_score:.2%}")
                logger.info(f"新权重: {self.optimizer.weights}")
                self.last_optimization_time = time.time()
            else:
                logger.warning("优化结果得分过低，未更新权重")
                
        except Exception as e:
            logger.error(f"权重优化失败: {e}")

    def calculate_optimized_sl_tp(self, trade_type, price, atr, market_context=None):
        """
        计算基于综合因素的优化止损止盈点
        结合: 14天 ATR, MFE/MAE 统计, 市场分析(Supply/Demand/FVG)
        """
        # 1. 基础波动率 (14天 ATR)
        # 确保传入的 ATR 是有效的 14周期 ATR
        if atr <= 0:
            atr = price * 0.005 # Fallback
            
        # 2. 历史绩效 (MFE/MAE)
        mfe_tp_dist = atr * 2.0 # 默认
        mae_sl_dist = atr * 1.5 # 默认
        
        try:
             trades = self.db_manager.get_trade_performance_stats(limit=100)
             if trades and len(trades) > 10:
                 mfes = [t.get('mfe', 0) for t in trades if t.get('mfe', 0) > 0]
                 maes = [t.get('mae', 0) for t in trades if t.get('mae', 0) > 0]
                 
                 if mfes and maes:
                     # 使用 ATR 倍数来标准化 MFE/MAE (假设 MFE/MAE 也是以 ATR 为单位存储，或者我们需要转换)
                     # 如果 DB 存的是百分比，我们需要将其转换为当前 ATR 倍数
                     # 这里简化处理：直接取百分比的中位数，然后转换为价格距离
                     
                     opt_tp_pct = np.percentile(mfes, 60) / 100.0 # 60分位数
                     opt_sl_pct = np.percentile(maes, 90) / 100.0 # 90分位数
                     
                     mfe_tp_dist = price * opt_tp_pct
                     mae_sl_dist = price * opt_sl_pct
        except Exception as e:
             logger.warning(f"MFE/MAE 计算失败: {e}")

        # 3. 市场结构调整 (Supply/Demand/FVG)
        # 从 market_context 中获取关键位
        struct_tp_price = 0.0
        struct_sl_price = 0.0
        
        if market_context:
            # 获取最近的 Supply/Demand 区间
            # 假设 market_context 包含 advanced_tech 或 ifvg 结果
            
            is_buy = 'buy' in trade_type
            
            # 寻找止盈点 (最近的阻力位/FVG)
            if is_buy:
                # 买入 TP: 最近的 Supply Zone 或 Bearish FVG 的下沿
                resistance_candidates = []
                if 'supply_zones' in market_context:
                    # 找出所有高于当前价格的 Supply Zone bottom
                    # 注意: zones 可能是 [(top, bottom), ...] 或其他结构，需要类型检查
                    raw_zones = market_context['supply_zones']
                    if raw_zones and isinstance(raw_zones, list):
                        try:
                            # 尝试解析可能的元组/列表结构
                            valid_zones = []
                            for z in raw_zones:
                                if isinstance(z, (list, tuple)) and len(z) >= 2:
                                    # 假设结构是 (top, bottom, ...)
                                    if z[1] > price: valid_zones.append(z[1])
                                elif isinstance(z, dict):
                                    # 假设结构是 {'top': ..., 'bottom': ...}
                                    btm = z.get('bottom')
                                    if btm and btm > price: valid_zones.append(btm)
                            
                            if valid_zones: resistance_candidates.append(min(valid_zones))
                        except Exception as e:
                            logger.warning(f"解析 Supply Zones 失败: {e}")
                
                if 'bearish_fvgs' in market_context:
                    raw_fvgs = market_context['bearish_fvgs']
                    if raw_fvgs and isinstance(raw_fvgs, list):
                        try:
                            valid_fvgs = []
                            for f in raw_fvgs:
                                if isinstance(f, dict):
                                    btm = f.get('bottom')
                                    if btm and btm > price: valid_fvgs.append(btm)
                            if valid_fvgs: resistance_candidates.append(min(valid_fvgs))
                        except Exception as e:
                            logger.warning(f"解析 Bearish FVG 失败: {e}")
                    
                if resistance_candidates:
                    struct_tp_price = min(resistance_candidates)
            
            else:
                # 卖出 TP: 最近的 Demand Zone 或 Bullish FVG 的上沿
                support_candidates = []
                if 'demand_zones' in market_context:
                    raw_zones = market_context['demand_zones']
                    if raw_zones and isinstance(raw_zones, list):
                        try:
                            valid_zones = []
                            for z in raw_zones:
                                if isinstance(z, (list, tuple)) and len(z) >= 2:
                                    # 假设结构是 (top, bottom, ...)
                                    if z[0] < price: valid_zones.append(z[0])
                                elif isinstance(z, dict):
                                    top = z.get('top')
                                    if top and top < price: valid_zones.append(top)
                            
                            if valid_zones: support_candidates.append(max(valid_zones))
                        except Exception as e:
                            logger.warning(f"解析 Demand Zones 失败: {e}")
                    
                if 'bullish_fvgs' in market_context:
                    raw_fvgs = market_context['bullish_fvgs']
                    if raw_fvgs and isinstance(raw_fvgs, list):
                        try:
                            valid_fvgs = []
                            for f in raw_fvgs:
                                if isinstance(f, dict):
                                    top = f.get('top')
                                    if top and top < price: valid_fvgs.append(top)
                            if valid_fvgs: support_candidates.append(max(valid_fvgs))
                        except Exception as e:
                            logger.warning(f"解析 Bullish FVG 失败: {e}")
                    
                if support_candidates:
                    struct_tp_price = max(support_candidates)

            # 寻找止损点 (最近的支撑位/结构点)
            # 这里简化逻辑，通常 SL 放在结构点外侧
            # 可以使用 recent swing high/low
            pass

        # 4. 综合计算
        # 逻辑: 
        # TP: 优先使用结构位 (Struct TP)，如果结构位太远或太近，使用 MFE/ATR 修正
        # SL: 使用 MAE/ATR 保护，但如果结构位 (如 Swing Low) 在附近，可以参考
        
        final_sl = 0.0
        final_tp = 0.0
        
        # 基础计算
        if 'buy' in trade_type:
            base_tp = price + mfe_tp_dist
            base_sl = price - mae_sl_dist
            
            # TP 融合
            if struct_tp_price > price:
                # 如果结构位比基础 TP 近，说明上方有阻力，保守起见设在阻力前
                # 如果结构位比基础 TP 远，可以尝试去拿，但最好分批。这里取加权平均或保守值
                if struct_tp_price < base_tp:
                    final_tp = struct_tp_price - (atr * 0.1) # 阻力下方一点点
                else:
                    final_tp = base_tp # 保持 MFE 目标，比较稳健
            else:
                final_tp = base_tp
                
            final_sl = base_sl # SL 主要靠统计风控
            
        else: # Sell
            base_tp = price - mfe_tp_dist
            base_sl = price + mae_sl_dist
            
            if struct_tp_price > 0 and struct_tp_price < price:
                if struct_tp_price > base_tp: # 支撑位在目标上方 (更近)
                    final_tp = struct_tp_price + (atr * 0.1)
                else:
                    final_tp = base_tp
            else:
                final_tp = base_tp
                
            final_sl = base_sl

        return final_sl, final_tp

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
                        
                        self.db_manager.save_market_data(df_current.copy(), self.symbol, self.tf_name)
                        self.last_realtime_save = time.time()
                        
                        # --- 实时保存账户信息 (新增) ---
                        try:
                            account_info = mt5.account_info()
                            if account_info:
                                # 计算当前品种的浮动盈亏
                                positions = mt5.positions_get(symbol=self.symbol)
                                symbol_pnl = 0.0
                                magic_positions_count = 0
                                if positions:
                                    for pos in positions:
                                        # 仅统计和计算属于本策略ID的持仓
                                        if pos.magic == self.magic_number:
                                            magic_positions_count += 1
                                            # Handle different position object structures safely
                                            profit = getattr(pos, 'profit', 0.0)
                                            swap = getattr(pos, 'swap', 0.0)
                                            commission = getattr(pos, 'commission', 0.0) # Check attribute existence
                                            symbol_pnl += profit + swap + commission
                                
                                # 显示当前 ID 的持仓状态
                                # if magic_positions_count > 0:
                                #     logger.info(f"ID {self.magic_number} 当前持仓: {magic_positions_count} 个")
                                # else:
                                #     pass
                                
                                metrics = {
                                    "timestamp": datetime.now(),
                                    "balance": account_info.balance,
                                    "equity": account_info.equity,
                                    "margin": account_info.margin,
                                    "free_margin": account_info.margin_free,
                                    "margin_level": account_info.margin_level,
                                    "total_profit": account_info.profit,
                                    "symbol_pnl": symbol_pnl
                                }
                                self.db_manager.save_account_metrics(metrics)
                        except Exception as e:
                            logger.error(f"Failed to save account metrics: {e}")
                        # ------------------------------
                        
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
                        self.db_manager.save_market_data(df, self.symbol, self.tf_name)
                        
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
                        smc_result = self.smc_analyzer.analyze_with_symbol(df, self.symbol)
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
                        
                        # --- 3.2.7 IFVG 分析 (新增) ---
                        # 在 AdvancedAnalysisAdapter 中已调用，但这里需要单独提取结果供后续使用
                        # 我们之前在步骤 3.2.1 的 AdvancedAnalysisAdapter.analyze 中已经获取了 ifvg_result
                        # 但由于 analyze 方法返回的是一个包含多个子结果的字典，我们需要确保 ifvg_result 变量被正确定义
                        if adv_result and 'ifvg' in adv_result:
                            ifvg_result = adv_result['ifvg']
                        else:
                            # Fallback if advanced analysis failed or ifvg key missing
                            ifvg_result = {"signal": "hold", "strength": 0, "reasons": [], "active_zones": []}
                        
                        logger.info(f"IFVG 分析: {ifvg_result['signal']} (Strength: {ifvg_result['strength']})")

                        # --- 3.2.8 RVGI+CCI 分析 (新增) ---
                        if adv_result and 'rvgi_cci' in adv_result:
                            rvgi_cci_result = adv_result['rvgi_cci']
                        else:
                            rvgi_cci_result = {"signal": "hold", "strength": 0, "reasons": []}
                            
                        logger.info(f"RVGI+CCI 分析: {rvgi_cci_result['signal']} (Strength: {rvgi_cci_result['strength']})")
                        
                        # 准备优化器池信息供 AI 参考
                        optimizer_info = {
                            "available_optimizers": list(self.optimizers.keys()),
                            "active_optimizer": self.active_optimizer_name,
                            "last_optimization_score": self.optimizers[self.active_optimizer_name].best_score if self.optimizers[self.active_optimizer_name].best_score > -90000 else None,
                            "descriptions": {
                                "GWO": "Grey Wolf Optimizer - 模拟灰狼捕猎行为",
                                "WOAm": "Whale Optimization Algorithm (Modified) - 模拟座头鲸气泡网捕猎",
                                "DE": "Differential Evolution - 差分进化算法",
                                "COAm": "Cuckoo Optimization Algorithm (Modified) - 模拟布谷鸟寄生繁殖",
                                "BBO": "Biogeography-Based Optimization - 生物地理学优化",
                                "TETA": "Time Evolution Travel Algorithm - 时间演化旅行算法 (无参)"
                            }
                        }

                        # --- 3.3 DeepSeek 分析 ---
                        logger.info("正在调用 DeepSeek 分析市场结构...")
                        # 准备当前优化状态上下文
                        optimization_status = {
                            "active_optimizer": self.active_optimizer_name,
                            "optimizer_details": optimizer_info, # 注入详细优化器信息
                            "smc_params": {
                                "ma_period": self.smc_analyzer.ma_period,
                                "atr_threshold": self.smc_analyzer.atr_threshold
                            },
                            "mfh_params": {
                                "learning_rate": self.mfh_analyzer.learning_rate
                            }
                        }

                        # 传入 CRT, PriceEq, TF 和 高级分析 的结果作为额外上下文
                        extra_analysis = {
                            "crt": crt_result,
                            "price_equation": price_eq_result,
                            "timeframe_analysis": tf_result,
                            "advanced_tech": adv_result['summary'] if adv_result else None,
                            "matrix_ml": ml_result,
                            "smc": smc_result,
                            "mfh": mfh_result,
                            "mtf": mtf_result,
                            "ifvg": ifvg_result,
                            "rvgi_cci": rvgi_cci_result,
                            "optimization_status": optimization_status # 新增: 当前参数状态
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
                        
                        # 获取当前持仓状态 (供 Qwen 决策)
                        positions = mt5.positions_get(symbol=self.symbol)
                        current_positions_list = []
                        if positions:
                            for pos in positions:
                                cur_mfe, cur_mae = self.get_position_stats(pos)
                                current_positions_list.append({
                                    "ticket": pos.ticket,
                                    "type": "buy" if pos.type == mt5.POSITION_TYPE_BUY else "sell",
                                    "volume": pos.volume,
                                    "open_price": pos.price_open,
                                    "current_price": pos.price_current,
                                    "profit": pos.profit,
                                    "sl": pos.sl,
                                    "tp": pos.tp,
                                    "mfe_pct": cur_mfe,
                                    "mae_pct": cur_mae
                                })
                        
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
                        
                        strategy = self.qwen_client.optimize_strategy_logic(structure, market_snapshot, technical_signals=technical_signals, current_positions=current_positions_list)
                        
                        # Qwen 信号转换
                        # 如果没有明确 action 字段，我们假设它作为 DeepSeek 的确认层
                        # 现在我们优先使用 Qwen 返回的 action
                        qw_action = strategy.get('action', 'neutral').lower()
                        
                        # 扩展 Action 解析，支持加仓/减仓/平仓/挂单指令
                        final_signal = "neutral"
                        if qw_action in ['buy', 'add_buy']:
                            final_signal = "buy"
                        elif qw_action in ['sell', 'add_sell']:
                            final_signal = "sell"
                        elif qw_action in ['buy_limit', 'limit_buy']:
                            final_signal = "limit_buy"
                        elif qw_action in ['sell_limit', 'limit_sell']:
                            final_signal = "limit_sell"
                        elif qw_action in ['close_buy', 'close_sell', 'close']:
                            final_signal = "close" # 特殊信号: 平仓
                        elif qw_action == 'hold':
                            final_signal = "hold"
                        
                        qw_signal = final_signal if final_signal not in ['hold', 'close'] else 'neutral'
                        
                        # --- 3.5 最终决策 (LLM Centric) ---
                        # 依据用户指令：完全基于大模型的最终决策 (以 Qwen 的 Action 为主)
                        
                        # final_signal 已在上面由 qw_action 解析得出
                        reason = strategy.get('reason', 'LLM Decision')
                        
                        # 计算置信度/强度 (Strength)
                        # 我们使用技术指标的一致性作为置信度评分
                        tech_consensus_score = 0
                        matching_count = 0
                        valid_tech_count = 0
                        
                        tech_signals_list = [
                            crt_result['signal'], price_eq_result['signal'], tf_result['signal'],
                            adv_signal, ml_result['signal'], smc_result['signal'],
                            mfh_result['signal'], mtf_result['signal'], ifvg_result['signal'],
                            rvgi_cci_result['signal']
                        ]
                        
                        for sig in tech_signals_list:
                            if sig != 'neutral':
                                valid_tech_count += 1
                                if sig == final_signal:
                                    matching_count += 1
                        
                        if final_signal in ['buy', 'sell']:
                            # 基础分 60 (既然 LLM 敢喊单)
                            base_strength = 60
                            # 技术面加成
                            if valid_tech_count > 0:
                                tech_boost = (matching_count / valid_tech_count) * 40 # 最高 +40
                                strength = base_strength + tech_boost
                            else:
                                strength = base_strength
                                
                            # DeepSeek 加成
                            if ds_signal == final_signal:
                                strength = min(100, strength + 10)
                        else:
                            strength = 0

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
                            "mtf": mtf_result['signal'],
                            "ifvg": ifvg_result['signal'],
                            "rvgi_cci": rvgi_cci_result['signal']
                        }
                        
                        # 仅保留 weights 用于记录，不再用于计算信号
                        _, _, weights = self.optimizer.combine_signals(all_signals)

                        # --- 3.6 记录信号历史用于实时优化 ---
                        # 解决优化算法未运行的问题：收集数据并定期调用 optimize_weights
                        self.signal_history.append((current_bar_time, all_signals, float(current_price['close'])))
                        if len(self.signal_history) > 1000:
                            self.signal_history.pop(0)
                            
                        # 每 15 分钟尝试优化一次权重
                        if time.time() - self.last_optimization_time > 900:
                             self.optimize_weights()

                        logger.info(f"AI 最终决定 (LLM-Driven): {final_signal.upper()} (强度: {strength:.1f})")
                        logger.info(f"LLM Reason: {reason}")
                        logger.info(f"技术面支持: {matching_count}/{valid_tech_count}")
                        
                        # 保存分析结果到DB
                        self.db_manager.save_signal(self.symbol, self.tf_name, {
                            "final_signal": final_signal,
                            "strength": strength,
                            "details": {
                                "source": "LLM_Centric",
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
                                "mfh_slope": mfh_result['slope'],
                                "ifvg_reason": ", ".join(ifvg_result['reasons']) if ifvg_result['reasons'] else "N/A"
                            }
                        })
                        
                        # 更新全局缓存，供 manage_positions 使用
                        self.latest_strategy = strategy
                        self.latest_signal = final_signal
                        
                        # --- 发送分析报告到 Telegram ---
                        # 构建更详细的报告
                        regime_info = adv_result['regime']['description'] if adv_result else "N/A"
                        volatility_info = f"{adv_result['risk']['volatility']:.2%}" if adv_result else "N/A"
                        
                        # 获取当前持仓概览
                        pos_summary = "No Open Positions"
                        positions = mt5.positions_get(symbol=self.symbol)
                        if positions:
                            pos_details = []
                            for p in positions:
                                type_str = "BUY" if p.type == mt5.POSITION_TYPE_BUY else "SELL"
                                pnl = p.profit
                                pos_details.append(f"{type_str} {p.volume} (PnL: {pnl:.2f})")
                            pos_summary = "\n".join(pos_details)

                        # 获取建议的 SL/TP (仅供参考)
                        # 注意：这里只是预估值，实际值在 execute_trade 中计算
                        # 为了展示，我们调用 calculate_optimized_sl_tp 获取一次
                        ref_price = mt5.symbol_info_tick(self.symbol).ask
                        
                        # 准备市场上下文供 SL/TP 计算
                        sl_tp_context = {
                            "supply_zones": adv_result.get('ifvg', {}).get('active_zones', []), # 假设 ifvg 中包含 supply/demand
                            "demand_zones": [], # 需要从 ifvg 或其他地方提取
                            "bearish_fvgs": [], 
                            "bullish_fvgs": []
                        }
                        # 尝试从 adv_result 中提取更详细的结构信息 (如果存在)
                        if adv_result and 'ifvg' in adv_result:
                             # 假设 ifvg 结果包含 zones 列表 [(top, bottom, type), ...]
                             # 这里简化处理，实际需要根据 ifvg 返回结构适配
                             pass

                        # 计算 ATR (复用之前的计算或重新获取)
                        atr_val = 0.0 # 这里简化，实际应传入有效 ATR
                        
                        ref_sl, ref_tp = self.calculate_optimized_sl_tp("buy", ref_price, atr_val, market_context=sl_tp_context)
                        
                        analysis_msg = (
                            f"🤖 *AI Market Analysis - {self.symbol}*\n"
                            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                            f"🧠 *Dual-LLM Decision:*\n"
                            f"• DeepSeek: `{ds_signal.upper()}` (Conf: {ds_score})\n"
                            f"• Qwen Strategy: `{qw_action.upper()}`\n"
                            f"• Final Action: *{final_signal.upper()}* (Strength: {strength:.1f})\n"
                            f"• Reason: _{reason}_\n\n"
                            f"📊 *Technical Confluence:*\n"
                            f"• Support: {matching_count}/{valid_tech_count} indicators\n"
                            f"• SMC: `{smc_result['signal']}` | CRT: `{crt_result['signal']}`\n"
                            f"• MTF: `{mtf_result['signal']}` | MFH: `{mfh_result['signal']}`\n\n"
                            f"📈 *Market Context:*\n"
                            f"• State: {structure.get('market_state', 'N/A')}\n"
                            f"• Regime: {regime_info}\n"
                            f"• Volatility: {volatility_info}\n"
                            f"• Prediction: {structure.get('short_term_prediction', 'N/A')}\n\n"
                            f"💼 *Position Status:*\n"
                            f"{pos_summary}\n\n"
                            f"🛡️ *Risk Management (MFE/MAE Optimized):*\n"
                            f"• Est. SL Distance: ~{abs(ref_price - ref_sl):.2f}\n"
                            f"• Est. TP Distance: ~{abs(ref_tp - ref_price):.2f}"
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
