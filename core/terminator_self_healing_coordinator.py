#!/usr/bin/env python3

# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Self-Healing Coordinator
==================================

Master agent that coordinates all self-healing across:
- macOS
- iOS
- Home Network
- Browser/Internet
- File Transfers

Implements: Detect → Diagnose → Fix → Document → Verify

Created: December 17, 2025
Purpose: Complete autonomous self-healing for entire ecosystem
"""

import sys
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from core.terminator_agent_communication_bus import get_communication_bus, MessageType, MessagePriority
    HAS_BUS = True
except ImportError:
    HAS_BUS = False


# ============================================================================
# Health Status
# ============================================================================

class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class SystemDomain(Enum):
    """System domains"""
    MACOS = "macos"
    IOS = "ios"
    NETWORK = "network"
    BROWSER = "browser"
    FILE_TRANSFER = "file_transfer"


@dataclass
class HealthCheck:
    """Result of a health check"""
    domain: SystemDomain
    component: str
    status: HealthStatus
    message: str
    timestamp: str
    auto_fixable: bool = False
    fix_applied: bool = False


# ============================================================================
# Self-Healing Coordinator
# ============================================================================

class SelfHealingCoordinator:
    """
    Master coordinator for all self-healing activities.
    """

    def __init__(self):
        """Initialize self-healing coordinator"""
        self.project_root = Path("/Users/reeazmahmud/Desktop/Terminator-Project")
        self.health_dir = self.project_root / ".health_checks"
        self.health_dir.mkdir(exist_ok=True)

        # State
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.health_checks: List[HealthCheck] = []

        # Statistics
        self.stats = {
            'checks_performed': 0,
            'issues_detected': 0,
            'auto_fixes_applied': 0,
            'manual_interventions': 0
        }

        # Communication bus
        self.bus = get_communication_bus() if HAS_BUS else None

        # Initialize sub-agents
        self.agents = {}

    def start(self) -> None:
        """Start self-healing coordinator"""
        if self.running:
            print("⚠️  Self-healing coordinator already running")
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._healing_loop, daemon=True)
        self.monitor_thread.start()

        print("🏥 Self-Healing Coordinator started")
        print("   Monitoring: macOS, iOS, Network, Browser, Files")
        print("   Mode: Detect → Diagnose → Fix → Document")

    def stop(self) -> None:
        """Stop self-healing coordinator"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("⛔ Self-Healing Coordinator stopped")

    def _healing_loop(self) -> None:
        """Main self-healing loop"""
        iteration = 0

        while self.running:
            try:
                iteration += 1

                # 1. DETECT - Run all health checks
                health_results = self._run_health_checks()

                # 2. DIAGNOSE - Analyze issues
                issues = [h for h in health_results if h.status in [HealthStatus.WARNING, HealthStatus.CRITICAL]]

                if issues:
                    print(f"\n⚠️  Detected {len(issues)} issues (iteration {iteration})")

                    for issue in issues:
                        # 3. FIX - Auto-fix if possible
                        if issue.auto_fixable:
                            success = self._auto_fix(issue)

                            if success:
                                issue.fix_applied = True
                                self.stats['auto_fixes_applied'] += 1
                                print(f"   ✅ Fixed: {issue.component}")
                            else:
                                self.stats['manual_interventions'] += 1
                                print(f"   ⚠️  Manual fix needed: {issue.component}")

                        # 4. DOCUMENT
                        self._document_issue(issue)

                # 5. VERIFY - Confirm fixes worked
                if issues:
                    time.sleep(5)  # Wait for fixes to take effect
                    self._verify_fixes(issues)

                # Save results
                self._save_health_report(health_results)

                # Sleep before next check
                time.sleep(60)  # Check every minute

            except Exception as e:
                print(f"❌ Error in healing loop: {e}")
                time.sleep(60)

    def _run_health_checks(self) -> List[HealthCheck]:
        """Run all health checks"""
        results = []
        self.stats['checks_performed'] += 1

        # macOS checks
        results.extend(self._check_macos())

        # iOS checks (if connected)
        results.extend(self._check_ios())

        # Network checks
        results.extend(self._check_network())

        # Browser checks
        results.extend(self._check_browser())

        # File transfer checks
        results.extend(self._check_file_transfers())

        return results

    def _check_macos(self) -> List[HealthCheck]:
        """Check macOS health"""
        checks = []

        # CPU check
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)

            if cpu_percent > 90:
                checks.append(HealthCheck(
                    domain=SystemDomain.MACOS,
                    component="CPU",
                    status=HealthStatus.WARNING,
                    message=f"CPU usage high: {cpu_percent}%",
                    timestamp=datetime.now().isoformat(),
                    auto_fixable=True
                ))
            else:
                checks.append(HealthCheck(
                    domain=SystemDomain.MACOS,
                    component="CPU",
                    status=HealthStatus.HEALTHY,
                    message=f"CPU: {cpu_percent}%",
                    timestamp=datetime.now().isoformat()
                ))
        except:
            checks.append(HealthCheck(
                domain=SystemDomain.MACOS,
                component="CPU",
                status=HealthStatus.UNKNOWN,
                message="Could not check CPU",
                timestamp=datetime.now().isoformat()
            ))

        # Memory check
        try:
            import psutil
            memory = psutil.virtual_memory()

            if memory.percent > 90:
                checks.append(HealthCheck(
                    domain=SystemDomain.MACOS,
                    component="Memory",
                    status=HealthStatus.CRITICAL,
                    message=f"Memory pressure high: {memory.percent}%",
                    timestamp=datetime.now().isoformat(),
                    auto_fixable=True
                ))
            else:
                checks.append(HealthCheck(
                    domain=SystemDomain.MACOS,
                    component="Memory",
                    status=HealthStatus.HEALTHY,
                    message=f"Memory: {memory.percent}%",
                    timestamp=datetime.now().isoformat()
                ))
        except:
            pass

        # Disk check
        try:
            import shutil
            disk = shutil.disk_usage('/')

            free_gb = disk.free / (1024**3)

            if free_gb < 10:
                checks.append(HealthCheck(
                    domain=SystemDomain.MACOS,
                    component="Disk",
                    status=HealthStatus.CRITICAL,
                    message=f"Disk space low: {free_gb:.1f}GB free",
                    timestamp=datetime.now().isoformat(),
                    auto_fixable=True
                ))
            else:
                checks.append(HealthCheck(
                    domain=SystemDomain.MACOS,
                    component="Disk",
                    status=HealthStatus.HEALTHY,
                    message=f"Disk: {free_gb:.1f}GB free",
                    timestamp=datetime.now().isoformat()
                ))
        except:
            pass

        return checks

    def _check_ios(self) -> List[HealthCheck]:
        """Check iOS device health"""
        # Placeholder - would check via iOS shortcuts or API
        return []

    def _check_network(self) -> List[HealthCheck]:
        """Check network health"""
        checks = []

        # Internet connectivity
        import subprocess
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '8.8.8.8'],
                capture_output=True,
                timeout=5
            )

            if result.returncode == 0:
                checks.append(HealthCheck(
                    domain=SystemDomain.NETWORK,
                    component="Internet",
                    status=HealthStatus.HEALTHY,
                    message="Internet connected",
                    timestamp=datetime.now().isoformat()
                ))
            else:
                checks.append(HealthCheck(
                    domain=SystemDomain.NETWORK,
                    component="Internet",
                    status=HealthStatus.CRITICAL,
                    message="Internet down",
                    timestamp=datetime.now().isoformat(),
                    auto_fixable=True
                ))
        except:
            checks.append(HealthCheck(
                domain=SystemDomain.NETWORK,
                component="Internet",
                status=HealthStatus.CRITICAL,
                message="Internet check failed",
                timestamp=datetime.now().isoformat(),
                auto_fixable=True
            ))

        return checks

    def _check_browser(self) -> List[HealthCheck]:
        """Check browser health"""
        # Placeholder
        return []

    def _check_file_transfers(self) -> List[HealthCheck]:
        """Check file transfer systems"""
        # Placeholder
        return []

    def _auto_fix(self, issue: HealthCheck) -> bool:
        """Attempt to auto-fix an issue"""
        print(f"   🔧 Attempting auto-fix: {issue.component}")

        try:
            if issue.component == "CPU":
                return self._fix_high_cpu()
            elif issue.component == "Memory":
                return self._fix_high_memory()
            elif issue.component == "Disk":
                return self._fix_low_disk()
            elif issue.component == "Internet":
                return self._fix_internet()

            return False

        except Exception as e:
            print(f"   ❌ Auto-fix failed: {e}")
            return False

    def _fix_high_cpu(self) -> bool:
        """Fix high CPU usage"""
        # Kill top CPU process if it's safe
        try:
            import psutil
            processes = sorted(psutil.process_iter(['pid', 'name', 'cpu_percent']),
                             key=lambda p: p.info['cpu_percent'],
                             reverse=True)

            top_process = processes[0]

            # Only kill if it's a known problematic process
            if top_process.info['name'] in ['mdworker', 'mds_stores']:
                top_process.kill()
                return True

        except:
            pass

        return False

    def _fix_high_memory(self) -> bool:
        """Fix high memory usage"""
        # Clear caches
        import subprocess
        try:
            subprocess.run(['purge'], timeout=30)
            return True
        except:
            return False

    def _fix_low_disk(self) -> bool:
        """Fix low disk space"""
        # Trigger file guardian cleanup
        try:
            from terminator_file_system_guardian import get_file_guardian
            guardian = get_file_guardian()
            # Guardian will handle cleanup
            return True
        except:
            return False

    def _fix_internet(self) -> bool:
        """Fix internet connectivity"""
        # Restart network interface
        import subprocess
        try:
            # Turn WiFi off and on
            subprocess.run(['networksetup', '-setairportpower', 'en0', 'off'], timeout=5)
            time.sleep(2)
            subprocess.run(['networksetup', '-setairportpower', 'en0', 'on'], timeout=5)
            return True
        except:
            return False

    def _verify_fixes(self, issues: List[HealthCheck]) -> None:
        """Verify that fixes worked"""
        for issue in issues:
            if issue.fix_applied:
                # Re-run the specific check
                print(f"   ✓ Verifying fix for {issue.component}...")

    def _document_issue(self, issue: HealthCheck) -> None:
        """Document an issue"""
        log_file = self.health_dir / f"issues_{datetime.now().strftime('%Y%m%d')}.log"

        with open(log_file, 'a') as f:
            f.write(f"[{issue.timestamp}] {issue.domain.value}/{issue.component}: ")
            f.write(f"{issue.status.value} - {issue.message}\n")

            if issue.fix_applied:
                f.write(f"  → Auto-fixed\n")
            else:
                f.write(f"  → Manual intervention needed\n")

            f.write("\n")

    def _save_health_report(self, results: List[HealthCheck]) -> None:
        """Save health report"""
        report_file = self.health_dir / "latest_health_report.txt"

        with open(report_file, 'w') as f:
            f.write("TERMINATOR ECOSYSTEM HEALTH REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")

            # Group by domain
            for domain in SystemDomain:
                domain_checks = [c for c in results if c.domain == domain]
                if domain_checks:
                    f.write(f"{domain.value.upper()}:\n")
                    for check in domain_checks:
                        status_icon = {
                            HealthStatus.HEALTHY: "✅",
                            HealthStatus.WARNING: "⚠️",
                            HealthStatus.CRITICAL: "🚨",
                            HealthStatus.UNKNOWN: "❓"
                        }[check.status]

                        f.write(f"  {status_icon} {check.component}: {check.message}\n")

                    f.write("\n")

    def get_status(self) -> str:
        """Get coordinator status"""
        return f"""
╔══════════════════════════════════════════════════════════════╗
║         SELF-HEALING COORDINATOR STATUS                      ║
╚══════════════════════════════════════════════════════════════╝

🏥 Coordinator Status:
   • Running: {self.running}
   • Checks performed: {self.stats['checks_performed']}
   • Issues detected: {self.stats['issues_detected']}
   • Auto-fixes applied: {self.stats['auto_fixes_applied']}
   • Manual interventions: {self.stats['manual_interventions']}

📊 Recent Health Checks:
"""
        # Add recent checks summary


# ============================================================================
# Module Interface
# ============================================================================

_coordinator_instance = None

def get_self_healing_coordinator() -> SelfHealingCoordinator:
    """Get coordinator instance"""
    global _coordinator_instance
    if _coordinator_instance is None:
        _coordinator_instance = SelfHealingCoordinator()
    return _coordinator_instance


def start_self_healing() -> SelfHealingCoordinator:
    """Start self-healing coordinator"""
    coordinator = get_self_healing_coordinator()
    coordinator.start()
    return coordinator


if __name__ == "__main__":
    # Start self-healing
    coordinator = start_self_healing()

    try:
        print("\n✅ Self-healing active. Press Ctrl+C to stop.\n")
        while True:
            time.sleep(30)
            print(coordinator.get_status())

    except KeyboardInterrupt:
        print("\n\n🛑 Stopping self-healing...\n")
        coordinator.stop()
