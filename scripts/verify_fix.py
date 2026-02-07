
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

try:
    print("Verifying imports...")
    from src.trading_bot.strategies.grid_strategy import KalmanGridStrategy
    print("✅ grid_strategy imported successfully. SyntaxError fixed.")
except ImportError as e:
    print(f"❌ ImportError: {e}")
except SyntaxError as e:
    print(f"❌ SyntaxError: {e}")
except Exception as e:
    print(f"❌ Exception: {e}")
