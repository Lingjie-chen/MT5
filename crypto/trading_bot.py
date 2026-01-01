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
        
        if df.empty: return None, None
            
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
        
        crt_res = self.crt_analyzer.analyze(self.symbol, latest, current_time)
        self.price_model.update(float(latest['close']))
        pem_res = self.price_model.predict(df)
        tf_res = self.tf_analyzer.analyze(self.symbol, current_time)
        
        # HTF Data for MTF
        df_htf1 = self.data_processor.get_historical_data(self.symbol, '1h', limit=500)
        df_htf2 = self.data_processor.get_historical_data(self.symbol, '4h', limit=500)
        mtf_res = self.mtf_analyzer.analyze(df, df_htf1, df_htf2) # Updated MTF signature
        
        adv_res = self.advanced_adapter.analyze_full(df, params=self.short_term_params)
        adv_sig = adv_res['signal_info']['signal'] if adv_res else 'neutral'
        
        ticks = [] # Crypto tick data hard to fetch in batch here, skip or implement later
        ml_res = self.matrix_ml.predict(ticks)
        
        smc_res = self.smc_analyzer.analyze(df)
        mfh_res = self.mfh_analyzer.predict(df)
        
        # --- DeepSeek ---
        current_positions = [] # Fetch actual positions if possible
        
        # Performance Stats
        trade_stats = self.db_manager.get_trade_performance_stats(limit=50)
        
        extra_analysis = {
            "crt": crt_res, "pem": pem_res, "mtf": mtf_res, "adv": adv_res,
            "matrix_ml": ml_res, "smc": smc_res, "mfh": mfh_res
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
            "performance_stats": trade_stats
        }
        
        strategy = self.qwen_client.optimize_strategy_logic(structure, market_snapshot, technical_signals=technical_signals)
        
        # --- Final Decision Logic (Gold Style) ---
        qw_action = strategy.get('action', 'neutral').lower()
        final_signal = "neutral"
        if qw_action in ['buy', 'add_buy', 'limit_buy', 'buy_limit']: final_signal = "buy" # Force Market
        elif qw_action in ['sell', 'add_sell', 'limit_sell', 'sell_limit']: final_signal = "sell" # Force Market
        elif qw_action in ['close', 'close_buy', 'close_sell']: final_signal = "close"
        elif qw_action == 'hold': final_signal = "hold"
        
        # Consensus Override
        reason = strategy.get('reason', 'LLM Decision')
        if final_signal in ['hold', 'neutral']:
            # DeepSeek Override
            if ds_signal in ['buy', 'sell'] and ds_score >= 80:
                final_signal = ds_signal
                reason = f"[Override] DeepSeek High Confidence ({ds_score})"
            
            # Technical Consensus Override
            tech_list = [crt_res['signal'], pem_res['signal'], adv_sig, ml_res['signal'], smc_res['signal'], mtf_res['signal']]
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
        
        # --- Telegram Report ---
        ds_analysis_text = f"• Market State: {self.escape_markdown(structure.get('market_state', 'N/A'))}\n"
        ds_analysis_text += f"• Signal: {self.escape_markdown(ds_signal.upper())} (Conf: {ds_score}/100)\n"
        ds_analysis_text += f"• Prediction: {self.escape_markdown(ds_pred)}\n"
        ds_analysis_text += f"• Reasoning: {self.escape_markdown(structure.get('reasoning', 'N/A'))}\n"
        
        qw_reason = strategy.get('reason', strategy.get('rationale', 'Strategy Optimization'))
        qw_analysis_text = f"• Action: {self.escape_markdown(qw_action.upper())}\n"
        qw_analysis_text += f"• Logic: _{self.escape_markdown(qw_reason)}_\n"
        
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
                 
        # 2. Calculate Contracts
        balance = self.data_processor.get_account_balance('USDT')
        equity = balance['total'] if balance else 1000.0
        
        target_val = equity * volume_pct
        amount = target_val / current_price
        # Simple contract size logic, adjust per symbol if needed
        contract_size = 0.1 if 'ETH' in self.symbol else 0.01 if 'BTC' in self.symbol else 1.0
        contracts = max(1, int(amount / contract_size))
        
        # 3. Execute
        try:
            side = 'buy' if is_buy else 'sell'
            self.data_processor.set_leverage(self.symbol, 5) # Default 5x
            
            # Attach Algo (SL/TP)
            # Use separate method or algo params if supported
            # Here we place market order then SL/TP
            
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
            self.db_manager.perform_checkpoint()
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
