#!/bin/bash
# Stop Smart Notification System

PID_FILE="$HOME/Desktop/Terminator-Project/.logs/notifications.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "❌ Notification System is not running"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p "$PID" > /dev/null 2>&1; then
    kill "$PID"
    rm "$PID_FILE"
    echo "✅ Notification System stopped (PID: $PID)"
else
    echo "⚠️ Notification System not running (removed stale PID file)"
    rm "$PID_FILE"
fi
