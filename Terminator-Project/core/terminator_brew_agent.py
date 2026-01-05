#!/usr/bin/env python3
"""
TERMINATOR Brew Package Manager Agent
=====================================

Part of the Self-Healing Ecosystem (Phase 2).
Manages Homebrew packages, updates, cleanup, and doctor checks.
"""

import subprocess
import asyncio
import logging
from typing import Dict, Any

from core.terminator_agent_communication_bus import AgentCommunicationBus

class BrewAgent:
    """
    Automates Homebrew maintenance and healing.
    """
    
    AGENT_NAME = "terminator_brew_agent"
    
    def __init__(self):
        self.bus = AgentCommunicationBus.get_instance()
        self.running = True

    async def start(self):
        """Initialize the agent."""
        print(f"🍺 Starting {self.AGENT_NAME}...")
        await self.bus.register_agent_async(self.AGENT_NAME)
        
        # Initial check
        asyncio.create_task(self.check_status())
        print(f"✅ {self.AGENT_NAME} ready.")

    async def check_status(self):
        """Run brew diagnostics."""
        print("🔍 Checking Homebrew status...")
        
        try:
            # Check for outdated packages
            outdated = subprocess.run(["brew", "outdated"], capture_output=True, text=True)
            if outdated.stdout.strip():
                count = len(outdated.stdout.strip().split('\n'))
                print(f"📦 {count} outdated packages found.")
                # Could trigger auto-update here based on policy
            
            # Check doctor
            doctor = subprocess.run(["brew", "doctor"], capture_output=True, text=True)
            if doctor.returncode != 0:
                print("⚠️  Brew Doctor found issues.")
                # Analyze issues
            else:
                print("✅ Brew Doctor is healthy.")
                
        except FileNotFoundError:
            print("❌ Homebrew not found.")

    async def handle_message(self, message: Dict[str, Any]):
        """Handle requests like 'update_all' or 'install_package'."""
        command = message.get("command")
        if command == "update":
            await self.update_system()
        elif command == "cleanup":
            await self.cleanup_system()

    async def update_system(self):
        print("🔄 Running brew update & upgrade...")
        subprocess.run(["brew", "update"])
        subprocess.run(["brew", "upgrade"])
        print("✅ System updated.")

    async def cleanup_system(self):
        print("🧹 Running brew cleanup...")
        subprocess.run(["brew", "cleanup"])
        print("✅ System cleaned.")

if __name__ == "__main__":
    agent = BrewAgent()
    asyncio.run(agent.start())
