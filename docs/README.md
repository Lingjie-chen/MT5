# 量化交易策略部署指南

本指南详细介绍了如何部署、配置和运行量化交易策略系统。

## 1. 前置条件

开始之前，请确保已安装以下软件：

*   **Python 3.10+**: [下载 Python](https://www.python.org/downloads/)
*   **Git**: [下载 Git](https://git-scm.com/downloads)
*   **PostgreSQL**: [下载 PostgreSQL](https://www.postgresql.org/download/)
*   **MetaTrader 5 (仅限 Windows)**: 运行交易机器人所需。

## 2. 安装步骤

### 2.1 克隆仓库
```bash
git clone https://github.com/Lingjie-chen/MT5.git
cd MT5
```

### 2.2 一键设置（推荐）
我们提供了自动化脚本来处理虚拟环境创建和依赖安装。

**Mac/Linux:**
```bash
# 添加执行权限
chmod +x scripts/setup/setup_env.sh
# 运行设置脚本
./scripts/setup/setup_env.sh
# 激活环境
source venv/bin/activate
```

**Windows:**
```cmd
# 运行设置脚本
scripts\setup\setup_env.bat
# 激活环境
venv\Scripts\activate
```

### 2.3 手动设置（可选）
如果您更喜欢手动安装：
```bash
python -m venv venv
# 激活环境 (Mac/Linux: source venv/bin/activate 或 Windows: venv\Scripts\activate)
pip install -r requirements.txt
```

## 3. 数据库配置

本系统采用基于 PostgreSQL 的**远程优先**架构。

1.  **启动 PostgreSQL**：确保服务正在运行。
2.  **创建数据库和用户**：
    ```sql
    CREATE DATABASE trading_bot;
    CREATE USER chenlingjie WITH ENCRYPTED PASSWORD 'clj568741230';
    GRANT ALL PRIVILEGES ON DATABASE trading_bot TO chenlingjie;
    ```
3.  **配置 .env**：在项目根目录创建一个 `.env` 文件：
    ```ini
    POSTGRES_CONNECTION_STRING=postgresql://chenlingjie:clj568741230@localhost:5432/trading_bot
    SERVER_API_KEY=my_secret_key
    SILICONFLOW_API_KEY=your_siliconflow_api_key
    ```

## 4. 运行系统

### 4.1 自动同步引擎（后台服务）
自动处理 **Git 同步**、**数据库同步**和**环境检查**。

*   **Windows**: `scripts\setup\同步windons.bat`
*   **Mac/Linux**: `bash scripts/setup/同步mac.sh`

### 4.2 交易机器人（仅限 Windows）
与 MT5 交互的核心逻辑。
*   运行策略启动器：
    ```cmd
    scripts\run\run_strategies-GOLD.bat
    ```
    *这将启动一个守护进程，如果机器人崩溃，它会自动重启。*

### 4.3 分析仪表板
用于监控性能的可视化界面。

*   **Windows**: `scripts\run\可视化.bat`
*   **Mac/Linux**: `bash scripts/run/run_dashboard.sh`

## 5. 优化与数据
**优化是否使用了所有交易数据？**
是的。优化模块 (`src/trading_bot/analysis/optimization.py`) 和 `main.py` 中的 `HybridOptimizer` 旨在充分利用历史数据。
*   **机制**：系统获取历史交易数据（存储在 PostgreSQL 中并同步到本地 `trading_data.db`）。
*   **种子初始化**：此历史数据用于为优化算法（如 WOAm - 鲸鱼优化算法）的初始种群进行“播种” (Seeding)。
*   **优势**：通过使用过去表现良好的参数作为起点，优化器能更快收敛并根据实际交易历史适应市场条件。

## 6. 项目结构
*   `src/trading_bot/`: 核心源代码。
    *   `ai/`: AI 模型 (DeepSeek, Qwen)。
    *   `analysis/`: 仪表板、优化 (`optimization.py`)、可视化。
    *   `strategies/`: 交易策略（如网格策略）。
*   `scripts/`:
    *   `setup/`: 安装和同步脚本。
    *   `run/`: 机器人和仪表板的启动脚本。
    *   `maintenance/`: 数据库修复和备份工具。
*   `docs/`: 文档。

## 7. 故障排除
*   **PostgreSQL 错误**：检查 5432 端口是否处于活动状态，且 `.env` 中的凭据是否正确。
*   **找不到 MT5**：交易机器人仅在安装了 MT5 的 Windows 上运行。仪表板和服务器可在 Mac/Linux 上运行。
*   **依赖缺失**：如果缺少模块，请重新运行 `pip install -r requirements.txt`。
