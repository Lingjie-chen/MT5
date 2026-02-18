# UTM Windows 虚拟机设置指南

## 1. 创建 Windows 虚拟机

### 步骤 1：打开 UTM
- 从 Launchpad 或 Applications 文件夹启动 UTM
- 点击「Create a New Virtual Machine」按钮

### 步骤 2：选择虚拟机类型
- 选择「Virtualize」选项
- 选择「Windows」作为操作系统
- 点击「Continue」

### 步骤 3：选择 Windows ISO
- 如果已有 Windows ISO 文件：
  - 选择「Browse」并导航到 ISO 文件位置
  - 推荐使用 Windows 11 或 Windows 10 64-bit
- 如果没有 ISO 文件：
  - 点击「Download Windows」按钮
  - 选择「Windows 10 Pro (64-bit)」
  - 等待下载完成

### 步骤 4：配置内存和 CPU
- 内存 (RAM)：建议分配至少 8 GB
- CPU 核心：建议分配 4 或 6 核心
- 点击「Continue」

### 步骤 5：配置存储
- 虚拟磁盘大小：建议至少 60 GB
- 点击「Continue」

### 步骤 6：配置共享文件夹
- 点击「Enable Shared Directory」
- 选择「Browse」并选择 `/Users/lenovo/tmp/quant_trading_strategy` 文件夹
- 点击「Continue」

### 步骤 7：完成设置
- 为虚拟机命名，如「Windows 10 MT5」
- 点击「Save」保存设置

## 2. 安装 Windows 系统

### 步骤 1：启动虚拟机
- 选中刚创建的虚拟机
- 点击「Play」按钮启动

### 步骤 2：安装 Windows
1. 选择语言和区域设置
2. 点击「Install Now」
3. 输入 Windows 产品密钥（或选择「I don't have a product key」）
4. 选择 Windows 版本（建议 Windows 10 Pro）
5. 接受许可条款
6. 选择「Custom: Install Windows only (advanced)」
7. 选择虚拟磁盘（通常是「Drive 0」）
8. 点击「Next」开始安装
9. 等待安装完成，系统会自动重启

### 步骤 3：完成 Windows 设置
1. 选择区域和键盘布局
2. 连接到网络
3. 选择「Set up for personal use」
4. 登录或创建 Microsoft 账户
5. 等待系统完成设置

## 3. 安装必要软件

### 步骤 1：安装 UTM 驱动程序
1. 在虚拟机中，点击 UTM 菜单栏的「Device」
2. 选择「CD/DVD」→「UTM Spice Tools」
3. 在 Windows 中，打开文件资源管理器
4. 导航到「This PC」→「UTM Spice Tools」
5. 双击「spice-guest-tools-xxx.exe」安装驱动
6. 重启虚拟机

### 步骤 2：安装 Python
1. 打开浏览器，访问 [python.org/downloads/windows](https://www.python.org/downloads/windows/)
2. 下载「Python 3.10.0 - 64-bit」安装程序
3. 运行安装程序，勾选「Add Python 3.10 to PATH」
4. 选择「Customize installation」
5. 保持默认选项，点击「Next」
6. 勾选「Install for all users」
7. 点击「Install」完成安装

### 步骤 3：安装 MetaTrader 5
1. 访问您的经纪商网站或 [MetaTrader 5 官网](https://www.metatrader5.com/)
2. 下载 MT5 终端安装程序
3. 运行安装程序，按照提示完成安装
4. 启动 MT5 终端，创建或登录账户

### 步骤 4：安装 Python 依赖
1. 打开命令提示符（管理员模式）
2. 导航到共享文件夹：
   ```cmd
   cd Z:\quant_trading_strategy
   ```
3. 安装依赖：
   ```cmd
   pip install -r requirements.txt
   ```
4. 验证 MT5 安装：
   ```cmd
   python -c "import MetaTrader5 as mt5; print('MT5 version:', mt5.__version__); print('MT5 initialized:', mt5.initialize())"
   ```

## 4. 配置和运行 Python 服务器

### 步骤 1：配置服务器
1. 在共享文件夹中，打开 `enhanced_server_ml.py`
2. 确保 `host` 设置为 `0.0.0.0`（允许外部访问）
3. 保存文件

### 步骤 2：运行服务器
1. 在命令提示符中：
   ```cmd
   cd Z:\quant_trading_strategy
   python enhanced_server_ml.py
   ```
2. 确认服务器启动成功，输出类似：
   ```
   2025-12-16 22:58:50,765 - __main__ - INFO - 启动增强版Python服务器...
   2025-12-16 22:58:50,766 - __main__ - INFO - 服务器运行在: http://0.0.0.0:5002
   ```

### 步骤 3：获取虚拟机 IP 地址
1. 在命令提示符中：
   ```cmd
   ipconfig
   ```
2. 查找「IPv4 Address」，例如：`192.168.64.2`

## 5. 配置 MQL5 EA

### 步骤 1：复制 EA 文件到 Windows
1. 在 macOS 中，打开 `mql5` 文件夹
2. 复制 `AI_MultiTF_SMC_EA_WebRequest.mq5` 和 `Include/fixed_json_functions.mqh`
3. 粘贴到虚拟机中的 MT5 Experts 文件夹
   - 通常位于：`C:\Users\<用户名>\AppData\Roaming\MetaQuotes\Terminal\<终端ID>\MQL5\Experts`

### 步骤 2：编译和运行 EA
1. 在 MT5 中，打开「Navigator」面板
2. 右键点击「Experts」→「Refresh」
3. 找到 `AI_MultiTF_SMC_EA_WebRequest`
4. 将其拖放到任意图表上
5. 在 EA 设置中：
   - 设置 `WebRequestHost` 为虚拟机的 IPv4 地址
   - 设置 `WebRequestPort` 为 5002
   - 勾选「Allow WebRequest for listed URL」
   - 添加 `http://*` 到允许列表
   - 点击「OK」

## 6. 测试连接

### 步骤 1：测试 API 端点
1. 在 macOS 中，打开浏览器
2. 访问：`http://<虚拟机IP>:5002/health`
3. 应该看到健康检查响应

### 步骤 2：测试 EA 连接
1. 在 MT5 中，查看「Journal」面板
2. 应该看到 EA 成功连接到 Python 服务器的日志
3. 检查是否有交易信号生成

## 7. 优化和维护

### 性能优化
- 分配更多内存和 CPU 核心
- 关闭不必要的 Windows 服务
- 禁用 Windows Defender 实时保护（仅在测试环境）

### 网络优化
- 确保虚拟机网络设置为「Shared Network」
- 检查防火墙设置，允许端口 5002 访问

### 自动启动
1. 创建启动脚本：
   ```cmd
   @echo off
   cd Z:\quant_trading_strategy
   python enhanced_server_ml.py
   ```
2. 保存为 `start_server.bat`
3. 将其添加到 Windows 启动文件夹

## 8. 故障排除

### 问题 1：共享文件夹不可见
- 确保已安装 UTM Spice Tools
- 重启虚拟机
- 检查 UTM 设置中的共享文件夹配置

### 问题 2：Python 无法找到 MetaTrader5
- 确保 MT5 终端已安装
- 以管理员身份运行命令提示符
- 检查 Python 和 MT5 是相同架构（64-bit）

### 问题 3：EA 无法连接到服务器
- 检查虚拟机 IP 地址是否正确
- 确保服务器正在运行
- 检查防火墙设置
- 确保 WebRequest 允许列表已正确配置

### 问题 4：虚拟机运行缓慢
- 分配更多内存和 CPU 资源
- 关闭 macOS 中不必要的应用程序
- 清理虚拟机中的磁盘空间

## 9. 后续步骤

1. **安装 Visual Studio Code**（可选）：用于编辑 Python 和 MQL5 代码
2. **配置远程桌面**：允许从其他设备访问虚拟机
3. **设置自动备份**：定期备份交易数据和策略
4. **测试交易策略**：使用模拟账户进行测试
5. **监控性能**：定期检查服务器日志和交易结果

## 10. 资源

- [UTM 官方文档](https://docs.getutm.app/)
- [Windows 10 安装指南](https://support.microsoft.com/en-us/windows/windows-10-installation-media-cd-dvd-usb-flash-drive-0aa5f448-9afd-7e90-c706-62a029014665)
- [MetaTrader 5 官方文档](https://www.mql5.com/en/docs)

## 总结

通过 UTM 虚拟机，您可以在 macOS 上运行完整的 Windows 环境，实现 MetaTrader 5 与 Python 服务器的无缝集成。这种方案提供了良好的性能和稳定性，适合开发、测试和生产环境使用。

祝您交易顺利！
