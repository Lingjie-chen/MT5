
import MetaTrader5 as mt5
import time

def diagnose():
    if not mt5.initialize():
        print(f"MT5 Init Failed: {mt5.last_error()}")
        return

    print(f"Terminal Info: {mt5.terminal_info()}")
    print(f"Account Info: {mt5.account_info()}")
    
    symbol_name = "GOLD"
    s_info = mt5.symbol_info(symbol_name)
    
    if s_info is None:
        print(f"Symbol '{symbol_name}' NOT FOUND via symbol_info()")
        # Try fuzzy search
        print("Searching for similar symbols...")
        symbols = mt5.symbols_get()
        for s in symbols:
            if "GOLD" in s.name or "XAU" in s.name:
                print(f"Found match: {s.name}, Path: {s.path}, Visible: {s.visible}")
    else:
        print(f"Symbol '{symbol_name}' FOUND.")
        print(f"  Path: {s_info.path}")
        print(f"  Visible: {s_info.visible}")
        print(f"  Selectable: {s_info.select}")
        print(f"  Trade Mode: {s_info.trade_mode} (0=Disabled, 1=LongOnly, 2=ShortOnly, 3=CloseOnly, 4=Full)")
        
        if not s_info.visible:
            print("Attempting to select (make visible)...")
            if mt5.symbol_select(symbol_name, True):
                print("  Selection SUCCESS")
            else:
                err = mt5.last_error()
                print(f"  Selection FAILED. Error Code: {err}")
        else:
            print("Symbol is already visible.")
            # Try to re-select just to test
            if mt5.symbol_select(symbol_name, True):
                print("  Re-selection SUCCESS")
            else:
                err = mt5.last_error()
                print(f"  Re-selection FAILED. Error Code: {err}")

    # Check Market Watch Count
    visible_symbols = mt5.symbols_get(group="*", selected=True) # group="*" might not work for selected, use loop?
    # Actually symbols_get() returns all. symbols_get(selected=True) returns selected.
    # Note: symbols_get only accepts `group` argument in some versions, or `selected` keyword?
    # Let's try getting all and filtering.
    # Actually mt5.symbols_total() returns count in market watch? No.
    
    print("Counting visible symbols...")
    count = 0
    try:
        all_selected = mt5.symbols_get() # This gets all available? No, usually all.
        # mt5.symbols_total() -> returns number of all symbols.
        # To get visible, we loop? No that's slow (thousands).
        # mt5.symbols_get() without args returns all symbols in Market Watch? 
        # No, doc says: symbols_get(group="*") returns all symbols.
        # Let's try checking a few.
        pass
    except Exception as e:
        print(f"Error counting: {e}")

    mt5.shutdown()

if __name__ == "__main__":
    diagnose()
