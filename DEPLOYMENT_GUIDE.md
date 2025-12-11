# AI_MultiTF_SMC_EA 部署和维护指南

## 1. 系统架构

本系统采用分布式架构，包含以下组件：

- **MT5终端**：运行EA，执行交易订单
- **Python服务**：处理数据、调用AI模型、生成交易信号
- **AI模型**：DeepSeek和Qwen3模型，用于市场分析和策略优化

## 2. 环境要求

### 2.1 硬件要求

| 组件 | 最低配置 | 推荐配置 |
|------|----------|----------|
| CPU | 4核 | 8核+ |
| 内存 | 8GB | 16GB+ |
| 硬盘 | 50GB可用空间 | 100GB SSD |
| 网络 | 稳定的宽带连接 | 光纤连接，低延迟 |

### 2.2 软件要求

| 组件 | 版本 |
|------|------|
| Windows | 10/11 64位 |
| MT5终端 | 最新版本 |
| Python | 3.8+ |
| pip | 最新版本 |
| Git | 最新版本 |

## 3. 环境配置

### 3.1 安装Python依赖

1. 克隆项目代码：
   ```bash
   git clone https://github.com/ai-quant-trading/ai_multitf_smc_ea.git
   cd ai_multitf_smc_ea
   ```

2. 创建虚拟环境：
   ```bash
   python -m venv venv
   ```

3. 激活虚拟环境：
   - Windows：
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux：
     ```bash
     source venv/bin/activate
     ```

4. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

### 3.2 配置API密钥

1. 创建API密钥配置文件：
   ```bash
   cp .env.example .env
   ```

2. 编辑`.env`文件，添加API密钥：
   ```
   # DeepSeek API配置
   DEEPSEEK_API_KEY=your_deepseek_api_key
   DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
   
   # Qwen3 API配置
   QWEN_API_KEY=your_qwen_api_key
   QWEN_BASE_URL=https://api.qwen.com/v1
   
   # 服务器配置
   SERVER_HOST=0.0.0.0
   SERVER_PORT=5000
   ```

### 3.3 配置MT5终端

1. 下载并安装MT5终端：https://www.metatrader5.com/

2. 登录您的交易账户

3. 启用DLL导入：
   - 点击`工具` → `选项` → `EA交易`
   - 勾选`允许DLL导入`和`允许WebRequest用于 listed URL`
   - 添加Python服务URL：`http://localhost:5000`到允许列表

## 4. 部署流程

### 4.1 启动Python服务

1. 激活虚拟环境（如果尚未激活）

2. 启动Python服务：
   ```bash
   python server.py
   ```

3. 确认服务启动成功：
   - 控制台输出：`Server running on http://0.0.0.0:5000`
   - 浏览器访问：`http://localhost:5000/health`，返回`{"status": "ok"}`

### 4.2 部署EA到MT5

1. 编译EA：
   - 打开MT5终端
   - 点击`文件` → `打开数据文件夹`
   - 将`AI_MultiTF_SMC_EA.mq5`文件复制到`MQL5\Experts`目录
   - 在MT5终端中，点击`工具` → `MetaEditor`
   - 打开`AI_MultiTF_SMC_EA.mq5`文件，点击编译按钮

2. 加载EA到图表：
   - 在MT5终端中，找到您要交易的品种（如GOLD）
   - 右键点击图表 → `EA交易` → `AI_MultiTF_SMC_EA`
   - 在EA属性窗口中，配置参数：
     - `SymbolName`：交易品种，如`GOLD`
     - `Timeframe`：交易周期，如`PERIOD_H1`
     - `RiskPerTrade`：每笔交易风险，如`1.0`
     - `MaxDailyLoss`：每日最大亏损，如`2.0`
     - `PythonServerURL`：Python服务URL，如`http://localhost:5001`
     - `MagicNumber`：魔术数字，如`123456`
     - `EnableLogging`：启用日志记录，勾选

3. 启动EA：
   - 点击`确定`按钮
   - 确保EA图标变为笑脸（表示EA正在运行）

## 5. 监控与维护

### 5.1 监控EA运行状态

1. 查看EA日志：
   - 在MT5终端中，点击`工具` → `专家顾问`
   - 查看EA的日志输出，确认：
     - EA初始化成功
     - 能够连接到Python服务
     - 能够获取市场数据
     - 能够执行交易订单

2. 监控Python服务日志：
   - 在Python服务控制台中，查看：
     - API调用是否成功
     - 数据处理是否正常
     - 信号生成是否稳定

### 5.2 定期维护任务

| 任务 | 频率 | 操作步骤 |
|------|------|----------|
| 备份数据 | 每日 | 备份MT5数据文件夹和Python服务日志 |
| 更新MT5终端 | 每周 | 检查并更新MT5终端到最新版本 |
| 更新Python依赖 | 每月 | 执行`pip install --upgrade -r requirements.txt` |
| 优化AI模型提示词 | 每季度 | 根据市场表现调整AI模型的提示词 |
| 回测策略 | 每季度 | 使用最新数据回测策略，评估性能 |
| 检查API使用情况 | 每月 | 查看API调用次数和费用，确保在预算范围内 |

### 5.3 常见问题排查

1. **EA无法连接到Python服务**
   - 检查Python服务是否正在运行
   - 检查防火墙设置，确保端口5000已开放
   - 检查MT5终端的WebRequest设置，确保Python服务URL已添加到允许列表

2. **API调用失败**
   - 检查API密钥是否正确
   - 检查网络连接是否稳定
   - 查看API服务商状态，确认服务是否正常
   - 检查API调用次数是否超过限制

3. **EA不生成交易信号**
   - 检查市场数据是否正常
   - 检查AI模型调用是否成功
   - 检查策略参数是否设置正确
   - 查看EA日志，确认是否有错误信息

4. **订单执行失败**
   - 检查交易账户余额是否充足
   - 检查交易品种的交易权限
   - 查看MT5终端的日志，确认错误代码
   - 检查止损止盈设置是否合理

## 6. 安全注意事项

1. **API密钥安全**：
   - 不要将API密钥硬编码到代码中
   - 不要将API密钥分享给他人
   - 定期更换API密钥
   - 使用环境变量或加密配置文件存储API密钥

2. **MT5终端安全**：
   - 设置强密码保护MT5终端
   - 启用双因素认证
   - 不要在公共网络上登录MT5终端
   - 定期更新MT5终端到最新版本

3. **Python服务安全**：
   - 不要将Python服务暴露在公共网络上
   - 使用防火墙限制访问
   - 定期更新Python和依赖库
   - 监控服务日志，及时发现异常

## 7. 性能优化

1. **Python服务优化**：
   - 使用多进程或多线程处理请求
   - 缓存AI模型调用结果，减少API调用次数
   - 优化数据处理算法，提高处理速度

2. **EA优化**：
   - 减少不必要的计算和函数调用
   - 优化交易信号生成逻辑
   - 合理设置定时器间隔，避免过度占用CPU资源

3. **网络优化**：
   - 使用低延迟网络连接
   - 优化API调用参数，减少数据传输量
   - 考虑使用CDN或代理服务器，减少API调用延迟

## 8. 版本更新

1. **检查更新**：
   - 定期查看项目GitHub仓库，确认是否有新版本
   - 关注项目的Release Notes，了解更新内容

2. **更新流程**：
   - 备份当前代码和配置
   - 拉取最新代码：
     ```bash
     git pull origin main
     ```
   - 检查配置文件是否有变化：
     ```bash
     git diff .env.example
     ```
   - 更新依赖：
     ```bash
     pip install --upgrade -r requirements.txt
     ```
   - 重新编译EA并部署到MT5
   - 启动Python服务和EA

## 9. 联系支持

如果您遇到任何问题，可以通过以下方式获取支持：

- **GitHub Issues**：https://github.com/ai-quant-trading/ai_multitf_smc_ea/issues
- **电子邮件**：support@ai-quant-trading.com
- **社区论坛**：https://forum.ai-quant-trading.com

## 10. 许可证

本项目采用MIT许可证，详见LICENSE文件。

---

*本指南最后更新于：2024年12月*
*版本：v1.0*
