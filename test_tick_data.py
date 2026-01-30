
import MetaTrader5 as mt5
import time
import sys

def test_tick_retrieval(symbol="GOLD"):
    print(f"Initializing MT5...")
    if not mt5.initialize():
        print(f"initialize() failed, error code = {mt5.last_error()}")
        return

    print(f"Attempting to select symbol: {symbol}")
    
    # Try to check visibility first
    s_info = mt5.symbol_info(symbol)
    if s_info is None:
        print(f"symbol_info({symbol}) returned None. Attempting to select...")
        if not mt5.symbol_select(symbol, True):
             print(f"symbol_select({symbol}) failed, error code = {mt5.last_error()}")
             mt5.shutdown()
             return
    elif not s_info.visible:
        print(f"Symbol {symbol} is not visible. Attempting to select...")
        if not mt5.symbol_select(symbol, True):
             print(f"symbol_select({symbol}) failed, error code = {mt5.last_error()}")
             mt5.shutdown()
             return

    # Retry loop for tick data
    max_retries = 3
    for i in range(max_retries):
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            print(f"Attempt {i+1}: symbol_info_tick({symbol}) returned None. Error code = {mt5.last_error()}")
            time.sleep(1)
        else:
            print(f"Successfully retrieved tick data for {symbol}:")
            print(f"  Time: {tick.time}")
            print(f"  Bid: {tick.bid}")
            print(f"  Ask: {tick.ask}")
            print(f"  Last: {tick.last}")
            print(f"  Volume: {tick.volume}")
            mt5.shutdown()
            return

    print("Failed to retrieve tick data after retries.")
    mt5.shutdown()

if __name__ == "__main__":
    target_symbol = "GOLD"
    if len(sys.argv) > 1:
        target_symbol = sys.argv[1]
    test_tick_retrieval(target_symbol)
