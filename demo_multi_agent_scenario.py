#!/usr/bin/env python3
"""
TERMINATOR Multi-Agent System - Real-Life Demo Scenario
========================================================

Demonstrates a complete real-world scenario where TERMINATOR coordinates
multiple sub-agents to complete a complex task with hierarchical structure.

Scenario: "Full System Health Check and Optimization"

Main Task: Perform comprehensive system health check
├── Sub-Task 1: Analyze agent communication patterns (context_awareness_agent)
├── Sub-Task 2: Check resource utilization (resource_manager_agent)
├── Sub-Task 3: Review error logs (error_monitor_agent)
├── Sub-Task 4: Assess code quality (qa_agent)
└── Sub-Task 5: Generate optimization recommendations (project_monitor_agent)

Features Demonstrated:
✅ Hierarchical task structure (main task with sub-tasks)
✅ Multiple agents working concurrently
✅ Live status monitoring
✅ Time tracking for all agents
✅ Progress updates
✅ Report generation with version control
✅ Report reuse enforcement

Created: December 17, 2025
"""

import sys
import os
import time
import asyncio
from datetime import datetime

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core'))

from core.terminator_multi_agent_orchestrator import (
    get_orchestrator,
    TaskPriority
)
from core.terminator_agent_communication_bus import get_communication_bus


class DemoScenario:
    """Real-life demo scenario orchestration"""

    def __init__(self):
        self.orchestrator = get_orchestrator()
        self.bus = get_communication_bus()
        self.task_ids = {}

    def print_section(self, title: str, icon: str = "🎯"):
        """Print section header"""
        print("\n" + "="*80)
        print(f"{icon} {title}")
        print("="*80 + "\n")

    def wait_with_progress(self, seconds: float, message: str = "Working"):
        """Visual progress indicator"""
        print(f"\n{message}", end="", flush=True)
        for _ in range(int(seconds)):
            print(".", end="", flush=True)
            time.sleep(1)
        print(" Done!\n")

    def simulate_agent_work(self, task_id: str, agent_name: str, work_time: float):
        """Simulate an agent working on a task"""
        # Start task
        self.orchestrator.start_task(task_id, agent_name)
        print(f"🚀 {agent_name} started working on {task_id}")

        # Simulate progress updates
        steps = 5
        for i in range(1, steps + 1):
            progress = (i / steps) * 100
            time.sleep(work_time / steps)

            note = f"Step {i}/{steps} completed"
            self.orchestrator.update_task_progress(task_id, progress, note)

            print(f"   📊 Progress: {progress:.0f}% - {note}")

        # Complete task
        results = {
            "completed_at": datetime.now().isoformat(),
            "agent": agent_name,
            "success": True
        }
        self.orchestrator.complete_task(task_id, agent_name, results)
        print(f"✅ {agent_name} completed {task_id}\n")

    def run_scenario(self):
        """Execute the full demo scenario"""

        self.print_section("TERMINATOR Multi-Agent System Demo", "🤖")

        print("""
This demo demonstrates a real-world scenario where TERMINATOR coordinates
multiple specialized agents to perform a comprehensive system health check.

Scenario: Full System Health Check and Optimization

Main Task → 5 Sub-Tasks (executed by different agent teams)
        """)

        input("Press Enter to start the demo...")

        # ============================================================================
        # Phase 1: Create Main Task
        # ============================================================================

        self.print_section("Phase 1: Creating Main Task", "📝")

        main_task = self.orchestrator.create_task(
            title="Complete System Health Check and Optimization",
            description="Comprehensive analysis of the TERMINATOR system including "
                       "communication patterns, resource usage, error tracking, "
                       "code quality, and optimization recommendations",
            assigned_agents=["project_monitor_agent", "context_awareness_agent"],
            priority=TaskPriority.CRITICAL,
            requirements=[
                "Analyze all core subsystems",
                "Identify performance bottlenecks",
                "Review agent communication efficiency",
                "Assess resource utilization",
                "Generate actionable recommendations"
            ],
            estimated_duration_seconds=180.0
        )

        self.task_ids['main'] = main_task.task_id

        print(f"✅ Created main task: {main_task.task_id}")
        print(f"   Title: {main_task.title}")
        print(f"   Priority: {main_task.priority.value}")
        print(f"   Estimated Duration: 180 seconds")

        time.sleep(2)

        # ============================================================================
        # Phase 2: Create Sub-Tasks
        # ============================================================================

        self.print_section("Phase 2: Creating Sub-Tasks", "🔀")

        # Sub-task 1: Communication Analysis
        sub_task_1 = self.orchestrator.create_task(
            title="Analyze Agent Communication Patterns",
            description="Review message bus traffic, analyze communication efficiency, "
                       "identify bottlenecks in inter-agent messaging",
            assigned_agents=["context_awareness_agent"],
            parent_task_id=main_task.task_id,
            priority=TaskPriority.HIGH,
            estimated_duration_seconds=30.0
        )
        self.task_ids['sub1'] = sub_task_1.task_id
        print(f"✅ Sub-Task 1: {sub_task_1.task_id} - Communication Analysis")

        # Sub-task 2: Resource Utilization
        sub_task_2 = self.orchestrator.create_task(
            title="Check Resource Utilization",
            description="Monitor CPU, memory, and network usage across all agents",
            assigned_agents=["resource_manager_agent"],
            parent_task_id=main_task.task_id,
            priority=TaskPriority.HIGH,
            estimated_duration_seconds=25.0
        )
        self.task_ids['sub2'] = sub_task_2.task_id
        print(f"✅ Sub-Task 2: {sub_task_2.task_id} - Resource Check")

        # Sub-task 3: Error Log Review
        sub_task_3 = self.orchestrator.create_task(
            title="Review Error Logs and Anomalies",
            description="Analyze system logs, identify recurring errors, track anomalies",
            assigned_agents=["error_monitor_agent"],
            parent_task_id=main_task.task_id,
            priority=TaskPriority.NORMAL,
            estimated_duration_seconds=35.0
        )
        self.task_ids['sub3'] = sub_task_3.task_id
        print(f"✅ Sub-Task 3: {sub_task_3.task_id} - Error Analysis")

        # Sub-task 4: Code Quality Assessment
        sub_task_4 = self.orchestrator.create_task(
            title="Assess Code Quality",
            description="Review code metrics, identify technical debt, check best practices",
            assigned_agents=["qa_agent"],
            parent_task_id=main_task.task_id,
            priority=TaskPriority.NORMAL,
            estimated_duration_seconds=40.0
        )
        self.task_ids['sub4'] = sub_task_4.task_id
        print(f"✅ Sub-Task 4: {sub_task_4.task_id} - Quality Assessment")

        # Sub-task 5: Optimization Recommendations
        sub_task_5 = self.orchestrator.create_task(
            title="Generate Optimization Recommendations",
            description="Compile findings and create actionable optimization plan",
            assigned_agents=["project_monitor_agent"],
            parent_task_id=main_task.task_id,
            priority=TaskPriority.HIGH,
            estimated_duration_seconds=45.0
        )
        self.task_ids['sub5'] = sub_task_5.task_id
        print(f"✅ Sub-Task 5: {sub_task_5.task_id} - Recommendations")

        time.sleep(2)

        # ============================================================================
        # Phase 3: Assign All Tasks
        # ============================================================================

        self.print_section("Phase 3: Assigning Tasks to Agents", "📤")

        for task_name, task_id in self.task_ids.items():
            self.orchestrator.assign_task(task_id)
            print(f"✅ Assigned {task_name}: {task_id}")
            time.sleep(0.5)

        time.sleep(2)

        # ============================================================================
        # Phase 4: Start Live Monitoring
        # ============================================================================

        self.print_section("Phase 4: Starting Live Monitoring", "🔍")

        self.orchestrator.start_monitoring(update_interval_seconds=1.0)
        print("✅ Live monitoring enabled (updates every 1 second)")

        time.sleep(2)

        # ============================================================================
        # Phase 5: Execute Tasks (Simulated)
        # ============================================================================

        self.print_section("Phase 5: Executing Tasks", "⚙️")

        print("Agents are now working on their assigned tasks...\n")

        # Start main task
        self.orchestrator.start_task(main_task.task_id, "project_monitor_agent")
        self.orchestrator.update_task_progress(main_task.task_id, 5.0, "Coordinating sub-tasks")

        time.sleep(1)

        # Execute sub-tasks (simulated concurrent execution)
        print("\n🔄 Executing Sub-Tasks...\n")

        # Sub-task 1
        self.simulate_agent_work(
            self.task_ids['sub1'],
            "context_awareness_agent",
            work_time=8.0
        )

        # Sub-task 2 (concurrent-ish)
        self.simulate_agent_work(
            self.task_ids['sub2'],
            "resource_manager_agent",
            work_time=6.0
        )

        # Update main task
        self.orchestrator.update_task_progress(main_task.task_id, 40.0, "2/5 sub-tasks completed")

        # Sub-task 3
        self.simulate_agent_work(
            self.task_ids['sub3'],
            "error_monitor_agent",
            work_time=7.0
        )

        # Sub-task 4
        self.simulate_agent_work(
            self.task_ids['sub4'],
            "qa_agent",
            work_time=8.0
        )

        # Update main task
        self.orchestrator.update_task_progress(main_task.task_id, 80.0, "4/5 sub-tasks completed")

        # Sub-task 5
        self.simulate_agent_work(
            self.task_ids['sub5'],
            "project_monitor_agent",
            work_time=9.0
        )

        # Complete main task
        self.orchestrator.update_task_progress(main_task.task_id, 100.0, "All sub-tasks completed")
        self.orchestrator.complete_task(main_task.task_id, "project_monitor_agent")

        time.sleep(2)

        # ============================================================================
        # Phase 6: Show Final Status
        # ============================================================================

        self.print_section("Phase 6: Final Status Report", "📊")

        # Show main task status
        main_status = self.orchestrator.get_task_status(main_task.task_id)
        print("MAIN TASK:")
        print(f"  Title: {main_status['title']}")
        print(f"  Status: {main_status['status']}")
        print(f"  Progress: {main_status['progress']}")
        print(f"  Total Time: {main_status['elapsed_time']}")
        print(f"  Sub-tasks: {main_status['sub_tasks_count']}")

        print("\nSUB-TASKS:")
        for i, (name, task_id) in enumerate(list(self.task_ids.items())[1:], 1):
            status = self.orchestrator.get_task_status(task_id)
            print(f"\n  {i}. {status['title']}")
            print(f"     Status: {status['status']}")
            print(f"     Progress: {status['progress']}")
            print(f"     Time: {status['elapsed_time']}")
            print(f"     Agent: {', '.join(status['assigned_agents'])}")

        print("\nAGENT WORKLOADS:")
        all_status = self.orchestrator.get_all_tasks_status()
        for agent_name, workload in all_status['agent_workloads'].items():
            if workload['completed_tasks'] > 0:
                print(f"\n  👤 {agent_name}:")
                print(f"     Completed Tasks: {workload['completed_tasks']}")
                print(f"     Time Worked: {workload['time_worked']}")

        time.sleep(2)

        # ============================================================================
        # Phase 7: Generate Reports
        # ============================================================================

        self.print_section("Phase 7: Generating Reports", "📄")

        # Generate report for main task
        print("Generating main task report...")
        main_report = self.orchestrator.generate_report(
            main_task.task_id,
            title="System Health Check Report",
            include_sub_tasks=True
        )

        print(f"\n✅ Generated report: {main_report.report_id}")
        print(f"   Version: {main_report.version}")
        print(f"   Generated by: {', '.join(main_report.generated_by)}")

        # Save report
        save_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "reports",
            f"system_health_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        saved_path = self.orchestrator.save_report(main_report.report_id, save_path)
        print(f"\n💾 Report saved to: {saved_path}")

        # Demonstrate report reuse
        print("\n🔄 Demonstrating report reuse...")
        print("Updating report instead of creating new copy...")

        updated_report = self.orchestrator.report_manager.update_report(
            main_report.report_id,
            content=main_report.content + "\n\n## Update\nAdded final summary notes.",
            updated_by=["project_monitor_agent"]
        )

        print(f"✅ Updated report to version {updated_report.version}")

        # Save updated version (overwrites existing file)
        self.orchestrator.save_report(updated_report.report_id, save_path)
        print(f"💾 Saved updated report (reused same file)")

        # Show report summary
        time.sleep(1)
        print("\n📊 Report Manager Summary:")
        summary = self.orchestrator.report_manager.get_summary()
        print(f"   Total Reports: {summary['total_reports']}")
        print(f"   Tasks with Reports: {summary['total_tasks_with_reports']}")
        print(f"   Max Copies Allowed: {summary['max_copies_allowed']}")

        time.sleep(2)

        # ============================================================================
        # Phase 8: Cleanup
        # ============================================================================

        self.print_section("Phase 8: Demo Complete", "🎉")

        # Stop monitoring
        self.orchestrator.stop_monitoring()
        print("⏹️  Stopped live monitoring")

        print("\n✅ Demo scenario completed successfully!")
        print("\n📋 Summary:")
        print(f"   • Main Task: 1")
        print(f"   • Sub-Tasks: 5")
        print(f"   • Agents Used: 5")
        print(f"   • Reports Generated: 1 (2 versions)")
        print(f"   • Total Time: ~{sum([8, 6, 7, 8, 9]):.0f} seconds")

        print("\n🚀 You can now:")
        print("   1. Run './terminator_command_center.py' for interactive control")
        print("   2. Check generated reports in ./reports/ directory")
        print("   3. Review agent communication bus logs")

        print("\n" + "="*80)
        print("Thank you for using TERMINATOR Multi-Agent System!")
        print("="*80 + "\n")


def main():
    """Main entry point"""
    try:
        demo = DemoScenario()
        demo.run_scenario()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user\n")
    except Exception as e:
        print(f"\n❌ Error in demo: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
