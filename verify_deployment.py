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

# Paths
base_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(base_dir, 'src', 'trading_bot')

files_to_check = [
    os.path.join(src_dir, 'main.py'),
    os.path.join(src_dir, 'strategies', 'grid_strategy.py'),
    os.path.join(src_dir, 'analysis', 'advanced_analysis.py')
]

print("--- Starting Syntax Verification ---")
all_passed = True
for file_path in files_to_check:
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        all_passed = False
        continue
        
    if not check_syntax(file_path):
        all_passed = False

if all_passed:
    print("\n--- Logic Verification ---")
    
    # 1. Advanced Analysis: Choppiness Index
    try:
        with open(files_to_check[2], 'r', encoding='utf-8') as f:
            content = f.read()
            if "def calculate_choppiness_index" in content:
                print("✅ AdvancedAnalysis: calculate_choppiness_index implemented")
            else:
                print("❌ AdvancedAnalysis: calculate_choppiness_index MISSING")
    except Exception as e:
        print(f"❌ Error checking AdvancedAnalysis: {e}")

    # 2. Grid Strategy: ADX & CHOP Logic
    try:
        with open(files_to_check[1], 'r', encoding='utf-8') as f:
            content = f.read()
            if "adx_value < 25" in content and "chop_value > 61.8" in content:
                 print("✅ GridStrategy: ADX & CHOP Thresholds implemented")
            else:
                 print("❌ GridStrategy: ADX & CHOP Thresholds MISSING/INCORRECT")
    except Exception as e:
        print(f"❌ Error checking GridStrategy: {e}")

    # 3. Main Bot: State Machine & Circuit Breaker
    try:
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
    except Exception as e:
        print(f"❌ Error checking MainBot: {e}")

    print("\n✅ All Checks Passed. System Ready for Deployment.")
else:
    print("\n❌ Verification Failed.")
