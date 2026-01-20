#!/bin/bash

# Ensure we are in the project root
cd "$(dirname "$0")/.." || exit 1

echo "🚀 Starting Data Server (FastAPI)..."
echo "📡 This server enables real-time data sync to PostgreSQL."

# Check environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run './setup_env.sh' first."
    exit 1
fi

# Activate venv
source venv/bin/activate

# Optional: Auto Migrate SQLite to Postgres on startup
echo "🔄 Checking for local data to migrate..."
python migrate_sqlite_to_postgres.py

# Start Server
echo "🟢 Starting Uvicorn Server on http://0.0.0.0:8000..."
echo "(Press Ctrl+C to stop)"
uvicorn gold.server.main:app --host 0.0.0.0 --port 8000 --reload
