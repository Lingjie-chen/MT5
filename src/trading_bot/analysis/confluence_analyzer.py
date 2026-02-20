import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from decimal import Decimal
from scipy import stats
import time
import logging
from datetime import datetime

logger = logging.getLogger("ConfluenceAnalyzer")

class TrendlineAnalyzer:
    """趋势线分析器"""
    
    def __init__(self, config):
        self.config = config
        self.cache = {}
        
    def get_data(self, symbol, timeframe):
        """获取分析所需的数据"""
        cache_key = f"{symbol}_{timeframe}"
        if cache_key in self.cache and time.time() - self.cache[cache_key]['time'] < 60:
            return self.cache[cache_key]['data']
        
        # Use a config-defined lookback or default to 1000
        lookback = getattr(self.config, 'trendline_lookback', 1000)
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, lookback)
        if rates is None or len(rates) == 0:
            logger.error(f"获取趋势线数据失败: {symbol}")
            return None
            
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        self.cache[cache_key] = {
            'data': df,
            'time': time.time()
        }
        
        return df
    
    def find_swing_points(self, df, lookback=5):
        """识别波峰波谷"""
        if df is None or len(df) < lookback * 2:
            return [], []
        
        highs = []
        lows = []
        
        for i in range(lookback, len(df) - lookback):
            # 寻找波峰
            is_swing_high = True
            for j in range(i - lookback, i + lookback + 1):
                if j == i:
                    continue
                if df['high'].iloc[j] >= df['high'].iloc[i]:
                    is_swing_high = False
                    break
            
            if is_swing_high:
                highs.append({
                    'index': i,
                    'price': df['high'].iloc[i],
                    'time': df['time'].iloc[i]
                })
            
            # 寻找波谷
            is_swing_low = True
            for j in range(i - lookback, i + lookback + 1):
                if j == i:
                    continue
                if df['low'].iloc[j] <= df['low'].iloc[i]:
                    is_swing_low = False
                    break
            
            if is_swing_low:
                lows.append({
                    'index': i,
                    'price': df['low'].iloc[i],
                    'time': df['time'].iloc[i]
                })
        
        return highs, lows
    
    def calculate_trendline(self, points):
        """计算趋势线并返回R²值"""
        if len(points) < 3:
            return None, 0
        
        x = np.array([p['index'] for p in points])
        y = np.array([p['price'] for p in points])
        
        # 线性回归
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        # 计算R²
        r_squared = r_value ** 2
        
        return {
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_squared,
            'points': points
        }, r_squared
    
    def identify_trendlines(self, df):
        """识别有效趋势线"""
        if df is None:
            return None, None
        
        highs, lows = self.find_swing_points(df)
        min_touches = getattr(self.config, 'trendline_min_touches', 3)
        r_squared_thresh = getattr(self.config, 'r_squared_threshold', 0.9)
        
        # 尝试从波峰中识别上升趋势线
        bullish_trendlines = []
        if len(lows) >= min_touches:
            # 按时间排序
            sorted_lows = sorted(lows, key=lambda x: x['index'])
            
            # 尝试不同的组合
            for i in range(len(sorted_lows) - min_touches + 1):
                for j in range(i + 2, len(sorted_lows)):
                    # 选择三个点
                    selected_points = sorted_lows[i:j+1]
                    if len(selected_points) < 3:
                        continue
                    
                    trendline, r_squared = self.calculate_trendline(selected_points)
                    
                    if trendline and r_squared > r_squared_thresh:
                        # 验证是否为上升趋势线（斜率>0）
                        if trendline['slope'] > 0:
                            # 检查后续点是否都在趋势线上方
                            valid = True
                            for k in range(j + 1, len(sorted_lows)):
                                expected_price = trendline['slope'] * sorted_lows[k]['index'] + trendline['intercept']
                                if sorted_lows[k]['price'] < expected_price:
                                    valid = False
                                    break
                            
                            if valid:
                                bullish_trendlines.append(trendline)
        
        # 尝试从波峰中识别下降趋势线
        bearish_trendlines = []
        if len(highs) >= min_touches:
            # 按时间排序
            sorted_highs = sorted(highs, key=lambda x: x['index'])
            
            # 尝试不同的组合
            for i in range(len(sorted_highs) - min_touches + 1):
                for j in range(i + 2, len(sorted_highs)):
                    # 选择三个点
                    selected_points = sorted_highs[i:j+1]
                    if len(selected_points) < 3:
                        continue
                    
                    trendline, r_squared = self.calculate_trendline(selected_points)
                    
                    if trendline and r_squared > r_squared_thresh:
                        # 验证是否为下降趋势线（斜率<0）
                        if trendline['slope'] < 0:
                            # 检查后续点是否都在趋势线下方
                            valid = True
                            for k in range(j + 1, len(sorted_highs)):
                                expected_price = trendline['slope'] * sorted_highs[k]['index'] + trendline['intercept']
                                if sorted_highs[k]['price'] > expected_price:
                                    valid = False
                                    break
                            
                            if valid:
                                bearish_trendlines.append(trendline)
        
        # 选择最显著的趋势线
        best_bullish = None
        if bullish_trendlines:
            best_bullish = max(bullish_trendlines, key=lambda x: x['r_squared'])
        
        best_bearish = None
        if bearish_trendlines:
            best_bearish = max(bearish_trendlines, key=lambda x: x['r_squared'])
        
        return best_bullish, best_bearish
    
    def check_breakout(self, df, trendline):
        """检查是否发生趋势线突破"""
        if df is None or trendline is None:
            return False, None
        
        current_price = df['close'].iloc[-1]
        current_index = len(df) - 1
        
        # 计算当前趋势线的价格
        trendline_price = trendline['slope'] * current_index + trendline['intercept']
        
        # 判断是否突破
        if trendline['slope'] > 0:  # 上升趋势线
            # 向下突破
            if current_price < trendline_price:
                return True, current_price - trendline_price
        else:  # 下降趋势线
            # 向上突破
            if current_price > trendline_price:
                return True, current_price - trendline_price
        
        return False, None
    
    def analyze(self, symbol, timeframe):
        """分析趋势线并返回信号"""
        df = self.get_data(symbol, timeframe)
        if df is None:
            return None
        
        bullish_trendline, bearish_trendline = self.identify_trendlines(df)
        
        bullish_breakout = False
        bearish_breakout = False
        
        if bullish_trendline:
            breakout, _ = self.check_breakout(df, bullish_trendline)
            if breakout:
                bullish_breakout = True
        
        if bearish_trendline:
            breakout, _ = self.check_breakout(df, bearish_trendline)
            if breakout:
                bearish_breakout = True
        
        return {
            'bullish_trendline': bullish_trendline,
            'bearish_trendline': bearish_trendline,
            'bullish_breakout': bullish_breakout,
            'bearish_breakout': bearish_breakout,
            'current_price': df['close'].iloc[-1]
        }

class MomentumAnalyzer:
    """动量分析器"""
    
    def __init__(self, config):
        self.config = config
        self.cache = {}
        
    def get_data(self, symbol, timeframe):
        """获取分析所需的数据"""
        cache_key = f"{symbol}_{timeframe}"
        if cache_key in self.cache and time.time() - self.cache[cache_key]['time'] < 60:
            return self.cache[cache_key]['data']
        
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 100)
        if rates is None or len(rates) == 0:
            logger.error(f"获取动量数据失败: {symbol}")
            return None
            
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        self.cache[cache_key] = {
            'data': df,
            'time': time.time()
        }
        
        return df
    
    def calculate_ema(self, df, period):
        """计算EMA"""
        return df['close'].ewm(span=period, adjust=False).mean()
    
    def calculate_macd(self, df):
        """计算MACD"""
        macd_fast = getattr(self.config, 'macd_fast', 12)
        macd_slow = getattr(self.config, 'macd_slow', 26)
        macd_signal = getattr(self.config, 'macd_signal', 9)

        ema_fast = df['close'].ewm(span=macd_fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=macd_slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=macd_signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def check_macd_divergence(self, histogram):
        """检查MACD柱状图是否发散"""
        if len(histogram) < 3:
            return 0  # 无法判断
        
        current = histogram.iloc[-1]
        prev = histogram.iloc[-2]
        prev2 = histogram.iloc[-3]
        
        # 检查看涨发散
        if current > prev > prev2:
            return 1  # 看涨发散
        
        # 检查看跌发散
        if current < prev < prev2:
            return -1  # 看跌发散
        
        return 0  # 无发散
    
    def analyze(self, symbol, timeframe):
        """分析动量指标"""
        df = self.get_data(symbol, timeframe)
        if df is None:
            return None
        
        current_price = df['close'].iloc[-1]
        
        # 计算EMA
        ema = self.calculate_ema(df, getattr(self.config, 'ema_period', 12))
        current_ema = ema.iloc[-1]
        
        # 判断价格相对于EMA的位置
        ema_position = 0
        if current_price > current_ema:
            ema_position = 1  # 价格在EMA上方，看涨
        elif current_price < current_ema:
            ema_position = -1  # 价格在EMA下方，看跌
        
        # 计算MACD
        macd_line, signal_line, histogram = self.calculate_macd(df)
        current_macd = macd_line.iloc[-1]
        current_signal = signal_line.iloc[-1]
        current_hist = histogram.iloc[-1]
        
        # 检查MACD交叉
        macd_cross = 0
        if current_macd > current_signal and macd_line.iloc[-2] <= signal_line.iloc[-2]:
            macd_cross = 1  # 金叉，看涨
        elif current_macd < current_signal and macd_line.iloc[-2] >= signal_line.iloc[-2]:
            macd_cross = -1  # 死叉，看跌
        
        # 检查MACD柱状图发散
        histogram_divergence = self.check_macd_divergence(histogram)
        
        return {
            'current_price': current_price,
            'ema': current_ema,
            'ema_position': ema_position,
            'macd': current_macd,
            'signal': current_signal,
            'histogram': current_hist,
            'macd_cross': macd_cross,
            'histogram_divergence': histogram_divergence
        }

class ConfluenceAnalyzer:
    """汇合度分析器 - 决策矩阵"""
    
    def __init__(self, config):
        self.config = config
    
    def calculate_confluence_score(self, smc_data, trendline_data, momentum_data):
        """计算汇合度评分"""
        score = 0.0
        details = {}
        
        smc_weight = getattr(self.config, 'smc_weight', 2.0)
        trendline_weight = getattr(self.config, 'trendline_weight', 1.5)
        ema_weight = getattr(self.config, 'ema_weight', 1.0)
        macd_weight = getattr(self.config, 'macd_weight', 1.0)
        ob_fvg_weight = getattr(self.config, 'ob_fvg_weight', 1.5)
        
        full_position_threshold = getattr(self.config, 'full_position_threshold', 5.0)
        half_position_threshold = getattr(self.config, 'half_position_threshold', 3.5)

        # SMC结构一致性评分
        if smc_data and smc_data.get('market_bias') != 0:
            details['smc_consistency'] = smc_weight
            score += smc_weight
        else:
            details['smc_consistency'] = 0.0
        
        # 趋势线突破强度评分
        trendline_score = 0.0
        if trendline_data:
            if (trendline_data.get('bullish_breakout') or 
                (trendline_data.get('bearish_trendline') and 
                 trendline_data['bearish_trendline'].get('r_squared', 0) > 0.9)):
                trendline_score = trendline_weight
            elif (trendline_data.get('bearish_breakout') or 
                  (trendline_data.get('bullish_trendline') and 
                   trendline_data['bullish_trendline'].get('r_squared', 0) > 0.9)):
                trendline_score = trendline_weight
        
        details['trendline_breakout'] = trendline_score
        score += trendline_score
        
        # 12 EMA位置评分
        ema_score = 0.0
        if momentum_data and momentum_data.get('ema_position') != 0:
            ema_score = ema_weight
        
        details['ema_position'] = ema_score
        score += ema_score
        
        # MACD柱状图状态评分
        macd_score = 0.0
        if momentum_data:
            if momentum_data.get('histogram_divergence') != 0 or momentum_data.get('macd_cross') != 0:
                macd_score = macd_weight
        
        details['macd_histogram'] = macd_score
        score += macd_score
        
        # OB/FVG汇合评分
        ob_fvg_score = 0.0
        if smc_data:
            if smc_data.get('nearby_bullish_ob') or smc_data.get('nearby_bullish_fvg'):
                ob_fvg_score = ob_fvg_weight
            elif smc_data.get('nearby_bearish_ob') or smc_data.get('nearby_bearish_fvg'):
                ob_fvg_score = ob_fvg_weight
        
        details['ob_fvg_confluence'] = ob_fvg_score
        score += ob_fvg_score
        
        return {
            'score': score,
            'details': details,
            'threshold_full': full_position_threshold,
            'threshold_half': half_position_threshold
        }
    
    def determine_position_size_multiplier(self, confluence_result):
        """根据汇合度评分确定仓位大小乘数"""
        score = confluence_result['score']
        
        if score >= confluence_result['threshold_full']:
            return 1.0  # 全仓
        elif score >= confluence_result['threshold_half']:
            return 0.5  # 半仓
        else:
            return 0.0  # 不执行
