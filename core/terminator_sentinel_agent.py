# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

import asyncio
import os
import time
import shutil
import platform
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional, List

# Try to import psutil, handle if missing
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from core.agent_framework import BaseAgent
from core.terminator_agent_communication_bus import Message, MessageType, MessagePriority

class SentinelAgent(BaseAgent):
    """
    Sentinel Endpoint Agent: Autonomous Endpoint Management.
    Monitors system health, enforces policies, and self-heals critical services.
    """
    AGENT_NAME = "SentinelAgent"
    AGENT_DESCRIPTION = "Autonomous Endpoint Manager for system health and self-healing."
    AGENT_CAPABILITIES = ["system_monitoring", "service_health", "auto_remediation", "patch_scanning"]

    def __init__(self, monitor_interval: int = 60):
        super().__init__(
            name=self.AGENT_NAME,
            description=self.AGENT_DESCRIPTION,
            capabilities=self.AGENT_CAPABILITIES
        )
        self.monitor_interval = monitor_interval
        self._monitor_task: Optional[asyncio.Task] = None
        self.critical_services = ["ollama"] # Add more as needed
        self.system_info = self._get_static_system_info()

    async def start(self):
        """Start the agent and the monitoring loop."""
        await super().start()
        if not PSUTIL_AVAILABLE:
            print(f"⚠️  {self.name}: 'psutil' not found. Enhanced metrics disabled. (pip install psutil)")
        
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
        print(f"🛡️  {self.name} started monitoring loop (Interval: {self.monitor_interval}s)")

    async def stop(self):
        """Stop the agent and monitoring."""
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        await super().stop()

    async def handle_message(self, message: Message) -> Optional[Dict[str, Any]]:
        """Handle on-demand requests."""
        subject = message.subject.lower()
        
        if subject == "get_health_status":
            return self._collect_telemetry()
        
        elif subject == "scan_patches":
            return await self._scan_updates()
            
        elif subject == "restart_service":
            service = message.content.get("service")
            if service:
                success = await self._restart_service(service)
                return {"service": service, "restarted": success}
            return {"error": "No service specified"}

        return {"error": f"Unknown subject: {subject}"}

    async def _monitoring_loop(self):
        """Background loop for continuous health checking."""
        while True:
            try:
                telemetry = self._collect_telemetry()
                
                # Check for critical issues
                alerts = self._analyze_telemetry(telemetry)
                
                if alerts:
                    # Report alerts to Orchestrator or Log
                    for alert in alerts:
                        print(f"🚨 {self.name} ALERT: {alert}")
                        # In a real system, send an ALERT message to the bus
                        # await self._bus.send_message_async(...) 
                
                # Check critical services
                await self._check_and_heal_services()

                await asyncio.sleep(self.monitor_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ {self.name} Monitor Error: {e}")
                await asyncio.sleep(self.monitor_interval)

    def _collect_telemetry(self) -> Dict[str, Any]:
        """Gather system metrics."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "hostname": self.system_info.get("node"),
            "os": self.system_info.get("system"),
        }

        # Disk
        try:
            total, used, free = shutil.disk_usage("/")
            metrics["disk"] = {
                "total_gb": total // (2**30),
                "used_gb": used // (2**30),
                "free_gb": free // (2**30),
                "percent": (used / total) * 100
            }
        except Exception:
            metrics["disk"] = "error"

        # CPU & RAM (if psutil)
        if PSUTIL_AVAILABLE:
            metrics["cpu_percent"] = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            metrics["memory"] = {
                "total_gb": mem.total // (2**30),
                "available_gb": mem.available // (2**30),
                "percent": mem.percent
            }
        
        return metrics

    def _analyze_telemetry(self, telemetry: Dict[str, Any]) -> List[str]:
        """Analyze metrics for anomalies and update system load state."""
        alerts = []
        load_level = "normal"
        
        # Disk Check
        disk = telemetry.get("disk")
        if isinstance(disk, dict) and disk["percent"] > 90:
            alerts.append(f"Disk usage critical: {disk['percent']:.1f}%")

        # Memory Check
        mem = telemetry.get("memory")
        if mem:
            if mem["percent"] > 90:
                alerts.append(f"Memory usage critical: {mem['percent']}%")
                load_level = "critical"
            elif mem["percent"] > 75:
                load_level = "high"

        # CPU Check
        cpu = telemetry.get("cpu_percent", 0)
        if cpu > 90:
            load_level = "critical"
        elif cpu > 75 and load_level != "critical":
            load_level = "high"

        # Update Shared Memory for other agents to react
        self._bus.set_shared_memory("system_load_level", load_level)

        return alerts

    async def _check_and_heal_services(self):
        """Check critical services and attempt restart if down."""
        for service in self.critical_services:
            is_running = self._is_process_running(service)
            if not is_running:
                print(f"⚠️  {self.name}: Service '{service}' is DOWN. Attempting self-healing...")
                success = await self._restart_service(service)
                if success:
                    print(f"✅ {self.name}: Service '{service}' recovered successfully.")
                else:
                    print(f"❌ {self.name}: Failed to recover '{service}'.")

    def _is_process_running(self, process_name: str) -> bool:
        """Check if a process is running."""
        # Simple check via pgrep or psutil
        if PSUTIL_AVAILABLE:
            for proc in psutil.process_iter(['name']):
                try:
                    if process_name.lower() in proc.info['name'].lower():
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            return False
        else:
            # Fallback to shell command
            try:
                # pgrep returns 0 if found, 1 if not
                code = subprocess.call(["pgrep", "-f", process_name], stdout=subprocess.DEVNULL)
                return code == 0
            except Exception:
                return False

    async def _restart_service(self, service: str) -> bool:
        """Attempt to restart a service."""
        if service == "ollama":
            # Attempt to start ollama serve
            try:
                # We start it as a background process
                subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                # Wait a bit to see if it stays up
                await asyncio.sleep(2)
                return self._is_process_running("ollama")
            except Exception as e:
                print(f"Error restarting ollama: {e}")
                return False
        
        # Add other services here
        return False

    async def _scan_updates(self) -> Dict[str, Any]:
        """Check for updates (Homebrew example)."""
        if platform.system() == "Darwin":
            try:
                proc = await asyncio.create_subprocess_shell(
                    "brew outdated",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, _ = await proc.communicate()
                outdated = stdout.decode().strip().split("\n")
                outdated = [p for p in outdated if p]
                return {"status": "success", "outdated_count": len(outdated), "packages": outdated}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        return {"status": "skipped", "message": "OS not supported for patch scan"}

    def _get_static_system_info(self) -> Dict[str, str]:
        return {
            "system": platform.system(),
            "node": platform.node(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor()
        }

# Factory
def create_agent():
    return SentinelAgent()
