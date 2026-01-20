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

### 6.1 Start System (One-Click)
We have combined the Data Server and Auto-Sync service into a single script.

**Windows:**
```cmd
start_system.bat
```
*This will:*
1.  *Activate the virtual environment.*
2.  *Migrate any existing local SQLite data to PostgreSQL.*
3.  *Start the **Data Server** (FastAPI) for real-time data ingestion.*
4.  *Launch a background service to periodically **checkpoint** local DBs and **clean them up** once data is safely uploaded.*

**Mac/Linux:**
```bash
./start_data_server.sh
```
*(Currently, Mac/Linux users should run the server script and sync script separately if needed, or use the provided shell script which handles the server part.)*

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
The `start_system.bat` (Windows) script handles everything:
1.  Starts the Data Server.
2.  Runs a background service for:
    *   **Git Auto-Sync**: Automatically pulls updates and pushes changes every 60s.
    *   **DB Cleanup**: Automatically cleans local .db files once uploaded.

You don't need to run any separate sync scripts.

### 7.2 Local DB Cleanup
The system automatically uploads data to PostgreSQL. Local `.db` files are cache-only. The system will automatically delete local DB files if they are fully checkpointed, keeping the system lightweight.

## 8. Troubleshooting

*   **Database Connection Error**: Check `POSTGRES_CONNECTION_STRING` in `.env` and ensure PostgreSQL service is active.
*   **MT5 Not Found**: Ensure you are on Windows and MT5 is installed. On Mac, you can only run the Server and Dashboard.
*   **Missing Dependencies**: Re-run `pip install -r requirements.txt`.

