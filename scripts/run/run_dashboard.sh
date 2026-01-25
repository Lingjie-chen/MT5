#!/bin/bash

# Set terminal title
echo -e "\033]0;AI Trading Dashboard\007"

# Switch to script directory
cd "$(dirname "$0")"

# Switch to parent directory (project root)
cd ../..

echo "[$(date)] Starting AI Trading Dashboard..."
echo "---------------------------------------------------"
echo "Access the dashboard at http://localhost:8501"
echo "---------------------------------------------------"

while true; do
    # Run Streamlit
    # Using python -m streamlit to ensure we use the module installed in the current python environment
    python3 -m streamlit run dashboard.py --server.port 8501 --server.address localhost --server.headless true

    # If Streamlit exits, restart it
    echo "[$(date)] Dashboard process ended. Restarting in 5 seconds..."
    sleep 5
done
