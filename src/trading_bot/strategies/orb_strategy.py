import pandas as pd
import numpy as np
import logging
from utils.math_lib import math_moments_normal, estimate_breakout_strength

logger = logging.getLogger("GoldORB")

class GoldORBStrategy:
    def __init__(self, symbol, open_hour=1, consolidation_candles=3):
        self.symbol = symbol
        self.open_hour = open_hour
        self.consolidation_candles = consolidation_candles
        self.final_range_high = None
        self.final_range_low = None
        self.is_range_final = False
        self.current_consolidation_count = 0
        self.last_processed_time = None
        
        # Fixed SL/TP from GOLD_ORB Repo (Default)
        self.use_fixed_sl_tp = True
        self.fixed_sl_points = 400
        self.fixed_tp_points = 1200
        
        # State for Signal Logic
        self.last_h1_df = None
        self.trades_per_day = 2
        self.trades_today_count = 0
        self.last_trade_date = None
        self.long_signal_taken_today = False
        self.short_signal_taken_today = False
        self.last_signal_candle_time = None
        
        # Stats
        self.range_mean = 0.0
        self.range_std = 0.0

    def update_params(self, open_hour=None, consolidation_candles=None, sl_points=None, tp_points=None):
        if open_hour is not None:
            self.open_hour = int(open_hour)
        if consolidation_candles is not None:
            self.consolidation_candles = int(consolidation_candles)
        if sl_points is not None:
            self.fixed_sl_points = int(sl_points)
        if tp_points is not None:
            self.fixed_tp_points = int(tp_points)
            
        # Reset calculation state
        self.final_range_high = None
        self.final_range_low = None
        self.is_range_final = False
        self.current_consolidation_count = 0
        self.last_processed_time = None
        # Do not reset trade counts

    def calculate_range_statistics(self, consolidation_data):
        """
        Calculate statistical properties of the consolidation range.
        Uses MathLib for consistency with strategy requirements.
        """
        if consolidation_data is None or len(consolidation_data) < 2:
            return
            
        prices = consolidation_data['close'].values
        mu = np.mean(prices)
        sigma = np.std(prices)
        
        # Using MathLib wrapper (returns tuple)
        moments = math_moments_normal(mu, sigma)
        if moments:
            self.range_mean = moments[0]
            # Moment returns variance (sigma^2), we store sigma for Z-score calc
            self.range_std = np.sqrt(moments[1]) 
        else:
            self.range_mean = mu
            self.range_std = sigma

    def calculate_orb_levels(self, df_h1, point=0.01):
        """
        Calculate ORB levels based on H1 data (Standard logic) 
        OR M5/M15 logic if user switches timeframe logic.
        But standard ORB is usually H1-based (Open Hour).
        We keep H1 as source for the "Hour" logic, but logic handles consolidation.
        """
        if df_h1 is None or len(df_h1) < 1:
            return None, None, False
            
        # Store for check_signal usage
        self.last_h1_df = df_h1

        # Ensure index is datetime
        if not isinstance(df_h1.index, pd.DatetimeIndex):
            df_h1.index = pd.to_datetime(df_h1.index)

        # Use Completed Candles Only (Exclude current open candle at -1)
        # Assuming df_h1 includes current candle.
        completed_df = df_h1.iloc[:-1]
        
        if len(completed_df) < 1:
             return None, None, False

        # Get today's date from the last COMPLETED candle
        last_candle_time = completed_df.index[-1]
        today = last_candle_time.date()
        
        # Reset Daily Counters if new day
        if self.last_trade_date != today:
            self.last_trade_date = today
            self.trades_today_count = 0
            self.long_signal_taken_today = False
            self.short_signal_taken_today = False
            self.last_signal_candle_time = None
        
        # Find the "Open Candle" for today
        today_data = completed_df[completed_df.index.date == today]
        
        open_candle = today_data[today_data.index.hour == self.open_hour]
        
        if open_candle.empty:
            self.final_range_high = None
            self.final_range_low = None
            self.is_range_final = False
            self.current_consolidation_count = 0
            return None, None, False

        # Helper: Get effective high/low (filtering long wicks)
        def get_effective_range(row):
            c_high = row['high']
            c_low = row['low']
            c_open = row['open']
            c_close = row['close']
            c_body_high = max(c_open, c_close)
            c_body_low = min(c_open, c_close)
            
            # 500 points logic
            limit = 500 * point 
            
            eff_high = c_high
            eff_low = c_low
            
            # Filter Long Upper Wick
            if (c_high - c_body_high) > limit:
                eff_high = c_body_high
                
            # Filter Long Lower Wick
            if (c_body_low - c_low) > limit:
                eff_low = c_body_low
                
            return eff_high, eff_low, c_body_high, c_body_low

        # Initial Range
        open_row = open_candle.iloc[0]
        initial_high, initial_low, _, _ = get_effective_range(open_row)
        
        # Get candles AFTER the open candle
        subsequent_candles = today_data[today_data.index > open_candle.index[0]]
        
        current_high = initial_high
        current_low = initial_low
        current_body_high = max(open_row['open'], open_row['close']) 
        current_body_low = min(open_row['open'], open_row['close'])
        
        consolidation_count = 0
        is_final = False
        
        # Collect data for statistics
        consolidation_prices = [open_row['close']]
        
        for time, row in subsequent_candles.iterrows():
            c_high, c_low, c_body_high, c_body_low = get_effective_range(row)
            
            # Check if this candle is inside the current range
            if c_high <= current_high and c_low >= current_low:
                consolidation_count += 1
                consolidation_prices.append(row['close'])
            else:
                # Range expansion logic
                is_expansion = False
                
                if c_high > current_high:
                    if c_body_high > current_body_high:
                        current_high = c_high
                        current_body_high = c_body_high
                        is_expansion = True
                
                if c_low < current_low:
                    if c_body_low < current_body_low:
                        current_low = c_low
                        current_body_low = c_body_low
                        is_expansion = True
                
                if is_expansion:
                    consolidation_count = 0
                    consolidation_prices = [row['close']] # Reset stats on expansion? Or keep rolling? 
                    # Logic: New range definition starts, but volatility context is continuous.
                    # For simplicity, let's keep recent history or just reset to reflect current tight range.
                    # Resetting matches the "Consolidation" concept.
                else:
                    consolidation_prices.append(row['close'])
            
            if consolidation_count >= self.consolidation_candles:
                is_final = True
                break
        
        self.final_range_high = current_high
        self.final_range_low = current_low
        self.is_range_final = is_final
        self.current_consolidation_count = consolidation_count
        
        # Calculate Stats if final
        if is_final:
            # Create a mini DF for calc
            stats_df = pd.DataFrame({'close': consolidation_prices})
            self.calculate_range_statistics(stats_df)
        
        if is_final and self.last_processed_time != today:
             self.last_processed_time = today
        
        return self.final_range_high, self.final_range_low, self.is_range_final

    def check_signal(self, current_price, df_h1=None, point=0.01):
        """
        Check for Breakout/Breakdown signal.
        Strictly follows 'Confirmed Candle Breakout' logic from Repo.
        Checks limits (Max Trades Per Day).
        """
        # If df_h1 provided, update levels (and store df)
        if df_h1 is not None:
            self.calculate_orb_levels(df_h1, point=point)
        
        # Use stored DF if argument is None
        target_df = df_h1 if df_h1 is not None else self.last_h1_df
        
        if not self.is_range_final or self.final_range_high is None or self.final_range_low is None:
            return None
            
        if target_df is None or len(target_df) < 2:
            return None
            
        # Check Max Trades Per Day
        if self.trades_today_count >= self.trades_per_day:
            return None

        # Last CLOSED candle is at -2 (assuming -1 is current open)
        # Verify assumption: Check if index[-1] is current hour.
        # But safest is -2.
        last_closed_candle = target_df.iloc[-2]
        candle_time = last_closed_candle.name
        
        # Avoid double signaling on the same candle
        if self.last_signal_candle_time == candle_time:
            return None
        
        c_close = last_closed_candle['close']
        c_open = last_closed_candle['open']
        
        # Buy Signal
        if c_close > c_open and c_close > self.final_range_high:
            if not self.long_signal_taken_today:
                self.long_signal_taken_today = True
                self.trades_today_count += 1
                self.last_signal_candle_time = candle_time
                logger.info(f"ORB BUY Signal Confirmed (Candle {candle_time})")
                
                sl_dist = self.fixed_sl_points * point
                tp_dist = self.fixed_tp_points * point
                
                # Calculate Statistical Strength
                breakout_score = estimate_breakout_strength(c_close, self.range_mean, self.range_std)
                
                return {
                    'signal': 'buy',
                    'sl_dist': sl_dist,
                    'tp_dist': tp_dist,
                    'price': c_close,
                    'sl_points': self.fixed_sl_points, # For risk calc
                    'stats': {
                        'range_mean': self.range_mean,
                        'range_std': self.range_std,
                        'breakout_score': breakout_score,
                        'z_score': (c_close - self.range_mean) / self.range_std if self.range_std > 0 else 0
                    }
                }
            
        # Sell Signal
        if c_close < c_open and c_close < self.final_range_low:
            if not self.short_signal_taken_today:
                self.short_signal_taken_today = True
                self.trades_today_count += 1
                self.last_signal_candle_time = candle_time
                logger.info(f"ORB SELL Signal Confirmed (Candle {candle_time})")
                
                sl_dist = self.fixed_sl_points * point
                tp_dist = self.fixed_tp_points * point
                
                # Calculate Statistical Strength
                breakout_score = estimate_breakout_strength(c_close, self.range_mean, self.range_std)
                
                return {
                    'signal': 'sell',
                    'sl_dist': sl_dist,
                    'tp_dist': tp_dist,
                    'price': c_close,
                    'sl_points': self.fixed_sl_points,
                    'stats': {
                        'range_mean': self.range_mean,
                        'range_std': self.range_std,
                        'breakout_score': breakout_score,
                        'z_score': (c_close - self.range_mean) / self.range_std if self.range_std > 0 else 0
                    }
                }
            
        return None
