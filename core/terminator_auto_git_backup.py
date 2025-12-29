#!/usr/bin/env python3
"""
TERMINATOR Auto-Git Backup Agent
Automatically commits and pushes code changes to prevent data loss
"""

import os
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import json
import re

class AutoGitBackup:
    def __init__(self):
        self.project_root = Path.home() / "Desktop" / "Terminator-Project"
        self.index_file = Path.home() / "PROJECT_MASTER_INDEX.md"
        self.backup_dir = self.project_root / ".backups"
        self.log_file = self.project_root / ".logs" / "git_backup.log"
        self.report_file = self.project_root / ".backups" / "backup_report.json"
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        (self.project_root / ".logs").mkdir(parents=True, exist_ok=True)
        
        self.backup_interval = 3600  # 1 hour
        self.monitored_projects: List[Path] = []
        
        # Files to never commit
        self.ignore_patterns = [
            '.env', '.env.local', '.env.production',
            'credentials.json', 'secrets.json', 'api_keys.json',
            '*.key', '*.pem', '*.p12',
            'node_modules/', '__pycache__/', '.DS_Store',
            '*.pyc', '*.pyo', '*.log'
        ]
    
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
    
    def load_monitored_projects(self) -> List[Path]:
        """Load active projects from PROJECT_MASTER_INDEX.md"""
        projects = []
        
        if not self.index_file.exists():
            self.log("PROJECT_MASTER_INDEX.md not found", "WARN")
            return projects
        
        try:
            content = self.index_file.read_text()
            
            # Find all active project locations
            for line in content.split('\n'):
                if line.startswith('**Location:**'):
                    # Extract path from: **Location:** `/path/to/project`
                    match = re.search(r'`([^`]+)`', line)
                    if match:
                        path = Path(match.group(1))
                        if path.exists() and path.is_dir():
                            projects.append(path)
            
            self.log(f"Loaded {len(projects)} projects to monitor")
        except Exception as e:
            self.log(f"Error loading projects: {e}", "ERROR")
        
        return projects
    
    def run_git_command(self, project_path: Path, command: List[str]) -> Optional[str]:
        """Run a git command in a project directory"""
        try:
            result = subprocess.run(
                ['git'] + command,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                if result.stderr:
                    self.log(f"Git error in {project_path.name}: {result.stderr.strip()}", "WARN")
                return None
        except subprocess.TimeoutExpired:
            self.log(f"Git command timeout in {project_path.name}", "ERROR")
            return None
        except Exception as e:
            self.log(f"Git command failed in {project_path.name}: {e}", "ERROR")
            return None
    
    def is_git_repo(self, project_path: Path) -> bool:
        """Check if project is a git repository"""
        return (project_path / '.git').exists()
    
    def init_git_repo(self, project_path: Path) -> bool:
        """Initialize git repository"""
        self.log(f"Initializing git repo in {project_path.name}")
        
        result = self.run_git_command(project_path, ['init'])
        if result is not None:
            # Create .gitignore if it doesn't exist
            gitignore = project_path / '.gitignore'
            if not gitignore.exists():
                gitignore.write_text('\n'.join(self.ignore_patterns) + '\n')
                self.log(f"Created .gitignore in {project_path.name}")
            
            return True
        return False
    
    def has_changes(self, project_path: Path) -> bool:
        """Check if project has uncommitted changes"""
        status = self.run_git_command(project_path, ['status', '--porcelain'])
        return status is not None and len(status) > 0
    
    def get_changed_files(self, project_path: Path) -> List[str]:
        """Get list of changed files"""
        status = self.run_git_command(project_path, ['status', '--porcelain'])
        if not status:
            return []
        
        changed_files = []
        for line in status.split('\n'):
            if line.strip():
                # Format: "XY filename"
                parts = line.strip().split(None, 1)
                if len(parts) == 2:
                    changed_files.append(parts[1])
        
        return changed_files
    
    def generate_commit_message(self, project_path: Path, changed_files: List[str]) -> str:
        """Generate intelligent commit message based on changes"""
        if not changed_files:
            return "Auto-backup: No specific changes"
        
        # Categorize changes
        added = []
        modified = []
        deleted = []
        
        status = self.run_git_command(project_path, ['status', '--porcelain'])
        if status:
            for line in status.split('\n'):
                if not line.strip():
                    continue
                
                status_code = line[:2]
                filename = line[3:].strip()
                
                if 'A' in status_code or '?' in status_code:
                    added.append(filename)
                elif 'M' in status_code:
                    modified.append(filename)
                elif 'D' in status_code:
                    deleted.append(filename)
        
        # Build message
        message_parts = []
        
        if added:
            message_parts.append(f"Added {len(added)} file(s)")
        if modified:
            message_parts.append(f"Modified {len(modified)} file(s)")
        if deleted:
            message_parts.append(f"Deleted {len(deleted)} file(s)")
        
        summary = ", ".join(message_parts) if message_parts else "Updates"
        
        # Detailed file list (limit to 5)
        details = []
        for file in (added + modified + deleted)[:5]:
            details.append(f"  - {file}")
        
        if len(changed_files) > 5:
            details.append(f"  ... and {len(changed_files) - 5} more")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        commit_message = f"""Auto-backup: {summary}

{chr(10).join(details)}

🤖 Generated by TERMINATOR Auto-Git Backup
📅 {timestamp}
"""
        return commit_message
    
    def commit_changes(self, project_path: Path) -> bool:
        """Commit all changes in project"""
        try:
            # Stage all changes (excluding ignored files)
            self.run_git_command(project_path, ['add', '-A'])
            
            # Get changed files for commit message
            changed_files = self.get_changed_files(project_path)
            
            if not changed_files:
                return False
            
            # Generate commit message
            commit_msg = self.generate_commit_message(project_path, changed_files)
            
            # Commit
            result = self.run_git_command(project_path, ['commit', '-m', commit_msg])
            
            if result is not None:
                self.log(f"✅ Committed changes in {project_path.name}")
                return True
            else:
                self.log(f"Failed to commit in {project_path.name}", "WARN")
                return False
                
        except Exception as e:
            self.log(f"Error committing in {project_path.name}: {e}", "ERROR")
            return False
    
    def has_remote(self, project_path: Path) -> bool:
        """Check if project has a remote repository"""
        remotes = self.run_git_command(project_path, ['remote', '-v'])
        return remotes is not None and len(remotes) > 0
    
    def push_to_remote(self, project_path: Path) -> bool:
        """Push commits to remote repository"""
        if not self.has_remote(project_path):
            self.log(f"No remote configured for {project_path.name}", "INFO")
            return False
        
        try:
            # Get current branch
            branch = self.run_git_command(project_path, ['branch', '--show-current'])
            if not branch:
                branch = 'main'
            
            # Push
            result = self.run_git_command(project_path, ['push', 'origin', branch])
            
            if result is not None:
                self.log(f"✅ Pushed {project_path.name} to remote")
                return True
            else:
                # Try with -u flag (set upstream)
                result = self.run_git_command(project_path, ['push', '-u', 'origin', branch])
                if result is not None:
                    self.log(f"✅ Pushed {project_path.name} to remote (set upstream)")
                    return True
                else:
                    self.log(f"Failed to push {project_path.name}", "WARN")
                    return False
        except Exception as e:
            self.log(f"Error pushing {project_path.name}: {e}", "ERROR")
            return False
    
    def backup_project(self, project_path: Path) -> Dict:
        """Backup a single project"""
        result = {
            'project': project_path.name,
            'path': str(project_path),
            'timestamp': datetime.now().isoformat(),
            'has_changes': False,
            'committed': False,
            'pushed': False,
            'error': None
        }
        
        try:
            # Initialize git if needed
            if not self.is_git_repo(project_path):
                if not self.init_git_repo(project_path):
                    result['error'] = "Failed to initialize git"
                    return result
            
            # Check for changes
            if self.has_changes(project_path):
                result['has_changes'] = True
                
                # Commit changes
                if self.commit_changes(project_path):
                    result['committed'] = True
                    
                    # Push to remote
                    if self.push_to_remote(project_path):
                        result['pushed'] = True
            
        except Exception as e:
            result['error'] = str(e)
            self.log(f"Error backing up {project_path.name}: {e}", "ERROR")
        
        return result
    
    def generate_backup_report(self, results: List[Dict]):
        """Generate backup report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_projects': len(results),
            'backed_up': sum(1 for r in results if r['committed']),
            'pushed': sum(1 for r in results if r['pushed']),
            'errors': sum(1 for r in results if r['error']),
            'results': results
        }
        
        # Save JSON report
        try:
            with open(self.report_file, 'w') as f:
                json.dump(report, f, indent=2)
        except Exception as e:
            self.log(f"Failed to save report: {e}", "ERROR")
        
        # Log summary
        self.log(f"📊 Backup Summary: {report['backed_up']}/{report['total_projects']} committed, {report['pushed']} pushed")
    
    async def backup_loop(self):
        """Main backup loop"""
        self.log("🔄 Auto-Git Backup Agent started")
        self.log(f"Backup interval: {self.backup_interval}s ({self.backup_interval // 3600}h)")
        
        while True:
            try:
                self.log("━" * 70)
                self.log("Running auto-backup...")
                
                # Load projects
                self.monitored_projects = self.load_monitored_projects()
                
                if not self.monitored_projects:
                    self.log("No projects to backup", "WARN")
                else:
                    # Backup each project
                    results = []
                    for project in self.monitored_projects:
                        self.log(f"Checking {project.name}...")
                        result = self.backup_project(project)
                        results.append(result)
                    
                    # Generate report
                    self.generate_backup_report(results)
                
                # Wait for next backup
                await asyncio.sleep(self.backup_interval)
                
            except KeyboardInterrupt:
                self.log("⚠️ Auto-Git Backup stopped by user")
                break
            except Exception as e:
                self.log(f"❌ Error in backup loop: {e}", "ERROR")
                await asyncio.sleep(300)  # Wait 5 min on error

if __name__ == "__main__":
    backup = AutoGitBackup()
    asyncio.run(backup.backup_loop())
