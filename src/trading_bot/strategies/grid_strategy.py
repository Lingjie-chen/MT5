import pandas as pd
import numpy as np
import MetaTrader5 as mt5
import logging
from trading_bot.risk.dynamic_risk_manager import DynamicRiskManager

logger = logging.getLogger("KalmanGrid")

class KalmanGridStrategy:
    def __init__(self, symbol, magic_number, initial_lot=0.01):
        self.symbol = symbol
        self.magic_number = magic_number
        self.lot = initial_lot
        logger.info(f"KalmanGridStrategy Initialized for {symbol} (v2026.01.12.1)")
        
        # Risk Manager
        self.risk_manager = DynamicRiskManager()
        self.market_status = {} # Store latest full market analysis
        self.ai_confidence = 0.8
        self.mae_stats = {} 
        
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
        
        self.dynamic_global_tp = None # Deprecated, use specific ones
        self.dynamic_tp_long = None
        self.dynamic_tp_short = None
        
        # [NEW] Basket SL (From AI)
        self.dynamic_sl_long = None
        self.dynamic_sl_short = None
        
        self.lock_profit_trigger = None # Store AI recommended Lock Trigger
        self.trailing_stop_config = None # Store AI recommended Trailing Config
        
        # [MODIFIED] Separate State for Long and Short Baskets
        self.basket_lock_level_long = None 
        self.max_basket_profit_long = 0.0 
        self.basket_lock_level_short = None
        self.max_basket_profit_short = 0.0
        
        # Deprecated mixed state (kept for safety if referenced elsewhere)
        self.basket_lock_level = None 
        self.max_basket_profit = 0.0 
        
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
        
        # XAUUSD Config (Trend Following - Optimized for M15)
        xau_config = {
            "grid_step_points": 250, # [Optimized] Wider grid (250 pts = $2.5) for M15 Trend Following
            "max_grid_steps": 20,    # [Optimized] Wide coverage for trend corrections
            "lot_type": 'GEOMETRIC',
            "lot_multiplier": 1.3,   # [Optimized] Slowly increasing (1.3x)
            "tp_steps": {
                # [Optimized] Trend Targets: $5, $8, $12...
                1: 5.0, 2: 8.0, 3: 12.0, 4: 18.0, 5: 25.0,
                6: 35.0, 7: 45.0, 8: 55.0, 9: 65.0, 10: 80.0,
                11: 100.0, 12: 120.0, 13: 140.0, 14: 160.0, 15: 180.0
            },
            "global_tp": 15.0 # [Optimized] Target $15 profit (Trend Following)
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

    def update_market_status(self, analysis: dict, ai_confidence: float = 0.8, mae_stats: dict = None):
        """
        Update real-time market status for Dynamic Risk Management
        """
        if analysis:
            self.market_status = analysis
        if ai_confidence is not None:
            self.ai_confidence = ai_confidence
        if mae_stats:
            self.mae_stats = mae_stats
            
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
        # Lookback 50 bars (Default) -> M15 requires shorter lookback? 
        # Actually, if we run on M15/H1 timeframe, 'df' is M15/H1.
        # But User requested "Analysis Fibonacci structure based on 15-minute structure".
        # Since 'update_market_data' receives 'df' which comes from main loop's timeframe (M15 or H1),
        # we cannot see M5 structure here directly unless main loop passes M5 data.
        
        # However, we can approximate "Micro Structure" by using a shorter lookback on current timeframe
        # or rely on the LLM (who sees multi-tf data) to guide the direction/levels via 'grid_config'.
        
        # For this function, we stick to calculating local swings.
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
        
        # [NEW POLICY]
        # Autonomous Grid Adding is PERMANENTLY DISABLED.
        # Adding positions is only allowed via LLM explicit signals (Pyramiding) or Limit Orders.
        
        return None, 0.0

    def calculate_next_lot(self, current_count, ai_override_multiplier=None):
        """
        Calculate next lot size based on strategy.
        Uses Martingale, Pyramid, or Fibonacci logic.
        """
        multiplier = 1.0
        
        # Priority 1: AI Override Multiplier
        if ai_override_multiplier and ai_override_multiplier > 0:
             # Treat as Geometric with custom multiplier
             multiplier = ai_override_multiplier ** current_count
             return float(f"{self.lot * multiplier:.2f}")

        # Priority 2: Fibonacci Sequence
        # User Requirement: Grid strategy requires matching Fibonacci sequence for callback adding positions
        # [MODIFIED] To ensure we use Fibonacci even if 'lot_type' wasn't explicitly set by legacy config
        # We default to FIBONACCI if no specific type or if type is GEOMETRIC/ARITHMETIC but we want to enforce User Rule.
        
        # Let's enforce Fibonacci if lot_type is not specifically set to something else strict,
        # or we can just make it the default logic as per user request.
        
        # For now, let's respect the flag but ensure it defaults to FIBONACCI in main.py initialization
        # (which we did in previous step: self.grid_strategy.lot_type = 'FIBONACCI')
        
        if getattr(self, 'lot_type', 'FIBONACCI') == 'FIBONACCI':
            # Fibonacci Sequence: 1, 1, 2, 3, 5, 8, 13...
            def fib(n):
                if n <= 1: return 1
                a, b = 1, 1
                for _ in range(2, n + 1):
                    a, b = b, a + b
                return b
            
            # current_count starts from 1 for the first add? 
            # Usually base position is count=0 (or 1).
            # If current_count represents the "nth grid level" (1, 2, 3...),
            # Level 1 (1st Add) -> Fib(1) = 1 (Same as Base)
            # Level 2 (2nd Add) -> Fib(2) = 1 (Same as Base)
            # Level 3 (3rd Add) -> Fib(3) = 2 (Double)
            # This is a safe progression.
            
            fib_mult = fib(current_count) 
            # Note: If current_count=0 (Base), fib(0)=1.
            # If current_count=1 (1st Grid Order), fib(1)=1.
            
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

    def generate_grid_plan(self, current_price, trend_direction, atr, point=0.01, dynamic_step_pips=None, grid_level_tps=None, override_lot_sequence=None):
        """
        Generate a plan for grid deployment (for limit orders)
        Uses Fibonacci Retracement Levels for placement if applicable.
        override_lot_sequence: Optional list of lot sizes for each grid level [lot_1, lot_2, ...]
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
        
        # [Optimized] Trend Strength Calculation (Internal)
        trend_strength = 0.0
        if self.ma_value > 0:
            trend_strength = (self.kalman_value - self.ma_value) / self.ma_value * 10000 
            
        is_strong_uptrend = trend_strength > 5.0
        is_strong_downtrend = trend_strength < -5.0

        # [Optimized] Dynamic Step Adjustment for Trends
        # If trend is strong, tighten the grid to catch shallow pullbacks (Trend Surfing)
        step_modifier = 1.0
        if (trend_direction == 'bullish' and is_strong_uptrend) or (trend_direction == 'bearish' and is_strong_downtrend):
            step_modifier = 0.6 # Reduce step by 40% in strong trends
            logger.info(f"Strong Trend Detected (Strength {trend_strength:.2f}). Tightening grid step by 40%.")

        # Calculate fixed step based on config or dynamic override
        if dynamic_step_pips and dynamic_step_pips > 0:
            fixed_step = dynamic_step_pips * 10 * point * step_modifier
            logger.info(f"Using Dynamic Grid Step: {dynamic_step_pips} pips * {step_modifier} = {fixed_step:.1f} points")
        else:
            fixed_step = self.grid_step_points * point * step_modifier
            
        # Ensure minimum safe step (e.g. 50 points or 0.2 ATR)
        min_safe_step = 50 * point
        if atr > 0:
             min_safe_step = max(min_safe_step, atr * 0.15)
        
        # In strong trend, allow slightly tighter minimum (Aggressive)
        if step_modifier < 1.0:
            min_safe_step *= 0.8
        
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
                # Use Fibonacci logic if specified or default, OR use override sequence
                lot = 0.01
                if override_lot_sequence and i < len(override_lot_sequence):
                    lot = float(override_lot_sequence[i])
                else:
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
                lot = 0.01
                if override_lot_sequence and i < len(override_lot_sequence):
                    lot = float(override_lot_sequence[i])
                else:
                    lot = self.calculate_next_lot(base_count + i)
                
                orders.append({'type': 'limit_sell', 'price': lvl, 'tp': tp_price, 'volume': lot})
                
        return orders

    # ... (Rest of existing methods: check_basket_tp, update_config, _update_positions_state) ...
    def check_grid_exit(self, positions, current_price, current_atr=None):
        """
        Basket Exit Logic:
        Close all positions if Total Profit > Dynamic Basket TP (calculated by AI + Algo).
        """
        # Update internal state (counts, last prices)
        self._update_positions_state(positions)
        
        should_close_long = False
        should_close_short = False
        
        # --- Long Basket ---
        if self.long_pos_count > 0:
            total_profit_long = 0.0
            for pos in positions:
                if pos.magic == self.magic_number and pos.type == mt5.POSITION_TYPE_BUY:
                    total_profit_long += (pos.profit + pos.swap)
            
            # [CHECK] Dynamic Basket TP
            # Calculate Tiered TP Target
            base_tp_long = self.dynamic_tp_long if (self.dynamic_tp_long is not None and self.dynamic_tp_long > 0) else self.global_tp
            target_tp_long = self.risk_manager.calculate_tiered_tp(
                base_tp=base_tp_long,
                current_atr=current_atr if current_atr else 0,
                level_index=self.long_pos_count
            )
            
            if total_profit_long >= target_tp_long:
                logger.info(f"✅ Long Basket TP Hit! Profit: ${total_profit_long:.2f} >= Target: ${target_tp_long:.2f} (Base: {base_tp_long}, Tiered)")
                should_close_long = True

            # [CHECK] Dynamic Basket SL (Enhanced)
            if self.dynamic_sl_long is not None and self.dynamic_sl_long < 0:
                base_sl = abs(self.dynamic_sl_long)
                effective_sl, log_details = self.risk_manager.calculate_dynamic_basket_sl(
                    base_sl_amount=base_sl,
                    direction='long',
                    market_analysis=self.market_status,
                    ai_confidence=self.ai_confidence,
                    mae_stats=self.mae_stats,
                    current_drawdown=abs(total_profit_long) if total_profit_long < 0 else 0
                )
                
                if total_profit_long <= effective_sl:
                    logger.warning(f"🛑 Long Basket Dynamic SL Reached! Profit: ${total_profit_long:.2f} <= Limit: ${effective_sl:.2f} (Base: -{base_sl})")
                    logger.info(f"Dynamic SL Logic: {log_details}")
                    should_close_long = True
                
            # [CHECK] Lock Profit / Trailing Logic (Enhanced)
            if not should_close_long and self.lock_profit_trigger and self.lock_profit_trigger > 0:
                # 触发逻辑: 只要浮盈超过 trigger (例如 10)，就启动保本/追踪
                if total_profit_long >= self.lock_profit_trigger:
                    # 记录最大浮盈
                    if total_profit_long > self.max_basket_profit_long:
                        self.max_basket_profit_long = total_profit_long
                        
                    # 计算锁定线: 默认锁定 50% 的最大浮盈，或者至少保本 (+1.0)
                    # 比如 Trigger=10, Max=20 -> Lock=10
                    # Trigger=10, Max=10 -> Lock=5
                    
                    # 简单逻辑: 启动后，锁定利润 = Max * 0.5 (可配置)
                    current_lock = max(10.0, self.max_basket_profit_long * 0.6) 
                    
                    if self.basket_lock_level_long is None or current_lock > self.basket_lock_level_long:
                        self.basket_lock_level_long = current_lock
                        # Log only on update
                        # logger.info(f"Long Basket Lock Updated: ${self.basket_lock_level_long:.2f} (Max: ${self.max_basket_profit_long:.2f})")
                
                # 检查是否触及锁定线 (且当前必须为盈利状态，亏损则不触发 Trailing Close，依靠 SL)
                if self.basket_lock_level_long is not None and total_profit_long < self.basket_lock_level_long:
                     # if total_profit_long > 0: # [USER REQ] 允许亏损时也触发 Trailing Hit (保护已到手的利润，即使回撤到亏损)
                     logger.info(f"🛑 Long Basket Trailing Hit! Profit ${total_profit_long:.2f} dropped below Lock ${self.basket_lock_level_long:.2f}")
                     should_close_long = True

        # --- Short Basket ---
        if self.short_pos_count > 0:
            total_profit_short = 0.0
            for pos in positions:
                if pos.magic == self.magic_number and pos.type == mt5.POSITION_TYPE_SELL:
                    total_profit_short += (pos.profit + pos.swap)
            
            # [CHECK] Dynamic Basket TP
            if self.dynamic_tp_short is not None and self.dynamic_tp_short > 0 and total_profit_short >= self.dynamic_tp_short:
                logger.info(f"✅ Short Basket TP Hit! Profit: ${total_profit_short:.2f} >= Target: ${self.dynamic_tp_short:.2f}")
                should_close_short = True

            # [CHECK] Dynamic Basket SL
            if self.dynamic_sl_short is not None and self.dynamic_sl_short < 0 and total_profit_short <= self.dynamic_sl_short:
                logger.warning(f"🛑 Short Basket SL Reached! Profit: ${total_profit_short:.2f} <= Limit: ${self.dynamic_sl_short:.2f}")
                should_close_short = True
            
            # [CHECK] Lock Profit / Trailing Logic (Enhanced)
            if not should_close_short and self.lock_profit_trigger and self.lock_profit_trigger > 0:
                if total_profit_short >= self.lock_profit_trigger:
                    if total_profit_short > self.max_basket_profit_short:
                        self.max_basket_profit_short = total_profit_short
                        
                        # 计算锁定线: 默认锁定 50% 的最大浮盈，或者至少保本 (+1.0)
                    # 比如 Trigger=10, Max=20 -> Lock=10
                    # Trigger=10, Max=10 -> Lock=5
                    
                    # 简单逻辑: 启动后，锁定利润 = Max * 0.6 (可配置)
                    current_lock = max(10.0, self.max_basket_profit_short * 0.6) 
                    
                    if self.basket_lock_level_short is None or current_lock > self.basket_lock_level_short:
                        self.basket_lock_level_short = current_lock
                
                if self.basket_lock_level_short is not None and total_profit_short < self.basket_lock_level_short:
                     # if total_profit_short > 0: # [USER REQ] Enable trailing close even if profit drops to negative
                     logger.info(f"🛑 Short Basket Trailing Hit! Profit ${total_profit_short:.2f} dropped below Lock ${self.basket_lock_level_short:.2f}")
                     should_close_short = True

        
        return should_close_long, should_close_short

    def _check_single_basket(self, total_profit, count, total_volume, current_atr, is_long=True):
        if count == 0:
            if is_long:
                self.max_basket_profit_long = 0.0
                self.basket_lock_level_long = None
            else:
                self.max_basket_profit_short = 0.0
                self.basket_lock_level_short = None
            return False
            
        # Select state variables
        if is_long:
            max_profit = self.max_basket_profit_long
            lock_level = self.basket_lock_level_long
        else:
            max_profit = self.max_basket_profit_short
            lock_level = self.basket_lock_level_short
            
        # Update Max Profit
        if total_profit > max_profit:
            max_profit = total_profit
            if is_long: self.max_basket_profit_long = max_profit
            else: self.max_basket_profit_short = max_profit
            
        # --- 1. Regular Basket TP ---
        target_tp = self.global_tp # Default fallback
        
        # Select Dynamic TP based on direction
        dynamic_tp = self.dynamic_tp_long if is_long else self.dynamic_tp_short
        
        # Fallback to legacy single dynamic var if specific not set (backward compatibility)
        if dynamic_tp is None:
            dynamic_tp = self.dynamic_global_tp
            
        used_source = "Default/Step"
        if dynamic_tp is not None and dynamic_tp > 0:
            target_tp = dynamic_tp
            used_source = f"Dynamic (Val={dynamic_tp})"
        else:
            # [NEW POLICY] If no Dynamic TP from LLM, do NOT fallback to small step TPs.
            # In Trend Mode, we want to let profits run unless LLM says otherwise.
            # We use a very high safety default if LLM is silent.
            target_tp = 99999.0 
            used_source = "Safety Max (No LLM TP)"
            
            # target_tp = self.tp_steps.get(count, self.global_tp)
            # if count > 9: target_tp = self.global_tp
            # used_source = f"Step (Count={count})"

        if total_profit >= target_tp:
            logger.info(f"Trend Position TP ({'LONG' if is_long else 'SHORT'}) Reached: Profit {total_profit:.2f} >= Target {target_tp} (Source: {used_source})")
            return True
            
        # --- 2. Profit Locking Logic (Trailing Stop for Basket) ---
        effective_trigger = 9999.0 # Default inactive
        
        if self.lock_profit_trigger is not None and self.lock_profit_trigger > 0:
             effective_trigger = self.lock_profit_trigger
             
        if max_profit >= effective_trigger:
            # We are in locking mode
            lock_ratio = 0.7 # Default 70%
            dynamic_sl_profit_dist = 0.0
            step_size_usd = 5.0 # Minimum step size to update lock (USD)
            
            if self.trailing_stop_config:
                t_type = self.trailing_stop_config.get('type', 'atr_distance')
                t_value = float(self.trailing_stop_config.get('value', 2.0))
                
                if t_type == 'atr_distance' and current_atr is not None and current_atr > 0:
                     contract_size = 100.0 
                     if "ETH" in self.symbol.upper(): contract_size = 1.0
                     if "EUR" in self.symbol.upper(): contract_size = 100000.0
                     dynamic_sl_profit_dist = current_atr * t_value * total_volume * contract_size
                elif t_type == 'fixed_pips':
                     pip_value_per_lot = 10.0
                     if "ETH" in self.symbol.upper(): pip_value_per_lot = 1.0
                     price_dist_pips = t_value
                     dynamic_sl_profit_dist = price_dist_pips * pip_value_per_lot * total_volume

            ideal_lock = 0.0
            if dynamic_sl_profit_dist > 0:
                ideal_lock = max_profit - dynamic_sl_profit_dist
            else:
                surplus = max(0.0, max_profit - effective_trigger)
                ideal_lock = effective_trigger + (surplus * lock_ratio)
            
            min_break_even = 2.0 
            ideal_lock = max(ideal_lock, min_break_even)
            
            # Step Logic
            new_lock_level = lock_level
            if lock_level is None:
                new_lock_level = ideal_lock
                logger.info(f"Grid Profit Lock ({'LONG' if is_long else 'SHORT'}) ACTIVATED: Step Lock Level set at {new_lock_level:.2f} (Trigger: {effective_trigger}, MaxProfit: {max_profit:.2f})")
            else:
                if ideal_lock >= (lock_level + step_size_usd):
                    new_lock_level = ideal_lock
                    logger.info(f"Grid Profit Lock ({'LONG' if is_long else 'SHORT'}) STEP UP: {lock_level:.2f} -> {new_lock_level:.2f} (Peak: {max_profit:.2f}, StepSize: {step_size_usd})")

            # Update state
            if is_long: self.basket_lock_level_long = new_lock_level
            else: self.basket_lock_level_short = new_lock_level
            
            if total_profit <= new_lock_level:
                logger.info(f"Grid Profit Lock ({'LONG' if is_long else 'SHORT'}) Triggered: Profit {total_profit:.2f} <= Step Lock {new_lock_level:.2f}")
                return True
                
        return False

    def update_dynamic_params(self, basket_tp=None, basket_tp_long=None, basket_tp_short=None, 
                              basket_sl_long=None, basket_sl_short=None,
                              lock_trigger=None, trailing_config=None):
        """Update dynamic parameters from AI analysis"""
        try:
            if basket_tp is not None:
                val = float(basket_tp)
                if val > 0:
                    self.dynamic_global_tp = val
                    # If specific ones are not provided, apply global to both
                    if basket_tp_long is None: self.dynamic_tp_long = val
                    if basket_tp_short is None: self.dynamic_tp_short = val
                    logger.info(f"Updated Dynamic Basket TP (Global): {self.dynamic_global_tp}")
        except (ValueError, TypeError):
             logger.warning(f"Invalid basket_tp value: {basket_tp}")
            
        try:
            if basket_tp_long is not None:
                val = float(basket_tp_long)
                if val > 0:
                    self.dynamic_tp_long = val
                    logger.info(f"Updated Dynamic Basket TP (Long): {self.dynamic_tp_long}")
        except (ValueError, TypeError):
             logger.warning(f"Invalid basket_tp_long value: {basket_tp_long}")
            
        try:
            if basket_tp_short is not None:
                val = float(basket_tp_short)
                if val > 0:
                    self.dynamic_tp_short = val
                    logger.info(f"Updated Dynamic Basket TP (Short): {self.dynamic_tp_short}")
        except (ValueError, TypeError):
             logger.warning(f"Invalid basket_tp_short value: {basket_tp_short}")

        # [NEW] Basket SL Updates
        try:
            if basket_sl_long is not None:
                val = float(basket_sl_long)
                if val < 0: val = abs(val) # Store as positive value representing loss amount
                if val > 0:
                    self.dynamic_sl_long = -val # Store as negative number
                    logger.info(f"Updated Dynamic Basket SL (Long): {self.dynamic_sl_long}")
        except (ValueError, TypeError):
             logger.warning(f"Invalid basket_sl_long value: {basket_sl_long}")

        try:
            if basket_sl_short is not None:
                val = float(basket_sl_short)
                if val < 0: val = abs(val)
                if val > 0:
                    self.dynamic_sl_short = -val # Store as negative number
                    logger.info(f"Updated Dynamic Basket SL (Short): {self.dynamic_sl_short}")
        except (ValueError, TypeError):
             logger.warning(f"Invalid basket_sl_short value: {basket_sl_short}")

            
        if lock_trigger is not None:
            if lock_trigger > 0:
                self.lock_profit_trigger = float(lock_trigger)
                logger.info(f"Updated Dynamic Lock Trigger: {self.lock_profit_trigger}")
            else:
                self.lock_profit_trigger = None
                logger.info("Dynamic Lock Trigger DISABLED (User Request)")
            
        if trailing_config is not None:
            if isinstance(trailing_config, dict) and trailing_config:
                self.trailing_stop_config = trailing_config
                logger.info(f"Updated Dynamic Trailing Config: {self.trailing_stop_config}")
            else:
                self.trailing_stop_config = None
                logger.info("Dynamic Trailing Config DISABLED (User Request)")

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
