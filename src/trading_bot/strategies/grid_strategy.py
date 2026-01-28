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
        
        # XAUUSD Config (High Frequency Scalping - Optimized)
        xau_config = {
            "grid_step_points": 150, # [Optimized] Tighter grid (150 pts = $1.5) for HFT
            "max_grid_steps": 20,    # [Optimized] More steps for wider coverage
            "lot_type": 'GEOMETRIC',
            "lot_multiplier": 1.3,   # [Optimized] Slowly increasing (1.3x)
            "tp_steps": {
                # [Optimized] Ultra-Fast Scalps: $3, $5, $8...
                1: 3.0, 2: 5.0, 3: 8.0, 4: 12.0, 5: 18.0,
                6: 25.0, 7: 35.0, 8: 45.0, 9: 55.0, 10: 70.0,
                11: 85.0, 12: 100.0, 13: 120.0, 14: 140.0, 15: 160.0
            },
            "global_tp": 8.0 # [Optimized] Target $8 quick profit (Aggressive HFT)
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
        
        # 3. Calculate Swing High/Low (for Fibonacci)
        # Lookback 50 bars
        if len(df) >= 50:
             self.swing_high = df['high'].iloc[-50:].max()
             self.swing_low = df['low'].iloc[-50:].min()
        else:
             self.swing_high = df['high'].max()
             self.swing_low = df['low'].min()

    def get_entry_signal(self, current_price, trend_direction=None):
        """
        Determine if we should start a grid.
        Returns: 'buy', 'sell', or None
        
        [Optimized] Hybrid Logic:
        1. Mean Reversion (Standard): Buy Low (BB Lower), Sell High (BB Upper).
        2. Trend Following (Aggressive): If trend is strong, enter on shallow pullbacks (Mid Band).
        """
        signal = None
        
        # Calculate Trend Strength (Simple Slope of Kalman Filter)
        # We need history of kalman values to calculate slope properly, 
        # but here we can compare current price vs MA vs Kalman
        
        # Proxy for Trend Strength: Distance between Kalman and MA
        # If Kalman > MA by a margin, it's an uptrend.
        trend_strength = 0.0
        if self.ma_value > 0:
            trend_strength = (self.kalman_value - self.ma_value) / self.ma_value * 10000 # Basis points
            
        is_strong_uptrend = trend_strength > 5.0 # Arbitrary threshold, tune based on asset
        is_strong_downtrend = trend_strength < -5.0
        
        # [Optimized Entry Logic]
        
        # 1. Buy Signal
        if trend_direction == 'bullish' or (trend_direction is None and is_strong_uptrend):
            # Aggressive Trend Entry: Price touches Mid Band (MA) or simply is below Kalman in strong trend
            if is_strong_uptrend and current_price < self.kalman_value:
                 # In strong uptrend, buy the dip to Kalman/Mid line, don't wait for BB Lower
                 logger.info(f"Aggressive Trend BUY Signal: Price {current_price} < Kalman {self.kalman_value} (Strong UpTrend)")
                 signal = 'buy'
            # Standard Mean Reversion Entry
            elif current_price < self.bb_lower and current_price > self.kalman_value:
                 signal = 'buy'
                 
        # 2. Sell Signal
        elif trend_direction == 'bearish' or (trend_direction is None and is_strong_downtrend):
            # Aggressive Trend Entry
            if is_strong_downtrend and current_price > self.kalman_value:
                 logger.info(f"Aggressive Trend SELL Signal: Price {current_price} > Kalman {self.kalman_value} (Strong DownTrend)")
                 signal = 'sell'
            # Standard Mean Reversion Entry
            elif current_price > self.bb_upper and current_price < self.kalman_value:
                 signal = 'sell'
            
        return signal

    def check_grid_add(self, positions, current_price, point=0.01, current_atr=None):
        """
        Check if we need to add a position to the grid.
        Returns: ('add_buy', lot) or ('add_sell', lot) or (None, 0)
        """
        # User Requirement: Disable autonomous grid adding. Rely on LLM/Grid Plan (Limit Orders).
        # "Grid Add BUY Signal... cancel this module, completely judge based on the big model"
        return None, 0.0

    def calculate_next_lot(self, current_count, ai_override_multiplier=None):
        """
        Calculate next lot size based on strategy.
        Uses Martingale, Pyramid, or Fibonacci logic.
        """
        multiplier = 1.0
        
        # [User Requirement] Fibonacci Lot Sequence
        # If lot_type is set to 'FIBONACCI', use Fibo sequence.
        # But allow AI override multiplier if provided.
        
        # Priority 1: AI Override Multiplier
        if ai_override_multiplier and ai_override_multiplier > 0:
             # Treat as Geometric with custom multiplier
             multiplier = ai_override_multiplier ** current_count
             return float(f"{self.lot * multiplier:.2f}")

        # Priority 2: Fibonacci Sequence
        # "Grid strategy requires matching Fibonacci sequence for callback adding positions"
        # We can implement a Fibo Lot Logic here.
        # Sequence: 1, 1, 2, 3, 5, 8, 13...
        # Index:    0, 1, 2, 3, 4, 5, 6...
        # current_count is 0-based index of NEW order (e.g., 1st add is count=1, 2nd add is count=2)
        # Wait, base_count in generate_grid_plan starts from 1.
        # Let's assume current_count 0 = Base Lot. 
        # current_count 1 = 1st Add = Base Lot.
        # current_count 2 = 2nd Add = 2 * Base.
        
        # Let's define Fibo function
        def fib(n):
            if n <= 1: return 1
            a, b = 1, 1
            for _ in range(2, n + 1):
                a, b = b, a + b
            return b
            
        # We use Fibonacci logic if specified or by default if requested
        # For now, let's stick to existing logic unless config changes, 
        # BUT user said "Combine with Fibonacci sequence".
        # Let's add a check for 'FIBONACCI' type or default behavior
        
        if getattr(self, 'lot_type', '') == 'FIBONACCI':
            fib_mult = fib(current_count + 1) # +1 to align 1st add (index 0?) No.
            # If current_count = 1 (1st grid level), fib(1) = 1.
            # If current_count = 2 (2nd grid level), fib(2) = 1.
            # If current_count = 3 (3rd grid level), fib(3) = 2.
            # If current_count = 4, fib(4) = 3.
            # If current_count = 5, fib(5) = 5.
            # This matches standard Fibo Martingale.
            return float(f"{self.lot * fib_mult:.2f}")

        if self.lot_type == 'GEOMETRIC':
            # Aggressive scaling for capital utilization
            
            # [Advanced Martingale] 
            # If lot_multiplier is customized (e.g. by AI or config > 1.0 but not matching hardcoded logic assumptions),
            # we respect the configured multiplier strictly.
            
            # Simple Heuristic: If lot_multiplier is significantly different from 1.0, use Standard Geometric
            
            if self.lot_multiplier > 1.0:
                 # Standard Geometric: Base * (Mult ^ Count)
                 multiplier = self.lot_multiplier ** current_count
            else:
                # Soft/Tiered Multiplier (Fallback) - Slowly Increasing Logic
                # Level 1-2: 1.0x
                # Level 3-5: 1.3x
                # Level 6+: 1.5x
                
                accum_mult = 1.0
                for i in range(1, current_count + 1):
                    if i <= 2: m = 1.0
                    elif i <= 5: m = 1.3
                    else: m = 1.5
                    accum_mult *= m
                multiplier = accum_mult
            
            # Override for safety if result is too huge
            if multiplier > 20.0: multiplier = 20.0
            
            # Use rounding to ensure 0.01 * 1.3 becomes 0.01 or 0.02 appropriately
            # Standard float logic: 0.013 -> 0.01. 0.0169 -> 0.02.
            # If user wants "slowly increase", we rely on the multiplier being large enough eventually.
            
            return float(f"{self.lot * multiplier:.2f}")

        elif self.lot_type == 'ARITHMETIC':
            multiplier = current_count + 1
            return float(f"{self.lot * multiplier:.2f}")
            
        return float(f"{self.lot * multiplier:.2f}")

    def generate_grid_plan(self, current_price, trend_direction, atr, point=0.01, dynamic_step_pips=None, grid_level_tps=None):
        """
        Generate a plan for grid deployment (for limit orders)
        Uses Fibonacci Retracement Levels for placement if applicable.
        """
        orders = []
        
        # Range
        upper_bound = current_price + (atr * 5)
        lower_bound = current_price - (atr * 5)
        
        # [User Requirement] Fibonacci Retracement Levels
        # Use Swing High/Low calculated in update_market_data
        fibo_levels = []
        use_fibo = True
        
        # Validate Swing
        swing_dist = 0
        if hasattr(self, 'swing_high') and hasattr(self, 'swing_low'):
             swing_dist = self.swing_high - self.swing_low
        
        # Minimum swing requirement (e.g. > 100 pips)
        if swing_dist < (1000 * point): 
            use_fibo = False
            
        if use_fibo:
            # Calculate Retracement Levels based on Trend Direction
            # If Bullish, we look to buy at retracements from Low to High? 
            # Or if trend is Bullish, we assume we are in an uptrend, so we buy dips.
            # Dips are measured from Swing Low to Swing High range.
            # Retracements: 0.236, 0.382, 0.5, 0.618, 0.786 from High down.
            
            # Standard Fibo Ratios
            ratios = [0.236, 0.382, 0.5, 0.618, 0.786]
            
            if trend_direction == 'bullish':
                # Buy Limit Orders below current price
                # Levels = High - Range * Ratio
                # Only keep levels < current_price
                for r in ratios:
                    lvl = self.swing_high - (swing_dist * r)
                    if lvl < current_price:
                        fibo_levels.append(lvl)
                fibo_levels.sort(reverse=True) # Descending (closest to price first)
                
            elif trend_direction == 'bearish':
                # Sell Limit Orders above current price
                # Levels = Low + Range * Ratio
                # Only keep levels > current_price
                for r in ratios:
                    lvl = self.swing_low + (swing_dist * r)
                    if lvl > current_price:
                        fibo_levels.append(lvl)
                fibo_levels.sort() # Ascending (closest to price first)
        
        # Find SMC Levels
        resistances = [p for p in self.smc_levels['ob_bearish'] if p > current_price]
        supports = [p for p in self.smc_levels['ob_bullish'] if p < current_price]
        
        # Calculate fixed step based on config or dynamic override
        if dynamic_step_pips and dynamic_step_pips > 0:
            fixed_step = dynamic_step_pips * 10 * point # Pip to Point (1 pip = 10 points)
            logger.info(f"Using Dynamic Grid Step: {dynamic_step_pips} pips ({fixed_step} points)")
        else:
            fixed_step = self.grid_step_points * point
            
        # Ensure minimum safe step (e.g. 50 points or 0.2 ATR)
        min_safe_step = 50 * point
        if atr > 0:
             min_safe_step = max(min_safe_step, atr * 0.15)
        
        if fixed_step < min_safe_step:
            logger.warning(f"Grid Step {fixed_step} too small, adjusting to safe minimum {min_safe_step}")
            fixed_step = min_safe_step
        
        # Determine active existing levels to prevent overlap
        # We need pending orders (limits) and open positions to check against
        # But here we generate a plan. The caller (start.py) should ideally check against pending.
        # However, we can at least ensure our generated levels don't overlap with themselves (handled by loop)
        # and don't overlap with current price too much (handled by range).
        
        if trend_direction == 'bullish':
            # Buy Grid
            # [Logic] Prioritize Fibo Levels, then SMC, then Fixed
            levels = []
            if use_fibo and fibo_levels:
                levels = fibo_levels
                logger.info(f"Using Fibonacci Levels for Grid: {levels}")
            elif supports:
                levels = sorted([p for p in supports if p > lower_bound], reverse=True)
            
            if not levels: # Fallback to arithmetic
                step = fixed_step if fixed_step > 0 else (atr * 0.5)
                # Ensure step is valid
                if step < min_safe_step: step = min_safe_step
                levels = [current_price - step*i for i in range(1, 6)]
            
            # Base count for lot calculation (Assume at least 1 exists if starting grid)
            base_count = self.long_pos_count if self.long_pos_count > 0 else 1
            
            # Filter levels that are too close to each other or current price
            valid_levels = []
            last_lvl = current_price
            
            for lvl in levels:
                if abs(last_lvl - lvl) >= min_safe_step:
                    valid_levels.append(lvl)
                    last_lvl = lvl
            
            # Cap at max grid steps (considering existing)
            remaining_slots = max(0, self.max_grid_steps - self.long_pos_count)
            valid_levels = valid_levels[:remaining_slots]

            for i, lvl in enumerate(valid_levels):
                # Calculate TP for this level
                # [Requirement] Remove all TP/SL settings, fully rely on LLM for exits
                tp_price = 0.0
                
                # Calculate Lot
                # Use Fibonacci logic if specified or default
                lot = self.calculate_next_lot(base_count + i)
                
                orders.append({'type': 'limit_buy', 'price': lvl, 'tp': tp_price, 'volume': lot})
                
        elif trend_direction == 'bearish':
            # Sell Grid
            levels = []
            if use_fibo and fibo_levels:
                levels = fibo_levels
                logger.info(f"Using Fibonacci Levels for Grid: {levels}")
            elif resistances:
                levels = sorted([p for p in resistances if p < upper_bound])
            
            if not levels:
                step = fixed_step if fixed_step > 0 else (atr * 0.5)
                # Ensure step is valid
                if step < min_safe_step: step = min_safe_step
                levels = [current_price + step*i for i in range(1, 6)]
                
            # Base count for lot calculation
            base_count = self.short_pos_count if self.short_pos_count > 0 else 1

            # Filter levels
            valid_levels = []
            last_lvl = current_price
            
            for lvl in levels:
                if abs(lvl - last_lvl) >= min_safe_step:
                    valid_levels.append(lvl)
                    last_lvl = lvl
            
            # Cap at max grid steps
            remaining_slots = max(0, self.max_grid_steps - self.short_pos_count)
            valid_levels = valid_levels[:remaining_slots]

            for i, lvl in enumerate(valid_levels):
                # Calculate TP for this level
                # [Requirement] Remove all TP/SL settings, fully rely on LLM for exits
                tp_price = 0.0
                
                # Calculate Lot
                lot = self.calculate_next_lot(base_count + i)
                
                orders.append({'type': 'limit_sell', 'price': lvl, 'tp': tp_price, 'volume': lot})
                
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
        # else:
        #      effective_trigger = 10.0 # Disabled default 10.0 trigger per user request
        
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
