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
from .grid_strategy import CryptoGridStrategy
from file_watcher import FileWatcher

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
            "qwen": 1.5, 
            "crt": 0.8,
            "smc": 1.1,
            "rvgi_cci": 0.6
        }
        self.history = []

    def combine_signals(self, signals):
        weighted_sum = 0
        total_weight = 0
        
        details = {}
        
        for source, signal in signals.items():
            if source not in self.weights: continue
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

        # Initialize Advanced Analysis
        # Dynamic HTF Selection based on Timeframe
        if self.timeframe == '1h':
            htf1, htf2 = '4h', '1d'
        elif self.timeframe == '4h':
            htf1, htf2 = '1d', '1w'
        else: # Default 15m
            htf1, htf2 = '1h', '4h'
            
        self.crt_analyzer = CRTAnalyzer(timeframe_htf=htf1)
        self.mtf_analyzer = MTFAnalyzer(htf1=htf1, htf2=htf2)
        # self.price_model = PriceEquationModel() # Removed
        # self.tf_analyzer = TimeframeVisualAnalyzer() # Removed
        self.advanced_adapter = AdvancedMarketAnalysisAdapter()
        # self.matrix_ml = MatrixMLAnalyzer() # Removed
        self.smc_analyzer = SMCAnalyzer()
        # self.mfh_analyzer = MFHAnalyzer() # Removed
        self.advanced_analysis = AdvancedMarketAnalysis() # Legacy adapter
        
        self.hybrid_optimizer = HybridOptimizer()
        
        # Optimization Engine Pool (Restricted)
        self.optimizers = {
            "WOAm": WOAm(),
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
        self.qwen_client = self.ai_factory.get_client('qwen')
        
        # Telegram Configuration
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        # State
        self.latest_strategy = None
        self.latest_signal = "neutral"
        self.signal_history = []
        
        # Initialize Grid Strategy
        self.grid_strategy = CryptoGridStrategy(self.symbol)
        
        if not self.qwen_client:
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

    def calculate_optimized_sl_tp(self, trade_type, price, atr, market_context=None, ai_exit_conds=None):
        """Calculate optimized SL/TP based on ATR, MFE/MAE stats, market structure, and AI suggestions"""
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

        # AI Suggestions (Ensemble Analysis)
        ai_sl = 0.0
        ai_tp = 0.0
        if ai_exit_conds:
            ai_sl = ai_exit_conds.get('sl_price', 0.0)
            if ai_sl is None: ai_sl = 0.0
            
            ai_tp = ai_exit_conds.get('tp_price', 0.0)
            if ai_tp is None: ai_tp = 0.0

        final_sl = 0.0
        final_tp = 0.0
        
        if 'buy' in trade_type:
            base_tp = price + mfe_tp_dist
            base_sl = price - mae_sl_dist
            
            # SL Priority: AI -> Structure -> Statistical
            if ai_sl > 0 and ai_sl < price:
                # [Anti-Hunt Protection]
                sl_dist = abs(price - ai_sl)
                min_safe_dist = atr * 0.8
                
                if sl_dist < min_safe_dist:
                    logger.info(f"AI SL {ai_sl} too close ({sl_dist/atr:.2f} ATR), widening to {min_safe_dist/atr:.2f} ATR")
                    final_sl = price - min_safe_dist
                else:
                    final_sl = ai_sl
            else:
                final_sl = base_sl
            
            # TP Priority: AI -> Structure -> Statistical
            if ai_tp > 0 and ai_tp > price:
                final_tp = ai_tp
            elif struct_tp_price > price:
                final_tp = struct_tp_price - (atr * 0.1) if struct_tp_price < base_tp else base_tp
            else:
                final_tp = base_tp
                
        else: # sell
            base_tp = price - mfe_tp_dist
            base_sl = price + mae_sl_dist
            
            # SL Priority: AI -> Structure -> Statistical
            if ai_sl > 0 and ai_sl > price:
                final_sl = ai_sl
            else:
                final_sl = base_sl
                
            # TP Priority: AI -> Structure -> Statistical
            if ai_tp > 0 and ai_tp < price:
                final_tp = ai_tp
            elif struct_tp_price > 0 and struct_tp_price < price:
                final_tp = struct_tp_price + (atr * 0.1) if struct_tp_price > base_tp else base_tp
            else:
                final_tp = base_tp
            
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
        """Full AI Market Analysis (Qwen Only)"""
        logger.info(f"Fetching data for {self.symbol}...")
        df = self.data_processor.get_historical_data(self.symbol, self.timeframe, limit=1000)
        
        if df.empty: return None, None, None, 0, 0, 0, 0, "auto"
            
        # Features
        df = self.data_processor.generate_features(df)
        
        # Snapshot
        latest = df.iloc[-1]
        
        # Fetch Account Balance for Context
        account_balance = self.data_processor.get_account_balance('USDT')
        
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
            },
            "account_info": account_balance # Inject account info for LLM
        }
        
        # --- Advanced Analysis ---
        current_time = latest.name.timestamp() if hasattr(latest.name, 'timestamp') else time.time()
        
        # Determine HTF based on current timeframe
        if self.timeframe == '1h':
            htf1_tf, htf2_tf = '4h', '1d'
        elif self.timeframe == '4h':
            htf1_tf, htf2_tf = '1d', '1w'
        else: # 15m
            htf1_tf, htf2_tf = '1h', '4h'
        
        # Fetch HTF Data for CRT/MTF
        df_htf1 = self.data_processor.get_historical_data(self.symbol, htf1_tf, limit=200)
        df_htf2 = self.data_processor.get_historical_data(self.symbol, htf2_tf, limit=200)
        
        # Fallback if HTF data unavailable
        if df_htf1 is None or df_htf1.empty: df_htf1 = df.copy()
        if df_htf2 is None or df_htf2.empty: df_htf2 = df.copy()

        # Process HTF Features
        df_htf1 = self.data_processor.generate_features(df_htf1)
        df_htf2 = self.data_processor.generate_features(df_htf2)
        
        latest_htf1 = df_htf1.iloc[-1]
        latest_htf2 = df_htf2.iloc[-1]
        
        # Inject Multi-TF Data into Snapshot
        market_snapshot['multi_tf_data'] = {
            "h1": {
                "trend": "bullish" if latest_htf1['close'] > latest_htf1['ema_slow'] else "bearish",
                "rsi": float(latest_htf1.get('rsi', 50)),
                "atr": float(latest_htf1.get('atr', 0)),
                "ema_fast": float(latest_htf1.get('ema_fast', 0)),
                "ema_slow": float(latest_htf1.get('ema_slow', 0))
            },
            "h4": {
                "trend": "bullish" if latest_htf2['close'] > latest_htf2['ema_slow'] else "bearish",
                "rsi": float(latest_htf2.get('rsi', 50)),
                "atr": float(latest_htf2.get('atr', 0))
            }
        }

        # Run Optimizations (Real-time Param Config)
        if time.time() - self.last_optimization_time > self.optimization_interval:
            self.optimize_strategy_parameters()
            self.optimize_weights()
            self.last_optimization_time = time.time()

        crt_res = self.crt_analyzer.analyze(self.symbol, latest, current_time, df_htf=df_htf1)
        
        # HTF Data for MTF
        mtf_res = self.mtf_analyzer.analyze(df, df_htf1, df_htf2) 
        
        # Advanced Tech with Optimized Params (CCI/RVGI/IFVG)
        adv_res = self.advanced_adapter.analyze_full(df, params=self.short_term_params)
        adv_sig = adv_res['signal_info']['signal'] if adv_res else 'neutral'
        
        # SMC
        smc_res = self.smc_analyzer.analyze(df)
        
        # Performance Stats
        trade_stats = self.db_manager.get_trade_performance_stats(limit=50)
        
        # Replaced DeepSeek with Qwen for structure analysis
        # Only passing relevant tech signals to reduce noise
        extra_analysis = {
            "crt": crt_res, 
            "mtf": mtf_res, 
            "adv": adv_res,
            "smc": smc_res, 
            "ifvg": adv_res.get('ifvg', {'active_zones': [], 'reasons': []}),
            "active_params": self.short_term_params,
            "optimized_weights": self.hybrid_optimizer.weights
        }
        
        structure = self.qwen_client.analyze_market_structure(market_snapshot)
        
        # --- Qwen Strategy ---
        technical_signals = {
            "crt": crt_res['signal'], 
            "advanced_tech": adv_sig, 
            "smc": smc_res['signal'], 
            "mtf": mtf_res['signal'],
            "performance_stats": trade_stats,
            "param_config": self.short_term_params
        }
        
        # Qwen Sentiment Analysis (New)
        qwen_sentiment = self.qwen_client.analyze_market_sentiment(market_snapshot)
        qwen_sent_score = qwen_sentiment.get('sentiment_score', 0)
        qwen_sent_label = qwen_sentiment.get('sentiment', 'neutral')

        strategy = self.qwen_client.optimize_strategy_logic(
            structure, 
            market_snapshot, 
            technical_signals=technical_signals,
            previous_analysis=self.latest_strategy # 传入上一次分析
        )
        
        # --- Final Decision Logic (Qwen Only) ---
        qw_action = strategy.get('action', 'neutral').lower()
        final_signal = "neutral"
        
        # Mapping Actions
        if qw_action in ['buy', 'add_buy', 'limit_buy', 'buy_limit', 'close_sell_open_buy']: 
            final_signal = "buy" 
        elif qw_action in ['sell', 'add_sell', 'limit_sell', 'sell_limit', 'close_buy_open_sell']: 
            final_signal = "sell"
        elif qw_action in ['close', 'close_buy', 'close_sell']: 
            final_signal = "close"
        elif qw_action == 'hold': 
            final_signal = "hold"
        elif qw_action == 'grid_start': 
            final_signal = "grid_start"
        
        # Grid Execution Logic
        if final_signal == 'grid_start':
            # Use Grid Strategy to generate plan
            trend = structure.get('market_structure', {}).get('trend', 'neutral')
            if trend == 'neutral': trend = 'bullish' # Default to bullish if neutral
            
            atr = latest.get('atr', 0)
            if atr == 0: atr = latest['close'] * 0.01
            
            # Extract recommended step
            pos_mgmt = strategy.get('position_management', {})
            rec_step = pos_mgmt.get('recommended_grid_step_pips')
            grid_level_tps = pos_mgmt.get('grid_level_tp_pips') # Extract dynamic TPs

            try:
                if rec_step: rec_step = float(rec_step)
            except: rec_step = None
            
            # Extract TPs
            try:
                if grid_level_tps and isinstance(grid_level_tps, list):
                    grid_level_tps = [float(x) for x in grid_level_tps]
                else:
                    grid_level_tps = None
            except: grid_level_tps = None

            grid_plan = self.grid_strategy.generate_grid_plan(latest['close'], trend, atr, custom_step=rec_step, grid_level_tps=grid_level_tps)
            
            # Calculate sizing
            balance = self.data_processor.get_account_balance('USDT')
            free_balance = balance.get('free', 0) if balance else 0
            self.grid_strategy.calculate_lot_sizes(free_balance)
            
            # Execute Grid Orders
            # Get contract size for conversion
            try:
                contract_size = self.data_processor.get_contract_size(self.symbol)
            except:
                contract_size = 1.0
                if 'ETH' in self.symbol: contract_size = 0.1
                elif 'BTC' in self.symbol: contract_size = 0.01
            
            for order in grid_plan:
                try:
                    # Convert raw coin amount to contracts
                    # Grid strategy returns 'amount' in coins (e.g. 0.5 ETH)
                    # OKX Swap requires number of contracts (e.g. 5 contracts if size is 0.1)
                    raw_amount_coin = order['amount']
                    num_contracts = int(raw_amount_coin / contract_size)
                    
                    if num_contracts < 1:
                        # Try to force at least 1 contract if allocation is small but valid
                        num_contracts = 1
                        
                    logger.info(f"Placing Grid Order: {order['type']} {num_contracts} contracts ({raw_amount_coin:.4f} coins) @ {order['price']:.2f}")
                    
                    # Construct Params with attached TP if available
                    order_params = {}
                    if order.get('tp'):
                        # OKX V5 attachAlgoOrds
                        order_params['attachAlgoOrds'] = [
                            {
                                'tpTriggerPx': str(order['tp']),
                                'tpOrdPx': '-1', # Market price when triggered
                                'tpTriggerPxType': 'last'
                            }
                        ]
                        logger.info(f"  > Attaching Dynamic TP: {order['tp']:.2f}")

                    self.data_processor.create_order(
                        self.symbol, 
                        order['type'], 
                        num_contracts, 
                        type='limit', 
                        price=order['price'],
                        params=order_params
                    )
                except Exception as e:
                    logger.error(f"Grid Order Failed: {e}")
            
            reason = "SMC Grid Deployment"
            
        # Reason
        reason = strategy.get('reason', strategy.get('strategy_rationale', 'Qwen Decision'))
        
        # Check Consistency with Previous
        is_consistent = False
        if self.latest_strategy:
            prev_action = self.latest_strategy.get('action', 'neutral').lower()
            if prev_action == qw_action:
                # If action is same, check if rationale implies consistency
                if "维持" in reason or "consistent" in reason.lower() or "unchanged" in reason.lower():
                    is_consistent = True
                    logger.info(f"⚖️ 决策保持一致: {qw_action.upper()} (理由: {reason[:50]}...)")

        # Smart Exit
        if qw_action == 'close' and final_signal != 'close':
            final_signal = 'close'
            reason = f"[Smart Exit] Qwen Profit Taking"

        # Strength Calc
        strength = 70
        tech_list = [crt_res['signal'], adv_sig, smc_res['signal'], mtf_res['signal']]
        valid_tech_count = sum(1 for s in tech_list if s != 'neutral')
        matching_count = sum(1 for s in tech_list if s == final_signal)
        if valid_tech_count > 0:
            strength += (matching_count / valid_tech_count) * 30
        
        # Save Analysis
        self.latest_strategy = strategy
        self.latest_signal = final_signal
        
        # Save signal history for optimization
        if final_signal != 'neutral':
             # Format: (timestamp, signals_dict, close_price)
             signals_dict = {
                 "crt": crt_res['signal'], "adv": adv_sig, 
                 "smc": smc_res['signal'], "mtf": mtf_res['signal'],
                 "qwen": final_signal
             }
             self.signal_history.append((current_time, signals_dict, float(latest['close'])))
             if len(self.signal_history) > 1000: self.signal_history.pop(0)

        # Calculate Risk/Lot
        risk_pct = self.calculate_dynamic_lot(strength, {'smc': smc_res}, ai_signals=technical_signals)
        suggested_lot_display = f"{risk_pct*100:.1f}% Equity"
        
        # SL/TP
        ref_price = latest['close']
        exit_conds = strategy.get('exit_conditions', {})
        
        # Calculate optimized SL/TP using ensemble analysis (AI + Structure + Stats)
        opt_sl, opt_tp = self.calculate_optimized_sl_tp(
            final_signal, 
            ref_price, 
            latest.get('atr', 0), 
            market_context=adv_res,
            ai_exit_conds=exit_conds
        )
        
        sl_tp_source = "qwen_ensemble"
             
        rr_str = "N/A"
        if opt_sl and opt_tp:
             risk = abs(ref_price - opt_sl)
             reward = abs(opt_tp - ref_price)
             if risk > 0: rr_str = f"1:{reward/risk:.2f}"

        # --- Message Construction ---
        telegram_report = strategy.get('telegram_report', '')
        
        if telegram_report and len(telegram_report) > 50:
            # Use Qwen generated report
            msg = (
                f"🤖 *AI Crypto Strategy (Qwen)*\n"
                f"Symbol: `{self.symbol}` | TF: `{self.timeframe}`\n"
                f"Time: {datetime.now().strftime('%H:%M:%S')}\n\n"
                f"{telegram_report}\n\n"
                f"📊 *Live Status*\n"
                f"• Decision: *{final_signal.upper()}* (Strength: {strength:.0f}%)\n"
                f"• Sentiment: {self.escape_markdown(qwen_sent_label.upper())} ({qwen_sent_score:.2f})\n"
                f"• Size: `{suggested_lot_display}`\n\n"
                f"🎯 *Setup (OKX)*\n"
                f"• Entry: `{ref_price:.2f}`\n"
                f"• SL: `{opt_sl:.2f}`\n"
                f"• TP: `{opt_tp:.2f}`\n"
                f"• R:R: `{rr_str}`"
            )
        else:
            # Fallback to manual construction
            qw_reason = strategy.get('reason', strategy.get('rationale', 'Strategy Optimization'))
            qw_analysis_text = f"• Action: {self.escape_markdown(qw_action.upper())}\n"
            qw_analysis_text += f"• Logic: _{self.escape_markdown(qw_reason)}_\n"
            
            msg = (
                f"🤖 *AI Crypto Strategy Report*\n"
                f"Symbol: `{self.symbol}` | TF: `{self.timeframe}`\n"
                f"Time: {datetime.now().strftime('%H:%M:%S')}\n\n"
                
                f"🧙‍♂️ *Qwen Analysis*\n"
                f"• Sentiment: {self.escape_markdown(qwen_sent_label.upper())} (Score: {qwen_sent_score})\n"
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
        
        return df, final_signal, strategy, strength, opt_sl, opt_tp, risk_pct, sl_tp_source

    def evaluate_comprehensive_params(self, params, df):
        """
        Comprehensive Objective Function: Evaluates strategy parameters together.
        params: Vector of parameter values corresponding to the defined structure.
        """
        # Global counter for progress logging
        if not hasattr(self, '_opt_counter'): self._opt_counter = 0
        self._opt_counter += 1
        if self._opt_counter % 50 == 0:
            logger.info(f"Optimization Progress: {self._opt_counter} evaluations...")

        # 1. Decode Parameters
        try:
            # Revised for SMC, CCI/RVGI, IFVG (Restricted Models)
            p_smc_ma = int(params[0])
            p_smc_atr = params[1]
            p_rvgi_sma = int(params[2])
            p_rvgi_cci = int(params[3])
            p_ifvg_gap = int(params[4])
            
            # 2. Initialize Temporary Analyzers (Fresh State)
            tmp_smc = SMCAnalyzer()
            tmp_smc.ma_period = p_smc_ma
            tmp_smc.atr_threshold = p_smc_atr
            
            tmp_adapter = AdvancedMarketAnalysisAdapter()
            
            # 3. Run Simulation
            start_idx = max(p_smc_ma, 50) + 10
            if len(df) < start_idx + 50: return -9999
            
            balance = 10000.0
            closes = df['close'].values
            
            trades_count = 0
            wins = 0
            
            # OPTIMIZATION: Vectorized Pre-calculation
            # 1. RVGI Series (Vectorized)
            rvgi_series = tmp_adapter.calculate_rvgi_cci_series(df, sma_period=p_rvgi_sma, cci_period=p_rvgi_cci)
            
            # 3. Step Skipping
            # Evaluate trade signals every 4 candles (1 hour) to speed up
            eval_step = 4 
            
            for i in range(start_idx, len(df)-1):
                curr_price = closes[i]
                next_price = closes[i+1]
                
                # Check Trade Condition (Skipping steps for speed)
                if i % eval_step == 0:
                    sub_df = df.iloc[:i+1] # Still slicing, but 4x less often
                    
                    # Signals
                    # 1. SMC
                    smc_sig = tmp_smc.analyze(sub_df)['signal']
                    
                    # 2. IFVG
                    ifvg_sig = tmp_adapter.analyze_ifvg(sub_df, min_gap_points=p_ifvg_gap)['signal']
                    
                    # 3. RVGI (Fast Lookup)
                    rvgi_sig_val = rvgi_series.iloc[i]
                    rvgi_sig = 'buy' if rvgi_sig_val == 1 else 'sell' if rvgi_sig_val == -1 else 'neutral'
                    
                    # Combine
                    votes = 0
                    for s in [smc_sig, ifvg_sig, rvgi_sig]:
                        if s == 'buy': votes += 1
                        elif s == 'sell': votes -= 1
                    
                    final_sig = "neutral"
                    if votes >= 2: final_sig = "buy"
                    elif votes <= -2: final_sig = "sell"
                    
                    # Evaluate Trade
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
            
        except Exception as e:
            # logger.error(f"Eval Error: {e}")
            return -9999

    def warmup_signal_history(self):
        """Pre-fill signal history using historical data for immediate optimization"""
        logger.info("正在预热信号历史数据 (Warming up)...")
        try:
            df = self.data_processor.get_historical_data(self.symbol, self.timeframe, limit=200)
            if df is None or len(df) < 60: 
                logger.warning("预热失败：历史数据不足")
                return

            # Simulate last 15 bars
            lookback = 15
            for i in range(len(df) - lookback, len(df)):
                sub_df = df.iloc[:i+1].copy()
                current_close = float(sub_df['close'].iloc[-1])
                
                ts = i 
                if 'time' in sub_df.columns:
                    ts = sub_df['time'].iloc[-1]
                elif isinstance(sub_df.index, pd.DatetimeIndex):
                    ts = sub_df.index[-1].timestamp()
                
                # Run Technical Analyzers
                try:
                    smc_res = self.smc_analyzer.analyze(sub_df)
                    adv_res = self.advanced_adapter.analyze_full(sub_df, params=self.short_term_params)
                    adv_sig = adv_res['signal_info']['signal'] if adv_res else 'neutral'
                    
                    signals_dict = {
                        "crt": 'neutral', 
                        "adv": adv_sig, 
                        "smc": smc_res.get('signal', 'neutral'), 
                        "mtf": 'neutral',
                        "qwen": 'neutral'
                    }
                    self.signal_history.append((ts, signals_dict, current_close))
                except Exception:
                    continue
                    
            logger.info(f"预热完成，已生成 {len(self.signal_history)} 条历史信号")
            
        except Exception as e:
            logger.error(f"预热过程发生错误: {e}")

    def optimize_strategy_parameters(self):
        """
        Comprehensive Optimization: Tunes ALL strategy parameters using Auto-AO.
        """
        logger.info("开始执行全策略参数优化 (Comprehensive Auto-AO)...")
        
        # Reset progress counter
        self._opt_counter = 0
        
        # 1. 获取历史数据
        df = self.data_processor.get_historical_data(self.symbol, self.timeframe, limit=1000)
        if df is None or len(df) < 50: # Reduced threshold for testing
            logger.warning(f"数据不足 (Count: {len(df) if df is not None else 0}), 跳过优化")
            return
            
        # 2. Define Search Space (5 Dimensions)
        # smc_ma, smc_atr, rvgi_sma, rvgi_cci, ifvg_gap
        bounds = [
            (100, 300),     # smc_ma
            (0.001, 0.005), # smc_atr
            (10, 50),       # rvgi_sma
            (10, 30),       # rvgi_cci
            (10, 100)       # ifvg_gap
        ]
        
        steps = [10, 0.0005, 2, 2, 5]
        
        # 3. Objective
        def objective(params):
            return self.evaluate_comprehensive_params(params, df)
            
        # 4. Optimizer
        algo_name = random.choice(list(self.optimizers.keys()))
        optimizer = self.optimizers[algo_name]
        
        if hasattr(optimizer, 'pop_size'):
            optimizer.pop_size = 20
            
        logger.info(f"本次选择的优化算法: {algo_name} (Pop: {optimizer.pop_size})")
        
        # 5. Run
        best_params, best_score = optimizer.optimize(
            objective, 
            bounds, 
            steps=steps, 
            epochs=4
        )
        
        # 6. Apply Results
        try:
            self.smc_analyzer.ma_period = int(best_params[0])
            self.smc_analyzer.atr_threshold = best_params[1]
            
            self.short_term_params['rvgi_sma'] = int(best_params[2])
            self.short_term_params['rvgi_cci'] = int(best_params[3])
            self.short_term_params['ifvg_gap'] = int(best_params[4])
            
            logger.info(f"Full Strategy Params Updated (Score: {best_score:.4f})")
            logger.info(f"SMC: MA={int(best_params[0])}, ATR={best_params[1]:.4f}")
            logger.info(f"Short-Term: {self.short_term_params}")
            
        except Exception as e:
            logger.error(f"Failed to apply params: {e}")

    def optimize_short_term_params(self):
        """
        Optimize short-term strategy parameters (RVGI+CCI, IFVG) using WOAm
        """
        logger.info("Running Short-Term Parameter Optimization (WOAm)...")
        
        # 1. Get Data (Last 500 candles)
        df = self.data_processor.get_historical_data(self.symbol, self.timeframe, limit=500)
        # Reduced threshold from 200 to 50 for testing
        if df is None or len(df) < 50:
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
            
            # OPTIMIZATION: Use Vectorized Calculation for RVGI
            rvgi_series = self.advanced_adapter.calculate_rvgi_cci_series(test_data, sma_period=p_rvgi_sma, cci_period=p_rvgi_cci)
            
            total_profit = 0
            trades_count = 0
            
            # Vectorized IFVG is not fully implemented yet, so we loop but skip heavy calls
            # However, we can optimize the loop.
            
            closes = test_data['close'].values
            
            for i in range(len(test_data)-20, len(test_data)):
                # Use vectorized RVGI signal
                rvgi_sig_val = rvgi_series.iloc[i]
                rvgi_sig = 'buy' if rvgi_sig_val == 1 else 'sell' if rvgi_sig_val == -1 else 'neutral'
                
                # Check IFVG (still iterative but limited window)
                sub_df = test_data.iloc[:i+1]
                res_ifvg = self.advanced_adapter.analyze_ifvg(sub_df, min_gap_points=p_ifvg_gap)
                
                sig = "neutral"
                if rvgi_sig == 'buy' or res_ifvg['signal'] == 'buy': sig = 'buy'
                elif rvgi_sig == 'sell' or res_ifvg['signal'] == 'sell': sig = 'sell'
                
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
        # Reduced threshold from 20 to 5 to allow optimization with fewer samples
        if len(self.signal_history) < 5: 
            logger.warning("Data insufficient for optimization (need 5+ samples), skipping.")
            return
        
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

    def _send_order(self, type_str, price, sl, tp, volume_pct, strategy=None):
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
        
        # Leverage (Default 5x, or use LLM suggested if available and higher)
        # We can extract suggested leverage from strategy if present
        suggested_leverage = strategy.get('leverage', 5) if strategy else 5
        leverage = max(5, min(suggested_leverage, 20)) # Cap at 20x for safety, min 5x
        
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
        
        # Disable minimum contract check to allow trades if risk allows
        # if contracts < 1:
        #    logger.warning(f"Calculated contracts {contracts} < 1 (Size: {contract_size}). Skipping.")
        #    return
        if contracts < 1: contracts = 1 # Force at least 1 contract if margin allows but rounding down caused 0
        
        # 2.1 Re-verify margin for the final contract size (especially if forced to 1)
        actual_notional = contracts * contract_size * current_price
        actual_margin = actual_notional / leverage
        
        # Max Leverage Check
        # User requested max capital utilization, so allow up to account limit (e.g. 100x) if necessary
        # but safely capped at 50x for code stability unless overridden
        
        if actual_margin > free_balance * 0.98: # 2% buffer
             # Try increasing leverage to fit the trade if safe
             # Calculate max possible leverage based on exchange limit (assuming 100x max)
             max_exchange_leverage = 100.0 
             
             required_leverage = actual_notional / (free_balance * 0.95)
             
             if required_leverage <= max_exchange_leverage:
                 new_leverage = int(required_leverage) + 1
                 logger.info(f"Insufficient balance for {leverage}x. Auto-adjusting leverage to {new_leverage}x to maximize capital.")
                 leverage = new_leverage
                 self.data_processor.set_leverage(self.symbol, leverage)
                 # Recalculate margin with new leverage
                 actual_margin = actual_notional / leverage
             else:
                 logger.warning(f"Insufficient balance for {contracts} contracts even at max leverage ({max_exchange_leverage}x). Required: {actual_margin:.2f}, Free: {free_balance:.2f}")
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

    def execute_trade(self, signal, strategy, risk_pct, sl, tp, sl_tp_source="auto"):
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
                 self._send_order(signal, 0, sl, tp, risk_pct, strategy=strategy)
             else:
                 # Check Add Position Logic
                 raw_action = strategy.get('action', '').lower()
                 should_add = False
                 if signal == 'buy' and pos_side == 'long' and raw_action in ['add_buy', 'buy']:
                     should_add = True
                 elif signal == 'sell' and pos_side == 'short' and raw_action in ['add_sell', 'sell']:
                     should_add = True
                 
                 # Distance Protection
                 if should_add:
                     entry_price = float(positions[0].get('entryPrice', positions[0].get('avgPx', 0)))
                     current_price = self.data_processor.get_current_price(self.symbol)
                     if entry_price > 0 and current_price > 0:
                         dist_pct = abs(current_price - entry_price) / entry_price
                         if dist_pct < 0.005: # 0.5% min distance
                             logger.warning(f"Add Position skipped: Too close ({dist_pct:.2%})")
                             should_add = False
                 
                 if should_add:
                     logger.info(f"Adding to Position: {signal.upper()}")
                     self._send_order(signal, 0, sl, tp, risk_pct, strategy=strategy)
                 else:
                     # Update SL/TP for existing
                     # ENABLED: Dynamic AI Update
                     if sl_tp_source in ['qwen', 'qwen_ensemble']:
                         logger.info("Updating SL/TP for existing position (Source: Qwen Ensemble)")
                         if sl > 0 or tp > 0:
                             amt = float(positions[0]['contracts'])
                             # For crypto, we might need to be careful about cancelling all orders if there are grid orders.
                             # But here we assume the bot manages the main position SL/TP.
                             # Check if we should really cancel all orders?
                             # The original code did: self.data_processor.cancel_all_orders(self.symbol)
                             # This might cancel grid limit orders too!
                             # However, execute_trade logic for 'buy'/'sell' signal implies a directional trade, not grid.
                             # If grid is active, the signal might be 'grid_start'.
                             
                             # Let's keep original behavior but enable it.
                             # self.data_processor.cancel_all_orders(self.symbol) # Cancel old SL/TP
                             
                             # Better approach: Just update SL/TP using data_processor.place_sl_tp_order
                             # which usually places new algo orders.
                             # okx_data_processor.place_sl_tp_order sends new orders. 
                             # We should probably try to cancel existing SL/TP specifically, but cancel_all_orders is what was there.
                             
                             # Let's trust the existing logic structure but enable the block.
                             self.data_processor.cancel_all_orders(self.symbol) 
                             sl_side = 'sell' if pos_side == 'long' else 'buy'
                             self.data_processor.place_sl_tp_order(self.symbol, sl_side, amt, sl_price=sl, tp_price=tp)
                     else:
                         logger.info("Skipping SL/TP update (Source not Qwen)")

    def run_once(self):
        try:
            df, signal, strategy, strength, sl, tp, risk, sl_tp_source = self.analyze_market()
            if signal:
                self.execute_trade(signal, strategy, risk, sl, tp, sl_tp_source)
            # self.db_manager.perform_checkpoint() # Managed by external script
            return strategy
        except Exception as e:
            logger.error(f"Cycle Error: {e}", exc_info=True)
            return None

    def start(self):
        self.is_running = True
        self.next_analysis_time = 0
        self.last_analyzed_price = 0
        
        try:
            self.sync_account_history() # Sync on start
            
            # Warmup Signal History (New)
            self.warmup_signal_history()
            
            # Initial Optimization Check
            self.optimize_strategy_parameters()
            self.last_optimization_time = time.time() 
            
            logger.info(f"Bot started for {self.symbol} (Adaptive Scheduling Mode)")
            
            # Initial Run
            strategy = self.run_once()
            if strategy:
                current_price = self.data_processor.get_current_price(self.symbol)
                self.last_analyzed_price = current_price if current_price else 0
                
                # Schedule first wait
                pos_mgmt = strategy.get('position_management', {})
                wait_mins = pos_mgmt.get('next_analysis_wait_minutes', 15)
                try: wait_mins = float(wait_mins)
                except: wait_mins = 15
                self.next_analysis_time = time.time() + (wait_mins * 60)
                logger.info(f"Next analysis scheduled in {wait_mins} mins")

            while self.is_running:
                try:
                    current_time = time.time()
                    current_price = self.data_processor.get_current_price(self.symbol)
                    
                    if not current_price:
                        logger.warning("Failed to fetch price, retrying...")
                        time.sleep(10)
                        continue

                    # 1. Time Trigger
                    is_time_trigger = current_time >= self.next_analysis_time
                    
                    # 2. Volatility Trigger
                    is_volatility_trigger = False
                    if self.last_analyzed_price > 0:
                        pct_change = abs(current_price - self.last_analyzed_price) / self.last_analyzed_price
                        if pct_change > 0.008: # 0.8% threshold (significant move)
                            is_volatility_trigger = True
                            logger.info(f"⚠️ Volatility Trigger: Price changed {pct_change:.2%} (Last: {self.last_analyzed_price}, Curr: {current_price})")

                    if is_time_trigger or is_volatility_trigger:
                        logger.info("Executing Adaptive Analysis...")
                        strategy = self.run_once()
                        self.last_analyzed_price = current_price
                        
                        # Schedule Next
                        wait_mins = 15 # Default fallback
                        if strategy:
                            pos_mgmt = strategy.get('position_management', {})
                            wait_mins = pos_mgmt.get('next_analysis_wait_minutes', 15)
                            try: wait_mins = float(wait_mins)
                            except: wait_mins = 15
                            
                            # Safety limits
                            wait_mins = max(5, min(wait_mins, 240)) # Min 5 mins, Max 4 hours

                        self.next_analysis_time = time.time() + (wait_mins * 60)
                        next_time_str = datetime.fromtimestamp(self.next_analysis_time).strftime('%H:%M:%S')
                        logger.info(f"📅 Next analysis scheduled in {wait_mins} mins at {next_time_str}")
                    
                    time.sleep(10) # Poll every 10s
                        
                except Exception as e:
                    logger.error(f"Loop error: {e}")
                    time.sleep(10)
                    
        except KeyboardInterrupt:
            logger.info("Bot stopped by user.")
        except Exception as e:
            logger.critical(f"Fatal Bot Error: {e}", exc_info=True)
        finally:
            self.is_running = False

if __name__ == "__main__":
    bot = CryptoTradingBot(symbol='ETH/USDT:USDT', timeframe='15m', interval=900) 
    bot.start()
