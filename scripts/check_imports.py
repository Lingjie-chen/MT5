
import sys
import os
from unittest.mock import MagicMock

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

# Mock MT5
sys.modules['MetaTrader5'] = MagicMock()

print("Attempting to import trading_bot.main...")
try:
    from trading_bot import main
    print("✅ Successfully imported trading_bot.main")
except ImportError as e:
    print(f"❌ Failed to import trading_bot.main: {e}")
except NameError as e:
    print(f"❌ NameError during import: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
