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

    def calculate_orb_levels(self, df_h1):
        """
        Calculate ORB levels based on H1 data.
        Should be called on every new candle close or tick.
        
        Logic:
        1. Find the first candle of the current day (defined by open_hour).
        2. Set initial range.
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
            # Maybe market hasn't opened yet or data is missing
            # logger.debug(f"ORB: No open candle found for {today} at hour {self.open_hour}")
            self.final_range_high = None
            self.final_range_low = None
            self.is_range_final = False
            self.current_consolidation_count = 0
            return None, None, False

        # Initial Range (High/Low of the open candle)
        initial_high = open_candle['high'].iloc[0]
        initial_low = open_candle['low'].iloc[0]
        
        # Get candles AFTER the open candle
        subsequent_candles = today_data[today_data.index > open_candle.index[0]]
        
        current_high = initial_high
        current_low = initial_low
        consolidation_count = 0
        is_final = False
        
        for time, row in subsequent_candles.iterrows():
            c_high = row['high']
            c_low = row['low']
            
            # Check if this candle is inside the current range
            if c_high <= current_high and c_low >= current_low:
                consolidation_count += 1
            else:
                # Range expansion
                if c_high > current_high:
                    current_high = c_high
                if c_low < current_low:
                    current_low = c_low
                
                # Reset count on expansion?
                # "Otherwise, the EA will just update... Once the minimum 'candle composition' is meet..."
                # Implies we need continuous consolidation or accumulated?
                # Usually ORB consolidation means "N consecutive candles inside".
                # If it breaks out (expands), we reset.
                consolidation_count = 0
            
            if consolidation_count >= self.consolidation_candles:
                is_final = True
                # Once final, we stop updating range?
                # "Once the minimum 'candle composition' is meet the range is now considered final."
                # "And if a breakout/breakdown happens on the 'final' range..."
                # So we stop updating.
                break
        
        self.final_range_high = current_high
        self.final_range_low = current_low
        self.is_range_final = is_final
        self.current_consolidation_count = consolidation_count
        
        return self.final_range_high, self.final_range_low, self.is_range_final

    def check_signal(self, current_price, df_h1=None):
        """
        Check for Breakout/Breakdown signal.
        If df_h1 is provided, update levels first.
        """
        if df_h1 is not None:
            self.calculate_orb_levels(df_h1)
        
        if not self.is_range_final or self.final_range_high is None or self.final_range_low is None:
            return None
            
        # Breakout Logic
        if current_price > self.final_range_high:
            return 'buy'
        elif current_price < self.final_range_low:
            return 'sell'
            
        return None

    def get_state(self):
        return {
            "final_high": self.final_range_high,
            "final_low": self.final_range_low,
            "is_final": self.is_range_final,
            "consolidation_count": self.current_consolidation_count
        }
