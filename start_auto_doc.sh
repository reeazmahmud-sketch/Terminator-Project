#!/bin/bash
# Start Auto-Documentation Updater in background

AGENT_SCRIPT="$HOME/Desktop/Terminator-Project/core/terminator_auto_doc_updater.py"
LOG_FILE="$HOME/Desktop/Terminator-Project/.logs/auto_doc.log"
PID_FILE="$HOME/Desktop/Terminator-Project/.logs/auto_doc.pid"

# Create directories
mkdir -p "$(dirname "$LOG_FILE")"

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ Auto-Doc Updater already running (PID: $PID)"
        exit 0
    fi
fi

# Start the agent
echo "📝 Starting Auto-Documentation Updater..."
nohup python3 "$AGENT_SCRIPT" > "$LOG_FILE" 2>&1 &
PID=$!
echo $PID > "$PID_FILE"

sleep 2

# Verify it started
if ps -p "$PID" > /dev/null 2>&1; then
    echo "✅ Auto-Doc Updater started (PID: $PID)"
    echo "📋 Log: $LOG_FILE"
    echo "⚙️  Config: ~/Desktop/Terminator-Project/.autodoc/config.json"
    echo "⏰ Check interval: Every 10 minutes"
else
    echo "❌ Failed to start Auto-Doc Updater"
    exit 1
fi
