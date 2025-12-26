#!/bin/bash
##
# TERMINATOR Multi-Agent Demo Launcher
# Runs the real-life scenario demonstration
##

echo "🎬 Starting TERMINATOR Multi-Agent Demo Scenario..."
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "   Please install Python 3 and try again."
    exit 1
fi

# Create reports directory if it doesn't exist
mkdir -p reports

echo "✅ Ready to start demo"
echo ""

# Run the demo
python3 demo_multi_agent_scenario.py

echo ""
echo "🎉 Demo complete!"
