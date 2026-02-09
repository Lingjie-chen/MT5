import numpy as np
from typing import Dict
import logging

logger = logging.getLogger("RLWeightOptimizer")

class RLWeightOptimizer:
    """
    Online Reinforcement Learning for Dynamic Weight Adjustment.
    Uses a simplified Multi-Armed Bandit (MAB) or Gradient approach to update 
    the weights of different signal sources (Qwen, SMC, CRT, etc.) based on realized performance.
    """
    
    def __init__(self, learning_rate: float = 0.05, decay: float = 0.99):
        self.learning_rate = learning_rate
        self.decay = decay
        self.weights = {
            "qwen": 1.5,
            "crt": 0.8,
            "smc": 1.1,
            "rvgi_cci": 0.6,
            "ema_ha": 0.9
        }
        self.history = {} # Store last signals to attribute rewards
        
    def update_weights(self, trade_result: Dict):
        """
        Update weights based on trade outcome.
        
        Args:
            trade_result: Dict with 'profit', 'signals_snapshot' (dict of what each source said)
        """
        profit = trade_result.get('profit', 0)
        snapshot = trade_result.get('signals_snapshot', {}) # e.g. {'qwen': 'buy', 'smc': 'neutral'}
        
        if not snapshot: return
        
        # Normalize Reward (-1 to 1 range approx)
        reward = np.tanh(profit / 100.0) 
        
        updated = False
        for source, signal in snapshot.items():
            if source not in self.weights: continue
            
            # Determine source contribution
            # If we Bought and Source said Buy -> Contribution +1
            # If we Bought and Source said Sell -> Contribution -1
            # If we Bought and Source said Neutral -> Contribution 0
            
            action = trade_result.get('action', '').upper() # BUY or SELL
            
            contribution = 0
            if action == 'BUY':
                if signal == 'buy': contribution = 1
                elif signal == 'sell': contribution = -1
            elif action == 'SELL':
                if signal == 'sell': contribution = 1
                elif signal == 'buy': contribution = -1
                
            # Update Rule: Weight = Weight + LR * Reward * Contribution
            # If Reward > 0 and Contribution > 0 (Correctly predicted win) -> Weight Increases
            # If Reward < 0 and Contribution > 0 (Predicted win but lost) -> Weight Decreases
            
            if contribution != 0:
                delta = self.learning_rate * reward * contribution
                self.weights[source] += delta
                # Clip weights to sane range (0.1 to 3.0)
                self.weights[source] = max(0.1, min(3.0, self.weights[source]))
                updated = True
                
        if updated:
            logger.info(f"RL Weights Updated: {self.weights}")
            
    def get_weights(self) -> Dict[str, float]:
        return self.weights
