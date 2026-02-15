import pandas as pd
import numpy as np
import MetaTrader5 as mt5
import logging
import json
import os
from .orb_strategy import GoldORBStrategy
try:
    from analysis.advanced_analysis import AdvancedMarketAnalysis
except ImportError:
    from src.trading_bot.analysis.advanced_analysis import AdvancedMarketAnalysis

logger = logging.getLogger("KalmanGrid")

class KalmanGridStrategy:
    def __init__(self, symbol, magic_number, initial_lot=0.01):
        self.symbol = symbol
        self.magic_number = magic_number
        self.lot = initial_lot
        logger.info(f"KalmanGridStrategy Initialized for {symbol} (v2026.02.13.1)")
        
        self.analysis = AdvancedMarketAnalysis()
        
        # --- Load Symbol Specific Config ---
        self._load_config()
        
        # ORB Strategy Instance (Managed by Main Controller mostly, but kept here for reference)
        self.orb_strategy = GoldORBStrategy(symbol)
        
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
        
        # Risk Management
        self.use_risk_based_sizing = True
        self.max_risk_per_trade_percent = 1.0
        self.account_balance = 0.0 
        
        # Indicators state
        self.kalman_value = 0.0
        self.bb_upper = 0.0
        self.bb_lower = 0.0
        self.ma_value = 0.0
        self.atr_value = 0.0
        
        # Market State
        self.is_ranging = False
        self.swing_high = 0.0
        self.swing_low = 0.0
        
        # Dynamic Params (from LLM)
        self.dynamic_tp_long = None
        self.dynamic_tp_short = None
        self.lock_profit_trigger = None
        self.trailing_stop_config = None
        
        # Basket State
        self.basket_lock_level_long = None 
        self.max_basket_profit_long = 0.0 
        self.basket_lock_level_short = None
        self.max_basket_profit_short = 0.0
        
        self.long_pos_count = 0
        self.short_pos_count = 0

    def _load_config(self):
        """Load configuration based on symbol"""
        # Default Configs - High Frequency Scalping Mode
        default_config = {
            "grid_step_points": 300, 
            "max_grid_steps": 10,
            "lot_type": 'FIBONACCI', # Default to Fibonacci as requested
            "lot_multiplier": 1.5,
            "tp_steps": { "1": 5.0, "2": 8.0, "3": 12.0 }, # Keys as strings for JSON compat
            "global_tp": 10.0 
        }
        
        # XAUUSD Config
        xau_config = {
            "grid_step_points": 250, 
            "max_grid_steps": 20,    
            "lot_type": 'FIBONACCI',
            "lot_multiplier": 1.3,   
            "tp_steps": { "1": 5.0, "2": 8.0, "3": 12.0 },
            "global_tp": 15.0 
        }
        
        config = default_config
        if "XAU" in self.symbol.upper() or "GOLD" in self.symbol.upper():
            config = xau_config
            
        # [NEW] Check for external optimized config
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # src/trading_bot/strategies/ -> src/trading_bot/config/grid_config.json
            config_path = os.path.join(current_dir, '..', 'config', 'grid_config.json')
            
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    optimized_config = json.load(f)
                    logger.info(f"Loading optimized grid config from {config_path}")
                    
                    # Update allowed keys
                    if "grid_step_points" in optimized_config:
                        config["grid_step_points"] = optimized_config["grid_step_points"]
                    if "lot_multiplier" in optimized_config:
                        config["lot_multiplier"] = optimized_config["lot_multiplier"]
                    if "global_tp" in optimized_config:
                        config["global_tp"] = optimized_config["global_tp"]
        except Exception as e:
            logger.error(f"Failed to load optimized config: {e}")
            
        self.grid_step_points = config["grid_step_points"]
        self.max_grid_steps = config["max_grid_steps"]
        self.lot_type = config["lot_type"]
        self.lot_multiplier = config["lot_multiplier"]
        self.tp_steps = config["tp_steps"]
        self.global_tp = config["global_tp"]

    def get_active_config(self):
        """Returns the current active configuration"""
        return {
            "grid_step_points": self.grid_step_points,
            "max_grid_steps": self.max_grid_steps,
            "lot_type": self.lot_type,
            "lot_multiplier": self.lot_multiplier,
            "tp_steps": self.tp_steps,
            "global_tp": self.global_tp
        }

    def reload_config(self):
        """Reload configuration from disk (used after optimization)"""
        logger.info("Reloading Grid Configuration...")
        self._load_config()
        return self.get_active_config()

    def update_market_data(self, df, df_h1=None):
        """
        Update indicators based on latest dataframe.
        """
        if df is None or len(df) < 100:
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
        
        # 2. Update Bollinger Bands & MA
        rolling_mean = df['close'].rolling(window=100).mean()
        rolling_std = df['close'].rolling(window=100).std()
        
        self.bb_upper = rolling_mean.iloc[-1] + (rolling_std.iloc[-1] * 2.0)
        self.bb_lower = rolling_mean.iloc[-1] - (rolling_std.iloc[-1] * 2.0)
        self.ma_value = rolling_mean.iloc[-1]
        
        # 3. Calculate ATR
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        self.atr_value = true_range.rolling(14).mean().iloc[-1]
        
        # 4. Detect Ranging State (Volatility Contraction & Market Profile)
        # Enhanced detection logic for LLM input preparation
        
        # A. BB Bandwidth Squeeze (Legacy/Monitoring)
        bb_width = (self.bb_upper - self.bb_lower) / self.ma_value
        is_bb_squeeze = bb_width < 0.002
        
        # B. Price Action Range
        self.swing_high = df['high'].iloc[-50:].max()
        self.swing_low = df['low'].iloc[-50:].min()
        
        range_mid_high = self.swing_low + 0.75 * (self.swing_high - self.swing_low)
        range_mid_low = self.swing_low + 0.25 * (self.swing_high - self.swing_low)
        is_price_in_range = range_mid_low <= current_price <= range_mid_high
        
        # C. Volume Profile (Simple)
        # Check if recent volume is below average (consolidation often has lower volume)
        avg_volume = df['tick_volume'].rolling(20).mean().iloc[-1]
        current_vol = df['tick_volume'].iloc[-1]
        is_low_volume = current_vol < avg_volume
        
        # D. [NEW] ADX & Choppiness Index (Volatility Paradox Resolution)
        # Replaces BB Squeeze as primary trigger
        regime = self.analysis.detect_market_regime(df)
        adx_value = regime.get('adx', 0)
        chop_value = self.analysis.calculate_choppiness_index(df)
        
        # Criteria: ADX < 25 (No Trend) AND CHOP > 61.8 (Consolidation)
        is_true_ranging = adx_value < 25 and chop_value > 61.8
        
        # Combine Signals
        # We consider it ranging if ADX/CHOP confirms true ranging
        # The LLM will do the final confirmation
        self.is_ranging = is_true_ranging
        
        # Store detailed state for LLM
        # Convert bools to native Python types (True/False) which are generally serializable,
        # but numpy bools are NOT. Ensure explicit conversion.
        self.market_state_details = {
            "bb_width": float(bb_width),
            "is_bb_squeeze": bool(is_bb_squeeze),
            "swing_high": float(self.swing_high),
            "swing_low": float(self.swing_low),
            "is_price_in_range": bool(is_price_in_range),
            "atr": float(self.atr_value),
            "is_low_volume": bool(is_low_volume),
            "trend_ma": "bullish" if current_price > self.ma_value else "bearish",
            "adx": float(adx_value),
            "chop_index": float(chop_value),
            "is_true_ranging": bool(is_true_ranging)
        }

    def generate_fibonacci_grid(self, current_price, trend_direction, point=0.01):
        """
        Generate Fibonacci Grid Levels based on recent Swing High/Low.
        Ratios: 0.236, 0.382, 0.5, 0.618, 0.786
        
        [NEW LOGIC] Single Direction Enforcement & Order Cleanup:
        1. Only generate orders in the requested 'trend_direction'.
        2. Before placing new orders, existing pending orders of the SAME direction must be cancelled (handled by caller or here).
           * Actually, `main.py` handles execution. This function just returns the PLAN.
           * We will add a 'clear_existing' flag to the order dict to signal the executor.
        """
        orders = []
        
        # Ensure we have valid swings
        if self.swing_high <= self.swing_low:
             # Fallback to local 50 bars
             return self.generate_simple_grid(current_price, trend_direction, point)
             
        swing_range = self.swing_high - self.swing_low
        ratios = [0.236, 0.382, 0.5, 0.618, 0.786]
        
        # Calculate levels
        levels_buy = []
        levels_sell = []
        
        # Retracements from Low to High
        for r in ratios:
            price_level_from_top = self.swing_high - (swing_range * r)
            
            # Filter Validity
            if price_level_from_top < current_price:
                levels_buy.append(price_level_from_top)
            elif price_level_from_top > current_price:
                levels_sell.append(price_level_from_top)
        
        # Sort levels
        levels_buy.sort(reverse=True) # Closest to price first
        levels_sell.sort() # Closest to price first
        
        # Generate Orders - SINGLE DIRECTION ONLY
        
        # Buy Limits (Only if Bullish/Neutral)
        if trend_direction == 'bullish' or trend_direction == 'neutral':
            # Signal to clear existing Buy Limits first
            if len(levels_buy) > 0:
                orders.append({'type': 'cancel_all_buy_limits'}) 
                
            for i, price in enumerate(levels_buy):
                lot = self.calculate_next_lot(i + 1)
                orders.append({
                    'type': 'limit_buy',
                    'price': price,
                    'tp': 0.0, # Managed by Basket
                    'volume': lot,
                    'comment': f'Fib Grid {ratios[i]}'
                })
            
        # Sell Limits (Only if Bearish/Neutral)
        # Note: If Neutral, we might theoretically want both, but user requested "Single Direction" enforcement.
        # Ideally, 'neutral' should split or pick one. For safety, let's strictly follow the 'trend_direction' passed.
        # If 'neutral' is passed, we might skip or do both. Given "Only same direction", we assume trend_direction is explicit.
        
        if trend_direction == 'bearish':
            # Signal to clear existing Sell Limits first
            if len(levels_sell) > 0:
                orders.append({'type': 'cancel_all_sell_limits'})

            for i, price in enumerate(levels_sell):
                lot = self.calculate_next_lot(i + 1)
                orders.append({
                    'type': 'limit_sell',
                    'price': price,
                    'tp': 0.0,
                    'volume': lot,
                    'comment': f'Fib Grid {ratios[i]}' 
                })
                
        return orders

    def generate_simple_grid(self, current_price, trend_direction, point=0.01):
        # Fallback simple grid - Single Direction Enforced
        step = self.grid_step_points * point
        orders = []
        
        if trend_direction == 'bullish':
            orders.append({'type': 'cancel_all_buy_limits'})
            for i in range(1, 6):
                price = current_price - (step * i)
                orders.append({'type': 'limit_buy', 'price': price, 'volume': self.calculate_next_lot(i), 'tp': 0.0})
        elif trend_direction == 'bearish':
            orders.append({'type': 'cancel_all_sell_limits'})
            for i in range(1, 6):
                price = current_price + (step * i)
                orders.append({'type': 'limit_sell', 'price': price, 'volume': self.calculate_next_lot(i), 'tp': 0.0})
                
        return orders

    def calculate_next_lot(self, current_count):
        """
        Calculate next lot size.
        Defaults to Fibonacci Sequence if lot_type is FIBONACCI.
        """
        # Fibonacci: 1, 1, 2, 3, 5, 8...
        if self.lot_type == 'FIBONACCI':
            def fib(n):
                if n <= 1: return 1
                a, b = 1, 1
                for _ in range(2, n + 1):
                    a, b = b, a + b
                return b
            
            fib_mult = fib(current_count)
            return float(f"{self.lot * fib_mult:.2f}")
            
        elif self.lot_type == 'GEOMETRIC':
            multiplier = self.lot_multiplier ** current_count
            return float(f"{self.lot * multiplier:.2f}")
            
        return self.lot

    def calculate_initial_lot(self, sl_points, account_balance, point_value=1.0, tick_size=0.01, tick_value=1.0):
        if not self.use_risk_based_sizing or sl_points <= 0 or account_balance <= 0:
            return self.lot
        risk_amount = account_balance * (self.max_risk_per_trade_percent / 100.0)
        try:
            steps = (sl_points * point_value) / tick_size
            loss_per_lot = steps * tick_value
            if loss_per_lot <= 0: return self.lot
            calc_lot = risk_amount / loss_per_lot
            calc_lot = round(calc_lot, 2)
            if calc_lot < 0.01: calc_lot = 0.01
            if calc_lot > 50.0: calc_lot = 50.0
            return calc_lot
        except:
            return self.lot

    def update_dynamic_params(self, basket_tp=None, basket_tp_long=None, basket_tp_short=None, 
                              lock_trigger=None, trailing_config=None):
        """Update dynamic parameters from AI analysis"""
        if basket_tp: self.global_tp = float(basket_tp) # Fallback global
        if basket_tp_long: self.dynamic_tp_long = float(basket_tp_long)
        if basket_tp_short: self.dynamic_tp_short = float(basket_tp_short)
        if lock_trigger: self.lock_profit_trigger = float(lock_trigger)
        if trailing_config: self.trailing_stop_config = trailing_config

    def check_grid_exit(self, positions, current_price, current_atr=None):
        """
        Basket Exit Logic with Smart TP and Trailing
        Returns: should_close_long, should_close_short, profit_long, profit_short, reason_long, reason_short
        """
        self._update_positions_state(positions)
        should_close_long = False
        should_close_short = False
        
        profit_long = 0.0
        profit_short = 0.0
        reason_long = ""
        reason_short = ""
        
        # --- Long Basket ---
        if self.long_pos_count > 0:
            # Calculate Volume and Profit
            long_positions = [p for p in positions if p.magic == self.magic_number and p.type == mt5.POSITION_TYPE_BUY]
            profit_long = sum([p.profit + p.swap for p in positions if p.magic == self.magic_number and p.type == mt5.POSITION_TYPE_BUY]) # Note: loop repeated for clarity, optimized below
            total_vol_long = sum([p.volume for p in long_positions])
            
            # 1. Dynamic TP
            # PRIORITY: Use dynamic_tp_long / dynamic_tp_short from AI Analysis if available
            target_tp = self.global_tp # Default fallback
            
            # [NEW] Volume-Based Scaling (Reasonable TP based on Position Size)
            # If no AI dynamic TP, calculate based on volume to prevent fixed $ targets being too small/large
            # Target ~400 points ($4.00 on Gold) average move
            # 1.0 Lot * 400 pts * $1/pt = $400
            # 0.01 Lot * 400 pts * $1/pt = $4
            scaled_tp = total_vol_long * 400.0 
            target_tp = max(self.global_tp, scaled_tp)
            
            if self.dynamic_tp_long and self.dynamic_tp_long > 0:
                target_tp = self.dynamic_tp_long
                # logger.info(f"Using AI Dynamic Long TP: {target_tp}")
            
            if profit_long >= target_tp:
                should_close_long = True
                reason_long = f"Basket TP Reached ({profit_long:.2f} >= {target_tp})"
                logger.info(f"Long {reason_long}")
                
            # 2. Lock & Trail
            if not should_close_long and self.lock_profit_trigger and profit_long >= self.lock_profit_trigger:
                if profit_long > self.max_basket_profit_long:
                    self.max_basket_profit_long = profit_long
                    
                # Lock 50% of Max Profit
                lock_val = max(1.0, self.max_basket_profit_long * 0.5)
                if self.basket_lock_level_long is None or lock_val > self.basket_lock_level_long:
                    self.basket_lock_level_long = lock_val
                    
                if profit_long < self.basket_lock_level_long:
                     should_close_long = True
                     reason_long = f"Basket Trailing Hit ({profit_long:.2f} < {self.basket_lock_level_long:.2f})"
                     logger.info(f"Long {reason_long}")

        # --- Short Basket ---
        if self.short_pos_count > 0:
            # Calculate Volume and Profit
            short_positions = [p for p in positions if p.magic == self.magic_number and p.type == mt5.POSITION_TYPE_SELL]
            profit_short = sum([p.profit + p.swap for p in positions if p.magic == self.magic_number and p.type == mt5.POSITION_TYPE_SELL])
            total_vol_short = sum([p.volume for p in short_positions])
            
            # 1. Dynamic TP
            # PRIORITY: Use dynamic_tp_long / dynamic_tp_short from AI Analysis if available
            target_tp = self.global_tp # Default fallback
            
            # [NEW] Volume-Based Scaling
            scaled_tp = total_vol_short * 400.0
            target_tp = max(self.global_tp, scaled_tp)
            
            if self.dynamic_tp_short and self.dynamic_tp_short > 0:
                target_tp = self.dynamic_tp_short
                # logger.info(f"Using AI Dynamic Short TP: {target_tp}")
            
            if profit_short >= target_tp:
                should_close_short = True
                reason_short = f"Basket TP Reached ({profit_short:.2f} >= {target_tp})"
                logger.info(f"Short {reason_short}")
                
            if not should_close_short and self.lock_profit_trigger and profit_short >= self.lock_profit_trigger:
                if profit_short > self.max_basket_profit_short:
                    self.max_basket_profit_short = profit_short
                
                lock_val = max(1.0, self.max_basket_profit_short * 0.5)
                if self.basket_lock_level_short is None or lock_val > self.basket_lock_level_short:
                    self.basket_lock_level_short = lock_val
                    
                if profit_short < self.basket_lock_level_short:
                     should_close_short = True
                     reason_short = f"Basket Trailing Hit ({profit_short:.2f} < {self.basket_lock_level_short:.2f})"
                     logger.info(f"Short {reason_short}")
                     
        return should_close_long, should_close_short, profit_long, profit_short, reason_long, reason_short

    def _update_positions_state(self, positions):
        self.long_pos_count = 0
        self.short_pos_count = 0
        for pos in positions:
            if pos.magic != self.magic_number: continue
            if pos.type == mt5.POSITION_TYPE_BUY: self.long_pos_count += 1
            elif pos.type == mt5.POSITION_TYPE_SELL: self.short_pos_count += 1
