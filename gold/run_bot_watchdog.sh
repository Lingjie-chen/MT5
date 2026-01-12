#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

while true; do
    echo "[$(date)] Starting Multi-Symbol AI Trading Bot..."
    echo "---------------------------------------------------"
    echo "Supported Symbols: GOLD, ETHUSD, EURUSD"
    echo "Usage: ./run_bot_watchdog.sh [Symbol1] [Symbol2] ..."
    echo "---------------------------------------------------"
    
    python -m gold.start "$@"
    
    echo "---------------------------------------------------"
    echo "[$(date)] Bot crashed or stopped. Restarting in 5 seconds..."
    sleep 5
done
