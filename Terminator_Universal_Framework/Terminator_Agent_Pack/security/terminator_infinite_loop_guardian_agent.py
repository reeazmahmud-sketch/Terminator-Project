#!/usr/bin/env python3

# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Infinite Loop Guardian Agent
======================================

Detects and prevents infinite loops from destroying system resources.
Monitors log files, detects repeating patterns, and automatically stops
runaway processes before they fill the disk.

Features:
- Real-time log file growth monitoring
- Repeating pattern detection (catches infinite loops)
- Automatic log file size enforcement (max 100MB per file)
- Process termination for runaway loops
- Emergency disk space protection
- Integration with Agent Communication Bus

Created: December 17, 2025
Purpose: Prevent disk space disasters from infinite loops
"""

import os
import sys
import time
import subprocess
import threading
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from core.terminator_agent_communication_bus import get_communication_bus, MessageType, MessagePriority
except ImportError:
    print("⚠️  Warning: Could not import communication bus")
    get_communication_bus = None
    MessageType = None
    MessagePriority = None


# ============================================================================
# Configuration
# ============================================================================

class Config:
    """Agent configuration"""
    # Log file limits
    MAX_LOG_FILE_SIZE = 100 * 1024 * 1024  # 100MB - hard limit
    WARNING_LOG_SIZE = 50 * 1024 * 1024    # 50MB - warning threshold

    # Pattern detection
    PATTERN_WINDOW_SIZE = 50               # Lines to check for patterns
    REPETITION_THRESHOLD = 10              # Same pattern 10x = infinite loop

    # Monitoring intervals
    CHECK_INTERVAL = 5                     # Check every 5 seconds
    LOG_GROWTH_WINDOW = 30                 # Track growth over 30 seconds

    # Emergency thresholds
    RAPID_GROWTH_THRESHOLD = 10 * 1024 * 1024  # 10MB in 30 seconds
    DISK_CRITICAL_THRESHOLD = 95           # Disk usage % for emergency mode

    # Directories to monitor
    TERMINATOR_ROOT = Path("/Users/reeazmahmud/Desktop/Terminator")
    TERMINATOR_PROJECT_ROOT = Path("/Users/reeazmahmud/Desktop/Terminator-Project")

    @classmethod
    def get_log_directories(cls) -> List[Path]:
        """Get all log directories to monitor"""
        return [
            cls.TERMINATOR_ROOT / "logs",
            cls.TERMINATOR_PROJECT_ROOT / "logs",
            Path.home() / "Library/Logs",
        ]


# ============================================================================
# Data Structures
# ============================================================================

class LoopSeverity(Enum):
    """Severity of detected infinite loop"""
    CRITICAL = "CRITICAL"  # Immediate disk threat
    HIGH = "HIGH"          # Rapid growth detected
    MEDIUM = "MEDIUM"      # Suspicious patterns
    LOW = "LOW"            # Minor repetition


@dataclass
class LogFileInfo:
    """Information about a monitored log file"""
    path: Path
    size: int
    last_check_size: int
    growth_rate: float = 0.0  # Bytes per second
    pattern_buffer: deque = field(default_factory=lambda: deque(maxlen=Config.PATTERN_WINDOW_SIZE))
    pattern_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    last_modified: float = 0.0
    is_growing_rapidly: bool = False
    warnings_sent: int = 0


@dataclass
class InfiniteLoopDetection:
    """Detected infinite loop incident"""
    timestamp: str
    log_file: Path
    severity: LoopSeverity
    pattern: str
    repetition_count: int
    growth_rate_mb_per_sec: float
    action_taken: str
    process_killed: Optional[str] = None


# ============================================================================
# Infinite Loop Guardian Agent
# ============================================================================

class InfiniteLoopGuardianAgent:
    """
    Monitors for infinite loops and prevents disk space disasters.
    """

    def __init__(self):
        """Initialize the guardian agent"""
        self.agent_name = "InfiniteLoopGuardian"
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None

        # State tracking
        self.monitored_files: Dict[str, LogFileInfo] = {}
        self.detected_loops: List[InfiniteLoopDetection] = []
        self.killed_processes: Set[int] = set()

        # Statistics
        self.stats = {
            'loops_detected': 0,
            'files_truncated': 0,
            'processes_killed': 0,
            'total_space_saved': 0,
        }

        # Communication bus
        if get_communication_bus:
            try:
                self.bus = get_communication_bus()
                self.bus.register_agent(self.agent_name, self)
                print(f"✅ {self.agent_name} registered with communication bus")
            except Exception as e:
                print(f"⚠️  Could not register with bus: {e}")
                self.bus = None
        else:
            self.bus = None

        # Discover log files
        self._discover_log_files()

    def _discover_log_files(self) -> None:
        """Discover all log files to monitor"""
        log_patterns = ['*.log', '*.txt', '*.out']

        for log_dir in Config.get_log_directories():
            if not log_dir.exists():
                continue

            for pattern in log_patterns:
                for log_file in log_dir.rglob(pattern):
                    if log_file.is_file():
                        self._add_log_file(log_file)

        print(f"📊 Monitoring {len(self.monitored_files)} log files")

    def _add_log_file(self, path: Path) -> None:
        """Add a log file to monitoring"""
        try:
            size = path.stat().st_size
            key = str(path)

            if key not in self.monitored_files:
                self.monitored_files[key] = LogFileInfo(
                    path=path,
                    size=size,
                    last_check_size=size,
                    last_modified=path.stat().st_mtime
                )
        except Exception as e:
            print(f"⚠️  Could not add {path}: {e}")

    def start(self) -> None:
        """Start monitoring"""
        if self.running:
            print(f"⚠️  {self.agent_name} already running")
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()

        print(f"🛡️  {self.agent_name} started - Protecting against infinite loops")
        print(f"   Max log size: {Config.MAX_LOG_FILE_SIZE / 1024 / 1024:.0f}MB")
        print(f"   Check interval: {Config.CHECK_INTERVAL}s")

    def stop(self) -> None:
        """Stop monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print(f"⛔ {self.agent_name} stopped")

    def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.running:
            try:
                # Check all monitored files
                for log_info in list(self.monitored_files.values()):
                    self._check_log_file(log_info)

                # Check disk space
                self._check_disk_space()

                # Periodic discovery of new files
                if int(time.time()) % 60 == 0:  # Every minute
                    self._discover_log_files()

                # Update bus status
                if self.bus:
                    try:
                        self.bus.update_agent_status(
                            self.agent_name,
                            "monitoring",
                            0.5,
                            extra_info=f"Watching {len(self.monitored_files)} files"
                        )
                    except:
                        pass

                time.sleep(Config.CHECK_INTERVAL)

            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                time.sleep(Config.CHECK_INTERVAL)

    def _check_log_file(self, log_info: LogFileInfo) -> None:
        """Check a single log file for infinite loops"""
        try:
            if not log_info.path.exists():
                return

            # Get current size
            current_size = log_info.path.stat().st_size
            size_delta = current_size - log_info.last_check_size

            # Calculate growth rate (bytes per second)
            log_info.growth_rate = size_delta / Config.CHECK_INTERVAL

            # Check for rapid growth
            if size_delta > Config.RAPID_GROWTH_THRESHOLD:
                log_info.is_growing_rapidly = True
                self._handle_rapid_growth(log_info)

            # Check for size limit violation
            if current_size > Config.MAX_LOG_FILE_SIZE:
                self._handle_oversized_log(log_info)
            elif current_size > Config.WARNING_LOG_SIZE:
                self._send_warning(log_info)

            # Check for repeating patterns (only if file is growing)
            if size_delta > 0:
                self._check_for_patterns(log_info)

            # Update tracking
            log_info.last_check_size = current_size
            log_info.size = current_size

        except Exception as e:
            print(f"⚠️  Error checking {log_info.path}: {e}")

    def _check_for_patterns(self, log_info: LogFileInfo) -> None:
        """Check log file for repeating patterns (infinite loops)"""
        try:
            # Read last N lines
            with open(log_info.path, 'rb') as f:
                # Seek to near end
                f.seek(max(0, log_info.size - 50000))  # Last 50KB
                lines = f.readlines()[-Config.PATTERN_WINDOW_SIZE:]

            # Check for repeating patterns
            for line in lines:
                try:
                    line_text = line.decode('utf-8', errors='ignore').strip()
                    if not line_text:
                        continue

                    # Create pattern hash (ignore timestamps)
                    pattern = self._extract_pattern(line_text)
                    log_info.pattern_counts[pattern] += 1

                    # Detect infinite loop
                    if log_info.pattern_counts[pattern] >= Config.REPETITION_THRESHOLD:
                        self._handle_infinite_loop(log_info, pattern, log_info.pattern_counts[pattern])
                        return

                except:
                    continue

        except Exception as e:
            pass  # Silently ignore read errors

    def _extract_pattern(self, line: str) -> str:
        """Extract error pattern from log line (remove timestamps, etc.)"""
        # Remove common timestamp patterns
        import re
        pattern = re.sub(r'\d{4}-\d{2}-\d{2}', '', line)
        pattern = re.sub(r'\d{2}:\d{2}:\d{2}', '', pattern)
        pattern = re.sub(r'\d+\.\d+', '', pattern)
        pattern = re.sub(r'\d+', '', pattern)

        # Create hash of cleaned pattern
        return hashlib.md5(pattern.encode()).hexdigest()[:16]

    def _handle_rapid_growth(self, log_info: LogFileInfo) -> None:
        """Handle rapidly growing log file"""
        growth_mb = log_info.growth_rate / 1024 / 1024

        print(f"🚨 RAPID GROWTH: {log_info.path.name}")
        print(f"   Growth: {growth_mb:.2f} MB/sec")

        # Find and kill the process writing to it
        self._find_and_kill_writer(log_info)

        # Truncate if too large
        if log_info.size > Config.WARNING_LOG_SIZE:
            self._truncate_log(log_info)

    def _handle_oversized_log(self, log_info: LogFileInfo) -> None:
        """Handle log file that exceeded max size"""
        size_mb = log_info.size / 1024 / 1024

        print(f"🚨 OVERSIZED LOG: {log_info.path.name}")
        print(f"   Size: {size_mb:.1f}MB (limit: {Config.MAX_LOG_FILE_SIZE / 1024 / 1024:.0f}MB)")

        # Emergency action: truncate immediately
        self._truncate_log(log_info, emergency=True)

        # Find and kill the writer
        self._find_and_kill_writer(log_info)

    def _handle_infinite_loop(self, log_info: LogFileInfo, pattern: str, count: int) -> None:
        """Handle detected infinite loop"""
        print(f"🔄 INFINITE LOOP DETECTED: {log_info.path.name}")
        print(f"   Pattern repeated {count} times")

        # Create detection record
        detection = InfiniteLoopDetection(
            timestamp=datetime.now().isoformat(),
            log_file=log_info.path,
            severity=LoopSeverity.HIGH,
            pattern=pattern,
            repetition_count=count,
            growth_rate_mb_per_sec=log_info.growth_rate / 1024 / 1024,
            action_taken="truncate_and_kill"
        )

        # Take action
        self._find_and_kill_writer(log_info)
        self._truncate_log(log_info)

        self.detected_loops.append(detection)
        self.stats['loops_detected'] += 1

        # Notify via bus
        self._send_alert(log_info, f"Infinite loop detected ({count} repetitions)")

    def _truncate_log(self, log_info: LogFileInfo, emergency: bool = False) -> None:
        """Truncate a log file"""
        try:
            old_size = log_info.size

            # Backup last 1000 lines before truncating
            try:
                with open(log_info.path, 'rb') as f:
                    f.seek(max(0, old_size - 100000))
                    backup_content = f.read()

                backup_path = log_info.path.parent / f"{log_info.path.name}.backup"
                with open(backup_path, 'wb') as f:
                    f.write(backup_content)
            except:
                pass

            # Truncate the file
            with open(log_info.path, 'w') as f:
                f.truncate(0)

            space_saved = old_size
            self.stats['total_space_saved'] += space_saved
            self.stats['files_truncated'] += 1

            print(f"✂️  Truncated {log_info.path.name}")
            print(f"   Freed: {space_saved / 1024 / 1024:.1f}MB")

            # Update tracking
            log_info.size = 0
            log_info.last_check_size = 0
            log_info.pattern_counts.clear()

        except Exception as e:
            print(f"❌ Failed to truncate {log_info.path}: {e}")

    def _find_and_kill_writer(self, log_info: LogFileInfo) -> None:
        """Find and kill the process writing to the log file"""
        try:
            # Use lsof to find process
            result = subprocess.run(
                ['lsof', str(log_info.path)],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header

                for line in lines:
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            pid = int(parts[1])
                            process_name = parts[0]

                            # Don't kill critical system processes
                            if process_name.lower() in ['kernel', 'launchd', 'systemd']:
                                continue

                            if pid not in self.killed_processes:
                                print(f"🔪 Killing process: {process_name} (PID: {pid})")

                                # Try graceful kill first
                                subprocess.run(['kill', str(pid)], timeout=5)
                                time.sleep(1)

                                # Force kill if still running
                                subprocess.run(['kill', '-9', str(pid)], timeout=5, stderr=subprocess.DEVNULL)

                                self.killed_processes.add(pid)
                                self.stats['processes_killed'] += 1

                        except (ValueError, subprocess.TimeoutExpired):
                            continue

        except Exception as e:
            print(f"⚠️  Could not kill writer process: {e}")

    def _check_disk_space(self) -> None:
        """Check overall disk space"""
        try:
            result = subprocess.run(
                ['df', '-h', '/'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    parts = lines[1].split()
                    if len(parts) >= 5:
                        usage_str = parts[4].rstrip('%')
                        usage = int(usage_str)

                        if usage >= Config.DISK_CRITICAL_THRESHOLD:
                            print(f"🚨 CRITICAL DISK USAGE: {usage}%")
                            self._emergency_cleanup()

        except Exception as e:
            pass

    def _emergency_cleanup(self) -> None:
        """Emergency cleanup when disk is critically full"""
        print("🆘 EMERGENCY CLEANUP INITIATED")

        # Truncate all large log files immediately
        for log_info in self.monitored_files.values():
            if log_info.size > Config.WARNING_LOG_SIZE:
                self._truncate_log(log_info, emergency=True)

    def _send_warning(self, log_info: LogFileInfo) -> None:
        """Send warning about large log file"""
        if log_info.warnings_sent >= 3:  # Don't spam
            return

        size_mb = log_info.size / 1024 / 1024
        print(f"⚠️  Large log file: {log_info.path.name} ({size_mb:.1f}MB)")

        log_info.warnings_sent += 1

    def _send_alert(self, log_info: LogFileInfo, message: str) -> None:
        """Send alert via communication bus"""
        if not self.bus:
            return

        try:
            self.bus.send_message(
                sender_agent=self.agent_name,
                recipient_agent=None,  # Broadcast
                message_type=MessageType.NOTIFICATION,
                subject="Infinite Loop Detected",
                content={
                    'file': str(log_info.path),
                    'size_mb': log_info.size / 1024 / 1024,
                    'growth_rate': log_info.growth_rate,
                    'message': message
                },
                priority=MessagePriority.HIGH
            )
        except:
            pass

    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            'running': self.running,
            'monitored_files': len(self.monitored_files),
            'loops_detected': self.stats['loops_detected'],
            'files_truncated': self.stats['files_truncated'],
            'processes_killed': self.stats['processes_killed'],
            'space_saved_mb': self.stats['total_space_saved'] / 1024 / 1024,
        }

    def get_report(self) -> str:
        """Get detailed status report"""
        status = self.get_status()

        report = f"""
╔══════════════════════════════════════════════════════════════╗
║        INFINITE LOOP GUARDIAN - STATUS REPORT               ║
╚══════════════════════════════════════════════════════════════╝

📊 Statistics:
   • Monitoring: {status['monitored_files']} log files
   • Loops Detected: {status['loops_detected']}
   • Files Truncated: {status['files_truncated']}
   • Processes Killed: {status['processes_killed']}
   • Space Saved: {status['space_saved_mb']:.1f} MB

🔍 Active Monitors:
"""

        # Show top 5 largest files
        sorted_files = sorted(
            self.monitored_files.values(),
            key=lambda x: x.size,
            reverse=True
        )[:5]

        for log_info in sorted_files:
            size_mb = log_info.size / 1024 / 1024
            growth = log_info.growth_rate / 1024 / 1024
            status_icon = "🚨" if log_info.is_growing_rapidly else "✅"

            report += f"   {status_icon} {log_info.path.name}: {size_mb:.1f}MB "
            if growth > 0:
                report += f"(+{growth:.2f} MB/s)"
            report += "\n"

        return report


# ============================================================================
# Module Interface
# ============================================================================

_guardian_instance: Optional[InfiniteLoopGuardianAgent] = None

def get_guardian() -> InfiniteLoopGuardianAgent:
    """Get the guardian agent instance"""
    global _guardian_instance
    if _guardian_instance is None:
        _guardian_instance = InfiniteLoopGuardianAgent()
    return _guardian_instance


def start_guardian() -> InfiniteLoopGuardianAgent:
    """Start the guardian agent"""
    guardian = get_guardian()
    guardian.start()
    return guardian


if __name__ == "__main__":
    # Start the guardian
    print("🛡️  Starting Infinite Loop Guardian Agent...")

    guardian = start_guardian()

    try:
        # Keep running
        while True:
            time.sleep(30)
            print(guardian.get_report())

    except KeyboardInterrupt:
        print("\n\n🛑 Stopping guardian...")
        guardian.stop()
        print("\n" + guardian.get_report())
