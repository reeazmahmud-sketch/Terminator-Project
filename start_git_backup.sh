#!/bin/bash
# Start Auto-Git Backup Agent in background

AGENT_SCRIPT="$HOME/Desktop/Terminator-Project/core/terminator_auto_git_backup.py"
LOG_FILE="$HOME/Desktop/Terminator-Project/.logs/git_backup.log"
PID_FILE="$HOME/Desktop/Terminator-Project/.logs/git_backup.pid"

# Create directories
mkdir -p "$(dirname "$LOG_FILE")"

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ Auto-Git Backup already running (PID: $PID)"
        exit 0
    fi
fi

# Start the agent
echo "🔄 Starting Auto-Git Backup Agent..."
nohup python3 "$AGENT_SCRIPT" > "$LOG_FILE" 2>&1 &
PID=$!
echo $PID > "$PID_FILE"

sleep 2

# Verify it started
if ps -p "$PID" > /dev/null 2>&1; then
    echo "✅ Auto-Git Backup started (PID: $PID)"
    echo "📋 Log: $LOG_FILE"
    echo "📊 Report: ~/Desktop/Terminator-Project/.backups/backup_report.json"
    echo "⏰ Backup interval: Every 1 hour"
else
    echo "❌ Failed to start Auto-Git Backup"
    exit 1
fi
