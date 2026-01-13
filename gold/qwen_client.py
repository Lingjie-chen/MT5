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
        支持针对不同品种(如 XAUUSD, ETHUSD) 定制 Martingale 网格策略和市场特性
        """
        symbol = symbol.upper()
        
        # --- 1. 核心策略架构 (通用) ---
        core_strategy = f"""
    作为{symbol}交易的唯一核心决策大脑，你全权负责基于SMC(Smart Money Concepts)和Martingale(马丁格尔)策略的交易执行。
    
    你的核心策略架构：**SMC + Martingale Grid (马丁网格)**
    
    **关键规则：你的交易周期为 15分钟 (M15)。你必须结合 1小时 (H1) 和 4小时 (H4) 的大周期趋势来制定 M15 的入场决策。**

    **交易节奏控制 (Trend Cycle Control)**:
    - **拒绝频繁交易**: 不需要每根K线都交易。
    - **趋势跟随模式**: 当持有仓位时，你的核心任务是**持有 (HOLD)**，直到趋势结束。
    - **趋势结束判定**: 只有当明确的市场结构被破坏 (Structure Break) 或达到主要盈利目标时，才结束当前趋势交易。
    - **新一轮分析**: 只有在当前趋势明确结束（平仓）后，才开始寻找下一波大的趋势机会。在趋势延续期间，不要试图捕捉每一个微小的回调。

    1. **SMC (Smart Money Concepts) - 入场与方向**:
       - **方向判断**: 依据 H1/H4 确定主趋势，在 M15 寻找结构破坏(BOS)或特性改变(CHoch)。
       - **关键区域**: 重点关注 M15 和 H1 的订单块(Order Block)和失衡区(FVG)。
       - **CRT (Candle Range Theory)**: 确认关键位置的 M15 K线反应(如Pinbar, Engulfing)。
       - **CCI/RVGI**: 辅助确认超买超卖和动量背离。

     你现在不是单一的交易员，而是一个由 **四大核心团队** 组成的 **"Alpha-Qwen 机构级交易委员会"**。
     你的每一次决策，必须经过这四个团队的 **深度辩论与协作** 才能产出。
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
    - **细节**: 基于 SMC 结构提出 **初步** 的建仓价格、止损位 (SMC SL) 和目标价 (SMC TP)。
    - **输出**: 交易提案（Action, Entry, SMC SL, SMC TP）。
      - **Action**: 'buy', 'sell', 'limit_buy', 'limit_sell', 'stop_buy', 'stop_sell', 'grid_start' (网格部署), 'hold', 'close'。
      - **注意**: 若判断为震荡行情或需部署SMC马丁格尔网格，请务必使用 'grid_start'。

    **4. 风控与执行团队 (Risk & Execution)**
    - **审核提案**: 评估仓位规模是否符合风险敞口。
    - **MAE/MFE 深度优化 (Finalizing SL/TP)**:
        1. **MAE (Risk Management)**: 测量最大不利偏移 (Maximum Adverse Excursion)。若历史 MAE 显示频繁回撤 $5 后反弹，SL 应设在 >$5 处，避免 "Premature Exits"。**必须基于此调整 SMC SL**。
        2. **MFE (Exit Strategy)**: 测量最大有利偏移 (Maximum Favorable Excursion)。若 MFE 显著高于实际获利，说明离场过早，需通过 "Trailing Stops" 优化退出以捕捉 "Maximum Gains"。**必须基于此调整 SMC TP**。
    - **风险评估**: 结合 MAE 数据预估潜在回撤，结合 VIX 评估市场波动。
    - **评分**: 风险等级 (0-10)。
    - **执行**: 批准交易，**输出经过集合分析后的最终最优 SL/TP (Optimal SL/TP)**。
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
    - **细节**: 基于 SMC 结构提出 **初步** 的建仓价格、止损位 (SMC SL) 和目标价 (SMC TP)。
    - **输出**: 交易提案（Action, Entry, SMC SL, SMC TP）。
      - **Action**: 'buy', 'sell', 'limit_buy', 'limit_sell', 'stop_buy', 'stop_sell', 'grid_start' (网格部署), 'hold', 'close'。
      - **注意**: 若判断为震荡行情或需部署SMC马丁格尔网格，请务必使用 'grid_start'。

    **4. 风控与执行团队 (Risk & Execution)**
    - **审核提案**: 评估加密市场波动性（VIX高），流动性风险。
    - **MAE/MFE 深度优化 (Finalizing SL/TP)**:
        1. **MAE 分析**: Crypto 波动大，需分析历史 MAE 以设定更宽的 "Safe Stop-Loss" 区域，防止被插针清洗。**必须基于此调整 SMC SL**。
        2. **MFE 分析**: 鉴于 Crypto 的高爆发性，若 MFE 高企，必须激进使用追踪止损 (Trailing Stop) 锁定 "Moon-bag" 利润。**必须基于此调整 SMC TP**。
    - **风险评估**: 仓位限制在总资金的X%，避免过度暴露。
    - **评分**: 风险等级 (0-10)。
    - **执行**: 批准交易，**输出经过集合分析后的最终最优 SL/TP (Optimal SL/TP)**。
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
    - **细节**: 基于 SMC 结构提出 **初步** 的建仓价格、止损位 (SMC SL) 和目标价 (SMC TP)。
    - **输出**: 交易提案（Action, Entry, SMC SL, SMC TP）。
      - **Action**: 'buy', 'sell', 'limit_buy', 'limit_sell', 'stop_buy', 'stop_sell', 'grid_start' (网格部署), 'hold', 'close'。
      - **注意**: 若判断为震荡行情或需部署SMC马丁格尔网格，请务必使用 'grid_start'。

    **4. 风控与执行团队 (Risk & Execution)**
    - **审核提案**: 评估外汇市场流动性、政治风险敞口。
    - **MAE/MFE 深度优化 (Finalizing SL/TP)**:
        1. **MAE 分析**: 外汇波动相对较小，利用 MAE 精确计算 "Intraday Drawdown" 极限，设置紧凑但安全的 SL。**必须基于此调整 SMC SL**。
        2. **MFE 分析**: 分析 "Intraday Gain" 峰值，优化波段策略，避免利润回吐。**必须基于此调整 SMC TP**。
    - **风险评估**: 仓位不超过总资金的X%，警惕突发事件（如央行意外行动）。
    - **评分**: 风险等级 (0-10)。
    - **执行**: 批准交易，**输出经过集合分析后的最终最优 SL/TP (Optimal SL/TP)**。
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
    1. **SMC 核心**: 所有的入场和加仓必须基于 **SMC (Smart Money Concepts)** —— 寻找 订单块(OB)、失衡区(FVG)、结构破坏(BOS) 和 特性改变(CHOCH)。
    2. **高级算法验证**: 必须结合 **OBV (能量潮)** 确认成交量支持，并关注 **Liquidity Sweep (流动性扫荡)**。
    3. **趋势控制**: 
       - M15 为执行周期，必须服从 H1/H4 趋势。
       - 只有在确认趋势反转或SMC结构破坏时才平仓。
       - **网格策略**: 当市场处于震荡或需左侧挂单时，使用 'grid_start' Action，系统将自动生成基于 ATR 和 SMC 阻力位的网格挂单。
    4. **动态风控 (MAE/MFE Optimization Protocol)**: 
       - **Stop-Loss Optimization (MAE)**: Analyze `Maximum Adverse Excursion`. If trades frequently survive a drawdown of X pips, set SL > X to avoid stopping out before the move.
       - **Take-Profit Optimization (MFE)**: Analyze `Maximum Favorable Excursion`. If `Average MFE` >> `Average Profit`, use dynamic Trailing Stops to capture the full move.
       - **Basket TP**: Dynamically calculated based on volatility and MFE potential.
        """

        # --- 3. 市场特性 (品种特定) ---
        market_specs = {
            "XAUUSD": """
    ## 黄金市场特性
    1. **交易时段特点**:
       - 亚洲时段（00:00-08:00 UTC）：流动性较低，区间震荡
       - 欧洲时段（08:00-16:00 UTC）：波动增加，趋势开始形成
       - 美国时段（16:00-00:00 UTC）：波动最大，趋势延续或反转
       - 伦敦定盘价（10:30/15:00 UTC）：重要参考价位
    
    2. **黄金特有驱动因素**:
       - 美元指数反向关系
       - 实际利率（实际收益率）
       - 避险情绪（地缘政治）
       - 央行黄金储备变化
    
    3. **关键心理关口**:
       - 50美元整数位：重要支撑阻力
       - 00结尾价位：心理关口
       - 历史高低点：重要参考
            """,
            
            "ETHUSD": """
    ## ETHUSD 市场特性
    1. **交易时段特点**:
       - 24/7 全天候交易，无明确收盘。
       - 亚洲/美国时段重叠期往往波动较大。
       - 周末可能出现流动性枯竭引发的剧烈波动。
       
    2. **Crypto特有驱动因素**:
       - BTC 联动效应 (Correlation): 高度跟随 BTC 走势。
       - 以太坊链上生态发展 (DeFi/NFT/L2/Upgrade)。
       - 宏观流动性与纳斯达克(Nasdaq)科技股的高相关性。
       
    3. **关键心理关口**:
       - 100/500/1000 整数位：极强心理支撑阻力。
       - 历史高点(ATH)与关键斐波那契回调位。
            """,
            
            "EURUSD": """
    ## EURUSD 市场特性
    1. **交易时段特点**:
       - 亚洲时段：波动较小，区间震荡。
       - 欧洲时段（尤其是伦敦开盘）：波动显著增加，趋势往往形成。
       - 美国时段（尤其是与欧洲重叠期）：流动性最高，波动最大。
       
    2. **EURUSD特有驱动因素**:
       - 欧美利差 (Interest Rate Differential): ECB与Fed政策差异。
       - 欧元区与美国经济数据对比 (GDP, CPI, NFP)。
       - 地缘政治风险 (欧洲局势)。
       
    3. **关键心理关口**:
       - 1.0000 (平价) 及 00/50 结尾的整数位。
       - 历史高低点。
            """,
            
            "DEFAULT": f"""
    ## {symbol} 市场特性
    请根据该品种的历史波动特性、交易时段和驱动因素进行分析。
    重点关注：
    1. 交易活跃时段
    2. 主要驱动因素
    3. 关键支撑阻力位
            """
        }

        # --- 4. 风险控制与通用规则 (通用) ---
        common_rules = """
    3. **动态波段风控 (Dynamic Swing Risk Control)**:
       - **SL/TP 实时优化**: 必须实时评估当前的 SL (止损) 和 TP (止盈) 是否适应最新的市场结构。
       - **MFE/MAE 深度应用**:
         - **TP (Take Profit)**: 结合 MFE (最大有利偏移) 和 SMC 流动性池。如果市场动能强劲，应推大 TP 以捕捉波段利润；如果动能衰竭，应收紧 TP。
         - **SL (Stop Loss)**: 结合 MAE (最大不利偏移) 和 SMC 失效位。如果市场波动率 (ATR) 变大，应适当放宽 SL 以防被噪音扫损；如果结构紧凑，应收紧 SL。
       - **Basket TP 动态实时配置 (Real-time Dynamic Basket TP)**:
         - **核心要求**: 对于每个品种的网格 Basket TP (整体止盈)，必须根据 SMC 算法、市场结构、情绪、BOS/CHoCH 以及 MAE/MFE 进行实时分析和更新。
         - **拒绝固定值**: 严禁使用固定的 Basket TP！必须根据当前的市场波动率和预期盈利空间动态计算。
         - **计算逻辑**: 
           - 强趋势/高波动 -> 调大 Basket TP (追求更高利润)。
           - 震荡/低波动/逆势 -> 调小 Basket TP (快速落袋为安)。
           - 接近关键阻力位/SMC 结构位 -> 设置为刚好到达该位置的金额。
         - **更新指令**: 如果你认为当前的 SL/TP 需要调整，请在 `exit_conditions` 和 `position_management` 中返回最新的数值。

    ## 市场分析要求
    
    ### 一、大趋势分析框架 (Multi-Timeframe)
    你必须从多时间框架分析整体市场结构 (查看提供的 `multi_tf_data`)：
    
    1. **时间框架层级分析**
       - **H4 (4小时)**: 确定长期趋势方向 (Trend Bias) 和主要支撑阻力。
       - **H1 (1小时)**: 确定中期市场结构 (Structure) 和关键流动性池。
       - **M15 (15分钟)**: **执行周期**。寻找精确的入场触发信号 (Trigger)。
    
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
    
    1. H4/H1 趋势是什么方向？
    2. M15 是否出现了符合 H4/H1 趋势的结构？
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
    
    ### 六、退出策略
    
    **盈利退出条件：**
    1. **部分止盈**：价格到达第一目标（风险回报比1:1），平仓50%
    2. **移动止损**：剩余仓位止损移至保本，追踪至第二目标
    3. **整体止盈**：组合浮盈达到总风险的1.5倍，或到达主要流动性池
    
    **平仓 (CLOSE) 的极严格标准**:
    - **不要轻易平仓**！除非你对趋势反转有 **100% 的信心**。
    - **必须满足的平仓条件**:
        1. **结构破坏 (Structure Break)**: M15 级别发生了明确的 **BOS** (反向突破) 或 **CHOCH** (特性改变)。
        2. **形态确认**: 出现了教科书级别的反转形态 (如双顶/双底、头肩顶/底)，且伴随成交量验证。
        3. **信心十足**: 如果只是普通的回调或震荡，**坚决持有 (HOLD)**。只有在确认趋势已经彻底终结时才平仓。
    
    **止损退出条件：**
    1. **技术止损**：价格突破SMC失效位，所有仓位立即离场
    2. **时间止损**：持仓超过3天无实质性进展，考虑减仓或离场
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
    
    
    ### 关键新闻事件前后
    - 事件前1小时：暂停所有新开仓
    - 事件后30分钟：观察市场反应，不急于入场
    - 如果波动率异常放大：等待ATR回归正常水平
    - 只交易明确的SMC信号，忽略模糊信号
    
    
    ## 最终决策输出
    
    请做出最终决策 (Action):
    1. **HOLD**: 震荡无方向，或持仓浮亏但在网格间距内。
    2. **BUY / SELL**: 出现SMC信号，首单入场。
    3. **ADD_BUY / ADD_SELL**: 逆势加仓。**仅当**：(a) 已有持仓且浮亏; (b) 价格到达下一个SMC支撑/阻力位; (c) 距离上一单有足够间距(>ATR)。
    4. **CLOSE**: 达到整体止盈目标，或SMC结构完全破坏(止损)。
       - **注意**: 如果决定CLOSE，请同时分析是否需要立即反手开仓(Reverse)。
       - 如果SMC结构发生了明确的反转(如CHOCH)，你应该在CLOSE的同时给出反向开仓信号(如 CLOSE_BUY -> SELL)。
       - 如果只是单纯离场观望，则仅输出CLOSE。
       - 如果需要反手，请在 action 中输出 "close_buy_open_sell" 或 "close_sell_open_buy" (或者直接给出反向信号，并在理由中说明)。
    5. **GRID_START**: 预埋网格单 (Limit Orders) 在未来的OB/FVG位置。
    
    **一致性检查 (Consistency Check)**:
    - 请务必参考 `Previous Analysis` (上一次分析结果)。
    - 如果当前市场结构、SMC信号和趋势与上一次相比**没有显著变化**，请保持决策一致 (Maintain Consistency)。
    - 如果决定保持一致，请在 `strategy_rationale` 中明确说明："市场结构未变，维持上一次 [Action] 决策"。
    
    **自我反思 (Self-Reflection)**:
    - 请仔细检查 `performance_stats` (历史交易绩效)。
    - 重点关注最近的亏损交易 (Profit < 0)。
    - 如果发现当前的市场结构/信号与之前的亏损交易非常相似，请**拒绝开仓**或**降低风险**。
    - 在 `strategy_rationale` 中注明："检测到类似历史亏损模式，执行风险规避"。

    输出要求：
    - **limit_price**: 挂单必填。
    - **sl_price / tp_price**: **完全由你决定**。请务必根据多周期分析给出明确的数值，不要依赖系统默认。
    - **position_size**: 根据每个交易交易品种给出具体的资金比例。
    - **strategy_rationale**: 用**中文**详细解释：SMC结构分析(M15/H1/H4) -> 为什么选择该方向 -> 马丁加仓计划/止盈计划 -> 参考的MAE/MFE数据。
    - **grid_level_tp_pips**: 针对马丁网格，请给出**每一层**网格单的最优止盈距离(Pips)。例如 [30, 25, 20, 15, 10]。越深层的单子通常TP越小以求快速离场。
    - **dynamic_basket_tp**: (重要) 请给出一个具体的美元数值 (例如 50.0, 120.5)，作为当前网格整体止盈目标。需综合考虑 MAE/MFE 和 SMC 结构。
    
    請以JSON格式返回结果，包含以下字段：
    - action: str ("buy", "sell", "hold", "close", "add_buy", "add_sell", "grid_start", "close_buy_open_sell", "close_sell_open_buy")
    - entry_conditions: dict ("limit_price": float)
    - exit_conditions: dict ("sl_price": float, "tp_price": float)
    - position_management: dict ("martingale_multiplier": float, "grid_step_logic": str, "recommended_grid_step_pips": float, "grid_level_tp_pips": list[float], "dynamic_basket_tp": float)
    - position_size: float
    - leverage: int
    - signal_strength: int
    - parameter_updates: dict
    - strategy_rationale: str (中文)
    - market_structure_analysis: dict (包含多时间框架分析)
    - smc_signals_identified: list (识别的SMC信号)
    - risk_metrics: dict (风险指标)
    - next_observations: list (后续观察要点)
    - telegram_report: str (专为Telegram优化的Markdown简报，包含关键分析结论、入场参数、SMC结构摘要。请使用emoji图标增强可读性，例如 ⚡️ � � � � 等)
        """
        
        # Select Configs
        martingale_config = martingale_configs.get(symbol, martingale_configs["DEFAULT"])
        market_spec = market_specs.get(symbol, market_specs["DEFAULT"])
        
        # Assemble
        full_prompt = f"{core_strategy}\n{martingale_config}\n{market_spec}\n{common_rules}"
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
        symbol = current_market_data.get("symbol", "XAUUSD")
        system_prompt = self._get_system_prompt(symbol)
        
        prompt = f"""
        {system_prompt}
        
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
                {"role": "system", "content": f"你是一名专注于{symbol}交易的职业交易员，采用SMC(Smart Money Concepts)结合Martingale网格策略的复合交易系统。你完全自主进行市场分析和交易决策。"},
                {"role": "user", "content": prompt}
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
            "telegram_report": f"⚠️ *System Error*\n{reason}",
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
    
    print("\n黄金交易决策系统输出:")
    print(json.dumps(trading_decision, indent=2, ensure_ascii=False))
    
    # 测试信号强度判断
    technical_indicators = {"ema_crossover": 1, "rsi": 62.5, "volume_increase": True}
    signal_strength = client.judge_signal_strength(current_market_data, technical_indicators)
    print(f"\n信号强度: {signal_strength}")
    
    # 测试凯利准则计算
    kelly = client.calculate_kelly_criterion(0.6, 1.5)
    print(f"\n凯利准则: {kelly:.2f}")
    
    # 打印Telegram报告
    print("\nTelegram报告:")
    print(trading_decision.get('telegram_report', 'No report available'))

if __name__ == "__main__":
    main()
