
import logging
from unittest.mock import MagicMock
import MetaTrader5 as mt5

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestFilters")

# Mock MT5
mt5.initialize = MagicMock(return_value=True)
mt5.symbol_info_tick = MagicMock()

# Mock Tick Data (Price = 2000.0)
mock_tick = MagicMock()
mock_tick.ask = 2000.0
mock_tick.bid = 1999.0 # Spread 1.0
mt5.symbol_info_tick.return_value = mock_tick

class TestBot:
    def __init__(self):
        self.symbol = "XAUUSD"
    
    def test_filter_logic(self, strategy, final_signal):
        logger.info(f"Testing Signal: {final_signal} with Strategy: {strategy}")
        
        # Copied Logic from main.py
        strength = float(strategy.get('confidence', 0))
        if strength <= 0: strength = 70 # Default fallback
        
        reason = "Initial Reason"
        
        if final_signal in ['buy', 'sell']:
            # 1. Check Strength
            if strength < 80:
                logger.info(f"⛔ 信号被过滤: Strength {strength:.1f} < 80")
                final_signal = 'hold'
                reason = f"[Filter] Low Strength ({strength:.1f} < 80)"
            
            # 2. Check R:R Ratio
            else:
                exit_conds = strategy.get('exit_conditions', {})
                sl_p = exit_conds.get('sl_price', 0)
                tp_p = exit_conds.get('tp_price', 0)
                entry_p = 0
                
                tick = mt5.symbol_info_tick(self.symbol)
                if tick:
                    entry_p = tick.ask if final_signal == 'buy' else tick.bid
                
                if sl_p > 0 and tp_p > 0 and entry_p > 0:
                    potential_profit = abs(tp_p - entry_p)
                    potential_loss = abs(entry_p - sl_p)
                    
                    if potential_loss > 0:
                        rr_ratio = potential_profit / potential_loss
                        if rr_ratio < 1.5:
                            logger.info(f"⛔ 信号被过滤: R:R {rr_ratio:.2f} < 1.5 (TP:{tp_p}, SL:{sl_p}, Entry:{entry_p})")
                            final_signal = 'hold'
                            reason = f"[Filter] Low R:R ({rr_ratio:.2f} < 1.5)"
                        else:
                            logger.info(f"✅ 信号通过: R:R {rr_ratio:.2f} >= 1.5")
                    else:
                        logger.warning("无法计算 R:R (SL距离为0)")
                else:
                    logger.info("⛔ 信号被过滤: 缺失有效的 SL/TP 价格")
                    final_signal = 'hold'
                    reason = f"[Filter] Missing SL/TP"

        return final_signal, reason

# Run Tests
bot = TestBot()

print("\n--- Test Case 1: Low Confidence (70) ---")
res1 = bot.test_filter_logic({"confidence": 70, "exit_conditions": {"sl_price": 1990, "tp_price": 2020}}, "buy")
print(f"Result: {res1[0]} (Expected: hold)")

print("\n--- Test Case 2: High Confidence (85) but Low RR (1.0) ---")
# Buy at 2000, SL 1990 (Risk 10), TP 2010 (Reward 10) -> RR 1.0
res2 = bot.test_filter_logic({"confidence": 85, "exit_conditions": {"sl_price": 1990, "tp_price": 2010}}, "buy")
print(f"Result: {res2[0]} (Expected: hold)")

print("\n--- Test Case 3: High Confidence (85) and High RR (2.0) ---")
# Buy at 2000, SL 1990 (Risk 10), TP 2020 (Reward 20) -> RR 2.0
res3 = bot.test_filter_logic({"confidence": 85, "exit_conditions": {"sl_price": 1990, "tp_price": 2020}}, "buy")
print(f"Result: {res3[0]} (Expected: buy)")

print("\n--- Test Case 4: Missing SL/TP ---")
res4 = bot.test_filter_logic({"confidence": 90, "exit_conditions": {}}, "buy")
print(f"Result: {res4[0]} (Expected: hold)")
