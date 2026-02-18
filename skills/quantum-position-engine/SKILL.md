---
name: quantum-position-engine
description: "Quantum Position Engine 仓位计算引擎指南。覆盖 Decimal 精度计算、跨币种汇率换算、保证金杠杆检查、回撤熔断等核心风控逻辑。当需要计算仓位、检查风控参数、调试仓位引擎时使用此 Skill。"
---

# Quantum Position Engine

高精度、生产级的仓位计算引擎，专为量化交易设计。全程使用 `Decimal` 运算杜绝浮点误差。

## 适用场景

- 计算新交易信号的最优仓位大小
- 检查保证金和杠杆约束
- 调试仓位计算异常
- 添加新资产类型支持
- 修改风控参数和阈值

## 核心架构

```
src/position_engine/
├── models.py      # TradeSignal 输入模型 + CalculationResult 输出模型
├── calculator.py  # PositionCalculator 核心计算逻辑
├── services.py    # ExchangeRateService 汇率服务 (Yahoo Finance)
└── config.py      # 缓存 TTL 等配置
```

## 计算流程

```
1. 熔断检查 → current_drawdown >= max_allowed_drawdown → BLOCKED
2. 获取汇率 → manual_exchange_rate 或 Yahoo Finance 实时查询
3. 计算风险额 → total_capital × risk_per_trade_percent / 100
4. 计算单手风险 → |entry - SL| × contract_size × exchange_rate
5. 理论仓位 → risk_amt / risk_per_unit
6. 保证金检查 → required_margin > total_capital → 降级仓位
7. 规格取整 → 按 asset_type 取整 (ROUND_FLOOR)
```

## TradeSignal 输入参数

| 字段 | 类型 | 说明 |
|------|------|------|
| `total_capital` | Decimal | 账户总资金 (>0) |
| `account_currency` | str | 账户本位币 (如 "USD") |
| `quote_currency` | str | 标的报价币 (如 "JPY") |
| `risk_per_trade_percent` | Decimal | 单笔风险比例 (0-100) |
| `entry_price` | Decimal | 入场价格 |
| `stop_loss_price` | Decimal | 止损价格 (不能等于入场价) |
| `asset_type` | AssetType | STOCK / FUTURE / FOREX / CRYPTO |
| `contract_size` | Decimal | 合约乘数 (默认 1.0) |
| `leverage` | Decimal | 杠杆倍数 (默认 1.0) |
| `current_drawdown_percent` | Decimal | 当前回撤百分比 |
| `max_allowed_drawdown_percent` | Decimal | 最大允许回撤 (默认 20%) |
| `manual_exchange_rate` | Decimal? | 手动指定汇率 (可选) |

## 风险等级 (Risk Tiers)

| Tier | Risk % | 适用场景 |
|------|--------|---------|
| Tier 1 (保守) | 0.5%-0.8% | 逆势/震荡行情 |
| Tier 2 (标准) | 1.0%-1.5% | 顺势/ORB 突破 |
| Tier 3 (激进) | 2.0%-3.0% | A+ Setup / SMC 高分 |

## 取整精度

| 资产类型 | 精度 | 示例 |
|---------|------|------|
| STOCK / FUTURE | 1 (整数) | 15 手 |
| FOREX | 0.01 | 1.25 手 |
| CRYPTO | 0.0001 | 0.5123 BTC |

## 关键规则

> **AI 角色**: AI 仅负责评估 Risk Tier，不直接计算手数。所有仓位计算必须通过 PositionCalculator。

- 所有金额和价格必须使用 `Decimal` 类型，禁止 `float`
- 汇率缓存 TTL 由 `config.py` 中 `CACHE_TTL` 控制
- 保证金不足时自动降仓，不会拒绝交易
- 回撤超限时直接熔断，返回零仓位

## 使用示例

```python
from src.position_engine.calculator import PositionCalculator
from src.position_engine.models import TradeSignal, AssetType
from decimal import Decimal

calc = PositionCalculator()
signal = TradeSignal(
    total_capital=Decimal("10000"),
    risk_per_trade_percent=Decimal("1.5"),  # Tier 2
    entry_price=Decimal("1850.50"),
    stop_loss_price=Decimal("1845.00"),
    asset_type=AssetType.FUTURE,
    contract_size=Decimal("100"),
    leverage=Decimal("20"),
    account_currency="USD",
    quote_currency="USD",
)
result = calc.calculate(signal)
print(f"仓位: {result.suggested_position_size} 手")
print(f"风险额: ${result.risk_amount_account}")
```
