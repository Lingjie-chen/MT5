import MetaTrader5 as mt5
import os
import threading
import logging
from dotenv import load_dotenv

# Configure Logging
logger = logging.getLogger("MT5Interface")

class MT5Interface:
    _instance = None
    _lock = threading.RLock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MT5Interface, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        load_dotenv()
        self.current_account_index = None
        self.lock = threading.RLock()
        self._initialized = True
        
        # Cache account configs
        self.accounts = {}
        self._load_accounts()

    def _load_accounts(self):
        """Load account configurations from environment variables"""
        # Support up to 5 accounts
        for i in range(1, 6):
            acc = os.getenv(f"MT5_ACCOUNT_{i}")
            if acc:
                self.accounts[i] = {
                    "login": int(acc),
                    "server": os.getenv(f"MT5_SERVER_{i}"),
                    "password": os.getenv(f"MT5_PASSWORD_{i}"),
                    "path": os.getenv(f"MT5_PATH_{i}")
                }
        logger.info(f"Loaded {len(self.accounts)} MT5 accounts configuration")

    def get_account_config(self, index):
        return self.accounts.get(index)

    def initialize_account(self, index):
        """Initialize a specific MT5 account"""
        if index not in self.accounts:
            logger.error(f"Account index {index} not found in configuration")
            return False

        config = self.accounts[index]
        
        # Check if already connected to this account
        if self.current_account_index == index:
            # Check if actually connected
            if mt5.terminal_info() is not None:
                return True
            
        # Shutdown previous connection
        mt5.shutdown()
        
        # Prepare init params
        init_params = {
            "login": config["login"],
            "server": config["server"],
            "password": config["password"]
        }
        if config["path"] and os.path.exists(config["path"]):
            init_params["path"] = config["path"]
            
        # Initialize
        if not mt5.initialize(**init_params):
            logger.error(f"Failed to initialize MT5 account {index}: {mt5.last_error()}")
            self.current_account_index = None
            return False
            
        self.current_account_index = index
        logger.info(f"Switched to MT5 Account {index} ({config['login']})")
        return True

    def use_account(self, index):
        """Context manager for using a specific account"""
        return MT5AccountContext(self, index)

class MT5AccountContext:
    def __init__(self, interface, account_index):
        self.interface = interface
        self.account_index = account_index

    def __enter__(self):
        self.interface.lock.acquire()
        try:
            if not self.interface.initialize_account(self.account_index):
                raise RuntimeError(f"Could not initialize MT5 account {self.account_index}")
        except Exception:
            self.interface.lock.release()
            raise
        return self.interface

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.interface.lock.release()
