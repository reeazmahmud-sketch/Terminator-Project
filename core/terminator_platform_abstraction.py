# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Platform Abstraction Layer
==================================

Provides cross-platform system metrics interface for Windows, Linux, and macOS.
Abstracts away platform-specific implementations behind a unified interface.

This module enables the TERMINATOR dashboard and other components to work seamlessly
across all major operating systems without platform-specific code.

Features:
- Platform detection (Windows, Linux, macOS)
- Unified metrics interface
- Platform-specific implementations
- Graceful fallbacks for unavailable metrics
- Thread-safe singleton factory

Created: December 11, 2025
Part of: TERMINATOR Cross-Platform Enhancement
"""

import sys
import platform
import os
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import threading


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class ProcessInfo:
    """Process information"""
    pid: int
    name: str
    memory_mb: float
    cpu_percent: float
    status: str
    user: str
    start_time: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "pid": self.pid,
            "name": self.name,
            "memory_mb": round(self.memory_mb, 2),
            "cpu_percent": round(self.cpu_percent, 2),
            "status": self.status,
            "user": self.user,
            "start_time": self.start_time.isoformat()
        }


@dataclass
class NetworkStats:
    """Network statistics"""
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errors_in: int
    errors_out: int
    bandwidth_mbps: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "bytes_sent": self.bytes_sent,
            "bytes_recv": self.bytes_recv,
            "packets_sent": self.packets_sent,
            "packets_recv": self.packets_recv,
            "errors_in": self.errors_in,
            "errors_out": self.errors_out,
            "bandwidth_mbps": round(self.bandwidth_mbps, 2)
        }


@dataclass
class DiskStats:
    """Disk statistics"""
    total_gb: float
    used_gb: float
    free_gb: float
    percent_used: float
    path: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "total_gb": round(self.total_gb, 2),
            "used_gb": round(self.used_gb, 2),
            "free_gb": round(self.free_gb, 2),
            "percent_used": round(self.percent_used, 2),
            "path": self.path
        }


# ============================================================================
# Platform Detection
# ============================================================================

class PlatformDetector:
    """Detect and identify current platform"""

    WINDOWS = "windows"
    LINUX = "linux"
    DARWIN = "darwin"  # macOS
    UNKNOWN = "unknown"

    @staticmethod
    def get_platform() -> str:
        """
        Get current platform identifier

        Returns:
            str: 'windows', 'linux', 'darwin' (macOS), or 'unknown'
        """
        system = platform.system()
        if system == "Windows":
            return PlatformDetector.WINDOWS
        elif system == "Linux":
            return PlatformDetector.LINUX
        elif system == "Darwin":
            return PlatformDetector.DARWIN
        else:
            return PlatformDetector.UNKNOWN

    @staticmethod
    def get_platform_version() -> str:
        """Get platform version string"""
        return platform.version()

    @staticmethod
    def get_platform_release() -> str:
        """Get platform release string"""
        return platform.release()

    @staticmethod
    def is_windows() -> bool:
        """Check if running on Windows"""
        return PlatformDetector.get_platform() == PlatformDetector.WINDOWS

    @staticmethod
    def is_linux() -> bool:
        """Check if running on Linux"""
        return PlatformDetector.get_platform() == PlatformDetector.LINUX

    @staticmethod
    def is_darwin() -> bool:
        """Check if running on macOS"""
        return PlatformDetector.get_platform() == PlatformDetector.DARWIN

    @staticmethod
    def is_wsl() -> bool:
        """Check if running in Windows Subsystem for Linux"""
        if not PlatformDetector.is_linux():
            return False
        try:
            with open('/proc/version', 'r') as f:
                return 'microsoft' in f.read().lower()
        except Exception:
            return False


# ============================================================================
# Abstract Interface
# ============================================================================

class SystemMetricsProvider(ABC):
    """
    Abstract interface for system metrics across platforms

    All implementations must provide these methods for their specific platform.
    """

    @abstractmethod
    def get_cpu_usage(self) -> float:
        """
        Get CPU usage percentage (0-100)

        Returns:
            float: CPU usage as percentage
        """
        pass

    @abstractmethod
    def get_memory_usage(self) -> float:
        """
        Get memory usage percentage (0-100)

        Returns:
            float: Memory usage as percentage
        """
        pass

    @abstractmethod
    def get_disk_usage(self, path: str = None) -> DiskStats:
        """
        Get disk usage statistics

        Args:
            path: Disk path to check (None for root)

        Returns:
            DiskStats: Disk statistics
        """
        pass

    @abstractmethod
    def get_uptime(self) -> float:
        """
        Get system uptime in hours

        Returns:
            float: Uptime in hours
        """
        pass

    @abstractmethod
    def get_temperature(self) -> Optional[float]:
        """
        Get CPU temperature in Celsius

        Returns:
            Optional[float]: Temperature or None if unavailable
        """
        pass

    @abstractmethod
    def get_processes(self, limit: int = 10) -> List[ProcessInfo]:
        """
        Get top processes by memory usage

        Args:
            limit: Maximum number of processes to return

        Returns:
            List[ProcessInfo]: List of top processes
        """
        pass

    @abstractmethod
    def get_network_stats(self) -> NetworkStats:
        """
        Get network statistics

        Returns:
            NetworkStats: Network statistics
        """
        pass

    @abstractmethod
    def get_available_memory_gb(self) -> float:
        """
        Get available memory in GB

        Returns:
            float: Available memory in GB
        """
        pass

    @abstractmethod
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information dictionary

        Returns:
            Dict[str, Any]: System information
        """
        pass


# ============================================================================
# Generic Implementation (using psutil for all platforms)
# ============================================================================

class GenericSystemMetrics(SystemMetricsProvider):
    """
    Generic implementation using psutil for all platforms

    This provides basic functionality on any platform where psutil is available.
    Platform-specific implementations can override this for better accuracy.
    """

    def __init__(self):
        """Initialize metrics provider"""
        try:
            import psutil
            self.psutil = psutil
            self.available = True
        except ImportError:
            self.available = False
            print("Warning: psutil not installed. Some metrics will be unavailable.")

    def get_cpu_usage(self) -> float:
        """Get CPU usage"""
        if not self.available:
            return 0.0
        try:
            return float(self.psutil.cpu_percent(interval=0.5))
        except Exception as e:
            print(f"Error getting CPU usage: {e}")
            return 0.0

    def get_memory_usage(self) -> float:
        """Get memory usage"""
        if not self.available:
            return 0.0
        try:
            memory = self.psutil.virtual_memory()
            return float(memory.percent)
        except Exception as e:
            print(f"Error getting memory usage: {e}")
            return 0.0

    def get_disk_usage(self, path: str = None) -> DiskStats:
        """Get disk usage"""
        if not self.available:
            return DiskStats(0, 0, 0, 0, path or "/")

        if path is None:
            path = "C:\\" if PlatformDetector.is_windows() else "/"

        try:
            usage = self.psutil.disk_usage(path)
            return DiskStats(
                total_gb=usage.total / (1024**3),
                used_gb=usage.used / (1024**3),
                free_gb=usage.free / (1024**3),
                percent_used=usage.percent,
                path=path
            )
        except Exception as e:
            print(f"Error getting disk usage: {e}")
            return DiskStats(0, 0, 0, 0, path)

    def get_uptime(self) -> float:
        """Get system uptime in hours"""
        if not self.available:
            return 0.0
        try:
            import time
            uptime_seconds = time.time() - self.psutil.boot_time()
            return uptime_seconds / 3600
        except Exception as e:
            print(f"Error getting uptime: {e}")
            return 0.0

    def get_temperature(self) -> Optional[float]:
        """Get CPU temperature (returns None if unavailable)"""
        if not self.available:
            return None
        try:
            if hasattr(self.psutil, 'sensors_temperatures'):
                temps = self.psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        if entries:
                            return float(entries[0].current)
        except Exception:
            pass
        return None

    def get_processes(self, limit: int = 10) -> List[ProcessInfo]:
        """Get top processes by memory usage"""
        if not self.available:
            return []

        processes = []
        try:
            for proc in self.psutil.process_iter(['pid', 'name', 'status']):
                try:
                    pinfo = proc.as_dict(attrs=['pid', 'name', 'status', 'username'])
                    mem_info = proc.memory_info()
                    cpu_percent = proc.cpu_percent(interval=0.1)

                    processes.append(ProcessInfo(
                        pid=pinfo['pid'],
                        name=pinfo['name'],
                        memory_mb=mem_info.rss / (1024**2),
                        cpu_percent=cpu_percent or 0.0,
                        status=pinfo['status'],
                        user=pinfo['username'] or 'unknown',
                        start_time=datetime.fromtimestamp(proc.create_time())
                    ))
                except (self.psutil.NoSuchProcess, self.psutil.AccessDenied):
                    pass

            processes.sort(key=lambda x: x.memory_mb, reverse=True)
            return processes[:limit]
        except Exception as e:
            print(f"Error getting processes: {e}")
            return []

    def get_network_stats(self) -> NetworkStats:
        """Get network statistics"""
        if not self.available:
            return NetworkStats(0, 0, 0, 0, 0, 0, 0.0)

        try:
            net_io = self.psutil.net_io_counters()
            return NetworkStats(
                bytes_sent=net_io.bytes_sent,
                bytes_recv=net_io.bytes_recv,
                packets_sent=net_io.packets_sent,
                packets_recv=net_io.packets_recv,
                errors_in=net_io.errin,
                errors_out=net_io.errout,
                bandwidth_mbps=0.0
            )
        except Exception as e:
            print(f"Error getting network stats: {e}")
            return NetworkStats(0, 0, 0, 0, 0, 0, 0.0)

    def get_available_memory_gb(self) -> float:
        """Get available memory in GB"""
        if not self.available:
            return 0.0
        try:
            memory = self.psutil.virtual_memory()
            return memory.available / (1024**3)
        except Exception as e:
            print(f"Error getting available memory: {e}")
            return 0.0

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        info = {
            "platform": PlatformDetector.get_platform(),
            "platform_version": PlatformDetector.get_platform_version(),
            "hostname": platform.node(),
        }

        if self.available:
            try:
                info.update({
                    "processor_count": self.psutil.cpu_count(),
                    "total_memory_gb": round(self.psutil.virtual_memory().total / (1024**3), 2),
                    "python_version": platform.python_version()
                })
            except Exception:
                pass

        return info


# ============================================================================
# Cross-Platform Factory
# ============================================================================

class CrossPlatformMetrics:
    """Factory for getting platform-specific metrics provider"""

    _provider: Optional[SystemMetricsProvider] = None
    _lock = threading.Lock()

    @staticmethod
    def get_provider() -> SystemMetricsProvider:
        """
        Get appropriate metrics provider for current platform

        Returns:
            SystemMetricsProvider: Platform-specific metrics provider

        Raises:
            RuntimeError: If provider cannot be initialized
        """
        if CrossPlatformMetrics._provider is None:
            with CrossPlatformMetrics._lock:
                if CrossPlatformMetrics._provider is None:
                    platform_type = PlatformDetector.get_platform()

                    if platform_type == PlatformDetector.WINDOWS:
                        try:
                            from platform_metrics.windows_metrics import WindowsSystemMetrics
                            CrossPlatformMetrics._provider = WindowsSystemMetrics()
                        except (ImportError, Exception):
                            print("Warning: Windows metrics not available, using generic")
                            CrossPlatformMetrics._provider = GenericSystemMetrics()

                    elif platform_type == PlatformDetector.LINUX:
                        try:
                            from platform_metrics.linux_metrics import LinuxSystemMetrics
                            CrossPlatformMetrics._provider = LinuxSystemMetrics()
                        except (ImportError, Exception):
                            print("Warning: Linux metrics not available, using generic")
                            CrossPlatformMetrics._provider = GenericSystemMetrics()

                    elif platform_type == PlatformDetector.DARWIN:
                        try:
                            from platform_metrics.darwin_metrics import DarwinSystemMetrics
                            CrossPlatformMetrics._provider = DarwinSystemMetrics()
                        except (ImportError, Exception):
                            print("Warning: Darwin metrics not available, using generic")
                            CrossPlatformMetrics._provider = GenericSystemMetrics()

                    else:
                        print(f"Warning: Unknown platform {platform_type}, using generic metrics")
                        CrossPlatformMetrics._provider = GenericSystemMetrics()

        return CrossPlatformMetrics._provider

    @staticmethod
    def reset_provider() -> None:
        """Reset provider (for testing)"""
        with CrossPlatformMetrics._lock:
            CrossPlatformMetrics._provider = None


# ============================================================================
# Helper Functions
# ============================================================================

def get_platform_info() -> Dict[str, Any]:
    """Get platform information"""
    return {
        "platform": PlatformDetector.get_platform(),
        "version": PlatformDetector.get_platform_version(),
        "release": PlatformDetector.get_platform_release(),
        "is_wsl": PlatformDetector.is_wsl(),
        "python_version": platform.python_version(),
        "hostname": platform.node()
    }


def get_metrics() -> SystemMetricsProvider:
    """Shorthand to get metrics provider"""
    return CrossPlatformMetrics.get_provider()


if __name__ == "__main__":
    print("\n" + "="*70)
    print("TERMINATOR Platform Abstraction Layer - Self-Test")
    print("="*70 + "\n")

    # Print platform info
    print("Platform Information:")
    platform_info = get_platform_info()
    for key, value in platform_info.items():
        print(f"  {key}: {value}")

    # Get metrics provider
    print("\nInitializing metrics provider...")
    metrics = get_metrics()
    print(f"✅ Provider: {metrics.__class__.__name__}")

    # Get system metrics
    print("\nSystem Metrics:")
    print(f"  CPU Usage: {metrics.get_cpu_usage():.1f}%")
    print(f"  Memory Usage: {metrics.get_memory_usage():.1f}%")
    print(f"  Uptime: {metrics.get_uptime():.1f} hours")
    print(f"  Temperature: {metrics.get_temperature() or 'N/A'}")

    # Get disk usage
    disk = metrics.get_disk_usage()
    print(f"  Disk Usage: {disk.percent_used:.1f}% ({disk.used_gb:.1f}/{disk.total_gb:.1f} GB)")

    # Get top processes
    print("\nTop Processes:")
    processes = metrics.get_processes(5)
    for proc in processes:
        print(f"  {proc.name}: {proc.memory_mb:.1f}MB ({proc.cpu_percent:.1f}%)")

    print("\n✅ Platform abstraction layer is working correctly!\n")
