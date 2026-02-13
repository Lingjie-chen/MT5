import time
import sys
import os
import json
import logging
import threading
import warnings
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Suppress warnings
warnings.filterwarnings("ignore")

# Path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path: sys.path.append(current_dir)
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path: sys.path.append(src_dir)

# Imports
try:
    import MetaTrader5 as mt5
    from ai.ai_client_factory import AIClientFactory
    from data.mt5_data_processor import MT5DataProcessor
    from data.database_manager import DatabaseManager
    from strategies.grid_strategy import KalmanGridStrategy
    from strategies.orb_strategy import GoldORBStrategy
    from analysis.smc_validator import SMCQualityValidator
    from position_engine.mt5_adapter import MT5RiskManager
    from utils.file_watcher import FileWatcher # Restore FileWatcher
except ImportError as e:
    # Handle FileWatcher Import separately
    if "FileWatcher" in str(e) or "utils.file_watcher" in str(e) or "utils" in str(e):
        try:
            # Add utils directory to path directly
            utils_path = os.path.join(src_dir, 'utils')
            if utils_path not in sys.path: sys.path.append(utils_path)
            # Try importing directly
            import file_watcher
            FileWatcher = file_watcher.FileWatcher
        except ImportError:
            print("Warning: FileWatcher not found, auto-reload disabled.")
            FileWatcher = None
    else:
        print(f"Critical Import Error: {e}")
        sys.exit(1)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('trading_bot.log', encoding='utf-8'), logging.StreamHandler()]
)
logger = logging.getLogger("TradingBot")

load_dotenv()

class SymbolTrader:
    def __init__(self, symbol="XAUUSD", timeframe=mt5.TIMEFRAME_M15):
        self.symbol = symbol
        self.timeframe = timeframe
        self.magic_number = 888888
        
        # 1. Initialize Strategies & Analyzers
        self.orb_strategy = GoldORBStrategy(symbol)
        self.grid_strategy = KalmanGridStrategy(symbol, self.magic_number)
        self.smc_validator = SMCQualityValidator()
        self.data_processor = MT5DataProcessor()
        self.risk_manager = MT5RiskManager() # Assuming this exists in position_engine
        
        # 2. AI Client
        self.ai_factory = AIClientFactory()
        self.llm_client = self.ai_factory.create_client("qwen") # Use Qwen for logic
        
        # 3. State
        self.last_tick_time = 0
        self.last_analysis_time = 0
        self.current_strategy_mode = "ORB_MONITOR" # ORB_MONITOR, GRID_RANGING
        self.last_grid_update = 0
        self.watcher = None # Initialize watcher attribute
        
        # 4. Data Buffers
        self.tick_buffer = []
        
    def initialize(self):
        if not mt5.initialize():
            logger.error("MT5 Initialize Failed")
            return False
        
        # Start File Watcher
        if FileWatcher:
            try:
                self.watcher = FileWatcher([src_dir]) # Keep reference to prevent GC
                self.watcher.start()
                logger.info("FileWatcher started successfully")
            except Exception as e:
                logger.error(f"Failed to start FileWatcher: {e}")
        else:
             logger.warning("FileWatcher unavailable - Auto-reload disabled")
            
        logger.info(f"Bot Initialized for {self.symbol}")
        return True

    def run(self):
        logger.info("Starting Main Trading Loop...")
        while True:
            try:
                tick = mt5.symbol_info_tick(self.symbol)
                if tick is None:
                    time.sleep(1)
                    continue
                
                # Millisecond Check
                if tick.time_msc == self.last_tick_time:
                    time.sleep(0.01) # 10ms poll
                    continue
                
                self.last_tick_time = tick.time_msc
                self.process_tick(tick)
                
            except Exception as e:
                logger.error(f"Loop Error: {e}")
                time.sleep(1)

    def process_tick(self, tick):
        current_price = tick.ask # Assume Buy Logic uses Ask, Sell uses Bid, simplified to Ask for trigger check
        
        # 1. Update Real-time Data
        # We need recent M15 data for SMC/ORB levels
        # Only update this periodically or if cache is stale
        if time.time() - self.last_analysis_time > 60: # Update every minute for candles
            self.update_candle_data()
            self.last_analysis_time = time.time()
            
        # 2. ORB Real-time Check (Highest Priority)
        # Returns immediate signal if price breaks range
        orb_signal = self.orb_strategy.check_realtime_breakout(current_price, tick.time_msc)
        
        if orb_signal:
            logger.info(f"ORB Trigger Detected: {orb_signal['signal']}")
            self.handle_orb_signal(orb_signal)
            return # Skip Grid logic if ORB active
            
        # 3. Grid Strategy Logic (If ORB inactive)
        # Only check grid logic if we are in Ranging Mode or if we need to switch
        # We check market state periodically
        
        if self.current_strategy_mode == "GRID_RANGING" or self.grid_strategy.is_ranging:
             # Check for Grid Updates (e.g. every 5 mins or if price moved significantly)
             if time.time() - self.last_grid_update > 300:
                 self.handle_grid_logic(current_price)
                 self.last_grid_update = time.time()
        
        # 4. Position Management (Universal)
        # Check Basket TP/SL/Trailing
        self.manage_positions(current_price)

    def update_candle_data(self):
        # Fetch M15 Data
        rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, 500)
        if rates is not None:
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            # Update Strategy States
            # H1 Data for ORB
            rates_h1 = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_H1, 0, 100)
            if rates_h1 is not None:
                df_h1 = pd.DataFrame(rates_h1)
                df_h1['time'] = pd.to_datetime(df_h1['time'], unit='s')
                self.orb_strategy.calculate_orb_levels(df_h1)
            
            # Update Grid Indicators
            self.grid_strategy.update_market_data(df)

    def handle_orb_signal(self, orb_signal):
        """
        1. Validate with SMC
        2. Get LLM Confirmation (Smart SL/TP)
        3. Execute
        """
        # 1. SMC Validation
        df_m15 = self.get_dataframe(self.timeframe, 100)
        is_valid, score, details = self.smc_validator.validate_signal(
            df_m15, 
            orb_signal['price'], 
            orb_signal['signal'],
            volatility_stats=orb_signal.get('stats')
        )
        
        if not is_valid:
            logger.warning(f"ORB Signal Ignored: SMC Score {score} < 75. Details: {details}")
            return

        # 2. LLM Confirmation (Smart SL & Basket TP)
        logger.info(f"SMC Validated ({score}). Requesting LLM Analysis...")
        
        market_context = {
            "symbol": self.symbol,
            "current_price": orb_signal['price'],
            "orb_signal": orb_signal,
            "smc_score": score,
            "smc_details": details
        }
        
        # Call LLM (Synchronous for safety, or Async if needed)
        # We use a specialized prompt method for 'Trade Execution'
        try:
            llm_decision = self.llm_client.optimize_strategy_logic(
                market_structure_analysis=details, # Pass SMC details
                current_market_data=market_context
            )
            
            # Extract Smart SL/TP
            smart_sl = llm_decision.get('exit_conditions', {}).get('sl_price', 0)
            smart_tp = llm_decision.get('exit_conditions', {}).get('tp_price', 0)
            basket_tp = llm_decision.get('position_management', {}).get('dynamic_basket_tp', 0)
            
            if smart_sl == 0: # Fallback to ORB default
                if orb_signal['signal'] == 'buy':
                    smart_sl = orb_signal['price'] - orb_signal['sl_dist']
                else:
                    smart_sl = orb_signal['price'] + orb_signal['sl_dist']
            
            # 3. Execute Trade
            lot_size = llm_decision.get('position_size', 0.01)
            
            logger.info(f"Executing ORB Trade: {orb_signal['signal'].upper()} | Lot: {lot_size} | SL: {smart_sl} | BasketTP: ${basket_tp}")
            
            self.execute_trade(
                signal=orb_signal['signal'],
                lot=lot_size,
                sl=smart_sl,
                tp=smart_tp, # Optional, we rely on Basket TP mostly
                comment=f"ORB_SMC_{score}"
            )
            
            # Update Grid Strategy with Basket Params
            self.grid_strategy.update_dynamic_params(basket_tp=basket_tp)
            
        except Exception as e:
            logger.error(f"LLM/Execution Error: {e}")

    def handle_grid_logic(self, current_price):
        """
        Deploy Fibonacci Grid if in Ranging Mode
        """
        # Check Trend Direction (Simple MA check or from Grid Strategy)
        trend = "bullish" if self.grid_strategy.ma_value < current_price else "bearish"
        
        # Generate Orders
        orders = self.grid_strategy.generate_fibonacci_grid(current_price, trend)
        
        if orders:
            logger.info(f"Deploying {len(orders)} Fibonacci Grid Orders ({trend})")
            # Cancel existing pending orders first?
            # self.cancel_all_pending() 
            
            for order in orders:
                self.place_limit_order(order)

    def manage_positions(self, current_price):
        """
        Unified Risk Management
        """
        positions = mt5.positions_get(symbol=self.symbol)
        if positions:
            close_long, close_short = self.grid_strategy.check_grid_exit(positions, current_price)
            
            if close_long:
                self.close_positions(positions, type_filter=mt5.POSITION_TYPE_BUY, reason="Basket TP/Lock")
            if close_short:
                self.close_positions(positions, type_filter=mt5.POSITION_TYPE_SELL, reason="Basket TP/Lock")

    # --- Execution Helpers ---
    def execute_trade(self, signal, lot, sl, tp, comment):
        order_type = mt5.ORDER_TYPE_BUY if signal == 'buy' else mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(self.symbol).ask if signal == 'buy' else mt5.symbol_info_tick(self.symbol).bid
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": float(lot),
            "type": order_type,
            "price": price,
            "sl": float(sl),
            "tp": float(tp),
            "deviation": 20,
            "magic": self.magic_number,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"Trade Failed: {result.comment}")
        else:
            logger.info(f"Trade Executed: {result.order}")

    def place_limit_order(self, order_dict):
        # Implementation of limit order placement
        pass

    def close_positions(self, positions, type_filter, reason):
        for pos in positions:
            if pos.magic == self.magic_number and pos.type == type_filter:
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.symbol,
                    "volume": pos.volume,
                    "type": mt5.ORDER_TYPE_SELL if pos.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                    "position": pos.ticket,
                    "price": mt5.symbol_info_tick(self.symbol).bid if pos.type == mt5.POSITION_TYPE_BUY else mt5.symbol_info_tick(self.symbol).ask,
                    "deviation": 20,
                    "magic": self.magic_number,
                    "comment": reason,
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
                mt5.order_send(request)

    def get_dataframe(self, timeframe, count):
        rates = mt5.copy_rates_from_pos(self.symbol, timeframe, 0, count)
        if rates is None: return None
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

if __name__ == "__main__":
    bot = SymbolTrader("XAUUSD")
    if bot.initialize():
        bot.run()
