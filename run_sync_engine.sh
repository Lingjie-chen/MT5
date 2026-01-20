#!/bin/bash
# One-Click Start for Auto Sync Engine (Mac/Linux)

# Ensure we are in the project root
cd "$(dirname "$0")"

# Add current directory to PYTHONPATH so python can find modules
export PYTHONPATH=$PYTHONPATH:$(pwd)

echo "🚀 Starting Auto Sync Engine..."
echo "Logs will be written to auto_sync_engine.log"

# Run the engine
python3 scripts/checkpoint_dbs.py