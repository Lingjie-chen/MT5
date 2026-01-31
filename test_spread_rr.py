
import logging
from unittest.mock import MagicMock
import MetaTrader5 as mt5

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestSpreadRR")

# Mock MT5
mt5.initialize = MagicMock(return_value=True)
mt5.symbol_info_tick = MagicMock()
mt5.symbol_info = MagicMock()

class TestBot:
    def __init__(self):
        self.symbol = "XAUUSD"

    def test_rr_logic(self, strategy, final_signal, ask, bid):
        # Setup Mock Data
        mock_tick = MagicMock()
        mock_tick.ask = ask
        mock_tick.bid = bid
        mt5.symbol_info_tick.return_value = mock_tick
        
        mock_info = MagicMock()
        mock_info.spread = int((ask - bid) * 100) # Assuming 2 decimal points for simplicity
        mock_info.point = 0.01
        mt5.symbol_info.return_value = mock_info
        
        logger.info(f"\n--- Testing Signal: {final_signal} (Ask={ask}, Bid={bid}, Spread={ask-bid:.2f}) ---")

        # Copied Logic from main.py
        strength = float(strategy.get('confidence', 0))
        if strength <= 0: strength = 70
        
        reason = "Test Reason"
        
        if final_signal in ['buy', 'sell']:
             # 2. Check R:R Ratio (Including Spread Cost)
            exit_conds = strategy.get('exit_conditions', {})
            sl_p = exit_conds.get('sl_price', 0)
            tp_p = exit_conds.get('tp_price', 0)
            entry_p = 0
            
            tick = mt5.symbol_info_tick(self.symbol)
            symbol_info = mt5.symbol_info(self.symbol)
            
            if tick and symbol_info:
                real_spread = tick.ask - tick.bid
                
                # Entry Price Logic
                if final_signal == 'buy':
                    entry_p = tick.ask 
                elif final_signal == 'sell':
                    entry_p = tick.bid
                
                if sl_p > 0 and tp_p > 0 and entry_p > 0:
                    potential_profit = abs(tp_p - entry_p)
                    potential_loss = abs(entry_p - sl_p)
                    
                    if potential_loss > 0:
                        rr_ratio = potential_profit / potential_loss
                        
                        logger.info(f"Calc: Profit={potential_profit:.2f}, Loss={potential_loss:.2f}, RR={rr_ratio:.2f}")
                        
                        if rr_ratio < 1.5:
                            logger.info(f"⛔ 信号被过滤: R:R {rr_ratio:.2f} < 1.5 (TP:{tp_p}, SL:{sl_p}, Entry:{entry_p}, Spread:{real_spread:.5f})")
                            final_signal = 'hold'
                            reason = f"[Filter] Low R:R ({rr_ratio:.2f} < 1.5)"
                        else:
                            logger.info(f"✅ 信号通过: R:R {rr_ratio:.2f} >= 1.5 (Spread:{real_spread:.5f})")
                    else:
                        logger.warning("无法计算 R:R (SL距离为0)")
            else:
                logger.info("Missing Tick/Symbol Info")
                
        return final_signal

# Run Tests
bot = TestBot()

# Case 1: Standard Spread, Good RR
# Buy at 2001 (Ask), SL 1991 (Risk 10), TP 2021 (Reward 20) -> RR 2.0
# Bid 2000. Spread 1.0.
bot.test_rr_logic(
    {"confidence": 85, "exit_conditions": {"sl_price": 1991.0, "tp_price": 2021.0}}, 
    "buy", 
    ask=2001.0, 
    bid=2000.0
)

# Case 2: High Spread, Bad RR (due to entry price being worse)
# Spread 5.0! Ask 2005, Bid 2000.
# Signal wants to Buy. Entry at 2005.
# SL 1995 (Risk 10). TP 2015 (Reward 10). RR 1.0 -> FAIL
bot.test_rr_logic(
    {"confidence": 85, "exit_conditions": {"sl_price": 1995.0, "tp_price": 2015.0}}, 
    "buy", 
    ask=2005.0, 
    bid=2000.0
)
