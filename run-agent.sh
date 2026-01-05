#!/bin/bash
# TERMINATOR Agentic System Launcher
#
# Usage:
#   ./run-agent.sh "Your goal here"
#   ./run-agent.sh --backend ollama "Analyze project"
#   ./run-agent.sh --backend claude "Build REST API"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate venv if exists
if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
fi

# Run the agentic system
python3 "$SCRIPT_DIR/core/terminator_agentic_system.py" "$@"
