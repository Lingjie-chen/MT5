import requests
import json
import logging
import time
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from datetime import datetime, date

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CustomJSONEncoder(json.JSONEncoder):
    """自定义JSON编码器，处理Timestamp等非序列化类型"""
    def default(self, o):
        if isinstance(o, (datetime, date, pd.Timestamp)):
            return o.isoformat()
        if isinstance(o, (pd.Series, pd.DataFrame)):
            return o.to_dict()
        if isinstance(o, (np.integer, int)):
            return int(o)
        if isinstance(o, (np.floating, float)):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        return super().default(o)

class QwenClient:
    """
    Qwen3 API客户端，用于策略逻辑优化、动态止盈止损生成和信号强度判断
    使用硅基流动API服务，遵循ValueCell的API调用模式
    """
    def __init__(self, api_key: str, base_url: str = "https://api.siliconflow.cn/v1", model: str = "Qwen/Qwen3-VL-235B-A22B-Thinking"):
        """
        初始化Qwen客户端
        
        Args:
            api_key (str): 硅基流动API密钥
            base_url (str): API基础URL，默认为https://api.siliconflow.cn/v1
            model (str): 使用的模型名称，默认为Qwen/Qwen3-VL-235B-A22B-Thinking
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 启用JSON模式，遵循ValueCell的实现
        self.enable_json_mode = True
    
    def _call_api(self, endpoint: str, payload: Dict[str, Any], max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        调用Qwen API，支持重试机制
        基于ValueCell的API调用模式，增强了错误处理和日志记录
        
        Args:
            endpoint (str): API端点
            payload (Dict[str, Any]): 请求负载
            max_retries (int): 最大尝试次数，默认为3 (增强稳定性)
        
        Returns:
            Optional[Dict[str, Any]]: API响应，失败返回None
        """
        url = f"{self.base_url}/{endpoint}"
        
        for retry in range(max_retries):
            response = None
            try:
                # 增加超时时间到60秒，提高在网络不稳定情况下的成功率
                response = requests.post(url, headers=self.headers, json=payload, timeout=60)
                
                # 详细记录响应状态
                logger.debug(f"API响应状态码: {response.status_code}, 模型: {self.model}, 重试: {retry+1}/{max_retries}")
                
                # 处理不同状态码
                if response.status_code == 401:
                    logger.error(f"API认证失败，状态码: {response.status_code}，请检查API密钥是否正确")
                    return None
                elif response.status_code == 403:
                    logger.error(f"API访问被拒绝，状态码: {response.status_code}，请检查API密钥权限")
                    return None
                elif response.status_code == 429:
                    logger.warning(f"API请求频率过高，状态码: {response.status_code}，进入退避重试")
                elif response.status_code >= 500:
                    logger.error(f"API服务器错误，状态码: {response.status_code}")
                
                response.raise_for_status()
                
                # 解析响应并添加调试信息
                response_json = response.json()
                logger.info(f"API调用成功，状态码: {response.status_code}, 模型: {self.model}")
                return response_json
            except requests.exceptions.ConnectionError as e:
                logger.error(f"API连接失败 (重试 {retry+1}/{max_retries}): {e}")
                logger.error(f"请求URL: {url}")
                logger.error("请检查网络连接和API服务可用性")
            except requests.exceptions.Timeout as e:
                logger.error(f"API请求超时 (重试 {retry+1}/{max_retries}): {e}")
                logger.error(f"请求URL: {url}")
                logger.error("请检查网络连接和API服务响应时间")
            except requests.exceptions.HTTPError as e:
                logger.error(f"API HTTP错误 (重试 {retry+1}/{max_retries}): {e}")
                logger.error(f"请求URL: {url}")
                if response:
                    logger.error(f"响应内容: {response.text[:200]}...")
            except requests.exceptions.RequestException as e:
                logger.error(f"API请求异常 (重试 {retry+1}/{max_retries}): {e}")
                logger.error(f"请求URL: {url}")
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {e}")
                if response:
                    logger.error(f"响应内容: {response.text}")
                return None
            except Exception as e:
                logger.error(f"API调用意外错误: {e}")
                logger.exception("完整错误堆栈:")
                return None
            
            if retry < max_retries - 1:
                # 线性延迟重试，提高网络不稳定情况下的成功率
                retry_delay = min(5 * (retry + 1), 30)  # 每次增加5秒，最大30秒
                logger.info(f"等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
            else:
                logger.error(f"API调用失败，已达到最大重试次数 {max_retries}")
                return None
    
    def optimize_strategy_logic(self, deepseek_analysis: Dict[str, Any], current_market_data: Dict[str, Any], technical_signals: Optional[Dict[str, Any]] = None, current_positions: Optional[List[Dict[str, Any]]] = None, performance_stats: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        优化策略逻辑，基于DeepSeek的情绪得分调整入场条件
        基于ValueCell的实现，支持JSON模式输出
        
        Args:
            deepseek_analysis (Dict[str, Any]): DeepSeek的市场分析结果
            current_market_data (Dict[str, Any]): 当前市场数据
            technical_signals (Optional[Dict[str, Any]]): 其他技术模型的信号（CRT, Price Equation等）
            current_positions (Optional[List[Dict[str, Any]]]): 当前持仓信息 (用于决定加仓或平仓)
            performance_stats (Optional[List[Dict[str, Any]]]): 历史交易绩效统计 (用于自学习)
        
        Returns:
            Dict[str, Any]: 优化后的策略参数
        """
        tech_context = ""
        perf_context = ""
        pos_context = ""
        
        if current_positions:
            pos_context = f"\n当前持仓状态 (包含实时 MFE/MAE 和 R-Multiple):\n{json.dumps(current_positions, indent=2, cls=CustomJSONEncoder)}\n"
        else:
            pos_context = "\n当前无持仓。\n"

        # 处理当前挂单信息
        open_orders = current_market_data.get('open_orders', [])
        orders_context = ""
        if open_orders:
             orders_context = f"\n当前挂单状态 (Limit/SL/TP):\n{json.dumps(open_orders, indent=2, cls=CustomJSONEncoder)}\n"
        else:
             orders_context = "\n当前无挂单。\n"

        # 处理性能统计 (优先使用 explicit argument)
        stats_to_use = performance_stats
        
        # 兼容旧逻辑：如果 explicit 为空，尝试从 technical_signals 中提取
        if not stats_to_use and technical_signals and isinstance(technical_signals.get('performance_stats'), list):
             stats_to_use = technical_signals.get('performance_stats')

        if stats_to_use:
            # 构建 MFE/MAE 象限分析数据
            recent_trades = []
            summary_stats = {}
            
            try:
                if isinstance(stats_to_use, list):
                    # Robust filtering
                    valid_trades = [t for t in stats_to_use if isinstance(t, dict)]
                    recent_trades = valid_trades
                    
                    if len(recent_trades) > 0:
                         mfe_list = [t.get('mfe', 0) for t in recent_trades if t.get('mfe') is not None]
                         mae_list = [t.get('mae', 0) for t in recent_trades if t.get('mae') is not None]
                         
                         # Calculate Win Rate and Profit Factor
                         wins = len([t for t in recent_trades if t.get('profit', 0) > 0])
                         total_profit = sum([t.get('profit', 0) for t in recent_trades if t.get('profit', 0) > 0])
                         total_loss = abs(sum([t.get('profit', 0) for t in recent_trades if t.get('profit', 0) < 0]))
                         
                         summary_stats = {
                             'avg_mfe': sum(mfe_list)/len(mfe_list) if mfe_list else 0,
                             'avg_mae': sum(mae_list)/len(mae_list) if mae_list else 0,
                             'trade_count': len(recent_trades),
                             'win_rate': (wins / len(recent_trades)) * 100 if recent_trades else 0,
                             'profit_factor': (total_profit / total_loss) if total_loss > 0 else 99.9
                         }
                elif isinstance(stats_to_use, dict):
                    summary_stats = stats_to_use
                    recent_trades = stats_to_use.get('recent_trades', [])
                    if not isinstance(recent_trades, list): recent_trades = []

                trades_summary = ""
                if recent_trades:
                    trades_summary = json.dumps(recent_trades[:10], indent=2, cls=CustomJSONEncoder)

                perf_context = (
                    f"\n历史交易绩效参考 (用于 MFE/MAE 象限分析与 SL/TP 优化):\n"
                    f"- 样本交易数: {summary_stats.get('trade_count', 0)}\n"
                    f"- 胜率 (Win Rate): {summary_stats.get('win_rate', 0):.2f}%\n"
                    f"- 盈亏比 (Profit Factor): {summary_stats.get('profit_factor', 0):.2f}\n"
                    f"- 平均 MFE: {summary_stats.get('avg_mfe', 0):.2f}%\n"
                    f"- 平均 MAE: {summary_stats.get('avg_mae', 0):.2f}%\n"
                    f"- 最近交易详情 (用于分析体质): \n{trades_summary}\n"
                )
            except Exception as e:
                logger.error(f"Error processing stats_to_use: {e}")
                perf_context = "\n历史交易绩效: 数据解析错误\n"

        if technical_signals:
            # 从 technical_signals 中移除 stats 以免重复 (浅拷贝处理)
            sigs_copy = technical_signals.copy()
            if 'performance_stats' in sigs_copy:
                del sigs_copy['performance_stats']
            tech_context = f"\n其他技术模型信号 (CRT/PriceEq/Hybrid):\n{json.dumps(sigs_copy, indent=2, cls=CustomJSONEncoder)}\n"

        prompt = f"""
        作为专业的量化交易策略优化专家，你是混合交易系统的核心决策层。请根据DeepSeek的市场分析结果、当前市场数据、当前持仓状态以及其他技术模型的信号，优化策略逻辑并做出最终执行决定。
        
        你现在拥有全套高级算法的信号支持，请特别关注SMC策略与其他信号的共振：
        1. **SMC (Smart Money Concepts) - 核心信号**:
           - 确认DeepSeek分析中识别的OB (订单块) 和 FVG (流动性缺口) 是否与当前价格位置匹配。
           - 寻找流动性扫荡后的反转确认 (例如: 扫荡低点后出现MSB)。
           - 在溢价区(Premium)寻找卖出机会，在折价区(Discount)寻找买入机会。
        2. **多模型共识**: 结合 IFVG, CRT, RVGI+CCI, MFH, MTF 的信号。如果SMC信号与其他模型冲突，请依据 DeepSeek 的市场结构分析和 MTF (多周期) 趋势来裁决。
        
        DeepSeek市场分析结果：
        {json.dumps(deepseek_analysis, indent=2, cls=CustomJSONEncoder)}
        
        当前市场数据：
        {json.dumps(current_market_data, indent=2, cls=CustomJSONEncoder)}
        {pos_context}
        {tech_context}
        {perf_context}
        
        请综合考虑所有信号，并输出最终的交易决策 (Action):
        1. DeepSeek 提供宏观结构和趋势判断。
        2. CRT (Candle Range Theory) 提供流动性猎取和反转信号。
        3. Price Equation 提供纯数学的动量预测。
        4. Hybrid Optimizer 提供加权共识。
        5. **MFE/MAE 象限分析与 SL/TP 优化**:
           - **数据**: 请参考提供的历史交易详情 (MFE, MAE, Profit)。
           - **分析**: 
             - 观察高盈利交易的 MFE 分布，将 TP 设定在能捕获大部分 MFE 的位置 (如 80% 分位)。
             - 观察亏损交易的 MAE 分布，将 SL 设定在能过滤掉"第一象限 (低MFE 高MAE)"交易的位置。
             - **动态调整**: 如果近期 MAE 普遍变大且盈利困难，说明市场波动剧烈或策略失效，请收紧 SL 或暂停交易。
        6. **持仓管理**: 
           - 如果有持仓且趋势延续，请考虑**加仓 (Add Position)**。
           - 如果有持仓但趋势反转或动能减弱，请考虑**平仓 (Close Position)** 或 **减仓 (Reduce Position)**。
           - **智能平仓逻辑 (Smart Exit)**: 如果当前持仓已有盈利，且满足以下任一条件，请果断建议平仓 (action: 'close')：
             1. **盈利达标**: 当前盈利已经达到合理的风险回报比 (例如 R-Multiple >= 1.5)，且市场情绪转弱 (Sentiment Score 下降)。
             2. **结构阻力**: 价格到达强阻力位/支撑位 (SMC OB/Liquidity)，且出现反转信号。
             3. **情绪满足**: 即使未到 TP，但 DeepSeek 认为当前市场情绪已充分释放 (Overextended)，且获利已足够安全。
           - 如果无持仓且信号明确，请**开仓 (Open Position)**。
        
        **重要提示**: 为了避免错过行情或在反转时错误成交，**请尽量使用市价单 (Market Execution)**，不要使用限价单 (Limit Orders)。如果看多，直接 Buy；如果看空，直接 Sell。

        请提供以下优化结果，并确保分析全面、逻辑严密，不要使用省略号或简化描述。**请务必使用中文进行输出（Strategy Logic Rationale 部分）**：
        1. 核心决策：buy/sell/hold/close/add_buy/add_sell (请避免使用 limit 挂单)
        2. 入场/加仓条件：基于情绪得分和技术指标的优化规则。
        3. 出场/减仓条件：**基于 MFE/MAE 分析的合理优化止盈止损点**。请直接给出具体价格（sl_price, tp_price）。
           - **Stop Loss (SL)**: 参考 MAE 分布，设定在能过滤掉大部分"假突破"但又能控制最大亏损的位置。结合市场结构，放在最近的 Swing High/Low 或结构位之外。
           - **Take Profit (TP)**: 参考 MFE 分布，设定在能捕获 80% 潜在收益的位置。结合市场结构，放在下一个 Liquidity Pool (流动性池) 或 OB 之前。
           - 不要使用 ATR 倍数，请给出具体的数值。
        4. 仓位管理：针对当前持仓的具体操作建议（如加仓、减仓、反手）。
        5. 风险管理建议：针对当前市场状态的风险控制措施。
        6. **参数自适应优化建议 (Parameter Optimization)**: 
           - 请分析当前市场状态 (波动率、趋势强度)，并评估现有算法参数的适用性。
           - 给出针对 SMC, MFH, MatrixML, Grid Strategy 或 Optimization Algorithm (GWO/WOAm/etc) 的具体参数调整建议。
           - 例如: "SMC ATR 阈值过低，建议提高到 0.003 以过滤噪音" 或 "建议切换到 DE 优化器以增加探索能力"。
           - **Grid Strategy 参数**: 请根据市场波动率调整 `grid_step_points` (例如高波动时增大间距) 和 `max_grid_steps`。如果建议启用网格加仓，请设置 `allow_add` 为 true。

        7. 策略逻辑详解：请详细解释做出上述决策的逻辑链条 (Strategy Logic Rationale)，**必须包含对 SMC 信号的解读、MFE/MAE 数据的分析以及为何选择该 SL/TP 点位**。
        
        请以JSON格式返回结果，包含以下字段：
        - action: str ("buy", "sell", "hold", "close", "add_buy", "add_sell")
        - entry_conditions: dict (包含 "trigger_type": "market", "confirmation")
        - exit_conditions: dict (包含 "sl_price", "tp_price", "close_rationale") **确保 sl_price 和 tp_price 是具体的数字**
        - position_management: dict (包含 "action", "volume_percent", "reason")
        - position_size: float
        - signal_strength: int
        - risk_management: dict
        - parameter_updates: dict (包含 "smc_atr_threshold": float, "mfh_learning_rate": float, "active_optimizer": str (GWO/WOAm/DE/COAm/BBO/TETA), "grid_settings": dict, "reason": str)
            - **grid_settings**: dict (包含 "grid_step_points": int, "max_grid_steps": int, "allow_add": bool, "lot_type": str, "tp_steps": dict)
        - strategy_rationale: str (中文)
        """
        
        # 构建payload，遵循ValueCell的实现
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一位专业的量化交易策略优化专家，擅长基于市场分析结果调整交易参数。请始终使用中文回复分析内容。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1500,
            "stream": False
        }
        
        # 启用JSON模式，ValueCell推荐使用JSON模式处理结构化输出
        if self.enable_json_mode:
            payload["response_format"] = {"type": "json_object"}
        
        response = self._call_api("chat/completions", payload)
        if response and "choices" in response:
            try:
                message_content = response["choices"][0]["message"]["content"]
                # Log full response for detailed analysis
                logger.info(f"收到模型响应: {message_content}")
                
                optimized_strategy = json.loads(message_content)
                
                if not isinstance(optimized_strategy, dict):
                    logger.error(f"Qwen响应格式错误 (期望dict, 实际{type(optimized_strategy)}): {optimized_strategy}")
                    return {
                        "action": "hold",
                        "entry_conditions": {"trigger_type": "market"},
                        "exit_conditions": {"sl_atr_multiplier": 1.5, "tp_atr_multiplier": 2.5},
                        "position_size": 0.01,
                        "signal_strength": 50,
                        "risk_management": {"max_risk": 0.02},
                        "strategy_rationale": "响应格式错误"
                    }

                # 强制统一 position_size 为 0.01 (User Request)
                optimized_strategy["position_size"] = 0.01
                
                return optimized_strategy
            except json.JSONDecodeError as e:
                logger.error(f"解析Qwen响应失败: {e}")
                logger.error(f"原始响应: {response}")
                # 返回默认策略参数
                return {
                    "action": "hold",
                    "entry_conditions": {"trigger_type": "market"},
                    "exit_conditions": {"sl_atr_multiplier": 1.5, "tp_atr_multiplier": 2.5},
                    "position_size": 0.01,
                    "signal_strength": 50,
                    "risk_management": {"max_risk": 0.02},
                    "strategy_rationale": "解析失败，使用默认参数"
                }
        return {
            "action": "hold",
            "entry_conditions": {"trigger_type": "market"},
            "exit_conditions": {"sl_atr_multiplier": 1.5, "tp_atr_multiplier": 2.5},
            "position_size": 0.01,
            "signal_strength": 50,
            "risk_management": {"max_risk": 0.02},
            "strategy_rationale": "API调用失败，使用默认参数"
        }
    
    def generate_dynamic_stoploss_takeprofit(self, volatility: float, market_state: str, signal_strength: int) -> Dict[str, float]:
        """
        [DEPRECATED] 该方法已弃用。
        现在 SL/TP 完全由 optimize_strategy_logic 中的 MFE/MAE/SMC 逻辑决定，不再使用基于 ATR 倍数的动态生成。
        保留此方法仅为了接口兼容性，返回默认占位值。
        """
        logger.warning("generate_dynamic_stoploss_takeprofit 被调用，但策略已切换为固定 SL/TP 模式。")
        return {"take_profit": 0.0, "stop_loss": 0.0}
    
    def judge_signal_strength(self, deepseek_signal: Dict[str, Any], technical_indicators: Dict[str, Any]) -> int:
        """
        对DeepSeek生成的初步信号进行二次验证，判断信号强度
        
        Args:
            deepseek_signal (Dict[str, Any]): DeepSeek生成的信号
            technical_indicators (Dict[str, Any]): 技术指标数据
        
        Returns:
            int: 信号强度，0-100，越高表示信号越可靠
        """
        prompt = f"""
        作为专业的交易信号分析师，请评估以下交易信号的强度：
        
        DeepSeek信号：
        {json.dumps(deepseek_signal, indent=2)}
        
        技术指标：
        {json.dumps(technical_indicators, indent=2)}
        
        请基于以下因素评估信号强度(0-100)：
        1. 多指标共振：技术指标是否一致支持该信号
        2. 市场结构：当前市场状态是否有利于该信号
        3. 成交量：成交量是否支持价格走势
        4. 波动率：当前波动率是否适合该信号
        5. 历史表现：类似情况下信号的历史成功率
        
        请只返回一个数字，不要包含任何其他文字或解释。
        """
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一位专业的交易信号分析师，擅长评估交易信号的强度和可靠性。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 10
        }
        
        response = self._call_api("chat/completions", payload)
        if response and "choices" in response:
            try:
                strength = int(response["choices"][0]["message"]["content"].strip())
                # 确保强度在0-100之间
                return max(0, min(100, strength))
            except ValueError:
                logger.error("无法解析信号强度")
        return 50
    
    def calculate_kelly_criterion(self, win_rate: float, risk_reward_ratio: float) -> float:
        """
        计算凯利准则，用于确定最优仓位
        
        Args:
            win_rate (float): 胜率(0-1)
            risk_reward_ratio (float): 风险回报比
        
        Returns:
            float: 最优仓位比例
        """
        prompt = f"""
        请根据以下参数计算凯利准则：
        胜率：{win_rate}
        风险回报比：{risk_reward_ratio}
        
        请只返回一个数字，表示最优仓位比例(0-1之间)，不要包含任何其他文字或解释。
        """
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一位专业的资金管理专家，擅长计算凯利准则。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 10
        }
        
        response = self._call_api("chat/completions", payload)
        if response and "choices" in response:
            try:
                kelly = float(response["choices"][0]["message"]["content"].strip())
                # 确保凯利比例在0-1之间
                return max(0.0, min(1.0, kelly))
            except ValueError:
                logger.error("无法解析凯利比例")
        # 使用传统凯利公式计算默认值
        default_kelly = win_rate - ((1 - win_rate) / risk_reward_ratio)
        return max(0.0, min(1.0, default_kelly))


def main():
    """
    主函数用于测试Qwen客户端
    """
    # 示例使用，实际需要替换为有效的API密钥
    api_key = "your_qwen_api_key"
    client = QwenClient(api_key)
    
    # 示例DeepSeek分析结果
    deepseek_analysis = {
        "market_state": "trend_up",
        "support_levels": [1.0800, 1.0750],
        "resistance_levels": [1.0900, 1.0950],
        "structure_score": 85,
        "short_term_prediction": "bullish",
        "indicator_analysis": "EMA黄金交叉，RSI处于中性区域"
    }
    
    # 示例当前市场数据
    current_market_data = {
        "symbol": "EURUSD",
        "timeframe": "H1",
        "prices": {
            "open": 1.0850,
            "high": 1.0875,
            "low": 1.0840,
            "close": 1.0865,
            "volume": 1234567
        },
        "indicators": {
            "ema_fast": 1.0855,
            "ema_slow": 1.0848,
            "rsi": 65.2,
            "atr": 0.0025
        }
    }
    
    # 测试策略优化
    optimized_strategy = client.optimize_strategy_logic(deepseek_analysis, current_market_data)
    print("优化后的策略参数:")
    print(json.dumps(optimized_strategy, indent=2, ensure_ascii=False))
    
    # 测试动态止盈止损生成
    sl_tp = client.generate_dynamic_stoploss_takeprofit(0.25, "trend_up", 85)
    print(f"\n动态止盈止损: {sl_tp}")
    
    # 测试信号强度判断
    deepseek_signal = {"signal": "buy", "confidence": 0.8}
    technical_indicators = {"ema_crossover": 1, "rsi": 65.2, "volume_increase": True}
    signal_strength = client.judge_signal_strength(deepseek_signal, technical_indicators)
    print(f"\n信号强度: {signal_strength}")
    
    # 测试凯利准则计算
    kelly = client.calculate_kelly_criterion(0.6, 1.5)
    print(f"\n凯利准则: {kelly:.2f}")

if __name__ == "__main__":
    main()
