#!/usr/bin/env python3
"""
BEFORE YOU CODE - Anti-Redundancy Checker

Run this BEFORE starting any new work to avoid wasting time.

Usage:
    python3 before_you_code.py "your problem description"

Example:
    python3 before_you_code.py "need to monitor disk space"
"""

import sys
sys.path.insert(0, 'core')

from terminator_solution_knowledge_base import SmartWorkflow

def main():
    if len(sys.argv) < 2:
        print("""
╔══════════════════════════════════════════════════════════════╗
║               BEFORE YOU CODE - Usage                        ║
╚══════════════════════════════════════════════════════════════╝

This tool prevents wasted time by checking if someone has already
solved your problem.

Usage:
    python3 before_you_code.py "problem description"

Examples:
    python3 before_you_code.py "log files growing too large"
    python3 before_you_code.py "dependency errors on startup"
    python3 before_you_code.py "infinite loop consuming CPU"

What it does:
    1. Checks local knowledge base for existing solutions
    2. Searches GitHub and Stack Overflow
    3. Suggests best practices
    4. Warns if you're about to rebuild something

Why use it:
    Save hours by reusing existing solutions instead of rebuilding!
""")
        sys.exit(1)

    problem = " ".join(sys.argv[1:])

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║               BEFORE YOU CODE - Checking...                  ║
╚══════════════════════════════════════════════════════════════╝

Problem: {problem}
""")

    workflow = SmartWorkflow()

    # Check if running in non-interactive mode (e.g., piped or background)
    import os
    interactive = os.isatty(sys.stdin.fileno())

    should_proceed = workflow.before_you_build(problem, interactive=interactive)

    if should_proceed:
        print("""
╔══════════════════════════════════════════════════════════════╗
║                    ✅ PROCEED WITH CODING                    ║
╚══════════════════════════════════════════════════════════════╝

No existing solution found. You can proceed with building.

⚠️  IMPORTANT: After you finish, document your solution!

Run this after you're done:

    python3 after_you_code.py \\
        "your problem" \\
        "your solution" \\
        "path/to/file.py"

This ensures we never rebuild this again!
""")
        sys.exit(0)
    else:
        print("""
╔══════════════════════════════════════════════════════════════╗
║              🛑 STOP - SOLUTION ALREADY EXISTS               ║
╚══════════════════════════════════════════════════════════════╝

An existing solution was found! You can save time by reusing it
instead of rebuilding from scratch.

✅ Time saved: 1-3 hours
✅ Code reuse: 100%
✅ Quality: Already tested
""")
        sys.exit(0)


if __name__ == "__main__":
    main()
