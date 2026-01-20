#!/bin/bash

# Ensure we are in the project root
cd "$(dirname "$0")/.." || exit 1

echo "🚀 Starting Quant Trading System..."
echo "==================================================="

# 1. Environment Check
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run './setup_env.sh' first."
    exit 1
fi

# 2. Activate Virtual Environment
echo "🟢 Activating virtual environment..."
source venv/bin/activate

# 2.5 Fix Git State (Auto-Commit & Lock Removal)
echo "🛠️ Ensuring clean Git state..."
# Kill any stale git processes that might be locking files
if pgrep git > /dev/null; then
    pkill git
fi
# Remove lock file if it exists
if [ -f ".git/index.lock" ]; then
    echo "🗑️ Removing stale .git/index.lock..."
    rm -f .git/index.lock
fi
# Auto-commit to prevent overwrite errors
echo "💾 Auto-saving local DB changes..."
git add gold/trading_data.db
git commit -m "Auto-save trading_data.db on startup" || echo "Nothing to commit"

# Ensure dependencies are installed (Fix for ModuleNotFoundError)
echo "📦 Checking critical dependencies..."
pip install sqlalchemy psycopg2-binary

# 3. Auto Data Migration
echo "🔄 Checking for local SQLite data to migrate..."
python migrate_sqlite_to_postgres.py

# 4. Start Background Sync Service
echo "🔄 Starting Background Sync Service (with Safe Cleanup)..."
# Run in background with nohup, redirect output to log
nohup python scripts/checkpoint_dbs.py --loop --cleanup --interval 60 > sync_service.log 2>&1 &
SYNC_PID=$!
echo "   (Background Service PID: $SYNC_PID)"

# 5. Start Data Server
echo "🟢 Starting Data Server (FastAPI)..."
echo "📡 This server enables real-time data sync to PostgreSQL."
echo "(Press Ctrl+C to stop)"
echo ""

# Trap Ctrl+C to kill background process when server stops
cleanup() {
    echo ""
    echo "🛑 Stopping Background Sync Service..."
    kill $SYNC_PID
    exit
}
trap cleanup SIGINT

uvicorn gold.server.main:app --host 0.0.0.0 --port 8000 --reload
