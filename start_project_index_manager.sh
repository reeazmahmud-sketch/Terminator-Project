#!/bin/bash
# Start Project Index Manager Agent in background

AGENT_SCRIPT="$HOME/Desktop/Terminator-Project/core/terminator_project_index_manager.py"
LOG_FILE="$HOME/Desktop/Terminator-Project/.logs/project_index_manager.log"
PID_FILE="$HOME/Desktop/Terminator-Project/.logs/project_index_manager.pid"

# Create logs directory if needed
mkdir -p "$(dirname "$LOG_FILE")"

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ Project Index Manager already running (PID: $PID)"
        exit 0
    fi
fi

# Start the agent in background
echo "🚀 Starting Project Index Manager Agent..."
nohup python3 "$AGENT_SCRIPT" > "$LOG_FILE" 2>&1 &
PID=$!
echo $PID > "$PID_FILE"

sleep 1

# Verify it started
if ps -p "$PID" > /dev/null 2>&1; then
    echo "✅ Project Index Manager started (PID: $PID)"
    echo "📋 Log file: $LOG_FILE"
    echo "🔍 Monitoring ~/Desktop for new projects every 5 minutes"
else
    echo "❌ Failed to start Project Index Manager"
    exit 1
fi
