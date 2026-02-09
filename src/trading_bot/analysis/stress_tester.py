import numpy as np
import pandas as pd
from typing import List, Dict
import logging

logger = logging.getLogger("StressTester")

class StrategyStressTester:
    """
    Monte Carlo Stress Tester for Trading Strategies.
    Evaluates strategy robustness by simulating variations in market conditions.
    """
    
    def __init__(self, num_simulations: int = 1000, confidence_level: float = 0.95):
        self.num_simulations = num_simulations
        self.confidence_level = confidence_level
        
    def run_stress_test(self, trades: List[Dict]) -> Dict:
        """
        Run Monte Carlo simulation on trade returns to estimate risk metrics.
        
        Args:
            trades: List of trade dicts with 'profit' key.
            
        Returns:
            Dict containing stress test scores (0-100) and risk metrics.
        """
        if not trades or len(trades) < 20:
            return {"score": 50, "reason": "Insufficient Data", "var_95": 0}
            
        profits = [t['profit'] for t in trades]
        returns = np.array(profits)
        
        # Monte Carlo Simulation
        simulated_drawdowns = []
        simulated_profits = []
        
        for _ in range(self.num_simulations):
            # Bootstrap resampling (shuffle returns) to break time-dependence
            # This tests if the strategy relies purely on luck/sequence
            shuffled_returns = np.random.choice(returns, size=len(returns), replace=True)
            cumulative = np.cumsum(shuffled_returns)
            
            # Calculate Max Drawdown for this path
            peak = np.maximum.accumulate(cumulative)
            drawdown = peak - cumulative
            max_dd = np.max(drawdown) if len(drawdown) > 0 else 0
            
            simulated_drawdowns.append(max_dd)
            simulated_profits.append(cumulative[-1])
            
        # Analyze Results
        avg_dd = np.mean(simulated_drawdowns)
        worst_case_dd = np.percentile(simulated_drawdowns, 95) # 95th percentile risk
        prob_loss = np.mean(np.array(simulated_profits) < 0)
        
        # Calculate Robustness Score (0-100)
        # Higher score = More robust
        # Factors: Probability of Loss (lower is better), Drawdown Stability
        
        score = 100
        
        # Penalize for high probability of loss
        score -= (prob_loss * 100)
        
        # Penalize for extreme drawdowns relative to average profit
        avg_profit = np.mean(profits) if len(profits) > 0 else 0
        if avg_profit > 0:
            risk_ratio = avg_dd / (avg_profit * len(profits)) # DD relative to total profit
            if risk_ratio > 0.5: score -= 20
            if risk_ratio > 1.0: score -= 30
        else:
            score -= 50 # Losing strategy
            
        return {
            "score": max(0, min(100, score)),
            "simulations": self.num_simulations,
            "avg_drawdown": avg_dd,
            "worst_case_dd_95": worst_case_dd,
            "probability_of_loss": prob_loss
        }
