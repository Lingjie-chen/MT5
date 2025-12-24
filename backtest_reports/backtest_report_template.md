# AI量化交易策略回测报告

## 1. 策略概述

### 1.1 策略名称
AI_MultiTF_SMC_EA

### 1.2 策略类型
多时间框架"聪明钱"概念(Smart Money Concepts)交易系统

### 1.3 核心逻辑
- **突破交易**：价格突破供应/需求区域
- **重测交易**：价格重新测试已突破的区域
- **区域拒绝交易**：价格在区域内被拒绝形成反转K线
- **多时间框架确认**：多个时间周期信号一致时才触发交易

### 1.4 模型融合
- **DeepSeek模型**：市场结构分析、情绪得分生成、数据处理
- **Qwen3模型**：策略逻辑优化、动态止盈止损、信号强度判断

## 2. 回测参数

| 参数 | 值 |
|------|-----|
| 初始资金 | {{initial_capital}} |
| 交易品种 | {{symbol}} |
| 交易周期 | {{timeframe}} |
| 回测周期 | {{start_date}} 至 {{end_date}} |
| 每笔交易风险 | {{risk_per_trade}}% |
| 每日最大亏损 | {{max_daily_loss}}% |
| 魔术数字 | {{magic_number}} |

## 3. 性能指标

| 指标 | 值 |
|------|-----|
| 总收益率 | {{total_return}} |
| 年化收益率 | {{annual_return}} |
| 波动率 | {{volatility}} |
| 夏普比率 | {{sharpe_ratio}} |
| 最大回撤 | {{max_drawdown}} |
| 胜率 | {{win_rate}} |
| 风险回报比 | {{risk_reward_ratio}} |
| 总交易次数 | {{total_trades}} |
| 盈利交易次数 | {{winning_trades}} |
| 亏损交易次数 | {{losing_trades}} |

## 4. 交易记录

### 4.1 最近10笔交易

| 入场时间 | 入场价格 | 出场时间 | 出场价格 | 信号类型 | 盈亏 | 盈亏比 |
|----------|----------|----------|----------|----------|------|--------|
{{recent_trades}}

### 4.2 交易分布

| 信号类型 | 交易次数 | 胜率 | 平均盈亏 |
|----------|----------|------|----------|
| 买入信号 | {{buy_trades}} | {{buy_win_rate}} | {{buy_avg_pnl}} |
| 卖出信号 | {{sell_trades}} | {{sell_win_rate}} | {{sell_avg_pnl}} |

## 5. 权益曲线与最大回撤

### 5.1 权益曲线

![权益曲线]({{equity_curve_image}})

### 5.2 最大回撤

![最大回撤]({{drawdown_image}})

## 6. 策略分析

### 6.1 优势
- 多时间框架确认提高了信号准确性
- 动态止盈止损适应不同市场条件
- 智能资金管理控制风险
- 结合AI模型优化策略逻辑

### 6.2 劣势
- 依赖Python服务的稳定性
- 高频数据处理可能导致延迟
- AI模型预测存在不确定性

### 6.3 改进建议
- 优化AI模型提示词，提高信号质量
- 添加更多技术指标作为辅助信号
- 优化仓位管理算法
- 增加市场极端情况的处理逻辑

## 7. 结论

### 7.1 回测结果总结
{{conclusion}}

### 7.2 实盘建议
- 建议先在模拟账户测试2-4周
- 初始实盘资金建议不超过总资金的20%
- 定期监控AI模型性能，每季度更新一次模型
- 根据实盘表现调整风险参数

## 8. 附录

### 8.1 策略参数配置
```json
{
  "symbol": "{{symbol}}",
  "timeframe": "{{timeframe}}",
  "risk_per_trade": {{risk_per_trade}},
  "max_daily_loss": {{max_daily_loss}},
  "magic_number": {{magic_number}}
}
```

### 8.2 AI模型调用记录
- DeepSeek API调用次数：{{deepseek_api_calls}}
- Qwen3 API调用次数：{{qwen_api_calls}}

### 8.3 回测日志
{{backtest_logs}}

---

*报告生成时间：{{report_generated_time}}*
*报告版本：v1.0*
