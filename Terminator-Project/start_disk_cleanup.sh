#!/bin/bash
# Start Intelligent Disk Cleanup Agent in background

AGENT_SCRIPT="$HOME/Desktop/Terminator-Project/core/terminator_intelligent_disk_cleanup.py"
LOG_FILE="$HOME/Desktop/Terminator-Project/.logs/disk_cleanup.log"
PID_FILE="$HOME/Desktop/Terminator-Project/.logs/disk_cleanup.pid"

# Create directories
mkdir -p "$(dirname "$LOG_FILE")"

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ Disk Cleanup already running (PID: $PID)"
        exit 0
    fi
fi

# Start the agent
echo "🧹 Starting Intelligent Disk Cleanup Agent..."
nohup python3 "$AGENT_SCRIPT" > "$LOG_FILE" 2>&1 &
PID=$!
echo $PID > "$PID_FILE"

sleep 2

# Verify it started
if ps -p "$PID" > /dev/null 2>&1; then
    echo "✅ Disk Cleanup started (PID: $PID)"
    echo "📋 Log: $LOG_FILE"
    echo "📊 Report: ~/Desktop/Terminator-Project/.cleanup/cleanup_report.json"
    echo "⏰ Check interval: Every 5 minutes"
else
    echo "❌ Failed to start Disk Cleanup"
    exit 1
fi
