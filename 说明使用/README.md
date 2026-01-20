# Quant Trading Strategy Deployment Guide

This guide details how to deploy, configure, and run the Quant Trading Strategy system on a new device (Windows/Mac/Linux).

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

### 2.2 Set up Virtual Environment
It is recommended to use a virtual environment to manage dependencies.

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### 2.3 Install Dependencies
```bash
pip install -r requirements.txt
```
*Note: On Mac/Linux, `MetaTrader5` package will be skipped as it is Windows-only. The analysis dashboard and backend server can still run on Mac/Linux.*

## 3. Database Configuration (PostgreSQL)

The system uses a **Remote-First** architecture where PostgreSQL is the primary data store.

### 3.1 Install and Start PostgreSQL
Ensure the PostgreSQL service is running.

### 3.2 Create Database and User
Open your terminal or SQL tool (like pgAdmin) and run:

```sql
CREATE DATABASE trading_bot;
CREATE USER chenlingjie WITH ENCRYPTED PASSWORD 'clj568741230';
GRANT ALL PRIVILEGES ON DATABASE trading_bot TO chenlingjie;
```

### 3.3 Configure Environment Variables
Create a `.env` file in the project root:

```ini
# Database Connection
POSTGRES_CONNECTION_STRING=postgresql://chenlingjie:clj568741230@localhost:5432/trading_bot

# API Keys
SERVER_API_KEY=my_secret_key
SILICONFLOW_API_KEY=your_siliconflow_api_key
```

## 4. One-Click Setup (Quick Start)

We have provided automation scripts to handle the entire setup process (virtual env, dependencies, .env file) in one go.

### Mac/Linux
```bash
# Make the script executable
chmod +x setup_env.sh

# Run the setup script
./setup_env.sh

# Activate the environment
source venv/bin/activate
```

### Windows
```cmd
# Run the setup script
setup_env.bat

# Activate the environment
venv\Scripts\activate
```

Once the environment is activated, you are ready to run the system!

## 5. Data Migration (Optional)

If you have existing local SQLite data (`.db` files) that you want to migrate to the new remote PostgreSQL database:

```bash
python migrate_sqlite_to_postgres.py
```
*This script automatically detects all `trading_data_*.db` files and uploads them to PostgreSQL.*

## 5. Running the System

The system consists of three main components:

### 5.1 Backend API Server (FastAPI)
This server handles data ingestion and serves history to the bot.

```bash
# Mac/Linux
export POSTGRES_CONNECTION_STRING="postgresql://chenlingjie:clj568741230@localhost:5432/trading_bot"
uvicorn gold.server.main:app --host 0.0.0.0 --port 8000 --reload

# Windows (Command Prompt)
set POSTGRES_CONNECTION_STRING=postgresql://chenlingjie:clj568741230@localhost:5432/trading_bot
uvicorn gold.server.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5.2 Trading Bot (Windows Only)
The core logic that interacts with MT5.

```cmd
python gold/start.py
```
*Ensure MT5 terminal is running and "Algo Trading" is enabled.*

### 5.3 Analysis Dashboard (Streamlit)
Visual interface for monitoring performance.

```bash
streamlit run dashboard.py
```

## 6. Maintenance & Sync

### 6.1 Auto-Sync Scripts
These scripts handle syncing code with GitHub and cleaning up local cache files once uploaded.

*   **Windows**: Run `scripts\自动.bat`
*   **Mac/Linux**: Run `bash scripts/auto_push.sh`

### 6.2 Local DB Cleanup
The system automatically uploads data to PostgreSQL. Local `.db` files are cache-only. The sync scripts above will automatically delete local DB files if they are fully checkpointed, keeping the system lightweight.

## 7. Troubleshooting

*   **Database Connection Error**: Check `POSTGRES_CONNECTION_STRING` in `.env` and ensure PostgreSQL service is active.
*   **MT5 Not Found**: Ensure you are on Windows and MT5 is installed. On Mac, you can only run the Server and Dashboard.
*   **Missing Dependencies**: Re-run `pip install -r requirements.txt`.

