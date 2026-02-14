# Quantum Position Engine & MT5 Trading Bot

本指南详细介绍了如何部署、配置和运行量化交易策略系统，包括最新的 **Quantum Position Engine** 风控模块。

## 1. 核心特性：Quantum Position Engine (New)

本项目集成了 **Quantum Position Engine**，一个高精度、生产级的仓位计算引擎，专为量化交易设计。

*   **精度问题**：全程使用 `Decimal` 运算，杜绝浮点数误差。
*   **跨币种风控**：支持账户本位币（如USD）与交易标的（如日经指数 JPY）不一致时的自动汇率换算。
*   **动态风控**：集成最大回撤熔断、保证金不足自动降仓等逻辑。
*   **模块化集成**：也能无缝嵌入 MetaTrader 5 (MT5) 策略中。

### 1.1 项目结构 (Updated)

```text
src/
├── position_engine/          # [核心风控模块]
│   ├── calculator.py         # 核心算法引擎 (Decimal)
│   ├── models.py             # 数据模型 (Pydantic)
│   ├── services.py           # 外部服务 (汇率 + 缓存)
│   ├── config.py             # 全局配置
│   └── mt5_adapter.py        # [关键] MT5 专用适配器
│
├── trading_bot/              # [原有策略模块]
│   ├── ai/                   # AI 模型 (DeepSeek, Qwen)
│   ├── analysis/             # 仪表板、优化、可视化
│   ├── strategies/           # 交易策略 (网格, Martingale)
│   └── main.py               # 策略入口 (已集成 Quantum Engine)
│
└── skill/                    # [AI 技能系统]
    ├── Skill_Seekers/        # Skill Seekers 源码仓库
    ├── skill-seekers/        # 生成的 AI 技能包
    └── superpowers/          # Superpowers 工作流配置
```

## 2. 前置条件

开始之前，请确保已安装以下软件：

*   **Python 3.10+**: [下载 Python](https://www.python.org/downloads/)
*   **Git**: [下载 Git](https://git-scm.com/downloads)
*   **PostgreSQL**: [下载 PostgreSQL](https://www.postgresql.org/download/)
*   **MetaTrader 5 (仅限 Windows)**:（ https://www.metatrader5.com/）

## 3. 安装步骤

### 3.1 克隆仓库
```bash
git clone https://github.com/Lingjie-chen/MT5.git
cd MT5
```

### 3.2 一键设置（推荐）
我们提供了自动化脚本来处理虚拟环境创建和依赖安装。

**Mac/Linux:**
```bash
chmod +x scripts/setup/setup_env.sh
./scripts/setup/setup_env.sh
source venv/bin/activate
```

**Windows:**
```cmd
scripts\setup\setup_env.bat
venv\Scripts\activate
```

### 3.3 手动安装依赖
如果您已经有环境，请更新依赖以支持 Quantum Engine：
```bash
pip install -r requirements.txt
```

## 4. 数据库配置

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

## 5. 运行系统

### 5.1 交易机器人（仅限 Windows）
与 MT5 交互的核心逻辑。

**方式 A: 使用脚本启动 (推荐)**
```cmd
scripts\run\run_strategies-GOLD.bat
```

**方式 B: 直接运行 Python 模块**
```cmd
python -m src.trading_bot.main GOLD
```

### 5.2 自动同步引擎（后台服务）
*   **Windows**: `scripts\setup\同步windons.bat`
*   **Mac/Linux**: `bash scripts/setup/同步mac.sh`

### 5.3 分析仪表板
*   **Windows**: `scripts\run\可视化.bat`
*   **Mac/Linux**: `bash scripts/run/run_dashboard.sh`

## 6. 故障排除
*   **PostgreSQL 错误**：检查 5432 端口是否处于活动状态，且 `.env` 中的凭据是否正确。
*   **找不到 MT5**：交易机器人仅在安装了 MT5 的 Windows 上运行。
*   **依赖缺失**：如果缺少模块，请重新运行 `pip install -r requirements.txt`。
