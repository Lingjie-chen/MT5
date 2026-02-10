
import sys
import os

# Add src to path
sys.path.append(os.path.abspath("src"))

try:
    print("Checking main.py...")
    import trading_bot.main
    print("main.py OK")
except Exception as e:
    print(f"Error in main.py: {e}")

try:
    print("Checking qwen_client.py...")
    import trading_bot.ai.qwen_client
    print("qwen_client.py OK")
except Exception as e:
    print(f"Error in qwen_client.py: {e}")

try:
    print("Checking advanced_analysis.py...")
    import trading_bot.analysis.advanced_analysis
    print("advanced_analysis.py OK")
except Exception as e:
    print(f"Error in advanced_analysis.py: {e}")
