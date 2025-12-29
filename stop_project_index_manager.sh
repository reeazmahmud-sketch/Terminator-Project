#!/bin/bash
# Stop Project Index Manager Agent

PID_FILE="$HOME/Desktop/Terminator-Project/.logs/project_index_manager.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "❌ Project Index Manager is not running (no PID file)"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p "$PID" > /dev/null 2>&1; then
    kill "$PID"
    rm "$PID_FILE"
    echo "✅ Project Index Manager stopped (PID: $PID)"
else
    echo "⚠️ Project Index Manager not running (stale PID file removed)"
    rm "$PID_FILE"
fi
