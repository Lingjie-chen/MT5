import time
import sys
import os
import logging
import threading
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from file_watcher import FileWatcher

# Try importing MetaTrader5
try:
    import MetaTrader5 as mt5
except ImportError:
    print("Error: MetaTrader5 module not found.")
    sys.exit(1)

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('windows_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("WindowsBot")

# Load Environment Variables
load_dotenv()

# Add current directory to sys.path to ensure local imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import Local Modules
try:
    from .ai_client_factory import AIClientFactory
    from .mt5_data_processor import MT5DataProcessor
    from .database_manager import DatabaseManager
    from .optimization import WOAm, TETA
    from .advanced_analysis import (
        AdvancedMarketAnalysis, AdvancedMarketAnalysisAdapter, SMCAnalyzer, 
        CRTAnalyzer, MTFAnalyzer
    )
    from .grid_strategy import KalmanGridStrategy
except ImportError:
    # Fallback for direct script execution
    try:
        from ai_client_factory import AIClientFactory
        from mt5_data_processor import MT5DataProcessor
        from database_manager import DatabaseManager
        from optimization import WOAm, TETA
        from advanced_analysis import (
            AdvancedMarketAnalysis, AdvancedMarketAnalysisAdapter, SMCAnalyzer, 
            CRTAnalyzer, MTFAnalyzer
        )
        from grid_strategy import KalmanGridStrategy
    except ImportError as e:
        logger.error(f"Failed to import modules: {e}")
        sys.exit(1)


# Imports for strategies
try:
    from strategies.llm_strategy import SymbolTrader
    from strategies.martingale import MartingaleStrategy
except ImportError:
    # Fallback if run from different context
    from strategies.llm_strategy import SymbolTrader
    from strategies.martingale import MartingaleStrategy

class MultiSymbolBot:
    def __init__(self, symbols, timeframe=mt5.TIMEFRAME_M15):
        self.symbols = symbols
        self.timeframe = timeframe
        self.traders = []
        self.is_running = False
        self.watcher = None

    def initialize_mt5(self, account_index=1):
        """Global MT5 Initialization"""
        # Account Configuration
        if account_index == 2:
             # Exness Account
             account = 232809484
             server = "Exness-MT5Real5"
             password = "Clj568741230#"
        else:
             # Default to Ava (Account 1)
             account = 89633982
             server = "Ava-Real 1-MT5"
             password = "Clj568741230#"
        
        logger.info(f"Connecting to MT5 Account {account_index}: {account} on {server}")
        
        # Initialize MT5
        if not mt5.initialize(login=account, server=server, password=password):
            err_code = mt5.last_error()
            logger.error(f"MT5 初始化失败 (Account {account_index}), 错误码: {err_code}")
            
            # Fallback: Try initialize without credentials (uses last logged in account in Terminal)
            if not mt5.initialize():
                logger.error("MT5 默认初始化也失败")
                return False
        
        # Check if login successful (login matches)
        current_login = mt5.account_info().login
        if current_login != account:
             logger.warning(f"⚠️ 登录账户 ({current_login}) 与配置账户 ({account}) 不一致！")
             logger.warning("请确保 MT5 终端已登录正确账户，或使用多个终端实例。")
             
        # Check algo trading status
        term_info = mt5.terminal_info()
        if not term_info.trade_allowed:
            logger.warning("⚠️ 警告: 终端 '自动交易' (Algo Trading) 未开启！")
            
        logger.info(f"MT5 全局初始化成功，当前登录账户: {current_login}")
        return True

    def _resolve_symbol(self, base_symbol):
        """
        自动识别不同平台的交易品种名称 (Exness/Ava/etc.)
        例如: GOLD -> XAUUSDm, EURUSD -> EURUSDm
        """
        # Handle User Typos or Aliases
        base_upper = base_symbol.upper()
        if base_upper == "XUAUSD" or base_upper == "XUAUSDM":
             base_upper = "XAUUSD"
        
        # 1. 尝试直接匹配
        if mt5.symbol_info(base_upper):
            return base_upper
            
        # 2. 常见变体映射
        variants = []
        
        # 针对特定品种的已知映射
        if base_upper == "GOLD" or base_upper == "XAUUSD":
            variants = ["XAUUSD", "XAUUSDm", "XAUUSDz", "XAUUSDk", "Gold", "GOLD", "Goldm", "XAUUSD.a", "XAUUSD.ecn"]
        elif base_upper == "EURUSD":
            variants = ["EURUSDm", "EURUSDz", "EURUSDk", "EURUSD.a", "EURUSD.ecn"]
        elif base_upper == "ETHUSD":
            variants = ["ETHUSDm", "ETHUSDz", "ETHUSDk", "ETHUSD.a", "ETHUSD.ecn"]
        
        # 3. 动态扫描 (Dynamic Scanning for Platform Specifics)
        # 获取所有可用交易品种，寻找最匹配的
        # 适用于未知品种或复杂后缀
        
        # 通用后缀尝试 (Priority 1)
        variants.extend([f"{base_upper}m", f"{base_upper}z", f"{base_upper}k", f"{base_upper}.a", f"{base_upper}.ecn"])
        
        # 4. Search in All Symbols (Heavy operation, but done once at startup)
        # 如果前面的常见变体都失败了，我们扫描所有品种
        # 优化: 仅当 variants 为空或都失败时执行
        
        # First pass: Check known variants
        for var in variants:
            if mt5.symbol_select(var, True):
                 if mt5.symbol_info(var):
                    logger.info(f"✅ 自动识别品种: {base_symbol} -> {var}")
                    return var
            elif mt5.symbol_info(var): 
                logger.info(f"✅ 自动识别品种 (Info): {base_symbol} -> {var}")
                return var
        
        # Second pass: Deep Search
        logger.info(f"Deep searching for symbol match: {base_upper}...")
        all_symbols = mt5.symbols_get()
        if all_symbols:
            # Sort by name length to find shortest match (usually standard) or specific suffix?
            # Prefer suffixes like 'm' or 'z' or '.a' if they contain the base name
            
            candidates = []
            for s in all_symbols:
                if base_upper in s.name.upper():
                    candidates.append(s.name)
            
            if candidates:
                # 智能选择最佳匹配
                # 优先规则: 
                # 1. Exness 偏好: 'm' 结尾 (e.g. XAUUSDm)
                # 2. Standard: 完全匹配
                # 3. Shortest: 最短的 (e.g. XAUUSD vs XAUUSD.ecn)
                
                # Exness Check
                exness_matches = [c for c in candidates if c.endswith('m') and len(c) == len(base_upper) + 1]
                if exness_matches:
                    chosen = exness_matches[0]
                    if mt5.symbol_select(chosen, True):
                        logger.info(f"✅ 自动识别品种 (Deep Exness): {base_symbol} -> {chosen}")
                        return chosen

                # Standard/Shortest
                candidates.sort(key=len)
                chosen = candidates[0]
                if mt5.symbol_select(chosen, True):
                    logger.info(f"✅ 自动识别品种 (Deep Match): {base_symbol} -> {chosen}")
                    return chosen

        logger.warning(f"⚠️ 未能自动识别品种变体: {base_symbol}, 将尝试使用原名")
        return base_symbol

    def start(self, account_index=1):
        if not self.initialize_mt5(account_index):
            logger.error("MT5 初始化失败，无法启动")
            return
            
        # --- 自动解析品种名称 ---
        resolved_symbols = []
        for s in self.symbols:
            resolved = self._resolve_symbol(s)
            if resolved not in resolved_symbols:
                resolved_symbols.append(resolved)
        self.symbols = resolved_symbols
        logger.info(f"最终交易品种列表: {self.symbols}")
        # -----------------------

        # Start File Watcher
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.watcher = FileWatcher([current_dir])
            self.watcher.start()
        except Exception as e:
            logger.error(f"Failed to start FileWatcher: {e}")

        self.is_running = True
        logger.info(f"🚀 Multi-Symbol Bot Started for: {self.symbols}")

        # Launch a thread for each symbol
        for symbol in self.symbols:
            try:
                # Create and start a worker thread for this symbol
                thread = threading.Thread(target=self._trader_worker, args=(symbol,), name=f"Thread-{symbol}", daemon=True)
                thread.start()
                logger.info(f"Thread for {symbol} started.")
            except Exception as e:
                logger.error(f"Failed to start thread for {symbol}: {e}")

        try:
            # Main thread keep-alive
            while self.is_running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Bot stopped by user.")
            self.is_running = False
            mt5.shutdown()
        except Exception as e:
            logger.critical(f"Fatal Bot Error: {e}", exc_info=True)
            self.is_running = False
            mt5.shutdown()

    def _trader_worker(self, symbol):
        """Worker function for each symbol thread"""
        try:
            # Initialize trader instance inside the thread
            # NOTE: MT5 calls are thread-safe, but we need to ensure separate state
            trader = SymbolTrader(symbol=symbol, timeframe=self.timeframe)
            trader.initialize()
            self.traders.append(trader) # Keep reference if needed
            
            logger.info(f"[{symbol}] Worker Loop Started")
            
            while self.is_running:
                try:
                    trader.process_tick()
                except Exception as e:
                    logger.error(f"[{symbol}] Process Error: {e}")
                
                # Independent sleep for this symbol's loop
                # Adjust polling rate if needed
                time.sleep(1) 
                
        except Exception as e:
            logger.error(f"[{symbol}] Worker Thread Crash: {e}")

if __name__ == "__main__":
    import argparse
    
    # Argument Parsing
    parser = argparse.ArgumentParser(description="Multi-Symbol AI Trading Bot")
    parser.add_argument("symbols", nargs="?", default="GOLD,ETHUSD,EURUSD", help="Comma separated symbols (e.g. GOLD,EURUSD)")
    parser.add_argument("--account", type=int, default=1, help="Account Index from .env (1=Ava, 2=Exness)")
    
    args = parser.parse_args()
    
    # Parse Symbols
    symbols = [s.strip().upper() for s in args.symbols.split(",")]
    
    logger.info(f"Starting Bot with Account {args.account} for symbols: {symbols}")
            
    # User Requirement: Change Timeframe back to 15 Minutes
    bot = MultiSymbolBot(symbols=symbols, timeframe=mt5.TIMEFRAME_M15)
    bot.start(account_index=args.account)