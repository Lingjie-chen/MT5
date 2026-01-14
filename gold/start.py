import time
import sys
import os
import logging
import threading
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import requests
from dotenv import load_dotenv
from file_watcher import FileWatcher

# Try importing MetaTrader5
try:
    import MetaTrader5 as mt5
except ImportError:
    print("Error: MetaTrader5 module not found.")
    sys.exit(1)

# Determine log filename based on arguments to allow parallel execution
log_filename = 'windows_bot.log'
if len(sys.argv) > 1:
    # Sanitize argument to create a safe filename
    # e.g. "ETHUSD" -> "windows_bot_ETHUSD.log"
    # e.g. "GOLD,ETHUSD" -> "windows_bot_GOLD_ETHUSD.log"
    arg_clean = sys.argv[1].replace(',', '_').replace(' ', '').upper()
    log_filename = f'windows_bot_{arg_clean}.log'

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("WindowsBot")

# Load Environment Variables
load_dotenv()

# Add current directory to sys.path to ensure local imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import Local Modules
try:
    from .ai_client_factory import AIClientFactory
    from .mt5_data_processor import MT5DataProcessor
    from .database_manager import DatabaseManager
    from .optimization import WOAm, TETA
    from .advanced_analysis import (
        AdvancedMarketAnalysis, AdvancedMarketAnalysisAdapter, SMCAnalyzer, 
        CRTAnalyzer, MTFAnalyzer
    )
    from .grid_strategy import KalmanGridStrategy
except ImportError:
    # Fallback for direct script execution
    try:
        from ai_client_factory import AIClientFactory
        from mt5_data_processor import MT5DataProcessor
        from database_manager import DatabaseManager
        from optimization import WOAm, TETA
        from advanced_analysis import (
            AdvancedMarketAnalysis, AdvancedMarketAnalysisAdapter, SMCAnalyzer, 
            CRTAnalyzer, MTFAnalyzer
        )
        from grid_strategy import KalmanGridStrategy
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
            "obv": 0.6 # type: ignore
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
    def __init__(self, symbol="GOLD", timeframe=mt5.TIMEFRAME_M15):
        self.symbol = symbol
        self.timeframe = timeframe
        self.tf_name = "M15"
        if timeframe == mt5.TIMEFRAME_M15: self.tf_name = "M15"
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
        self.ai_factory = AIClientFactory()
        
        # Only Qwen as Sole Decision Maker
        self.qwen_client = self.ai_factory.create_client("qwen")
        
        # Advanced Models: SMC, CRT, CCI (via Adapter)
        # MTF kept for context structure
        self.crt_analyzer = CRTAnalyzer(timeframe_htf=mt5.TIMEFRAME_H1)
        self.mtf_analyzer = MTFAnalyzer(htf1=mt5.TIMEFRAME_H1, htf2=mt5.TIMEFRAME_H4) 
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
        self.last_atr = 0.0 # Initialize ATR
        
        self.latest_strategy = None
        self.latest_signal = "neutral"
        
        # Optimizers: WOAm and TETA only
        self.optimizers = {
            "WOAm": WOAm(),
            "TETA": TETA()
        }
        self.active_optimizer_name = "WOAm"

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
        rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, num_candles)
        
        if rates is None or len(rates) == 0:
            logger.error("无法获取 K 线数据")
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
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"平仓失败 #{position.ticket}: {result.comment}")
            return False
        else:
            logger.info(f"平仓成功 #{position.ticket}")
            
            # Calculate total profit for this position
            total_profit = 0.0
            total_swap = 0.0
            total_commission = 0.0
            net_profit = 0.0
            
            try:
                # Short delay to ensure history is updated
                time.sleep(0.5)
                # Get all deals associated with this position
                deals = mt5.history_deals_get(position=position.ticket)
                
                if deals:
                    for deal in deals:
                        total_profit += deal.profit
                        total_swap += deal.swap
                        total_commission += deal.commission
                    net_profit = total_profit + total_swap + total_commission
                else:
                    # Fallback to result profit if history not available
                    net_profit = getattr(result, 'profit', 0.0)
                    total_profit = net_profit
                    
            except Exception as e:
                logger.error(f"获取平仓盈亏失败: {e}")
                net_profit = getattr(result, 'profit', 0.0)

            # Construct detailed message
            msg = f"🔄 *Position Closed*\n"
            msg += f"Ticket: `{position.ticket}`\n"
            msg += f"Reason: {comment}\n"
            msg += f"Profit: `{total_profit:.2f}`\n"
            msg += f"Swap: `{total_swap:.2f}`\n"
            msg += f"Comm: `{total_commission:.2f}`\n"
            msg += f"💰 *Net PnL: {net_profit:.2f}*"

            self.send_telegram_message(msg)
            return True

    def check_risk_reward_ratio(self, entry_price, sl_price, tp_price):
        """检查盈亏比是否达标"""
        if sl_price <= 0 or tp_price <= 0:
            return False, 0.0
            
        risk = abs(entry_price - sl_price)
        reward = abs(tp_price - entry_price)
        
        if risk == 0:
            return False, 0.0
            
        rr_ratio = reward / risk
        # 硬性要求: 盈亏比必须 >= 1.5
        if rr_ratio < 1.5:
            logger.warning(f"盈亏比过低 ({rr_ratio:.2f} < 1.5), 拒绝交易. Risk={risk:.2f}, Reward={reward:.2f}")
            return False, rr_ratio
            
        return True, rr_ratio

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
            
            # 安全检查：如果可用保证金不足，直接返回最小手数或0
            if margin_free < 100: # 至少保留 100 资金缓冲
                logger.warning(f"可用保证金不足 ({margin_free:.2f})，强制最小手数")
                return mt5.symbol_info(self.symbol).volume_min

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
            # 简单规则：任何单一品种的预估保证金占用不应超过剩余自由保证金的 50%
            max_allowed_risk_amount = margin_free * 0.5 
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
             # Ensure entry_params is available if not passed
             if entry_params is None:
                 entry_params = self.latest_strategy.get('entry_conditions', {})
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
                    self.close_position(pos, comment=f"AI: {close_reason}")
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
            elif llm_action in ['buy', 'sell']:
        # 检查是否是反向开仓（需要先平仓后开仓）
        # 这个逻辑已经在之前的持仓管理部分处理过了
        # 所以这里应该允许开仓
              logger.info(f"已有持仓，但执行反向开仓逻辑")
        # 继续执行，上面的持仓管理逻辑会处理平仓
            elif 'add' not in llm_action and llm_action != 'grid_start':
              logger.info(f"已有持仓 ({len(bot_positions)}), 且非加仓指令 ({llm_action}), 跳过开仓")
              return
        # 执行开仓/挂单
        trade_type = None
        price = 0.0
        
        # Mapping 'add_buy'/'add_sell' to normal buy/sell if no position exists
        # This handles cases where LLM says "add" but position was closed or didn't exist
        
        if llm_action in ['buy', 'add_buy']:
            trade_type = "buy"
            price = tick.ask
        elif llm_action in ['sell', 'add_sell']:
            trade_type = "sell"
            price = tick.bid
        elif llm_action in ['limit_buy', 'buy_limit', 'stop_buy', 'buy_stop']:
            # 检查现有 Limit 挂单
            current_orders = mt5.orders_get(symbol=self.symbol)
            if current_orders:
                for o in current_orders:
                    if o.magic == self.magic_number:
                        # 如果是 Sell Limit/Stop (反向)，则取消
                        # 增强逻辑: 对于 GOLD, ETHUSD, EURUSD 等品种，严格执行反向单清除
                        if o.type in [mt5.ORDER_TYPE_SELL_LIMIT, mt5.ORDER_TYPE_SELL_STOP]:
                             logger.info(f"[{self.symbol}] 发现反向卖出挂单 #{o.ticket} (Type: {o.type})，执行取消以配合新买入策略")
                             req = {"action": mt5.TRADE_ACTION_REMOVE, "order": o.ticket}
                             mt5.order_send(req)

            # 优先使用 limit_price (与 prompt 一致)，回退使用 entry_price
            price = entry_params.get('limit_price', entry_params.get('entry_price', 0.0)) if entry_params else 0.0
            
            # 增强：如果价格无效，尝试自动修复
            if price <= 0:
                # 使用 self.last_atr 作为回退
                atr = self.last_atr if self.last_atr > 0 else (tick.ask * 0.005)
                logger.warning(f"LLM 建议 Limit Buy 但未提供价格，尝试使用 ATR ({atr:.4f}) 自动计算")
                
                if atr > 0:
                    price = tick.ask - (atr * 0.5) # 默认在当前价格下方 0.5 ATR 处挂单
                    logger.info(f"自动设定 Limit Buy 价格: {price:.2f} (Ask: {tick.ask})")
            
            # 智能判断 Limit vs Stop
            if price > 0:
                # 检查最小间距 (Stops Level)
                symbol_info = mt5.symbol_info(self.symbol)
                stop_level = symbol_info.trade_stops_level * symbol_info.point if symbol_info else 0
                price = self._normalize_price(price)
                
                if price > tick.ask:
                    trade_type = "stop_buy" # 价格高于当前价 -> 突破买入
                    # Buy Stop must be >= Ask + StopLevel
                    min_price = tick.ask + stop_level
                    if price < min_price:
                        logger.warning(f"Stop Buy Price {price} too close to Ask {tick.ask}, adjusting to {min_price}")
                        price = self._normalize_price(min_price)
                else:
                    trade_type = "limit_buy" # 价格低于当前价 -> 回调买入
                    # Buy Limit must be <= Ask - StopLevel
                    max_price = tick.ask - stop_level
                    if price > max_price:
                         logger.warning(f"Limit Buy Price {price} too close to Ask {tick.ask}, adjusting to {max_price}")
                         price = self._normalize_price(max_price)
            else:
                logger.error("Limit Buy 失败: 无法确定价格")
                
        elif llm_action in ['limit_sell', 'sell_limit', 'stop_sell', 'sell_stop']:
            # 检查现有 Limit 挂单
            current_orders = mt5.orders_get(symbol=self.symbol)
            if current_orders:
                for o in current_orders:
                    if o.magic == self.magic_number:
                        # 如果是 Buy Limit/Stop (反向)，则取消
                        # 增强逻辑: 对于 GOLD, ETHUSD, EURUSD 等品种，严格执行反向单清除
                        if o.type in [mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_BUY_STOP]:
                             logger.info(f"[{self.symbol}] 发现反向买入挂单 #{o.ticket} (Type: {o.type})，执行取消以配合新卖出策略")
                             req = {"action": mt5.TRADE_ACTION_REMOVE, "order": o.ticket}
                             mt5.order_send(req)
                        # 如果是同向 (Sell Limit/Stop)，则保留 (叠加)

            price = entry_params.get('limit_price', entry_params.get('entry_price', 0.0)) if entry_params else 0.0
            
            # 增强：如果价格无效，尝试自动修复
            if price <= 0:
                logger.warning(f"LLM 建议 Limit Sell 但未提供价格，尝试使用 ATR 自动计算")
                # 获取 ATR
                rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, 20)
                if rates is not None and len(rates) > 14:
                     df_temp = pd.DataFrame(rates)
                     high_low = df_temp['high'] - df_temp['low']
                     atr = high_low.rolling(14).mean().iloc[-1]
                     if atr > 0:
                        price = tick.bid + (atr * 0.5) # 默认在当前价格上方 0.5 ATR 处挂单
                        logger.info(f"自动设定 Limit Sell 价格: {price:.2f} (Bid: {tick.bid}, ATR: {atr:.4f})")
            
            # 智能判断 Limit vs Stop
            if price > 0:
                # 检查最小间距 (Stops Level)
                symbol_info = mt5.symbol_info(self.symbol)
                stop_level = symbol_info.trade_stops_level * symbol_info.point if symbol_info else 0
                price = self._normalize_price(price)

                if price < tick.bid:
                    trade_type = "stop_sell" # 价格低于当前价 -> 突破卖出
                    # Sell Stop must be <= Bid - StopLevel
                    max_price = tick.bid - stop_level
                    if price > max_price:
                        logger.warning(f"Stop Sell Price {price} too close to Bid {tick.bid}, adjusting to {max_price}")
                        price = self._normalize_price(max_price)
                else:
                    trade_type = "limit_sell" # 价格高于当前价 -> 反弹卖出
                    # Sell Limit must be >= Bid + StopLevel
                    min_price = tick.bid + stop_level
                    if price < min_price:
                        logger.warning(f"Limit Sell Price {price} too close to Bid {tick.bid}, adjusting to {min_price}")
                        price = self._normalize_price(min_price)








            # 3. 生成网格计划
            # 使用当前价格作为基准
            current_price = tick.ask if direction == 'bullish' else tick.bid
            
            # 获取 Point
            symbol_info = mt5.symbol_info(self.symbol)
            point = symbol_info.point if symbol_info else 0.01
            
            # 提取 LLM 建议的动态网格间距 (Pips) 和 动态TP配置
            dynamic_step = None
            grid_level_tps = None
            grid_levels_config = None 
            
            if self.latest_strategy:
                pos_mgmt = self.latest_strategy.get('position_management', {})
                if pos_mgmt:
                    dynamic_step = float(pos_mgmt.get('recommended_grid_step_pips', 0))
                    grid_level_tps = pos_mgmt.get('grid_level_tp_pips')
                    basket_tp = pos_mgmt.get('dynamic_basket_tp')
                    
                    logger.info(f"🤖 AI 网格配置解析:\n"
                                f"- 动态步长: {dynamic_step} pips\n"
                                f"- 动态 Basket TP: ${basket_tp}\n"
                                f"- 分层止盈配置: {grid_level_tps}")
                    
                    grid_params = pos_mgmt.get('grid_params', {})
                    if grid_params and 'grid_levels' in grid_params:
                        grid_levels_config = grid_params['grid_levels']
                        logger.info(f"Using Explicit Grid Levels from LLM (Count: {len(grid_levels_config)})")
                    elif 'grid_levels' in pos_mgmt:
                        grid_levels_config = pos_mgmt['grid_levels']
                        logger.info(f"Using Explicit Grid Levels from LLM (Count: {len(grid_levels_config)})")

            
            # Use explicit grid levels if available, otherwise fallback to auto-generation
            if grid_levels_config:
                grid_orders = []
                for lvl in grid_levels_config:
                    try:
                        # Determine Order Type based on Level vs Current Price
                        l_price = float(lvl['level'])
                        l_vol = float(lvl.get('volume', lvl.get('size', self.lot_size)))
                        l_tp = float(lvl.get('tp', 0.0))
                        l_sl = float(lvl.get('sl', 0.0))
                        
                        o_type = None
                        if direction == 'bullish':
                            if l_price < tick.ask: o_type = mt5.ORDER_TYPE_BUY_LIMIT
                            elif l_price > tick.ask: o_type = mt5.ORDER_TYPE_BUY_STOP
                        else: # bearish
                            if l_price > tick.bid: o_type = mt5.ORDER_TYPE_SELL_LIMIT
                            elif l_price < tick.bid: o_type = mt5.ORDER_TYPE_SELL_STOP
                            
                        if o_type is not None:
                            grid_orders.append({
                                'type': o_type,
                                'price': l_price,
                                'volume': l_vol, 
                                'tp': l_tp,
                                'sl': l_sl
                            })
                    except Exception as e:
                        logger.error(f"Error parsing grid level {lvl}: {e}")
            else:
                # Fallback to standard algorithmic generation
                grid_orders = self.grid_strategy.generate_grid_plan(current_price, direction, atr, point=point, dynamic_step_pips=dynamic_step, grid_level_tps=grid_level_tps)
            
            # 4. 执行挂单
            if grid_orders:
                logger.info(f"网格计划生成 {len(grid_orders)} 个挂单")
                
                # 计算一个基础手数
                base_lot = self.lot_size
                if suggested_lot and suggested_lot > 0:
                    base_lot = suggested_lot
                
                for i, order in enumerate(grid_orders):
                    o_type = order['type']
                    o_price = self._normalize_price(order['price'])
                    o_tp = self._normalize_price(order.get('tp', 0.0))
                    o_sl = self._normalize_price(order.get('sl', 0.0))
                    
                    vol_to_use = order.get('volume', base_lot)
                    
                    # 发送订单
                    self._send_order(o_type, o_price, sl=o_sl, tp=o_tp, volume=vol_to_use, comment=f"AI-Grid-{i+1}")
                    
                logger.info("网格部署完成")
                return 
            else:
                logger.warning("网格计划为空，未执行任何操作")
                return

        if trade_type and price > 0:
            # 再次确认 SL/TP 是否存在
            if explicit_sl is None or explicit_tp is None:
                # 策略优化: 如果 LLM 未提供明确价格，则使用基于 MFE/MAE 的统计优化值
                # 移除旧的 ATR 动态计算，确保策略的一致性和基于绩效的优化
                logger.info("LLM 未提供明确 SL/TP，使用 MFE/MAE 统计优化值")
                
                # 计算 ATR
                rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, 20)
                atr = 0.0
                if rates is not None and len(rates) > 14:
                     df_temp = pd.DataFrame(rates)
                     high_low = df_temp['high'] - df_temp['low']
                     atr = high_low.rolling(14).mean().iloc[-1]
                
                explicit_sl, explicit_tp = self.calculate_optimized_sl_tp(trade_type, price, atr, ai_exit_conds=sl_tp_params)
                
                if explicit_sl == 0 or explicit_tp == 0:
                     logger.error("无法计算优化 SL/TP，放弃交易")
                     return 

            # 再次确认 R:R (针对 Limit 单的最终确认)
            if 'limit' in trade_type or 'stop' in trade_type:
                 valid, rr = self.check_risk_reward_ratio(price, explicit_sl, explicit_tp)
                 if not valid:
                     logger.warning(f"Limit单最终 R:R 检查未通过: {rr:.2f}")
                     return

            # FIX: Ensure 'action' is defined for the comment
            # action variable was used in _send_order's comment but was coming from llm_action
            action_str = llm_action.upper() if llm_action else "UNKNOWN"
            comment = f"AI-{action_str}"
            
            # --- 动态仓位计算 ---
            if suggested_lot and suggested_lot > 0:
                optimized_lot = suggested_lot
                logger.info(f"使用预计算的建议手数: {optimized_lot}")
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
            
            self._send_order(trade_type, price, explicit_sl, explicit_tp, comment=comment)
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
        
        digits = symbol_info.digits
        return round(price, digits)

    def _send_order(self, type_str, price, sl=0.0, tp=0.0, volume=None, comment=""):
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
        
        # Calculate dynamic spread
        tick = mt5.symbol_info_tick(self.symbol)
        spread = (tick.ask - tick.bid) if tick else (symbol_info.spread * point)
        
        # Base stops level required by broker
        base_stops_level = symbol_info.trade_stops_level * point
        
        # SL requires Spread buffer because it triggers on the other side of execution price
        # (Buy executes at Ask, SL triggers at Bid; Sell executes at Bid, SL triggers at Ask)
        sl_min_dist = base_stops_level + spread + (20 * point)
        
        # TP triggers on the same side as execution price (usually), so Spread is strictly not required,
        # but a small safety buffer (20 points) is good.
        tp_min_dist = base_stops_level + (20 * point)
        
        is_buy = "buy" in str(type_str).lower()
        is_sell = "sell" in str(type_str).lower()
        
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
        if sl > 0:
            dist = abs(price - sl)
            if dist < sl_min_dist:
                logger.warning(f"SL too close (Dist {dist:.5f} < Level {sl_min_dist:.5f}). Adjusting.")
                if is_buy: 
                    sl = price - sl_min_dist
                else: 
                    sl = price + sl_min_dist
                sl = self._normalize_price(sl)
                
        if tp > 0:
            dist = abs(price - tp)
            if dist < tp_min_dist:
                logger.warning(f"TP too close (Dist {dist:.5f} < Level {tp_min_dist:.5f}). Adjusting.")
                if is_buy: 
                    tp = price + tp_min_dist
                else: 
                    tp = price - tp_min_dist
                tp = self._normalize_price(tp)
        
        # ----------------------------------------
        
        order_type = mt5.ORDER_TYPE_BUY
        action = mt5.TRADE_ACTION_DEAL
        
        # Use provided volume or default self.lot_size
        lot_to_use = float(volume) if volume is not None and volume > 0 else self.lot_size

        if isinstance(type_str, int):
            order_type = type_str
            # Infer action from type
            if order_type in [mt5.ORDER_TYPE_BUY, mt5.ORDER_TYPE_SELL]:
                action = mt5.TRADE_ACTION_DEAL
            else:
                action = mt5.TRADE_ACTION_PENDING
            # Back-map to string for logging if needed, or just use generic
            type_str = "int_type"
        else:
            type_str = type_str.lower()
            if type_str == "buy":
                order_type = mt5.ORDER_TYPE_BUY
                action = mt5.TRADE_ACTION_DEAL
            elif type_str == "sell":
                order_type = mt5.ORDER_TYPE_SELL
                action = mt5.TRADE_ACTION_DEAL
            elif type_str in ["limit_buy", "buy_limit"]:
                order_type = mt5.ORDER_TYPE_BUY_LIMIT
                action = mt5.TRADE_ACTION_PENDING
            elif type_str in ["limit_sell", "sell_limit"]:
                order_type = mt5.ORDER_TYPE_SELL_LIMIT
                action = mt5.TRADE_ACTION_PENDING
            elif type_str in ["stop_buy", "buy_stop"]:
                order_type = mt5.ORDER_TYPE_BUY_STOP
                action = mt5.TRADE_ACTION_PENDING
            elif type_str in ["stop_sell", "sell_stop"]:
                order_type = mt5.ORDER_TYPE_SELL_STOP
                action = mt5.TRADE_ACTION_PENDING
            
        request = {
            "action": action,
            "symbol": self.symbol,
            "volume": lot_to_use,
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

        # --- 资金检查 (防止 No Money Error) ---
        try:
            # 先使用 order_check 快速验证
            check_res = mt5.order_check(request)
            if check_res and check_res.retcode == mt5.TRADE_RETCODE_NO_MONEY:
                logger.warning(f"预检查失败: 资金不足 (Req: {lot_to_use} lots). 尝试自动调整手数...")
                
                account_info = mt5.account_info()
                if account_info and symbol_info:
                    # 计算当前手数所需保证金
                    margin_needed = mt5.order_calc_margin(order_type, self.symbol, lot_to_use, price)
                    
                    if margin_needed and margin_needed > 0:
                        free_margin = account_info.margin_free
                        logger.info(f"当前可用保证金: {free_margin:.2f}, 所需: {margin_needed:.2f}")
                        
                        if free_margin < margin_needed:
                            # 按比例缩减，保留 5% 缓冲
                            ratio = free_margin / margin_needed
                            new_vol = lot_to_use * ratio * 0.95
                            
                            # 对齐到步长
                            step = symbol_info.volume_step
                            if step > 0:
                                new_vol = (new_vol // step) * step
                                new_vol = round(new_vol, 2)
                            
                            if new_vol >= symbol_info.volume_min:
                                logger.info(f"自动调整手数: {lot_to_use} -> {new_vol}")
                                lot_to_use = new_vol
                                request['volume'] = lot_to_use
                            else:
                                logger.error(f"可用资金不足以开启最小手数 {symbol_info.volume_min}")
                                return
                    else:
                        logger.warning("无法计算所需保证金，跳过调整")
        except Exception as e:
            logger.error(f"资金检查时发生异常: {e}")
        
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
                logger.info(f"发送订单请求: Action={action}, Type={order_type}, Volume={lot_to_use}, Price={price:.2f}, SL={sl:.2f}, TP={tp:.2f}, Filling={mode}")
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
            "http": "http://127.0.0.1:7897",
            "https": "http://127.0.0.1:7897"
        }
        
        try:
            import requests
            response = None
            try:
                # 尝试通过代理发送
                response = requests.post(url, json=data, timeout=10, proxies=proxies)
            except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError):
                # 如果代理失败，尝试直连 (虽然可能也会被墙)
                logger.warning("代理连接失败，尝试直连 Telegram...")
                response = requests.post(url, json=data, timeout=10)
                
            if response.status_code != 200:
                logger.error(f"Telegram 发送失败 (Markdown): {response.text}")
                
                # 自动降级重试：如果是因为 Markdown 解析失败，移除格式后重发
                if "can't parse entities" in response.text:
                    logger.warning("检测到 Markdown 语法错误，尝试以纯文本发送...")
                    if "parse_mode" in data:
                        del data["parse_mode"]
                    
                    try:
                        response = requests.post(url, json=data, timeout=10, proxies=proxies)
                    except:
                        response = requests.post(url, json=data, timeout=10)
                        
                    if response.status_code == 200:
                        logger.info("纯文本消息发送成功")
                    else:
                        logger.error(f"Telegram 纯文本发送也失败: {response.text}")

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

        # 获取 ATR 用于计算移动止损距离 (动态调整)
        rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, 20)
        atr = 0.0
        if rates is not None and len(rates) > 14:
            df_temp = pd.DataFrame(rates)
            high_low = df_temp['high'] - df_temp['low']
            atr = high_low.rolling(14).mean().iloc[-1]
            
        if atr <= 0:
            return # 无法计算 ATR，跳过

        # --- Grid Strategy Logic ---
        # 1. Check Basket TP
        if self.grid_strategy.check_basket_tp(positions):
            logger.info("Grid Strategy: Basket TP Reached. Closing ALL positions.")
            for pos in positions:
                if pos.magic == self.magic_number:
                    self.close_position(pos, comment="Grid Basket TP")
            return

        # 2. Check Grid Add (Only if allowed by LLM)
        # 增加 LLM 权限控制: 默认允许，但如果 LLM 明确禁止 (allow_grid=False)，则暂停加仓
        allow_grid = True
        if self.latest_strategy and isinstance(self.latest_strategy, dict):
            # 检查是否有 'grid_settings' 且其中有 'allow_add'
            grid_settings = self.latest_strategy.get('parameter_updates', {}).get('grid_settings', {})
            if 'allow_add' in grid_settings:
                allow_grid = bool(grid_settings['allow_add'])
        
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
                if self.latest_strategy:
                     pos_mgmt = self.latest_strategy.get('position_management', {})
                     grid_tps = pos_mgmt.get('grid_level_tp_pips')
                     if grid_tps:
                         # Determine level index
                         current_count = self.grid_strategy.long_pos_count if trade_type == 'buy' else self.grid_strategy.short_pos_count
                         # Use specific TP if available
                         tp_pips = grid_tps[current_count] if current_count < len(grid_tps) else grid_tps[-1]
                         
                         point = mt5.symbol_info(self.symbol).point
                         if trade_type == 'buy':
                             add_tp = price + (tp_pips * 10 * point)
                         else:
                             add_tp = price - (tp_pips * 10 * point)
                         
                         logger.info(f"Dynamic Add TP: {add_tp} ({tp_pips} pips)")
                
                # Fallback if no TP from LLM
                if add_tp == 0.0 and atr > 0:
                    # Fallback: ATR * 3.0 (Wider for grid)
                    fallback_dist = atr * 3.0
                    if trade_type == 'buy': add_tp = price + fallback_dist
                    else: add_tp = price - fallback_dist
                    add_tp = self._normalize_price(add_tp)
                    logger.info(f"Dynamic Add TP (Fallback ATR): {add_tp:.2f} (ATR={atr:.2f})")

                self._send_order(trade_type, price, 0.0, add_tp, comment=f"Grid: {action}")
                # Don't return, allow SL/TP update for existing positions

        trailing_dist = atr * 1.5 # 默认移动止损距离
        
        # 如果有策略参数，尝试解析最新的 SL/TP 设置
        new_sl_multiplier = 1.5
        new_tp_multiplier = 2.5
        has_new_params = False
        
        if strategy_params:
            exit_cond = strategy_params.get('exit_conditions')
            if exit_cond:
                new_sl_multiplier = exit_cond.get('sl_atr_multiplier', 1.5)
                new_tp_multiplier = exit_cond.get('tp_atr_multiplier', 2.5)
                has_new_params = True

        symbol_info = mt5.symbol_info(self.symbol)
        if not symbol_info:
            return
        point = symbol_info.point
        stop_level_dist = symbol_info.trade_stops_level * point

        # 遍历所有持仓，独立管理
        for pos in positions:
            if pos.magic != self.magic_number:
                continue
                
            symbol = pos.symbol
            type_pos = pos.type # 0: Buy, 1: Sell
            price_open = pos.price_open
            sl = pos.sl
            tp = pos.tp
            current_price = pos.price_current
            
            # 针对每个订单独立计算最优 SL/TP
            # 如果是挂单成交后的新持仓，或者老持仓，都统一处理
            
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": symbol,
                "position": pos.ticket,
                "sl": sl,
                "tp": tp
            }
            
            changed = False
            
            # --- 1. 基于最新策略更新 SL/TP (全量覆盖更新) ---
            # 策略调整: 恢复 AI 驱动的持仓参数更新逻辑
            # 但不使用机械式的 Trailing Stop，而是依赖 LLM 的 MFE/MAE 分析给出的新点位
            
            # [Manual Override Protection]
            # 检查用户是否手动修改了 SL/TP
            # 我们假设机器人上次设置的 SL/TP 应该与当前持仓的一致
            # 如果差异很大且不是 0，说明用户手动干预了
            # 为了简化，我们设定规则: 只有当 AI 建议的新 SL/TP 明显优于当前设置，或者当前设置明显偏离风险控制时才强制更新
            
            allow_update = True # Enabled per User Request (Dynamic AI Update)
            
            if allow_update and has_new_params:
                # 使用 calculate_optimized_sl_tp 进行统一计算和验证
                ai_exits = strategy_params.get('exit_conditions', {})
                
                # Check if Qwen provided explicit SL/TP
                sl_val = ai_exits.get('sl_price')
                tp_val = ai_exits.get('tp_price')
                
                qwen_sl_provided = sl_val is not None and float(sl_val) > 0
                qwen_tp_provided = tp_val is not None and float(tp_val) > 0
                
                # If Qwen didn't provide explicit values, skip dynamic update (User Request)
                if not qwen_sl_provided and not qwen_tp_provided:
                    logger.info("Qwen 未提供明确 SL/TP，跳过动态更新 (防止自动移动)")
                else:
                    trade_dir = 'buy' if type_pos == mt5.POSITION_TYPE_BUY else 'sell'
                    
                    # --- NEW LOGIC: Use Qwen's Analysis Directly ---
                    # Instead of calculating based on ATR multipliers inside calculate_optimized_sl_tp,
                    # we trust the explicit values provided by the LLM (which integrated SMC/MFE/MAE/ATR)
                    
                    # Safe get with float conversion
                    try:
                        opt_sl = float(ai_exits.get('sl_price', 0.0))
                        opt_tp = float(ai_exits.get('tp_price', 0.0))
                    except (ValueError, TypeError):
                        logger.error(f"Invalid SL/TP from AI: {ai_exits}")
                        opt_sl = 0.0
                        opt_tp = 0.0
                    
                    # Validate and Normalize
                    opt_sl = self._normalize_price(opt_sl)
                    opt_tp = self._normalize_price(opt_tp)
                    
                    # --- Update SL ---
                    if opt_sl > 0:
                        diff_sl = abs(opt_sl - sl)
                        
                        # Validate Stop Level distance
                        valid_sl = True
                        if type_pos == mt5.POSITION_TYPE_BUY:
                            if (current_price - opt_sl) < stop_level_dist: valid_sl = False # SL must be below price
                            if opt_sl >= current_price: valid_sl = False # Basic sanity
                        elif type_pos == mt5.POSITION_TYPE_SELL:
                            if (opt_sl - current_price) < stop_level_dist: valid_sl = False # SL must be above price
                            if opt_sl <= current_price: valid_sl = False # Basic sanity
                        
                        # Only update if valid and difference is significant (reduce api spam)
                        if valid_sl and diff_sl > (point * 10):
                            request['sl'] = opt_sl
                            changed = True
                            logger.info(f"AI Model 更新 SL: {sl:.2f} -> {opt_sl:.2f}")

                    # --- Update TP ---
                    if opt_tp > 0:
                        diff_tp = abs(opt_tp - tp)
                        
                        # Validate Stop Level distance
                        valid_tp = True
                        if type_pos == mt5.POSITION_TYPE_BUY:
                             if (opt_tp - current_price) < stop_level_dist: valid_tp = False # TP must be above price
                             if opt_tp <= current_price: valid_tp = False
                        elif type_pos == mt5.POSITION_TYPE_SELL:
                             if (current_price - opt_tp) < stop_level_dist: valid_tp = False # TP must be below price
                             if opt_tp >= current_price: valid_tp = False
                        
                        # Only update if valid and difference is significant
                        if valid_tp and diff_tp > (point * 10):
                            request['tp'] = opt_tp
                            changed = True
                            logger.info(f"AI Model 更新 TP: {tp:.2f} -> {opt_tp:.2f}")

                # 如果没有明确价格，但有 ATR 倍数建议 (兼容旧逻辑或备用)，则计算
                # REMOVED/SKIPPED to enforce "No Dynamic Movement"
                # elif new_sl_multiplier > 0 or new_tp_multiplier > 0:
                #     # DEBUG: Replaced logic
                #     current_sl_dist = atr * new_sl_multiplier
                #     current_tp_dist = atr * new_tp_multiplier
                #     
                #     suggested_sl = 0.0
                #     suggested_tp = 0.0
                #     
                #     if type_pos == mt5.POSITION_TYPE_BUY:
                #         suggested_sl = current_price - current_sl_dist
                #         suggested_tp = current_price + current_tp_dist
                #     elif type_pos == mt5.POSITION_TYPE_SELL:
                #         suggested_sl = current_price + current_sl_dist
                #         suggested_tp = current_price - current_tp_dist
                #     
                #     # Normalize
                #     suggested_sl = self._normalize_price(suggested_sl)
                #     suggested_tp = self._normalize_price(suggested_tp)
                #
                #     # 仅当差异显著时更新
                #     if suggested_sl > 0:
                #         diff_sl = abs(suggested_sl - sl)
                #         is_better_sl = False
                #         if type_pos == mt5.POSITION_TYPE_BUY and suggested_sl > sl: is_better_sl = True
                #         if type_pos == mt5.POSITION_TYPE_SELL and suggested_sl < sl: is_better_sl = True
                #         
                #         valid = True
                #         if type_pos == mt5.POSITION_TYPE_BUY and (current_price - suggested_sl < stop_level_dist): valid = False
                #         if type_pos == mt5.POSITION_TYPE_SELL and (suggested_sl - current_price < stop_level_dist): valid = False
                #         
                #         if valid and (diff_sl > point * 20 or (is_better_sl and diff_sl > point * 5)):
                #             request['sl'] = suggested_sl
                #             changed = True
                #     
                #     if suggested_tp > 0 and abs(suggested_tp - tp) > point * 30:
                #         valid = True
                #         if type_pos == mt5.POSITION_TYPE_BUY and (suggested_tp - current_price < stop_level_dist): valid = False
                #         if type_pos == mt5.POSITION_TYPE_SELL and (current_price - suggested_tp < stop_level_dist): valid = False
                #         
                #         if valid:
                #             request['tp'] = suggested_tp
                #             changed = True
            
            # --- 2. 兜底移动止损 (Trailing Stop) ---
            # 已禁用，仅依赖 AI 更新
            # if not changed: ... pass
             
            if changed:
                logger.info(f"更新持仓 #{pos.ticket}: SL={request['sl']:.2f}, TP={request['tp']:.2f}")
                result = mt5.order_send(request)
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    logger.error(f"持仓修改失败: {result.comment}")
            # 如果最新信号转为反向或中立，且强度足够，可以考虑提前平仓
            # 但 execute_trade 已经处理了反向开仓(会先平仓)。
            # 这里只处理: 信号变 Weak/Neutral 时的防御性平仓 (如果需要)
            # 用户: "operate SL/TP, or close, open"
            if signal == 'neutral' and strategy_params:
                # 检查是否应该平仓
                # 简单逻辑: 如果盈利 > 0 且信号消失，落袋为安?
                # 或者依靠 SL/TP 自然离场。
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
        if best_score > -1000:
            logger.info(f"全策略优化完成! Best Score: {best_score:.2f}")
            
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

        # 5. 综合计算与融合
        final_sl = 0.0
        final_tp = 0.0
        
        if 'buy' in trade_type:
            # --- SL Calculation ---
            base_sl = price - mae_sl_dist
            
            # Priority: AI -> Structure -> Statistical
            if ai_sl > 0:
                # [Anti-Hunt Protection] Check if AI SL is too close (e.g. within 0.8 ATR)
                # User complaint: SL hit then reversal. 
                # If AI SL is too tight, we widen it to at least 0.8 ATR or use structure if safer.
                sl_dist = abs(price - ai_sl)
                min_safe_dist = atr * 0.8 # Minimum 0.8 ATR buffer
                
                if sl_dist < min_safe_dist:
                    logger.info(f"AI SL {ai_sl} too close ({sl_dist/atr:.2f} ATR), widening to {min_safe_dist/atr:.2f} ATR")
                    if 'buy' in trade_type:
                        final_sl = min(ai_sl, price - min_safe_dist)
                    else:
                        final_sl = max(ai_sl, price + min_safe_dist)
                else:
                    final_sl = ai_sl
            elif struct_sl_price > 0:
                final_sl = struct_sl_price if (price - struct_sl_price) >= min_sl_buffer else (price - min_sl_buffer)
            else:
                final_sl = base_sl
            
            if (price - final_sl) < min_sl_buffer:
                final_sl = price - min_sl_buffer
                
            # --- TP Calculation ---
            base_tp = price + mfe_tp_dist
            
            if ai_tp > 0:
                final_tp = ai_tp
            elif struct_tp_price > 0:
                final_tp = min(struct_tp_price - (atr * 0.1), base_tp)
            else:
                final_tp = base_tp
                
        else: # Sell
            # --- SL Calculation ---
            base_sl = price + mae_sl_dist
            
            if ai_sl > 0:
                # [Anti-Hunt Protection]
                sl_dist = abs(price - ai_sl)
                min_safe_dist = atr * 0.8 
                
                if sl_dist < min_safe_dist:
                    logger.info(f"AI SL {ai_sl} too close ({sl_dist/atr:.2f} ATR), widening to {min_safe_dist/atr:.2f} ATR")
                    if 'buy' in trade_type:
                         final_sl = min(ai_sl, price - min_safe_dist)
                    else:
                         final_sl = max(ai_sl, price + min_safe_dist)
                else:
                    final_sl = ai_sl
            elif struct_sl_price > 0:
                final_sl = struct_sl_price if (struct_sl_price - price) >= min_sl_buffer else (price + min_sl_buffer)
            else:
                final_sl = base_sl
                
            if (final_sl - price) < min_sl_buffer:
                final_sl = price + min_sl_buffer
                
            # --- TP Calculation ---
            base_tp = price - mfe_tp_dist
            
            if ai_tp > 0:
                final_tp = ai_tp
            elif struct_tp_price > 0:
                final_tp = max(struct_tp_price + (atr * 0.1), base_tp)
            else:
                final_tp = base_tp

        return final_sl, final_tp



    def optimize_short_term_params(self):
        """
        Optimize short-term strategy parameters (RVGI+CCI, IFVG)
        Executed every 1 hour
        """
        logger.info("Running Short-Term Parameter Optimization (WOAm)...")
        
        # 1. Get Data (Last 500 M15 candles)
        df = self.get_market_data(500)
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
                        
                        cursor.execute('''
                            INSERT OR IGNORE INTO trades (ticket, symbol, action, volume, price, time, result, close_price, close_time, profit, mfe, mae)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            ticket, 
                            symbol, 
                            pos_type, 
                            deal.volume, 
                            0.0, # Open price unknown
                            datetime.fromtimestamp(deal.time), # Approximate open time (actually this is close time)
                            'CLOSED',
                            deal.price,
                            datetime.fromtimestamp(deal.time),
                            profit,
                            0.0, # MFE unknown without analysis
                            0.0  # MAE unknown
                        ))
                        count += 1
            
            if count > 0:
                conn.commit()
                logger.info(f"Synced {count} historical trades from MT5 to local DB.")
                
        except Exception as e:
            logger.error(f"Failed to sync account history: {e}")

    def initialize(self):
        """Initialize Trader State"""
        logger.info(f"初始化交易代理 - {self.symbol}")
        # Sync history on startup
        self.sync_account_history()
        self.is_running = True

    def _get_mt5_data(self, timeframe, count):
        """Helper to get data frame from MT5 directly"""
        rates = mt5.copy_rates_from_pos(self.symbol, timeframe, 0, count)
        if rates is None or len(rates) == 0:
            return None
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        
        if 'tick_volume' in df.columns:
            df.rename(columns={'tick_volume': 'volume'}, inplace=True)
            
        return df

    def process_tick(self):
        """Single tick processing"""
        if not self.is_running:
            return

        # 限制 ETHUSD 仅在周末交易 (周六=5, 周日=6)
        if self.symbol == "ETHUSD":
            if datetime.now().weekday() < 5:
                # 非周末，不执行交易逻辑
                return

        try:
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
                
                # New Bar Logic
                is_new_bar = current_bar_time > self.last_bar_time
                
                # 每秒执行的逻辑 (Check orders, manage positions)
                # ---------------------------------------------------
                
                # ---------------------------------------------------

                if is_new_bar:
                    logger.info(f"New Bar Detected: {datetime.fromtimestamp(current_bar_time)}")
                    self.last_bar_time = current_bar_time
                    
                    # 2. 获取数据并计算指标
                    # M15 Data (Main)
                    # self.data_loader might not exist in SymbolTrader (it exists in MT5Bot),
                    # so we use mt5.copy_rates_from_pos directly or self.db_manager.
                    # Since this is SymbolTrader, we should rely on standard mt5 calls or passed in components.
                    # Reverting to direct MT5 calls for safety if data_loader is missing.
                    
                    df = self._get_mt5_data(self.timeframe, 1000)
                    if df is None or df.empty:
                        logger.error("无法获取 K 线数据")
                        return

                    # H1 Data (Trend)
                    df_h1 = self._get_mt5_data(mt5.TIMEFRAME_H1, 500)
                    if df_h1 is None: df_h1 = pd.DataFrame()
                    
                    # H4 Data (Macro)
                    df_h4 = self._get_mt5_data(mt5.TIMEFRAME_H4, 200)
                    if df_h4 is None: df_h4 = pd.DataFrame()
                    
                    # 保存数据到 DB
                    if not df.empty:
                        self.db_manager.save_market_data(df, self.symbol, self.tf_name)
                        logger.info(f"新K线生成 ({datetime.fromtimestamp(current_bar_time)}), 执行策略分析...")
                    
                    # 更新分析时间戳
                    self.last_analysis_time = time.time()
                    
                    # 2. 获取数据并分析
                    # (df already fetched above as M15 Main)
                    
                    # Fetch Multi-Timeframe Data (Already fetched above as df_h1, df_h4)
                    # Just need to ensure they are standard DataFrames with time index for processor
                    
                    # 更新 Grid Strategy 数据
                    self.grid_strategy.update_market_data(df)
                    
                    # 使用 data_processor 计算指标
                    processor = MT5DataProcessor()
                    df_features = processor.generate_features(df)
                    
                    # Calculate features for H1/H4
                    df_features_h1 = processor.generate_features(df_h1) if not df_h1.empty else pd.DataFrame()
                    df_features_h4 = processor.generate_features(df_h4) if not df_h4.empty else pd.DataFrame()
                    
                    # Helper to safely get latest dict
                    def get_latest_safe(dframe):
                        if dframe.empty: return {}
                        return dframe.iloc[-1].to_dict()

                    feat_h1 = get_latest_safe(df_features_h1)
                    feat_h4 = get_latest_safe(df_features_h4)

                    # 3. 调用 AI 与高级分析
                    # 构建市场快照
                    current_price = df.iloc[-1]
                    latest_features = df_features.iloc[-1].to_dict()
                    self.last_atr = float(latest_features.get('atr', 0.0))
                    
                    # 获取账户信息
                    acc_info = mt5.account_info()
                    account_data = {
                        "balance": 0.0,
                        "equity": 0.0,
                        "margin_free": 0.0,
                        "available_balance": 0.0
                    }
                    if acc_info:
                        account_data = {
                            "balance": float(acc_info.balance),
                            "equity": float(acc_info.equity),
                            "margin_free": float(acc_info.margin_free),
                            "available_balance": float(acc_info.margin_free) # Approximation
                        }

                    market_snapshot = {
                        "symbol": self.symbol,
                        "timeframe": self.tf_name,
                        "account_info": account_data,
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
                            "obv": float(latest_features.get('obv', 0)),
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
                            "H4": {
                                "close": float(feat_h4.get('close', 0)),
                                "rsi": float(feat_h4.get('rsi', 50)),
                                "ema_fast": float(feat_h4.get('ema_fast', 0)),
                                "ema_slow": float(feat_h4.get('ema_slow', 0)),
                                "trend": "bullish" if feat_h4.get('ema_fast', 0) > feat_h4.get('ema_slow', 0) else "bearish"
                            }
                        }
                    }
                    
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
                    
                    # 获取历史交易绩效 (MFE/MAE) - Filter by Current Symbol
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
                        "performance_stats": trade_stats
                    }
                    
                    # Qwen Sentiment Analysis
                    qwen_sent_score = 0
                    qwen_sent_label = 'neutral'
                    try:
                        # DEBUG: Verify method existence
                        if not hasattr(self.qwen_client, 'analyze_market_sentiment'):
                            logger.error(f"Method analyze_market_sentiment missing in {type(self.qwen_client)}")
                            logger.error(f"Available methods: {[m for m in dir(self.qwen_client) if not m.startswith('__')]}")
                        
                        qwen_sentiment = self.qwen_client.analyze_market_sentiment(market_snapshot)
                        if qwen_sentiment:
                            qwen_sent_score = qwen_sentiment.get('sentiment_score', 0)
                            qwen_sent_label = qwen_sentiment.get('sentiment', 'neutral')
                    except Exception as e:
                        logger.error(f"Sentiment Analysis Failed: {e}")

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
                            
                            # 3. Dynamic Position & Grid Management (from Qwen Analysis)
                            pos_mgmt = strategy.get('position_management', {})
                            if pos_mgmt:
                                # Update Global TP for Basket
                                if 'global_tp' in pos_mgmt:
                                    self.grid_strategy.global_tp = float(pos_mgmt['global_tp'])
                                    logger.info(f"AI 更新 Grid Global TP: {self.grid_strategy.global_tp}")
                                
                                # Update Dynamic Basket TP
                                if 'dynamic_basket_tp' in pos_mgmt:
                                    try:
                                        basket_tp = float(pos_mgmt['dynamic_basket_tp'])
                                        self.grid_strategy.update_dynamic_params(basket_tp=basket_tp)
                                    except Exception as e:
                                        logger.error(f"Failed to update Dynamic Basket TP: {e}")
                                    
                                # Update Lot Multiplier
                                if 'martingale_multiplier' in pos_mgmt:
                                    self.grid_strategy.lot_multiplier = float(pos_mgmt['martingale_multiplier'])
                                    logger.info(f"AI 更新 Grid Lot Multiplier: {self.grid_strategy.lot_multiplier}")
                                    
                                # Update Grid Step (Spacing)
                                if 'recommended_grid_step_pips' in pos_mgmt:
                                    step_pips = float(pos_mgmt['recommended_grid_step_pips'])
                                    if step_pips > 0:
                                        # Convert pips to points (assuming 1 pip = 10 points for standard pairs)
                                        self.grid_strategy.grid_step_points = int(step_pips * 10) 
                                        logger.info(f"AI 更新 Grid Step: {step_pips} pips ({self.grid_strategy.grid_step_points} points)")
                                
                                # Update TP Steps (Dynamic Grid Levels)
                                if 'grid_level_tp_pips' in pos_mgmt:
                                    tp_list = pos_mgmt['grid_level_tp_pips']
                                    if isinstance(tp_list, list) and len(tp_list) > 0:
                                        # Get Symbol Info for accurate conversion
                                        symbol_info = mt5.symbol_info(self.symbol)
                                        tick_value = symbol_info.trade_tick_value if symbol_info else 1.0
                                        # Assuming 1 Pip = 10 Points
                                        pip_val_usd = 10 * tick_value * self.grid_strategy.lot
                                        
                                        # Convert Pips to Estimated Dollar Profit
                                        # New Logic: Qwen returns Pips distance. 
                                        # We want Total Profit Target ($) for that step.
                                        # Approx: Pips * PipValue * InitialLot * Multiplier_Factor(Simplified)
                                        # Simplified: Pips * PipValue_Per_Lot * InitialLot
                                        
                                        new_tp_steps = {}
                                        for i, tp_pips in enumerate(tp_list):
                                            # Ensure float
                                            pips = float(tp_pips)
                                            # Profit ($) = Pips * ($/Pip for 1 Lot) * LotSize
                                            profit_target = pips * pip_val_usd
                                            new_tp_steps[i+1] = profit_target
                                            
                                        self.grid_strategy.tp_steps.update(new_tp_steps)
                                        logger.info(f"AI 更新 Grid Level TPs ($): {new_tp_steps}")
                                     
                        except Exception as e:
                            logger.error(f"参数动态更新失败: {e}")
                        
                        # Qwen 信号转换
                        qw_action = strategy.get('action', 'neutral').lower()
                        
                        final_signal = "neutral"
                        if qw_action in ['buy', 'add_buy']:
                            final_signal = "buy"
                        elif qw_action in ['sell', 'add_sell']:
                            final_signal = "sell"
                        elif qw_action in ['limit_buy', 'buy_limit']:
                            final_signal = "limit_buy"
                        elif qw_action in ['limit_sell', 'sell_limit']:
                            final_signal = "limit_sell"
                        elif qw_action in ['stop_buy', 'buy_stop']:
                            final_signal = "stop_buy"
                        elif qw_action in ['stop_sell', 'sell_stop']:
                            final_signal = "stop_sell"
                        elif qw_action in ['close_buy', 'close_sell', 'close']:
                            final_signal = "close"
                        elif qw_action == 'hold':
                            final_signal = "hold"
                        elif qw_action == 'grid_start':
                            final_signal = "grid_start"
                        qw_signal = final_signal
                        # Reason
                        reason = strategy.get('strategy_rationale', 'Qwen Decision') # Use rationale if available
                        if reason == 'Qwen Decision':
                             reason = strategy.get('reason', 'Qwen Decision')

                        # 3. 智能平仓信号处理
                        if qw_action == 'close' and final_signal != 'close':
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
                            "rvgi_cci": rvgi_cci_result['signal']
                        }
                        
                        # Combine Signals (Using HybridOptimizer just for weighting record)
                        # We don't use the result of optimizer, just for logging weights if needed
                        # Or skip if optimizer is not critical here.
                        weights = {}
                        if hasattr(self, 'optimizer'):
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
                        
                        # 清理报告中可能的敏感或冗余技术参数
                        # 例如: 移除 "Score: ...", "MA=...", "RVGI(...", "Grid: Step=..." 等行
                        if telegram_report:
                            lines = telegram_report.split('\n')
                            clean_lines = []
                            for line in lines:
                                # 过滤掉包含特定技术关键词的行，保留核心分析
                                if not any(k in line for k in ["Score:", "MA=", "RVGI(", "Grid: Step=", "IFVG(", "ATR="]):
                                    clean_lines.append(line)
                            telegram_report = "\n".join(clean_lines).strip()

                        if telegram_report and len(telegram_report) > 50:
                            # 使用 Qwen 生成的专用 Telegram 报告
                            analysis_msg = (
                                f"🤖 *AI Strategy Report (Qwen)*\n"
                                f"Symbol: `{self.symbol}` | TF: `{self.tf_name}`\n"
                                f"Time: {datetime.now().strftime('%H:%M:%S')}\n\n"
                                f"{telegram_report}\n\n"
                                f"📊 *Live Status*\n"
                                f"• Action: *{final_signal.upper()}*\n"
                                f"• Lots: `{strategy.get('position_size', 0.01)}`\n"
                                f"• Strength: {strength:.0f}%\n"
                                f"• Sentiment: {qwen_sent_label.upper()} ({qwen_sent_score:.2f})\n\n"
                                f"💼 *Positions*\n"
                                f"{self.escape_markdown(pos_summary)}"
                            )
                        else:
                            # 备用：手动构建结构化消息
                            analysis_msg = (
                                f"🤖 *AI Strategy Report (Qwen)*\n"
                                f"Symbol: `{self.symbol}` | TF: `{self.tf_name}`\n"
                                f"Time: {datetime.now().strftime('%H:%M:%S')}\n\n"
                                
                                f"🧙‍♂️ *Qwen Analysis*\n"
                                f"• Action: *{qw_action.upper()}*\n"
                                f"• Lots: `{strategy.get('position_size', 0.01)}` (Dynamic)\n"
                                f"• Sentiment: {qwen_sent_label.upper()} ({qwen_sent_score})\n"
                                f"• Logic: _{self.escape_markdown(reason)}_\n\n"
                                
                                f"🏆 *Decision: {final_signal.upper()}*\n"
                                f"• Strength: {strength:.0f}%\n"
                                
                                f"💼 *Positions*\n"
                                f"{self.escape_markdown(pos_summary)}"
                            )
                        self.send_telegram_message(analysis_msg)

                        # 4. 执行交易
                        if final_signal != 'hold':
                            logger.info(f">>> 准备执行交易: {final_signal.upper()} (原始Action: {qw_action}) <<<")
                            
                            # 传入 Qwen 参数
                            entry_params = strategy.get('entry_conditions')
                            exit_params = strategy.get('exit_conditions')
                            
                            # Calculate Lot (Martingale aware if needed, or handled in execute_trade)
                            # Here we use calculate_dynamic_lot for initial lot
                            
                            # 优先使用 Qwen 计算的动态手数
                            qwen_lot = strategy.get('position_size')
                            if qwen_lot and isinstance(qwen_lot, (int, float)) and qwen_lot > 0:
                                suggested_lot = float(qwen_lot)
                                logger.info(f"使用 Qwen 动态计算手数: {suggested_lot}")
                            else:
                                # 回退到本地计算
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
                
        except KeyboardInterrupt:
            logger.info("用户停止机器人")
            mt5.shutdown()
        except Exception as e:
            logger.error(f"发生未捕获异常: {e}", exc_info=True)
            mt5.shutdown()

class MultiSymbolBot:
    def __init__(self, symbols, timeframe=mt5.TIMEFRAME_M15):
        self.symbols = symbols
        self.timeframe = timeframe
        self.traders = []
        self.is_running = False
        self.watcher = None

    def initialize_mt5(self):
        """Global MT5 Initialization"""
        # 尝试使用指定账户登录
        account = 89633982
        server = "Ava-Real 1-MT5"
        password = "Clj568741230#"
        
        if not mt5.initialize(login=account, server=server, password=password):
            logger.error(f"MT5 初始化失败, 错误码: {mt5.last_error()}")
            # 尝试不带账号初始化
            if not mt5.initialize():
                return False
        
        # 检查终端状态
        term_info = mt5.terminal_info()
        if not term_info.trade_allowed:
            logger.warning("⚠️ 警告: 终端 '自动交易' (Algo Trading) 未开启！")
            
        logger.info(f"MT5 全局初始化成功，账户: {mt5.account_info().login}")
        return True

    def start(self):
        if not self.initialize_mt5():
            logger.error("MT5 初始化失败，无法启动")
            return

        # Start File Watcher
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.watcher = FileWatcher([current_dir])
            self.watcher.start()
        except Exception as e:
            logger.error(f"Failed to start FileWatcher: {e}")

        self.is_running = True
        logger.info(f"🚀 Single-Process Bot Started for: {self.symbols}")

        # In Single Process Mode (run via run_strategies.bat), we usually have only 1 symbol per process.
        # However, MultiSymbolBot class structure supports multiple threads.
        # If run_strategies.bat passes 1 symbol (e.g. "GOLD"), this loop runs once -> 1 thread -> effectively single process per strategy.
        
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
    # Default symbols
    symbols = ["GOLD", "ETHUSD"]
    
    # Allow command line override (comma separated)
    if len(sys.argv) > 1:
        # Check if argument is a list of symbols or just one
        arg = sys.argv[1]
        if "," in arg:
            symbols = [s.strip().upper() for s in arg.split(",")]
        else:
            symbols = [arg.upper()]
            
    bot = MultiSymbolBot(symbols=symbols, timeframe=mt5.TIMEFRAME_M15)
    bot.start()