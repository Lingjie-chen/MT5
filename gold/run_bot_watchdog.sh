#!/bin/bash

# Set terminal title
echo -e "\033]0;AI Gold Trading Bot Watchdog\007"

# Switch to script directory
cd "$(dirname "$0")"

# Switch to parent directory (project root)
cd ..

while true; do
    echo "[$(date)] Starting Gold Trading Bot..."
    echo "---------------------------------------------------"
    
    # Run as module, passing all arguments
    python3 -m gold.start "$@"
    
    echo "---------------------------------------------------"
    echo "[$(date)] Bot crashed or stopped. Restarting in 5 seconds..."
    sleep 5
done
