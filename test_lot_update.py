
import logging
from unittest.mock import MagicMock
import MetaTrader5 as mt5

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestLotSize")

# Mock MT5
mt5.initialize = MagicMock(return_value=True)
mt5.symbol_info = MagicMock()
mt5.symbol_info.return_value.volume_step = 0.01
mt5.symbol_info.return_value.volume_min = 0.01
mt5.symbol_info.return_value.volume_max = 100.0

# Mock other components
class MockGridStrategy:
    def __init__(self):
        self.lot = 0.01

class MockQwenClient:
    def optimize_strategy_logic(self, *args, **kwargs):
        return {
            "action": "buy",
            "position_size": 0.55,  # AI suggests 0.55
            "reason": "Test Logic",
            "exit_conditions": {"tp_price": 2000.0, "sl_price": 1900.0}
        }

# Simplified Bot Class for Testing
class TestBot:
    def __init__(self):
        self.symbol = "XAUUSD"
        self.lot_size = 0.01
        self.grid_strategy = MockGridStrategy()
        self.qwen_client = MockQwenClient()
        self.latest_strategy = {}

    def test_logic(self):
        # Simulate the logic in process_tick
        strategy = self.qwen_client.optimize_strategy_logic()
        
        # Copied from main.py logic
        if 'position_size' in strategy:
            try:
                qwen_lot = float(strategy['position_size'])
                if qwen_lot > 0:
                    # [FIX] Validate against Symbol Info (Min/Max/Step)
                    symbol_info = mt5.symbol_info(self.symbol)
                    if symbol_info:
                        step = symbol_info.volume_step
                        min_vol = symbol_info.volume_min
                        max_vol = symbol_info.volume_max
                        
                        # 1. Normalize to step
                        if step > 0:
                            qwen_lot = round(qwen_lot / step) * step
                            qwen_lot = round(qwen_lot, 2) # Safety round
                        
                        # 2. Clamp to limits
                        if qwen_lot < min_vol:
                            logger.warning(f"Qwen Lot {qwen_lot} < Min {min_vol}. Adjusting to Min.")
                            qwen_lot = min_vol
                        elif qwen_lot > max_vol:
                            qwen_lot = max_vol
                    
                    self.lot_size = qwen_lot
                    # Update grid strategy lot size too for consistency
                    if hasattr(self, 'grid_strategy'):
                        self.grid_strategy.lot = qwen_lot
                    logger.info(f"Updated lot size from Qwen: {self.lot_size}")
            except Exception as e:
                logger.error(f"Failed to update lot size: {e}")

# Run Test
bot = TestBot()
bot.test_logic()

if bot.lot_size == 0.55:
    print("SUCCESS: Lot size updated to 0.55")
else:
    print(f"FAILURE: Lot size is {bot.lot_size}, expected 0.55")
