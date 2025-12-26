# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Resource Manager Agent - Resource Allocation and Optimization
==================================================================

Manages system resources, allocates them to tasks, optimizes usage,
and handles resource conflicts.

Features:
- Resource tracking and monitoring
- Allocation optimization
- Load balancing
- Constraint satisfaction
- Priority-based allocation
- Resource pooling
- Performance tracking

Created: December 11, 2025
Part of: TERMINATOR Enhancement Roadmap - Tier 5 (Collaboration)
"""

import threading
import time
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
from uuid import uuid4

from core.terminator_agent_communication_bus import get_communication_bus, MessageType, MessagePriority


# ============================================================================
# Data Structures
# ============================================================================

class ResourceType(Enum):
    """Type of resource"""
    MODEL = "model"
    TOOL = "tool"
    COMPUTE = "compute"
    MEMORY = "memory"
    NETWORK = "network"


@dataclass
class Resource:
    """A system resource"""
    resource_id: str
    resource_type: ResourceType
    name: str
    total_capacity: float
    available_capacity: float
    utilization_percent: float = 0.0
    allocated_tasks: List[str] = field(default_factory=list)


@dataclass
class AllocationRequest:
    """Request to allocate resources"""
    request_id: str
    task_id: str
    requested_resources: Dict[str, float]  # {resource_id: amount}
    priority: int = 3
    required: bool = True  # vs nice-to-have


@dataclass
class Allocation:
    """An allocation of resources"""
    allocation_id: str
    task_id: str
    resources: Dict[str, float]  # {resource_id: amount}
    allocated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    released_at: Optional[str] = None


# ============================================================================
# Resource Manager Agent
# ============================================================================

class TerminatorResourceManagerAgent:
    """
    Main resource manager agent that allocates and optimizes
    system resources across tasks.
    """

    _instance: Optional['TerminatorResourceManagerAgent'] = None
    _lock = threading.Lock()

    def __init__(self):
        """Initialize resource manager agent"""
        self.bus = get_communication_bus()
        self.agent_name = "ResourceManager"
        self.resources: Dict[str, Resource] = {}
        self.allocations: Dict[str, Allocation] = {}
        self.pending_requests: List[AllocationRequest] = []
        self.managing = False
        self.manage_thread: Optional[threading.Thread] = None

        self._initialize_resources()
        self.bus.register_agent(self.agent_name, self)

    def _initialize_resources(self) -> None:
        """Initialize default resources"""
        # Models
        self.register_resource("claude-3-haiku", ResourceType.MODEL, "Claude 3 Haiku", capacity=3.0)
        self.register_resource("claude-3-sonnet", ResourceType.MODEL, "Claude 3 Sonnet", capacity=2.0)
        self.register_resource("claude-3-opus", ResourceType.MODEL, "Claude 3 Opus", capacity=1.0)

        # Tools
        self.register_resource("web_search", ResourceType.TOOL, "Web Search Tool", capacity=5.0)
        self.register_resource("file_search", ResourceType.TOOL, "File Search Tool", capacity=10.0)

        # Compute
        self.register_resource("cpu", ResourceType.COMPUTE, "CPU", capacity=100.0)
        self.register_resource("memory", ResourceType.MEMORY, "Memory (GB)", capacity=16.0)

    @classmethod
    def get_instance(cls) -> 'TerminatorResourceManagerAgent':
        """Get singleton instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def register_resource(
        self,
        resource_id: str,
        resource_type: ResourceType,
        name: str,
        capacity: float
    ) -> None:
        """Register a new resource"""
        self.resources[resource_id] = Resource(
            resource_id=resource_id,
            resource_type=resource_type,
            name=name,
            total_capacity=capacity,
            available_capacity=capacity
        )

    def start_managing(self) -> None:
        """Start the resource management loop"""
        if self.managing:
            print(f"{self.agent_name}: Already managing")
            return

        self.managing = True
        self.manage_thread = threading.Thread(target=self._management_loop, daemon=True)
        self.manage_thread.start()
        print(f"✅ {self.agent_name} started")

    def stop_managing(self) -> None:
        """Stop the resource management loop"""
        self.managing = False
        if self.manage_thread:
            self.manage_thread.join(timeout=5)
        print(f"⛔ {self.agent_name} stopped")

    def _management_loop(self) -> None:
        """Main resource management loop"""
        while self.managing:
            try:
                # Process pending requests
                self._process_allocation_requests()

                # Check for resource optimization opportunities
                self._optimize_allocation()

                # Listen for messages
                message = self.bus.get_message(self.agent_name, timeout=1)
                if message:
                    self._handle_message(message)

                self.bus.update_agent_status(self.agent_name, "idle", 0.3)
                time.sleep(1)
            except Exception as e:
                print(f"Error in {self.agent_name} management loop: {e}")
                time.sleep(1)

    def request_allocation(
        self,
        task_id: str,
        requested_resources: Dict[str, float],
        priority: int = 3,
        required: bool = True
    ) -> str:
        """Request resource allocation for a task"""
        request_id = str(uuid4())[:8]

        request = AllocationRequest(
            request_id=request_id,
            task_id=task_id,
            requested_resources=requested_resources,
            priority=priority,
            required=required
        )

        self.pending_requests.append(request)

        # Try immediate allocation
        allocation = self._try_allocate(request)

        return allocation.allocation_id if allocation else request_id

    def _try_allocate(self, request: AllocationRequest) -> Optional[Allocation]:
        """Try to allocate requested resources"""
        allocation_dict = {}

        # Check if all resources available
        for resource_id, amount in request.requested_resources.items():
            if resource_id not in self.resources:
                if request.required:
                    return None
                else:
                    continue

            resource = self.resources[resource_id]

            if resource.available_capacity >= amount:
                allocation_dict[resource_id] = amount
            elif request.required:
                return None

        # Perform allocation
        if allocation_dict:
            allocation_id = str(uuid4())[:8]
            allocation = Allocation(
                allocation_id=allocation_id,
                task_id=request.task_id,
                resources=allocation_dict
            )

            # Update resources
            for resource_id, amount in allocation_dict.items():
                self.resources[resource_id].available_capacity -= amount
                self.resources[resource_id].allocated_tasks.append(request.task_id)
                self._update_utilization(resource_id)

            self.allocations[allocation_id] = allocation

            # Notify bus
            self.bus.send_message(
                sender_agent=self.agent_name,
                recipient_agent=None,
                message_type=MessageType.STATUS,
                subject="Resources Allocated",
                content={
                    "allocation_id": allocation_id,
                    "task_id": request.task_id,
                    "resources": allocation_dict
                },
                priority=MessagePriority.NORMAL
            )

            return allocation

        return None

    def _process_allocation_requests(self) -> None:
        """Process pending allocation requests"""
        if not self.pending_requests:
            return

        # Sort by priority
        self.pending_requests.sort(key=lambda r: r.priority, reverse=True)

        remaining = []

        for request in self.pending_requests:
            allocation = self._try_allocate(request)
            if not allocation and request.required:
                remaining.append(request)

        self.pending_requests = remaining

    def _optimize_allocation(self) -> None:
        """Optimize resource allocation"""
        # Could rebalance allocations, consolidate, etc.
        for resource_id, resource in self.resources.items():
            self._update_utilization(resource_id)

    def _update_utilization(self, resource_id: str) -> None:
        """Update utilization percentage for a resource"""
        if resource_id not in self.resources:
            return

        resource = self.resources[resource_id]
        used = resource.total_capacity - resource.available_capacity
        resource.utilization_percent = (used / resource.total_capacity * 100) if resource.total_capacity > 0 else 0

    def _handle_message(self, message: Any) -> None:
        """Handle incoming message"""
        if message.subject == "Resource Request":
            task_id = message.content.get("task_id")
            resources = message.content.get("resources", {})
            priority = message.content.get("priority", 3)

            self.request_allocation(task_id, resources, priority)

    def release_allocation(self, allocation_id: str) -> None:
        """Release an allocation"""
        if allocation_id not in self.allocations:
            return

        allocation = self.allocations[allocation_id]
        allocation.released_at = datetime.now().isoformat()

        # Free resources
        for resource_id, amount in allocation.resources.items():
            if resource_id in self.resources:
                self.resources[resource_id].available_capacity += amount
                if allocation.task_id in self.resources[resource_id].allocated_tasks:
                    self.resources[resource_id].allocated_tasks.remove(allocation.task_id)
                self._update_utilization(resource_id)

    def get_resource_status(self, resource_id: str = None) -> Dict[str, Any]:
        """Get resource status"""
        if resource_id:
            if resource_id not in self.resources:
                return {}

            resource = self.resources[resource_id]
            return {
                "resource_id": resource_id,
                "name": resource.name,
                "type": resource.resource_type.value,
                "total": resource.total_capacity,
                "available": resource.available_capacity,
                "utilization": resource.utilization_percent,
                "allocated_tasks": len(resource.allocated_tasks)
            }
        else:
            # Return all resources
            return {
                resource_id: {
                    "name": resource.name,
                    "type": resource.resource_type.value,
                    "available": resource.available_capacity,
                    "utilization": resource.utilization_percent
                }
                for resource_id, resource in self.resources.items()
            }

    def get_allocation_status(self, allocation_id: str) -> Optional[Dict[str, Any]]:
        """Get allocation status"""
        if allocation_id not in self.allocations:
            return None

        allocation = self.allocations[allocation_id]
        return {
            "allocation_id": allocation_id,
            "task_id": allocation.task_id,
            "resources": allocation.resources,
            "allocated_at": allocation.allocated_at,
            "released_at": allocation.released_at
        }

    def get_all_allocations(self) -> Dict[str, Dict[str, Any]]:
        """Get all allocations"""
        return {
            alloc_id: {
                "task_id": alloc.task_id,
                "resources": alloc.resources
            }
            for alloc_id, alloc in self.allocations.items()
            if alloc.released_at is None
        }


# ============================================================================
# Module-level access functions
# ============================================================================

def get_resource_manager() -> TerminatorResourceManagerAgent:
    """Get the resource manager agent instance"""
    return TerminatorResourceManagerAgent.get_instance()


if __name__ == "__main__":
    # Test the resource manager agent
    manager = get_resource_manager()
    manager.start_managing()

    print("\n=== Resource Manager Agent Test ===\n")

    # Check initial resource status
    print("=== Resource Status ===")
    status = manager.get_resource_status()
    for resource_id, info in status.items():
        print(f"  {resource_id}: {info['utilization']:.0f}% utilization")

    # Request allocation
    print("\n=== Allocating Resources ===")
    alloc_id = manager.request_allocation(
        task_id="task_001",
        requested_resources={
            "claude-3-sonnet": 1.0,
            "web_search": 2.0
        },
        priority=4
    )

    print(f"✅ Allocation ID: {alloc_id}")

    time.sleep(1)

    # Check resource status after allocation
    print("\n=== Updated Resource Status ===")
    status = manager.get_resource_status()
    for resource_id, info in status.items():
        print(f"  {resource_id}: {info['utilization']:.0f}% utilization")

    manager.stop_managing()
