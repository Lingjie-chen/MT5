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
        logger.info(f"KalmanGridStrategy Initialized for {symbol} (v2026.01.12.1)")
        
        # --- Load Symbol Specific Config ---
        self._load_config()
        
        # SMC Parameters
        self.smc_levels = {
            'ob_bullish': [], # Order Blocks
            'ob_bearish': [],
            'fvg_bullish': [], # Fair Value Gaps
            'fvg_bearish': []
        }
        
        # Kalman Parameters
        self.kalman_measurement_variance = 10.0
        self.kalman_process_variance = 1.0
        self.prev_state = None
        self.prev_covariance = 1.0
        
        # BB Parameters
        self.bb_period = 100
        self.bb_deviation = 2.0
        
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

    def _load_config(self):
        """Load configuration based on symbol"""
        # Default Configs
        default_config = {
            "grid_step_points": 300,
            "max_grid_steps": 10,
            "lot_type": 'GEOMETRIC',
            "lot_multiplier": 1.5,
            "tp_steps": {
                1: 3.0, 2: 6.0, 3: 10.0, 4: 15.0, 5: 25.0,
                6: 35.0, 7: 45.0, 8: 55.0, 9: 65.0
            },
            "global_tp": 100.0
        }
        
        # ETHUSD Config
        eth_config = {
            "grid_step_points": 2000, # Approx 20.00 USD (Assuming point=0.01)
            "max_grid_steps": 5,      # Stricter for crypto
            "lot_type": 'GEOMETRIC',
            "lot_multiplier": 1.2,    # Conservative
            "tp_steps": {
                1: 10.0, 2: 20.0, 3: 40.0, 4: 70.0, 5: 100.0
            },
            "global_tp": 200.0
        }
        
        # XAUUSD Config (same as default but explicit)
        xau_config = default_config.copy()
        
        # Select Config
        config = default_config
        if "ETH" in self.symbol.upper():
            config = eth_config
        elif "XAU" in self.symbol.upper() or "GOLD" in self.symbol.upper():
            config = xau_config
            
        # Apply Config
        self.grid_step_points = config["grid_step_points"]
        self.max_grid_steps = config["max_grid_steps"]
        self.lot_type = config["lot_type"]
        self.lot_multiplier = config["lot_multiplier"]
        self.tp_steps = config["tp_steps"]
        self.global_tp = config["global_tp"]
        
        logger.info(f"[{self.symbol}] Grid Config Loaded: Step={self.grid_step_points}, Max={self.max_grid_steps}, Mult={self.lot_multiplier}")

    def update_smc_levels(self, smc_data):
        """
        Update SMC levels from DeepSeek/SMC Analyzer for intelligent grid placement
        """
        if not smc_data: return

        # Expected format: {'ob': [{'top': x, 'bottom': y, 'type': 'bullish'}], ...}
        
        if 'ob' in smc_data:
            self.smc_levels['ob_bullish'] = [
                (zone['top'] + zone['bottom'])/2 
                for zone in smc_data['ob'] if zone.get('type') == 'bullish'
            ]
            self.smc_levels['ob_bearish'] = [
                (zone['top'] + zone['bottom'])/2 
                for zone in smc_data['ob'] if zone.get('type') == 'bearish'
            ]
            
        if 'fvg' in smc_data:
            self.smc_levels['fvg_bullish'] = [
                (zone['top'] + zone['bottom'])/2 
                for zone in smc_data['fvg'] if zone.get('type') == 'bullish'
            ]
            self.smc_levels['fvg_bearish'] = [
                (zone['top'] + zone['bottom'])/2 
                for zone in smc_data['fvg'] if zone.get('type') == 'bearish'
            ]
        logger.info(f"Updated SMC Levels: {len(self.smc_levels['ob_bullish'])} Bullish OBs")

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
        rolling_mean = df['close'].rolling(window=self.bb_period).mean()
        rolling_std = df['close'].rolling(window=self.bb_period).std()
        
        self.bb_upper = rolling_mean.iloc[-1] + (rolling_std.iloc[-1] * self.bb_deviation)
        self.bb_lower = rolling_mean.iloc[-1] - (rolling_std.iloc[-1] * self.bb_deviation)
        self.ma_value = rolling_mean.iloc[-1]

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
        
        # Default Grid Distance
        grid_dist = self.grid_step_points * point
        
        # SMC-Aware Grid Spacing (Optional Dynamic Adjustment)
        # If price is near an OB, we might want to add sooner or later
        
        # Check Buy Grid
        if self.long_pos_count > 0 and self.long_pos_count < self.max_grid_steps:
            dist = self.last_long_price - current_price
            if dist >= grid_dist:
                # SMC Check: Is there a support level nearby?
                # If yes, align with it? For simplicity, we stick to distance but scale lot
                next_lot = self.calculate_next_lot(self.long_pos_count)
                return 'add_buy', next_lot
                
        # Check Sell Grid
        if self.short_pos_count > 0 and self.short_pos_count < self.max_grid_steps:
            dist = current_price - self.last_short_price
            if dist >= grid_dist:
                next_lot = self.calculate_next_lot(self.short_pos_count)
                return 'add_sell', next_lot
                
        return None, 0.0

    def calculate_next_lot(self, current_count):
        """
        Calculate next lot size based on strategy.
        Uses Martingale or Pyramid logic.
        """
        multiplier = 1.0
        if self.lot_type == 'GEOMETRIC':
            # Aggressive scaling for capital utilization
            multiplier = self.lot_multiplier ** current_count 
        elif self.lot_type == 'ARITHMETIC':
            multiplier = current_count + 1
            
        return float(f"{self.lot * multiplier:.2f}")

    def generate_grid_plan(self, current_price, trend_direction, atr, point=0.01, dynamic_step_pips=None, grid_level_tps=None):
        """
        Generate a plan for grid deployment (for limit orders)
        grid_level_tps: List of TP pips for each level [tp1, tp2, ...]
        """
        orders = []
        
        # Range
        upper_bound = current_price + (atr * 5)
        lower_bound = current_price - (atr * 5)
        
        # Find SMC Levels
        resistances = [p for p in self.smc_levels['ob_bearish'] if p > current_price]
        supports = [p for p in self.smc_levels['ob_bullish'] if p < current_price]
        
        # Calculate fixed step based on config or dynamic override
        if dynamic_step_pips and dynamic_step_pips > 0:
            fixed_step = dynamic_step_pips * 10 * point # Pip to Point (1 pip = 10 points)
            logger.info(f"Using Dynamic Grid Step: {dynamic_step_pips} pips ({fixed_step} points)")
        else:
            fixed_step = self.grid_step_points * point
        
        if trend_direction == 'bullish':
            # Buy Grid
            levels = sorted([p for p in supports if p > lower_bound], reverse=True)
            if not levels: # Fallback to arithmetic
                step = fixed_step if fixed_step > 0 else (atr * 0.5)
                levels = [current_price - step*i for i in range(1, 6)]
            
            for i, lvl in enumerate(levels):
                # Calculate TP for this level
                tp_price = 0.0
                if grid_level_tps and len(grid_level_tps) > 0:
                    # Use specific TP if available, else last available
                    tp_pips = grid_level_tps[i] if i < len(grid_level_tps) else grid_level_tps[-1]
                    tp_price = lvl + (tp_pips * 10 * point)
                else:
                    # Default: ATR * 2 or global config
                    tp_price = lvl + (atr * 2.0)
                    
                orders.append({'type': 'limit_buy', 'price': lvl, 'tp': tp_price})
                
        elif trend_direction == 'bearish':
            # Sell Grid
            levels = sorted([p for p in resistances if p < upper_bound])
            if not levels:
                step = fixed_step if fixed_step > 0 else (atr * 0.5)
                levels = [current_price + step*i for i in range(1, 6)]
                
            for i, lvl in enumerate(levels):
                # Calculate TP for this level
                tp_price = 0.0
                if grid_level_tps and len(grid_level_tps) > 0:
                    tp_pips = grid_level_tps[i] if i < len(grid_level_tps) else grid_level_tps[-1]
                    tp_price = lvl - (tp_pips * 10 * point)
                else:
                    tp_price = lvl - (atr * 2.0)
                    
                orders.append({'type': 'limit_sell', 'price': lvl, 'tp': tp_price})
                
        return orders

    # ... (Rest of existing methods: check_basket_tp, update_config, _update_positions_state) ...
    def check_basket_tp(self, positions):
        """
        Check if total profit exceeds threshold.
        Returns: True (should close all), False
        """
        total_profit = 0.0
        count = 0
        for pos in positions:
            if pos.magic == self.magic_number:
                commission = getattr(pos, 'commission', 0.0)
                swap = getattr(pos, 'swap', 0.0)
                total_profit += pos.profit + swap + commission
                count += 1
        
        if count == 0: return False
        
        # Dynamic TP based on step count
        target_tp = self.tp_steps.get(count, self.global_tp)
        if count > 9: target_tp = self.global_tp # Fallback
        
        if total_profit >= target_tp:
            logger.info(f"Grid Basket TP Reached: Profit {total_profit:.2f} >= Target {target_tp}")
            return True
            
        return False

    def update_config(self, params):
        if not params: return
        if 'grid_step_points' in params: self.grid_step_points = int(params['grid_step_points'])
        if 'max_grid_steps' in params: self.max_grid_steps = int(params['max_grid_steps'])
        if 'global_tp' in params: self.global_tp = float(params['global_tp'])

    def get_config(self):
        """
        Return current configuration state for optimization/reporting
        """
        return {
            'grid_step_points': self.grid_step_points,
            'max_grid_steps': self.max_grid_steps,
            'lot_type': self.lot_type,
            'global_tp': self.global_tp,
            'tp_steps': self.tp_steps,
            'kalman_measurement_variance': self.kalman_measurement_variance,
            'kalman_process_variance': self.kalman_process_variance
        }

    def _update_positions_state(self, positions):
        self.long_pos_count = 0
        self.short_pos_count = 0
        self.last_long_price = 0.0
        self.last_short_price = 0.0
        last_long_time = 0
        last_short_time = 0
        
        for pos in positions:
            if pos.magic != self.magic_number: continue
            if pos.type == mt5.POSITION_TYPE_BUY:
                self.long_pos_count += 1
                if pos.time_msc > last_long_time:
                    last_long_time = pos.time_msc
                    self.last_long_price = pos.price_open
            elif pos.type == mt5.POSITION_TYPE_SELL:
                self.short_pos_count += 1
                if pos.time_msc > last_short_time:
                    last_short_time = pos.time_msc
                    self.last_short_price = pos.price_open
