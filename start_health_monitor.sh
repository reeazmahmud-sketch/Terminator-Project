#!/bin/bash
# Start Agent Health Monitor in background

AGENT_SCRIPT="$HOME/Desktop/Terminator-Project/core/terminator_agent_health_monitor.py"
LOG_FILE="$HOME/Desktop/Terminator-Project/.logs/health_monitor.log"
PID_FILE="$HOME/Desktop/Terminator-Project/.logs/health_monitor.pid"

# Create logs directory
mkdir -p "$(dirname "$LOG_FILE")"

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ Health Monitor already running (PID: $PID)"
        exit 0
    fi
fi

# Start the monitor
echo "🏥 Starting Agent Health Monitor..."
nohup python3 "$AGENT_SCRIPT" > "$LOG_FILE" 2>&1 &
PID=$!
echo $PID > "$PID_FILE"

sleep 2

# Verify it started
if ps -p "$PID" > /dev/null 2>&1; then
    echo "✅ Health Monitor started (PID: $PID)"
    echo "📋 Log: $LOG_FILE"
    echo "📊 Report: ~/.Desktop/Terminator-Project/.health_checks/agent_health_report.txt"
else
    echo "❌ Failed to start Health Monitor"
    exit 1
fi
