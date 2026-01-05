#!/usr/bin/env python3
"""
AFTER YOU CODE - Solution Documentation

Run this AFTER building a solution to document it forever.

Usage:
    python3 after_you_code.py "problem" "solution" [file_path]

Example:
    python3 after_you_code.py \\
        "log files too large" \\
        "created guardian agent to monitor and truncate" \\
        "core/guardian_agent.py"
"""

import sys
sys.path.insert(0, 'core')

from terminator_solution_knowledge_base import document_fix

def main():
    if len(sys.argv) < 3:
        print("""
╔══════════════════════════════════════════════════════════════╗
║              AFTER YOU CODE - Usage                          ║
╚══════════════════════════════════════════════════════════════╝

This tool documents your solution so you never rebuild it again.

Usage:
    python3 after_you_code.py "problem" "solution" [file_path]

Required:
    problem     - What problem did you solve?
    solution    - How did you solve it?

Optional:
    file_path   - Path to the file you created/modified

Examples:

    python3 after_you_code.py \\
        "disk space running out" \\
        "created monitoring agent that cleans old logs"

    python3 after_you_code.py \\
        "dependency errors on startup" \\
        "added pre-flight check system" \\
        "core/preflight_system.py"

Why document:
    • Never rebuild the same solution twice
    • Share knowledge with other developers
    • Build a searchable knowledge base
    • Track solution quality over time
""")
        sys.exit(1)

    problem = sys.argv[1]
    solution = sys.argv[2]
    file_path = sys.argv[3] if len(sys.argv) > 3 else None

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║            AFTER YOU CODE - Documenting...                   ║
╚══════════════════════════════════════════════════════════════╝

Problem:  {problem}
Solution: {solution}
File:     {file_path or 'N/A'}
""")

    document_fix(
        problem=problem,
        solution=solution,
        file=file_path
    )

    print("""
╔══════════════════════════════════════════════════════════════╗
║                  ✅ SOLUTION DOCUMENTED                      ║
╚══════════════════════════════════════════════════════════════╝

Your solution has been saved to the knowledge base!

Benefits:
    ✅ Searchable forever
    ✅ Will warn if someone tries to rebuild this
    ✅ Can be reused by other developers
    ✅ Tracked for quality metrics

Next time someone has this problem, they'll see:
    "WAIT! We've solved this before!"
    And they'll reuse your solution.

Time saved for future: 1-3 hours per reuse! 🎉
""")

if __name__ == "__main__":
    main()
