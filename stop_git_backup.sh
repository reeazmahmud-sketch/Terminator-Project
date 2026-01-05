#!/bin/bash
# Stop Auto-Git Backup Agent

PID_FILE="$HOME/Desktop/Terminator-Project/.logs/git_backup.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "❌ Auto-Git Backup is not running"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p "$PID" > /dev/null 2>&1; then
    kill "$PID"
    rm "$PID_FILE"
    echo "✅ Auto-Git Backup stopped (PID: $PID)"
else
    echo "⚠️ Auto-Git Backup not running (removed stale PID file)"
    rm "$PID_FILE"
fi
