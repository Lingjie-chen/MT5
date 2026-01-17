
import logging
import json
from robust_json_parser import safe_parse_or_default

# Setup logging
logging.basicConfig(level=logging.WARNING)

def test_unterminated_string():
    # Simulate a truncated JSON response with an unterminated string
    # "Unterminated string starting at: line 142 column 16 (char 3832)" usually means the string wasn't closed
    
    # Case 1: Simple truncated string
    bad_json_1 = '{"key": "value", "description": "This is a long description that got cut off...'
    
    # Case 2: Truncated inside a nested object
    bad_json_2 = '{"data": {"summary": "Start of summary", "details": "Unfinished'
    
    # Case 3: Unescaped newlines in string (common LLM issue)
    bad_json_3 = '{"key": "Line 1\nLine 2"}'
    
    print("--- Testing Bad JSON 1 (Truncated) ---")
    try:
        res1 = safe_parse_or_default(bad_json_1)
        print(f"Result 1: {res1}")
    except Exception as e:
        print(f"Error 1: {e}")

    print("\n--- Testing Bad JSON 2 (Nested Truncated) ---")
    try:
        res2 = safe_parse_or_default(bad_json_2)
        print(f"Result 2: {res2}")
    except Exception as e:
        print(f"Error 2: {e}")

    print("\n--- Testing Bad JSON 3 (Unescaped Newline) ---")
    try:
        res3 = safe_parse_or_default(bad_json_3)
        print(f"Result 3: {res3}")
    except Exception as e:
        print(f"Error 3: {e}")

if __name__ == "__main__":
    test_unterminated_string()
