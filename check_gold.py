
import MetaTrader5 as mt5

# Credentials from main.py (Account 1)
account = 89633982
server = "Ava-Real 1-MT5"
password = "Clj568741230#"

if not mt5.initialize(login=account, server=server, password=password):
    print(f"Init failed with specific credentials: {mt5.last_error()}")
    # Fallback
    if not mt5.initialize():
        print("Init failed with default")
        quit()
    else:
        print("Initialized with default (fallback)")
else:
    print(f"Initialized with Account {account}")

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
