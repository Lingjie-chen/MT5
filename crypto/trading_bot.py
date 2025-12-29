import time
import logging
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

from .okx_data_processor import OKXDataProcessor
from .ai_client_factory import AIClientFactory
from .database_manager import DatabaseManager
from .advanced_analysis import AdvancedMarketAnalysis, SMCAnalyzer, MFHAnalyzer, MTFAnalyzer, PEMAnalyzer, MatrixMLAnalyzer
from .optimization import WOAm

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("trading_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CryptoTradingBot:
    def __init__(self, symbol='ETH/USDT', timeframe='15m', interval=3600):
        """
        Initialize the Crypto Trading Bot
        
        Args:
            symbol (str): Trading pair
            timeframe (str): Candle timeframe (e.g., '15m', '1h', '4h')
            interval (int): Loop interval in seconds
        """
        self.symbol = symbol
        self.timeframe = timeframe
        self.interval = interval
        self.is_running = False
        
        # Optimization Engine (WOAm - Whale Optimization Algorithm Modified)
        # Used for real-time parameter tuning based on recent market data
        self.optimizer = WOAm(pop_size=10) # Lightweight population for speed
        self.last_optimization_time = 0
        self.optimization_interval = 3600 * 4 # Re-optimize every 4 hours
        
        # Adaptive Parameters (Initial defaults for Medium-term Strategy)
        self.strategy_params = {
            'crt_range_period': 20,       # Wider range for medium-term
            'crt_confirm_period': 2,
            'rvgi_sma_period': 30,
            'rvgi_cci_period': 14,
            'ifvg_min_gap': 50            # Tighter gap check for crypto
        }
        
        # Initialize Data Processor
        self.data_processor = OKXDataProcessor()

        # Initialize Advanced Analysis
        self.advanced_analysis = AdvancedMarketAnalysis()
        self.smc_analyzer = SMCAnalyzer()
        self.mfh_analyzer = MFHAnalyzer()
        self.mtf_analyzer = MTFAnalyzer()
        self.pem_analyzer = PEMAnalyzer()
        self.matrix_ml = MatrixMLAnalyzer()

        # Initialize Database Manager
        # Using a dedicated database file for Crypto strategy to keep it separate from Gold strategy
        # Ensure db is stored in the same directory as this script
        current_dir = os.path.dirname(os.path.realpath(__file__))
        db_path = os.path.join(current_dir, 'crypto_trading.db')
        self.db_manager = DatabaseManager(db_name=db_path)
        
        # Initialize AI Clients
        self.ai_factory = AIClientFactory()
        self.deepseek_client = self.ai_factory.get_client('deepseek')
        self.qwen_client = self.ai_factory.get_client('qwen')
        
        # Telegram Configuration
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not self.deepseek_client or not self.qwen_client:
            logger.warning("AI Clients not fully initialized. Trading functionality may be limited.")

    def send_telegram_message(self, message):
        """Send message to Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code != 200:
                logger.error(f"Failed to send Telegram message: {response.text}")
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")

    def _load_opt_history(self):
        """Load optimization history for seeding"""
        if not os.path.exists(self.opt_history_path):
            return []
        try:
            with open(self.opt_history_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load optimization history: {e}")
            return []

    def _save_opt_history(self, params, score):
        """Save optimization result"""
        history = self._load_opt_history()
        # Add new result
        history.append({
            'timestamp': time.time(),
            'params': list(params), # Convert numpy array to list
            'score': float(score)
        })
        # Keep top 50
        history = sorted(history, key=lambda x: x['score'], reverse=True)[:50]
        try:
            with open(self.opt_history_path, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save optimization history: {e}")
            
    def optimize_parameters(self, df):
        """Run real-time parameter optimization"""
        logger.info("Running real-time parameter optimization...")
        
        # Define objective function: Maximize returns on recent data
        def objective_function(params):
            # params: [crt_range, crt_confirm, rvgi_sma, rvgi_cci, ifvg_gap]
            p_crt_range = int(params[0])
            p_crt_confirm = int(params[1])
            p_rvgi_sma = int(params[2])
            p_rvgi_cci = int(params[3])
            p_ifvg_gap = int(params[4])
            
            # Backtest loop on the last 100 candles
            # We use a simplified loop for performance
            score = 0
            trades = 0
            wins = 0
            
            # To avoid re-calculating everything inside the loop, we pick a sample
            # But indicators depend on lookback.
            # We iterate every 5th candle to speed up
            test_indices = range(len(df)-100, len(df)-1, 5)
            
            for i in test_indices:
                if i < 50: continue
                sub_df = df.iloc[:i+1]
                
                # Future result (1 candle later)
                future_close = df.iloc[i+1]['close']
                current_close = df.iloc[i]['close']
                
                # 1. CRT
                crt = self.advanced_analysis.analyze_crt_strategy(sub_df, range_period=p_crt_range, confirm_period=p_crt_confirm)
                
                # 2. RVGI
                rvgi = self.advanced_analysis.analyze_rvgi_cci_strategy(sub_df, sma_period=p_rvgi_sma, cci_period=p_rvgi_cci)
                
                # 3. IFVG
                ifvg = self.advanced_analysis.analyze_ifvg(sub_df, min_gap_points=p_ifvg_gap)
                
                # Vote
                vote = 0
                if crt['signal'] == 'buy': vote += 1
                elif crt['signal'] == 'sell': vote -= 1
                
                if rvgi['signal'] == 'buy': vote += 1
                elif rvgi['signal'] == 'sell': vote -= 1
                
                if ifvg['signal'] == 'buy': vote += 1
                elif ifvg['signal'] == 'sell': vote -= 1
                
                if vote > 0: # Buy
                    trades += 1
                    if future_close > current_close: wins += 1
                    else: score -= 1
                elif vote < 0: # Sell
                    trades += 1
                    if future_close < current_close: wins += 1
                    else: score -= 1
                    
            if trades == 0: return 0
            win_rate = wins / trades
            final_score = (win_rate * 100) + (trades * 2) # Reward activity slightly
            return final_score

        # Bounds: [crt_range, crt_confirm, rvgi_sma, rvgi_cci, ifvg_gap]
        bounds = [
            (10.0, 50.0), # crt_range
            (1.0, 5.0),   # crt_confirm
            (10.0, 50.0), # rvgi_sma
            (7.0, 21.0),  # rvgi_cci
            (10.0, 100.0) # ifvg_gap
        ]
        
        steps = [1.0, 1.0, 1.0, 1.0, 5.0]
        
        # Use a larger population or more epochs for better results if resources allow
        best_params, best_score = self.optimizer.optimize(
            objective_function, 
            bounds=bounds, 
            steps=steps, 
            epochs=3 
        )
        
        # Update strategy parameters
        self.strategy_params['crt_range_period'] = int(best_params[0])
        self.strategy_params['crt_confirm_period'] = int(best_params[1])
        self.strategy_params['rvgi_sma_period'] = int(best_params[2])
        self.strategy_params['rvgi_cci_period'] = int(best_params[3])
        self.strategy_params['ifvg_min_gap'] = int(best_params[4])
        
        logger.info(f"Optimized Parameters (Score {best_score:.2f}): {self.strategy_params}")

    def analyze_market(self):
        """Analyze market using DeepSeek"""
        logger.info(f"Fetching data for {self.symbol}...")
        # Increase limit to allow for optimization history
        df = self.data_processor.get_historical_data(self.symbol, self.timeframe, limit=200)
        
        if df.empty:
            logger.error("Failed to fetch historical data")
            return None, None
            
        # Generate features
        df = self.data_processor.generate_features(df)
        
        # Check if we need to run optimization
        current_time = time.time()
        if current_time - self.last_optimization_time > self.optimization_interval:
            self.optimize_parameters(df)
            self.last_optimization_time = current_time
        
        # --- Self-Learning: Train Local Models ---
        if len(df) > 2:
            current_close = df['close'].iloc[-1]
            prev_close = df['close'].iloc[-2]
            actual_return = current_close - prev_close
            
            # Train MFH
            self.mfh_analyzer.train(actual_return)
            
            # Train MatrixML
            self.matrix_ml.train(actual_return)
            
        # Prepare data for AI analysis
        # We take the last few candles and latest indicators
        latest_data = df.iloc[-1].to_dict()
        recent_candles = df.iloc[-5:].reset_index().to_dict('records')
        
        market_data = {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "current_price": latest_data.get('close'),
            "indicators": {
                "ema_fast": latest_data.get('ema_fast'),
                "ema_slow": latest_data.get('ema_slow'),
                "rsi": latest_data.get('rsi'),
                "atr": latest_data.get('atr'),
                "volatility": latest_data.get('volatility')
            },
            "recent_candles": recent_candles
        }
        
        # Fetch current positions for context
        current_positions = []
        try:
            positions = self.data_processor.exchange.fetch_positions([self.symbol])
            current_positions = [p for p in positions if float(p['contracts']) > 0]
        except Exception:
            pass

        technical_signals = market_data.get('indicators', {})

        # --- Advanced Algorithm Integration ---
        # 1. CRT (Candle Range Theory) Analysis
        crt_analysis = self.advanced_analysis.analyze_crt_strategy(
            df, 
            range_period=self.strategy_params['crt_range_period'],
            confirm_period=self.strategy_params['crt_confirm_period']
        )
        
        # 2. IFVG (Inverse Fair Value Gap) Analysis
        ifvg_analysis = self.advanced_analysis.analyze_ifvg(
            df, 
            min_gap_points=self.strategy_params['ifvg_min_gap']
        )
        
        # 3. RVGI + CCI Strategy
        rvgi_analysis = self.advanced_analysis.analyze_rvgi_cci_strategy(
            df, 
            sma_period=self.strategy_params['rvgi_sma_period'],
            cci_period=self.strategy_params['rvgi_cci_period']
        )
        
        # 4. Market Regime Detection
        regime_analysis = self.advanced_analysis.detect_market_regime(df)

        # 5. SMC Analysis
        smc_analysis = self.smc_analyzer.analyze(df)

        # 6. MFH Analysis
        mfh_analysis = self.mfh_analyzer.predict(df)

        # 7. MTF Analysis (New) - Fetch Higher TF Data
        # Assume 4h data for HTF if current is 1h or 15m
        # Normalize timeframe for check
        tf_lower = self.timeframe.lower()
        if tf_lower in ['1h', '15m', '30m']:
            htf_timeframe = '4h'
        elif tf_lower in ['4h', 'h4']:
            htf_timeframe = '1d'
        else:
            htf_timeframe = '1d' # Default fallback
            
        df_htf = self.data_processor.get_historical_data(self.symbol, htf_timeframe, limit=100)
        mtf_analysis = {"signal": "neutral", "reason": "No HTF Data"}
        if not df_htf.empty:
            mtf_analysis = self.mtf_analyzer.analyze(df, df_htf)
            
        # 8. PEM Analysis (Price Equation Model)
        pem_analysis = self.pem_analyzer.analyze(df)
        
        # 9. MatrixML Analysis
        returns_data = df['close'].diff().dropna().values
        matrix_ml_analysis = self.matrix_ml.predict(returns_data)
        
        # Combine into extra_analysis for DeepSeek
        extra_analysis_data = {
            "technical_indicators": technical_signals,
            "crt_strategy": crt_analysis,
            "ifvg_strategy": ifvg_analysis,
            "rvgi_cci_strategy": rvgi_analysis,
            "market_regime": regime_analysis,
            "smc_strategy": smc_analysis,
            "mfh_strategy": mfh_analysis,
            "mtf_strategy": mtf_analysis,
            "pem_strategy": pem_analysis,
            "matrix_ml_strategy": matrix_ml_analysis
        }
        
        logger.info(f"Advanced Analysis Signals: CRT={crt_analysis['signal']}, IFVG={ifvg_analysis['signal']}, RVGI={rvgi_analysis['signal']}")
        logger.info(f"SMC: {smc_analysis['signal']}, MTF: {mtf_analysis['signal']}, PEM: {pem_analysis['signal']}, MatrixML: {matrix_ml_analysis['signal']}")

        # 1. DeepSeek Market Structure Analysis
        logger.info("Requesting DeepSeek market structure analysis...")
        structure_analysis = self.deepseek_client.analyze_market_structure(
            market_data, 
            current_positions=current_positions,
            extra_analysis=extra_analysis_data
        )
        logger.info(f"Market Structure Analysis: {structure_analysis.get('market_state')}")
        
        # Add technical_signals to structure_analysis for Qwen
        structure_analysis['technical_signals'] = extra_analysis_data
        
        # Log analysis to database
        try:
            self.db_manager.log_analysis(
                symbol=self.symbol,
                market_state=structure_analysis.get('market_state'),
                structure_score=structure_analysis.get('structure_score'),
                ai_decision=None, # Will be updated after decision is made or just log analysis here
                raw_analysis=structure_analysis
            )
        except Exception as e:
            logger.error(f"Failed to log analysis to DB: {e}")
            
        return df, structure_analysis

    def make_decision(self, df, structure_analysis):
        """Make trading decision using Qwen"""
        if not self.qwen_client:
            logger.error("Qwen client not initialized")
            return None

        latest_data = df.iloc[-1].to_dict()
        
        # Get current balance
        balance = self.data_processor.get_account_balance('USDT')
        available_usdt = balance['free'] if balance else 0.0
        
        # Also get total equity (balance + unrealized PnL) to give AI a better picture
        total_equity = balance['total'] if balance else available_usdt
        
        logger.info(f"Current available USDT: {available_usdt}, Total Equity: {total_equity}")
        
        # Get current balance/positions (simplified)
        # In a real scenario, you'd fetch actual positions from OKX
        # Fetch actual positions to provide accurate context to AI
        # Filter out invalid positions (contracts = 0)
        valid_positions = []
        try:
            positions = self.data_processor.exchange.fetch_positions([self.symbol])
            # Process positions for AI context
            for pos in positions:
                contracts = float(pos['contracts'])
                if contracts > 0:
                    valid_positions.append({
                        "symbol": pos['symbol'],
                        "side": pos['side'], # long or short
                        "contracts": contracts,
                        "size": pos['info'].get('sz', 0), # Position size in base currency or contracts
                        "notional": pos['notional'], # Position value in USDT
                        "leverage": pos['leverage'],
                        "unrealized_pnl": pos['unrealizedPnl'],
                        "margin_mode": pos['marginMode'],
                        "liquidation_price": pos['liquidationPrice']
                    })
            current_positions = valid_positions
            logger.info(f"Current Positions: {json.dumps(current_positions, default=str)}")
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            current_positions = [] 

        # Fetch open orders to provide context about pending limits or SL/TPs
        try:
            open_orders_raw = self.data_processor.get_open_orders(self.symbol)
            open_orders = []
            for order in open_orders_raw:
                open_orders.append({
                    "id": order['id'],
                    "type": order['type'],
                    "side": order['side'],
                    "price": order['price'],
                    "amount": order['amount'],
                    "status": order['status'],
                    "reduce_only": order['info'].get('reduceOnly', False)
                })
            logger.info(f"Open Orders: {len(open_orders)}")
        except Exception as e:
            logger.error(f"Error fetching open orders: {e}")
            open_orders = []
        
        market_data = {
            "symbol": self.symbol,
            "price": latest_data.get('close'),
            "indicators": {
                "ema_fast": latest_data.get('ema_fast'),
                "ema_slow": latest_data.get('ema_slow'),
                "rsi": latest_data.get('rsi')
            },
            "account_info": {
                "available_usdt": available_usdt,
                "total_equity": total_equity
            },
            "open_orders": open_orders
        }
        
        # --- Feedback Loop: Fetch Historical Performance ---
        performance_stats = []
        try:
            performance_stats = self.db_manager.get_trade_performance_stats(limit=50)
            logger.info(f"Fetched {len(performance_stats)} past trades for feedback learning")
        except Exception as e:
            logger.error(f"Failed to fetch performance stats: {e}")
            
        logger.info("Requesting Qwen strategy optimization...")
        decision = self.qwen_client.optimize_strategy_logic(
            structure_analysis,
            market_data,
            current_positions=current_positions,
            performance_stats=performance_stats # Passing feedback for self-learning
        )
        
        # Send Analysis to Telegram
        try:
            exit_cond = decision.get('exit_conditions', {})
            sl_price = exit_cond.get('sl_price', 'N/A')
            tp_price = exit_cond.get('tp_price', 'N/A')
            
            action = decision.get('action')
            display_action = action
            
            # Check if we should display "Waiting for Market Direction" instead of "hold"
            # Logic: If action is hold and we have no positions, be more descriptive
            has_positions = len(current_positions) > 0
            if action == 'hold' and not has_positions:
                display_action = "WAITING FOR MARKET DIRECTION ⏳"
            
            msg = (
                f"🤖 *AI Crypto Strategy Analysis*\n"
                f"Symbol: `{self.symbol}`\n"
                f"Timeframe: `{self.timeframe}`\n\n"
                f"📊 *Market Structure*: {structure_analysis.get('market_state')} (Score: {structure_analysis.get('structure_score')})\n"
                f"💡 *Action*: `{display_action}`\n"
                f"💪 *Signal Strength*: {decision.get('signal_strength')}\n\n"
                f"📝 *Rationale*:\n{decision.get('strategy_rationale')}\n\n"
                f"🎯 *Targets*:\n"
                f"• SL: `{sl_price}`\n"
                f"• TP: `{tp_price}`\n\n"
                f"💰 *Positioning*:\n"
                f"• Leverage: {decision.get('leverage')}x\n"
                f"• Size: {float(decision.get('position_size', 0))*100:.1f}%"
            )
            self.send_telegram_message(msg)
        except Exception as e:
            logger.error(f"Failed to construct telegram message: {e}")
        
        return decision

    def execute_trade(self, decision):
        """Execute trade based on decision"""
        action = decision.get('action')
        rationale = decision.get('strategy_rationale', 'No rationale provided')
        
        # Determine current positions status for logic handling
        target_pos = None
        try:
            positions = self.data_processor.exchange.fetch_positions([self.symbol])
            if positions:
                # Assuming simple mode: one position per symbol
                for p in positions:
                    if float(p['contracts']) > 0:
                        target_pos = p
                        break
        except Exception as e:
            logger.error(f"Failed to fetch positions during execution: {e}")

        # --- CASE 1: Close Logic (close_buy / close_sell) ---
        if action in ['close_buy', 'close_sell']:
            if target_pos:
                logger.info(f"Executing CLOSE position for {self.symbol} based on AI decision")
                try:
                    # Close position by placing market order in opposite direction
                    pos_side = target_pos['side'] # 'long' or 'short'
                    # Verify if action matches position side (optional safety)
                    # if (action == 'close_buy' and pos_side != 'long') or ...
                    
                    close_side = 'sell' if pos_side == 'long' else 'buy'
                    close_amount = float(target_pos['contracts'])
                    
                    # Cancel existing open orders (SL/TPs) first
                    self.data_processor.cancel_all_orders(self.symbol)
                    
                    logger.info(f"Closing {pos_side} position: {close_side} {close_amount} contracts")
                    order = self.data_processor.create_order(self.symbol, close_side, close_amount, type='market')
                    
                    if order:
                        self.send_telegram_message(f"🚫 *Position Closed*\nSymbol: `{self.symbol}`\nReason: AI Signal `{action}`")
                except Exception as e:
                    logger.error(f"Failed to close position: {e}")
            else:
                logger.info("AI suggested closing position, but no open position found.")
            return

        # --- CASE 2: Hold / Update SL/TP Logic ---
        if action == 'hold':
            if target_pos:
                exit_conditions = decision.get('exit_conditions', {})
                new_sl = exit_conditions.get('sl_price')
                new_tp = exit_conditions.get('tp_price')
                
                if new_sl or new_tp:
                    logger.info(f"Updating SL/TP for existing position: SL={new_sl}, TP={new_tp}")
                    
                    # Determine direction for SL order (opposite to position)
                    pos_side = target_pos['side'] # 'long' or 'short'
                    sl_tp_side = 'sell' if pos_side == 'long' else 'buy'
                    pos_amount = float(target_pos['contracts']) 
                    
                    # Cancel existing open orders (SL/TPs) to avoid stacking
                    self.data_processor.cancel_all_orders(self.symbol)
                    
                    # Place new SL/TP
                    self.data_processor.place_sl_tp_order(self.symbol, sl_tp_side, pos_amount, sl_price=new_sl, tp_price=new_tp)
                    self.send_telegram_message(f"🔄 *Updated SL/TP*\nSymbol: `{self.symbol}`\nNew SL: `{new_sl}`\nNew TP: `{new_tp}`")
            return

        # --- CASE 3: Open New Position (buy / sell) ---
        # If we have an existing position, check if we need to flip (reverse) it
        if target_pos:
            pos_side = target_pos['side'] # 'long' or 'short'
            
            # Check for Reversal: Signal is Buy but we are Short, OR Signal is Sell but we are Long
            is_reversal = (action == 'buy' and pos_side == 'short') or (action == 'sell' and pos_side == 'long')
            
            if is_reversal:
                logger.info(f"reversal signal detected: Current {pos_side}, New Signal {action}. Closing existing position first.")
                try:
                    # 1. Close existing position
                    close_side = 'sell' if pos_side == 'long' else 'buy'
                    close_amount = float(target_pos['contracts'])
                    self.data_processor.cancel_all_orders(self.symbol)
                    self.data_processor.create_order(self.symbol, close_side, close_amount, type='market')
                    self.send_telegram_message(f"🔄 *Position Reversal Initiated*\nClosing existing {pos_side} position.")
                    
                    # Wait a moment for processing (optional but safer)
                    time.sleep(1)
                    
                    # 2. Proceed to open new position (code continues below)
                except Exception as e:
                    logger.error(f"Failed to close position for reversal: {e}")
                    return # Stop if close fails to avoid mixed positions (if not hedge mode)
            else:
                # Same direction signal: 
                # Option A: Add to position (Pyramiding) - For now, we might skip or just update SL/TP
                # Option B: Ignore if already in position
                logger.info(f"Signal {action} matches existing {pos_side} position. Checking for SL/TP updates.")
                # Treat as 'hold' logic to update SL/TP
                exit_conditions = decision.get('exit_conditions', {})
                new_sl = exit_conditions.get('sl_price')
                new_tp = exit_conditions.get('tp_price')
                
                # Update SL/TP if provided
                if new_sl or new_tp:
                    sl_tp_side = 'sell' if pos_side == 'long' else 'buy'
                    pos_amount = float(target_pos['contracts'])
                    self.data_processor.cancel_all_orders(self.symbol)
                    self.data_processor.place_sl_tp_order(self.symbol, sl_tp_side, pos_amount, sl_price=new_sl, tp_price=new_tp)
                    self.send_telegram_message(f"🔄 *Updated SL/TP (Same Direction)*\nSymbol: `{self.symbol}`\nNew SL: `{new_sl}`\nNew TP: `{new_tp}`")
                return # Exit, don't open duplicate position for now

        # ... (Proceed with standard Open Logic for buy/sell/limit) ...
        logger.info(f"Strategy Decision: {action}")
        logger.info(f"Rationale: {rationale}")
        leverage = int(decision.get('leverage', 1))
        logger.info(f"Suggested Leverage: {leverage}x")
        
        # Determine trade volume based on available balance and model recommendation
        volume_percent = decision.get('position_size', 0.0)
        
        # Ensure volume_percent is within 0-1 range
        volume_percent = max(0.0, min(1.0, float(volume_percent)))
        
        logger.info(f"Model recommended position size: {volume_percent:.2%} of available funds")
        
        if volume_percent <= 0:
            logger.warning("Recommended position size is 0, skipping trade")
            return

        # Fetch latest balance
        balance = self.data_processor.get_account_balance('USDT')
        available_usdt = balance['free'] if balance else 0.0
        
        # Calculate target USDT amount
        target_usdt = available_usdt * volume_percent
        
        # Get current price
        current_price = self.data_processor.get_current_price(self.symbol)
        
        if not current_price:
            logger.error("Failed to get current price, skipping trade")
            return
            
        # Ensure price is float
        try:
            current_price = float(current_price)
        except ValueError:
             logger.error(f"Invalid price format: {current_price}")
             return

        # Calculate amount in base currency (e.g. ETH)
        # Reserve 1% for fees to be safe if going full allocation
        if volume_percent > 0.95:
             target_usdt = target_usdt * 0.99

        target_margin = target_usdt
        # Leverage is already defined at the beginning of the function
        leverage = int(decision.get('leverage', 1))
        
        target_position_value = target_margin * leverage

        # Amount = Position Value / Price
        # Ensure we use the leveraged position value
        amount_eth = target_position_value / current_price
        
        # Convert to contracts
        # Get contract size dynamically
        contract_size = self.data_processor.get_contract_size(self.symbol)
        if not contract_size:
            contract_size = 0.1 # Fallback
            
        num_contracts = int(amount_eth / contract_size)
        
        logger.info(f"Volume Calculation: Available USDT={available_usdt}, Percent={volume_percent:.2%}, Margin={target_margin:.2f}, Leverage={leverage}x, Position Value={target_position_value:.2f}, Price={current_price}, Contract Size={contract_size}, Contracts={num_contracts}")
        
        # Minimum position value check (at least 1 contract)
        if num_contracts < 1:
            min_required_value = current_price * contract_size
            min_required_margin = min_required_value / leverage
            logger.warning(f"Calculated contracts ({num_contracts}) is less than 1. Minimum position value required: {min_required_value:.2f} USDT. At {leverage}x leverage, you need {min_required_margin:.2f} USDT margin.")
            return

        # Prepare SL/TP params for OKX
        exit_conditions = decision.get('exit_conditions', {})
        sl_price = exit_conditions.get('sl_price')
        tp_price = exit_conditions.get('tp_price')
        
        order_params = {}
        if sl_price or tp_price:
            # Prepare attached algo order for SL/TP
            # We don't provide attachAlgoClOrdId to let system generate one, avoiding format errors
            algo_order = {
                'tpTriggerPxType': 'last',
                'slTriggerPxType': 'last'
            }
            if tp_price:
                algo_order['tpTriggerPx'] = str(tp_price)
                algo_order['tpOrdPx'] = '-1' # Market price
            if sl_price:
                algo_order['slTriggerPx'] = str(sl_price)
                algo_order['slOrdPx'] = '-1' # Market price
                
            order_params['attachAlgoOrds'] = [algo_order]
            logger.info(f"Attaching SL/TP: SL={sl_price}, TP={tp_price}")

        try:
            # Set leverage before placing order
            self.data_processor.set_leverage(self.symbol, leverage)
            
            order = None
            if action == 'buy':
                logger.info(f"Executing BUY order for {self.symbol}, contracts: {num_contracts}")
                order = self.data_processor.create_order(self.symbol, 'buy', num_contracts, type='market', params=order_params)
                
            elif action == 'sell':
                # In Perpetual Swap, 'sell' usually means Open Short if no position, or Close Long.
                logger.info(f"Executing SELL order for {self.symbol}, contracts: {num_contracts}")
                order = self.data_processor.create_order(self.symbol, 'sell', num_contracts, type='market', params=order_params)
                
            elif action == 'buy_limit':
                limit_price = decision.get('entry_conditions', {}).get('limit_price')
                if limit_price:
                    logger.info(f"Executing BUY LIMIT order for {self.symbol}, contracts: {num_contracts}, price: {limit_price}")
                    order = self.data_processor.create_order(self.symbol, 'buy', num_contracts, type='limit', price=limit_price, params=order_params)
                else:
                    logger.warning("Buy limit order requested but no limit price provided")
                    
            elif action == 'sell_limit':
                limit_price = decision.get('entry_conditions', {}).get('limit_price')
                if limit_price:
                    logger.info(f"Executing SELL LIMIT order for {self.symbol}, contracts: {num_contracts}, price: {limit_price}")
                    order = self.data_processor.create_order(self.symbol, 'sell', num_contracts, type='limit', price=limit_price, params=order_params)
                else:
                    logger.warning("Sell limit order requested but no limit price provided")
            
            # Log trade to database if order was created
            if order:
                trade_record = {
                    'symbol': self.symbol,
                    'action': action,
                    'order_type': 'limit' if 'limit' in action else 'market',
                    'contracts': num_contracts,
                    'price': current_price if 'limit' not in action else limit_price,
                    'leverage': leverage,
                    'order_id': order.get('id'),
                    'strategy_rationale': rationale
                }
                self.db_manager.log_trade(trade_record)
                
                # Send Execution Notification to Telegram
                try:
                    exec_msg = (
                        f"✅ *Trade Executed*\n"
                        f"Action: `{action.upper()}`\n"
                        f"Symbol: `{self.symbol}`\n"
                        f"Contracts: `{num_contracts}`\n"
                        f"Price: `{trade_record['price']}`\n"
                        f"Leverage: `{leverage}x`\n"
                        f"Order ID: `{order.get('id')}`"
                    )
                    self.send_telegram_message(exec_msg)
                except Exception as e:
                    logger.error(f"Failed to send execution telegram: {e}")
                
        except Exception as e:
            logger.error(f"Failed to execute trade: {e}")

    def run_once(self):
        """Run a single trading cycle"""
        try:
            logger.info("Starting trading cycle...")
            df, analysis = self.analyze_market()
            
            if df is not None and analysis is not None:
                decision = self.make_decision(df, analysis)
                self.execute_trade(decision)
            
            logger.info("Trading cycle completed")
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}", exc_info=True)

    def start(self):
        """Start the bot loop"""
        self.is_running = True
        logger.info(f"Starting bot for {self.symbol} with {self.interval}s interval")
        
        while self.is_running:
            self.run_once()
            logger.info(f"Waiting {self.interval} seconds before next analysis...")
            time.sleep(self.interval)

if __name__ == "__main__":
    # Example usage
    bot = CryptoTradingBot(symbol='ETH/USDT:USDT', timeframe='15m', interval=3600 ) # 15 minutes interval
    bot.start()
if __name__ == "__main__":
    # Example usage
    bot = CryptoTradingBot(symbol='ETH/USDT:USDT', timeframe='15m', interval=3600 ) # 15 minutes interval
    bot.start()
