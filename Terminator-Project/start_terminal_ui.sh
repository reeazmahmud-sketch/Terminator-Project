#!/bin/bash

# TERMINATOR - Terminal UI Launcher
# Starts beautiful terminal interface with animations

cd "$(dirname "$0")"

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║        TERMINATOR - Terminal UI with Robot Animations        ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Check dependencies
if ! python3 -c "import textual" &> /dev/null; then
    echo "Installing Textual..."
    pip3 install textual rich
fi

python3 terminator_tui.py
