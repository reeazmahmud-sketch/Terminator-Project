#!/usr/bin/env python3
"""
TERMINATOR Agent Health Monitor & Auto-Restart System
Ensures 24/7 uptime by monitoring and auto-restarting failed agents
"""

import os
import asyncio
import time
import subprocess
import psutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import json

class AgentRegistry:
    """Registry of all agents that should be monitored"""
    
    AGENTS = {
        'project_index_manager': {
            'name': 'Project Index Manager',
            'script': 'core/terminator_project_index_manager.py',
            'pid_file': '.logs/project_index_manager.pid',
            'log_file': '.logs/project_index_manager.log',
            'critical': True,
            'auto_restart': True,
            'max_restarts': 5,
            'restart_delay': 10,  # seconds
        },
        # Add more agents here as needed
        'auto_git_backup': {
            'name': 'Auto-Git Backup',
            'script': 'core/terminator_auto_git_backup.py',
            'pid_file': '.logs/git_backup.pid',
            'log_file': '.logs/git_backup.log',
            'critical': True,
            'auto_restart': True,
            'max_restarts': 5,
            'restart_delay': 10,
        },
        'intelligent_disk_cleanup': {
            'name': 'Intelligent Disk Cleanup',
            'script': 'core/terminator_intelligent_disk_cleanup.py',
            'pid_file': '.logs/disk_cleanup.pid',
            'log_file': '.logs/disk_cleanup.log',
            'critical': True,
            'auto_restart': True,
            'max_restarts': 5,
            'restart_delay': 10,
        },
        'smart_notifications': {
            'name': 'Smart Notification System',
            'script': 'core/terminator_smart_notifications.py',
            'pid_file': '.logs/notifications.pid',
            'log_file': '.logs/notifications.log',
            'critical': False,  # Not critical, but nice to have
            'auto_restart': True,
            'max_restarts': 5,
            'restart_delay': 10,
        },
        'auto_doc_updater': {
            'name': 'Auto-Documentation Updater',
            'script': 'core/terminator_auto_doc_updater.py',
            'pid_file': '.logs/auto_doc.pid',
            'log_file': '.logs/auto_doc.log',
            'critical': False,
            'auto_restart': True,
            'max_restarts': 5,
            'restart_delay': 10,
        },
    }

class AgentHealthMonitor:
    def __init__(self):
        self.project_root = Path.home() / "Desktop" / "Terminator-Project"
        self.health_dir = self.project_root / ".health_checks"
        self.health_file = self.health_dir / "agent_health_status.json"
        self.report_file = self.health_dir / "agent_health_report.txt"
        self.log_file = self.project_root / ".logs" / "health_monitor.log"
        
        self.health_dir.mkdir(parents=True, exist_ok=True)
        (self.project_root / ".logs").mkdir(parents=True, exist_ok=True)
        
        self.agent_status: Dict[str, Dict] = {}
        self.check_interval = 60  # Check every 60 seconds
        
        self.load_health_status()
    
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
    
    def load_health_status(self):
        """Load previous health status from disk"""
        if self.health_file.exists():
            try:
                with open(self.health_file, 'r') as f:
                    self.agent_status = json.load(f)
                self.log(f"Loaded health status for {len(self.agent_status)} agents")
            except Exception as e:
                self.log(f"Failed to load health status: {e}", "ERROR")
                self.agent_status = {}
        else:
            self.agent_status = {}
    
    def save_health_status(self):
        """Save current health status to disk"""
        try:
            with open(self.health_file, 'w') as f:
                json.dump(self.agent_status, f, indent=2)
        except Exception as e:
            self.log(f"Failed to save health status: {e}", "ERROR")
    
    def is_process_running(self, pid: int) -> bool:
        """Check if a process is running"""
        try:
            process = psutil.Process(pid)
            return process.is_running() and process.status() != psutil.STATUS_ZOMBIE
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
    
    def get_agent_pid(self, agent_id: str) -> Optional[int]:
        """Get PID of an agent from its PID file"""
        agent_config = AgentRegistry.AGENTS.get(agent_id)
        if not agent_config:
            return None
        
        pid_file = self.project_root / agent_config['pid_file']
        if not pid_file.exists():
            return None
        
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            return pid
        except (ValueError, IOError):
            return None
    
    def start_agent(self, agent_id: str) -> bool:
        """Start an agent"""
        agent_config = AgentRegistry.AGENTS.get(agent_id)
        if not agent_config:
            self.log(f"Unknown agent: {agent_id}", "ERROR")
            return False
        
        script_path = self.project_root / agent_config['script']
        if not script_path.exists():
            self.log(f"Agent script not found: {script_path}", "ERROR")
            return False
        
        try:
            # Start agent in background
            log_file = self.project_root / agent_config['log_file']
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(log_file, 'a') as log:
                process = subprocess.Popen(
                    ['python3', str(script_path)],
                    stdout=log,
                    stderr=log,
                    start_new_session=True
                )
            
            # Give it a moment to start
            time.sleep(2)
            
            # Verify it's running
            if process.poll() is None:
                # Save PID
                pid_file = self.project_root / agent_config['pid_file']
                pid_file.parent.mkdir(parents=True, exist_ok=True)
                with open(pid_file, 'w') as f:
                    f.write(str(process.pid))
                
                self.log(f"✅ Started {agent_config['name']} (PID: {process.pid})")
                return True
            else:
                self.log(f"❌ Failed to start {agent_config['name']}", "ERROR")
                return False
        
        except Exception as e:
            self.log(f"❌ Error starting {agent_config['name']}: {e}", "ERROR")
            return False
    
    def check_agent_health(self, agent_id: str) -> Dict:
        """Check health of a specific agent"""
        agent_config = AgentRegistry.AGENTS.get(agent_id)
        if not agent_config:
            return {'status': 'unknown', 'message': 'Agent not in registry'}
        
        # Initialize status if not exists
        if agent_id not in self.agent_status:
            self.agent_status[agent_id] = {
                'restart_count': 0,
                'last_restart': None,
                'last_seen': None,
                'consecutive_failures': 0,
            }
        
        status = self.agent_status[agent_id]
        pid = self.get_agent_pid(agent_id)
        
        if pid and self.is_process_running(pid):
            # Agent is running
            status['last_seen'] = datetime.now().isoformat()
            status['consecutive_failures'] = 0
            return {
                'status': 'running',
                'pid': pid,
                'uptime': self.get_process_uptime(pid),
                'message': f"✅ {agent_config['name']} is healthy"
            }
        else:
            # Agent is not running
            status['consecutive_failures'] += 1
            
            # Should we auto-restart?
            if agent_config['auto_restart']:
                max_restarts = agent_config['max_restarts']
                if status['restart_count'] < max_restarts:
                    # Calculate backoff delay
                    delay = agent_config['restart_delay'] * (2 ** status['consecutive_failures'])
                    delay = min(delay, 300)  # Max 5 minutes
                    
                    self.log(f"⚠️ {agent_config['name']} is down. Restarting in {delay}s (attempt {status['restart_count'] + 1}/{max_restarts})...", "WARN")
                    time.sleep(delay)
                    
                    if self.start_agent(agent_id):
                        status['restart_count'] += 1
                        status['last_restart'] = datetime.now().isoformat()
                        self.save_health_status()
                        
                        return {
                            'status': 'restarted',
                            'message': f"🔄 {agent_config['name']} auto-restarted (attempt {status['restart_count']})"
                        }
                    else:
                        return {
                            'status': 'failed',
                            'message': f"❌ {agent_config['name']} restart failed"
                        }
                else:
                    self.log(f"❌ {agent_config['name']} exceeded max restarts ({max_restarts})", "CRITICAL")
                    return {
                        'status': 'critical',
                        'message': f"❌ {agent_config['name']} CRITICAL - Max restarts exceeded"
                    }
            else:
                return {
                    'status': 'stopped',
                    'message': f"⚠️ {agent_config['name']} is stopped (auto-restart disabled)"
                }
    
    def get_process_uptime(self, pid: int) -> str:
        """Get uptime of a process"""
        try:
            process = psutil.Process(pid)
            create_time = process.create_time()
            uptime_seconds = time.time() - create_time
            
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            
            if hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        except:
            return "unknown"
    
    def generate_health_report(self) -> str:
        """Generate human-readable health report"""
        report_lines = []
        report_lines.append("=" * 70)
        report_lines.append("TERMINATOR AGENT HEALTH REPORT")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("=" * 70)
        report_lines.append("")
        
        total_agents = len(AgentRegistry.AGENTS)
        running = 0
        critical = 0
        
        for agent_id, agent_config in AgentRegistry.AGENTS.items():
            pid = self.get_agent_pid(agent_id)
            status = self.agent_status.get(agent_id, {})
            
            if pid and self.is_process_running(pid):
                running += 1
                uptime = self.get_process_uptime(pid)
                report_lines.append(f"✅ {agent_config['name']}")
                report_lines.append(f"   PID: {pid} | Uptime: {uptime}")
            else:
                critical += 1
                report_lines.append(f"❌ {agent_config['name']} - NOT RUNNING")
                if status.get('restart_count', 0) > 0:
                    report_lines.append(f"   Restarts: {status['restart_count']} | Last: {status.get('last_restart', 'N/A')}")
            
            report_lines.append("")
        
        report_lines.append("=" * 70)
        report_lines.append(f"Summary: {running}/{total_agents} agents running")
        if critical > 0:
            report_lines.append(f"⚠️ WARNING: {critical} agents are down!")
        report_lines.append("=" * 70)
        
        report = '\n'.join(report_lines)
        
        # Save to file
        try:
            with open(self.report_file, 'w') as f:
                f.write(report)
        except Exception as e:
            self.log(f"Failed to save report: {e}", "ERROR")
        
        return report
    
    async def monitor_loop(self):
        """Main monitoring loop"""
        self.log("🏥 Agent Health Monitor started")
        self.log(f"Monitoring {len(AgentRegistry.AGENTS)} agents every {self.check_interval}s")
        
        while True:
            try:
                self.log("━" * 70)
                self.log("Running health check...")
                
                for agent_id in AgentRegistry.AGENTS:
                    result = self.check_agent_health(agent_id)
                    self.log(result['message'])
                
                # Save status and generate report
                self.save_health_status()
                self.generate_health_report()
                
                await asyncio.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                self.log("⚠️ Agent Health Monitor stopped by user")
                break
            except Exception as e:
                self.log(f"❌ Error in monitor loop: {e}", "ERROR")
                await asyncio.sleep(60)

if __name__ == "__main__":
    monitor = AgentHealthMonitor()
    asyncio.run(monitor.monitor_loop())
