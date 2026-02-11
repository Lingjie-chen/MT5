import pandas as pd
import numpy as np
import logging

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

    def update_params(self, open_hour=None, consolidation_candles=None):
        if open_hour is not None:
            self.open_hour = int(open_hour)
        if consolidation_candles is not None:
            self.consolidation_candles = int(consolidation_candles)
        # Reset state on param change
        self.final_range_high = None
        self.final_range_low = None
        self.is_range_final = False
        self.current_consolidation_count = 0
        self.last_processed_time = None

    def calculate_orb_levels(self, df_h1, point=0.01):
        """
        Calculate ORB levels based on H1 data.
        Should be called on every new candle close or tick.
        
        Logic:
        1. Find the first candle of the current day (defined by open_hour).
        2. Set initial range (High/Low, but handle Long Wick filtering).
        3. Check subsequent candles for consolidation.
        4. Finalize range.
        """
        if df_h1 is None or len(df_h1) < 1:
            return None, None, False

        # Ensure index is datetime
        if not isinstance(df_h1.index, pd.DatetimeIndex):
            df_h1.index = pd.to_datetime(df_h1.index)

        # Get today's date from the last candle
        last_candle_time = df_h1.index[-1]
        today = last_candle_time.date()
        
        # Find the "Open Candle" for today (e.g., 01:00)
        # We need the candle that OPENS at self.open_hour
        today_data = df_h1[df_h1.index.date == today]
        
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
            # Assuming 'point' is provided. For Gold (2 digits), point=0.01. 500 points = 5.0.
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
        current_body_high = max(open_row['open'], open_row['close']) # Track body for strict expansion check
        current_body_low = min(open_row['open'], open_row['close'])
        
        consolidation_count = 0
        is_final = False
        
        for time, row in subsequent_candles.iterrows():
            c_high, c_low, c_body_high, c_body_low = get_effective_range(row)
            
            # Check if this candle is inside the current range
            # Note: Repo logic expands if wick > range AND body > range body (significant move)
            # Simplified: If candle is inside, increment count.
            if c_high <= current_high and c_low >= current_low:
                consolidation_count += 1
            else:
                # Range expansion logic from repo:
                # if(previous_candle.wick_high > range.wick_high && ... && previous_candle.body_high > range.body_high ...)
                
                is_expansion = False
                
                if c_high > current_high:
                    # Check significance (body must also be higher to confirm strength?)
                    # Repo: previous_candle.body_high > range.body_high
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
                else:
                    # If it broke wick but not body (weak breakout), maybe we don't reset?
                    # Repo resets on valid expansion.
                    # If we are here, it means it is NOT fully inside.
                    # But if we didn't expand (because body check failed), what do we do?
                    # The repo code logic is:
                    # if (inside) -> count++
                    # else -> check expansion.
                    # if (expansion conditions met) -> update & reset.
                    # what if neither? (e.g. wick broke out but body didn't).
                    # It falls through. Count does NOT increment. Count stays same?
                    # Repo: "else" of expansion check is implicit fallthrough.
                    # So if not inside, and not valid expansion -> count pauses?
                    pass 
            
            if consolidation_count >= self.consolidation_candles:
                is_final = True
                break
        
        self.final_range_high = current_high
        self.final_range_low = current_low
        self.is_range_final = is_final
        self.current_consolidation_count = consolidation_count
        
        if is_final and self.last_processed_time != today:
             self.last_processed_time = today
        
        return self.final_range_high, self.final_range_low, self.is_range_final

    def check_signal(self, current_price, df_h1=None, point=0.01):
        """
        Check for Breakout/Breakdown signal.
        Strictly follows 'Confirmed Candle Breakout' logic from Repo.
        """
        if df_h1 is not None:
            self.calculate_orb_levels(df_h1, point=point)
        
        if not self.is_range_final or self.final_range_high is None or self.final_range_low is None:
            return None
            
        # Repo Logic: Signal triggers if *Previous Candle* broke out.
        # We need to check the last CLOSED candle in df_h1.
        if df_h1 is None or len(df_h1) < 1:
            return None
            
        last_candle = df_h1.iloc[-1]
        
        # Check if last candle is strictly AFTER the consolidation phase?
        # The calculate_orb_levels runs up to the last candle.
        # If is_range_final is True, it means we have a range.
        # We need to check if the *last* candle broke it.
        
        c_close = last_candle['close']
        c_open = last_candle['open']
        c_high = last_candle['high']
        c_low = last_candle['low']
        
        # Buy Signal:
        # 1. Bullish Candle (Close > Open)
        # 2. Body High (Close) > Range High
        if c_close > c_open and c_close > self.final_range_high:
            return 'buy'
            
        # Sell Signal:
        # 1. Bearish Candle (Close < Open)
        # 2. Body Low (Close) < Range Low
        if c_close < c_open and c_close < self.final_range_low:
            return 'sell'
            
        return None

    def get_state(self):
        return {
            "final_high": self.final_range_high,
            "final_low": self.final_range_low,
            "is_final": self.is_range_final,
            "consolidation_count": self.current_consolidation_count
        }
