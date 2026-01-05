#!/usr/bin/env python3

# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Error Monitoring & Auto-Remediation Agent
Monitors Terminator application for errors, automatically diagnoses issues,
fixes problems, and adds necessary plugins for smooth operation.

Features:
- Real-time error detection and logging
- Intelligent error classification
- Automatic remediation with self-healing
- Plugin dependency management
- Health checkpoint creation
- Multi-level alerting system
"""

import os
import sys
import json
import subprocess
import traceback
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import threading
import time
from dataclasses import dataclass, asdict
from enum import Enum

# Set up safe logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
try:
    from terminator_safe_logging import SafeLogger
except ImportError:
    # Fallback basic logger if SafeLogger not available
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    SafeLogger = logging.getLogger

TERMINATOR_ROOT = Path("/Users/reeazmahmud/Desktop/Terminator")
LOGS_DIR = TERMINATOR_ROOT / "logs" / "error_monitor"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

logger = SafeLogger(__name__) if hasattr(SafeLogger, '__call__') else logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""
    CRITICAL = "CRITICAL"      # System down, immediate action needed
    HIGH = "HIGH"              # Major functionality broken
    MEDIUM = "MEDIUM"          # Degraded functionality
    LOW = "LOW"                # Minor issues
    INFO = "INFO"              # Informational only


class ErrorCategory(Enum):
    """Error categories for classification"""
    DEPENDENCY = "DEPENDENCY"           # Missing/broken packages
    CONFIGURATION = "CONFIGURATION"     # Config file issues
    OLLAMA = "OLLAMA"                   # Ollama service issues
    MEMORY = "MEMORY"                   # Memory/persistence issues
    VOICE = "VOICE"                     # Voice processing issues
    WEB_SERVER = "WEB_SERVER"           # Flask/web server issues
    TOOL = "TOOL"                       # Tool execution failures
    LLM = "LLM"                         # LLM model issues
    RUNTIME = "RUNTIME"                 # Runtime exceptions
    DISK = "DISK"                       # Disk space/I/O issues
    PERMISSION = "PERMISSION"           # Permission denied errors
    PORT = "PORT"                       # Port conflict issues
    UNKNOWN = "UNKNOWN"                 # Unclassified errors


@dataclass
class ErrorReport:
    """Structured error report"""
    timestamp: str
    error_id: str
    severity: ErrorSeverity
    category: ErrorCategory
    component: str
    error_message: str
    error_traceback: Optional[str]
    suggested_fix: str
    auto_fixed: bool
    fix_attempt_count: int
    created_checkpoint: bool


class PluginManager:
    """Manages plugin dependencies and installation"""

    def __init__(self):
        self.required_plugins = {
            # Core packages
            'langchain': {'version': '>=0.1.0', 'category': 'core'},
            'ollama': {'version': '>=0.1.0', 'category': 'core'},
            'flask': {'version': '>=2.0.0', 'category': 'web'},
            'python-dotenv': {'version': '>=0.19.0', 'category': 'core'},
            'pydantic': {'version': '>=2.0.0', 'category': 'core'},
            'requests': {'version': '>=2.28.0', 'category': 'network'},

            # Optional but recommended
            'edge-tts': {'version': '>=6.1.0', 'category': 'voice'},
            'google-cloud-text-to-speech': {'version': '>=2.14.0', 'category': 'voice'},
            'yt-dlp': {'version': '>=2023.0.0', 'category': 'tools'},
            'rclone': {'version': 'system', 'category': 'tools'},
            'ollama-python': {'version': '>=0.1.0', 'category': 'llm'},
        }

        self.installation_attempts = {}

    def check_installed_plugins(self) -> Dict[str, bool]:
        """Check which plugins are installed"""
        status = {}
        for plugin_name in self.required_plugins.keys():
            try:
                __import__(plugin_name.replace('-', '_'))
                status[plugin_name] = True
            except ImportError:
                status[plugin_name] = False
        return status

    def install_missing_plugins(self) -> Dict[str, bool]:
        """Install missing plugins"""
        status = self.check_installed_plugins()
        installed = {}

        for plugin_name, is_installed in status.items():
            if not is_installed:
                try:
                    logger.info(f"Installing missing plugin: {plugin_name}")
                    result = subprocess.run(
                        [sys.executable, '-m', 'pip', 'install', plugin_name, '--break-system-packages'],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    installed[plugin_name] = result.returncode == 0
                    if installed[plugin_name]:
                        logger.info(f"Successfully installed {plugin_name}")
                    else:
                        logger.warning(f"Failed to install {plugin_name}: {result.stderr}")
                except Exception as e:
                    logger.error(f"Error installing {plugin_name}: {str(e)}")
                    installed[plugin_name] = False
            else:
                installed[plugin_name] = True

        return installed


class ErrorDetector:
    """Detects and classifies errors from various sources"""

    def __init__(self):
        self.error_patterns = {
            ErrorCategory.DEPENDENCY: [
                r"ModuleNotFoundError",
                r"ImportError",
                r"No module named",
                r"cannot import name",
            ],
            ErrorCategory.OLLAMA: [
                r"ConnectionError.*ollama",
                r"Connection refused.*11434",
                r"Ollama.*not.*running",
                r"Failed to connect.*Ollama",
            ],
            ErrorCategory.CONFIGURATION: [
                r"FileNotFoundError.*\.json",
                r"JSONDecodeError",
                r"KeyError.*config",
                r"Missing required config",
            ],
            ErrorCategory.PORT: [
                r"Address already in use",
                r"Port.*already.*use",
                r"EADDRINUSE",
            ],
            ErrorCategory.PERMISSION: [
                r"Permission denied",
                r"PermissionError",
                r"Access denied",
            ],
            ErrorCategory.DISK: [
                r"No space left on device",
                r"Disk space",
                r"ENOSPC",
                r"out of disk",
            ],
            ErrorCategory.MEMORY: [
                r"MemoryError",
                r"out of memory",
                r"RuntimeError.*memory",
            ],
        }

    def classify_error(self, error_message: str, component: str = "unknown") -> Tuple[ErrorCategory, ErrorSeverity]:
        """Classify error by type and determine severity"""
        import re

        error_lower = error_message.lower()
        category = ErrorCategory.UNKNOWN
        severity = ErrorSeverity.MEDIUM

        for cat, patterns in self.error_patterns.items():
            for pattern in patterns:
                if re.search(pattern, error_message, re.IGNORECASE):
                    category = cat
                    break

        # Determine severity
        if "critical" in error_lower or "fatal" in error_lower:
            severity = ErrorSeverity.CRITICAL
        elif "error" in error_lower:
            if category in [ErrorCategory.DEPENDENCY, ErrorCategory.OLLAMA, ErrorCategory.DISK]:
                severity = ErrorSeverity.HIGH
            else:
                severity = ErrorSeverity.MEDIUM
        elif "warning" in error_lower:
            severity = ErrorSeverity.LOW

        return category, severity


class AutoRemediator:
    """Automatically fixes detected errors"""

    def __init__(self):
        self.remediation_steps = {
            ErrorCategory.DEPENDENCY: self._fix_dependency,
            ErrorCategory.OLLAMA: self._fix_ollama,
            ErrorCategory.PORT: self._fix_port_conflict,
            ErrorCategory.PERMISSION: self._fix_permission,
            ErrorCategory.CONFIGURATION: self._fix_configuration,
            ErrorCategory.DISK: self._fix_disk_space,
        }

        self.fix_attempts = {}

    def attempt_fix(self, error_report: ErrorReport) -> bool:
        """Attempt to automatically fix an error"""
        error_id = error_report.error_id

        if error_id not in self.fix_attempts:
            self.fix_attempts[error_id] = 0

        self.fix_attempts[error_id] += 1

        # Limit retry attempts to 3
        if self.fix_attempts[error_id] > 3:
            logger.warning(f"Max retry attempts reached for {error_id}")
            return False

        try:
            if error_report.category in self.remediation_steps:
                return self.remediation_steps[error_report.category](error_report)
            else:
                logger.info(f"No automatic fix available for {error_report.category}")
                return False
        except Exception as e:
            logger.error(f"Error during remediation: {str(e)}")
            return False

    def _fix_dependency(self, error_report: ErrorReport) -> bool:
        """Fix missing dependencies"""
        plugin_manager = PluginManager()
        results = plugin_manager.install_missing_plugins()
        return all(results.values())

    def _fix_ollama(self, error_report: ErrorReport) -> bool:
        """Fix Ollama connection issues"""
        try:
            # Check if Ollama is running
            result = subprocess.run(
                ["pgrep", "-l", "ollama"],
                capture_output=True,
                timeout=5
            )

            if result.returncode != 0:
                logger.info("Ollama not running, attempting to start...")
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                time.sleep(5)  # Wait for Ollama to start
                return True
            return True
        except Exception as e:
            logger.error(f"Failed to fix Ollama: {str(e)}")
            return False

    def _fix_port_conflict(self, error_report: ErrorReport) -> bool:
        """Fix port conflict issues"""
        try:
            # Extract port from error message (commonly port 5000)
            port = 5000
            import re
            port_match = re.search(r'port\s+(\d+)', error_report.error_message, re.IGNORECASE)
            if port_match:
                port = int(port_match.group(1))

            logger.info(f"Killing process on port {port}")
            subprocess.run(
                ["lsof", "-ti", f":{port}"],
                capture_output=True
            )

            result = subprocess.run(
                ["kill", "-9", f"$(lsof -ti :{port})"],
                shell=True,
                capture_output=True
            )
            return True
        except Exception as e:
            logger.error(f"Failed to fix port conflict: {str(e)}")
            return False

    def _fix_permission(self, error_report: ErrorReport) -> bool:
        """Fix permission denied errors"""
        try:
            import re
            # Try to extract filename from error
            file_match = re.search(r"'([^']+)'", error_report.error_message)
            if file_match:
                filepath = file_match.group(1)
                logger.info(f"Fixing permissions for {filepath}")
                subprocess.run(
                    ["chmod", "+x", filepath],
                    capture_output=True,
                    timeout=5
                )
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to fix permissions: {str(e)}")
            return False

    def _fix_configuration(self, error_report: ErrorReport) -> bool:
        """Fix configuration file issues"""
        try:
            config_path = TERMINATOR_ROOT / ".terminator_model_config.json"

            # Create default configuration if missing
            if not config_path.exists():
                default_config = {
                    "default_model": "phi4",
                    "auto_select": True,
                    "fallback_model": "qwen2",
                    "task_preferences": {
                        "coding": "codestral",
                        "math": "phi4",
                        "creative": "llama2",
                        "general": "qwen2"
                    },
                    "model_parameters": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "top_k": 40,
                        "max_tokens": 2048
                    }
                }

                with open(config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)

                logger.info(f"Created default configuration at {config_path}")
                return True
            return True
        except Exception as e:
            logger.error(f"Failed to fix configuration: {str(e)}")
            return False

    def _fix_disk_space(self, error_report: ErrorReport) -> bool:
        """Fix disk space issues"""
        try:
            logger.warning("Disk space low, running cleanup...")

            # Clean old log files
            logs_dir = TERMINATOR_ROOT / "logs"
            if logs_dir.exists():
                for log_file in logs_dir.glob("**/*.log.*"):
                    try:
                        log_file.unlink()
                        logger.info(f"Removed old log: {log_file}")
                    except:
                        pass

            # Clean old checkpoints
            checkpoints_dir = TERMINATOR_ROOT / "checkpoints"
            if checkpoints_dir.exists():
                checkpoint_dirs = sorted(
                    [d for d in checkpoints_dir.iterdir() if d.is_dir()],
                    key=lambda x: x.stat().st_mtime,
                    reverse=True
                )
                for old_checkpoint in checkpoint_dirs[3:]:  # Keep last 3
                    try:
                        import shutil
                        shutil.rmtree(old_checkpoint)
                        logger.info(f"Removed old checkpoint: {old_checkpoint}")
                    except:
                        pass

            return True
        except Exception as e:
            logger.error(f"Failed to fix disk space: {str(e)}")
            return False


class CheckpointManager:
    """Creates recovery checkpoints"""

    def create_checkpoint(self, error_report: ErrorReport, fix_successful: bool) -> bool:
        """Create a checkpoint after error detection/fix"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            checkpoint_dir = TERMINATOR_ROOT / "checkpoints" / f"error_recovery_{timestamp}"
            checkpoint_dir.mkdir(parents=True, exist_ok=True)

            # Save error report
            report_file = checkpoint_dir / "error_report.json"
            report_data = asdict(error_report)
            report_data['severity'] = report_data['severity'].value
            report_data['category'] = report_data['category'].value

            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)

            # Save system state
            state_file = checkpoint_dir / "system_state.json"
            system_state = {
                'timestamp': datetime.now().isoformat(),
                'disk_usage': self._get_disk_usage(),
                'running_processes': self._get_running_processes(),
                'terminator_config_exists': (TERMINATOR_ROOT / ".terminator_model_config.json").exists(),
            }

            with open(state_file, 'w') as f:
                json.dump(system_state, f, indent=2)

            # Create restore script
            restore_script = checkpoint_dir / "restore.sh"
            restore_script.write_text(f"""#!/bin/bash
# Restore from error recovery checkpoint
echo "Restoring from checkpoint: {timestamp}"
# Add restoration logic here
""")
            restore_script.chmod(0o755)

            logger.info(f"Created checkpoint: {checkpoint_dir}")
            return True
        except Exception as e:
            logger.error(f"Failed to create checkpoint: {str(e)}")
            return False

    def _get_disk_usage(self) -> Dict[str, Any]:
        """Get current disk usage"""
        try:
            result = subprocess.run(
                ["df", "-h", "/"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return {'raw': result.stdout}
        except:
            return {}

    def _get_running_processes(self) -> List[str]:
        """Get relevant running processes"""
        try:
            result = subprocess.run(
                ["pgrep", "-a", "python"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip().split('\n')[:10]  # First 10
        except:
            return []


class TerminatorErrorMonitorAgent:
    """Main error monitoring agent"""

    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self.running = False
        self.monitor_thread = None

        self.detector = ErrorDetector()
        self.remediator = AutoRemediator()
        self.plugin_manager = PluginManager()
        self.checkpoint_manager = CheckpointManager()

        self.error_history: List[ErrorReport] = []
        self.max_history = 1000

    def start_monitoring(self) -> None:
        """Start the error monitoring agent"""
        if self.running:
            logger.warning("Monitor already running")
            return

        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("Terminator Error Monitor Agent started")

    def stop_monitoring(self) -> None:
        """Stop the error monitoring agent"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Terminator Error Monitor Agent stopped")

    def _monitor_loop(self) -> None:
        """Main monitoring loop"""
        while self.running:
            try:
                self._check_system_health()
                self._check_log_files()
                self._verify_dependencies()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in monitor loop: {str(e)}")

    def _check_system_health(self) -> None:
        """Check overall system health"""
        # Check if Terminator components are running
        try:
            result = subprocess.run(
                ["pgrep", "-f", "terminator|agent|ollama"],
                capture_output=True,
                timeout=5
            )

            if result.returncode != 0:
                self._report_error(
                    component="system",
                    error_message="Terminator process not detected",
                    category=ErrorCategory.RUNTIME,
                    severity=ErrorSeverity.HIGH
                )
        except Exception as e:
            logger.error(f"Health check error: {str(e)}")

    def _check_log_files(self) -> None:
        """Check log files for errors"""
        try:
            log_dir = TERMINATOR_ROOT / "logs"
            if log_dir.exists():
                for log_file in log_dir.glob("**/*.log"):
                    try:
                        with open(log_file, 'r', errors='ignore') as f:
                            lines = f.readlines()[-100:]  # Last 100 lines

                        for line in lines:
                            if any(keyword in line.upper() for keyword in ['ERROR', 'CRITICAL', 'FAILED']):
                                self._report_error(
                                    component=log_file.name,
                                    error_message=line.strip(),
                                    category=ErrorCategory.RUNTIME,
                                    severity=ErrorSeverity.MEDIUM
                                )
                    except Exception as e:
                        logger.debug(f"Error checking log file {log_file}: {str(e)}")
        except Exception as e:
            logger.error(f"Log file check error: {str(e)}")

    def _verify_dependencies(self) -> None:
        """Verify all critical dependencies are installed"""
        status = self.plugin_manager.check_installed_plugins()
        critical_plugins = ['langchain', 'ollama', 'flask', 'pydantic']

        for plugin in critical_plugins:
            if plugin in status and not status[plugin]:
                self._report_error(
                    component="dependency",
                    error_message=f"Missing critical dependency: {plugin}",
                    category=ErrorCategory.DEPENDENCY,
                    severity=ErrorSeverity.HIGH
                )

    def _report_error(self, component: str, error_message: str,
                      category: ErrorCategory = None, severity: ErrorSeverity = None) -> ErrorReport:
        """Report and handle an error"""
        import uuid

        error_id = f"ERR-{uuid.uuid4().hex[:8].upper()}"

        if category is None or severity is None:
            detected_category, detected_severity = self.detector.classify_error(error_message, component)
            category = category or detected_category
            severity = severity or detected_severity

        # Create error report
        error_report = ErrorReport(
            timestamp=datetime.now().isoformat(),
            error_id=error_id,
            severity=severity,
            category=category,
            component=component,
            error_message=error_message,
            error_traceback=None,
            suggested_fix=self._get_suggested_fix(category),
            auto_fixed=False,
            fix_attempt_count=0,
            created_checkpoint=False
        )

        logger.warning(f"[{error_id}] {severity.value} - {category.value}: {error_message}")

        # Attempt automatic fix
        if severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]:
            if self.remediator.attempt_fix(error_report):
                error_report.auto_fixed = True
                logger.info(f"[{error_id}] Auto-fix successful")
            else:
                error_report.fix_attempt_count = self.remediator.fix_attempts.get(error_id, 0)

        # Create checkpoint
        if severity == ErrorSeverity.CRITICAL:
            error_report.created_checkpoint = self.checkpoint_manager.create_checkpoint(
                error_report,
                error_report.auto_fixed
            )

        # Store in history
        self.error_history.append(error_report)
        if len(self.error_history) > self.max_history:
            self.error_history = self.error_history[-self.max_history:]

        # Save error log
        self._save_error_report(error_report)

        return error_report

    def _get_suggested_fix(self, category: ErrorCategory) -> str:
        """Get suggested fix for error category"""
        fixes = {
            ErrorCategory.DEPENDENCY: "Run: pip install -r requirements.txt --break-system-packages",
            ErrorCategory.OLLAMA: "Run: ollama serve (in separate terminal)",
            ErrorCategory.PORT: "Kill conflicting process: lsof -ti :PORT | xargs kill -9",
            ErrorCategory.PERMISSION: "Run: chmod +x <filename>",
            ErrorCategory.CONFIGURATION: "Check .terminator_model_config.json exists and is valid",
            ErrorCategory.DISK: "Free up disk space: rm -rf logs/*.log.* old backups",
        }
        return fixes.get(category, "Check logs for more details")

    def _save_error_report(self, error_report: ErrorReport) -> None:
        """Save error report to file"""
        try:
            report_file = LOGS_DIR / f"error_{error_report.error_id}.json"
            report_data = asdict(error_report)
            report_data['severity'] = report_data['severity'].value
            report_data['category'] = report_data['category'].value

            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save error report: {str(e)}")

    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        return {
            'timestamp': datetime.now().isoformat(),
            'running': self.running,
            'total_errors': len(self.error_history),
            'critical_errors': len([e for e in self.error_history if e.severity == ErrorSeverity.CRITICAL]),
            'auto_fixed_count': len([e for e in self.error_history if e.auto_fixed]),
            'dependencies': self.plugin_manager.check_installed_plugins(),
            'recent_errors': [
                {
                    'id': e.error_id,
                    'timestamp': e.timestamp,
                    'severity': e.severity.value,
                    'category': e.category.value,
                    'message': e.error_message[:100],
                }
                for e in self.error_history[-10:]
            ]
        }


# Global agent instance
_agent_instance: Optional[TerminatorErrorMonitorAgent] = None


def get_error_monitor_agent() -> TerminatorErrorMonitorAgent:
    """Get or create the global error monitor agent"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = TerminatorErrorMonitorAgent(check_interval=60)
    return _agent_instance


def start_error_monitoring() -> None:
    """Start error monitoring"""
    agent = get_error_monitor_agent()
    agent.start_monitoring()


def stop_error_monitoring() -> None:
    """Stop error monitoring"""
    agent = get_error_monitor_agent()
    agent.stop_monitoring()


def get_monitor_status() -> Dict[str, Any]:
    """Get current monitor status"""
    agent = get_error_monitor_agent()
    return agent.get_health_status()


if __name__ == "__main__":
    # Test the error monitor agent
    agent = get_error_monitor_agent()
    agent.start_monitoring()

    logger.info("Error Monitor Agent is running. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping error monitor agent...")
        agent.stop_monitoring()
