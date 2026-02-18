---
name: root-cause-tracing
description: "量化交易系统异常根因追踪。当交易系统出现策略切换失败、风控拦截、订单执行异常、仓位计算错误等深层问题时，使用此 Skill 进行系统性根因分析。"
---

# 量化交易系统根因追踪

当系统异常发生在执行深层且难以直接定位时使用。

## 适用场景

- 策略切换（ORB ↔ Grid）失败或延迟
- 风控拦截了看似正常的交易信号
- 仓位计算结果与预期不符
- 订单执行异常（滑点过大、未成交、重复下单）
- 汇率服务返回异常数据
- 数据库连接或写入异常

## 追踪方法论

### Step 1: 症状收集
```
收集以下信息:
1. 错误发生时间 (精确到秒)
2. 错误描述 (日志原文)
3. 受影响的品种/账户
4. 当时的市场状态 (价格、波动率)
5. 最近一次正常执行的时间
```

### Step 2: 影响范围界定
```
确定:
- 这是偶发还是必现？
- 影响单一品种还是多品种？
- 是否与特定时间段/市场状态相关？
- 其他系统组件是否正常？
```

### Step 3: 假设生成与验证

对量化交易系统，优先检查以下常见根因：

| 排查层级 | 检查点 | 诊断命令/方法 |
|---------|--------|-------------|
| **数据层** | 行情连接是否正常 | 检查 MT5 连接状态和心跳 |
| **数据层** | 汇率缓存是否过期 | 检查 `ExchangeRateService` 缓存 TTL |
| **计算层** | Decimal 精度异常 | 打印中间计算步骤的 Decimal 值 |
| **计算层** | 保证金计算溢出 | 检查极端价格/杠杆组合 |
| **风控层** | 回撤熔断误触发 | 验证 `current_drawdown_percent` 来源 |
| **风控层** | 风控参数配置错误 | 比对 config 与实际生效值 |
| **执行层** | MT5 订单被拒 | 检查 MT5 return code 和错误码 |
| **执行层** | 网络超时/重试 | 检查网络延迟和重试日志 |
| **日志层** | 策略切换记录 | 查看 `strategy_logs` 表的切换轨迹 |
| **数据库层** | 连接池耗尽 | 检查 PostgreSQL 活跃连接数 |

### Step 4: 修复与验证

```
1. 先在测试环境复现问题
2. 定位并修复根因代码
3. 编写回归测试
4. 验证修复在生产环境的效果
5. 监控 24h 确认无复发
```

## 日志分析指南

### 关键日志文件

| 文件 | 内容 |
|------|------|
| `windows_bot.log` | 交易机器人主日志 |
| `auto_sync_engine.log` | 同步引擎日志 |
| `sync_service.log` | 同步服务日志 |
| 策略切换日志 | `src/trading_bot/` 内部日志 |

### 日志搜索模式

```bash
# 搜索错误和异常
grep -i "ERROR\|EXCEPTION\|FAILED\|BLOCKED" windows_bot.log | tail -50

# 搜索风控拦截事件
grep "MAX DRAWDOWN\|Margin Constraint\|BLOCKED" windows_bot.log

# 搜索策略切换
grep "strategy.*switch\|ORB.*Grid\|Grid.*ORB" windows_bot.log
```

## 常见根因速查表

| 症状 | 最可能根因 | 快速修复 |
|------|-----------|---------|
| 仓位为 0 但行情正常 | 回撤熔断触发 | 检查 `max_allowed_drawdown_percent` |
| 仓位远小于预期 | 保证金不足降仓 | 检查 `leverage` 和资金量 |
| 汇率计算错误 | Yahoo Finance API 异常 | 使用 `manual_exchange_rate` |
| SL 价格无效 | SL = Entry 验证失败 | 检查信号生成逻辑 |
| 策略不切换 | 冷却期未过 | 检查冷却期配置 |
| 下单失败 | MT5 连接断开 | 重启 MT5 终端 |

## 引用

- 原始来源: [obra/superpowers/root-cause-tracing](https://github.com/obra/superpowers/tree/main/skills/root-cause-tracing)
- 相关文档: `src/docs/strategy_rules.md` 第9章 (系统日志与监控)
