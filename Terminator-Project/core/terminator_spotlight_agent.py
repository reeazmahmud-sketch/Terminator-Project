#!/usr/bin/env python3
"""
TERMINATOR Spotlight Agent
==========================

Part of the Self-Healing Ecosystem (Phase 2).
Monitors Spotlight indexing and fixes search issues.
"""

import subprocess
import asyncio
import os
from core.terminator_agent_communication_bus import AgentCommunicationBus

class SpotlightAgent:
    """
    Manages macOS Spotlight indexing.
    """
    
    AGENT_NAME = "terminator_spotlight_agent"
    
    def __init__(self):
        self.bus = AgentCommunicationBus.get_instance()

    async def start(self):
        print(f"🔍 Starting {self.AGENT_NAME}...")
        await self.bus.register_agent_async(self.AGENT_NAME)
        print(f"✅ {self.AGENT_NAME} ready.")

    async def check_indexing_status(self):
        """Check if Spotlight is currently indexing."""
        try:
            result = subprocess.run(["mdutil", "-s", "/"], capture_output=True, text=True)
            if "Indexing enabled" in result.stdout:
                return "enabled"
            elif "Indexing disabled" in result.stdout:
                return "disabled"
            return "unknown"
        except:
            return "error"

    async def reindex_root(self):
        """Force re-indexing of the root volume."""
        print("🔄 Re-indexing Spotlight...")
        # Requires sudo usually, so this might fail without privileges or user interaction
        subprocess.run(["sudo", "mdutil", "-E", "/"]) 

if __name__ == "__main__":
    agent = SpotlightAgent()
    asyncio.run(agent.start())
