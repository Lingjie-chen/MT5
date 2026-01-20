#!/bin/bash
# One-Click Start for Auto Sync Engine (Mac/Linux)

# Ensure we are in the project root
# Because this script is in "说明使用", we need to go up one level to project root
cd "$(dirname "$0")/.."

# Add current directory to PYTHONPATH so python can find modules
export PYTHONPATH=$PYTHONPATH:$(pwd)

echo "🚀 Starting Auto Sync Engine..."
echo "Logs will be written to auto_sync_engine.log"

# Check if PostgreSQL service is running (optional, basic check)
# Assuming typical port 5432
if ! nc -z localhost 5432 2>/dev/null; then
    echo "⚠️  Warning: PostgreSQL does not seem to be listening on port 5432."
    echo "    Please ensure your remote DB tunnel or local DB is active."
fi

# Run the engine
python3 scripts/checkpoint_dbs.py