#!/bin/bash
# Run TERMINATOR Real-World Test Suite
#
# Usage:
#   ./run-real-world-tests.sh          # Quick test (5 scenarios)
#   ./run-real-world-tests.sh --full   # Full suite (30+ scenarios)
#   ./run-real-world-tests.sh --help   # Show help

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case "$1" in
    --full)
        echo "🚀 Running FULL test suite (30+ scenarios)..."
        python3 "$SCRIPT_DIR/tests/real_world_scenarios.py"
        ;;
    --help)
        echo "TERMINATOR Real-World Test Suite"
        echo ""
        echo "Usage:"
        echo "  ./run-real-world-tests.sh          # Quick test (5 scenarios)"
        echo "  ./run-real-world-tests.sh --full   # Full suite (30+ scenarios)"
        echo "  ./run-real-world-tests.sh --help   # Show this help"
        echo ""
        echo "See tests/README_TESTING.md for more information"
        ;;
    *)
        echo "🚀 Running QUICK tests (5 scenarios)..."
        python3 "$SCRIPT_DIR/tests/scenario_executor.py"
        ;;
esac
