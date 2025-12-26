#!/bin/bash

# TERMINATOR - Smart Startup with Pre-Flight Checks
# This script runs pre-flight checks first, auto-fixes issues,
# and only starts Terminator when everything is perfect (green signal).

cd "$(dirname "$0")"

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║            TERMINATOR INTELLIGENT STARTUP SYSTEM              ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Run pre-flight checks
echo "🛫 Running pre-flight checks..."
echo ""

python3 core/terminator_preflight_system.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🚀 Starting TERMINATOR..."
    echo ""

    # Start ALL infrastructure agents
    python3 core/terminator_infrastructure_coordinator.py > /dev/null 2>&1 &
    INFRA_PID=$!
    echo "🏗️  Infrastructure Agents Started (PID: $INFRA_PID)"
    echo "   • Claude Activity Logger"
    echo "   • File System Guardian"
    echo "   • Change Propagation System"
    echo "   • Solution Knowledge Base"
    echo "   • Infinite Loop Guardian"

    # Choose interface
    echo ""
    echo "Select interface:"
    echo "  [1] Web Terminal"
    echo "  [2] Terminal UI"
    echo "  [3] Simple CLI"
    echo ""
    read -p "Choice [1-3]: " choice

    case $choice in
        1)
            ./start_web_terminal.sh
            ;;
        2)
            python3 terminator_tui.py
            ;;
        3)
            python3 terminator.py
            ;;
        *)
            echo "Invalid choice"
            kill $GUARDIAN_PID 2>/dev/null
            exit 1
            ;;
    esac

    # Cleanup guardian on exit
    kill $GUARDIAN_PID 2>/dev/null

else
    echo ""
    echo "🔴 System not ready. Pre-flight checks failed."
    echo "   Issues were detected that could not be auto-fixed."
    echo "   Please check the error messages above."
    echo ""
    exit 1
fi
