#!/usr/bin/env python3
"""
TERMINATOR Smart Notification System
Intelligent macOS notifications for important system events
"""

import os
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import re

class NotificationLevel:
    """Notification priority levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class SmartNotificationSystem:
    def __init__(self):
        self.project_root = Path.home() / "Desktop" / "Terminator-Project"
        self.config_file = self.project_root / ".notifications" / "config.json"
        self.state_file = self.project_root / ".notifications" / "notification_state.json"
        self.log_file = self.project_root / ".logs" / "notifications.log"
        
        (self.project_root / ".notifications").mkdir(parents=True, exist_ok=True)
        (self.project_root / ".logs").mkdir(parents=True, exist_ok=True)
        
        # Notification configuration
        self.config = {
            'enabled': True,
            'notify_on': {
                'agent_crash': True,
                'agent_restart': True,
                'disk_warning': True,
                'disk_critical': True,
                'git_backup_fail': True,
                'health_issues': True,
                'new_project_detected': True,
                'cleanup_performed': True
            },
            'quiet_hours': {
                'enabled': False,
                'start': '22:00',
                'end': '08:00'
            },
            'notification_cooldown': 300,  # seconds (5 min)
            'group_similar': True
        }
        
        # Load saved config
        self.load_config()
        
        # Notification state (for deduplication)
        self.notification_history: Dict[str, datetime] = {}
        self.load_state()
        
        # Monitored log files
        self.monitored_logs = {
            'health_monitor': self.project_root / '.logs' / 'health_monitor.log',
            'git_backup': self.project_root / '.logs' / 'git_backup.log',
            'disk_cleanup': self.project_root / '.logs' / 'disk_cleanup.log',
            'project_index': self.project_root / '.logs' / 'project_index_manager.log'
        }
        
        # Track log positions
        self.log_positions: Dict[str, int] = {}
        
        self.check_interval = 30  # Check logs every 30 seconds
    
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
    
    def load_config(self):
        """Load notification configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
                self.log("Loaded notification config")
            except Exception as e:
                self.log(f"Failed to load config: {e}", "ERROR")
    
    def save_config(self):
        """Save notification configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.log(f"Failed to save config: {e}", "ERROR")
    
    def load_state(self):
        """Load notification state"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    # Convert ISO strings back to datetime
                    self.notification_history = {
                        k: datetime.fromisoformat(v) for k, v in state.get('history', {}).items()
                    }
                    self.log_positions = state.get('log_positions', {})
            except Exception as e:
                self.log(f"Failed to load state: {e}", "ERROR")
    
    def save_state(self):
        """Save notification state"""
        try:
            state = {
                'history': {k: v.isoformat() for k, v in self.notification_history.items()},
                'log_positions': self.log_positions
            }
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.log(f"Failed to save state: {e}", "ERROR")
    
    def is_quiet_hours(self) -> bool:
        """Check if we're in quiet hours"""
        if not self.config['quiet_hours']['enabled']:
            return False
        
        now = datetime.now().time()
        start = datetime.strptime(self.config['quiet_hours']['start'], '%H:%M').time()
        end = datetime.strptime(self.config['quiet_hours']['end'], '%H:%M').time()
        
        if start < end:
            return start <= now <= end
        else:  # Quiet hours span midnight
            return now >= start or now <= end
    
    def should_notify(self, notification_key: str) -> bool:
        """Check if we should send this notification (cooldown check)"""
        if notification_key in self.notification_history:
            last_sent = self.notification_history[notification_key]
            cooldown = timedelta(seconds=self.config['notification_cooldown'])
            if datetime.now() - last_sent < cooldown:
                return False
        
        return True
    
    def send_notification(self, title: str, message: str, level: str = NotificationLevel.INFO):
        """Send macOS notification"""
        if not self.config['enabled']:
            return
        
        if self.is_quiet_hours():
            self.log(f"Skipping notification (quiet hours): {title}")
            return
        
        # Create notification key for deduplication
        notification_key = f"{title}:{message}"
        
        if self.config['group_similar'] and not self.should_notify(notification_key):
            self.log(f"Skipping duplicate notification: {title}")
            return
        
        # Choose notification icon based on level
        if level == NotificationLevel.CRITICAL:
            icon = "🚨"
            sound = "Basso"
        elif level == NotificationLevel.WARNING:
            icon = "⚠️"
            sound = "Funk"
        else:
            icon = "ℹ️"
            sound = "Glass"
        
        try:
            # Use osascript to send macOS notification
            script = f'''
            display notification "{message}" with title "{icon} TERMINATOR" subtitle "{title}" sound name "{sound}"
            '''
            
            subprocess.run(['osascript', '-e', script], check=True, capture_output=True)
            
            self.log(f"📬 Sent notification: {title} - {message}")
            self.notification_history[notification_key] = datetime.now()
            self.save_state()
            
        except Exception as e:
            self.log(f"Failed to send notification: {e}", "ERROR")
    
    def parse_log_line(self, line: str, log_name: str) -> Optional[Dict]:
        """Parse log line and extract event information"""
        # Match log pattern: [timestamp] [LEVEL] message
        match = re.match(r'\[([^\]]+)\] \[([^\]]+)\] (.+)', line)
        if not match:
            return None
        
        timestamp_str, level, message = match.groups()
        
        event = {
            'timestamp': timestamp_str,
            'level': level,
            'message': message,
            'source': log_name
        }
        
        return event
    
    def analyze_event(self, event: Dict):
        """Analyze event and send notification if needed"""
        message = event['message'].lower()
        level = event['level']
        source = event['source']
        
        # Agent crash/restart detection
        if 'crashed' in message or 'failed to start' in message:
            if self.config['notify_on']['agent_crash']:
                self.send_notification(
                    f"Agent Failure - {source}",
                    event['message'][:100],
                    NotificationLevel.CRITICAL
                )
        
        elif 'restarted' in message or 'auto-restart' in message:
            if self.config['notify_on']['agent_restart']:
                self.send_notification(
                    f"Agent Restarted - {source}",
                    event['message'][:100],
                    NotificationLevel.WARNING
                )
        
        # Disk warnings
        elif 'critical' in message and 'disk' in message:
            if self.config['notify_on']['disk_critical']:
                self.send_notification(
                    "Critical Disk Space",
                    event['message'][:100],
                    NotificationLevel.CRITICAL
                )
        
        elif 'warning' in message and 'disk' in message:
            if self.config['notify_on']['disk_warning']:
                self.send_notification(
                    "Disk Space Warning",
                    event['message'][:100],
                    NotificationLevel.WARNING
                )
        
        # Cleanup performed
        elif 'cleanup summary' in message or 'freed' in message:
            if self.config['notify_on']['cleanup_performed']:
                self.send_notification(
                    "Disk Cleanup Completed",
                    event['message'][:100],
                    NotificationLevel.INFO
                )
        
        # New project detected
        elif 'detected new project' in message:
            if self.config['notify_on']['new_project_detected']:
                # Extract project name
                project_match = re.search(r'project:\s*(\w+)', message)
                project_name = project_match.group(1) if project_match else "Unknown"
                self.send_notification(
                    "New Project Detected",
                    f"Added {project_name} to index",
                    NotificationLevel.INFO
                )
        
        # Git backup failures
        elif 'failed to' in message and source == 'git_backup':
            if self.config['notify_on']['git_backup_fail']:
                self.send_notification(
                    "Git Backup Failed",
                    event['message'][:100],
                    NotificationLevel.WARNING
                )
        
        # Health issues
        elif level in ['ERROR', 'CRITICAL']:
            if self.config['notify_on']['health_issues']:
                self.send_notification(
                    f"System Issue - {source}",
                    event['message'][:100],
                    NotificationLevel.WARNING if level == 'ERROR' else NotificationLevel.CRITICAL
                )
    
    def monitor_log_file(self, log_name: str, log_path: Path):
        """Monitor a log file for new entries"""
        if not log_path.exists():
            return
        
        try:
            # Get current file size
            current_size = log_path.stat().st_size
            
            # Get last known position
            last_position = self.log_positions.get(str(log_path), 0)
            
            # If file shrunk or is new, start from beginning
            if current_size < last_position:
                last_position = 0
            
            # Read new content
            if current_size > last_position:
                with open(log_path, 'r') as f:
                    f.seek(last_position)
                    new_lines = f.readlines()
                    
                    # Process each new line
                    for line in new_lines:
                        event = self.parse_log_line(line.strip(), log_name)
                        if event:
                            self.analyze_event(event)
                    
                    # Update position
                    self.log_positions[str(log_path)] = f.tell()
                    self.save_state()
        
        except Exception as e:
            self.log(f"Error monitoring {log_name}: {e}", "ERROR")
    
    async def monitor_loop(self):
        """Main monitoring loop"""
        self.log("📬 Smart Notification System started")
        self.log(f"Monitoring {len(self.monitored_logs)} log files")
        
        # Send startup notification
        self.send_notification(
            "TERMINATOR Online",
            "All autonomous agents operational",
            NotificationLevel.INFO
        )
        
        while True:
            try:
                # Monitor all log files
                for log_name, log_path in self.monitored_logs.items():
                    self.monitor_log_file(log_name, log_path)
                
                await asyncio.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                self.log("⚠️ Notification System stopped by user")
                self.send_notification(
                    "TERMINATOR Shutdown",
                    "Notification system stopped",
                    NotificationLevel.WARNING
                )
                break
            except Exception as e:
                self.log(f"❌ Error in monitor loop: {e}", "ERROR")
                await asyncio.sleep(60)

if __name__ == "__main__":
    notifier = SmartNotificationSystem()
    asyncio.run(notifier.monitor_loop())
