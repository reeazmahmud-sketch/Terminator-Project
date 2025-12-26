# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Task Planner - Intelligent Task Planning and Scheduling
==============================================================

Plans task execution, optimizes schedules, allocates resources,
analyzes critical paths, and adapts plans dynamically.

Features:
- Task scheduling and timeline optimization
- Resource allocation across tasks
- Critical path analysis
- Priority-based scheduling
- Constraint satisfaction
- Adaptive replanning based on changes
- Time estimation and buffer management

Created: December 11, 2025
Part of: TERMINATOR Enhancement Roadmap - Tier 4 (Planning)
"""

import json
import os
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
from uuid import uuid4


# ============================================================================
# Data Structures
# ============================================================================

class ScheduleStatus(Enum):
    """Status of a schedule"""
    PLANNED = "planned"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class ResourceType(Enum):
    """Type of resource"""
    MODEL = "model"
    TOOL = "tool"
    TIME = "time"
    MEMORY = "memory"
    COMPUTE = "compute"


@dataclass
class ResourceAllocation:
    """Allocation of a resource to a task"""
    resource_id: str
    resource_type: ResourceType
    task_id: str
    quantity: float
    allocated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    released_at: Optional[str] = None
    utilization_percent: float = 100.0


@dataclass
class ScheduleSlot:
    """A time slot in the schedule"""
    slot_id: str
    task_id: str
    scheduled_start: str  # ISO format
    scheduled_end: str
    estimated_duration_hours: float
    priority: int
    resources: List[ResourceAllocation] = field(default_factory=list)
    buffer_hours: float = 0.5  # Safety buffer
    critical_path: bool = False  # Is this on the critical path?


@dataclass
class Schedule:
    """A complete task schedule"""
    schedule_id: str
    goal_id: str
    slots: List[ScheduleSlot] = field(default_factory=list)
    status: ScheduleStatus = ScheduleStatus.PLANNED
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    total_duration_hours: float = 0.0
    critical_path_duration_hours: float = 0.0
    efficiency_score: float = 0.0  # 0.0-1.0


# ============================================================================
# Task Scheduler
# ============================================================================

class TaskScheduler:
    """Schedules tasks in optimal order"""

    def schedule_tasks(
        self,
        tasks: Dict[str, Any],
        dependencies: Dict[str, Set[str]],
        start_time: datetime = None
    ) -> Schedule:
        """
        Schedule tasks respecting dependencies

        Args:
            tasks: Dict of {task_id: task_data}
            dependencies: Dict of {task_id: set of dependent task_ids}
            start_time: When to start scheduling

        Returns:
            Schedule with ordered task slots
        """
        if start_time is None:
            start_time = datetime.now()

        schedule = Schedule(
            schedule_id=str(uuid4())[:8],
            goal_id="unknown"  # Would be set by caller
        )

        # Topological sort to get task order
        ordered_tasks = self._topological_sort(tasks, dependencies)

        # Schedule each task
        current_time = start_time

        for task_id in ordered_tasks:
            task = tasks[task_id]
            duration = task.get("estimated_duration_hours", 1.0)
            priority = task.get("priority", 3)

            slot = ScheduleSlot(
                slot_id=str(uuid4())[:8],
                task_id=task_id,
                scheduled_start=current_time.isoformat(),
                scheduled_end=(current_time + timedelta(hours=duration)).isoformat(),
                estimated_duration_hours=duration,
                priority=priority
            )

            schedule.slots.append(slot)
            current_time += timedelta(hours=duration + 0.5)  # 30 min buffer

        # Calculate total duration
        schedule.total_duration_hours = (current_time - start_time).total_seconds() / 3600

        return schedule

    def _topological_sort(
        self,
        tasks: Dict[str, Any],
        dependencies: Dict[str, Set[str]]
    ) -> List[str]:
        """Topological sort of tasks based on dependencies"""
        visited = set()
        stack = []

        def visit(task_id: str) -> None:
            if task_id in visited:
                return

            visited.add(task_id)

            # Visit all dependencies first
            for dep_id in dependencies.get(task_id, set()):
                visit(dep_id)

            stack.append(task_id)

        for task_id in tasks.keys():
            visit(task_id)

        return stack

    def optimize_schedule(self, schedule: Schedule) -> Schedule:
        """Optimize schedule for efficiency"""
        # Find tasks on critical path
        self._identify_critical_path(schedule)

        # Calculate efficiency
        total_estimated = sum(slot.estimated_duration_hours for slot in schedule.slots)
        schedule.efficiency_score = total_estimated / schedule.total_duration_hours if schedule.total_duration_hours > 0 else 0

        return schedule

    def _identify_critical_path(self, schedule: Schedule) -> None:
        """Identify tasks on the critical path"""
        if not schedule.slots:
            return

        # Sort slots by start time
        sorted_slots = sorted(schedule.slots, key=lambda s: s.scheduled_start)

        # Tasks that can't be delayed are on critical path
        for slot in sorted_slots:
            # If this task has dependent tasks, it's critical
            has_dependents = False
            for other_slot in sorted_slots:
                if slot.task_id in other_slot.resources:
                    has_dependents = True
                    break

            slot.critical_path = has_dependents


# ============================================================================
# Resource Allocator
# ============================================================================

class ResourceAllocator:
    """Allocates resources to tasks"""

    def __init__(self):
        """Initialize resource allocator"""
        self.resources: Dict[str, Dict[str, Any]] = {}
        self.allocations: List[ResourceAllocation] = []

    def register_resource(
        self,
        resource_id: str,
        resource_type: ResourceType,
        capacity: float = 1.0
    ) -> None:
        """Register an available resource"""
        self.resources[resource_id] = {
            "type": resource_type,
            "capacity": capacity,
            "available": capacity,
            "registered_at": datetime.now().isoformat()
        }

    def allocate_resource(
        self,
        resource_id: str,
        task_id: str,
        quantity: float
    ) -> Optional[ResourceAllocation]:
        """Allocate resource to task"""
        if resource_id not in self.resources:
            return None

        resource = self.resources[resource_id]

        if resource["available"] < quantity:
            return None  # Not enough capacity

        allocation = ResourceAllocation(
            resource_id=resource_id,
            resource_type=resource["type"],
            task_id=task_id,
            quantity=quantity
        )

        resource["available"] -= quantity
        self.allocations.append(allocation)

        return allocation

    def release_resource(self, resource_id: str, task_id: str) -> None:
        """Release allocated resource"""
        for allocation in self.allocations:
            if allocation.resource_id == resource_id and allocation.task_id == task_id:
                allocation.released_at = datetime.now().isoformat()

                self.resources[resource_id]["available"] += allocation.quantity
                break

    def get_resource_utilization(self) -> Dict[str, float]:
        """Get utilization percentage for each resource"""
        utilization = {}

        for resource_id, resource in self.resources.items():
            used = resource["capacity"] - resource["available"]
            util_percent = (used / resource["capacity"] * 100) if resource["capacity"] > 0 else 0
            utilization[resource_id] = util_percent

        return utilization


# ============================================================================
# Critical Path Analyzer
# ============================================================================

class CriticalPathAnalyzer:
    """Analyzes the critical path through tasks"""

    def analyze(
        self,
        schedule: Schedule,
        dependencies: Dict[str, Set[str]]
    ) -> Dict[str, Any]:
        """Analyze critical path"""
        if not schedule.slots:
            return {"critical_path": [], "duration": 0.0}

        # Find path with maximum total duration
        critical_path = self._find_critical_path(dependencies)
        critical_duration = self._calculate_path_duration(critical_path, schedule)

        return {
            "critical_path": critical_path,
            "duration_hours": critical_duration,
            "num_tasks": len(critical_path),
            "slack_analysis": self._calculate_slack(schedule, dependencies)
        }

    def _find_critical_path(self, dependencies: Dict[str, Set[str]]) -> List[str]:
        """Find the critical path"""
        # Simplified: find longest path
        paths = []

        def find_paths(node: str, current_path: List[str]) -> None:
            current_path.append(node)

            has_dependents = False
            for task_id, deps in dependencies.items():
                if node in deps:
                    has_dependents = True
                    find_paths(task_id, current_path[:])

            if not has_dependents:
                paths.append(current_path)

        # Start from tasks with no dependencies
        start_tasks = [
            task_id for task_id, deps in dependencies.items()
            if not deps
        ]

        for start_task in start_tasks:
            find_paths(start_task, [])

        # Return longest path
        return max(paths, key=len) if paths else []

    def _calculate_path_duration(self, path: List[str], schedule: Schedule) -> float:
        """Calculate duration of a path"""
        duration = 0.0

        for task_id in path:
            slot = next((s for s in schedule.slots if s.task_id == task_id), None)
            if slot:
                duration += slot.estimated_duration_hours

        return duration

    def _calculate_slack(
        self,
        schedule: Schedule,
        dependencies: Dict[str, Set[str]]
    ) -> Dict[str, float]:
        """Calculate slack time for each task"""
        slack = {}

        for slot in schedule.slots:
            # Slack is the difference between scheduled completion and latest possible completion
            # For now, simplified calculation
            slack[slot.task_id] = slot.buffer_hours

        return slack


# ============================================================================
# Adaptive Replanner
# ============================================================================

class AdaptiveReplanner:
    """Replans schedule when conditions change"""

    def replan(
        self,
        schedule: Schedule,
        changes: Dict[str, Any]
    ) -> Schedule:
        """
        Replan based on changes

        Args:
            schedule: Current schedule
            changes: Dictionary of {task_id: {changes}}

        Returns:
            Updated schedule
        """
        updated_schedule = schedule

        for task_id, task_changes in changes.items():
            if "duration_hours" in task_changes:
                # Adjust duration
                slot = next((s for s in updated_schedule.slots if s.task_id == task_id), None)
                if slot:
                    new_duration = task_changes["duration_hours"]
                    duration_change = new_duration - slot.estimated_duration_hours

                    # Update this slot
                    new_end = datetime.fromisoformat(slot.scheduled_end) + timedelta(hours=duration_change)
                    slot.scheduled_end = new_end.isoformat()

                    # Cascade change to subsequent tasks
                    self._cascade_changes(updated_schedule, slot, duration_change)

            if "priority" in task_changes:
                # Update priority
                slot = next((s for s in updated_schedule.slots if s.task_id == task_id), None)
                if slot:
                    slot.priority = task_changes["priority"]

        return updated_schedule

    def _cascade_changes(self, schedule: Schedule, affected_slot: ScheduleSlot, time_change: float) -> None:
        """Cascade time changes to subsequent tasks"""
        affected_start = datetime.fromisoformat(affected_slot.scheduled_end)

        for slot in schedule.slots:
            slot_start = datetime.fromisoformat(slot.scheduled_start)

            if slot_start >= affected_start and slot.task_id != affected_slot.task_id:
                # Shift this task
                new_start = slot_start + timedelta(hours=time_change)
                new_end = datetime.fromisoformat(slot.scheduled_end) + timedelta(hours=time_change)

                slot.scheduled_start = new_start.isoformat()
                slot.scheduled_end = new_end.isoformat()


# ============================================================================
# Main Task Planner
# ============================================================================

class TerminatorTaskPlanner:
    """
    Main task planner that creates optimal schedules, allocates resources,
    analyzes critical paths, and adapts plans dynamically.
    """

    _instance: Optional['TerminatorTaskPlanner'] = None
    _lock = threading.Lock()

    def __init__(self):
        """Initialize task planner"""
        self.scheduler = TaskScheduler()
        self.allocator = ResourceAllocator()
        self.critical_analyzer = CriticalPathAnalyzer()
        self.replanner = AdaptiveReplanner()

        self.schedules: Dict[str, Schedule] = {}
        self.storage_path = "/Users/reeazmahmud/Desktop/Terminator/planning/data"
        os.makedirs(self.storage_path, exist_ok=True)

    @classmethod
    def get_instance(cls) -> 'TerminatorTaskPlanner':
        """Get singleton instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def plan_goal_execution(
        self,
        goal_id: str,
        tasks: Dict[str, Any],
        dependencies: Dict[str, Set[str]],
        start_time: datetime = None
    ) -> Schedule:
        """Plan execution of all goal tasks"""
        schedule = self.scheduler.schedule_tasks(tasks, dependencies, start_time)
        schedule.goal_id = goal_id

        # Optimize schedule
        schedule = self.scheduler.optimize_schedule(schedule)

        # Calculate critical path
        critical_analysis = self.critical_analyzer.analyze(schedule, dependencies)
        schedule.critical_path_duration_hours = critical_analysis["duration_hours"]

        self.schedules[schedule.schedule_id] = schedule
        return schedule

    def allocate_resources_to_schedule(
        self,
        schedule_id: str,
        allocations: Dict[str, Dict[str, float]]
    ) -> None:
        """
        Allocate resources to tasks in schedule

        Args:
            schedule_id: Schedule ID
            allocations: {task_id: {resource_id: quantity}}
        """
        if schedule_id not in self.schedules:
            return

        schedule = self.schedules[schedule_id]

        for task_id, resource_allocs in allocations.items():
            slot = next((s for s in schedule.slots if s.task_id == task_id), None)

            if slot:
                for resource_id, quantity in resource_allocs.items():
                    allocation = self.allocator.allocate_resource(resource_id, task_id, quantity)
                    if allocation:
                        slot.resources.append(allocation)

    def adapt_schedule(
        self,
        schedule_id: str,
        changes: Dict[str, Any]
    ) -> Schedule:
        """Adapt schedule based on changes"""
        if schedule_id not in self.schedules:
            return None

        schedule = self.schedules[schedule_id]
        updated_schedule = self.replanner.replan(schedule, changes)

        self.schedules[schedule_id] = updated_schedule
        return updated_schedule

    def get_schedule_summary(self, schedule_id: str) -> Dict[str, Any]:
        """Get summary of a schedule"""
        if schedule_id not in self.schedules:
            return None

        schedule = self.schedules[schedule_id]

        return {
            "schedule_id": schedule_id,
            "goal_id": schedule.goal_id,
            "status": schedule.status.value,
            "total_duration_hours": schedule.total_duration_hours,
            "critical_path_hours": schedule.critical_path_duration_hours,
            "efficiency_score": schedule.efficiency_score,
            "num_tasks": len(schedule.slots),
            "created_at": schedule.created_at
        }

    def get_next_scheduled_task(self, schedule_id: str) -> Optional[Tuple[str, str, str]]:
        """Get the next task to execute"""
        if schedule_id not in self.schedules:
            return None

        schedule = self.schedules[schedule_id]
        now = datetime.now()

        # Find first unstarted task
        for slot in sorted(schedule.slots, key=lambda s: s.scheduled_start):
            if slot.scheduled_start:
                slot_start = datetime.fromisoformat(slot.scheduled_start)
                if slot_start > now:
                    return (slot.task_id, slot.scheduled_start, slot.scheduled_end)

        return None

    def register_resource(
        self,
        resource_id: str,
        resource_type: ResourceType,
        capacity: float = 1.0
    ) -> None:
        """Register a resource for allocation"""
        self.allocator.register_resource(resource_id, resource_type, capacity)

    def get_resource_utilization(self) -> Dict[str, float]:
        """Get resource utilization"""
        return self.allocator.get_resource_utilization()


# ============================================================================
# Module-level access functions
# ============================================================================

def get_task_planner() -> TerminatorTaskPlanner:
    """Get the task planner instance"""
    return TerminatorTaskPlanner.get_instance()


if __name__ == "__main__":
    # Test the task planner
    planner = get_task_planner()

    # Register resources
    planner.register_resource("gpt4", ResourceType.MODEL, capacity=2.0)
    planner.register_resource("web_search", ResourceType.TOOL, capacity=5.0)

    # Create sample tasks
    tasks = {
        "task1": {"title": "Research", "estimated_duration_hours": 2.0, "priority": 4},
        "task2": {"title": "Analysis", "estimated_duration_hours": 3.0, "priority": 4},
        "task3": {"title": "Implementation", "estimated_duration_hours": 4.0, "priority": 5},
        "task4": {"title": "Testing", "estimated_duration_hours": 2.0, "priority": 4},
    }

    dependencies = {
        "task1": set(),
        "task2": {"task1"},
        "task3": {"task2"},
        "task4": {"task3"},
    }

    # Create schedule
    schedule = planner.plan_goal_execution("goal_001", tasks, dependencies)

    print(f"\n✅ Created schedule: {schedule.schedule_id}")

    # Get summary
    print("\n=== Schedule Summary ===")
    summary = planner.get_schedule_summary(schedule.schedule_id)
    for key, value in summary.items():
        print(f"  {key}: {value}")

    # Allocate resources
    allocations = {
        "task1": {"web_search": 2.0},
        "task2": {"gpt4": 1.0},
        "task3": {"gpt4": 2.0},
        "task4": {"web_search": 1.0},
    }

    planner.allocate_resources_to_schedule(schedule.schedule_id, allocations)

    print("\n=== Resource Utilization ===")
    for resource_id, utilization in planner.get_resource_utilization().items():
        print(f"  {resource_id}: {utilization:.0f}%")

    # Get next task
    print("\n=== Next Task ===")
    next_task = planner.get_next_scheduled_task(schedule.schedule_id)
    if next_task:
        task_id, start, end = next_task
        print(f"  Task: {task_id}")
        print(f"  Start: {start}")
        print(f"  End: {end}")
