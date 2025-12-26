#!/bin/bash

# TERMINATOR - Web Terminal Launcher
# Starts WebSocket bridge and serves React web terminal

cd "$(dirname "$0")"

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║           TERMINATOR - Web Terminal with Voice AI            ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Build React app if not built
if [ ! -d "terminator-web-terminal/dist" ]; then
    echo "Building React web terminal..."
    cd terminator-web-terminal
    npm install
    npm run build
    cd ..
fi

echo "Starting WebSocket Bridge on http://0.0.0.0:8000"
echo ""
echo "Access the web terminal at:"
echo "  → http://localhost:8000"
echo "  → http://$(ipconfig getifaddr en0):8000 (from other devices)"
echo ""

# Start bridge
python3 terminator_bridge.py
