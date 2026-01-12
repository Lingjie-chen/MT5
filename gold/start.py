import logging
import json
import sys
import os

# Ensure the package can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from gold.qwen_client import QwenClient, RoleBasedAnalysisSystem, CustomJSONEncoder, main
except ImportError:
    # Fallback for direct execution
    from qwen_client import QwenClient, RoleBasedAnalysisSystem, CustomJSONEncoder, main

if __name__ == "__main__":
    # This entry point currently runs the test harness defined in qwen_client.py
    # If a real trading loop is implemented, it should be called here instead.
    logging.info("Starting Gold/Multi-Asset Analysis System...")
    main()
