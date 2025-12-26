# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Agent Communication Bus - Inter-Agent Message System
===========================================================

Enables multiple specialized agents to communicate, coordinate work,
share data, and collaborate on complex problems.

Optimized for:
- Asynchronous operation (asyncio)
- High-concurrency "Push" messaging (Pub/Sub)
- Strict typing and validation
- Hybrid Sync/Async compatibility for legacy agents

Features:
- Asynchronous message passing
- Per-agent priority queues (No "thundering herd")
- Event system for state changes
- Shared memory (Context Streams)
- Message history and audit trail
- Agent status dashboard

Created: December 11, 2025
Refactored: December 14, 2025 (AsyncIO Optimization with Hybrid Bridge)
"""

import json
import os
import asyncio
import time
import threading
import zlib
import base64
from datetime import datetime
from typing import Optional, Dict, List, Any, Callable, Set, Union, Awaitable
from dataclasses import dataclass, asdict, field
from enum import Enum, IntEnum
from collections import defaultdict

# ============================================================================
# Data Structures
# ============================================================================

class MessageType(str, Enum):
    """Type of message"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"
    STATUS = "status"


class MessagePriority(IntEnum):
    """Message priority level (Lower value = Higher priority)"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass(frozen=True, order=True)
class Message:
    """
    A message between agents.
    Immutable and orderable for PriorityQueue.
    Supports transparent compression for large payloads.
    """
    priority_value: int = field(init=False)
    timestamp_val: float = field(init=False)
    
    message_id: str = field(compare=False)
    sender_agent: str = field(compare=False)
    recipient_agent: Optional[str] = field(compare=False)
    subject: str = field(compare=False)
    
    # Internal content storage (can be Dict or compressed bytes)
    _content: Any = field(compare=False, default_factory=dict)
    is_compressed: bool = field(compare=False, default=False)
    
    message_type: MessageType = field(compare=False, default=MessageType.REQUEST)
    priority: MessagePriority = field(compare=False, default=MessagePriority.NORMAL)
    timestamp: str = field(compare=False, default_factory=lambda: datetime.now().isoformat())
    requires_response: bool = field(compare=False, default=False)
    response_timeout_seconds: int = field(compare=False, default=30)
    
    def __post_init__(self):
        object.__setattr__(self, 'priority_value', self.priority.value)
        object.__setattr__(self, 'timestamp_val', time.time())
        if not self.sender_agent:
            raise ValueError("sender_agent cannot be empty")
        if not self.message_id:
            raise ValueError("message_id cannot be empty")

    @property
    def content(self) -> Dict[str, Any]:
        """Lazy decompression of content"""
        if self.is_compressed:
            try:
                # Expecting _content to be base64 encoded string or bytes
                if isinstance(self._content, str):
                    compressed_data = base64.b64decode(self._content)
                else:
                    compressed_data = self._content
                
                json_str = zlib.decompress(compressed_data).decode('utf-8')
                return json.loads(json_str)
            except Exception as e:
                print(f"❌ Decompression error for msg {self.message_id}: {e}")
                return {}
        return self._content

@dataclass
class AgentStatus:
    """Status of an agent"""
    agent_name: str
    status: str  # "idle", "working", "error", "offline"
    last_activity: str
    messages_processed: int = 0
    errors_encountered: int = 0
    utilization_percent: float = 0.0


# ============================================================================
# Message Bus
# ============================================================================

class AgentCommunicationBus:
    """
    Central message bus for agent communication.
    AsyncIO implementation with per-agent queues.
    Includes a background event loop for synchronous compatibility.
    """

    _instance: Optional['AgentCommunicationBus'] = None
    
    def __init__(self):
        """Initialize communication bus"""
        self.queues: Dict[str, asyncio.PriorityQueue] = {}
        self.message_history: List[Message] = []
        self.agent_registry: Dict[str, AgentStatus] = {}
        
        self.shared_memory: Dict[str, Any] = {}
        self.event_handlers: Dict[str, List[Callable[[Message], Awaitable[None]]]] = defaultdict(list)
        self.agents: Dict[str, Any] = {}

        self.storage_path = "/Users/reeazmahmud/Desktop/Terminator/communication/data"
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Hybrid Bridge: Background Loop
        self._loop = asyncio.new_event_loop()
        self._loop_thread = threading.Thread(target=self._run_loop, daemon=True, name="BusLoop")
        self._loop_thread.start()

        # Monitoring
        self.monitoring = False

    @classmethod
    def get_instance(cls) -> 'AgentCommunicationBus':
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _run_loop(self):
        """Run the background asyncio loop"""
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    # --- Async Implementation (The Core) ---

    async def register_agent_async(self, agent_name: str, agent_instance: Any = None) -> None:
        """Async registration"""
        if agent_name not in self.queues:
            self.queues[agent_name] = asyncio.PriorityQueue()
        
        self.agents[agent_name] = agent_instance
        self.agent_registry[agent_name] = AgentStatus(
            agent_name=agent_name,
            status="idle",
            last_activity=datetime.now().isoformat()
        )
        print(f"✅ Registered agent: {agent_name}")

    async def send_message_async(
        self,
        sender_agent: str,
        recipient_agent: Optional[str],
        subject: str,
        content: Dict[str, Any],
        message_type: MessageType = MessageType.REQUEST,
        priority: MessagePriority = MessagePriority.NORMAL,
        requires_response: bool = False
    ) -> str:
        """Async send message with auto-compression"""
        message_id = f"msg_{int(time.time()*1000)}_{sender_agent}"

        # Compression Logic
        try:
            json_content = json.dumps(content)
            content_size = len(json_content)
        except (TypeError, ValueError):
            # Fallback if content isn't JSON serializable (rare but safe)
            json_content = str(content)
            content_size = len(json_content)

        is_compressed = False
        final_content = content

        if content_size > 1024: # Compress if > 1KB
            try:
                compressed_data = zlib.compress(json_content.encode('utf-8'))
                # Store as base64 string to keep it JSON serializable if needed later
                final_content = base64.b64encode(compressed_data).decode('ascii')
                is_compressed = True
                # print(f"📦 Compressed message {message_id}: {content_size} -> {len(final_content)} bytes")
            except Exception as e:
                print(f"⚠️ Compression failed: {e}")
                is_compressed = False

        message = Message(
            message_id=message_id,
            sender_agent=sender_agent,
            recipient_agent=recipient_agent,
            message_type=message_type,
            priority=priority,
            subject=subject,
            _content=final_content,
            is_compressed=is_compressed,
            requires_response=requires_response
        )

        self.message_history.append(message)
        if len(self.message_history) > 1000:
            self.message_history = self.message_history[-1000:]

        if sender_agent in self.agent_registry:
            self.agent_registry[sender_agent].messages_processed += 1
            self.agent_registry[sender_agent].last_activity = datetime.now().isoformat()

        if recipient_agent:
            if recipient_agent in self.queues:
                await self.queues[recipient_agent].put(message)
            else:
                # Buffer or drop? For now create queue on fly to support legacy behavior
                if recipient_agent not in self.queues:
                    self.queues[recipient_agent] = asyncio.PriorityQueue()
                await self.queues[recipient_agent].put(message)
        else:
            for agent_name, queue in self.queues.items():
                if agent_name != sender_agent:
                    await queue.put(message)

        event_key = f"{recipient_agent or 'broadcast'}:incoming_message"
        asyncio.create_task(self._trigger_event(event_key, message))

        return message_id

    async def get_message_async(self, agent_name: str, timeout: Optional[float] = None) -> Optional[Message]:
        """Async get message"""
        if agent_name not in self.queues:
            await self.register_agent_async(agent_name)
            
        queue = self.queues[agent_name]
        try:
            if timeout:
                return await asyncio.wait_for(queue.get(), timeout)
            else:
                return await queue.get()
        except asyncio.TimeoutError:
            return None

    async def _trigger_event(self, event_key: str, message: Message) -> None:
        handlers = self.event_handlers.get(event_key, [])
        if handlers:
            await asyncio.gather(*[h(message) for h in handlers], return_exceptions=True)

    # --- Synchronous Bridge (Compatibility Layer) ---

    def register_agent(self, agent_name: str, agent_instance: Any = None) -> None:
        """Synchronous wrapper for register_agent"""
        future = asyncio.run_coroutine_threadsafe(
            self.register_agent_async(agent_name, agent_instance), self._loop
        )
        return future.result()

    def send_message(
        self,
        sender_agent: str,
        recipient_agent: Optional[str],
        message_type: MessageType = MessageType.REQUEST,
        subject: str = "",
        content: Dict[str, Any] = None,
        priority: MessagePriority = MessagePriority.NORMAL,
        requires_response: bool = False
    ) -> str:
        """Synchronous wrapper for send_message. Params matched to old signature for compat."""
        if content is None: content = {}
        
        future = asyncio.run_coroutine_threadsafe(
            self.send_message_async(
                sender_agent=sender_agent,
                recipient_agent=recipient_agent,
                subject=subject,
                content=content,
                message_type=message_type,
                priority=priority,
                requires_response=requires_response
            ),
            self._loop
        )
        return future.result()

    def get_message(self, agent_name: str, timeout: int = 1) -> Optional[Message]:
        """Synchronous wrapper for get_message"""
        try:
            future = asyncio.run_coroutine_threadsafe(
                self.get_message_async(agent_name, float(timeout)), self._loop
            )
            return future.result()
        except Exception:
            return None

    def broadcast_message(
        self,
        sender_agent: str,
        message_type: MessageType,
        subject: str,
        content: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> str:
        """Synchronous wrapper for broadcast"""
        future = asyncio.run_coroutine_threadsafe(
            self.send_message_async(
                sender_agent=sender_agent,
                recipient_agent=None,
                subject=subject,
                content=content,
                message_type=message_type,
                priority=priority
            ),
            self._loop
        )
        return future.result()

    def update_agent_status(self, agent_name: str, status: str, utilization_percent: float = 0.0) -> None:
        """Synchronous update status"""
        if agent_name in self.agent_registry:
            self.agent_registry[agent_name].status = status
            self.agent_registry[agent_name].utilization_percent = utilization_percent
            self.agent_registry[agent_name].last_activity = datetime.now().isoformat()

    def set_shared_memory(self, key: str, value: Any) -> None:
        """Sync wrapper for shared memory"""
        self.shared_memory[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "modified_by": "system"
        }

    def get_shared_memory(self, key: str) -> Optional[Any]:
        if key in self.shared_memory:
            return self.shared_memory[key].get("value")
        return None

    def get_bus_status(self) -> Dict[str, Any]:
        """Get status (Sync)"""
        return {
            "timestamp": datetime.now().isoformat(),
            "agents_online": sum(1 for s in self.agent_registry.values() if s.status != "offline"),
            "total_agents": len(self.agent_registry),
            "queues": {name: q.qsize() for name, q in self.queues.items()},
            "message_history_size": len(self.message_history),
            "shared_memory_entries": len(self.shared_memory),
            "agent_statuses": {
                name: {
                    "status": s.status,
                    "messages": s.messages_processed,
                    "errors": s.errors_encountered,
                    "utilization": f"{s.utilization_percent:.0f}%"
                }
                for name, s in self.agent_registry.items()
            }
        }
        
    def get_all_agent_statuses(self) -> Dict[str, AgentStatus]:
        return self.agent_registry.copy()

    # Legacy Monitoring methods (No-op or basic logging to prevent crash)
    def start_monitoring(self) -> None:
        self.monitoring = True
        print("✅ Agent Communication Bus monitoring enabled")

    def stop_monitoring(self) -> None:
        self.monitoring = False
        print("⛔ Agent Communication Bus monitoring disabled")


# ============================================================================
# Module-level access functions
# ============================================================================

def get_communication_bus() -> AgentCommunicationBus:
    """Get the communication bus instance"""
    return AgentCommunicationBus.get_instance()

# Module-level helpers (mapped to sync methods)
def send_message(
    sender_agent: str,
    recipient_agent: str,
    subject: str,
    content: Dict[str, Any],
    priority: MessagePriority = MessagePriority.NORMAL
) -> str:
    bus = get_communication_bus()
    return bus.send_message(
        sender_agent=sender_agent,
        recipient_agent=recipient_agent,
        message_type=MessageType.REQUEST,
        subject=subject,
        content=content,
        priority=priority
    )

if __name__ == "__main__":
    # Test Hybrid Bus
    bus = get_communication_bus()
    
    print("\n=== Hybrid Agent Communication Bus Test ===\n")
    
    # Sync Registration
    bus.register_agent("agent_sync")
    
    # Async Registration (via sync wrapper)
    bus.register_agent("agent_qa")
    
    print("✅ Agents registered via sync wrapper")

    # Sync Send
    msg_id = bus.send_message(
        sender_agent="agent_sync",
        recipient_agent="agent_qa",
        message_type=MessageType.REQUEST,
        subject="Sync Message",
        content={"data": 123},
        priority=MessagePriority.HIGH
    )
    print(f"✅ Sent sync message: {msg_id}")
    
    # Sync Get
    print("waiting for message (sync)...")
    msg = bus.get_message("agent_qa", timeout=2)
    
    if msg:
        print(f"📨 Received: {msg.subject} from {msg.sender_agent}")
    else:
        print("❌ Timed out")
        
    status = bus.get_bus_status()
    print(json.dumps(status, indent=2, default=str))