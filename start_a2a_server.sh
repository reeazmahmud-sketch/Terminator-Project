#!/bin/bash
# Start Terminator A2A (Agent2Agent) Protocol Server
# Enables inter-agent communication with external A2A-compliant agents

echo "🤖 Starting Terminator A2A Protocol Server..."
echo ""

# Check if a2a-sdk is installed
if ! python3 -c "import aiohttp" &>/dev/null; then
    echo "❌ Required dependency 'aiohttp' not found"
    echo "📦 Installing dependencies..."
    pip3 install aiohttp
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
REQUIRED_VERSION="3.13"

if (( $(echo "$PYTHON_VERSION < $REQUIRED_VERSION" | bc -l) )); then
    echo "⚠️  Warning: Python 3.13+ recommended, you have $PYTHON_VERSION"
fi

echo "🚀 Launching A2A Server on port 8001..."
echo ""
echo "📡 Endpoints:"
echo "   • Agent Cards:    http://localhost:8001/a2a/agents"
echo "   • JSON-RPC:       http://localhost:8001/a2a/rpc"
echo "   • Agent Card:     http://localhost:8001/a2a/agents/{name}/card"
echo "   • Discovery:      http://localhost:8001/a2a/discover"
echo ""
echo "💡 Test with:"
echo "   curl http://localhost:8001/a2a/agents"
echo ""
echo "Press Ctrl+C to stop the server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start the server
cd "$(dirname "$0")"
python3 core/terminator_a2a_integration.py
