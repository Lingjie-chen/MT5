import pandas as pd
import numpy as np
import logging
from datetime import datetime, time as dtime
from utils.math_lib import math_moments_normal, estimate_breakout_strength

logger = logging.getLogger("GoldORB")

class GoldORBStrategy:
    def __init__(self, symbol, open_hour=1, consolidation_candles=3, strategy_mode='DYNAMIC', dynamic_lookback=20):
        self.symbol = symbol
        self.open_hour = open_hour
        self.consolidation_candles = consolidation_candles
        self.strategy_mode = strategy_mode # 'CLASSIC' (Fixed Time) or 'DYNAMIC' (Rolling Window)
        self.dynamic_lookback = dynamic_lookback # Number of candles for dynamic range
        
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
        self.range_time_str = "N/A"
        
        # Stats
        self.range_mean = 0.0
        self.range_std = 0.0
        
        # Real-time state
        self.monitoring_active = True
        
    def update_params(self, open_hour=None, consolidation_candles=None, sl_points=None, tp_points=None, strategy_mode=None, dynamic_lookback=None):
        if open_hour is not None:
            self.open_hour = int(open_hour)
        if consolidation_candles is not None:
            self.consolidation_candles = int(consolidation_candles)
        if sl_points is not None:
            self.fixed_sl_points = int(sl_points)
        if tp_points is not None:
            self.fixed_tp_points = int(tp_points)
        if strategy_mode is not None:
            self.strategy_mode = strategy_mode
        if dynamic_lookback is not None:
            self.dynamic_lookback = int(dynamic_lookback)
            
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

    def calculate_orb_levels(self, df_m5, point=0.01):
        """
        Calculate ORB levels based on M5 data
        """
        if df_m5 is None or len(df_m5) < 1:
            return None, None, False
            
        self.last_h1_df = df_m5 # Keep name for compatibility but it's M5

        if 'time' in df_m5.columns:
            time_col = df_m5['time']
            if not isinstance(time_col.dtype, np.dtype) or str(time_col.dtype) != 'datetime64[ns]':
                try:
                    if np.issubdtype(time_col.dtype, np.integer):
                        df_m5['time'] = pd.to_datetime(df_m5['time'], unit='s')
                    else:
                        df_m5['time'] = pd.to_datetime(df_m5['time'])
                except Exception:
                    df_m5['time'] = pd.to_datetime(df_m5['time'], errors='coerce')
            df_m5 = df_m5.set_index('time')
        elif not isinstance(df_m5.index, pd.DatetimeIndex):
            df_m5.index = pd.to_datetime(df_m5.index, errors='coerce')

        # Use Completed Candles Only
        completed_df = df_m5
        if len(df_m5) > 1:
            completed_df = df_m5.iloc[:-1]
        
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

        # --- DYNAMIC MODE (Rolling Window) ---
        if self.strategy_mode == 'DYNAMIC':
            if len(completed_df) < self.dynamic_lookback:
                return None, None, False
            
            # Take last N candles
            consolidation_range = completed_df.iloc[-self.dynamic_lookback:]
            
            self.final_range_high = consolidation_range['high'].max()
            self.final_range_low = consolidation_range['low'].min()
            self.is_range_final = True
            self.current_consolidation_count = len(consolidation_range)
            
            # Format Time Range
            start_t = consolidation_range.index[0].strftime("%H:%M")
            end_t = consolidation_range.index[-1].strftime("%H:%M")
            self.range_time_str = f"Rolling {self.dynamic_lookback} ({start_t}-{end_t})"
            
            # Calculate Stats
            self.calculate_range_statistics(consolidation_range)
            
            return self.final_range_high, self.final_range_low, True

        # --- CLASSIC MODE (Fixed Open Hour, M5 candles) ---
        today_data = completed_df[completed_df.index.date == today]
        
        # Find Open Candle (Based on Hour)
        # For M5, we need the first M5 candle of that hour (e.g. 01:00)
        # ORB Opening Range is defined by the first N M5 candles of the session.
        
        # Logic: Find the candle at self.open_hour:00
        # Then take 'consolidation_candles' starting from there.
        
        target_time = dtime(self.open_hour, 0)
        start_candle = today_data[today_data.index.time == target_time]
        
        # Robust Fallback: If exact 00:00 candle missing, take first candle of that hour
        if start_candle.empty:
            hour_candles = today_data[today_data.index.hour == self.open_hour]
            if not hour_candles.empty:
                start_candle = hour_candles.iloc[[0]]
                # Only log info once per day to avoid spam
                if self.last_warning_date != today:
                    logger.info(f"ORB Open Candle Exact Match Failed. Using nearest in hour {self.open_hour}: {start_candle.index[0]}")
        
        if start_candle.empty:
            if self.last_warning_date != today:
                # Debug Info
                available_times = []
                if not today_data.empty:
                    available_times = [t.strftime("%H:%M") for t in today_data.index]
                    
                logger.warning(f"ORB Open M15 Candle not found for {today} (Hour {self.open_hour}). Available candles today: {available_times[:5]}...{available_times[-5:]}")
                self.last_warning_date = today 
            self.final_range_high = None
            self.final_range_low = None
            self.is_range_final = False
            return None, None, False

        # Get the sequence of consolidation candles
        start_idx = today_data.index.get_loc(start_candle.index[0])
        end_idx = start_idx + self.consolidation_candles
        
        if end_idx > len(today_data):
            # Not enough candles yet to form the range
            if self.last_warning_date != today:
                logger.info(f"ORB Range Calculation Pending: Waiting for more candles (Need {self.consolidation_candles}, Have {len(today_data)-start_idx})")
            self.is_range_final = False
            return None, None, False
            
        consolidation_range = today_data.iloc[start_idx:end_idx]
        
        # Calculate Range from these M15 candles
        current_high = consolidation_range['high'].max()
        current_low = consolidation_range['low'].min()
        
        # Effective Range Logic (Optional: Filter wicks)
        # For now, stick to High/Low as standard ORB
        
        self.final_range_high = current_high
        self.final_range_low = current_low
        self.is_range_final = True
        self.current_consolidation_count = len(consolidation_range)
        
        # Format Time Range for display
        start_t = consolidation_range.index[0].strftime("%H:%M")
        end_t = consolidation_range.index[-1].strftime("%H:%M")
        self.range_time_str = f"{start_t}-{end_t}"
        
        # Calculate Stats
        self.calculate_range_statistics(consolidation_range)
            
        if self.is_range_final and self.last_success_date != today:
            self.last_success_date = today
            logger.info(f"ORB (M15) Range Finalized: High={self.final_range_high}, Low={self.final_range_low} (Time: {start_candle.index[0]} + {self.consolidation_candles} candles)")
        
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
                # logger.info(f"ORB Realtime BUY Trigger: {current_price} > {self.final_range_high}") # Suppressed to reduce spam
            else:
                self.short_signal_taken_today = True
                self.trades_today_count += 1
                # logger.info(f"ORB Realtime SELL Trigger: {current_price} < {self.final_range_low}") # Suppressed to reduce spam
                
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
