import sys
import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', 'src')
if src_dir not in sys.path: sys.path.append(src_dir)

# Import Modules
from trading_bot.analysis.optimization import WOAm
from trading_bot.analysis.fast_grid_backtest import run_fast_grid_backtest
from trading_bot.data.mt5_data_processor import MT5DataProcessor

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("OptimizationScript")

def real_objective_function(params, df):
    """
    Real Objective Function using Fast Backtest.
    """
    # Run backtest
    score = run_fast_grid_backtest(df, params)
    return score

def main():
    logger.info("Starting REAL Strategy Parameter Optimization...")
    
    # 1. Fetch Historical Data
    processor = MT5DataProcessor()
    symbol = "GOLD" # Or XAUUSD based on availability
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30) # Last 30 Days
    
    logger.info(f"Fetching {symbol} data from {start_date} to {end_date}...")
    df = processor.get_historical_data(symbol, None, start_date, end_date) # Default M15
    
    if df is None or df.empty:
        # Fallback for symbol name
        symbol = "XAUUSD"
        logger.info(f"Retrying with {symbol}...")
        df = processor.get_historical_data(symbol, None, start_date, end_date)
        
    if df is None or df.empty:
        logger.error("Failed to fetch data. Aborting.")
        return

    logger.info(f"Data fetched: {len(df)} candles.")
    
    # 2. Define Search Space
    # (Min, Max) for each parameter
    bounds = [
        (100.0, 500.0), # Grid Step (Points)
        (1.1, 2.0),     # Lot Multiplier
        (10.0, 100.0)   # Global TP ($ or Points, backtest assumes PnL sum)
    ]
    
    # Define Discretization Steps
    steps = [
        10.0, # Grid step
        0.1,  # Multiplier
        5.0   # TP
    ]
    
    # 3. Initialize Optimizer
    optimizer = WOAm(pop_size=30, power_dist_coeff=20.0)
    
    # 4. Run Optimization
    # Use lambda/partial to pass df
    logger.info(f"Optimizing parameters over 30 epochs (Population: 30)...")
    
    # Wrapper for joblib serialization compatibility
    # We define it here to capture 'df'
    def obj_func_wrapper(p):
        return real_objective_function(p, df)
    
    best_params, best_score = optimizer.optimize(
        objective_function=obj_func_wrapper,
        bounds=bounds,
        steps=steps,
        epochs=30,
        n_jobs=1 # Use 1 job for debugging/simplicity, or higher if stable
    )
    
    # 5. Output Results
    logger.info("Optimization Complete!")
    logger.info(f"Best Score (Net Profit - Drawdown Penalty): {best_score:.2f}")
    logger.info("Best Parameters:")
    logger.info(f"  Grid Step: {best_params[0]:.1f}")
    logger.info(f"  Lot Multiplier: {best_params[1]:.1f}")
    logger.info(f"  TP Pips: {best_params[2]:.1f}")
    
    print("\nRecommended Config Update:")
    print(f"grid_step_points = {int(best_params[0])}")
    print(f"lot_multiplier = {best_params[1]:.1f}")
    print(f"global_tp = {best_params[2]:.1f}")

    # 6. Save to JSON for Bot Auto-Loading
    config_path = os.path.join(src_dir, 'trading_bot', 'config', 'grid_config.json')
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    new_config = {
        "grid_step_points": int(best_params[0]),
        "lot_multiplier": round(float(best_params[1]), 2),
        "global_tp": round(float(best_params[2]), 2),
        "updated_at": datetime.now().isoformat()
    }
    
    try:
        import json
        with open(config_path, 'w') as f:
            json.dump(new_config, f, indent=4)
        logger.info(f"Configuration saved to {config_path}")
    except Exception as e:
        logger.error(f"Failed to save configuration: {e}")
    
    processor.close()

if __name__ == "__main__":
    main()
