---
name: csv-data-summarizer
description: "交易日志 CSV 数据分析工具。自动分析交易记录 CSV 文件，计算胜率、盈亏比、最大回撤、Sharpe Ratio 等量化指标并生成可视化报告。当需要分析交易绩效、优化策略参数或生成交易报告时使用此 Skill。"
---

# 交易日志 CSV 数据分析师

自动分析交易记录 CSV，生成量化绩效指标。

## 适用场景

- 分析 MT5 导出的交易历史 CSV
- 计算策略核心绩效指标
- 对比不同时期/品种的交易表现
- 识别交易模式和改进方向
- 生成给团队/投资者的绩效报告

## 核心指标计算

### 基础指标

| 指标 | 公式 | 说明 |
|------|------|------|
| 胜率 (Win Rate) | `wins / total_trades × 100%` | 盈利交易占比 |
| 盈亏比 (Profit Factor) | `gross_profit / gross_loss` | 总盈利/总亏损 |
| 平均盈亏比 (Avg R:R) | `avg_win / avg_loss` | 平均利润/平均亏损 |
| 期望值 (Expectancy) | `win_rate × avg_win - loss_rate × avg_loss` | 每笔预期收益 |

### 风控指标

| 指标 | 公式 | 说明 |
|------|------|------|
| 最大回撤 (Max DD) | `(peak - trough) / peak × 100%` | 最大资金峰谷跌幅 |
| 最大回撤持续期 | 连续回撤的自然日数 | 恢复所需时间 |
| 最大连续亏损 | 连续亏损笔数 | 心理压力指标 |
| 最大单笔亏损 | 亏损最多的单笔交易 | 极端风险 |

### 高级指标

| 指标 | 公式 | 说明 |
|------|------|------|
| Sharpe Ratio | `(R_p - R_f) / σ_p` | 风险调整后收益 |
| Sortino Ratio | `(R_p - R_f) / σ_down` | 仅考虑下行风险 |
| Calmar Ratio | `annualized_return / max_dd` | 收益/回撤比 |
| Recovery Factor | `net_profit / max_dd` | 恢复能力 |

## CSV 数据格式

### MT5 标准导出格式
```csv
Ticket,Open Time,Type,Volume,Symbol,Open Price,SL,TP,Close Time,Close Price,Commission,Swap,Profit
12345,2025.01.01 10:00,buy,0.10,XAUUSD,2630.50,2625.00,2645.00,2025.01.01 14:30,2641.20,0.00,-0.50,107.00
```

### 自定义交易日志格式
```csv
timestamp,symbol,direction,entry,exit,sl,tp,volume,pnl,strategy,risk_tier
2025-01-01T10:00:00,XAUUSD,LONG,2630.50,2641.20,2625.00,2645.00,0.10,107.00,ORB,Tier2
```

## 分析维度

### 按品种分析
```
对每个交易品种分别计算:
- 胜率和盈亏比
- 最佳/最差交易
- 平均持仓时间
- 品种收益贡献度
```

### 按策略分析
```
对每种策略分别计算:
- ORB vs Grid 策略对比
- 各 Risk Tier 的实际表现
- 顺势 vs 逆势交易效果
```

### 按时间分析
```
按日/周/月聚合:
- 交易频率趋势
- 收益波动分析
- 关键经济事件前后表现
- 不同交易时段的胜率
```

## 输出报告模板

```markdown
# 交易绩效报告 - 2025年1月

## 概览
- 总交易笔数: 150
- 净利润: $12,350
- 胜率: 62.7%
- 盈亏比: 1.82

## 核心指标
| 指标 | 值 | 评级 |
|------|-----|-----|
| 最大回撤 | 8.3% | ✅ 良好 (< 20%) |
| Sharpe Ratio | 1.85 | ✅ 优秀 (> 1.5) |
| Profit Factor | 2.14 | ✅ 健康 (> 1.5) |
| Recovery Factor | 3.2 | ✅ 强劲 |

## 品种表现
(按收益排名的各品种绩效表)

## 改进建议
(基于数据分析的具体改进建议)
```

## 引用

- 原始来源: [coffeefuelbump/csv-data-summarizer-claude-skill](https://github.com/coffeefuelbump/csv-data-summarizer-claude-skill)
