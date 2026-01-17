
import logging
import json
from robust_json_parser import safe_parse_or_default

# Setup logging
logging.basicConfig(level=logging.WARNING)

def test_logic():
    # Simulate LLM returning a list instead of a dict, wrapped in markdown
    llm_response = """
```json
    [
        {
            "action": "buy",
            "entry_conditions": {"limit_price": 2000.0},
            "exit_conditions": {"sl_price": 1990.0, "tp_price": 2020.0},
            "position_management": {},
            "position_size": 0.1,
            "strategy_rationale": "Test",
            "telegram_report": "Test"
        }
    ]
```
    """
    
    fallback_decision = {"action": "fallback"}
    
    print("Testing with list response...")
    trading_decision = safe_parse_or_default(
        llm_response,
        fallback=fallback_decision
    )
    
    print(f"Type of trading_decision: {type(trading_decision)}")
    print(f"Value: {trading_decision}")
    
    if not isinstance(trading_decision, dict):
        print("WARNING: Result is not a dict!")
        # This matches the logic in qwen_client.py
        trading_decision = fallback_decision
        print(f"Fallback used: {trading_decision}")
    else:
        print("Result is a dict.")

if __name__ == "__main__":
    test_logic()
