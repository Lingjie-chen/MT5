# Quant Trading Strategy Deployment Guide

This guide details how to deploy, configure, and run the Quant Trading Strategy system.

## 1. Prerequisites

Before starting, ensure you have the following installed:

*   **Python 3.10+**: [Download Python](https://www.python.org/downloads/)
*   **Git**: [Download Git](https://git-scm.com/downloads)
*   **PostgreSQL**: [Download PostgreSQL](https://www.postgresql.org/download/)
*   **MetaTrader 5 (Windows only)**: Required for the trading bot execution.

## 2. Installation Steps

### 2.1 Clone the Repository
```bash
git clone https://github.com/Lingjie-chen/MT5.git
cd MT5
```

### 2.2 One-Click Setup (Recommended)
We provide automation scripts to handle virtual environment creation and dependency installation.

**Mac/Linux:**
```bash
# Make script executable
chmod +x scripts/setup/setup_env.sh
# Run setup
./scripts/setup/setup_env.sh
# Activate environment
source venv/bin/activate
```

**Windows:**
```cmd
# Run setup script
scripts\setup\setup_env.bat
# Activate environment
venv\Scripts\activate
```

### 2.3 Manual Setup (Alternative)
If you prefer manual installation:
```bash
python -m venv venv
# Activate venv (source venv/bin/activate OR venv\Scripts\activate)
pip install -r requirements.txt
```

## 3. Database Configuration

The system uses a **Remote-First** architecture with PostgreSQL.

1.  **Start PostgreSQL**: Ensure the service is running.
2.  **Create Database & User**:
    ```sql
    CREATE DATABASE trading_bot;
    CREATE USER chenlingjie WITH ENCRYPTED PASSWORD 'clj568741230';
    GRANT ALL PRIVILEGES ON DATABASE trading_bot TO chenlingjie;
    ```
3.  **Configure .env**: Create a `.env` file in the project root:
    ```ini
    POSTGRES_CONNECTION_STRING=postgresql://chenlingjie:clj568741230@localhost:5432/trading_bot
    SERVER_API_KEY=my_secret_key
    SILICONFLOW_API_KEY=your_siliconflow_api_key
    ```

## 4. Running the System

### 4.1 Auto-Sync Engine (Background Service)
Handles **Git Sync**, **DB Sync**, and **Environment Checks**.

*   **Windows**: `scripts\setup\同步windons.bat`
*   **Mac/Linux**: `bash scripts/setup/同步mac.sh`

### 4.2 Trading Bot (Windows Only)
The core logic interacting with MT5.
*   Run the strategy launcher:
    ```cmd
    scripts\run\run_strategies-GOLD.bat
    ```
    *This will launch a watchdog process that automatically restarts the bot if it crashes.*

### 4.3 Analysis Dashboard
Visual interface for monitoring performance.

*   **Windows**: `scripts\run\可视化.bat`
*   **Mac/Linux**: `bash scripts/run/run_dashboard.sh`

## 5. Optimization & Data
**Does optimization use all transaction data?**
Yes. The optimization module (`src/trading_bot/analysis/optimization.py`) and the `HybridOptimizer` in `main.py` are designed to utilize historical data.
*   **Mechanism**: The system fetches historical trade data (stored in PostgreSQL and synced locally to `trading_data.db`).
*   **Seeding**: This historical data is used to "seed" the initial population of the optimization algorithms (like WOAm - Whale Optimization Algorithm).
*   **Benefit**: By using past high-performing parameters as a starting point, the optimizer converges faster and adapts to market conditions based on actual transaction history.

## 6. Project Structure
*   `src/trading_bot/`: Core source code.
    *   `ai/`: AI models (DeepSeek, Qwen).
    *   `analysis/`: Dashboard, Optimization (`optimization.py`), Visualization.
    *   `strategies/`: Trading strategies (e.g., Grid).
*   `scripts/`:
    *   `setup/`: Installation and Sync scripts.
    *   `run/`: Launch scripts for Bot and Dashboard.
    *   `maintenance/`: DB repair and backup tools.
*   `docs/`: Documentation.

## 7. Troubleshooting
*   **PostgreSQL Error**: Check if port 5432 is active and `.env` credentials are correct.
*   **MT5 Missing**: The trading bot only runs on Windows with MT5 installed. Dashboard and Server work on Mac/Linux.
*   **Dependencies**: Re-run `pip install -r requirements.txt` if modules are missing.
