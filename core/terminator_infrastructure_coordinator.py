#!/usr/bin/env python3

# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Infrastructure Coordinator
====================================

Starts and coordinates all infrastructure agents:
1. Claude Activity Logger - Logs all Claude changes
2. File System Guardian - Organizes files, prevents deletion
3. Change Propagation System - Notifies agents of changes
4. Documentation Maintainer - Auto-updates .md files
5. Solution Knowledge Base - Prevents redundant work

These agents run in the background, maintaining system health.

Created: December 17, 2025
Purpose: Autonomous infrastructure management
"""

import sys
import time
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from terminator_claude_activity_logger import get_activity_logger
from terminator_file_system_guardian import start_guardian
from terminator_change_propagation_system import get_propagation_system
from terminator_solution_knowledge_base import get_knowledge_base
from terminator_infinite_loop_guardian_agent import start_guardian as start_loop_guardian
from terminator_self_healing_coordinator import start_self_healing

# Phase 2: macOS Self-Healing Agents
from terminator_macos_health_agent import MacOSHealthAgent
from terminator_brew_agent import BrewAgent
from terminator_spotlight_agent import SpotlightAgent
from terminator_app_recovery_agent import AppRecoveryAgent
from terminator_permissions_agent import PermissionsAgent
import asyncio


# ============================================================================
# Infrastructure Coordinator
# ============================================================================

class InfrastructureCoordinator:
    """
    Coordinates all infrastructure agents.
    """

    def __init__(self):
        """Initialize coordinator"""
        self.agents = {}
        self.running = False

    def start_all(self) -> None:
        """Start all infrastructure agents"""
        print("\n" + "=" * 60)
        print("🚀 STARTING INFRASTRUCTURE AGENTS")
        print("=" * 60 + "\n")

        # 1. Claude Activity Logger
        try:
            logger = get_activity_logger()
            self.agents['claude_logger'] = logger
            print("✅ Claude Activity Logger active")
        except Exception as e:
            print(f"⚠️  Could not start Claude Logger: {e}")

        # 2. File System Guardian
        try:
            guardian = start_guardian()
            self.agents['file_guardian'] = guardian
            print("✅ File System Guardian active")
        except Exception as e:
            print(f"⚠️  Could not start File Guardian: {e}")

        # 3. Change Propagation System
        try:
            propagation = get_propagation_system()
            self.agents['propagation'] = propagation
            print("✅ Change Propagation System active")
        except Exception as e:
            print(f"⚠️  Could not start Change Propagation: {e}")

        # 4. Solution Knowledge Base
        try:
            kb = get_knowledge_base()
            self.agents['knowledge_base'] = kb
            print("✅ Solution Knowledge Base active")
        except Exception as e:
            print(f"⚠️  Could not start Knowledge Base: {e}")

        # 5. Infinite Loop Guardian
        try:
            loop_guardian = start_loop_guardian()
            self.agents['loop_guardian'] = loop_guardian
            print("✅ Infinite Loop Guardian active")
        except Exception as e:
            print(f"⚠️  Could not start Loop Guardian: {e}")

        # 6. Self-Healing Coordinator
        try:
            healing = start_self_healing()
            self.agents['self_healing'] = healing
            print("✅ Self-Healing Coordinator active")
        except Exception as e:
            print(f"⚠️  Could not start Self-Healing: {e}")

        # --- Phase 2: macOS Self-Healing ---
        
        def _start_async(agent):
            """Helper to start async agents in background"""
            try:
                # If we are already in an async loop (e.g. inside another agent)
                loop = asyncio.get_running_loop()
                loop.create_task(agent.start())
            except RuntimeError:
                # No running loop (e.g. called from sync script), run in thread
                import threading
                def run_loop():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(agent.start())
                    loop.run_forever()
                t = threading.Thread(target=run_loop, daemon=True)
                t.start()

        # 7. macOS Health Agent
        try:
            macos_agent = MacOSHealthAgent()
            _start_async(macos_agent)
            self.agents['macos_health'] = macos_agent
            print("✅ macOS Health Agent active")
        except Exception as e:
            print(f"⚠️  Could not start macOS Health Agent: {e}")

        # 8. Brew Agent
        try:
            brew_agent = BrewAgent()
            _start_async(brew_agent)
            self.agents['brew_manager'] = brew_agent
            print("✅ Brew Package Manager active")
        except Exception as e:
            print(f"⚠️  Could not start Brew Agent: {e}")

        # 9. Spotlight Agent
        try:
            spotlight_agent = SpotlightAgent()
            _start_async(spotlight_agent)
            self.agents['spotlight_manager'] = spotlight_agent
            print("✅ Spotlight Indexing Agent active")
        except Exception as e:
            print(f"⚠️  Could not start Spotlight Agent: {e}")

        # 10. App Recovery Agent
        try:
            app_recovery = AppRecoveryAgent()
            _start_async(app_recovery)
            self.agents['app_recovery'] = app_recovery
            print("✅ App Recovery Agent active")
        except Exception as e:
            print(f"⚠️  Could not start App Recovery Agent: {e}")

        # 11. Permissions Agent
        try:
            permissions_agent = PermissionsAgent()
            _start_async(permissions_agent)
            self.agents['permissions_monitor'] = permissions_agent
            print("✅ Permissions Monitor active")
        except Exception as e:
            print(f"⚠️  Could not start Permissions Agent: {e}")

        self.running = True

        print("\n" + "=" * 60)
        print(f"✅ {len(self.agents)} INFRASTRUCTURE AGENTS RUNNING")
        print("=" * 60 + "\n")

        self._print_status()

    def stop_all(self) -> None:
        """Stop all agents"""
        print("\n🛑 Stopping infrastructure agents...")

        for name, agent in self.agents.items():
            try:
                if hasattr(agent, 'stop'):
                    if asyncio.iscoroutinefunction(agent.stop):
                        # Fire and forget for sync context
                        pass 
                    else:
                        agent.stop()
                elif hasattr(agent, 'running'):
                    agent.running = False
                print(f"   ✅ Stopped {name}")
            except Exception as e:
                print(f"   ⚠️  Error stopping {name}: {e}")

        self.running = False
        print("✅ All agents stopped\n")

    def _print_status(self) -> None:
        """Print status of all agents"""
        print("📊 Agent Status:\n")

        print("1. Infrastructure Core")
        print("   └─ Claude Activity Logger, File Guardian")
        print("   └─ Change Propagation, Knowledge Base")
        print("   └─ Infinite Loop Guardian, Self-Healing Coord\n")

        print("2. macOS Self-Healing (Phase 2)")
        print("   └─ macOS Health: Monitors CPU, RAM, Disk")
        print("   └─ Brew Manager: Updates packages")
        print("   └─ Spotlight: Fixes search indexing")
        print("   └─ App Recovery: Restarts crashed apps")
        print("   └─ Permissions: Monitors access rights\n")

    def get_full_report(self) -> str:
        """Get comprehensive status report"""
        report = """
╔══════════════════════════════════════════════════════════════╗
║        INFRASTRUCTURE STATUS REPORT                          ║
╚══════════════════════════════════════════════════════════════╝

"""

        # Claude Activity Logger
        if 'claude_logger' in self.agents:
            logger = self.agents['claude_logger']
            report += logger.get_session_report() + "\n"

        # File System Guardian
        if 'file_guardian' in self.agents:
            guardian = self.agents['file_guardian']
            report += guardian.get_status() + "\n"

        # Change Propagation
        if 'propagation' in self.agents:
            prop = self.agents['propagation']
            report += prop.get_changes_report() + "\n"

        # Knowledge Base
        if 'knowledge_base' in self.agents:
            kb = self.agents['knowledge_base']
            report += kb.get_solution_report() + "\n"

        return report


# ============================================================================
# Quick Start Functions
# ============================================================================

_coordinator_instance = None

def get_coordinator() -> InfrastructureCoordinator:
    """Get coordinator instance"""
    global _coordinator_instance
    if _coordinator_instance is None:
        _coordinator_instance = InfrastructureCoordinator()
    return _coordinator_instance


def start_infrastructure() -> InfrastructureCoordinator:
    """Start all infrastructure agents"""
    coordinator = get_coordinator()
    coordinator.start_all()
    return coordinator


def stop_infrastructure():
    """Stop all infrastructure agents"""
    coordinator = get_coordinator()
    coordinator.stop_all()


if __name__ == "__main__":
    # Start infrastructure
    print("""
╔══════════════════════════════════════════════════════════════╗
║         TERMINATOR INFRASTRUCTURE COORDINATOR                ║
╚══════════════════════════════════════════════════════════════╝

Starting autonomous infrastructure agents...
These agents run in the background, maintaining system health.

""")

    coordinator = start_infrastructure()

    try:
        print("\n✅ Infrastructure running. Press Ctrl+C to stop.\n")

        while True:
            time.sleep(60)  # Sleep for 1 minute
            # Could print periodic status here

    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down infrastructure...\n")
        coordinator.stop_all()
        print("\n✅ Shutdown complete\n")
