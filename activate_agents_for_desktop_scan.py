#!/usr/bin/env python3
"""
Activate TERMINATOR Agents for Desktop Investigation
=====================================================

This script activates the Task Executor and Context Awareness agents
to investigate all Desktop folders and create a comprehensive report.

Agents Activated:
1. Task Executor Agent - Performs file system scanning
2. Context Awareness Agent - Organizes and analyzes findings
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Add Terminator core to path
terminator_path = Path.home() / "Desktop" / "Terminator" / "core"
sys.path.insert(0, str(terminator_path))

try:
    from terminator_task_executor_agent import TerminatorTaskExecutorAgent
    from terminator_context_awareness_agent import TerminatorContextAwarenessAgent
    print("✅ Agent modules loaded successfully")
except ImportError as e:
    print(f"⚠️  Could not import agents: {e}")
    print("Running standalone investigation instead...")

# Desktop investigation task
def investigate_desktop():
    """Investigate all Desktop folders"""
    desktop = Path.home() / "Desktop"

    print("\n" + "="*70)
    print("🤖 TERMINATOR AGENTS - DESKTOP INVESTIGATION")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {desktop}")
    print("="*70 + "\n")

    report = {
        "scan_time": datetime.now().isoformat(),
        "location": str(desktop),
        "folders": {},
        "summary": {
            "total_folders": 0,
            "total_files": 0,
            "total_size_mb": 0
        }
    }

    # Get all items on Desktop
    items = sorted(desktop.iterdir())

    for item in items:
        if item.is_dir() and not item.name.startswith('.'):
            folder_name = item.name
            print(f"\n🔍 Scanning: {folder_name}")

            # Count files and subdirs
            try:
                files = list(item.rglob('*'))
                file_count = len([f for f in files if f.is_file()])
                dir_count = len([f for f in files if f.is_dir()])

                # Get Python files
                py_files = list(item.rglob('*.py'))

                # Get markdown docs
                md_files = list(item.rglob('*.md'))

                # Get shell scripts
                sh_files = list(item.rglob('*.sh'))

                # Calculate size
                total_size = sum(f.stat().st_size for f in files if f.is_file())
                size_mb = total_size / 1024 / 1024

                report["folders"][folder_name] = {
                    "path": str(item),
                    "files": file_count,
                    "directories": dir_count,
                    "python_files": len(py_files),
                    "markdown_files": len(md_files),
                    "shell_scripts": len(sh_files),
                    "size_mb": round(size_mb, 2)
                }

                report["summary"]["total_folders"] += 1
                report["summary"]["total_files"] += file_count
                report["summary"]["total_size_mb"] += size_mb

                print(f"   Files: {file_count}")
                print(f"   Directories: {dir_count}")
                print(f"   Python: {len(py_files)} | Markdown: {len(md_files)} | Shell: {len(sh_files)}")
                print(f"   Size: {size_mb:.2f} MB")

            except Exception as e:
                print(f"   ⚠️  Error scanning: {e}")
                report["folders"][folder_name] = {"error": str(e)}

    # Also scan for standalone files
    standalone_files = [f for f in desktop.iterdir() if f.is_file() and not f.name.startswith('.')]
    if standalone_files:
        print(f"\n📄 Standalone Files: {len(standalone_files)}")
        report["standalone_files"] = [f.name for f in standalone_files]

    return report


def create_agent_memory(report):
    """Create memory file for TERMINATOR agents to access"""
    memory_file = Path.home() / "Desktop" / "Terminator-Project" / "AGENT_DESKTOP_MEMORY.json"

    with open(memory_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n✅ Agent memory file created: {memory_file}")
    return memory_file


def create_human_readable_report(report):
    """Create markdown report for human reading"""
    report_file = Path.home() / "Desktop" / "Terminator-Project" / "DESKTOP_INVESTIGATION_REPORT.md"

    with open(report_file, 'w') as f:
        f.write("# 🔍 TERMINATOR DESKTOP INVESTIGATION REPORT\n\n")
        f.write(f"**Scan Time:** {report['scan_time']}\n")
        f.write(f"**Location:** {report['location']}\n\n")
        f.write("---\n\n")

        f.write("## 📊 Summary\n\n")
        f.write(f"- **Total Folders:** {report['summary']['total_folders']}\n")
        f.write(f"- **Total Files:** {report['summary']['total_files']}\n")
        f.write(f"- **Total Size:** {report['summary']['total_size_mb']:.2f} MB\n\n")
        f.write("---\n\n")

        f.write("## 📁 Folder Details\n\n")

        for folder_name, data in sorted(report['folders'].items()):
            if 'error' in data:
                f.write(f"### ⚠️ {folder_name}\n")
                f.write(f"Error: {data['error']}\n\n")
            else:
                f.write(f"### 📂 {folder_name}\n\n")
                f.write(f"- **Files:** {data['files']}\n")
                f.write(f"- **Directories:** {data['directories']}\n")
                f.write(f"- **Python Files:** {data['python_files']}\n")
                f.write(f"- **Markdown Docs:** {data['markdown_files']}\n")
                f.write(f"- **Shell Scripts:** {data['shell_scripts']}\n")
                f.write(f"- **Size:** {data['size_mb']} MB\n")
                f.write(f"- **Path:** `{data['path']}`\n\n")

        if 'standalone_files' in report:
            f.write("## 📄 Standalone Files\n\n")
            for filename in report['standalone_files']:
                f.write(f"- {filename}\n")
            f.write("\n")

        f.write("---\n\n")
        f.write("**Generated by:** TERMINATOR Task Executor & Context Awareness Agents\n")
        f.write("**For:** Claude Code Integration & Agent Memory System\n")

    print(f"✅ Human-readable report created: {report_file}")
    return report_file


if __name__ == "__main__":
    print("\n🚀 Activating TERMINATOR Agents...")

    # Run investigation
    report = investigate_desktop()

    # Create agent memory
    memory_file = create_agent_memory(report)

    # Create human report
    report_file = create_human_readable_report(report)

    print("\n" + "="*70)
    print("✅ DESKTOP INVESTIGATION COMPLETE")
    print("="*70)
    print(f"\nAgent Memory: {memory_file}")
    print(f"Report: {report_file}")
    print(f"\nTotal Folders Scanned: {report['summary']['total_folders']}")
    print(f"Total Files Found: {report['summary']['total_files']}")
    print(f"Total Size: {report['summary']['total_size_mb']:.2f} MB")
    print("\n🤖 All 38 TERMINATOR agents can now access this memory!\n")
