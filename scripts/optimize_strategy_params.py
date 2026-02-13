import sys
import os
import logging
import numpy as np

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', 'src')
if src_dir not in sys.path: sys.path.append(src_dir)

from trading_bot.analysis.optimization import WOAm, TETA

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("OptimizationScript")

def mock_objective_function(params):
    """
    Mock objective function for demonstration.
    In a real scenario, this would run a backtest with the given parameters.
    
    Params:
    [0]: grid_step_points (100 - 500)
    [1]: lot_multiplier (1.0 - 2.0)
    [2]: tp_pips (10 - 100)
    """
    grid_step = params[0]
    lot_mult = params[1]
    tp_pips = params[2]
    
    # Simulate a fitness landscape
    # Assume optimal is around: Step=250, Mult=1.5, TP=50
    
    score = 0
    score -= abs(grid_step - 250) * 0.5
    score -= abs(lot_mult - 1.5) * 100
    score -= abs(tp_pips - 50) * 2
    
    # Add some noise
    noise = np.random.normal(0, 5)
    
    return score + 1000 + noise

def main():
    logger.info("Starting Strategy Parameter Optimization using WOAm...")
    
    # Define Search Space
    # (Min, Max) for each parameter
    bounds = [
        (100.0, 500.0), # Grid Step
        (1.0, 2.0),     # Lot Multiplier
        (10.0, 100.0)   # TP Pips
    ]
    
    # Define Discretization Steps (SeInDiSp)
    # Step size for each parameter
    steps = [
        10.0, # Grid step in 10 point increments
        0.1,  # Multiplier in 0.1 increments
        5.0   # TP in 5 pip increments
    ]
    
    # Initialize Optimizer
    optimizer = WOAm(pop_size=50, power_dist_coeff=20.0)
    
    # Run Optimization
    logger.info(f"Optimizing {len(bounds)} parameters over 50 epochs...")
    best_params, best_score = optimizer.optimize(
        objective_function=mock_objective_function,
        bounds=bounds,
        steps=steps,
        epochs=50,
        n_jobs=4 # Use parallel processing
    )
    
    logger.info("Optimization Complete!")
    logger.info(f"Best Score: {best_score:.4f}")
    logger.info("Best Parameters:")
    logger.info(f"  Grid Step: {best_params[0]:.1f}")
    logger.info(f"  Lot Multiplier: {best_params[1]:.1f}")
    logger.info(f"  TP Pips: {best_params[2]:.1f}")
    
    print("\nRecommended Config Update:")
    print(f"grid_step_points = {int(best_params[0])}")
    print(f"lot_multiplier = {best_params[1]:.1f}")
    print(f"global_tp = {best_params[2]:.1f}")

if __name__ == "__main__":
    main()
