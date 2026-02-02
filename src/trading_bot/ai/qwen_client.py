import requests
import json
import logging
import time
import os
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from datetime import datetime, date
try:
    from ..utils.robust_json_parser import safe_parse_or_default
except ImportError:
    # 尝试包内导入
    try:
        from robust_json_parser import safe_parse_or_default
    except ImportError:
        import logging
        logging.getLogger(__name__).warning("Warning: robust_json_parser not found, please ensure it is in the same directory.")
        # 定义一个简单的 fallback 防止 crash，虽然这不应该发生如果文件被正确创建
        def safe_parse_or_default(text, required_keys=None, defaults=None, fallback=None):
            import json
            import re
            try:
                # 简易版 fallback
                match = re.search(r'\{.*\}', text, re.DOTALL)
                if match: return json.loads(match.group(0))
                return json.loads(text)
            except:
                if fallback: return fallback
                raise ValueError("JSON parsing failed (fallback implementation)")

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
        role_definition = f"""
    作为{symbol}交易的唯一核心决策大脑，你全权负责基于SMC(Smart Money Concepts)和趋势跟随(Trend Following)策略的交易执行。
    
    你的核心策略架构：**SMC + Trend Following (趋势跟随)**
    
    **关键规则：你的交易周期为 15分钟 (M15)。你必须结合 1小时 (H1) 和 15分钟 (M15) 的周期趋势来制定入场决策。**
    
    **重要指令: 用户已明确取消网格交易 (Grid Trading Cancelled)。**
    - **禁止**使用任何网格策略 (Grid Strategy)。
    - **禁止**使用 `GRID_START_LONG`, `GRID_START_SHORT` 等 Action。
    - **禁止**逆势加仓 (Martingale)。
    - **必须**使用单边趋势交易 (One-sided Trend Trading)。

    **交易节奏控制 (Trend Cycle Control)**:
    - **拒绝频繁交易**: 不需要每根K线都交易。
    - **趋势跟随模式**: 当持有仓位时，你的核心任务是**持有 (HOLD)**，直到趋势结束。
    - **趋势结束判定**: 只有当明确的市场结构被破坏 (Structure Break) 或达到主要盈利目标时，才结束当前趋势交易。
    - **新一轮分析**: 只有在当前趋势明确结束（平仓）后，才开始寻找下一波大的趋势机会。
    - **拒绝追涨杀跌 (Anti-FOMO)**: 
      - **严禁在局部高点追多 (No Buying at Tops)**: 如果价格处于近期高位 (Premium Zone)，必须等待回调 (Pullback/Callback) 至合理区域 (Discount Zone) 或关键支撑位 (Order Block/FVG) 后再考虑入场。
      - **严禁在局部低点追空 (No Selling at Bottoms)**: 如果价格处于近期低位 (Discount Zone)，必须等待反弹至合理区域 (Premium Zone) 或关键阻力位后再考虑入场。
    -3. **Trend Surfing (趋势冲浪)**: 如果识别到强劲的单边趋势（如价格持续在MA上方或突破关键阻力），不要等待深度回调，但仍需等待 M15 级别的结构确认 (Micro-Structure Confirmation)。

    **策略模式 (Strategy Mode) - 单边趋势专用**:
    *   **模式**: **Trend Following (趋势跟随)** - 顺势而为，果断追击。
    *   **Action**: `BUY` (做多) 或 `SELL` (做空) - **市价单或挂单入场**。
    *   **Grid Add**: **永久禁止 (Disabled)**。
    *   **Position Sizing**: **完全由大模型分析判断**。你必须基于 M15 的市场情绪和技术形态，计算出精确的仓位 (Lots)。
    *   **Risk/Reward Requirement**: **盈亏比 (Risk/Reward Ratio) 必须至少 1.5**。如果 (TP距离 / SL距离) < 1.5，则**禁止开仓**，必须返回 HOLD。

    **仓位管理指令 (Position Sizing Instructions)**:
    - **账户规模感知**: 
        - 账户余额 (Balance) < 1000 USD: 推荐手数 0.01 - 0.02
        - 账户余额 1000 - 5000 USD: 推荐手数 0.03 - 0.10
        - 账户余额 > 5000 USD: 推荐手数 = Balance / 50000 (保守) 或 Balance / 20000 (激进)
        - **必须严格遵守上述比例，禁止过度杠杆。**
    - **Risk per Trade**: 单笔交易风险 (Stop Loss Risk) 不得超过账户余额的 1% - 2%。
    
    1. **SMC (Smart Money Concepts) - 核心入场逻辑**:
       - **结构确认 (Structure Mapping)**:
         - **BOS (Break of Structure)**: 顺势突破结构，确认趋势延续。
         - **CHoCH (Change of Character)**: 逆势反转信号，确认趋势改变。
         - **入场时机**: 必须等待 BOS 后产生的回调 (Retracement) 测试关键区域。
       - **关键区域 (POI - Points of Interest)**:
         - **Order Block (OB)**: 机构留下的未成交订单区域。
         - **FVG (Fair Value Gap)**: 快速移动留下的失衡区，价格倾向于回补。
         - **Supply & Demand Zones**: 严格的供需区。
       - **CRT (Candle Range Theory)**: 确认关键位置的 M15 K线反应(如Pinbar, Engulfing)。
       - **CCI/RVGI**: 辅助确认超买超卖和动量背离。
       - **斐波那契结构 (Fibonacci Structure)**: 
         - **M15 结构分析**: 当你生成分析时，必须基于 15分钟 (M15) 的微观结构来绘制斐波那契回撤位。
         - **分配逻辑**: 寻找 M15 周期内的最新 Swing High/Low，重点关注 0.382, 0.5, 0.618 回撤位作为潜在的浅回调入场点 (尤其在趋势冲浪模式下)。
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
    - **细节**: 基于 SMC 结构提出 **初步** 的建仓价格和目标价 (SMC TP)。
    - **输出**: 交易提案（Action, Entry, SMC TP）。
      - **Action**: 'buy', 'sell', 'limit_buy', 'limit_sell', 'stop_buy', 'stop_sell', 'hold', 'close'。
      - **注意**: 
        - **Market Order (市价单)**: 当 Action 为 'buy' 或 'sell' 时，系统将直接以当前市场价格成交。适用于确认突破或急需入场的情况。
        - **Limit/Stop Order (挂单)**: 当 Action 为 'limit_buy', 'limit_sell', 'stop_buy', 'stop_sell' 时，系统将在指定价格挂单。适用于回调接多或突破确认。
        - **Grid Start**: **已禁用 (Disabled)**。

    **4. 风控与执行团队 (Risk & Execution)**
    - **审核提案**: 评估仓位规模是否符合风险敞口。
    - **MFE 深度优化 (Finalizing TP)**:
        1. **MFE (Exit Strategy)**: 测量最大有利偏移 (Maximum Favorable Excursion)。若 MFE 显著高于实际获利，说明离场过早，需通过优化退出以捕捉 "Maximum Gains"。**必须基于此调整 SMC TP**。
    - **风险评估**: 结合 MAE 数据预估潜在回撤，结合 VIX 评估市场波动。
    - **评分**: 风险等级 (0-10)。
    - **执行**: 批准交易，**输出经过集合分析后的最终最优 TP (Optimal TP)**。

    **5. 学习与自我修正团队 (Self-Learning Team)**
    - **反思机制**: 
        - 每次交易结束后，必须调用 `Trade Reflection` 技能。
        - 分析 `performance_stats` 中的历史盈亏归因。
        - 识别 "Execution Gap" (执行偏差)：计划 vs 实际。
    - **Qlib 深度研习**:
        - 在每个 Session 启动时，主动回顾 Qlib 源码架构。
        - 思考如何利用 Qlib 的 `Data Handler` 和 `Strategy` 模块优化现有的因子分析。
        - 如果发现现有代码效率低下，提出重构建议。
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
    - **细节**: 基于 SMC 结构提出 **初步** 的建仓价格和目标价 (SMC TP)。
    - **输出**: 交易提案（Action, Entry, SMC TP）。
      - **Action**: 'buy', 'sell', 'limit_buy', 'limit_sell', 'stop_buy', 'stop_sell', 'hold', 'close'。
      - **注意**: Grid Start 已禁用。

    **4. 风控与执行团队 (Risk & Execution)**
    - **审核提案**: 评估加密市场波动性（VIX高），流动性风险。
    - **MFE 深度优化 (Finalizing TP)**:
        1. **MFE 分析**: 鉴于 Crypto 的高爆发性，若 MFE 高企，必须激进使用追踪止损 (Trailing Stop) 锁定 "Moon-bag" 利润。**必须基于此调整 SMC TP**。
    - **风险评估**: 仓位限制在总资金的X%，避免过度暴露。
    - **评分**: 风险等级 (0-10)。
    - **执行**: 批准交易，**输出经过集合分析后的最终最优 TP (Optimal TP)**。

    **5. 学习与自我修正团队 (Self-Learning Team)**
    - **反思机制**: 
        - 每次交易结束后，必须调用 `Trade Reflection` 技能。
        - 分析 `performance_stats` 中的历史盈亏归因。
        - 识别 "Execution Gap" (执行偏差)：计划 vs 实际。
    - **Qlib 深度研习**:
        - 在每个 Session 启动时，主动回顾 Qlib 源码架构。
        - 思考如何利用 Qlib 的 `Data Handler` 和 `Strategy` 模块优化现有的因子分析。
        - 如果发现现有代码效率低下，提出重构建议。
        """




        # EURUSD Instructions
        eurusd_instructions = """
    ### 三、EURUSD（欧元兑美元）分析团队指令

    **1. 分析师团队 (The Analyst Team)**
    - **基本面分析师**:
        - **角色**: 专注于欧美两大经济体的货币政策差异与宏观数据。
        - **指令**:
            1. 重点对比美联储 (Fed) 与欧洲央行 (ECB) 的利率决议及政策声明。
            2. 分析关键经济数据差异：非农就业 (NFP)、CPI/PCE 通胀数据、PMI 指数。
            3. 关注欧元区核心国家 (德国、法国) 的经济健康度及政治稳定性。
            4. 输出：欧美货币政策差异及经济强弱对比报告。
    - **情绪分析师**:
        - **角色**: 追踪市场对美元和欧元的投机情绪。
        - **指令**:
            1. 监测 COT 报告 (Commitment of Traders) 中的非商业持仓变化。
            2. 分析美元指数 (DXY) 走势对 EURUSD 的直接压制或支撑。
            3. 关注市场风险偏好 (Risk On/Off) 对融资货币 (Funding Currency) 的影响。
            4. 输出：多空情绪评分及拥挤度评估。
    - **新闻分析师**:
        - **角色**: 即时解读央行官员讲话及突发地缘政治事件。
        - **指令**:
            1. 捕捉拉加德 (Lagarde) 或鲍威尔 (Powell) 的讲话鹰鸽倾向。
            2. 评估俄乌冲突等欧洲地缘政治事件对欧元的冲击。
            3. 输出：新闻事件对汇率的短期冲击评估。
    - **技术分析师**:
        - **角色**: 运用 SMC 和经典图表形态分析 EURUSD 走势。
        - **指令**:
            1. **SMC 结构分析**: 识别 M6/M15 的 BOS (结构破坏) 和 CHOCH (特性改变)。
            2. **流动性识别**: 标注亚洲盘高低点 (Asian Range High/Low) 及午夜开盘价 (Midnight Open) 的流动性掠夺。
            3. **关键时段**: 重点关注伦敦开盘 (London Open) 和纽约开盘 (NY Open) 的 Judas Swing (诱多/诱空)。
            4. **输出**: 包含 SMC 结构、FVG、OB 及关键时段行为的技术分析报告。

    **2. 研究员团队 (The Researcher Team)**
    - **看多研究员（Bullish）**:
        - 亮点：ECB 加息预期升温、美元见顶回落、欧元区经济数据超预期。
        - 反驳空头：美联储暂停加息，利差缩窄利好欧元。
        - 逻辑：估值修复，欧元有望反弹。
    - **看空研究员（Bearish）**:
        - 漏洞：欧元区衰退风险、能源危机隐忧、美元避险属性增强。
        - 反驳多头：ECB 鸽派，美联储维持高利率更久 (Higher for Longer)。
        - 逻辑：经济基本面差异支持美元走强。

    **3. 交易员团队 (Trader Agent)**
    - **综合研判**: 结合欧美利差、DXY 走势及 SMC 结构。
    - **策略**: 若 DXY 遇阻回落且 EURUSD 完成流动性扫荡后出现 CHOCH，决定买入。
    - **细节**: 基于 SMC 提出建仓价格和止盈 (SMC TP)。
    - **输出**: 交易提案（Action, Entry, SMC TP）。
      - **Action**: 'buy', 'sell', 'limit_buy', 'limit_sell', 'stop_buy', 'stop_sell', 'grid_start', 'hold', 'close'。
      - **注意**: 欧美时段重叠期波动最大，适合趋势交易；亚盘适合震荡网格。

    **4. 风控与执行团队 (Risk & Execution)**
    - **审核提案**: 确认非农/CPI 等重大数据发布前后的风险敞口。
    - **MFE 深度优化 (Finalizing TP)**:
        1. **MFE 分析**: 关注 1.0800, 1.1000 等整数关口的反应，适时止盈。
    - **风险评估**: 单笔风险控制在 1-2%。
    - **执行**: 批准交易，**输出经过集合分析后的最终最优 TP (Optimal TP)**。

    **5. 学习与自我修正团队 (Self-Learning Team)**
    - **反思机制**: 
        - 每次交易结束后，必须调用 `Trade Reflection` 技能。
        - 分析 `performance_stats` 中的历史盈亏归因。
        - 识别 "Execution Gap" (执行偏差)：计划 vs 实际。
    - **Qlib 深度研习**:
        - 在每个 Session 启动时，主动回顾 Qlib 源码架构。
        - 思考如何利用 Qlib 的 `Data Handler` 和 `Strategy` 模块优化现有的因子分析。
        - 如果发现现有代码效率低下，提出重构建议。
        """

        # Select Instructions
        target_instructions = ""
        if "XAU" in symbol or "GOLD" in symbol:
            target_instructions = gold_instructions
        elif "ETH" in symbol:
            target_instructions = eth_instructions
        elif "EUR" in symbol:
            target_instructions = eurusd_instructions
        else:
            target_instructions = f"""
    ### {symbol} 分析团队指令 (通用)
    请参照上述标准，组建针对 {symbol} 的分析师、研究员、交易员和风控团队。
    重点关注：SMC结构、市场情绪、基本面驱动和风险控制。
            """

        # --- 3. 策略技术规范 (Trend Only) ---
        # 必须保留原有的参数结构，但内容更新为单边趋势
        
        strategy_specs = """
    ## 交易策略规范 (Trend Following - Strict Mode)

    **核心理念**: 宁可错过，绝不做错。严格等待高质量的回调确认。

    **交易节奏控制 (Trend Cycle Control)**:
    - **拒绝频繁交易**: 不需要每根K线都交易。
    - **趋势跟随模式**: 当持有仓位时，你的核心任务是**持有 (HOLD)**，直到趋势结束。
    - **趋势结束判定**: 只有当明确的市场结构被破坏 (Structure Break) 或达到主要盈利目标时，才结束当前趋势交易。
    - **新一轮分析**: 只有在当前趋势明确结束（平仓）后，才开始寻找下一波大的趋势机会。
    - **拒绝追涨杀跌 (Anti-FOMO)**: 
      - **严禁在局部高点追多 (No Buying at Tops)**: 如果价格处于近期高位 (Premium Zone)，必须等待回调 (Pullback/Callback) 至合理区域 (Discount Zone) 或关键支撑位 (Order Block/FVG) 后再考虑入场。
      - **严禁在局部低点追空 (No Selling at Bottoms)**: 如果价格处于近期低位 (Discount Zone)，必须等待反弹至合理区域 (Premium Zone) 或关键阻力位后再考虑入场。
    - **Trend Surfing (趋势冲浪)**: 如果识别到强劲的单边趋势（如价格持续在MA上方或突破关键阻力），不要等待深度回调，但仍需等待微小级别的结构确认 (Micro-Structure Confirmation)。

    **策略模式 (Strategy Mode) - 单边趋势专用**:
    *   **模式**: **Trend Following (趋势跟随)** - 顺势而为，果断追击。
    *   **Action**: `BUY` (做多) 或 `SELL` (做空) - **市价单或挂单入场**。
    *   **Grid Add**: **永久禁止 (Disabled)**。
    *   **Position Sizing**: **完全由大模型分析判断**。你必须基于 M6/M15 的市场情绪和技术形态，计算出精确的仓位 (Lots)。

    1. **SMC (Smart Money Concepts) - 核心入场逻辑**:
       - **结构确认 (Structure Mapping)**:
         - **BOS (Break of Structure)**: 顺势突破结构，确认趋势延续。
         - **CHoCH (Change of Character)**: 逆势反转信号，确认趋势改变。
         - **入场时机**: 必须等待 BOS 后产生的回调 (Retracement) 测试关键区域。
       - **关键区域 (POI - Points of Interest)**:
         - **Order Block (OB)**: 机构留下的未成交订单区域。
         - **FVG (Fair Value Gap)**: 快速移动留下的失衡区，价格倾向于回补。
         - **Supply & Demand Zones**: 严格的供需区。
       - **CRT (Candle Range Theory)**: 确认关键位置的 M15 K线反应(如Pinbar, Engulfing)。
       - **CCI/RVGI**: 辅助确认超买超卖和动量背离。

    2. **出场与风控 (Exit & Risk)**:
       - **止损 (SL)**: 必须设置在结构保护点之外 (Recent Swing Low/High)。
       - **止盈 (TP)**: 分批止盈。
         - TP1: 1:1.5 RR (风险回报比)。
         - TP2: 下一个关键流动性池 (Liquidity Pool) 或 OB。
         - Trailing Stop: 价格突破关键结构后，将 SL 移动至保本或盈利位。

    3. **市场分析要求**:
       - 在 `analysis_summary` 中，必须明确指出当前的**市场结构 (Bullish/Bearish Structure)**。
       - 必须明确指出当前的**价格位置 (Premium vs Discount)**。
       - 必须明确指出最近的 **BOS** 和 **CHoCH** 位置。
        """

        martingale_configs = {
            "DEFAULT": """
    **交易员与风控团队必须严格遵守的【单边趋势交易技术规范 (Trend Only)】**:
    1. **仓位管理 (Position Sizing)**: 
       - **完全由大模型决定**: 必须基于 M15/H1 的市场情绪 (Sentiment) 和 SMC 结构置信度，计算出精确的首单手数 (Initial Lot)。
       - **禁止固定手数**: 严禁无脑使用 0.01。如果机会好，应该重仓 (e.g., 0.5, 1.0, etc.)；如果风险大，轻仓或空仓。
    2. **加仓 (Adding)**: 
       - **禁止网格加仓 (No Grid)**。
       - **允许顺势金字塔加仓 (Pyramiding)**: 仅当价格向有利方向移动至少 1N (ATR) 且出现新的 SMC 结构突破时，才允许加仓。
    3. **止盈 (TP)**: 必须设定明确的 TP，基于流动性池或 MFE。
    4. **止损 (SL)**: 必须设定明确的 SL，基于结构失效位。
            """
        }
        
        tech_specs = martingale_configs.get(symbol, martingale_configs["DEFAULT"])
        
        # --- 4. 共同执行规则 ---
        common_rules = """
    ## 共同执行规则 (All Teams Must Follow)
    1. **SMC 核心**: 所有的入场和加仓必须基于 **SMC (Smart Money Concepts)** —— 寻找 订单块(OB)、失衡区(FVG)、结构破坏(BOS) 和 特性改变(CHOCH)。
    2. **高级算法验证**: 必须结合 **OBV (能量潮)** 确认成交量支持，并关注 **Liquidity Sweep (流动性扫荡)**。
    3. **趋势控制**: 
       - M15 为执行周期，必须服从 H1 趋势。
       - **量化书籍参考**: 遵循《量化交易策略》中的均值回归与趋势跟踪双重验证原则。
       - 只有在确认趋势反转或SMC结构破坏时才平仓。
       - **单边策略**: 严禁使用 Grid Start。只能使用 BUY/SELL Action。
    4. **动态风控 (MFE Optimization Protocol)**: 
       - **智能配置 (Smart Configuration)**: 开仓时，TP 必须结合 **市场趋势情绪 (Sentiment)**、**MFE (最大有利偏移)** 以及所有高级算法进行自动优化配置。
       - **智能移动 (Smart Strategic Move)**: 
         - **仅限结构性调整**: 只有当市场结构发生重大变化（如新的支撑/阻力形成、SMC 结构破坏）或情绪发生根本性逆转时，才允许移动 TP。
         - **MFE 驱动**: 
             - **TP**: 根据实时 MFE 预测，如果动能衰竭，提前移动 TP 锁定利润。
       - **Basket TP 动态实时配置 (Real-time Dynamic Basket TP)**:
         - **核心要求**: 对于每个品种的网格 Basket TP (整体止盈)，必须根据以下所有维度进行综合分析和自我学习，给出一个**最优的美元数值**：
           1. **市场情绪 (Sentiment)**: 如果情绪极度乐观(Bullish)且方向做多，大幅上调 Basket TP；反之则保守。
           2. **结构趋势 (Structure)**: 
              - **强趋势 (Trend Surfing)**: 若市场处于单边强趋势 (如 H1/H4 结构破坏且 MA 发散)，**必须大幅上调 Basket TP** (例如正常值的 2-3 倍)，防止只吃了一小部分利润就过早离场。
              - **震荡/逆势**: 目标应保守，快速落袋为安。
           3. **高级算法 (Algo Metrics)**: 
              - 参考 `technical_signals` 中的 **EMA/HA** 数据。
              - 如果价格远离 EMA 50 (乖离率高)，预期会有回归，TP 应保守。
              - 如果 EMA 50 强劲倾斜且 HA 连续同色，TP 应激进。
           4. **历史绩效 (Self-Learning)**: 
              - **必须参考** `performance_stats` 中的 `avg_mfe` (平均最大有利偏移)。
              - **Basket TP 上限** = (Position Size * Contract Size * Avg_MFE_Points * 0.8)。不要设定超过历史平均表现太多的不切实际目标。
              - **Basket TP 下限** = 能够覆盖交易成本 (Spread + Swap + Commission) 的最小利润。
           5. **量化书籍优化**: 
              - 引入 Kelly Criterion (凯利公式) 思想，在胜率高时允许更大的 TP 以最大化几何增长。
              - 参考《交易系统的胜算》中的 "Expectancy" (期望值) 概念，确保 (WinRate * AvgWin) > (LossRate * AvgLoss)。
           6. **长期历史优化种子 (Long-term Optimization Seeds)**:
              - **必须参考** `historical_seeds` 中的最佳参数组合。
              - 如果历史数据显示某组参数 (如特定的 SMC ATR 阈值或 Grid Step) 长期表现优异，应在策略制定中给予更高权重。
              - 将历史最优参数作为决策的 "Anchor" (锚点)，在此基础上进行微调，而不是凭空猜测。
         - **计算公式参考**:
           - `Base_Target` = (ATR * Position_Size * Contract_Size)
           - `Sentiment_Multiplier`: 0.5 (Weak) to 3.0 (Strong Trend)
           - `Structure_Multiplier`: 0.8 (Range) to 2.0 (Trend Surfing)
           - `Dynamic_Basket_TP` = `Base_Target` * `Sentiment_Multiplier` * `Structure_Multiplier` (并用 Avg_MFE 做校验)
         - **拒绝固定值**: 严禁使用固定的数值 (如 50.0)！必须是经过上述逻辑计算后的结果。
         - **更新指令**: 在 `position_management` -> `dynamic_basket_tp` 中返回计算后的数值。
       - **Lock Profit Trigger (Profit Locking)**:
         - **User Instruction**: **已被禁用**。请不要设置此值，或将其设置为 null / 0。我们不再使用利润锁定机制，完全依赖 Basket TP。
         - **更新指令**: 在 `position_management` -> `lock_profit_trigger` 中返回 null 或 0。
       - **Trailing Stop Config (移动止损配置)**:
         - **User Instruction**: **已被禁用**。请不要设置此值。
         - **更新指令**: 在 `position_management` -> `trailing_stop_config` 中返回 null。

    5. **CandleSmoothing EMA 策略 (Strategy B)**:
       - **核心逻辑**: 基于 EMA50 趋势过滤，结合 EMA20 High/Low 通道突破和 Heiken Ashi 蜡烛形态。
       - **做多信号 (Buy)**: HA收盘价 > EMA20 High AND HA阳线 AND HA收盘价 > EMA50 AND EMA50上升趋势 AND 前一HA收盘价 < EMA50 (金叉)。
       - **做空信号 (Sell)**: HA收盘价 < EMA20 Low AND HA阴线 AND HA收盘价 < EMA50 AND EMA50下降趋势 AND 前一HA收盘价 > EMA50 (死叉)。
       - **权重**: 当此策略发出信号且与 SMC 结构方向一致时，置信度应显著提高。

    6. **LLM原生风控配置 (LLM-Native Risk Management)**:
       - **核心思想**: 摒弃固定参数，所有风控指标必须由大模型实时分析得出。
       - **Max Drawdown (最大回撤配置)**:
         - 在 `grid_config` 中必须输出 `max_drawdown_usd`。
         - **计算逻辑**: Account_Balance * Risk_Tolerance_Factor (e.g., 0.05 for conservative, 0.15 for aggressive).
         - **动态调整 (Dynamic Adjustment)**: 
           - **Volatility Based**: 参考 `risk_metrics.volatility` (ATR)。如果当前 ATR > Average ATR * 1.5，说明市场剧烈波动，必须 **降低** Max Drawdown (例如减半) 以防止被动止损。
           - **Event Based**: 当 VIX > 20 或 市场处于重大新闻发布前，必须降低 Risk_Tolerance_Factor。
         - **硬性限制**: 任何时候，`max_drawdown_usd` 不得超过账户总资金的 20%。

    7. **Turtle Trading Protocol (海龟交易法则 - 趋势跟随)**:
       - **唐奇安通道 (Donchian Channel)**: 
         - **突破信号**: 关注 `donchian` 指标。当价格突破 Donchian Upper (20日高点) 时，为潜在做多信号；跌破 Donchian Lower (20日低点) 时，为潜在做空信号。
         - **SMC 过滤**: 海龟信号必须得到 SMC 结构的验证 (即突破方向必须有 FVG 或 OB 支持)。
         - **退出规则**: 使用 10日 Donchian 反向突破作为趋势结束的离场信号 (Trailing Stop)。
       - **加仓 (Pyramiding)**: 趋势确认后，若价格继续向有利方向移动 1N (1 ATR)，可加仓。

    8. **Strict Supply/Demand (严格供需)**:
       - **优先权**: 在寻找入场位时，优先参考 `strict_supply_demand` 返回的区域，而非普通 OB。
       - **特征**: 这些区域具备 "Strong Impulse" (强力脱离) 和 "Fresh Base" (新鲜基地)，胜率更高。
       - **操作**: 在 Demand Zone 上沿挂 Limit Buy，在 Supply Zone 下沿挂 Limit Sell。
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
       - **伦敦时段 (07:00 - 16:00 UTC)**: 交易量最大，趋势往往在此形成。
       - **纽约时段 (12:00 - 21:00 UTC)**: 与伦敦重叠期 (12:00-16:00 UTC) 波动最剧烈。
       - **亚洲时段**: 通常波动较小，以区间震荡为主。
       
    2. **主要驱动因素**:
       - **欧美利差**: 美联储与欧洲央行的利率政策差异。
       - **宏观数据**: 美国非农 (NFP)、CPI、GDP；欧元区 CPI、PMI。
       - **避险情绪**: 风险厌恶时资金流向美元，利空 EURUSD。
       
    3. **关键心理关口**:
       - 00 和 50 结尾的整数位 (如 1.0800, 1.0850)。
       - 历史年度高低点。
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

        analysis_framework = """
    ### 一、大趋势分析框架 (Multi-Timeframe)
    你必须从多时间框架分析整体市场结构 (查看提供的 `multi_tf_data`):
    
    1. **时间框架层级分析**
       - **H1 (1小时)**: 确定长期趋势方向 (Trend Bias) 和主要支撑阻力。
       - **M15 (15分钟)**: **执行周期**。确定市场结构 (Structure)、关键流动性池，并寻找入场触发信号 (Trigger)。
    
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
    
    1. H1 趋势是什么方向？
    2. M15 是否出现了符合 H1 趋势的结构？
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
       - **量化优化**: 价格应处于 50%-61.8% Fibonacci 回撤位附近，或完成 Liquidity Sweep (流动性扫荡)。
    
    2. **CRT确认信号出现**
       - 明显的反转或延续形态
       - 收盘确认信号有效性
    
    3. **动量指标支持**
       - CCI显示背离或极端值回归
       - RVGI确认成交量配合
       - **高级算法**: 参考 EMA20/50 均线排列和 Heiken Ashi 颜色一致性。
    
    4. **流动性目标明确**
       - **盈亏比要求**: 预期盈利(Reward) 必须至少是 潜在风险(Risk) 的 1.5倍。
       - **风险定义**: 即便我们不设硬止损，你也必须基于 **最近的结构失效点 (Structural Invalidation)** 来估算潜在风险距离。
       - **拒绝交易**: 如果 (TP距离 / 结构失效距离) < 1.5，请直接返回 **HOLD**，不要开仓。
       - 明确的上方/下方流动性目标
    
    ### 六、退出策略 (Grid Exit Logic)
    
    **整体止盈 (Basket TP)**:
    1. **目标设定**: 网格策略的核心在于整体浮盈出场。请基于 ATR 和 SMC 阻力位计算 `basket_tp_usd`。
    2. **动态调整**: 当市场动能衰竭或遇到强阻力时，应在下一次分析中降低 `basket_tp_usd` 以确保落袋为安。
    
    **平仓 (CLOSE_ALL) 标准**:
    - **仅用于紧急情况**: 正常情况下，让网格自动止盈。只有在以下情况手动 CLOSE_ALL：
        1. **结构彻底破坏**: H4/H1 趋势完全反转。
        2. **重大风险事件**: 即将发布超预期利空数据。
        3. **风控触发**: 浮亏超过账户净值的 20% (或预设阈值)。
    
    **止损退出**:
    - 网格策略不设单单止损，而是依赖 `basket_sl_usd` (整体止损)。请在 `grid_config` 中合理设置此值。
    
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
    3. 具体入场计划（价格、仓位、止盈）
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
    1. **GRID_START_LONG**:
       - 含义: 启动多头网格策略 (Initial Entry + Grid Setup)。
       - 适用场景: SMC 确认看涨趋势 (BOS/CHOCH)，价格位于 H4/H1 关键支撑位 (OB/FVG)。
       - **执行逻辑**: 系统将立即开启首单 BUY，并自动挂出后续的 LIMIT_BUY 网格单。
    2. **GRID_START_SHORT**:
       - 含义: 启动空头网格策略 (Initial Entry + Grid Setup)。
       - 适用场景: SMC 确认看跌趋势 (BOS/CHOCH)，价格位于 H4/H1 关键阻力位 (OB/FVG)。
       - **执行逻辑**: 系统将立即开启首单 SELL，并自动挂出后续的 LIMIT_SELL 网格单。
    3. **HOLD**:
       - 含义: 暂时观望，不开启新网格。
       - 适用场景: 市场方向不明、处于震荡区间中间、或已有网格在运行中。
       - **注意**: 如果已有持仓，HOLD 意味着维持当前网格策略不变。
    4. **CLOSE_ALL**:
       - 含义: 紧急平仓所有头寸 (Panic Button)。
       - 适用场景: 发生重大基本面利空、SMC 结构完全失效 (失效位被强力击穿)、或达到总账户风控阈值。

    **自我学习与适应 (Self-Learning & Adaptation)**:
    - **数据源**: 你现在接收来自远程数据库 (Remote DB) 的实时历史交易数据 (`performance_stats`)。
    - **动态修正**:
        1. **胜率低**: 如果 `win_rate` < 40%，请在 `grid_config` 中增大 `grid_step_pips` (拉大网格间距) 以降低风险。
        2. **波动率高**: 如果当前 ATR 显著高于 `avg_atr`，请在 `grid_config` 中使用 `atr_based` 间距。
        3. **连败保护**: 如果 `recent_trades` 显示连续亏损，请在 `rationale` 中建议暂停开新仓或降低 `initial_lot`。

    **一致性检查 (Consistency Check)**:
    - **SMC 验证**: 你的 GRID_START 决策必须得到 SMC 结构的支持 (如 H1 Order Block 支撑)。严禁在毫无依据的半空中开网格。
    - **趋势顺势**: 尽量顺应 H4 大趋势开启网格。逆势网格必须有更严格的过滤条件。

    ## 市场分析要求 - 严格 JSON 输出

    请以 **JSON 格式** 返回结果，严禁包含 markdown 代码块标记 (如 ```json ... ```)，只返回纯 JSON 字符串。
    JSON 必须包含以下字段：

    - **action**: str ("GRID_START_LONG", "GRID_START_SHORT", "HOLD", "CLOSE_ALL", "BUY", "SELL")
    - **strategy_mode**: str ("grid" 或 "trend") -- 必须明确指定当前策略模式
    - **sl**: float (趋势交易止损价格. 对于 BUY/SELL Action 必须提供)
    - **tp**: float (趋势交易止盈价格. 对于 BUY/SELL Action 必须提供)
    - **grid_config**: dict (网格策略核心参数)
        - "initial_lot": float (首单手数, e.g., 0.01)
        - "allow_add": bool (是否允许网格加仓. Grid模式=true, Trend模式=false)
        - "grid_step_mode": str ("fixed" 或 "atr")
        - "grid_step_pips": float (基础网格间距, e.g., 20.0)
        - "martingale_mode": str ("multiply" 或 "add")
        - "martingale_multiplier": float (马丁倍数, e.g., 1.5)
        - "max_grid_levels": int (最大网格层数, e.g., 5)
        - "basket_tp_usd": float (整体止盈金额 USD, e.g., 50.0)
        - "basket_sl_usd": float (整体止损金额 USD, e.g., -200.0)
        - "max_drawdown_usd": float (网格交易最大允许回撤 USD, e.g., 500.0. 必须基于账户资金和风险偏好由大模型分析得出)
    - **strategy_rationale**: str (中文, 详细解释 SMC 结构、为什么在此处启动网格、ATR 分析等)
    - **market_structure**: dict (SMC 分析摘要)
        - "trend_h1": str (H1 趋势分析)
        - "trend_m15": str (M15 趋势分析)
        - "key_level": str (关键位分析)
    - **telegram_report**: str (Markdown 格式的简报，用于发送通知。包含 emoji，简洁明了)
        """
        
        # Select Configs
        martingale_config = martingale_configs.get(symbol, martingale_configs["DEFAULT"])
        market_spec = market_specs.get(symbol, market_specs["DEFAULT"])
        
        # Reflection Skills (Synced from CLAUDE.local.md)
        reflection_skills = """
    ## Skill: Trade Reflection & Self-Improvement (交易反思与自我提升)

    **Description:**
    此技能用于指导大模型在每一笔交易（或网格周期）结束后进行深度自我反思，分析盈亏原因，识别不足，并提出具体的改进措施，从而实现策略的自我迭代与优化。

    **Trigger:**
    当检测到交易结束（`CLOSE`、`CLOSE_ALL` 或止盈/止损触发）时调用。

    **Analysis Framework (反思框架):**

    1.  **盈亏归因分析 (Attribution Analysis)**:
        *   **盈利 (Win)**:
            *   核心驱动力是什么？(SMC结构准确 / 顺势交易 / 运气?)
            *   *为什么盈利少 (Low Profit)?*: 是否离场过早？移动止损(Trailing Stop)是否太紧？网格层数是否不足？
        *   **亏损 (Loss)**:
            *   核心败因是什么？(逆势抄底 / 关键位失效 / 重大新闻冲击?)
            *   *为什么亏损大 (High Loss)?*: 网格间距(Grid Step)是否太密？马丁倍数(Multiplier)是否过高？是否未及时止损？

    2.  **执行偏差检查 (Execution Gap)**:
        *   对比 **交易计划 (Strategy Rationale)** 与 **实际执行 (Actual Execution)**。
        *   是否存在“知行不一”的情况？(例如：计划说做多，实际却在高位开了空)

    3.  **自我提升行动 (Actionable Improvements)**:
        *   **Keep (保持)**: 本次交易中做对的一件事 (例如：耐心等待了 H1 回调)。
        *   **Fix (改进)**: 下次必须修正的一个弱点 (例如：在 ATR 高波动时，将网格间距扩大 1.5 倍)。
        *   **Optimization (优化)**: 针对参数的微调建议 (例如：建议将 `initial_lot` 从 0.01 降至 0.005，或将 `basket_tp` 提高 $10)。

    **Output Format (输出格式 - 存入 Long-Term Memory):**

    ```json
    {
      "reflection_type": "POST_TRADE_ANALYSIS",
      "trade_id": "{TICKET_ID}",
      "outcome": "WIN" | "LOSS",
      "reasoning": "简述盈亏的核心逻辑 (中文)",
      "shortcomings": "本次交易的不足之处",
      "improvements": "下次交易的具体改进措施",
      "self_rating": 8.5  // (0-10分 自我评分)
    }
    ```

    **Usage Instruction:**
    请在每次 `analyze_market` 的 prompt 中包含上述反思的历史记录 (Memory Retrieval)，以确保大模型能够“记住”之前的教训，避免犯同样的错误。
        """

        # Assemble
        full_prompt = f"{role_definition}\n{analysis_framework}\n{martingale_config}\n{market_spec}\n{common_rules}\n{reflection_skills}"
        return full_prompt

    
    def __init__(self, api_key: str, base_url: str = "https://api.siliconflow.cn/v1", model: str = "Qwen/Qwen3-VL-235B-A22B-Thinking"):
        """
        初始化Qwen客户端
        
        Args:
            api_key (str): 默认 API 密钥 (用于 Gold/XAUUSD)
            base_url (str): 默认 API 基础 URL
            model (str): 默认模型名称
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

        # --- 多品种配置中心 (Multi-Symbol Configuration) ---
        import os
        
        # 加载环境变量中的 EURUSD 配置
        eurusd_key = os.getenv("EURUSD_API_KEY", api_key)
        eurusd_url = os.getenv("EURUSD_API_URL", "https://api.siliconflow.cn/v1")
        eurusd_model = os.getenv("EURUSD_MODEL", "Qwen/Qwen3-VL-235B-A22B-Thinking")
        
        # 加载环境变量中的 ETHUSD 配置
        ethusd_key = os.getenv("ETHUSD_API_KEY", api_key)
        ethusd_url = os.getenv("ETHUSD_API_URL", "https://api.siliconflow.cn/v1")
        ethusd_model = os.getenv("ETHUSD_MODEL", "Qwen/Qwen3-VL-235B-A22B-Thinking")
        
        # 默认配置 (Gold/XAUUSD 使用 SiliconFlow GLM-4.7)
        default_config = {
            "api_key": api_key,
            "base_url": base_url,
            "model": model
        }
        
        # 专用配置
        eurusd_config = {
            "api_key": eurusd_key,
            "base_url": eurusd_url,
            "model": eurusd_model
        }
        
        ethusd_config = {
            "api_key": ethusd_key,
            "base_url": ethusd_url,
            "model": ethusd_model
        }
        
        self.symbol_configs = {
            "DEFAULT": default_config,
            "XAUUSD": default_config,
            "GOLD": default_config,
            "ETHUSD": ethusd_config,
            "EURUSD": eurusd_config
        }

    def _get_config(self, symbol: str) -> Dict[str, str]:
        """根据品种获取完整的配置 (Key, URL, Model)"""
        symbol = symbol.upper()
        if "EUR" in symbol:
            return self.symbol_configs["EURUSD"]
        elif "XAU" in symbol or "GOLD" in symbol:
            return self.symbol_configs["XAUUSD"]
        elif "ETH" in symbol:
            return self.symbol_configs["ETHUSD"]
        else:
            return self.symbol_configs["DEFAULT"]

    def _call_api(self, endpoint: str, payload: Dict[str, Any], max_retries: int = 3, symbol: str = "DEFAULT") -> Optional[Dict[str, Any]]:
        """
        调用Qwen API，支持重试机制和多品种配置动态切换
        """
        # 1. 获取当前品种的特定配置
        config = self._get_config(symbol)
        current_api_key = config["api_key"]
        current_base_url = config["base_url"]
        current_model = config["model"]
        
        # 2. 动态检测是否为 ChatAnywhere
        is_chatanywhere = "chatanywhere" in current_base_url
        
        url = f"{current_base_url}/{endpoint}"
        
        headers = self.headers.copy()
        headers["Authorization"] = f"Bearer {current_api_key}"
        
        # 3. 动态更新 payload 中的 model 字段 (如果存在)
        if "model" in payload:
            payload["model"] = current_model
            
        # ChatAnywhere 兼容性适配
        if is_chatanywhere:
            # 确保 stream 显式设置为 False (如果未设置)
            if "stream" not in payload:
                payload["stream"] = False
                
            # 强制移除 response_format
            # 原因：ChatAnywhere (或其背后的 gpt-5.1 映射) 在启用 json_object 模式时极不稳定，
            # 经常返回 HTTP 200 但 Content-Length 为 0 的空响应。
            # 我们必须移除此参数，并完全依赖 Prompt 指令和 robust_json_parser 来提取 JSON。
            if "response_format" in payload:
                logger.info(f"[{symbol}] ChatAnywhere: 强制移除 response_format 以避免空响应问题")
                del payload["response_format"]
            
        # Create a session to manage settings
        session = requests.Session()
        session.trust_env = False # Disable environment proxies
        
        # 获取超时设置，默认为 300 秒
        timeout = int(os.getenv("API_TIMEOUT", 300))
        
        for retry in range(max_retries):
            response = None
            try:
                # 使用配置的超时时间
                response = session.post(url, headers=headers, json=payload, timeout=timeout)
                
                # 详细记录响应状态
                logger.debug(f"API响应状态码: {response.status_code}, Symbol: {symbol}, 模型: {current_model}")
                
                # 处理不同状态码
                if response.status_code == 401:
                    logger.error(f"API认证失败 ({symbol})，状态码: {response.status_code}")
                    return None
                elif response.status_code == 403:
                    logger.error(f"API访问被拒绝 ({symbol})，状态码: {response.status_code}")
                    return None
                elif response.status_code == 429:
                    logger.warning(f"API请求频率过高，状态码: {response.status_code}，进入退避重试")
                elif response.status_code >= 500:
                    logger.error(f"API服务器错误，状态码: {response.status_code}")
                
                response.raise_for_status()
                
                # 解析响应并添加调试信息
                try:
                    response_json = response.json()
                    logger.info(f"API调用成功 [{symbol}], 状态码: {response.status_code}, 模型: {current_model}")
                    return response_json
                except json.JSONDecodeError:
                    # 如果直接返回了内容字符串 (非标准API行为，但以防万一)
                    logger.warning(f"API返回非JSON格式，尝试直接包装: {response.text[:100]}...")
                    return {"choices": [{"message": {"content": response.text}}]}

            except requests.exceptions.ConnectionError as e:
                logger.error(f"API连接失败 (重试 {retry+1}/{max_retries}): {e}")
                logger.error(f"请求URL: {repr(url)}")
                logger.error("请检查网络连接和API服务可用性")
            except requests.exceptions.Timeout as e:
                logger.error(f"API请求超时 (重试 {retry+1}/{max_retries}): {e}")
                logger.error(f"请求URL: {repr(url)}")
                logger.error(f"当前超时设置: {timeout}秒. 可通过环境变量 'API_TIMEOUT' 增加此值")
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
        
        3. **SMC信号识别 (详细)**
           - 识别活跃的订单块(Order Blocks) 和 严格的供需区 (Supply/Demand Zones)
           - 识别重要的失衡区(FVGs)
           - 评估流动性池位置 (Liquidity Pools)
           - **结构确认**: 明确指出最近的 BOS (结构破坏) 和 CHoCH (特性改变) 位置
           - **位置评估**: 当前价格是否处于 Premium (溢价区) 还是 Discount (折扣区)？

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
                    "h1": str,
                    "m15": str
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
                {"role": "system", "content": f"你是一位拥有20年经验的华尔街{symbol}交易员，精通SMC(Smart Money Concepts)和价格行为学。IMPORTANT: You must output strictly valid JSON format only."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1500,
            "stream": False,
            "response_format": {"type": "json_object"}
        }
        
        # 调用API (带应用层重试机制)
        max_app_retries = 3
        for attempt in range(max_app_retries):
            response = self._call_api("chat/completions", payload, symbol=symbol)
            if response and "choices" in response:
                try:
                    content = response["choices"][0]["message"]["content"]
                    
                    if not content or len(content.strip()) == 0:
                        logger.warning(f"市场结构分析收到空响应 (Attempt {attempt+1}/{max_app_retries})，尝试重试...")
                        time.sleep(2)
                        continue

                    # 稳健解析
                    parsed_result = safe_parse_or_default(content, fallback=None)
                    if parsed_result:
                         return parsed_result
                    
                except Exception as e:
                    logger.error(f"解析市场结构分析失败 (Attempt {attempt+1}/{max_app_retries}): {e}")
            
            time.sleep(1)

        logger.error("市场结构分析失败，返回默认值")
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
                {"role": "system", "content": "你是一位专注于价格行为和SMC策略的黄金交易专家。IMPORTANT: You must output strictly valid JSON format only."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 800,
            "stream": False,
            "response_format": {"type": "json_object"}
        }
        
        try:
            # 增加重试机制
            max_app_retries = 3
            for attempt in range(max_app_retries):
                response = self._call_api("chat/completions", payload, symbol=symbol)
                if response and "choices" in response:
                    content = response["choices"][0]["message"]["content"]
                    
                    if not content or len(content.strip()) == 0:
                        logger.warning(f"情绪分析收到空响应 (Attempt {attempt+1}/{max_app_retries})，重试...")
                        time.sleep(2)
                        continue

                    # 稳健解析
                    parsed_result = safe_parse_or_default(content, fallback=None)
                    if parsed_result:
                        return parsed_result
                
                time.sleep(1)
                
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
        
        ## 强制输出格式要求 (Format Enforcement)
        你必须返回一个严格符合 JSON 格式的响应，包含以下顶层字段：
        - "action": "buy" | "sell" | "wait" | "hold" | "close" | "grid_start"
        - "position_size": float (例如 0.15) - **即使是 Hold 也要填一个建议值或 0**
        - "reason": "你的分析逻辑"
        - "confidence": 0-100
        - "exit_conditions": {{"tp_price": float, "sl_price": float}}
        - "market_state": string

        **Action Definitions**:
        - "wait": **CRITICAL**: Use this ONLY when there are NO open positions and you are just observing. (Display: ⏳ 观望中)
        - "hold": **CRITICAL**: Use this ONLY when there are EXISTING open positions that you want to keep open. (Display: 💎 持仓中)
        - "buy"/"sell": Strong signal to enter market.
        - "close": Close existing positions.

        **Action Logic Constraint**:
        - IF `current_positions` is EMPTY: You CANNOT return "hold". You must return "wait" (if no signal) or "buy"/"sell".
        - IF `current_positions` is NOT EMPTY: You CANNOT return "wait". You must return "hold" (to keep) or "close" (to exit) or "buy"/"sell" (to add/reverse).

        ** CRITICAL INSTRUCTION **
        You MUST include the "position_size" field in your JSON response.
        Calculation: (Account Balance * Risk %) / (Stop Loss Distance * Contract Size)
        If uncertain, output 0.01 but DO NOT OMIT the field.


        ## 核心指令更新：动态仓位计算 (Dynamic Position Sizing)
        你必须根据以下因素，精确计算本次交易的 **position_size (Lots)**：
        1. **实时账户资金**: {current_market_data.get('account_info', {}).get('available_balance', 10000)} USD
        2. **交易商特性与风险适配 (Broker Specifics)**:
           - **Exness (高杠杆/低点差)**: 允许更激进的网格加仓和稍大的首单风险 (Risk% 可上浮 20%)。但需注意滑点。
           - **AvaTrade (标准/监管严)**: 严格遵守标准风险模型，禁止过度激进。
           - **合约规格**: 请优先参考 `symbol_details` 中的 `trade_contract_size`。通常 XAUUSD=100, ETHUSD=1, EURUSD=100000。
        3. **风险管理 (AI Driven Risk) - 你的最高优先级**: 
           - **完全授权**: 忽略任何固定的 0.01 手限制。你必须根据你的信心水平和账户资金动态调整仓位。
           - **单笔风险**: **完全由你分析决定，不设固定限制**。
           - **建议范围**: 
             - 低置信度 / 逆势 / 震荡: 建议 0.5% - 1.0% 账户余额风险
             - 中置信度 / 顺势 / 结构良好: 建议 1.0% - 3.0% 账户余额风险
             - 高置信度 (Strong Buy/Sell) / 极佳SMC结构: 可提升至 3.0% - 5.0% 甚至更高（如果你认为机会极佳）。
           - **计算公式**: Position Size (Lots) = (Account Balance * Risk Percentage) / (Stop Loss Distance * Contract Size).
        4. **具体示例**:
           - 资金 $10,000, 风险 2% ($200). 止损距离 $4.
           - Lots = 200 / (4 * 100) = 0.50 Lots.
           - **必须输出结果到 `position_size` 字段 (JSON key)**
        5. **市场情绪**: 结合 {market_analysis.get('sentiment_analysis', {}).get('sentiment', 'neutral')} 情绪调整。
        
        **绝对不要**默认使用 0.01 手！必须基于资金量和你的分析信心计算。如果你认为机会很好，请大胆给出合适的仓位（例如 0.5, 1.0, 2.0 等）。
        请给出一个精确到小数点后两位的数字 (例如 0.15, 0.50, 1.20)，并在 `strategy_rationale` 中详细解释计算逻辑。
        
        ** 重要提示 **: 如果你的 JSON 中缺少 `position_size` 字段，将被视为分析失败！

        ## 强制要求：高质量交易过滤器 (High Quality Filter)
        只有满足以下 **所有** 条件时，才允许返回 `action: buy` 或 `action: sell`，否则请返回 `action: hold`：
        1. **Confidence Score**: 必须 >= 70 (Out of 100). 如果信心不足，请不要强行交易。
        2. **Risk:Reward Ratio**: 必须 >= 1.5. (潜在盈利空间 / 止损风险).
           - 计算公式: Abs(TP - Entry) / Abs(Entry - SL) >= 1.5
           - **Spread Impact**: 请注意点差 (Spread) 成本。你的 SL 和 TP 必须足够宽，以覆盖点差成本。
        
        如果你的分析结果显示信心只有 60 或盈亏比只有 1.2，**请直接返回 HOLD**，并在 `reason` 中说明原因 (例如 "Confidence 60 < 70" 或 "RR 1.2 < 1.5").

        ## 强制要求：明确的最优 SL 和 TP (Optimal Stop Loss & Take Profit)
        无论 Action 是什么 (BUY/SELL/HOLD/WAIT)，你 **必须** 在 `exit_conditions` 中返回明确的、最优的 `sl_price` 和 `tp_price`。
        
        **Directional Logic (Long vs Short)**:
        - **Long (Buy)**: SL < Entry Price < TP. (SL must be BELOW price).
        - **Short (Sell)**: TP < Entry Price < SL. (SL must be ABOVE price).
        - **Validation**: Ensure `abs(Entry - SL)` > `2 * Spread` to cover costs.

        - **TP (止盈)**: 基于下一个流动性池 (Liquidity Pool) 或 MFE 统计。
        - **SL (止损)**: 必须设置在关键结构位之外 (SMC Invalid Point) 或基于 ATR 保护。
        - **严禁** 返回 0.0 或 null！即使是 HOLD/WAIT 状态，也请给出"如果现在进场，合理的SL/TP在哪里"的建议。
        
        **点差适配 (Spread Awareness)**:
        - 不同的交易商 (Exness/Ava) 和品种 (XAUUSD/ETHUSD) 点差差异巨大。
        - 必须在 TP 和 SL 中预留点差缓冲。
        - 当前预估点差 (Points): {current_market_data.get('spread', 20)}
        - 建议缓冲: 至少 2 * Spread。


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
        3. 参考MFE数据优化止盈
        4. 制定Martingale网格加仓计划
        5. 严格遵循风险管理规则
        6. 生成Telegram简报 (Telegram Report):
           - **Content Alignment**: Report MUST match Action.
           - If "wait": Report "⏳ 观望中 (Waiting)" and brief reason.
           - If "hold": Report "💎 持仓中 (Holding)" and PnL/Trend update.
           - If "buy"/"sell": Report "🚀 信号触发 (Signal)" with Entry/SL/TP.
           - **Consistency**: "hold" is ONLY for existing positions!
        """
        
        # 构建payload
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": f"你是一名专注于{symbol}交易的职业交易员，采用SMC(Smart Money Concepts)结合Martingale网格策略的复合交易系统。你完全自主进行市场分析和交易决策。IMPORTANT: You must output strictly valid JSON format only."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 3000,
            "stream": False,
            "response_format": {"type": "json_object"}
        }
        
        # 调用API (带应用层重试机制)
        max_app_retries = 3
        for attempt in range(max_app_retries):
            response = self._call_api("chat/completions", payload, symbol=symbol)
            if response and "choices" in response:
                try:
                    message_content = response["choices"][0]["message"]["content"]
                    
                    # 检查内容是否为空
                    if not message_content or len(message_content.strip()) == 0:
                        logger.warning(f"收到空响应 (Attempt {attempt+1}/{max_app_retries})，尝试重试...")
                        time.sleep(2) # 稍作等待
                        continue

                    # 清洗响应内容 (DeepSeek R1 可能返回 Markdown 代码块)
                    if message_content.startswith("```json"):
                        message_content = message_content[7:]
                    if message_content.endswith("```"):
                        message_content = message_content[:-3]
                    
                    message_content = message_content.strip()
                    
                    logger.info(f"收到模型响应 (Length: {len(message_content)})")
                    
                    # 使用 robust_json_parser 进行稳健解析
                    required_fields = ['action', 'entry_conditions', 'exit_conditions', 'strategy_rationale', 'telegram_report', 'grid_config', 'position_size']
                    defaults = {field: self._get_default_value(field) for field in required_fields}
                    # Ensure position_management default is available for compatibility
                    defaults['position_management'] = self._get_default_value('position_management')
                    defaults['position_size'] = 0.01
                    
                    # 准备 fallback
                    fallback_decision = self._get_default_decision("解析失败或空响应，使用默认参数")
                    
                    # 调用解析
                    trading_decision = safe_parse_or_default(
                        message_content,
                        required_keys=required_fields,
                        defaults=defaults,
                        fallback=fallback_decision
                    )
                    
                    if not isinstance(trading_decision, dict):
                        # 尝试自动修复：如果是列表
                        if isinstance(trading_decision, list):
                            found_dict = False
                            # 1. 遍历列表寻找第一个字典
                            for item in trading_decision:
                                if isinstance(item, dict):
                                    logger.info(f"解析结果为列表，自动提取第一个字典元素")
                                    trading_decision = item
                                    found_dict = True
                                    break
                            
                            # 2. 如果没找到字典，尝试看是否是 JSON 字符串被包裹在列表中 ["{...}"]
                            if not found_dict and len(trading_decision) > 0 and isinstance(trading_decision[0], str):
                                try:
                                    # 尝试解析第一个字符串
                                    potential_dict = safe_parse_or_default(trading_decision[0], fallback=None)
                                    if isinstance(potential_dict, dict):
                                        logger.info("解析结果为包含JSON字符串的列表，成功提取并解析")
                                        trading_decision = potential_dict
                                        found_dict = True
                                except:
                                    pass

                            if found_dict and isinstance(trading_decision, dict):
                                # 补全默认值 (因为 robust_json_parser 对列表不应用 defaults)
                                if defaults:
                                    for key, value in defaults.items():
                                        if key not in trading_decision:
                                            trading_decision[key] = value
                            else:
                                logger.warning(f"解析结果为列表但未找到有效字典 (Len: {len(trading_decision)}, FirstType: {type(trading_decision[0]) if trading_decision else 'Empty'})，使用 fallback。")
                                trading_decision = fallback_decision
                        else:
                            logger.warning(f"解析结果非字典且无法修复 (Type: {type(trading_decision)})，使用 fallback。")
                            trading_decision = fallback_decision
                    
                    # 兼容性适配: 将 grid_config 映射回 position_management
                    if isinstance(trading_decision, dict) and 'grid_config' in trading_decision and isinstance(trading_decision['grid_config'], dict):
                        gc = trading_decision['grid_config']
                        pm = trading_decision.get('position_management', {})
                        if not isinstance(pm, dict): pm = {}
                        
                        # 映射关键字段
                        pm['dynamic_basket_tp'] = gc.get('basket_tp_usd', pm.get('dynamic_basket_tp', 50.0))
                        pm['martingale_multiplier'] = gc.get('martingale_multiplier', pm.get('martingale_multiplier', 1.5))
                        pm['recommended_grid_step_pips'] = gc.get('grid_step_pips', pm.get('recommended_grid_step_pips', 20.0))
                        
                        # 估算 Lock Trigger (70% of Basket TP)
                        if 'basket_tp_usd' in gc:
                            pm['lock_profit_trigger'] = gc['basket_tp_usd'] * 0.7
                            
                        trading_decision['position_management'] = pm

                    # Post-processing: Enforce HOLD/WAIT logic based on positions
                    action_raw = trading_decision.get('action', 'wait').lower()
                    has_positions = len(current_positions) > 0 if current_positions else False
                    
                    if action_raw == 'hold' and not has_positions:
                        trading_decision['action'] = 'wait'
                        if 'telegram_report' in trading_decision:
                            trading_decision['telegram_report'] = trading_decision['telegram_report'].replace("持仓", "观望").replace("Holding", "Waiting")

                    if action_raw == 'wait' and has_positions:
                        trading_decision['action'] = 'hold'
                        if 'telegram_report' in trading_decision:
                            trading_decision['telegram_report'] = trading_decision['telegram_report'].replace("观望", "持仓").replace("Waiting", "Holding")

                    # 再次校验模型返回的 position_size，确保其存在且合法
                    if "position_size" not in trading_decision:
                        logger.warning("⚠️ 模型响应中缺失 'position_size' 字段，使用默认值 0.01")
                        trading_decision["position_size"] = 0.01 # 默认值作为保底
                    else:
                        # 限制范围，防止模型给出极端值
                        try:
                            raw_size = trading_decision["position_size"]
                            size = float(raw_size)
                            
                            # Log dynamic position size only if action implies potential entry
                            # Suppress log for 'hold' or 'wait' or 'close' to avoid noise as per user request
                            action_val = trading_decision.get('action', 'hold').lower()
                            if action_val not in ['hold', 'wait', 'close', 'neutral']:
                                logger.info(f"✅ 模型返回动态仓位: {raw_size} (已根据资金动态计算)")
                            
                            # 0.01 到 10.0 手之间 (根据资金规模调整，放宽上限以适应大资金)
                            trading_decision["position_size"] = max(0.01, min(10.0, size))
                        except (ValueError, TypeError):
                            logger.warning(f"⚠️ 模型返回的 'position_size' 无效 ({trading_decision['position_size']})，重置为 0.01")
                            trading_decision["position_size"] = 0.01

                    # 添加市场分析结果到决策中
                    trading_decision['market_analysis'] = market_analysis
                    
                    return trading_decision
                    
                except json.JSONDecodeError as e:
                    logger.error(f"解析Qwen响应失败: {e}")
                    logger.error(f"原始响应: {response}")
                    # 如果是 JSON 格式错误，也可以选择重试，这里暂不重试
                    return self._get_default_decision("解析失败，使用默认参数")
            
            # 如果 response 为空或结构不对，也重试
            logger.warning(f"API返回无效响应 (Attempt {attempt+1}/{max_app_retries})，尝试重试...")
            time.sleep(2)
        
        return self._get_default_decision("API调用失败（多次重试无效），使用默认参数")
    
    def _get_default_decision(self, reason: str = "系统错误") -> Dict[str, Any]:
        """获取默认决策"""
        return {
            "action": "hold",
            "strategy_mode": "trend",
            "entry_conditions": {"trigger_type": "market"},
            "exit_conditions": {"sl_atr_multiplier": 1.5, "tp_atr_multiplier": 2.5},
            "position_management": {
                "martingale_multiplier": 1.0, 
                "grid_step_logic": "ATR_based",
                "recommended_grid_step_pips": 20,
                "grid_level_tp_pips": [30, 25, 20, 15, 10],
                "dynamic_basket_tp": 50.0
            },
            "grid_config": {
                "initial_lot": 0.01,
                "allow_add": False,
                "grid_step_mode": "atr",
                "grid_step_pips": 20.0,
                "martingale_mode": "multiply",
                "martingale_multiplier": 1.0,
                "max_grid_levels": 0,
                "basket_tp_usd": 50.0,
                "basket_sl_usd": -50.0,
                "max_drawdown_usd": 100.0
            },
            "position_size": 0.01,
            "leverage": 1,
            "signal_strength": 50,
            "parameter_updates": {},
            "strategy_rationale": reason,
            "market_structure_analysis": {"trend": "neutral", "phase": "waiting"},
            "smc_signals_identified": [],
            "risk_metrics": {"max_risk": 0.01, "current_risk": 0},
            "next_observations": ["等待明确信号"],
            "telegram_report": f"⚠️ *System Error (Trend Mode)*\n{reason}",
            "market_analysis": {
                "market_structure": {"trend": "neutral", "phase": "unknown"},
                "sentiment_analysis": {"sentiment": "neutral", "sentiment_score": 0.0}
            }
        }
    
    def _get_default_value(self, field: str) -> Any:
        """获取字段默认值"""
        defaults = {
            'action': 'hold',
            'strategy_mode': 'trend',
            'entry_conditions': {"trigger_type": "market"},
            'exit_conditions': {"sl_atr_multiplier": 1.5, "tp_atr_multiplier": 2.5},
            'position_management': {
                "martingale_multiplier": 1.5, 
                "grid_step_logic": "ATR_based",
                "recommended_grid_step_pips": 20,
                "grid_level_tp_pips": [30, 25, 20, 15, 10],
                "dynamic_basket_tp": 50.0,
                "trailing_stop_config": {"type": "atr_distance", "value": 2.0}
            },
            'grid_config': {
                "initial_lot": 0.01,
                "allow_add": False,
                "grid_step_mode": "atr",
                "grid_step_pips": 20.0,
                "martingale_mode": "multiply",
                "martingale_multiplier": 1.5,
                "max_grid_levels": 5,
                "basket_tp_usd": 50.0,
                "basket_sl_usd": -200.0,
                "max_drawdown_usd": 500.0
            },
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
        
        # 使用当前品种
        symbol = market_data.get("symbol", "DEFAULT")
        response = self._call_api("chat/completions", payload, symbol=symbol)
        
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
        
        # 凯利公式通用，不需要特定 symbol，但为了调用 _call_api 保持一致性，传入 DEFAULT
        response = self._call_api("chat/completions", payload, symbol="DEFAULT")
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
    print("QwenClient module loaded.")

if __name__ == "__main__":
    main()
