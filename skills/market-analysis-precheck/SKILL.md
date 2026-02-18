---
name: market-analysis-precheck
description: "盘前 8 问和市场分析检查清单。每次交易决策前执行标准化的 8 问质询，确保趋势、结构、偏见和执行条件完整验证。当需要评估是否入场、分析当前市场状态或执行盘前检查时使用此 Skill。"
---

# 盘前 8 问 & 市场分析检查清单

**铁律**: 如果任何关键条件不满足，Action 必须为 **WAIT/HOLD**。

## 适用场景

- 每个交易日开盘前的市场分析
- 每次入场决策前的最终检查
- 策略切换前的市场状态评估
- 交易复盘时的决策质量审计

## 盘前 8 问 (Pre-Market 8 Questions)

每次决策前，**必须逐一回答以下 8 个问题**：

### Q1 趋势方向
> 当前市场是 **多头 (Bullish)** / **空头 (Bearish)** / **震荡 (Ranging)**？

**检查方法**:
- H1 级别 MA 方向和斜率
- 近期高低点是否递升/递降
- 关键支撑阻力位的突破情况

### Q2 趋势起点
> 本轮趋势的**关键发起点**在哪里？

**检查方法**:
- 找到最近的 BOS (Break of Structure)
- 标记趋势发起的 Order Block
- 确认推动浪的起点

### Q3 当前阶段
> 市场处于 **积累 (Accumulation)** / **扩张 (Expansion)** / **分配 (Distribution)** 阶段？

**参考标准**:
| 阶段 | 特征 |
|------|------|
| 积累 | 窄幅震荡、成交量萎缩、流动性积聚 |
| 扩张 | 突破区间、放量、结构快速推进 |
| 分配 | 高位放量、频繁假突破、巨量换手 |

### Q4 波浪级别
> 当前处于**第几浪**？(Elliott Wave 参考)

**判断要点**:
- 推动浪 (1, 3, 5) vs 调整浪 (2, 4)
- 第 3 浪通常最强，第 5 浪可能背离
- 小心第 4 浪的复杂调整

### Q5 交易偏见
> 你的偏见是 **做多 (Long)** / **做空 (Short)** / **观望 (Wait)**？

**决策依据**:
- Q1-Q4 的综合分析
- 只在趋势方向上建仓
- 震荡行情选择观望或 Grid 策略

### Q6 周期一致性
> 你的交易方向是 **顺势 (Trend-Following)** 还是 **逆势 (Counter-Trend)**？

**硬性规则**:
- ✅ 顺势交易: M5 + M15 + H1 同向 → 允许
- ⚠️ 混合趋势: 部分周期不一致 → WAIT
- ❌ 逆势交易: 除 H1 CHoCH 反转信号外 → 禁止

### Q7 防守位置
> 明确的**失效位 (Invalidation Level)** 在哪里？

**设定方法**:
- 多单: 最近 Swing Low 或 OB 下边界
- 空单: 最近 Swing High 或 OB 上边界
- 失效位 = 止损位，必须基于结构

### Q8 执行条件
> **所有条件是否完全满足？(Yes/No)**

**最终检查**:
- [ ] 趋势共振 ✓
- [ ] SMC 结构到位 ✓
- [ ] 价格行为确认 ✓
- [ ] 盈亏比 ≥ 1:1.5 ✓
- [ ] Risk Tier 已确定 ✓
- [ ] 回撤在安全范围 ✓

> **⚠️ 如果 Q8 为 No，Action 必须为 WAIT/HOLD。绝不妥协。**

## 输出模板

```json
{
  "timestamp": "2025-01-01T09:00:00",
  "symbol": "XAUUSD",
  "analysis": {
    "Q1_trend": "Bullish",
    "Q2_origin": "H1 OB at 2620.00",
    "Q3_phase": "Expansion",
    "Q4_wave": "Wave 3",
    "Q5_bias": "Long",
    "Q6_alignment": "Trend-Following (M5/M15/H1 aligned)",
    "Q7_invalidation": "2615.50 (Swing Low)",
    "Q8_ready": true
  },
  "action": "EXECUTE LONG",
  "risk_tier": "Tier 2 (1.5%)",
  "entry": 2635.00,
  "sl": 2615.50,
  "tp": 2665.00,
  "rr_ratio": "1:1.54"
}
```
