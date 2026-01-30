import time
import sys
import os
import logging
import threading
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Try importing MetaTrader5
try:
    import MetaTrader5 as mt5
except ImportError:
    print("Error: MetaTrader5 module not found.")
    sys.exit(1)

# Configure Logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'windows_bot.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("WindowsBot")

# Load Environment Variables
load_dotenv()

# Add project root to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import Local Modules
try:
    from src.trading_bot.ai.ai_client_factory import AIClientFactory
    from src.trading_bot.data.mt5_data_processor import MT5DataProcessor
    from src.trading_bot.data.database_manager import DatabaseManager
    from src.trading_bot.analysis.optimization import WOAm, TETA
    from src.trading_bot.analysis.advanced_analysis import (
        AdvancedMarketAnalysis, AdvancedMarketAnalysisAdapter, SMCAnalyzer, 
        CRTAnalyzer, MTFAnalyzer
    )
    from src.trading_bot.strategies.grid_strategy import KalmanGridStrategy
    from src.trading_bot.utils.file_watcher import FileWatcher
except ImportError as e:
    logger.error(f"Failed to import modules: {e}")
    sys.exit(1)

class HybridOptimizer:
    def __init__(self):
        self.weights = {
            "qwen": 1.5, 
            "crt": 0.8,
            "smc": 1.1,
            "rvgi_cci": 0.6,
            "ema_ha": 0.9
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
        if final_score > 0.15: final_signal = "buy" # 降低阈值，更灵敏
        elif final_score < -0.15: final_signal = "sell"
        
        return final_signal, final_score, self.weights

class SymbolTrader:
    def __init__(self, symbol="GOLD", timeframe=mt5.TIMEFRAME_M6): # Changed Default to M6
        self.symbol = symbol
        self.timeframe = timeframe
        self.tf_name = "M15"
        if timeframe == mt5.TIMEFRAME_M5: self.tf_name = "M5"
        elif timeframe == mt5.TIMEFRAME_M10: self.tf_name = "M10" # Added M10 Name
        elif timeframe == mt5.TIMEFRAME_M15: self.tf_name = "M15"
        elif timeframe == mt5.TIMEFRAME_H1: self.tf_name = "H1"
        elif timeframe == mt5.TIMEFRAME_H4: self.tf_name = "H4"
        elif timeframe == mt5.TIMEFRAME_M6: self.tf_name = "M6"
        
        self.magic_number = 123456
        self.lot_size = 0.01 
        self.max_drawdown_pct = 0.05
        
        # 使用特定品种的独立数据库文件，确保数据完全隔离
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_filename = f"trading_data_{symbol}.db"
        db_path = os.path.join(current_dir, db_filename)
        
        self.db_manager = DatabaseManager(db_path=db_path)
        
        # [NEW] 初始化主数据库 (Master DB) 用于数据汇总和集体学习
        self.master_db_path = os.path.join(current_dir, "trading_data.db")
        self.master_db_manager = DatabaseManager(db_path=self.master_db_path)
        
        # [Optimization] Flag to skip heavy analysis after first run
        self.first_analysis_done = False
        self.cached_analysis = {}
        
        self.ai_factory = AIClientFactory()
        
        # Only Qwen as Sole Decision Maker
        self.qwen_client = self.ai_factory.create_client("qwen")
        
        # Advanced Models: SMC, CRT, CCI (via Adapter)
        # MTF kept for context structure
        self.crt_analyzer = CRTAnalyzer(timeframe_htf=mt5.TIMEFRAME_H1)
        self.mtf_analyzer = MTFAnalyzer(htf1=mt5.TIMEFRAME_M15, htf2=mt5.TIMEFRAME_H1) 
        self.advanced_adapter = AdvancedMarketAnalysisAdapter()
        self.smc_analyzer = SMCAnalyzer()
        
        # Grid Strategy Integration
        self.grid_strategy = KalmanGridStrategy(self.symbol, self.magic_number)
        
        self.optimizer = HybridOptimizer()
        
        self.last_bar_time = 0
        self.last_analysis_time = 0
        self.last_llm_time = 0 
        self.signal_history = []
        self.last_optimization_time = 0
        self.last_realtime_save = 0
        self.last_checkpoint_time = 0
        
        self.latest_strategy = None
        self.latest_signal = "neutral"
        
        # Optimizers: WOAm and TETA only
        self.optimizers = {
            "WOAm": WOAm(),
            "TETA": TETA()
        }
        self.active_optimizer_name = "WOAm"

    def check_account_safety(self, close_if_critical=True):
        """
        全面账户安全检查 (Margin, Drawdown, Equity Protection)
        返回: (is_safe: bool, reason: str)
        """
        try:
            account_info = mt5.account_info()
            if not account_info:
                return False, "Failed to get account info"

            # 1. 保证金水平检查 (Margin Level)
            # User Requirement: Function removed as requested
            # if margin_level < 120 and close_if_critical: ...


            # 2. 净值回撤检查 (Equity Drawdown)
            # User Requirement: Remove fixed drawdown check, rely on AI trend analysis.
            # Only check for critical Margin Level (< 50%) to prevent broker stopout.
            
            if account_info.margin_level > 0 and account_info.margin_level < 50.0:
                 msg = f"CRITICAL: Margin Level Critical! {account_info.margin_level:.2f}% < 50.0%"
                 logger.critical(msg)
                 if close_if_critical:
                     logger.critical("⚠️ 触发保证金紧急风控，正在强制平仓所有头寸！")
                     positions = mt5.positions_get(symbol=self.symbol)
                     if positions:
                         for pos in positions:
                             if pos.magic == self.magic_number:
                                 self.close_position(pos, comment="Margin Call Protection")
                 return False, msg

            return True, "Safe"
            
        except Exception as e:
            logger.error(f"Risk Check Error: {e}")
            return False, f"Error: {e}"

    def initialize(self):
        """
        初始化交易员实例
        - 检查 MT5 连接
        - 预热数据
        - 检查数据库
        """
        logger.info(f"[{self.symbol}] 初始化交易员...")
        
        # 1. 检查 MT5 连接
        if not self.check_mt5_connection():
            logger.error(f"[{self.symbol}] MT5 连接检查失败")
            # 这里不返回 False，因为可能只是暂时的，让主循环重试
            
        # 2. 预热数据 (可选)
        # self.get_market_data(limit=100)
        
        logger.info(f"[{self.symbol}] 交易员初始化完成")
        return True

    def check_mt5_connection(self):
        """检查 MT5 连接状态"""
        # 检查终端状态
        term_info = mt5.terminal_info()
        if term_info is None:
            logger.error("无法获取终端信息")
            return False
            
        if not term_info.trade_allowed:
            logger.warning(f"[{self.symbol}] ⚠️ 警告: 终端 '自动交易' (Algo Trading) 未开启！")
            
        if not term_info.connected:
            logger.warning(f"[{self.symbol}] ⚠️ 警告: 终端未连接到交易服务器")
            return False
        
        # 确认交易品种存在
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            logger.error(f"[{self.symbol}] 找不到交易品种")
            return False
            
        if not symbol_info.visible:
            logger.info(f"[{self.symbol}] 交易品种不可见，尝试选中")
            if not mt5.symbol_select(self.symbol, True):
                logger.error(f"[{self.symbol}] 无法选中交易品种")
                return False
        
        return True

    def get_market_data(self, num_candles=100):
        """直接从 MT5 获取历史数据"""
        # Ensure symbol is selected and available
        s_info = mt5.symbol_info(self.symbol)
        if s_info and not s_info.visible:
             if not mt5.symbol_select(self.symbol, True):
                err = mt5.last_error()
                logger.error(f"Failed to select symbol {self.symbol} in get_market_data (Error={err})")
                return None
        
        rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, num_candles)
        
        if rates is None:
            # Try to get last error
            err = mt5.last_error()
            logger.error(f"无法获取 K 线数据 ({self.symbol}): Error={err}")
            return None
            
        if len(rates) == 0:
             logger.error(f"无法获取 K 线数据 ({self.symbol}): Empty result")
             return None
            
        # 转换为 DataFrame
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        
        # 将 tick_volume 重命名为 volume 以保持一致性
        if 'tick_volume' in df.columns:
            df.rename(columns={'tick_volume': 'volume'}, inplace=True)
        
        return df

    def get_position_stats(self, pos):
        """
        计算持仓的 MFE (最大潜在收益) 和 MAE (最大潜在亏损)
        """
        try:
            # 获取持仓期间的 M1 数据
            now = datetime.now()
            # pos.time 是时间戳，转换为 datetime
            open_time = datetime.fromtimestamp(pos.time)
            
            # 获取数据
            rates = mt5.copy_rates_range(self.symbol, mt5.TIMEFRAME_M1, open_time, now)
            
            if rates is None or len(rates) == 0:
                # 如果获取不到数据，尝试只用当前价格估算
                # 这种情况可能发生在刚刚开仓的一瞬间
                current_price = pos.price_current
                if pos.type == mt5.POSITION_TYPE_BUY:
                    mfe_price = max(0, current_price - pos.price_open)
                    mae_price = max(0, pos.price_open - current_price)
                else:
                    mfe_price = max(0, pos.price_open - current_price)
                    mae_price = max(0, current_price - pos.price_open)
                
                if pos.price_open > 0:
                    return (mfe_price / pos.price_open) * 100, (mae_price / pos.price_open) * 100
                return 0.0, 0.0
                
            df = pd.DataFrame(rates)
            
            # 计算期间最高价和最低价
            # 注意: 还需要考虑当前价格，因为 M1 数据可能还没包含当前的 tick
            period_high = max(df['high'].max(), pos.price_current)
            period_low = min(df['low'].min(), pos.price_current)
            
            mfe = 0.0
            mae = 0.0
            
            if pos.type == mt5.POSITION_TYPE_BUY:
                # 买入: MFE = High - Open, MAE = Open - Low
                mfe_price = max(0, period_high - pos.price_open)
                mae_price = max(0, pos.price_open - period_low)
            else:
                # 卖出: MFE = Open - Low, MAE = High - Open
                mfe_price = max(0, pos.price_open - period_low)
                mae_price = max(0, period_high - pos.price_open)
                
            # 转换为百分比
            if pos.price_open > 0:
                mfe = (mfe_price / pos.price_open) * 100
                mae = (mae_price / pos.price_open) * 100
                
            return mfe, mae
            
        except Exception as e:
            logger.error(f"计算持仓统计时出错: {e}")
            return 0.0, 0.0





    def close_position(self, position, comment="AI-Bot Close"):
        """辅助函数: 平仓"""
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": mt5.ORDER_TYPE_SELL if position.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
            "position": position.ticket,
            "price": mt5.symbol_info_tick(self.symbol).bid if position.type == mt5.POSITION_TYPE_BUY else mt5.symbol_info_tick(self.symbol).ask,
            "deviation": 20,
            "magic": self.magic_number,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        
        result = mt5.order_send(request)
        
        if result is None:
            logger.error(f"平仓请求失败 (MT5 Returned None) #{position.ticket}. Check connection.")
            return False
            
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"平仓失败 #{position.ticket}: {result.comment} (Retcode: {result.retcode})")
            return False
        else:
            logger.info(f"平仓成功 #{position.ticket}")
            profit = getattr(result, 'profit', 0.0)
            self.send_telegram_message(f"🔄 *Position Closed*\nTicket: `{position.ticket}`\nReason: {comment}\nProfit: {profit}")
            return True

    def close_all_positions(self, positions, reason="Close All"):
        """Close all given positions"""
        if not positions:
            return
        
        logger.info(f"Closing all positions. Reason: {reason}")
        for pos in positions:
            if pos.magic == self.magic_number:
                self.close_position(pos, comment=reason)

    def cancel_all_pending_orders(self):
        """Cancel all pending orders for the current symbol"""
        try:
            orders = mt5.orders_get(symbol=self.symbol)
            if orders:
                # Filter for pending orders only (though orders_get returns orders, not positions)
                # Filter by magic number
                my_orders = [o for o in orders if o.magic == self.magic_number]
                
                if my_orders:
                    logger.info(f"Found {len(my_orders)} pending orders to cancel for {self.symbol} (New Grid Start)")
                    for order in my_orders:
                        request = {
                            "action": mt5.TRADE_ACTION_REMOVE,
                            "order": order.ticket,
                            "magic": self.magic_number,
                        }
                        result = mt5.order_send(request)
                        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
                            err_comment = result.comment if result else "Unknown Error"
                            logger.error(f"Failed to remove order {order.ticket}: {err_comment}")
                        else:
                            logger.info(f"Order {order.ticket} removed")
                else:
                    logger.info("No pending orders to cancel.")
            else:
                logger.info("No pending orders to cancel.")
        except Exception as e:
            logger.error(f"Error canceling orders: {e}")

    def check_risk_reward_ratio(self, entry_price, sl_price, tp_price, atr=None):
        """检查盈亏比是否达标"""
        # User Requirement: Profit must be > 1.5 * Lose Risk.
        # Since SL is removed (sl_price <= 0), we use a Structural Risk Estimate based on ATR.
        
        # Estimate Risk (Distance to Invalidation)
        risk = 0.0
        
        if sl_price > 0:
             risk = abs(entry_price - sl_price)
        else:
             # If no Hard SL, assume Structural Risk is ~1.5 ATR (Standard Swing Stop)
             if atr and atr > 0:
                 risk = 1.5 * atr
             else:
                 # Fallback if ATR is missing (should be rare)
                 # Assume 0.2% price move as risk? No, safer to default to True or calculate locally?
                 # Let's try to calculate ATR on the fly if missing? No, too complex here.
                 # Return True if we really can't estimate, but log warning.
                 return True, 999.0
        
        if tp_price <= 0 or risk <= 0:
             return False, 0.0
             
        reward = abs(entry_price - tp_price)
        ratio = reward / risk
        
        # Enforce Minimum RRR of 1.5
        if ratio < 1.5:
            logger.warning(f"Risk:Reward Check Failed. Ratio: {ratio:.2f} < 1.5 (Risk={risk:.2f}, Reward={reward:.2f})")
            return False, ratio
            
        return True, ratio

    def check_daily_loss_limit(self):
        """检查当日亏损是否超限"""
        try:
            # 获取当日历史交易
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            deals = mt5.history_deals_get(today, datetime.now() + timedelta(days=1))
            
            if deals is None:
                return True
                
            daily_profit = sum([d.profit + d.swap + d.commission for d in deals])
            account_info = mt5.account_info()
            if not account_info:
                return True
                
            balance = account_info.balance
            # 每日最大亏损: 余额的 10%
            max_daily_loss = -1 * (balance * 0.10)
            
            if daily_profit < max_daily_loss:
                logger.error(f"今日累计亏损 {daily_profit:.2f} 已超过风控限额 {max_daily_loss:.2f} (10%). 停止今日交易.")
                return False
                
            return True
        except Exception as e:
            logger.error(f"检查日内风控失败: {e}")
            return True # 失败时不阻断，避免死循环，但需注意

    def check_consecutive_losses(self):
        """检查连续亏损冷却"""
        # 获取最近 10 笔已平仓交易 (足够覆盖5笔)
        history = self.db_manager.get_trade_performance_stats(limit=10)
        if not history:
            return True
            
        losses = 0
        for trade in history:
            # 确保 trade 是字典并且有 profit 字段
            if isinstance(trade, dict) and trade.get('profit', 0) < 0:
                losses += 1
            else:
                break # 遇到盈利就中断
        
        # 阈值修改为 5 笔
        if losses >= 5:
            # 如果连续亏损 >= 5 笔，检查最后一笔交易的时间
            # 确保 history[0] 存在且是字典
            if history and isinstance(history[0], dict):
                last_trade_time_str = history[0].get('close_time')
                try:
                    # 简单解析时间，如果 DB 格式不同需调整
                    if last_trade_time_str:
                        last_trade_time = datetime.fromisoformat(str(last_trade_time_str))
                        time_diff = datetime.now() - last_trade_time
                        
                        # 冷却期 2 小时
                        if time_diff.total_seconds() < 7200:
                            logger.warning(f"触发连续亏损冷却 ({losses} 连败). 上次平仓于 {last_trade_time}. 需等待 2 小时.")
                            return False
                except Exception:
                    pass
                
        return True

    def calculate_dynamic_lot(self, strength, market_context=None, mfe_mae_ratio=None, ai_signals=None):
        """
        智能资金管理核心:
        结合 AI 信心、市场结构、历史绩效、算法共振、账户状态进行自适应仓位计算
        """
        try:
            account_info = mt5.account_info()
            if account_info is None:
                return self.lot_size
                
            balance = account_info.balance
            equity = account_info.equity
            margin_free = account_info.margin_free
            leverage = account_info.leverage
            
            # --- High Leverage & Exness Symbol Check ---
            # User Requirement: Exness xuausdm/eurusdm/ethusdm with 1:2000 leverage -> Allow larger lots
            is_high_leverage = leverage >= 2000
            symbol_lower = self.symbol.lower()
            is_exness_special = symbol_lower.endswith('m') or \
                                symbol_lower in ['xuausdm', 'eurusdm', 'ethusdm', 'xauusdm']
            
            allow_aggressive = is_high_leverage and is_exness_special
            
            min_margin_buffer = 100
            if allow_aggressive:
                min_margin_buffer = 50 # Lower buffer for high leverage accounts
            
            # 安全检查：如果可用保证金不足，直接返回最小手数或0
            if margin_free < min_margin_buffer: 
                logger.warning(f"可用保证金不足 ({margin_free:.2f})，强制最小手数")
                return mt5.symbol_info(self.symbol).volume_min

            # --- 0. 优先使用 LLM 建议的仓位 (LLM Suggestion) ---
            # 策略要求: 不强制 0.01，优先采纳大模型基于资金分析的结果
            if self.latest_strategy and 'position_size' in self.latest_strategy:
                try:
                    llm_lot = float(self.latest_strategy['position_size'])
                    if llm_lot > 0:
                        symbol_info = mt5.symbol_info(self.symbol)
                        if symbol_info:
                            # 简单的步长修正
                            step = symbol_info.volume_step
                            llm_lot = round(llm_lot / step) * step
                            llm_lot = max(symbol_info.volume_min, min(llm_lot, symbol_info.volume_max))
                            
                            # --- 真实保证金检查 (Broker Specific Margin Check) ---
                            # 解决 Exness/AVA 等平台合约大小不同导致的 "No money" 错误
                            try:
                                tick = mt5.symbol_info_tick(self.symbol)
                                if tick:
                                    # 推断方向 (默认为 Buy，如果是 Sell 则调整)
                                    action_str = str(self.latest_strategy.get('action', '')).lower()
                                    is_sell = 'sell' in action_str
                                    
                                    calc_type = mt5.ORDER_TYPE_SELL if is_sell else mt5.ORDER_TYPE_BUY
                                    calc_price = tick.bid if is_sell else tick.ask
                                    
                                    margin_required = mt5.order_calc_margin(calc_type, self.symbol, llm_lot, calc_price)
                                    
                                    if margin_required is not None:
                                        # 检查资金是否足够 (保留 5% 缓冲)
                                        if margin_required > (margin_free * 0.95):
                                            logger.warning(f"⚠️ 资金不足 (Need ${margin_required:.2f}, Free ${margin_free:.2f}) for {llm_lot} lots. Exness/Ava info differs.")
                                            
                                            # 动态降级仓位
                                            # Margin = Volume * ContractSize * Price / Leverage (Roughly)
                                            # So Volume ~ Margin
                                            margin_per_lot = margin_required / llm_lot
                                            safe_margin = margin_free * 0.95
                                            
                                            if margin_per_lot > 0:
                                                new_lot = safe_margin / margin_per_lot
                                                # 再次修正步长
                                                new_lot = round(new_lot / step) * step
                                                new_lot = max(symbol_info.volume_min, new_lot)
                                                
                                                # 如果修正后仍然无法满足 (例如最小手数也买不起)，则只能由后续逻辑处理或保持最小
                                                # 这里我们更新 llm_lot
                                                if new_lot < llm_lot:
                                                    logger.info(f"↘️ 根据账户资金自动调整仓位: {llm_lot} -> {new_lot}")
                                                    llm_lot = new_lot
                                    else:
                                        logger.warning("无法计算保证金 (order_calc_margin returned None)")
                            except Exception as e:
                                logger.error(f"保证金检查异常: {e}")

                            # 风险验证 (Risk Guardrail) - 放宽限制以支持 AI 全权风控
                            # 估算: 1 Lot * 500 points * TickValue (压力测试)
                            tick_val = symbol_info.trade_tick_value
                            if not tick_val: tick_val = 1.0
                            
                            est_risk = llm_lot * 500.0 * tick_val
                            
                            # Risk Cap Logic
                            risk_cap_pct = 0.25
                            if allow_aggressive:
                                risk_cap_pct = 0.50 # Allow up to 50% equity risk exposure for high leverage specialized accounts
                                logger.info("High Leverage Exness Mode: Relaxing Risk Cap to 50%")
                            
                            max_risk = equity * risk_cap_pct 
                            
                            if est_risk <= max_risk:
                                logger.info(f"✅ 采用大模型全权建议仓位: {llm_lot} Lots (AI Driven Risk)")
                                return llm_lot
                            else:
                                logger.warning(f"⚠️ 大模型建议仓位 {llm_lot} 极端风险过高 (StressTest ${est_risk:.2f} > ${max_risk:.2f})，触发熔断保护。")
                except Exception as e:
                    logger.warning(f"解析 LLM 仓位失败: {e}")

            # --- 1. 自适应基础风险 (Self-Adaptive Base Risk) ---
            # 基于近期胜率和盈亏比动态调整基础风险
            # 默认 2%
            base_risk_pct = 0.02
            
            metrics = self.db_manager.get_performance_metrics(symbol=self.symbol, limit=20)
            win_rate = metrics.get('win_rate', 0.0)
            profit_factor = metrics.get('profit_factor', 0.0)
            consecutive_losses = metrics.get('consecutive_losses', 0)
            
            # 学习逻辑:
            # 如果近期表现好 (WinRate > 55% & PF > 1.5)，基础风险上调至 2.5% - 3.0%
            # 如果近期表现差 (WinRate < 40% 或 连败 > 2)，基础风险下调至 1.0%
            
            if win_rate > 0.55 and profit_factor > 1.5:
                base_risk_pct = 0.03
                logger.info(f"资金管理学习: 近期表现优异 (WR={win_rate:.2%}, PF={profit_factor:.2f}), 基础风险上调至 3%")
            elif win_rate < 0.40 or consecutive_losses >= 2:
                base_risk_pct = 0.01
                logger.info(f"资金管理学习: 近期表现不佳/连败 (WR={win_rate:.2%}, LossStreak={consecutive_losses}), 基础风险下调至 1%")
            
            # --- 2. AI 与 算法共振加成 (Consensus Multiplier) ---
            consensus_multiplier = 1.0
            
            if ai_signals:
                # A. 大模型一致性 (Only Qwen now)
                qw_sig = ai_signals.get('qwen', 'neutral')
                target_sig = self.latest_signal # 最终决策方向
                
                if qw_sig == target_sig:
                    consensus_multiplier += 0.2 
                
                # B. 高级算法共振 (Voting)
                tech_signals = [
                    ai_signals.get('crt'), 
                    ai_signals.get('smc'),
                    ai_signals.get('rvgi_cci')
                ]
                # 计算同向比例
                same_dir_count = sum(1 for s in tech_signals if s == target_sig)
                total_tech = len(tech_signals)
                
                if total_tech > 0:
                    ratio = same_dir_count / total_tech
                    if ratio >= 0.8: # 80% 以上指标同向
                        consensus_multiplier += 0.4
                    elif ratio >= 0.6:
                        consensus_multiplier += 0.2
                    elif ratio < 0.3:
                        consensus_multiplier -= 0.3 # 只有少数指标支持，减仓
            
            # --- 3. 信心分数调整 (Strength) ---
            # 这里的 strength 已经是结合了投票结果的，可能与上面的共振有部分重叠
            # 我们将其作为微调系数
            strength_multiplier = 1.0
            if strength > 70:
                strength_multiplier = 1.2
            elif strength < 50:
                strength_multiplier = 0.6
                
            # --- 4. 市场结构与盈亏比调整 ---
            structure_multiplier = 1.0
            
            # MFE/MAE
            if mfe_mae_ratio and mfe_mae_ratio > 2.0:
                structure_multiplier += 0.2
            elif mfe_mae_ratio and mfe_mae_ratio < 0.8:
                structure_multiplier -= 0.2
                
            # SMC Strong Trend
            if market_context and 'smc' in market_context:
                smc = market_context['smc']
                if smc.get('structure') in ['Strong Bullish', 'Strong Bearish']:
                    structure_multiplier += 0.2
            
            # Volatility Regime (Matrix ML / Advanced Tech)
            # 如果是极高波动率，应该减仓以防滑点和剧烈扫损
            if market_context and 'volatility_regime' in market_context:
                regime = market_context['volatility_regime']
                if regime == 'High' or regime == 'Extreme':
                    structure_multiplier *= 0.7
                    logger.info("检测到高波动率市场，自动降低仓位系数")

            # --- 5. 综合计算 ---
            final_risk_pct = base_risk_pct * consensus_multiplier * strength_multiplier * structure_multiplier
            
            # 硬性风控上限 (Max Risk Cap)
            # 无论如何优化，单笔亏损不得超过权益的 6%
            final_risk_pct = min(final_risk_pct, 0.06)
            # 下限保护
            final_risk_pct = max(final_risk_pct, 0.005) # 至少 0.5%
            
            risk_amount = equity * final_risk_pct
            
            # 资金池分配检查 (Portfolio Management)
            # 确保当前品种的占用资金不会耗尽所有自由保证金
            # 简单规则：任何单一品种的预估保证金占用不应超过剩余自由保证金的 50% (80% for Aggressive)
            alloc_pct = 0.5
            if allow_aggressive:
                alloc_pct = 0.8
                
            max_allowed_risk_amount = margin_free * alloc_pct
            if risk_amount > max_allowed_risk_amount:
                logger.warning(f"风险金额 ({risk_amount:.2f}) 超过可用保证金池限制 ({max_allowed_risk_amount:.2f}). 自动下调.")
                risk_amount = max_allowed_risk_amount
            
            # --- 6. 动态止损距离估算 ---
            # 如果有明确的 SL 价格，计算实际距离；否则用 ATR
            sl_distance_points = 500.0 # 默认
            
            # 尝试从 latest_strategy 获取建议的 SL
            if self.latest_strategy:
                sl_price = self.latest_strategy.get('exit_conditions', {}).get('sl_price')
                entry_price_ref = mt5.symbol_info_tick(self.symbol).ask # 假设当前进场
                
                if sl_price and sl_price > 0:
                    sl_distance_points = abs(entry_price_ref - sl_price) / mt5.symbol_info(self.symbol).point
            
            # 如果上面的计算异常(太小)，回退到 ATR
            if sl_distance_points < 100 and market_context and 'atr' in market_context:
                atr = market_context['atr']
                if atr > 0:
                    sl_distance_points = (atr * 1.5) / mt5.symbol_info(self.symbol).point
            
            # 再次保护，防止除以零或过小
            if sl_distance_points < 50: sl_distance_points = 500.0
            
            # 计算合约价值 (Gold: 1 lot = 100 oz, tick_value usually corresponds to volume)
            # 简单估算: Gold 1.0 lot, 1 point ($0.01 move) = $1 profit/loss?
            # 通常 XAUUSD: 1 lot, 0.01 price change = $1.  1.00 price change = $100.
            # Point = 0.01. 
            # Loss per lot = sl_distance_points * tick_value
            
            symbol_info = mt5.symbol_info(self.symbol)
            tick_value = symbol_info.trade_tick_value
            # 有些 broker 的 tick_value 可能配置不同，这里做个典型值兜底
            if tick_value is None or tick_value == 0:
                tick_value = 1.0 # 假设标准合约
                
            loss_per_lot = sl_distance_points * tick_value
            
            calculated_lot = risk_amount / loss_per_lot
            
            # 标准化
            step = symbol_info.volume_step
            min_lot = symbol_info.volume_min
            max_lot = symbol_info.volume_max
            
            calculated_lot = round(calculated_lot / step) * step
            final_lot = max(min_lot, min(calculated_lot, max_lot))
            
            logger.info(
                f"💰 智能资金管理 ({self.symbol}):\n"
                f"• Base Risk: {base_risk_pct:.1%}\n"
                f"• Multipliers: Consensus={consensus_multiplier:.2f}, Strength={strength_multiplier:.2f}, Struct={structure_multiplier:.2f}\n"
                f"• Final Risk: {final_risk_pct:.2%} (${risk_amount:.2f})\n"
                f"• Margin Free: {margin_free:.2f} (Cap: {max_allowed_risk_amount:.2f})\n"
                f"• SL Dist: {sl_distance_points:.0f} pts\n"
                f"• Lot Size: {final_lot}"
            )
            
            return final_lot
            
        except Exception as e:
            logger.error(f"动态仓位计算失败: {e}")
            return self.lot_size

    def execute_trade(self, signal, strength, sl_tp_params, entry_params=None, suggested_lot=None):
        """
        执行交易指令，完全由大模型驱动
        :param suggested_lot: 预计算的建议手数 (可选)
        """
        # 允许所有相关指令进入
        valid_actions = ['buy', 'sell', 'limit_buy', 'limit_sell', 'close', 'add_buy', 'add_sell', 'hold', 'close_buy_open_sell', 'close_sell_open_buy']
        # 注意: signal 参数这里传入的是 final_signal，已经被归一化为 buy/sell/close/hold
        # 但我们更关心 entry_params 中的具体 action
        
        # --- 1. 获取市场状态 ---
        positions = mt5.positions_get(symbol=self.symbol)
        tick = mt5.symbol_info_tick(self.symbol)
        if not tick:
            logger.error("无法获取 Tick 数据")
            return

        # 解析 LLM 指令
        # 这里的 entry_params 是从 strategy 字典中提取的 'entry_conditions'
        # 但 strategy 字典本身也有 'action'
        # 为了更准确，我们应该直接使用 self.latest_strategy (在 run 循环中更新)
        
        # 兼容性处理
        llm_action = "hold"
        if self.latest_strategy:
             llm_action = self.latest_strategy.get('action', 'hold').lower()
        elif entry_params and 'action' in entry_params:
             llm_action = entry_params.get('action', 'hold').lower()
        else:
             llm_action = signal if signal in valid_actions else 'hold'

        # Normalize Compound Actions (Reverse)
        if llm_action == 'close_buy_open_sell':
            logger.info("Action Normalized: close_buy_open_sell -> sell")
            llm_action = 'sell'
        elif llm_action == 'close_sell_open_buy':
            logger.info("Action Normalized: close_sell_open_buy -> buy")
            llm_action = 'buy'

        # Force Override: 如果 final_signal (signal) 已经被修正为 buy/sell，但 llm_action 仍为 hold，则强制同步
        if signal in ['buy', 'sell'] and llm_action in ['hold', 'neutral']:
             logger.info(f"Applying Signal Override: {llm_action} -> {signal}")
             llm_action = signal

        # 显式 MFE/MAE 止损止盈
        # LLM 应该返回具体的 sl_price 和 tp_price，或者 MFE/MAE 的百分比建议
        # 如果 LLM 提供了具体的 SL/TP 价格，优先使用
        explicit_sl = None
        explicit_tp = None
        
        if self.latest_strategy:
            explicit_sl = self.latest_strategy.get('sl')
            explicit_tp = self.latest_strategy.get('tp')
        
        # 如果没有具体价格，回退到 sl_tp_params (通常也是 LLM 生成的)
        if explicit_sl is None and sl_tp_params:
             explicit_sl = sl_tp_params.get('sl_price')
        if explicit_tp is None and sl_tp_params:
             explicit_tp = sl_tp_params.get('tp_price')

        logger.info(f"执行逻辑: Action={llm_action}, Signal={signal}, Explicit SL={explicit_sl}, TP={explicit_tp}")

        # --- 2. 持仓管理 (已开仓状态) ---
        added_this_cycle = False
        if positions and len(positions) > 0:
            for pos in positions:
                pos_type = pos.type # 0: Buy, 1: Sell
                is_buy_pos = (pos_type == mt5.POSITION_TYPE_BUY)
                
                # A. 平仓/减仓逻辑 (Close)
                should_close = False
                close_reason = ""
                
                if llm_action in ['close', 'close_buy', 'close_sell']:
                    # 检查方向匹配
                    if llm_action == 'close': should_close = True
                    elif llm_action == 'close_buy' and is_buy_pos: should_close = True
                    elif llm_action == 'close_sell' and not is_buy_pos: should_close = True
                    
                    if should_close: close_reason = "LLM Close Instruction"
                
                # 反向信号平仓 (Reversal)
                elif (llm_action in ['buy', 'add_buy'] and not is_buy_pos):
                     should_close = True
                     close_reason = "Reversal (Sell -> Buy)"
                elif (llm_action in ['sell', 'add_sell'] and is_buy_pos):
                     should_close = True
                     close_reason = "Reversal (Buy -> Sell)"

                if should_close:
                    logger.info(f"执行平仓 #{pos.ticket}: {close_reason}")
                    
                    # Close the position
                    close_result = self.close_position(pos, comment=f"AI: {close_reason}")
                    
                    # Calculate Profit if closed successfully
                    if close_result:
                        try:
                            # 尝试获取刚刚平仓的成交记录以确认盈亏
                            # 注意: close_position 返回的是 Result 对象，包含 order ticket，不直接包含 profit
                            # 我们需要查询 Deal 历史
                            
                            # 短暂等待以确保 Deal 已写入历史
                            time.sleep(0.5) 
                            
                            from_date = datetime.now() - timedelta(minutes=1)
                            to_date = datetime.now() + timedelta(minutes=1)
                            deals = mt5.history_deals_get(from_date, to_date)
                            
                            realized_profit = 0.0
                            found_deal = False
                            
                            if deals:
                                for d in deals:
                                    if d.position_id == pos.ticket and d.entry in [mt5.DEAL_ENTRY_OUT, mt5.DEAL_ENTRY_INOUT]:
                                        realized_profit = d.profit + d.swap + d.commission
                                        found_deal = True
                                        break
                            
                            if found_deal:
                                profit_msg = f"💰 *Position Closed* (#{pos.ticket})\nSymbol: {self.symbol}\nProfit: `{realized_profit:.2f}` USD\nReason: _{close_reason}_"
                                self.send_telegram_message(profit_msg)
                                logger.info(f"Position Closed Profit: {realized_profit}")
                            else:
                                # Fallback if deal not found immediately (unlikely but possible)
                                self.send_telegram_message(f"🔒 *Position Closed* (#{pos.ticket})\nChecking profit details...")
                                
                        except Exception as e:
                            logger.error(f"Error reporting close profit: {e}")
                    
                    continue 

                # B. 加仓逻辑 (Add Position)
                should_add = False
                # 用户需求: 如果大模型综合分析结果为同方向，则视为加仓指令
                # 限制: 每个周期只加仓一次，避免重复加仓
                if not added_this_cycle:
                    if is_buy_pos and llm_action in ['add_buy', 'buy']: 
                        should_add = True
                    elif not is_buy_pos and llm_action in ['add_sell', 'sell']: 
                        should_add = True
                
                if should_add:
                    # [NEW] Safety Check for Adding Position
                    is_safe, reason = self.check_account_safety(close_if_critical=False)
                    if not is_safe:
                        logger.warning(f"🚫 拒绝加仓: 账户风险检查未通过 ({reason})")
                        continue

                    # --- 加仓距离保护 ---
                    can_add = True
                    min_dist_points = 200 # 20 pips
                    symbol_info = mt5.symbol_info(self.symbol)
                    point = symbol_info.point if symbol_info else 0.01
                    current_check_price = tick.ask if is_buy_pos else tick.bid
                    
                    for existing in positions:
                        if existing.magic == self.magic_number and existing.type == pos.type:
                            dist = abs(existing.price_open - current_check_price) / point
                            if dist < min_dist_points:
                                logger.warning(f"加仓保护: 距离现有持仓太近 ({dist:.0f} < {min_dist_points}), 跳过.")
                                can_add = False
                                break
                    
                    if not can_add:
                        continue
                    # -------------------

                    logger.info(f"执行加仓 #{pos.ticket} 方向 (Action: {llm_action})")
                    # 加仓逻辑复用开仓逻辑，但可能调整手数
                    self._send_order(
                        "buy" if is_buy_pos else "sell", 
                        tick.ask if is_buy_pos else tick.bid,
                        explicit_sl,
                        explicit_tp,
                        comment="AI: Add Position"
                    )
                    added_this_cycle = True # 标记本轮已加仓
                    pass
                    
                # C. 持仓 (Hold) - 默认行为
                # 更新 SL/TP (如果 LLM 给出了新的优化值)
                # 只有当新给出的 SL/TP 与当前差别较大时才修改
                if explicit_sl is not None and explicit_tp is not None:
                    # 简单的阈值检查，避免频繁修改
                    point = mt5.symbol_info(self.symbol).point
                    if abs(pos.sl - explicit_sl) > 10 * point or abs(pos.tp - explicit_tp) > 10 * point:
                        logger.info(f"更新持仓 SL/TP #{pos.ticket}: SL {pos.sl}->{explicit_sl}, TP {pos.tp}->{explicit_tp}")
                        request = {
                            "action": mt5.TRADE_ACTION_SLTP,
                            "position": pos.ticket,
                            "sl": explicit_sl,
                            "tp": explicit_tp
                        }
                        mt5.order_send(request)

        # --- 3. 开仓/挂单逻辑 (未开仓 或 加仓) ---
        # 注意: 上面的循环处理了已有仓位的 Close 和 Add。
        
        # [NEW] Pre-Trade Safety Check (Risk Management)
        # Check before opening any NEW position (Market, Limit, Grid)
        is_opening_action = llm_action in ['buy', 'sell', 'add_buy', 'add_sell', 'limit_buy', 'limit_sell', 'buy_limit', 'sell_limit', 'grid_start', 'close_buy_open_sell', 'close_sell_open_buy']
        
        if is_opening_action:
             is_safe, reason = self.check_account_safety(close_if_critical=False)
             if not is_safe:
                 logger.warning(f"🚫 拒绝开仓/网格指令 ({llm_action}): 账户风险检查未通过 ({reason})")
                 return
             
             # [NEW] Price Position Check (Callback/Pullback Logic)
             # User Requirement: 如果当前位置不适合开仓，则等待回调
             # 简单的逻辑：如果做多 (Buy)，当前价格不应在近期最高点附近；如果做空 (Sell)，不应在最低点附近。
             # 或者使用 entry_params 中的价格作为必须条件。
             
             # 1. Check if specific entry price is required by LLM
             required_entry = 0.0
             if entry_params and 'price' in entry_params:
                 try: required_entry = float(entry_params['price'])
                 except: pass
             
             current_ask = tick.ask
             current_bid = tick.bid
             
             if required_entry > 0:
                 # Check deviation
                 threshold_pips = 10 * mt5.symbol_info(self.symbol).point * 10 # 10 pips tolerance? or strict?
                 # Let's use points directly. 100 points = 10 pips (usually)
                 threshold_points = 50 * mt5.symbol_info(self.symbol).point 
                 
                 if "buy" in llm_action or "long" in llm_action:
                     # For Buy, we want price <= required_entry (better or equal)
                     # But if price is slightly above, maybe wait?
                     if current_ask > (required_entry + threshold_points):
                         logger.info(f"⏳ 价格过高，等待回调 (Current: {current_ask:.2f} > Target: {required_entry:.2f}). 跳过本次开仓。")
                         return
                 elif "sell" in llm_action or "short" in llm_action:
                     # For Sell, we want price >= required_entry
                     if current_bid < (required_entry - threshold_points):
                         logger.info(f"⏳ 价格过低，等待反弹 (Current: {current_bid:.2f} < Target: {required_entry:.2f}). 跳过本次开仓。")
                         return
             
             # 2. General Pullback Logic (if no specific price)
             # If Strength is not super high, avoid buying at local top / selling at local bottom
             # Use simple 20-bar Donchian Channel logic
             else:
                 if strength < 0.9: # Only check if not super confident
                     rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, 20)
                     if rates is not None and len(rates) > 0:
                         highs = [x['high'] for x in rates]
                         lows = [x['low'] for x in rates]
                         recent_high = max(highs)
                         recent_low = min(lows)
                         
                         # Check Buy at Top
                         if "buy" in llm_action or "long" in llm_action:
                             # If current price is very close to recent high (e.g. within top 10% of range)
                             rng = recent_high - recent_low
                             if rng > 0 and (current_ask - recent_low) / rng > 0.9:
                                  logger.info(f"⏳ 价格处于近期高位 ({current_ask:.2f} near High {recent_high:.2f})，等待回调。")
                                  return
                         
                         # Check Sell at Bottom
                         elif "sell" in llm_action or "short" in llm_action:
                             # If current price is very close to recent low (e.g. within bottom 10% of range)
                             rng = recent_high - recent_low
                             if rng > 0 and (current_bid - recent_low) / rng < 0.1:
                                  logger.info(f"⏳ 价格处于近期低位 ({current_bid:.2f} near Low {recent_low:.2f})，等待反弹。")
                                  return

              # 3. SMC / Supply & Demand / BOS / CHoCH Validation (Enhanced)
              # 如果 LLM 分析中包含这些关键词，尝试进一步校验
              # (注：SMC 分析结果已包含在 self.latest_strategy['details'] 中，如果存在)
              if self.latest_strategy and 'details' in self.latest_strategy:
                  smc_details = self.latest_strategy['details'].get('smc_structure', {})
                  
                  # 获取关键区域
                  # 这里假设 smc_structure 包含 'poi' (Points of Interest) 或 'liquidity' 等
                  # 由于具体结构未完全标准化，我们进行关键词匹配
                  
                  # A. BOS (Break of Structure) Check
                  # 如果是 Buy，我们希望看到 bullish BOS 已经发生，或者正在回踩 OB (Order Block)
                  # 如果是 Sell，我们希望看到 bearish BOS
                  
                  # B. Premium/Discount Zone
                  # Buy should be in Discount zone (< 0.5 of range)
                  # Sell should be in Premium zone (> 0.5 of range)
                  
                  pass # (此逻辑目前作为占位符，因为需要更复杂的 SMC 计算模块支持。当前通过 K 线高低点已实现基础的 Discount/Premium 检查)

        # 如果当前没有仓位，或者上面的逻辑没有触发 Close (即是 Hold)，
        # 或者是 Reversal (Close 之后)，我们需要看是否需要开新仓。
        
        # 重新检查持仓数 (因为刚才可能平仓了)
        # 仅检查由本机器人 (Magic Number) 管理的持仓
        all_positions = mt5.positions_get(symbol=self.symbol)
        bot_positions = [p for p in all_positions if p.magic == self.magic_number] if all_positions else []
        has_position = len(bot_positions) > 0
        
        # 如果有持仓且不是加仓指令，则不再开新仓
        if has_position:
            if added_this_cycle:
                logger.info(f"本轮已执行加仓，跳过额外开仓")
                return
            
            # [User Requirement] 取消对 "非加仓指令就跳过" 的限制。
            # 允许在已有持仓的情况下，如果 AI 发出了新的网格启动指令 (grid_start_long/short)，
            # 且方向与现有持仓一致（或者 AI 认为需要重新部署网格），则允许执行。
            # 实际上，grid_start_long/short 会在下方逻辑中被处理，会先 cancel pending orders，然后根据 grid_strategy 生成新挂单。
            # 如果是同向，这相当于"网格重置/增强"。如果是反向，通常应该先平仓（由上方 Close 逻辑处理），如果没平仓直接反向开网格，就是对冲。
            
            # 过滤掉单纯的 'buy'/'sell' 指令（因为我们已经是 Grid-Only 模式），只放行 grid_start 系列
            # 且如果是 grid_start，我们需要确保不会无限叠加首单。
            
            if 'grid_start' in llm_action:
                logger.info(f"已有持仓 ({len(bot_positions)})，但收到新的网格指令 ({llm_action})，允许调整/重新部署网格。")
                # Pass through to grid logic below
            elif 'add' in llm_action:
                 # Explicit add command from LLM
                 pass 
            elif llm_action in ['buy', 'sell']:
                 # [User Requirement] 即使有持仓，如果 AI 明确给出 buy/sell (且 confidence 高)，也允许加仓。
                 # 但我们之前为了强制网格策略，屏蔽了单纯的 buy/sell。
                 # 这里我们需要放行，并将其转化为 grid_start 或 add 逻辑。
                 
                 # 假设 buy/sell 在有持仓时意味着 "Trend Following Add"
                 logger.info(f"已有持仓，收到 ({llm_action}) 指令。视为趋势加仓信号，放行。")
                 pass
            else:
                # 只有完全不相关的指令才拦截
                logger.info(f"已有持仓 ({len(bot_positions)}), 且非加仓/网格指令 ({llm_action}), 跳过开仓")
                return

        # 执行开仓/挂单
        trade_type = None
        price = 0.0
        
        # Mapping 'add_buy'/'add_sell' to normal buy/sell if no position exists
        # This handles cases where LLM says "add" but position was closed or didn't exist
        
        # User Requirement: 如果很确定的话 (High Strength) 可以直接开市场价
        # [DISABLED] Market Buy/Sell Logic for Single Orders
        # if strength is not None and strength >= 0.8:
        #     if llm_action in ['limit_buy', 'buy_limit']:
        #         logger.info(f"High confidence ({strength}), switching Limit Buy to Market Buy")
        #         llm_action = 'buy'
        #     elif llm_action in ['limit_sell', 'sell_limit']:
        #         logger.info(f"High confidence ({strength}), switching Limit Sell to Market Sell")
        #         llm_action = 'sell'

        # User Requirement: Disable all single 'buy'/'sell'/'add' actions.
        # Grid Strategy ONLY.
        
        # [MODIFIED] Allow 'buy'/'sell'/'add' to pass through and be converted to grid actions
        # if llm_action in ['buy', 'add_buy', 'sell', 'add_sell', 'limit_buy', 'buy_limit', 'limit_sell', 'sell_limit']:
        #     logger.info(f"Ignoring '{llm_action}' action as per Strict Grid-Only policy.")
        #     return
        
        # Determine if this is a grid deployment (explicit or converted)
        is_grid_action = False
        direction = 'bullish' # Default
        
        if llm_action in ['grid_start', 'grid_start_long', 'grid_start_short']:
            is_grid_action = True
            if llm_action == 'grid_start_long': direction = 'bullish'
            elif llm_action == 'grid_start_short': direction = 'bearish'
            else:
                # Legacy grid_start inference
                if self.latest_strategy:
                    market_state = str(self.latest_strategy.get('market_state', '')).lower()
                    pred = str(self.latest_strategy.get('short_term_prediction', '')).lower()
                    if 'down' in market_state or 'bear' in pred or 'sell' in str(self.latest_strategy.get('action', '')).lower():
                        direction = 'bearish'
                        
        elif llm_action in ['buy', 'add_buy', 'limit_buy', 'buy_limit']:
             # [NEW] Enforce Trend Mode (High/Low Swing) - No Grid
             is_grid_action = False
             
             if 'limit' in llm_action:
                 trade_type = "limit_buy"
                 # Try to extract price from entry_params
                 if entry_params and 'price' in entry_params:
                     try:
                         price = float(entry_params['price'])
                     except: pass
                 
                 # If price missing, default to Ask - 50 points (Buy Limit)
                 if price <= 0:
                     si = mt5.symbol_info(self.symbol)
                     point = si.point if si else 0.01
                     price = tick.ask - (50 * point)
             else:
                 trade_type = "buy" # Market Buy
                 price = tick.ask
             
             # If explicit_sl/tp not set by now (from strategy), try to extract from entry_params if present
             if entry_params:
                 if not explicit_sl and 'sl' in entry_params: explicit_sl = float(entry_params['sl'])
                 if not explicit_tp and 'tp' in entry_params: explicit_tp = float(entry_params['tp'])
                 
                 # Extract suggested lot from entry_params if available
                 if 'lots' in entry_params:
                     try: suggested_lot = float(entry_params['lots'])
                     except: pass
                 elif 'volume' in entry_params:
                     try: suggested_lot = float(entry_params['volume'])
                     except: pass

             # [Validation] Fix Inverted SL/TP
             if explicit_sl and explicit_sl > 0 and explicit_tp and explicit_tp > 0:
                 if "buy" in llm_action: # Buy
                     if explicit_sl > price and explicit_tp < price:
                         logger.warning(f"Swapping inverted SL/TP for BUY (SL={explicit_sl}, TP={explicit_tp})")
                         explicit_sl, explicit_tp = explicit_tp, explicit_sl
                 elif "sell" in llm_action: # Sell
                     if explicit_sl < price and explicit_tp > price:
                         logger.warning(f"Swapping inverted SL/TP for SELL (SL={explicit_sl}, TP={explicit_tp})")
                         explicit_sl, explicit_tp = explicit_tp, explicit_sl

             # [Defaults] Calculate SL/TP if missing (to ensure R:R check works)
             if (not explicit_sl or explicit_sl <= 0) or (not explicit_tp or explicit_tp <= 0):
                 # Need ATR
                 rates_atr = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, 20)
                 local_atr = 0.0
                 if rates_atr is not None and len(rates_atr) > 14:
                     df_atr = pd.DataFrame(rates_atr)
                     hl = df_atr['high'] - df_atr['low']
                     local_atr = hl.rolling(14).mean().iloc[-1]
                 
                 if local_atr > 0:
                     if "buy" in llm_action:
                         if not explicit_sl or explicit_sl <= 0: explicit_sl = price - 1.5 * local_atr
                         if not explicit_tp or explicit_tp <= 0: explicit_tp = price + 2.0 * local_atr
                     elif "sell" in llm_action:
                         if not explicit_sl or explicit_sl <= 0: explicit_sl = price + 1.5 * local_atr
                         if not explicit_tp or explicit_tp <= 0: explicit_tp = price - 2.0 * local_atr
                     logger.info(f"Generated Default SL/TP using ATR: SL={explicit_sl:.2f}, TP={explicit_tp:.2f}")

             logger.info(f"Trend Mode: Executing decisive '{llm_action}' without grid. Price={price}, SL={explicit_sl}, TP={explicit_tp}, Lot={suggested_lot}")
             
             # Fall through to common execution logic (DO NOT RETURN)
             # self.execute_trade calls _send_order at the end.
             # If we return here, we skip the rest of execute_trade logic (R:R check, dynamic lot calc, etc.)
             # Wait, the previous code had 'logger.info...' then fell through to 'if is_grid_action'.
             # It did NOT return.
             # BUT, if is_grid_action is False, it goes to... where?
             # It goes to line 1300+ where R:R check and _send_order are.
             # So we must update the local variables 'explicit_sl', 'explicit_tp', 'suggested_lot' and let it flow.
             pass
             
        elif llm_action in ['sell', 'add_sell', 'limit_sell', 'sell_limit']:
             # [NEW] Enforce Trend Mode (High/Low Swing) - No Grid
             is_grid_action = False
             
             if 'limit' in llm_action:
                 trade_type = "limit_sell"
                 # Try to extract price from entry_params
                 if entry_params and 'price' in entry_params:
                     try:
                         price = float(entry_params['price'])
                     except: pass
                 
                 # If price missing, default to Bid + 50 points (Sell Limit)
                 if price <= 0:
                     si = mt5.symbol_info(self.symbol)
                     point = si.point if si else 0.01
                     price = tick.bid + (50 * point)
             else:
                 trade_type = "sell" # Market Sell
                 price = tick.bid
                 
             # If explicit_sl/tp not set by now (from strategy), try to extract from entry_params if present
             if entry_params:
                 if not explicit_sl and 'sl' in entry_params: explicit_sl = float(entry_params['sl'])
                 if not explicit_tp and 'tp' in entry_params: explicit_tp = float(entry_params['tp'])
                 
                 # Extract suggested lot from entry_params if available
                 if 'lots' in entry_params:
                     try: suggested_lot = float(entry_params['lots'])
                     except: pass
                 elif 'volume' in entry_params:
                     try: suggested_lot = float(entry_params['volume'])
                     except: pass

             # [Validation] Fix Inverted SL/TP
             if explicit_sl and explicit_sl > 0 and explicit_tp and explicit_tp > 0:
                 if "buy" in llm_action: # Buy
                     if explicit_sl > price and explicit_tp < price:
                         logger.warning(f"Swapping inverted SL/TP for BUY (SL={explicit_sl}, TP={explicit_tp})")
                         explicit_sl, explicit_tp = explicit_tp, explicit_sl
                 elif "sell" in llm_action: # Sell
                     if explicit_sl < price and explicit_tp > price:
                         logger.warning(f"Swapping inverted SL/TP for SELL (SL={explicit_sl}, TP={explicit_tp})")
                         explicit_sl, explicit_tp = explicit_tp, explicit_sl

             # [Defaults] Calculate SL/TP if missing (to ensure R:R check works)
             if (not explicit_sl or explicit_sl <= 0) or (not explicit_tp or explicit_tp <= 0):
                 # Need ATR
                 rates_atr = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, 20)
                 local_atr = 0.0
                 if rates_atr is not None and len(rates_atr) > 14:
                     df_atr = pd.DataFrame(rates_atr)
                     hl = df_atr['high'] - df_atr['low']
                     local_atr = hl.rolling(14).mean().iloc[-1]
                 
                 if local_atr > 0:
                     if "buy" in llm_action:
                         if not explicit_sl or explicit_sl <= 0: explicit_sl = price - 1.5 * local_atr
                         if not explicit_tp or explicit_tp <= 0: explicit_tp = price + 2.0 * local_atr
                     elif "sell" in llm_action:
                         if not explicit_sl or explicit_sl <= 0: explicit_sl = price + 1.5 * local_atr
                         if not explicit_tp or explicit_tp <= 0: explicit_tp = price - 2.0 * local_atr
                     logger.info(f"Generated Default SL/TP using ATR: SL={explicit_sl:.2f}, TP={explicit_tp:.2f}")

             logger.info(f"Trend Mode: Executing decisive '{llm_action}' without grid. Price={price}, SL={explicit_sl}, TP={explicit_tp}, Lot={suggested_lot}")
             
             pass
        
        if is_grid_action:
            # [NEW POLICY] 
            # Grid Deployment is PERMANENTLY DISABLED based on User Request.
            # "这边把grid 网格交易取消掉，只有单一的高抛低吸模式"
            
            logger.warning(f"Grid Deployment Blocked (User Policy: Single Trend Only). Action '{llm_action}' ignored or needs manual conversion.")
            return

            # logger.info(f">>> 执行网格部署 (Direction: {direction}) <<<")
            
            # [NEW] Clear existing pending orders before starting new grid
            # self.cancel_all_pending_orders()
            
            # 2. 提取配置 (Grid Config)
            grid_config = {}
            if self.latest_strategy:
                grid_config = self.latest_strategy.get('grid_config', {})
                # Compatibility with position_management
                if not grid_config:
                     pm = self.latest_strategy.get('position_management', {})
                     grid_config = {
                         'grid_step_pips': pm.get('recommended_grid_step_pips'),
                         'martingale_multiplier': pm.get('martingale_multiplier'),
                         'basket_tp_usd': pm.get('dynamic_basket_tp'),
                         'initial_lot': self.latest_strategy.get('position_size')
                     }

            # 3. 更新网格策略参数
            if grid_config:
                # Multiplier
                if grid_config.get('martingale_multiplier'):
                    try:
                        self.grid_strategy.lot_multiplier = float(grid_config['martingale_multiplier'])
                        logger.info(f"Updated Grid Multiplier: {self.grid_strategy.lot_multiplier}")
                    except: pass
                
                # Basket TP
                basket_tp = grid_config.get('basket_tp_usd')
                if basket_tp:
                    self.grid_strategy.update_dynamic_params(basket_tp=basket_tp)
            
            # 4. 获取 ATR (用于网格间距)
            rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, 20)
            atr = 0.0
            if rates is not None and len(rates) > 14:
                 df_temp = pd.DataFrame(rates)
                 high_low = df_temp['high'] - df_temp['low']
                 atr = high_low.rolling(14).mean().iloc[-1]
            
            if atr <= 0:
                logger.warning("无法计算 ATR，无法生成网格计划")
                return

            logger.info(f"网格方向: {direction} (ATR: {atr:.5f})")

            # 5. 执行首单 (Initial Entry)
            # User Requirement: 不要立即执行市价首单，改为挂单 (Limit Order)
            # 原因: 很多次 Initial Entry 市价进场即亏损
            # 策略: 将首单也作为 Limit 单挂在当前价格下方一点点 (做多) 或 上方一点点 (做空)
            
            initial_lot = 0.02 # [User Requirement] Fixed Initial Lot 0.02
            
            # Update class lot_size for consistency
            self.lot_size = initial_lot
            self.grid_strategy.lot = initial_lot
            
            # 获取 Point
            symbol_info = mt5.symbol_info(self.symbol)
            point = symbol_info.point if symbol_info else 0.01
            
            # 计算首单挂单位置 (Offset based on ATR or Fixed Points)
            # 使用 ATR 的 10% 作为微小回撤等待，或者直接挂在 Grid Step 的第一个位置？
            # 用户只说 "不要立刻开仓"， implying wait for better price.
            # Let's use a small offset: 0.1 * ATR or 50 points
            initial_offset = atr * 0.1 if atr > 0 else 50 * point
            
            if direction == 'bullish':
                entry_type = "limit_buy" # Convert to pending
                # 挂单价格 = 当前Ask - Offset (等待回调接多)
                entry_price = tick.ask - initial_offset
            else:
                entry_type = "limit_sell"
                # 挂单价格 = 当前Bid + Offset (等待反弹接空)
                entry_price = tick.bid + initial_offset
                
            entry_price = self._normalize_price(entry_price)
            
            logger.info(f"执行网格首单(挂单): {entry_type.upper()} {initial_lot} Lots @ {entry_price:.2f} (Offset: {initial_offset:.2f})")
            self._send_order(entry_type, entry_price, sl=0.0, tp=0.0, comment="AI-Grid-Initial-Limit")

            # 6. 生成后续网格计划
            # 注意: 首单现在是 Limit 单，后续网格应该基于这个 Limit 价格继续向下/向上铺设
            # 使用 entry_price 作为基准
            current_price = entry_price 
            
            # 提取 LLM 建议的动态网格间距 (Pips) 和 动态TP配置
            dynamic_step = grid_config.get('grid_step_pips')
            grid_level_tps = self.latest_strategy.get('position_management', {}).get('grid_level_tp_pips')
            
            grid_orders = self.grid_strategy.generate_grid_plan(current_price, direction, atr, point=point, dynamic_step_pips=dynamic_step, grid_level_tps=grid_level_tps)
            
            # 7. 执行挂单
            if grid_orders:
                logger.info(f"网格计划生成 {len(grid_orders)} 个挂单")
                
                # --- [Safety Check] Margin & Overlap ---
                account_info = mt5.account_info()
                if not account_info:
                    logger.error("无法获取账户信息进行风控检查，取消网格部署")
                    return
                
                # A. Overlap Check with Pending Orders
                existing_orders = mt5.orders_get(symbol=self.symbol)
                existing_prices = []
                if existing_orders:
                    for o in existing_orders:
                        if o.magic == self.magic_number:
                            existing_prices.append(o.price_open)
                
                min_dist_points = 50 * point # 50 points safety
                
                final_grid_orders = []
                for order in grid_orders:
                    o_price = order['price']
                    
                    # Check Overlap
                    is_overlap = False
                    for ep in existing_prices:
                        if abs(o_price - ep) < min_dist_points:
                            is_overlap = True
                            break
                    
                    if is_overlap:
                        logger.warning(f"网格挂单价格 {o_price:.2f} 与现有挂单太近，跳过")
                        continue
                        
                    final_grid_orders.append(order)
                
                # B. Margin Pre-Calculation
                total_margin_required = 0.0
                margin_safe = True
                
                for order in final_grid_orders:
                    try:
                        # Estimate margin: Lot * ContractSize / Leverage (Approx)
                        # Better use order_calc_margin but requires knowing type exactly
                        o_type = mt5.ORDER_TYPE_BUY if 'buy' in order['type'] else mt5.ORDER_TYPE_SELL
                        o_vol = order.get('volume', self.lot_size)
                        
                        margin_req = mt5.order_calc_margin(o_type, self.symbol, o_vol, order['price'])
                        if margin_req:
                            total_margin_required += margin_req
                    except Exception as e:
                        logger.warning(f"Margin calc warning: {e}")
                        # Fallback approx
                        total_margin_required += (o_vol * 100000 / 100) * 0.01 # Rough guess if fails
                
                # Check against Free Margin (with buffer)
                if total_margin_required > (account_info.margin_free * 0.8):
                    logger.warning(f"网格部署所需保证金 ({total_margin_required:.2f}) 超过可用保证金的 80% ({account_info.margin_free:.2f})")
                    logger.warning("尝试缩减网格层数...")
                    
                    # Trim orders from the end (furthest away)
                    while total_margin_required > (account_info.margin_free * 0.8) and len(final_grid_orders) > 0:
                        removed = final_grid_orders.pop()
                        # Deduct margin
                        try:
                            o_type = mt5.ORDER_TYPE_BUY if 'buy' in removed['type'] else mt5.ORDER_TYPE_SELL
                            o_vol = removed.get('volume', self.lot_size)
                            margin_req = mt5.order_calc_margin(o_type, self.symbol, o_vol, removed['price'])
                            if margin_req: total_margin_required -= margin_req
                        except: pass
                
                if not final_grid_orders:
                    logger.warning("可用资金不足以部署任何网格单，取消操作")
                    return


                # 临时保存原始 lot_size (although we updated it above, keep logic safe)
                original_lot = self.lot_size
                
                for i, order in enumerate(final_grid_orders):
                    o_type = order['type']
                    o_price = self._normalize_price(order['price'])
                    o_tp = self._normalize_price(order.get('tp', 0.0))
                    o_volume = order.get('volume', 0.0)
                    
                    if o_volume > 0:
                        self.lot_size = o_volume
                    
                    # 发送订单
                    self._send_order(o_type, o_price, sl=0.0, tp=o_tp, comment=f"AI-Grid-{i+1}")
                    
                # 恢复 lot_size (Optional, but good practice if shared state)
                # self.lot_size = original_lot 
                logger.info("网格部署完成 (Initial + Limits)")
                return # 结束本次 execute_trade
            else:
                logger.warning("网格计划为空，未执行任何操作")
                return

        if trade_type and price > 0:
            # [MODIFIED] User Requirement: Enforce SL/TP for Trend Mode
            # explicit_sl = 0.0 # REMOVED: Do not force SL to 0
            
            # Initialize atr to avoid UnboundLocalError
            atr = 0.0
            
            # 再次确认 TP 是否存在
            if explicit_tp is None:
                # User Requirement: Disable Individual TP
                # explicit_tp = 0.0 # REMOVED: Do not force TP to 0
                pass
                
                # logger.info("LLM 未提供明确 TP，尝试计算优化值")
                # 计算 ATR
                # rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, 20)
                # ...
                # Only calculate TP, ignore SL return
                # _, explicit_tp = self.calculate_optimized_sl_tp(trade_type, price, atr, ai_exit_conds=sl_tp_params)
                
                # if explicit_tp == 0:
                #      logger.warning("无法计算优化 TP，使用 ATR 默认值")
                #      if atr > 0:
                #          if "buy" in trade_type: explicit_tp = price + 3.0 * atr
                #          else: explicit_tp = price - 3.0 * atr 

            # User Requirement: 只有盈利比亏损的风险大于 1.2 的情况下交易
            # Enforce R:R check for ALL trade types (Limit/Stop AND Market Buy/Sell)
            # Need ATR for risk estimation if SL is 0
            if atr <= 0:
                 rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, 20)
                 if rates is not None and len(rates) > 14:
                     df_temp = pd.DataFrame(rates)
                     high_low = df_temp['high'] - df_temp['low']
                     atr = high_low.rolling(14).mean().iloc[-1]
            
            # [MODIFIED] Re-enable Hard R:R Check >= 1.2
            if explicit_sl and explicit_sl > 0 and explicit_tp and explicit_tp > 0:
                potential_profit = abs(explicit_tp - price)
                potential_loss = abs(price - explicit_sl)
                
                if potential_loss > 0:
                    rr_ratio = potential_profit / potential_loss
                    if rr_ratio < 1.2:
                        logger.warning(f"R:R check failed: {rr_ratio:.2f} < 1.2 (Profit: {potential_profit:.2f}, Loss: {potential_loss:.2f}). Cancel trade.")
                        return
                    else:
                        logger.info(f"R:R check passed: {rr_ratio:.2f} >= 1.2")
            else:
                logger.info("Skipping Hard R:R Check (SL/TP not fully defined)")

            # FIX: Ensure 'action' is defined for the comment
            # action variable was used in _send_order's comment but was coming from llm_action
            action_str = llm_action.upper() if llm_action else "UNKNOWN"
            comment = f"AI-{action_str}"
            
            # --- 动态仓位计算 ---
            if suggested_lot and suggested_lot > 0:
                # [NEW] Margin Check for Suggested Lot
                try:
                    account_info = mt5.account_info()
                    if account_info:
                         o_type_check = mt5.ORDER_TYPE_BUY if "buy" in action_str.lower() else mt5.ORDER_TYPE_SELL
                         margin_needed = mt5.order_calc_margin(o_type_check, self.symbol, suggested_lot, price)
                         
                         if margin_needed and margin_needed > (account_info.margin_free * 0.9): # 90% buffer
                             max_lot = (account_info.margin_free * 0.9) / (margin_needed / suggested_lot)
                             # Round down to 2 decimal places
                             max_lot = int(max_lot * 100) / 100.0
                             if max_lot < 0.01: max_lot = 0.01
                             
                             logger.warning(f"⚠️ 建议仓位 {suggested_lot} 超过保证金限制 ({margin_needed:.2f} > {account_info.margin_free * 0.9:.2f}). 调整为: {max_lot}")
                             suggested_lot = max_lot
                except Exception as e:
                    logger.error(f"Margin check failed: {e}")

                optimized_lot = suggested_lot
                logger.info(f"使用建议手数 (经过风控检查): {optimized_lot}")
            else:
                # 准备上下文 (Fallback)
                # 获取历史 MFE/MAE 统计 (如果有缓存，从 db_manager 获取)
                trade_stats = self.db_manager.get_trade_performance_stats(limit=50)
                mfe_mae_ratio = 1.0
                if trade_stats and 'avg_mfe' in trade_stats and 'avg_mae' in trade_stats:
                    if abs(trade_stats['avg_mae']) > 0:
                        mfe_mae_ratio = trade_stats['avg_mfe'] / abs(trade_stats['avg_mae'])
                
                # 准备 SMC 上下文 (如果 self.smc_analyzer 最近分析过)
                # 我们从 latest_strategy 的 details 中尝试获取
                market_ctx = {}
                if self.latest_strategy and 'details' in self.latest_strategy:
                     market_ctx['smc'] = {'structure': self.latest_strategy['details'].get('smc_structure')}
                
                # 获取 ATR (复用上面的计算)
                rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, 20)
                if rates is not None:
                    df_temp = pd.DataFrame(rates)
                    high_low = df_temp['high'] - df_temp['low']
                    atr = high_low.rolling(14).mean().iloc[-1]
                    market_ctx['atr'] = atr
                
                # 从 strategy details 中提取所有 AI 信号
                ai_signals_data = None
                if self.latest_strategy and 'details' in self.latest_strategy:
                    ai_signals_data = self.latest_strategy['details'].get('signals', {})
                    # 尝试获取 Volatility Regime
                    if 'adv_summary' in self.latest_strategy['details']:
                        adv_sum = self.latest_strategy['details']['adv_summary']
                        if isinstance(adv_sum, dict) and 'regime_analysis' in adv_sum:
                            market_ctx['volatility_regime'] = adv_sum.get('risk', {}).get('level', 'Normal')

                # 计算最终仓位
                optimized_lot = self.calculate_dynamic_lot(
                    strength, 
                    market_context=market_ctx, 
                    mfe_mae_ratio=mfe_mae_ratio,
                    ai_signals=ai_signals_data
                )
            
            self.lot_size = optimized_lot # 临时覆盖 self.lot_size 供 _send_order 使用
            
            result = self._send_order(trade_type, price, explicit_sl, explicit_tp, comment=comment)
            
            # [NEW] Save Trade to Master DB (Redundant check if _send_order handles it)
            # Actually _send_order calls save_trade, so we need to modify _send_order instead or rely on duplicate calls in _send_order?
            # Let's check _send_order implementation.
            
        else:
            if llm_action not in ['hold', 'neutral']:
                logger.warning(f"无法执行交易: Action={llm_action}, TradeType={trade_type}, Price={price}")



    def _get_filling_mode(self):
        """
        Get the correct order filling mode for the symbol.
        Checks broker support for FOK/IOC.
        """
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            return mt5.ORDER_FILLING_FOK # Default
            
        # filling_mode is a flag property
        # 1: FOK, 2: IOC
        modes = symbol_info.filling_mode
        
        # Use integer values directly if constants are missing in some MT5 versions
        # SYMBOL_FILLING_FOK = 1
        # SYMBOL_FILLING_IOC = 2
        
        # Check using integer values to avoid AttributeError if constants are missing
        SYMBOL_FILLING_FOK_VAL = 1
        SYMBOL_FILLING_IOC_VAL = 2
        
        if modes & SYMBOL_FILLING_FOK_VAL: 
            return mt5.ORDER_FILLING_FOK
        elif modes & SYMBOL_FILLING_IOC_VAL: 
            return mt5.ORDER_FILLING_IOC
        else:
            return mt5.ORDER_FILLING_RETURN

    def _normalize_price(self, price):
        """Standardize price to symbol's tick size"""
        if price is None or price == 0:
            return 0.0
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            return price
        
        # 使用 tick_size 进行更精确的规范化
        tick_size = symbol_info.trade_tick_size
        if tick_size > 0:
            return round(round(price / tick_size) * tick_size, symbol_info.digits)
        else:
            return round(price, symbol_info.digits)

    def _send_order(self, type_str, price, sl, tp, comment=""):
        """底层下单函数"""
        # Normalize prices
        price = self._normalize_price(price)
        sl = self._normalize_price(sl)
        tp = self._normalize_price(tp)
        
        # --- 增强验证逻辑 (Fix Invalid Stops) ---
        symbol_info = mt5.symbol_info(self.symbol)
        if not symbol_info:
            logger.error("无法获取品种信息")
            return

        point = symbol_info.point
        stops_level = (symbol_info.trade_stops_level + 10) * point # 额外加 10 points 缓冲
        
        is_buy = "buy" in type_str
        is_sell = "sell" in type_str
        
        # 1. 检查方向性 (Directionality)
        if is_buy:
            # Buy: SL must be < Price, TP must be > Price
            if sl > 0 and sl >= price:
                logger.warning(f"Invalid SL for BUY (SL {sl:.2f} >= Price {price:.2f}). Auto-Correcting: Removing SL.")
                sl = 0.0 # 移除无效 SL，优先保证成交
            
            if tp > 0 and tp <= price:
                logger.warning(f"Invalid TP for BUY (TP {tp:.2f} <= Price {price:.2f}). Auto-Correcting: Removing TP.")
                tp = 0.0
                
        elif is_sell:
            # Sell: SL must be > Price, TP must be < Price
            if sl > 0 and sl <= price:
                logger.warning(f"Invalid SL for SELL (SL {sl:.2f} <= Price {price:.2f}). Auto-Correcting: Removing SL.")
                sl = 0.0
                
            if tp > 0 and tp >= price:
                logger.warning(f"Invalid TP for SELL (TP {tp:.2f} >= Price {price:.2f}). Auto-Correcting: Removing TP.")
                tp = 0.0

        # 2. 检查最小间距 (Stops Level)
        # 防止 SL/TP 距离价格太近导致 Error 10016
        # 增加额外的 buffer 确保调整后的价格能够满足 Broker 要求
        safe_buffer = point * 20
        
        if sl > 0:
            dist = abs(price - sl)
            if dist < stops_level:
                logger.warning(f"SL too close (Dist {dist:.5f} < Level {stops_level:.5f}). Adjusting.")
                if is_buy: 
                    sl = price - (stops_level + safe_buffer)
                else: 
                    sl = price + (stops_level + safe_buffer)
                sl = self._normalize_price(sl)
                
        if tp > 0:
            dist = abs(price - tp)
            if dist < stops_level:
                logger.warning(f"TP too close (Dist {dist:.5f} < Level {stops_level:.5f}). Adjusting.")
                if is_buy: 
                    tp = price + (stops_level + safe_buffer)
                else: 
                    tp = price - (stops_level + safe_buffer)
                tp = self._normalize_price(tp)
        
        # 3. 检查 Pending Order 的挂单价格合法性 (Invalid Price Check)
        # 对于 Limit Buy，挂单价必须低于当前 Ask
        # 对于 Limit Sell，挂单价必须高于当前 Bid
        # 否则 MT5 会返回 retcode=10015 (Invalid Price)
        
        tick = mt5.symbol_info_tick(self.symbol)
        if tick:
            current_ask = tick.ask
            current_bid = tick.bid
            
            if type_str == "limit_buy":
                if price >= current_ask:
                    logger.warning(f"Limit Buy Price {price:.2f} >= Current Ask {current_ask:.2f}. Adjusting to Ask - 50 points.")
                    price = current_ask - (50 * point) # Ensure it's below
                    price = self._normalize_price(price)
            
            elif type_str == "limit_sell":
                if price <= current_bid:
                    logger.warning(f"Limit Sell Price {price:.2f} <= Current Bid {current_bid:.2f}. Adjusting to Bid + 50 points.")
                    price = current_bid + (50 * point) # Ensure it's above
                    price = self._normalize_price(price)

        # ----------------------------------------
        
        order_type = mt5.ORDER_TYPE_BUY
        action = mt5.TRADE_ACTION_DEAL
        
        if type_str == "buy":
            order_type = mt5.ORDER_TYPE_BUY
            action = mt5.TRADE_ACTION_DEAL
        elif type_str == "sell":
            order_type = mt5.ORDER_TYPE_SELL
            action = mt5.TRADE_ACTION_DEAL
        elif type_str == "limit_buy":
            order_type = mt5.ORDER_TYPE_BUY_LIMIT
            action = mt5.TRADE_ACTION_PENDING
        elif type_str == "limit_sell":
            order_type = mt5.ORDER_TYPE_SELL_LIMIT
            action = mt5.TRADE_ACTION_PENDING
        elif type_str == "stop_buy":
            order_type = mt5.ORDER_TYPE_BUY_STOP
            action = mt5.TRADE_ACTION_PENDING
        elif type_str == "stop_sell":
            order_type = mt5.ORDER_TYPE_SELL_STOP
            action = mt5.TRADE_ACTION_PENDING
            
        request = {
            "action": action,
            "symbol": self.symbol,
            "volume": self.lot_size,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": self.magic_number,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": self._get_filling_mode(),
        }
        
        # --- 增强的订单发送逻辑 (自动重试不同的 Filling Mode) ---
        # 针对 Error 10030 (Unsupported filling mode) 进行自动故障转移
        
        filling_modes = []
        
        # 确定尝试顺序
        if "limit" in type_str or "stop" in type_str:
            # 挂单通常优先尝试 RETURN
            filling_modes = [mt5.ORDER_FILLING_RETURN, mt5.ORDER_FILLING_IOC, mt5.ORDER_FILLING_FOK]
        else:
            # 市价单优先使用 _get_filling_mode 检测到的模式
            preferred = self._get_filling_mode()
            filling_modes = [preferred, mt5.ORDER_FILLING_FOK, mt5.ORDER_FILLING_IOC, mt5.ORDER_FILLING_RETURN]
            
        # 去重并保持顺序
        filling_modes = list(dict.fromkeys(filling_modes))
        
        result = None
        success = False
        
        for mode in filling_modes:
            request['type_filling'] = mode
            
            # 仅记录第一次尝试或重试信息，避免刷屏
            if mode == filling_modes[0]:
                logger.info(f"发送订单请求: Action={action}, Type={order_type}, Price={price:.2f}, SL={sl:.2f}, TP={tp:.2f}, Filling={mode}")
            else:
                logger.info(f"重试订单 (Filling Mode: {mode})...")
                
            result = mt5.order_send(request)
            
            if result is None:
                logger.error("order_send 返回 None")
                break
                
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                success = True
                logger.info(f"下单成功 ({type_str}) #{result.order} (Mode: {mode})")
                self.send_telegram_message(f"✅ *Order Executed*\nType: `{type_str.upper()}`\nPrice: `{price}`\nSL: `{sl}`\nTP: `{tp}`")
                break
            elif result.retcode == 10030: # Unsupported filling mode
                logger.warning(f"Filling mode {mode} 不支持 (10030), 尝试下一个模式...")
                continue
            else:
                # 其他错误，不重试
                logger.error(f"下单失败 ({type_str}): {result.comment}, retcode={result.retcode}")
                break
                
        if not success and result and result.retcode == 10030:
             logger.error(f"下单失败 ({type_str}): 所有 Filling Mode 均被拒绝 (10030)")



                



    def escape_markdown(self, text):
        """Helper to escape Markdown special characters for Telegram"""
        if not isinstance(text, str):
            text = str(text)
        # Escaping for Markdown (V1)
        escape_chars = '_*[`'
        for char in escape_chars:
            text = text.replace(char, f'\\{char}')
        return text

    def send_telegram_message(self, message):
        """发送消息到 Telegram"""
        token = "8253887074:AAE_o7hfEb6iJCZ2MdVIezOC_E0OnTCvCzY"
        chat_id = "5254086791"
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        # 配置代理 (针对中国大陆用户)
        # 如果您使用 Clash，通常端口是 7890
        # 如果您使用 v2rayN，通常端口是 10809
        proxies = {
            "http": "http://127.0.0.1:7890",
            "https": "http://127.0.0.1:7890"
        }
        
        try:
            import requests
            try:
                # 尝试通过代理发送
                response = requests.post(url, json=data, timeout=10, proxies=proxies)
            except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError):
                # 如果代理失败，尝试直连 (虽然可能也会被墙)
                logger.warning("代理连接失败，尝试直连 Telegram...")
                response = requests.post(url, json=data, timeout=10)
                
            if response.status_code != 200:
                logger.error(f"Telegram 发送失败: {response.text}")
                # Fallback: Try sending as plain text if Markdown parsing fails
                if response.status_code == 400 and "parse entities" in response.text:
                    logger.warning("Markdown 解析失败，尝试以纯文本发送...")
                    if "parse_mode" in data:
                        del data["parse_mode"]
                    try:
                         # Retry without proxy first (or with proxy as before) - just keep logic simple
                         # Re-use the same proxy logic
                         try:
                             response = requests.post(url, json=data, timeout=10, proxies=proxies)
                         except:
                             response = requests.post(url, json=data, timeout=10)
                             
                         if response.status_code == 200:
                             logger.info("纯文本消息发送成功")
                         else:
                             logger.error(f"纯文本发送也失败: {response.text}")
                    except Exception as e_retry:
                        logger.error(f"重试发送失败: {e_retry}")

        except Exception as e:
            logger.error(f"Telegram 发送异常: {e}")

    def manage_positions(self, signal=None, strategy_params=None):
        """
        根据最新分析结果管理持仓:
        1. Grid Strategy Logic (Basket TP, Adding Positions)
        2. 更新止损止盈 (覆盖旧设置) - 基于 strategy_params
        3. 执行移动止损 (Trailing Stop)
        4. 检查是否需要平仓 (非反转情况，例如信号转弱)
        """
        positions = mt5.positions_get(symbol=self.symbol)
        if positions is None or len(positions) == 0:
            return

        # --- Grid Strategy Logic ---
        # 1. Check Basket TP (Moved to main loop for better ATR handling and Tuple fix)
        # if self.grid_strategy.check_basket_tp(positions): ...

        # 2. Check Grid Add (Only if allowed by LLM)
        # 增加 LLM 权限控制: 默认允许，但如果 LLM 明确禁止 (allow_grid=False)，则暂停加仓
        allow_grid = True
        
        # [USER REQUEST] Cancel Grid Strategy Completely
        # "取消网格交易策略...仓位完全有大模型来分析判断"
        # We force allow_grid to False to disable adding positions autonomously.
        # Position sizing is handled by 'execute_trade' calling 'calculate_dynamic_lot' based on LLM input.
        allow_grid = False 
        
        if self.latest_strategy and isinstance(self.latest_strategy, dict):
            # 0. Check Strategy Mode (Trend Mode disables Grid)
            if self.latest_strategy.get('strategy_mode') == 'trend':
                allow_grid = False
            else:
                # 1. Check root 'grid_config' (New Standard)
                grid_config = self.latest_strategy.get('grid_config', {})
                if 'allow_add' in grid_config:
                     allow_grid = bool(grid_config['allow_add'])
                else:
                     # 2. Check legacy 'parameter_updates'
                     grid_settings = self.latest_strategy.get('parameter_updates', {}).get('grid_settings', {})
                     if 'allow_add' in grid_settings:
                         allow_grid = bool(grid_settings['allow_add'])
        
        # Override again to be sure, based on user's latest instruction
        # "取消网格交易策略" means NO autonomous grid adding.
        allow_grid = False
        
        tick = mt5.symbol_info_tick(self.symbol)
        if tick and allow_grid:
            current_price_check = tick.bid # Use Bid for price check approximation
            action, lot = self.grid_strategy.check_grid_add(positions, current_price_check)
            if action:
                logger.info(f"Grid Strategy Trigger: {action} Lot={lot}")
                trade_type = "buy" if action == 'add_buy' else "sell"
                price = tick.ask if trade_type == 'buy' else tick.bid
                
                # Dynamic Add TP Logic
                add_tp = 0.0
                # User Requirement: Disable Individual TP, rely on Basket TP
                # if self.latest_strategy:
                #      pos_mgmt = self.latest_strategy.get('position_management', {})
                #      grid_tps = pos_mgmt.get('grid_level_tp_pips')
                #      if grid_tps:
                #          # Determine level index
                #          current_count = self.grid_strategy.long_pos_count if trade_type == 'buy' else self.grid_strategy.short_pos_count
                #          # Use specific TP if available
                #          tp_pips = grid_tps[current_count] if current_count < len(grid_tps) else grid_tps[-1]
                #          
                #          point = mt5.symbol_info(self.symbol).point
                #          if trade_type == 'buy':
                #              add_tp = price + (tp_pips * 10 * point)
                #          else:
                #              add_tp = price - (tp_pips * 10 * point)
                #          
                #          logger.info(f"Dynamic Add TP: {add_tp} ({tp_pips} pips)")

                self._send_order(trade_type, price, 0.0, add_tp, comment=f"Grid: {action}")
                # Don't return, allow SL/TP update for existing positions

        # 获取 ATR 用于计算移动止损距离 (动态调整)
        # REMOVED: User requested no SL and no Trailing Stop.
        # This section previously calculated ATR and managed individual position SL/TP updates.
        # It has been removed to ensure no SL is applied or moved.
        pass

    def analyze_closed_trades(self):
        """
        分析已平仓的交易，计算 MFE (最大有利波动) and MAE (最大不利波动)
        用于后续 AI 学习和策略优化
        """
        try:
            # 1. 获取数据库中尚未标记为 CLOSED 的交易
            open_trades = self.db_manager.get_open_trades()
            
            if not open_trades:
                return

            for trade in open_trades:
                ticket = trade['ticket'] # 这是 Order Ticket
                symbol = trade['symbol']
                
                # 2. 检查该订单是否已完全平仓
                # 我们通过 Order Ticket 查找对应的 History Orders 或 Deals
                # 注意: 在 MT5 中，一个 Position 可能由多个 Deal 组成 (In, Out)
                # 我们需要找到该 Order 开启的 Position ID
                
                # 尝试通过 Order Ticket 获取 Position ID
                # history_orders_get 可以通过 ticket 获取指定历史订单
                # 但我们需要的是 Deals 来确定是否平仓
                
                # 方法 A: 获取该 Order 的 Deal，得到 Position ID，然后查询 Position 的所有 Deals
                # 假设 Order Ticket 也是 Position ID (通常情况)
                position_id = ticket 
                
                # 获取该 Position ID 的所有历史交易
                # from_date 设为很久以前，确保能找到
                deals = mt5.history_deals_get(position=position_id)
                
                if deals is None or len(deals) == 0:
                    # 可能还没平仓，或者 Ticket 不是 Position ID
                    # 如果是 Netting 账户，PositionID 通常等于开仓 Deal 的 Ticket
                    continue
                    
                # 检查是否有 ENTRY_OUT (平仓) 类型的 Deal
                has_out = False
                close_time = 0
                close_price = 0.0
                profit = 0.0
                open_price = trade['price'] # 使用 DB 中的开仓价
                open_time_ts = 0
                
                # 重新计算利润和确认平仓
                total_profit = 0.0
                
                for deal in deals:
                    # Safely access commission
                    commission = getattr(deal, 'commission', 0.0)
                    total_profit += deal.profit + deal.swap + commission
                    
                    if deal.entry == mt5.DEAL_ENTRY_IN:
                        open_time_ts = deal.time
                        # 如果 DB 中没有准确的开仓价，可以用这个: open_price = deal.price
                    
                    if deal.entry == mt5.DEAL_ENTRY_OUT:
                        has_out = True
                        close_time = deal.time
                        close_price = deal.price
                
                # 如果有 OUT deal，说明已平仓 (或部分平仓，这里简化为只要有 OUT 就视为结束分析)
                # 并且要确保此时持仓量为 0 (完全平仓)
                # 通过 positions_get(ticket=position_id) 检查是否还存在不要简化
                
                active_pos = mt5.positions_get(ticket=position_id)
                is_fully_closed = True
                if active_pos is not None and len(active_pos) > 0:
                    # Position still exists
                    is_fully_closed = False
                
                if has_out and is_fully_closed:
                    # 这是一个已平仓的完整交易
                    # 获取该时段的 M1 数据来计算 MFE/MAE
                    
                    # 确保时间范围有效
                    if open_time_ts == 0:
                        open_time_ts = int(pd.to_datetime(trade['time']).timestamp())
                        
                    start_dt = datetime.fromtimestamp(open_time_ts)
                    end_dt = datetime.fromtimestamp(close_time)
                    
                    if start_dt >= end_dt:
                        continue
                        
                    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, start_dt, end_dt)
                                               
                    if rates is not None and len(rates) > 0:
                        df_rates = pd.DataFrame(rates)
                        max_high = df_rates['high'].max()
                        min_low = df_rates['low'].min()
                        
                        mfe = 0.0
                        mae = 0.0
                        
                        action = trade['action']
                        
                        if action == 'BUY':
                            mfe = (max_high - open_price) / open_price * 100 # %
                            mae = abs((min_low - open_price) / open_price * 100) # % (Absolute)
                        elif action == 'SELL':
                            mfe = (open_price - min_low) / open_price * 100 # %
                            mae = abs((open_price - max_high) / open_price * 100) # % (Absolute)
                            
                        # 更新数据库
                        self.db_manager.update_trade_performance(ticket, {
                            "close_price": close_price,
                            "close_time": end_dt,
                            "profit": total_profit,
                            "mfe": mfe,
                            "mae": mae
                        })
                        
                        # [NEW] Sync Performance Update to Master DB
                        self.master_db_manager.update_trade_performance(ticket, {
                            "result": "WIN" if total_profit > 0 else "LOSS",
                            "close_price": close_price,
                            "close_time": end_dt,
                            "profit": total_profit,
                            "mfe": mfe,
                            "mae": mae
                        })
                        
                        logger.info(f"分析交易 #{ticket} 完成: MFE={mfe:.2f}%, MAE={mae:.2f}%, Profit={total_profit:.2f}")

        except Exception as e:
            logger.error(f"分析历史交易失败: {e}")

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
            # Revised for SMC, CCI/RVGI, Grid
            p_smc_ma = int(params[0])
            p_smc_atr = params[1]
            p_rvgi_sma = int(params[2])
            p_rvgi_cci = int(params[3])
            p_ifvg_gap = int(params[4])
            
            # Extract Grid Params
            p_grid_step = int(params[5]) if len(params) > 5 else 300
            p_grid_tp = float(params[6]) if len(params) > 6 else 100.0
            
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
                    
                    if final_sig == "buy":
                        trades_count += 1
                        diff = next_price - curr_price
                        balance += diff
                        if diff > 0: wins += 1
                        
                        # Grid Penalty (Simplified)
                        if p_grid_step < 100: balance -= 10 
                        
                    elif final_sig == "sell":
                        trades_count += 1
                        diff = curr_price - next_price
                        balance += diff
                        if diff > 0: wins += 1
                        
                        if p_grid_step < 100: balance -= 10
            
            if trades_count == 0: return -100
            
            # Simple Profit Metric
            score = (balance - 10000.0)
            return score
            
        except Exception as e:
            return -9999

    def optimize_strategy_parameters(self):
        """
        Comprehensive Optimization: Tunes ALL strategy parameters using Auto-AO.
        """
        logger.info("开始执行全策略参数优化 (Comprehensive Auto-AO)...")
        
        # Reset progress counter
        self._opt_counter = 0
        
        # 1. 获取历史数据
        df = self.get_market_data(1000) 
        if df is None or len(df) < 500:
            logger.warning("数据不足，跳过优化")
            return
            
        # 2. Define Search Space
        # smc_ma, smc_atr, rvgi_sma, rvgi_cci, ifvg_gap, grid_step, grid_tp
        bounds = [
            (100, 300),     # smc_ma
            (0.001, 0.005), # smc_atr
            (10, 50),       # rvgi_sma
            (10, 30),       # rvgi_cci
            (10, 100),      # ifvg_gap
            (200, 600),     # grid_step (points)
            (50.0, 200.0)   # grid_tp (global TP USD)
        ]
        
        steps = [10, 0.0005, 2, 2, 5, 50, 10.0]
        
        # 3. Objective
        def objective(params):
            return self.evaluate_comprehensive_params(params, df)
            
        # 4. Optimizer
        import random
        algo_name = random.choice(list(self.optimizers.keys()))
        optimizer = self.optimizers[algo_name]
        
        # Adjust population size for realtime performance
        if hasattr(optimizer, 'pop_size'):
            # Calculate pop_size to match roughly 500 evaluations
            # Total Evals = Pop_Size (Init) + Pop_Size * Epochs
            # 200 = 50 + 50 * 3
            optimizer.pop_size = 50
            
        logger.info(f"本次选择的优化算法: {algo_name} (Pop: {optimizer.pop_size})")

        # [NEW] Fetch Historical Data for Seeding
        # Try to get 'good' params from previous runs from DB
        historical_seeds = []
        
        # 1. Load from DB (Best historical results)
        try:
            db_seeds = self.db_manager.get_top_optimization_results(self.symbol, limit=100) # Load up to 100 historical seeds
            if db_seeds:
                historical_seeds.extend(db_seeds)
                logger.info(f"Loaded {len(db_seeds)} historical optimization seeds from DB")
        except Exception as e:
            logger.error(f"Failed to load historical seeds: {e}")
        
        # 2. Add current active params as a seed (if valid)
        if hasattr(self, 'short_term_params') and self.short_term_params:
             # Construct a param vector from current settings (as a good starting point)
             # smc_ma, smc_atr, rvgi_sma, rvgi_cci, ifvg_gap, grid_step, grid_tp
             current_seed = [
                 self.smc_analyzer.ma_period,
                 self.smc_analyzer.atr_threshold,
                 self.short_term_params.get('rvgi_sma', 20),
                 self.short_term_params.get('rvgi_cci', 14),
                 self.short_term_params.get('ifvg_gap', 20),
                 self.grid_strategy.grid_step_points,
                 self.grid_strategy.global_tp
             ]
             # Assign a high score to current params to encourage exploitation if they are good, 
             # but we don't know the score yet. Let's give it a reasonable dummy score or skip score.
             # The optimizer sorts by score, so we give it a high prior.
             historical_seeds.append({'params': current_seed, 'score': 9999}) 
        
        # 5. Run
        best_params, best_score = optimizer.optimize(
            objective, 
            bounds, 
            steps=steps, 
            epochs=3,
            historical_data=historical_seeds # Pass seeds
        )
        
        # 6. Apply Results
        if best_score > -1000:
            logger.info(f"全策略优化完成! Best Score: {best_score:.2f}")
            
            # Save to DB for future seeding
            self.db_manager.save_optimization_result(
                algo_name, 
                self.symbol, 
                self.tf_name, 
                best_params, 
                best_score
            )
            
            # Extract
            p_smc_ma = int(best_params[0])
            p_smc_atr = best_params[1]
            p_rvgi_sma = int(best_params[2])
            p_rvgi_cci = int(best_params[3])
            p_ifvg_gap = int(best_params[4])
            p_grid_step = int(best_params[5])
            p_grid_tp = float(best_params[6])
            
            # Apply
            self.smc_analyzer.ma_period = p_smc_ma
            self.smc_analyzer.atr_threshold = p_smc_atr
            
            self.short_term_params = {
                'rvgi_sma': p_rvgi_sma,
                'rvgi_cci': p_rvgi_cci,
                'ifvg_gap': p_ifvg_gap
            }

            # Apply Grid Params
            self.grid_strategy.grid_step_points = p_grid_step
            self.grid_strategy.global_tp = p_grid_tp
            
            msg = (
                f"🧬 *Comprehensive Optimization ({algo_name})*\n"
                f"Score: {best_score:.2f}\n"
                f"• SMC: MA={p_smc_ma}, ATR={p_smc_atr:.4f}\n"
                f"• ST: RVGI({p_rvgi_sma},{p_rvgi_cci}), IFVG({p_ifvg_gap})\n"
                f"• Grid: Step={p_grid_step}, GlobalTP={p_grid_tp:.1f}"
            )
            self.send_telegram_message(msg)
            logger.info(f"已更新所有策略参数: {msg}")
            
        else:
            logger.warning("优化失败，保持原有参数")

    def optimize_weights(self):
        """
        使用激活的优化算法 (GWO, WOAm, etc.) 实时优化 HybridOptimizer 的权重
        解决优化算法一直为负数的问题：确保有实际运行并使用正向的适应度函数 (准确率)
        """
        if len(self.signal_history) < 20: # 需要一定的历史数据
            return

        logger.info(f"正在运行权重优化 ({self.active_optimizer_name})... 样本数: {len(self.signal_history)}")
        
        # 1. 准备数据
        # 提取历史信号和实际结果
        # history items: (timestamp, signals_dict, close_price)
        # 我们需要计算每个样本的实际涨跌: price[i+1] - price[i]
        
        samples = []
        for i in range(len(self.signal_history) - 1):
            curr = self.signal_history[i]
            next_bar = self.signal_history[i+1]
            
            signals = curr[1]
            price_change = next_bar[2] - curr[2]
            
            actual_dir = 0
            if price_change > 0: actual_dir = 1
            elif price_change < 0: actual_dir = -1
            
            if actual_dir != 0:
                samples.append((signals, actual_dir))
                
        if len(samples) < 10:
            return

        # 2. 定义目标函数 (适应度函数)
        # 输入: 权重向量 [w1, w2, ...]
        # 输出: 准确率 (0.0 - 1.0) -> 保证非负
        strategy_keys = list(self.optimizer.weights.keys())
        
        def objective(weights_vec):
            correct = 0
            total = 0
            
            # 构建临时权重字典
            temp_weights = {k: w for k, w in zip(strategy_keys, weights_vec)}
            
            for signals, actual_dir in samples:
                # 模拟 combine_signals
                weighted_sum = 0
                total_w = 0
                
                for strat, sig in signals.items():
                    w = temp_weights.get(strat, 1.0)
                    if sig == 'buy':
                        weighted_sum += w
                        total_w += w
                    elif sig == 'sell':
                        weighted_sum -= w
                        total_w += w
                
                if total_w > 0:
                    norm_score = weighted_sum / total_w
                    
                    pred_dir = 0
                    if norm_score > 0.3: pred_dir = 1
                    elif norm_score < -0.3: pred_dir = -1
                    
                    if pred_dir == actual_dir:
                        correct += 1
                    total += 1
            
            if total == 0: return 0.0
            return correct / total # 返回准确率
            
        # 3. 运行优化
        optimizer = self.optimizers[self.active_optimizer_name]
        
        # 定义边界: 权重范围 [0.0, 2.0]
        bounds = [(0.0, 2.0) for _ in range(len(strategy_keys))]
        
        try:
            best_weights_vec, best_score = optimizer.optimize(
                objective_function=objective,
                bounds=bounds,
                epochs=20 # 实时运行不宜过久
            )
            
            # 4. 应用最佳权重
            if best_score > 0: # 确保结果有效
                for i, k in enumerate(strategy_keys):
                    self.optimizer.weights[k] = best_weights_vec[i]
                
                logger.info(f"权重优化完成! 最佳准确率: {best_score:.2%}")
                logger.info(f"新权重: {self.optimizer.weights}")
                self.last_optimization_time = time.time()
            else:
                logger.warning("优化结果得分过低，未更新权重")
                
        except Exception as e:
            logger.error(f"权重优化失败: {e}")

    def calculate_optimized_sl_tp(self, trade_type, price, atr, market_context=None, ai_exit_conds=None):
        """
        计算基于综合因素的优化止损止盈点
        结合: 14天 ATR, MFE/MAE 统计, 市场分析(Supply/Demand/FVG), 大模型建议
        """
        # 1. 基础波动率 (14天 ATR)
        if atr <= 0:
            atr = price * 0.005 # Fallback
            
        # 2. 历史绩效 (MFE/MAE)
        mfe_tp_dist = atr * 2.0 
        mae_sl_dist = atr * 1.5 
        
        try:
             # [NEW] Use Master DB for Collective Learning (Cross-Symbol Learning)
             # Fetch more trades (200) to get better stats from all symbols
             stats = self.master_db_manager.get_trade_performance_stats(limit=200)
             if not stats:
                 # Fallback to local DB if master is empty
                 stats = self.db_manager.get_trade_performance_stats(limit=100)
                 
             trades = []
             if isinstance(stats, list): trades = stats
             elif isinstance(stats, dict) and 'recent_trades' in stats: trades = stats['recent_trades']
             
             if trades and len(trades) > 10:
                 mfes = [t.get('mfe', 0) for t in trades if t.get('mfe', 0) > 0]
                 maes = [abs(t.get('mae', 0)) for t in trades if abs(t.get('mae', 0)) > 0]
                 
                 if mfes and maes:
                     opt_tp_pct = np.percentile(mfes, 60) / 100.0 
                     opt_sl_pct = np.percentile(maes, 95) / 100.0 
                     
                     min_sl_dist = atr * 2.5
                     calc_sl_dist = price * opt_sl_pct
                     
                     mfe_tp_dist = price * opt_tp_pct
                     mae_sl_dist = max(calc_sl_dist, min_sl_dist) 
        except Exception as e:
             logger.warning(f"MFE/MAE 计算失败: {e}")

        # 3. 市场结构调整 (Supply/Demand/FVG)
        struct_tp_price = 0.0
        struct_sl_price = 0.0
        min_sl_buffer = atr * 2.0
        
        if market_context:
            is_buy = 'buy' in trade_type
            
            # 解析 SMC 关键位
            resistance_candidates = []
            support_candidates = []
            
            if is_buy:
                # Buy TP: Resistance
                if 'supply_zones' in market_context:
                    for z in market_context['supply_zones']:
                        val = z[1] if isinstance(z, (list, tuple)) else z.get('bottom')
                        if val and val > price: resistance_candidates.append(val)
                if 'bearish_fvgs' in market_context:
                    for f in market_context['bearish_fvgs']:
                        val = f.get('bottom')
                        if val and val > price: resistance_candidates.append(val)
                if resistance_candidates: struct_tp_price = min(resistance_candidates)
                
                # Buy SL: Support
                if 'demand_zones' in market_context:
                     for z in market_context['demand_zones']:
                        val = z[0] if isinstance(z, (list, tuple)) else z.get('top')
                        if val and val < price: support_candidates.append(val)
                if support_candidates: struct_sl_price = max(support_candidates)
                
            else: # Sell
                # Sell TP: Support
                if 'demand_zones' in market_context:
                    for z in market_context['demand_zones']:
                        val = z[0] if isinstance(z, (list, tuple)) else z.get('top')
                        if val and val < price: support_candidates.append(val)
                if 'bullish_fvgs' in market_context:
                    for f in market_context['bullish_fvgs']:
                        val = f.get('top')
                        if val and val < price: support_candidates.append(val)
                if support_candidates: struct_tp_price = max(support_candidates)
                
                # Sell SL: Resistance
                if 'supply_zones' in market_context:
                    for z in market_context['supply_zones']:
                        val = z[1] if isinstance(z, (list, tuple)) else z.get('bottom')
                        if val and val > price: resistance_candidates.append(val)
                if resistance_candidates: struct_sl_price = min(resistance_candidates)

        # 4. 大模型建议 (AI Integration)
        ai_sl = 0.0
        ai_tp = 0.0
        if ai_exit_conds:
            ai_sl = ai_exit_conds.get('sl_price', 0.0)
            if ai_sl is None: ai_sl = 0.0
            
            ai_tp = ai_exit_conds.get('tp_price', 0.0)
            if ai_tp is None: ai_tp = 0.0
            
            # Validate AI Suggestion Direction
            if 'buy' in trade_type:
                if ai_sl >= price: ai_sl = 0.0 # Invalid SL
                if ai_tp <= price: ai_tp = 0.0 # Invalid TP
            else:
                if ai_sl <= price: ai_sl = 0.0
                if ai_tp >= price: ai_tp = 0.0

        # 5. 综合计算与融合 (Advanced Optimization & Positioning)
        # Requirement: "TP 和 SL 需要每次结合大模型集成分析市场趋势情绪，以及 MAE，MFE，所有高级算法后自动优化配置，移动，不是动态移动"
        # Interpret: Initial Setup must be "Moved" to the optimal level derived from all factors.
        
        final_sl = 0.0
        final_tp = 0.0
        
        # Helper to log optimization steps
        opt_log = []

        if 'buy' in trade_type:
            # --- SL Optimization ---
            # 1. Base (MAE Statistical Safety Net)
            mae_safe_sl = price - mae_sl_dist
            
            # 2. Structural (SMC Invalidation)
            struct_safe_sl = struct_sl_price if struct_sl_price > 0 else 0.0
            
            # 3. AI Proposal
            ai_prop_sl = ai_sl if ai_sl > 0 else 0.0
            
            # 4. Optimization Logic (The "Move" Process)
            # Start with AI proposal or Structure
            candidate_sl = ai_prop_sl if ai_prop_sl > 0 else struct_safe_sl
            
            # Fallback to MAE if nothing else
            if candidate_sl == 0: candidate_sl = mae_safe_sl
            
            # Constraint 1: MAE Check (Don't set SL tighter than historical average adverse excursion)
            # If candidate is HIGHER than mae_safe_sl (i.e. distance is smaller), it's risky.
            # But maybe structure is there. We check ATR buffer.
            # Let's enforce MAE as a soft floor.
            if candidate_sl > mae_safe_sl:
                 # AI/Structure is tighter than MAE. 
                 # If trend is strong, tight is okay. If ranging, need wide.
                 # Let's use ATR to decide. If diff is small, keep tight. If large diff, maybe widen.
                 pass
            
            # Constraint 2: Structure Check (Don't place SL exactly ON support, move it below)
            if struct_safe_sl > 0:
                 # Ensure SL is slightly below structure (ATR buffer)
                 buffer = atr * 0.2
                 if candidate_sl > (struct_safe_sl - buffer):
                      candidate_sl = struct_safe_sl - buffer
                      opt_log.append(f"Moved SL below Structure {struct_safe_sl}")

            # Constraint 3: Anti-Hunt (Too close check)
            min_dist = atr * 0.8
            if (price - candidate_sl) < min_dist:
                 candidate_sl = price - min_dist
                 opt_log.append("Widened SL for Anti-Hunt")

            final_sl = candidate_sl
            
            # --- TP Optimization ---
            # 1. Base (MFE Potential)
            mfe_target_tp = price + mfe_tp_dist
            
            # 2. Structural (Liquidity/Resistance)
            struct_target_tp = struct_tp_price if struct_tp_price > 0 else 0.0
            
            # 3. AI Proposal
            ai_prop_tp = ai_tp if ai_tp > 0 else 0.0
            
            # 4. Optimization
            candidate_tp = ai_prop_tp if ai_prop_tp > 0 else mfe_target_tp
            
            # Constraint: If Structure Resistance is BEFORE Candidate TP, we might want to "Move" TP to just before structure
            # to ensure fill.
            if struct_target_tp > 0 and struct_target_tp < candidate_tp:
                 # Resistance is closer than target. Move TP to resistance (minus buffer).
                 buffer = atr * 0.1
                 candidate_tp = struct_target_tp - buffer
                 opt_log.append(f"Moved TP to Resistance {struct_target_tp}")
            
            # Constraint: MFE Statistical Cap (Don't be too greedy)
            # If Candidate > MFE * 1.5, maybe pull back?
            # Let's trust AI for big moves, but respect MFE stats.
            
            final_tp = candidate_tp

        else: # Sell
            # --- SL Optimization ---
            mae_safe_sl = price + mae_sl_dist
            struct_safe_sl = struct_sl_price if struct_sl_price > 0 else 0.0
            ai_prop_sl = ai_sl if ai_sl > 0 else 0.0
            
            candidate_sl = ai_prop_sl if ai_prop_sl > 0 else struct_safe_sl
            if candidate_sl == 0: candidate_sl = mae_safe_sl
            
            # Constraint: MAE (If candidate < mae_safe, i.e. tighter)
            
            # Constraint: Structure (Move above resistance)
            if struct_safe_sl > 0:
                 buffer = atr * 0.2
                 if candidate_sl < (struct_safe_sl + buffer):
                      candidate_sl = struct_safe_sl + buffer
                      opt_log.append(f"Moved SL above Structure {struct_safe_sl}")

            # Anti-Hunt
            min_dist = atr * 0.8
            if (candidate_sl - price) < min_dist:
                 candidate_sl = price + min_dist
                 opt_log.append("Widened SL for Anti-Hunt")
                 
            final_sl = candidate_sl

            # --- TP Optimization ---
            mfe_target_tp = price - mfe_tp_dist
            struct_target_tp = struct_tp_price if struct_tp_price > 0 else 0.0
            ai_prop_tp = ai_tp if ai_tp > 0 else 0.0
            
            candidate_tp = ai_prop_tp if ai_prop_tp > 0 else mfe_target_tp
            
            # Constraint: Support is higher (closer) than TP
            if struct_target_tp > 0 and struct_target_tp > candidate_tp:
                 buffer = atr * 0.1
                 candidate_tp = struct_target_tp + buffer
                 opt_log.append(f"Moved TP to Support {struct_target_tp}")
            
            final_tp = candidate_tp

        if opt_log:
            logger.info(f"SL/TP Optimized Move: {'; '.join(opt_log)}")

        return final_sl, final_tp



    def analyze_ema_ha_strategy(self, df):
        """
        CandleSmoothing EMA Engine Strategy Implementation
        Indicators: EMA 50 (Close), EMA 20 High, EMA 20 Low, Heiken Ashi
        """
        try:
            if df is None or len(df) < 55:
                return {"signal": "neutral", "reason": "Not enough data"}

            # 1. Calculate Indicators
            # EMA
            ema_50 = df['close'].ewm(span=50, adjust=False).mean()
            ema_20_high = df['high'].ewm(span=20, adjust=False).mean()
            ema_20_low = df['low'].ewm(span=20, adjust=False).mean()

            # Heiken Ashi (Manual Calculation)
            ha_close = (df['open'] + df['high'] + df['low'] + df['close']) / 4
            
            # HA Open requires iteration or shifting
            # Fast vectorized approximation or loop
            # Since we only need the last few values for signal, we can calculate fully or just last few if we had prev state.
            # But here we calculate for dataframe.
            
            ha_open = np.zeros(len(df))
            ha_open[0] = (df['open'].iloc[0] + df['close'].iloc[0]) / 2
            
            # Using loop for correctness (HA Open depends on previous HA Open)
            # This might be slightly slow for very large DF, but for 600 rows it's negligible
            ha_close_values = ha_close.values
            for i in range(1, len(df)):
                ha_open[i] = (ha_open[i-1] + ha_close_values[i-1]) / 2
            
            ha_open = pd.Series(ha_open, index=df.index)
            
            # 2. Logic Implementation
            # MQL Logic:
            # buySignal = (haClose1 > ema20h_closed) && haBull1 && (haClose1 > ema50_closed) &&
            #             trendBull && (haClosePrev < ema50_prev);
            
            # Python Indexing:
            # -1: Current (Forming) -> Ignore for signal usually, or use if confirmed close
            # MQL uses [1] (Last Closed) and [2] (Prev Closed)
            # So we use .iloc[-2] and .iloc[-3]
            
            idx_1 = -2
            idx_2 = -3
            
            ha_c_1 = ha_close.iloc[idx_1]
            ha_o_1 = ha_open.iloc[idx_1]
            ha_c_2 = ha_close.iloc[idx_2]
            
            ema_20_h_1 = ema_20_high.iloc[idx_1]
            ema_20_l_1 = ema_20_low.iloc[idx_1]
            
            ema_50_1 = ema_50.iloc[idx_1]
            ema_50_2 = ema_50.iloc[idx_2]
            
            # Conditions
            ha_bull_1 = ha_c_1 > ha_o_1
            trend_bull = ema_50_1 > ema_50_2
            trend_bear = ema_50_1 < ema_50_2
            
            buy_signal = (ha_c_1 > ema_20_h_1) and ha_bull_1 and (ha_c_1 > ema_50_1) and \
                         trend_bull and (ha_c_2 < ema_50_2)
            
            sell_signal = (ha_c_1 < ema_20_l_1) and (not ha_bull_1) and (ha_c_1 < ema_50_1) and \
                          trend_bear and (ha_c_2 > ema_50_2)
            
            result = {
                "signal": "neutral",
                "reason": "No Crossover",
                "values": {
                    "ema_50": ema_50_1,
                    "ema_20_high": ema_20_h_1,
                    "ema_20_low": ema_20_l_1,
                    "ha_close": ha_c_1,
                    "ha_open": ha_o_1,
                    "trend": "bullish" if trend_bull else "bearish"
                }
            }
            
            if buy_signal:
                result["signal"] = "buy"
                result["reason"] = "EMA-HA Crossover Bullish"
            elif sell_signal:
                result["signal"] = "sell"
                result["reason"] = "EMA-HA Crossover Bearish"
                
            return result
            
        except Exception as e:
            logger.error(f"EMA-HA Analysis Failed: {e}")
            return {"signal": "neutral", "reason": "Error", "values": {}}

    def optimize_short_term_params(self):
        """
        Optimize short-term strategy parameters (RVGI+CCI, IFVG)
        Executed every 1 hour
        """
        # [DISABLED] as per user request
        return

        logger.info("Running Short-Term Parameter Optimization (WOAm)...")
        
        # 1. Get Data (Last 500 M10 candles) [Changed from M15 to M10 if available, but MT5 standard is M10/M15? MT5 has M10.]
        # User request: "改成交易周期 10 分钟" (Change trading timeframe to 10 minutes)
        # We need to ensure we request TIMEFRAME_M10
        df = self.get_market_data(500) # This uses self.timeframe which we will update
        if df is None or len(df) < 200:
            return

        # 2. Define Objective Function
        def objective(params):
            p_rvgi_sma = int(params[0])
            p_rvgi_cci = int(params[1])
            p_ifvg_gap = int(params[2])
            
            backtest_window = 100
            if len(df) < backtest_window + 50: return -100
            
            test_data = df.iloc[-(backtest_window+50):]
            
            # Simple Backtest Loop (Maximize Total Profit)
            total_profit = 0
            trades_count = 0
            
            closes = test_data['close'].values
            
            for i in range(len(test_data)-20, len(test_data)):
                sub_df = test_data.iloc[:i+1]
                
                # Check signals
                res_rvgi = self.advanced_adapter.analyze_rvgi_cci_strategy(sub_df, sma_period=p_rvgi_sma, cci_period=p_rvgi_cci)
                res_ifvg = self.advanced_adapter.analyze_ifvg(sub_df, min_gap_points=p_ifvg_gap)
                
                sig = "neutral"
                if res_rvgi['signal'] == 'buy' or res_ifvg['signal'] == 'buy': sig = 'buy'
                elif res_rvgi['signal'] == 'sell' or res_ifvg['signal'] == 'sell': sig = 'sell'
                
                # Check profit 5 bars later
                if sig != "neutral" and i + 5 < len(test_data):
                    entry = closes[i]
                    exit_p = closes[i+5]
                    if sig == 'buy': profit = (exit_p - entry) / entry
                    else: profit = (entry - exit_p) / entry
                    
                    total_profit += profit
                    trades_count += 1
            
            if trades_count == 0: return 0
            return total_profit

        # 3. Optimization
        optimizer = WOAm()
        bounds = [(10, 50), (7, 21), (10, 100)] # [sma, cci, gap]
        steps = [1, 1, 5]
        
        best_params, best_score = optimizer.optimize(objective, bounds, steps=steps, epochs=3)
        
        # 4. Apply
        if best_score > 0:
            logger.info(f"Short-Term Optimization Complete. Score: {best_score}")
            logger.info(f"New Params: RVGI_SMA={int(best_params[0])}, RVGI_CCI={int(best_params[1])}, IFVG_GAP={int(best_params[2])}")
            
            # Store these params in a property to be used by analyze_full
            # We need to add a property to store these or pass them
            self.short_term_params = {
                'rvgi_sma': int(best_params[0]),
                'rvgi_cci': int(best_params[1]),
                'ifvg_gap': int(best_params[2])
            }
            # We also need to update the analyze call in run() to use these
        else:
            logger.info("Short-Term Optimization found no improvement.")

    def sync_account_history(self):
        """
        Sync historical account trades to local DB to enable immediate self-learning.
        Fetches last 30 days of history.
        """
        try:
            # Sync last 30 days
            from_date = datetime.now() - pd.Timedelta(days=30)
            to_date = datetime.now()
            
            # Fetch history deals
            deals = mt5.history_deals_get(from_date, to_date)
            
            if deals is None or len(deals) == 0:
                logger.info("No historical deals found in the last 30 days.")
                return

            count = 0
            for deal in deals:
                # Only care about exits (deals that closed a position) to record profit
                # ENTRY_OUT = 1, ENTRY_INOUT = 2 (Reversal)
                if deal.entry in [mt5.DEAL_ENTRY_OUT, mt5.DEAL_ENTRY_INOUT]:
                    # Use position_id as ticket
                    ticket = deal.position_id
                    symbol = deal.symbol
                    # Safely access commission
                    commission = getattr(deal, 'commission', 0.0)
                    profit = deal.profit + deal.swap + commission
                    
                    # We need to ensure this trade exists in our DB
                    # Since we don't have the full open info easily without searching IN deals,
                    # we do a partial update/insert just for the metrics (profit)
                    
                    # Check if exists
                    # This is a direct DB operation, effectively "Upsert" for performance stats
                    # We use a custom SQL in db_manager or just standard save logic if possible.
                    # But save_trade expects more fields.
                    # Let's manually insert/ignore to ensure we have the record for stats.
                    
                    conn = self.db_manager._get_connection()
                    cursor = conn.cursor()
                    
                    # Try to get existing
                    cursor.execute("SELECT ticket FROM trades WHERE ticket = ?", (ticket,))
                    exists = cursor.fetchone()
                    
                    if not exists:
                        # Insert new record from history
                        # We might not know if it was BUY or SELL without checking IN deal, 
                        # but for WinRate/ProfitFactor, direction doesn't matter much.
                        # We can infer direction from profit vs price change if needed, but let's skip for now.
                        action = "UNKNOWN"
                        if deal.type == mt5.DEAL_TYPE_BUY: action = "BUY" # This is the closing deal type!
                        elif deal.type == mt5.DEAL_TYPE_SELL: action = "SELL"
                        
                        # Note: Closing deal type is opposite to Position type usually.
                        # If I closed with a SELL deal, I was Long (BUY).
                        pos_type = "BUY" if deal.type == mt5.DEAL_TYPE_SELL else "SELL"
                        
                        insert_sql = '''
                            INSERT OR IGNORE INTO trades (ticket, symbol, action, volume, price, time, result, close_price, close_time, profit, mfe, mae)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        '''
                        insert_params = (
                            ticket, 
                            symbol, 
                            pos_type, 
                            deal.volume, 
                            0.0, # Open price unknown
                            datetime.fromtimestamp(deal.time), # Approximate open time
                            'CLOSED',
                            deal.price,
                            datetime.fromtimestamp(deal.time),
                            profit,
                            0.0, 
                            0.0
                        )
                        
                        # Sync to Local DB
                        cursor.execute(insert_sql, insert_params)
                        
                        # [NEW] Sync to Master DB
                        try:
                            m_conn = self.master_db_manager._get_connection()
                            m_cursor = m_conn.cursor()
                            m_cursor.execute(insert_sql, insert_params)
                            m_conn.commit()
                        except Exception as e_master:
                            logger.error(f"Failed to sync historical trade {ticket} to Master DB: {e_master}")
                            
                        count += 1
            
            if count > 0:
                self.db_manager.conn.commit()
                logger.info(f"Synced {count} historical trades from MT5 to local & master DB.")
                
        except Exception as e:
            logger.error(f"Failed to sync account history: {e}")

    def initialize(self):
        """Initialize Trader State"""
        logger.info(f"初始化交易代理 - {self.symbol}")
        
        # [NEW] Start FileWatcher
        # Watch 'src' and 'config' (if it exists)
        watch_dirs = [
            os.path.join(project_root, "src"),
            os.path.join(project_root, "config")
        ]
        # Filter out non-existent dirs
        watch_dirs = [d for d in watch_dirs if os.path.exists(d)]
        
        self.file_watcher = FileWatcher(watch_dirs)
        self.file_watcher.start()
        logger.info(f"File Watcher started on: {watch_dirs}")
        
        # Sync history on startup
        self.sync_account_history()
        self.is_running = True

    def calculate_smart_basket_tp(self, llm_tp, atr, market_regime, smc_data, current_positions, performance_stats=None):
        """
        结合 LLM 建议、市场波动率 (ATR)、市场结构 (SMC) 和风险状态计算最终的 Dynamic Basket TP
        """
        if not current_positions:
            return llm_tp if llm_tp else 100.0
            
        # 1. 基础值: LLM 建议 (权重最高，因为包含了宏观和综合判断)
        base_tp = float(llm_tp) if llm_tp and float(llm_tp) > 0 else 100.0
        
        # 2. 波动率约束 (ATR Constraint)
        # 最小 TP 应该至少覆盖 3 倍 ATR 的波动，否则容易被噪音止盈
        # 假设 1 Lot, ATR=2.0 (200 points) -> Value = $200 approx for Gold? No.
        # ATR 是价格差。如果持仓量大，ATR 对应的金额也大。
        # 我们这里估算: Basket TP (USD) >= Total Lots * ATR_Points * TickValue * Multiplier
        
        total_volume = sum([p['volume'] for p in current_positions])
        symbol_info = mt5.symbol_info(self.symbol)
        tick_value = symbol_info.trade_tick_value if symbol_info else 1.0
        point = symbol_info.point if symbol_info else 0.01
        
        # ATR (Price Diff) -> ATR Value (USD)
        # ATR Value = ATR / Point * TickValue * Volume
        atr_value_total = (atr / point) * tick_value * total_volume
        
        min_tp_volatility = atr_value_total * 2.0 # 至少赚取 2倍 ATR 的波动价值
        
        # 3. 市场体制修正 (Regime Correction)
        regime_multiplier = 1.0
        if market_regime == 'trending':
            regime_multiplier = 1.2 # 趋势中放大目标
        elif market_regime == 'ranging':
            regime_multiplier = 0.8 # 震荡中缩小目标
            
        # [NEW] 3.5 MFE/MAE 历史绩效修正
        mfe_multiplier = 1.0
        if performance_stats:
            try:
                # Filter recent winners
                winners = [t for t in performance_stats if t.get('profit', 0) > 0]
                if len(winners) > 5:
                    avg_mfe = sum([float(t.get('mfe', 0)) for t in winners]) / len(winners)
                    avg_profit = sum([float(t.get('profit', 0)) for t in winners]) / len(winners)
                    
                    if avg_profit > 0 and avg_mfe > (avg_profit * 1.5):
                        # Historical MFE is 1.5x larger than realized profit -> We are leaving money on table
                        mfe_multiplier = 1.3
                        logger.info(f"Performance Optimization: Avg MFE ({avg_mfe:.2f}) >> Avg Profit ({avg_profit:.2f}). Boosting TP by 30%.")
            except Exception as e:
                logger.warning(f"Failed to calc MFE stats: {e}")
            
        # 4. SMC 阻力位修正 (SMC Resistance Cap)
        # ... (Existing logic implied, but we use MFE/Regime to override)
        
        # 计算混合 TP
        # 逻辑: 加权平均
        # 60% LLM, 40% Volatility-based (Increased Volatility weight to respect Market Structure more)
        # 且应用 Regime & MFE Multiplier
        
        tech_tp = min_tp_volatility
        
        # 如果 LLM 值异常小 (小于 ATR 价值)，可能是保守或错误，取较大值
        # 如果 LLM 值异常大，可能是贪婪，取加权
        
        # [USER REQUEST] Remove ATR_Val (tech_tp) from Final TP Calculation
        # The user observed: Base(LLM)=150.00, ATR_Val=1241.81 -> Final=1241.81
        # This implies tech_tp is dominating and pushing TP too high (or too low if LLM is high).
        # We will use LLM as the primary driver (100% weight) but still respect Regime/MFE multipliers.
        # We still calculate tech_tp for logging but don't mix it.
        
        final_tp = base_tp 
        final_tp *= regime_multiplier
        final_tp *= mfe_multiplier
        
        # 5. 硬性下限
        # final_tp = max(final_tp, min_tp_volatility) # [REMOVED] Don't force ATR lower bound if user wants LLM value
        final_tp = max(final_tp, 5.0) # Absolute min $5
        
        # User Requirement: Basket TP based on reasonable config & market sentiment
        # "Cannot be too high nor too low" -> Dynamic Range based on ATR & Avg Open Price
        
        if total_volume > 0 and atr > 0:
            # Calculate Weighted Average Open Price
            weighted_sum = sum([p['open_price'] * p['volume'] for p in current_positions])
            avg_open_price = weighted_sum / total_volume
            
            # Calculate Target Distance in Price Units
            # Profit = Volume * Distance * TickVal / Point
            # Distance = (Profit * Point) / (Volume * TickVal)
            target_dist_price = (final_tp * point) / (total_volume * tick_value)
            
            # Compare with ATR
            atr_ratio = target_dist_price / atr
            
            # Define reasonable bounds based on Regime
            min_atr_ratio = 0.2 
            max_atr_ratio = 1.0 
            
            if market_regime == 'trending':
                max_atr_ratio = 3.5 # [Optimized] Increased from 2.5 to 3.5 to allow Trend Surfing
            elif market_regime == 'ranging':
                max_atr_ratio = 1.0 # [Optimized] Increased from 0.8 to 1.0
            
            # Clamp Distance
            clamped_dist = max(min_atr_ratio * atr, min(target_dist_price, max_atr_ratio * atr))
            
            # Recalculate TP from Clamped Distance
            adjusted_tp = (clamped_dist * total_volume * tick_value) / point
            
            if abs(adjusted_tp - final_tp) > 0.5:
                logger.info(f"TP Adjusted by ATR Structure: {final_tp:.2f} -> {adjusted_tp:.2f} (Dist: {target_dist_price:.2f} -> {clamped_dist:.2f}, ATR: {atr:.2f})")
                final_tp = adjusted_tp
                
        # Final Hard Limits
        # [Optimized] Relaxed Upper Limits significantly to allow big wins
        upper_limit = 500.0 
        if market_regime == 'trending':
            upper_limit = 2000.0
            
        final_tp = max(final_tp, 5.0) # Min $5
        final_tp = min(final_tp, upper_limit)
        
        logger.info(f"Smart Basket TP Calc: Base(LLM)={base_tp:.2f}, ATR_Val={tech_tp:.2f}, Regime={market_regime}, MFE_Mult={mfe_multiplier} -> Final={final_tp:.2f}")
        return final_tp

    def check_trading_schedule(self):
        """
        Check if trading is allowed based on the schedule and symbol.
        Rules:
        - ETHUSD: Weekend (Sat-Sun) + Monday < 07:00.
        - GOLD/XAUUSD/EURUSD: Monday >= 06:30 to Saturday 00:00.
        """
        now = datetime.now()
        weekday = now.weekday() # 0=Mon, 6=Sun
        current_time = now.time()
        
        symbol_upper = self.symbol.upper()
        
        # Crypto Rules (ETHUSD)
        # 允许交易时间: 周六(5), 周日(6), 周一(0) 07:00 之前
        if "ETH" in symbol_upper:
            is_weekend = weekday >= 5
            is_monday_morning = (weekday == 0 and current_time.hour < 7)
            
            if is_weekend or is_monday_morning:
                return True
            else:
                # 只有在整点或半点打印日志，避免刷屏
                if current_time.minute % 30 == 0 and current_time.second < 2:
                    logger.info(f"[{self.symbol}] 非交易时间 (Crypto). 允许: 周六-周一07:00. 当前: {now.strftime('%A %H:%M')}")
                return False
                
        # Forex/Metal Rules (GOLD, EURUSD)
        # Standard Market Time (UTC+8 approx):
        # Open: Monday 06:00 (Winter) / 05:00 (Summer)
        # Close: Saturday 06:00 (Winter) / 05:00 (Summer)
        # We use a conservative schedule to ensure safety across seasons.
        if "GOLD" in symbol_upper or "XAU" in symbol_upper or "EUR" in symbol_upper:
            # Monday: Allow from 06:30 (Safe buffer after 06:00 Winter Open)
            if weekday == 0:
                if (current_time.hour > 6) or (current_time.hour == 6 and current_time.minute >= 30):
                    return True
                else:
                    if current_time.minute % 30 == 0 and current_time.second < 2:
                        logger.info(f"[{self.symbol}] 非交易时间 (Forex Start). 允许: 周一 06:30+. 当前: {now.strftime('%A %H:%M')}")
                    return False
            
            # Tuesday(1) - Friday(4): All Day
            elif 1 <= weekday <= 4:
                return True
                
            # Saturday(5): Allow until 06:00 (Safe buffer before 05:00 Summer Close)
            elif weekday == 5:
                if current_time.hour < 6:
                    return True
                else:
                    if current_time.minute % 30 == 0 and current_time.second < 2:
                        logger.info(f"[{self.symbol}] 非交易时间 (Forex Weekend). 允许: 周一06:30 - 周六06:00. 当前: {now.strftime('%A %H:%M')}")
                    return False
            
            # Sunday(6): Closed
            else:
                if current_time.minute % 30 == 0 and current_time.second < 2:
                    logger.info(f"[{self.symbol}] 非交易时间 (Forex Weekend). 允许: 周一06:30 - 周六06:00. 当前: {now.strftime('%A %H:%M')}")
                return False
                
        # Default: Allow if not specified
        return True

    def process_tick(self):
        """Single tick processing"""
        if not self.is_running:
            return

        # 0. Check Trading Schedule
        if not self.check_trading_schedule():
            return

        # [NEW] Safety Check (Continuous Monitoring)
        is_safe, reason = self.check_account_safety(close_if_critical=True)
        if not is_safe and "CRITICAL" in reason:
             # Critical issues already handled (positions closed), just return to prevent further actions
             return

        try:
            # 1. 获取最新数据
            # Using copy_rates_from_pos instead of copy_rates_range for simplicity/speed
            # [User Request]: "改成交易周期 10 分钟" -> self.timeframe should be TIMEFRAME_M10
            # Ensure we are using the correct timeframe property
            
            # Ensure symbol is selected and available
            # Optimization: Check visibility first to avoid unnecessary select calls
            s_info = mt5.symbol_info(self.symbol)
            
            # If symbol info is missing, force selection immediately
            if s_info is None:
                if not mt5.symbol_select(self.symbol, True):
                    err = mt5.last_error()
                    logger.warning(f"Failed to force select symbol {self.symbol} in process_tick (Error={err})")
                    return
                
                # Check again after selection
                s_info = mt5.symbol_info(self.symbol)
                if s_info is None:
                    logger.warning(f"Symbol info still not found for {self.symbol} after selection")
                    return

            if not s_info.visible:
                if not mt5.symbol_select(self.symbol, True):
                    err = mt5.last_error()
                    logger.warning(f"Failed to select symbol {self.symbol} in process_tick (Error={err})")
                    return

            rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, 500)
            if rates is None:
                 err = mt5.last_error()
                 logger.warning(f"Failed to get rates for {self.symbol} (Error={err})")
                 return
                 
            if len(rates) < 100:
                logger.warning(f"Insufficient rates for {self.symbol} (Got {len(rates)}, Need 100)")
                return

            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            # --- Grid Strategy Update (Fast Loop) ---
            self.grid_strategy.update_market_data(df)
            
            # Get Current Positions
            positions = mt5.positions_get(symbol=self.symbol)
            if positions is None: positions = []
            
            # Extract features needed for dynamic calc
            # Use simple TR if cache missing
            high = df['high'].values
            low = df['low'].values
            close = df['close'].values
            tr1 = high[-1] - low[-1]
            tr2 = abs(high[-1] - close[-2])
            tr3 = abs(low[-1] - close[-2])
            current_atr = max(tr1, max(tr2, tr3))
            
            # Check Grid TP / Lock (Moved to end of loop)
            # should_close_long, should_close_short = self.grid_strategy.check_basket_tp(positions, current_atr=current_atr)


            # Single iteration logic (replacing while True)
            if True:
                # 0. 管理持仓 (移动止损) - 使用最新策略
                if self.latest_strategy:
                    self.manage_positions(self.latest_signal, self.latest_strategy)
                else:
                    self.manage_positions() # 降级为默认
                
                # 0.5 分析已平仓交易 (每 60 次循环 / 约 1 分钟执行一次)
                if int(time.time()) % 60 == 0:
                    self.analyze_closed_trades()
                    
                # 0.6 执行策略参数优化 (每 4 小时一次)
                if time.time() - self.last_optimization_time > 14400:
                    self.optimize_strategy_parameters()
                    self.last_optimization_time = time.time()
                
                # 0.7 执行短线参数优化 (每 1 小时一次)
                if int(time.time()) % 3600 == 0:
                    self.optimize_short_term_params()
                
                # 0.8 执行数据库 Checkpoint (每 1 分钟一次，以满足高实时性整合需求)
                # 虽然 WAL 模式下读取已是实时，但定期 Checkpoint 可确保 .db 文件物理更新
                # 已由独立的 checkpoint 服务接管，此处移除以避免锁竞争
                # if int(time.time()) % 60 == 0:
                #    self.db_manager.perform_checkpoint()

                # 1. 检查新 K 线
                # 获取最后一根 K 线的时间
                rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, 1)
                if rates is None:
                    time.sleep(1)
                    return
                    
                current_bar_time = rates[0]['time']
                
                # --- Real-time Data Update (Added for Dashboard) ---
                # 每隔 10 秒保存一次当前正在形成的 K 线数据到数据库
                # 这样 Dashboard 就可以看到实时价格跳动
                if time.time() - self.last_realtime_save > 10:
                    try:
                        # [Checkpoint] 每隔 5 分钟 (300秒) 执行一次 WAL Checkpoint
                        if time.time() - self.last_checkpoint_time > 300:
                            self.db_manager.perform_checkpoint()
                            self.master_db_manager.perform_checkpoint()
                            self.last_checkpoint_time = time.time()
                            
                        df_current = pd.DataFrame(rates)
                        df_current['time'] = pd.to_datetime(df_current['time'], unit='s')
                        df_current.set_index('time', inplace=True)
                        if 'tick_volume' in df_current.columns:
                            df_current.rename(columns={'tick_volume': 'volume'}, inplace=True)
                        
                        self.db_manager.save_market_data(df_current.copy(), self.symbol, self.tf_name)
                        # [NEW] Sync to Master DB
                        self.master_db_manager.save_market_data(df_current.copy(), self.symbol, self.tf_name)
                        
                        self.last_realtime_save = time.time()
                        
                        # --- 实时保存账户信息 (新增) ---
                        try:
                            account_info = mt5.account_info()
                            if account_info:
                                # 计算当前品种的浮动盈亏
                                positions = mt5.positions_get(symbol=self.symbol)
                                symbol_pnl = 0.0
                                magic_positions_count = 0
                                if positions:
                                    for pos in positions:
                                        # 仅统计和计算属于本策略ID的持仓
                                        if pos.magic == self.magic_number:
                                            magic_positions_count += 1
                                            # Handle different position object structures safely
                                            profit = getattr(pos, 'profit', 0.0)
                                            swap = getattr(pos, 'swap', 0.0)
                                            commission = getattr(pos, 'commission', 0.0) # Check attribute existence
                                            symbol_pnl += profit + swap + commission
                                
                                # 显示当前 ID 的持仓状态
                                # if magic_positions_count > 0:
                                #     logger.info(f"ID {self.magic_number} 当前持仓: {magic_positions_count} 个")
                                # else:
                                #     pass
                                
                                metrics = {
                                    "timestamp": datetime.now(),
                                    "balance": account_info.balance,
                                    "equity": account_info.equity,
                                    "margin": account_info.margin,
                                    "free_margin": account_info.margin_free,
                                    "margin_level": account_info.margin_level,
                                    "total_profit": account_info.profit,
                                    "symbol_pnl": symbol_pnl
                                }
                                self.db_manager.save_account_metrics(metrics)
                                # [NEW] Sync Account Metrics to Master DB
                                self.master_db_manager.save_account_metrics(metrics)
                        except Exception as e:
                            logger.error(f"Failed to save account metrics: {e}")
                        # ------------------------------
                        
                        # 实时更新持仓 SL/TP (使用最近一次分析的策略)
                        if self.latest_strategy:
                            self.manage_positions(self.latest_signal, self.latest_strategy)
                            
                    except Exception as e:
                        logger.error(f"Real-time data save failed: {e}")
                # ---------------------------------------------------

                # 如果是新 K 线 或者 这是第一次运行 (last_bar_time 为 0)
                # 用户需求: 交易周期改为 6 分钟，大模型 6 分钟分析
                is_new_bar = current_bar_time != self.last_bar_time
                # 交易分析触发器: 新K线生成 (或第一次运行)
                should_trade_analyze = is_new_bar or (self.last_analysis_time == 0)
                
                if should_trade_analyze:
                    # Run Optimization if needed (Every 4 hours)
                    if time.time() - self.last_optimization_time > 3600 * 4: # 4 hours
                         self.optimize_strategy_parameters()
                         self.optimize_weights()
                         self.last_optimization_time = time.time()

                    if self.last_analysis_time == 0:
                        logger.info("首次运行，立即执行分析...")
                    else:
                        logger.info(f"新K线生成 ({datetime.fromtimestamp(current_bar_time)}), 执行策略分析...")
                    
                    self.last_bar_time = current_bar_time
                    self.last_analysis_time = time.time()
                    
                    # 2. 获取数据并分析
                    # PEM 需要至少 108 根 K 线 (ma_fast_period)，MTF 更新 Zones 需要 500 根
                    # 为了确保所有模块都有足够数据，我们获取 600 根 (60 hours of M6)
                    df = self.get_market_data(600) 
                    
                    if df is not None:
                        # Fetch Multi-Timeframe Data (H1, M15)
                        rates_h1 = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_H1, 0, 200)
                        rates_m15 = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M15, 0, 100)
                        
                        df_h1 = pd.DataFrame(rates_h1) if rates_h1 is not None else pd.DataFrame()
                        df_m15 = pd.DataFrame(rates_m15) if rates_m15 is not None else pd.DataFrame()

                        if not df_h1.empty: 
                            df_h1['time'] = pd.to_datetime(df_h1['time'], unit='s')
                            if 'tick_volume' in df_h1: df_h1.rename(columns={'tick_volume': 'volume'}, inplace=True)
                        if not df_m15.empty: 
                            df_m15['time'] = pd.to_datetime(df_m15['time'], unit='s')
                            if 'tick_volume' in df_m15: df_m15.rename(columns={'tick_volume': 'volume'}, inplace=True)

                        # 保存市场数据到DB
                        self.db_manager.save_market_data(df, self.symbol, self.tf_name)
                        
                        # 更新 Grid Strategy 数据
                        self.grid_strategy.update_market_data(df)
                        
                        # 使用 data_processor 计算指标
                        processor = MT5DataProcessor()
                        df_features = processor.generate_features(df)
                        
                        # Calculate features for H1/M15
                        df_features_h1 = processor.generate_features(df_h1) if not df_h1.empty else pd.DataFrame()
                        df_features_m15 = processor.generate_features(df_m15) if not df_m15.empty else pd.DataFrame()
                        
                        # Helper to safely get latest dict
                        def get_latest_safe(dframe):
                            if dframe.empty: return {}
                            return dframe.iloc[-1].to_dict()

                        feat_h1 = get_latest_safe(df_features_h1)
                        feat_m15 = get_latest_safe(df_features_m15)

                        # 3. 调用 AI 与高级分析
                        # 构建市场快照
                        current_price = df.iloc[-1]
                        latest_features = df_features.iloc[-1].to_dict()
                        
                        # 获取账户资金信息
                        account_info_dict = {}
                        try:
                            acc = mt5.account_info()
                            if acc:
                                account_info_dict = {
                                    "balance": float(acc.balance),
                                    "equity": float(acc.equity),
                                    "margin": float(acc.margin),
                                    "margin_free": float(acc.margin_free),
                                    "leverage": int(acc.leverage), # [NEW] Pass leverage to AI
                                    "available_balance": float(acc.balance) 
                                }
                        except Exception as e:
                            logger.error(f"Error fetching account info: {e}")

                        market_snapshot = {
                            "symbol": self.symbol,
                            "account_info": account_info_dict,
                            "timeframe": self.tf_name,
                            "prices": {
                                "open": float(current_price['open']),
                                "high": float(current_price['high']),
                                "low": float(current_price['low']),
                                "close": float(current_price['close']),
                                "volume": int(current_price['volume'])
                            },
                            "indicators": {
                                "rsi": float(latest_features.get('rsi', 50)),
                                "atr": float(latest_features.get('atr', 0)),
                                "ema_fast": float(latest_features.get('ema_fast', 0)),
                                "ema_slow": float(latest_features.get('ema_slow', 0)),
                                "volatility": float(latest_features.get('volatility', 0))
                            },
                            "multi_tf_data": {
                                "H1": {
                                    "close": float(feat_h1.get('close', 0)),
                                    "rsi": float(feat_h1.get('rsi', 50)),
                                    "ema_fast": float(feat_h1.get('ema_fast', 0)),
                                    "ema_slow": float(feat_h1.get('ema_slow', 0)),
                                    "trend": "bullish" if feat_h1.get('ema_fast', 0) > feat_h1.get('ema_slow', 0) else "bearish"
                                },
                                "M15": {
                                    "close": float(feat_m15.get('close', 0)),
                                    "rsi": float(feat_m15.get('rsi', 50)),
                                    "ema_fast": float(feat_m15.get('ema_fast', 0)),
                                    "ema_slow": float(feat_m15.get('ema_slow', 0)),
                                    "trend": "bullish" if feat_m15.get('ema_fast', 0) > feat_m15.get('ema_slow', 0) else "bearish"
                                }
                            }
                        }
                        
                        # --- 3.1 & 3.2 Advanced Analysis (Cached after first run) ---
                        # [Optimization] Skip heavy analysis after first run, use cached context
                        if not self.first_analysis_done:
                            logger.info("⚡ Executing Full Advanced Analysis (First Run)...")
                            
                            # --- 3.1 CRT 分析 ---
                            crt_result = self.crt_analyzer.analyze(self.symbol, current_price, current_bar_time)
                            logger.info(f"CRT 分析: {crt_result['signal']} ({crt_result['reason']})")
                            
                            # --- 3.2.1 多时间周期分析 (MTF) ---
                            mtf_result = self.mtf_analyzer.analyze(self.symbol, current_price, current_bar_time)
                            logger.info(f"MTF 分析: {mtf_result['signal']} ({mtf_result['reason']})")
                            
                            # --- 3.2.2 高级技术分析 (CCI/RVGI/IFVG) ---
                            st_params = getattr(self, 'short_term_params', {})
                            adv_result = self.advanced_adapter.analyze_full(df, params=st_params)
                            adv_signal = "neutral"
                            if adv_result:
                                adv_signal = adv_result['signal_info']['signal']
                                logger.info(f"高级技术分析: {adv_signal} (强度: {adv_result['signal_info']['strength']})")
                                
                            # --- 3.2.3 SMC 分析 ---
                            smc_result = self.smc_analyzer.analyze(df, self.symbol)
                            logger.info(f"SMC 结构: {smc_result['structure']} (信号: {smc_result['signal']})")
                            
                            # --- 3.2.4 IFVG 分析 ---
                            if adv_result and 'ifvg' in adv_result:
                                ifvg_result = adv_result['ifvg']
                            else:
                                ifvg_result = {"signal": "hold", "strength": 0, "reasons": [], "active_zones": []}
                            logger.info(f"IFVG 分析: {ifvg_result['signal']} (Strength: {ifvg_result['strength']})")

                            # --- 3.2.5 RVGI+CCI 分析 ---
                            if adv_result and 'rvgi_cci' in adv_result:
                                rvgi_cci_result = adv_result['rvgi_cci']
                            else:
                                rvgi_cci_result = {"signal": "hold", "strength": 0, "reasons": []}
                            logger.info(f"RVGI+CCI 分析: {rvgi_cci_result['signal']} (Strength: {rvgi_cci_result['strength']})")
                            
                            # --- 3.2.5.b CandleSmoothing EMA Strategy ---
                            ema_ha_result = self.analyze_ema_ha_strategy(df)
                            logger.info(f"EMA-HA 策略: {ema_ha_result['signal']}")

                            # --- 3.2.6 Grid Strategy Analysis ---
                            # Extract SMC and IFVG levels for Grid
                            smc_grid_data = {'ob': [], 'fvg': []}
                            
                            # From IFVG
                            if 'active_zones' in ifvg_result:
                                for z in ifvg_result['active_zones']:
                                    z_type = 'bearish' if z['type'] == 'supply' else 'bullish'
                                    smc_grid_data['ob'].append({'top': z['top'], 'bottom': z['bottom'], 'type': z_type})
                            
                            # From SMC Analyzer
                            if 'details' in smc_result:
                                if 'ob' in smc_result['details'] and 'active_obs' in smc_result['details']['ob']:
                                    for ob in smc_result['details']['ob']['active_obs']:
                                        smc_grid_data['ob'].append({'top': ob['top'], 'bottom': ob['bottom'], 'type': ob['type']})
                                if 'fvg' in smc_result['details'] and 'active_fvgs' in smc_result['details']['fvg']:
                                    for fvg in smc_result['details']['fvg']['active_fvgs']:
                                        smc_grid_data['fvg'].append({'top': fvg['top'], 'bottom': fvg['bottom'], 'type': fvg['type']})

                            self.grid_strategy.update_smc_levels(smc_grid_data)
                            
                            grid_signal = self.grid_strategy.get_entry_signal(float(current_price['close']))
                            logger.info(f"Grid Kalman Signal: {grid_signal}")
                            
                            # Cache Results
                            self.cached_analysis = {
                                'crt': crt_result,
                                'mtf': mtf_result,
                                'adv': adv_result,
                                'smc': smc_result,
                                'ifvg': ifvg_result,
                                'rvgi_cci': rvgi_cci_result,
                                'ema_ha': ema_ha_result,
                                'grid_signal': grid_signal
                            }
                            self.first_analysis_done = True
                            
                        else:
                            # Load from Cache
                            logger.info("⚡ Using Cached Advanced Analysis (Skipping heavy computation)")
                            crt_result = self.cached_analysis.get('crt')
                            mtf_result = self.cached_analysis.get('mtf')
                            adv_result = self.cached_analysis.get('adv')
                            smc_result = self.cached_analysis.get('smc')
                            ifvg_result = self.cached_analysis.get('ifvg')
                            rvgi_cci_result = self.cached_analysis.get('rvgi_cci')
                            ema_ha_result = self.cached_analysis.get('ema_ha')
                            grid_signal = self.cached_analysis.get('grid_signal')
                            
                            # Restore adv_signal
                            adv_signal = "neutral"
                            if adv_result:
                                adv_signal = adv_result['signal_info']['signal']
                            
                            # Ensure SMC levels are still present in grid strategy (they persist in the object)
                            # Update Grid Signal with CURRENT price even if levels are old?
                            # User said "Directly call Large Model", implies skip everything.
                            # So we keep the old grid signal too.
                        
                        grid_status = {
                            "active": self.grid_strategy.long_pos_count > 0 or self.grid_strategy.short_pos_count > 0,
                            "longs": self.grid_strategy.long_pos_count,
                            "shorts": self.grid_strategy.short_pos_count,
                            "kalman_price": self.grid_strategy.kalman_value
                        }

                        # 准备优化器池信息
                        optimizer_info = {
                            "available_optimizers": list(self.optimizers.keys()),
                            "active_optimizer": self.active_optimizer_name,
                            "last_optimization_score": self.optimizers[self.active_optimizer_name].best_score if self.optimizers[self.active_optimizer_name].best_score > -90000 else None,
                            "descriptions": {
                                "WOAm": "Whale Optimization Algorithm (Modified)",
                                "TETA": "Time Evolution Travel Algorithm"
                            }
                        }

                        # --- 3.3 Qwen 策略分析 (Sole Decision Maker) ---
                        logger.info("正在调用 Qwen 生成策略...")
                        
                        # 获取历史交易绩效 (MFE/MAE) - 优先尝试远程 PostgreSQL 数据库 (Self-Learning)
                        trade_stats = []
                        try:
                            # 尝试从远程获取 (Remote Storage is initialized in DatabaseManager)
                            if self.db_manager.remote_storage.enabled:
                                logger.info("Fetching trade history from Remote PostgreSQL for Self-Learning...")
                                remote_trades = self.db_manager.remote_storage.get_trades(limit=None)
                                if remote_trades:
                                    trade_stats = remote_trades
                                    logger.info(f"Successfully loaded {len(trade_stats)} trades from Remote DB.")
                        except Exception as e:
                            logger.error(f"Failed to fetch remote trades: {e}")

                        if not trade_stats:
                            # Fallback to local Master DB
                            trade_stats = self.master_db_manager.get_trade_performance_stats(limit=100)
                        
                        if not trade_stats:
                             # Fallback to local Symbol DB
                             trade_stats = self.db_manager.get_trade_performance_stats(symbol=self.symbol, limit=50)
                        
                        # 获取当前持仓状态
                        positions = mt5.positions_get(symbol=self.symbol)
                        current_positions_list = []
                        if positions:
                            for pos in positions:
                                cur_mfe, cur_mae = self.get_position_stats(pos)
                                r_multiple = 0.0
                                if pos.sl > 0:
                                    risk_dist = abs(pos.price_open - pos.sl)
                                    if risk_dist > 0:
                                        profit_dist = (pos.price_current - pos.price_open) if pos.type == mt5.POSITION_TYPE_BUY else (pos.price_open - pos.price_current)
                                        r_multiple = profit_dist / risk_dist
                                
                                current_positions_list.append({
                                    "ticket": pos.ticket,
                                    "type": "buy" if pos.type == mt5.POSITION_TYPE_BUY else "sell",
                                    "volume": pos.volume,
                                    "open_price": pos.price_open,
                                    "current_price": pos.price_current,
                                    "profit": pos.profit,
                                    "sl": pos.sl,
                                    "tp": pos.tp,
                                    "mfe_pct": cur_mfe,
                                    "mae_pct": cur_mae,
                                    "r_multiple": r_multiple
                                })
                        
                        # 准备技术信号摘要
                        technical_signals = {
                            "crt": crt_result,
                            "smc": smc_result['signal'],
                            "grid_strategy": {
                                "signal": grid_signal,
                                "status": grid_status,
                                "config": self.grid_strategy.get_config()
                            },
                            "mtf": mtf_result['signal'], 
                            "ifvg": ifvg_result['signal'],
                            "rvgi_cci": rvgi_cci_result['signal'],
                            "ema_ha": ema_ha_result, # Pass full result including values
                            "performance_stats": trade_stats
                        }
                        
                        # Qwen Sentiment Analysis
                        # [OPTIMIZED] Sentiment is now derived directly from Strategy Logic to ensure consistency
                        qwen_sent_score = 0
                        qwen_sent_label = 'neutral'
                        # Separate call removed to avoid inconsistency with Strategy Content
                        
                        # Call Qwen
                        # Removed DeepSeek structure, pass simplified structure
                        dummy_structure = {"market_state": "Analyzed by Qwen", "preliminary_signal": "neutral"}
                        
                        strategy = self.qwen_client.optimize_strategy_logic(
                            dummy_structure, # Qwen will ignore this or treat as base
                            market_snapshot, 
                            technical_signals=technical_signals, 
                            current_positions=current_positions_list,
                            performance_stats=trade_stats,
                            previous_analysis=self.latest_strategy
                        )
                        self.latest_strategy = strategy
                        self.last_llm_time = time.time()
                        
                        # [NEW] Extract Sentiment from Strategy for Consistency
                        if 'market_analysis' in strategy:
                            ma = strategy['market_analysis']
                            if 'sentiment_analysis' in ma:
                                sa = ma['sentiment_analysis']
                                qwen_sent_label = sa.get('sentiment', 'neutral')
                                qwen_sent_score = sa.get('sentiment_score', 0)
                        
                        # --- [NEW] Update Grid Strategy Dynamic Params (Basket TP & Lock Trigger) ---
                        # Ensure AI Dynamic TP is applied
                        pos_mgmt = strategy.get('position_management', {})
                        if pos_mgmt:
                            raw_basket_tp = pos_mgmt.get('dynamic_basket_tp')
                            
                            # User Requirement: Disable trigger locked entirely
                            lock_trigger = 0.0 
                            # lock_trigger = pos_mgmt.get('lock_profit_trigger')
                            
                            trailing_config = {} # Disable trailing config as well
                            # trailing_config = pos_mgmt.get('trailing_stop_config')
                            
                            # [RESTORED] Smart Basket TP Calculation
                            # Get ATR
                            atr_current = float(latest_features.get('atr', 0))
                            # Get Regime
                            regime_current = adv_result['regime']['regime'] if adv_result and 'regime' in adv_result else 'ranging'
                            
                            smart_basket_tp = self.calculate_smart_basket_tp(
                                raw_basket_tp,
                                atr_current,
                                regime_current,
                                smc_result,
                                current_positions_list,
                                performance_stats=trade_stats
                            )
                            
                            if smart_basket_tp or lock_trigger or trailing_config:
                                try:
                                    self.grid_strategy.update_dynamic_params(
                                        basket_tp=smart_basket_tp, 
                                        lock_trigger=lock_trigger,
                                        trailing_config=trailing_config
                                    )
                                    logger.info(f"Applied AI Dynamic Params: BasketTP={smart_basket_tp:.2f} (LLM:{raw_basket_tp}), LockTrigger={lock_trigger}, Trailing={trailing_config}")
                                except Exception as e:
                                    logger.error(f"Failed to update dynamic params: {e}")

                        # Update lot_size from Qwen Strategy
                        if 'position_size' in strategy:
                            try:
                                qwen_lot = float(strategy['position_size'])
                                if qwen_lot > 0:
                                    self.lot_size = qwen_lot
                                    # Update grid strategy lot size too for consistency
                                    if hasattr(self, 'grid_strategy'):
                                        self.grid_strategy.lot = qwen_lot
                                    logger.info(f"Updated lot size from Qwen: {self.lot_size}")
                            except Exception as e:
                                logger.error(f"Failed to update lot size: {e}")
                        
                        # --- [NEW] Requirement: Update Stop Loss for New Positions immediately ---
                        # "对于一开始开仓设置的止损点夜市要这样" (Initial Stop Loss must also follow this logic)
                        # We extract sl_price from Qwen's decision and apply it if we are opening a trade.
                        # But wait, Qwen returns specific SL price. 
                        # If user wants "Step Stop" logic applied to initial SL?
                        # Step Stop is for PROFIT locking. Initial SL is for loss protection.
                        # Maybe user means: The initial SL should also be "Fixed" and not moved closer unless step logic triggers?
                        # Or user means: The initial SL calculation should be rigorous?
                        # Qwen already provides 'sl_price'. We just ensure it's used.
                        
                        # Logic: When executing BUY/SELL, we use the SL provided by Qwen.
                        # This is handled in `execute_trade`.
                        # However, we must ensure `execute_trade` respects the `exit_conditions` from Qwen.
                        
                        # Let's verify execute_trade uses these.
                        
                        # --- 参数自适应优化 (Feedback Loop) ---
                        param_updates = strategy.get('parameter_updates', {})
                        if param_updates:
                            try:
                                update_reason = param_updates.get('reason', 'AI Optimized')
                                logger.info(f"应用参数优化 ({update_reason}): {param_updates}")
                                
                                # 1. SMC 参数
                                if 'smc_atr_threshold' in param_updates:
                                    self.smc_analyzer.atr_threshold = float(param_updates['smc_atr_threshold'])
                                    
                                # 2. Grid Strategy 参数
                                if 'grid_settings' in param_updates:
                                    self.grid_strategy.update_config(param_updates['grid_settings'])
                                     
                            except Exception as e:
                                logger.error(f"参数动态更新失败: {e}")
                        
                        # Qwen 信号转换
                        qw_action = strategy.get('action', 'neutral').lower()
                        
                        final_signal = "neutral"
                        if qw_action in ['buy', 'add_buy']:
                            final_signal = "buy"
                        elif qw_action in ['sell', 'add_sell']:
                            final_signal = "sell"
                        elif qw_action in ['close_buy', 'close_sell', 'close']:
                            final_signal = "close"
                        elif qw_action == 'hold':
                            final_signal = "hold"
                        elif qw_action in ['grid_start', 'grid_start_long', 'grid_start_short']:
                            final_signal = qw_action
                            
                        # Reason
                        reason = strategy.get('reason', 'Qwen Decision')
                        
                        # --- [NEW] SMC Strict Override (User Requirement) ---
                        # "当市场结构 bos，choch 等 smc 算法市场趋势结构被破坏就严格立刻执行对应方向的交易"
                        if smc_result.get('is_strict_trigger', False):
                            smc_sig = smc_result.get('signal', 'neutral')
                            if smc_sig in ['buy', 'sell']:
                                logger.info(f"!!! SMC STRICT TRIGGER ACTIVATED: {smc_sig.upper()} !!!")
                                logger.info(f"Overriding Qwen Action ({qw_action}) with SMC Signal")
                                
                                final_signal = smc_sig
                                reason = f"[SMC STRICT] {smc_result.get('reason', 'Structure Break')}"
                                
                                # Force Strength to max to ensure execution
                                strength = 95 
                                
                                # Update Strategy Context to reflect this override for logging
                                strategy['action'] = final_signal
                                strategy['reason'] = reason
                        
                        # 3. 智能平仓信号处理
                        if qw_action == 'close' and final_signal != 'close' and not smc_result.get('is_strict_trigger', False):
                            final_signal = 'close'
                            reason = f"[Smart Exit] Qwen Profit Taking: {reason}"

                        qw_signal = final_signal if final_signal not in ['hold', 'close'] else 'neutral'
                        
                        # 计算置信度 (简化版，仅参考 Qwen 和 Tech 一致性)
                        matching_count = 0
                        valid_tech_count = 0
                        tech_signals_list = [
                            crt_result['signal'], adv_signal, smc_result['signal'],
                            mtf_result['signal'], ifvg_result['signal'], rvgi_cci_result['signal']
                        ]
                        
                        for sig in tech_signals_list:
                            if sig != 'neutral':
                                valid_tech_count += 1
                                if sig == final_signal:
                                    matching_count += 1
                        
                        strength = 70 # Base for Qwen
                        if valid_tech_count > 0:
                            strength += (matching_count / valid_tech_count) * 30
                            
                        # 构建所有信号字典
                        all_signals = {
                            "qwen": qw_signal,
                            "crt": crt_result['signal'],
                            "advanced_tech": adv_signal,
                            "smc": smc_result['signal'],
                            "mtf": mtf_result['signal'],
                            "ifvg": ifvg_result['signal'],
                            "rvgi_cci": rvgi_cci_result['signal'],
                            "ema_ha": ema_ha_result['signal']
                        }
                        
                        # Combine Signals (Using HybridOptimizer just for weighting record)
                        _, _, weights = self.optimizer.combine_signals(all_signals)

                        logger.info(f"AI 最终决定 (Qwen): {final_signal.upper()} (强度: {strength:.1f})")
                        logger.info(f"Reason: {reason}")
                        
                        # 保存分析结果到DB
                        self.db_manager.save_signal(self.symbol, self.tf_name, {
                            "final_signal": final_signal,
                            "strength": strength,
                            "details": {
                                "source": "Qwen_Solo",
                                "reason": reason,
                                "weights": weights,
                                "signals": all_signals,
                                "market_state": strategy.get('market_state', 'N/A'),
                                "crt_reason": crt_result['reason'],
                                "mtf_reason": mtf_result['reason'],
                                "smc_structure": smc_result['structure'],
                                "ifvg_reason": ", ".join(ifvg_result['reasons']) if ifvg_result['reasons'] else "N/A"
                            }
                        })

                        # [NEW] Sync Signal to Master DB
                        self.master_db_manager.save_signal(self.symbol, self.tf_name, {
                            "final_signal": final_signal,
                            "strength": strength,
                            "details": {
                                "source": "Qwen_Solo",
                                "reason": reason,
                                "weights": weights,
                                "signals": all_signals,
                                "market_state": strategy.get('market_state', 'N/A'),
                                "crt_reason": crt_result['reason'],
                                "mtf_reason": mtf_result['reason'],
                                "smc_structure": smc_result['structure'],
                                "ifvg_reason": ", ".join(ifvg_result['reasons']) if ifvg_result['reasons'] else "N/A"
                            }
                        })
                        
                        self.latest_strategy = strategy
                        self.latest_signal = final_signal
                        
                        # --- 发送分析报告到 Telegram ---
                        # (保持原有的 Telegram 逻辑，简化 DeepSeek 部分)
                        
                        # 获取当前持仓概览
                        pos_summary = "No Open Positions"
                        if current_positions_list:
                            pos_details = []
                            for p in current_positions_list:
                                type_str = "BUY" if p['type'] == 'buy' else "SELL"
                                pnl = p['profit']
                                pos_details.append(f"{type_str} {p['volume']} (PnL: {pnl:.2f})")
                            pos_summary = "\n".join(pos_details)

                        # SL/TP
                        exit_conds = strategy.get('exit_conditions', {})
                        opt_sl = exit_conds.get('sl_price')
                        opt_tp = exit_conds.get('tp_price')
                        
                        # Fallback calc
                        if not opt_sl or not opt_tp:
                            current_bid = mt5.symbol_info_tick(self.symbol).bid
                            current_ask = mt5.symbol_info_tick(self.symbol).ask
                            ref_price = current_ask if final_signal == 'buy' else current_bid
                            atr_val = float(latest_features.get('atr', ref_price * 0.005))
                            calc_sl, calc_tp = self.calculate_optimized_sl_tp(
                                final_signal if final_signal in ['buy', 'sell'] else 'buy', 
                                ref_price, 
                                atr_val,
                                ai_exit_conds=exit_conds
                            )
                            if not opt_sl: opt_sl = calc_sl
                            if not opt_tp: opt_tp = calc_tp

                        # 构建消息
                        telegram_report = strategy.get('telegram_report', '')
                        
                        # 获取当前使用的大模型名称 (从 QwenClient 配置中获取)
                        current_model_name = "Unknown Model"
                        try:
                            # 通过 qwen_client 内部逻辑获取当前品种的配置
                            # 这里我们需要访问私有方法 _get_config，或者假设 qwen_client 有公开接口
                            # 由于 Python 没有严格私有，我们可以尝试调用 _get_config
                            config = self.qwen_client._get_config(self.symbol)
                            current_model_name = config.get("model", "Default")
                        except Exception:
                            current_model_name = self.qwen_client.model # Fallback to default

                        if telegram_report and len(telegram_report) > 50:
                            # 使用 Qwen 生成的专用 Telegram 报告
                            analysis_msg = (
                                f"🤖 *AI Strategy Report ({current_model_name})*\n"
                                f"Symbol: `{self.symbol}` | TF: `{self.tf_name}`\n"
                                f"Time: {datetime.now().strftime('%H:%M:%S')}\n\n"
                                f"{telegram_report}\n\n"
                                f"📊 *Live Status*\n"
                        f"• Action: *{strategy.get('action', final_signal).upper()}*\n"
                        f"• Lots: `{self.lot_size if self.lot_size else strategy.get('position_size', 0.01)}`\n"
                        f"• Strength: {strength:.0f}%\n"
                        f"• Sentiment: {qwen_sent_label.upper()} ({qwen_sent_score:.2f})\n\n"
                        f"💼 *Positions*\n"
                                f"{self.escape_markdown(pos_summary)}"
                            )
                        else:
                            # 备用：手动构建结构化消息
                            analysis_msg = (
                                f"🤖 *AI Strategy Report ({current_model_name})*\n"
                                f"Symbol: `{self.symbol}` | TF: `{self.tf_name}`\n"
                                f"Time: {datetime.now().strftime('%H:%M:%S')}\n\n"
                                
                                f"🧙‍♂️ *Qwen Analysis*\n"
                        f"• Action: *{qw_action.upper()}*\n"
                        f"• Lots: `{self.lot_size if self.lot_size else strategy.get('position_size', 0.01)}` (Dynamic)\n"
                        f"• Sentiment: {qwen_sent_label.upper()} ({qwen_sent_score})\n"
                        f"• Logic: _{self.escape_markdown(reason)}_\n\n"
                                
                                f"🏆 *Decision: {final_signal.upper()}*\n"
                                f"• Strength: {strength:.0f}%\n"
                                f"• SL: `{opt_sl:.2f}` | TP: `{opt_tp:.2f}`\n\n"
                                
                                f"💼 *Positions*\n"
                                f"{self.escape_markdown(pos_summary)}"
                            )
                        self.send_telegram_message(analysis_msg)

                        # 4. 执行交易
                        if final_signal != 'hold':
                            logger.info(f">>> 执行 Qwen 决策: {final_signal.upper()} <<<")
                            
                            # 传入 Qwen 参数
                            entry_params = strategy.get('entry_conditions')
                            exit_params = strategy.get('exit_conditions')
                            
                            # Calculate Lot (Martingale aware if needed, or handled in execute_trade)
                            # Here we use calculate_dynamic_lot for initial lot
                            suggested_lot = self.calculate_dynamic_lot(
                                strength, 
                                market_context={'smc': smc_result}, 
                                ai_signals=all_signals
                            )
                            
                            self.execute_trade(
                                final_signal, 
                                strength, 
                                exit_params,
                                entry_params,
                                suggested_lot=suggested_lot
                            )
                
                # Check Grid TP / Lock (Moved from start)
                should_close_long, should_close_short = self.grid_strategy.check_basket_tp(positions, current_atr=current_atr)
                
                if should_close_long or should_close_short:
                    logger.info(f"Grid Strategy triggered Basket TP/Lock! (Long:{should_close_long}, Short:{should_close_short}) Closing positions...")
                    
                    to_close = []
                    if should_close_long:
                        to_close.extend([p for p in positions if p.type == mt5.POSITION_TYPE_BUY])
                    if should_close_short:
                        to_close.extend([p for p in positions if p.type == mt5.POSITION_TYPE_SELL])
                    
                    if to_close:
                        self.close_all_positions(to_close, reason="Grid Basket TP/Lock")
                    return

        except KeyboardInterrupt:
            logger.info("用户停止机器人")
            mt5.shutdown()
        except Exception as e:
            logger.error(f"发生未捕获异常: {e}", exc_info=True)
            mt5.shutdown()

class MultiSymbolBot:
    def __init__(self, symbols, timeframe=mt5.TIMEFRAME_M6):
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
            
    # User Requirement: Change Timeframe back to 6 Minutes
    bot = MultiSymbolBot(symbols=symbols, timeframe=mt5.TIMEFRAME_M6)
    bot.start(account_index=args.account)