# 在 UTM 虚拟机 (Windows) 上部署量化交易策略指南

本指南将帮助您在 Mac 上的 UTM 虚拟机中安装 Windows，并部署 AI 量化交易策略。

## 准备工作

1.  **UTM 软件**: 确保已在 Mac 上安装 UTM (https://mac.getutm.app/)。
2.  **Windows 镜像**: 下载 Windows 11 (ARM64) 或 Windows 10 的 ISO 镜像文件 (推荐使用 CrystalFetch 下载)。
3.  **本项目代码**: 确保您已经将本项目上传到 Git 仓库，或者可以通过其他方式传输到虚拟机中。

---

## 步骤 1: 创建并配置 Windows 虚拟机

1.  打开 UTM，点击 "+" 创建新虚拟机。
2.  选择 "虚拟化" (Virtualize) -> "Windows"。
3.  勾选 "安装 Windows 10 或更高版本" (Install Windows 10 or higher) 和 "安装驱动程序和 SPICE 工具" (Install drivers and SPICE tools)。
4.  选择您下载的 Windows ISO 镜像文件。
5.  配置硬件：
    *   **内存**: 建议至少 4GB (4096MB)，推荐 8GB。
    *   **CPU**: 默认即可。
    *   **存储**: 建议至少 64GB。
6.  保存并启动虚拟机，按照 Windows 安装向导完成安装。

> **注意**: 如果安装过程中遇到网络问题，可以先跳过网络连接步骤，安装完成后再安装 SPICE Guest Tools 驱动。

---

## 步骤 2: 安装基础环境 (在虚拟机 Windows 中)

### 1. 安装 Git
*   下载并安装 [Git for Windows](https://git-scm.com/download/win)。
*   安装时一路点击 "Next" 即可。

### 2. 安装 Python
*   下载 [Python 3.10 或 3.11](https://www.python.org/downloads/windows/) (Windows 64-bit installer)。
*   **重要**: 安装时务必勾选 **"Add Python to PATH"** (将 Python 添加到环境变量)。
*   点击 "Install Now"。

### 3. 安装 MetaTrader 5 (MT5)
*   从您的经纪商网站或 [MetaTrader 官网](https://www.metatrader5.com/en/download) 下载并安装 MT5 终端。

---

## 步骤 3: 部署项目代码

1.  在 Windows 中打开命令提示符 (CMD) 或 PowerShell。
2.  克隆您的 Git 仓库 (或者将项目文件复制到虚拟机中)：
    ```powershell
    git clone https://forge.mql5.io/lingjiechen/mql5.git C:\quant_trading_strategy
    cd C:\quant_trading_strategy
    ```
3.  安装 Python 依赖库：
    ```powershell
    pip install -r requirements.txt
    ```
    *这会自动安装 `MetaTrader5`, `flask`, `pandas`, `scikit-learn` 等必要的库。*

---

## 步骤 4: 配置 MetaTrader 5

这是最关键的一步，确保 EA 能与 Python 服务器通信。

1.  打开 MT5 终端。
2.  点击菜单栏 **工具 (Tools)** -> **选项 (Options)** (快捷键 `Ctrl+O`)。
3.  切换到 **EA 交易 (Expert Advisors)** 选项卡。
4.  勾选以下选项：
    *   [x] 允许算法交易 (Allow algorithmic trading)
    *   [x] 允许 WebRequest (Allow WebRequest for listed URL)
5.  在 WebRequest URL 列表中，添加并启用：
    *   `http://127.0.0.1:5002`
    *   `http://localhost:5002`
6.  点击 **确定 (OK)** 保存。

---

## 步骤 5: 安装 EA 脚本

1.  在 MT5 中，点击菜单栏 **文件 (File)** -> **打开数据文件夹 (Open Data Folder)**。
2.  进入 `MQL5` 文件夹。
3.  **复制 Include 文件**:
    *   将项目中的 `mql5/Include/fixed_json_functions.mqh` 复制到 MT5 数据文件夹的 `MQL5/Include/` 目录中。
4.  **复制 EA 文件**:
    *   将项目中的 `mql5/AI_MultiTF_SMC_EA_WebRequest.mq5` 复制到 MT5 数据文件夹的 `MQL5/Experts/` 目录中。
5.  回到 MT5 终端，在 **导航器 (Navigator)** 面板中，右键点击 **EA 交易 (Expert Advisors)**，选择 **刷新 (Refresh)**。
6.  您应该能看到 `AI_MultiTF_SMC_EA_WebRequest` 出现在列表中。

---

## 步骤 6: 启动系统

### 1. 启动 Python 服务器
在 Windows 的 CMD 或 PowerShell 中运行：
```powershell
cd C:\quant_trading_strategy
python enhanced_server.py
```
*您应该看到类似 "服务器运行在: http://0.0.0.0:5002" 的日志。*

### 2. 运行 EA
1.  在 MT5 中打开一个图表 (例如 EURUSD H1)。
2.  将 `AI_MultiTF_SMC_EA_WebRequest` 拖拽到图表上。
3.  在弹出的参数窗口中：
    *   确保 **常用 (Common)** 标签页中的 "允许算法交易" 已勾选。
    *   在 **输入 (Inputs)** 标签页中，检查设置 (默认即可)。
4.  点击 **确定 (OK)**。

**成功标志**:
*   图表右上角的帽子图标应该是蓝色的（而不是灰色）。
*   MT5 底部的 **工具箱 (Toolbox)** -> **专家 (Experts)** 标签页中应该显示 "WebRequest成功，响应: ..." 或 "AI信号处理..." 的日志。
*   Python 服务器窗口应该显示 "请求处理成功: get_signal..." 的日志。

---

## 常见问题排查

1.  **错误: "Failed to connect to server" (连接服务器失败)**
    *   检查 Python 服务器是否正在运行。
    *   检查 MT5 选项中是否已添加 `http://127.0.0.1:5002` 到 WebRequest 允许列表。
    *   检查 Windows 防火墙是否阻止了 Python 进程 (通常本地回环连接不会被阻止，但值得检查)。

2.  **错误: "ModuleNotFoundError: No module named 'MetaTrader5'"**
    *   确保您是在 Windows 环境下安装的 Python。
    *   确保运行了 `pip install MetaTrader5`。

3.  **EA 图标是灰色的**
    *   点击 MT5 工具栏上的 "算法交易" (Algo Trading) 按钮，使其变绿。

4.  **Python 服务器报错 "Address already in use"**
    *   端口 5002 被占用。打开任务管理器结束所有 python 进程，或重启虚拟机。
