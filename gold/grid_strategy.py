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
        
        self.dynamic_global_tp = None # Store AI recommended TP
        self.lock_profit_trigger = None # Store AI recommended Lock Trigger
        self.trailing_stop_config = None # Store AI recommended Trailing Config
        self.basket_lock_level = None # Fixed lock level once triggered
        self.max_basket_profit = 0.0 # Track max profit for current basket
        
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
        # Default Configs - High Frequency Scalping Mode
        # [User Request]: "Grid Basket TP can be small (5-10 USD), High Lot Size, High Frequency"
        default_config = {
            "grid_step_points": 300, # 300 points = $3 (Gold)
            "max_grid_steps": 10,
            "lot_type": 'GEOMETRIC',
            "lot_multiplier": 1.5,
            # TP Steps - Reduced for Scalping
            "tp_steps": {
                1: 5.0, 2: 8.0, 3: 12.0, 4: 18.0, 5: 25.0,
                6: 35.0, 7: 45.0, 8: 55.0, 9: 65.0
            },
            # Global Basket TP - Reduced for Scalping
            "global_tp": 10.0 # Default fallback, LLM can override
        }
        
        # ETHUSD Config
        eth_config = {
            "grid_step_points": 2000, 
            "max_grid_steps": 5,
            "lot_type": 'GEOMETRIC',
            "lot_multiplier": 1.2,
            "tp_steps": {
                1: 10.0, 2: 25.0, 3: 45.0, 4: 75.0, 5: 120.0
            },
            "global_tp": 20.0
        }
        
        # XAUUSD Config (High Frequency Scalping)
        xau_config = {
            "grid_step_points": 200, # Tighter grid for HFT (200 pts = $2)
            "max_grid_steps": 15,    # More steps allowed
            "lot_type": 'GEOMETRIC',
            "lot_multiplier": 1.5,   # Aggressive scaling
            "tp_steps": {
                # Quick Scalps: $5, $8, $12...
                1: 5.0, 2: 8.0, 3: 12.0, 4: 18.0, 5: 25.0,
                6: 35.0, 7: 45.0, 8: 55.0, 9: 65.0, 10: 80.0
            },
            "global_tp": 10.0 # Target $10 quick profit
        }
        
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
            # For BUY, we add when price drops below last open
            dist = self.last_long_price - current_price
            
            # Use points logic
            # grid_step_points is already integer points (e.g., 2000 for ETH)
            # point is e.g. 0.01 for ETH
            min_dist_price = self.grid_step_points * point
            
            # Ensure strictly greater than minimum distance
            if dist >= min_dist_price:
                # Double check not adding too close to existing (in case of volatility spikes)
                # But here self.last_long_price is the *latest* opened position.
                
                next_lot = self.calculate_next_lot(self.long_pos_count)
                logger.info(f"Grid Add BUY Signal: Dist {dist:.2f} >= Min {min_dist_price:.2f} (Step {self.grid_step_points})")
                return 'add_buy', next_lot
                
        # Check Sell Grid
        if self.short_pos_count > 0 and self.short_pos_count < self.max_grid_steps:
            # For SELL, we add when price rises above last open
            dist = current_price - self.last_short_price
            
            min_dist_price = self.grid_step_points * point
            
            if dist >= min_dist_price:
                next_lot = self.calculate_next_lot(self.short_pos_count)
                logger.info(f"Grid Add SELL Signal: Dist {dist:.2f} >= Min {min_dist_price:.2f} (Step {self.grid_step_points})")
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
                # [Requirement] Remove all TP/SL settings, fully rely on LLM for exits
                tp_price = 0.0
                
                orders.append({'type': 'limit_buy', 'price': lvl, 'tp': tp_price})
                
        elif trend_direction == 'bearish':
            # Sell Grid
            levels = sorted([p for p in resistances if p < upper_bound])
            if not levels:
                step = fixed_step if fixed_step > 0 else (atr * 0.5)
                levels = [current_price + step*i for i in range(1, 6)]
                
            for i, lvl in enumerate(levels):
                # Calculate TP for this level
                # [Requirement] Remove all TP/SL settings, fully rely on LLM for exits
                tp_price = 0.0
                
                orders.append({'type': 'limit_sell', 'price': lvl, 'tp': tp_price})
                
        return orders

    # ... (Rest of existing methods: check_basket_tp, update_config, _update_positions_state) ...
    def check_basket_tp(self, positions, current_atr=None):
        """
        Check if total profit exceeds threshold or hits lock profit logic.
        current_atr: Passed from main loop for dynamic calculations
        Returns: True (should close all), False
        """
        total_profit = 0.0
        count = 0
        total_volume = 0.0
        
        for pos in positions:
            if pos.magic == self.magic_number:
                commission = getattr(pos, 'commission', 0.0)
                swap = getattr(pos, 'swap', 0.0)
                total_profit += pos.profit + swap + commission
                count += 1
                total_volume += pos.volume
        
        if count == 0: 
            self.max_basket_profit = 0.0 # Reset
            self.basket_lock_level = None # Reset Fixed Lock
            return False
            
        # Update Max Profit
        if total_profit > self.max_basket_profit:
            self.max_basket_profit = total_profit
            
        # --- 1. Regular Basket TP ---
        target_tp = self.global_tp # Default fallback
        
        if self.dynamic_global_tp is not None and self.dynamic_global_tp > 0:
            target_tp = self.dynamic_global_tp
        else:
            target_tp = self.tp_steps.get(count, self.global_tp)
            if count > 9: target_tp = self.global_tp

        if total_profit >= target_tp:
            logger.info(f"Grid Basket TP Reached: Profit {total_profit:.2f} >= Target {target_tp} (AI Dynamic: {self.dynamic_global_tp})")
            return True
            
        # --- 2. Profit Locking Logic (Trailing Stop for Basket) ---
        # Requirement: "Fully dynamic based on AI recommendation"
        
        effective_trigger = 9999.0 # Default inactive
        
        if self.lock_profit_trigger is not None and self.lock_profit_trigger > 0:
             effective_trigger = self.lock_profit_trigger
        else:
             effective_trigger = 10.0
        
        if self.max_basket_profit >= effective_trigger:
            # We are in locking mode
            
            # --- Requirement: "对于止损不要移动止损了，固定止损" ---
            # But Updated Requirement: "希望它像台阶一样（每上一个台阶固定一次），那是 Step Stop"
            
            # Logic:
            # 1. Calculate the 'Ideal' Lock Level based on current Max Profit (Dynamic)
            # 2. If 'Ideal' > 'Current Fixed Lock', Update 'Current Fixed Lock' (Step Up)
            # 3. Never Step Down
            
            # --- Dynamic Calculation (Ideal Lock) ---
            # Default fallback logic if no config
            lock_ratio = 0.7 # Default 70%
            dynamic_sl_profit_dist = 0.0
            step_size_usd = 5.0 # Minimum step size to update lock (USD)
            
            if self.trailing_stop_config:
                t_type = self.trailing_stop_config.get('type', 'atr_distance')
                t_value = float(self.trailing_stop_config.get('value', 2.0))
                
                if t_type == 'atr_distance' and current_atr is not None and current_atr > 0:
                     # Calculate contract size properly
                     contract_size = 100.0 # Default for XAUUSD/Standard Lots
                     if "ETH" in self.symbol.upper(): contract_size = 1.0
                     if "EUR" in self.symbol.upper(): contract_size = 100000.0
                     
                     # Distance in USD = ATR * Value * TotalVolume * ContractSize
                     dynamic_sl_profit_dist = current_atr * t_value * total_volume * contract_size
                     
                elif t_type == 'fixed_pips':
                     # Value is in pips
                     pip_val_usd = 0.01 * 10 # 0.1 USD per pip for 0.01 lot roughly? No.
                     # Pip value calculation is tricky without API, use approximate
                     # XAUUSD: 1 pip = 0.1 USD per 0.01 lot. 
                     # Wait, 1 pip (0.1) for 1 lot (100oz) is $10.
                     # So for volume V, 1 pip = V * 10 (USD).
                     
                     pip_value_per_lot = 10.0 # Standard for XAUUSD/EURUSD
                     if "ETH" in self.symbol.upper(): pip_value_per_lot = 1.0 # Approx
                     
                     price_dist_pips = t_value
                     dynamic_sl_profit_dist = price_dist_pips * pip_value_per_lot * total_volume

            # Calculate Current Ideal Lock Level
            ideal_lock = 0.0
            
            if dynamic_sl_profit_dist > 0:
                # Logic: Locked = CurrentProfit - Distance
                ideal_lock = self.max_basket_profit - dynamic_sl_profit_dist
            else:
                # Fallback Ratio Logic
                surplus = max(0.0, self.max_basket_profit - effective_trigger)
                ideal_lock = effective_trigger + (surplus * lock_ratio)
            
            # --- Constraints ---
            # Must be at least break-even (plus small buffer)
            min_break_even = 2.0 
            ideal_lock = max(ideal_lock, min_break_even)
            
            # If we just triggered, initial lock shouldn't be too tight unless distance says so
            # But the 'effective_trigger' acts as a floor for the lock in some logic?
            # Actually, if we trigger at $50, and distance is $20, lock at $30.
            # If trigger at $50, and distance is $60, lock at $2 (break even).
            
            # --- Step Logic Implementation ---
            if self.basket_lock_level is None:
                self.basket_lock_level = ideal_lock
                logger.info(f"Grid Profit Lock ACTIVATED: Step Lock Level set at {self.basket_lock_level:.2f} (Trigger: {effective_trigger}, MaxProfit: {self.max_basket_profit:.2f})")
            else:
                # Only Step Up if the difference is significant (Step Size)
                if ideal_lock >= (self.basket_lock_level + step_size_usd):
                    old_lock = self.basket_lock_level
                    self.basket_lock_level = ideal_lock
                    logger.info(f"Grid Profit Lock STEP UP: {old_lock:.2f} -> {self.basket_lock_level:.2f} (Peak: {self.max_basket_profit:.2f}, StepSize: {step_size_usd})")

            # Check against the STEPPED lock level
            if total_profit <= self.basket_lock_level:
                logger.info(f"Grid Profit Lock Triggered: Profit {total_profit:.2f} <= Step Lock {self.basket_lock_level:.2f}")
                return True
                
        return False

    def update_dynamic_params(self, basket_tp=None, lock_trigger=None, trailing_config=None):
        """Update dynamic parameters from AI analysis"""
        if basket_tp is not None and basket_tp > 0:
            self.dynamic_global_tp = float(basket_tp)
            logger.info(f"Updated Dynamic Basket TP: {self.dynamic_global_tp}")
            
        if lock_trigger is not None and lock_trigger > 0:
            self.lock_profit_trigger = float(lock_trigger)
            logger.info(f"Updated Dynamic Lock Trigger: {self.lock_profit_trigger}")
            
        if trailing_config is not None and isinstance(trailing_config, dict):
            self.trailing_stop_config = trailing_config
            logger.info(f"Updated Dynamic Trailing Config: {self.trailing_stop_config}")

    def update_config(self, params):
        if not params: return
        if 'grid_step_points' in params: self.grid_step_points = int(params['grid_step_points'])
        if 'max_grid_steps' in params: self.max_grid_steps = int(params['max_grid_steps'])
        if 'global_tp' in params: self.global_tp = float(params['global_tp'])
        if 'tp_steps' in params: self.tp_steps.update(params['tp_steps'])

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
