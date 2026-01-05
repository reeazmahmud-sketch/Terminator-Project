#!/bin/bash
##
# TERMINATOR Command Center Launcher
# Starts the interactive multi-agent control interface
##

echo "🤖 Starting TERMINATOR Command Center..."
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "   Please install Python 3 and try again."
    exit 1
fi

# Check if required dependencies are installed
echo "Checking dependencies..."

python3 -c "import asyncio" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Installing required dependencies..."
    pip3 install -r requirements.txt
fi

echo "✅ Dependencies OK"
echo ""

# Run the command center
python3 terminator_command_center.py

echo ""
echo "👋 Command Center closed"
