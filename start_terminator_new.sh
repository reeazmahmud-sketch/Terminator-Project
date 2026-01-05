#!/bin/bash
# TERMINATOR New Architecture Launcher
# =====================================
# Uses the proper module-based agent system

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║           TERMINATOR - NEW ARCHITECTURE                   ║"
echo "╠═══════════════════════════════════════════════════════════╣"
echo "║  • Unified LLM Router (Gemini/Claude/OpenAI/Grok/Ollama)  ║"
echo "║  • Module-based Agent System                              ║"
echo "║  • Auto-Solution Coding Agent                             ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check for required packages
python3 -c "import rich" 2>/dev/null || {
    echo "Installing rich library..."
    pip3 install rich
}

python3 -c "import httpx" 2>/dev/null || {
    echo "Installing httpx library..."
    pip3 install httpx
}

# Run the new terminator
python3 "$SCRIPT_DIR/terminator_new.py" "$@"
