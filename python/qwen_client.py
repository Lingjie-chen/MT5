import requests
import json
import logging
import time
from typing import Dict, Any, Optional, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    
    def optimize_strategy_logic(self, deepseek_analysis: Dict[str, Any], current_market_data: Dict[str, Any], technical_signals: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        优化策略逻辑，基于DeepSeek的情绪得分调整入场条件
        基于ValueCell的实现，支持JSON模式输出
        
        Args:
            deepseek_analysis (Dict[str, Any]): DeepSeek的市场分析结果
            current_market_data (Dict[str, Any]): 当前市场数据
            technical_signals (Optional[Dict[str, Any]]): 其他技术模型的信号（CRT, Price Equation等）
        
        Returns:
            Dict[str, Any]: 优化后的策略参数
        """
        tech_context = ""
        perf_context = ""
        
        if technical_signals:
            # 提取性能统计 (如果存在) 并单独处理，避免被 json.dumps 混淆
            perf_stats = technical_signals.get('performance_stats')
            if perf_stats:
                perf_context = (
                    f"\n历史交易绩效参考 (用于优化 SL/TP):\n"
                    f"- 平均 MFE (最大有利波动): {perf_stats.get('avg_mfe', 0):.2f}%\n"
                    f"- 平均 MAE (最大不利波动): {perf_stats.get('avg_mae', 0):.2f}%\n"
                    f"- 平均利润: {perf_stats.get('avg_profit', 0):.2f}\n"
                    f"- 样本交易数: {perf_stats.get('trade_count', 0)}\n"
                )
                # 从 technical_signals 中移除 stats 以免重复 (浅拷贝处理)
                sigs_copy = technical_signals.copy()
                if 'performance_stats' in sigs_copy:
                    del sigs_copy['performance_stats']
                tech_context = f"\n其他技术模型信号 (CRT/PriceEq/Hybrid):\n{json.dumps(sigs_copy, indent=2)}\n"
            else:
                tech_context = f"\n其他技术模型信号 (CRT/PriceEq/Hybrid):\n{json.dumps(technical_signals, indent=2)}\n"

        prompt = f"""
        作为专业的量化交易策略优化专家，你是混合交易系统的核心决策层。请根据DeepSeek的市场分析结果、当前市场数据以及其他技术模型的信号，优化策略逻辑。
        
        DeepSeek市场分析结果：
        {json.dumps(deepseek_analysis, indent=2)}
        
        当前市场数据：
        {json.dumps(current_market_data, indent=2)}
        {tech_context}
        {perf_context}
        
        请综合考虑所有信号：
        1. DeepSeek 提供宏观结构和趋势判断。
        2. CRT (Candle Range Theory) 提供流动性猎取和反转信号。
        3. Price Equation 提供纯数学的动量预测。
        4. Hybrid Optimizer 提供加权共识。
        5. MFE/MAE 历史数据 (如有) 提供止盈止损优化的参考依据。
           - 如果平均 MFE 较高，可适当放宽 TP。
           - 如果平均 MAE 较低但频繁止损，可适当放宽 SL 或优化入场。
        
        请提供以下优化结果，并确保分析全面、逻辑严密，不要使用省略号或简化描述。**请务必使用中文进行输出（Strategy Logic Rationale 部分）**：
        1. 入场条件：基于情绪得分和技术指标的优化入场规则，详细说明触发条件
        2. 出场条件：止盈止损参数，给出具体的数值或计算逻辑
        3. 仓位大小：基于市场波动率的最优仓位
        4. 交易信号强度：0-100的得分，表示信号的可靠性
        5. 风险管理建议：针对当前市场状态的风险控制措施
        6. 策略逻辑详解：请详细解释做出上述决策的逻辑链条 (Strategy Logic Rationale)，**必须使用中文**
        
        请以JSON格式返回结果，包含以下字段：
        - action: str ("buy", "sell", "hold") - 明确的交易行动建议
        - entry_conditions: dict (包含 "trigger_type": "market"|"limit", "limit_price": float (optional), "confirmation": str)
        - exit_conditions: dict (包含 "sl_atr_multiplier": float, "tp_atr_multiplier": float)
        - position_size: float
        - signal_strength: int
        - risk_management: dict
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
        根据市场波动率生成自适应止盈止损
        
        Args:
            volatility (float): 当前波动率(ATR百分比)
            market_state (str): 市场状态(趋势/震荡/高波动)
            signal_strength (int): 信号强度(0-100)
        
        Returns:
            Dict[str, float]: 动态止盈止损参数
        """
        prompt = f"""
        作为专业的风险管理专家，请根据以下参数生成动态止盈止损：
        
        当前波动率(ATR百分比)：{volatility}
        市场状态：{market_state}
        信号强度：{signal_strength}
        
        请基于以下原则生成参数：
        1. 趋势市场：止盈较大，止损较小
        2. 震荡市场：止盈较小，止损较小
        3. 高波动市场：止盈较大，止损较大
        4. 信号强度高：止盈较大，止损相对较小
        5. 波动率高：止盈止损都较大
        
        请以ATR倍数返回止盈止损参数，格式为：
        {{"take_profit": X.XX, "stop_loss": X.XX}}
        
        请只返回JSON格式的结果，不要包含其他解释。
        """
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一位专业的风险管理专家，擅长根据市场条件生成动态止盈止损参数。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 100
        }
        
        response = self._call_api("chat/completions", payload)
        if response and "choices" in response:
            try:
                sl_tp = json.loads(response["choices"][0]["message"]["content"])
                return sl_tp
            except json.JSONDecodeError as e:
                logger.error(f"解析止盈止损参数失败: {e}")
        return {"take_profit": 1.5, "stop_loss": 1.0}
    
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
