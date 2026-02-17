---
name: deep-research
description: "量化交易市场深度研究工具。支持宏观经济分析、技术面研究、资产相关性分析和市场微观结构研究。当需要进行深度市场调研、分析经济数据影响或研究新交易品种时使用此 Skill。"
---

# 量化交易市场深度研究

系统化的市场研究框架，为交易决策提供深度支撑。

## 适用场景

- 分析宏观经济事件对交易品种的影响
- 研究新品种的交易特性和相关性
- 深入分析技术面结构和流动性分布
- 竞品策略研究和市场微观结构分析
- 回测数据的深度挖掘

## 研究框架

### 1. 宏观经济研究

| 研究维度 | 关注要素 |
|---------|---------|
| 央行政策 | 利率决议、QE/QT、前瞻指引 |
| 经济数据 | GDP、CPI、非农、PMI |
| 地缘政治 | 贸易战、地区冲突、制裁 |
| 市场情绪 | VIX、恐慌贪婪指数、资金流向 |

**研究模板**:
```
1. 本周关键经济数据日历
2. 各央行近期政策倾向
3. 影响当前持仓品种的核心因素
4. 潜在的 Black Swan 风险评估
```

### 2. 技术面深度研究

| 分析层级 | 工具/方法 |
|---------|----------|
| 多周期分析 | H1 趋势 + M15 结构 + M5 入场 |
| SMC 结构 | OB, FVG, BOS, CHoCH, Liquidity Pools |
| 波动率 | ATR, Bollinger Bands, IV/HV |
| 订单流 | 机构持仓 (COT), 暗池数据 |
| 量价关系 | 成交量分布 (VP), VWAP |

### 3. 资产相关性分析

```
研究步骤:
1. 计算品种间 Pearson 相关系数矩阵
2. 识别强正相关 (r > 0.7) 和强负相关 (r < -0.7) 对
3. 分析相关性的时间稳定性 (滚动窗口)
4. 评估 Basket 持仓的集中度风险
5. 寻找对冲和分散化机会
```

**常见相关性**:
| 品种对 | 典型相关性 | 注意事项 |
|--------|-----------|---------|
| XAUUSD vs DXY | 强负相关 | USD 走强压制金价 |
| XAUUSD vs USDJPY | 中负相关 | 避险情绪影响 |
| 股指 vs VIX | 强负相关 | 恐慌卖出 |
| 原油 vs CAD | 正相关 | 加拿大石油出口 |

### 4. 市场微观结构研究

- **流动性分布**: 识别 Stop Hunting 区域和 Liquidity Grab 位置
- **订单簿分析**: 大单分布和 Iceberg Order 检测
- **做市商行为**: 识别 Manipulation Phase 和 Distribution Phase
- **价差分析**: 不同时段的 Spread 变化和流动性窗口

## 研究输出格式

```json
{
  "research_type": "weekly_macro",
  "timestamp": "2025-01-13",
  "symbol": "XAUUSD",
  "findings": {
    "macro_outlook": "...",
    "technical_structure": "...",
    "correlations": {...},
    "risk_events": [...],
    "trading_implications": "..."
  },
  "confidence": "HIGH/MEDIUM/LOW",
  "action_recommendation": "..."
}
```

## 数据源参考

| 数据源 | 用途 |
|--------|------|
| Yahoo Finance | 价格数据、基本面 |
| TradingView | 技术分析图表 |
| Investing.com | 经济日历、实时数据 |
| CFTC COT Report | 机构持仓 |
| Bloomberg/Reuters | 宏观新闻 |

## 引用

- 原始来源: [sanjay3290/ai-skills/deep-research](https://github.com/sanjay3290/ai-skills/tree/main/skills/deep-research)
