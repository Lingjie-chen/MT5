import time
import logging
import os
import json
import requests
import random
import numpy as np
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

from .okx_data_processor import OKXDataProcessor
from .ai_client_factory import AIClientFactory
from .database_manager import DatabaseManager
from .advanced_analysis import AdvancedMarketAnalysis, SMCAnalyzer, MFHAnalyzer, MTFAnalyzer, PEMAnalyzer, MatrixMLAnalyzer
from .optimization import GWO, WOAm, DE, COAm, BBO, TETA

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

class HybridOptimizer:
    def __init__(self):
        self.weights = {
            "deepseek": 1.0,
            "qwen": 1.2, 
            "crt": 0.8,
            "price_equation": 0.6,
            "tf_visual": 0.5,
            "advanced_tech": 0.7,
            "matrix_ml": 0.9,
            "smc": 1.1,
            "mfh": 0.8,
            "mtf": 0.8,
            "ifvg": 0.7,
            "rvgi_cci": 0.6
        }
        self.history = []

    def combine_signals(self, signals):
        weighted_sum = 0
        total_weight = 0
        
        details = {}
        
        for source, signal in signals.items():
            weight = self.weights.get(source, 0.5)
            val = 0
            if signal == 'buy': val = 1
            elif signal == 'sell': val = -1
            
            weighted_sum += val * weight
            total_weight += weight
            details[source] = val * weight
            
        if total_weight == 0: return "neutral", 0, self.weights
        
        final_score = weighted_sum / total_weight
        
        final_signal = "neutral"
        if final_score > 0.15: final_signal = "buy" # Lower threshold for sensitivity
        elif final_score < -0.15: final_signal = "sell"
        
        return final_signal, final_score, self.weights

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
        
        # Initialize Database Manager
        current_dir = os.path.dirname(os.path.realpath(__file__))
        db_path = os.path.join(current_dir, 'crypto_trading.db')
        self.db_manager = DatabaseManager(db_name=db_path)
        
        # Initialize Data Processor
        self.data_processor = OKXDataProcessor()

        # Initialize Advanced Analysis
        self.advanced_analysis = AdvancedMarketAnalysis()
        self.smc_analyzer = SMCAnalyzer()
        self.mfh_analyzer = MFHAnalyzer()
        self.mtf_analyzer = MTFAnalyzer()
        self.pem_analyzer = PEMAnalyzer()
        self.matrix_ml = MatrixMLAnalyzer()
        
        self.hybrid_optimizer = HybridOptimizer()
        
        # Optimization Engine Pool
        self.optimizers = {
            "GWO": GWO(),
            "WOAm": WOAm(),
            "DE": DE(),
            "COAm": COAm(),
            "BBO": BBO(),
            "TETA": TETA()
        }
        self.active_optimizer_name = "WOAm"
        self.last_optimization_time = 0
        self.optimization_interval = 3600 * 4 # Re-optimize every 4 hours
        
        # Short-term params
        self.short_term_params = {
            'rvgi_sma': 30,
            'rvgi_cci': 14,
            'ifvg_gap': 50
        }
        
        # Initialize AI Clients
        self.ai_factory = AIClientFactory()
        self.deepseek_client = self.ai_factory.get_client('deepseek')
        self.qwen_client = self.ai_factory.get_client('qwen')
        
        # Telegram Configuration
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not self.deepseek_client or not self.qwen_client:
            logger.warning("AI Clients not fully initialized. Trading functionality may be limited.")

    def escape_markdown(self, text):
        """Helper to escape markdown special characters"""
        if not isinstance(text, str):
            text = str(text)
        escape_chars = '_*[`'
        for char in escape_chars:
            text = text.replace(char, f'\\{char}')
        return text

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

    def evaluate_comprehensive_params(self, params, df):
        """
        Comprehensive Objective Function: Evaluates ALL dataframe-based strategy parameters together.
        params: Vector of parameter values corresponding to the defined structure.
        """
        # 1. Decode Parameters
        # 0: smc_ma (int)
        # 1: smc_atr (float)
        # 2: mfh_lr (float)
        # 3: mfh_horizon (int)
        # 4: pem_fast (int)
        # 5: pem_slow (int)
        # 6: pem_adx (float)
        # 7: rvgi_sma (int)
        # 8: rvgi_cci (int)
        # 9: ifvg_gap (int)
        
        try:
            p_smc_ma = int(params[0])
            p_smc_atr = params[1]
            p_mfh_lr = params[2]
            p_mfh_horizon = int(params[3])
            p_pem_fast = int(params[4])
            p_pem_slow = int(params[5])
            p_pem_adx = params[6]
            p_rvgi_sma = int(params[7])
            p_rvgi_cci = int(params[8])
            p_ifvg_gap = int(params[9])
            
            # 2. Initialize Temporary Analyzers (Fresh State)
            tmp_smc = SMCAnalyzer()
            tmp_smc.ma_period = p_smc_ma
            tmp_smc.atr_threshold = p_smc_atr
            
            tmp_mfh = MFHAnalyzer(learning_rate=p_mfh_lr)
            tmp_mfh.horizon = p_mfh_horizon
            
            # Note: PEMAnalyzer in Crypto might need attribute adjustment if different from Gold
            tmp_pem = PEMAnalyzer() 
            # Assuming PEMAnalyzer has similar analyze method signature or we mock it
            # Crypto PEMAnalyzer uses analyze(df, ma_fast_period, ma_slow_period, adx_threshold)
            
            tmp_adapter = AdvancedMarketAnalysis()
            
            # 3. Run Simulation
            start_idx = max(p_smc_ma, p_pem_slow, 50) + 10
            if len(df) < start_idx + 50: return -9999
            
            balance = 10000.0
            closes = df['close'].values
            
            trades_count = 0
            wins = 0
            
            # Optimization: Step size > 1 to speed up
            for i in range(start_idx, len(df)-1):
                sub_df = df.iloc[:i+1]
                curr_price = closes[i]
                next_price = closes[i+1]
                
                # MFH Train (Must happen every step for consistency)
                if i > p_mfh_horizon:
                    past_ret = (closes[i] - closes[i-p_mfh_horizon]) / closes[i-p_mfh_horizon]
                    tmp_mfh.train(past_ret)
                
                # Signals
                smc_sig = tmp_smc.analyze(sub_df)['signal']
                mfh_sig = tmp_mfh.predict(sub_df)['signal']
                
                # PEM Signal (passing params explicitly as per Crypto implementation)
                pem_res = tmp_pem.analyze(sub_df, ma_fast_period=p_pem_fast, ma_slow_period=p_pem_slow, adx_threshold=p_pem_adx)
                pem_sig = pem_res['signal']
                
                # Short Term
                ifvg_sig = tmp_adapter.analyze_ifvg(sub_df, min_gap_points=p_ifvg_gap)['signal']
                rvgi_sig = tmp_adapter.analyze_rvgi_cci_strategy(sub_df, sma_period=p_rvgi_sma, cci_period=p_rvgi_cci)['signal']
                
                # Combine
                votes = 0
                for s in [smc_sig, mfh_sig, pem_sig, ifvg_sig, rvgi_sig]:
                    if s == 'buy': votes += 1
                    elif s == 'sell': votes -= 1
                
                final_sig = "neutral"
                if votes >= 2: final_sig = "buy"
                elif votes <= -2: final_sig = "sell"
                
                # Evaluate
                if final_sig == "buy":
                    trades_count += 1
                    if next_price > curr_price: wins += 1
                    balance += (next_price - curr_price)
                elif final_sig == "sell":
                    trades_count += 1
                    if next_price < curr_price: wins += 1
                    balance += (curr_price - next_price)
            
            if trades_count == 0: return -100
            
            # Simple Profit Metric
            score = (balance - 10000.0)
            return score
            
        except Exception:
            return -9999

    def optimize_strategy_parameters(self, df):
        """
        Comprehensive Optimization: Tunes ALL strategy parameters using Auto-AO.
        """
        logger.info("Starting Comprehensive Strategy Optimization (Auto-AO)...")
        
        if df is None or len(df) < 400:
            logger.warning("Insufficient data for optimization, skipping")
            return
            
        # 2. Define Search Space (10 Dimensions)
        # smc_ma, smc_atr, mfh_lr, mfh_horizon, pem_fast, pem_slow, pem_adx, rvgi_sma, rvgi_cci, ifvg_gap
        bounds = [
            (100, 300),     # smc_ma
            (0.001, 0.005), # smc_atr
            (0.001, 0.1),   # mfh_lr
            (3, 10),        # mfh_horizon
            (10, 50),       # pem_fast
            (100, 300),     # pem_slow
            (15.0, 30.0),   # pem_adx
            (10, 50),       # rvgi_sma
            (10, 30),       # rvgi_cci
            (10, 100)       # ifvg_gap
        ]
        
        steps = [10, 0.0005, 0.005, 1, 5, 10, 1.0, 2, 2, 5]
        
        # 3. Objective
        def objective(params):
            return self.evaluate_comprehensive_params(params, df)
            
        # 4. Optimizer
        algo_name = random.choice(list(self.optimizers.keys()))
        optimizer = self.optimizers[algo_name]
        logger.info(f"Selected Optimizer: {algo_name}")
        
        # 5. Run
        best_params, best_score = optimizer.optimize(
            objective, 
            bounds, 
            steps=steps, 
            epochs=5 # Lower epochs for faster crypto loop
        )
        
        # 6. Apply Results
        if best_score > -1000:
            logger.info(f"Optimization Complete! Best Score: {best_score:.2f}")
            
            # Extract
            p_smc_ma = int(best_params[0])
            p_smc_atr = best_params[1]
            p_mfh_lr = best_params[2]
            p_mfh_horizon = int(best_params[3])
            p_pem_fast = int(best_params[4])
            p_pem_slow = int(best_params[5])
            p_pem_adx = best_params[6]
            p_rvgi_sma = int(best_params[7])
            p_rvgi_cci = int(best_params[8])
            p_ifvg_gap = int(best_params[9])
            
            # Apply
            self.smc_analyzer.ma_period = p_smc_ma
            self.smc_analyzer.atr_threshold = p_smc_atr
            
            self.mfh_analyzer.learning_rate = p_mfh_lr
            self.mfh_analyzer.horizon = p_mfh_horizon
            
            # PEM in Crypto might need params passed to analyze method or set attributes if supported
            # Assuming we can set them for future analyze calls, but analyze() signature requires them passed?
            # Let's store them in self.pem_params
            self.pem_params = {
                'ma_fast': p_pem_fast,
                'ma_slow': p_pem_slow,
                'adx_threshold': p_pem_adx
            }
            
            self.short_term_params = {
                'rvgi_sma': p_rvgi_sma,
                'rvgi_cci': p_rvgi_cci,
                'ifvg_gap': p_ifvg_gap
            }
            
            msg = (
                f"🧬 *Comprehensive Optimization ({algo_name})*\n"
                f"Score: {best_score:.2f}\n"
                f"• SMC: MA={p_smc_ma}, ATR={p_smc_atr:.4f}\n"
                f"• MFH: LR={p_mfh_lr:.3f}, H={p_mfh_horizon}\n"
                f"• PEM: Fast={p_pem_fast}, Slow={p_pem_slow}, ADX={p_pem_adx:.1f}\n"
                f"• ST: RVGI({p_rvgi_sma},{p_rvgi_cci}), IFVG({p_ifvg_gap})"
            )
            self.send_telegram_message(msg)
            logger.info(f"Updated all strategy params: {msg}")
            
        else:
            logger.warning("Optimization failed to find positive score, keeping original params")

    def calculate_optimized_sl_tp(self, trade_type, price, atr, market_context=None):
        """
        Calculate optimized SL/TP based on ATR, MFE/MAE stats, and market structure
        """
        if atr <= 0:
            atr = price * 0.01 # Fallback 1%
            
        # 1. Base Volatility
        mfe_tp_dist = atr * 2.0
        mae_sl_dist = atr * 1.5
        
        # 2. Historical Stats (MFE/MAE)
        try:
             stats = self.db_manager.get_trade_performance_stats(limit=100)
             # ... Logic similar to Gold if stats available ...
        except Exception:
             pass

        # 3. Market Structure
        struct_tp_price = 0.0
        
        # ... (Simplified version of Gold's logic) ...
        
        final_sl = 0.0
        final_tp = 0.0
        
        if 'buy' in trade_type:
            final_tp = price + mfe_tp_dist
            final_sl = price - mae_sl_dist
        else:
            final_tp = price - mfe_tp_dist
            final_sl = price + mae_sl_dist
            
        return final_sl, final_tp

    def analyze_market(self):
        """Analyze market using DeepSeek"""
        logger.info(f"Fetching data for {self.symbol}...")
        # Increase limit to allow for optimization history
        df = self.data_processor.get_historical_data(self.symbol, self.timeframe, limit=600)
        
        if df.empty:
            logger.error("Failed to fetch historical data")
            return None, None
            
        # Generate features
        df = self.data_processor.generate_features(df)
        
        # Check if we need to run optimization
        current_time = time.time()
        if current_time - self.last_optimization_time > self.optimization_interval:
            self.optimize_strategy_parameters(df)
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
        
        # Fetch current positions
        current_positions = []
        try:
            positions = self.data_processor.exchange.fetch_positions([self.symbol])
            current_positions = [p for p in positions if float(p['contracts']) > 0]
        except Exception:
            pass

        technical_signals = market_data.get('indicators', {})

        # --- Advanced Algorithm Integration ---
        # 1. CRT
        crt_analysis = self.advanced_analysis.analyze_crt_strategy(df) # Use default or optimized if method signature updated
        
        # 2. IFVG (Use optimized)
        ifvg_analysis = self.advanced_analysis.analyze_ifvg(
            df, 
            min_gap_points=self.short_term_params.get('ifvg_gap', 50)
        )
        
        # 3. RVGI + CCI (Use optimized)
        rvgi_analysis = self.advanced_analysis.analyze_rvgi_cci_strategy(
            df, 
            sma_period=self.short_term_params.get('rvgi_sma', 30),
            cci_period=self.short_term_params.get('rvgi_cci', 14)
        )
        
        # 4. Market Regime
        regime_analysis = self.advanced_analysis.detect_market_regime(df)

        # 5. SMC
        smc_analysis = self.smc_analyzer.analyze(df)

        # 6. MFH
        mfh_analysis = self.mfh_analyzer.predict(df)

        # 7. MTF
        # ... Fetch HTF data ...
        tf_lower = self.timeframe.lower()
        htf_timeframe = '4h' if tf_lower in ['1h', '15m', '30m'] else '1d'
        df_htf = self.data_processor.get_historical_data(self.symbol, htf_timeframe, limit=100)
        mtf_analysis = {"signal": "neutral", "reason": "No HTF Data"}
        if not df_htf.empty:
            mtf_analysis = self.mtf_analyzer.analyze(df, df_htf)
            
        # 8. PEM (Use optimized params)
        pem_p = getattr(self, 'pem_params', {})
        pem_analysis = self.pem_analyzer.analyze(
            df, 
            ma_fast_period=pem_p.get('ma_fast', 108),
            ma_slow_period=pem_p.get('ma_slow', 60),
            adx_threshold=pem_p.get('adx_threshold', 20)
        )
        
        # 9. MatrixML
        returns_data = df['close'].diff().dropna().values
        matrix_ml_analysis = self.matrix_ml.predict(returns_data)
        
        # Combine
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
        
        logger.info(f"Signals: SMC={smc_analysis['signal']}, MFH={mfh_analysis['signal']}, PEM={pem_analysis['signal']}, IFVG={ifvg_analysis['signal']}")

        # 1. DeepSeek
        logger.info("Requesting DeepSeek market structure analysis...")
        structure_analysis = self.deepseek_client.analyze_market_structure(
            market_data, 
            current_positions=current_positions,
            extra_analysis=extra_analysis_data
        )
        
        # DeepSeek Signal Logic (similar to Gold)
        ds_signal = structure_analysis.get('preliminary_signal', 'neutral')
        ds_score = structure_analysis.get('structure_score', 50)
        ds_pred = structure_analysis.get('short_term_prediction', 'neutral')
        
        # Combine Signals using HybridOptimizer logic
        all_signals = {
            "deepseek": ds_signal,
            "crt": crt_analysis['signal'],
            "price_equation": pem_analysis['signal'],
            "matrix_ml": matrix_ml_analysis['signal'],
            "smc": smc_analysis['signal'],
            "mfh": mfh_analysis['signal'],
            "mtf": mtf_analysis['signal'],
            "ifvg": ifvg_analysis['signal'],
            "rvgi_cci": rvgi_analysis['signal']
        }
        
        final_signal, final_score, _ = self.hybrid_optimizer.combine_signals(all_signals)
        logger.info(f"Hybrid Signal: {final_signal} (Score: {final_score:.2f})")
        
        structure_analysis['technical_signals'] = extra_analysis_data
        structure_analysis['hybrid_signal'] = final_signal # Pass to Qwen
        structure_analysis['hybrid_score'] = final_score
        
        try:
            self.db_manager.log_analysis(
                symbol=self.symbol,
                market_state=structure_analysis.get('market_state'),
                structure_score=structure_analysis.get('structure_score'),
                ai_decision=None,
                raw_analysis=structure_analysis
            )
        except Exception as e:
            logger.error(f"Failed to log analysis: {e}")
            
        return df, structure_analysis

    def make_decision(self, df, structure_analysis):
        """Make trading decision using Qwen"""
        if not self.qwen_client: return None

        latest_data = df.iloc[-1].to_dict()
        balance = self.data_processor.get_account_balance('USDT')
        available_usdt = balance['free'] if balance else 0.0
        total_equity = balance['total'] if balance else available_usdt
        
        # Fetch actual positions
        valid_positions = []
        try:
            positions = self.data_processor.exchange.fetch_positions([self.symbol])
            for pos in positions:
                if float(pos['contracts']) > 0:
                    valid_positions.append({
                        "symbol": pos['symbol'],
                        "side": pos['side'],
                        "contracts": float(pos['contracts']),
                        "unrealized_pnl": pos['unrealizedPnl'],
                        "leverage": pos['leverage']
                    })
        except Exception:
            pass
            
        # Open Orders
        open_orders = []
        try:
            raw_orders = self.data_processor.get_open_orders(self.symbol)
            for o in raw_orders:
                open_orders.append({"id": o['id'], "type": o['type'], "price": o['price']})
        except Exception:
            pass
        
        market_data = {
            "symbol": self.symbol,
            "price": latest_data.get('close'),
            "indicators": {
                "rsi": latest_data.get('rsi'),
                "atr": latest_data.get('atr')
            },
            "account_info": {"available_usdt": available_usdt, "total_equity": total_equity},
            "open_orders": open_orders
        }
        
        # Feedback
        performance_stats = []
        try:
            performance_stats = self.db_manager.get_trade_performance_stats(limit=50)
        except Exception:
            pass
            
        logger.info("Requesting Qwen strategy optimization...")
        decision = self.qwen_client.optimize_strategy_logic(
            structure_analysis,
            market_data,
            current_positions=valid_positions,
            performance_stats=performance_stats
        )
        
        # Check if Qwen provided SL/TP, if not, use Optimized Calculation
        exit_cond = decision.get('exit_conditions', {})
        if not exit_cond.get('sl_price') or not exit_cond.get('tp_price'):
            logger.info("Qwen did not provide SL/TP, using Optimized Calculation")
            trade_dir = "buy"
            action = decision.get('action', 'hold')
            if action in ['sell', 'limit_sell']: trade_dir = "sell"
            
            atr = latest_data.get('atr', 0)
            price = latest_data.get('close')
            
            calc_sl, calc_tp = self.calculate_optimized_sl_tp(trade_dir, price, atr)
            
            if not exit_cond.get('sl_price'): exit_cond['sl_price'] = calc_sl
            if not exit_cond.get('tp_price'): exit_cond['tp_price'] = calc_tp
            
            decision['exit_conditions'] = exit_cond

        # Send Telegram
        try:
            sl_price = exit_cond.get('sl_price')
            tp_price = exit_cond.get('tp_price')
            action = decision.get('action')
            
            display_action = action
            if action == 'hold' and not valid_positions:
                display_action = "WAITING FOR MARKET DIRECTION ⏳"
            
            ds_signal = structure_analysis.get('preliminary_signal', 'N/A')
            ds_score = structure_analysis.get('structure_score', 0)
            hybrid_signal = structure_analysis.get('hybrid_signal', 'N/A')
            hybrid_score = structure_analysis.get('hybrid_score', 0)
            
            msg = (
                f"🤖 *AI Crypto Strategy Insight*\n"
                f"Symbol: `{self.symbol}` | TF: `{self.timeframe}`\n"
                f"Time: {datetime.now().strftime('%H:%M:%S')}\n\n"
                
                f"🧠 *AI Consensus*\n"
                f"• Decision: *{display_action.upper()}*\n"
                f"• Qwen Action: `{self.escape_markdown(action)}`\n"
                f"• Hybrid Signal: `{hybrid_signal}` ({hybrid_score:.2f})\n"
                f"• DeepSeek: `{ds_signal}` ({ds_score}/100)\n\n"
                
                f"📝 *Rationale*: _{self.escape_markdown(decision.get('strategy_rationale'))}_\n\n"
                
                f"🎯 *Setup*\n"
                f"• SL: `{sl_price}`\n"
                f"• TP: `{tp_price}`\n"
                f"• Lev: {decision.get('leverage')}x | Size: {float(decision.get('position_size', 0))*100:.1f}%\n\n"
                
                f"📊 *Market State*: `{structure_analysis.get('market_state')}`"
            )
            self.send_telegram_message(msg)
        except Exception as e:
            logger.error(f"Failed to construct telegram: {e}")
        
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
                    pos_side = target_pos['side'] # 'long' or 'short'
                    close_side = 'sell' if pos_side == 'long' else 'buy'
                    close_amount = float(target_pos['contracts'])
                    self.data_processor.cancel_all_orders(self.symbol)
                    order = self.data_processor.create_order(self.symbol, close_side, close_amount, type='market')
                    if order:
                        self.send_telegram_message(f"🚫 *Position Closed*\nSymbol: `{self.symbol}`\nReason: AI Signal `{action}`")
                except Exception as e:
                    logger.error(f"Failed to close position: {e}")
            return

        # --- CASE 2: Hold / Update SL/TP Logic ---
        if action == 'hold':
            if target_pos:
                exit_conditions = decision.get('exit_conditions', {})
                new_sl = exit_conditions.get('sl_price')
                new_tp = exit_conditions.get('tp_price')
                
                if new_sl or new_tp:
                    logger.info(f"Updating SL/TP for existing position: SL={new_sl}, TP={new_tp}")
                    pos_side = target_pos['side']
                    sl_tp_side = 'sell' if pos_side == 'long' else 'buy'
                    pos_amount = float(target_pos['contracts']) 
                    self.data_processor.cancel_all_orders(self.symbol)
                    self.data_processor.place_sl_tp_order(self.symbol, sl_tp_side, pos_amount, sl_price=new_sl, tp_price=new_tp)
                    self.send_telegram_message(f"🔄 *Updated SL/TP*\nSymbol: `{self.symbol}`\nNew SL: `{new_sl}`\nNew TP: `{new_tp}`")
            return

        # --- CASE 3: Open New Position (buy / sell) ---
        if target_pos:
            pos_side = target_pos['side']
            is_reversal = (action == 'buy' and pos_side == 'short') or (action == 'sell' and pos_side == 'long')
            
            if is_reversal:
                logger.info(f"Reversal signal detected. Closing existing {pos_side} position.")
                try:
                    close_side = 'sell' if pos_side == 'long' else 'buy'
                    close_amount = float(target_pos['contracts'])
                    self.data_processor.cancel_all_orders(self.symbol)
                    self.data_processor.create_order(self.symbol, close_side, close_amount, type='market')
                    self.send_telegram_message(f"🔄 *Position Reversal Initiated*")
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Failed to close position for reversal: {e}")
                    return
            else:
                # Same direction, update SL/TP
                logger.info(f"Signal {action} matches existing {pos_side} position. Updating SL/TP.")
                exit_conditions = decision.get('exit_conditions', {})
                new_sl = exit_conditions.get('sl_price')
                new_tp = exit_conditions.get('tp_price')
                if new_sl or new_tp:
                    sl_tp_side = 'sell' if pos_side == 'long' else 'buy'
                    pos_amount = float(target_pos['contracts'])
                    self.data_processor.cancel_all_orders(self.symbol)
                    self.data_processor.place_sl_tp_order(self.symbol, sl_tp_side, pos_amount, sl_price=new_sl, tp_price=new_tp)
                return

        # Execute New Trade
        leverage = int(decision.get('leverage', 1))
        volume_percent = float(decision.get('position_size', 0.0))
        volume_percent = max(0.0, min(1.0, volume_percent))
        
        if volume_percent <= 0: return

        balance = self.data_processor.get_account_balance('USDT')
        available_usdt = balance['free'] if balance else 0.0
        target_usdt = available_usdt * volume_percent
        if volume_percent > 0.95: target_usdt *= 0.99
        
        current_price = self.data_processor.get_current_price(self.symbol)
        if not current_price: return
        
        target_position_value = target_usdt * leverage
        amount_eth = target_position_value / current_price
        contract_size = self.data_processor.get_contract_size(self.symbol) or 0.1
        num_contracts = int(amount_eth / contract_size)
        
        if num_contracts < 1:
            logger.warning(f"Calculated contracts < 1. Required margin too high.")
            return

        # Prepare SL/TP
        exit_conditions = decision.get('exit_conditions', {})
        sl_price = exit_conditions.get('sl_price')
        tp_price = exit_conditions.get('tp_price')
        
        order_params = {}
        if sl_price or tp_price:
            algo_order = {'tpTriggerPxType': 'last', 'slTriggerPxType': 'last'}
            if tp_price: algo_order['tpTriggerPx'] = str(tp_price); algo_order['tpOrdPx'] = '-1'
            if sl_price: algo_order['slTriggerPx'] = str(sl_price); algo_order['slOrdPx'] = '-1'
            order_params['attachAlgoOrds'] = [algo_order]

        try:
            self.data_processor.set_leverage(self.symbol, leverage)
            
            order = None
            if action == 'buy':
                order = self.data_processor.create_order(self.symbol, 'buy', num_contracts, type='market', params=order_params)
            elif action == 'sell':
                order = self.data_processor.create_order(self.symbol, 'sell', num_contracts, type='market', params=order_params)
            elif action == 'buy_limit':
                lp = decision.get('entry_conditions', {}).get('limit_price')
                if lp: order = self.data_processor.create_order(self.symbol, 'buy', num_contracts, type='limit', price=lp, params=order_params)
            elif action == 'sell_limit':
                lp = decision.get('entry_conditions', {}).get('limit_price')
                if lp: order = self.data_processor.create_order(self.symbol, 'sell', num_contracts, type='limit', price=lp, params=order_params)
            
            if order:
                trade_record = {
                    'symbol': self.symbol, 'action': action, 'order_type': 'limit' if 'limit' in action else 'market',
                    'contracts': num_contracts, 'price': current_price, 'leverage': leverage,
                    'order_id': order.get('id'), 'strategy_rationale': rationale
                }
                self.db_manager.log_trade(trade_record)
                
                exec_msg = (
                    f"✅ *Trade Executed*\nAction: `{action.upper()}`\nSymbol: `{self.symbol}`\n"
                    f"Contracts: `{num_contracts}`\nPrice: `{trade_record['price']}`\nLeverage: `{leverage}x`"
                )
                self.send_telegram_message(exec_msg)
                
        except Exception as e:
            logger.error(f"Failed to execute trade: {e}")

    def run_once(self):
        """Run a single trading cycle"""
        try:
            logger.info("Starting trading cycle...")
            df, analysis = self.analyze_market()
            
            if df is not None and analysis is not None:
                decision = self.make_decision(df, analysis)
                if decision:
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
    bot = CryptoTradingBot(symbol='ETH/USDT:USDT', timeframe='15m', interval=900) 
    bot.start()
