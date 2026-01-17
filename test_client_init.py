
import os
import sys

# Add the current directory to sys.path so we can import gold.qwen_client
sys.path.append(os.getcwd())

try:
    from gold.qwen_client import QwenClient
    print("Successfully imported QwenClient")
    
    client = QwenClient(api_key="test_key")
    print("Successfully initialized QwenClient")
    
    # Check if _call_api uses the timeout logic (static analysis or just ensuring it exists)
    import inspect
    source = inspect.getsource(client._call_api)
    if "API_TIMEOUT" in source:
        print("Verified: API_TIMEOUT logic is present in _call_api")
    else:
        print("Warning: API_TIMEOUT logic not found in source")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
