#!/usr/bin/env python3
"""
Terminal Agent - An intelligent terminal automation assistant for macOS
"""

import subprocess
import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
import shlex
import argparse

class TerminalAgent:
    """Terminal automation agent with safety features"""
    
    def __init__(self):
        self.safe_commands = {
            'ls', 'pwd', 'echo', 'date', 'whoami', 'uname', 'df', 'du',
            'ps', 'top', 'htop', 'btop', 'which', 'whereis', 'file',
            'wc', 'head', 'tail', 'grep', 'find', 'cat', 'bat', 'lsd',
            'git', 'brew', 'python', 'python3', 'pip', 'pip3', 'node',
            'npm', 'curl', 'wget', 'ping', 'ifconfig', 'netstat'
        }
        
        self.dangerous_patterns = [
            'rm -rf /', 'rm -rf ~', 'dd if=', ':(){ :|:& };:',
            'mkfs', 'format', '> /dev/sd', 'sudo rm -rf'
        ]
        
        self.history_file = Path.home() / '.terminal_agent_history.json'
        self.load_history()
        
        self.workflows = {
            'git-status': {
                'description': 'Check git status across all repos in current directory',
                'commands': [
                    'find . -type d -name .git -maxdepth 2 | while read dir; do echo "\\n📁 $(dirname $dir):"; git -C "$(dirname $dir)" status -s; done'
                ]
            },
            'system-info': {
                'description': 'Get comprehensive system information',
                'commands': [
                    'echo "🖥️  System: $(uname -a)"',
                    'echo "💾 Disk Usage:"; df -h',
                    'echo "🧠 Memory:"; top -l 1 | grep PhysMem',
                    'echo "📊 CPU:"; sysctl -n machdep.cpu.brand_string',
                    'echo "🌡️  Processes:"; ps aux | head -10'
                ]
            },
            'dev-setup': {
                'description': 'Check development environment setup',
                'commands': [
                    'echo "🐍 Python: $(python3 --version)"',
                    'echo "📦 Node: $(node --version 2>/dev/null || echo "Not installed")"',
                    'echo "🦀 Rust: $(rustc --version 2>/dev/null || echo "Not installed")"',
                    'echo "🐹 Go: $(go version 2>/dev/null || echo "Not installed")"',
                    'echo "☕ Java: $(java --version 2>/dev/null | head -1 || echo "Not installed")"'
                ]
            },
            'network-check': {
                'description': 'Network diagnostics',
                'commands': [
                    'echo "🌐 Network Interfaces:"; ifconfig | grep "inet "',
                    'echo "\\n📡 WiFi Status:"; /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I',
                    'echo "\\n🏓 Connectivity Test:"; ping -c 3 8.8.8.8',
                    'echo "\\n🔍 DNS Check:"; nslookup google.com'
                ]
            },
            'cleanup': {
                'description': 'Clean up system junk (safe)',
                'commands': [
                    'echo "🗑️  Cleaning brew cache..."; brew cleanup -s 2>/dev/null',
                    'echo "📁 Cleaning Downloads older than 30 days..."; find ~/Downloads -mtime +30 -type f -exec echo "Would delete: {}" \\;',
                    'echo "🧹 Emptying Trash..."; rm -rf ~/.Trash/* 2>/dev/null',
                    'echo "✨ Cleanup complete!"'
                ]
            }
        }
    
    def load_history(self):
        """Load command history"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            else:
                self.history = []
        except:
            self.history = []
    
    def save_history(self, command, result, success):
        """Save command to history"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'success': success,
            'result': result[:500] if result else None  # Limit size
        }
        self.history.append(entry)
        # Keep only last 100 commands
        self.history = self.history[-100:]
        
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def is_safe_command(self, command):
        """Check if command is safe to execute"""
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if pattern in command.lower():
                return False, f"⚠️  Dangerous pattern detected: {pattern}"
        
        # Check if base command is in safe list
        try:
            base_command = shlex.split(command)[0]
            base_name = os.path.basename(base_command)
            
            # Allow if in safe commands or is a path to a safe command
            if base_name in self.safe_commands:
                return True, "Safe command"
            
            # Check for sudo (require confirmation)
            if base_command == 'sudo':
                return None, "Requires confirmation for sudo"
                
            # Unknown command - require confirmation
            return None, f"Unknown command: {base_name}"
        except:
            return False, "Could not parse command"
    
    def execute_command(self, command, timeout=30):
        """Execute a terminal command safely"""
        is_safe, reason = self.is_safe_command(command)
        
        if is_safe is False:
            print(f"❌ Refusing to execute: {reason}")
            return None
        
        if is_safe is None:
            response = input(f"⚠️  {reason}. Execute anyway? (y/n): ")
            if response.lower() != 'y':
                print("Command cancelled.")
                return None
        
        print(f"🚀 Executing: {command}")
        print("-" * 50)
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            output = result.stdout + result.stderr
            self.save_history(command, output, result.returncode == 0)
            
            if result.returncode == 0:
                print(result.stdout)
                if result.stderr:
                    print(f"⚠️  Warnings:\n{result.stderr}")
            else:
                print(f"❌ Command failed with code {result.returncode}")
                if result.stderr:
                    print(f"Error: {result.stderr}")
                if result.stdout:
                    print(f"Output: {result.stdout}")
            
            return result
            
        except subprocess.TimeoutExpired:
            print(f"⏱️  Command timed out after {timeout} seconds")
            self.save_history(command, "Timeout", False)
            return None
        except Exception as e:
            print(f"❌ Error executing command: {e}")
            self.save_history(command, str(e), False)
            return None
    
    def run_workflow(self, workflow_name):
        """Run a predefined workflow"""
        if workflow_name not in self.workflows:
            print(f"❌ Unknown workflow: {workflow_name}")
            print(f"Available workflows: {', '.join(self.workflows.keys())}")
            return
        
        workflow = self.workflows[workflow_name]
        print(f"🔄 Running workflow: {workflow_name}")
        print(f"📝 {workflow['description']}")
        print("=" * 60)
        
        for command in workflow['commands']:
            self.execute_command(command)
            time.sleep(0.5)  # Small delay between commands
        
        print("=" * 60)
        print(f"✅ Workflow '{workflow_name}' completed!")
    
    def interactive_mode(self):
        """Run in interactive mode"""
        print("""
╔════════════════════════════════════════╗
║     🤖 Terminal Agent - macOS          ║
║     Type 'help' for commands           ║
║     Type 'exit' to quit                ║
╚════════════════════════════════════════╝
        """)
        
        while True:
            try:
                command = input("\n🤖 > ").strip()
                
                if command.lower() in ['exit', 'quit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                elif command.lower() == 'help':
                    self.show_help()
                
                elif command.lower() == 'history':
                    self.show_history()
                
                elif command.lower() == 'workflows':
                    self.list_workflows()
                
                elif command.startswith('workflow '):
                    workflow_name = command.split(' ', 1)[1]
                    self.run_workflow(workflow_name)
                
                elif command:
                    self.execute_command(command)
                    
            except KeyboardInterrupt:
                print("\n👋 Interrupted. Type 'exit' to quit.")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def show_help(self):
        """Show help information"""
        print("""
📚 Terminal Agent Commands:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  help              - Show this help message
  history           - Show command history
  workflows         - List available workflows
  workflow <name>   - Run a specific workflow
  exit/quit         - Exit the agent
  
  Or type any terminal command to execute it!
  
🛡️  Safety Features:
  • Safe command validation
  • Dangerous pattern detection
  • Confirmation for unknown commands
  • Command timeout protection
  • Full history tracking
        """)
    
    def show_history(self):
        """Show command history"""
        if not self.history:
            print("📭 No command history yet.")
            return
        
        print("\n📜 Recent Command History:")
        print("-" * 60)
        for entry in self.history[-10:]:
            timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%H:%M:%S')
            status = "✅" if entry['success'] else "❌"
            print(f"{timestamp} {status} {entry['command'][:50]}")
    
    def list_workflows(self):
        """List available workflows"""
        print("\n🔧 Available Workflows:")
        print("-" * 60)
        for name, workflow in self.workflows.items():
            print(f"  {name:15} - {workflow['description']}")
        print("\nRun with: workflow <name>")

def main():
    parser = argparse.ArgumentParser(description='Terminal Agent - Intelligent automation for macOS')
    parser.add_argument('command', nargs='*', help='Command to execute')
    parser.add_argument('-w', '--workflow', help='Run a specific workflow')
    parser.add_argument('-l', '--list', action='store_true', help='List available workflows')
    parser.add_argument('-H', '--history', action='store_true', help='Show command history')
    
    args = parser.parse_args()
    
    agent = TerminalAgent()
    
    if args.list:
        agent.list_workflows()
    elif args.history:
        agent.show_history()
    elif args.workflow:
        agent.run_workflow(args.workflow)
    elif args.command:
        command = ' '.join(args.command)
        agent.execute_command(command)
    else:
        # Interactive mode
        agent.interactive_mode()

if __name__ == "__main__":
    main()
