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

## 6. Running the System

The system consists of three main components:

### 6.1 Start Auto-Sync Engine (Recommended)
This engine handles **Git Sync**, **DB Sync**, and **Environment Setup** automatically.

**Windows:**
```cmd
说明使用\同步windons.bat
```
*This script will:*
1.  *Auto-detect and activate virtual environment.*
2.  *Check if PostgreSQL port (5432) is active.*
3.  *Start the background sync engine.*

**Mac/Linux:**
```bash
bash 说明使用/同步mac.sh
```

### 6.2 Trading Bot (Windows Only)
The core logic that interacts with MT5.

```cmd
python gold/start.py
```
*Ensure MT5 terminal is running and "Algo Trading" is enabled.*

### 6.3 Analysis Dashboard (Streamlit)
Visual interface for monitoring performance.

```bash
streamlit run dashboard.py
```

## 7. Maintenance & Sync

### 7.1 Auto-Sync & System Startup
The `同步windons.bat` (Windows) or `同步mac.sh` (Mac) scripts handle everything:
1.  **Git Auto-Sync**: Automatically pulls updates and pushes changes every 60s.
2.  **DB Sync**: Automatically syncs local SQLite data to remote PostgreSQL.

You don't need to run any separate sync scripts.

### 7.2 Local DB Cleanup
The system automatically uploads data to PostgreSQL. Local `.db` files are cache-only. The system will automatically delete local DB files if they are fully checkpointed, keeping the system lightweight.

## 8. Troubleshooting

*   **Database Connection Error**: Check `POSTGRES_CONNECTION_STRING` in `.env` and ensure PostgreSQL service is active.
*   **MT5 Not Found**: Ensure you are on Windows and MT5 is installed. On Mac, you can only run the Server and Dashboard.
*   **Missing Dependencies**: Re-run `pip install -r requirements.txt`.

