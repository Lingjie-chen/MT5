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
    from analysis.advanced_analysis import AdvancedMarketAnalysisAdapter
    from utils.file_watcher import FileWatcher # Restore FileWatcher
    from utils.telegram_notifier import TelegramNotifier # Add Telegram Notifier
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
    def __init__(self, symbol="GOLD", timeframe=mt5.TIMEFRAME_M15, account_index=1):
        self.symbol = symbol
        self.timeframe = timeframe
        self.account_index = account_index
        self.magic_number = 888888
        
        # 1. Initialize Strategies & Analyzers
        self.orb_strategy = GoldORBStrategy(symbol)
        self.grid_strategy = KalmanGridStrategy(symbol, self.magic_number)
        self.smc_validator = SMCQualityValidator()
        self.advanced_analysis = AdvancedMarketAnalysisAdapter()
        self.data_processor = MT5DataProcessor()
        self.risk_manager = MT5RiskManager() # Assuming this exists in position_engine
        
        # 2. AI Client
        self.ai_factory = AIClientFactory()
        self.llm_client = self.ai_factory.create_client("qwen") # Use Qwen for logic
        
        # 3. Notifiers
        self.telegram = TelegramNotifier()
        
        # 4. State
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

        # --- Auto Login Logic ---
        # Try to login to the specific account based on account_index
        acc_id = os.getenv(f"MT5_ACCOUNT_{self.account_index}")
        acc_pass = os.getenv(f"MT5_PASSWORD_{self.account_index}")
        acc_server = os.getenv(f"MT5_SERVER_{self.account_index}")
        
        if acc_id and acc_pass and acc_server:
            try:
                authorized = mt5.login(int(acc_id), password=acc_pass, server=acc_server)
                if authorized:
                    logger.info(f"Automatically logged into Account {self.account_index} ({acc_id}) on {acc_server}")
                else:
                    logger.error(f"Failed to login to Account {self.account_index} ({acc_id}): {mt5.last_error()}")
                    # Don't return False here, maybe user is already logged in manually to another account
                    # But warn them
            except Exception as e:
                logger.error(f"Login exception: {e}")
        else:
            logger.info(f"No credentials found for Account {self.account_index}, using current terminal login.")

        # Check Symbol Availability & Auto-Switch
        # Some brokers use GOLD, some XAUUSD, some XAUUSD.m
        # We try to find the best match if the default fails
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            logger.warning(f"Symbol {self.symbol} not found. Attempting auto-discovery...")
            
            # 1. Try common suffixes
            suffixes = [".m", ".pro", "_i", ".c", ".ecn"]
            found = False
            for suffix in suffixes:
                cand = f"{self.symbol}{suffix}"
                if mt5.symbol_info(cand):
                    self.symbol = cand
                    logger.info(f"Auto-switched to available symbol: {self.symbol}")
                    found = True
                    break
            
            # 2. If still not found, and it looks like Gold, try Gold variants
            if not found and self.symbol.upper() in ["GOLD", "XAUUSD"]:
                candidates = ["GOLD", "XAUUSD", "XAUUSD.m", "Gold", "XAUUSD_i"]
                for cand in candidates:
                    if mt5.symbol_info(cand):
                        self.symbol = cand
                        logger.info(f"Auto-switched to available Gold symbol: {self.symbol}")
                        found = True
                        break
            
            if not found:
                logger.error(f"Critical: Could not find symbol {self.symbol} or variants.")
                return False
                
        # Enable Market Watch for the symbol
        if not mt5.symbol_select(self.symbol, True):
            logger.error(f"Failed to select symbol {self.symbol} in Market Watch")
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
        1. Validate with SMC (Score >= 75)
        2. Get LLM Confirmation (Smart SL & Basket TP)
        3. Execute with Millisecond Response
        """
        # 0. Regime Filter (Advanced Analysis)
        df_m15 = self.get_dataframe(self.timeframe, 200)
        regime_info = self.advanced_analysis.analyze_full(df_m15)
        
        if regime_info:
            regime = regime_info.get('regime', {}).get('regime', 'unknown')
            confidence = regime_info.get('regime', {}).get('confidence', 0)
            
            # ORB works best in Trending or High Volatility
            if regime == "ranging" and confidence > 0.7:
                logger.warning(f"ORB Signal Filtered: Market is Ranging (Conf: {confidence})")
                return

        # 1. SMC Validation - Integrated SMC Data Interface
        # df_m15 already fetched above
        
        # Calculate Quality Score: Liquidity, Order Flow, Institutional Participation
        is_valid, score, details = self.smc_validator.validate_signal(
            df_m15, 
            orb_signal['price'], 
            orb_signal['signal'],
            volatility_stats=orb_signal.get('stats')
        )
        
        # Quality Threshold Filter: Score >= 75
        if score < 75:
            logger.warning(f"ORB Signal Ignored: SMC Score {score} < 75. Details: {details}")
            return

        # 2. LLM Integrated Analysis System
        # Request Smart SL and Basket TP Analysis
        logger.info(f"SMC Validated ({score} >= 75). Requesting LLM Smart Analysis...")
        
        market_context = {
            "symbol": self.symbol,
            "current_price": orb_signal['price'],
            "orb_signal": orb_signal,
            "smc_score": score,
            "smc_details": details,
            "analysis_mode": "SMART_EXECUTION" # Instruct LLM to perform Smart SL/TP analysis
        }
        
        try:
            # Call LLM to analyze Micro-structure, Volatility, and Order Flow
            llm_decision = self.llm_client.optimize_strategy_logic(
                market_structure_analysis=details, 
                current_market_data=market_context
            )
            
            # Extract Smart SL (Optimal Stop Loss)
            smart_sl = llm_decision.get('exit_conditions', {}).get('sl_price', 0)
            
            # Extract Basket TP (Layered Take Profit for the Basket)
            basket_tp = llm_decision.get('position_management', {}).get('dynamic_basket_tp', 0)
            
            # Extract Reasoning for Telegram
            reasoning = llm_decision.get('reasoning', f"SMC Score: {score}")

            # Fallback Logic if LLM returns invalid SL
            if smart_sl == 0:
                if orb_signal['signal'] == 'buy':
                    smart_sl = orb_signal['price'] - orb_signal['sl_dist']
                else:
                    smart_sl = orb_signal['price'] + orb_signal['sl_dist']
            
            # Notify Telegram about Analysis - ONLY if Trade is Executed
            # self.telegram.notify_llm_analysis(
            #     self.symbol, 
            #     "ORB_OPTIMIZATION", 
            #     "EXECUTE", 
            #     reasoning, 
            #     f"SMC:{score} | SL:{smart_sl} | BasketTP:{basket_tp}"
            # )

            # 3. Execute Trade (Millisecond Response)
            lot_size = llm_decision.get('position_size', 0.01)
            
            logger.info(f"Executing ORB Trade: {orb_signal['signal'].upper()} | Lot: {lot_size} | Smart SL: {smart_sl} | Basket TP: ${basket_tp}")
            
            # Notify Telegram with LLM Reasoning
            self.telegram.notify_trade(
                self.symbol, 
                orb_signal['signal'], 
                orb_signal['price'], 
                smart_sl, 
                basket_tp, 
                lot_size, 
                reason=reasoning
            )
            
            self.execute_trade(
                signal=orb_signal['signal'],
                lot=lot_size,
                sl=smart_sl,
                tp=0.0, # TP is managed by Basket Logic
                comment=f"ORB_SMC_{score}"
            )
            
            # Update Grid Strategy with Basket Params for Global Management
            self.grid_strategy.update_dynamic_params(basket_tp=basket_tp)
            
        except Exception as e:
            logger.error(f"LLM/Execution Error: {e}")

    def handle_grid_logic(self, current_price):
        """
        Deploy Fibonacci Grid if in Ranging Mode with LLM Confirmation
        """
        # 0. Regime Filter (Advanced Analysis)
        df_m15 = self.get_dataframe(self.timeframe, 200)
        regime_info = self.advanced_analysis.analyze_full(df_m15)
        
        if regime_info:
            regime = regime_info.get('regime', {}).get('regime', 'unknown')
            confidence = regime_info.get('regime', {}).get('confidence', 0)
            
            # Grid works best in Ranging. Avoid Strong Trends unless pulling back.
            if regime == "high_volatility" and confidence > 0.8:
                logger.info(f"Grid Deployment Skipped: Market is High Volatility (Conf: {confidence})")
                return
            if regime == "trending" and confidence > 0.85:
                logger.info(f"Grid Deployment Skipped: Market is Strong Trending (Conf: {confidence})")
                return

        # 1. Prepare Market State Context
        grid_context = getattr(self.grid_strategy, 'market_state_details', {})
        if not grid_context:
            return

        # 2. Ask LLM to Analyze Market State
        # Only ask if we haven't asked recently (cooldown)
        if time.time() - self.last_grid_update < 300: # 5 min cooldown
             return

        logger.info(f"Analyzing Market State for Grid Deployment... (Context: {grid_context})")
        
        try:
            # We reuse optimize_strategy_logic but with a specific flag or prompt structure
            # For now, we simulate a specific call or extend the prompt
            
            # Construct a prompt-friendly context
            market_data_input = {
                "symbol": self.symbol,
                "current_price": current_price,
                "strategy_mode": "GRID_ANALYSIS", # Signal to LLM
                "technical_indicators": grid_context
            }
            
            # Call LLM
            llm_decision = self.llm_client.optimize_strategy_logic(
                market_structure_analysis={"summary": "Checking for Ranging Market"},
                current_market_data=market_data_input
            )
            
            # 3. Parse Decision
            # We expect LLM to return "action": "deploy_grid" or "hold"
            action = llm_decision.get('action', 'hold')
            reason = llm_decision.get('reason', 'Market conditions not optimal')
            trend = llm_decision.get('direction', 'neutral')
            
            # Send Analysis to Telegram - ONLY if Action is DEPLOY/EXECUTE
            # context_summary = f"Ranging:{grid_context.get('is_ranging')} | Vol:{grid_context.get('is_low_volume')} | Trend:{trend}"
            # self.telegram.notify_llm_analysis(self.symbol, "GRID_DEPLOYMENT", action, reason, context_summary)
            
            if action == 'deploy_grid' or self.grid_strategy.is_ranging: # Fallback to local logic if LLM is ambiguous but local is strong
                
                if trend == 'neutral':
                    trend = grid_context.get('trend_ma', 'bullish')
                
                # 4. Generate Orders
                orders = self.grid_strategy.generate_fibonacci_grid(current_price, trend)
                
                if orders:
                    logger.info(f"LLM Confirmed Grid Deployment ({len(orders)} orders, {trend}). Executing...")
                    
                    # Notify Telegram
                    self.telegram.notify_grid_deployment(self.symbol, len(orders), trend, current_price)
                    
                    # Safety: Cancel old grid orders before placing new ones
                    logger.info("Cancelling existing Pending Orders before deploying new Grid...")
                    self.cancel_all_pending()
                    
                    for order in orders:
                        self.place_limit_order(order)
                        
                    self.last_grid_update = time.time()
            else:
                logger.info(f"LLM Grid Analysis: {action} (Market not suitable for grid)")
                
        except Exception as e:
            logger.error(f"LLM Grid Analysis Failed: {e}")
            # Fallback to local logic if critical
            if self.grid_strategy.is_ranging:
                 orders = self.grid_strategy.generate_fibonacci_grid(current_price, "neutral")
                 for order in orders:
                        self.place_limit_order(order)
                 self.last_grid_update = time.time()

    def manage_positions(self, current_price):
        """
        Unified Risk Management
        """
        positions = mt5.positions_get(symbol=self.symbol)
        if positions:
            close_long, close_short, total_profit_long, total_profit_short, reason_long, reason_short = self.grid_strategy.check_grid_exit(positions, current_price)
            
            if close_long:
                self.close_positions(positions, type_filter=mt5.POSITION_TYPE_BUY, reason=reason_long)
                # Notify Telegram
                self.telegram.notify_basket_close(self.symbol, "LONG", total_profit_long, reason_long)
                
            if close_short:
                self.close_positions(positions, type_filter=mt5.POSITION_TYPE_SELL, reason=reason_short)
                # Notify Telegram
                self.telegram.notify_basket_close(self.symbol, "SHORT", total_profit_short, reason_short)

    # --- Execution Helpers ---
    def execute_trade(self, signal, lot, sl, tp, comment):
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            logger.error(f"Symbol {self.symbol} not found")
            return

        order_type = mt5.ORDER_TYPE_BUY if signal == 'buy' else mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(self.symbol).ask if signal == 'buy' else mt5.symbol_info_tick(self.symbol).bid
        
        # Normalize Prices
        tick_size = symbol_info.trade_tick_size
        if tick_size <= 0:
            tick_size = symbol_info.point

        if tick_size > 0:
            if sl > 0: sl = round(sl / tick_size) * tick_size
            if tp > 0: tp = round(tp / tick_size) * tick_size
            
        sl = round(sl, symbol_info.digits)
        tp = round(tp, symbol_info.digits)
        
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
            logger.error(f"Trade Failed: {result.comment} ({result.retcode})")
            self.telegram.notify_error(f"Trade Execution ({signal})", f"{result.comment} ({result.retcode})")
        else:
            logger.info(f"Trade Executed: {result.order}")

    def place_limit_order(self, order_dict):
        """
        Execute a Pending Limit Order for Grid Strategy
        """
        # Ensure Price is Normalized to tick size
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            logger.error(f"Cannot place order: Symbol {self.symbol} not found")
            return

        price = float(order_dict['price'])
        
        # Normalize price to tick size
        tick_size = symbol_info.trade_tick_size
        if tick_size <= 0:
            tick_size = symbol_info.point # Fallback to point
            
        if tick_size > 0:
            price = round(price / tick_size) * tick_size
            
        price = round(price, symbol_info.digits)

        # Check against current market to prevent 10015 (Limit vs Stop confusion)
        # Buy Limit must be < Ask, Sell Limit must be > Bid
        tick = mt5.symbol_info_tick(self.symbol)
        
        # Map strategy type strings to MT5 constants
        order_type_str = order_dict['type']
        mt5_type = mt5.ORDER_TYPE_BUY_LIMIT
        
        if order_type_str in ['buy_limit', 'limit_buy']:
            mt5_type = mt5.ORDER_TYPE_BUY_LIMIT
        elif order_type_str in ['sell_limit', 'limit_sell']:
            mt5_type = mt5.ORDER_TYPE_SELL_LIMIT
        else:
            logger.error(f"Unknown order type: {order_type_str}")
            return

        if tick:
            # Check StopLevel (minimum distance from price)
            stop_level = symbol_info.trade_stops_level * symbol_info.point
            
            if mt5_type == mt5.ORDER_TYPE_BUY_LIMIT:
                if price >= tick.ask:
                    logger.warning(f"Skipping Buy Limit @ {price} >= Ask {tick.ask}")
                    return
                if (tick.ask - price) < stop_level:
                    logger.warning(f"Skipping Buy Limit @ {price} too close to Ask {tick.ask} (StopLevel {stop_level})")
                    return
                    
            elif mt5_type == mt5.ORDER_TYPE_SELL_LIMIT:
                if price <= tick.bid:
                    logger.warning(f"Skipping Sell Limit @ {price} <= Bid {tick.bid}")
                    return
                if (price - tick.bid) < stop_level:
                    logger.warning(f"Skipping Sell Limit @ {price} too close to Bid {tick.bid} (StopLevel {stop_level})")
                    return

        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": self.symbol,
            "volume": float(order_dict.get('volume', 0.01)),
            "type": mt5_type,
            "price": price,
            "sl": float(order_dict.get('sl', 0)),
            "tp": float(order_dict.get('tp', 0)),
            "deviation": 20,
            "magic": self.magic_number,
            "comment": order_dict.get('comment', 'Grid Order'),
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }
        
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"Grid Order Failed: {result.comment} ({result.retcode}) - Price: {price} | TickSize: {tick_size} | Digits: {symbol_info.digits}")
        else:
            logger.info(f"Grid Order Placed: {order_dict['type']} @ {price} | Ticket: {result.order}")

    def cancel_all_pending(self):
        """
        Cancel all pending orders for this symbol/magic number
        """
        orders = mt5.orders_get(symbol=self.symbol)
        if orders:
            logger.info(f"Found {len(orders)} pending orders to cancel.")
            for order in orders:
                if order.magic == self.magic_number:
                    request = {
                        "action": mt5.TRADE_ACTION_REMOVE,
                        "order": order.ticket,
                        "magic": self.magic_number,
                    }
                    result = mt5.order_send(request)
                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        logger.info(f"Cancelled Order #{order.ticket}")
                    else:
                        logger.warning(f"Failed to cancel Order #{order.ticket}: {result.comment}")
        else:
            logger.info("No pending orders to cancel.")

    def close_positions(self, positions, type_filter, reason):
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            logger.error(f"Cannot close positions: Symbol {self.symbol} not found")
            return

        # Determine correct filling mode
        filling_mode = mt5.ORDER_FILLING_FOK # Default fallback
        if symbol_info.filling_mode & mt5.SYMBOL_FILLING_IOC:
            filling_mode = mt5.ORDER_FILLING_IOC
        elif symbol_info.filling_mode & mt5.SYMBOL_FILLING_FOK:
            filling_mode = mt5.ORDER_FILLING_FOK
            
        for pos in positions:
            if pos.magic == self.magic_number and pos.type == type_filter:
                # Retry logic for closing
                for attempt in range(3):
                    tick = mt5.symbol_info_tick(self.symbol)
                    if tick is None:
                        time.sleep(0.5)
                        continue
                        
                    price = tick.bid if pos.type == mt5.POSITION_TYPE_BUY else tick.ask
                    
                    request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": self.symbol,
                        "volume": float(pos.volume), # Explicit float cast
                        "type": mt5.ORDER_TYPE_SELL if pos.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                        "position": int(pos.ticket), # Explicit int cast
                        "price": float(price),
                        "deviation": 20,
                        "magic": self.magic_number,
                        "comment": str(reason),
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": filling_mode,
                    }
                    
                    result = mt5.order_send(request)
                    
                    if result is None:
                        last_error = mt5.last_error()
                        logger.error(f"Order Send Failed (None result) for Position #{pos.ticket}. MT5 Error: {last_error}")
                        time.sleep(0.5)
                        continue
                        
                    if result.retcode != mt5.TRADE_RETCODE_DONE:
                        logger.error(f"Failed to Close Position #{pos.ticket} (Attempt {attempt+1}): {result.comment} ({result.retcode})")
                        time.sleep(0.5)
                    else:
                        logger.info(f"Position #{pos.ticket} Closed: {reason} | Price: {result.price}")
                        break # Success
                else:
                    # All attempts failed
                    try:
                        self.telegram.notify_error(f"Close Fail #{pos.ticket}", "Max retries exceeded")
                    except: pass

    def get_dataframe(self, timeframe, count):
        rates = mt5.copy_rates_from_pos(self.symbol, timeframe, 0, count)
        if rates is None: return None
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Rename tick_volume to volume for compatibility with analysis modules
        if 'tick_volume' in df.columns and 'volume' not in df.columns:
            df.rename(columns={'tick_volume': 'volume'}, inplace=True)
            
        return df

if __name__ == "__main__":
    # Support command line args for symbol and account index
    # Usage: python main.py [SYMBOL] [ACCOUNT_INDEX]
    target_symbol = "GOLD"
    target_account = 1
    
    if len(sys.argv) > 1:
        target_symbol = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            target_account = int(sys.argv[2])
        except ValueError:
            pass

    bot = SymbolTrader(target_symbol, account_index=target_account)
    if bot.initialize():
        bot.run()
