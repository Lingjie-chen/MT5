import pandas as pd
import numpy as np
import MetaTrader5 as mt5
import logging
from .orb_strategy import GoldORBStrategy

logger = logging.getLogger("KalmanGrid")

class KalmanGridStrategy:
    def __init__(self, symbol, magic_number, initial_lot=0.01):
        self.symbol = symbol
        self.magic_number = magic_number
        self.lot = initial_lot
        logger.info(f"KalmanGridStrategy Initialized for {symbol} (v2026.02.13.1)")
        
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
            "tp_steps": { 1: 5.0, 2: 8.0, 3: 12.0 },
            "global_tp": 10.0 
        }
        
        # XAUUSD Config
        xau_config = {
            "grid_step_points": 250, 
            "max_grid_steps": 20,    
            "lot_type": 'FIBONACCI',
            "lot_multiplier": 1.3,   
            "tp_steps": { 1: 5.0, 2: 8.0, 3: 12.0 },
            "global_tp": 15.0 
        }
        
        config = default_config
        if "XAU" in self.symbol.upper() or "GOLD" in self.symbol.upper():
            config = xau_config
            
        self.grid_step_points = config["grid_step_points"]
        self.max_grid_steps = config["max_grid_steps"]
        self.lot_type = config["lot_type"]
        self.lot_multiplier = config["lot_multiplier"]
        self.tp_steps = config["tp_steps"]
        self.global_tp = config["global_tp"]

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
        
        # A. BB Bandwidth Squeeze
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
        
        # Combine Signals
        # We consider it ranging if BB is squeezing OR price is stuck in middle 50%
        # The LLM will do the final confirmation
        self.is_ranging = is_bb_squeeze or is_price_in_range
        
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
            "trend_ma": "bullish" if current_price > self.ma_value else "bearish"
        }

    def generate_fibonacci_grid(self, current_price, trend_direction, point=0.01):
        """
        Generate Fibonacci Grid Levels based on recent Swing High/Low.
        Ratios: 0.236, 0.382, 0.5, 0.618, 0.786
        """
        orders = []
        
        # Ensure we have valid swings
        if self.swing_high <= self.swing_low:
             # Fallback to local 50 bars
             return self.generate_simple_grid(current_price, trend_direction, point)
             
        swing_range = self.swing_high - self.swing_low
        ratios = [0.236, 0.382, 0.5, 0.618, 0.786]
        
        # Grid deployment logic:
        # If Ranging/Neutral: Place Limit Buys at lower Fibs, Limit Sells at upper Fibs.
        # If Trend Following (Bullish): Buy Dips at Fib levels.
        
        # Assuming we use this for "Grid Strategy" in Ranging Market (Switching Logic)
        
        if self.is_ranging or True: # Force Fib Grid if called
            
            # Calculate levels
            levels_buy = []
            levels_sell = []
            
            # Retracements from Low to High
            # 0.236 from Top is High - 0.236*Range
            
            for r in ratios:
                price_level_from_top = self.swing_high - (swing_range * r)
                # If price is below this level, it might be a resistance (Sell Limit candidate if above current)
                # If price is above this level, it is a support (Buy Limit candidate if below current)
                
                # To ensure we deploy ALL grid levels (batch deployment), we don't strictly filter by current price proximity for execution NOW,
                # but we filter for Validity (Buy Limit must be < Current, Sell Limit must be > Current).
                # The user requested "Deploy all at once", which we are doing.
                
                if price_level_from_top < current_price:
                    levels_buy.append(price_level_from_top)
                elif price_level_from_top > current_price:
                    levels_sell.append(price_level_from_top)
            
            # Sort levels
            levels_buy.sort(reverse=True) # Closest to price first
            levels_sell.sort() # Closest to price first
            
            # Generate Orders - BATCH DEPLOYMENT
            # We deploy ALL valid levels found above
            
            # Buy Limits
            for i, price in enumerate(levels_buy):
                lot = self.calculate_next_lot(i + 1)
                orders.append({
                    'type': 'limit_buy',
                    'price': price,
                    'tp': 0.0, # Managed by Basket
                    'volume': lot,
                    'comment': f'Fib Grid {ratios[i]}'
                })
                
            # Sell Limits
            for i, price in enumerate(levels_sell):
                lot = self.calculate_next_lot(i + 1)
                orders.append({
                    'type': 'limit_sell',
                    'price': price,
                    'tp': 0.0,
                    'volume': lot,
                    'comment': f'Fib Grid {ratios[i]}' # Ratio logic might be inverted index-wise
                })
                
        return orders

    def generate_simple_grid(self, current_price, trend_direction, point=0.01):
        # Fallback simple grid
        step = self.grid_step_points * point
        orders = []
        for i in range(1, 6):
            if trend_direction == 'bullish':
                price = current_price - (step * i)
                orders.append({'type': 'limit_buy', 'price': price, 'volume': self.calculate_next_lot(i), 'tp': 0.0})
            else:
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
            profit_long = sum([p.profit + p.swap for p in positions if p.magic == self.magic_number and p.type == mt5.POSITION_TYPE_BUY])
            
            # 1. Dynamic TP
            # PRIORITY: Use dynamic_tp_long / dynamic_tp_short from AI Analysis if available
            target_tp = self.global_tp # Default fallback
            
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
            profit_short = sum([p.profit + p.swap for p in positions if p.magic == self.magic_number and p.type == mt5.POSITION_TYPE_SELL])
            
            target_tp = self.dynamic_tp_short if self.dynamic_tp_short else self.global_tp
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
