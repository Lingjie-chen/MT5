
import sys
import os

# Add current directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print(f"Testing imports in main.py context. Sys.path: {sys.path[0]}")

try:
    from utils.file_watcher import FileWatcher
    print("Importing FileWatcher success")
except ImportError as e:
    print(f"Importing FileWatcher failed: {e}")

try:
    from ai.ai_client_factory import AIClientFactory
    print("Importing AIClientFactory success")
except ImportError as e:
    print(f"Importing AIClientFactory failed: {e}")

try:
    from data.database_manager import DatabaseManager
    print("Importing DatabaseManager success")
except ImportError as e:
    print(f"Importing DatabaseManager failed: {e}")
