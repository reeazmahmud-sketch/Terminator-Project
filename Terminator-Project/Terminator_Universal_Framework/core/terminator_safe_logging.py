#!/usr/bin/env python3

# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR SAFE LOGGING SYSTEM
==========================
Prevents the 135GB log file disaster by:
1. Auto-rotating logs at 10MB
2. Keeping only last 5 log files  
3. Compression of old logs
4. Disk space checks before logging
"""

import os
import sys
import gzip
import shutil
from datetime import datetime
from pathlib import Path

# ============================================================================
# CONFIGURATION - SAFE LIMITS
# ============================================================================

TERMINATOR_ROOT = "/Users/reeazmahmud/Desktop/Terminator"
LOG_DIR = f"{TERMINATOR_ROOT}/logs/runtime"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB max per log file
MAX_LOG_FILES = 5  # Keep only 5 log files
DISK_MIN_FREE = 5 * 1024 * 1024 * 1024  # 5GB minimum free space

# ============================================================================
# SAFE LOGGER CLASS
# ============================================================================

class TerminatorSafeLogger:
    def __init__(self, name="terminator"):
        self.name = name
        self.log_dir = Path(LOG_DIR)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_log = self.log_dir / f"{name}.log"
        self._check_disk_space()
    
    def _check_disk_space(self):
        """Check if enough disk space before logging"""
        stat = os.statvfs(str(self.log_dir))
        free_space = stat.f_bavail * stat.f_frsize
        
        if free_space < DISK_MIN_FREE:
            self._emergency_cleanup()
            raise IOError(f"CRITICAL: Only {free_space/1e9:.1f}GB free! Logging disabled.")
        
        return free_space
    
    def _emergency_cleanup(self):
        """Emergency: Delete all logs if disk critically low"""
        print("⚠️  EMERGENCY: Cleaning up logs to free disk space!")
        for f in self.log_dir.glob("*.log*"):
            try:
                f.unlink()
                print(f"  Deleted: {f}")
            except:
                pass
    
    def _rotate_if_needed(self):
        """Rotate log if it exceeds max size"""
        if not self.current_log.exists():
            return
        
        if self.current_log.stat().st_size > MAX_LOG_SIZE:
            # Rotate: current.log -> current.log.1.gz
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            rotated = self.log_dir / f"{self.name}.log.{timestamp}.gz"
            
            # Compress and move
            with open(self.current_log, 'rb') as f_in:
                with gzip.open(rotated, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Clear current log
            self.current_log.write_text("")
            print(f"📦 Log rotated: {rotated.name}")
            
            # Clean old logs
            self._cleanup_old_logs()
    
    def _cleanup_old_logs(self):
        """Keep only last N log files"""
        logs = sorted(self.log_dir.glob(f"{self.name}.log.*.gz"), 
                     key=lambda x: x.stat().st_mtime, reverse=True)
        
        for old_log in logs[MAX_LOG_FILES:]:
            old_log.unlink()
            print(f"🗑️  Removed old log: {old_log.name}")
    
    def log(self, level, message):
        """Thread-safe logging with rotation"""
        self._check_disk_space()
        self._rotate_if_needed()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] [{level}] {message}\n"
        
        with open(self.current_log, 'a') as f:
            f.write(entry)
    
    def info(self, message):
        self.log("INFO", message)
    
    def error(self, message):
        self.log("ERROR", message)
    
    def warning(self, message):
        self.log("WARN", message)
    
    def debug(self, message):
        self.log("DEBUG", message)

# ============================================================================
# GLOBAL LOGGER INSTANCE
# ============================================================================

_logger = None

def get_logger(name="terminator"):
    global _logger
    if _logger is None:
        _logger = TerminatorSafeLogger(name)
    return _logger

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def log_info(msg): get_logger().info(msg)
def log_error(msg): get_logger().error(msg)
def log_warning(msg): get_logger().warning(msg)
def log_debug(msg): get_logger().debug(msg)

# ============================================================================
# STARTUP CHECK
# ============================================================================

def startup_check():
    """Run at Terminator startup to ensure safe logging"""
    logger = get_logger()
    
    # Check current log sizes
    total_size = sum(f.stat().st_size for f in Path(LOG_DIR).glob("*") if f.is_file())
    
    if total_size > 100 * 1024 * 1024:  # 100MB total logs
        logger._cleanup_old_logs()
        print(f"⚠️  Cleaned up {total_size/1e6:.1f}MB of logs")
    
    # Check disk space
    free_space = logger._check_disk_space()
    print(f"✅ Safe logging enabled. Disk free: {free_space/1e9:.1f}GB")
    
    return True

if __name__ == "__main__":
    print("Testing Safe Logging System...")
    startup_check()
    
    logger = get_logger()
    logger.info("Test message 1")
    logger.warning("Test warning")
    logger.error("Test error")
    
    print(f"✅ Log file: {logger.current_log}")
    print(f"✅ Size: {logger.current_log.stat().st_size} bytes")
