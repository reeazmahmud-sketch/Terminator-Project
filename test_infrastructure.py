#!/usr/bin/env python3
"""
Test the infrastructure agents and log today's work.
"""

import sys
sys.path.insert(0, 'core')

from terminator_infrastructure_coordinator import start_infrastructure
from terminator_claude_activity_logger import log_created
from terminator_change_propagation_system import log_agent_change
import time

print("=" * 60)
print("TESTING INFRASTRUCTURE AGENTS")
print("=" * 60 + "\n")

# Start infrastructure
coordinator = start_infrastructure()

print("\n⏳ Letting agents initialize (3 seconds)...\n")
time.sleep(3)

# Log today's work using Claude Activity Logger
print("📝 Logging today's Claude activities...\n")

log_created(
    "core/terminator_claude_activity_logger.py",
    "Created Claude Activity Logger to track all changes",
    "User requested automatic logging of all Claude changes"
)

log_created(
    "core/terminator_file_system_guardian.py",
    "Created File System Guardian for organization and protection",
    "User requested file organization and protection agents"
)

log_created(
    "core/terminator_infrastructure_coordinator.py",
    "Created Infrastructure Coordinator to manage all background agents",
    "User requested centralized agent management"
)

# Log change propagation
print("\n📢 Logging agent updates...\n")

log_agent_change(
    title="Created infrastructure agent system",
    description="""Created comprehensive infrastructure layer with 5 autonomous agents:
1. Claude Activity Logger - Logs every change Claude makes
2. File System Guardian - Organizes files, prevents deletion, syncs to cloud
3. Change Propagation System - Auto-notifies agents of changes
4. Solution Knowledge Base - Prevents redundant work
5. Infinite Loop Guardian - Prevents disk disasters

All agents start automatically with TERMINATOR.""",
    files=[
        "core/terminator_claude_activity_logger.py",
        "core/terminator_file_system_guardian.py",
        "core/terminator_infrastructure_coordinator.py"
    ]
)

print("\n" + "=" * 60)
print("INFRASTRUCTURE TEST COMPLETE")
print("=" * 60 + "\n")

# Show comprehensive report
print(coordinator.get_full_report())

print("\n📁 Check these files:")
print("   • .claude_activity/CLAUDE_ACTIVITY_SUMMARY.md")
print("   • GLOBAL_CHANGES.md")
print("   • AGENT_CHANGES.md")
print("\n")

# Stop infrastructure
coordinator.stop_all()
