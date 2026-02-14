# Alpha-Qwen 交易策略与风控规则 (Strategy Rules)

## 核心理念 (Core Philosophy)
**"宁可错过，绝不做错。"**
我们采用 **SMC (Smart Money Concepts)** 结合 **Martingale (顺势马丁)** 的复合策略。
核心目标是捕捉 **H1 级别的趋势**，并利用 **M15 级别的结构** 进行精确打击。

---

## 1. 交易节奏控制 (Trend Cycle Control)

*   **ORB 策略底层运行优化 (ORB Execution)**:
    *   **24/7 监控**: 建立全天候市场监控机制，不间断扫描价格行为。
    *   **实时信号检测**: 价格一旦突破 ORB 定义的区间 (Opening Range)，系统必须立即触发信号处理流程。
    *   **毫秒级响应**: 确保从信号触发到执行的延迟控制在毫秒级别。

*   **拒绝频繁交易**: 不需要每根 K 线都交易。质量 > 数量。
*   **趋势跟随模式 (Trend Following)**:
    *   以 **H1** 为主趋势方向 (Macro Trend)。
    *   以 **M15** 为入场执行周期 (Execution)。
    *   **严禁逆势交易**：除非出现明确的大级别反转信号 (H1 CHoCH)。
*   **拒绝追涨杀跌 (Anti-FOMO)**:
    *   **No Buying at Tops**: 价格处于近期高位 (Premium Zone) 时，必须等待回调 (Pullback) 至合理区域 (Discount Zone) 或关键支撑位 (Order Block/FVG)。
    *   **No Selling at Bottoms**: 价格处于近期低位 (Discount Zone) 时，必须等待反弹。
*   **Trend Surfing (趋势冲浪)**:
    *   如果识别到强劲的单边趋势（如价格持续在 MA 上方或突破关键阻力），不要等待深度回调，但仍需等待微小级别的结构确认 (Micro-Structure Confirmation)。

---

## 2. 大模型集成分析系统 (LLM Integration)

*   **智能止损模块 (Smart SL)**:
    *   当 ORB 信号触发时，调用大模型实时分析市场微观结构、波动率 (ATR) 和订单流。
    *   **输出**: 动态计算出的最优止损位 (基于结构而非固定点数)。
*   **篮子止盈管理 (Basket TP)**:
    *   大模型综合分析多币种相关性、波动率矩阵和风险敞口。
    *   **输出**: 为整个交易篮子设定分层止盈目标 (Layered TP Targets)。
*   **SMC 数据验证 (SMC Validation)**:
    *   **数据接口**: 实时集成机构订单区块 (OB)、公允价值缺口 (FVG)、流动性池 (Liquidity Pools)。
    *   **质量评分**: 将 SMC 数据与 ORB 信号交叉验证 (流动性匹配度、订单流一致性)。
    *   **阈值过滤**: 仅当 SMC 验证分数 **≥70%** 时，才允许执行 ORB 交易。

---

## 3. 入场执行标准 (Entry Execution)

**必须满足以下所有条件才能开仓 (AND Logic):**

1.  **多周期趋势共振 (Trend Alignment)**:
    *   M5、M15、H1 趋势方向必须一致。
    *   如果趋势不一致 (Mixed)，**坚决观望 (WAIT)**。

2.  **SMC 结构验证 (Structure Validation)**:
    *   **关键位**: 价格必须到达关键的 Order Block (OB) 或 Fair Value Gap (FVG)。
    *   **有效反应**: 必须观察到价格在该区域的**拒绝/反转信号** (如 Pinbar, Engulfing)。
    *   **结构破坏 (BOS)**: 顺势突破结构，确认趋势延续。

3.  **价格行为确认 (Price Action)**:
    *   **回踩确认 (Retest)**: 突破关键位后，等待回踩不破。
    *   **K线收盘**: 必须等待 M15 K 线收盘确认。

---

## 4. 仓位管理 (Position Sizing) - Powered by Quantum Engine

*   **Quantum Position Engine 集成**:
    *   所有仓位计算必须通过 **Quantum Position Engine** 进行，确保 `Decimal` 级精度。
    *   **AI 角色**: AI 仅负责评估风险等级 (Risk Tier)，不直接计算手数。
*   **风险偏好 (Risk Tiers)**:
    *   **Tier 1 (保守)**: Risk 0.5% - 0.8% (逆势/震荡)
    *   **Tier 2 (标准)**: Risk 1.0% - 1.5% (顺势/ORB突破)
    *   **Tier 3 (激进)**: Risk 2.0% - 3.0% (A+ Setup/SMC高分)
*   **计算公式**: `Position Size (Lots) = (Account Balance * Risk %) / (Stop Loss Distance * Contract Size)`

---

## 5. 止损与止盈 (SL & TP)

*   **Stop Loss (SL)**:
    *   必须基于 **SMC 结构失效位**。
    *   多单: 最近的 Swing Low 或 OB 下边界。
    *   空单: 最近的 Swing High 或 OB 上边界。
*   **Take Profit (TP)**:
    *   指向下一个 **流动性池 (Liquidity Pool)** 或未回补的 **FVG**。
    *   **盈亏比 (R:R)**: 必须至少 **1:1.5**。

---

## 6. Grid 策略智能切换系统 (Smart Grid Switching)

*   **市场状态识别**:
    *   当 ORB 无信号时，大模型分析价格行为、波动率收缩、成交量分布。
    *   **特征**: 识别震荡行情 (Consolidation)。
*   **斐波那契网格 (Fibonacci Grid)**:
    *   基于当前震荡区间，自动部署限价单 (Limit Orders)。
    *   **比例**: 0.236, 0.382, 0.5, 0.618, 0.786。
*   **切换风控**:
    *   **冷却期**: 策略切换必须有冷却时间，防止频繁震荡。
    *   **最大滑点**: 严格控制滑点。
    *   **无缝切换**: 确保 ORB 与 Grid 切换延迟 **<100ms**。
    *   **统一风控**: 两种策略共享止损和仓位限制。

---

## 7. 马丁格尔与网格 (Martingale & Grid)

*   **顺势加仓 (Pyramiding)**:
    *   仅当当前持仓 **盈利** 且趋势强劲时，允许顺势加仓。
    *   加仓必须基于新的 SMC 信号。
*   **逆势网格 (Defensive Grid)**:
    *   仅在明确的 **震荡行情** 或 **左侧挂单** 时启用。
    *   必须设定严格的 `max_drawdown_usd` (最大回撤金额)。
*   **Basket TP (整体止盈)**:
    *   必须根据 **总持仓量** 动态调整。
    *   仓位越重，TP 目标金额应越大 (Risk/Reward 匹配)。

---

## 8. 盘前 8 问 (Pre-Market 8 Questions)

每次决策前必须回答：
1.  **Q1 趋势**: 多头/空头/震荡?
2.  **Q2 起点**: 趋势发起的关键点?
3.  **Q3 阶段**: 积累/扩张/分配?
4.  **Q4 级别**: 当前处于第几浪?
5.  **Q5 偏见**: 做多/做空/观望?
6.  **Q6 周期**: 顺势还是逆势?
7.  **Q7 防守**: 明确的失效位?
8.  **Q8 执行**: 条件是否完全满足? (Yes/No)

**如果 Q8 为 No，Action 必须为 WAIT/HOLD。**

---

## 9. 系统日志与监控 (System Logs)

*   **全链路记录**: 必须记录每次策略切换的依据、大模型分析结果 (JSON) 和执行质量。
*   **故障排查**: 任何策略切换失败或风控拦截都必须生成 ERROR 级日志。
