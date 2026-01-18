#!/bin/bash
set -e

# Start Virtual Display (Xvfb)
echo "[Docker] Starting Xvfb..."
Xvfb :1 -screen 0 1024x768x16 &
sleep 2

# Start Window Manager (Fluxbox)
echo "[Docker] Starting Fluxbox..."
fluxbox &
sleep 1

# Start VNC Server (no password)
echo "[Docker] Starting VNC Server on port 5900..."
x11vnc -display :1 -forever -nopw -quiet &

# Check if MT5 is installed
MT5_PATH="$HOME/.wine/drive_c/Program Files/MetaTrader 5/terminal64.exe"

if [ ! -f "$MT5_PATH" ]; then
    echo "[Docker] MetaTrader 5 not found. Starting Installer..."
    echo "[Docker] IMPORTANT: Connect via VNC (localhost:5900) to complete the installation wizard!"
    
    # Run installer
    wine /tmp/mt5setup.exe
    
    echo "[Docker] Waiting for installation to complete..."
    wineserver -w
    
    if [ ! -f "$MT5_PATH" ]; then
        echo "[Docker] ERROR: Installation failed or was cancelled."
        exit 1
    fi
    echo "[Docker] Installation completed."
fi

# Execute the command passed to docker run
echo "[Docker] Running command: $@"
# Use 'wine' to run the command (assuming it's a python command or windows executable)
# If the command starts with 'python', we prepend 'wine'
if [[ "$1" == "python" ]]; then
    shift
    wine python "$@"
else
    # Run generic command
    exec "$@"
fi
