import time
import sys
import os
import math
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
        self.orb_strategy = GoldORBStrategy(symbol, strategy_mode='DYNAMIC', dynamic_lookback=20) 
        self.grid_strategy = KalmanGridStrategy(symbol, self.magic_number)
        self.smc_validator = SMCQualityValidator()
        self.advanced_analysis = AdvancedMarketAnalysisAdapter()
        self.data_processor = MT5DataProcessor()
        self.risk_manager = MT5RiskManager()
        
        # 2. AI Client
        self.ai_factory = AIClientFactory()
        self.llm_client = self.ai_factory.create_client("qwen") 
        
        # 3. Notifiers
        self.telegram = TelegramNotifier()
        
        # 4. State Machine (Dynamic Risk)
        # States: OBSERVATION, GRID_ACTIVE, BREAKOUT_ACTIVE
        self.state = "OBSERVATION" 
        
        self.last_tick_time = 0
        self.last_analysis_time = 0
        self.last_grid_update = 0
        self.last_orb_filter_time = 0 
        self.orb_cooldowns = {'buy': 0, 'sell': 0} 
        self.last_heartbeat_time = 0 
        self.watcher = None 
        self.is_optimizing = False 
        
        # 5. Optimization Scheduler State
        self.last_optimization_time = time.time() 
        self.optimization_interval = 3600 
        
        # 6. Data Buffers
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
        
        # Trigger initial optimization on startup (Blocking to ensure fresh config)
        logger.info("Running Startup Strategy Optimization (Blocking)...")
        self.run_periodic_optimization(blocking=True)
        self.last_optimization_time = time.time()
        
        while True:
            try:
                # Periodic Tasks
                current_time = time.time()
                
                # 1. Strategy Optimization (Every Hour - Non-blocking)
                if current_time - self.last_optimization_time > self.optimization_interval:
                    logger.info("Triggering Hourly Strategy Optimization...")
                    self.run_periodic_optimization(blocking=False)
                    self.last_optimization_time = current_time

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

    def run_periodic_optimization(self, blocking=False):
        """
        Runs the optimization script.
        blocking: If True, waits for completion (good for startup).
        """
        if self.is_optimizing:
            logger.warning("Optimization already running, skipping trigger.")
            return

        self.is_optimizing = True

        def _optimization_task():
            try:
                import subprocess
                # Locate the script: scripts/optimize_strategy_params.py
                # current_dir is src/trading_bot
                # script is in src/../scripts/
                
                script_path = os.path.join(src_dir, '..', 'scripts', 'optimize_strategy_params.py')
                script_path = os.path.abspath(script_path)
                
                if not os.path.exists(script_path):
                     logger.error(f"Optimization script not found at {script_path}")
                     self.is_optimizing = False
                     return

                logger.info(f"Running Optimization Script: {script_path}")
                
                # Run as subprocess
                process = subprocess.Popen(
                    [sys.executable, script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    logger.info("Optimization Completed Successfully.")
                    # Log last few lines of output
                    lines = stdout.strip().split('\n')
                    for line in lines[-5:]:
                        logger.info(f"[Optimizer] {line}")
                        
                    # Reload Config in Grid Strategy
                    new_config = self.grid_strategy.reload_config()
                    logger.info(f"Grid Strategy Config Updated: {new_config}")
                    
                    # self.telegram.notify_info("Strategy Optimization", "Optimization completed. Grid parameters updated.")
                else:
                    logger.error(f"Optimization Failed (Code {process.returncode}):\n{stderr}")
                    
            except Exception as e:
                logger.error(f"Error running optimization task: {e}")
            finally:
                self.is_optimizing = False

        if blocking:
            _optimization_task()
        else:
            # Run in Daemon Thread
            t = threading.Thread(target=_optimization_task, daemon=True)
            t.start()

    def process_tick(self, tick):
        current_price = tick.ask
        
        # 0. Heartbeat (Every 60s)
        if time.time() - self.last_heartbeat_time > 60:
            self._log_heartbeat(current_price)
            self.last_heartbeat_time = time.time()
        
        # 1. Update Real-time Data (M15 Candles) & State Machine
        if time.time() - self.last_analysis_time > 60:
            self.update_candle_data()
            self.last_analysis_time = time.time()
            
            # [NEW] Update Market State Machine (Phase 2: Logic Refactoring)
            self.update_market_regime_state(current_price)
            
        # 2. State Machine Execution
        # Priority Check: ORB Breakout (Can trigger in ANY state)
        orb_signal = self.orb_strategy.check_realtime_breakout(current_price, tick.time_msc)
        if orb_signal:
            self._process_orb_signal_with_state_transition(orb_signal)
            # If ORB triggered, we skip Grid logic for this tick
        else:
            # State Dispatch
            if self.state == "OBSERVATION":
                 # In Observation Mode, we monitor (transition handled in update_market_regime_state)
                 pass
                 
            elif self.state == "GRID_ACTIVE":
                 # In Grid Mode, we check for Grid updates
                 if time.time() - self.last_grid_update > 300:
                     self.handle_grid_logic(current_price)
                     self.last_grid_update = time.time()
                     
            elif self.state == "BREAKOUT_ACTIVE":
                 self._state_breakout_logic(current_price)

        # 3. Position Management (Universal)
        self.manage_positions(current_price)

    def update_market_regime_state(self, current_price):
        """
        Implements the Finite State Machine (FSM) from the Optimization Report.
        Transitions: Observation <-> Grid <-> Breakout
        """
        # Fetch latest analysis
        df_m15 = self.get_dataframe(self.timeframe, 200)
        if df_m15 is None or len(df_m15) < 50: return

        regime_info = self.advanced_analysis.analyze_full(df_m15)
        if not regime_info: return
        
        # Extract Key Metrics
        adx = regime_info.get('regime', {}).get('adx', 0)
        chop = regime_info.get('chop_index', 50)
        
        # Calculate BB Width if not in dict (fallback)
        bb_width = regime_info.get('indicators', {}).get('bb_width', 0)
        if bb_width == 0:
            bb_upper = regime_info.get('indicators', {}).get('bb_upper', 0)
            bb_lower = regime_info.get('indicators', {}).get('bb_lower', 0)
            bb_mid = regime_info.get('indicators', {}).get('bb_middle', 1)
            if bb_mid > 0:
                bb_width = (bb_upper - bb_lower) / bb_mid
        
        new_state = self.state
        
        # --- State Transition Logic ---
        
        # 1. Check for Grid / Ranging (Only enter Grid if strict conditions met)
        # Condition: Low ADX AND High CHOP (True Ranging)
        if adx < 25 and chop > 61.8:
            new_state = "GRID_ACTIVE"
            
        # 2. Default / Trending / Breakout Regime -> OBSERVATION
        # If ADX is high, we stay in OBSERVATION. 
        # BREAKOUT_ACTIVE is ONLY entered when a trade is actually taken (via _process_orb_signal).
        else:
            # Only switch to observation if we are not locked in a trade
            if self.state != "BREAKOUT_ACTIVE":
                new_state = "OBSERVATION"
            
        # --- Handle Transitions ---
        if new_state != self.state:
            # Special Case: Don't exit BREAKOUT_ACTIVE if WE have positions
            if self.state == "BREAKOUT_ACTIVE":
                 positions = mt5.positions_get(symbol=self.symbol)
                 # FIX: Filter by Magic Number to avoid staying stuck due to manual trades
                 bot_positions = [p for p in positions if p.magic == self.magic_number] if positions else []
                 if bot_positions: return # Stay in Breakout mode until OUR positions closed
            
            logger.info(f"State Transition: {self.state} -> {new_state} (ADX:{adx:.1f}, CHOP:{chop:.1f})")
            
            # Exit Actions
            if self.state == "GRID_ACTIVE":
                # Leaving Grid Mode -> Cancel Grid Orders
                logger.info("Exiting Grid Mode: Cancelling all pending grid orders.")
                self.cancel_all_pending()
                self.grid_strategy.is_ranging = False
                
            # Entry Actions
            if new_state == "GRID_ACTIVE":
                self.grid_strategy.is_ranging = True
                # Trigger immediate Grid Check
                self.last_grid_update = 0 
                
            self.state = new_state
            # Notify Telegram
            self.telegram.notify_info("Market Regime Change", f"New Mode: **{new_state}**\nADX: {adx:.1f} | CHOP: {chop:.1f}")

    def _process_orb_signal_with_state_transition(self, orb_signal):
        # Check Cooldown
        signal_type = orb_signal['signal']
        if time.time() - self.orb_cooldowns.get(signal_type, 0) < 60:
            self._reset_orb_flags(signal_type)
            return

        logger.info(f"ORB Trigger Detected in state {self.state}: {orb_signal['signal']}")
        
        # Handle the signal (SMC Validation -> LLM -> Execution)
        success = self.handle_orb_signal(orb_signal)
        
        if success:
            # Transition to BREAKOUT_ACTIVE
            if self.state == "GRID_ACTIVE":
                logger.warning("ORB Breakout! Stopping Grid & Closing Counter Positions.")
                self.cancel_all_pending()
                # Close counter positions logic is handled inside handle_orb_signal
                
            self.state = "BREAKOUT_ACTIVE"
            self.grid_strategy.is_ranging = False
        else:
            # Signal rejected (SMC/Filter), return to previous state logic
            pass

    def _state_observation_logic(self, current_price):
        """
        Default State: Monitor for Ranging (Grid) or Breakout (ORB)
        """
        # Check if we should enter Grid Mode
        # Condition: is_ranging (ADX < 25 & CHOP > 61.8)
        if self.grid_strategy.is_ranging:
            # Double check with time-based throttling
            if time.time() - self.last_grid_update > 300:
                logger.info("Market Ranging Detected (ADX<25, CHOP>61.8). transitioning to GRID_ACTIVE...")
                self.state = "GRID_ACTIVE"
                self.handle_grid_logic(current_price)
                self.last_grid_update = time.time()

    def _state_grid_logic(self, current_price):
        """
        Grid Active: Place/Manage Grid Orders
        Exit if Trend Detected (ADX > 30)
        """
        # Check Exit Condition: Trend Forming
        # We access the latest analysis from grid strategy update
        details = getattr(self.grid_strategy, 'market_state_details', {})
        adx = details.get('adx', 0)
        
        if adx > 30: # Trend Warning
            logger.info(f"Trend Detected (ADX {adx:.1f} > 30). Exiting GRID_ACTIVE -> OBSERVATION.")
            self.state = "OBSERVATION"
            self.grid_strategy.is_ranging = False
            self.cancel_all_pending() # Stop adding new risk
            
            # [NEW] Circuit Breaker: Immediate Close All Grid Positions
            # If ADX > 30, the ranging thesis is broken. Close to prevent drawdown.
            positions = mt5.positions_get(symbol=self.symbol)
            if positions:
                grid_positions = [p for p in positions if p.magic == self.magic_number]
                if grid_positions:
                    logger.warning(f"Circuit Breaker Triggered (ADX {adx:.1f}). Closing {len(grid_positions)} Grid Positions.")
                    self.close_positions(grid_positions, mt5.POSITION_TYPE_BUY, reason="Circuit Breaker (ADX)")
                    self.close_positions(grid_positions, mt5.POSITION_TYPE_SELL, reason="Circuit Breaker (ADX)")
                    self.telegram.notify_error("Circuit Breaker", f"ADX Spike ({adx:.1f}). Closed all grid positions.")
            return

        # Periodic Grid Maintenance
        if time.time() - self.last_grid_update > 300:
            self.handle_grid_logic(current_price)
            self.last_grid_update = time.time()

    def _state_breakout_logic(self, current_price):
        """
        Breakout Active: Managing ORB Trade
        Exit when trade closes
        """
        # Check if we still have active positions
        positions = mt5.positions_get(symbol=self.symbol)
        
        # FIX: Filter by Magic Number
        has_active_trade = False
        if positions:
            for p in positions:
                if p.magic == self.magic_number:
                    has_active_trade = True
                    break
        
        if not has_active_trade:
            # Trade closed, return to OBSERVATION
            # Add a small delay/cooldown?
            logger.info("Breakout Trade Closed. Returning to OBSERVATION.")
            self.state = "OBSERVATION"

    def _reset_orb_flags(self, signal_type):
        if signal_type == 'buy':
            self.orb_strategy.long_signal_taken_today = False
            self.orb_strategy.trades_today_count = max(0, self.orb_strategy.trades_today_count - 1)
        else:
            self.orb_strategy.short_signal_taken_today = False
            self.orb_strategy.trades_today_count = max(0, self.orb_strategy.trades_today_count - 1)

    def update_candle_data(self):
        # Fetch M15 Data
        rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, 500)
        if rates is not None:
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            # Update Strategy States
            # H1 Data for ORB (REPLACED WITH M15)
            # rates_h1 = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_H1, 0, 100)
            # if rates_h1 is not None:
            #     df_h1 = pd.DataFrame(rates_h1)
            #     df_h1['time'] = pd.to_datetime(df_h1['time'], unit='s')
            #     self.orb_strategy.calculate_orb_levels(df_h1)
            
            # Use M15 Data for ORB Calculation
            self.orb_strategy.calculate_orb_levels(df) # df is already M15 from above
            
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
        
        # [NEW] Check Hedging Condition
        # If we are in GRID_ACTIVE and trigger ORB, it's a breakout against the grid.
        # We need to hedge or reverse.
        is_hedging = self.state == "GRID_ACTIVE"
        
        if regime_info:
            regime = regime_info.get('regime', {}).get('regime', 'unknown')
            confidence = regime_info.get('regime', {}).get('confidence', 0)
            
            # ORB works best in Trending or High Volatility
            # BUT if we are Hedging, we ignore the filter because we MUST protect the account
            if not is_hedging and regime == "ranging" and confidence > 0.7:
                if time.time() - self.last_orb_filter_time > 300:
                     logger.info(f"ORB Signal Filtered: Market is Ranging (Conf: {confidence})")
                     self.last_orb_filter_time = time.time()
                
                # Set Cooldown
                self.orb_cooldowns[orb_signal['signal']] = time.time()

                # RESET FLAGS so we don't kill ORB for the day just because of a filter
                # and importantly, so we don't fall through to Grid Logic next tick
                if orb_signal['signal'] == 'buy':
                    self.orb_strategy.long_signal_taken_today = False
                    self.orb_strategy.trades_today_count = max(0, self.orb_strategy.trades_today_count - 1)
                else:
                    self.orb_strategy.short_signal_taken_today = False
                    self.orb_strategy.trades_today_count = max(0, self.orb_strategy.trades_today_count - 1)
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
        
        # Quality Threshold Filter: Score >= 70
        # If Hedging, lower threshold or bypass
        min_score = 50 if is_hedging else 70
        
        if score < min_score:
            if time.time() - self.last_orb_filter_time > 300:
                logger.info(f"ORB Signal Filtered: SMC Score {score} < {min_score}. Details: {details}")
                self.last_orb_filter_time = time.time()
            
            # Set Cooldown
            self.orb_cooldowns[orb_signal['signal']] = time.time()

            # RESET FLAGS
            if orb_signal['signal'] == 'buy':
                self.orb_strategy.long_signal_taken_today = False
                self.orb_strategy.trades_today_count = max(0, self.orb_strategy.trades_today_count - 1)
            else:
                self.orb_strategy.short_signal_taken_today = False
                self.orb_strategy.trades_today_count = max(0, self.orb_strategy.trades_today_count - 1)
            return

        # 2. LLM Integrated Analysis System
        # Request Smart SL and Basket TP Analysis
        logger.info(f"SMC Validated ({score} >= {min_score}). Requesting LLM Smart Analysis...")
        
        # Prepare Technical Signals including Grid Config
        tech_signals = {
            "grid_strategy": {
                "config": self.grid_strategy.get_active_config(),
                "orb_data": {
                    "stats": orb_signal.get('stats', {})
                }
            }
        }
        
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
                current_market_data=market_context,
                technical_signals=tech_signals # Pass optimization config here
            )
            
            if not llm_decision:
                logger.error("LLM Decision is None. Aborting ORB execution.")
                return

            # Extract Smart SL (Optimal Stop Loss)
            smart_sl = llm_decision.get('exit_conditions', {}).get('sl_price', 0)
            
            # Extract Smart TP (Optimal Take Profit)
            smart_tp = llm_decision.get('exit_conditions', {}).get('tp_price', 0)
            
            # Extract Basket TP (Layered Take Profit for the Basket)
            # Prioritize 'position_management' -> 'dynamic_basket_tp', fallback to 'grid_config' -> 'basket_tp_usd'
            pos_mgmt = llm_decision.get('position_management', {})
            grid_conf = llm_decision.get('grid_config', {})
            
            basket_tp = pos_mgmt.get('dynamic_basket_tp', 0)
            if not basket_tp:
                basket_tp = grid_conf.get('basket_tp_usd', 0)
            
            # Extract Reason for Telegram
            reason = llm_decision.get('reason', f"SMC Score: {score}")

            # Fallback Logic if LLM returns invalid SL/TP (Math Model Fallback)
            if smart_sl == 0:
                if orb_signal['signal'] == 'buy':
                    smart_sl = orb_signal['price'] - orb_signal['sl_dist']
                else:
                    smart_sl = orb_signal['price'] + orb_signal['sl_dist']
                    
            if smart_tp == 0:
                if orb_signal['signal'] == 'buy':
                    smart_tp = orb_signal['price'] + orb_signal['tp_dist']
                else:
                    smart_tp = orb_signal['price'] - orb_signal['tp_dist']
            
            # Update Grid Strategy with Basket Params for Global Management
            # CRITICAL: This must be updated BEFORE execution to ensure the Basket Logic picks it up immediately
            if basket_tp > 0:
                self.grid_strategy.update_dynamic_params(
                    basket_tp=basket_tp, 
                    basket_tp_long=basket_tp, # Assuming ORB direction dictates primary basket
                    basket_tp_short=basket_tp
                )
                logger.info(f"Updated Dynamic Basket TP: ${basket_tp}")
            else:
                logger.warning("LLM returned 0 or missing Basket TP, keeping existing config.")

            # 3. Execute Trade (Millisecond Response)
            # Quantum Position Engine Integration
            try:
                # Extract Risk % from LLM (Default to 1.0% if missing)
                risk_metrics = llm_decision.get('risk_metrics', {})
                recommended_risk = float(risk_metrics.get('recommended_risk_percent', 1.0))
                
                # [NEW] Hedging Multiplier
                # If Hedging (Breakout from Grid), increase risk/size to recover loss
                if is_hedging:
                    recommended_risk *= 2.0 # Double Risk for Hedging
                    logger.warning(f"Hedging Mode: Doubling Risk to {recommended_risk}%")
                
                # Calculate Precise Lot using Quantum Engine
                calc_lot = self.risk_manager.calculate_lot_size(
                    self.symbol, 
                    orb_signal['price'], 
                    smart_sl, 
                    risk_percent=recommended_risk
                )
                
                logger.info(f"Quantum Engine: AI Risk {recommended_risk}% -> Calc Lot {calc_lot} (vs LLM Raw {llm_decision.get('position_size')})")
                
                if calc_lot <= 0:
                    logger.warning("Quantum Engine rejected trade (Lot=0). Risk too high or invalid SL.")
                    return
                
                lot_size = calc_lot
                
            except Exception as e:
                logger.error(f"Quantum Engine Calc Failed: {e}, falling back to LLM size.")
                lot_size = float(llm_decision.get('position_size', 0.01))
                if is_hedging: lot_size *= 2.0
            
            # Format TP Display for Telegram
            tp_display = f"{smart_tp:.2f}"
            if basket_tp > 0:
                tp_display += f" (Basket: ${basket_tp})"
            
            logger.info(f"Executing ORB Trade: {orb_signal['signal'].upper()} | Lot: {lot_size} | Smart SL: {smart_sl} | TP: {smart_tp} | Basket TP: ${basket_tp}")
            
            # --- FORCE STOP GRID STRATEGY & CLOSE COUNTER-TREND POSITIONS ---
            if self.state == "GRID_ACTIVE":
                logger.warning("ORB Breakout Confirmed: STOPPING Grid Strategy & Closing Counter-Trend Positions.")
                # Note: State transition to BREAKOUT_ACTIVE happens in _process_orb_signal_with_state_transition caller
                self.grid_strategy.is_ranging = False 
                self.cancel_all_pending() 
                
                # Close Counter-Trend Positions
                # If ORB Signal is BUY, close SELLS. If SELL, close BUYS.
                positions = mt5.positions_get(symbol=self.symbol)
                if positions:
                    counter_type = mt5.POSITION_TYPE_SELL if orb_signal['signal'] == 'buy' else mt5.POSITION_TYPE_BUY
                    counter_positions = [p for p in positions if p.magic == self.magic_number and p.type == counter_type]
                    
                    if counter_positions:
                        logger.info(f"Closing {len(counter_positions)} counter-trend positions...")
                        self.close_positions(counter_positions, counter_type, reason="ORB Breakout Reversal")
            
            # Notify Telegram with LLM Reasoning
            self.telegram.notify_trade(
                self.symbol, 
                orb_signal['signal'], 
                orb_signal['price'], 
                smart_sl, 
                tp_display, 
                lot_size, 
                mode="BREAKOUT_ACTIVE",
                win_rate=f"{score}% (SMC)",
                reason=reason
            )
            
            # Execute with Smart SL and TP
            self.execute_trade(
                signal=orb_signal['signal'],
                lot=lot_size,
                sl=smart_sl, # <--- Smart SL is passed here
                tp=smart_tp, # <--- Smart TP is passed here (Math Model Fallback)
                comment=f"ORB_SMC_{score}"
            )
            return True # Success
            
        except Exception as e:
            logger.error(f"LLM/Execution Error: {e}")
            return False

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
            
            # Prepare Technical Signals including Grid Config
            tech_signals = {
                "grid_strategy": {
                    "config": self.grid_strategy.get_active_config(),
                    "orb_data": {} # No ORB data for Grid check
                }
            }
            
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
                current_market_data=market_data_input,
                technical_signals=tech_signals # Pass optimization config here
            )
            
            if not llm_decision:
                logger.warning("LLM Grid Analysis returned None/Empty. Skipping.")
                return

            # 3. Parse Decision
            # We expect LLM to return "action": "deploy_grid" or "hold"
            action = llm_decision.get('action', 'hold')
            reason = llm_decision.get('reason', 'Market conditions not optimal')
            trend = llm_decision.get('direction', 'neutral')
            
            # Extract and Apply Basket TP from Grid Analysis as well
            pos_mgmt = llm_decision.get('position_management', {})
            grid_conf = llm_decision.get('grid_config', {})
            basket_tp = pos_mgmt.get('dynamic_basket_tp', 0)
            if not basket_tp:
                basket_tp = grid_conf.get('basket_tp_usd', 0)
                
            if basket_tp > 0:
                self.grid_strategy.update_dynamic_params(
                    basket_tp=basket_tp,
                    basket_tp_long=basket_tp,
                    basket_tp_short=basket_tp
                )
                logger.info(f"LLM Grid Analysis: Updated Basket TP to ${basket_tp}")
            
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
                    
                    # [NEW] Trigger Background Optimization on Grid Start
                    logger.info("Grid Strategy Started: Triggering Background Optimization...")
                    self.run_periodic_optimization(blocking=False)
                    
                    # Notify Telegram
                    self.telegram.notify_grid_deployment(self.symbol, len(orders), trend, current_price, basket_tp=basket_tp)
                    
                    for order in orders:
                        # Handle Control Actions (Clean & Deploy)
                        if order['type'] == 'cancel_all_buy_limits':
                            logger.info("Cleaning up existing Buy Limits...")
                            self.cancel_pending_by_type(mt5.ORDER_TYPE_BUY_LIMIT)
                        elif order['type'] == 'cancel_all_sell_limits':
                            logger.info("Cleaning up existing Sell Limits...")
                            self.cancel_pending_by_type(mt5.ORDER_TYPE_SELL_LIMIT)
                        else:
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

    def _log_heartbeat(self, current_price):
        """Log periodic status update"""
        orb_status = "WAITING"
        if self.orb_strategy.is_range_final:
            orb_status = f"READY [{self.orb_strategy.final_range_low:.2f} - {self.orb_strategy.final_range_high:.2f}] (Time: {self.orb_strategy.range_time_str})"
        
        grid_status = "INACTIVE"
        if self.grid_strategy.is_ranging:
            grid_status = "RANGING"
        
        # Count active orders
        orders = mt5.orders_get(symbol=self.symbol)
        order_count = len(orders) if orders else 0
        positions = mt5.positions_get(symbol=self.symbol)
        pos_count = len(positions) if positions else 0
        
        # Log Heartbeat always (Every 60s)
        logger.info(f"❤️ Heartbeat | Price: {current_price:.2f} | Mode: {self.state} | ORB: {orb_status} | Grid: {grid_status} | Pos: {pos_count} | Orders: {order_count}")

        # Send to Telegram - STRICT FILTER: Only send if there is ACTIVE POSITIONS (Open Trades)
        # We ignore pending orders to reduce spam as requested.
        if pos_count > 0:
            tg_msg = (
                 f"Symbol: `{self.symbol}`\n"
                 f"Price: `{current_price:.2f}`\n"
                 f"Mode: `{self.state}`\n"
                 f"Positions: `{pos_count}`\n"
                 f"Orders: `{order_count}`"
            )
            threading.Thread(target=self.telegram.notify_info, args=("Active Trading Status", tg_msg), daemon=True).start()

    def normalize_volume(self, volume):
        """
        Normalize volume to symbol step and limits.
        """
        symbol_info = mt5.symbol_info(self.symbol)
        if not symbol_info: return volume
        
        step = symbol_info.volume_step
        v_min = symbol_info.volume_min
        v_max = symbol_info.volume_max
        
        # 1. Align to Step
        if step > 0:
            steps = round(volume / step)
            volume = steps * step
            
        # 2. Clamp to Limits
        if v_min > 0: volume = max(v_min, volume)
        if v_max > 0: volume = min(v_max, volume)
        
        # 3. Dynamic Rounding
        decimals = 2
        if step > 0:
            try:
                decimals = max(0, int(-math.log10(step) + 0.5)) 
            except: pass
            
        volume = round(volume, decimals)
        return volume

    # --- Execution Helpers ---
    def execute_trade(self, signal, lot, sl, tp, comment):
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            logger.error(f"Symbol {self.symbol} not found")
            return

        order_type = mt5.ORDER_TYPE_BUY if signal == 'buy' else mt5.ORDER_TYPE_SELL
        tick = mt5.symbol_info_tick(self.symbol)
        price = tick.ask if signal == 'buy' else tick.bid
        
        # Normalize Prices
        tick_size = symbol_info.trade_tick_size
        if tick_size <= 0:
            tick_size = symbol_info.point

        if tick_size > 0:
            if sl > 0: sl = round(sl / tick_size) * tick_size
            if tp > 0: tp = round(tp / tick_size) * tick_size
            
        sl = round(sl, symbol_info.digits)
        tp = round(tp, symbol_info.digits)
        
        # [NEW] Normalize Volume (Prevent 10014)
        raw_lot = lot
        lot = self.normalize_volume(lot)
        
        if raw_lot != lot:
            logger.info(f"Volume Normalized: {raw_lot} -> {lot}")
        
        # [NEW] Dynamic Stops Level Check (Prevent 10016)
        stop_level = symbol_info.trade_stops_level * symbol_info.point
        min_dist = stop_level + (2 * symbol_info.point) # Buffer
        
        if sl > 0:
            dist = abs(price - sl)
            if dist < min_dist:
                old_sl = sl
                if signal == 'buy': # Buy: SL must be below price
                    sl = price - min_dist
                else: # Sell: SL must be above price
                    sl = price + min_dist
                sl = round(sl, symbol_info.digits)
                logger.warning(f"Auto-Adjusting SL (Too Close): {old_sl} -> {sl} (Min Dist: {min_dist})")

        if tp > 0:
            dist = abs(price - tp)
            if dist < min_dist:
                old_tp = tp
                if signal == 'buy': # Buy: TP must be above price
                    tp = price + min_dist
                else: # Sell: TP must be below price
                    tp = price - min_dist
                tp = round(tp, symbol_info.digits)
                logger.warning(f"Auto-Adjusting TP (Too Close): {old_tp} -> {tp} (Min Dist: {min_dist})")

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
            "type_filling": mt5.ORDER_FILLING_FOK, # Default fallback
        }
        
        # Determine correct filling mode dynamically
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info:
             if symbol_info.filling_mode & 1: # FOK
                 request['type_filling'] = mt5.ORDER_FILLING_FOK
             elif symbol_info.filling_mode & 2: # IOC
                 request['type_filling'] = mt5.ORDER_FILLING_IOC
        
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
             # Retry with RETURN if FOK/IOC failed
             if result.retcode == 10030:
                 logger.warning(f"Filling mode failed, retrying with RETURN...")
                 request['type_filling'] = mt5.ORDER_FILLING_RETURN
                 result = mt5.order_send(request)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"Trade Failed: {result.comment} ({result.retcode})")
            self.telegram.notify_error(f"Trade Execution ({signal})", f"{result.comment} ({result.retcode})")
        else:
            logger.info(f"Trade Executed: {result.order}")
            
            # --- Post-Trade Validation (Smart SL/TP) ---
            # Some brokers (ECN/STP) ignore SL/TP in Market Execution. We must verify and update if needed.
            if sl > 0 or tp > 0:
                time.sleep(0.5) # Wait for broker to process
                positions = mt5.positions_get(ticket=result.order)
                
                if positions:
                    pos = positions[0]
                    needs_update = False
                    
                    # Check SL
                    if sl > 0 and abs(pos.sl - sl) > 0.001:
                        logger.warning(f"Order SL mismatch (Set: {sl}, Actual: {pos.sl}). Updating...")
                        needs_update = True
                        
                    # Check TP (only if we set one, usually we use Basket)
                    if tp > 0 and abs(pos.tp - tp) > 0.001:
                        logger.warning(f"Order TP mismatch (Set: {tp}, Actual: {pos.tp}). Updating...")
                        needs_update = True
                        
                    if needs_update:
                        req_update = {
                            "action": mt5.TRADE_ACTION_SLTP,
                            "position": result.order,
                            "symbol": self.symbol,
                            "sl": float(sl),
                            "tp": float(tp),
                            "magic": self.magic_number
                        }
                        res_update = mt5.order_send(req_update)
                        if res_update.retcode == mt5.TRADE_RETCODE_DONE:
                            logger.info(f"Position #{result.order} SL/TP Updated Successfully.")
                        else:
                            logger.error(f"Failed to update SL/TP for #{result.order}: {res_update.comment}")
                            self.telegram.notify_error(f"SL/TP Update Fail #{result.order}", res_update.comment)

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
        
        # [NEW] Normalize Volume for Pending Orders (Prevent 10014)
        raw_volume = float(order_dict.get('volume', 0.01))
        volume = self.normalize_volume(raw_volume)
        
        if raw_volume != volume:
            logger.info(f"Pending Order Volume Normalized: {raw_volume} -> {volume}")

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
            # Add a small buffer to be safe (e.g. 2 points)
            buffer = 2 * symbol_info.point
            
            if mt5_type == mt5.ORDER_TYPE_BUY_LIMIT:
                if price >= tick.ask:
                    # If price is already above Ask, Limit Buy is invalid (becomes market).
                    # But for Grid, maybe we just want to skip or place at Ask?
                    # Let's skip to be safe, or adjust to Ask - StopLevel if that was the intent.
                    logger.warning(f"Skipping Buy Limit @ {price} >= Ask {tick.ask}")
                    return
                
                if (tick.ask - price) < stop_level:
                    # Auto-adjust price to be valid
                    new_price = tick.ask - stop_level - buffer
                    new_price = round(new_price, symbol_info.digits)
                    logger.info(f"Adjusting Buy Limit Price: {price} -> {new_price} (Too close to Ask {tick.ask}, StopLevel {stop_level})")
                    price = new_price
                    
            elif mt5_type == mt5.ORDER_TYPE_SELL_LIMIT:
                if price <= tick.bid:
                    logger.warning(f"Skipping Sell Limit @ {price} <= Bid {tick.bid}")
                    return
                
                if (price - tick.bid) < stop_level:
                    # Auto-adjust price to be valid
                    new_price = tick.bid + stop_level + buffer
                    new_price = round(new_price, symbol_info.digits)
                    logger.info(f"Adjusting Sell Limit Price: {price} -> {new_price} (Too close to Bid {tick.bid}, StopLevel {stop_level})")
                    price = new_price

        # [NEW] Check SL/TP vs Limit Price (Prevent 10016 for Pending Orders)
        sl = float(order_dict.get('sl', 0))
        tp = float(order_dict.get('tp', 0))
        
        # Re-calculate min_dist in case it wasn't set above (if tick was None)
        stop_level = symbol_info.trade_stops_level * symbol_info.point
        min_dist = stop_level + (2 * symbol_info.point)
        
        if sl > 0:
            if abs(price - sl) < min_dist:
                old_sl = sl
                if mt5_type == mt5.ORDER_TYPE_BUY_LIMIT: # SL below Entry
                    sl = price - min_dist
                else: # SL above Entry
                    sl = price + min_dist
                sl = round(sl, symbol_info.digits)
                logger.warning(f"Auto-Adjusting Grid Order SL: {old_sl} -> {sl} (Entry: {price})")

        if tp > 0:
            if abs(price - tp) < min_dist:
                old_tp = tp
                if mt5_type == mt5.ORDER_TYPE_BUY_LIMIT: # TP above Entry
                    tp = price + min_dist
                else: # TP below Entry
                    tp = price - min_dist
                tp = round(tp, symbol_info.digits)
                logger.warning(f"Auto-Adjusting Grid Order TP: {old_tp} -> {tp} (Entry: {price})")

        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": self.symbol,
            "volume": float(volume),
            "type": mt5_type,
            "price": price,

            "sl": float(sl),
            "tp": float(tp),
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

    def cancel_pending_by_type(self, order_type):
        """
        Cancel pending orders of a specific type (e.g. ORDER_TYPE_BUY_LIMIT)
        """
        orders = mt5.orders_get(symbol=self.symbol)
        if orders:
            for order in orders:
                if order.magic == self.magic_number and order.type == order_type:
                    request = {
                        "action": mt5.TRADE_ACTION_REMOVE,
                        "order": order.ticket,
                        "magic": self.magic_number,
                    }
                    result = mt5.order_send(request)
                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        logger.info(f"Cancelled Specific Order #{order.ticket} (Type: {order_type})")
                    else:
                        logger.warning(f"Failed to cancel Specific Order #{order.ticket}: {result.comment}")

    def close_positions(self, positions, type_filter, reason):
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            logger.error(f"Cannot close positions: Symbol {self.symbol} not found")
            return

        # Determine correct filling mode
        filling_mode = mt5.ORDER_FILLING_FOK # Default fallback
        try:
            fill_flags = symbol_info.filling_mode
            if fill_flags & 2: # SYMBOL_FILLING_IOC
                filling_mode = mt5.ORDER_FILLING_IOC
            elif fill_flags & 1: # SYMBOL_FILLING_FOK
                filling_mode = mt5.ORDER_FILLING_FOK
        except Exception:
            filling_mode = mt5.ORDER_FILLING_IOC # Common default
            
        for pos in positions:
            if pos.magic == self.magic_number and pos.type == type_filter:
                # Check if position still exists
                if not mt5.positions_get(ticket=pos.ticket):
                    logger.info(f"Position #{pos.ticket} already closed.")
                    continue

                # Retry logic for closing
                # Try different filling modes in sequence if one fails
                filling_modes_to_try = [filling_mode, mt5.ORDER_FILLING_IOC, mt5.ORDER_FILLING_FOK, mt5.ORDER_FILLING_RETURN]
                # Remove duplicates
                filling_modes_to_try = list(dict.fromkeys(filling_modes_to_try))
                
                success = False
                for attempt in range(5): # Increased retries
                    if success: break
                    
                    # Refresh tick
                    tick = mt5.symbol_info_tick(self.symbol)
                    if tick is None:
                        time.sleep(0.5)
                        continue
                        
                    price = tick.bid if pos.type == mt5.POSITION_TYPE_BUY else tick.ask
                    
                    # Try filling modes
                    for f_mode in filling_modes_to_try:
                        request = {
                            "action": mt5.TRADE_ACTION_DEAL,
                            "symbol": self.symbol,
                            "volume": float(pos.volume),
                            "type": mt5.ORDER_TYPE_SELL if pos.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                            "position": int(pos.ticket),
                            "price": float(price),
                            "deviation": 100, # Increased deviation for closing
                            "magic": self.magic_number,
                            "comment": "Basket Close", # Force simple comment to avoid -2 Invalid Argument
                            "type_time": mt5.ORDER_TIME_GTC,
                            "type_filling": f_mode,
                        }
                        
                        result = mt5.order_send(request)
                        
                        if result is None:
                            logger.error(f"Order Send Failed (None) for #{pos.ticket}. Error: {mt5.last_error()}")
                            continue
                            
                        if result.retcode == mt5.TRADE_RETCODE_DONE:
                            logger.info(f"Position #{pos.ticket} Closed: {reason} | Price: {result.price}")
                            success = True
                            break # Break filling mode loop
                        elif result.retcode == 10030: # Unsupported filling mode
                            logger.warning(f"Filling mode {f_mode} unsupported, trying next...")
                            continue # Try next filling mode
                        elif result.retcode == 10004: # Requote
                             logger.warning(f"Requote for #{pos.ticket}, retrying...")
                             break # Break filling loop to refresh price
                        elif result.retcode == 10027: # AutoTrading Disabled
                             logger.error("AutoTrading Disabled in Client! Please enable it.")
                             success = True # Stop retrying to avoid spam
                             break
                        else:
                            logger.error(f"Failed to Close #{pos.ticket} (Att {attempt+1}, Mode {f_mode}): {result.comment} ({result.retcode})")
                            
                    if not success:
                        time.sleep(0.5) # Wait before next attempt
                
                if not success:
                    try:
                        self.telegram.notify_error(f"Close Fail #{pos.ticket}", "Max retries/modes exceeded")
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
