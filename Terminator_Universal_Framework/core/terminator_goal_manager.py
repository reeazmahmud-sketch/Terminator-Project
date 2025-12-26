# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Goal Manager - Multi-Step Goal Planning and Tracking
==========================================================

Manages complex multi-step goals, breaks them into milestones and tasks,
tracks progress, detects obstacles, and adapts plans.

Features:
- Goal decomposition into subtasks and milestones
- Dependency graph management
- Progress tracking with real-time updates
- Obstacle detection and mitigation
- Adaptive replanning
- Timeline estimation
- Priority management

Created: December 11, 2025
Part of: TERMINATOR Enhancement Roadmap - Tier 4 (Planning)
"""

import json
import os
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Set, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from uuid import uuid4


# ============================================================================
# Data Structures
# ============================================================================

class GoalStatus(Enum):
    """Status of a goal"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskStatus(Enum):
    """Status of a task"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class ObstacleType(Enum):
    """Type of obstacle"""
    RESOURCE_SHORTAGE = "resource_shortage"
    DEPENDENCY_BLOCKED = "dependency_blocked"
    TIME_CONSTRAINT = "time_constraint"
    EXTERNAL_BLOCKER = "external_blocker"
    TECHNICAL_ISSUE = "technical_issue"


@dataclass
class Task:
    """A single task within a goal"""
    task_id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.NOT_STARTED
    estimated_duration_hours: float = 1.0
    actual_duration_hours: float = 0.0
    priority: int = 3  # 1-5
    dependencies: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    assigned_to: Optional[str] = None
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['status'] = self.status.value
        return data


@dataclass
class Milestone:
    """A milestone within a goal"""
    milestone_id: str
    title: str
    description: str
    target_date: str
    tasks: List[str] = field(default_factory=list)  # Task IDs
    completed: bool = False
    completion_date: Optional[str] = None


@dataclass
class Obstacle:
    """An obstacle blocking progress"""
    obstacle_id: str
    obstacle_type: ObstacleType
    description: str
    affected_tasks: List[str] = field(default_factory=list)
    severity: int = 2  # 1-5
    mitigation_steps: List[str] = field(default_factory=list)
    resolved: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Goal:
    """A complex multi-step goal"""
    goal_id: str
    title: str
    description: str
    status: GoalStatus = GoalStatus.PLANNED
    priority: int = 3  # 1-5
    target_completion_date: Optional[str] = None
    tasks: Dict[str, Task] = field(default_factory=dict)
    milestones: List[Milestone] = field(default_factory=list)
    obstacles: List[Obstacle] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    success_criteria: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['status'] = self.status.value
        data['tasks'] = {k: v.to_dict() if hasattr(v, 'to_dict') else v for k, v in self.tasks.items()}
        return data


# ============================================================================
# Dependency Graph
# ============================================================================

class DependencyGraph:
    """Manages task dependencies"""

    def __init__(self):
        """Initialize dependency graph"""
        self.graph: Dict[str, Set[str]] = {}  # task_id -> set of dependent task_ids
        self.reverse_graph: Dict[str, Set[str]] = {}  # task_id -> set of prerequisite task_ids

    def add_dependency(self, task_id: str, depends_on: str) -> None:
        """Add a dependency"""
        if task_id not in self.graph:
            self.graph[task_id] = set()
        if depends_on not in self.reverse_graph:
            self.reverse_graph[depends_on] = set()

        self.graph[task_id].add(depends_on)
        self.reverse_graph[depends_on].add(task_id)

    def get_dependencies(self, task_id: str) -> Set[str]:
        """Get all tasks that must complete before this one"""
        return self.graph.get(task_id, set())

    def get_dependents(self, task_id: str) -> Set[str]:
        """Get all tasks that depend on this one"""
        return self.reverse_graph.get(task_id, set())

    def can_start_task(self, task_id: str, completed_tasks: Set[str]) -> bool:
        """Check if task can start (all dependencies complete)"""
        dependencies = self.get_dependencies(task_id)
        return all(dep_id in completed_tasks for dep_id in dependencies)

    def find_circular_dependencies(self) -> List[List[str]]:
        """Find any circular dependencies (should be none)"""
        cycles = []

        def visit(node: str, visiting: Set[str], path: List[str]) -> None:
            if node in visiting:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return

            visiting.add(node)
            path.append(node)

            for dependent in self.get_dependencies(node):
                visit(dependent, visiting, path[:])

            visiting.remove(node)

        for task_id in self.graph.keys():
            visit(task_id, set(), [])

        return cycles


# ============================================================================
# Goal Decomposer
# ============================================================================

class GoalDecomposer:
    """Decomposes goals into manageable tasks"""

    def decompose_goal(
        self,
        goal_title: str,
        goal_description: str,
        complexity: float = 0.5  # 0.0-1.0
    ) -> Dict[str, Any]:
        """
        Decompose a goal into tasks and milestones

        Args:
            goal_title: Title of the goal
            goal_description: Detailed description
            complexity: Estimated complexity (affects number of subtasks)

        Returns:
            Dictionary with suggested decomposition
        """
        # Estimate number of tasks based on complexity
        base_tasks = 3
        num_tasks = max(base_tasks, int(base_tasks + complexity * 7))
        num_milestones = max(2, int(num_tasks / 3))

        tasks = self._generate_tasks(goal_description, num_tasks)
        milestones = self._generate_milestones(num_milestones, len(tasks))

        return {
            "tasks": tasks,
            "milestones": milestones,
            "estimated_complexity": complexity,
            "estimated_total_hours": sum(t["estimated_duration_hours"] for t in tasks),
            "estimated_milestones": num_milestones
        }

    def _generate_tasks(self, description: str, count: int) -> List[Dict[str, Any]]:
        """Generate task suggestions based on description"""
        task_suggestions = [
            {"title": "Planning & Requirements", "description": "Define clear objectives and success criteria"},
            {"title": "Research & Analysis", "description": "Gather information and analyze requirements"},
            {"title": "Design", "description": "Create design and architecture"},
            {"title": "Implementation", "description": "Implement the solution"},
            {"title": "Testing & Validation", "description": "Test and validate results"},
            {"title": "Refinement", "description": "Refine based on feedback"},
            {"title": "Documentation", "description": "Document the solution"},
            {"title": "Deployment", "description": "Deploy to production"},
            {"title": "Monitoring & Support", "description": "Monitor and provide ongoing support"},
            {"title": "Review & Closure", "description": "Final review and project closure"},
        ]

        selected = task_suggestions[:count]
        tasks = []

        for i, suggestion in enumerate(selected):
            tasks.append({
                "title": suggestion["title"],
                "description": suggestion["description"],
                "estimated_duration_hours": 2.0 + (i * 0.5),
                "priority": 5 - (i // 3),  # Earlier tasks higher priority
                "dependencies": [i - 1] if i > 0 else []
            })

        return tasks

    def _generate_milestones(self, count: int, num_tasks: int) -> List[Dict[str, Any]]:
        """Generate milestone suggestions"""
        milestones = []

        tasks_per_milestone = num_tasks / count

        for i in range(count):
            date = datetime.now() + timedelta(days=(i + 1) * 7)
            milestone_num = i + 1

            milestones.append({
                "title": f"Milestone {milestone_num}",
                "description": f"Phase {milestone_num} completion",
                "target_date": date.isoformat(),
                "task_count": int(tasks_per_milestone)
            })

        return milestones


# ============================================================================
# Progress Tracker
# ============================================================================

class ProgressTracker:
    """Tracks progress of goals and tasks"""

    def __init__(self):
        """Initialize progress tracker"""
        self.progress_history: List[Tuple[str, float, str]] = []  # (goal_id, percentage, timestamp)

    def calculate_goal_progress(self, goal: Goal) -> float:
        """Calculate completion percentage of goal"""
        if not goal.tasks:
            return 0.0

        completed = sum(1 for t in goal.tasks.values() if t.status == TaskStatus.COMPLETED)
        total = len(goal.tasks)

        return (completed / total * 100) if total > 0 else 0.0

    def calculate_milestone_progress(self, goal: Goal, milestone: Milestone) -> float:
        """Calculate completion percentage of milestone"""
        if not milestone.tasks:
            return 0.0

        completed = sum(
            1 for task_id in milestone.tasks
            if task_id in goal.tasks and goal.tasks[task_id].status == TaskStatus.COMPLETED
        )
        total = len(milestone.tasks)

        return (completed / total * 100) if total > 0 else 0.0

    def record_progress(self, goal_id: str, percentage: float) -> None:
        """Record progress snapshot"""
        self.progress_history.append((goal_id, percentage, datetime.now().isoformat()))

    def get_progress_history(self, goal_id: str) -> List[Tuple[float, str]]:
        """Get progress history for a goal"""
        return [(p, ts) for gid, p, ts in self.progress_history if gid == goal_id]


# ============================================================================
# Main Goal Manager
# ============================================================================

class TerminatorGoalManager:
    """
    Main goal management system that handles complex multi-step projects,
    tracks progress, and adapts plans as needed.
    """

    _instance: Optional['TerminatorGoalManager'] = None
    _lock = threading.Lock()

    def __init__(self):
        """Initialize goal manager"""
        self.goals: Dict[str, Goal] = {}
        self.decomposer = GoalDecomposer()
        self.progress_tracker = ProgressTracker()
        self.dependency_graphs: Dict[str, DependencyGraph] = {}

        self.storage_path = "/Users/reeazmahmud/Desktop/Terminator/goals/data"
        os.makedirs(self.storage_path, exist_ok=True)

    @classmethod
    def get_instance(cls) -> 'TerminatorGoalManager':
        """Get singleton instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def create_goal(
        self,
        title: str,
        description: str,
        target_completion_date: Optional[str] = None,
        priority: int = 3
    ) -> Goal:
        """Create a new goal"""
        goal_id = str(uuid4())[:8]

        goal = Goal(
            goal_id=goal_id,
            title=title,
            description=description,
            target_completion_date=target_completion_date,
            priority=priority
        )

        self.goals[goal_id] = goal
        self.dependency_graphs[goal_id] = DependencyGraph()

        return goal

    def decompose_goal(self, goal_id: str, complexity: float = 0.5) -> Goal:
        """Decompose a goal into tasks"""
        if goal_id not in self.goals:
            return None

        goal = self.goals[goal_id]
        decomposition = self.decomposer.decompose_goal(
            goal.title,
            goal.description,
            complexity
        )

        # Create tasks
        for task_data in decomposition["tasks"]:
            task_id = str(uuid4())[:8]
            task = Task(
                task_id=task_id,
                title=task_data["title"],
                description=task_data["description"],
                estimated_duration_hours=task_data["estimated_duration_hours"],
                priority=task_data["priority"]
            )

            goal.tasks[task_id] = task

            # Add dependencies
            for dep_task_idx in task_data.get("dependencies", []):
                if dep_task_idx >= 0:
                    task_list = list(goal.tasks.keys())
                    if dep_task_idx < len(task_list) - 1:
                        dep_task_id = task_list[dep_task_idx]
                        self.dependency_graphs[goal_id].add_dependency(task_id, dep_task_id)

        # Create milestones
        for milestone_data in decomposition["milestones"]:
            milestone = Milestone(
                milestone_id=str(uuid4())[:8],
                title=milestone_data["title"],
                description=milestone_data["description"],
                target_date=milestone_data["target_date"]
            )
            goal.milestones.append(milestone)

        goal.status = GoalStatus.IN_PROGRESS
        goal.started_at = datetime.now().isoformat()

        return goal

    def update_task_status(self, goal_id: str, task_id: str, status: TaskStatus) -> None:
        """Update task status"""
        if goal_id not in self.goals or task_id not in self.goals[goal_id].tasks:
            return

        task = self.goals[goal_id].tasks[task_id]
        task.status = status

        if status == TaskStatus.IN_PROGRESS and task.started_at is None:
            task.started_at = datetime.now().isoformat()
        elif status == TaskStatus.COMPLETED and task.completed_at is None:
            task.completed_at = datetime.now().isoformat()

        # Update goal progress
        progress = self.progress_tracker.calculate_goal_progress(self.goals[goal_id])
        self.progress_tracker.record_progress(goal_id, progress)

        # Check if goal is complete
        if progress >= 100:
            self.goals[goal_id].status = GoalStatus.COMPLETED
            self.goals[goal_id].completed_at = datetime.now().isoformat()

    def add_obstacle(
        self,
        goal_id: str,
        obstacle_type: ObstacleType,
        description: str,
        affected_tasks: List[str] = None
    ) -> Obstacle:
        """Add an obstacle"""
        if goal_id not in self.goals:
            return None

        obstacle = Obstacle(
            obstacle_id=str(uuid4())[:8],
            obstacle_type=obstacle_type,
            description=description,
            affected_tasks=affected_tasks or []
        )

        self.goals[goal_id].obstacles.append(obstacle)

        # Mark affected tasks as blocked
        for task_id in obstacle.affected_tasks:
            if task_id in self.goals[goal_id].tasks:
                self.goals[goal_id].tasks[task_id].status = TaskStatus.BLOCKED

        # Mark goal as blocked if critical
        if obstacle.severity >= 4:
            self.goals[goal_id].status = GoalStatus.BLOCKED

        return obstacle

    def resolve_obstacle(self, goal_id: str, obstacle_id: str) -> None:
        """Mark obstacle as resolved"""
        if goal_id not in self.goals:
            return

        goal = self.goals[goal_id]

        for obstacle in goal.obstacles:
            if obstacle.obstacle_id == obstacle_id:
                obstacle.resolved = True

                # Unblock affected tasks
                for task_id in obstacle.affected_tasks:
                    if task_id in goal.tasks:
                        goal.tasks[task_id].status = TaskStatus.NOT_STARTED

                # Unblock goal if all obstacles resolved
                if all(o.resolved for o in goal.obstacles):
                    goal.status = GoalStatus.IN_PROGRESS

                break

    def get_goal_summary(self, goal_id: str) -> Dict[str, Any]:
        """Get summary of a goal"""
        if goal_id not in self.goals:
            return None

        goal = self.goals[goal_id]
        progress = self.progress_tracker.calculate_goal_progress(goal)

        return {
            "goal_id": goal_id,
            "title": goal.title,
            "status": goal.status.value,
            "progress": progress,
            "total_tasks": len(goal.tasks),
            "completed_tasks": sum(1 for t in goal.tasks.values() if t.status == TaskStatus.COMPLETED),
            "blocked_tasks": sum(1 for t in goal.tasks.values() if t.status == TaskStatus.BLOCKED),
            "estimated_hours": sum(t.estimated_duration_hours for t in goal.tasks.values()),
            "completed_hours": sum(t.actual_duration_hours for t in goal.tasks.values()),
            "obstacles": len([o for o in goal.obstacles if not o.resolved]),
            "target_completion": goal.target_completion_date
        }

    def get_next_tasks(self, goal_id: str, count: int = 5) -> List[Task]:
        """Get next tasks to work on"""
        if goal_id not in self.goals:
            return []

        goal = self.goals[goal_id]
        dependency_graph = self.dependency_graphs[goal_id]

        # Find tasks that can be started
        completed = {t_id for t_id, t in goal.tasks.items() if t.status == TaskStatus.COMPLETED}

        available_tasks = [
            task for task_id, task in goal.tasks.items()
            if task.status == TaskStatus.NOT_STARTED and
               dependency_graph.can_start_task(task_id, completed)
        ]

        # Sort by priority
        available_tasks.sort(key=lambda t: (t.priority, -t.estimated_duration_hours), reverse=True)

        return available_tasks[:count]


# ============================================================================
# Module-level access functions
# ============================================================================

def get_goal_manager() -> TerminatorGoalManager:
    """Get the goal manager instance"""
    return TerminatorGoalManager.get_instance()


if __name__ == "__main__":
    # Test the goal manager
    manager = get_goal_manager()

    # Create a goal
    goal = manager.create_goal(
        title="Build AI Dashboard",
        description="Create a comprehensive dashboard to visualize AI system metrics",
        priority=4
    )

    print(f"\n✅ Created goal: {goal.title} ({goal.goal_id})")

    # Decompose goal
    goal = manager.decompose_goal(goal.goal_id, complexity=0.7)

    # Get summary
    print("\n=== Goal Summary ===")
    summary = manager.get_goal_summary(goal.goal_id)
    for key, value in summary.items():
        print(f"  {key}: {value}")

    # Get next tasks
    print("\n=== Next Tasks ===")
    next_tasks = manager.get_next_tasks(goal.goal_id, count=3)
    for task in next_tasks:
        print(f"  - {task.title} ({task.estimated_duration_hours}h, Priority: {task.priority})")

    # Complete a task
    if goal.tasks:
        first_task_id = list(goal.tasks.keys())[0]
        manager.update_task_status(goal.goal_id, first_task_id, TaskStatus.COMPLETED)
        print(f"\n✅ Completed: {goal.tasks[first_task_id].title}")

        # Get updated summary
        summary = manager.get_goal_summary(goal.goal_id)
        print(f"Progress: {summary['progress']:.0f}%")
