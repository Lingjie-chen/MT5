import pandas as pd
import numpy as np
import logging

logger = logging.getLogger("FastBacktest")

def run_fast_grid_backtest(df: pd.DataFrame, params: list):
    """
    Fast Event-Driven Backtester for Grid Strategy.
    
    Params:
    [0]: grid_step_points (float)
    [1]: lot_multiplier (float)
    [2]: global_tp (float)
    """
    # 1. Parse Params
    grid_step_points = params[0]
    lot_multiplier = params[1]
    global_tp = params[2]
    
    # Constants
    POINT = 0.01 # Assuming Gold/Standard
    initial_balance = 10000.0
    balance = initial_balance
    
    positions = [] # List of {'type': 1/-1, 'price': float, 'volume': float}
    pending_orders = [] # List of {'type': 1/-1, 'price': float, 'volume': float}
    
    # State
    equity_curve = []
    
    # Pre-calculate Numpy arrays for speed
    opens = df['open'].values
    highs = df['high'].values
    lows = df['low'].values
    closes = df['close'].values
    
    n_candles = len(closes)
    
    # Simplified logic: 
    # If no positions, deploy grid around current close.
    # Check execution.
    # Check TP.
    
    base_lot = 0.01
    
    for i in range(n_candles):
        current_open = opens[i]
        current_high = highs[i]
        current_low = lows[i]
        current_close = closes[i]
        
        # 1. Check Pending Orders Execution
        # Buy Limit: Executed if Low <= Price
        # Sell Limit: Executed if High >= Price
        # (Simplified: assuming price touches limit)
        
        executed_indices = []
        for idx, order in enumerate(pending_orders):
            if order['type'] == 1: # Buy Limit
                if current_low <= order['price']:
                    positions.append(order)
                    executed_indices.append(idx)
            elif order['type'] == -1: # Sell Limit
                if current_high >= order['price']:
                    positions.append(order)
                    executed_indices.append(idx)
        
        # Remove executed (iterate reverse to avoid index shift)
        for idx in sorted(executed_indices, reverse=True):
            del pending_orders[idx]
            
        # 2. Calculate Floating PnL
        floating_pnl = 0.0
        if positions:
            for pos in positions:
                if pos['type'] == 1: # Buy
                    diff = current_close - pos['price']
                else: # Sell
                    diff = pos['price'] - current_close
                
                # Profit = Diff * Volume * ContractSize (100 for Gold usually, or 1 for simplified)
                # Let's assume 1 pip = $1 for 0.01 lot for simplicity or use standard calculation
                # Standard Gold: 1 lot = 100 oz. 0.01 lot = 1 oz. $1 move = $1.
                floating_pnl += diff * pos['volume'] * 100 
        
        # 3. Check Basket TP
        if positions and floating_pnl >= global_tp:
            balance += floating_pnl
            positions = []
            pending_orders = [] # Cancel pending on TP
            
        # 4. Deploy Grid if Empty
        if not positions and not pending_orders:
            # Simple Grid Deployment: 
            # 5 Buy Limits below, 5 Sell Limits above
            step_price = grid_step_points * POINT
            
            # Buy Grid
            for k in range(1, 6):
                price = current_close - (step_price * k)
                vol = base_lot * (lot_multiplier ** (k-1))
                pending_orders.append({'type': 1, 'price': price, 'volume': vol})
                
            # Sell Grid
            for k in range(1, 6):
                price = current_close + (step_price * k)
                vol = base_lot * (lot_multiplier ** (k-1))
                pending_orders.append({'type': -1, 'price': price, 'volume': vol})
                
        # Record Equity
        equity_curve.append(balance + floating_pnl)
        
    # Return Score (Net Profit - Drawdown Penalty)
    final_equity = balance + floating_pnl
    profit = final_equity - initial_balance
    
    # Calculate Max Drawdown
    peak = initial_balance
    max_dd = 0.0
    for eq in equity_curve:
        if eq > peak: peak = eq
        dd = peak - eq
        if dd > max_dd: max_dd = dd
        
    # Objective: Maximize Profit, Minimize DD
    # Score = Profit - (MaxDD * 2)
    score = profit - (max_dd * 1.5)
    
    return score
