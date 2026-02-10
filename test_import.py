try:
    import sys
    import os
    sys.path.append(os.getcwd())
    from src.trading_bot.ai import qwen_client
    print("Import successful")
except Exception as e:
    print(f"Import failed: {e}")
