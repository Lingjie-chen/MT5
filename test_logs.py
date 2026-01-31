
import logging
from unittest.mock import MagicMock
import MetaTrader5 as mt5

# Configure logging to capture output
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestLogBehavior")

# Mock MT5
mt5.symbol_info = MagicMock()
mt5.symbol_info.return_value.volume_step = 0.01
mt5.symbol_info.return_value.volume_min = 0.01
mt5.symbol_info.return_value.volume_max = 100.0

class TestBot:
    def __init__(self):
        self.symbol = "XAUUSD"
        self.lot_size = 0.01
    
    def test_log_logic(self, strategy):
        action = strategy.get('action', 'neutral').lower()
        logger.info(f"\n--- Testing Action: {action.upper()} ---")
        
        # Copied Logic from main.py (simplified)
        if 'position_size' in strategy:
            try:
                qwen_lot = float(strategy['position_size'])
                if qwen_lot > 0:
                    # Mock Symbol Info Logic
                    step = 0.01
                    min_vol = 0.01
                    max_vol = 100.0
                    
                    if step > 0:
                        qwen_lot = round(qwen_lot / step) * step
                        qwen_lot = round(qwen_lot, 2)
                    
                    self.lot_size = qwen_lot
                    
                    # LOGGING LOGIC TO TEST
                    temp_action = strategy.get('action', 'neutral').lower()
                    if temp_action not in ['hold', 'wait', 'close', 'neutral']:
                        logger.info(f"[LOG] Updated lot size from Qwen: {self.lot_size}")
                    else:
                        logger.info(f"[SUPPRESSED] Lot size log suppressed for {temp_action}")
                        
            except Exception as e:
                logger.error(f"Error: {e}")

        # Final Decision Logic
        final_signal = "neutral"
        if action == 'wait': final_signal = "wait"
        elif action == 'hold': final_signal = "hold"
        elif action == 'buy': final_signal = "buy"
        
        display_signal = final_signal.upper()
        if final_signal == 'wait':
            display_signal = "WAIT (不开仓)"
        elif final_signal == 'hold':
            display_signal = "HOLD (保持仓位)"

        logger.info(f"AI 最终决定 (Qwen): {display_signal}")

# Run Tests
bot = TestBot()

# Case 1: WAIT
bot.test_log_logic({"action": "wait", "position_size": 0.5})

# Case 2: HOLD
bot.test_log_logic({"action": "hold", "position_size": 0.5})

# Case 3: BUY
bot.test_log_logic({"action": "buy", "position_size": 0.5})
