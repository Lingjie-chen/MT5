#!/bin/bash
# One-Click Start for Auto Sync Engine (Mac/Linux)

# Ensure we are in the project root
cd "$(dirname "$0")/../.." || exit 1

# 0. Check/Setup Environment
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found! Running setup..."
    bash "scripts/setup/setup_env.sh"
fi

# 1. Activate Virtual Environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Add current directory to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# --- Fix Git State (Auto-Unlock) ---
if [ -f ".git/index.lock" ]; then
    echo "🗑️ Removing stale .git/index.lock..."
    rm -f .git/index.lock
fi
# -----------------------------------

echo "==================================================="
echo "   Quant Trading System Startup"
echo "==================================================="

# 2. Check PostgreSQL and Auto-Start
echo "🐘 Checking PostgreSQL connection..."
if nc -z localhost 5432 2>/dev/null; then
    echo -e "\033[32m✅ PostgreSQL is running on port 5432.\033[0m"
else
    echo -e "\033[33m⚠️  PostgreSQL is NOT running. Attempting to start service...\033[0m"
    # Try common start commands (Homebrew, systemctl, pg_ctl)
    if command -v brew &> /dev/null; then
        brew services start postgresql
    elif command -v systemctl &> /dev/null; then
        sudo systemctl start postgresql
    elif command -v pg_ctl &> /dev/null; then
        pg_ctl -D /usr/local/var/postgres start
    fi
    
    sleep 5
    
    if nc -z localhost 5432 2>/dev/null; then
        echo -e "\033[32m✅ PostgreSQL started successfully.\033[0m"
    else
        echo -e "\033[31m❌ ERROR: Failed to auto-start PostgreSQL.\033[0m"
        echo "   Please start your database server manually."
    fi
fi

echo ""
echo "[1/2] Starting API Server..."
# Launch API server in a new terminal window
osascript -e 'tell app "Terminal" to do script "cd \"'$(pwd)'\" && source venv/bin/activate && python -m uvicorn src.trading_bot.server.main:app --host 0.0.0.0 --port 8000 --reload"'

echo "[2/2] Starting Auto Sync Engine..."
echo "Logs will be written to auto_sync_engine.log"

# Auto-resolve Git conflicts
python scripts/maintenance/git_auto_resolve.py

# Fix "modify/delete" conflicts
if git status | grep -q "deleted by them"; then
    echo "⚠️ Conflict 'deleted by them' detected. Keeping local files..."
    git add .
    git commit -m "auto: resolve modify/delete conflict"
fi

# Auto-repair Database
python scripts/maintenance/db_auto_repair.py

# Merge Archived DBs to Main
echo "📦 Consolidating databases..."
python scripts/maintenance/consolidate_dbs.py

# 3. Backup PostgreSQL to GitHub
echo "📦 Backing up PostgreSQL data to GitHub..."
python scripts/maintenance/backup_postgres.py

# 4. Clean up duplicate data
echo "🧹 Cleaning up duplicate data..."
python scripts/maintenance/clean_backup_data.py
python scripts/maintenance/clean_postgres_db.py

# Run the engine (Enable Safe Cleanup by default)
# Wrap in a loop to support auto-restart by FileWatcher
while true; do
    echo "🔄 Starting Checkpoint Engine..."
    python scripts/maintenance/checkpoint_dbs.py --cleanup
    echo "⚠️ Engine stopped. Restarting in 3 seconds..."
    sleep 3
done
