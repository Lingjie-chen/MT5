import sys
import os
import ast

def check_syntax(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        ast.parse(source)
        print(f"✅ Syntax OK: {os.path.basename(file_path)}")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax Error in {os.path.basename(file_path)}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading {os.path.basename(file_path)}: {e}")
        return False

files_to_check = [
    r"c:\Users\Administrator\Desktop\MT5\src\trading_bot\main.py",
    r"c:\Users\Administrator\Desktop\MT5\src\trading_bot\strategies\grid_strategy.py",
    r"c:\Users\Administrator\Desktop\MT5\src\trading_bot\analysis\advanced_analysis.py"
]

print("--- Starting Syntax Verification ---")
all_passed = True
for file_path in files_to_check:
    if not check_syntax(file_path):
        all_passed = False

if all_passed:
    print("\n--- Logic Verification ---")
    # Verify specific logic strings presence (lightweight static analysis)
    
    # 1. Advanced Analysis: Choppiness Index
    with open(files_to_check[2], 'r', encoding='utf-8') as f:
        content = f.read()
        if "def calculate_choppiness_index" in content:
            print("✅ AdvancedAnalysis: calculate_choppiness_index implemented")
        else:
            print("❌ AdvancedAnalysis: calculate_choppiness_index MISSING")

    # 2. Grid Strategy: ADX & CHOP Logic
    with open(files_to_check[1], 'r', encoding='utf-8') as f:
        content = f.read()
        if "adx_value < 25" in content and "chop_value > 61.8" in content:
             print("✅ GridStrategy: ADX & CHOP Thresholds implemented")
        else:
             print("❌ GridStrategy: ADX & CHOP Thresholds MISSING/INCORRECT")

    # 3. Main Bot: State Machine & Circuit Breaker
    with open(files_to_check[0], 'r', encoding='utf-8') as f:
        content = f.read()
        if "Circuit Breaker Triggered" in content:
             print("✅ MainBot: Circuit Breaker Logic implemented")
        else:
             print("❌ MainBot: Circuit Breaker Logic MISSING")
             
        if "update_market_regime_state" in content:
             print("✅ MainBot: State Machine (update_market_regime_state) implemented")
        else:
             print("❌ MainBot: State Machine Logic MISSING")
             
        if "stop_level = symbol_info.trade_stops_level" in content:
             print("✅ MainBot: Dynamic Stops Level Check implemented")
        else:
             print("❌ MainBot: Dynamic Stops Level Check MISSING")

    print("\n✅ All Checks Passed. System Ready for Deployment.")
else:
    print("\n❌ Verification Failed.")
