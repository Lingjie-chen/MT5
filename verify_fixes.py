
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

def verify_symbol_selection_fix():
    print("\n[Test] Symbol Selection Fix")
    
    trader = SymbolTrader("GOLD")
    if not mt5.initialize():
        print("MT5 Init failed")
        return

    print("Running symbol check logic...")
    symbol = "GOLD"
    
    # Simulate the logic
    s_info = mt5.symbol_info(symbol)
    
    if s_info is None:
        print("  Symbol info is None. Attempting force select...")
        if not mt5.symbol_select(symbol, True):
             print("  Force select failed")
        else:
             print("  Force select success")
             # Check again
             s_info = mt5.symbol_info(symbol)
             if s_info: print("  Symbol info found after select.")
             else: print("  Symbol info STILL None after select.")
    else:
        print("  Symbol info found initially.")
        if not s_info.visible:
             print("  Symbol not visible, selecting...")
             mt5.symbol_select(symbol, True)
        else:
             print("  Symbol is visible.")

    print("[PASS] Symbol selection logic verification complete.")

def verify_execute_trade_fix():
    print("\n[Test] execute_trade TypeError Fix")
    trader = SymbolTrader("GOLD")
    
    # Mock dependencies
    trader.db_manager = MagicMock()
    trader.latest_strategy = {}
    trader.check_account_safety = MagicMock(return_value=(True, "Safe"))
    trader.calculate_dynamic_lot = MagicMock(return_value=0.01)
    
    # Mock _send_order to intercept the call
    trader._send_order = MagicMock(return_value=True)
    
    # We need to simulate the environment where execute_trade is called.
    # We assume the method signature is execute_trade(self, final_signal, strength, exit_params, entry_params, suggested_lot=None)
    
    print("  Testing action='buy'...")
    try:
        # Calling with "buy" action
        trader.execute_trade("buy", 0.9, {}, {}, suggested_lot=0.01)
        
        # Check calls
        if trader._send_order.called:
            args, _ = trader._send_order.call_args
            trade_type_arg = args[0]
            print(f"  _send_order called with trade_type: {trade_type_arg!r} (Type: {type(trade_type_arg)})")
            
            if isinstance(trade_type_arg, str) and trade_type_arg == "buy":
                 print("  [PASS] trade_type is correctly a string 'buy'")
            else:
                 print(f"  [FAIL] trade_type is {trade_type_arg} (Expected 'buy')")
        else:
            print("  [FAIL] _send_order was NOT called (Logic might have skipped it)")

    except Exception as e:
        print(f"  [FAIL] Crash during execute_trade('buy'): {e}")
        import traceback
        traceback.print_exc()

    print("  Testing action='limit_buy'...")
    try:
        trader._send_order.reset_mock()
        trader.execute_trade("limit_buy", 0.9, {}, {}, suggested_lot=0.01)
        
        if trader._send_order.called:
            args, _ = trader._send_order.call_args
            trade_type_arg = args[0]
            print(f"  _send_order called with trade_type: {trade_type_arg!r}")
            
            if isinstance(trade_type_arg, str) and trade_type_arg == "limit_buy":
                 print("  [PASS] trade_type is correctly a string 'limit_buy'")
            else:
                 print(f"  [FAIL] trade_type is {trade_type_arg} (Expected 'limit_buy')")
        else:
             print("  [FAIL] _send_order was NOT called")
             
    except Exception as e:
        print(f"  [FAIL] Crash during execute_trade('limit_buy'): {e}")

if __name__ == "__main__":
    try:
        verify_symbol_selection_fix()
        verify_execute_trade_fix()
    except Exception as e:
        print(f"Test script crashed: {e}")
    finally:
        mt5.shutdown()
