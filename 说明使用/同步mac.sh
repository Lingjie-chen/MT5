#!/bin/bash
# One-Click Start for Auto Sync Engine (Mac/Linux)

# Ensure we are in the project root
cd "$(dirname "$0")/.."

# 0. Check/Setup Environment
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found! Running setup..."
    bash "说明使用/setup_env.sh"
fi

# 1. Activate Virtual Environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Add current directory to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

echo "==================================================="
echo "   Quant Trading System - Auto Sync Engine"
echo "==================================================="

# 2. Check PostgreSQL
echo "🐘 Checking PostgreSQL connection..."
if nc -z localhost 5432 2>/dev/null; then
    echo "✅ PostgreSQL is running on port 5432."
else
    echo "❌ ERROR: PostgreSQL is NOT running on port 5432."
    echo "   Please start your database server and try again."
    echo "   (If using a remote DB, ensure the tunnel is active at localhost:5432)"
fi

echo "🚀 Starting Auto Sync Engine..."
echo "Logs will be written to auto_sync_engine.log"

# Run the engine
python3 scripts/checkpoint_dbs.py
