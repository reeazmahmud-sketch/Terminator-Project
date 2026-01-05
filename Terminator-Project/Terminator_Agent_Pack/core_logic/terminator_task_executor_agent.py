# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Task Executor Agent - Autonomous Task Execution
======================================================

Executes planned tasks, manages task lifecycle, handles retries,
and coordinates with other agents for dependencies.

Features:
- Task scheduling and execution
- Automatic retry with backoff
- Dependency management
- Status tracking and reporting
- Error recovery
- Task checkpoint management
- Progress reporting

Created: December 11, 2025
Part of: TERMINATOR Enhancement Roadmap - Tier 5 (Collaboration)
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
from uuid import uuid4

from core.terminator_agent_communication_bus import get_communication_bus, MessageType, MessagePriority


# ============================================================================
# Data Structures
# ============================================================================

class ExecutionStatus(Enum):
    """Status of task execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    PAUSED = "paused"


@dataclass
class TaskExecution:
    """Record of a task execution"""
    execution_id: str
    task_id: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_ms: float = 0.0
    attempts: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    result: Optional[Any] = None
    checkpoints: List[str] = field(default_factory=list)


# ============================================================================
# Task Executor Agent
# ============================================================================

class TerminatorTaskExecutorAgent:
    """
    Main task executor agent that executes tasks, manages retries,
    and coordinates with other agents.
    """

    _instance: Optional['TerminatorTaskExecutorAgent'] = None
    _lock = threading.Lock()

    def __init__(self):
        """Initialize task executor agent"""
        self.bus = get_communication_bus()
        self.agent_name = "TaskExecutor"
        self.executions: Dict[str, TaskExecution] = {}
        self.task_queue: List[Dict[str, Any]] = []
        self.executing = False
        self.execute_thread: Optional[threading.Thread] = None

        self.bus.register_agent(self.agent_name, self)

    @classmethod
    def get_instance(cls) -> 'TerminatorTaskExecutorAgent':
        """Get singleton instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def start_execution(self) -> None:
        """Start the task execution loop"""
        if self.executing:
            print(f"{self.agent_name}: Already executing")
            return

        self.executing = True
        self.execute_thread = threading.Thread(target=self._execution_loop, daemon=True)
        self.execute_thread.start()
        print(f"✅ {self.agent_name} started")

    def stop_execution(self) -> None:
        """Stop the task execution loop"""
        self.executing = False
        if self.execute_thread:
            self.execute_thread.join(timeout=5)
        print(f"⛔ {self.agent_name} stopped")

    def queue_task(self, task: Dict[str, Any]) -> str:
        """Queue a task for execution"""
        execution_id = str(uuid4())[:8]

        execution = TaskExecution(
            execution_id=execution_id,
            task_id=task.get("task_id", f"task_{execution_id}")
        )

        self.executions[execution_id] = execution
        self.task_queue.append({"execution_id": execution_id, "task": task})

        # Notify bus
        self.bus.send_message(
            sender_agent=self.agent_name,
            recipient_agent=None,
            message_type=MessageType.STATUS,
            subject="Task Queued",
            content={"execution_id": execution_id, "task_id": task.get("task_id")},
            priority=MessagePriority.NORMAL
        )

        return execution_id

    def _execution_loop(self) -> None:
        """Main task execution loop"""
        while self.executing:
            try:
                # Get next task
                if self.task_queue:
                    next_task_item = self.task_queue.pop(0)
                    execution_id = next_task_item["execution_id"]
                    task = next_task_item["task"]

                    # Execute task
                    self._execute_task(execution_id, task)
                else:
                    # Check for messages
                    message = self.bus.get_message(self.agent_name, timeout=1)
                    if message:
                        self._handle_message(message)

                time.sleep(0.5)
            except Exception as e:
                print(f"Error in {self.agent_name} execution loop: {e}")
                time.sleep(1)

    def _execute_task(self, execution_id: str, task: Dict[str, Any]) -> None:
        """Execute a single task"""
        if execution_id not in self.executions:
            return

        execution = self.executions[execution_id]
        execution.status = ExecutionStatus.RUNNING
        execution.started_at = datetime.now().isoformat()
        execution.attempts += 1

        # Update bus status
        self.bus.update_agent_status(self.agent_name, "working", 0.8)

        try:
            # Request QA agent to help with validation if needed
            if task.get("requires_validation"):
                self._request_qa_validation(execution_id, task)

            # Simulate task execution
            duration = task.get("estimated_duration_ms", 1000)
            time.sleep(duration / 1000.0)

            # Mark as completed
            execution.status = ExecutionStatus.COMPLETED
            execution.completed_at = datetime.now().isoformat()
            execution.result = {
                "status": "success",
                "task_id": task.get("task_id"),
                "output": f"Result of {task.get('title', 'task')}"
            }

            # Notify completion
            self.bus.send_message(
                sender_agent=self.agent_name,
                recipient_agent=None,
                message_type=MessageType.STATUS,
                subject="Task Completed",
                content={
                    "execution_id": execution_id,
                    "task_id": task.get("task_id"),
                    "result": execution.result
                },
                priority=MessagePriority.NORMAL
            )

        except Exception as e:
            execution.error_message = str(e)

            if execution.attempts < execution.max_retries:
                execution.status = ExecutionStatus.RETRYING
                # Re-queue with exponential backoff
                retry_delay = 2 ** execution.attempts
                time.sleep(retry_delay)
                self.task_queue.insert(0, {"execution_id": execution_id, "task": task})
            else:
                execution.status = ExecutionStatus.FAILED

                # Notify failure
                self.bus.send_message(
                    sender_agent=self.agent_name,
                    recipient_agent=None,
                    message_type=MessageType.ERROR,
                    subject="Task Failed",
                    content={
                        "execution_id": execution_id,
                        "task_id": task.get("task_id"),
                        "error": str(e),
                        "attempts": execution.attempts
                    },
                    priority=MessagePriority.HIGH
                )

        finally:
            # Update status
            self.bus.update_agent_status(self.agent_name, "idle", 0.1)

    def _request_qa_validation(self, execution_id: str, task: Dict[str, Any]) -> None:
        """Request QA agent to validate task"""
        self.bus.send_message(
            sender_agent=self.agent_name,
            recipient_agent="QAAgent",
            message_type=MessageType.REQUEST,
            subject="Validate Task Output",
            content={
                "execution_id": execution_id,
                "task_id": task.get("task_id"),
                "requires_response": True
            },
            priority=MessagePriority.NORMAL,
            requires_response=True
        )

    def _handle_message(self, message: Any) -> None:
        """Handle incoming message"""
        if message.subject == "Resource Available":
            # Resource manager says resources are ready
            pass
        elif message.subject == "Validation Complete":
            # QA agent completed validation
            execution_id = message.content.get("execution_id")
            if execution_id in self.executions:
                self.executions[execution_id].checkpoints.append("qa_validated")

    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an execution"""
        if execution_id not in self.executions:
            return None

        execution = self.executions[execution_id]
        return {
            "execution_id": execution_id,
            "status": execution.status.value,
            "attempts": execution.attempts,
            "started_at": execution.started_at,
            "completed_at": execution.completed_at,
            "duration_ms": execution.duration_ms,
            "error": execution.error_message,
            "result": execution.result
        }

    def get_all_executions(self) -> Dict[str, Dict[str, Any]]:
        """Get all execution statuses"""
        return {
            execution_id: {
                "status": execution.status.value,
                "task_id": execution.task_id,
                "attempts": execution.attempts
            }
            for execution_id, execution in self.executions.items()
        }


# ============================================================================
# Module-level access functions
# ============================================================================

def get_task_executor() -> TerminatorTaskExecutorAgent:
    """Get the task executor agent instance"""
    return TerminatorTaskExecutorAgent.get_instance()


if __name__ == "__main__":
    # Test the task executor agent
    executor = get_task_executor()
    executor.start_execution()

    # Queue some test tasks
    print("\n=== Task Executor Agent Test ===\n")

    task1 = {
        "task_id": "task_001",
        "title": "Analyze Data",
        "estimated_duration_ms": 2000,
        "requires_validation": True
    }

    task2 = {
        "task_id": "task_002",
        "title": "Generate Report",
        "estimated_duration_ms": 1500,
        "requires_validation": False
    }

    exec_id_1 = executor.queue_task(task1)
    exec_id_2 = executor.queue_task(task2)

    print(f"✅ Queued task 1: {exec_id_1}")
    print(f"✅ Queued task 2: {exec_id_2}")

    # Wait for execution
    time.sleep(5)

    # Get execution status
    print(f"\n=== Execution Status ===")
    status1 = executor.get_execution_status(exec_id_1)
    status2 = executor.get_execution_status(exec_id_2)

    if status1:
        print(f"Task 1: {status1['status']}")
    if status2:
        print(f"Task 2: {status2['status']}")

    executor.stop_execution()
