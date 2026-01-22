
import MetaTrader5 as mt5
import sys

def check_mt5():
    if not mt5.initialize():
        print("initialize() failed")
        mt5.shutdown()
        return

    print(f"MT5 package version: {mt5.__version__}")
    print(f"MT5 terminal info: {mt5.terminal_info()}")
    print(f"MT5 version: {mt5.version()}")

    symbol = "GOLD"
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"Symbol '{symbol}' not found in Market Watch.")
        # Try to search for similar symbols
        all_symbols = mt5.symbols_get()
        if all_symbols:
            print("Available symbols containing 'GOLD' or 'XAU':")
            for s in all_symbols:
                if "GOLD" in s.name.upper() or "XAU" in s.name.upper():
                    print(f"- {s.name}")
    else:
        print(f"Symbol '{symbol}' found. Visible: {symbol_info.visible}")
        if not symbol_info.visible:
            print(f"Selecting '{symbol}' in Market Watch...")
            if not mt5.symbol_select(symbol, True):
                print(f"symbol_select({symbol}) failed, error code =", mt5.last_error())
            else:
                print(f"symbol_select({symbol}) succeeded")

    # Check timeframe
    try:
        tf = mt5.TIMEFRAME_M10
        print(f"TIMEFRAME_M10 constant exists: {tf}")
    except AttributeError:
        print("TIMEFRAME_M10 constant NOT found in mt5 module.")

    # Try to get rates
    if symbol_info and symbol_info.visible:
        print(f"Attempting to copy rates for {symbol} M10...")
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M10, 0, 500)
        if rates is None:
            print(f"copy_rates_from_pos failed, error code = {mt5.last_error()}")
        else:
            print(f"Successfully got {len(rates)} rates.")

    mt5.shutdown()

if __name__ == "__main__":
    check_mt5()
