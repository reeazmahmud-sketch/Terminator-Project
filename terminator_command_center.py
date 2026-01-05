#!/usr/bin/env python3
"""
TERMINATOR Command Center - Multi-Agent Control Interface
=========================================================

Interactive command center for User and TERMINATOR to:
1. Command and control all 38+ specialized agents
2. View live status and progress of all agents
3. Create and manage hierarchical tasks
4. Monitor real-time execution
5. Generate and manage reports
6. Track time and performance metrics

Commands:
    /create-task <title> <description> <agents...>  - Create new task
    /assign <task_id>                               - Assign task to agents
    /start <task_id> <agent>                        - Start task execution
    /progress <task_id> <percent>                   - Update task progress
    /complete <task_id> <agent>                     - Complete task
    /status [task_id]                               - Show task status
    /agents [agent_name]                            - Show agent status
    /report <task_id> [save_path]                   - Generate and save report
    /monitor                                        - Toggle live monitoring
    /help                                           - Show all commands
    /quit                                           - Exit command center

Created: December 17, 2025
"""

import sys
import os
import time
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core'))

from core.terminator_multi_agent_orchestrator import (
    get_orchestrator,
    MultiAgentOrchestrator,
    TaskPriority,
    TaskStatus
)
from core.terminator_agent_communication_bus import get_communication_bus


# ============================================================================
# Command Center
# ============================================================================

class TerminatorCommandCenter:
    """Interactive command center for multi-agent control"""

    def __init__(self):
        self.orchestrator = get_orchestrator()
        self.bus = get_communication_bus()
        self.monitoring_enabled = False
        self.running = True

        # Available agents (can be expanded)
        self.available_agents = [
            "context_awareness_agent",
            "decision_engine",
            "task_executor_agent",
            "error_monitor_agent",
            "learning_system",
            "memory_agent",
            "project_monitor_agent",
            "qa_agent",
            "resource_manager_agent",
            "market_analysis_agent",
            "risk_assessment_agent",
            "user_advocate_agent",
            "task_prediction_agent"
        ]

        # Register all available agents
        self._register_agents()

    def _register_agents(self):
        """Register all available agents with the bus"""
        print("\n🔧 Registering agents...")
        for agent in self.available_agents:
            try:
                self.bus.register_agent(agent)
                print(f"  ✅ {agent}")
            except Exception as e:
                print(f"  ⚠️  {agent}: {str(e)}")

    def _clear_screen(self):
        """Clear screen using safe method"""
        print("\n" * 50)  # Simple but portable screen clear

    def print_banner(self):
        """Print welcome banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║        🤖 TERMINATOR COMMAND CENTER 🤖                           ║
║                                                                  ║
║        Multi-Agent Task Orchestration & Control System          ║
║                                                                  ║
║        38+ Specialized Agents | Live Monitoring                 ║
║        Hierarchical Tasks | Report Management                   ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

Type /help for available commands or /quit to exit
        """
        print(banner)

    def print_help(self):
        """Print help message with all commands"""
        help_text = """
📋 AVAILABLE COMMANDS:

TASK MANAGEMENT:
  /create-task <title> | <description> | <agent1,agent2> | <priority> | <duration>
      Create new task with specified agents
      Priority: critical, high, normal, low
      Example: /create-task System Analysis | Analyze architecture | context_awareness_agent,project_monitor_agent | high | 120

  /create-subtask <parent_task_id> | <title> | <description> | <agents> | <duration>
      Create sub-task under a parent task

  /assign <task_id>
      Assign task to designated agents

  /start <task_id> <agent_name>
      Start task execution by specific agent

  /progress <task_id> <percent> [note]
      Update task progress (0-100)

  /complete <task_id> <agent_name>
      Mark task as completed

STATUS & MONITORING:
  /status
      Show status of all tasks

  /status <task_id>
      Show detailed status of specific task

  /agents
      Show status of all agents

  /agents <agent_name>
      Show detailed status of specific agent

  /monitor
      Toggle live monitoring on/off

  /available
      List all available agents

REPORTS:
  /report <task_id>
      Generate report for task

  /report <task_id> <save_path>
      Generate and save report to specific path

  /reports
      Show report manager summary

SYSTEM:
  /bus
      Show communication bus status

  /clear
      Clear screen

  /help
      Show this help message

  /quit
      Exit command center
"""
        print(help_text)

    def display_live_status(self):
        """Display live status dashboard"""
        self._clear_screen()

        print("\n" + "="*80)
        print(f"  🔴 LIVE STATUS - {datetime.now().strftime('%H:%M:%S')}")
        print("="*80)

        # Get all tasks status
        all_status = self.orchestrator.get_all_tasks_status()

        print(f"\n📊 TASKS OVERVIEW:")
        print(f"  Total Tasks: {all_status['total_tasks']}")

        for status, tasks in all_status['tasks_by_status'].items():
            print(f"\n  {status.upper()} ({len(tasks)}):")
            for task in tasks[:5]:  # Show first 5
                print(f"    • {task['task_id']}: {task['title'][:50]}")
                print(f"      Agents: {', '.join(task['assigned_agents'])}")
                print(f"      Progress: {task['progress']}")

        print(f"\n👥 AGENT WORKLOADS:")
        for agent_name, workload in all_status['agent_workloads'].items():
            status_icon = "🟢" if workload['active_task'] else "⚪"
            print(f"  {status_icon} {agent_name}:")
            print(f"      Active: {workload['active_task'] or 'None'}")
            print(f"      Assigned: {workload['assigned_tasks']}")
            print(f"      Completed: {workload['completed_tasks']}")
            print(f"      Time Worked: {workload['time_worked']}")

        print("\n" + "="*80)
        print("  Press Ctrl+C to pause monitoring")
        print("="*80 + "\n")

    def handle_create_task(self, args: str):
        """Handle create-task command"""
        try:
            parts = [p.strip() for p in args.split('|')]

            if len(parts) < 3:
                print("❌ Usage: /create-task <title> | <description> | <agents> | [priority] | [duration]")
                return

            title = parts[0]
            description = parts[1]
            agents = [a.strip() for a in parts[2].split(',')]

            priority = TaskPriority.NORMAL
            if len(parts) > 3 and parts[3]:
                priority_map = {
                    'critical': TaskPriority.CRITICAL,
                    'high': TaskPriority.HIGH,
                    'normal': TaskPriority.NORMAL,
                    'low': TaskPriority.LOW
                }
                priority = priority_map.get(parts[3].lower(), TaskPriority.NORMAL)

            duration = 60.0
            if len(parts) > 4 and parts[4]:
                try:
                    duration = float(parts[4])
                except ValueError:
                    duration = 60.0

            task = self.orchestrator.create_task(
                title=title,
                description=description,
                assigned_agents=agents,
                priority=priority,
                estimated_duration_seconds=duration
            )

            print(f"\n✅ Created task: {task.task_id}")
            print(f"   Title: {title}")
            print(f"   Agents: {', '.join(agents)}")
            print(f"   Priority: {priority.value}")
            print(f"   Estimated Duration: {duration}s\n")

        except Exception as e:
            print(f"❌ Error creating task: {e}")

    def handle_create_subtask(self, args: str):
        """Handle create-subtask command"""
        try:
            parts = [p.strip() for p in args.split('|')]

            if len(parts) < 4:
                print("❌ Usage: /create-subtask <parent_id> | <title> | <description> | <agents> | [duration]")
                return

            parent_id = parts[0]
            title = parts[1]
            description = parts[2]
            agents = [a.strip() for a in parts[3].split(',')]

            duration = 30.0
            if len(parts) > 4 and parts[4]:
                try:
                    duration = float(parts[4])
                except ValueError:
                    duration = 30.0

            task = self.orchestrator.create_task(
                title=title,
                description=description,
                assigned_agents=agents,
                parent_task_id=parent_id,
                estimated_duration_seconds=duration
            )

            print(f"\n✅ Created sub-task: {task.task_id}")
            print(f"   Parent: {parent_id}")
            print(f"   Title: {title}")
            print(f"   Agents: {', '.join(agents)}\n")

        except Exception as e:
            print(f"❌ Error creating sub-task: {e}")

    def handle_assign(self, task_id: str):
        """Handle assign command"""
        if self.orchestrator.assign_task(task_id):
            print(f"✅ Task {task_id} assigned to agents")
        else:
            print(f"❌ Failed to assign task {task_id}")

    def handle_start(self, args: str):
        """Handle start command"""
        parts = args.split()
        if len(parts) < 2:
            print("❌ Usage: /start <task_id> <agent_name>")
            return

        task_id = parts[0]
        agent_name = parts[1]

        if self.orchestrator.start_task(task_id, agent_name):
            print(f"✅ Task {task_id} started by {agent_name}")
        else:
            print(f"❌ Failed to start task {task_id}")

    def handle_progress(self, args: str):
        """Handle progress command"""
        parts = args.split(maxsplit=2)
        if len(parts) < 2:
            print("❌ Usage: /progress <task_id> <percent> [note]")
            return

        task_id = parts[0]
        try:
            percent = float(parts[1])
        except ValueError:
            print("❌ Progress must be a number (0-100)")
            return

        note = parts[2] if len(parts) > 2 else None

        if self.orchestrator.update_task_progress(task_id, percent, note):
            print(f"✅ Updated task {task_id} progress to {percent}%")
        else:
            print(f"❌ Failed to update task {task_id}")

    def handle_complete(self, args: str):
        """Handle complete command"""
        parts = args.split()
        if len(parts) < 2:
            print("❌ Usage: /complete <task_id> <agent_name>")
            return

        task_id = parts[0]
        agent_name = parts[1]

        if self.orchestrator.complete_task(task_id, agent_name):
            print(f"✅ Task {task_id} completed by {agent_name}")
        else:
            print(f"❌ Failed to complete task {task_id}")

    def handle_status(self, task_id: Optional[str] = None):
        """Handle status command"""
        if task_id:
            # Show specific task status
            status = self.orchestrator.get_task_status(task_id)
            if status:
                print(f"\n📋 TASK STATUS: {task_id}")
                print(f"   Title: {status['title']}")
                print(f"   Status: {status['status']}")
                print(f"   Priority: {status['priority']}")
                print(f"   Agents: {', '.join(status['assigned_agents'])}")
                print(f"   Progress: {status['progress']}")
                print(f"   Elapsed: {status['elapsed_time']}")
                print(f"   Est. Remaining: {status['estimated_remaining']}")
                print(f"   Sub-tasks: {status['sub_tasks_count']}")
                print(f"   Notes: {status['notes_count']}\n")
            else:
                print(f"❌ Task {task_id} not found")
        else:
            # Show all tasks status
            status = self.orchestrator.get_all_tasks_status()
            print("\n" + json.dumps(status, indent=2))

    def handle_agents(self, agent_name: Optional[str] = None):
        """Handle agents command"""
        if agent_name:
            # Show specific agent status
            status = self.orchestrator.get_agent_status(agent_name)
            if status:
                print(f"\n👤 AGENT STATUS: {agent_name}")
                print(f"   Assigned Tasks: {status['assigned_tasks']}")
                print(f"   Active Task: {status['active_task'] or 'None'}")
                print(f"   Completed: {status['total_completed']}")
                print(f"   Time Worked: {status['total_time_worked']}")
                print(f"   Utilization: {status['current_utilization']}")
                print(f"   Last Heartbeat: {status['last_heartbeat']}\n")
            else:
                print(f"❌ Agent {agent_name} not found")
        else:
            # Show all agents
            print("\n👥 AVAILABLE AGENTS:\n")
            for agent in self.available_agents:
                status = self.orchestrator.get_agent_status(agent)
                if status:
                    active_icon = "🟢" if status['active_task'] else "⚪"
                    print(f"  {active_icon} {agent}")
                else:
                    print(f"  ⚪ {agent}")
            print()

    def handle_monitor(self):
        """Handle monitor command (toggle)"""
        if not self.monitoring_enabled:
            self.orchestrator.start_monitoring(update_interval_seconds=2.0)
            self.monitoring_enabled = True
            print("🔍 Live monitoring ENABLED")

            try:
                while self.monitoring_enabled:
                    self.display_live_status()
                    time.sleep(2)
            except KeyboardInterrupt:
                self.monitoring_enabled = False
                self.orchestrator.stop_monitoring()
                print("\n⏹️  Live monitoring DISABLED")
        else:
            self.monitoring_enabled = False
            self.orchestrator.stop_monitoring()
            print("⏹️  Live monitoring DISABLED")

    def handle_report(self, args: str):
        """Handle report command"""
        parts = args.split(maxsplit=1)
        if len(parts) < 1:
            print("❌ Usage: /report <task_id> [save_path]")
            return

        task_id = parts[0]
        save_path = parts[1] if len(parts) > 1 else None

        try:
            # Generate report
            report = self.orchestrator.generate_report(task_id, include_sub_tasks=True)
            print(f"\n✅ Generated report: {report.report_id}")
            print(f"   Version: {report.version}")
            print(f"   Generated by: {', '.join(report.generated_by)}\n")

            # Save report
            saved_path = self.orchestrator.save_report(report.report_id, save_path)
            print(f"💾 Report saved to: {saved_path}\n")

        except Exception as e:
            print(f"❌ Error generating report: {e}")

    def handle_reports(self):
        """Handle reports command (show summary)"""
        summary = self.orchestrator.report_manager.get_summary()
        print("\n📊 REPORT MANAGER SUMMARY:")
        print(json.dumps(summary, indent=2))
        print()

    def handle_bus(self):
        """Handle bus command"""
        status = self.bus.get_bus_status()
        print("\n🚌 COMMUNICATION BUS STATUS:")
        print(json.dumps(status, indent=2))
        print()

    def handle_available(self):
        """Handle available command"""
        print("\n👥 AVAILABLE AGENTS:\n")
        for i, agent in enumerate(self.available_agents, 1):
            print(f"  {i:2d}. {agent}")
        print(f"\n  Total: {len(self.available_agents)} agents\n")

    def process_command(self, command: str):
        """Process a user command"""
        command = command.strip()

        if not command:
            return

        if not command.startswith('/'):
            print("❌ Commands must start with /")
            return

        parts = command[1:].split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        # Command routing
        if cmd == "help":
            self.print_help()
        elif cmd == "quit" or cmd == "exit":
            self.running = False
            print("\n👋 Goodbye!\n")
        elif cmd == "clear":
            self._clear_screen()
        elif cmd == "create-task":
            self.handle_create_task(args)
        elif cmd == "create-subtask":
            self.handle_create_subtask(args)
        elif cmd == "assign":
            self.handle_assign(args)
        elif cmd == "start":
            self.handle_start(args)
        elif cmd == "progress":
            self.handle_progress(args)
        elif cmd == "complete":
            self.handle_complete(args)
        elif cmd == "status":
            self.handle_status(args if args else None)
        elif cmd == "agents":
            self.handle_agents(args if args else None)
        elif cmd == "monitor":
            self.handle_monitor()
        elif cmd == "report":
            self.handle_report(args)
        elif cmd == "reports":
            self.handle_reports()
        elif cmd == "bus":
            self.handle_bus()
        elif cmd == "available":
            self.handle_available()
        else:
            print(f"❌ Unknown command: /{cmd}")
            print("   Type /help for available commands")

    def run(self):
        """Main command center loop"""
        self.print_banner()

        while self.running:
            try:
                command = input("\n🤖 TERMINATOR> ").strip()
                if command:
                    self.process_command(command)
            except KeyboardInterrupt:
                print("\n\n⚠️  Use /quit to exit\n")
            except EOFError:
                break
            except Exception as e:
                print(f"❌ Error: {e}")

        # Cleanup
        if self.monitoring_enabled:
            self.orchestrator.stop_monitoring()


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    try:
        command_center = TerminatorCommandCenter()
        command_center.run()
    except KeyboardInterrupt:
        print("\n\n👋 Terminated by user\n")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}\n")
        import traceback
        traceback.print_exc()
