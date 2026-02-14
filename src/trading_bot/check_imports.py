
import sys
import os

# Path setup similar to main.py
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path: sys.path.append(current_dir)
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path: sys.path.append(src_dir)

print(f"Checking imports in {current_dir}")
print(f"Source dir: {src_dir}")

try:
    import MetaTrader5 as mt5
    print("MetaTrader5 imported")
    from ai.ai_client_factory import AIClientFactory
    print("AIClientFactory imported")
    from data.mt5_data_processor import MT5DataProcessor
    print("MT5DataProcessor imported")
    from data.database_manager import DatabaseManager
    print("DatabaseManager imported")
    from strategies.grid_strategy import KalmanGridStrategy
    print("KalmanGridStrategy imported")
    from strategies.orb_strategy import GoldORBStrategy
    print("GoldORBStrategy imported")
    from analysis.smc_validator import SMCQualityValidator
    print("SMCQualityValidator imported")
    from position_engine.mt5_adapter import MT5RiskManager
    print("MT5RiskManager imported")
    from analysis.advanced_analysis import AdvancedMarketAnalysisAdapter
    print("AdvancedMarketAnalysisAdapter imported")
    from utils.file_watcher import FileWatcher
    print("FileWatcher imported")
    from utils.telegram_notifier import TelegramNotifier
    print("TelegramNotifier imported")
    
    print("All imports successful!")
except ImportError as e:
    print(f"Import failed: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
