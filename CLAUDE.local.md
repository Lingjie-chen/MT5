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

## Skill: Qlib Source Code Study (Qlib 源码研习)

**Description:**
此技能要求 Agent 在每个 Session 启动时，主动研究 Qlib 源码，学习如何使用 Qlib 原生工具（如数据加载器、回测引擎、因子分析等）来实现量化任务，从而提升代码的专业性和效率。

**Trigger:**
Session Start (每当开启一个新的对话会话时).

**Action Items:**
1.  **Locate Qlib**: 尝试查找环境中是否安装了 Qlib (`import qlib`) 或存在源码目录。
2.  **Study Core Modules**:
    *   `qlib.data`: 学习数据加载与处理 (Data Handler).
    *   `qlib.strategy`: 学习策略基类与实现.
    *   `qlib.backtest`: 学习回测引擎与执行器.
    *   `qlib.workflow`: 学习完整的量化工作流.
3.  **Apply Knowledge**: 在编写量化代码时，优先使用 Qlib 提供的原生接口，避免重复造轮子。
4.  **Self-Correction**: 如果发现自己编写的代码可以用 Qlib 工具替代，请进行重构。
