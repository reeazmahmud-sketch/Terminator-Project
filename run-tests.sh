#!/bin/bash
# TERMINATOR Test Runner - Quick test execution
#
# Usage:
#   ./run-tests.sh              # Auto-detect and run all tests
#   ./run-tests.sh --coverage   # With coverage
#   ./run-tests.sh -t test_auth # Specific test pattern
#   ./run-tests.sh --json       # JSON output for CI

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python3 "$SCRIPT_DIR/core/terminator_test_runner_agent.py" "$@"
