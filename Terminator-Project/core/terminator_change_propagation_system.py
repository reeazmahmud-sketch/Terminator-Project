#!/usr/bin/env python3

# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Change Propagation & Auto-Documentation System
========================================================

Automatically propagates changes to relevant agents and updates documentation.

When you fix something:
1. Change is logged automatically
2. Relevant agents are notified
3. Documentation is auto-updated
4. Global files are synchronized

Examples:
- Terminal fix → Terminal agents notified
- Disk fix → macOS agents notified
- Agent fix → All agents notified

Created: December 17, 2025
Purpose: Automatic change propagation and documentation
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from core.terminator_agent_communication_bus import get_communication_bus, MessageType, MessagePriority
    HAS_BUS = True
except ImportError:
    HAS_BUS = False


# ============================================================================
# Change Types and Domains
# ============================================================================

class ChangeDomain(Enum):
    """Domain of the change"""
    TERMINAL = "terminal"
    DISK = "disk"
    MACOS = "macos"
    AGENT = "agent"
    NETWORK = "network"
    SECURITY = "security"
    PERFORMANCE = "performance"
    GENERAL = "general"


class ChangeType(Enum):
    """Type of change"""
    FIX = "fix"
    FEATURE = "feature"
    OPTIMIZATION = "optimization"
    DOCUMENTATION = "documentation"
    AGENT_UPDATE = "agent_update"


@dataclass
class Change:
    """A change that was made"""
    change_id: str
    timestamp: str
    domain: ChangeDomain
    change_type: ChangeType
    title: str
    description: str
    affected_files: List[str]
    affected_agents: List[str]
    created_by: str = "Claude"
    propagated: bool = False
    documented: bool = False


# ============================================================================
# Change Propagation System
# ============================================================================

class ChangePropagationSystem:
    """
    Automatically propagates changes to relevant agents and updates documentation.
    """

    def __init__(self):
        """Initialize change propagation system"""
        self.project_root = Path("/Users/reeazmahmud/Desktop/Terminator-Project")
        self.changes_dir = self.project_root / ".changes"
        self.changes_dir.mkdir(exist_ok=True)

        # Files
        self.changelog_file = self.changes_dir / "CHANGELOG.json"
        self.global_doc_file = self.project_root / "GLOBAL_CHANGES.md"
        self.agent_updates_file = self.changes_dir / "agent_updates.json"

        # State
        self.changes: List[Change] = []
        self.agent_subscriptions: Dict[str, List[ChangeDomain]] = {}

        # Communication bus
        self.bus = get_communication_bus() if HAS_BUS else None

        self._load_changes()
        self._initialize_agent_subscriptions()

    def _load_changes(self) -> None:
        """Load existing changes"""
        if self.changelog_file.exists():
            try:
                with open(self.changelog_file, 'r') as f:
                    data = json.load(f)
                    for change_dict in data:
                        change = Change(
                            change_id=change_dict['change_id'],
                            timestamp=change_dict['timestamp'],
                            domain=ChangeDomain(change_dict['domain']),
                            change_type=ChangeType(change_dict['change_type']),
                            title=change_dict['title'],
                            description=change_dict['description'],
                            affected_files=change_dict.get('affected_files', []),
                            affected_agents=change_dict.get('affected_agents', []),
                            created_by=change_dict.get('created_by', 'Claude'),
                            propagated=change_dict.get('propagated', False),
                            documented=change_dict.get('documented', False)
                        )
                        self.changes.append(change)
            except Exception as e:
                print(f"⚠️  Could not load changes: {e}")

    def _save_changes(self) -> None:
        """Save changes to file"""
        try:
            with open(self.changelog_file, 'w') as f:
                json.dump(
                    [self._change_to_dict(c) for c in self.changes],
                    f,
                    indent=2
                )
        except Exception as e:
            print(f"⚠️  Could not save changes: {e}")

    def _change_to_dict(self, change: Change) -> dict:
        """Convert change to dictionary"""
        return {
            **asdict(change),
            'domain': change.domain.value,
            'change_type': change.change_type.value
        }

    def _initialize_agent_subscriptions(self) -> None:
        """Initialize which agents care about which domains"""
        self.agent_subscriptions = {
            # Terminal-related agents
            "terminator_tui": [ChangeDomain.TERMINAL],
            "terminator": [ChangeDomain.TERMINAL],
            "terminator_universal_cli": [ChangeDomain.TERMINAL],

            # Disk/macOS agents
            "terminator_infinite_loop_guardian_agent": [ChangeDomain.DISK, ChangeDomain.MACOS],
            "terminator_resource_manager_agent": [ChangeDomain.DISK, ChangeDomain.MACOS, ChangeDomain.PERFORMANCE],
            "terminator_error_monitor_agent": [ChangeDomain.DISK, ChangeDomain.MACOS],

            # Pre-flight system
            "terminator_preflight_system": [ChangeDomain.DISK, ChangeDomain.TERMINAL, ChangeDomain.MACOS],

            # All agents care about agent updates
            "ALL": [ChangeDomain.AGENT],
        }

    def log_change(
        self,
        domain: ChangeDomain,
        change_type: ChangeType,
        title: str,
        description: str,
        affected_files: List[str] = None,
        affected_agents: List[str] = None
    ) -> Change:
        """
        Log a change and automatically propagate it.
        """
        import uuid

        change = Change(
            change_id=str(uuid.uuid4())[:8],
            timestamp=datetime.now().isoformat(),
            domain=domain,
            change_type=change_type,
            title=title,
            description=description,
            affected_files=affected_files or [],
            affected_agents=affected_agents or []
        )

        self.changes.append(change)
        self._save_changes()

        print(f"✅ Change logged: {change.change_id}")
        print(f"   Domain: {domain.value}")
        print(f"   Title: {title}\n")

        # Automatically propagate
        self.propagate_change(change)

        # Automatically document
        self.update_documentation(change)

        return change

    def propagate_change(self, change: Change) -> None:
        """
        Propagate change to relevant agents via communication bus.
        """
        if not self.bus:
            print("⚠️  No communication bus available for propagation")
            return

        # Find agents that care about this domain
        relevant_agents = self._get_relevant_agents(change.domain)

        if not relevant_agents:
            print(f"ℹ️  No agents subscribed to {change.domain.value} domain")
            return

        print(f"📢 Propagating to {len(relevant_agents)} agents...")

        for agent_name in relevant_agents:
            try:
                self.bus.send_message(
                    sender_agent="ChangePropagationSystem",
                    recipient_agent=agent_name,
                    message_type=MessageType.NOTIFICATION,
                    subject="Domain Update",
                    content={
                        'change_id': change.change_id,
                        'domain': change.domain.value,
                        'type': change.change_type.value,
                        'title': change.title,
                        'description': change.description,
                        'affected_files': change.affected_files,
                        'timestamp': change.timestamp
                    },
                    priority=MessagePriority.NORMAL
                )

                print(f"   ✅ {agent_name} notified")

            except Exception as e:
                print(f"   ⚠️  Could not notify {agent_name}: {e}")

        change.propagated = True
        change.affected_agents = relevant_agents
        self._save_changes()

        print(f"✅ Change propagated to {len(relevant_agents)} agents\n")

    def _get_relevant_agents(self, domain: ChangeDomain) -> List[str]:
        """Get list of agents that care about this domain"""
        relevant = []

        for agent_name, subscribed_domains in self.agent_subscriptions.items():
            if domain in subscribed_domains:
                if agent_name == "ALL":
                    # Get all agent files
                    relevant.extend(self._get_all_agents())
                else:
                    relevant.append(agent_name)

        return list(set(relevant))  # Remove duplicates

    def _get_all_agents(self) -> List[str]:
        """Get list of all agent files"""
        core_dir = self.project_root / "core"
        agents = []

        for file in core_dir.glob("terminator_*_agent.py"):
            agents.append(file.stem)  # stem = filename without extension

        return agents

    def update_documentation(self, change: Change) -> None:
        """
        Automatically update global documentation files.
        """
        print("📝 Updating documentation...")

        # Update GLOBAL_CHANGES.md
        self._update_global_changes_md(change)

        # Update domain-specific docs
        self._update_domain_docs(change)

        change.documented = True
        self._save_changes()

        print("✅ Documentation updated\n")

    def _update_global_changes_md(self, change: Change) -> None:
        """Update the global changes markdown file"""
        # Read existing content
        if self.global_doc_file.exists():
            with open(self.global_doc_file, 'r') as f:
                content = f.read()
        else:
            content = """# TERMINATOR Global Changes Log

This file is automatically updated when changes are made to the system.

---

"""

        # Add new change entry
        new_entry = f"""## [{change.timestamp[:10]}] {change.title}

**Domain:** {change.domain.value}
**Type:** {change.change_type.value}
**ID:** {change.change_id}

{change.description}

**Affected Files:**
{self._format_file_list(change.affected_files)}

**Propagated To:**
{self._format_agent_list(change.affected_agents)}

---

"""

        # Insert after header
        parts = content.split("---\n", 1)
        if len(parts) == 2:
            content = parts[0] + "---\n\n" + new_entry + parts[1]
        else:
            content += new_entry

        # Write back
        with open(self.global_doc_file, 'w') as f:
            f.write(content)

    def _update_domain_docs(self, change: Change) -> None:
        """Update domain-specific documentation"""
        domain_docs = {
            ChangeDomain.TERMINAL: self.project_root / "TERMINAL_CHANGES.md",
            ChangeDomain.DISK: self.project_root / "DISK_CHANGES.md",
            ChangeDomain.MACOS: self.project_root / "MACOS_CHANGES.md",
            ChangeDomain.AGENT: self.project_root / "AGENT_CHANGES.md",
        }

        domain_file = domain_docs.get(change.domain)
        if not domain_file:
            return

        # Create or update domain-specific file
        if domain_file.exists():
            with open(domain_file, 'r') as f:
                content = f.read()
        else:
            content = f"""# {change.domain.value.upper()} Changes Log

Automatically tracked changes related to {change.domain.value}.

---

"""

        # Add entry
        entry = f"""### {change.timestamp[:10]} - {change.title}

{change.description}

Files: {', '.join(change.affected_files) if change.affected_files else 'None'}

---

"""

        content += entry

        with open(domain_file, 'w') as f:
            f.write(content)

    def _format_file_list(self, files: List[str]) -> str:
        """Format list of files"""
        if not files:
            return "- None"
        return "\n".join(f"- `{f}`" for f in files)

    def _format_agent_list(self, agents: List[str]) -> str:
        """Format list of agents"""
        if not agents:
            return "- None"
        return "\n".join(f"- {a}" for a in agents)

    def get_changes_report(self, domain: Optional[ChangeDomain] = None) -> str:
        """Get report of all changes"""
        changes_to_show = self.changes

        if domain:
            changes_to_show = [c for c in self.changes if c.domain == domain]

        report = f"""
╔══════════════════════════════════════════════════════════════╗
║            CHANGE PROPAGATION SYSTEM REPORT                  ║
╚══════════════════════════════════════════════════════════════╝

📊 Statistics:
   • Total changes: {len(self.changes)}
   • Changes propagated: {sum(1 for c in self.changes if c.propagated)}
   • Changes documented: {sum(1 for c in self.changes if c.documented)}
"""

        if domain:
            report += f"   • Showing: {domain.value} domain only\n"

        report += "\n📋 Recent Changes:\n\n"

        for change in changes_to_show[-5:]:
            report += f"""   [{change.change_id}] {change.title}
   Domain: {change.domain.value} | Type: {change.change_type.value}
   Date: {change.timestamp[:10]}
   Agents notified: {len(change.affected_agents)}
   Files affected: {len(change.affected_files)}

"""

        return report


# ============================================================================
# Quick Logging Functions
# ============================================================================

_system_instance = None

def get_propagation_system() -> ChangePropagationSystem:
    """Get the propagation system instance"""
    global _system_instance
    if _system_instance is None:
        _system_instance = ChangePropagationSystem()
    return _system_instance


def log_terminal_change(title: str, description: str, files: List[str] = None):
    """Quick log for terminal changes"""
    system = get_propagation_system()
    return system.log_change(
        domain=ChangeDomain.TERMINAL,
        change_type=ChangeType.FIX,
        title=title,
        description=description,
        affected_files=files
    )


def log_disk_change(title: str, description: str, files: List[str] = None):
    """Quick log for disk changes"""
    system = get_propagation_system()
    return system.log_change(
        domain=ChangeDomain.DISK,
        change_type=ChangeType.FIX,
        title=title,
        description=description,
        affected_files=files
    )


def log_macos_change(title: str, description: str, files: List[str] = None):
    """Quick log for macOS changes"""
    system = get_propagation_system()
    return system.log_change(
        domain=ChangeDomain.MACOS,
        change_type=ChangeType.FIX,
        title=title,
        description=description,
        affected_files=files
    )


def log_agent_change(title: str, description: str, files: List[str] = None):
    """Quick log for agent changes"""
    system = get_propagation_system()
    return system.log_change(
        domain=ChangeDomain.AGENT,
        change_type=ChangeType.AGENT_UPDATE,
        title=title,
        description=description,
        affected_files=files
    )


if __name__ == "__main__":
    # Demo
    system = get_propagation_system()
    print(system.get_changes_report())
