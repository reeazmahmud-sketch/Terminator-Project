# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR PROJECT TARGET AGENT
============================

Main Focus: Maintain project targets and track all requirements
- Track past, current, and future tasks
- Monitor project requirements
- Daily reporting at scheduled time
- Real-time updates when code/modules change
- Ensure timely completion of requirements

Created: December 13, 2025
Part of: TERMINATOR Continuous Project Management System
"""

import json
import os
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from pathlib import Path
from enum import Enum
import hashlib

# Import communication bus
try:
    from core.terminator_agent_communication_bus import get_communication_bus, MessageType, MessagePriority
except ImportError:
    get_communication_bus = None


# ============================================================================
# DATA STRUCTURES
# ============================================================================

class TaskStatus(Enum):
    """Task status enum"""
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    SCHEDULED = "scheduled"
    OVERDUE = "overdue"
    PENDING = "pending"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority enum"""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    TRIVIAL = 1


@dataclass
class Task:
    """Represents a single project task"""
    task_id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    created_date: str
    start_date: Optional[str] = None
    due_date: Optional[str] = None
    completed_date: Optional[str] = None
    assigned_to: str = "Terminator"
    requirements: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    related_files: List[str] = field(default_factory=list)
    progress_percent: int = 0
    notes: List[str] = field(default_factory=list)
    changes_detected: List[str] = field(default_factory=list)
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ProjectState:
    """Overall project state"""
    project_name: str
    project_description: str
    total_tasks: int = 0
    completed_tasks: int = 0
    in_progress_tasks: int = 0
    blocked_tasks: int = 0
    overdue_tasks: int = 0
    health_score: float = 100.0
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    creation_date: str = field(default_factory=lambda: datetime.now().isoformat())


# ============================================================================
# PROJECT TARGET AGENT
# ============================================================================

class TerminatorProjectTargetAgent:
    """
    Agent responsible for maintaining project targets and tracking requirements.

    Features:
    - Maintain comprehensive task list
    - Track past, current, and future tasks
    - Daily reporting at scheduled time
    - Real-time change detection
    - Requirement fulfillment tracking
    - Automatic status updates
    """

    _instance: Optional['TerminatorProjectTargetAgent'] = None
    _lock = threading.Lock()

    def __init__(self, project_name: str = "TERMINATOR", project_dir: str = "/Users/reeazmahmud/Desktop/Terminator"):
        """Initialize Project Target Agent"""

        self.agent_name = "ProjectTargetAgent"
        self.project_name = project_name
        self.project_dir = Path(project_dir)
        self.data_dir = self.project_dir / "project_data" / "target_agent"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize bus communication
        self.bus = get_communication_bus() if get_communication_bus else None
        if self.bus:
            self.bus.register_agent(self.agent_name, self)

        # Data storage
        self.tasks: Dict[str, Task] = {}
        self.project_state = ProjectState(
            project_name=project_name,
            project_description="TERMINATOR Autonomous AI Assistant System"
        )

        # File tracking for change detection
        self.file_hashes: Dict[str, str] = {}
        self.last_scan_time = datetime.now()

        # Scheduling
        self.reporting_time = "09:00"  # Daily report at 9 AM
        self.reporting_enabled = True
        self.reporting_thread: Optional[threading.Thread] = None

        # Load existing data
        self._load_project_state()
        self._load_tasks()

    @classmethod
    def get_instance(cls, project_name: str = "TERMINATOR") -> 'TerminatorProjectTargetAgent':
        """Get singleton instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(project_name)
        return cls._instance

    # ========================================================================
    # TASK MANAGEMENT
    # ========================================================================

    def add_task(self,
                 title: str,
                 description: str,
                 priority: TaskPriority = TaskPriority.MEDIUM,
                 due_date: Optional[str] = None,
                 requirements: List[str] = None,
                 dependencies: List[str] = None) -> str:
        """Add new task to project"""

        task_id = f"TASK-{len(self.tasks) + 1:04d}"

        task = Task(
            task_id=task_id,
            title=title,
            description=description,
            status=TaskStatus.SCHEDULED,
            priority=priority,
            created_date=datetime.now().isoformat(),
            due_date=due_date,
            assigned_to="Terminator",
            requirements=requirements or [],
            dependencies=dependencies or []
        )

        self.tasks[task_id] = task
        self._update_project_state()
        self._save_tasks()

        # Notify via bus
        if self.bus:
            self.bus.send_message(
                sender_agent=self.agent_name,
                recipient_agent="Terminator",
                message_type=MessageType.NOTIFICATION,
                subject="task_created",
                content={
                    "event": "task_created",
                    "task_id": task_id,
                    "title": title,
                    "priority": priority.name
                }
            )

        return task_id

    def update_task_status(self, task_id: str, new_status: TaskStatus, notes: str = "") -> bool:
        """Update task status"""

        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        old_status = task.status

        task.status = new_status
        task.last_updated = datetime.now().isoformat()

        if notes:
            task.notes.append(f"[{datetime.now().isoformat()}] {notes}")

        # Set completion date if completed
        if new_status == TaskStatus.COMPLETED:
            task.completed_date = datetime.now().isoformat()
            task.progress_percent = 100

        # Set start date if in progress
        if new_status == TaskStatus.IN_PROGRESS and not task.start_date:
            task.start_date = datetime.now().isoformat()

        self._update_project_state()
        self._save_tasks()

        # Notify via bus
        if self.bus:
            self.bus.send_message(
                sender_agent=self.agent_name,
                recipient_agent="Terminator",
                message_type=MessageType.NOTIFICATION,
                subject="task_status_changed",
                content={
                    "event": "task_status_changed",
                    "task_id": task_id,
                    "old_status": old_status.value,
                    "new_status": new_status.value
                }
            )

        return True

    def update_task_progress(self, task_id: str, progress_percent: int) -> bool:
        """Update task progress"""

        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        task.progress_percent = min(100, max(0, progress_percent))
        task.last_updated = datetime.now().isoformat()

        self._save_tasks()

        return True

    def detect_code_changes(self) -> Dict[str, Any]:
        """Detect changes in code/modules"""

        changes = {
            "added_files": [],
            "modified_files": [],
            "deleted_files": [],
            "timestamp": datetime.now().isoformat()
        }

        # Scan project directory for changes
        for file_path in self.project_dir.rglob("*"):
            if file_path.is_file() and not str(file_path).startswith("."):
                try:
                    with open(file_path, 'rb') as f:
                        content_hash = hashlib.md5(f.read()).hexdigest()

                    file_key = str(file_path)

                    if file_key not in self.file_hashes:
                        # New file
                        changes["added_files"].append(str(file_path.relative_to(self.project_dir)))
                    elif self.file_hashes[file_key] != content_hash:
                        # Modified file
                        changes["modified_files"].append(str(file_path.relative_to(self.project_dir)))

                    self.file_hashes[file_key] = content_hash

                except:
                    pass

        # Check for deleted files
        deleted_keys = [k for k in self.file_hashes if not Path(k).exists()]
        for deleted_key in deleted_keys:
            changes["deleted_files"].append(str(Path(deleted_key).relative_to(self.project_dir)))
            del self.file_hashes[deleted_key]

        return changes

    def update_task_from_changes(self, task_id: str, changes: List[str]) -> bool:
        """Update task with detected changes"""

        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        task.changes_detected = changes
        task.last_updated = datetime.now().isoformat()

        self._save_tasks()

        # Notify via bus
        if self.bus:
            self.bus.send_message(
                sender_agent=self.agent_name,
                recipient_agent="Terminator",
                message_type=MessageType.NOTIFICATION,
                subject="task_changes_detected",
                content={
                    "event": "task_changes_detected",
                    "task_id": task_id,
                    "changes_count": len(changes),
                    "changes": changes[:5]  # First 5 changes
                }
            )

        return True

    # ========================================================================
    # REPORTING & DISPLAY
    # ========================================================================

    def get_daily_report(self) -> Dict[str, Any]:
        """Generate daily report of tasks"""

        past_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]
        current_tasks = [t for t in self.tasks.values()
                        if t.status in [TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED]]
        future_tasks = [t for t in self.tasks.values()
                       if t.status in [TaskStatus.SCHEDULED, TaskStatus.PENDING]]

        return {
            "timestamp": datetime.now().isoformat(),
            "project": self.project_name,
            "summary": {
                "total_tasks": len(self.tasks),
                "completed": len(past_tasks),
                "in_progress": sum(1 for t in current_tasks if t.status == TaskStatus.IN_PROGRESS),
                "blocked": sum(1 for t in current_tasks if t.status == TaskStatus.BLOCKED),
                "scheduled": len(future_tasks),
                "overdue": sum(1 for t in self.tasks.values() if t.status == TaskStatus.OVERDUE),
                "health_score": self.project_state.health_score
            },
            "past_tasks": [
                {
                    "id": t.task_id,
                    "title": t.title,
                    "completed_date": t.completed_date
                }
                for t in sorted(past_tasks, key=lambda x: x.completed_date, reverse=True)[:5]
            ],
            "current_tasks": [
                {
                    "id": t.task_id,
                    "title": t.title,
                    "status": t.status.value,
                    "priority": t.priority.name,
                    "progress": f"{t.progress_percent}%",
                    "due_date": t.due_date
                }
                for t in sorted(current_tasks, key=lambda x: x.priority.value, reverse=True)
            ],
            "future_tasks": [
                {
                    "id": t.task_id,
                    "title": t.title,
                    "priority": t.priority.name,
                    "due_date": t.due_date
                }
                for t in sorted(future_tasks, key=lambda x: x.priority.value, reverse=True)[:5]
            ]
        }

    def display_daily_report(self) -> str:
        """Display formatted daily report"""

        report = self.get_daily_report()

        output = f"""
================================================================================
                    📊 PROJECT TARGET REPORT - DAILY
================================================================================
Project: {report['project']}
Generated: {report['timestamp']}

SUMMARY
-------
Total Tasks: {report['summary']['total_tasks']}
Completed: {report['summary']['completed']} ✅
In Progress: {report['summary']['in_progress']} 🔄
Blocked: {report['summary']['blocked']} 🚫
Scheduled: {report['summary']['scheduled']} 📋
Overdue: {report['summary']['overdue']} ⏰
Health Score: {report['summary']['health_score']:.1f}%

PAST TASKS (Last 5 Completed)
-----------------------------
"""

        for task in report['past_tasks']:
            output += f"✅ {task['id']}: {task['title']}\n   Completed: {task['completed_date']}\n"

        output += f"""
CURRENT TASKS (In Progress / Blocked)
-------------------------------------
"""

        for task in report['current_tasks']:
            status_icon = "🔄" if task['status'] == "in_progress" else "🚫"
            output += f"{status_icon} {task['id']}: {task['title']}\n"
            output += f"   Status: {task['status']} | Priority: {task['priority']} | Progress: {task['progress']}\n"
            if task['due_date']:
                output += f"   Due: {task['due_date']}\n"

        output += f"""
FUTURE TASKS (Next 5 Scheduled)
-------------------------------
"""

        for task in report['future_tasks']:
            output += f"📋 {task['id']}: {task['title']}\n"
            output += f"   Priority: {task['priority']}"
            if task['due_date']:
                output += f" | Due: {task['due_date']}"
            output += "\n"

        output += """
================================================================================
"""

        return output

    # ========================================================================
    # SCHEDULING & NOTIFICATIONS
    # ========================================================================

    def start_daily_reporting(self, time_str: str = "09:00") -> None:
        """Start daily reporting at specified time"""

        self.reporting_time = time_str
        self.reporting_enabled = True

        if self.reporting_thread is None or not self.reporting_thread.is_alive():
            self.reporting_thread = threading.Thread(
                target=self._daily_reporting_loop,
                daemon=True
            )
            self.reporting_thread.start()

    def stop_daily_reporting(self) -> None:
        """Stop daily reporting"""

        self.reporting_enabled = False

    def _daily_reporting_loop(self) -> None:
        """Background loop for daily reporting"""

        while self.reporting_enabled:
            try:
                # Calculate time until next report
                now = datetime.now()
                target_time = datetime.strptime(self.reporting_time, "%H:%M").replace(
                    year=now.year,
                    month=now.month,
                    day=now.day
                )

                # If target time passed today, schedule for tomorrow
                if now > target_time:
                    target_time += timedelta(days=1)

                # Sleep until target time
                wait_seconds = (target_time - now).total_seconds()

                if wait_seconds > 0:
                    asyncio.run(asyncio.sleep(min(wait_seconds, 3600)))  # Max 1 hour checks

                # Generate and send report
                if datetime.now().hour == int(self.reporting_time.split(":")[0]):
                    self._send_daily_report()

            except Exception as e:
                print(f"Error in daily reporting loop: {e}")

    def _send_daily_report(self) -> None:
        """Send daily report via communication bus"""

        report = self.get_daily_report()
        display_text = self.display_daily_report()

        if self.bus:
            self.bus.send_message(
                sender_agent=self.agent_name,
                recipient_agent="Terminator",
                message_type=MessageType.NOTIFICATION,
                subject="daily_report",
                content={
                    "event": "daily_report",
                    "report": report,
                    "display": display_text
                },
                priority=MessagePriority.HIGH
            )

        # Also print to console
        print(display_text)

    # ========================================================================
    # PERSISTENCE
    # ========================================================================

    def _update_project_state(self) -> None:
        """Update project state based on tasks"""

        self.project_state.total_tasks = len(self.tasks)
        self.project_state.completed_tasks = sum(1 for t in self.tasks.values()
                                                 if t.status == TaskStatus.COMPLETED)
        self.project_state.in_progress_tasks = sum(1 for t in self.tasks.values()
                                                   if t.status == TaskStatus.IN_PROGRESS)
        self.project_state.blocked_tasks = sum(1 for t in self.tasks.values()
                                              if t.status == TaskStatus.BLOCKED)
        self.project_state.overdue_tasks = sum(1 for t in self.tasks.values()
                                              if t.status == TaskStatus.OVERDUE)

        # Calculate health score
        if self.project_state.total_tasks > 0:
            completion_rate = self.project_state.completed_tasks / self.project_state.total_tasks
            self.project_state.health_score = (completion_rate * 100) - (self.project_state.overdue_tasks * 5)
        else:
            self.project_state.health_score = 100.0

        self.project_state.last_updated = datetime.now().isoformat()
        self._save_project_state()

    def _save_project_state(self) -> None:
        """Save project state to file"""

        state_file = self.data_dir / "project_state.json"

        with open(state_file, 'w') as f:
            json.dump(asdict(self.project_state), f, indent=2)

    def _save_tasks(self) -> None:
        """Save tasks to file"""

        tasks_file = self.data_dir / "tasks.json"

        tasks_data = {
            task_id: {
                **asdict(task),
                "status": task.status.value,
                "priority": task.priority.value
            }
            for task_id, task in self.tasks.items()
        }

        with open(tasks_file, 'w') as f:
            json.dump(tasks_data, f, indent=2)

    def _load_project_state(self) -> None:
        """Load project state from file"""

        state_file = self.data_dir / "project_state.json"

        if state_file.exists():
            with open(state_file, 'r') as f:
                data = json.load(f)
                self.project_state = ProjectState(**data)

    def _load_tasks(self) -> None:
        """Load tasks from file"""

        tasks_file = self.data_dir / "tasks.json"

        if tasks_file.exists():
            with open(tasks_file, 'r') as f:
                tasks_data = json.load(f)
                for task_id, task_dict in tasks_data.items():
                    task_dict['status'] = TaskStatus(task_dict['status'])
                    task_dict['priority'] = TaskPriority(task_dict['priority'])
                    self.tasks[task_id] = Task(**task_dict)

    # ========================================================================
    # UTILITIES
    # ========================================================================

    def get_project_summary(self) -> Dict[str, Any]:
        """Get high-level project summary"""

        return {
            "project_name": self.project_name,
            "total_tasks": len(self.tasks),
            "completed_percent": (self.project_state.completed_tasks / len(self.tasks) * 100) if self.tasks else 0,
            "health_score": self.project_state.health_score,
            "created": self.project_state.creation_date,
            "last_updated": self.project_state.last_updated
        }


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def get_project_target_agent(project_name: str = "TERMINATOR") -> TerminatorProjectTargetAgent:
    """Get or create Project Target Agent instance"""
    return TerminatorProjectTargetAgent.get_instance(project_name)
