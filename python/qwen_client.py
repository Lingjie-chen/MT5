import requests
import json
import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QwenClient:
    """
    Qwen3 API客户端，用于策略逻辑优化、动态止盈止损生成和信号强度判断
    """
    def __init__(self, api_key: str, base_url: str = "https://api.qwen.com/v1"):
        """
        初始化Qwen客户端
        
        Args:
            api_key (str): Qwen API密钥
            base_url (str): API基础URL，默认为https://api.qwen.com/v1
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def _call_api(self, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        调用Qwen API
        
        Args:
            endpoint (str): API端点
            payload (Dict[str, Any]): 请求负载
        
        Returns:
            Optional[Dict[str, Any]]: API响应，失败返回None
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API调用失败: {e}")
            return None
    
    def optimize_strategy_logic(self, deepseek_analysis: Dict[str, Any], current_market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        优化策略逻辑，基于DeepSeek的情绪得分调整入场条件
        
        Args:
            deepseek_analysis (Dict[str, Any]): DeepSeek的市场分析结果
            current_market_data (Dict[str, Any]): 当前市场数据
        
        Returns:
            Dict[str, Any]: 优化后的策略参数
        """
        prompt = f"""
        作为专业的量化交易策略优化专家，请根据DeepSeek的市场分析结果和当前市场数据，优化以下策略逻辑：
        
        DeepSeek市场分析结果：
        {json.dumps(deepseek_analysis, indent=2)}
        
        当前市场数据：
        {json.dumps(current_market_data, indent=2)}
        
        请提供以下优化结果：
        1. 入场条件：基于情绪得分和技术指标的优化入场规则
        2. 出场条件：止盈止损参数
        3. 仓位大小：基于市场波动率的最优仓位
        4. 交易信号强度：0-100的得分，表示信号的可靠性
        5. 风险管理建议：针对当前市场状态的风险控制措施
        
        请以JSON格式返回结果，包含以下字段：
        - entry_conditions: dict
        - exit_conditions: dict
        - position_size: float
        - signal_strength: int
        - risk_management: dict
        """
        
        payload = {
            "model": "qwen-plus",
            "messages": [
                {"role": "system", "content": "你是一位专业的量化交易策略优化专家，擅长基于市场分析结果调整交易参数。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1200
        }
        
        response = self._call_api("chat/completions", payload)
        if response and "choices" in response:
            try:
                optimized_strategy = json.loads(response["choices"][0]["message"]["content"])
                return optimized_strategy
            except json.JSONDecodeError as e:
                logger.error(f"解析Qwen响应失败: {e}")
                # 返回默认策略参数
                return {
                    "entry_conditions": {"ema_crossover": 1, "rsi_threshold": 50},
                    "exit_conditions": {"take_profit": 1.5, "stop_loss": 1.0},
                    "position_size": 0.01,
                    "signal_strength": 50,
                    "risk_management": {"max_risk": 0.02}
                }
        return {
            "entry_conditions": {"ema_crossover": 1, "rsi_threshold": 50},
            "exit_conditions": {"take_profit": 1.5, "stop_loss": 1.0},
            "position_size": 0.01,
            "signal_strength": 50,
            "risk_management": {"max_risk": 0.02}
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
            "model": "qwen-plus",
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
            "model": "qwen-plus",
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
            "model": "qwen-plus",
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
