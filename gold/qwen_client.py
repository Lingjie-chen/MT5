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
        采用 "多角色协作分析框架" (Multi-Role Collaborative Analysis Framework)
        结合 SMC + Martingale 策略
        """
        symbol = symbol.upper()
        
        # --- 1. 团队架构定义 ---
        role_framework = f"""
    你现在不是单一的交易员，而是一个由 **四大核心团队** 组成的 **"Alpha-Qwen 机构级交易委员会"**。
    你的每一次决策，必须经过这四个团队的 **深度辩论与协作** 才能产出。
    
    **交易品种**: {symbol}
    **核心策略**: SMC (Smart Money Concepts) + Martingale Grid (马丁格尔网格)
    **执行周期**: M15 (结合 H1/H4 趋势)
    """

        # --- 2. 各品种详细角色指令 ---
        
        # Gold Instructions
        gold_instructions = """
    ### 一、Gold（黄金）分析团队指令

    **1. 分析师团队 (The Analyst Team)**
    - **基本面分析师**:
        - **角色**: 专注于黄金的供需基本面、宏观经济关联性及避险属性。
        - **指令**:
            1. 分析全球央行黄金储备动向、珠宝需求、工业用途等供需数据。
            2. 评估通胀率、实际利率（名义利率-通胀率）对黄金价值的影响。
            3. 识别危险信号：如美元走强、利率上升或地缘政治缓和。
            4. 输出：黄金供需平衡报告及价值高估/低估评估。
    - **情绪分析师**:
        - **角色**: 追踪市场对黄金的避险情绪和投机热度。
        - **指令**:
            1. 监测Twitter、Reddit上关于黄金的讨论热度（如#GoldInvesting）。
            2. 计算“恐惧指数”（如地缘政治风险事件引发的避险情绪）。
            3. 短期预测：情绪推动的金价波动方向（如过度乐观或恐慌抛售）。
            4. 输出：情绪评分报告（看涨/看跌/中性）。
    - **新闻分析师**:
        - **角色**: 解读宏观经济与地缘政治事件对黄金的影响。
        - **指令**:
            1. 分析美联储利率决议、通胀数据（CPI/PPI）及地缘冲突（如中东局势）。
            2. 评估突发新闻对黄金的短期/长期影响（如央行购金公告）。
            3. 输出：事件驱动的黄金价格影响评估报告。
    - **技术分析师**:
        - **角色**: 通过图表、SMC高级算法和指标预测趋势。
        - **指令**:
            1. **SMC 核心分析**: 识别图表中的 CHOCH (特性改变) 和 BOS (结构破坏) 以确认趋势反转或延续。
            2. **关键区域识别**: 标注 FVG (失衡区) 和 Order Blocks (订单块)，作为高胜率入场点。
            3. **量价分析**: 使用 OBV (能量潮) 确认价格趋势背后的成交量支持，识别量价背离。
            4. **流动性分析**: 识别上方/下方的 Liquidity Sweep (流动性扫荡) 区域。
            5. **传统指标辅助**: 结合 RSI (背离)、MACD 和布林带作为辅助确认。
            6. **输出**: 包含 SMC 结构、FVG/OB 位置及 OBV 状态的综合技术信号报告。

    **2. 研究员团队 (The Researcher Team)**
    - **看多研究员（Bullish）**:
        - 挖掘亮点：通胀上升、地缘政治紧张、央行持续购金。
        - 反驳空头：利率上升可能被通胀抵消，黄金避险需求仍强。
        - 逻辑：黄金作为抗通胀和避险资产，长期上涨潜力。
    - **看空研究员（Bearish）**:
        - 寻找漏洞：美元走强、利率实际上升、地缘冲突缓和。
        - 反驳多头：投机需求过热，金价可能回调。
        - 逻辑：经济复苏削弱避险需求，技术面超买风险。

    **3. 交易员团队 (Trader Agent)**
    - **综合研判**: 权衡通胀数据、地缘政治风险、技术指标。
    - **策略**: 若通胀超预期+技术面突破阻力位，决定买入黄金。
    - **细节**: 确定建仓价格、止损位、目标价。
    - **输出**: 交易提案（Action, Entry, SL, TP）。

    **4. 风控与执行团队 (Risk & Execution)**
    - **审核提案**: 评估仓位规模是否符合风险敞口。
    - **风险评估**: 当前VIX波动性高，流动性充足。
    - **评分**: 风险等级 (0-10)。
    - **执行**: 批准交易，设置止损并监控市场波动。
        """

        # ETHUSD Instructions
        eth_instructions = """
    ### 二、ETHUSD（以太坊兑美元）分析团队指令

    **1. 分析师团队 (The Analyst Team)**
    - **基本面分析师**:
        - **角色**: 聚焦以太坊生态发展、区块链应用及链上数据。
        - **指令**:
            1. 分析以太坊网络活跃度（Gas费、DeFi锁仓量、NFT交易量）。
            2. 评估关键指标：网络拥堵率、开发者活跃度、Layer2扩展进展。
            3. 识别风险：监管政策、技术漏洞或竞争币（如Solana）威胁。
            4. 输出：以太坊生态健康度报告。
    - **情绪分析师**:
        - **角色**: 追踪加密社区对以太坊的情绪波动。
        - **指令**:
            1. 监测Twitter（#Ethereum）、Reddit（r/CryptoCurrency）讨论热度。
            2. 计算“贪婪指数”：如对合并升级或ETH2.0的过度乐观。
            3. 短期预测：情绪驱动的短期暴涨或暴跌。
            4. 输出：情绪评分报告（极端贪婪/恐慌）。
    - **新闻分析师**:
        - **角色**: 解读监管、技术升级及行业动态对ETH的影响。
        - **指令**:
            1. 分析SEC监管政策、以太坊硬分叉公告、大型机构持仓变化。
            2. 评估事件影响：如美国ETF审批通过 vs. 中国监管打压。
            3. 输出：事件驱动的价格波动评估报告。
    - **技术分析师**:
        - **角色**: 结合SMC算法、OBV及加密专用指标分析ETH趋势。
        - **指令**:
            1. **SMC 结构分析**: 重点识别 CHOCH 和 BOS，确认趋势结构变化。
            2. **流动性与缺口**: 标注 FVG (失衡区) 和 Order Blocks (订单块)，特别是大额清算区域。
            3. **量价与链上**: 结合 OBV (能量潮) 和链上交易量，验证价格突破的有效性。
            4. **加密特性**: 分析 ETH/BTC 汇率相关性及关键斐波那契回撤位。
            5. **输出**: 包含 SMC/FVG/OBV 及链上数据的综合技术分析报告。

    **2. 研究员团队 (The Researcher Team)**
    - **看多研究员（Bullish）**:
        - 亮点：ETH2.0升级成功、DeFi增长、机构采用增加。
        - 反驳空头：监管影响可控，技术领先优势。
        - 逻辑：以太坊作为智能合约龙头，长期增长潜力。
    - **看空研究员（Bearish）**:
        - 漏洞：监管不确定性、高Gas费导致用户流失、Layer2竞争。
        - 反驳多头：技术升级延迟或市场过热泡沫。
        - 逻辑：短期风险大于收益，可能回调。

    **3. 交易员团队 (Trader Agent)**
    - **综合研判**: 技术突破+DeFi锁仓量上升+监管利好传闻。
    - **策略**: 若ETH突破关键阻力位，决定买入。
    - **细节**: 确定建仓价格、止损位、目标价。
    - **输出**: 交易提案。

    **4. 风控与执行团队 (Risk & Execution)**
    - **审核提案**: 评估加密市场波动性（VIX高），流动性风险。
    - **风险评估**: 仓位限制在总资金的X%，避免过度暴露。
    - **评分**: 风险等级 (0-10)。
    - **执行**: 批准交易，设置追踪止损，警惕监管突发风险。
        """

        # EURUSD Instructions
        eur_instructions = """
    ### 三、EURUSD（欧元兑美元）分析团队指令

    **1. 分析师团队 (The Analyst Team)**
    - **基本面分析师**:
        - **角色**: 专注于欧元区与美国的经济差异及货币政策。
        - **指令**:
            1. 分析欧元区GDP、失业率、制造业PMI vs. 美国经济数据。
            2. 评估关键指标：欧元区通胀率、欧央行利率决议预期。
            3. 识别风险：经济衰退、政治动荡（如欧盟选举）或贸易摩擦。
            4. 输出：欧元区经济相对强弱报告。
    - **情绪分析师**:
        - **角色**: 追踪外汇市场对欧元的情绪波动。
        - **指令**:
            1. 监测Twitter（#FXTrader）、专业论坛对欧元前景的讨论。
            2. 计算“风险偏好指数”：如市场对欧央行鹰派/鸽派的预期。
            3. 短期预测：情绪驱动的汇率波动（如避险情绪导致欧元下跌）。
            4. 输出：情绪评分报告（看涨/看跌/中性）。
    - **新闻分析师**:
        - **角色**: 解读货币政策、地缘政治及经济数据对EURUSD的影响。
        - **指令**:
            1. 分析欧央行/美联储利率决议、通胀数据公布、俄乌冲突进展。
            2. 评估事件影响：如欧央行提前加息 vs. 美国经济衰退预期。
            3. 输出：事件驱动的汇率波动评估报告。
    - **技术分析师**:
        - **角色**: 结合SMC算法、OBV及外汇图表分析欧元趋势。
        - **指令**:
            1. **SMC 结构分析**: 精确识别 CHOCH 和 BOS，捕捉趋势反转点。
            2. **机构订单流**: 标注 FVG (失衡区) 和 Order Blocks (订单块)，跟随机构资金流向。
            3. **动能与成交量**: 使用 OBV (能量潮) 和 ADX 判断趋势强度及量价背离。
            4. **流动性猎杀**: 识别关键高低点的 Liquidity Sweep (流动性扫荡)。
            5. **输出**: 包含 SMC/FVG/OBV 及关键斐波那契位的综合技术分析报告。

    **2. 研究员团队 (The Researcher Team)**
    - **看多研究员（Bullish）**:
        - 亮点：欧央行鹰派立场、欧元区经济复苏快于预期。
        - 反驳空头：美国经济放缓，利差缩小支撑欧元。
        - 逻辑：欧元相对美元升值潜力。
    - **看空研究员（Bearish）**:
        - 漏洞：欧元区能源危机、政治不确定性、美国经济韧性。
        - 反驳多头：利差扩大，美元避险需求。
        - 逻辑：欧元下行风险，可能受经济数据拖累。

    **3. 交易员团队 (Trader Agent)**
    - **综合研判**: 欧央行加息预期+技术面突破阻力位。
    - **策略**: 若欧元区数据超预期，决定买入欧元。
    - **细节**: 确定建仓价格、止损位、目标价。
    - **输出**: 交易提案。

    **4. 风控与执行团队 (Risk & Execution)**
    - **审核提案**: 评估外汇市场流动性、政治风险敞口。
    - **风险评估**: 仓位不超过总资金的X%，警惕突发事件（如央行意外行动）。
    - **评分**: 风险等级 (0-10)。
    - **执行**: 批准交易，设置止损，同时考虑对冲策略。
        """

        # Select Instructions
        target_instructions = ""
        if "XAU" in symbol or "GOLD" in symbol:
            target_instructions = gold_instructions
        elif "ETH" in symbol:
            target_instructions = eth_instructions
        elif "EUR" in symbol:
            target_instructions = eur_instructions
        else:
            target_instructions = f"""
    ### {symbol} 分析团队指令 (通用)
    请参照上述标准，组建针对 {symbol} 的分析师、研究员、交易员和风控团队。
    重点关注：SMC结构、市场情绪、基本面驱动和风险控制。
            """

        # --- 3. 策略技术规范 (SMC + Martingale) ---
        # 必须保留原有的马丁格尔参数，供"Trader Agent"和"Risk Team"参考
        
        martingale_configs = {
            "XAUUSD": """
    **交易员与风控团队必须严格遵守的【Martingale网格技术规范 (XAUUSD)】**:
    1. **首单**: 基于SMC信号轻仓 (资金的 0.5%)。
    2. **加仓 (Grid Add)**: 仅在SMC关键位(OB/FVG)加仓，禁止固定间距。
    3. **参数表**:
       - 加仓系数: 1.5倍
       - 最小间距: ATR(14) * 1.5
       - 最大层数: 5层 (总风险 < 15%)
       - 止盈: 下一流动性池或 MFE 80% 分位
            """,
            
            "ETHUSD": """
    **交易员与风控团队必须严格遵守的【Martingale网格技术规范 (ETHUSD)】**:
    1. **首单**: 0.5% 风险。
    2. **加仓**: 必须基于结构位 (OB/FVG)。
    3. **参数表**:
       - 加仓系数: 1.2 - 1.5倍
       - 最小间距: ATR(14) * 2.0 (适应高波动)
       - 最大层数: 5层
            """,
            
            "EURUSD": """
    **交易员与风控团队必须严格遵守的【Martingale网格技术规范 (EURUSD)】**:
    1. **首单**: 0.5% 风险。
    2. **加仓**: 基于结构位。
    3. **参数表**:
       - 加仓系数: 1.5倍
       - 最小间距: ATR(14) * 1.5
       - 最大层数: 8层
            """,
            "DEFAULT": """
    **交易员与风控团队必须严格遵守的【Martingale网格技术规范 (通用)】**:
    1. 首单: 0.5% 风险。
    2. 加仓系数: 1.5倍。
    3. 间距: ATR * 1.5。
    4. 最大层数: 5层。
            """
        }
        
        tech_specs = martingale_configs.get(symbol, martingale_configs["DEFAULT"])
        
        # --- 4. 共同执行规则 ---
        common_rules = """
    ## 共同执行规则 (All Teams Must Follow)
    1. **SMC 核心**: 所有的入场和加仓必须基于 **SMC (Smart Money Concepts)** —— 寻找 订单块(OB)、失衡区(FVG) 和 结构破坏(BOS)。
    2. **趋势控制**: 
       - M15 为执行周期，必须服从 H1/H4 趋势。
       - 只有在确认趋势反转或SMC结构破坏时才平仓。
    3. **动态风控**: 
       - Basket TP (整体止盈) 必须动态计算，随市场波动调整。
       - 实时监控 MAE/MFE，优化 SL/TP。
        """

        # --- 5. 最终组装 ---
        full_prompt = f"{role_framework}\\n{target_instructions}\\n{tech_specs}\\n{common_rules}"
        return full_prompt

    
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

        # API Key Mapping for Multi-Symbol Support
        self.api_keys = {
            "DEFAULT": api_key,
            "ETHUSD": "sk-ftwixmoqnubuwdlutwmwkjxltesmlfiygpjnjaoytljicupf",
            "XAUUSD": "sk-lapiomzehuojnvjentexbctuajfpyfxjakwtowyiwldsfogo",
            "GOLD": "sk-lapiomzehuojnvjentexbctuajfpyfxjakwtowyiwldsfogo",
            "EURUSD": "sk-mwfloodyqbiqpyrmnwsdojupecximapjekwolsjjxgzneglm"
        }

    def _get_api_key(self, symbol: str = "DEFAULT") -> str:
        """根据品种获取对应的 API Key"""
        key = self.api_keys.get(symbol.upper(), self.api_keys["DEFAULT"])
        # Fallback logic if symbol contains substrings
        if "ETH" in symbol.upper(): key = self.api_keys["ETHUSD"]
        elif "XAU" in symbol.upper() or "GOLD" in symbol.upper(): key = self.api_keys["XAUUSD"]
        elif "EUR" in symbol.upper(): key = self.api_keys["EURUSD"]
        return key

    def _call_api(self, endpoint: str, payload: Dict[str, Any], max_retries: int = 3, symbol: str = "DEFAULT") -> Optional[Dict[str, Any]]:
        """
        调用Qwen API，支持重试机制和多品种 API Key 切换
        """
        url = f"{self.base_url}/{endpoint}"
        
        # Determine correct API Key for this call
        current_api_key = self._get_api_key(symbol)
        
        headers = self.headers.copy()
        headers["Authorization"] = f"Bearer {current_api_key}"
        
        for retry in range(max_retries):
            response = None
            try:
                # 增加超时时间到300秒，应对 SiliconFlow/DeepSeek 响应慢的问题
                response = requests.post(url, headers=headers, json=payload, timeout=300)
                
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
    
    def analyze_market_structure(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Qwen 独立市场结构与情绪分析 (多品种通用版)
        完全自主进行市场结构、情绪和SMC信号分析
        """
        symbol = market_data.get("symbol", "UNKNOWN")
        
        prompt = f"""
        作为专业的{symbol}交易员，请根据以下市场数据进行全面的市场结构与情绪分析：
        
        市场数据:
        {json.dumps(market_data, indent=2, cls=CustomJSONEncoder)}
        
        请完成以下分析：
        
        1. **市场特性分析**
           - 当前交易时段特征（亚盘/欧盘/美盘）
           - 相关性分析（如美元指数、BTC、SPX等影响）
           - 避险/风险情绪状态
        
        2. **多时间框架市场结构分析**
           - 识别当前主要趋势方向（牛市/熊市/盘整）
           - 找出关键的市场结构点（BOS/CHoch）
           - 评估市场当前处于哪个阶段（积累/扩张/分配）
        
        3. **SMC信号识别**
           - 识别活跃的订单块(Order Blocks)
           - 识别重要的失衡区(FVGs)
           - 评估流动性池位置
        
        4. **情绪分析**
           - 情绪得分 (Sentiment Score): -1.0 (极度看空) 到 1.0 (极度看多)
           - 市场情绪状态: bullish/bearish/neutral
        
        5. **关键水平识别**
           - 列出3-5个最重要的支撑位
           - 列出3-5个最重要的阻力位
           - 关注心理整数关口
        
        请以JSON格式返回以下内容：
        {{
            "market_structure": {{
                "trend": "bullish/bearish/neutral",
                "phase": "accumulation/expansion/distribution",
                "timeframe_analysis": {{
                    "monthly": str,
                    "weekly": str,
                    "daily": str,
                    "h4": str
                }},
                "key_levels": {{
                    "support": [list of support levels],
                    "resistance": [list of resistance levels]
                }},
                "bos_points": [list of BOS levels],
                "choch_points": [list of CHOCH levels]
            }},
            "smc_signals": {{
                "order_blocks": [list of identified order blocks],
                "fvgs": [list of identified fair value gaps],
                "liquidity_pools": {{
                    "above": price,
                    "below": price
                }}
            }},
            "sentiment_analysis": {{
                "sentiment": "bullish/bearish/neutral",
                "sentiment_score": float (-1.0 to 1.0),
                "confidence": float (0.0 to 1.0),
                "market_context": str (当前市场背景描述)
            }},
            "symbol_specific_analysis": {{
                "trading_session": "asia/europe/us",
                "macro_influence": "positive/negative/neutral",
                "risk_status": "on/off"
            }},
            "key_observations": str (简短的中文分析)
        }}
        """
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": f"你是一位拥有20年经验的华尔街{symbol}交易员，精通SMC(Smart Money Concepts)和价格行为学。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1500,
            "stream": False,
            "response_format": {"type": "json_object"}
        }
        
        response = self._call_api("chat/completions", payload, symbol=symbol)
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
                "timeframe_analysis": {
                    "monthly": "unknown",
                    "weekly": "unknown",
                    "daily": "unknown",
                    "h4": "unknown"
                },
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
                "confidence": 0.0,
                "market_context": "分析失败"
            },
            "symbol_specific_analysis": {
                "trading_session": "unknown",
                "macro_influence": "neutral",
                "risk_status": "unknown"
            },
            "key_observations": "分析失败"
        }

    def analyze_market_sentiment(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        独立的情绪分析模块 - 全方位评估
        """
        logger.info("Executing Sentiment Analysis...")
        symbol = market_data.get("symbol", "DEFAULT")
        
        prompt = f"""
        作为资深{symbol}市场分析师，请依据提供的市场数据，对当前市场情绪和趋势进行深度、全面的评估。
        
        输入数据:
        {json.dumps(market_data, cls=CustomJSONEncoder)}
        
        请从以下核心维度进行分析：
        1. **价格行为与趋势结构 (Price Action)**: 识别当前的高低点排列 (HH/HL 或 LH/LL)，判断市场是处于上升、下降还是震荡整理阶段。
        2. **SMC 视角 (Smart Money Concepts)**: 
           - 关注是否有流动性扫荡 (Liquidity Sweep) 行为。
           - 价格对关键区域 (如 FVG, Order Block) 的反应。
        3. **动能与力度 (Momentum)**: 评估当前走势的强度，是否存在衰竭迹象。
        4. **关键位置**: 当前价格相对于近期支撑/阻力的位置关系。
        
        请严格返回以下 JSON 格式:
        {{
            "sentiment": "bullish" | "bearish" | "neutral",
            "sentiment_score": float, // 范围 -1.0 (极度看空) 到 1.0 (极度看多)
            "trend_assessment": {{
                "direction": "uptrend" | "downtrend" | "sideways",
                "strength": "strong" | "moderate" | "weak"
            }},
            "key_drivers": ["因素1", "因素2", "因素3"],
            "potential_risks": "主要风险点",
            "reason": "综合分析结论 (100字以内)"
        }}
        """
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一位专注于价格行为和SMC策略的黄金交易专家。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 800,
            "response_format": {"type": "json_object"}
        }
        
        try:
            response = self._call_api("chat/completions", payload, symbol=symbol)
            if response and "choices" in response:
                content = response["choices"][0]["message"]["content"]
                return json.loads(content)
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
        
        return {"sentiment": "neutral", "sentiment_score": 0.0, "reason": "Error", "trend_assessment": {"direction": "unknown", "strength": "weak"}}

    def optimize_strategy_logic(self, market_structure_analysis: Dict[str, Any], current_market_data: Dict[str, Any], technical_signals: Optional[Dict[str, Any]] = None, current_positions: Optional[List[Dict[str, Any]]] = None, performance_stats: Optional[List[Dict[str, Any]]] = None, previous_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        黄金(XAUUSD)交易决策系统 - 基于SMC+Martingale策略
        整合完整的交易决策框架，完全自主进行市场分析和交易决策
        
        Args:
            market_structure_analysis (Dict[str, Any]): 市场结构分析结果 (或占位符)
            current_market_data (Dict[str, Any]): 当前市场数据
            technical_signals (Optional[Dict[str, Any]]): 技术信号（SMC/CRT/CCI等）
            current_positions (Optional[List[Dict[str, Any]]]): 当前持仓信息
            performance_stats (Optional[List[Dict[str, Any]]]): 历史交易绩效统计
            previous_analysis (Optional[Dict[str, Any]]): 上一次的分析结果
        
        Returns:
            Dict[str, Any]: 完整的交易决策
        """
        # 首先进行市场结构分析 (如果传入的分析为空或只是占位符，则重新分析)
        market_analysis = market_structure_analysis
        if not market_analysis or len(market_analysis) < 3: # 简单的检查
             market_analysis = self.analyze_market_structure(current_market_data)
        
        # 构建上下文信息
        tech_context = ""
        perf_context = ""
        pos_context = ""
        prev_context = ""
        market_context = ""
        
        # 1. 市场分析结果上下文
        market_context = f"\\n市场结构分析结果:\\n{json.dumps(market_analysis, indent=2, cls=CustomJSONEncoder)}\\n"
        
        # 2. 上一次分析结果上下文
        if previous_analysis:
            prev_action = previous_analysis.get('action', 'unknown')
            prev_rationale = previous_analysis.get('strategy_rationale', 'none')
            prev_context = f"\\n上一次分析结果 (Previous Analysis):\\n- Action: {prev_action}\\n- Rationale: {prev_rationale[:200]}...\\n"
        else:
            prev_context = "\\n上一次分析结果: 无 (首次运行)\\n"
        
        # 3. 当前持仓状态上下文
        if current_positions:
            pos_context = f"\\n当前持仓状态 (包含实时 MFE/MAE 和 R-Multiple):\\n{json.dumps(current_positions, indent=2, cls=CustomJSONEncoder)}\\n"
        else:
            pos_context = "\\n当前无持仓。\\n"

        # 4. 挂单状态上下文
        open_orders = current_market_data.get('open_orders', [])
        orders_context = ""
        if open_orders:
            orders_context = f"\\n当前挂单状态 (Limit/SL/TP):\\n{json.dumps(open_orders, indent=2, cls=CustomJSONEncoder)}\\n"
        else:
            orders_context = "\\n当前无挂单。\\n"

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
                    f"\\n历史交易绩效参考 (用于 MFE/MAE 象限分析与 SL/TP 优化):\\n"
                    f"- 样本交易数: {summary_stats.get('trade_count', 0)}\\n"
                    f"- 胜率 (Win Rate): {summary_stats.get('win_rate', 0):.2f}%\\n"
                    f"- 盈亏比 (Profit Factor): {summary_stats.get('profit_factor', 0):.2f}\\n"
                    f"- 平均 MFE: {summary_stats.get('avg_mfe', 0):.2f}%\\n"
                    f"- 平均 MAE: {summary_stats.get('avg_mae', 0):.2f}%\\n"
                    f"- 最近交易详情 (用于分析体质): \\n{trades_summary}\\n"
                )
            except Exception as e:
                logger.error(f"Error processing stats_to_use: {e}")
                perf_context = "\\n历史交易绩效: 数据解析错误\\n"

        # 6. 技术信号上下文
        if technical_signals:
            sigs_copy = technical_signals.copy()
            if 'performance_stats' in sigs_copy:
                del sigs_copy['performance_stats']
            tech_context = f"\\n技术信号 (SMC/CRT/CCI):\\n{json.dumps(sigs_copy, indent=2, cls=CustomJSONEncoder)}\\n"

        # 构建完整提示词
        symbol = current_market_data.get("symbol", "XAUUSD")
        system_prompt = self._get_system_prompt(symbol)
        
        user_prompt = f"""
        ## 核心指令更新：动态仓位计算 (Dynamic Position Sizing)
        你必须根据以下因素，精确计算本次交易的 **position_size (Lots)**：
        1. **实时账户资金**: {current_market_data.get('account_info', {}).get('available_balance', 10000)} (请根据资金规模合理配比)
        2. **风险偏好**: 单笔风险严格控制在 1% - 3% 之间。
        3. **信号置信度 & 高级算法**: 
        4. **市场情绪**: 结合 {market_analysis.get('sentiment_analysis', {}).get('sentiment', 'neutral')} 情绪调整。
        5. **凯利公式**: 参考你的胜率预估。

        **绝对不要**使用固定的 0.01 手！
        请给出一个精确到小数点后两位的数字 (例如 0.15, 0.50, 1.20)，并在 `strategy_rationale` 中详细解释计算逻辑 (例如："基于2%风险和强SMC信号，计算得出...")。

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
        
        ## {symbol} 特定注意事项
        - 当前交易时段: {market_analysis.get('symbol_specific_analysis', {}).get('trading_session', 'unknown')}
        - 宏观影响: {market_analysis.get('symbol_specific_analysis', {}).get('macro_influence', 'neutral')}
        - 风险状态: {market_analysis.get('symbol_specific_analysis', {}).get('risk_status', 'unknown')}
        
        ## 现在，基于以上所有信息，请输出完整的交易决策
        特别注意：请计算具体的仓位大小，并给出合理的止损止盈点位。
        
        决策要求：
        1. 基于市场结构分析结果进行方向判断
        2. 结合SMC信号寻找最佳入场点
        3. 参考MAE/MFE数据优化止损止盈
        4. 制定Martingale网格加仓计划
        5. 严格遵循风险管理规则
        6. 生成Telegram简报（使用emoji图标增强可读性）
        """
        
        # 构建payload
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 3000,
            "stream": False
        }
        
        # 启用JSON模式
        if self.enable_json_mode:
            payload["response_format"] = {"type": "json_object"}
        
        # 调用API
        response = self._call_api("chat/completions", payload, symbol=symbol)
        if response and "choices" in response:
            try:
                message_content = response["choices"][0]["message"]["content"]
                logger.info(f"收到模型响应: {message_content}")
                
                # 解析响应
                trading_decision = json.loads(message_content)
                
                if not isinstance(trading_decision, dict):
                    logger.error(f"Qwen响应格式错误 (期望dict, 实际{type(trading_decision)}): {trading_decision}")
                    return self._get_default_decision("响应格式错误")
                
                # Qwen 动态计算仓位
                # trading_decision["position_size"] = 0.01 
                
                # 确保必要的字段存在
                required_fields = ['action', 'entry_conditions', 'exit_conditions', 'strategy_rationale', 'telegram_report']
                for field in required_fields:
                    if field not in trading_decision:
                        trading_decision[field] = self._get_default_value(field)
                
                # 再次校验模型返回的 position_size，确保其存在且合法
                if "position_size" not in trading_decision:
                    trading_decision["position_size"] = 0.01 # 默认值作为保底
                else:
                    # 限制范围，防止模型给出极端值
                    try:
                        size = float(trading_decision["position_size"])
                        # 0.01 到 10.0 手之间 (根据资金规模调整，放宽上限以适应大资金)
                        trading_decision["position_size"] = max(0.01, min(10.0, size))
                    except (ValueError, TypeError):
                        trading_decision["position_size"] = 0.01

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
            "leverage": 1,
            "signal_strength": 50,
            "parameter_updates": {},
            "strategy_rationale": reason,
            "market_structure_analysis": {"trend": "neutral", "phase": "waiting"},
            "smc_signals_identified": [],
            "risk_metrics": {"max_risk": 0.02, "current_risk": 0},
            "next_observations": ["等待明确信号"],
            "telegram_report": f"⚠️ *System Error*\\n{reason}",
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
            'leverage': 1,
            'signal_strength': 50,
            'parameter_updates': {},
            'strategy_rationale': "默认决策",
            'market_structure_analysis': {"trend": "neutral", "phase": "waiting"},
            'smc_signals_identified': [],
            'risk_metrics': {"max_risk": 0.02, "current_risk": 0},
            'next_observations': ["等待明确信号"],
            'telegram_report': "⚠️ *Default Decision*",
            'market_analysis': {
                "market_structure": {"trend": "neutral", "phase": "unknown"},
                "sentiment_analysis": {"sentiment": "neutral", "sentiment_score": 0.0}
            }
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
        作为专业的黄金交易信号分析师，请评估以下交易信号的强度：
        
        市场数据：
        {json.dumps(market_data, indent=2)}
        
        技术指标：
        {json.dumps(technical_indicators, indent=2)}
        
        请基于以下因素评估信号强度(0-100)：
        1. 市场结构：当前黄金市场状态是否有利于交易
        2. SMC信号：订单块、失衡区的质量
        3. 多指标共振：技术指标是否一致支持该信号
        4. 成交量：成交量是否支持价格走势
        5. 波动率：当前波动率是否适合交易
        6. 黄金特性：美元走势和避险情绪影响
        
        请只返回一个数字，不要包含任何其他文字或解释。
        """
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一位专业的黄金交易信号分析师，擅长评估交易信号的强度和可靠性。"},
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
    
    # 示例黄金市场数据
    current_market_data = {
        "symbol": "XAUUSD",
        "timeframe": "H1",
        "prices": {
            "open": 2350.50,
            "high": 2365.75,
            "low": 2348.20,
            "close": 2362.30,
            "volume": 125000
        },
        "indicators": {
            "ema_fast": 2355.50,
            "ema_slow": 2348.80,
            "rsi": 62.5,
            "atr": 8.75,
            "cci": 125.3,
            "rvgi": 0.65
        },
        "order_blocks": [
            {"price": 2352.0, "type": "bullish", "timeframe": "H1", "freshness": "fresh"},
            {"price": 2340.0, "type": "bullish", "timeframe": "H4", "freshness": "tested"}
        ],
        "fvgs": [
            {"range": [2355.0, 2348.0], "direction": "bullish"}
        ],
        "market_structure": {
            "higher_tf_trend": "bullish",
            "bos_levels": [2375.0, 2320.0],
            "choch_levels": [2360.0, 2335.0]
        },
        "account_info": {
            "available_balance": 10000.0,
            "total_balance": 12000.0,
            "used_margin": 2000.0
        }
    }
    
    # 测试市场结构分析
    market_analysis = client.analyze_market_structure(current_market_data)
    print("黄金市场结构分析结果:")
    print(json.dumps(market_analysis, indent=2, ensure_ascii=False))
    
    # 测试交易决策
    trading_decision = client.optimize_strategy_logic(
        market_structure_analysis=market_analysis,
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
    
    print("\\n黄金交易决策系统输出:")
    print(json.dumps(trading_decision, indent=2, ensure_ascii=False))
    
    # 测试信号强度判断
    technical_indicators = {"ema_crossover": 1, "rsi": 62.5, "volume_increase": True}
    signal_strength = client.judge_signal_strength(current_market_data, technical_indicators)
    print(f"\\n信号强度: {signal_strength}")
    
    # 测试凯利准则计算
    kelly = client.calculate_kelly_criterion(0.6, 1.5)
    print(f"\\n凯利准则: {kelly:.2f}")
    
    # 打印Telegram报告
    print("\\nTelegram报告:")
    print(trading_decision.get('telegram_report', 'No report available'))

if __name__ == "__main__":
    main()
