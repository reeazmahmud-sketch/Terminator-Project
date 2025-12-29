#!/usr/bin/env python3
"""
TERMINATOR Intelligent Disk Cleanup Agent
Prevents disk space crises through smart, safe cleanup strategies
"""

import os
import asyncio
import subprocess
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import json

class DiskCleanupAgent:
    def __init__(self):
        self.project_root = Path.home() / "Desktop" / "Terminator-Project"
        self.cleanup_dir = self.project_root / ".cleanup"
        self.log_file = self.project_root / ".logs" / "disk_cleanup.log"
        self.report_file = self.cleanup_dir / "cleanup_report.json"
        
        self.cleanup_dir.mkdir(parents=True, exist_ok=True)
        (self.project_root / ".logs").mkdir(parents=True, exist_ok=True)
        
        # Thresholds
        self.warning_threshold = 80  # % disk usage
        self.critical_threshold = 90
        
        # Monitoring interval
        self.check_interval = 300  # 5 minutes
        
        # Safe cleanup targets (never touch user code/data)
        self.cleanup_strategies = {
            'logs': {
                'enabled': True,
                'max_size_mb': 100,  # Clean logs > 100MB
                'max_age_days': 30,  # Clean logs > 30 days
                'patterns': ['*.log', '*.log.*'],
                'exclude_paths': ['.health_checks', '.backups']
            },
            'node_modules': {
                'enabled': True,
                'max_age_days': 60,  # Clean node_modules not used in 60 days
                'patterns': ['node_modules'],
                'exclude_paths': []
            },
            'python_cache': {
                'enabled': True,
                'patterns': ['__pycache__', '*.pyc', '*.pyo', '.pytest_cache'],
                'exclude_paths': []
            },
            'build_artifacts': {
                'enabled': True,
                'max_age_days': 30,
                'patterns': ['dist', 'build', '*.egg-info', '.tox'],
                'exclude_paths': []
            },
            'temp_files': {
                'enabled': True,
                'patterns': ['.DS_Store', '*.tmp', '*.temp', 'Thumbs.db'],
                'exclude_paths': []
            },
            'old_backups': {
                'enabled': True,
                'max_age_days': 90,
                'patterns': ['*.backup', '*.bak', '*~'],
                'exclude_paths': ['.backups']  # Keep our own backups
            }
        }
        
        self.dry_run = False  # Set to True to preview without deleting
    
    def log(self, message: str, level: str = "INFO"):
        """Log message to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        try:
            with open(self.log_file, 'a') as f:
                f.write(log_entry + '\n')
        except Exception as e:
            print(f"Failed to write log: {e}")
    
    def get_disk_usage(self) -> Dict:
        """Get current disk usage statistics"""
        try:
            result = subprocess.run(
                ['df', '-H', '/System/Volumes/Data'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    parts = lines[1].split()
                    return {
                        'total': parts[1],
                        'used': parts[2],
                        'available': parts[3],
                        'percent': int(parts[4].rstrip('%')),
                        'status': 'ok' if int(parts[4].rstrip('%')) < self.warning_threshold else 
                                 'warning' if int(parts[4].rstrip('%')) < self.critical_threshold else 'critical'
                    }
        except Exception as e:
            self.log(f"Error getting disk usage: {e}", "ERROR")
        
        return {'percent': 0, 'status': 'unknown'}
    
    def get_dir_size(self, path: Path) -> int:
        """Get total size of directory in bytes"""
        total = 0
        try:
            for entry in path.rglob('*'):
                if entry.is_file():
                    try:
                        total += entry.stat().st_size
                    except:
                        pass
        except Exception as e:
            self.log(f"Error calculating size for {path}: {e}", "WARN")
        return total
    
    def format_size(self, bytes_size: int) -> str:
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f}{unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f}PB"
    
    def is_safe_to_delete(self, path: Path, strategy: Dict) -> bool:
        """Check if path is safe to delete"""
        # Never delete from excluded paths
        for exclude in strategy.get('exclude_paths', []):
            if exclude in str(path):
                return False
        
        # Check age if max_age_days is specified
        if 'max_age_days' in strategy:
            try:
                mtime = path.stat().st_mtime
                age_days = (datetime.now().timestamp() - mtime) / 86400
                if age_days < strategy['max_age_days']:
                    return False
            except:
                return False
        
        # Check size for logs
        if 'max_size_mb' in strategy and path.is_file():
            try:
                size_mb = path.stat().st_size / (1024 * 1024)
                if size_mb < strategy['max_size_mb']:
                    return False
            except:
                return False
        
        return True
    
    def find_cleanup_targets(self, search_path: Path, strategy_name: str) -> List[Tuple[Path, int]]:
        """Find files/folders matching cleanup strategy"""
        strategy = self.cleanup_strategies.get(strategy_name)
        if not strategy or not strategy.get('enabled'):
            return []
        
        targets = []
        
        try:
            for pattern in strategy['patterns']:
                for path in search_path.rglob(pattern):
                    if self.is_safe_to_delete(path, strategy):
                        size = self.get_dir_size(path) if path.is_dir() else path.stat().st_size
                        targets.append((path, size))
        except Exception as e:
            self.log(f"Error finding targets for {strategy_name}: {e}", "ERROR")
        
        return targets
    
    def delete_path(self, path: Path) -> bool:
        """Safely delete a file or directory"""
        if self.dry_run:
            self.log(f"[DRY RUN] Would delete: {path}")
            return True
        
        try:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            return True
        except Exception as e:
            self.log(f"Failed to delete {path}: {e}", "ERROR")
            return False
    
    def run_cleanup(self, search_paths: List[Path]) -> Dict:
        """Run cleanup strategies"""
        cleanup_report = {
            'timestamp': datetime.now().isoformat(),
            'disk_before': self.get_disk_usage(),
            'strategies': {},
            'total_freed': 0,
            'total_files': 0
        }
        
        for strategy_name in self.cleanup_strategies:
            self.log(f"Running {strategy_name} cleanup...")
            
            strategy_results = {
                'files_deleted': 0,
                'space_freed': 0,
                'errors': 0
            }
            
            for search_path in search_paths:
                if not search_path.exists():
                    continue
                
                targets = self.find_cleanup_targets(search_path, strategy_name)
                
                for target_path, size in targets:
                    if self.delete_path(target_path):
                        strategy_results['files_deleted'] += 1
                        strategy_results['space_freed'] += size
                    else:
                        strategy_results['errors'] += 1
            
            if strategy_results['files_deleted'] > 0:
                self.log(f"  ✅ {strategy_name}: Deleted {strategy_results['files_deleted']} items, "
                        f"freed {self.format_size(strategy_results['space_freed'])}")
            
            cleanup_report['strategies'][strategy_name] = strategy_results
            cleanup_report['total_freed'] += strategy_results['space_freed']
            cleanup_report['total_files'] += strategy_results['files_deleted']
        
        cleanup_report['disk_after'] = self.get_disk_usage()
        
        return cleanup_report
    
    def generate_cleanup_report(self, report: Dict):
        """Generate and save cleanup report"""
        # Save JSON report
        try:
            with open(self.report_file, 'w') as f:
                json.dump(report, f, indent=2)
        except Exception as e:
            self.log(f"Failed to save report: {e}", "ERROR")
        
        # Log summary
        self.log("━" * 70)
        self.log("📊 Cleanup Summary:")
        self.log(f"  Total files cleaned: {report['total_files']}")
        self.log(f"  Total space freed: {self.format_size(report['total_freed'])}")
        self.log(f"  Disk before: {report['disk_before']['percent']}% ({report['disk_before']['available']} free)")
        self.log(f"  Disk after: {report['disk_after']['percent']}% ({report['disk_after']['available']} free)")
        self.log("━" * 70)
    
    def emergency_cleanup(self):
        """Emergency cleanup for critical disk situations"""
        self.log("🚨 EMERGENCY CLEANUP TRIGGERED", "CRITICAL")
        
        # More aggressive cleanup
        desktop = Path.home() / "Desktop"
        downloads = Path.home() / "Downloads"
        
        search_paths = [desktop, downloads]
        
        # Enable all strategies
        for strategy in self.cleanup_strategies.values():
            strategy['enabled'] = True
        
        report = self.run_cleanup(search_paths)
        self.generate_cleanup_report(report)
    
    def routine_cleanup(self):
        """Routine cleanup when disk usage is high"""
        self.log("🧹 Running routine cleanup...")
        
        # Focus on Desktop projects
        desktop = Path.home() / "Desktop"
        search_paths = [desktop]
        
        report = self.run_cleanup(search_paths)
        self.generate_cleanup_report(report)
    
    async def monitor_loop(self):
        """Main monitoring loop"""
        self.log("🧹 Intelligent Disk Cleanup Agent started")
        self.log(f"Monitoring disk every {self.check_interval}s")
        self.log(f"Warning threshold: {self.warning_threshold}%")
        self.log(f"Critical threshold: {self.critical_threshold}%")
        
        while True:
            try:
                disk = self.get_disk_usage()
                
                if disk['status'] == 'critical':
                    self.log(f"🚨 CRITICAL: Disk at {disk['percent']}%", "CRITICAL")
                    self.emergency_cleanup()
                
                elif disk['status'] == 'warning':
                    self.log(f"⚠️ WARNING: Disk at {disk['percent']}%", "WARN")
                    self.routine_cleanup()
                
                else:
                    self.log(f"✅ Disk healthy: {disk['percent']}% used ({disk['available']} free)")
                
                await asyncio.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                self.log("⚠️ Disk Cleanup Agent stopped by user")
                break
            except Exception as e:
                self.log(f"❌ Error in monitor loop: {e}", "ERROR")
                await asyncio.sleep(60)

if __name__ == "__main__":
    cleanup = DiskCleanupAgent()
    asyncio.run(cleanup.monitor_loop())
