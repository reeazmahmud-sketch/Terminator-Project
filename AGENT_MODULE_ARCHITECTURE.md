# Terminator Agent Module Architecture

## Overview
This document defines the standardized architecture for integrating agents as dynamic, loadable modules within the Terminator ecosystem. The goal is to move from ad-hoc agent scripts to a unified plugin system.

## 1. Agent API Definition
All agents must inherit from the `BaseAgent` class and implement the required interface.

### The `BaseAgent` Interface
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from core.terminator_agent_communication_bus import Message, MessageType

class BaseAgent(ABC):
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.status = "initializing"
        self.capabilities: List[str] = []

    async def start(self):
        """Connect to bus and begin listening."""
        self.status = "idle"
        # ... logic to subscribe to bus ...

    async def stop(self):
        """Cleanup and disconnect."""
        self.status = "offline"

    @abstractmethod
    async def process_message(self, message: Message) -> Dict[str, Any]:
        """Core logic handler. Must return a dict (response) or None."""
        pass
        
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "capabilities": self.capabilities,
            "status": self.status
        }
```

## 2. Module Loading Mechanism (`AgentLoader`)
We will implement a `TerminatorAgentLoader` class that dynamically discovers and loads agents.

- **Discovery Path:** `core/agents/*.py` (Proposed new directory) or `core/terminator_*_agent.py`
- **Loading Logic:**
    1. Scan directory for `.py` files.
    2. Import module using `importlib`.
    3. Look for a class inheriting from `BaseAgent` OR a `create_agent()` factory.
    4. Instantiate and register with the Bus.

## 3. Inter-Agent Communication
We leverage the existing `AgentCommunicationBus` but standardize the **Message Schema**.

### Standard Message Protocol
All inter-agent messages must adhere to this structure in the `content` field:

```json
{
  "action": "perform_task",  // or "report_status", "query_data"
  "payload": { ... },        // Task-specific data
  "context_id": "uuid",      // Trace ID for multi-step reasoning
  "response_required": true
}
```

## 4. Resource Management
To prevent rogue agents from consuming system resources:

- **Execution Timeout:** `BaseAgent` will wrap `process_message` in a strict `asyncio.wait_for`.
- **Concurrency Limit:** Each agent has a `semaphore` limiting parallel tasks (default: 1).

## 5. Error Handling Strategy
- **Isolation:** Agents run in the main process loop (async) but are logically isolated. One crash shouldn't kill the bus.
- **Circuit Breaker:** 
    - If an agent raises Exceptions > 3 times in 1 minute -> Status set to `ERROR`.
    - `AgentManager` receives `ERROR` notification and can attempt a restart.

## 6. Measurable Outcome: Agent Discoverability
A new system command `/agents` (CLI) and API endpoint will list all loaded modules.

### Discovery Output Example
```text
Agent Registry:
------------------------------------------------
| Name            | Version | Status | Capabilities
|-----------------|---------|--------|----------
| qa_agent        | 1.2.0   | IDLE   | [search, summarize]
| coder_agent     | 0.9.beta| BUSY   | [write_code, debug]
| translator      | 1.0.0   | ERROR  | [en_to_bn]
```
