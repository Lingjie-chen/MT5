# AI_MultiTF_SMC_EA MT5编译指南

## 1. 环境准备

### 1.1 安装MetaTrader 5
确保您已经安装了最新版本的MetaTrader 5终端。

### 1.2 安装MetaEditor
MetaEditor通常随MetaTrader 5一起安装，您可以在MT5终端中通过以下方式打开：
- 点击顶部菜单栏的 "工具" -> "MetaEditor"
- 或使用快捷键 `F4`

## 2. 编译EA

### 2.1 打开项目
1. 打开MetaEditor
2. 点击 "文件" -> "打开"，导航到 `AI_MultiTF_SMC_EA.mqproj` 文件
3. 选择项目文件并点击 "打开"

### 2.2 编译选项设置
1. 在MetaEditor中，点击 "工具" -> "选项"
2. 选择 "编译器" 标签页
3. 确保以下选项已正确设置：
   - ✅ 严格模式 (Strict mode)
   - ❌ 警告视为错误 (Treat warnings as errors)
   - ✅ 优化代码 (Optimize code)
   - ❌ 包含调试信息 (Include debug information)

### 2.3 编译EA
1. 在MetaEditor中，点击 "编译" -> "编译" 或使用快捷键 `F7`
2. 查看编译日志，确保没有错误
3. 编译成功后，EA文件 `AI_MultiTF_SMC_EA.ex5` 将生成在同一目录下

## 3. 配置WebRequest白名单

MT5的WebRequest函数需要将URL添加到白名单才能正常工作。

### 3.1 添加URL到白名单
1. 在MetaEditor中，点击 "工具" -> "选项"
2. 选择 "EA交易" 标签页
3. 点击 "允许WebRequest用于以下URL"
4. 添加以下URL：
   - `http://localhost:5002`
   - `http://127.0.0.1:5002`
5. 点击 "确定" 保存设置

### 3.2 在MT5终端中启用EA交易
1. 打开MT5终端
2. 点击 "工具" -> "选项"
3. 选择 "EA交易" 标签页
4. 确保以下选项已勾选：
   - ✅ 允许算法交易 (Allow algorithmic trading)
   - ✅ 允许DLL导入 (Allow DLL imports)
   - ✅ 允许WebRequest (Allow WebRequest for listed URLs)
5. 点击 "确定" 保存设置

## 4. 运行EA

### 4.1 在图表上加载EA
1. 打开MT5终端
2. 打开您想要交易的图表
3. 将EA从 "导航器" 窗口拖放到图表上
4. 在EA参数设置窗口中，配置您的参数：
   - SymbolName: 交易品种（如 "GOLD" 或 "XAUUSD"）
   - Timeframe: 交易周期（如 PERIOD_H1）
   - RiskPerTrade: 每笔交易风险百分比
   - PythonServerURL: Python服务URL（默认 "http://localhost:5002"）
   - MagicNumber: 魔术数字
   - EnableLogging: 是否启用日志记录
5. 点击 "确定" 运行EA

### 4.2 查看EA日志
1. 在MT5终端中，点击 "工具" -> "专家顾问" -> "日志"
2. 查看EA的运行日志，确保没有错误

## 5. 调试和故障排除

### 5.1 常见错误

#### 错误：WebRequest失败，错误代码 400
**原因**：URL未添加到WebRequest白名单
**解决方案**：按照第3节的步骤添加URL到白名单

#### 错误：无法连接到Python服务器
**原因**：Python服务未启动或URL配置错误
**解决方案**：
1. 确保Python服务已启动
2. 检查PythonServerURL参数是否正确
3. 尝试使用IP地址 `http://127.0.0.1:5002` 替代 `http://localhost:5002`

#### 错误：OrderSend失败，错误代码 10013
**原因**：无效的价格或超出允许的偏差
**解决方案**：
1. 检查交易品种的价格是否有效
2. 调整OrderSend函数中的偏差参数

### 5.2 启用详细日志
1. 在EA参数设置中，将EnableLogging设置为true
2. 查看MT5终端的专家日志，获取详细的错误信息

## 6. 优化建议

### 6.1 代码优化
- 定期更新EA代码，修复bug和优化性能
- 使用最新版本的MT5 API函数
- 优化WebRequest调用，添加适当的超时和重试机制

### 6.2 风险管理
- 根据您的风险偏好调整RiskPerTrade参数
- 设置合理的MaxDailyLoss参数，避免过度亏损
- 定期监控EA的运行状态，及时调整参数

## 7. 版本历史

### v1.00 (2024-12-11)
- 初始版本
- 支持多时间框架分析
- 集成AI信号生成
- 实现智能资金概念策略
- 支持WebRequest调用Python服务

## 8. 联系方式

如有任何问题或建议，请联系：
- GitHub: [https://github.com/ai-quant-trading](https://github.com/ai-quant-trading)
- 邮箱: contact@ai-quant-trading.com

## 9. 许可证

本EA使用MIT许可证，详情请查看项目根目录下的LICENSE文件。