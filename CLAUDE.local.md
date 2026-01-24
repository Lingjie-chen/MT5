# CLAUDE.local.md - Local Skills & Instructions

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

2.  **网格配置合理性评估 (Grid Configuration Audit)**:
    *   **网格间距 (Grid Step)**: 当前设置是否适应了当时的 ATR 波动？是否因为间距太小导致在窄幅震荡中过早打满仓位？
    *   **整体止盈 (Basket TP)**: 目标设定是否过高导致无法触及？或者过低导致错失大行情？
    *   **仓位控制 (Position Sizing)**: 首单仓位 (Initial Lot) 是否相对于账户资金过重？加仓倍数是否带来了不可控的风险？
    *   **最大回撤优化 (Max Drawdown Optimization)**: 
        *   *止损位置分析*: 止损 (Basket SL) 是否正好设置在流动性扫荡区 (Liquidity Sweep Zone)？(即：刚打止损就反弹)
        *   *改进策略*: 如果发生了"打损反弹"，说明 Basket SL 设置过于保守。下次应参考历史 MAE (最大不利偏移) 的 90% 分位值，并结合关键支撑位 **下方** 预留更多缓冲空间。

3.  **执行偏差检查 (Execution Gap)**:
    *   对比 **交易计划 (Strategy Rationale)** 与 **实际执行 (Actual Execution)**。
    *   是否存在“知行不一”的情况？(例如：计划说做多，实际却在高位开了空)

4.  **自我提升行动 (Actionable Improvements for Next Trade)**:
    *   **开仓时机优化 (Timing)**: 下次是否应该等待更明确的 SMC 确认信号 (如 Candle Close) 再入场，而不是挂单左侧摸顶底？
    *   **参数动态调整 (Parameter Tuning)**:
        *   *如果本次抗单严重*: 下次需 **扩大** 网格间距 (e.g., 1.5 * ATR -> 2.0 * ATR) 或 **降低** 首单仓位。
        *   *如果本次踏空*: 下次需 **缩小** 间距或使用更灵敏的 Basket TP。
        *   *如果遭遇"打损反弹"*: 下次需 **放宽** Basket SL (例如增加 20% 空间) 或 **减少** 最大加仓层数以降低总风险。
    *   **Action Item**: 生成一条具体的 JSON 配置指令，用于覆盖下一次的默认参数。

**Output Format (输出格式 - 存入 Long-Term Memory):**

```json
{
  "reflection_type": "POST_TRADE_ANALYSIS",
  "trade_id": "{TICKET_ID}",
  "outcome": "WIN" | "LOSS",
  "reasoning": "简述盈亏的核心逻辑 (中文)",
  "grid_audit": {
      "step_rating": "too_tight" | "optimal" | "too_wide",
      "tp_rating": "too_high" | "optimal" | "too_low",
      "entry_timing": "early" | "perfect" | "late",
      "sl_placement": "too_tight" | "optimal" | "too_loose" // 新增止损评估
  },
  "drawdown_analysis": { // 新增回撤分析
      "max_drawdown_reached": -150.0,
      "sl_trigger_point": -200.0,
      "was_liquidity_sweep": true, // 是否为流动性扫荡(打损反弹)
      "optimal_sl_suggestion": -250.0 // 基于事后分析的最优止损建议
  },
  "shortcomings": "本次交易的不足之处",
  "improvements": "下次交易的具体改进措施 (包含参数调整建议)",
  "next_trade_adjustments": {
      "suggested_initial_lot": 0.01,
      "suggested_grid_step_multiplier": 1.2,
      "suggested_basket_tp_adjustment": "+10%",
      "suggested_basket_sl_adjustment": "-20%" // 建议放宽止损
  },
  "self_rating": 8.5
}
```

**Usage Instruction:**
请在每次 `analyze_market` 的 prompt 中包含上述反思的历史记录 (Memory Retrieval)，以确保大模型能够“记住”之前的教训，避免犯同样的错误。
