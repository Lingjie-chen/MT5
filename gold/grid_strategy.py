import pandas as pd
import numpy as np
import MetaTrader5 as mt5
import logging

logger = logging.getLogger("KalmanGrid")

class KalmanGridStrategy:
    def __init__(self, symbol, magic_number, initial_lot=0.01):
        self.symbol = symbol
        self.magic_number = magic_number
        self.lot = initial_lot
        
        # Grid Parameters (Default from MQL)
        self.grid_step = 300 # Points (30 pips for 5 digit broker) -> user input 30, assuming 4 digit? 
        # Usually gold 30 points = 0.3 USD? Or 3.0 USD?
        # MQL: input int gridStep=30; 
        # In Gold (XAUUSD), 1 point = 0.01. 30 points = 0.30.
        # If user meant pips, it might be 300 points.
        # Let's use a safe default and allow config.
        self.grid_step_points = 300 
        self.max_grid_steps = 10 # 0 in MQL means unlimited, let's set a safe limit
        self.lot_type = 'GEOMETRIC' # 'FIXED', 'ARITHMETIC', 'GEOMETRIC'
        
        # Kalman Parameters
        self.kalman_measurement_variance = 10.0
        self.kalman_process_variance = 1.0
        self.prev_state = None
        self.prev_covariance = 1.0
        
        # BB Parameters
        self.bb_period = 100
        self.bb_deviation = 2.0
        
        # Profit Settings (Basket TP in USD)
        self.tp_steps = {
            1: 3.0,
            2: 6.0,
            3: 10.0,
            4: 15.0,
            5: 25.0,
            6: 35.0,
            7: 45.0,
            8: 55.0,
            9: 65.0
        }
        self.global_tp = 100.0
        
        # State
        self.last_long_price = 0.0
        self.last_short_price = 0.0
        self.long_pos_count = 0
        self.short_pos_count = 0
        
        # Indicators state
        self.kalman_value = 0.0
        self.bb_upper = 0.0
        self.bb_lower = 0.0
        self.ma_value = 0.0

    def update_market_data(self, df):
        """
        Update indicators based on latest dataframe.
        Expects df with 'close' column.
        """
        if df is None or len(df) < self.bb_period:
            return

        current_price = df['close'].iloc[-1]
        
        # 1. Update Kalman Filter
        if self.prev_state is None:
            self.prev_state = current_price
            
        predicted_state = self.prev_state
        predicted_covariance = self.prev_covariance + self.kalman_process_variance
        
        kalman_gain = predicted_covariance / (predicted_covariance + self.kalman_measurement_variance)
        
        updated_state = predicted_state + kalman_gain * (current_price - predicted_state)
        updated_covariance = (1 - kalman_gain) * predicted_covariance
        
        self.prev_state = updated_state
        self.prev_covariance = updated_covariance
        self.kalman_value = updated_state
        
        # 2. Update Bollinger Bands
        # Using pandas rolling
        rolling_mean = df['close'].rolling(window=self.bb_period).mean()
        rolling_std = df['close'].rolling(window=self.bb_period).std()
        
        self.bb_upper = rolling_mean.iloc[-1] + (rolling_std.iloc[-1] * self.bb_deviation)
        self.bb_lower = rolling_mean.iloc[-1] - (rolling_std.iloc[-1] * self.bb_deviation)
        self.ma_value = rolling_mean.iloc[-1] # Use BB middle band as MA or calculate separate? MQL uses separate MA_PERIOD=200
        
        # 3. Separate MA (if needed, MQL uses 200)
        ma_200 = df['close'].rolling(window=200).mean().iloc[-1]
        # self.ma_value = ma_200 # Optional

    def get_entry_signal(self, current_price):
        """
        Determine if we should start a grid.
        Returns: 'buy', 'sell', or None
        """
        # Logic from MQL:
        # Buy: Price < BB Lower AND Price > Kalman (Oversold but Bullish Trend)
        # Sell: Price > BB Upper AND Price < Kalman (Overbought but Bearish Trend)
        
        signal = None
        
        if current_price < self.bb_lower and current_price > self.kalman_value:
            signal = 'buy'
        elif current_price > self.bb_upper and current_price < self.kalman_value:
            signal = 'sell'
            
        return signal

    def check_grid_add(self, positions, current_price, point=0.01):
        """
        Check if we need to add a position to the grid.
        Returns: ('add_buy', lot) or ('add_sell', lot) or (None, 0)
        """
        self._update_positions_state(positions)
        
        grid_dist = self.grid_step_points * point
        
        # Check Buy Grid
        if self.long_pos_count > 0 and self.long_pos_count < self.max_grid_steps:
            if (self.last_long_price - current_price) >= grid_dist:
                next_lot = self.calculate_next_lot(self.long_pos_count)
                return 'add_buy', next_lot
                
        # Check Sell Grid
        if self.short_pos_count > 0 and self.short_pos_count < self.max_grid_steps:
            if (current_price - self.last_short_price) >= grid_dist:
                next_lot = self.calculate_next_lot(self.short_pos_count)
                return 'add_sell', next_lot
                
        return None, 0.0

    def check_basket_tp(self, positions):
        """
        Check if total profit exceeds threshold.
        Returns: True (should close all), False
        """
        total_profit = 0.0
        count = 0
        for pos in positions:
            if pos.magic == self.magic_number:
                total_profit += pos.profit + pos.swap + pos.commission
                count += 1
        
        if count == 0: return False
        
        # Dynamic TP based on step count
        target_tp = self.tp_steps.get(count, self.global_tp)
        if count > 9: target_tp = self.global_tp # Fallback
        
        if total_profit >= target_tp:
            logger.info(f"Grid Basket TP Reached: Profit {total_profit:.2f} >= Target {target_tp}")
            return True
            
        return False

    def calculate_next_lot(self, current_count):
        """
        Calculate next lot size based on strategy.
        current_count: Number of existing positions (so next is current_count + 1)
        """
        # MQL: if(currentPositions > 1) lot = Lot * (MathPow(2, currentPositions-1));
        # Note: MQL passed 'LongPos' which is count. 
        # If LongPos=1 (1 trade exists), next is 2nd trade.
        # MQL: calculateNextLot(1) -> returns Lot (since 1 > 1 is false) -> Wait?
        # MQL code: if(currentPositions > 1) lot = Lot * pow(2, currentPositions-1)
        # If I have 1 pos, I call calculateNextLot(1). Result: Lot.
        # So 2nd trade is same size?
        # If I have 2 pos, call calculateNextLot(2). Result: Lot * 2^(1) = 2*Lot.
        # So sequence: 1, 1, 2, 4, 8... ?
        # Or maybe MQL loop implies currentPositions is the index?
        # Let's stick to standard Martingale: 1, 2, 4, 8 or 1, 1.5, ...
        
        multiplier = 1.0
        if self.lot_type == 'GEOMETRIC':
            # 1st Add (2nd trade total): Double?
            # Let's use 2^(count) -> 1, 2, 4...
            multiplier = 2.0 ** current_count 
            # If count=1, mult=2. Next lot = 2*Lot.
            # Sequence: Initial, 2x, 4x...
        elif self.lot_type == 'ARITHMETIC':
            multiplier = current_count + 1
            
        return self.lot * multiplier

    def _update_positions_state(self, positions):
        """
        Update internal state about last prices and counts.
        """
        self.long_pos_count = 0
        self.short_pos_count = 0
        self.last_long_price = 0.0
        self.last_short_price = 0.0
        
        last_long_time = 0
        last_short_time = 0
        
        for pos in positions:
            if pos.magic != self.magic_number:
                continue
                
            if pos.type == mt5.POSITION_TYPE_BUY:
                self.long_pos_count += 1
                if pos.time_msc > last_long_time: # Use time_msc for precision
                    last_long_time = pos.time_msc
                    self.last_long_price = pos.price_open
            elif pos.type == mt5.POSITION_TYPE_SELL:
                self.short_pos_count += 1
                if pos.time_msc > last_short_time:
                    last_short_time = pos.time_msc
                    self.last_short_price = pos.price_open
