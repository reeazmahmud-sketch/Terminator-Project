#!/usr/bin/env python3
"""
TERMINATOR Auto-Documentation Updater
Automatically updates documentation when code changes
"""

import os
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set
import json
import re
import ast

class AutoDocUpdater:
    def __init__(self):
        self.project_root = Path.home() / "Desktop" / "Terminator-Project"
        self.index_file = Path.home() / "PROJECT_MASTER_INDEX.md"
        self.config_file = self.project_root / ".autodoc" / "config.json"
        self.state_file = self.project_root / ".autodoc" / "doc_state.json"
        self.log_file = self.project_root / ".logs" / "auto_doc.log"
        
        (self.project_root / ".autodoc").mkdir(parents=True, exist_ok=True)
        (self.project_root / ".logs").mkdir(parents=True, exist_ok=True)
        
        # Configuration
        self.config = {
            'enabled': True,
            'update_on': {
                'readme': True,
                'claude_md': True,
                'docstrings': False,  # Advanced feature
                'api_docs': False      # Advanced feature
            },
            'sync_across_projects': True,
            'check_interval': 600,  # 10 minutes
            'safe_mode': True  # Don't overwrite user content
        }
        
        self.load_config()
        
        # Track last known state
        self.file_hashes: Dict[str, str] = {}
        self.load_state()
        
        self.monitored_projects: List[Path] = []
        
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
        """Load configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
            except Exception as e:
                self.log(f"Failed to load config: {e}", "ERROR")
    
    def save_config(self):
        """Save configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.log(f"Failed to save config: {e}", "ERROR")
    
    def load_state(self):
        """Load documentation state"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    self.file_hashes = state.get('file_hashes', {})
            except Exception as e:
                self.log(f"Failed to load state: {e}", "ERROR")
    
    def save_state(self):
        """Save documentation state"""
        try:
            state = {'file_hashes': self.file_hashes}
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.log(f"Failed to save state: {e}", "ERROR")
    
    def get_file_hash(self, file_path: Path) -> str:
        """Get hash of file content"""
        try:
            import hashlib
            content = file_path.read_bytes()
            return hashlib.md5(content).hexdigest()
        except:
            return ""
    
    def load_monitored_projects(self) -> List[Path]:
        """Load active projects from PROJECT_MASTER_INDEX.md"""
        projects = []
        
        if not self.index_file.exists():
            return projects
        
        try:
            content = self.index_file.read_text()
            for line in content.split('\n'):
                if line.startswith('**Location:**'):
                    match = re.search(r'`([^`]+)`', line)
                    if match:
                        path = Path(match.group(1))
                        if path.exists() and path.is_dir():
                            projects.append(path)
        except Exception as e:
            self.log(f"Error loading projects: {e}", "ERROR")
        
        return projects
    
    def analyze_python_file(self, file_path: Path) -> Dict:
        """Analyze Python file to extract functions and classes"""
        try:
            content = file_path.read_text()
            tree = ast.parse(content)
            
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'docstring': ast.get_docstring(node) or "No description"
                    })
                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        'name': node.name,
                        'docstring': ast.get_docstring(node) or "No description"
                    })
            
            return {
                'functions': functions,
                'classes': classes,
                'module_docstring': ast.get_docstring(tree) or "No description"
            }
        except Exception as e:
            self.log(f"Error analyzing {file_path.name}: {e}", "WARN")
            return {'functions': [], 'classes': [], 'module_docstring': ''}
    
    def detect_project_type(self, project_path: Path) -> List[str]:
        """Detect project type (Python, Node, etc.)"""
        types = []
        
        if (project_path / 'requirements.txt').exists() or \
           (project_path / 'setup.py').exists():
            types.append('python')
        
        if (project_path / 'package.json').exists():
            types.append('node')
        
        if (project_path / '.git').exists():
            types.append('git')
        
        return types
    
    def generate_project_summary(self, project_path: Path) -> str:
        """Generate project summary based on structure"""
        types = self.detect_project_type(project_path)
        
        summary = f"# {project_path.name}\n\n"
        
        # Basic info
        summary += f"**Type:** {', '.join(types) if types else 'Unknown'}\n"
        summary += f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        # Count files
        py_files = list(project_path.rglob('*.py'))
        js_files = list(project_path.rglob('*.js'))
        
        if py_files:
            summary += f"**Python Files:** {len(py_files)}\n"
        if js_files:
            summary += f"**JavaScript Files:** {len(js_files)}\n"
        
        summary += "\n## Overview\n\n"
        summary += "This project is part of the TERMINATOR autonomous system.\n\n"
        
        return summary
    
    def update_readme(self, project_path: Path):
        """Update README.md with current project info"""
        readme = project_path / 'README.md'
        
        if not readme.exists():
            # Create new README
            self.log(f"Creating README for {project_path.name}")
            content = self.generate_project_summary(project_path)
            readme.write_text(content)
            return True
        
        # In safe mode, don't overwrite existing READMEs
        if self.config['safe_mode']:
            content = readme.read_text()
            if len(content) > 100:  # Has substantial content
                self.log(f"Skipping README update for {project_path.name} (safe mode)")
                return False
        
        return True
    
    def update_claude_md(self, project_path: Path):
        """Update CLAUDE.md with architecture info"""
        claude_md = project_path / 'CLAUDE.md'
        
        # Only update if we're the Terminator-Project or it doesn't exist
        if project_path == self.project_root:
            # Update our own CLAUDE.md with agent list
            self.update_terminator_claude_md()
            return True
        
        if not claude_md.exists():
            self.log(f"Creating CLAUDE.md for {project_path.name}")
            content = f"""# {project_path.name}

This file provides guidance to Claude Code when working with this project.

## Overview

{self.generate_project_summary(project_path)}

## Last Updated

{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Auto-generated by TERMINATOR Auto-Documentation Updater
"""
            claude_md.write_text(content)
            return True
        
        return False
    
    def update_terminator_claude_md(self):
        """Update Terminator-Project CLAUDE.md with current agent list"""
        claude_md = self.project_root / 'CLAUDE.md'
        
        if not claude_md.exists():
            return
        
        # Find all agents
        core_dir = self.project_root / 'core'
        agents = []
        
        for agent_file in core_dir.glob('terminator_*.py'):
            agent_name = agent_file.stem.replace('terminator_', '').replace('_', ' ').title()
            agents.append(agent_name)
        
        self.log(f"Found {len(agents)} agents in core/")
        # Note: Full CLAUDE.md update would be more complex
        # This is a simplified version
    
    def check_for_changes(self, project_path: Path) -> List[Path]:
        """Check which documentation files need updating"""
        changed_files = []
        
        # Check Python files for changes
        for py_file in project_path.rglob('*.py'):
            if '__pycache__' in str(py_file):
                continue
            
            file_key = str(py_file)
            current_hash = self.get_file_hash(py_file)
            
            if file_key not in self.file_hashes or \
               self.file_hashes[file_key] != current_hash:
                changed_files.append(py_file)
                self.file_hashes[file_key] = current_hash
        
        return changed_files
    
    def update_project_docs(self, project_path: Path):
        """Update documentation for a project"""
        if not self.config['enabled']:
            return
        
        self.log(f"Checking docs for {project_path.name}...")
        
        # Check for code changes
        changed_files = self.check_for_changes(project_path)
        
        if not changed_files and project_path in self.monitored_projects:
            return  # No changes
        
        if changed_files:
            self.log(f"Detected {len(changed_files)} changed files in {project_path.name}")
        
        # Update README
        if self.config['update_on']['readme']:
            self.update_readme(project_path)
        
        # Update CLAUDE.md
        if self.config['update_on']['claude_md']:
            self.update_claude_md(project_path)
        
        self.save_state()
    
    async def monitor_loop(self):
        """Main monitoring loop"""
        self.log("📝 Auto-Documentation Updater started")
        self.log(f"Check interval: {self.config['check_interval']}s")
        
        while True:
            try:
                # Load monitored projects
                self.monitored_projects = self.load_monitored_projects()
                
                if not self.monitored_projects:
                    self.log("No projects to monitor", "WARN")
                else:
                    self.log(f"Monitoring {len(self.monitored_projects)} projects")
                    
                    # Update docs for each project
                    for project in self.monitored_projects:
                        self.update_project_docs(project)
                
                await asyncio.sleep(self.config['check_interval'])
                
            except KeyboardInterrupt:
                self.log("⚠️ Auto-Doc Updater stopped by user")
                break
            except Exception as e:
                self.log(f"❌ Error in monitor loop: {e}", "ERROR")
                await asyncio.sleep(60)

if __name__ == "__main__":
    updater = AutoDocUpdater()
    asyncio.run(updater.monitor_loop())
