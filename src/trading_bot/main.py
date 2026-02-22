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
    from analysis.confluence_analyzer import TrendlineAnalyzer, MomentumAnalyzer, ConfluenceAnalyzer
    from analysis.smc_validator import SMCQualityValidator
    from analysis.breakout_quality_filter import BreakoutQualityFilter
    from position_engine.mt5_adapter import MT5RiskManager
    from analysis.advanced_analysis import AdvancedMarketAnalysisAdapter
    from utils.file_watcher import FileWatcher # Restore FileWatcher
    from utils.telegram_notifier import TelegramNotifier # Add Telegram Notifier
    
    # AI System Integrations
    from analysis.factor_discovery import FactorDiscovery
    from analysis.pattern_recognition_system import PatternRecognitionSystem
    
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

try:
    from strategies.orb_strategy import GoldORBStrategy
except Exception:
    GoldORBStrategy = None

try:
    from analysis.pattern_recognition_system import PatternRecognitionSystem
except ImportError:
    PatternRecognitionSystem = None

try:
    from analysis.factor_discovery import FactorDiscovery
except ImportError:
    FactorDiscovery = None

try:
    from analysis.enhanced_optimization import EnhancedOptimizationEngine
except ImportError:
    EnhancedOptimizationEngine = None

load_dotenv()

class DummyConfig:
    def __init__(self):
        self.smc_weight = 2.0
        self.trendline_weight = 1.5
        self.ema_weight = 1.0
        self.macd_weight = 1.0
        self.ob_fvg_weight = 1.5
        self.full_position_threshold = 5.0
        self.half_position_threshold = 3.5

class SymbolTrader:
    def __init__(self, symbol="GOLD", timeframe=mt5.TIMEFRAME_M5, account_index=1):
        self.symbol = symbol.strip() if isinstance(symbol, str) else symbol
        self.timeframe = timeframe
        self.account_index = account_index
        self.magic_number = 888888
        
        # Confluence Config
        self.confluence_config = DummyConfig()
        
        # 1. Initialize Strategies & Analyzers
        self.trendline_analyzer = TrendlineAnalyzer(self.confluence_config)
        self.momentum_analyzer = MomentumAnalyzer(self.confluence_config)
        self.confluence_analyzer = ConfluenceAnalyzer(self.confluence_config)
        self.smc_validator = SMCQualityValidator()
        self.quality_filter = BreakoutQualityFilter()
        self.advanced_analysis = AdvancedMarketAnalysisAdapter()
        self.data_processor = MT5DataProcessor()
        self.risk_manager = MT5RiskManager()
        
        # 2. AI Client
        self.ai_factory = AIClientFactory()
        self.llm_client = self.ai_factory.create_client("qwen") 
        
        self.pattern_recognizer = PatternRecognitionSystem() if PatternRecognitionSystem else None
        self.factor_discovery = FactorDiscovery() if FactorDiscovery else None
        
        if EnhancedOptimizationEngine:
            param_bounds = {
                'smc_weight': (0.5, 3.0),
                'trendline_weight': (0.5, 3.0),
                'ema_weight': (0.5, 2.0),
                'macd_weight': (0.5, 2.0),
                'ob_fvg_weight': (0.5, 3.0),
                'full_position_threshold': (3.0, 7.0),
                'half_position_threshold': (2.0, 5.0)
            }
            self.enhanced_optimizer = EnhancedOptimizationEngine(
                param_bounds=param_bounds,
                optimization_mode='adaptive',
                model_type='qwen'
            )
            # Set initial params:
            initial_params = {
                'smc_weight': self.confluence_config.smc_weight,
                'trendline_weight': self.confluence_config.trendline_weight,
                'ema_weight': self.confluence_config.ema_weight,
                'macd_weight': self.confluence_config.macd_weight,
                'ob_fvg_weight': self.confluence_config.ob_fvg_weight,
                'full_position_threshold': self.confluence_config.full_position_threshold,
                'half_position_threshold': self.confluence_config.half_position_threshold
            }
            self.enhanced_optimizer.set_current_params(initial_params)
        else:
            self.enhanced_optimizer = None
        
        # 3. Notifiers
        self.telegram = TelegramNotifier()
        
        # Market State and Performance for AI Tuner
        self.current_market_state = {}
        self.performance_metrics = {
            'return': 0.0,
            'sharpe': 0.0,
            'max_drawdown': 0.0,
            'total_trades': 0,
            'winning_trades': 0
        }
        
        # 4. State Machine (Dynamic Risk)
        # States: OBSERVATION, BREAKOUT_ACTIVE
        self.state = "OBSERVATION" 
        
        self.last_tick_time = 0
        self.last_analysis_time = 0
        self.last_state_change = 0
        self.last_orb_filter_time = 0 
        self.orb_cooldowns = {'buy': 0, 'sell': 0} 
        self.last_heartbeat_time = 0 
        self.last_pos_count = 0
        self.last_analysis_result = {}
        self.watcher = None 
        self.is_optimizing = False 
        self.atr_breakeven_triggered = set()
        self.orb_strategy = None
        
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

        if GoldORBStrategy:
            self.orb_strategy = GoldORBStrategy(self.symbol)
        
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
        if not self.initialize():
            logger.error("Failed to initialize MT5")
            return

        # Start File Watcher
        if FileWatcher:
            self.watcher = FileWatcher([os.path.join(src_dir, 'trading_bot'), os.path.join(src_dir, 'analysis'), os.path.join(src_dir, 'utils')])
            self.watcher.start()
            logger.info("File watcher started for hot reloading.")
            
        logger.info(f"Started monitoring {self.symbol}...")
        self.telegram.send_message(f"🚀 Bot Started\nSymbol: {self.symbol}\nMode: Confluence Analyzer Strategy")

        try:
            while True:
                tick = mt5.symbol_info_tick(self.symbol)
                if tick:
                    self.process_tick(tick)
                    self._log_heartbeat(tick.bid)
                    
                    # Check for parameter optimization schedule
                    if self.enhanced_optimizer and (time.time() - self.last_optimization_time > self.optimization_interval):
                        try:
                            logger.info("Executing periodic AI Parameter Adjustments...")
                            self.enhanced_optimizer.monitor_and_adjust(
                                current_performance=self.performance_metrics,
                                market_data=self.current_market_state
                            )
                            # Sync back changes
                            if self.enhanced_optimizer.adaptive_tuner:
                                new_params = self.enhanced_optimizer.adaptive_tuner.current_params
                                if new_params:
                                    for k, v in new_params.items():
                                        if hasattr(self.confluence_config, k):
                                            setattr(self.confluence_config, k, v)
                                    logger.info(f"Confluence config synced with AI Tuner")
                            self.last_optimization_time = time.time()
                        except Exception as e:
                            logger.error(f"Enhanced Optimization failed: {e}", exc_info=True)

                time.sleep(1.0) # 1s loop
                
        except KeyboardInterrupt:
            logger.info("\nStopping bot...")
        except Exception as e:
            logger.error(f"Loop Error: {e}", exc_info=True)
            self.telegram.send_message(f"🚨 Bot Crashed\nError: {str(e)}")
        finally:
            mt5.shutdown()
            if self.watcher:
                self.watcher.stop()

    def process_tick(self, tick):
        current_price = tick.bid
        current_time = time.time()
        
        # 1. Update Candle Data Structure periodically (every 1M candle close approx)
        if current_time - self.last_analysis_time >= 60:
            self.update_candle_data()
            self.last_analysis_time = current_time
            
            # Analyze Market Confluence
            self._analyze_confluence(current_price)

        # 2. Risk Management (Real-time checks)
        self.manage_positions(current_price)

    def _analyze_confluence(self, current_price):
        # Timeframes aligned with ConfluenceAnalyzer specs
        # Higher timeframe for SMC, lower for trend/momentum
        htf = mt5.TIMEFRAME_M15
        ltf = mt5.TIMEFRAME_M5
        
        smc_data = self.smc_validator.analyze_market_structure(self.symbol, htf)
        trendline_data = self.trendline_analyzer.analyze(self.symbol, ltf)
        momentum_data = self.momentum_analyzer.analyze(self.symbol, ltf)
        
        # Record Market State for AI Tuner
        try:
            self.current_market_state = {
                'trend_strength': 1.0 if momentum_data and momentum_data.get('ema_position') != 0 else 0.0,
                'volatility': 0.5, # Rough proxy until ATR integration
                'volume_ratio': 1.0, 
                'sentiment': smc_data.get('market_bias', 0) if smc_data else 0,
                'momentum': momentum_data.get('ema_position', 0) if momentum_data else 0,
                'choppiness_index': 0.5 
            }
        except Exception:
            pass
        
        # AI System Integrations
        df_ltf = None
        try:
            df_ltf = self.get_dataframe(ltf, 1000)
        except Exception:
            pass

        if self.pattern_recognizer and df_ltf is not None and not df_ltf.empty:
            try:
                # Need to use the correct API `analyze_market`
                pattern_result = self.pattern_recognizer.analyze_market(df_ltf)
                if pattern_result and 'comprehensive_analysis' in pattern_result:
                    signal = pattern_result['comprehensive_analysis'].get('signal')
                    logger.info(f"AI Pattern Identified Signal: {signal}")
            except Exception as e:
                logger.debug(f"Pattern Recognition failed softly: {e}")
                
        if self.factor_discovery and df_ltf is not None and not df_ltf.empty:
            try:
                factors = self.factor_discovery.discover_factors(df_ltf)
                if factors:
                    logger.debug(f"AI Factors updated: {list(factors.keys())}")
            except Exception as e:
                logger.debug(f"Factor Discovery failed softly: {e}")
            
        confluence_result = self.confluence_analyzer.calculate_confluence_score(
            smc_data, trendline_data, momentum_data
        )
        
        score = confluence_result['score']
        details = confluence_result['details']
        
        # Inject Pattern Recognition Bias into Confluence Score
        pattern_signal = None
        if 'pattern_result' in locals() and pattern_result and 'comprehensive_analysis' in pattern_result:
            pattern_signal = pattern_result['comprehensive_analysis'].get('signal')
            conf = pattern_result['comprehensive_analysis'].get('confidence', 0)
            if pattern_signal == 'buy':
                score += (2.0 * conf) # Add up to 2 points for strong pattern buy
                details['pattern_bonus'] = f"+{2.0 * conf:.2f} (Buy Pattern)"
            elif pattern_signal == 'sell':
                score += (2.0 * conf)
                details['pattern_bonus'] = f"+{2.0 * conf:.2f} (Sell Pattern)"
        
        if score >= self.confluence_config.half_position_threshold:
            multiplier = self.confluence_analyzer.determine_position_size_multiplier(confluence_result)
            
            # Determine direction based on Momentum + SMC
            direction = None
            if momentum_data and momentum_data['ema_position'] == 1 and (smc_data is None or smc_data.get('market_bias') != -1):
                direction = "bullish"
            elif momentum_data and momentum_data['ema_position'] == -1 and (smc_data is None or smc_data.get('market_bias') != 1):
                direction = "bearish"
                
            if direction and (time.time() - self.last_orb_filter_time > 300): # Repurposing last_orb_filter_time as trade cooldown
                logger.info(f"High Confluence ({score}) Signal Detected: {direction}. Details: {details}")
                self.last_orb_filter_time = time.time()
                self._execute_confluence_trade(direction, multiplier, current_price, smc_data, momentum_data, score, details)

    def _execute_confluence_trade(self, direction, multiplier, current_price, smc_data, momentum_data, score=0, details=None):
        """Execute trade based on Confluence Score"""
        details = details or {}
        positions = mt5.positions_get(symbol=self.symbol)
        
        # Max open positions check (simple)
        if positions and len(positions) >= 2:
            return
            
        # Calculate Lot Size
        # Determine standard lot based on account free margin, then apply multiplier
        account_info = mt5.account_info()
        base_lot = 0.01  # Default fallback
        if account_info:
            margin_free = account_info.margin_free
            base_lot = self.normalize_volume(margin_free * 0.00001) # Very rough risk
            
        optimal_lot = self.normalize_volume(base_lot * multiplier)
        if optimal_lot <= 0: return

        # Calculate SL/TP
        if direction == "bullish":
            trade_type = mt5.ORDER_TYPE_BUY
            sl = current_price * 0.995 # fallback
            # Look for recent FVG or EMA for SL
            if momentum_data and momentum_data.get('ema'):
                sl = momentum_data['ema'] * 0.998
            if sl >= current_price:
                sl = current_price * 0.995
            tp = current_price + (current_price - sl) * 2 # 1:2 RRR fallback
        else:
            trade_type = mt5.ORDER_TYPE_SELL
            sl = current_price * 1.005 # fallback
            if momentum_data and momentum_data.get('ema'):
                sl = momentum_data['ema'] * 1.002
            if sl <= current_price:
                sl = current_price * 1.005
            tp = current_price - (sl - current_price) * 2 # 1:2 RRR fallback
            
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info:
            digits = symbol_info.digits
            point = symbol_info.point
            stops_level = symbol_info.trade_stops_level * point
            if stops_level == 0:
                stops_level = point * 10 # Some brokers return 0 but still have a minimum

            # Enforce minimal stop level distance 
            if direction == "bullish":
                if current_price - sl <= stops_level:
                    sl = current_price - stops_level * 1.5
                if tp - current_price <= stops_level:
                    tp = current_price + stops_level * 1.5
            else:
                if sl - current_price <= stops_level:
                    sl = current_price + stops_level * 1.5
                if current_price - tp <= stops_level:
                    tp = current_price - stops_level * 1.5
                    
            sl = round(sl, digits)
            tp = round(tp, digits)
        
        filling_mode = mt5.ORDER_FILLING_FOK
        try:
            fill_flags = symbol_info.filling_mode
            logger.info(f"Symbol {self.symbol} filling_mode_flags: {fill_flags}")
            if fill_flags & 2:
                filling_mode = mt5.ORDER_FILLING_IOC
                logger.info("Detected IOC support, will try IOC first")
            elif fill_flags & 1:
                filling_mode = mt5.ORDER_FILLING_FOK
                logger.info("Detected FOK support, will try FOK first")
        except Exception as e:
            filling_mode = mt5.ORDER_FILLING_IOC
            logger.warning(f"Could not detect filling mode, using IOC default. Error: {e}")

        filling_modes_to_try = [filling_mode, mt5.ORDER_FILLING_IOC, mt5.ORDER_FILLING_FOK, mt5.ORDER_FILLING_RETURN]
        filling_modes_to_try = list(dict.fromkeys(filling_modes_to_try))
        logger.info(f"Will try filling modes in order: {[{mt5.ORDER_FILLING_IOC: 'IOC', mt5.ORDER_FILLING_FOK: 'FOK', mt5.ORDER_FILLING_RETURN: 'RETURN'}.get(m, str(m)) for m in filling_modes_to_try]}")

        success = False
        last_result = None
        for attempt in range(3):
            if success:
                break

            tick = mt5.symbol_info_tick(self.symbol)
            if tick is None:
                time.sleep(0.5)
                continue

            price = tick.ask if trade_type == mt5.ORDER_TYPE_BUY else tick.bid

            for f_mode in filling_modes_to_try:
                mode_name = {mt5.ORDER_FILLING_IOC: 'IOC', mt5.ORDER_FILLING_FOK: 'FOK', mt5.ORDER_FILLING_RETURN: 'RETURN'}.get(f_mode, str(f_mode))
                logger.info(f"Attempting Confluence trade with {mode_name} mode (attempt {attempt+1}/3)")
                
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.symbol,
                    "volume": float(optimal_lot),
                    "type": trade_type,
                    "price": float(price),
                    "sl": float(sl),
                    "tp": float(tp),
                    "deviation": 20,
                    "magic": self.magic_number,
                    "comment": "Confluence Exec",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": f_mode,
                }

                result = mt5.order_send(request)
                last_result = result

                if result is None:
                    logger.error(f"Confluence Execution Failed (None): {mt5.last_error()}")
                    continue

                logger.info(f"Order send result with {mode_name}: retcode={result.retcode}, comment={result.comment}")

                if result.retcode == mt5.TRADE_RETCODE_DONE:
                    logger.info(f"Confluence Trade Executed: {direction} Lot: {optimal_lot} Score: {multiplier}")
                    self.telegram.send_message(f"🏆 Confluence Trade\nDir: {direction}\nLot: {optimal_lot}\nEntry: {price}\nSL: {sl:.2f}\nTP: {tp:.2f}")
                    success = True
                    break

                if result.retcode == 10030:
                    logger.warning(f"Filling mode {mode_name} not supported (retcode 10030), trying next mode...")
                    continue

                if result.retcode == 10016:
                    logger.warning(f"Invalid stops (10016). Retrying without SL/TP...")
                    request["sl"] = 0.0
                    request["tp"] = 0.0
                    result_no_stops = mt5.order_send(request)
                    if result_no_stops is not None and result_no_stops.retcode == mt5.TRADE_RETCODE_DONE:
                        logger.info(f"Trade executed without stops. Attempting to modify position...")
                        # Modify position
                        mod_request = {
                            "action": mt5.TRADE_ACTION_SLTP,
                            "symbol": self.symbol,
                            "sl": float(sl),
                            "tp": float(tp),
                            "position": result_no_stops.order
                        }
                        mod_result = mt5.order_send(mod_request)
                        if mod_result is not None and mod_result.retcode == mt5.TRADE_RETCODE_DONE:
                            logger.info("Successfully modified SL/TP.")
                        else:
                            logger.error(f"Failed to modify SL/TP: {mod_result.comment if mod_result else 'None'}")
                        self.telegram.send_message(f"🏆 Confluence Trade (Modified SL/TP)\nDir: {direction}\nLot: {optimal_lot}\nEntry: {price}\nSL: {sl:.2f}\nTP: {tp:.2f}")
                        success = True
                        break
                    else:
                        logger.error(f"Failed to execute even without stops. Retcode: {result_no_stops.retcode if result_no_stops else 'None'}")

                if result.retcode == 10004:
                    logger.warning(f"Requote (retcode 10004), will refresh price and retry...")
                    break

                if result.retcode == 10027:
                    logger.error("AutoTrading Disabled in Client! Please enable it.")
                    success = True
                    break

            if not success:
                time.sleep(0.5)

        if not success:
            if last_result is None:
                logger.error("Confluence Execution Failed: No result from MT5")
            else:
                logger.error(f"Confluence Execution Failed: All filling modes failed. Last result: retcode={last_result.retcode}, comment={last_result.comment}, request_volume={optimal_lot}, symbol={self.symbol}")
                logger.error(f"Last order details: price={price}, sl={sl}, tp={tp}")

    def update_candle_data(self):
        # Fetch M5 Data
        rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, 500)
        if rates is not None:
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            # Rename tick_volume to volume for compatibility with analysis modules
            if 'tick_volume' in df.columns and 'volume' not in df.columns:
                df.rename(columns={'tick_volume': 'volume'}, inplace=True)
            
            # Update SMC Analyzer's internal data if it uses it
            if hasattr(self.smc_validator, 'update_data'):
                self.smc_validator.update_data(df)
            if hasattr(self.trendline_analyzer, 'update_data'):
                self.trendline_analyzer.update_data(df)
            if hasattr(self.momentum_analyzer, 'update_data'):
                self.momentum_analyzer.update_data(df)

    def manage_positions(self, current_price):
        """
        Unified Risk Management
        """
        positions = mt5.positions_get(symbol=self.symbol)
        
        # Record Performance for AI Tuner proxy
        if self.enhanced_optimizer:
            account_info = mt5.account_info()
            if account_info:
                self.performance_metrics['return'] = account_info.profit
                
        if positions:
            # Simple check for positions opened by this bot
            bot_positions = [p for p in positions if p.magic == self.magic_number]
            
            # Example: Close positions if they hit a certain profit target or time limit
            for pos in bot_positions:
                profit = pos.profit
                
                # Close if profit is very high (e.g., 5% of initial margin)
                # This is a placeholder for more sophisticated exit logic
                if profit > 0 and profit / pos.volume / pos.price_open > 0.005: # 0.5% profit
                    logger.info(f"Closing position #{pos.ticket} due to high profit: {profit:.2f}")
                    self.close_positions([pos], pos.type, "High Profit Target")
                    self.telegram.send_message(f"✅ Position #{pos.ticket} closed with profit: {profit:.2f}")
                
                # Close if position is open for too long (e.g., 4 hours)
                if (time.time() - pos.time_msc / 1000) > (4 * 3600):
                    logger.info(f"Closing position #{pos.ticket} due to time limit.")
                    self.close_positions([pos], pos.type, "Time Limit Exceeded")
                    self.telegram.send_message(f"⏳ Position #{pos.ticket} closed due to time limit.")

    def _log_heartbeat(self, current_price):
        """Log periodic status update"""
        
        # Count active orders
        orders = mt5.orders_get(symbol=self.symbol)
        order_count = len(orders) if orders else 0
        positions = mt5.positions_get(symbol=self.symbol)
        pos_count = len(positions) if positions else 0
        
        # Log Heartbeat always (Every 60s)
        if time.time() - self.last_heartbeat_time > 60:
            logger.info(f"❤️ Heartbeat | Price: {current_price:.2f} | Pos: {pos_count} | Orders: {order_count}")
            self.last_heartbeat_time = time.time()

        # Send to Telegram - STRICT FILTER: Only send if there is ACTIVE POSITIONS (Open Trades)
        # We ignore pending orders to reduce spam as requested.
        # [MODIFIED] Only send when position count increases from 0 (First Open)
        if pos_count > 0 and self.last_pos_count == 0:
            # Get Position Details (SL/TP)
            sl_text = "None"
            tp_text = "None"
            
            symbol_info = mt5.symbol_info(self.symbol)
            decimals = symbol_info.digits if symbol_info else 2
            
            if positions:
                # Use the first position's SL/TP as reference
                first_pos = positions[0]
                sl_text = f"{first_pos.sl:.{decimals}f}" if first_pos.sl > 0 else "None"
                tp_text = f"{first_pos.tp:.{decimals}f}" if first_pos.tp > 0 else "None"
                
            tg_msg = (
                 f"Symbol: `{self.symbol}`\n"
                 f"Price: `{current_price:.2f}`\n"
                 f"Positions: `{pos_count}`\n"
                 f"SL: `{sl_text}`\n"
                 f"TP: `{tp_text}`\n"
                 f"Orders: `{order_count}`"
            )
            # DO NOT spam telegram with heartbeats as requested by user
            # threading.Thread(target=self.telegram.notify_info, args=("Active Trading Status", tg_msg), daemon=True).start()
        
        # Update state tracking
        self.last_pos_count = pos_count

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
        target_symbol = sys.argv[1].strip()
    if len(sys.argv) > 2:
        try:
            target_account = int(sys.argv[2])
        except ValueError:
            pass

    bot = SymbolTrader(target_symbol, account_index=target_account)
    if bot.initialize():
        bot.run()

