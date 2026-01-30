
import MetaTrader5 as mt5
import os
from dotenv import load_dotenv

load_dotenv()

if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

# Search for symbols with "GOLD" or "XAU"
symbols_gold = mt5.symbols_get(pattern="*GOLD*")
symbols_xau = mt5.symbols_get(pattern="*XAU*")

print("Symbols matching *GOLD*:")
if symbols_gold:
    for s in symbols_gold:
        print(s.name)
else:
    print("None")

print("\nSymbols matching *XAU*:")
if symbols_xau:
    for s in symbols_xau:
        print(s.name)
else:
    print("None")

mt5.shutdown()
