#!/bin/bash
# Stop Agent Health Monitor

PID_FILE="$HOME/Desktop/Terminator-Project/.logs/health_monitor.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "❌ Health Monitor is not running"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p "$PID" > /dev/null 2>&1; then
    kill "$PID"
    rm "$PID_FILE"
    echo "✅ Health Monitor stopped (PID: $PID)"
else
    echo "⚠️ Health Monitor not running (removed stale PID file)"
    rm "$PID_FILE"
fi
