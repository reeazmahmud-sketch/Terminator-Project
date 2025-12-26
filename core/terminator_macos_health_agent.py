#!/usr/bin/env python3
"""
TERMINATOR macOS Health Agent
=============================

Part of the Self-Healing Ecosystem (Phase 2).
Monitors system vitals (CPU, RAM, Disk, Battery, Temp) and takes corrective action.
"""

import psutil
import shutil
import subprocess
import asyncio
import platform
from datetime import datetime
from typing import Dict, Any

from core.terminator_agent_communication_bus import AgentCommunicationBus

class MacOSHealthAgent:
    """
    Monitors macOS system health and performs self-healing actions.
    """
    
    AGENT_NAME = "terminator_macos_health_agent"
    
    # Thresholds
    CPU_THRESHOLD = 90.0
    RAM_THRESHOLD = 90.0
    DISK_MIN_GB = 10.0
    
    def __init__(self):
        self.bus = AgentCommunicationBus.get_instance()
        self.running = True
        self.system = platform.system()

    async def start(self):
        """Initialize the agent."""
        print(f"🩺 Starting {self.AGENT_NAME}...")
        await self.bus.register_agent_async(self.AGENT_NAME)
        
        if self.system != "Darwin":
            print("❌ This agent only runs on macOS.")
            return

        asyncio.create_task(self._monitor_loop())
        print(f"✅ {self.AGENT_NAME} active and monitoring.")

    async def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            health = self.check_health()
            
            # Report status
            # await self.bus.send_message("orchestrator", "health_update", health)
            
            # Auto-healing logic
            if health["cpu_usage"] > self.CPU_THRESHOLD:
                print(f"⚠️  High CPU: {health['cpu_usage']}%")
                # self.mitigate_cpu()
                
            if health["ram_usage"] > self.RAM_THRESHOLD:
                print(f"⚠️  High RAM: {health['ram_usage']}%")
                
            if health["disk_free_gb"] < self.DISK_MIN_GB:
                print(f"⚠️  Low Disk Space: {health['disk_free_gb']}GB")
                
            await asyncio.sleep(60) # Check every minute

    def check_health(self) -> Dict[str, Any]:
        """Gather system metrics."""
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        
        disk = shutil.disk_usage("/")
        disk_free_gb = round(disk.free / (1024**3), 2)
        
        # Battery (requires external command on some macs, or psutil if supported)
        battery = psutil.sensors_battery()
        battery_percent = battery.percent if battery else 100
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_usage": cpu,
            "ram_usage": ram,
            "disk_free_gb": disk_free_gb,
            "battery": battery_percent
        }

    async def stop(self):
        self.running = False
        print(f"🛑 {self.AGENT_NAME} stopped.")

if __name__ == "__main__":
    agent = MacOSHealthAgent()
    asyncio.run(agent.start())
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        asyncio.run(agent.stop())
