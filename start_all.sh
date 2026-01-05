#!/bin/bash

# TERMINATOR - Launch All Interfaces
# Opens selection menu for all available interfaces

cd "$(dirname "$0")"

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                 TERMINATOR LAUNCH MENU                        ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "Select interface to launch:"
echo ""
echo "  [1] Web Terminal (React UI with Voice)"
echo "  [2] Terminal UI (CLI with Animations)"
echo "  [3] Simple CLI (Minimal)"
echo "  [4] All Interfaces (Background)"
echo ""
read -p "Choice [1-4]: " choice

case $choice in
    1)
        ./start_web_terminal.sh
        ;;
    2)
        ./start_terminal_ui.sh
        ;;
    3)
        ./start_cli.sh
        ;;
    4)
        echo "Launching all interfaces..."
        ./start_web_terminal.sh &
        sleep 2
        echo "Web Terminal: http://localhost:8000"
        echo "Press Ctrl+C to stop all services"
        wait
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
