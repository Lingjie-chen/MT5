
import MetaTrader5 as mt5

if not mt5.initialize():
    print("Init failed")
    quit()

symbol_info = mt5.symbol_info("GOLD")
if symbol_info:
    print(f"Symbol found: {symbol_info.name}")
    print(f"Path: {symbol_info.path}")
    print(f"Visible: {symbol_info.visible}")
    
    # Try to select it
    if mt5.symbol_select("GOLD", True):
        print("Selected successfully")
    else:
        print("Selection failed")
else:
    print("Symbol 'GOLD' not found via symbol_info")

# Check XAUUSD just in case
symbol_info_xau = mt5.symbol_info("XAUUSD")
if symbol_info_xau:
    print(f"Symbol found: {symbol_info_xau.name}")
else:
    print("Symbol 'XAUUSD' not found")

mt5.shutdown()
