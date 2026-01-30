
import sys
import os
from unittest.mock import MagicMock

# Add src to path
sys.path.append(os.path.abspath("src"))

# Mock MT5
sys.modules["MetaTrader5"] = MagicMock()

try:
    from trading_bot.main import SymbolTrader
    print("Successfully imported SymbolTrader from trading_bot.main")
except Exception as e:
    print(f"Failed to import: {e}")
    sys.exit(1)
