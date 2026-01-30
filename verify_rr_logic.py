
import sys
import os
import logging
from unittest.mock import MagicMock

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

import MetaTrader5 as mt5

try:
    from trading_bot.main import SymbolTrader
except ImportError:
    print("Failed to import SymbolTrader. Check path.")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestRR")

def test_rr_logic():
    print("\n[Test] Risk:Reward Ratio Logic (Min 1.2)")
    
    trader = SymbolTrader("GOLD")
    trader.db_manager = MagicMock()
    trader.latest_strategy = {}
    trader._send_order = MagicMock(return_value=True)
    trader.calculate_dynamic_lot = MagicMock(return_value=0.01)
    
    # Mock MT5 data for ATR calculation (if needed, though we force SL/TP)
    # We don't need real MT5 connection if we mock everything, but main.py imports it.
    # Assuming mt5 is mocked or initialized dummy.
    
    # Scenario 1: Valid Trade (R:R = 2.0)
    # Buy @ 2000, SL=1990 (Risk 10), TP=2020 (Reward 20) -> Ratio 2.0 -> Pass
    print("  Scenario 1: Valid Trade (R:R=2.0)")
    trader.execute_trade(
        "buy", 
        0.9, 
        {"sl_price": 1990.0, "tp_price": 2020.0}, # exit_params
        {"price": 2000.0}, # entry_params
        suggested_lot=0.01
    )
    
    if trader._send_order.called:
        print("  [PASS] Order sent for Valid R:R.")
    else:
        print("  [FAIL] Order BLOCKED for Valid R:R!")

    trader._send_order.reset_mock()
    
    # Scenario 2: Invalid Trade (R:R = 1.0)
    # Buy @ 2000, SL=1990 (Risk 10), TP=2010 (Reward 10) -> Ratio 1.0 -> Fail
    print("  Scenario 2: Invalid Trade (R:R=1.0 < 1.2)")
    trader.execute_trade(
        "buy", 
        0.9, 
        {"sl_price": 1990.0, "tp_price": 2010.0}, 
        {"price": 2000.0}, 
        suggested_lot=0.01
    )
    
    if not trader._send_order.called:
        print("  [PASS] Order correctly BLOCKED for Invalid R:R.")
    else:
        print("  [FAIL] Order SENT despite Invalid R:R!")

    trader._send_order.reset_mock()

    # Scenario 3: Sell Trade (R:R = 1.5)
    # Sell @ 2000, SL=2010 (Risk 10), TP=1985 (Reward 15) -> Ratio 1.5 -> Pass
    print("  Scenario 3: Sell Trade (R:R=1.5)")
    trader.execute_trade(
        "sell", 
        0.9, 
        {"sl_price": 2010.0, "tp_price": 1985.0}, 
        {"price": 2000.0}, 
        suggested_lot=0.01
    )
    
    if trader._send_order.called:
        print("  [PASS] Sell Order sent for Valid R:R.")
    else:
        print("  [FAIL] Sell Order BLOCKED for Valid R:R!")

    # Scenario 4: Parameter Extraction Test (SL/TP in entry_params)
    print("  Scenario 4: SL/TP Extraction from entry_params")
    trader._send_order.reset_mock()
    trader.execute_trade(
        "buy", 
        0.9, 
        {}, # Empty exit_params
        {"price": 2000.0, "sl": 1990.0, "tp": 2020.0}, # SL/TP here
        suggested_lot=0.01
    )
    
    if trader._send_order.called:
        # Verify args
        args, _ = trader._send_order.call_args
        # _send_order(type, price, sl, tp, ...)
        sl_arg = args[2]
        tp_arg = args[3]
        if sl_arg == 1990.0 and tp_arg == 2020.0:
            print("  [PASS] SL/TP correctly extracted from entry_params.")
        else:
            print(f"  [FAIL] SL/TP extraction failed. Got SL={sl_arg}, TP={tp_arg}")
    else:
        print("  [FAIL] Order not sent (Extraction might have failed causing R:R check fail or other error)")

if __name__ == "__main__":
    try:
        test_rr_logic()
    except Exception as e:
        print(f"Test crashed: {e}")
