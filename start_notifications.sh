#!/bin/bash
# Start Smart Notification System in background

AGENT_SCRIPT="$HOME/Desktop/Terminator-Project/core/terminator_smart_notifications.py"
LOG_FILE="$HOME/Desktop/Terminator-Project/.logs/notifications.log"
PID_FILE="$HOME/Desktop/Terminator-Project/.logs/notifications.pid"

# Create directories
mkdir -p "$(dirname "$LOG_FILE")"

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ Notification System already running (PID: $PID)"
        exit 0
    fi
fi

# Start the agent
echo "📬 Starting Smart Notification System..."
nohup python3 "$AGENT_SCRIPT" > "$LOG_FILE" 2>&1 &
PID=$!
echo $PID > "$PID_FILE"

sleep 2

# Verify it started
if ps -p "$PID" > /dev/null 2>&1; then
    echo "✅ Notification System started (PID: $PID)"
    echo "📋 Log: $LOG_FILE"
    echo "⚙️  Config: ~/Desktop/Terminator-Project/.notifications/config.json"
    echo "⏰ Check interval: Every 30 seconds"
else
    echo "❌ Failed to start Notification System"
    exit 1
fi
