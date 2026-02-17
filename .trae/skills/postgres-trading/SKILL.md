---
name: postgres-trading
description: "交易数据库 PostgreSQL 只读查询工具。用于查询交易记录、持仓数据、盈亏统计、策略执行日志。当需要分析历史交易数据、检查数据库状态或生成统计报告时使用此 Skill。"
---

# PostgreSQL 交易数据库查询

安全的只读查询工具，专为交易数据库设计。

## 适用场景

- 查询历史交易记录和持仓数据
- 统计胜率、盈亏比、最大回撤等指标
- 检查策略执行日志和异常记录
- 生成交易绩效报告
- 排查数据库中的异常数据

## 前置条件

```bash
pip install psycopg2-binary
```

## 数据库连接配置

在 `skill/postgres-trading/connections.json` 或 `~/.config/claude/postgres-connections.json` 创建配置：

```json
{
  "databases": [
    {
      "name": "trading_bot",
      "description": "量化交易系统主数据库 - 订单、持仓、策略日志、盈亏记录",
      "host": "localhost",
      "port": 5432,
      "database": "trading_bot",
      "user": "chenlingjie",
      "password": "${POSTGRES_PASSWORD}",
      "sslmode": "prefer"
    }
  ]
}
```

> **安全提示**: 请设置 `chmod 600 connections.json`，密码建议通过环境变量 `.env` 注入。

## 常用查询模板

### 交易记录查询
```sql
-- 最近 N 笔交易
SELECT * FROM trades ORDER BY open_time DESC LIMIT 20;

-- 特定品种盈亏汇总
SELECT symbol, COUNT(*) as total, 
       SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) as wins,
       ROUND(AVG(profit), 2) as avg_profit
FROM trades GROUP BY symbol;
```

### 策略绩效分析
```sql
-- 日收益统计
SELECT DATE(close_time) as trade_date,
       COUNT(*) as trades,
       SUM(profit) as daily_pnl,
       ROUND(SUM(CASE WHEN profit > 0 THEN 1.0 ELSE 0.0 END) / COUNT(*) * 100, 1) as win_rate
FROM trades WHERE close_time IS NOT NULL
GROUP BY DATE(close_time) ORDER BY trade_date DESC;

-- 最大连续亏损
WITH consecutive AS (
  SELECT *, SUM(CASE WHEN profit >= 0 THEN 1 ELSE 0 END) 
    OVER (ORDER BY close_time) as grp
  FROM trades WHERE close_time IS NOT NULL
)
SELECT MIN(close_time) as start, MAX(close_time) as end,
       COUNT(*) as streak, SUM(profit) as total_loss
FROM consecutive WHERE profit < 0
GROUP BY grp ORDER BY total_loss LIMIT 5;
```

### 风控监控
```sql
-- 当前持仓汇总
SELECT symbol, direction, SUM(volume) as total_lots,
       SUM(profit) as unrealized_pnl
FROM positions WHERE status = 'open'
GROUP BY symbol, direction;

-- 回撤计算
SELECT MAX(balance) as peak_balance,
       MIN(balance) as trough_balance,
       ROUND((MAX(balance) - MIN(balance)) / MAX(balance) * 100, 2) as max_dd_pct
FROM account_snapshots WHERE timestamp > NOW() - INTERVAL '30 days';
```

## 安全规则

- ✅ **只读模式**: 使用 `readonly=True` PostgreSQL 连接
- ✅ **仅 SELECT**: 只允许 SELECT, SHOW, EXPLAIN, WITH 查询
- ✅ **单语句**: 禁止多条语句执行
- ✅ **超时保护**: 30 秒查询超时
- ✅ **行数限制**: 最多返回 10,000 行
- ❌ **禁止写入**: INSERT, UPDATE, DELETE, DROP 全部被阻断

## 数据库意图匹配

| 用户问题关键词 | 查询方向 |
|---------------|---------|
| 盈亏、收益、利润 | trades / account_snapshots |
| 持仓、仓位 | positions |
| 策略、信号 | strategy_logs / signals |
| 回撤、风控 | account_snapshots / risk_events |
| 订单、成交 | orders / trades |

## 引用

- 原始来源: [sanjay3290/ai-skills/postgres](https://github.com/sanjay3290/ai-skills/tree/main/skills/postgres)
- 数据库配置: `.env` 中的 `POSTGRES_CONNECTION_STRING`
