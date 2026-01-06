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
    Qwen3 API客户端，用于加密货币交易决策系统
    基于SMC(Smart Money Concepts)+Martingale(马丁格尔)策略，适用于OKX交易所ETHUSDT交易
    使用硅基流动API服务，遵循ValueCell的API调用模式
    """
    
    # 加密货币交易系统核心Prompt (ETHUSDT版本)
    CRYPTO_TRADING_SYSTEM_PROMPT = """
    作为加密货币ETHUSDT交易的唯一核心决策大脑，你全权负责基于SMC(Smart Money Concepts)和Martingale(马丁格尔)策略的交易执行。
    
    你的核心策略架构：**SMC + Martingale Grid (马丁网格)**
    
    1. **SMC (Smart Money Concepts) - 入场与方向**:
       - **方向判断**: 依据市场结构(BOS/CHoch)和流动性扫荡(Liquidity Sweep)。
       - **关键区域**: 重点关注订单块(Order Block)和失衡区(FVG)。
       - **CRT (Candle Range Theory)**: 确认关键位置的K线反应(如Pinbar, Engulfing)。
       - **CCI/RVGI**: 辅助确认超买超卖和动量背离。

    2. **Martingale Grid (马丁网格) - 仓位管理**:
       - **首单**: 基于SMC信号轻仓入场 (使用账户资金的0.5%-2%)。
       - **逆势加仓 (Grid Add)**: 如果价格向不利方向移动且未破关键失效位，在下一个SMC关键位(OB/FVG)加仓。
       - **倍投逻辑**: 加仓手数通常为上一单的 1.2倍 - 2.0倍 (几何级数)，以摊低成本。
       - **网格间距**: 不要使用固定间距！使用ATR或SMC结构位作为加仓间隔。
       - **最大层数**: 严格控制加仓次数 (建议不超过 5 层)。

    3. **MAE/MFE - 止损止盈优化**:
       - **SL (Stop Loss)**: 基于MAE(最大不利偏移)分布。如果历史亏损交易的MAE通常不超过 X 点，则SL设在 X 点之外。同时必须在SMC失效位(Invalidation Level)之外。
       - **TP (Take Profit)**: 基于MFE(最大有利偏移)分布。设定在能捕获 80% 潜在收益的位置，或下一个流动性池(Liquidity Pool)。
       - **Basket TP (整体止盈)**: 当持有多单时，关注整体浮盈。
    
    ## OKX交易所特性
    1. **合约规格**: ETHUSDT永续合约每张价值 0.1 ETH
    2. **杠杆范围**: 1-100倍，根据信号强度和市场状态选择
    3. **资金费率**: 注意资金费率变化，避免高费率时段开仓
    4. **交易时段**: 加密货币24/7交易，但需注意波动时段：
       - 亚洲时段（00:00-08:00 UTC）：相对平静
       - 欧洲时段（08:00-16:00 UTC）：波动开始增加
       - 美国时段（16:00-00:00 UTC）：波动最大
    
    ## 市场分析框架
    
    ### 一、大趋势分析
    你必须从多时间框架分析ETH的整体市场结构：
    
    1. **时间框架层级分析**
       - 周图/日图：识别长期趋势方向和市场相位
       - H4：确定中期市场结构和关键水平
       - H1：寻找交易机会和入场时机
       - 15分钟：精确定位入场点
    
    2. **市场结构识别**
       - 明确标注当前更高级别时间框架的趋势方向（牛市、熊市、盘整）
       - 识别并列出最近的BOS（突破市场结构）和CHoch（变化高点）点位
       - 判断市场当前处于：积累阶段、扩张阶段还是分配阶段
    
    3. **流动性分析**
       - 识别上方卖单流动性池（近期高点之上明显的止损区域）
       - 识别下方买单流动性池（近期低点之下明显的止损区域）
       - 评估流动性扫荡的可能性：哪个方向的流动性更容易被触发
    
    4. **关键水平识别**
       - 列出3-5个最重要的支撑位（包括订单块、失衡区、心理关口）
       - 列出3-5个最重要的阻力位（包括订单块、失衡区、心理关口）
       - 特别关注多时间框架汇合的关键水平
    
    ### 二、SMC信号处理
    
    1. **订单块分析**
       - 识别当前价格附近的新鲜订单块（最近3-5根K线形成的）
       - 评估订单块的质量：成交量、K线强度、时间框架重要性
       - 标注订单块的方向和失效水平
    
    2. **失衡区分析**
       - 识别当前活跃的FVG（公平价值缺口）
       - 评估FVG的大小和回填概率
       - 判断FVG是推动型还是回流型
    
    3. **CRT信号确认**
       - 观察关键水平附近的K线反应：Pinbar、吞没形态、内部K线
       - 评估CRT信号的质量：影线比例、收盘位置、成交量配合
       - 确认信号是否得到多时间框架共振
    
    4. **动量指标辅助**
       - CCI分析：是否出现背离？是否进入超买超卖区？
       - RVGI分析：成交量是否确认价格行为？
       - 评估多空力量对比
    
    ## 交易决策流程
    
    ### 三、方向判断决策树
    你必须明确回答以下问题：
    
    1. 更高级别趋势是什么方向？
    2. 当前价格相对于关键水平处于什么位置？
    3. 最近的价格行为显示了什么意图？
    4. 流动性分布暗示了什么方向偏好？
    
    基于以上分析，你必须给出明确的交易方向：
    - 主要方向：做多、做空或观望
    - 置信度：高、中、低
    - 时间框架：交易是基于哪个时间框架的信号
    
    ### 四、入场执行标准
    
    **首单入场必须满足所有条件：**
    
    1. **价格到达关键SMC区域**
       - 订单块或失衡区内
       - 距离失效位有合理的风险回报空间
    
    2. **CRT确认信号出现**
       - 明显的反转或延续形态
       - 收盘确认信号有效性
    
    3. **动量指标支持**
       - CCI显示背离或极端值回归
       - RVGI确认成交量配合
    
    4. **流动性目标明确**
       - 至少有1:1.5的风险回报比
       - 明确的上方/下方流动性目标
    
    ### 五、Martingale网格管理
    
    **首单参数：**
    - 仓位：账户资金的0.5%-2%（根据信号强度调整）
    - 止损：设在SMC失效位之外，考虑MAE历史数据
    - 止盈：下一流动性池或MFE分布的80%分位
    
    **加仓规则：**
    1. **触发条件**：价格向不利方向移动但未破关键失效位
    2. **加仓位置**：下一个SMC关键区域（订单块或失衡区）
    3. **加仓手数**：前一手数的1.5倍（可调整系数）
    4. **加仓间距**：使用ATR(14) × 1.5 或自然结构位间距
    5. **最大层数**：严格限制5层，总风险不超过5%
    
    **网格计算公式：**
    第1层：0.5%风险
    第2层：0.75%风险（1.5倍）
    第3层：1.125%风险
    第4层：1.6875%风险
    第5层：2.53125%风险
    总风险：约6.6%（但必须控制在5%硬止损内）
    
    ### 六、退出策略
    
    **盈利退出条件：**
    1. **部分止盈**：价格到达第一目标（风险回报比1:1），平仓50%
    2. **移动止损**：剩余仓位止损移至保本，追踪至第二目标
    3. **整体止盈**：组合浮盈达到总风险的1.5倍，或到达主要流动性池
    
    **止损退出条件：**
    1. **技术止损**：价格突破SMC失效位，所有仓位立即离场
    2. **时间止损**：持仓超过2天无实质性进展，考虑减仓或离场
    3. **情绪止损**：连续2次亏损后，必须降低仓位50%
    
    ## 输出格式要求
    
    你的每次分析必须包含以下部分：
    
    ### 第一部分：市场结构分析
    1. 多时间框架趋势分析
    2. 关键水平识别
    3. 流动性分布评估
    4. 市场情绪判断
    
    ### 第二部分：SMC信号识别
    1. 活跃订单块列表
    2. 重要失衡区识别
    3. CRT确认信号描述
    4. 动量指标状态
    
    ### 第三部分：交易决策
    1. 明确的方向判断
    2. 置信度评估
    3. 具体入场计划（价格、仓位、止损、止盈）
    4. 加仓计划（条件、位置、仓位）
    
    ### 第四部分：风险管理
    1. 单笔风险计算
    2. 总风险控制
    3. 应急预案
    4. 时间框架提醒
    
    ### 第五部分：后续行动指南
    1. 如果行情按预期发展：下一步行动
    2. 如果行情反向发展：应对措施
    3. 如果行情盘整：等待策略
    4. 关键观察位和决策点
    
    ## 特殊情景处理规则
    
    ### 高波动性市场（ATR > 近期均值1.5倍）
    - 立即将仓位规模减少30%
    - 扩大止损范围至ATR × 2
    - 优先选择高时间框架的订单块
    - 避免在流动性稀薄时段交易
    
    ### 关键新闻事件前后（FOMC、CPI等）
    - 事件前1小时：暂停所有新开仓
    - 事件后30分钟：观察市场反应，不急于入场
    - 如果波动率异常放大：等待ATR回归正常水平
    - 只交易明确的SMC信号，忽略模糊信号
    
    
    ## 合约计算说明
    
    1. **合约张数计算**:
       - ETHUSDT永续合约每张 = 0.1 ETH
       - 名义价值 = 入场价格 × 0.1 × 合约张数
       - 保证金 = 名义价值 / 杠杆
    
    2. **仓位规模计算示例**:
       - 账户余额：10,000 USDT
       - 风险比例：1%
       - 风险金额：100 USDT
       - 入场价格：3,500 USDT
       - 止损距离：50 USDT
       - 合约张数 = 风险金额 / (止损距离 × 0.1) = 100 / (50 × 0.1) = 20张
    
    3. **杠杆选择建议**:
       - 低波动/震荡市场：3-10倍
       - 趋势明确市场：10-30倍
       - 强趋势/高信号强度：30-50倍
       - 极端机会：50-100倍（需严格控制风险）
    
    ## 最终决策输出
    
    请做出最终决策 (Action):
    1. **HOLD**: 震荡无方向，或持仓浮亏但在网格间距内。
    2. **BUY / SELL**: 出现SMC信号，首单入场。
    3. **ADD_BUY / ADD_SELL**: 逆势加仓。**仅当**：(a) 已有持仓且浮亏; (b) 价格到达下一个SMC支撑/阻力位; (c) 距离上一单有足够间距(>ATR)。
    4. **CLOSE**: 达到整体止盈目标，或SMC结构完全破坏(止损)。
    5. **GRID_START**: 预埋网格单 (Limit Orders) 在未来的OB/FVG位置。
    
    输出要求：
    - **limit_price**: 挂单必填。
    - **sl_price / tp_price**: 必填，基于MAE/MFE和SMC结构。
    - **position_size**: 给出具体的资金比例 (0.005 - 0.05)。
    - **contract_quantity**: 计算具体的合约张数（基于每张0.1 ETH）。
    - **leverage**: 建议的杠杆倍数（1-100）。
    - **strategy_rationale**: 用**中文**详细解释：SMC结构分析 -> 为什么选择该方向 -> 马丁加仓计划/止盈计划 -> 参考的MAE/MFE数据。
    
    请以JSON格式返回结果，包含以下字段：
    - action: str ("buy", "sell", "hold", "close", "add_buy", "add_sell", "grid_start")
    - entry_conditions: dict ("limit_price": float, "trigger_type": "market/limit")
    - exit_conditions: dict ("sl_price": float, "tp_price": float)
    - position_management: dict ("martingale_multiplier": float, "grid_step_logic": str)
    - position_size: float (资金比例 0.005-0.05)
    - contract_quantity: int (合约张数)
    - leverage: int (杠杆倍数 1-100)
    - signal_strength: int (0-100)
    - risk_metrics: dict ("max_risk": float, "current_risk": float)
    - strategy_rationale: str (中文)
    - market_structure_analysis: dict
    - smc_signals_identified: list
    - next_observations: list
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
                # 增加超时时间到300秒，应对 SiliconFlow/DeepSeek 响应慢的问题
                response = requests.post(
                    url, 
                    headers=self.headers, 
                    json=payload, 
                    timeout=300
                )
                
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
                # 线性延迟重试，提高网络不稳定情况下的成功率
                retry_delay = min(5 * (retry + 1), 30)  # 每次增加5秒，最大30秒
                logger.info(f"等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
            else:
                logger.error(f"API调用失败，已达到最大重试次数 {max_retries}")
                return None
    
    def analyze_market_structure(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Qwen 市场结构与情绪分析 (加密货币版)
        完全自主进行市场结构、情绪和SMC信号分析
        
        Args:
            market_data (Dict[str, Any]): 市场数据
            
        Returns:
            Dict[str, Any]: 市场结构分析结果
        """
        prompt = f"""
        作为专业的加密货币市场分析师和SMC交易专家，请根据以下市场数据进行全面的市场结构与情绪分析：
        
        市场数据:
        {json.dumps(market_data, indent=2, cls=CustomJSONEncoder)}
        
        请完成以下分析：
        
        1. **多时间框架市场结构分析**
           - 识别当前主要趋势方向（牛市/熊市/盘整）
           - 找出关键的市场结构点（BOS/CHoch）
           - 评估市场当前处于哪个阶段（积累/扩张/分配）
        
        2. **SMC信号识别**
           - 识别活跃的订单块(Order Blocks)
           - 识别重要的失衡区(FVGs)
           - 评估流动性池位置
        
        3. **情绪分析**
           - 情绪得分 (Sentiment Score): -1.0 (极度看空) 到 1.0 (极度看多)
           - 市场情绪状态: bullish/bearish/neutral
        
        4. **关键水平识别**
           - 列出3-5个最重要的支撑位
           - 列出3-5个最重要的阻力位
        
        请以JSON格式返回以下内容：
        {
            "market_structure": {
                "trend": "bullish/bearish/neutral",
                "phase": "accumulation/expansion/distribution",
                "key_levels": {
                    "support": [list of support levels],
                    "resistance": [list of resistance levels]
                },
                "bos_points": [list of BOS levels],
                "choch_points": [list of CHOCH levels]
            },
            "smc_signals": {
                "order_blocks": [list of identified order blocks],
                "fvgs": [list of identified fair value gaps],
                "liquidity_pools": {
                    "above": price,
                    "below": price
                }
            },
            "sentiment_analysis": {
                "sentiment": "bullish/bearish/neutral",
                "sentiment_score": float (-1.0 to 1.0),
                "confidence": float (0.0 to 1.0)
            },
            "key_observations": str (简短的中文分析)
        }
        """
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一位精通SMC(Smart Money Concepts)和价格行为学的加密货币交易专家。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1000,
            "stream": False,
            "response_format": {"type": "json_object"}
        }
        
        response = self._call_api("chat/completions", payload)
        if response and "choices" in response:
            try:
                content = response["choices"][0]["message"]["content"]
                return json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"解析市场结构分析失败: {e}")
        
        return {
            "market_structure": {
                "trend": "neutral",
                "phase": "unknown",
                "key_levels": {"support": [], "resistance": []},
                "bos_points": [],
                "choch_points": []
            },
            "smc_signals": {
                "order_blocks": [],
                "fvgs": [],
                "liquidity_pools": {"above": None, "below": None}
            },
            "sentiment_analysis": {
                "sentiment": "neutral",
                "sentiment_score": 0.0,
                "confidence": 0.0
            },
            "key_observations": "分析失败"
        }

    def execute_trading_decision(self, current_market_data: Dict[str, Any], technical_signals: Optional[Dict[str, Any]] = None, current_positions: Optional[List[Dict[str, Any]]] = None, performance_stats: Optional[List[Dict[str, Any]]] = None, previous_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        ETHUSDT加密货币交易决策系统 - 基于SMC+Martingale策略
        适用于OKX交易所，整合完整的交易决策框架
        完全自主进行市场分析和交易决策
        
        Args:
            current_market_data (Dict[str, Any]): 当前市场数据
            technical_signals (Optional[Dict[str, Any]]): 技术信号（SMC/CRT/CCI等）
            current_positions (Optional[List[Dict[str, Any]]]): 当前持仓信息
            performance_stats (Optional[List[Dict[str, Any]]]): 历史交易绩效统计
            previous_analysis (Optional[Dict[str, Any]]): 上一次的分析结果
        
        Returns:
            Dict[str, Any]: 完整的交易决策
        """
        # 首先进行市场结构分析
        market_analysis = self.analyze_market_structure(current_market_data)
        
        # 构建上下文信息
        tech_context = ""
        perf_context = ""
        pos_context = ""
        prev_context = ""
        market_context = ""
        
        # 1. 市场分析结果上下文
        market_context = f"\n市场结构分析结果:\n{json.dumps(market_analysis, indent=2, cls=CustomJSONEncoder)}\n"
        
        # 2. 上一次分析结果上下文
        if previous_analysis:
            prev_action = previous_analysis.get('action', 'unknown')
            prev_rationale = previous_analysis.get('strategy_rationale', 'none')
            prev_context = f"\n上一次分析结果 (Previous Analysis):\n- Action: {prev_action}\n- Rationale: {prev_rationale[:200]}...\n"
        else:
            prev_context = "\n上一次分析结果: 无 (首次运行)\n"
        
        # 3. 当前持仓状态上下文
        if current_positions:
            pos_context = f"\n当前持仓状态 (包含实时 MFE/MAE 和 R-Multiple):\n{json.dumps(current_positions, indent=2, cls=CustomJSONEncoder)}\n"
        else:
            pos_context = "\n当前无持仓。\n"

        # 4. 挂单状态上下文
        open_orders = current_market_data.get('open_orders', [])
        orders_context = ""
        if open_orders:
            orders_context = f"\n当前挂单状态 (Limit/SL/TP):\n{json.dumps(open_orders, indent=2, cls=CustomJSONEncoder)}\n"
        else:
            orders_context = "\n当前无挂单。\n"

        # 5. 性能统计上下文
        stats_to_use = performance_stats
        
        if stats_to_use:
            recent_trades = []
            summary_stats = {}
            
            try:
                if isinstance(stats_to_use, list):
                    valid_trades = [t for t in stats_to_use if isinstance(t, dict)]
                    recent_trades = valid_trades
                    
                    if len(recent_trades) > 0:
                         mfe_list = [t.get('mfe', 0) for t in recent_trades if t.get('mfe') is not None]
                         mae_list = [t.get('mae', 0) for t in recent_trades if t.get('mae') is not None]
                         
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

        # 6. 技术信号上下文
        if technical_signals:
            sigs_copy = technical_signals.copy()
            if 'performance_stats' in sigs_copy:
                del sigs_copy['performance_stats']
            tech_context = f"\n技术信号 (SMC/CRT/CCI):\n{json.dumps(sigs_copy, indent=2, cls=CustomJSONEncoder)}\n"

        # 构建完整提示词
        prompt = f"""
        {self.CRYPTO_TRADING_SYSTEM_PROMPT}
        
        ## 当前交易上下文
        
        当前市场数据：
        {json.dumps(current_market_data, indent=2, cls=CustomJSONEncoder)}
        
        市场结构分析结果：
        {market_context}
        
        持仓状态 (Martingale 核心关注):
        {pos_context}
        
        挂单状态:
        {orders_context}
        
        技术信号 (SMC/CRT/CCI):
        {tech_context}
        
        历史绩效 (MFE/MAE 参考):
        {perf_context}
        
        上一次分析:
        {prev_context}
        
        ## 合约计算参数
        - 当前ETH价格: {current_market_data.get('prices', {}).get('close', 'N/A')} USDT
        - 账户余额: {current_market_data.get('account_info', {}).get('available_usdt', 'N/A')} USDT
        - 每张合约价值: 0.1 ETH
        
        ## 现在，基于以上所有信息，请输出完整的交易决策
        特别注意：请计算具体的合约张数，并给出合理的杠杆建议。
        
        决策要求：
        1. 基于市场结构分析结果进行方向判断
        2. 结合SMC信号寻找最佳入场点
        3. 参考MAE/MFE数据优化止损止盈
        4. 制定Martingale网格加仓计划
        5. 严格遵循风险管理规则
        """
        
        # 构建payload
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一名专注于ETHUSDT交易的职业交易员，采用SMC(Smart Money Concepts)结合Martingale网格策略的复合交易系统。你完全自主进行市场分析和交易决策。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 2500,
            "stream": False
        }
        
        # 启用JSON模式
        if self.enable_json_mode:
            payload["response_format"] = {"type": "json_object"}
        
        # 调用API
        response = self._call_api("chat/completions", payload)
        if response and "choices" in response:
            try:
                message_content = response["choices"][0]["message"]["content"]
                logger.info(f"收到模型响应: {message_content}")
                
                # 解析响应
                trading_decision = json.loads(message_content)
                
                if not isinstance(trading_decision, dict):
                    logger.error(f"Qwen响应格式错误 (期望dict, 实际{type(trading_decision)}): {trading_decision}")
                    return self._get_default_decision("响应格式错误")
                
                # 确保必要的字段存在
                required_fields = ['action', 'entry_conditions', 'exit_conditions', 'strategy_rationale']
                for field in required_fields:
                    if field not in trading_decision:
                        trading_decision[field] = self._get_default_value(field)
                
                # 计算合约张数（如果未提供）
                if 'contract_quantity' not in trading_decision and 'position_size' in trading_decision:
                    try:
                        current_price = current_market_data.get('prices', {}).get('close', 3500)
                        account_balance = current_market_data.get('account_info', {}).get('available_usdt', 10000)
                        position_size = trading_decision.get('position_size', 0.01)
                        leverage = trading_decision.get('leverage', 10)
                        
                        # 计算名义价值
                        nominal_value = account_balance * position_size * leverage
                        # 计算合约张数（每张0.1 ETH）
                        contract_qty = int(nominal_value / (current_price * 0.1))
                        trading_decision['contract_quantity'] = max(1, contract_qty)
                    except Exception as e:
                        logger.error(f"计算合约张数失败: {e}")
                        trading_decision['contract_quantity'] = 10  # 默认值
                
                # 添加市场分析结果到决策中
                trading_decision['market_analysis'] = market_analysis
                
                return trading_decision
                
            except json.JSONDecodeError as e:
                logger.error(f"解析Qwen响应失败: {e}")
                logger.error(f"原始响应: {response}")
                return self._get_default_decision("解析失败，使用默认参数")
        
        return self._get_default_decision("API调用失败，使用默认参数")
    
    def _get_default_decision(self, reason: str = "系统错误") -> Dict[str, Any]:
        """获取默认决策"""
        return {
            "action": "hold",
            "entry_conditions": {"trigger_type": "market"},
            "exit_conditions": {"sl_atr_multiplier": 1.5, "tp_atr_multiplier": 2.5},
            "position_management": {"martingale_multiplier": 1.5, "grid_step_logic": "ATR_based"},
            "position_size": 0.01,
            "contract_quantity": 10,
            "leverage": 10,
            "signal_strength": 50,
            "risk_metrics": {"max_risk": 0.02, "current_risk": 0},
            "strategy_rationale": reason,
            "market_structure_analysis": {"trend": "neutral", "phase": "waiting"},
            "smc_signals_identified": [],
            "next_observations": ["等待明确信号"],
            "market_analysis": {
                "market_structure": {"trend": "neutral", "phase": "unknown"},
                "sentiment_analysis": {"sentiment": "neutral", "sentiment_score": 0.0}
            }
        }
    
    def _get_default_value(self, field: str) -> Any:
        """获取字段默认值"""
        defaults = {
            'action': 'hold',
            'entry_conditions': {"trigger_type": "market"},
            'exit_conditions': {"sl_atr_multiplier": 1.5, "tp_atr_multiplier": 2.5},
            'position_management': {"martingale_multiplier": 1.5, "grid_step_logic": "ATR_based"},
            'position_size': 0.01,
            'contract_quantity': 10,
            'leverage': 10,
            'signal_strength': 50,
            'risk_metrics': {"max_risk": 0.02, "current_risk": 0},
            'strategy_rationale': "默认决策",
            'market_structure_analysis': {"trend": "neutral", "phase": "waiting"},
            'smc_signals_identified': [],
            'next_observations': ["等待明确信号"]
        }
        return defaults.get(field, None)
    
    def judge_signal_strength(self, market_data: Dict[str, Any], technical_indicators: Dict[str, Any]) -> int:
        """
        判断交易信号强度
        基于市场数据和技术指标评估信号强度
        
        Args:
            market_data (Dict[str, Any]): 市场数据
            technical_indicators (Dict[str, Any]): 技术指标数据
        
        Returns:
            int: 信号强度，0-100，越高表示信号越可靠
        """
        prompt = f"""
        作为专业的交易信号分析师，请评估以下交易信号的强度：
        
        市场数据：
        {json.dumps(market_data, indent=2)}
        
        技术指标：
        {json.dumps(technical_indicators, indent=2)}
        
        请基于以下因素评估信号强度(0-100)：
        1. 市场结构：当前市场状态是否有利于交易
        2. SMC信号：订单块、失衡区的质量
        3. 多指标共振：技术指标是否一致支持该信号
        4. 成交量：成交量是否支持价格走势
        5. 波动率：当前波动率是否适合交易
        
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
    
    # 示例ETHUSDT市场数据
    current_market_data = {
        "symbol": "ETHUSDT",
        "timeframe": "H1",
        "prices": {
            "open": 3500.50,
            "high": 3525.75,
            "low": 3498.20,
            "close": 3512.30,
            "volume": 125000
        },
        "indicators": {
            "ema_fast": 3505.50,
            "ema_slow": 3498.80,
            "rsi": 62.5,
            "atr": 25.75,
            "cci": 125.3,
            "rvgi": 0.65
        },
        "order_blocks": [
            {"price": 3502.0, "type": "bullish", "timeframe": "H1", "freshness": "fresh"},
            {"price": 3480.0, "type": "bullish", "timeframe": "H4", "freshness": "tested"}
        ],
        "fvgs": [
            {"range": [3505.0, 3498.0], "direction": "bullish"}
        ],
        "market_structure": {
            "higher_tf_trend": "bullish",
            "bos_levels": [3550.0, 3450.0],
            "choch_levels": [3520.0, 3485.0]
        },
        "account_info": {
            "available_usdt": 10000.0,
            "total_balance": 12000.0,
            "used_margin": 2000.0
        }
    }
    
    # 测试市场结构分析
    market_analysis = client.analyze_market_structure(current_market_data)
    print("市场结构分析结果:")
    print(json.dumps(market_analysis, indent=2, ensure_ascii=False))
    
    # 测试交易决策
    trading_decision = client.execute_trading_decision(
        current_market_data=current_market_data,
        technical_signals={
            "crt_signal": "pinbar",
            "crt_confidence": 0.8,
            "price_action": "bullish_reversal"
        },
        current_positions=None,
        performance_stats=[
            {"profit": 125, "mfe": 1.5, "mae": 0.8},
            {"profit": -80, "mfe": 0.5, "mae": 1.2}
        ]
    )
    
    print("\nETHUSDT交易决策系统输出:")
    print(json.dumps(trading_decision, indent=2, ensure_ascii=False))
    
    # 测试信号强度判断
    technical_indicators = {"ema_crossover": 1, "rsi": 62.5, "volume_increase": True}
    signal_strength = client.judge_signal_strength(current_market_data, technical_indicators)
    print(f"\n信号强度: {signal_strength}")
    
    # 测试凯利准则计算
    kelly = client.calculate_kelly_criterion(0.6, 1.5)
    print(f"\n凯利准则: {kelly:.2f}")

if __name__ == "__main__":
    main()