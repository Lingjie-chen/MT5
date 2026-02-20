import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal, getcontext
from scipy import stats
import asyncio
import time
import logging

# 设置Decimal精度
getcontext().prec = 8

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TradingConfig:
    """交易配置类 - 高汇合度策略参数"""
    def __init__(self):
        # 交易品种设置
        self.symbol = " GOLD"  # 默认交易黄金
        self.timeframe = mt5.TIMEFRAME_M15  # 15分钟K线
        self.higher_timeframe = mt5.TIMEFRAME_H1  # H1时间框架用于SMC分析
        
        # SMC参数
        self.smc_lookback = 50  # SMC分析回看周期
        self.bos_pips_threshold = 0.5  # BOS确认的最小点数
        
        # 趋势线参数
        self.trendline_lookback = 20  # 趋势线回看周期
        self.trendline_min_touches = 3  # 最小触碰次数
        self.r_squared_threshold = 0.85  # R²阈值
        
        # 动量参数
        self.ema_period = 12
        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9
        
        # 汇合度评分权重
        self.smc_weight = 2.0
        self.trendline_weight = 1.5
        self.ema_weight = 1.0
        self.macd_weight = 1.0
        self.ob_fvg_weight = 1.5
        
        # 执行门槛
        self.full_position_threshold = 4.5
        self.half_position_threshold = 3.0
        self.ignore_threshold = 3.0
        
        # 风控参数
        self.magic = 100
        self.risk_percent = Decimal('0.01')  # 1%单笔风险
        self.min_risk = Decimal('0.005')  # 最小0.5%风险
        self.max_risk = Decimal('0.02')  # 最大2%风险
        self.max_positions = 5  # 最大持仓数
        self.daily_loss_limit = Decimal('0.05')  # 日内最大亏损5%
        self.min_rrr = 3.0  # 最小盈亏比1:3
        
        # 止损参数
        self.break_even_at_rrr = 1.5  # 盈亏比1:1.5时保本
        self.trailing_start_rrr = 2.0  # 盈亏比2.0时开始追踪
        self.trailing_distance_points = 50  # 追踪距离（点数）

class PositionEngine:
    """高精度仓位计算引擎"""
    
    def calculate_position_size(self, symbol, entry_price, sl_price, risk_percent):
        """基于账户净值和风险百分比计算仓位大小"""
        account_info = mt5.account_info()
        if account_info is None:
            logger.error("获取账户信息失败")
            return Decimal('0.01')
        
        equity = Decimal(str(account_info.equity))
        risk_amount = equity * Decimal(str(risk_percent))
        
        # 获取品种信息
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logger.error(f"获取品种信息失败: {symbol}")
            return Decimal('0.01')
        
        # 计算风险点数
        tick_value = Decimal(str(symbol_info.trade_tick_value))
        tick_size = Decimal(str(symbol_info.trade_tick_size))
        sl_distance = abs(entry_price - sl_price)
        sl_points = sl_distance / tick_size
        
        if sl_points == 0:
            logger.warning("止损距离为0，使用最小仓位")
            return Decimal('0.01')
        
        # 计算仓位大小
        position_size = risk_amount / (sl_points * tick_value)
        
        # 限制在允许范围内
        min_volume = Decimal(str(symbol_info.volume_min))
        max_volume = Decimal(str(symbol_info.volume_max))
        volume_step = Decimal(str(symbol_info.volume_step))
        
        # 四舍五入到volume_step的倍数
        position_size = (position_size / volume_step).quantize(Decimal('1')) * volume_step
        position_size = max(min(position_size, max_volume), min_volume)
        
        return position_size

class SMCAnalyzer:
    """聪明钱概念(SMC)分析器"""
    
    def __init__(self, config):
        self.config = config
        self.cache = {}
        
    def get_smc_data(self, symbol, timeframe):
        """获取SMC分析所需的数据"""
        cache_key = f"{symbol}_{timeframe}"
        if cache_key in self.cache and time.time() - self.cache[cache_key]['time'] < 60:
            return self.cache[cache_key]['data']
        
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, self.config.smc_lookback)
        if rates is None or len(rates) == 0:
            logger.error(f"获取SMC数据失败: {symbol}")
            return None
            
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        self.cache[cache_key] = {
            'data': df,
            'time': time.time()
        }
        
        return df
    
    def detect_bos(self, df):
        """检测结构突破(BOS)"""
        if df is None or len(df) < 10:
            return None, None
            
        high = df['high'].values
        low = df['low'].values
        close = df['close'].values
        
        bullish_bos = None
        bearish_bos = None
        
        # 检测最近的高点突破
        for i in range(5, len(df)-1):
            prev_high = high[i]
            for j in range(i-4, i):
                if high[j] > prev_high:
                    prev_high = high[j]
            
            if close[i+1] > prev_high:
                bullish_bos = {
                    'index': i+1,
                    'price': prev_high,
                    'time': df.iloc[i+1]['time']
                }
                break
        
        # 检测最近的低点突破
        for i in range(5, len(df)-1):
            prev_low = low[i]
            for j in range(i-4, i):
                if low[j] < prev_low:
                    prev_low = low[j]
            
            if close[i+1] < prev_low:
                bearish_bos = {
                    'index': i+1,
                    'price': prev_low,
                    'time': df.iloc[i+1]['time']
                }
                break
        
        return bullish_bos, bearish_bos
    
    def detect_choch(self, df):
        """检测性格改变(CHoCH)"""
        if df is None or len(df) < 10:
            return None, None
            
        high = df['high'].values
        low = df['low'].values
        close = df['close'].values
        
        bullish_choch = None
        bearish_choch = None
        
        # 检测看涨CHoCH：在下跌趋势中，首次突破最近的高点
        bearish_trend = True
        last_high = high[-1]
        
        for i in range(len(df)-2, 0, -1):
            if high[i] > last_high:
                bearish_trend = False
                break
            last_high = high[i]
        
        if bearish_trend:
            for i in range(len(df)-1, 5, -1):
                swing_high = max(high[i-5:i])
                if close[i] > swing_high:
                    bullish_choch = {
                        'index': i,
                        'price': swing_high,
                        'time': df.iloc[i]['time']
                    }
                    break
        
        # 检测看跌CHoCH：在上涨趋势中，首次跌破最近的低点
        bullish_trend = True
        last_low = low[-1]
        
        for i in range(len(df)-2, 0, -1):
            if low[i] < last_low:
                bullish_trend = False
                break
            last_low = low[i]
        
        if bullish_trend:
            for i in range(len(df)-1, 5, -1):
                swing_low = min(low[i-5:i])
                if close[i] < swing_low:
                    bearish_choch = {
                        'index': i,
                        'price': swing_low,
                        'time': df.iloc[i]['time']
                    }
                    break
        
        return bullish_choch, bearish_choch
    
    def identify_order_blocks(self, df):
        """识别订单块(Order Blocks)"""
        if df is None or len(df) < 10:
            return None, None
            
        bullish_obs = []
        bearish_obs = []
        
        high = df['high'].values
        low = df['low'].values
        open_p = df['open'].values
        close_p = df['close'].values
        
        # 识别看涨订单块：导致强力向上移动前的最后一根看跌蜡烛
        for i in range(5, len(df)-1):
            # 检查当前蜡烛是否为看涨突破
            if close_p[i] > high[i-1] and (close_p[i] - open_p[i]) > 0.7 * (high[i] - low[i]):
                # 向后寻找导致此移动的看跌蜡烛
                for j in range(i-1, i-5, -1):
                    if j < 0:
                        break
                    if close_p[j] < open_p[j] and (open_p[j] - close_p[j]) > 0.5 * (high[j] - low[j]):
                        bullish_obs.append({
                            'index': j,
                            'high': high[j],
                            'low': low[j],
                            'open': open_p[j],
                            'close': close_p[j],
                            'time': df.iloc[j]['time']
                        })
                        break
        
        # 识别看跌订单块：导致强力向下移动前的最后一根看涨蜡烛
        for i in range(5, len(df)-1):
            # 检查当前蜡烛是否为看跌突破
            if close_p[i] < low[i-1] and (open_p[i] - close_p[i]) > 0.7 * (high[i] - low[i]):
                # 向后寻找导致此移动的看涨蜡烛
                for j in range(i-1, i-5, -1):
                    if j < 0:
                        break
                    if close_p[j] > open_p[j] and (close_p[j] - open_p[j]) > 0.5 * (high[j] - low[j]):
                        bearish_obs.append({
                            'index': j,
                            'high': high[j],
                            'low': low[j],
                            'open': open_p[j],
                            'close': close_p[j],
                            'time': df.iloc[j]['time']
                        })
                        break
        
        return bullish_obs, bearish_obs
    
    def identify_fvg(self, df):
        """识别公允价值缺口(FVG)"""
        if df is None or len(df) < 4:
            return None, None
            
        bullish_fvgs = []
        bearish_fvgs = []
        
        high = df['high'].values
        low = df['low'].values
        
        # 识别看涨FVG：第1根蜡烛的高点低于第3根蜡烛的低点
        for i in range(3, len(df)):
            if high[i-3] < low[i]:
                bullish_fvgs.append({
                    'index': i-2,
                    'top': low[i],
                    'bottom': high[i-3],
                    'gap': low[i] - high[i-3],
                    'time': df.iloc[i]['time']
                })
        
        # 识别看跌FVG：第1根蜡烛的低点高于第3根蜡烛的高点
        for i in range(3, len(df)):
            if low[i-3] > high[i]:
                bearish_fvgs.append({
                    'index': i-2,
                    'top': low[i-3],
                    'bottom': high[i],
                    'gap': low[i-3] - high[i],
                    'time': df.iloc[i]['time']
                })
        
        return bullish_fvgs, bearish_fvgs
    
    def analyze_market_structure(self, symbol, timeframe):
        """分析市场结构，返回SMC信号"""
        df = self.get_smc_data(symbol, timeframe)
        if df is None:
            return None
        
        # 获取最新价格
        current_price = df['close'].iloc[-1]
        
        # 识别市场结构
        bullish_bos, bearish_bos = self.detect_bos(df)
        bullish_choch, bearish_choch = self.detect_choch(df)
        bullish_obs, bearish_obs = self.identify_order_blocks(df)
        bullish_fvgs, bearish_fvgs = self.identify_fvg(df)
        
        # 判断市场偏见
        market_bias = 0  # 0=中性, 1=看涨, -1=看跌
        
        if bullish_bos or bullish_choch:
            market_bias = 1
        elif bearish_bos or bearish_choch:
            market_bias = -1
        
        # 寻找价格附近的入场区域
        nearby_bullish_ob = None
        nearby_bearish_ob = None
        
        for ob in bullish_obs:
            if abs(current_price - ob['low']) < abs(current_price - ob['low']) * 0.05:
                nearby_bullish_ob = ob
                break
        
        for ob in bearish_obs:
            if abs(current_price - ob['high']) < abs(current_price - ob['high']) * 0.05:
                nearby_bearish_ob = ob
                break
        
        # 寻找价格附近的FVG
        nearby_bullish_fvg = None
        nearby_bearish_fvg = None
        
        for fvg in bullish_fvgs:
            if fvg['bottom'] <= current_price <= fvg['top']:
                nearby_bullish_fvg = fvg
                break
        
        for fvg in bearish_fvgs:
            if fvg['bottom'] <= current_price <= fvg['top']:
                nearby_bearish_fvg = fvg
                break
        
        return {
            'market_bias': market_bias,
            'bullish_bos': bullish_bos,
            'bearish_bos': bearish_bos,
            'bullish_choch': bullish_choch,
            'bearish_choch': bearish_choch,
            'bullish_obs': bullish_obs,
            'bearish_obs': bearish_obs,
            'bullish_fvgs': bullish_fvgs,
            'bearish_fvgs': bearish_fvgs,
            'nearby_bullish_ob': nearby_bullish_ob,
            'nearby_bearish_ob': nearby_bearish_ob,
            'nearby_bullish_fvg': nearby_bullish_fvg,
            'nearby_bearish_fvg': nearby_bearish_fvg,
            'current_price': current_price
        }

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
        
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, self.config.trendline_lookback)
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
        
        # 尝试从波峰中识别上升趋势线
        bullish_trendlines = []
        if len(lows) >= self.config.trendline_min_touches:
            # 按时间排序
            sorted_lows = sorted(lows, key=lambda x: x['index'])
            
            # 尝试不同的组合
            for i in range(len(sorted_lows) - self.config.trendline_min_touches + 1):
                for j in range(i + 2, len(sorted_lows)):
                    # 选择三个点
                    selected_points = sorted_lows[i:j+1]
                    if len(selected_points) < 3:
                        continue
                    
                    trendline, r_squared = self.calculate_trendline(selected_points)
                    
                    if trendline and r_squared > self.config.r_squared_threshold:
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
        if len(highs) >= self.config.trendline_min_touches:
            # 按时间排序
            sorted_highs = sorted(highs, key=lambda x: x['index'])
            
            # 尝试不同的组合
            for i in range(len(sorted_highs) - self.config.trendline_min_touches + 1):
                for j in range(i + 2, len(sorted_highs)):
                    # 选择三个点
                    selected_points = sorted_highs[i:j+1]
                    if len(selected_points) < 3:
                        continue
                    
                    trendline, r_squared = self.calculate_trendline(selected_points)
                    
                    if trendline and r_squared > self.config.r_squared_threshold:
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
        ema_fast = df['close'].ewm(span=self.config.macd_fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=self.config.macd_slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=self.config.macd_signal, adjust=False).mean()
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
        ema = self.calculate_ema(df, self.config.ema_period)
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
        
        # SMC结构一致性评分 (+2.0)
        if smc_data and smc_data['market_bias'] != 0:
            details['smc_consistency'] = self.config.smc_weight
            score += self.config.smc_weight
        else:
            details['smc_consistency'] = 0.0
        
        # 趋势线突破强度评分 (+1.5)
        trendline_score = 0.0
        if trendline_data:
            if (trendline_data['bullish_breakout'] or 
                (trendline_data['bearish_trendline'] and 
                 trendline_data['bearish_trendline']['r_squared'] > 0.9)):
                trendline_score = self.config.trendline_weight
            elif (trendline_data['bearish_breakout'] or 
                  (trendline_data['bullish_trendline'] and 
                   trendline_data['bullish_trendline']['r_squared'] > 0.9)):
                trendline_score = self.config.trendline_weight
        
        details['trendline_breakout'] = trendline_score
        score += trendline_score
        
        # 12 EMA位置评分 (+1.0)
        ema_score = 0.0
        if momentum_data and momentum_data['ema_position'] != 0:
            ema_score = self.config.ema_weight
        
        details['ema_position'] = ema_score
        score += ema_score
        
        # MACD柱状图状态评分 (+1.0)
        macd_score = 0.0
        if momentum_data:
            if momentum_data['histogram_divergence'] != 0 or momentum_data['macd_cross'] != 0:
                macd_score = self.config.macd_weight
        
        details['macd_histogram'] = macd_score
        score += macd_score
        
        # OB/FVG汇合评分 (+1.5)
        ob_fvg_score = 0.0
        if smc_data:
            if smc_data['nearby_bullish_ob'] or smc_data['nearby_bullish_fvg']:
                ob_fvg_score = self.config.ob_fvg_weight
            elif smc_data['nearby_bearish_ob'] or smc_data['nearby_bearish_fvg']:
                ob_fvg_score = self.config.ob_fvg_weight
        
        details['ob_fvg_confluence'] = ob_fvg_score
        score += ob_fvg_score
        
        return {
            'score': score,
            'details': details,
            'threshold_full': self.config.full_position_threshold,
            'threshold_half': self.config.half_position_threshold
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

class RiskManager:
    """风险管理系统"""
    
    def __init__(self, config):
        self.config = config
        self.daily_start_balance = None
        self.daily_pnl = Decimal('0')
        self.positions_count = 0
        
    def check_daily_loss_limit(self):
        """检查日内亏损限制"""
        account_info = mt5.account_info()
        if account_info is None:
            return True
        
        equity = Decimal(str(account_info.equity))
        
        # 如果是第一次运行，记录初始余额
        if self.daily_start_balance is None:
            self.daily_start_balance = equity
            self.daily_pnl = Decimal('0')
            return True
        
        # 计算日内盈亏
        current_pnl = equity - self.daily_start_balance
        
        # 检查是否超过日内最大亏损限制
        if current_pnl < -self.daily_start_balance * self.config.daily_loss_limit:
            logger.warning(f"触发日内最大亏损限制: {current_pnl}")
            return False
        
        return True
    
    def check_max_positions(self):
        """检查是否超过最大持仓数"""
        positions = mt5.positions_get()
        if positions is None:
            return True
        
        current_positions = len(positions)
        self.positions_count = current_positions
        
        return current_positions < self.config.max_positions
    
    def check_margin(self):
        """检查保证金是否充足"""
        account_info = mt5.account_info()
        if account_info is None:
            return False
        
        margin_free = Decimal(str(account_info.margin_free))
        margin_used = Decimal(str(account_info.margin_used))
        
        # 如果使用的保证金大于可用保证金的80%，返回False
        if margin_used > 0 and (margin_free / margin_used) < Decimal('0.25'):
            logger.warning("保证金不足")
            return False
        
        return True
    
    def calculate_stop_loss(self, entry_price, direction, smc_data, momentum_data):
        """计算止损位"""
        sl_price = None
        
        if direction == 1:  # 做多
            # 优先使用订单块下沿作为止损
            if smc_data and smc_data['nearby_bullish_ob']:
                sl_price = smc_data['nearby_bullish_ob']['low']
            # 或者使用FVG下沿
            elif smc_data and smc_data['nearby_bullish_fvg']:
                sl_price = smc_data['nearby_bullish_fvg']['bottom']
            # 或者使用12 EMA下方
            elif momentum_data:
                sl_price = momentum_data['ema'] * Decimal('0.998')
        else:  # 做空
            # 优先使用订单块上沿作为止损
            if smc_data and smc_data['nearby_bearish_ob']:
                sl_price = smc_data['nearby_bearish_ob']['high']
            # 或者使用FVG上沿
            elif smc_data and smc_data['nearby_bearish_fvg']:
                sl_price = smc_data['nearby_bearish_fvg']['top']
            # 或者使用12 EMA上方
            elif momentum_data:
                sl_price = momentum_data['ema'] * Decimal('1.002')
        
        return sl_price
    
    def check_min_rrr(self, entry_price, sl_price, tp_price):
        """检查是否满足最小盈亏比"""
        if sl_price is None or tp_price is None:
            return True
        
        risk = abs(entry_price - sl_price)
        reward = abs(tp_price - entry_price)
        
        if risk == 0:
            return True
        
        rrr = reward / risk
        return rrr >= self.config.min_rrr
    
    def update_trailing_stop(self, position, momentum_data):
        """更新追踪止损"""
        if position is None or momentum_data is None:
            return None
        
        if position.sl == 0:
            return None
        
        current_price = mt5.symbol_info_tick(position.symbol).bid if position.type == 0 else \
                        mt5.symbol_info_tick(position.symbol).ask
        entry_price = position.price_open
        sl_price = position.sl
        
        # 计算当前盈亏比
        risk = abs(entry_price - sl_price)
        current_reward = abs(current_price - entry_price) if position.type == 0 else abs(entry_price - current_price)
        
        if risk == 0:
            return None
        
        current_rrr = current_reward / risk
        
        new_sl = None
        
        # 盈亏比达到1.5时，移动止损到保本位置
        if current_rrr >= self.config.break_even_at_rrr:
            new_sl = entry_price
        
        # 盈亏比达到2.0时，使用12 EMA作为追踪止损
        elif current_rrr >= self.config.trailing_start_rrr:
            if position.type == 0:  # 做多
                if momentum_data['ema'] > new_sl:
                    new_sl = momentum_data['ema']
            else:  # 做空
                if momentum_data['ema'] < new_sl:
                    new_sl = momentum_data['ema']
        
        return new_sl

class OrderManager:
    """订单管理器"""
    
    def __init__(self, config):
        self.config = config
    
    def open_position(self, symbol, direction, volume, entry_price, sl_price, tp_price):
        """开仓"""
        # 获取品种信息
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logger.error(f"获取品种信息失败: {symbol}")
            return None
        
        # 确保品种在市场观察中
        if not symbol_info.visible:
            if not mt5.symbol_select(symbol, True):
                logger.error(f"品种 {symbol} 无法添加到市场观察")
                return None
        
        # 准备订单请求
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(volume),
            "type": mt5.ORDER_TYPE_BUY if direction == 1 else mt5.ORDER_TYPE_SELL,
            "price": float(entry_price),
            "sl": float(sl_price) if sl_price is not None else 0.0,
            "tp": float(tp_price) if tp_price is not None else 0.0,
            "deviation": 20,
            "magic": self.config.magic,
            "comment": "SMC Sniper",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # 发送订单
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"开仓失败: {result.comment}")
            return None
        
        logger.info(f"开仓成功: {symbol} {direction} {volume} @ {entry_price}")
        return result
    
    def close_position(self, position):
        """平仓"""
        # 准备平仓请求
        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": position.ticket,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": mt5.ORDER_TYPE_BUY if position.type == 1 else mt5.ORDER_TYPE_SELL,
            "price": mt5.symbol_info_tick(position.symbol).bid if position.type == 0 else \
                    mt5.symbol_info_tick(position.symbol).ask,
            "deviation": 20,
            "magic": position.magic,
            "comment": "Close Position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # 发送平仓订单
        result = mt5.order_send(close_request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"平仓失败: {result.comment}")
            return False
        
        logger.info(f"平仓成功: {position.symbol} Ticket {position.ticket}")
        return True
    
    def modify_position_sl(self, position, new_sl):
        """修改持仓止损"""
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": position.ticket,
            "symbol": position.symbol,
            "sl": float(new_sl),
            "tp": position.tp,
            "deviation": 20,
        }
        
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"修改止损失败: {result.comment}")
            return False
        
        logger.info(f"修改止损成功: {position.symbol} Ticket {position.ticket} New SL: {new_sl}")
        return True

class TradingBot:
    """高汇合度交易机器人"""
    
    def __init__(self):
        self.config = TradingConfig()
        self.position_engine = PositionEngine()
        self.smc_analyzer = SMCAnalyzer(self.config)
        self.trendline_analyzer = TrendlineAnalyzer(self.config)
        self.momentum_analyzer = MomentumAnalyzer(self.config)
        self.confluence_analyzer = ConfluenceAnalyzer(self.config)
        self.risk_manager = RiskManager(self.config)
        self.order_manager = OrderManager(self.config)
        
        self.is_running = False
        self.last_analysis_time = None
    
    def initialize(self):
        """初始化MT5连接"""
        if not mt5.initialize():
            logger.error(f"MT5初始化失败: {mt5.last_error()}")
            return False
        
        # 获取账户信息
        account_info = mt5.account_info()
        if account_info is None:
            logger.error("获取账户信息失败")
            return False
        
        logger.info(f"账户: {account_info.login} 服务器: {account_info.server}")
        logger.info(f"余额: {account_info.balance} 权益: {account_info.equity}")
        
        return True
    
    def shutdown(self):
        """关闭MT5连接"""
        self.is_running = False
        mt5.shutdown()
        logger.info("MT5连接已关闭")
    
    def analyze_market(self):
        """分析市场并生成交易信号"""
        symbol = self.config.symbol
        
        # 1. SMC分析
        smc_data = self.smc_analyzer.analyze_market_structure(symbol, self.config.higher_timeframe)
        
        # 2. 趋势线分析
        trendline_data = self.trendline_analyzer.analyze(symbol, self.config.timeframe)
        
        # 3. 动量分析
        momentum_data = self.momentum_analyzer.analyze(symbol, self.config.timeframe)
        
        # 4. 汇合度评分
        confluence_result = self.confluence_analyzer.calculate_confluence_score(
            smc_data, trendline_data, momentum_data
        )
        
        return {
            'smc': smc_data,
            'trendline': trendline_data,
            'momentum': momentum_data,
            'confluence': confluence_result
        }
    
    def generate_signal(self, analysis_result):
        """生成交易信号"""
        confluence_result = analysis_result['confluence']
        smc_data = analysis_result['smc']
        momentum_data = analysis_result['momentum']
        
        # 检查汇合度评分
        score = confluence_result['score']
        multiplier = self.confluence_analyzer.determine_position_size_multiplier(confluence_result)
        
        if multiplier == 0:
            return None  # 汇合度不足，不交易
        
        # 确定交易方向
        direction = 0
        
        if (smc_data and smc_data['market_bias'] == 1 and 
            momentum_data and momentum_data['ema_position'] == 1 and
            momentum_data['histogram_divergence'] >= 0):
            direction = 1  # 做多
        elif (smc_data and smc_data['market_bias'] == -1 and 
              momentum_data and momentum_data['ema_position'] == -1 and
              momentum_data['histogram_divergence'] <= 0):
            direction = -1  # 做空
        
        if direction == 0:
            return None  # 无法确定交易方向
        
        return {
            'direction': direction,
            'multiplier': multiplier,
            'score': score
        }
    
    def execute_trade(self, signal, analysis_result):
        """执行交易"""
        symbol = self.config.symbol
        
        # 获取当前价格
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return False
        
        entry_price = Decimal(str(tick.ask)) if signal['direction'] == 1 else Decimal(str(tick.bid))
        
        # 计算止损
        smc_data = analysis_result['smc']
        momentum_data = analysis_result['momentum']
        sl_price = self.risk_manager.calculate_stop_loss(
            entry_price, signal['direction'], smc_data, momentum_data
        )
        
        if sl_price is None:
            logger.warning("无法确定止损位，取消交易")
            return False
        
        # 计算止盈（基于最小盈亏比）
        risk = abs(entry_price - sl_price)
        tp_price = (entry_price + risk * self.config.min_rrr) if signal['direction'] == 1 else \
                   (entry_price - risk * self.config.min_rrr)
        
        # 计算仓位大小
        base_risk = self.config.risk_percent * signal['multiplier']
        volume = self.position_engine.calculate_position_size(
            symbol, entry_price, sl_price, base_risk
        )
        
        # 检查最小盈亏比
        if not self.risk_manager.check_min_rrr(entry_price, sl_price, tp_price):
            logger.warning("不满足最小盈亏比，取消交易")
            return False
        
        # 开仓
        result = self.order_manager.open_position(
            symbol, signal['direction'], volume, entry_price, sl_price, tp_price
        )
        
        return result is not None
    
    def manage_positions(self, analysis_result):
        """管理现有持仓"""
        symbol = self.config.symbol
        positions = mt5.positions_get(symbol=symbol)
        
        if positions is None:
            return
        
        for position in positions:
            # 只管理本系统开的仓位
            if position.magic != self.config.magic:
                continue
            
            # 获取当前价格
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                continue
            
            current_price = Decimal(str(tick.bid)) if position.type == 0 else Decimal(str(tick.ask))
            
            # 检查是否触及止损或止盈
            if position.sl != 0:
                sl_hit = (position.type == 0 and current_price <= Decimal(str(position.sl))) or \
                         (position.type == 1 and current_price >= Decimal(str(position.sl)))
                
                if sl_hit:
                    logger.info(f"触发止损: {symbol} Ticket {position.ticket}")
                    self.order_manager.close_position(position)
                    continue
            
            if position.tp != 0:
                tp_hit = (position.type == 0 and current_price >= Decimal(str(position.tp))) or \
                         (position.type == 1 and current_price <= Decimal(str(position.tp)))
                
                if tp_hit:
                    logger.info(f"触发止盈: {symbol} Ticket {position.ticket}")
                    self.order_manager.close_position(position)
                    continue
            
            # 更新追踪止损
            momentum_data = analysis_result['momentum']
            new_sl = self.risk_manager.update_trailing_stop(position, momentum_data)
            
            if new_sl is not None and new_sl != position.sl:
                self.order_manager.modify_position_sl(position, new_sl)
    
    def run(self):
        """运行交易机器人"""
        logger.info("启动高汇合度交易机器人...")
        
        if not self.initialize():
            return
        
        self.is_running = True
        
        try:
            while self.is_running:
                # 检查风险限制
                if not self.risk_manager.check_daily_loss_limit():
                    logger.warning("触发日内最大亏损限制，暂停交易")
                    time.sleep(60)
                    continue
                
                if not self.risk_manager.check_max_positions():
                    time.sleep(10)
                    continue
                
                if not self.risk_manager.check_margin():
                    time.sleep(10)
                    continue
                
                # 检查是否是新K线
                current_time = datetime.now()
                if self.last_analysis_time is None or \
                   (current_time.minute % 15 == 0 and current_time.second == 0 and 
                    self.last_analysis_time.minute != current_time.minute):
                    
                    logger.info(f"\n{'='*50}")
                    logger.info(f"分析时间: {current_time}")
                    self.last_analysis_time = current_time
                    
                    # 分析市场
                    analysis_result = self.analyze_market()
                    
                    # 管理现有持仓
                    self.manage_positions(analysis_result)
                    
                    # 生成交易信号
                    signal = self.generate_signal(analysis_result)
                    
                    if signal:
                        logger.info(f"生成交易信号: 方向={signal['direction']}, "
                                  f"评分={signal['score']:.2f}, 仓位={signal['multiplier']*100:.0f}%")
                        
                        # 执行交易
                        self.execute_trade(signal, analysis_result)
                
                time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("收到停止信号，正在退出...")
        except Exception as e:
            logger.error(f"发生错误: {e}")
        finally:
            self.shutdown()

def main():
    """主函数"""
    bot = TradingBot()
    bot.run()

if __name__ == "__main__":
    main()