# Alpha-Qwen 交易策略与风控规则 (Strategy Rules)

## 核心理念 (Core Philosophy)
**"宁可错过，绝不做错。"**
我们采用 **SMC (Smart Money Concepts)** 结合 **Martingale (顺势马丁)** 的复合策略。
核心目标是捕捉 **H1 级别的趋势**，并利用 **M15 级别的结构** 进行精确打击。

---

## 1. 交易节奏控制 (Trend Cycle Control)

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

## 2. 入场执行标准 (Entry Execution)

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

## 3. 仓位管理 (Position Sizing)

*   **完全动态计算**:
    *   **禁止**使用固定手数 (如 0.01)。
    *   **计算公式**: `Position Size (Lots) = (Account Balance * Risk %) / (Stop Loss Distance * Contract Size)`
*   **风险偏好**:
    *   **低置信度 / 逆势**: Risk 0.5% - 1.0%
    *   **中置信度 / 顺势**: Risk 1.0% - 3.0%
    *   **高置信度 (Sniper Entry)**: Risk 3.0% - 5.0%

---

## 4. 止损与止盈 (SL & TP)

*   **Stop Loss (SL)**:
    *   必须基于 **SMC 结构失效位**。
    *   多单: 最近的 Swing Low 或 OB 下边界。
    *   空单: 最近的 Swing High 或 OB 上边界。
*   **Take Profit (TP)**:
    *   指向下一个 **流动性池 (Liquidity Pool)** 或未回补的 **FVG**。
    *   **盈亏比 (R:R)**: 必须至少 **1:1.5**。

---

## 5. 马丁格尔与网格 (Martingale & Grid)

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

## 6. 盘前 8 问 (Pre-Market 8 Questions)

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
