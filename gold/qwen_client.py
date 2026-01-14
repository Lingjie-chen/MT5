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
    Qwen3 API客户端，用于黄金(XAUUSD)交易决策系统
    基于SMC(Smart Money Concepts)+Martingale(马丁格尔)策略
    使用硅基流动API服务，遵循ValueCell的API调用模式
    """
    
    def _get_system_prompt(self, symbol: str) -> str:
        """
        根据交易品种生成特定的系统提示词 (System Prompt)
        """
        symbol = symbol.upper()
        
        # --- 核心策略架构 ---
        core_strategy = f"""
    作为{symbol}交易的唯一核心决策大脑，你全权负责基于SMC(Smart Money Concepts)和Martingale(马丁格尔)策略的交易执行。
    你的目标是稳定盈利，控制风险，并严格遵循数据驱动的决策流程。
    """
        
        # --- 品种特定指令 (Gold) ---
        gold_instructions = """
    ### Gold (XAUUSD) 核心指令
    1. **市场特性**: 关注美元指数(DXY)、实际利率、地缘政治风险。亚盘震荡，欧盘趋势形成，美盘波动加剧。
    2. **SMC分析**: 寻找H1/H4的订单块(OB)和失衡区(FVG)作为关键支撑阻力。M15作为执行周期。
    3. **网格策略**: 当判断为震荡或需要左侧挂单时，使用 'grid_start'。
        """

        # --- ETH 指令 ---
        eth_instructions = """
    ### ETHUSD 核心指令
    1. **市场特性**: 关注BTC联动、链上Gas费、DeFi锁仓量。24/7交易，波动率极高。
    2. **SMC分析**: 重点关注流动性扫荡(Liquidity Sweep)和结构破坏(BOS)。
    3. **网格策略**: 间距需比黄金更宽 (ATR * 2.0)，以适应高波动。
        """

        target_instructions = gold_instructions if "XAU" in symbol or "GOLD" in symbol else eth_instructions if "ETH" in symbol else f"### {symbol} 通用指令"

        # --- 输出格式与动作定义 ---
        action_definitions = """
    ## 决策输出 (Action) 定义
    你必须从以下列表中选择一个明确的 Action：
    - **buy**: 现价买入 (Market Buy)。仅在SMC结构确认且动能强劲时使用。
    - **sell**: 现价卖出 (Market Sell)。仅在SMC结构确认且动能强劲时使用。
    - **limit_buy**: 挂单买入 (Limit Buy)。在下方的OB/FVG处等待回调。**必须提供 limit_price**。
    - **limit_sell**: 挂单卖出 (Limit Sell)。在上方的OB/FVG处等待回调。**必须提供 limit_price**。
    - **stop_buy**: 突破买入 (Stop Buy)。价格突破关键阻力位时触发。
    - **stop_sell**: 突破卖出 (Stop Sell)。价格跌破关键支撑位时触发。
    - **grid_start**: **网格策略启动**。当你判断市场将进入震荡，或者希望在关键区域分批建仓时使用。系统将基于你的参数自动部署网格。
    - **add_buy**: 逆势加仓买入。仅在已有买单被套且到达下一个SMC支撑位时使用。
    - **add_sell**: 逆势加仓卖出。仅在已有卖单被套且到达下一个SMC阻力位时使用。
    - **close**: 平仓。达到止盈目标或结构破坏(止损)。
    - **hold**: 持有/观望。当前无明确机会，或持仓运行正常。
        """

        # --- JSON 格式要求 ---
        json_format = """
    ## JSON 输出格式 (严格遵守)
    {
        "action": "buy/sell/limit_buy/limit_sell/grid_start/hold/close/...",
        "entry_conditions": {
            "limit_price": float (挂单必填，0.0表示现价)
        },
        "exit_conditions": {
            "sl_price": float (SMC止损位),
            "tp_price": float (SMC止盈位)
        },
        "position_management": {
            "martingale_multiplier": float (例如 1.5),
            "recommended_grid_step_pips": float (网格间距，例如 25.0),
            "grid_level_tp_pips": [30.0, 25.0, 20.0, 15.0, 10.0] (每层网格止盈),
            "dynamic_basket_tp": float (整体止盈金额，例如 50.0)
        },
        "position_size": float (建议仓位，例如 0.01),
        "strategy_rationale": "中文决策理由...",
        "market_structure_analysis": { ... },
        "telegram_report": "Markdown格式简报..."
    }
        """

        return f"{core_strategy}\n{target_instructions}\n{action_definitions}\n{json_format}"

    def __init__(self, api_key: str, base_url: str = "https://api.siliconflow.cn/v1", model: str = "Qwen/Qwen3-VL-235B-A22B-Thinking"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.enable_json_mode = True
        
        # 多品种 API Key 支持
        self.api_keys = {
            "DEFAULT": api_key,
            "ETHUSD": "sk-ftwixmoqnubuwdlutwmwkjxltesmlfiygpjnjaoytljicupf",
            "XAUUSD": "sk-lapiomzehuojnvjentexbctuajfpyfxjakwtowyiwldsfogo",
            "GOLD": "sk-lapiomzehuojnvjentexbctuajfpyfxjakwtowyiwldsfogo"
        }

    def _get_api_key(self, symbol: str = "DEFAULT") -> str:
        key = self.api_keys.get(symbol.upper(), self.api_keys["DEFAULT"])
        if "ETH" in symbol.upper(): key = self.api_keys["ETHUSD"]
        elif "XAU" in symbol.upper() or "GOLD" in symbol.upper(): key = self.api_keys["XAUUSD"]
        return key

    def _call_api(self, endpoint: str, payload: Dict[str, Any], max_retries: int = 3, symbol: str = "DEFAULT") -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/{endpoint}"
        current_api_key = self._get_api_key(symbol)
        headers = self.headers.copy()
        headers["Authorization"] = f"Bearer {current_api_key}"
        
        session = requests.Session()
        session.trust_env = False
        
        for retry in range(max_retries):
            try:
                response = session.post(url, headers=headers, json=payload, timeout=300)
                if response.status_code == 200:
                    return response.json()
                
                logger.warning(f"API调用非200: {response.status_code} - {response.text[:100]}")
                if response.status_code in [401, 403]:
                    logger.error("认证失败，停止重试")
                    return None
                    
            except Exception as e:
                logger.error(f"API请求异常 (Retry {retry+1}): {e}")
            
            time.sleep(min(5 * (retry + 1), 20))
            
        return None

    def analyze_market_structure(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """独立市场结构分析"""
        symbol = market_data.get("symbol", "UNKNOWN")
        prompt = f"分析以下{symbol}市场数据，返回JSON格式的市场结构分析：\n{json.dumps(market_data, indent=2, cls=CustomJSONEncoder)}"
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一流的技术分析师。请分析市场结构(Trend, BOS, CHoCH, Key Levels)。"},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"}
        }
        
        data = self._call_api("chat/completions", payload, symbol=symbol)
        if data and "choices" in data:
            try:
                return json.loads(data["choices"][0]["message"]["content"])
            except:
                pass
        return {} # Fallback

    def analyze_market_sentiment(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """独立情绪分析"""
        symbol = market_data.get("symbol", "UNKNOWN")
        prompt = f"分析以下{symbol}市场数据，返回JSON格式的情绪分析(sentiment, score, reason)：\n{json.dumps(market_data, indent=2, cls=CustomJSONEncoder)}"
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一流的情绪分析师。"},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"}
        }
        
        data = self._call_api("chat/completions", payload, symbol=symbol)
        if data and "choices" in data:
            try:
                return json.loads(data["choices"][0]["message"]["content"])
            except:
                pass
        return {"sentiment": "neutral", "sentiment_score": 0.0}

    def optimize_strategy_logic(self, market_structure_analysis: Dict[str, Any], current_market_data: Dict[str, Any], technical_signals: Optional[Dict[str, Any]] = None, current_positions: Optional[List[Dict[str, Any]]] = None, performance_stats: Optional[List[Dict[str, Any]]] = None, previous_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        核心策略逻辑函数 - 对应 start.py 的调用
        确保返回包含 action, entry_conditions 等关键字段的字典
        """
        symbol = current_market_data.get("symbol", "XAUUSD")
        
        # 1. 确保有市场结构分析
        market_analysis = market_structure_analysis
        if not market_analysis or len(market_analysis) < 3:
            market_analysis = self.analyze_market_structure(current_market_data)
            
        # 2. 构建 Prompt
        system_prompt = self._get_system_prompt(symbol)
        
        user_prompt = f"""
        ## 实时市场数据
        {json.dumps(current_market_data, indent=2, cls=CustomJSONEncoder)}
        
        ## 市场结构分析
        {json.dumps(market_analysis, indent=2, cls=CustomJSONEncoder)}
        
        ## 技术信号 (SMC/Indicators)
        {json.dumps(technical_signals, indent=2, cls=CustomJSONEncoder) if technical_signals else "None"}
        
        ## 当前持仓
        {json.dumps(current_positions, indent=2, cls=CustomJSONEncoder) if current_positions else "None"}
        
        ## 历史绩效
        {json.dumps(performance_stats[:5], indent=2, cls=CustomJSONEncoder) if performance_stats else "None"}
        
        请根据以上信息，输出最终交易决策 JSON。确保 'action' 字段准确无误。
        """
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 2000,
            "temperature": 0.3,
            "response_format": {"type": "json_object"}
        }
        
        # 3. 调用 API
        response_data = self._call_api("chat/completions", payload, symbol=symbol)
        
        # 4. 解析结果 & 默认值回退
        default_decision = {
            "action": "hold",
            "entry_conditions": {"limit_price": 0.0},
            "exit_conditions": {"sl_price": 0.0, "tp_price": 0.0},
            "position_management": {
                "martingale_multiplier": 1.5,
                "recommended_grid_step_pips": 20.0,
                "grid_level_tp_pips": [30.0, 25.0, 20.0, 15.0, 10.0],
                "dynamic_basket_tp": 50.0
            },
            "position_size": 0.01,
            "strategy_rationale": "Default Hold (API Error or Parse Error)",
            "market_structure_analysis": market_analysis,
            "telegram_report": "⚠️ System Warning: Using Default Strategy"
        }
        
        if response_data and "choices" in response_data:
            try:
                content = response_data["choices"][0]["message"]["content"]
                decision = json.loads(content)
                
                # 必须确保关键字段存在
                for key in default_decision.keys():
                    if key not in decision:
                        decision[key] = default_decision[key]
                
                # 特殊处理 position_management
                if "position_management" not in decision or not isinstance(decision["position_management"], dict):
                    decision["position_management"] = default_decision["position_management"]
                
                return decision
            except Exception as e:
                logger.error(f"解析策略响应失败: {e}")
        
        return default_decision

