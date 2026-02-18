---
name: trading-risk-management
description: "交易风控决策框架。覆盖最大回撤熔断、保证金自动降仓、Basket TP 管理、马丁格尔加仓规则、Grid 策略风控。当需要评估交易风险、设定风控参数、分析回撤或优化止损止盈时使用此 Skill。"
---

# 交易风控决策框架

全方位的风控体系，保护资金安全并最大化收益。

## 适用场景

- 评估当前持仓的风险敞口
- 设定或调整最大回撤阈值
- 分析保证金使用率和杠杆风险
- 管理多品种篮子止盈
- 优化马丁格尔加仓策略
- 排查风控拦截和熔断事件

## 风控层次体系

```
Layer 1: 单笔风控  →  Risk Tier 控制单笔风险比例
Layer 2: 仓位风控  →  Quantum Engine 保证金检查 + 降仓
Layer 3: 组合风控  →  Basket TP + 多币种相关性
Layer 4: 系统风控  →  最大回撤熔断 + 冷却期
```

## 1. 最大回撤熔断

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `max_allowed_drawdown_percent` | 20% | 回撤超过此值所有新单被熔断 |
| 触发行为 | 返回零仓位 | `CalculationResult.risk_level = "BLOCKED"` |
| 恢复条件 | 人工确认 | 需手动解除熔断状态 |

**规则**: 当 `current_drawdown_percent >= max_allowed_drawdown_percent` 时，PositionCalculator 立即返回零仓位。

## 2. 保证金不足自动降仓

当 `required_margin > total_capital` 时：
- **不拒绝交易**，而是自动降低仓位至保证金可承受范围
- 降级公式: `position = (capital × leverage) / (entry_price × contract_size × exchange_rate)`
- 标记 `risk_level = "HIGH (Margin Constraint)"`

## 3. Basket TP 管理

| 规则 | 说明 |
|------|------|
| 分层止盈 | LLM 分析多币种相关性设定 Layered TP Targets |
| 动态调整 | 仓位越重，TP 目标金额越大 (Risk/Reward 匹配) |
| 整体止盈 | 根据总持仓量动态调整，非单品种独立止盈 |

## 4. 马丁格尔加仓风控

### 顺势加仓 (Pyramiding)
- ✅ 当前持仓**盈利**且趋势强劲
- ✅ 加仓基于新的 SMC 信号
- ❌ 亏损时禁止加仓

### 逆势网格 (Defensive Grid)
- ✅ 仅在明确**震荡行情**或**左侧挂单**时启用
- ✅ 必须设定 `max_drawdown_usd` 上限
- ❌ 趋势行情中禁止逆势网格

## 5. Grid 策略切换风控

| 参数 | 要求 |
|------|------|
| 冷却期 | 策略切换后强制等待，防频繁振荡 |
| 最大滑点 | 严格控制，超限取消切换 |
| 切换延迟 | ORB ↔ Grid 切换 < 100ms |
| 统一风控 | 两种策略共享止损和仓位限制 |

## 6. 止损规则

| 方向 | SL 位置 | 依据 |
|------|---------|------|
| 多单 | 最近 Swing Low / OB 下边界 | SMC 结构失效位 |
| 空单 | 最近 Swing High / OB 上边界 | SMC 结构失效位 |

> **禁止**: 使用固定点数止损。SL 必须基于市场结构。

## 7. 系统监控要求

- **全链路记录**: 策略切换依据 + LLM 分析结果 (JSON) + 执行质量
- **ERROR 日志**: 策略切换失败或风控拦截必须生成
- **审计追踪**: 每次风控动作都留有完整记录

## 风控检查清单

执行任何交易前，必须确认：
- [ ] 回撤是否接近熔断线？
- [ ] 保证金使用率是否健康？
- [ ] 盈亏比是否 ≥ 1:1.5？
- [ ] Risk Tier 是否匹配当前行情？
- [ ] Basket 整体风险敞口是否可控？
