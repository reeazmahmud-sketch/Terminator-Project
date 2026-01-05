#!/usr/bin/env python3
"""
TERMINATOR Project Index Manager Agent
Autonomous agent that monitors Desktop for new projects and auto-updates PROJECT_MASTER_INDEX.md
"""

import os
import asyncio
import time
from pathlib import Path
from datetime import datetime
from typing import Set, Dict

# Project detection patterns
PROJECT_INDICATORS = {
    'python': ['requirements.txt', 'setup.py', 'pyproject.toml', 'main.py', '__init__.py'],
    'node': ['package.json', 'node_modules'],
    'git': ['.git'],
    'ai': ['CLAUDE.md', 'README.md', 'agent', 'terminator'],
    'web': ['index.html', 'public', 'dist'],
}

class ProjectIndexManager:
    def __init__(self):
        self.desktop_path = Path.home() / "Desktop"
        self.index_file = Path.home() / "PROJECT_MASTER_INDEX.md"
        self.known_projects: Set[str] = set()
        self.scan_interval = 300  # 5 minutes
        
    def load_known_projects(self):
        """Load existing projects from index"""
        if self.index_file.exists():
            content = self.index_file.read_text()
            for line in content.split('\n'):
                if line.startswith('### '):
                    project_name = line.split('. ', 1)[-1].strip()
                    self.known_projects.add(project_name)
    
    def detect_project_type(self, project_path: Path) -> str:
        """Detect what type of project this is"""
        types = []
        for ptype, indicators in PROJECT_INDICATORS.items():
            for indicator in indicators:
                if (project_path / indicator).exists():
                    types.append(ptype)
                    break
        return ', '.join(types) if types else 'general'
    
    def analyze_project(self, project_path: Path) -> Dict:
        """Analyze project and extract metadata"""
        info = {
            'name': project_path.name,
            'location': str(project_path),
            'type': self.detect_project_type(project_path),
            'size': self.get_dir_size(project_path),
            'created': datetime.fromtimestamp(project_path.stat().st_ctime).strftime('%Y-%m-%d'),
        }
        
        # Try to extract purpose from README
        readme = project_path / 'README.md'
        if readme.exists():
            try:
                content = readme.read_text()
                # Get first non-empty line after title
                for line in content.split('\n')[1:]:
                    if line.strip() and not line.startswith('#'):
                        info['purpose'] = line.strip()[:100]
                        break
            except:
                pass
        
        if 'purpose' not in info:
            info['purpose'] = f"{info['type'].title()} project"
        
        return info
    
    def get_dir_size(self, path: Path) -> str:
        """Get directory size in human readable format"""
        try:
            total = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
            for unit in ['B', 'KB', 'MB', 'GB']:
                if total < 1024.0:
                    return f"{total:.1f}{unit}"
                total /= 1024.0
            return f"{total:.1f}TB"
        except:
            return "Unknown"
    
    def add_project_to_index(self, project_info: Dict):
        """Add new project to PROJECT_MASTER_INDEX.md"""
        if not self.index_file.exists():
            return
        
        content = self.index_file.read_text()
        
        # Find the next project number
        import re
        numbers = re.findall(r'^### (\d+)\.', content, re.MULTILINE)
        next_num = max([int(n) for n in numbers], default=0) + 1
        
        # Create new project entry
        new_entry = f"""
### {next_num}. {project_info['name']}
**Location:** `{project_info['location']}`
**Status:** ✅ Active
**Purpose:** {project_info['purpose']}
**Type:** {project_info['type']}
**Size:** {project_info['size']}
**Created:** {project_info['created']}
**Protection:** File System Guardian monitoring
**Cloud Sync:** Enabled
"""
        
        # Insert before "## Project Health" section or at end of Active Projects
        if '## Project Health' in content:
            parts = content.split('## Project Health')
            parts[0] += new_entry + '\n'
            new_content = '## Project Health'.join(parts)
        else:
            new_content = content + new_entry
        
        # Update last modified date
        new_content = re.sub(
            r'\*\*Last Updated:\*\* .*',
            f'**Last Updated:** {datetime.now().strftime("%B %d, %Y")}',
            new_content
        )
        
        self.index_file.write_text(new_content)
        print(f"✅ Added {project_info['name']} to PROJECT_MASTER_INDEX.md")
    
    def scan_for_new_projects(self):
        """Scan Desktop for new project directories"""
        if not self.desktop_path.exists():
            return
        
        for item in self.desktop_path.iterdir():
            if not item.is_dir():
                continue
            
            # Skip hidden and system folders
            if item.name.startswith('.') or item.name in ['Applications', 'Library']:
                continue
            
            # Skip if already known
            if item.name in self.known_projects:
                continue
            
            # Check if it looks like a project (has project indicators)
            has_indicators = False
            for indicators in PROJECT_INDICATORS.values():
                if any((item / ind).exists() for ind in indicators):
                    has_indicators = True
                    break
            
            if has_indicators:
                print(f"🔍 Detected new project: {item.name}")
                project_info = self.analyze_project(item)
                self.add_project_to_index(project_info)
                self.known_projects.add(item.name)
    
    async def run(self):
        """Main agent loop"""
        print("🤖 Project Index Manager Agent started")
        print(f"📁 Monitoring: {self.desktop_path}")
        print(f"📋 Index file: {self.index_file}")
        print(f"🔄 Scan interval: {self.scan_interval}s")
        
        self.load_known_projects()
        print(f"✅ Loaded {len(self.known_projects)} known projects")
        
        while True:
            try:
                self.scan_for_new_projects()
                await asyncio.sleep(self.scan_interval)
            except KeyboardInterrupt:
                print("\n⚠️ Project Index Manager Agent stopped")
                break
            except Exception as e:
                print(f"❌ Error in scan: {e}")
                await asyncio.sleep(60)  # Wait 1 min on error

if __name__ == "__main__":
    manager = ProjectIndexManager()
    asyncio.run(manager.run())
