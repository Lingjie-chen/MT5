#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Project root is one level up
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Starting Strategy Servers..."

# Function to launch a new terminal window running the strategy
launch_strategy() {
    local strategy=$1
    local title="Strategy - $strategy"
    
    echo "Launching $strategy Strategy..."
    
    # AppleScript to open a new terminal window and run the command
    osascript <<EOF
tell application "Terminal"
    do script "cd '$PROJECT_ROOT'; echo -n -e '\\033]0;$title\\007'; while true; do echo '[$(date)] Starting $strategy Bot...'; python -m gold.start $strategy; echo; echo '[$(date)] Bot Stopped/Crashed! Restarting in 5s...'; sleep 5; done"
    activate
end tell
EOF
}

launch_strategy "GOLD"
sleep 1
launch_strategy "ETHUSD"
sleep 1
launch_strategy "EURUSD"

echo ""
echo "========================================================"
echo " All 3 strategies have been launched in separate windows."
echo " The strategy windows will stay open and auto-restart."
echo "========================================================"
