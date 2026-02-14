import sys
import os
import logging

# Add src to path
current_dir = os.getcwd()
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

print(f"Python Path: {sys.path}")

try:
    from trading_bot.ai.qwen_client import QwenClient
    
    print("Initializing QwenClient...")
    # Suppress logging for cleaner output
    logging.basicConfig(level=logging.ERROR)
    
    client = QwenClient(api_key="dummy_key")
    
    print("Testing _get_system_prompt('XAUUSD')...")
    # This method triggers the f-string construction and file loading
    prompt = client._get_system_prompt("XAUUSD")
    
    print(f"Success! Prompt generated. Length: {len(prompt)}")
    
    # 1. Verify Strategy Rules Loading
    # We look for a unique string from the new strategy_rules.md content
    target_rule_snippet = "大模型集成分析系统"
    if target_rule_snippet in prompt:
        print("✅ Strategy Rules loaded successfully (Path fix confirmed).")
    else:
        print("❌ WARNING: Strategy Rules content NOT found in prompt (Path fix might be wrong).")
        # Print path logic debug
        script_dir = os.path.dirname(os.path.abspath(client.__class__.__module__))
        print(f"Client Module Dir: {script_dir}")
        
    # 2. Verify F-String Formatting
    # We check if the JSON example is correctly formatted (single braces in output)
    target_json_snippet = '"risk_metrics": {'
    if target_json_snippet in prompt:
        print("✅ Risk Metrics JSON format looks correct (F-string fix confirmed).")
    else:
        print("❌ WARNING: Risk Metrics JSON format mismatch.")
        
except ValueError as e:
    print(f"❌ FAILED with ValueError (Likely F-string issue): {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ FAILED with Exception: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
