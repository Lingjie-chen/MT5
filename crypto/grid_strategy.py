import logging
import numpy as np
import pandas as pd

logger = logging.getLogger("CryptoGrid")

class CryptoGridStrategy:
    def __init__(self, symbol, initial_balance=1000.0, leverage=1.0):
        self.symbol = symbol
        self.initial_balance = initial_balance
        self.leverage = leverage
        
        # Grid Parameters (Default)
        self.grid_type = "long"  # 'long', 'short', 'neutral'
        self.grid_upper_price = 0.0
        self.grid_lower_price = 0.0
        self.grid_steps = 10
        self.grid_orders = []  # List of dicts: {'price': float, 'amount': float, 'type': 'buy'/'sell'}
        
        # SMC Context
        self.smc_levels = {
            'ob_bullish': [], # Order Blocks
            'ob_bearish': [],
            'fvg_bullish': [], # Fair Value Gaps
            'fvg_bearish': [],
            'liquidity_high': 0.0,
            'liquidity_low': 0.0
        }
        
        # State
        self.active_grid = False
        self.entry_price_avg = 0.0
        self.total_position_size = 0.0

    def update_smc_levels(self, smc_data):
        """
        Update SMC levels from DeepSeek/SMC Analyzer
        smc_data: dict containing lists of price levels or zones
        """
        if not smc_data:
            return

        # Expected format: {'ob': [{'top': x, 'bottom': y, 'type': 'bullish'}], ...}
        # Simplify for grid: use mid-price of zones
        
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
            
        logger.info(f"Updated SMC Levels for Grid: {self.smc_levels}")

    def generate_grid_plan(self, current_price, trend_direction, volatility_atr, custom_step=None, grid_level_tps=None):
        """
        Generate a grid plan based on SMC levels and Trend.
        This focuses on "Smart Grid" placement - placing orders at key levels rather than fixed spacing.
        custom_step: Optional fixed step size (in price units) suggested by AI.
        grid_level_tps: Optional list of TP prices (or offsets) for each grid level.
        """
        self.grid_orders = []
        
        # 1. Determine Grid Range based on SMC
        # Look for nearest OB/FVG as support/resistance
        
        upper_bound = current_price + (volatility_atr * 10) # Fallback
        lower_bound = current_price - (volatility_atr * 10) # Fallback
        
        # Find nearest Resistance (Bearish OB / FVG)
        resistances = [p for p in self.smc_levels['ob_bearish'] + self.smc_levels['fvg_bearish'] if p > current_price]
        if resistances:
            upper_bound = min(resistances) # First resistance
            
        # Find nearest Support (Bullish OB / FVG)
        supports = [p for p in self.smc_levels['ob_bullish'] + self.smc_levels['fvg_bullish'] if p < current_price]
        if supports:
            lower_bound = max(supports) # First support
            
        self.grid_upper_price = upper_bound
        self.grid_lower_price = lower_bound
        
        logger.info(f"Grid Range Calculated: {lower_bound:.2f} - {upper_bound:.2f} (Current: {current_price:.2f})")
        
        # 2. Generate Orders
        # Strategy: 
        # - Long Grid: Place buy limits at support levels (OB/FVG) inside the range
        # - Short Grid: Place sell limits at resistance levels inside the range
        
        if trend_direction == 'bullish':
            self.grid_type = 'long'
            # Place buy orders from current price down to lower bound
            # Priority 1: SMC Levels
            key_levels = sorted([p for p in supports if p >= lower_bound and p < current_price], reverse=True)
            
            # Priority 2: Fill gaps with arithmetic spacing if SMC levels are sparse or Custom Step provided
            if custom_step and custom_step > 0:
                # Use AI recommended step
                num_steps = 5
                arithmetic_levels = [current_price - custom_step * i for i in range(1, num_steps + 1)]
                # Merge and sort (prioritize SMC, but ensure we have steps)
                key_levels = sorted(list(set(key_levels + arithmetic_levels)), reverse=True)
            elif len(key_levels) < 3:
                step = (current_price - lower_bound) / 5
                arithmetic_levels = [current_price - step * i for i in range(1, 6)]
                # Merge and sort
                key_levels = sorted(list(set(key_levels + arithmetic_levels)), reverse=True)
            
            for i, level in enumerate(key_levels):
                if level <= 0: continue
                
                # Dynamic TP Calculation
                tp = None
                if grid_level_tps and len(grid_level_tps) > 0:
                    # Use provided TP (assuming it's absolute price or offset?)
                    # If AI returns explicit prices, use them. If offsets, calculate.
                    # Assuming AI returns optimized absolute TP prices for simplicity, or offsets if small.
                    # Let's handle generic numeric values:
                    val = grid_level_tps[i] if i < len(grid_level_tps) else grid_level_tps[-1]
                    
                    if val > level: # Absolute price
                        tp = val
                    else: # Offset
                        tp = level + val
                
                self.grid_orders.append({
                    'price': level,
                    'type': 'buy', # Should be limit_buy really, but 'buy' + limit type is handled
                    'reason': 'SMC Support / Grid Step',
                    'tp': tp
                })
                
        elif trend_direction == 'bearish':
            self.grid_type = 'short'
            # Place sell orders from current price up to upper bound
            key_levels = sorted([p for p in resistances if p <= upper_bound and p > current_price])
            
            if custom_step and custom_step > 0:
                 # Use AI recommended step
                num_steps = 5
                arithmetic_levels = [current_price + custom_step * i for i in range(1, num_steps + 1)]
                key_levels = sorted(list(set(key_levels + arithmetic_levels)))
            elif len(key_levels) < 3:
                step = (upper_bound - current_price) / 5
                arithmetic_levels = [current_price + step * i for i in range(1, 6)]
                key_levels = sorted(list(set(key_levels + arithmetic_levels)))
                
            for i, level in enumerate(key_levels):
                # Dynamic TP Calculation
                tp = None
                if grid_level_tps and len(grid_level_tps) > 0:
                    val = grid_level_tps[i] if i < len(grid_level_tps) else grid_level_tps[-1]
                    
                    if val > 0 and val < level: # Absolute price below entry (for short)
                        tp = val
                    else: # Offset (positive number)
                        tp = level - val

                self.grid_orders.append({
                    'price': level,
                    'type': 'sell',
                    'reason': 'SMC Resistance / Grid Step',
                    'tp': tp
                })
        
        return self.grid_orders

    def calculate_lot_sizes(self, available_balance, risk_per_grid=0.02):
        """
        Calculate position sizes for grid orders.
        Uses Martingale or Fixed risk? 
        User asked for "Max capital utilization" but let's be smart.
        We distribute the risk across the grid steps.
        """
        if not self.grid_orders:
            return
        
        num_orders = len(self.grid_orders)
        if num_orders == 0: return
        
        # Simple Logic: Allocate total capital for this grid session
        # e.g., use 50% of available balance for the grid
        total_allocation = available_balance * 0.5 * self.leverage
        
        # Distribute: 
        # Option A: Equal split
        # base_amount_usd = total_allocation / num_orders
        
        # Option B: Pyramid (scale in larger at better prices)
        # 1, 1.2, 1.4, 1.6 ...
        weights = [1.0 + (i * 0.2) for i in range(num_orders)]
        total_weight = sum(weights)
        
        for i, order in enumerate(self.grid_orders):
            weight = weights[i]
            amount_usd = (weight / total_weight) * total_allocation
            # Convert USD to coin amount
            amount_coin = amount_usd / order['price']
            order['amount'] = amount_coin
            
        logger.info(f"Calculated lots for {num_orders} grid orders. Total allocation: {total_allocation:.2f} USD")

    def get_execution_orders(self):
        """Return the list of orders to be placed"""
        return self.grid_orders
