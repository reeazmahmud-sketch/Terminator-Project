#!/bin/bash
# Claude Guard - Auto-fix config errors before launching Claude Code
#
# Usage: ./claude-guard.sh [claude arguments...]
# Install: Add alias to .zshrc: alias claude='~/Desktop/Terminator-Project/claude-guard.sh'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GUARDIAN="$SCRIPT_DIR/core/terminator_claude_config_guardian.py"

# Run guardian silently (only shows if errors found and fixed)
if [ -f "$GUARDIAN" ]; then
    python3 "$GUARDIAN" --quiet 2>/dev/null

    # Check exit code
    if [ $? -ne 0 ]; then
        echo "⚠️  Claude Config Guardian detected and attempted fixes"
        echo "   Re-run if issues persist"
        echo ""
    fi
fi

# Launch Claude with all passed arguments
exec claude "$@"
