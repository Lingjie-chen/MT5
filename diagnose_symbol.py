
import MetaTrader5 as mt5
import math
import sys

def analyze_symbol(symbol_name):
    if not mt5.initialize():
        print("MT5 Init Failed")
        return

    info = mt5.symbol_info(symbol_name)
    if not info:
        print(f"Symbol {symbol_name} not found")
        return

    print(f"Symbol: {info.name}")
    print(f"Volume Min: {info.volume_min}")
    print(f"Volume Max: {info.volume_max}")
    print(f"Volume Step: {info.volume_step}")
    print(f"Digits: {info.digits}")
    
    step = info.volume_step
    if step > 0:
        decimals = max(0, int(-math.log10(step)))
        print(f"Calculated Decimals from Step: {decimals}")
        
        # Test Normalization Logic
        test_lots = [0.01, 0.1, 0.123, 1.0, 1.5, 0.001]
        for lot in test_lots:
            steps = round(lot / step)
            norm_lot = steps * step
            norm_lot = round(norm_lot, decimals)
            print(f"  Test Lot {lot} -> {norm_lot}")

    mt5.shutdown()

if __name__ == "__main__":
    symbol = "GOLD"
    if len(sys.argv) > 1: symbol = sys.argv[1]
    analyze_symbol(symbol)
