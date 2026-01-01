import time
import logging
import os
import json
import requests
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

from .okx_data_processor import OKXDataProcessor
from .ai_client_factory import AIClientFactory
from .database_manager import DatabaseManager
from .advanced_analysis import (
    AdvancedMarketAnalysis, AdvancedMarketAnalysisAdapter, MFHAnalyzer, SMCAnalyzer, 
    MatrixMLAnalyzer, CRTAnalyzer, PriceEquationModel, 
    TimeframeVisualAnalyzer, MTFAnalyzer
)
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
    def __init__(self, symbol='ETH/USDT', timeframe='15m', interval=900):
        """
        Initialize the Crypto Trading Bot
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

        # Initialize Advanced Analysis (Gold Strategy Alignment)
        # 15m Timeframe -> H1 CRT, H1/H4 MTF
        self.crt_analyzer = CRTAnalyzer(timeframe_htf='1h')
        self.mtf_analyzer = MTFAnalyzer(htf1='1h', htf2='4h')
        self.price_model = PriceEquationModel()
        self.tf_analyzer = TimeframeVisualAnalyzer()
        self.advanced_adapter = AdvancedMarketAnalysisAdapter()
        self.matrix_ml = MatrixMLAnalyzer()
        self.smc_analyzer = SMCAnalyzer()
        self.mfh_analyzer = MFHAnalyzer()
        self.advanced_analysis = AdvancedMarketAnalysis() # Legacy adapter
        
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
        self.optimization_interval = 3600 * 4 
        
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
        
        # State
        self.latest_strategy = None
        self.latest_signal = "neutral"
        self.signal_history = []
        
        if not self.deepseek_client or not self.qwen_client:
            logger.warning("AI Clients not fully initialized.")

    def sync_account_history(self):
        """Sync recent account history to DB for Self-Learning"""
        logger.info("Syncing account history from OKX...")
        try:
            trades = self.data_processor.get_recent_trades(self.symbol, limit=100)
            if trades:
                self.db_manager.save_trade_history_batch(trades)
        except Exception as e:
            logger.error(f"Failed to sync history: {e}")

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
        if not self.telegram_token or not self.telegram_chat_id: return
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            # Proxy settings for China users (optional, remove if not needed or configure via env)
            proxies = {
                "http": "http://127.0.0.1:7890",
                "https": "http://127.0.0.1:7890"
            }
            try:
                requests.post(url, json=payload, timeout=10, proxies=proxies)
            except:
                requests.post(url, json=payload, timeout=10) # Retry without proxy
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")

    def calculate_optimized_sl_tp(self, trade_type, price, atr, market_context=None):
        """Calculate optimized SL/TP based on ATR, MFE/MAE stats, and market structure"""
        if atr <= 0: atr = price * 0.01 
            
        mfe_tp_dist = atr * 2.0
        mae_sl_dist = atr * 1.5
        
        # MFE/MAE Stats
        try:
             stats = self.db_manager.get_trade_performance_stats(limit=100)
             trades = stats if isinstance(stats, list) else stats.get('recent_trades', [])
             
             if trades and len(trades) > 10:
                 mfes = [t.get('mfe', 0) for t in trades if t.get('mfe', 0) > 0]
                 maes = [abs(t.get('mae', 0)) for t in trades if abs(t.get('mae', 0)) > 0]
                 
                 if mfes and maes:
                     opt_tp_pct = np.percentile(mfes, 60) / 100.0
                     opt_sl_pct = np.percentile(maes, 90) / 100.0
                     mfe_tp_dist = price * opt_tp_pct
                     mae_sl_dist = price * opt_sl_pct
        except Exception: pass

        # Structure
        struct_tp_price = 0.0
        if market_context:
            is_buy = 'buy' in trade_type
            candidates = []
            if 'active_zones' in market_context:
                 for zone in market_context['active_zones']:
                     if is_buy and zone.get('type') == 'bearish' and zone.get('bottom', 0) > price:
                         candidates.append(zone['bottom'])
                     elif not is_buy and zone.get('type') == 'bullish' and zone.get('top', 0) < price:
                         candidates.append(zone['top'])
            
            if candidates:
                struct_tp_price = min(candidates) if is_buy else max(candidates)

        final_sl = 0.0
        final_tp = 0.0
        
        if 'buy' in trade_type:
            base_tp = price + mfe_tp_dist
            base_sl = price - mae_sl_dist
            if struct_tp_price > price:
                final_tp = struct_tp_price - (atr * 0.1) if struct_tp_price < base_tp else base_tp
            else:
                final_tp = base_tp
            final_sl = base_sl
        else:
            base_tp = price - mfe_tp_dist
            base_sl = price + mae_sl_dist
            if struct_tp_price > 0 and struct_tp_price < price:
                final_tp = struct_tp_price + (atr * 0.1) if struct_tp_price > base_tp else base_tp
            else:
                final_tp = base_tp
            final_sl = base_sl
            
        return final_sl, final_tp

    def calculate_dynamic_lot(self, strength, market_context, mfe_mae_ratio=1.0, ai_signals=None):
        """
        Calculate dynamic position size based on signal strength and market context.
        Adapted for Crypto (returns % of equity).
        """
        base_risk = 0.02 # 2% base risk
        
        # 1. Consensus Multiplier
        consensus_mult = 1.0
        if ai_signals:
            buy_votes = sum(1 for k, v in ai_signals.items() if v == 'buy')
            sell_votes = sum(1 for k, v in ai_signals.items() if v == 'sell')
            total = len(ai_signals)
            if total > 0:
                consensus_ratio = max(buy_votes, sell_votes) / total
                if consensus_ratio > 0.7: consensus_mult = 1.3
                elif consensus_ratio < 0.4: consensus_mult = 0.7
        
        # 2. Strength Multiplier
        strength_mult = 1.0
        if strength >= 80: strength_mult = 1.5
        elif strength >= 60: strength_mult = 1.2
        elif strength < 40: strength_mult = 0.5
        
        # 3. Structure Multiplier (SMC)
        struct_mult = 1.0
        if market_context and 'smc' in market_context:
             smc = market_context['smc'].get('structure', 'neutral')
             if smc == 'bullish_breakout' or smc == 'bearish_breakout':
                 struct_mult = 1.2
        
        # 4. MFE/MAE Multiplier
        perf_mult = 1.0
        if mfe_mae_ratio > 2.0: perf_mult = 1.2
        elif mfe_mae_ratio < 0.8: perf_mult = 0.8
        
        final_risk = base_risk * consensus_mult * strength_mult * struct_mult * perf_mult
        final_risk = min(final_risk, 0.05) # Max 5% risk
        
        return final_risk # Returns risk percentage (e.g., 0.03 for 3%)

    def analyze_market(self):
        """Full AI Market Analysis (Gold Logic)"""
        logger.info(f"Fetching data for {self.symbol}...")
        df = self.data_processor.get_historical_data(self.symbol, self.timeframe, limit=1000)
        
        if df.empty: return None, None, None, 0, 0, 0, 0
            
        # Features
        df = self.data_processor.generate_features(df)
        
        # Self-Learning Training
        if len(df) > 2:
            change = df['close'].iloc[-1] - df['close'].iloc[-2]
            self.mfh_analyzer.train(change)
            self.matrix_ml.train(change)
            
        # Snapshot
        latest = df.iloc[-1]
        market_snapshot = {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "prices": {
                "open": float(latest['open']), "high": float(latest['high']), 
                "low": float(latest['low']), "close": float(latest['close']), "volume": float(latest['volume'])
            },
            "indicators": {
                "rsi": float(latest.get('rsi', 50)),
                "atr": float(latest.get('atr', 0)),
                "ema_fast": float(latest.get('ema_fast', 0)),
                "volatility": float(latest.get('volatility', 0))
            }
        }
        
        # --- Advanced Analysis ---
        current_time = latest.name.timestamp() if hasattr(latest.name, 'timestamp') else time.time()
        
        # Fetch HTF Data for CRT/MTF
        df_htf1 = self.data_processor.get_historical_data(self.symbol, '1h', limit=200)
        df_htf2 = self.data_processor.get_historical_data(self.symbol, '4h', limit=200)
        
        # Fallback if HTF data unavailable
        if df_htf1 is None or df_htf1.empty: df_htf1 = df.copy()
        if df_htf2 is None or df_htf2.empty: df_htf2 = df.copy()

        # Run Optimizations (Real-time Param Config)
        if time.time() - self.last_optimization_time > self.optimization_interval:
            self.optimize_short_term_params()
            self.optimize_weights()

        crt_res = self.crt_analyzer.analyze(self.symbol, latest, current_time, df_htf=df_htf1)
        self.price_model.update(float(latest['close']))
        
        # Use optimized params for PEM
        pem_fast = getattr(self.price_model, 'ma_fast_period', 108)
        pem_slow = getattr(self.price_model, 'ma_slow_period', 60)
        pem_adx = getattr(self.price_model, 'adx_threshold', 20)
        pem_res = self.price_model.analyze(df, ma_fast_period=pem_fast, ma_slow_period=pem_slow, adx_threshold=pem_adx)
        
        tf_res = self.tf_analyzer.analyze(self.symbol, current_time, df_current=df)
        
        # HTF Data for MTF
        # df_htf1 is already fetched (1h), df_htf2 (4h)
        mtf_res = self.mtf_analyzer.analyze(df, df_htf1, df_htf2) 
        
        # Advanced Tech with Optimized Params
        adv_res = self.advanced_adapter.analyze_full(df, params=self.short_term_params)
        adv_sig = adv_res['signal_info']['signal'] if adv_res else 'neutral'
        
        # Matrix ML
        ticks = [] 
        ml_res = self.matrix_ml.predict(ticks)
        
        # SMC & MFH
        smc_res = self.smc_analyzer.analyze(df)
        mfh_res = self.mfh_analyzer.predict(df)
        
        # --- DeepSeek ---
        current_positions = [] 
        
        # Performance Stats
        trade_stats = self.db_manager.get_trade_performance_stats(limit=50)
        
        # Combine all advanced strategies for DeepSeek
        extra_analysis = {
            "crt": crt_res, 
            "pem": pem_res, 
            "mtf": mtf_res, 
            "adv": adv_res,
            "matrix_ml": ml_res, 
            "smc": smc_res, 
            "mfh": mfh_res,
            "active_params": self.short_term_params,
            "optimized_weights": self.hybrid_optimizer.weights
        }
        
        structure = self.deepseek_client.analyze_market_structure(
            market_snapshot, 
            current_positions=current_positions,
            extra_analysis=extra_analysis,
            performance_stats=trade_stats
        )
        
        # DeepSeek Signal
        ds_signal = structure.get('preliminary_signal', 'neutral')
        ds_score = structure.get('structure_score', 50)
        ds_pred = structure.get('short_term_prediction', 'neutral')
        if ds_signal == 'neutral':
             if ds_pred == 'bullish' and ds_score > 60: ds_signal = "buy"
             elif ds_pred == 'bearish' and ds_score > 60: ds_signal = "sell"
             
        # --- Qwen Strategy ---
        technical_signals = {
            "crt": crt_res, "price_equation": pem_res, "timeframe_analysis": tf_res,
            "advanced_tech": adv_sig, "matrix_ml": ml_res['signal'],
            "smc": smc_res['signal'], "mfh": mfh_res['signal'], "mtf": mtf_res['signal'],
            "deepseek_analysis": {
                "market_state": structure.get('market_state'),
                "preliminary_signal": ds_signal,
                "confidence": structure.get('signal_confidence'),
                "prediction": ds_pred
            },
            "performance_stats": trade_stats,
            "param_config": self.short_term_params
        }
        
        strategy = self.qwen_client.optimize_strategy_logic(structure, market_snapshot, technical_signals=technical_signals)
        
        # --- Final Decision Logic (Gold Style) ---
        qw_action = strategy.get('action', 'neutral').lower()
        final_signal = "neutral"
        if qw_action in ['buy', 'add_buy', 'limit_buy', 'buy_limit']: final_signal = "buy" 
        elif qw_action in ['sell', 'add_sell', 'limit_sell', 'sell_limit']: final_signal = "sell"
        elif qw_action in ['close', 'close_buy', 'close_sell']: final_signal = "close"
        elif qw_action == 'hold': final_signal = "hold"
        
        # Consensus Override
        reason = strategy.get('reason', 'LLM Decision')
        
        # Prepare Technical Consensus List
        tech_list = [crt_res['signal'], pem_res['signal'], adv_sig, ml_res['signal'], smc_res['signal'], mtf_res['signal']]
        
        if final_signal in ['hold', 'neutral']:
            # DeepSeek Override
            if ds_signal in ['buy', 'sell'] and ds_score >= 80:
                final_signal = ds_signal
                reason = f"[Override] DeepSeek High Confidence ({ds_score})"
            
            # Technical Consensus Override
            buy_votes = sum(1 for s in tech_list if s == 'buy')
            sell_votes = sum(1 for s in tech_list if s == 'sell')
            total_tech = len(tech_list)
            if total_tech > 0:
                if buy_votes/total_tech >= 0.7: 
                    final_signal = "buy"
                    reason = f"[Override] Tech Consensus Buy ({buy_votes}/{total_tech})"
                elif sell_votes/total_tech >= 0.7:
                    final_signal = "sell"
                    reason = f"[Override] Tech Consensus Sell ({sell_votes}/{total_tech})"
        
        # Smart Exit
        if qw_action == 'close' and final_signal != 'close':
            final_signal = 'close'
            reason = f"[Smart Exit] Qwen Profit Taking"

        # Strength Calc
        strength = 60
        valid_tech_count = sum(1 for s in tech_list if s != 'neutral')
        matching_count = sum(1 for s in tech_list if s == final_signal)
        if valid_tech_count > 0:
            strength += (matching_count / valid_tech_count) * 40
        if ds_signal == final_signal: strength = min(100, strength + 10)
        
        # Save Analysis
        self.latest_strategy = strategy
        self.latest_signal = final_signal
        
        # Save signal history for optimization
        if final_signal != 'neutral':
             # Format: (timestamp, signals_dict, close_price)
             signals_dict = {
                 "crt": crt_res['signal'], "pem": pem_res['signal'], "adv": adv_sig, 
                 "ml": ml_res['signal'], "smc": smc_res['signal'], "mtf": mtf_res['signal'],
                 "ds": ds_signal
             }
             self.signal_history.append((current_time, signals_dict, float(latest['close'])))
             if len(self.signal_history) > 1000: self.signal_history.pop(0)

        # --- Telegram Report ---
        ds_analysis_text = f"• Market State: {self.escape_markdown(structure.get('market_state', 'N/A'))}\n"
        ds_analysis_text += f"• Signal: {self.escape_markdown(ds_signal.upper())} (Conf: {ds_score}/100)\n"
        ds_analysis_text += f"• Prediction: {self.escape_markdown(ds_pred)}\n"
        ds_analysis_text += f"• Reasoning: {self.escape_markdown(structure.get('reasoning', 'N/A'))}\n"
        
        qw_reason = strategy.get('reason', strategy.get('rationale', 'Strategy Optimization'))
        qw_analysis_text = f"• Action: {self.escape_markdown(qw_action.upper())}\n"
        qw_analysis_text += f"• Logic: _{self.escape_markdown(qw_reason)}_\n"
        if 'param_config' in strategy:
             qw_analysis_text += f"• Params: Updated by LLM\n"
        
        # Calculate Risk/Lot
        risk_pct = self.calculate_dynamic_lot(strength, {'smc': smc_res}, ai_signals=technical_signals)
        suggested_lot_display = f"{risk_pct*100:.1f}% Equity"
        
        # SL/TP
        ref_price = latest['close']
        exit_conds = strategy.get('exit_conditions', {})
        opt_sl = exit_conds.get('sl_price')
        opt_tp = exit_conds.get('tp_price')
        
        if not opt_sl or not opt_tp:
             calc_sl, calc_tp = self.calculate_optimized_sl_tp(final_signal, ref_price, latest.get('atr', 0), market_context=adv_res)
             if not opt_sl: opt_sl = calc_sl
             if not opt_tp: opt_tp = calc_tp
             
        rr_str = "N/A"
        if opt_sl and opt_tp:
             risk = abs(ref_price - opt_sl)
             reward = abs(opt_tp - ref_price)
             if risk > 0: rr_str = f"1:{reward/risk:.2f}"

        msg = (
            f"🤖 *AI Crypto Strategy Report*\n"
            f"Symbol: `{self.symbol}` | TF: `{self.timeframe}`\n"
            f"Time: {datetime.now().strftime('%H:%M:%S')}\n\n"
            
            f"🕵️ *DeepSeek Analysis*\n"
            f"{ds_analysis_text}\n"
            
            f"🧙‍♂️ *Qwen Analysis*\n"
            f"{qw_analysis_text}\n"
            
            f"🏆 *Final Result*\n"
            f"• Decision: *{final_signal.upper()}* (Strength: {strength:.0f}%)\n"
            f"• Size: `{suggested_lot_display}`\n"
            f"• Reason: _{self.escape_markdown(reason)}_\n\n"
            
            f"🎯 *Setup (OKX)*\n"
            f"• Entry: `{ref_price:.2f}`\n"
            f"• SL: `{opt_sl:.2f}`\n"
            f"• TP: `{opt_tp:.2f}`\n"
            f"• R:R: `{rr_str}`"
        )
        self.send_telegram_message(msg)
        
        return df, final_signal, strategy, strength, opt_sl, opt_tp, risk_pct

    def optimize_short_term_params(self):
        """
        Optimize short-term strategy parameters (RVGI+CCI, IFVG) using WOAm
        """
        logger.info("Running Short-Term Parameter Optimization (WOAm)...")
        
        # 1. Get Data (Last 500 candles)
        df = self.data_processor.get_historical_data(self.symbol, self.timeframe, limit=500)
        if df is None or len(df) < 200:
            return
            
        # 2. Define Objective Function
        def objective(params):
            p_rvgi_sma = int(params[0])
            p_rvgi_cci = int(params[1])
            p_ifvg_gap = int(params[2])
            
            # Backtest Simulation
            # Use a simplified backtest core to evaluate these params on recent data
            # We iterate through the last N bars and check signal profitability
            
            backtest_window = 100
            if len(df) < backtest_window + 50: return -100
            
            test_data = df.iloc[-(backtest_window+50):] # Add buffer for indicators
            
            # Recalculate indicators with new params
            # Note: This can be slow inside an optimization loop. 
            # In a real efficient system, we would pre-calculate or use vectorization.
            # Here we call the adapter which uses pandas rolling (fast enough for 100 bars)
            
            param_dict = {'rvgi_sma': p_rvgi_sma, 'rvgi_cci': p_rvgi_cci, 'ifvg_gap': p_ifvg_gap}
            
            # We can't call analyze_full for every bar as it's too heavy.
            # We call specific strategy functions directly.
            
            # Calculate RVGI/CCI signals for the whole window
            rvgi_res = self.advanced_adapter.analyze_rvgi_cci_strategy(test_data, sma_period=p_rvgi_sma, cci_period=p_rvgi_cci)
            
            # Calculate IFVG signals
            ifvg_res = self.advanced_adapter.analyze_ifvg(test_data, min_gap_points=p_ifvg_gap)
            
            # Evaluate
            # Since analyze_rvgi_cci_strategy only returns the LATEST signal, 
            # we actually need to run it on a rolling basis or modify the analyzer to return series.
            # The current AdvancedMarketAnalysis is designed for snapshot analysis.
            
            # For "NO SIMPLIFICATION", we must simulate properly.
            # We will iterate the last 50 bars.
            
            balance = 1000.0
            position = 0
            entry_price = 0
            
            closes = test_data['close'].values
            
            # To avoid re-calculating everything 50 times inside the optimizer (which runs 100s of times),
            # we accept a slight simplification: we optimize based on the LATEST snapshot's strength 
            # matched against recent trend? No, that's overfitting.
            
            # Correct approach: Vectorized backtest of the logic.
            # But the logic is in `analyze_rvgi_cci_strategy`.
            
            # Let's try a robust heuristic:
            # We optimize for parameters that would have generated a correct signal 
            # at the most recent significant pivot points.
            
            # Or, we just accept the cost and loop 20 times (last 20 candles).
            
            total_profit = 0
            trades_count = 0
            
            for i in range(len(test_data)-20, len(test_data)):
                sub_df = test_data.iloc[:i+1]
                
                # Check signals
                res_rvgi = self.advanced_adapter.analyze_rvgi_cci_strategy(sub_df, sma_period=p_rvgi_sma, cci_period=p_rvgi_cci)
                res_ifvg = self.advanced_adapter.analyze_ifvg(sub_df, min_gap_points=p_ifvg_gap)
                
                sig = "neutral"
                if res_rvgi['signal'] == 'buy' or res_ifvg['signal'] == 'buy': sig = 'buy'
                elif res_rvgi['signal'] == 'sell' or res_ifvg['signal'] == 'sell': sig = 'sell'
                
                # Check profit 5 bars later (or end of data)
                if sig != "neutral" and i + 5 < len(test_data):
                    entry = closes[i]
                    exit_p = closes[i+5]
                    if sig == 'buy': profit = (exit_p - entry) / entry
                    else: profit = (entry - exit_p) / entry
                    
                    total_profit += profit
                    trades_count += 1
            
            if trades_count == 0: return 0
            return total_profit
            
        # 3. Optimize
        bounds = [(10, 50), (10, 30), (10, 100)]
        # Increased steps/epochs for better convergence
        # steps=[1, 1, 1] ensures integer steps for the 3 parameters
        best_params, best_score = self.optimizers['WOAm'].optimize(objective, bounds, steps=[1, 1, 1], epochs=3)
        
        self.short_term_params['rvgi_sma'] = int(best_params[0])
        self.short_term_params['rvgi_cci'] = int(best_params[1])
        self.short_term_params['ifvg_gap'] = int(best_params[2])
        
        logger.info(f"Updated Params (Score {best_score:.4f}): {self.short_term_params}")

    def optimize_weights(self):
        """Optimize Hybrid Weights based on history (Full Implementation)"""
        if len(self.signal_history) < 20: return
        
        logger.info(f"Running Weight Optimization... Samples: {len(self.signal_history)}")
        
        # 1. Prepare Data
        samples = []
        for i in range(len(self.signal_history) - 1):
            curr = self.signal_history[i]
            next_bar = self.signal_history[i+1]
            signals = curr[1]
            price_change = next_bar[2] - curr[2]
            actual_dir = 1 if price_change > 0 else -1 if price_change < 0 else 0
            if actual_dir != 0: samples.append((signals, actual_dir))
            
        if len(samples) < 10: return

        # 2. Objective Function
        strategy_keys = list(self.hybrid_optimizer.weights.keys())
        
        def objective(weights_vec):
            correct = 0; total = 0
            temp_weights = {k: w for k, w in zip(strategy_keys, weights_vec)}
            
            for signals, actual_dir in samples:
                weighted_sum = 0; total_w = 0
                for strat, sig in signals.items():
                    w = temp_weights.get(strat, 1.0)
                    if sig == 'buy': weighted_sum += w
                    elif sig == 'sell': weighted_sum -= w
                    total_w += w
                
                if total_w > 0:
                    score = weighted_sum / total_w
                    pred = 1 if score > 0.15 else -1 if score < -0.15 else 0
                    if pred == actual_dir: correct += 1
                    total += 1
            return correct / total if total > 0 else 0

        # 3. Optimize
        bounds = [(0.0, 2.0) for _ in range(len(strategy_keys))]
        best_weights, best_score = self.optimizers['WOAm'].optimize(objective, bounds, steps=None, epochs=3)
        
        # 4. Apply
        if best_score > 0.4: # Only update if decent accuracy
            for i, k in enumerate(strategy_keys):
                self.hybrid_optimizer.weights[k] = best_weights[i]
            logger.info(f"Weights Updated (Acc {best_score:.2%}): {self.hybrid_optimizer.weights}")
        else:
            logger.info(f"Weight optimization score too low ({best_score:.2%}), skipping update.")

    def _send_order(self, type_str, price, sl, tp, volume_pct):
        """Wrapper for OKX Order with Validation"""
        # 1. Validation (Invalid Stops)
        current_price = self.data_processor.get_current_price(self.symbol)
        if not current_price: return
        
        is_buy = 'buy' in type_str
        is_sell = 'sell' in type_str
        
        # Auto-Correct Invalid Stops
        if is_buy:
             if sl > 0 and sl >= current_price: 
                 logger.warning("Invalid SL for BUY. Removing.")
                 sl = 0.0
             if tp > 0 and tp <= current_price:
                 logger.warning("Invalid TP for BUY. Removing.")
                 tp = 0.0
        elif is_sell:
             if sl > 0 and sl <= current_price:
                 logger.warning("Invalid SL for SELL. Removing.")
                 sl = 0.0
             if tp > 0 and tp >= current_price:
                 logger.warning("Invalid TP for SELL. Removing.")
                 tp = 0.0
                 
        # 2. Calculate Contracts with Margin Check
        balance = self.data_processor.get_account_balance('USDT')
        if not balance:
            logger.error("Failed to fetch balance. Aborting order.")
            return

        equity = balance.get('total', 0)
        free_balance = balance.get('free', 0)
        
        # Leverage (Default 5x)
        leverage = 5 
        self.data_processor.set_leverage(self.symbol, leverage)
        
        # Calculate target margin
        # volume_pct is derived from AI risk (e.g. 0.02 for 2% risk)
        # We treat this as "Risk 2% of Equity", so Margin = Equity * volume_pct
        target_margin = equity * volume_pct
        
        # Safety Check: Ensure we don't exceed available free balance
        # Leave 5% buffer for fees/fluctuations
        max_margin = free_balance * 0.95
        
        if target_margin > max_margin:
            logger.warning(f"Target margin {target_margin:.2f} exceeds free balance {free_balance:.2f}. Adjusting to {max_margin:.2f}")
            target_margin = max_margin
            
        if target_margin < 0.5: # Minimum order size check (lowered to allow smaller trades for cheap assets)
            logger.warning(f"Margin {target_margin:.2f} too small. Skipping.")
            return

        # Calculate Notional Value and Contracts
        amount_usdt = target_margin * leverage
        amount_coins = amount_usdt / current_price
        
        # Contract Size Logic
        # Try to get contract size from data processor if available, else fallback
        try:
            contract_size = self.data_processor.get_contract_size(self.symbol)
            if not contract_size:
                raise ValueError("Contract size not found")
        except:
             # Fallback if API fails
             if 'ETH' in self.symbol: contract_size = 0.1
             elif 'BTC' in self.symbol: contract_size = 0.01
             elif 'SOL' in self.symbol: contract_size = 1.0
             else: contract_size = 1.0 
        
        contracts = int(amount_coins / contract_size)
        
        if contracts < 1:
            logger.warning(f"Calculated contracts {contracts} < 1 (Size: {contract_size}). Skipping.")
            return
        
        # 3. Execute
        try:
            side = 'buy' if is_buy else 'sell'
            
            logger.info(f"Placing Order: {side} {contracts} contracts (Margin: {target_margin:.2f} USDT)")
            
            order = self.data_processor.create_order(self.symbol, side, contracts, type='market')
            if order:
                 logger.info(f"Order Executed: {side} {contracts}")
                 # Place SL/TP
                 if sl > 0 or tp > 0:
                     self.data_processor.place_sl_tp_order(self.symbol, 'sell' if is_buy else 'buy', contracts, sl_price=sl, tp_price=tp)
        except Exception as e:
            logger.error(f"Execution Failed: {e}")

    def execute_trade(self, signal, strategy, risk_pct, sl, tp):
        """Execute trade based on analyzed signal"""
        # Check current positions
        positions = []
        try:
            raw_pos = self.data_processor.exchange.fetch_positions([self.symbol])
            positions = [p for p in raw_pos if float(p['contracts']) > 0]
        except: pass
        
        has_pos = len(positions) > 0
        pos_side = positions[0]['side'] if has_pos else None # 'long' or 'short'
        
        # Close Logic
        if signal == 'close':
            if has_pos:
                logger.info("Closing position...")
                close_side = 'sell' if pos_side == 'long' else 'buy'
                amt = float(positions[0]['contracts'])
                self.data_processor.cancel_all_orders(self.symbol)
                self.data_processor.create_order(self.symbol, close_side, amt, type='market')
                self.send_telegram_message(f"🚫 *Position Closed* (Smart Exit)")
            return

        # Reversal Logic
        if has_pos:
             is_reversal = (signal == 'buy' and pos_side == 'short') or (signal == 'sell' and pos_side == 'long')
             if is_reversal:
                 logger.info("Reversal detected. Closing first.")
                 close_side = 'sell' if pos_side == 'long' else 'buy'
                 amt = float(positions[0]['contracts'])
                 self.data_processor.cancel_all_orders(self.symbol)
                 self.data_processor.create_order(self.symbol, close_side, amt, type='market')
                 has_pos = False # Now we are flat
        
        # Open/Add Logic
        if signal in ['buy', 'sell']:
             if not has_pos:
                 logger.info(f"Opening New Position: {signal.upper()}")
                 self._send_order(signal, 0, sl, tp, risk_pct)
             else:
                 # Update SL/TP for existing
                 logger.info("Updating SL/TP for existing position")
                 if sl > 0 or tp > 0:
                     amt = float(positions[0]['contracts'])
                     self.data_processor.cancel_all_orders(self.symbol) # Cancel old SL/TP
                     sl_side = 'sell' if pos_side == 'long' else 'buy'
                     self.data_processor.place_sl_tp_order(self.symbol, sl_side, amt, sl_price=sl, tp_price=tp)

    def run_once(self):
        try:
            df, signal, strategy, strength, sl, tp, risk = self.analyze_market()
            if signal:
                self.execute_trade(signal, strategy, risk, sl, tp)
            # self.db_manager.perform_checkpoint() # Managed by external script
        except Exception as e:
            logger.error(f"Cycle Error: {e}", exc_info=True)

    def start(self):
        self.is_running = True
        self.sync_account_history() # Sync on start
        logger.info(f"Bot started for {self.symbol}")
        while self.is_running:
            self.run_once()
            time.sleep(self.interval)

if __name__ == "__main__":
    bot = CryptoTradingBot(symbol='ETH/USDT:USDT', timeframe='15m', interval=900) 
    bot.start()
