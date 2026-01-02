import time
import sys
import os
import logging
from datetime import datetime
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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('windows_bot.log', encoding='utf-8'),
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
    from .optimization import GWO, WOAm, DE, COAm, BBO, TETA
    from .advanced_analysis import (
        AdvancedMarketAnalysis, AdvancedMarketAnalysisAdapter, MFHAnalyzer, SMCAnalyzer, 
        MatrixMLAnalyzer, CRTAnalyzer, PriceEquationModel, 
        TimeframeVisualAnalyzer, MTFAnalyzer
    )
except ImportError:
    # Fallback for direct script execution
    try:
        from ai_client_factory import AIClientFactory
        from mt5_data_processor import MT5DataProcessor
        from database_manager import DatabaseManager
        from optimization import GWO, WOAm, DE, COAm, BBO, TETA
        from advanced_analysis import (
            AdvancedMarketAnalysis, AdvancedMarketAnalysisAdapter, MFHAnalyzer, SMCAnalyzer, 
            MatrixMLAnalyzer, CRTAnalyzer, PriceEquationModel, 
            TimeframeVisualAnalyzer, MTFAnalyzer
        )
    except ImportError as e:
        logger.error(f"Failed to import modules: {e}")
        sys.exit(1)

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
            
            # DeepSeek/Qwen 信号包含强度，可以进一步加权?
            # 这里简化处理，只看方向
            
            weighted_sum += val * weight
            total_weight += weight
            details[source] = val * weight
            
        if total_weight == 0: return "neutral", 0, self.weights
        
        final_score = weighted_sum / total_weight
        
        final_signal = "neutral"
        if final_score > 0.15: final_signal = "buy" # 降低阈值，更灵敏
        elif final_score < -0.15: final_signal = "sell"
        
        return final_signal, final_score, self.weights
class AI_MT5_Bot:
    def __init__(self, symbol="XAUUSD", timeframe=mt5.TIMEFRAME_M15):
        self.symbol = symbol
        self.timeframe = timeframe
        self.tf_name = "M15"
        if timeframe == mt5.TIMEFRAME_M15: self.tf_name = "M15"
        elif timeframe == mt5.TIMEFRAME_H1: self.tf_name = "H1"
        elif timeframe == mt5.TIMEFRAME_H4: self.tf_name = "H4"
        
        self.magic_number = 123456
        self.lot_size = 0.01 
        self.max_drawdown_pct = 0.05
        
        self.db_manager = DatabaseManager()
        self.ai_factory = AIClientFactory()
        
        self.deepseek_client = self.ai_factory.create_client("deepseek")
        self.qwen_client = self.ai_factory.create_client("qwen")
        
        # Adjusted for M15 Timeframe with H1/H4 MTF Analysis
        self.crt_analyzer = CRTAnalyzer(timeframe_htf=mt5.TIMEFRAME_H1)
        self.mtf_analyzer = MTFAnalyzer(htf1=mt5.TIMEFRAME_H1, htf2=mt5.TIMEFRAME_H4)
        self.price_model = PriceEquationModel()
        self.tf_analyzer = TimeframeVisualAnalyzer()
        self.advanced_adapter = AdvancedMarketAnalysisAdapter()
        self.matrix_ml = MatrixMLAnalyzer()
        self.smc_analyzer = SMCAnalyzer()
        self.mfh_analyzer = MFHAnalyzer()
        
        self.optimizer = HybridOptimizer()
        
        self.last_bar_time = 0
        self.last_analysis_time = 0
        self.last_llm_time = 0 # Track LLM call time
        self.signal_history = []
        self.last_optimization_time = 0
        self.last_realtime_save = 0
        
        self.latest_strategy = None
        self.latest_signal = "neutral"
        
        self.optimizers = {
            "GWO": GWO(),
            "WOAm": WOAm(),
            "DE": DE(),
            "COAm": COAm(),
            "BBO": BBO(),
            "TETA": TETA()
        }
        self.active_optimizer_name = "WOAm"
    def initialize_mt5(self):
        """初始化 MT5 连接"""
        # 尝试使用指定账户登录
        account = 89633982
        server = "Ava-Real 1-MT5"
        password = "Clj568741230#"
        
        if not mt5.initialize(login=account, server=server, password=password):
            logger.error(f"MT5 初始化失败, 错误码: {mt5.last_error()}")
            # 尝试不带账号初始化
            if not mt5.initialize():
                return False
            
        # 确保数据库路径设置正确
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, 'trading_data.db')
        
        # 检查是否需要更新 db_manager 的路径
        # DatabaseManager 默认初始化时可能使用了不同的路径，这里强制覆盖
        if self.db_manager.db_path != db_path:
             logger.info(f"重新定向数据库路径到: {db_path}")
             self.db_manager = DatabaseManager(db_path=db_path)

        # 检查终端状态
        term_info = mt5.terminal_info()
        if term_info is None:
            logger.error("无法获取终端信息")
            return False
            
        if not term_info.trade_allowed:
            logger.warning("⚠️ 警告: 终端 '自动交易' (Algo Trading) 未开启，无法执行交易！请在 MT5 工具栏点击 'Algo Trading' 按钮。")
            
        if not term_info.connected:
            logger.warning("⚠️ 警告: 终端未连接到交易服务器，请检查网络或账号设置。")
        
        # 确认交易品种存在
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            logger.error(f"找不到交易品种 {self.symbol}")
            return False
            
        if not symbol_info.visible:
            logger.info(f"交易品种 {self.symbol} 不可见，尝试选中")
            if not mt5.symbol_select(self.symbol, True):
                logger.error(f"无法选中交易品种 {self.symbol}")
                return False
        
        # 检查品种是否允许交易
        if symbol_info.trade_mode == mt5.SYMBOL_TRADE_MODE_DISABLED:
            logger.error(f"交易品种 {self.symbol} 禁止交易")
            return False
                
        logger.info(f"MT5 初始化成功，已连接到账户: {mt5.account_info().login}")
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
            profit = getattr(result, 'profit', 0.0)
            self.send_telegram_message(f"🔄 *Position Closed*\nTicket: `{position.ticket}`\nReason: {comment}\nProfit: {profit}")
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
            
            # --- 1. 自适应基础风险 (Self-Adaptive Base Risk) ---
            # 基于近期胜率和盈亏比动态调整基础风险
            # 默认 2%
            base_risk_pct = 0.02
            
            metrics = self.db_manager.get_performance_metrics(limit=20)
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
                # A. 大模型一致性
                ds_sig = ai_signals.get('deepseek', 'neutral')
                qw_sig = ai_signals.get('qwen', 'neutral')
                target_sig = self.latest_signal # 最终决策方向
                
                if ds_sig == target_sig and qw_sig == target_sig:
                    consensus_multiplier += 0.3 # 双模型共振
                
                # B. 高级算法共振 (Voting)
                tech_signals = [
                    ai_signals.get('crt'), ai_signals.get('price_equation'),
                    ai_signals.get('matrix_ml'), ai_signals.get('smc'),
                    ai_signals.get('mfh'), ai_signals.get('mtf')
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
                f"💰 智能资金管理:\n"
                f"• Base Risk: {base_risk_pct:.1%}\n"
                f"• Multipliers: Consensus={consensus_multiplier:.2f}, Strength={strength_multiplier:.2f}, Struct={structure_multiplier:.2f}\n"
                f"• Final Risk: {final_risk_pct:.2%} (${risk_amount:.2f})\n"
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
        valid_actions = ['buy', 'sell', 'limit_buy', 'limit_sell', 'close', 'add_buy', 'add_sell', 'hold']
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
                if llm_action == 'add_buy' and is_buy_pos: should_add = True
                elif llm_action == 'add_sell' and not is_buy_pos: should_add = True
                
                # 如果是单纯的 buy/sell 信号，且已有同向仓位，通常视为 hold，除非明确 add
                # 但如果用户希望 "完全交给大模型"，那么如果大模型在有仓位时发出了 buy，可能意味着加仓
                # 为了安全，我们严格限制只有 'add_xxx' 才加仓，或者 signal 极强
                
                if should_add:
                    logger.info(f"执行加仓 #{pos.ticket} 方向")
                    # 加仓逻辑复用开仓逻辑，但可能调整手数
                    self._send_order(
                        "buy" if is_buy_pos else "sell", 
                        tick.ask if is_buy_pos else tick.bid,
                        explicit_sl,
                        explicit_tp,
                        comment="AI: Add Position"
                    )
                    
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
        if has_position and 'add' not in llm_action:
            logger.info(f"已有持仓 ({len(bot_positions)}), 且非加仓指令 ({llm_action}), 跳过开仓")
            return

        # 执行开仓/挂单
        trade_type = None
        price = 0.0
        
        if llm_action == 'buy':
            trade_type = "buy"
            price = tick.ask
        elif llm_action == 'sell':
            trade_type = "sell"
            price = tick.bid
        elif llm_action in ['limit_buy', 'buy_limit']:
            # 检查现有 Limit 挂单
            current_orders = mt5.orders_get(symbol=self.symbol)
            if current_orders:
                for o in current_orders:
                    if o.magic == self.magic_number:
                        # 如果是 Sell Limit/Stop (反向)，则取消
                        if o.type in [mt5.ORDER_TYPE_SELL_LIMIT, mt5.ORDER_TYPE_SELL_STOP]:
                             logger.info(f"取消反向挂单 #{o.ticket} (Type: {o.type})")
                             req = {"action": mt5.TRADE_ACTION_REMOVE, "order": o.ticket}
                             mt5.order_send(req)
                        # 如果是同向 (Buy Limit/Stop)，则保留 (叠加)
                        
            # 优先使用 limit_price (与 prompt 一致)，回退使用 entry_price
            price = entry_params.get('limit_price', entry_params.get('entry_price', 0.0)) if entry_params else 0.0
            
            # 增强：如果价格无效，尝试自动修复
            if price <= 0:
                logger.warning(f"LLM 建议 Limit Buy 但未提供价格，尝试使用 ATR 自动计算")
                # 获取 ATR
                rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, 20)
                if rates is not None and len(rates) > 14:
                     df_temp = pd.DataFrame(rates)
                     high_low = df_temp['high'] - df_temp['low']
                     atr = high_low.rolling(14).mean().iloc[-1]
                     if atr > 0:
                        price = tick.ask - (atr * 0.5) # 默认在当前价格下方 0.5 ATR 处挂单
                        logger.info(f"自动设定 Limit Buy 价格: {price:.2f} (Ask: {tick.ask}, ATR: {atr:.4f})")
            
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
                
        elif llm_action in ['limit_sell', 'sell_limit']:
            # 检查现有 Limit 挂单
            current_orders = mt5.orders_get(symbol=self.symbol)
            if current_orders:
                for o in current_orders:
                    if o.magic == self.magic_number:
                        # 如果是 Buy Limit/Stop (反向)，则取消
                        if o.type in [mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_BUY_STOP]:
                             logger.info(f"取消反向挂单 #{o.ticket} (Type: {o.type})")
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
                
                explicit_sl, explicit_tp = self.calculate_optimized_sl_tp(trade_type, price, atr)
                
                if explicit_sl == 0 or explicit_tp == 0:
                     logger.error("无法计算优化 SL/TP，放弃交易")
                     return 

            comment = f"AI: {llm_action.upper()}"
            
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
        if sl > 0:
            dist = abs(price - sl)
            if dist < stops_level:
                logger.warning(f"SL too close (Dist {dist:.5f} < Level {stops_level:.5f}). Adjusting.")
                if is_buy: 
                    sl = price - stops_level
                else: 
                    sl = price + stops_level
                sl = self._normalize_price(sl)
                
        if tp > 0:
            dist = abs(price - tp)
            if dist < stops_level:
                logger.warning(f"TP too close (Dist {dist:.5f} < Level {stops_level:.5f}). Adjusting.")
                if is_buy: 
                    tp = price + stops_level
                else: 
                    tp = price - stops_level
                tp = self._normalize_price(tp)
        
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
        
        # 挂单需要不同的 filling type? 通常 Pending 订单不用 FOK，用 RETURN 或默认
        if "limit" in type_str or "stop" in type_str:
             if 'type_filling' in request:
                 del request['type_filling']
             request['type_filling'] = mt5.ORDER_FILLING_RETURN
        
        logger.info(f"发送订单请求: Action={action}, Type={order_type}, Price={price:.2f}, SL={sl:.2f}, TP={tp:.2f}")
        result = mt5.order_send(request)
        if result is None:
             logger.error("order_send 返回 None")
             return

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"下单失败 ({type_str}): {result.comment}, retcode={result.retcode}")
        else:
            logger.info(f"下单成功 ({type_str}) #{result.order}")
            self.send_telegram_message(f"✅ *Order Executed*\nType: `{type_str.upper()}`\nPrice: `{price}`\nSL: `{sl}`\nTP: `{tp}`")



                



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
        except Exception as e:
            logger.error(f"Telegram 发送异常: {e}")

    def manage_positions(self, signal=None, strategy_params=None):
        """
        根据最新分析结果管理持仓:
        1. 更新止损止盈 (覆盖旧设置) - 基于 strategy_params
        2. 执行移动止损 (Trailing Stop)
        3. 检查是否需要平仓 (非反转情况，例如信号转弱)
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
            
            allow_update = True
            # if abs(sl - some_last_known_sl) > point * 10: ... (Requires state tracking)
            # 替代方案: 如果当前 SL 与 建议 SL 差距小于 20 point，视为"差不多"，不频繁修改干扰用户
            # 如果差距很大，说明 AI 发现了新的结构，或者用户设置的很不合理，需要修正
            
            if has_new_params:
                # 使用 calculate_optimized_sl_tp 进行统一计算和验证
                ai_exits = strategy_params.get('exit_conditions', {})
                trade_dir = 'buy' if type_pos == mt5.POSITION_TYPE_BUY else 'sell'
                
                opt_sl, opt_tp = self.calculate_optimized_sl_tp(trade_dir, current_price, atr, market_context=None, ai_exit_conds=ai_exits)
                
                opt_sl = self._normalize_price(opt_sl)
                opt_tp = self._normalize_price(opt_tp)
                
                if opt_sl > 0:
                    diff_sl = abs(opt_sl - sl)
                    is_better_sl = False
                    if type_pos == mt5.POSITION_TYPE_BUY and opt_sl > sl: is_better_sl = True
                    if type_pos == mt5.POSITION_TYPE_SELL and opt_sl < sl: is_better_sl = True
                    
                    valid_sl = True
                    if type_pos == mt5.POSITION_TYPE_BUY and (current_price - opt_sl < stop_level_dist): valid_sl = False
                    if type_pos == mt5.POSITION_TYPE_SELL and (opt_sl - current_price < stop_level_dist): valid_sl = False
                    
                    if valid_sl and (diff_sl > point * 20 or (is_better_sl and diff_sl > point * 5)):
                        request['sl'] = opt_sl
                        changed = True
                        logger.info(f"AI/Stats 更新 SL: {sl:.2f} -> {opt_sl:.2f}")

                if opt_tp > 0:
                    diff_tp = abs(opt_tp - tp)
                    valid_tp = True
                    if type_pos == mt5.POSITION_TYPE_BUY and (opt_tp - current_price < stop_level_dist): valid_tp = False
                    if type_pos == mt5.POSITION_TYPE_SELL and (current_price - opt_tp < stop_level_dist): valid_tp = False
                    
                    if valid_tp and diff_tp > point * 30:
                        request['tp'] = opt_tp
                        changed = True
                        logger.info(f"AI/Stats 更新 TP: {tp:.2f} -> {opt_tp:.2f}")

                # 如果没有明确价格，但有 ATR 倍数建议 (兼容旧逻辑或备用)，则计算
                elif new_sl_multiplier > 0 or new_tp_multiplier > 0:
                    # DEBUG: Replaced logic
                    current_sl_dist = atr * new_sl_multiplier
                    current_tp_dist = atr * new_tp_multiplier
                    
                    suggested_sl = 0.0
                    suggested_tp = 0.0
                    
                    if type_pos == mt5.POSITION_TYPE_BUY:
                        suggested_sl = current_price - current_sl_dist
                        suggested_tp = current_price + current_tp_dist
                    elif type_pos == mt5.POSITION_TYPE_SELL:
                        suggested_sl = current_price + current_sl_dist
                        suggested_tp = current_price - current_tp_dist
                    
                    # Normalize
                    suggested_sl = self._normalize_price(suggested_sl)
                    suggested_tp = self._normalize_price(suggested_tp)

                    # 仅当差异显著时更新
                    if suggested_sl > 0:
                        diff_sl = abs(suggested_sl - sl)
                        is_better_sl = False
                        if type_pos == mt5.POSITION_TYPE_BUY and suggested_sl > sl: is_better_sl = True
                        if type_pos == mt5.POSITION_TYPE_SELL and suggested_sl < sl: is_better_sl = True
                        
                        valid = True
                        if type_pos == mt5.POSITION_TYPE_BUY and (current_price - suggested_sl < stop_level_dist): valid = False
                        if type_pos == mt5.POSITION_TYPE_SELL and (suggested_sl - current_price < stop_level_dist): valid = False
                        
                        if valid and (diff_sl > point * 20 or (is_better_sl and diff_sl > point * 5)):
                            request['sl'] = suggested_sl
                            changed = True
                    
                    if suggested_tp > 0 and abs(suggested_tp - tp) > point * 30:
                        valid = True
                        if type_pos == mt5.POSITION_TYPE_BUY and (suggested_tp - current_price < stop_level_dist): valid = False
                        if type_pos == mt5.POSITION_TYPE_SELL and (current_price - suggested_tp < stop_level_dist): valid = False
                        
                        if valid:
                            request['tp'] = suggested_tp
                            changed = True
            
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
                    total_profit += deal.profit + deal.swap + deal.commission
                    
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
        Comprehensive Objective Function: Evaluates ALL dataframe-based strategy parameters together.
        params: Vector of parameter values corresponding to the defined structure.
        """
        # Global counter for progress logging
        if not hasattr(self, '_opt_counter'): self._opt_counter = 0
        self._opt_counter += 1
        if self._opt_counter % 50 == 0:
            logger.info(f"Optimization Progress: {self._opt_counter} evaluations...")

        # 1. Decode Parameters
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
            
            tmp_pem = PriceEquationModel()
            tmp_pem.ma_fast_period = p_pem_fast
            tmp_pem.ma_slow_period = p_pem_slow
            tmp_pem.adx_threshold = p_pem_adx
            
            tmp_adapter = AdvancedMarketAnalysisAdapter()
            
            # 3. Run Simulation
            start_idx = max(p_smc_ma, p_pem_slow, 50) + 10
            if len(df) < start_idx + 50: return -9999
            
            balance = 10000.0
            closes = df['close'].values
            
            trades_count = 0
            wins = 0
            
            # OPTIMIZATION: Vectorized Pre-calculation
            # 1. RVGI Series (Vectorized)
            rvgi_series = tmp_adapter.calculate_rvgi_cci_series(df, sma_period=p_rvgi_sma, cci_period=p_rvgi_cci)
            
            # 2. MFH Features (Vectorized Batch)
            mfh_features = tmp_mfh.prepare_features_batch(df)
            
            # 3. Step Skipping
            # Evaluate trade signals every 4 candles (1 hour) to speed up SMC/PEM/IFVG
            eval_step = 4 
            
            for i in range(start_idx, len(df)-1):
                curr_price = closes[i]
                next_price = closes[i+1]
                
                # MFH Train (Must happen every step for consistency)
                if mfh_features is not None:
                    # Get features for current step i
                    feats = mfh_features[i]
                    
                    # Predict first (using current weights)
                    pred = np.dot(tmp_mfh.weights, feats) + tmp_mfh.bias
                    
                    # Determine signal from prediction
                    mfh_sig = "buy" if pred > 0.001 else "sell" if pred < -0.001 else "neutral"
                    
                    # Train (using PAST return)
                    # The return we are predicting at 'i' is (price[i] - price[i-h])/price[i-h]
                    # Wait, MFH predicts FUTURE return? No, usually it predicts next step or horizon.
                    # The `train` method in MFHAnalyzer uses `current_price_change`.
                    # In `evaluate_comprehensive_params` original:
                    # if i > p_mfh_horizon:
                    #   past_ret = (closes[i] - closes[i-p_mfh_horizon]) / closes[i-p_mfh_horizon]
                    #   tmp_mfh.train(past_ret)
                    
                    if i > p_mfh_horizon:
                        past_ret = (closes[i] - closes[i-p_mfh_horizon]) / closes[i-p_mfh_horizon]
                        error = past_ret - tmp_mfh.last_prediction # Use cached prediction from previous steps? 
                        # Actually we need to emulate `train` logic:
                        # train(target) -> error = target - last_prediction -> weights += ... * last_features
                        # Here we have `pred` calculated above. But `train` uses `last_prediction` which corresponds to `last_features`.
                        # If we predict at `i`, we are predicting return at `i`. 
                        # Wait, `predict(df)` uses `df` ending at `i`.
                        # It predicts return? 
                        # `train` takes `current_price_change`.
                        # This implies we predict at T, and train at T+1 (or T+H) when result is known.
                        
                        # Simplified Batch Training:
                        # We just update weights using the error of the *current* prediction against *future*?
                        # No, standard online learning: Predict x_t -> y_hat. Observe y_t. Update.
                        # Here `past_ret` is the return realized *now* (from t-H to t).
                        # So we should have predicted this `H` steps ago.
                        # This complexity suggests we should stick to the original `train` method if possible, 
                        # but `train` relies on `self.last_features` stored in object.
                        # So we must manually update:
                        
                        # Correct Logic:
                        # 1. We have stored `last_features` and `last_prediction` from step `i-1` (or `i-H`?)
                        # 2. `train` uses `past_ret` (target) and `self.last_prediction`.
                        # 3. Then `predict` sets new `self.last_features`.
                        
                        # But `past_ret` is `(close[i] - close[i-H])`.
                        # This corresponds to prediction made at `i-H`.
                        # The original code called `train(past_ret)` then `predict(sub_df)`.
                        # `predict` stores `last_features` (features at `i`).
                        # `train` uses `last_features`? No, `train` uses `last_features` which was set by PREVIOUS `predict`.
                        # So if we call `predict` at `i`, `last_features` becomes features at `i`.
                        # Next loop `i+1`, `train` is called. It updates weights based on `last_features` (from `i`).
                        # But `past_ret` passed to train is `(closes[i+1] - closes[i+1-H])`.
                        # This seems mismatched if H > 1.
                        # But let's replicate original flow:
                        
                        target = past_ret
                        # We need `last_prediction` and `last_features` from the *previous* predict call (which was at i-1? No, original loop called predict at i).
                        # Original:
                        # Loop i:
                        #   train(past_ret_at_i) -> updates using self.last_features (from i-1)
                        #   predict(sub_df_i) -> sets self.last_features (to i)
                        
                        # So we need to maintain state.
                        
                        if tmp_mfh.last_features is not None:
                            err = target - tmp_mfh.last_prediction
                            tmp_mfh.weights += tmp_mfh.learning_rate * err * tmp_mfh.last_features
                            tmp_mfh.bias += tmp_mfh.learning_rate * err
                        
                        # Now Predict for *next*
                        tmp_mfh.last_features = feats
                        tmp_mfh.last_prediction = pred
                
                # Check Trade Condition (Skipping steps for speed)
                if i % eval_step == 0:
                    sub_df = df.iloc[:i+1] # Still slicing, but 4x less often
                    
                    # Update PEM (Fast update)
                    tmp_pem.update(curr_price)
                    
                    # Signals
                    # 1. SMC (Heavy)
                    smc_sig = tmp_smc.analyze(sub_df)['signal']
                    
                    # 2. PEM (Medium - has rolling)
                    pem_sig = tmp_pem.predict(sub_df)['signal']
                    
                    # 3. IFVG (Medium)
                    ifvg_sig = tmp_adapter.analyze_ifvg(sub_df, min_gap_points=p_ifvg_gap)['signal']
                    
                    # 4. RVGI (Fast Lookup)
                    rvgi_sig_val = rvgi_series.iloc[i]
                    rvgi_sig = 'buy' if rvgi_sig_val == 1 else 'sell' if rvgi_sig_val == -1 else 'neutral'
                    
                    # 5. MFH (Already calc)
                    # mfh_sig determined above
                    
                    # Combine
                    votes = 0
                    for s in [smc_sig, mfh_sig, pem_sig, ifvg_sig, rvgi_sig]:
                        if s == 'buy': votes += 1
                        elif s == 'sell': votes -= 1
                    
                    final_sig = "neutral"
                    if votes >= 2: final_sig = "buy"
                    elif votes <= -2: final_sig = "sell"
                    
                    # Evaluate Trade
                    # We assume we hold for `eval_step` candles or until next signal?
                    # Original logic checked every candle.
                    # Simplification: We check result `eval_step` candles later?
                    # Or we just take the PnL of the next candle (i to i+1) and assume we hold if signal persists?
                    # Original:
                    # if final_sig == 'buy': balance += (next - curr)
                    # This implies 1-bar holding period (Scalping).
                    
                    # If we only check every 4 bars, we miss trades in between.
                    # But for optimization, we just want to know if parameters are good generally.
                    # We will accumulate return for the *next* candle only (i to i+1), effectively trading 25% of time.
                    # This is a valid proxy for parameter quality.
                    
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

    def optimize_strategy_parameters(self):
        """
        Comprehensive Optimization: Tunes ALL strategy parameters using Auto-AO.
        """
        logger.info("开始执行全策略参数优化 (Comprehensive Auto-AO)...")
        
        # Reset progress counter
        self._opt_counter = 0
        
        # 1. 获取历史数据
        # For M15, we fetch 1000 candles to cover enough time for valid optimization
        # 1000 candles = ~250 hours (10 days) of M15 data
        df = self.get_market_data(1000) 
        if df is None or len(df) < 500:
            logger.warning("数据不足，跳过优化")
            return
            
        # 2. Define Search Space (10 Dimensions)
        # smc_ma, smc_atr, mfh_lr, mfh_horizon, pem_fast, pem_slow, pem_adx, rvgi_sma, rvgi_cci, ifvg_gap
        bounds = [
            (100, 300),     # smc_ma
            (0.001, 0.005), # smc_atr (Adjusted for M15)
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
        import random
        algo_name = random.choice(list(self.optimizers.keys()))
        optimizer = self.optimizers[algo_name]
        
        # Adjust population size for realtime performance
        # Default is 50, which is too slow for 10-dim complex sim
        if hasattr(optimizer, 'pop_size'):
            optimizer.pop_size = 20
            
        logger.info(f"本次选择的优化算法: {algo_name} (Pop: {optimizer.pop_size})")
        
        # 5. Run
        # Increase epochs slightly as space is larger, but keep low for realtime
        best_params, best_score = optimizer.optimize(
            objective, 
            bounds, 
            steps=steps, 
            epochs=4  # Reduced from 8 to 4 for speed
        )
        
        # 6. Apply Results
        if best_score > -1000:
            logger.info(f"全策略优化完成! Best Score: {best_score:.2f}")
            
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
            # Re-init MFH buffers if horizon changed? 
            # MFHAnalyzer uses horizon in calculate_features. 
            # Ideally we should re-init but learning rate update is fine.
            
            self.price_model.ma_fast_period = p_pem_fast
            self.price_model.ma_slow_period = p_pem_slow
            self.price_model.adx_threshold = p_pem_adx
            
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
            ai_tp = ai_exit_conds.get('tp_price', 0.0)
            
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
                    profit = deal.profit + deal.swap + deal.commission
                    
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
                self.db_manager.conn.commit()
                logger.info(f"Synced {count} historical trades from MT5 to local DB.")
                
        except Exception as e:
            logger.error(f"Failed to sync account history: {e}")

    def run(self):
        """主循环"""
        if not self.initialize_mt5():
            return

        logger.info(f"启动 AI 自动交易机器人 - {self.symbol}")
        self.send_telegram_message(f"🤖 *AI Bot Started*\nSymbol: `{self.symbol}`\nTimeframe: `{self.timeframe}`")
        
        # Sync history on startup
        self.sync_account_history()
        
        try:
            while True:
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
                    continue
                    
                current_bar_time = rates[0]['time']
                
                # --- Real-time Data Update (Added for Dashboard) ---
                # 每隔 3 秒保存一次当前正在形成的 K 线数据到数据库
                # 这样 Dashboard 就可以看到实时价格跳动
                if time.time() - self.last_realtime_save > 3:
                    try:
                        df_current = pd.DataFrame(rates)
                        df_current['time'] = pd.to_datetime(df_current['time'], unit='s')
                        df_current.set_index('time', inplace=True)
                        if 'tick_volume' in df_current.columns:
                            df_current.rename(columns={'tick_volume': 'volume'}, inplace=True)
                        
                        self.db_manager.save_market_data(df_current.copy(), self.symbol, self.tf_name)
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
                # 用户需求: 交易周期改为 15 分钟，大模型 1 小时分析
                # is_new_bar = current_bar_time != self.last_bar_time
                # 交易分析触发器: 900秒 (15分钟)
                should_trade_analyze = (time.time() - self.last_analysis_time >= 900) or (self.last_analysis_time == 0)
                
                if should_trade_analyze:
                    # Run Optimization if needed (Every 4 hours)
                    if time.time() - self.last_optimization_time > 3600 * 4: # 4 hours
                         self.optimize_strategy_parameters()
                         self.optimize_weights()
                         self.last_optimization_time = time.time()

                    if self.last_analysis_time == 0:
                        logger.info("首次运行，立即执行分析...")
                    else:
                        logger.info(f"执行周期性分析 (900s)...")
                    
                    self.last_bar_time = current_bar_time
                    self.last_analysis_time = time.time()
                    
                    # 2. 获取数据并分析
                    # ... 这里的代码保持不变 ...
                    # PEM 需要至少 108 根 K 线 (ma_fast_period)，MTF 更新 Zones 需要 500 根
                    # 为了确保所有模块都有足够数据，我们获取 600 根 (150 hours of M15)
                    df = self.get_market_data(600) 
                    
                    # 获取最近的 Tick 数据用于 Matrix ML
                    # 尝试获取最近 20 个 tick
                    ticks = mt5.copy_ticks_from(self.symbol, current_bar_time, 20, mt5.COPY_TICKS_ALL)
                    if ticks is None:
                        ticks = []
                    
                    if df is not None:
                        # 保存市场数据到DB
                        self.db_manager.save_market_data(df, self.symbol, self.tf_name)
                        
                        # 使用 data_processor 计算指标
                        processor = MT5DataProcessor()
                        df_features = processor.generate_features(df)
                        
                        # 3. 调用 AI 与高级分析
                        # 构建市场快照
                        current_price = df.iloc[-1]
                        latest_features = df_features.iloc[-1].to_dict()
                        
                        market_snapshot = {
                            "symbol": self.symbol,
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
                            }
                        }
                        
                        # --- 3.1 CRT 分析 ---
                        crt_result = self.crt_analyzer.analyze(self.symbol, current_price, current_bar_time)
                        logger.info(f"CRT 分析: {crt_result['signal']} ({crt_result['reason']})")
                        
                        # --- 3.2 价格方程模型 (PEM) ---
                        self.price_model.update(float(current_price['close']))
                        price_eq_result = self.price_model.predict(df) # 传入 df 进行分析
                        logger.info(f"PEM 预测: {price_eq_result['signal']} (目标: {price_eq_result['predicted_price']:.2f})")
                        
                        # --- 3.2.1 多时间周期分析 (新增) ---
                        tf_result = self.tf_analyzer.analyze(self.symbol, current_bar_time)
                        logger.info(f"TF 分析: {tf_result['signal']} ({tf_result['reason']})")
                        
                        # --- 3.2.2 高级技术分析 (新增) ---
                        # Use optimized parameters if available
                        st_params = getattr(self, 'short_term_params', {})
                        adv_result = self.advanced_adapter.analyze_full(df, params=st_params)
                        adv_signal = "neutral"
                        if adv_result:
                            adv_signal = adv_result['signal_info']['signal']
                            logger.info(f"高级技术分析: {adv_signal} (强度: {adv_result['signal_info']['strength']})")
                            logger.info(f"市场状态: {adv_result['regime']['description']}")
                            
                        # --- 3.2.3 Matrix ML 分析 (新增) ---
                        # 首先进行训练 (基于上一次预测和当前价格变动)
                        price_change = float(current_price['close']) - float(df.iloc[-2]['close']) if len(df) > 1 else 0
                        loss = self.matrix_ml.train(price_change)
                        if loss:
                            logger.info(f"Matrix ML 训练 Loss: {loss:.4f}")
                            
                        # 进行预测
                        ml_result = self.matrix_ml.predict(ticks)
                        logger.info(f"Matrix ML 预测: {ml_result['signal']} (Raw: {ml_result.get('raw_output', 0.0):.2f})")
                        
                        # --- 3.2.4 SMC 分析 (新增) ---
                        smc_result = self.smc_analyzer.analyze(df, self.symbol)
                        logger.info(f"SMC 结构: {smc_result['structure']} (信号: {smc_result['signal']})")
                        
                        # --- 3.2.5 MFH 分析 (新增) ---
                        # 计算真实收益率用于训练 (t - t_horizon)
                        # 我们需要足够的数据来计算 Horizon 收益
                        horizon = 5
                        mfh_slope = 0.0
                        mfh_signal = "neutral"
                        
                        if len(df) > horizon + 10:
                            # 1. 训练 (Delayed Training)
                            # 实际发生的 Horizon 收益: (Close[t] - Close[t-5]) / Close[t-5]
                            current_close = float(current_price['close'])
                            past_close = float(df.iloc[-1 - horizon]['close'])
                            
                            if past_close > 0:
                                actual_return = (current_close - past_close) / past_close
                                self.mfh_analyzer.train(actual_return)
                            
                            # 2. 预测
                            mfh_result = self.mfh_analyzer.predict(df)
                            mfh_slope = mfh_result['slope']
                            mfh_signal = mfh_result['signal']
                            logger.info(f"MFH 斜率: {mfh_slope:.4f} (信号: {mfh_signal})")
                        else:
                            mfh_result = {"signal": "neutral", "slope": 0.0}
                        
                        # --- 3.2.6 MTF 分析 (新增) ---
                        mtf_result = self.mtf_analyzer.analyze(self.symbol, current_price, current_bar_time)
                        logger.info(f"MTF 分析: {mtf_result['signal']} ({mtf_result['reason']})")
                        
                        # --- 3.2.7 IFVG 分析 (新增) ---
                        # 在 AdvancedAnalysisAdapter 中已调用，但这里需要单独提取结果供后续使用
                        # 我们之前在步骤 3.2.1 的 AdvancedAnalysisAdapter.analyze 中已经获取了 ifvg_result
                        # 但由于 analyze 方法返回的是一个包含多个子结果的字典，我们需要确保 ifvg_result 变量被正确定义
                        if adv_result and 'ifvg' in adv_result:
                            ifvg_result = adv_result['ifvg']
                        else:
                            # Fallback if advanced analysis failed or ifvg key missing
                            ifvg_result = {"signal": "hold", "strength": 0, "reasons": [], "active_zones": []}
                        
                        logger.info(f"IFVG 分析: {ifvg_result['signal']} (Strength: {ifvg_result['strength']})")

                        # --- 3.2.8 RVGI+CCI 分析 (新增) ---
                        if adv_result and 'rvgi_cci' in adv_result:
                            rvgi_cci_result = adv_result['rvgi_cci']
                        else:
                            rvgi_cci_result = {"signal": "hold", "strength": 0, "reasons": []}
                            
                        logger.info(f"RVGI+CCI 分析: {rvgi_cci_result['signal']} (Strength: {rvgi_cci_result['strength']})")
                        
                        # 准备优化器池信息供 AI 参考
                        optimizer_info = {
                            "available_optimizers": list(self.optimizers.keys()),
                            "active_optimizer": self.active_optimizer_name,
                            "last_optimization_score": self.optimizers[self.active_optimizer_name].best_score if self.optimizers[self.active_optimizer_name].best_score > -90000 else None,
                            "descriptions": {
                                "GWO": "Grey Wolf Optimizer - 模拟灰狼捕猎行为",
                                "WOAm": "Whale Optimization Algorithm (Modified) - 模拟座头鲸气泡网捕猎",
                                "DE": "Differential Evolution - 差分进化算法",
                                "COAm": "Cuckoo Optimization Algorithm (Modified) - 模拟布谷鸟寄生繁殖",
                                "BBO": "Biogeography-Based Optimization - 生物地理学优化",
                                "TETA": "Time Evolution Travel Algorithm - 时间演化旅行算法 (无参)"
                            }
                        }

                        # --- 3.3 DeepSeek 分析 (Throttle to 1 Hour) ---
                        should_run_llm = (time.time() - self.last_llm_time >= 3600) or (self.last_llm_time == 0)

                        # --- 3.3 DeepSeek 分析 ---
                        logger.info("正在调用 DeepSeek 分析市场结构...")
                        
                        # 获取历史交易绩效 (MFE/MAE) - 提前获取供 DeepSeek 使用
                        trade_stats = self.db_manager.get_trade_performance_stats(limit=50)
                        
                        # 获取当前持仓状态 (供 DeepSeek 和 Qwen 决策) - 提前获取
                        positions = mt5.positions_get(symbol=self.symbol)
                        current_positions_list = []
                        if positions:
                            for pos in positions:
                                cur_mfe, cur_mae = self.get_position_stats(pos)
                                # Calculate R-Multiple (Current Profit / Initial Risk)
                                # Assuming Risk = SL Distance * Volume * TickValue, but simpler:
                                # R = (Current Price - Open Price) / (Open Price - SL)
                                r_multiple = 0.0
                                if pos.sl > 0:
                                    risk_dist = abs(pos.price_open - pos.sl)
                                    if risk_dist > 0:
                                        profit_dist = 0.0
                                        if pos.type == mt5.POSITION_TYPE_BUY:
                                            profit_dist = pos.price_current - pos.price_open
                                        else:
                                            profit_dist = pos.price_open - pos.price_current
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
                        
                        # 准备当前优化状态上下文
                        optimization_status = {
                            "active_optimizer": self.active_optimizer_name,
                            "optimizer_details": optimizer_info, # 注入详细优化器信息
                            "smc_params": {
                                "ma_period": self.smc_analyzer.ma_period,
                                "atr_threshold": self.smc_analyzer.atr_threshold
                            },
                            "mfh_params": {
                                "learning_rate": self.mfh_analyzer.learning_rate
                            }
                        }

                        # 传入 CRT, PriceEq, TF 和 高级分析 的结果作为额外上下文
                        extra_analysis = {
                            "crt": crt_result,
                            "price_equation": price_eq_result,
                            "timeframe_analysis": tf_result,
                            "advanced_tech": adv_result['summary'] if adv_result else None,
                            "matrix_ml": ml_result,
                            "smc": smc_result,
                            "mfh": mfh_result,
                            "mtf": mtf_result,
                            "ifvg": ifvg_result,
                            "rvgi_cci": rvgi_cci_result,
                            "optimization_status": optimization_status # 新增: 当前参数状态
                        }
                        
                        # 调用 DeepSeek，传入性能数据和持仓信息
                        if should_run_llm:
                            structure = self.deepseek_client.analyze_market_structure(
                                market_snapshot, 
                                current_positions=current_positions_list,
                                extra_analysis=extra_analysis, 
                                performance_stats=trade_stats
                            )
                        else:
                            structure = {}
                            logger.info("跳过 DeepSeek 分析 (Throttle)")
                        logger.info(f"DeepSeek 分析完成: {structure.get('market_state')}")
                        
                        # DeepSeek 信号转换
                        ds_signal = structure.get('preliminary_signal', 'neutral')
                        ds_pred = structure.get('short_term_prediction', 'neutral')
                        ds_score = structure.get('structure_score', 50)
                        
                        # 如果 DeepSeek 没有返回 preliminary_signal (旧版本兼容)，使用简单的规则
                        if ds_signal == 'neutral':
                             if ds_pred == 'bullish' and ds_score > 60:
                                 ds_signal = "buy"
                             elif ds_pred == 'bearish' and ds_score > 60:
                                 ds_signal = "sell"
                        
                        # --- 3.4 Qwen 策略 ---
                        logger.info("正在调用 Qwen 生成策略...")
                        
                        # 准备混合信号供 Qwen 参考
                        technical_signals = {
                            "crt": crt_result,
                            "price_equation": price_eq_result,
                            "timeframe_analysis": tf_result,
                            "advanced_tech": adv_signal,
                            "matrix_ml": ml_result['signal'],
                            "smc": smc_result['signal'],
                            "mfh": mfh_result['signal'],
                            "mtf": mtf_result['signal'], 
                            "deepseek_analysis": { # 传入完整的 DeepSeek 分析结果
                                "market_state": structure.get('market_state'),
                                "preliminary_signal": ds_signal,
                                "confidence": structure.get('signal_confidence'),
                                "consistency": structure.get('consistency_analysis'),
                                "prediction": ds_pred
                            },
                            "performance_stats": trade_stats # 传入历史绩效
                        }
                        
                        if should_run_llm:
                            strategy = self.qwen_client.optimize_strategy_logic(structure, market_snapshot, technical_signals=technical_signals, current_positions=current_positions_list)
                            self.latest_strategy = strategy
                            self.last_llm_time = time.time()
                        elif self.latest_strategy:
                            strategy = self.latest_strategy
                            logger.info("使用缓存的 LLM 策略")
                        else:
                            strategy = {"action": "hold", "reason": "Waiting for LLM"}
                            logger.info("无缓存策略，默认 Hold")
                        
                        # --- 参数自适应优化 (Feedback Loop) ---
                        # 将大模型的参数优化建议应用到当前运行的算法中
                        if should_run_llm:
                            param_updates = strategy.get('parameter_updates', {})
                            if param_updates:
                                try:
                                    update_reason = param_updates.get('reason', 'AI Optimized')
                                    logger.info(f"应用参数优化 ({update_reason}): {param_updates}")
                                    
                                    # 1. SMC 参数
                                    if 'smc_atr_threshold' in param_updates:
                                        new_val = float(param_updates['smc_atr_threshold'])
                                        self.smc_analyzer.atr_threshold = new_val
                                        logger.info(f"Updated SMC ATR Threshold -> {new_val}")
                                        
                                    # 2. MFH 参数
                                    if 'mfh_learning_rate' in param_updates:
                                        new_val = float(param_updates['mfh_learning_rate'])
                                        self.mfh_analyzer.learning_rate = new_val
                                        logger.info(f"Updated MFH Learning Rate -> {new_val}")
                                        
                                    # 3. 切换优化器
                                    if 'active_optimizer' in param_updates:
                                        new_opt = str(param_updates['active_optimizer'])
                                        if new_opt in self.optimizers and new_opt != self.active_optimizer_name:
                                            self.active_optimizer_name = new_opt
                                            logger.info(f"Switched Optimizer -> {new_opt}")
                                            
                                    # 4. Matrix ML 参数 (如需)
                                    if 'matrix_ml_learning_rate' in param_updates:
                                         self.matrix_ml.learning_rate = float(param_updates['matrix_ml_learning_rate'])
                                         
                                except Exception as e:
                                    logger.error(f"参数动态更新失败: {e}")
                        
                        # Qwen 信号转换
                        # 如果没有明确 action 字段，我们假设它作为 DeepSeek 的确认层
                        # 现在我们优先使用 Qwen 返回的 action
                        qw_action = strategy.get('action', 'neutral').lower()
                        
                        # 扩展 Action 解析，支持加仓/减仓/平仓/挂单指令
                        final_signal = "neutral"
                        if qw_action in ['buy', 'add_buy']:
                            final_signal = "buy"
                        elif qw_action in ['sell', 'add_sell']:
                            final_signal = "sell"
                        elif qw_action in ['buy_limit', 'limit_buy']:
                            final_signal = "buy" # 强制转换为市价单
                            logger.info("[Override] Converting Limit Buy -> Market Buy per user preference")
                        elif qw_action in ['sell_limit', 'limit_sell']:
                            final_signal = "sell" # 强制转换为市价单
                            logger.info("[Override] Converting Limit Sell -> Market Sell per user preference")
                        elif qw_action in ['close_buy', 'close_sell', 'close']:
                            final_signal = "close" # 特殊信号: 平仓
                        elif qw_action == 'hold':
                            final_signal = "hold"
                            
                        # --- 增强: 多模型与技术共振修正 (Consensus Override) ---
                        # 如果 Qwen 偏向保守 (Hold/Neutral)，但 DeepSeek 或 技术指标极强，则进行覆盖
                        reason = strategy.get('reason', 'LLM Decision')
                        
                        if final_signal in ['hold', 'neutral']:
                            # 1. DeepSeek 强信号覆盖 (Only if available)
                            if ds_signal in ['buy', 'sell'] and ds_score >= 80:
                                final_signal = ds_signal
                                reason = f"[Override] DeepSeek High Confidence ({ds_score}): {structure.get('market_state')}"
                                logger.info(f"策略修正: DeepSeek 强信号 ({ds_score}) 覆盖 Qwen Hold -> {final_signal}")
                            
                            # 2. 技术指标共振覆盖 (如果 DeepSeek 也没信号)
                            elif final_signal in ['hold', 'neutral']:
                                tech_signals_list = [
                                    crt_result['signal'], price_eq_result['signal'], tf_result['signal'],
                                    adv_signal, ml_result['signal'], smc_result['signal'],
                                    mfh_result['signal'], mtf_result['signal'], ifvg_result['signal'],
                                    rvgi_cci_result['signal']
                                ]
                                buy_votes = sum(1 for s in tech_signals_list if s == 'buy')
                                sell_votes = sum(1 for s in tech_signals_list if s == 'sell')
                                total_tech = len(tech_signals_list)
                                
                                if total_tech > 0:
                                    buy_ratio = buy_votes / total_tech
                                    sell_ratio = sell_votes / total_tech
                                    
                                    if buy_ratio >= 0.7: # 70% 指标看多
                                        final_signal = "buy"
                                        reason = f"[Override] Technical Consensus Buy ({buy_votes}/{total_tech})"
                                        logger.info(f"策略修正: 技术指标共振 ({buy_ratio:.1%}) 覆盖 Hold -> Buy")
                                    elif sell_ratio >= 0.7: # 70% 指标看空
                                        final_signal = "sell"
                                        reason = f"[Override] Technical Consensus Sell ({sell_votes}/{total_tech})"
                                        logger.info(f"策略修正: 技术指标共振 ({sell_ratio:.1%}) 覆盖 Hold -> Sell")
                        
                        # 3. 智能平仓信号处理 (High Priority)
                        if qw_action == 'close' and final_signal != 'close':
                            final_signal = 'close'
                            reason = f"[Smart Exit] Qwen Profit Taking: {qw_reason}"
                            logger.info(f"策略修正: Qwen 触发智能平仓 -> CLOSE")

                        qw_signal = final_signal if final_signal not in ['hold', 'close'] else 'neutral'
                        
                        # --- 3.5 最终决策 (LLM Centric + Consensus) ---
                        
                        # 计算置信度/强度 (Strength)
                        # 我们使用技术指标的一致性作为置信度评分
                        tech_consensus_score = 0
                        matching_count = 0
                        valid_tech_count = 0
                        
                        tech_signals_list = [
                            crt_result['signal'], price_eq_result['signal'], tf_result['signal'],
                            adv_signal, ml_result['signal'], smc_result['signal'],
                            mfh_result['signal'], mtf_result['signal'], ifvg_result['signal'],
                            rvgi_cci_result['signal']
                        ]
                        
                        for sig in tech_signals_list:
                            if sig != 'neutral':
                                valid_tech_count += 1
                                if sig == final_signal:
                                    matching_count += 1
                        
                        if final_signal in ['buy', 'sell']:
                            # 基础分 60 (既然 LLM 敢喊单)
                            base_strength = 60
                            # 技术面加成
                            if valid_tech_count > 0:
                                tech_boost = (matching_count / valid_tech_count) * 40 # 最高 +40
                                strength = base_strength + tech_boost
                            else:
                                strength = base_strength
                                
                            # DeepSeek 加成
                            if ds_signal == final_signal:
                                strength = min(100, strength + 10)
                        else:
                            strength = 0

                        all_signals = {
                            "deepseek": ds_signal,
                            "qwen": qw_signal,
                            "crt": crt_result['signal'],
                            "price_equation": price_eq_result['signal'],
                            "tf_visual": tf_result['signal'],
                            "advanced_tech": adv_signal,
                            "matrix_ml": ml_result['signal'],
                            "smc": smc_result['signal'],
                            "mfh": mfh_result['signal'],
                            "mtf": mtf_result['signal'],
                            "ifvg": ifvg_result['signal'],
                            "rvgi_cci": rvgi_cci_result['signal']
                        }
                        
                        # 仅保留 weights 用于记录，不再用于计算信号
                        _, _, weights = self.optimizer.combine_signals(all_signals)

                        # --- 3.6 记录信号历史用于实时优化 ---
                        # 解决优化算法未运行的问题：收集数据并定期调用 optimize_weights
                        self.signal_history.append((current_bar_time, all_signals, float(current_price['close'])))
                        if len(self.signal_history) > 1000:
                            self.signal_history.pop(0)
                            
                        # 每 15 分钟尝试优化一次权重
                        if time.time() - self.last_optimization_time > 900:
                             self.optimize_weights()

                        logger.info(f"AI 最终决定 (LLM-Driven): {final_signal.upper()} (强度: {strength:.1f})")
                        logger.info(f"LLM Reason: {reason}")
                        logger.info(f"技术面支持: {matching_count}/{valid_tech_count}")
                        
                        # 保存分析结果到DB
                        self.db_manager.save_signal(self.symbol, self.tf_name, {
                            "final_signal": final_signal,
                            "strength": strength,
                            "details": {
                                "source": "LLM_Centric",
                                "reason": reason, # Add reason field for dashboard/visualization
                                "weights": weights,
                                "signals": all_signals,
                                "market_state": structure.get('market_state'),
                                "prediction": structure.get('short_term_prediction'),
                                "crt_reason": crt_result['reason'],
                                "mtf_reason": mtf_result['reason'],
                                "adv_summary": adv_result['summary'] if adv_result else None,
                                "matrix_ml_raw": ml_result['raw_output'],
                                "smc_structure": smc_result['structure'],
                                "smc_reason": smc_result['reason'],
                                "mfh_slope": mfh_result['slope'],
                                "ifvg_reason": ", ".join(ifvg_result['reasons']) if ifvg_result['reasons'] else "N/A"
                            }
                        })
                        
                        # 更新全局缓存，供 manage_positions 使用
                        self.latest_strategy = strategy
                        self.latest_signal = final_signal
                        
                        # --- 发送分析报告到 Telegram ---
                        # 构建更详细的报告
                        regime_info = adv_result['regime']['description'] if adv_result else "N/A"
                        volatility_info = f"{adv_result['risk']['volatility']:.2%}" if adv_result else "N/A"
                        
                        # 获取当前持仓概览
                        pos_summary = "No Open Positions"
                        positions = mt5.positions_get(symbol=self.symbol)
                        if positions:
                            pos_details = []
                            for p in positions:
                                type_str = "BUY" if p.type == mt5.POSITION_TYPE_BUY else "SELL"
                                pnl = p.profit
                                pos_details.append(f"{type_str} {p.volume} (PnL: {pnl:.2f})")
                            pos_summary = "\n".join(pos_details)

                        # 获取建议的 SL/TP (用于展示最优 SL/TP)
                        # 逻辑: 优先展示 Qwen 策略中明确的 SL/TP，如果没有，则展示基于 MFE/MAE 优化的计算值
                        current_bid = mt5.symbol_info_tick(self.symbol).bid
                        current_ask = mt5.symbol_info_tick(self.symbol).ask
                        ref_price = current_ask # 默认参考价
                        
                        trade_dir_for_calc = "buy"
                        if final_signal == 'sell':
                            trade_dir_for_calc = "sell"
                            ref_price = current_bid
                        
                        # 1. 尝试从 Qwen 策略获取
                        exit_conds = strategy.get('exit_conditions', {})
                        opt_sl = exit_conds.get('sl_price')
                        opt_tp = exit_conds.get('tp_price')
                        
                        # 2. 如果 Qwen 未提供，使用内部优化算法计算
                        if not opt_sl or not opt_tp:
                            # 准备市场上下文
                            sl_tp_context = {
                                "supply_zones": adv_result.get('ifvg', {}).get('active_zones', []),
                                "demand_zones": [],
                                "bearish_fvgs": [], 
                                "bullish_fvgs": []
                            }
                            # 计算 ATR (复用)
                            atr_val = float(latest_features.get('atr', 0))
                            if atr_val == 0: atr_val = ref_price * 0.005
                            
                            calc_sl, calc_tp = self.calculate_optimized_sl_tp(trade_dir_for_calc, ref_price, atr_val, market_context=sl_tp_context)
                            
                            if not opt_sl: opt_sl = calc_sl
                            if not opt_tp: opt_tp = calc_tp

                        # 计算盈亏比 (R:R)
                        rr_str = "N/A"
                        if opt_sl and opt_tp and ref_price:
                            risk = abs(ref_price - opt_sl)
                            reward = abs(opt_tp - ref_price)
                            if risk > 0:
                                rr = reward / risk
                                rr_str = f"1:{rr:.2f}"

                        # 优化显示逻辑: 如果是 Hold 且无持仓，显示为 "Waiting for Market Direction"
                        display_decision = final_signal.upper()
                        if final_signal == 'hold' and (not positions or len(positions) == 0):
                            display_decision = "WAITING FOR MARKET DIRECTION ⏳"

                        # --- 准备资金管理与自我学习数据 ---
                        # 获取自我学习状态
                        metrics = self.db_manager.get_performance_metrics(limit=20)
                        win_rate = metrics.get('win_rate', 0.0)
                        profit_factor = metrics.get('profit_factor', 0.0)
                        
                        # 预计算建议手数 (用于展示)
                        # 准备完整的市场上下文 (与 execute_trade 一致，移除简化)
                        full_market_ctx = {}
                        if 'smc' in extra_analysis: full_market_ctx['smc'] = extra_analysis['smc']
                        if 'atr' in latest_features: full_market_ctx['atr'] = float(latest_features['atr'])
                        if adv_result and 'risk' in adv_result:
                             full_market_ctx['volatility_regime'] = adv_result['risk'].get('level', 'Normal')
                        
                        # 添加更多详细上下文，确保资金管理模块能获取完整信息
                        full_market_ctx['supply_zones'] = ifvg_result.get('active_zones', [])
                        if adv_result and 'demand_zones' in adv_result: full_market_ctx['demand_zones'] = adv_result['demand_zones']
                        if smc_result and 'bearish_fvgs' in smc_result: full_market_ctx['bearish_fvgs'] = smc_result['bearish_fvgs']
                        if smc_result and 'bullish_fvgs' in smc_result: full_market_ctx['bullish_fvgs'] = smc_result['bullish_fvgs']

                        # 计算真实的 MFE/MAE Ratio
                        real_mfe_mae_ratio = 1.0
                        if trade_stats and 'avg_mfe' in trade_stats and 'avg_mae' in trade_stats:
                             if abs(trade_stats['avg_mae']) > 0:
                                 real_mfe_mae_ratio = trade_stats['avg_mfe'] / abs(trade_stats['avg_mae'])
                        
                        # 计算
                        suggested_lot = self.calculate_dynamic_lot(
                            strength, 
                            market_context=full_market_ctx, 
                            mfe_mae_ratio=real_mfe_mae_ratio, # 使用真实计算值
                            ai_signals=all_signals
                        )
                        
                        # 估算风险百分比
                        account_equity = mt5.account_info().equity if mt5.account_info() else 0
                        risk_pct_display = "N/A"
                        if account_equity > 0 and opt_sl and ref_price:
                            risk_usd = abs(ref_price - opt_sl) * suggested_lot * (mt5.symbol_info(self.symbol).trade_tick_value or 1.0)
                            risk_pct_val = (risk_usd / account_equity) * 100
                            risk_pct_display = f"{risk_pct_val:.2f}%"

                        # 格式化 DeepSeek 和 Qwen 的详细分析
                        # DeepSeek Report
                        ds_analysis_text = f"• Market State: {self.escape_markdown(structure.get('market_state', 'N/A'))}\n"
                        ds_analysis_text += f"• Signal: {self.escape_markdown(ds_signal.upper())} (Conf: {ds_score}/100)\n"
                        ds_analysis_text += f"• Prediction: {self.escape_markdown(ds_pred)}\n"
                        ds_analysis_text += f"• Reasoning: {self.escape_markdown(structure.get('reasoning', 'N/A'))}\n" 
                        
                        # Qwen Report
                        qw_reason = strategy.get('reason', strategy.get('rationale', 'Strategy Optimization'))
                        qw_analysis_text = f"• Action: {self.escape_markdown(qw_action.upper())}\n"
                        qw_analysis_text += f"• Logic: _{self.escape_markdown(qw_reason)}_\n"
                        if param_updates:
                            qw_analysis_text += f"• Params Updated: {len(param_updates)} items"

                        safe_reason = self.escape_markdown(reason)
                        safe_volatility = self.escape_markdown(volatility_info)
                        safe_pos_summary = self.escape_markdown(pos_summary)
                        
                        # 构建单一整合消息
                        analysis_msg = (
                            f"🤖 *AI Gold Strategy Comprehensive Report*\n"
                            f"Symbol: `{self.symbol}` | TF: `{self.tf_name}`\n"
                            f"Time: {datetime.now().strftime('%H:%M:%S')}\n\n"
                            
                            f"🧠 *Self-Learning Status*\n"
                            f"• Win Rate (20): `{win_rate:.1%}`\n"
                            f"• Profit Factor: `{profit_factor:.2f}`\n"
                            f"• Adaptive Risk: `{risk_pct_display}`\n\n"
                            
                            f"🕵️ *DeepSeek Analysis (Structure)*\n"
                            f"{ds_analysis_text}\n"
                            
                            f"🧙‍♂️ *Qwen Analysis (Strategy)*\n"
                            f"{qw_analysis_text}\n"
                            
                            f"🏆 *Final Consolidated Result*\n"
                            f"• Decision: *{display_decision}* (Strength: {strength:.0f}%)\n"
                            f"• Direction: `{trade_dir_for_calc.upper()}`\n"
                            f"• Recommended Lot: `{suggested_lot}`\n"
                            f"• Reason: _{safe_reason}_\n\n"
                            
                            f"🎯 *Optimal Trade Setup (Best SL/TP)*\n"
                            f"• Ref Entry: `{ref_price:.2f}`\n"
                            f"• 🛑 Stop Loss: `{opt_sl:.2f}`\n"
                            f"• 🏆 Take Profit: `{opt_tp:.2f}`\n"
                            f"• R:R Ratio: `{rr_str}`\n\n"
                            
                            f"💼 *Account Status*\n"
                            f"{safe_pos_summary}"
                        )
                        self.send_telegram_message(analysis_msg)

                        
                        # 4. 执行交易
                        # 修正逻辑: 优先尊重 Qwen 的信号和参数 (大模型集合最终结果)
                        # 如果 Qwen 明确说 "hold" 或 "neutral"，即使 final_signal 是 buy/sell，也应该谨慎
                        # 但如果 final_signal 极强 (如 100.0)，我们可能还是想交易
                        # 现在的逻辑是: 交易方向以 final_signal 为准 (因为它是混合投票的结果，Qwen 也是其中一票)
                        # 但 参数 (Entry/Exit) 必须优先使用 Qwen 的建议
                        
                        if final_signal != 'hold':
                            logger.info(f">>> 准备执行 AI 集合决策: {final_signal.upper()} <<<")
                            entry_params = strategy.get('entry_conditions')
                            exit_params = strategy.get('exit_conditions')
                            
                            # 强制使用 Qwen 的参数，不再进行一致性回退检查
                            # 除非 Qwen 建议的参数明显不可用 (如 None)
                            
                            # 日志记录差异，但不阻止使用参数
                            if qw_signal != final_signal and qw_signal not in ['neutral', 'hold']:
                                logger.warning(f"Qwen 信号 ({qw_signal}) 与最终决策 ({final_signal}) 不一致，但仍优先使用 Qwen 参数")
                            
                            trade_res = self.execute_trade(
                                final_signal, 
                                strength, 
                                exit_params,
                                entry_params,
                                suggested_lot=suggested_lot
                            )
                            
                time.sleep(1) # 避免 CPU 占用过高
                
        except KeyboardInterrupt:
            logger.info("用户停止机器人")
            mt5.shutdown()
        except Exception as e:
            logger.error(f"发生未捕获异常: {e}", exc_info=True)
            mt5.shutdown()

if __name__ == "__main__":
    # 可以通过命令行参数传入品种
    symbol = "GOLD" 
    if len(sys.argv) > 1:
        symbol = sys.argv[1].upper()
    else:
        symbol = "GOLD" # 默认改为黄金
        
    bot = AI_MT5_Bot(symbol=symbol)
    bot.run()