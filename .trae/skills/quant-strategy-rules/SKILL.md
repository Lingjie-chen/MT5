---
name: quant-strategy-rules
description: "Alpha-Qwen 量化交易策略规则引擎。应用 SMC (Smart Money Concepts) + 顺势马丁格尔复合策略，覆盖多周期趋势共振、结构验证、入场执行、Grid 切换等核心逻辑。当需要分析行情、判断入场/出场、讨论策略优化时使用此 Skill。"
---

# Alpha-Qwen 量化交易策略规则

**核心理念**: "宁可错过，绝不做错。"  
**策略框架**: SMC (Smart Money Concepts) + Martingale (顺势马丁)  
**目标**: 捕捉 H1 级别趋势，利用 M15 级别结构精确打击

## 适用场景

- 分析当前行情是否满足入场条件
- 评估交易信号的结构有效性
- 讨论策略参数优化和回测
- 判断 ORB 信号和 Grid 策略切换
- 执行 SMC 数据验证 (≥70% 阈值)

## 交易节奏控制

| 规则 | 要求 |
|------|------|
| ORB 执行 | 24/7 监控，毫秒级响应突破 Opening Range |
| 趋势跟随 | H1 = 主趋势方向，M15 = 入场执行周期 |
| 逆势禁令 | 除 H1 CHoCH 反转信号外，严禁逆势交易 |
| Anti-FOMO | Premium Zone 不追多，Discount Zone 不追空 |
| Trend Surfing | 强势单边可免深度回调，但需微观结构确认 |

## 入场执行标准 (AND Logic)

**必须同时满足以下全部条件：**

1. **多周期趋势共振**: M5 + M15 + H1 方向一致，否则 WAIT
2. **SMC 结构验证**: 
   - 价格到达关键 Order Block (OB) 或 Fair Value Gap (FVG)
   - 观察到拒绝/反转信号 (Pinbar, Engulfing)
   - 顺势 BOS (Break of Structure) 确认趋势延续
3. **价格行为确认**:
   - 突破关键位后回踩不破 (Retest)
   - 等待 M15 K 线收盘确认

## 止损与止盈

- **SL**: 基于 SMC 结构失效位，多单=Swing Low/OB 下边界，空单=Swing High/OB 上边界
- **TP**: 指向下一个流动性池或未回补的 FVG，最低盈亏比 **1:1.5**

## LLM 集成分析

| 模块 | 功能 |
|------|------|
| 智能止损 | 实时分析微观结构 + ATR + 订单流，输出动态最优 SL |
| 篮子止盈 | 分析多币种相关性 + 波动率矩阵，设定分层 TP |
| SMC 验证 | 交叉验证 OB/FVG/流动性池，验证分数 ≥70% 才执行 |

## Grid 策略切换

- **触发条件**: ORB 无信号 + 波动率收缩 + 成交量萎缩 → 识别震荡行情
- **网格部署**: 斐波那契比例 0.236, 0.382, 0.5, 0.618, 0.786
- **切换风控**: 冷却期 + 滑点控制 + 延迟 <100ms + 统一风控

## 马丁格尔规则

- **顺势加仓**: 仅当持仓盈利且趋势强劲时，基于新 SMC 信号加仓
- **逆势网格**: 仅限震荡行情或左侧挂单，必须设定 `max_drawdown_usd`
- **Basket TP**: 根据总持仓量动态调整，仓位越重 TP 越大

## 引用

- 详细策略文档: `src/docs/strategy_rules.md`
- 仓位计算引擎: `src/position_engine/`
- 交易机器人: `src/trading_bot/`
