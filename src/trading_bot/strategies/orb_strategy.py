import pandas as pd
import numpy as np
import logging
from datetime import datetime, time as dtime
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
        self.last_warning_date = None
        self.last_success_date = None
        
        # Stats
        self.range_mean = 0.0
        self.range_std = 0.0
        
        # Real-time state
        self.monitoring_active = True
        
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
            self.range_std = np.sqrt(moments[1]) 
        else:
            self.range_mean = mu
            self.range_std = sigma

    def calculate_orb_levels(self, df_h1, point=0.01):
        """
        Calculate ORB levels based on H1 data (Standard logic)
        """
        if df_h1 is None or len(df_h1) < 1:
            return None, None, False
            
        self.last_h1_df = df_h1

        if 'time' in df_h1.columns:
            time_col = df_h1['time']
            if not isinstance(time_col.dtype, np.dtype) or str(time_col.dtype) != 'datetime64[ns]':
                try:
                    if np.issubdtype(time_col.dtype, np.integer):
                        df_h1['time'] = pd.to_datetime(df_h1['time'], unit='s')
                    else:
                        df_h1['time'] = pd.to_datetime(df_h1['time'])
                except Exception:
                    df_h1['time'] = pd.to_datetime(df_h1['time'], errors='coerce')
            df_h1 = df_h1.set_index('time')
        elif not isinstance(df_h1.index, pd.DatetimeIndex):
            df_h1.index = pd.to_datetime(df_h1.index, errors='coerce')

        # Use Completed Candles Only
        completed_df = df_h1
        if len(df_h1) > 1:
            completed_df = df_h1.iloc[:-1]
        
        if len(completed_df) < 1:
             return None, None, False

        last_candle_time = completed_df.index[-1]
        today = last_candle_time.date()
        
        # Reset Daily Counters if new day
        if self.last_trade_date != today:
            self.last_trade_date = today
            self.trades_today_count = 0
            self.long_signal_taken_today = False
            self.short_signal_taken_today = False
            self.last_signal_candle_time = None
        
        today_data = completed_df[completed_df.index.date == today]
        open_candle = today_data[today_data.index.hour == self.open_hour]
        
        if open_candle.empty:
            if self.last_warning_date != today:
                logger.warning(f"ORB Open Candle not found for {today} (Hour {self.open_hour}). Data range: {completed_df.index[0]} to {completed_df.index[-1]}")
                self.last_warning_date = today 
            self.final_range_high = None
            self.final_range_low = None
            self.is_range_final = False
            return None, None, False

        def get_effective_range(row):
            c_high = row['high']
            c_low = row['low']
            c_open = row['open']
            c_close = row['close']
            c_body_high = max(c_open, c_close)
            c_body_low = min(c_open, c_close)
            
            limit = 500 * point 
            eff_high = c_high
            eff_low = c_low
            
            if (c_high - c_body_high) > limit:
                eff_high = c_body_high
            if (c_body_low - c_low) > limit:
                eff_low = c_body_low
            return eff_high, eff_low, c_body_high, c_body_low

        open_row = open_candle.iloc[0]
        initial_high, initial_low, _, _ = get_effective_range(open_row)
        
        subsequent_candles = today_data[today_data.index > open_candle.index[0]]
        
        current_high = initial_high
        current_low = initial_low
        current_body_high = max(open_row['open'], open_row['close']) 
        current_body_low = min(open_row['open'], open_row['close'])
        
        consolidation_count = 0
        is_final = False
        consolidation_prices = [open_row['close']]
        
        for time_idx, row in subsequent_candles.iterrows():
            c_high, c_low, c_body_high, c_body_low = get_effective_range(row)
            
            if c_high <= current_high and c_low >= current_low:
                consolidation_count += 1
                consolidation_prices.append(row['close'])
            else:
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
                    consolidation_prices = [row['close']] 
                else:
                    consolidation_prices.append(row['close'])
            
            if consolidation_count >= self.consolidation_candles:
                is_final = True
                break
        
        self.final_range_high = current_high
        self.final_range_low = current_low
        self.is_range_final = is_final
        self.current_consolidation_count = consolidation_count
        
        if len(consolidation_prices) >= 2:
            stats_df = pd.DataFrame({'close': consolidation_prices})
            self.calculate_range_statistics(stats_df)
            
        if is_final and self.last_success_date != today:
            self.last_success_date = today
            logger.info(f"ORB Range Finalized: High={self.final_range_high}, Low={self.final_range_low}, Consolidation Count={consolidation_count}")
        
        return self.final_range_high, self.final_range_low, self.is_range_final

    def check_realtime_breakout(self, current_price, current_time_msc=None, point=0.01):
        """
        High-Frequency Breakout Check (Millisecond Level Response)
        Returns: Signal Dict or None
        """
        # Ensure we have valid range levels
        if not self.is_range_final or self.final_range_high is None or self.final_range_low is None:
            return None
            
        if self.trades_today_count >= self.trades_per_day:
            return None

        # --- 24-Hour Monitor / Session Filter ---
        # Although ORB is usually an "opening" range breakout, once the range is defined,
        # we monitor it for the rest of the day (or until reset).
        # This function is called on every TICK, so it satisfies the "Real-time Signal Detection" requirement.
        
        signal = None
        
        if current_price > self.final_range_high:
            if not self.long_signal_taken_today:
                signal = 'buy'
        elif current_price < self.final_range_low:
            if not self.short_signal_taken_today:
                signal = 'sell'
                
        if signal:
            # Prevent double entry on same day
            if signal == 'buy':
                self.long_signal_taken_today = True
                self.trades_today_count += 1
                logger.info(f"ORB Realtime BUY Trigger: {current_price} > {self.final_range_high}")
            else:
                self.short_signal_taken_today = True
                self.trades_today_count += 1
                logger.info(f"ORB Realtime SELL Trigger: {current_price} < {self.final_range_low}")
                
            sl_dist = self.fixed_sl_points * point
            tp_dist = self.fixed_tp_points * point
            
            breakout_score = estimate_breakout_strength(current_price, self.range_mean, self.range_std)
            
            return {
                'signal': signal,
                'sl_dist': sl_dist,
                'tp_dist': tp_dist,
                'price': current_price,
                'sl_points': self.fixed_sl_points,
                'stats': {
                    'range_mean': self.range_mean,
                    'range_std': self.range_std,
                    'breakout_score': breakout_score,
                    'z_score': (current_price - self.range_mean) / self.range_std if self.range_std > 0 else 0
                }
            }
            
        return None

    def check_signal(self, current_price, df_h1=None, point=0.01):
        """
        Legacy Candle-Close Check (Compatible with existing calls)
        """
        if df_h1 is not None:
            self.calculate_orb_levels(df_h1, point=point)
        
        current_stats = {
            'range_high': self.final_range_high,
            'range_low': self.final_range_low,
            'is_range_final': self.is_range_final,
            'range_mean': self.range_mean,
            'range_std': self.range_std,
            'z_score': (current_price - self.range_mean) / self.range_std if self.range_std > 0 else 0,
            'breakout_score': estimate_breakout_strength(current_price, self.range_mean, self.range_std)
        }
        
        # We can reuse the realtime check here if we consider 'current_price' as the 'close' of the candle
        # But legacy logic required candle close > level.
        
        # Let's keep it consistent: check_signal is usually called at end of candle.
        # So we can just delegate to internal logic or return stats.
        
        # Note: If realtime check already triggered (via main loop tick listener), 
        # this method might return None because 'signal_taken_today' is already True.
        # This is desired behavior.
        
        return None, current_stats
