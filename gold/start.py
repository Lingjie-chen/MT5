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
        if timeframe == mt5.TIMEFRAME_H1: self.tf_name = "H1"
        elif timeframe == mt5.TIMEFRAME_H4: self.tf_name = "H4"
        
        self.magic_number = 123456
        self.lot_size = 0.01 
        self.max_drawdown_pct = 0.05
        
        self.db_manager = DatabaseManager()
        self.ai_factory = AIClientFactory()
        
        self.deepseek_client = self.ai_factory.create_client("deepseek")
        self.qwen_client = self.ai_factory.create_client("qwen")
        
        self.crt_analyzer = CRTAnalyzer(timeframe_htf=mt5.TIMEFRAME_H1)
        self.mtf_analyzer = MTFAnalyzer(htf1=mt5.TIMEFRAME_M30, htf2=mt5.TIMEFRAME_H1)
        self.price_model = PriceEquationModel()
        self.tf_analyzer = TimeframeVisualAnalyzer()
        self.advanced_adapter = AdvancedMarketAnalysisAdapter()
        self.matrix_ml = MatrixMLAnalyzer()
        self.smc_analyzer = SMCAnalyzer()
        self.mfh_analyzer = MFHAnalyzer()
        
        self.optimizer = HybridOptimizer()
        
        self.last_bar_time = 0
        self.last_analysis_time = 0
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

    def execute_trade(self, signal, strength, sl_tp_params, entry_params=None):
        """
        执行交易指令，完全由大模型驱动
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
        positions = mt5.positions_get(symbol=self.symbol)
        has_position = len(positions) > 0 if positions else False
        
        # 如果有持仓且不是加仓指令，则不再开新仓
        if has_position and 'add' not in llm_action:
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
        elif llm_action == 'limit_buy':
            trade_type = "limit_buy"
            # 优先使用 limit_price (与 prompt 一致)，回退使用 entry_price
            price = entry_params.get('limit_price', entry_params.get('entry_price', 0.0)) if entry_params else 0.0
        elif llm_action == 'limit_sell':
            trade_type = "limit_sell"
            price = entry_params.get('limit_price', entry_params.get('entry_price', 0.0)) if entry_params else 0.0

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
            self._send_order(trade_type, price, explicit_sl, explicit_tp, comment=comment)



    def _send_order(self, type_str, price, sl, tp, comment=""):
        """底层下单函数"""
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
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        
        # 挂单需要不同的 filling type? 通常 Pending 订单不用 FOK，用 RETURN 或默认
        if "limit" in type_str:
             if 'type_filling' in request:
                 del request['type_filling']
        
        result = mt5.order_send(request)
        if result is None:
             logger.error("order_send 返回 None")
             return

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"下单失败 ({type_str}): {result.comment}, retcode={result.retcode}")
        else:
            logger.info(f"下单成功 ({type_str}) #{result.order}")
            self.send_telegram_message(f"✅ *Order Executed*\nType: `{type_str.upper()}`\nPrice: `{price}`\nSL: `{sl}`\nTP: `{tp}`")



                



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
            # 用户指令: "止盈和止损也需要根据大模型的最后整合分析结果来进行移动...而不是只有当新计算的 Trailing SL ... 还要高时，才再次更新"
            # 解读: 允许 SL/TP 动态调整，既可以收紧也可以放宽 (Breathing Stop)，以适应 LLM 对市场波动率和结构的最新判断。
            
            if has_new_params:
                current_sl_dist = atr * new_sl_multiplier
                current_tp_dist = atr * new_tp_multiplier
                
                # 计算建议的 SL/TP 价格 (基于当前价格)
                suggested_sl = 0.0
                suggested_tp = 0.0
                
                if type_pos == mt5.POSITION_TYPE_BUY:
                    suggested_sl = current_price - current_sl_dist
                    suggested_tp = current_price + current_tp_dist
                    
                    # 更新 SL: 始终更新 (移除 > sl 的限制)
                    # 注意: 这意味着如果 ATR 变大或 Multiplier 变大，SL 可能会下移 (放宽)
                    if abs(suggested_sl - sl) > point * 5: # 避免微小抖动
                        request['sl'] = suggested_sl
                        changed = True
                    
                    # 更新 TP
                    if abs(suggested_tp - tp) > point * 10:
                        request['tp'] = suggested_tp
                        changed = True

                elif type_pos == mt5.POSITION_TYPE_SELL:
                    suggested_sl = current_price + current_sl_dist
                    suggested_tp = current_price - current_tp_dist
                    
                    # 更新 SL: 始终更新 (移除 < sl 的限制)
                    if abs(suggested_sl - sl) > point * 5:
                        request['sl'] = suggested_sl
                        changed = True
                        
                    # 更新 TP
                    if abs(suggested_tp - tp) > point * 10:
                        request['tp'] = suggested_tp
                        changed = True
            
            # --- 2. 兜底移动止损 (Trailing Stop) ---
            # 如果上面没有因为 LLM 参数变化而更新，我们依然执行常规的 Trailing 逻辑 (仅收紧)
            # 只有当 'changed' 为 False 时才检查，避免冲突
            
            if not changed:
                if type_pos == mt5.POSITION_TYPE_BUY:
                    target_sl = current_price - (atr * new_sl_multiplier)
                    # 常规 Trailing: 仅收紧
                    current_req_sl = request['sl'] if request['sl'] > 0 else sl
                    if target_sl > current_req_sl:
                         if (current_price - target_sl) >= point * 10:
                            request['sl'] = target_sl
                            changed = True

                elif type_pos == mt5.POSITION_TYPE_SELL:
                    target_sl = current_price + (atr * new_sl_multiplier)
                    # 常规 Trailing: 仅收紧
                    current_req_sl = request['sl']
                    if current_req_sl == 0 or target_sl < current_req_sl:
                        if (target_sl - current_price) >= point * 10:
                            request['sl'] = target_sl
                            changed = True
                        
                # 2. 移动止盈 (Trailing Take Profit)
                dist_to_tp = current_price - tp
                if dist_to_tp > 0 and dist_to_tp < (atr * 0.5):
                    if signal == 'sell':
                        new_tp = current_price - (atr * max(new_tp_multiplier, 1.0))
                        if new_tp < tp:
                            request['tp'] = new_tp
                            changed = True
                            logger.info(f"🚀 移动止盈触发 (Sell): TP 延伸至 {new_tp:.2f}")
            
            if changed:
                logger.info(f"更新持仓 #{pos.ticket}: SL={request['sl']:.2f}, TP={request['tp']:.2f} (ATR x {new_sl_multiplier})")
                result = mt5.order_send(request)
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    logger.error(f"持仓修改失败: {result.comment}")
                    
            # --- 3. 检查信号平仓 ---
            # 如果最新信号转为反向或中立，且强度足够，可以考虑提前平仓
            # 但 execute_trade 已经处理了反向开仓(会先平仓)。
            # 这里只处理: 信号变 Weak/Neutral 时的防御性平仓 (如果需要)
            # 用户: "operate SL/TP, or close, open"
            if signal == 'neutral' and strategy_params:
                # 检查是否应该平仓
                # 简单逻辑: 如果盈利 > 0 且信号消失，落袋为安?
                # 或者依靠 Trailing Stop 自然离场。
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
                            mae = (min_low - open_price) / open_price * 100 # % (Negative)
                        elif action == 'SELL':
                            mfe = (open_price - min_low) / open_price * 100 # %
                            mae = (open_price - max_high) / open_price * 100 # % (Negative)
                            
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

    def evaluate_smc_params(self, params, df):
        """
        目标函数: 评估 SMC 策略参数的表现
        params: [ma_period, atr_threshold]
        完整回测逻辑，不简化处理
        """
        ma_period = int(params[0])
        atr_threshold = params[1]
        
        # 创建临时分析器
        analyzer = SMCAnalyzer()
        analyzer.ma_period = ma_period
        analyzer.atr_threshold = atr_threshold
        
        score = 0
        total_trades = 0
        win_trades = 0
        total_profit_pips = 0.0
        
        closes = df['close'].values
        
        # 我们需要足够的数据来计算 MA
        if len(closes) < ma_period + 50:
            return -1000
            
        # 完整的逐 K 线回测
        # 从 ma_period 开始，模拟每根 K 线作为"当前" K 线
        # 记录虚拟交易
        
        # 账户状态维护
        equity = 10000.0 # 初始净值
        balance = 10000.0 # 初始余额
        
        positions = [] # [{'type': 'buy', 'price': 1.0, 'vol': 0.1, 'sl': 0.9, 'tp': 1.2}, ...]
        
        in_trade = False
        trade_type = "" # buy, sell
        entry_price = 0.0
        entry_idx = 0
        
        # 为了提高效率，维护复杂的账户净值 
        # 这里的"不简化"指的是: 必须逐个遍历检查信号，而不是跳跃采样
        
        holding_period = 24 
        
        start_idx = ma_period
        end_idx = len(closes) - holding_period # 留出平仓空间
        
        # 预计算 MA (向量化) 以避免循环中重复计算
        # 注意: SMCAnalyzer 内部使用 rolling mean，这里为了模拟真实情况，
        # 我们应该让 Analyzer 自己算。但为了速度，我们可以手动计算指标传入 Analyzer?
        # 不，为了准确性，我们传入切片。虽然慢，但符合"不简化"的要求。
        # 优化: Analyzer 的 get_market_sentiment 只需要最近的数据。
        # 如果我们每次都传入完整 df.iloc[:i]，随着 i 增大，切片开销大。
        # 实际上 SMCAnalyzer.analyze 只需要最近 ma_period + small_buffer 的数据。
        
        lookback_needed = ma_period + 50
        
        for i in range(start_idx, end_idx):
            # 1. 更新账户净值 (Mark to Market)
            current_close = closes[i]
            current_high = df['high'].iloc[i]
            current_low = df['low'].iloc[i]
            
            unrealized_pl = 0.0
            
            # 检查现有持仓的盈亏和止损止盈
            active_positions = []
            for pos in positions:
                pl = 0.0
                if pos['type'] == 'buy':
                    pl = (current_close - pos['price']) * pos['vol'] * 100000 # 假设标准合约
                    
                    # 检查 SL/TP (基于 High/Low)
                    if current_low <= pos['sl']: # 触发止损
                        close_p = pos['sl']
                        realized_pl = (close_p - pos['price']) * pos['vol'] * 100000
                        balance += realized_pl
                        total_trades += 1
                        if realized_pl > 0: win_trades += 1
                        continue # 移除持仓
                    elif current_high >= pos['tp']: # 触发止盈
                        close_p = pos['tp']
                        realized_pl = (close_p - pos['price']) * pos['vol'] * 100000
                        balance += realized_pl
                        total_trades += 1
                        if realized_pl > 0: win_trades += 1
                        continue # 移除持仓
                        
                elif pos['type'] == 'sell':
                    pl = (pos['price'] - current_close) * pos['vol'] * 100000
                    
                    if current_high >= pos['sl']: # 触发止损
                        close_p = pos['sl']
                        realized_pl = (pos['price'] - close_p) * pos['vol'] * 100000
                        balance += realized_pl
                        total_trades += 1
                        if realized_pl > 0: win_trades += 1
                        continue
                    elif current_low <= pos['tp']: # 触发止盈
                        close_p = pos['tp']
                        realized_pl = (pos['price'] - close_p) * pos['vol'] * 100000
                        balance += realized_pl
                        total_trades += 1
                        if realized_pl > 0: win_trades += 1
                        continue
                
                unrealized_pl += pl
                active_positions.append(pos)
            
            positions = active_positions # 更新持仓列表
            equity = balance + unrealized_pl
            
            if equity <= 0: # 爆仓
                return -99999
            
            # 2. 生成信号
            # 获取上下文窗口
            window_start = max(0, i - lookback_needed)
            sub_df = df.iloc[window_start:i+1] # 注意 iloc 是左闭右开，所以要 i+1
            
            result = analyzer.analyze(sub_df)
            signal = result['signal']
            
            # 3. 交易逻辑
            # 简单的交易逻辑: 如果有信号且无持仓，则开仓
            # 如果有持仓，检查是否反转
            
            # 简单的 ATR 计算用于 SL/TP
            # 这里简单取最近 14 根 High-Low 的均值作为 ATR 估计
            atr_est = np.mean(df['high'].iloc[i-14:i] - df['low'].iloc[i-14:i])
            if atr_est <= 0: atr_est = current_close * 0.001
            
            if len(positions) == 0:
                if signal != 'neutral':
                    # 开仓
                    sl_dist = atr_est * 1.5
                    tp_dist = atr_est * 2.5
                    
                    sl = current_close - sl_dist if signal == 'buy' else current_close + sl_dist
                    tp = current_close + tp_dist if signal == 'buy' else current_close - tp_dist
                    
                    positions.append({
                        'type': signal,
                        'price': current_close,
                        'vol': 0.1, # 固定 0.1 手
                        'sl': sl,
                        'tp': tp,
                        'entry_idx': i
                    })
            else:
                # 检查平仓条件 (反转)
                # 假设单向持仓
                curr_pos = positions[0]
                if (curr_pos['type'] == 'buy' and signal == 'sell') or \
                   (curr_pos['type'] == 'sell' and signal == 'buy'):
                    
                    # 平仓
                    pl = 0.0
                    if curr_pos['type'] == 'buy':
                        pl = (current_close - curr_pos['price']) * curr_pos['vol'] * 100000
                    else:
                        pl = (curr_pos['price'] - current_close) * curr_pos['vol'] * 100000
                        
                    balance += pl
                    total_trades += 1
                    if pl > 0: win_trades += 1
                    positions = [] # 清空
                    
                    # 反手开仓
                    sl_dist = atr_est * 1.5
                    tp_dist = atr_est * 2.5
                    sl = current_close - sl_dist if signal == 'buy' else current_close + sl_dist
                    tp = current_close + tp_dist if signal == 'buy' else current_close - tp_dist
                    
                    positions.append({
                        'type': signal,
                        'price': current_close,
                        'vol': 0.1,
                        'sl': sl,
                        'tp': tp,
                        'entry_idx': i
                    })
                    
        # 处理最后一笔未平仓交易 (按当前价平仓)
        for pos in positions:
            pl = 0.0
            if pos['type'] == 'buy':
                pl = (closes[end_idx] - pos['price']) * pos['vol'] * 100000
            else:
                pl = (pos['price'] - closes[end_idx]) * pos['vol'] * 100000
            balance += pl
            total_trades += 1
            if pl > 0: win_trades += 1

        # 评分公式
        if total_trades == 0:
            return -100
            
        # 最终得分基于净值增长
        net_profit = balance - 10000.0
        
        # 综合评分: 净利润 + 胜率修正
        win_rate = win_trades / total_trades
        score = net_profit * (1 + win_rate)
        
        return score

    def optimize_strategy_parameters(self):
        """
        使用 自动选择的优化器 优化策略参数
        包含自动选择最佳算法的逻辑 (Auto-Selection)
        """
        logger.info("开始执行策略参数优化 (Auto-AO)...")
        
        # 1. 获取用于优化的历史数据 (最近 500 根 H1)
        df = self.get_market_data(500)
        if df is None or len(df) < 300:
            logger.warning("数据不足，跳过优化")
            return
            
        # 2. 定义搜索空间
        # [MA Period (100-300), ATR Threshold (0.001-0.005)]
        bounds = [(100, 300), (0.001, 0.005)]
        steps = [10, 0.0005] # 步长
        
        # 3. 定义目标函数 Wrapper
        def objective(params):
            return self.evaluate_smc_params(params, df)
            
        # 4. 自动选择或轮询优化算法
        # 简单逻辑: 随机选择或轮询，或者记录历史表现选择最好的
        # 这里演示: 随机选择一个算法进行本次优化
        import random
        algo_name = random.choice(list(self.optimizers.keys()))
        optimizer = self.optimizers[algo_name]
        
        logger.info(f"本次选择的优化算法: {algo_name}")
        
        # 5. 运行优化
        # 获取历史交易数据供自我学习
        historical_trades = self.db_manager.get_trade_performance_stats(limit=100)
        
        best_params, best_score = optimizer.optimize(
            objective, 
            bounds, 
            steps=steps, 
            epochs=5, # 快速优化
            historical_data=historical_trades # 传入历史数据
        )
        
        # 6. 验证和应用最佳参数
        # 如果得分是负数且非常低（如初始值-99999），说明优化未找到有效解，不应更新
        if best_score > -1000:
            new_ma = int(best_params[0])
            new_atr = best_params[1]
            
            logger.info(f"优化完成! Best Score: {best_score:.4f}")
            logger.info(f"更新参数: MA Period={new_ma}, ATR Threshold={new_atr:.4f}")
            
            self.smc_analyzer.ma_period = new_ma
            self.smc_analyzer.atr_threshold = new_atr
            
            self.send_telegram_message(
                f"🧬 *Auto-AO Optimization ({algo_name})*\n"
                f"Best Score: {best_score:.2f}\n"
                f"New Params:\n"
                f"• MA Period: {new_ma}\n"
                f"• ATR Thresh: {new_atr:.4f}"
            )
        else:
            logger.warning(f"优化失败或未找到正收益参数 (Score: {best_score:.4f})，保持原有参数。")
            self.send_telegram_message(
                f"🧬 *Auto-AO Optimization ({algo_name})*\n"
                f"Optimization Skipped (Low Score: {best_score:.2f})"
            )

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

    def calculate_optimized_sl_tp(self, trade_type, price, atr, market_context=None):
        """
        计算基于综合因素的优化止损止盈点
        结合: 14天 ATR, MFE/MAE 统计, 市场分析(Supply/Demand/FVG)
        """
        # 1. 基础波动率 (14天 ATR)
        # 确保传入的 ATR 是有效的 14周期 ATR
        if atr <= 0:
            atr = price * 0.005 # Fallback
            
        # 2. 历史绩效 (MFE/MAE)
        mfe_tp_dist = atr * 2.0 # 默认
        mae_sl_dist = atr * 1.5 # 默认
        
        try:
             stats = self.db_manager.get_trade_performance_stats(limit=100)
             
             trades = []
             if isinstance(stats, list):
                 trades = stats
             elif isinstance(stats, dict) and 'recent_trades' in stats:
                 trades = stats['recent_trades']
             
             if trades and len(trades) > 10:
                 mfes = [t.get('mfe', 0) for t in trades if t.get('mfe', 0) > 0]
                 maes = [t.get('mae', 0) for t in trades if t.get('mae', 0) > 0]
                 
                 if mfes and maes:
                     # 使用 ATR 倍数来标准化 MFE/MAE (假设 MFE/MAE 也是以 ATR 为单位存储，或者我们需要转换)
                     # 如果 DB 存的是百分比，我们需要将其转换为当前 ATR 倍数
                     # 这里简化处理：直接取百分比的中位数，然后转换为价格距离
                     
                     opt_tp_pct = np.percentile(mfes, 60) / 100.0 # 60分位数
                     opt_sl_pct = np.percentile(maes, 90) / 100.0 # 90分位数
                     
                     mfe_tp_dist = price * opt_tp_pct
                     mae_sl_dist = price * opt_sl_pct
        except Exception as e:
             logger.warning(f"MFE/MAE 计算失败: {e}")

        # 3. 市场结构调整 (Supply/Demand/FVG)
        # 从 market_context 中获取关键位
        struct_tp_price = 0.0
        struct_sl_price = 0.0
        
        if market_context:
            # 获取最近的 Supply/Demand 区间
            # 假设 market_context 包含 advanced_tech 或 ifvg 结果
            
            is_buy = 'buy' in trade_type
            
            # 寻找止盈点 (最近的阻力位/FVG)
            if is_buy:
                # 买入 TP: 最近的 Supply Zone 或 Bearish FVG 的下沿
                resistance_candidates = []
                if 'supply_zones' in market_context:
                    # 找出所有高于当前价格的 Supply Zone bottom
                    # 注意: zones 可能是 [(top, bottom), ...] 或其他结构，需要类型检查
                    raw_zones = market_context['supply_zones']
                    if raw_zones and isinstance(raw_zones, list):
                        try:
                            # 尝试解析可能的元组/列表结构
                            valid_zones = []
                            for z in raw_zones:
                                if isinstance(z, (list, tuple)) and len(z) >= 2:
                                    # 假设结构是 (top, bottom, ...)
                                    if z[1] > price: valid_zones.append(z[1])
                                elif isinstance(z, dict):
                                    # 假设结构是 {'top': ..., 'bottom': ...}
                                    btm = z.get('bottom')
                                    if btm and btm > price: valid_zones.append(btm)
                            
                            if valid_zones: resistance_candidates.append(min(valid_zones))
                        except Exception as e:
                            logger.warning(f"解析 Supply Zones 失败: {e}")
                
                if 'bearish_fvgs' in market_context:
                    raw_fvgs = market_context['bearish_fvgs']
                    if raw_fvgs and isinstance(raw_fvgs, list):
                        try:
                            valid_fvgs = []
                            for f in raw_fvgs:
                                if isinstance(f, dict):
                                    btm = f.get('bottom')
                                    if btm and btm > price: valid_fvgs.append(btm)
                            if valid_fvgs: resistance_candidates.append(min(valid_fvgs))
                        except Exception as e:
                            logger.warning(f"解析 Bearish FVG 失败: {e}")
                    
                if resistance_candidates:
                    struct_tp_price = min(resistance_candidates)
            
            else:
                # 卖出 TP: 最近的 Demand Zone 或 Bullish FVG 的上沿
                support_candidates = []
                if 'demand_zones' in market_context:
                    raw_zones = market_context['demand_zones']
                    if raw_zones and isinstance(raw_zones, list):
                        try:
                            valid_zones = []
                            for z in raw_zones:
                                if isinstance(z, (list, tuple)) and len(z) >= 2:
                                    # 假设结构是 (top, bottom, ...)
                                    if z[0] < price: valid_zones.append(z[0])
                                elif isinstance(z, dict):
                                    top = z.get('top')
                                    if top and top < price: valid_zones.append(top)
                            
                            if valid_zones: support_candidates.append(max(valid_zones))
                        except Exception as e:
                            logger.warning(f"解析 Demand Zones 失败: {e}")
                    
                if 'bullish_fvgs' in market_context:
                    raw_fvgs = market_context['bullish_fvgs']
                    if raw_fvgs and isinstance(raw_fvgs, list):
                        try:
                            valid_fvgs = []
                            for f in raw_fvgs:
                                if isinstance(f, dict):
                                    top = f.get('top')
                                    if top and top < price: valid_fvgs.append(top)
                            if valid_fvgs: support_candidates.append(max(valid_fvgs))
                        except Exception as e:
                            logger.warning(f"解析 Bullish FVG 失败: {e}")
                    
                if support_candidates:
                    struct_tp_price = max(support_candidates)

            # 寻找止损点 (最近的支撑位/结构点)
            # 这里简化逻辑，通常 SL 放在结构点外侧
            # 可以使用 recent swing high/low
            pass

        # 4. 综合计算
        # 逻辑: 
        # TP: 优先使用结构位 (Struct TP)，如果结构位太远或太近，使用 MFE/ATR 修正
        # SL: 使用 MAE/ATR 保护，但如果结构位 (如 Swing Low) 在附近，可以参考
        
        final_sl = 0.0
        final_tp = 0.0
        
        # 基础计算
        if 'buy' in trade_type:
            base_tp = price + mfe_tp_dist
            base_sl = price - mae_sl_dist
            
            # TP 融合
            if struct_tp_price > price:
                # 如果结构位比基础 TP 近，说明上方有阻力，保守起见设在阻力前
                # 如果结构位比基础 TP 远，可以尝试去拿，但最好分批。这里取加权平均或保守值
                if struct_tp_price < base_tp:
                    final_tp = struct_tp_price - (atr * 0.1) # 阻力下方一点点
                else:
                    final_tp = base_tp # 保持 MFE 目标，比较稳健
            else:
                final_tp = base_tp
                
            final_sl = base_sl # SL 主要靠统计风控
            
        else: # Sell
            base_tp = price - mfe_tp_dist
            base_sl = price + mae_sl_dist
            
            if struct_tp_price > 0 and struct_tp_price < price:
                if struct_tp_price > base_tp: # 支撑位在目标上方 (更近)
                    final_tp = struct_tp_price + (atr * 0.1)
                else:
                    final_tp = base_tp
            else:
                final_tp = base_tp
                
            final_sl = base_sl

        return final_sl, final_tp



    def optimize_short_term_params(self):
        """
        Optimize short-term strategy parameters (RVGI+CCI, IFVG)
        Executed every 1 hour
        """
        logger.info("Running Short-Term Parameter Optimization (WOAm)...")
        
        # 1. Get Data (Last 200 M15 candles)
        df = self.get_market_data(200)
        if df is None or len(df) < 100:
            return

        # 2. Define Objective Function
        # Optimize for RVGI+CCI and IFVG parameters
        def objective(params):
            # Params: [rvgi_sma, rvgi_cci, ifvg_gap]
            p_rvgi_sma = int(params[0])
            p_rvgi_cci = int(params[1])
            p_ifvg_gap = int(params[2])
            
            # Run simulation
            # We use a simplified simulation here for speed
            # Calculate indicators on the whole dataframe
            try:
                # RVGI+CCI
                # We need to call analyze_rvgi_cci_strategy for each candle? No, too slow.
                # We rely on the fact that we can calculate the whole series.
                # But the Analyzer methods currently return a single snapshot for the last candle.
                # To do this efficiently without rewriting everything, we iterate over the last 50 candles.
                
                score = 0
                trades = 0
                wins = 0
                
                # Iterate through the last 50 candles as "current"
                for i in range(len(df)-50, len(df)):
                    sub_df = df.iloc[:i+1]
                    future_close = df.iloc[i+1]['close'] if i+1 < len(df) else df.iloc[i]['close']
                    current_close = df.iloc[i]['close']
                    
                    # RVGI Signal
                    res_rvgi = self.advanced_adapter.analyze_rvgi_cci_strategy(
                        sub_df, sma_period=p_rvgi_sma, cci_period=p_rvgi_cci
                    )
                    
                    # IFVG Signal
                    res_ifvg = self.advanced_adapter.analyze_ifvg(
                        sub_df, min_gap_points=p_ifvg_gap
                    )
                    
                    signal = 0
                    if res_rvgi['signal'] == 'buy': signal += 1
                    elif res_rvgi['signal'] == 'sell': signal -= 1
                    
                    if res_ifvg['signal'] == 'buy': signal += 1
                    elif res_ifvg['signal'] == 'sell': signal -= 1
                    
                    if signal > 0: # Buy
                        trades += 1
                        if future_close > current_close: wins += 1
                        else: score -= 1
                    elif signal < 0: # Sell
                        trades += 1
                        if future_close < current_close: wins += 1
                        else: score -= 1
                        
                if trades == 0: return 0
                win_rate = wins / trades
                score += (win_rate * 100)
                return score
                
            except Exception:
                return -100

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

    def run(self):
        """主循环"""
        if not self.initialize_mt5():
            return

        logger.info(f"启动 AI 自动交易机器人 - {self.symbol}")
        self.send_telegram_message(f"🤖 *AI Bot Started*\nSymbol: {self.symbol}\nTimeframe: {self.timeframe}")
        
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
                # 用户需求: 每15分钟执行一次分析 (即跟随 M15 K 线收盘)
                is_new_bar = current_bar_time != self.last_bar_time
                
                if is_new_bar:
                    if self.last_bar_time == 0:
                        logger.info("首次运行，立即执行分析...")
                    else:
                        logger.info(f"发现新 K 线: {datetime.fromtimestamp(current_bar_time)}")
                    
                    self.last_bar_time = current_bar_time
                    self.last_analysis_time = time.time()
                    
                    # 2. 获取数据并分析
                    # ... 这里的代码保持不变 ...
                    # PEM 需要至少 108 根 K 线 (ma_fast_period)，MTF 更新 Zones 需要 500 根
                    # 为了确保所有模块都有足够数据，我们获取 300 根 (MTF Zones 在 update_zones 内部单独获取)
                    df = self.get_market_data(300) 
                    
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

                        # --- 3.3 DeepSeek 分析 ---
                        logger.info("正在调用 DeepSeek 分析市场结构...")
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
                        structure = self.deepseek_client.analyze_market_structure(market_snapshot, extra_analysis=extra_analysis)
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
                        
                        # 获取历史交易绩效 (MFE/MAE)
                        trade_stats = self.db_manager.get_trade_performance_stats(limit=50)
                        
                        # 获取当前持仓状态 (供 Qwen 决策)
                        positions = mt5.positions_get(symbol=self.symbol)
                        current_positions_list = []
                        if positions:
                            for pos in positions:
                                cur_mfe, cur_mae = self.get_position_stats(pos)
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
                                    "mae_pct": cur_mae
                                })
                        
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
                        
                        strategy = self.qwen_client.optimize_strategy_logic(structure, market_snapshot, technical_signals=technical_signals, current_positions=current_positions_list)
                        
                        # --- 参数自适应优化 (Feedback Loop) ---
                        # 将大模型的参数优化建议应用到当前运行的算法中
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
                            final_signal = "limit_buy"
                        elif qw_action in ['sell_limit', 'limit_sell']:
                            final_signal = "limit_sell"
                        elif qw_action in ['close_buy', 'close_sell', 'close']:
                            final_signal = "close" # 特殊信号: 平仓
                        elif qw_action == 'hold':
                            final_signal = "hold"
                        
                        qw_signal = final_signal if final_signal not in ['hold', 'close'] else 'neutral'
                        
                        # --- 3.5 最终决策 (LLM Centric) ---
                        # 依据用户指令：完全基于大模型的最终决策 (以 Qwen 的 Action 为主)
                        # Qwen 已经接收了所有技术指标(technical_signals)作为输入，因此它的输出即为"集合最终分析结果"
                        
                        # final_signal 已在上面由 qw_action 解析得出
                        reason = strategy.get('reason', 'LLM Decision')
                        
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
                        
                        if final_signal in ['buy', 'sell', 'limit_buy', 'limit_sell']:
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
                        if final_signal in ['sell', 'limit_sell']:
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

                        # 格式化 DeepSeek 和 Qwen 的详细分析
                        ds_analysis_text = f"• Signal: {ds_signal.upper()}\n"
                        ds_analysis_text += f"• Conf: {ds_score}/100\n"
                        ds_analysis_text += f"• Pred: {ds_pred}"
                        
                        qw_analysis_text = f"• Action: {qw_action.upper()}\n"
                        if param_updates:
                            qw_analysis_text += f"• Params Updated: {len(param_updates)} items"

                        analysis_msg = (
                            f"🤖 *AI Gold Strategy Insight*\n"
                            f"Symbol: `{self.symbol}` | TF: `{self.tf_name}`\n"
                            f"Time: {datetime.now().strftime('%H:%M:%S')}\n\n"
                            
                            f"🧠 *AI Consensus Analysis*\n"
                            f"• Final Decision: *{display_decision}* (Strength: {strength:.0f}%)\n"
                            f"• Rationale: _{reason}_\n\n"
                            
                            f"🕵️ *Model Details*\n"
                            f"*DeepSeek (Market Structure):*\n{ds_analysis_text}\n"
                            f"*Qwen (Strategy Logic):*\n{qw_analysis_text}\n\n"
                            
                            f"🎯 *Optimal Trade Setup*\n"
                            f"• Direction: `{trade_dir_for_calc.upper()}`\n"
                            f"• Ref Entry: `{ref_price:.2f}`\n"
                            f"• 🛑 Opt. SL: `{opt_sl:.2f}`\n"
                            f"• 🏆 Opt. TP: `{opt_tp:.2f}`\n"
                            f"• R:R Ratio: `{rr_str}`\n\n"
                            
                            f"📊 *Market X-Ray*\n"
                            f"• State: `{structure.get('market_state', 'N/A')}`\n"
                            f"• Volatility: `{volatility_info}`\n"
                            f"• Tech Confluence: {matching_count}/{valid_tech_count} signals match\n"
                            f"• Key Signals: SMC[{smc_result['signal']}], CRT[{crt_result['signal']}], MTF[{mtf_result['signal']}]\n\n"
                            
                            f"💼 *Account & Positions*\n"
                            f"{pos_summary}"
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
                                entry_params
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
