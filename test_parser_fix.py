
import json
from src.trading_bot.ai.robust_json_parser import safe_parse_or_default

def test_parser():
    print("Testing robust_json_parser...")

    # Case 1: Normal input
    json_1 = '{"action": "buy", "position_size": 0.5}'
    res_1 = safe_parse_or_default(json_1, required_keys=["action", "position_size"])
    print(f"Case 1 (Normal): {res_1}")
    assert res_1['position_size'] == 0.5

    # Case 2: Explicit 0.0
    json_2 = '{"action": "buy", "position_size": 0.0}'
    res_2 = safe_parse_or_default(json_2, required_keys=["action", "position_size"])
    print(f"Case 2 (Explicit 0.0): {res_2}")
    assert res_2['position_size'] == 0.0

    # Case 3: Missing field (Should NOT be 0.0 anymore)
    json_3 = '{"action": "buy"}'
    res_3 = safe_parse_or_default(json_3, required_keys=["action", "position_size"])
    print(f"Case 3 (Missing): {res_3}")
    # After fix, position_size should NOT be in res_3
    if 'position_size' in res_3:
        print(f"FAIL: position_size present in Case 3: {res_3['position_size']}")
    else:
        print("PASS: position_size correctly missing in Case 3")

if __name__ == "__main__":
    test_parser()
