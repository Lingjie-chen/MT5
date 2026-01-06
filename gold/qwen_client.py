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
                # 增加超时时间到120秒，提高在网络不稳定情况下的成功率
                response = requests.post(url, headers=self.headers, json=payload, timeout=120)
                
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
                logger.error(f"请求URL: {repr(url)}")
                logger.error("请检查网络连接和API服务可用性")
            except requests.exceptions.Timeout as e:
                logger.error(f"API请求超时 (重试 {retry+1}/{max_retries}): {e}")
                logger.error(f"请求URL: {repr(url)}")
                logger.error("请检查网络连接和API服务响应时间")
            except requests.exceptions.HTTPError as e:
                logger.error(f"API HTTP错误 (重试 {retry+1}/{max_retries}): {e}")
                logger.error(f"请求URL: {repr(url)}")
                if response:
                    logger.error(f"响应内容: {response.text[:200]}...")
            except requests.exceptions.RequestException as e:
                logger.error(f"API请求异常 (重试 {retry+1}/{max_retries}): {e}")
                logger.error(f"请求URL: {repr(url)}")

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
                # 延长重试等待时间，应对服务器过载
                retry_delay = min(15 * (retry + 1), 60)  # 每次增加15秒，最大60秒
                logger.info(f"等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
            else:
                logger.error(f"API调用失败，已达到最大重试次数 {max_retries}")
                return None
    
    def analyze_market_sentiment(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        [New] Qwen 独立市场结构与情绪分析 (黄金版)
        用于与 DeepSeek 的分析进行交叉验证 (Double Check)
        
        Args:
            market_data (Dict[str, Any]): 市场数据
            
        Returns:
            Dict[str, Any]: 情绪分析结果
        """
        prompt = f"""
        作为专业的黄金(XAUUSD)交易员，请根据以下市场数据进行独立的市场结构与情绪分析：
        
        市场数据:
        {json.dumps(market_data, indent=2, cls=CustomJSONEncoder)}
        
        请重点分析：
        1. **黄金特有结构**: 关注亚盘/欧盘/美盘的盘口特征。
        2. **情绪得分 (Sentiment Score)**: -1 (极度看空) 到 1 (极度看多)。
        3. **避险与通胀**: 结合当前波动率判断市场属性（单边趋势还是震荡洗盘）。
        
        请以JSON格式返回：
        - sentiment: str ("bullish", "bearish", "neutral")
        - sentiment_score: float (-1.0 to 1.0)
        - structure_bias: str (e.g., "Range Bound", "Bullish Breakout", "Bearish Correction")
        - key_observation: str (简短的中文分析)
        """
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一位拥有20年经验的华尔街黄金交易员。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 500,
            "stream": False,
            "response_format": {"type": "json_object"}
        }
        
        response = self._call_api("chat/completions", payload)
        if response and "choices" in response:
            try:
                content = response["choices"][0]["message"]["content"]
                return json.loads(content)
            except json.JSONDecodeError:
                logger.error("解析 Qwen 情绪分析失败")
        
        return {"sentiment": "neutral", "sentiment_score": 0.0, "structure_bias": "Unknown", "key_observation": "分析失败"}

    def optimize_strategy_logic(self, deepseek_analysis: Dict[str, Any], current_market_data: Dict[str, Any], technical_signals: Optional[Dict[str, Any]] = None, current_positions: Optional[List[Dict[str, Any]]] = None, performance_stats: Optional[List[Dict[str, Any]]] = None, previous_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        优化策略逻辑，基于DeepSeek的情绪得分调整入场条件
        基于ValueCell的实现，支持JSON模式输出
        
        Args:
            deepseek_analysis (Dict[str, Any]): DeepSeek的市场分析结果
            current_market_data (Dict[str, Any]): 当前市场数据
            technical_signals (Optional[Dict[str, Any]]): 其他技术模型的信号（CRT, Price Equation等）
            current_positions (Optional[List[Dict[str, Any]]]): 当前持仓信息 (用于决定加仓或平仓)
            performance_stats (Optional[List[Dict[str, Any]]]): 历史交易绩效统计 (用于自学习)
            previous_analysis (Optional[Dict[str, Any]]): 上一次的分析结果 (用于连续性分析)
        
        Returns:
            Dict[str, Any]: 优化后的策略参数
        """
        tech_context = ""
        perf_context = ""
        pos_context = ""
        prev_context = ""
        
        if previous_analysis:
            # 提取上一次的关键信息
            prev_action = previous_analysis.get('action', 'unknown')
            prev_rationale = previous_analysis.get('strategy_rationale', 'none')
            prev_context = f"\n上一次分析结果 (Previous Analysis):\n- Action: {prev_action}\n- Rationale: {prev_rationale[:200]}...\n"
        else:
            prev_context = "\n上一次分析结果: 无 (首次运行)\n"
        
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
        作为黄金(XAUUSD)交易的**首席策略官与执行总监**，你现在身兼两职：既要像DeepSeek一样进行宏观趋势与情绪分析，又要负责具体的SMC+Martingale交易执行。
        
        请按照以下逻辑流进行深度分析与决策：

        ### 第一阶段：宏观格局与趋势分析 (The Strategist)
        1. **市场结构 (Market Structure)**: 
           - 分析当前处于什么阶段？(吸筹 Accumulation / 操纵 Manipulation / 派发 Distribution / 趋势 Trend)。
           - 识别大周期 (H1/H4) 的主要流动性池 (Liquidity Pools) 和 订单块 (OB)。
           - **趋势定性**: 当前是大牛市、大熊市、还是宽幅震荡？
        2. **市场情绪 (Sentiment)**:
           - 结合价格行为判断当前市场情绪是 Risk-On (激进) 还是 Risk-Off (避险)。
           - 黄金特有属性：关注亚盘/欧盘/美盘的盘口特征（如美盘前的诱多/诱空）。
        
        ### 第二阶段：SMC 精细化入场 (The Sniper)
        1. **SMC 核心信号**:
           - 寻找 **BOS (结构破坏)** 或 **CHoch (角色转变)** 确认趋势延续或反转。
           - 识别 **FVG (价值缺口)** 作为回调入场的关键位。
           - 确认 **Liquidity Sweep (流动性扫荡)**，特别是对前高/前低的假突破。
        2. **CRT 与共振**:
           - 结合 CRT (K线理论) 确认关键位置的 K线形态 (如 Pinbar, Engulfing)。
           - 检查 CCI/RVGI 是否支持当前方向。

        ### 第三阶段：Martingale Grid 资金管理 (The Risk Manager)
        - **首单策略**: 基于上述分析，在最佳 SMC 位置轻仓试错。
        - **逆势加仓 (Grid Add)**: 如果判断大趋势未变但短线被套，制定马丁加仓计划。
           - **加仓位**: 必须是下一个强支撑/阻力 (OB/FVG)，绝非固定点数。
           - **倍投**: 1.2x - 2.0x 几何递增。
        - **止损止盈 (MAE/MFE)**: 
           - 利用 MAE 数据设定"安全"止损（过滤假突破）。
           - 利用 MFE 数据设定"贪婪"止盈（吃满波段）。

        ---
        **输入数据**:
        当前市场数据：
        {json.dumps(current_market_data, indent=2, cls=CustomJSONEncoder)}
        
        持仓状态 (关注浮亏与加仓机会):
        {pos_context}
        
        挂单状态:
        {orders_context}
        
        技术信号 (SMC/CRT/CCI):
        {tech_context}
        
        历史绩效 (MFE/MAE 参考):
        {perf_context}
        
        上一次分析 (连续性参考):
        {prev_context}
        
        ---
        **决策输出 (Action)**:
        请给出明确的交易指令。
        1. **STRONG_BUY / BUY**: 宏观趋势向上 + SMC 回调到位 + 情绪看多。
        2. **STRONG_SELL / SELL**: 宏观趋势向下 + SMC 反弹受阻 + 情绪看空。
        3. **ADD_BUY / ADD_SELL**: 逆势加仓，摊低成本 (需满足马丁加仓条件)。
        4. **GRID_START**: 震荡市，在上下方关键位预埋网格单。
        5. **CLOSE**: 趋势反转或达到止盈目标。
        6. **HOLD**: 方向不明或未到关键位。

        **输出要求**:
        - **limit_price**: 挂单必填，精确到 0.01。
        - **sl_price / tp_price**: 必填，基于结构位和 MAE/MFE。
        - **position_size**: 资金比例 (0.01 - 0.1)。
        - **strategy_rationale**: **(中文)** 必须包含三部分：
           1. **宏观分析**: "当前黄金处于H4级别的...阶段，情绪偏向..."
           2. **SMC逻辑**: "价格回踩了2030的H1 FVG，且出现M15 BOS..."
           3. **执行计划**: "因此执行买入，若跌破2025则在2020加仓(马丁)..."

        请以JSON格式返回结果，包含以下字段：
        - action: str
        - entry_conditions: dict ("limit_price": float)
        - exit_conditions: dict ("sl_price": float, "tp_price": float)
        - position_management: dict ("martingale_multiplier": float, "grid_step_logic": str)
        - position_size: float
        - leverage: int
        - signal_strength: int
        - parameter_updates: dict
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
