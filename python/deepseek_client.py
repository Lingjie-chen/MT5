import requests
import json
import logging
import time
from typing import Dict, Any, Optional, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeepSeekClient:
    """
    DeepSeek API客户端，用于市场分析和情绪得分生成
    使用硅基流动API服务，遵循ValueCell的API调用模式
    """
    def __init__(self, api_key: str, base_url: str = "https://api.siliconflow.cn/v1", model: str = "deepseek-ai/DeepSeek-V3.1-Terminus"):
        """
        初始化DeepSeek客户端
        
        Args:
            api_key (str): 硅基流动API密钥
            base_url (str): API基础URL，默认为https://api.siliconflow.cn/v1
            model (str): 使用的模型名称，默认为deepseek-ai/DeepSeek-V3.1-Terminus
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
        调用DeepSeek API，支持重试机制
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
                # 增加超时时间到60秒，提高在网络不稳定或模型响应慢情况下的成功率
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
    
    def analyze_market_structure(self, market_data: Dict[str, Any], extra_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        分析市场结构，识别趋势与震荡行情
        基于ValueCell的实现，支持JSON模式输出
        
        Args:
            market_data (Dict[str, Any]): 市场数据，包含价格、成交量、指标等
            extra_analysis (Optional[Dict[str, Any]]): 额外的技术分析数据（如CRT、价格方程等）
        
        Returns:
            Dict[str, Any]: 市场结构分析结果
        """
        extra_context = ""
        if extra_analysis:
            extra_context = f"\n额外技术分析参考:\n{json.dumps(extra_analysis, indent=2)}\n"

        prompt = f"""
        作为专业的量化交易分析师，你是混合交易系统的一部分。请分析以下市场数据，识别当前的市场结构。
        {extra_context}
        市场数据：
        {json.dumps(market_data, indent=2)}
        
        请提供以下分析结果：
        1. 市场状态：趋势（上升/下降）、震荡、高波动
        2. 主要支撑位和阻力位
        3. 市场结构评分（0-100）：高分表示趋势明确，低分表示震荡
        4. 短期预测（1-3天）：请提供完整、详细的预测逻辑和目标位描述，不要使用"..."或省略号
        5. 关键指标解读

        如果提供了额外技术分析（如CRT或价格方程），请将其纳入考虑，验证你的结构分析。
        
        请以JSON格式返回结果，包含以下字段：
        - market_state: str
        - support_levels: list[float]
        - resistance_levels: list[float]
        - structure_score: int
        - short_term_prediction: str
        - indicator_analysis: str
        """
        
        # 构建payload，遵循ValueCell的实现
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一位专业的量化交易分析师，擅长市场结构分析和趋势识别。"},
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
                # Log full response to avoid truncation
                logger.info(f"收到模型响应: {message_content}")
                
                analysis_result = json.loads(message_content)
                return analysis_result
            except json.JSONDecodeError as e:
                logger.error(f"解析DeepSeek响应失败: {e}")
                logger.error(f"原始响应: {response}")
                # 如果解析失败，返回默认值
                return {
                    "market_state": "neutral",
                    "support_levels": [],
                    "resistance_levels": [],
                    "structure_score": 50,
                    "short_term_prediction": "neutral",
                    "indicator_analysis": "无法解析市场数据"
                }
        return {
            "market_state": "neutral",
            "support_levels": [],
            "resistance_levels": [],
            "structure_score": 50,
            "short_term_prediction": "neutral",
            "indicator_analysis": "API调用失败"
        }
    
    def generate_sentiment_score(self, historical_data: Dict[str, Any]) -> float:
        """
        生成市场情绪得分
        
        Args:
            historical_data (Dict[str, Any]): 历史市场数据
        
        Returns:
            float: 情绪得分，范围-1到1，-1表示极度看空，1表示极度看多
        """
        prompt = f"""
        作为专业的市场情绪分析师，请根据以下历史数据生成市场情绪得分：
        
        {json.dumps(historical_data, indent=2)}
        
        请基于价格走势、成交量变化和指标信号，生成一个情绪得分。
        得分范围为-1到1，其中：
        - -1：极度看空
        - 0：中性
        - 1：极度看多
        
        请只返回一个数字，不要包含任何其他文字或解释。
        """
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一位专业的市场情绪分析师，擅长基于历史数据生成准确的情绪得分。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 10
        }
        
        response = self._call_api("chat/completions", payload)
        if response and "choices" in response:
            try:
                sentiment_score = float(response["choices"][0]["message"]["content"].strip())
                # 确保得分在-1到1之间
                return max(-1.0, min(1.0, sentiment_score))
            except ValueError:
                logger.error("无法解析情绪得分")
        return 0.0
    
    def process_data_for_qwen(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理数据，为Qwen3提供结构化输入
        
        Args:
            raw_data (Dict[str, Any]): 原始市场数据
        
        Returns:
            Dict[str, Any]: 结构化的模型输入数据
        """
        prompt = f"""
        作为专业的数据分析师，请将以下原始市场数据处理为结构化格式，用于量化交易策略生成：
        
        {json.dumps(raw_data, indent=2)}
        
        请提取关键特征，计算必要的统计指标，并组织成适合输入到交易策略模型的数据格式。
        
        处理要求：
        1. 提取关键价格数据：最高价、最低价、收盘价、成交量
        2. 计算技术指标：EMA交叉、ATR波动率、RSI超买超卖
        3. 识别价格模式：支撑位、阻力位、趋势线
        4. 计算风险指标：波动率、最大回撤
        5. 生成特征向量：用于机器学习模型的输入
        
        请以JSON格式返回处理后的数据，确保结构清晰，便于后续模型处理。
        """
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一位专业的数据分析师，擅长处理金融市场数据，为量化交易策略生成结构化输入。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1500
        }
        
        response = self._call_api("chat/completions", payload)
        if response and "choices" in response:
            try:
                processed_data = json.loads(response["choices"][0]["message"]["content"])
                return processed_data
            except json.JSONDecodeError as e:
                logger.error(f"解析处理后的数据失败: {e}")
                return raw_data
        return raw_data


def main():
    """
    主函数用于测试DeepSeek客户端
    """
    # 示例使用，实际需要替换为有效的API密钥
    api_key = "your_deepseek_api_key"
    client = DeepSeekClient(api_key)
    
    # 示例市场数据
    market_data = {
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
        },
        "recent_candles": [
            {"time": "2024-01-01 10:00", "open": 1.0840, "high": 1.0860, "low": 1.0835, "close": 1.0855},
            {"time": "2024-01-01 09:00", "open": 1.0830, "high": 1.0850, "low": 1.0825, "close": 1.0840},
            {"time": "2024-01-01 08:00", "open": 1.0820, "high": 1.0840, "low": 1.0815, "close": 1.0830}
        ]
    }
    
    # 测试市场结构分析
    structure_analysis = client.analyze_market_structure(market_data)
    print("市场结构分析:")
    print(json.dumps(structure_analysis, indent=2, ensure_ascii=False))
    
    # 测试情绪得分生成
    sentiment_score = client.generate_sentiment_score(market_data)
    print(f"\n市场情绪得分: {sentiment_score}")
    
    # 测试数据处理
    processed_data = client.process_data_for_qwen(market_data)
    print("\n处理后的数据:")
    print(json.dumps(processed_data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
