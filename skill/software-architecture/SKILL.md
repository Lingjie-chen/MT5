---
name: software-architecture
description: "金融量化系统软件架构规范。基于 Clean Architecture 和 DDD 原则，增加量化交易特有架构规则：Decimal 精度、跨币种处理、事件驱动策略切换、风控隔离。当设计新模块、重构代码、审查架构时使用此 Skill。"
---

# 金融量化系统架构规范

基于 Clean Architecture 和领域驱动设计 (DDD)，适配量化交易系统的架构指南。

## 适用场景

- 设计新的策略模块或风控组件
- 重构现有代码架构
- 进行代码评审和架构审查
- 评估技术方案的合理性
- 新增资产类型或交易通道

## 通用架构原则

### Early Return & 简洁性
- 使用早返回 (early return) 替代深层嵌套
- 函数不超过 50 行，文件不超过 200 行
- 复杂逻辑拆分为可复用的小函数

### Library-First
- 优先使用成熟库而非自造轮子
- 但金融精度计算 (`Decimal`) 和核心风控 **必须自主实现**
- 可用第三方: `yfinance` (行情), `psycopg2` (DB), `pydantic` (模型), `cachetools` (缓存)

### 关注点分离
- 业务逻辑与 UI/API 分离
- 数据库查询不混入控制器
- 策略逻辑与风控逻辑独立

## 量化系统专属规则

### 1. Decimal 精度 (最高优先级)

> **铁律**: 所有金额、价格和仓位计算 **必须** 使用 `Decimal` 类型，**禁止** `float`。

```python
# ✅ 正确
from decimal import Decimal
risk_amt = Decimal("10000") * (Decimal("1.5") / Decimal("100"))

# ❌ 错误
risk_amt = 10000 * (1.5 / 100)  # 浮点误差！
```

### 2. 跨币种处理

| 场景 | 处理方式 |
|------|---------|
| 账户币 = 标的报价币 | exchange_rate = 1.0 |
| 账户 USD，标的 JPY | 自动查询 JPY→USD 汇率 |
| Crypto 对法币 | 优先 Yahoo Finance，fallback BTC-USD 格式 |

- 汇率必须有**缓存** (TTL 可配)
- 汇率获取失败必须返回明确错误，不使用默认值

### 3. 事件驱动策略切换

```
ORB 策略 ←→ Grid 策略

切换条件: 
  ORB 无信号 + 波动率收缩 + 成交量萎缩
  → 切换到 Grid

切换约束:
  - 冷却期 (防频繁切换)
  - 延迟 < 100ms
  - 统一风控 (共享止损/仓位限制)
```

### 4. 风控隔离

```
Layer 1: PositionCalculator  (单笔仓位计算)
         ↓
Layer 2: RiskManager         (组合风控)
         ↓  
Layer 3: CircuitBreaker      (熔断机制)
```

- 每层独立，高层不绕过低层
- 熔断不依赖外部服务

### 5. 模块化设计

```
src/
├── position_engine/    # 独立风控模块 (可独立测试)
│   ├── models.py       # Pydantic 数据模型
│   ├── calculator.py   # 核心计算 (纯函数+Decimal)
│   ├── services.py     # 外部服务 (汇率)
│   └── config.py       # 配置
├── trading_bot/        # 交易执行层
│   ├── strategies/     # 策略实现
│   ├── ai/             # LLM 集成
│   ├── analysis/       # 分析模块
│   └── utils/          # 工具函数
└── mql5_sources/       # MQL5 策略源码 (MT5 平台)
```

## 命名规范

| 类别 | 正确 ✅ | 错误 ❌ |
|------|---------|---------|
| 计算器 | `PositionCalculator` | `Utils`, `Helpers` |
| 模型 | `TradeSignal`, `AssetType` | `Data`, `Info` |
| 服务 | `ExchangeRateService` | `ApiClient`, `Fetcher` |
| 枚举 | `RiskTier.CONSERVATIVE` | `TIER_1`, `RISK_LOW` |

## 反模式清单

- ❌ 金额计算用 `float`
- ❌ 汇率获取失败用默认值 1.0
- ❌ 策略逻辑和风控逻辑混在一个函数
- ❌ 硬编码交易参数（应走配置文件）
- ❌ 缺少异常处理的外部 API 调用
- ❌ 无日志的风控决策

## 引用

- 原始来源: [NeoLabHQ/software-architecture](https://github.com/NeoLabHQ/context-engineering-kit/tree/master/plugins/ddd/skills/software-architecture)
