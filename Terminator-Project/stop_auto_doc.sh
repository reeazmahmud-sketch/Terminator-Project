#!/bin/bash
# Stop Auto-Documentation Updater

PID_FILE="$HOME/Desktop/Terminator-Project/.logs/auto_doc.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "❌ Auto-Doc Updater is not running"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p "$PID" > /dev/null 2>&1; then
    kill "$PID"
    rm "$PID_FILE"
    echo "✅ Auto-Doc Updater stopped (PID: $PID)"
else
    echo "⚠️ Auto-Doc Updater not running (removed stale PID file)"
    rm "$PID_FILE"
fi
