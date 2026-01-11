#!/bin/bash

# Set terminal title
echo -e "\033]0;AI Multi-Symbol Trading Bot (Gold/ETH/EUR)\007"

# Switch to script directory
cd "$(dirname "$0")"

# Switch to parent directory (project root)
cd ..

while true; do
    echo "[$(date)] Starting Multi-Symbol AI Trading Bot..."
    echo "---------------------------------------------------"
    echo "Supported Symbols: GOLD, ETHUSD, EURUSD"
    echo "Usage: ./run_bot_watchdog.sh [Symbol1,Symbol2,...]"
    echo "Default: GOLD, ETHUSD, EURUSD"
    echo "---------------------------------------------------"
    
    # Run as module, passing all arguments
    python3 -m gold.start "$@"
    
    echo "---------------------------------------------------"
    echo "[$(date)] Bot crashed or stopped. Restarting in 5 seconds..."
    sleep 5
done
