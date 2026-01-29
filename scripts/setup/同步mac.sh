#!/bin/bash
# One-Click Start for Auto Sync Engine (Mac/Linux)

# Ensure we are in the project root
cd "$(dirname "$0")/../.."

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
echo "   Quant Trading System - Auto Sync Engine"
echo "==================================================="

# 2. Check PostgreSQL and Auto-Start
echo "🐘 Checking PostgreSQL connection..."
if nc -z localhost 5432 2>/dev/null; then
    echo "✅ PostgreSQL is running on port 5432."
else
    echo "⚠️ PostgreSQL is NOT running. Attempting to start service..."
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
        echo "✅ PostgreSQL started successfully."
    else
        echo "❌ ERROR: Failed to auto-start PostgreSQL."
        echo "   Please start your database server manually."
    fi
fi

echo "🚀 Starting Auto Sync Engine..."
echo "Logs will be written to auto_sync_engine.log"

# Auto-resolve Git conflicts
python3 scripts/maintenance/git_auto_resolve.py

# Fix "modify/delete" conflicts
if git status | grep -q "deleted by them"; then
    echo "⚠️ Conflict 'deleted by them' detected. Keeping local files..."
    git add .
    git commit -m "auto: resolve modify/delete conflict"
fi

# Auto-repair Database
python3 scripts/maintenance/db_auto_repair.py

# Merge Archived DBs to Main
echo "📦 Consolidating databases..."
python3 scripts/maintenance/consolidate_dbs.py

# 3. Backup PostgreSQL to GitHub
echo "📦 Backing up PostgreSQL data to GitHub..."
python3 scripts/maintenance/backup_postgres.py

# 4. Clean up duplicate data
echo "🧹 Cleaning up duplicate data..."
python3 scripts/maintenance/clean_backup_data.py
python3 scripts/maintenance/clean_postgres_db.py

# Run the engine
python3 scripts/maintenance/checkpoint_dbs.py
