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
├── position_engine/              # [核心风控模块]
├── trading_bot/                  # [原有策略模块]
├── mql5_sources/                 # [MQL5 策略源码]
│   ├── Include/
│   ├── MQL5/
│   └── ...
└── docs/                         # [策略文档]
    └── strategy_rules.md

skill/                            # [AI 技能系统]
    ├── skills-registry.yaml      # 全局技能注册表
    ├── Skill_Seekers/            # Skill Seekers 源码仓库
    ├── skill-seekers/            # 生成的 AI 技能包
    ├── superpowers/              # Superpowers 工作流配置
    ├── quant-strategy-rules/     # SMC+马丁策略规则
    ├── quantum-position-engine/  # 仓位计算引擎指南
    ├── trading-risk-management/  # 风控决策框架
    ├── market-analysis-precheck/ # 盘前 8 问检查清单
    ├── postgres-trading/         # 交易数据库查询
    ├── changelog-generator/      # 策略变更日志
    ├── software-architecture/    # 金融系统架构规范
    ├── deep-research/            # 市场深度研究
    ├── csv-data-summarizer/      # 交易日志分析
    └── root-cause-tracing/       # 异常根因追踪
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

## 6. AI Skill System

本项目集成了 **12 个 AI Skills**，统一注册在 `skill/skills-registry.yaml`，覆盖策略执行、风控决策、数据分析和开发工程全链路。

所有 Skill 资源统一管理在 `skill/` 目录下，并已自动同步至 `.trae/skills/` 以供 AI 助手调用。

### 6.1 交易策略 Skills（自定义）

| Skill | 用途 |
|-------|------|
| `quant-strategy-rules` | SMC + 顺势马丁策略规则引擎（入场/出场/Grid 切换） |
| `quantum-position-engine` | Decimal 精度仓位计算引擎（Risk Tier/保证金/汇率） |
| `trading-risk-management` | 风控决策框架（回撤熔断/降仓/Basket TP/马丁加仓） |
| `market-analysis-precheck` | 盘前 8 问质询清单（趋势/结构/偏见/执行条件） |

### 6.2 数据与分析 Skills（适配自 awesome-claude-skills）

| Skill | 用途 | 来源 |
|-------|------|------|
| `postgres-trading` | 交易数据库只读查询 + 绩效统计模板 | [postgres](https://github.com/sanjay3290/ai-skills/tree/main/skills/postgres) |
| `csv-data-summarizer` | 交易日志 CSV 分析（胜率/盈亏比/Sharpe/回撤） | [csv-data-summarizer](https://github.com/coffeefuelbump/csv-data-summarizer-claude-skill) |
| `deep-research` | 量化市场深度研究（宏观/技术面/相关性/微观结构） | [deep-research](https://github.com/sanjay3290/ai-skills/tree/main/skills/deep-research) |

### 6.3 工程与开发 Skills（适配自 awesome-claude-skills）

| Skill | 用途 | 来源 |
|-------|------|------|
| `software-architecture` | 金融系统架构规范（Decimal 精度/跨币种/DDD） | [software-architecture](https://github.com/NeoLabHQ/context-engineering-kit) |
| `changelog-generator` | 策略迭代变更日志（📈策略/🛡️风控/⚡引擎分类） | [changelog-generator](https://github.com/ComposioHQ/awesome-claude-skills) |
| `root-cause-tracing` | 交易系统异常根因追踪（信号/风控/执行/DB） | [superpowers](https://github.com/obra/superpowers) |

### 6.4 预装 Skills

| Skill | 用途 |
|-------|------|
| `superpowers` | RED-GREEN-REFACTOR 与两阶段评审工作流 |
| `skill-seekers` | 文档/代码库 RAG 预处理与 Skill 生成 |

### 6.5 Skill Seekers 使用指南

**Skill Seekers** 是一个强大的文档和代码库处理工具，已在本项目中全局配置。

#### 方式 A: 通过 AI 助手使用 (推荐)
在对话中直接请求执行相关任务，AI 会自动调用 Skill Seekers 的能力：
*   "请帮我学习 https://fastapi.tiangolo.com/ 的文档并生成 Skill"
*   "分析当前代码库的架构和设计模式"
*   "把这个 PDF 手册转换成 Skill"

#### 方式 B: 命令行使用 (CLI)
```bash
# 抓取文档网站
skill-seekers scrape --url https://react.dev --name react

# 分析 GitHub 仓库
skill-seekers github --repo facebook/react

# 交互式配置
skill-seekers config
```

### 6.6 维护与同步

修改 `skills/` 目录下的 Skill 后，运行以下命令同步到 `.trae/skills/` 和 `.agent/skills/`：
```bash
for d in skills/*/; do name=$(basename "$d"); mkdir -p ".trae/skills/$name" ".agent/skills/$name" && cp "$d/SKILL.md" ".trae/skills/$name/" && cp "$d/SKILL.md" ".agent/skills/$name/" 2>/dev/null; done
```

## 7. 故障排除
*   **PostgreSQL 错误**：检查 5432 端口是否处于活动状态，且 `.env` 中的凭据是否正确。
*   **找不到 MT5**：交易机器人仅在安装了 MT5 的 Windows 上运行。
*   **依赖缺失**：如果缺少模块，请重新运行 `pip install -r requirements.txt`。
