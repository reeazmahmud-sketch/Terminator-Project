#!/bin/bash
# Stop Intelligent Disk Cleanup Agent

PID_FILE="$HOME/Desktop/Terminator-Project/.logs/disk_cleanup.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "❌ Disk Cleanup is not running"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p "$PID" > /dev/null 2>&1; then
    kill "$PID"
    rm "$PID_FILE"
    echo "✅ Disk Cleanup stopped (PID: $PID)"
else
    echo "⚠️ Disk Cleanup not running (removed stale PID file)"
    rm "$PID_FILE"
fi
