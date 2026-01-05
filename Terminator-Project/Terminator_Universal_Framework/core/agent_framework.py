# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

import asyncio
import importlib
import inspect
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type
from datetime import datetime
import uuid

from core.terminator_agent_communication_bus import AgentCommunicationBus, Message, MessageType, MessagePriority, AgentStatus
from core.terminator_governance_system import GovernanceSystem
from core.terminator_memory_system import MemorySystem

# --- 1. BaseAgent Interface ---
class BaseAgent(ABC):
    """
    Abstract base class for all Terminator agents.
    Provides common functionality for communication, registration, lifecycle management, and memory.
    """
    def __init__(self, name: str, description: str, version: str = "1.0.0", capabilities: Optional[List[str]] = None):
        if not name:
            raise ValueError("Agent name cannot be empty.")
        self.name = name
        self.description = description
        self.version = version
        self.capabilities = capabilities if capabilities is not None else []
        self._bus = AgentCommunicationBus.get_instance()
        self.governance = GovernanceSystem.get_instance()
        self.memory = MemorySystem.get_instance() # Initialize Memory
        self._status_obj = AgentStatus(
            agent_name=self.name,
            status="initialized",
            last_activity=datetime.now().isoformat(),
            messages_processed=0,
            errors_encountered=0,
            utilization_percent=0.0
        )
        self._running_task: Optional[asyncio.Task] = None
        self._message_queue = asyncio.Queue() # Agent-specific internal message queue
        self._is_running = False

    def learn(self, content: str, tags: List[str] = None, scope: str = "agent"):
        """Store knowledge in long-term memory."""
        return self.memory.store(self.name, content, tags, scope)

    def recall(self, query: str, limit: int = 5) -> List[Dict]:
        """Retrieve relevant knowledge from memory."""
        return self.memory.retrieve(self.name, query, limit)

    async def start(self):
        """
        Registers the agent with the bus and starts listening for messages.
        This method should be called by the AgentLoader.
        """
        if self._is_running:
            print(f"Agent {self.name} is already running.")
            return

        await self._bus.register_agent_async(self.name, self)
        self._status_obj.status = "idle"
        self._bus.update_agent_status(self.name, "idle")
        self._is_running = True
        print(f"✅ Agent '{self.name}' (v{self.version}) started and registered with capabilities: {self.capabilities}")
        
        self._running_task = asyncio.create_task(self._listen_for_messages())
        print(f"Agent '{self.name}' started listening.")

    async def stop(self):
        """
        Stops the agent, unregisters it from the bus, and performs cleanup.
        """
        if not self._is_running:
            print(f"Agent {self.name} is not running.")
            return

        print(f"Attempting to stop agent '{self.name}'...")
        self._is_running = False
        self._bus.update_agent_status(self.name, "stopping")
        
        if self._running_task:
            self._running_task.cancel()
            try:
                await self._running_task
            except asyncio.CancelledError:
                print(f"Agent '{self.name}' listener task cancelled.")
        
        self._bus.update_agent_status(self.name, "offline")
        print(f"⛔ Agent '{self.name}' stopped and unregistered.")

    @abstractmethod
    async def handle_message(self, message: Message) -> Optional[Message]:
        """
        Abstract method to process an incoming message.
        Agent-specific logic should be implemented here.
        Should return a response message if required, or None.
        """
        pass

    async def _listen_for_messages(self):
        """Internal method for agents to listen for messages from the bus.
        Implements Adaptive Polling for Power Efficiency.
        """
        min_sleep = 0.1
        max_sleep = 5.0
        current_sleep = min_sleep

        while self._is_running:
            try:
                # Check permissions before processing
                # (Optimization: You could cache this decision if policy doesn't change often)
                
                # Get message from the bus
                message = await self._bus.get_message_async(self.name, timeout=current_sleep)
                
                if message:
                    # Wake up!
                    current_sleep = min_sleep
                    
                    print(f"Agent '{self.name}' received message: {message.subject}")
                    
                    # --- Governance Check ---
                    if not self.governance.check_permission(self.name, message.subject, message.content):
                        print(f"🛑 Agent '{self.name}' Action BLOCKED by Governance: {message.subject}")
                        if message.requires_response:
                            await self._bus.send_message_async(
                                sender_agent=self.name,
                                recipient_agent=message.sender_agent,
                                subject=f"governance_denial_to_{message.subject}",
                                content={"error": "Action denied by Governance Policy"},
                                message_type=MessageType.ERROR,
                                priority=MessagePriority.CRITICAL
                            )
                        continue # Skip processing
                    # ------------------------

                    self._bus.update_agent_status(self.name, "working")
                    try:
                        response_content = await self.handle_message(message)
                        
                        # Increment processed count
                        self._status_obj.messages_processed += 1
                        self._bus.agent_registry[self.name].messages_processed = self._status_obj.messages_processed
                        
                        if message.requires_response and response_content:
                            await self._bus.send_message_async(
                                sender_agent=self.name,
                                recipient_agent=message.sender_agent,
                                subject=f"response_to_{message.subject}",
                                content=response_content,
                                message_type=MessageType.RESPONSE,
                                priority=MessagePriority.NORMAL
                            )
                    except Exception as e:
                        print(f"❌ Agent '{self.name}' error processing message: {e}")
                        self._status_obj.errors_encountered += 1
                        self._bus.update_agent_status(self.name, "error")
                        if message.requires_response:
                            await self._bus.send_message_async(
                                sender_agent=self.name,
                                recipient_agent=message.sender_agent,
                                subject=f"error_response_to_{message.subject}",
                                content={"error": str(e), "original_message_id": message.message_id},
                                message_type=MessageType.ERROR,
                                priority=MessagePriority.CRITICAL
                            )
                    finally:
                        self._bus.update_agent_status(self.name, "idle")
                else:
                    # No message, sleep longer next time (Power Saving)
                    current_sleep = min(current_sleep * 1.5, max_sleep)
                    # Note: get_message_async already waited for 'timeout', so we loop back.
                    # Effectively we are just increasing the wait time in the next call.
            
            except asyncio.CancelledError:
                print(f"Agent '{self.name}' listener task was cancelled.")
                break
            except Exception as e:
                print(f"Agent '{self.name}' listening loop error: {e}")
                await asyncio.sleep(1) # Prevent busy loop on persistent error

    def get_metadata(self) -> Dict[str, Any]:
        """Returns the agent's metadata."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "capabilities": self.capabilities,
            "status": self._status_obj.status,
            "last_activity": self._status_obj.last_activity,
            "messages_processed": self._status_obj.messages_processed,
            "errors_encountered": self._status_obj.errors_encountered,
            "utilization_percent": self._status_obj.utilization_percent
        }

# --- 2. AgentLoader ---
class AgentLoader:
    """
    Scans a directory for agent modules, loads them dynamically,
    and manages their lifecycle.
    """
    def __init__(self, agent_dir: str = "core", plugin_dirs: List[str] = None):
        self.agent_dirs = [agent_dir]
        if plugin_dirs:
            self.agent_dirs.extend(plugin_dirs)
        
        self.loaded_agents: Dict[str, BaseAgent] = {}
        self._bus = AgentCommunicationBus.get_instance()

    async def load_and_start_agents(self) -> Dict[str, BaseAgent]:
        """Scans the agent directories, loads all valid agents, and starts them."""
        modules_to_load = []
        
        for directory in self.agent_dirs:
            if not os.path.exists(directory):
                print(f"⚠️  Agent directory not found: {directory}")
                continue
                
            print(f"Scanning for agents in '{directory}'...")
            
            # Add to sys.path to allow imports
            abs_path = os.path.abspath(directory)
            if abs_path not in sys.path:
                sys.path.insert(0, abs_path)
                
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.startswith("terminator_") and file.endswith("_agent.py"):
                        # Construct module path
                        # If the file is in a subdirectory, we need dot notation relative to the added sys.path entry
                        rel_path = os.path.relpath(os.path.join(root, file), start=directory)
                        module_name = rel_path.replace(os.sep, ".")[:-3] # Remove .py
                        modules_to_load.append(module_name)
        
        print(f"Found {len(modules_to_load)} potential agent modules.")

        for module_name in modules_to_load:
            try:
                module = importlib.import_module(module_name)
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # 1. Modern BaseAgent
                    if issubclass(obj, BaseAgent) and obj is not BaseAgent:
                        # ... (Existing logic for BaseAgent) ...
                        # ... (Keep the existing factory logic here) ...
                        # For brevity in this replace block, I'll reconstruct the BaseAgent logic 
                        # and add the Legacy logic below.
                        
                        agent_instance: Optional[BaseAgent] = None
                        if hasattr(module, 'create_agent') and inspect.isfunction(module.create_agent):
                            try:
                                agent_instance = module.create_agent()
                            except Exception as e:
                                print(f"⚠️ Error calling create_agent in {module_name}: {e}")
                                continue
                        else:
                            try:
                                agent_name_from_class = getattr(obj, 'AGENT_NAME', name)
                                agent_description_from_class = getattr(obj, 'AGENT_DESCRIPTION', f"A dynamically loaded agent: {name}")
                                agent_capabilities_from_class = getattr(obj, 'AGENT_CAPABILITIES', [])
                                agent_instance = obj(
                                    name=agent_name_from_class, 
                                    description=agent_description_from_class,
                                    capabilities=agent_capabilities_from_class
                                )
                            except Exception:
                                # Fallback for no-arg init
                                try:
                                    agent_instance = obj()
                                except Exception as e:
                                    print(f"⚠️  Error instantiating agent '{name}' from {module_name}: {e}")
                                    continue

                        if agent_instance:
                            if agent_instance.name in self.loaded_agents:
                                print(f"⚠️  Duplicate agent name '{agent_instance.name}'. Skipping.")
                                continue
                            self.loaded_agents[agent_instance.name] = agent_instance
                            await agent_instance.start()
                            break 

                    # 2. Legacy Agent Support
                    elif name.startswith("Terminator") and name.endswith("Agent"):
                        try:
                            print(f"🕰️  Found Legacy Agent: {name}")
                            # Most legacy agents use Singleton get_instance or simple init
                            if hasattr(obj, 'get_instance'):
                                instance = obj.get_instance()
                            else:
                                instance = obj()
                            
                            # Store with class name as key
                            self.loaded_agents[name] = instance
                            
                            # Start if possible
                            if hasattr(instance, 'start_monitoring'):
                                print(f"   ▷ Starting monitoring for {name}...")
                                # Check if it's async or sync
                                if inspect.iscoroutinefunction(instance.start_monitoring):
                                    await instance.start_monitoring()
                                else:
                                    instance.start_monitoring()
                            elif hasattr(instance, 'start'):
                                if inspect.iscoroutinefunction(instance.start):
                                    await instance.start()
                                else:
                                    instance.start()
                                    
                            print(f"   ✅ Legacy Agent '{name}' active.")
                            break 
                        except Exception as e:
                            print(f"⚠️  Failed to load Legacy Agent {name}: {e}")
            except Exception as e:
                print(f"❌ Error loading agent module {module_name}: {e}")
        
        print(f"🎉 Successfully loaded and started {len(self.loaded_agents)} agents.")
        return self.loaded_agents

    async def stop_all_agents(self):
        """Stops all loaded agents."""
        print("Stopping all agents...")
        for agent_name, agent_instance in list(self.loaded_agents.items()):
            try:
                if hasattr(agent_instance, 'stop'):
                    if inspect.iscoroutinefunction(agent_instance.stop):
                        await agent_instance.stop()
                    else:
                        agent_instance.stop()
                else:
                    print(f"⚠️  Agent '{agent_name}' has no stop() method.")
            except Exception as e:
                print(f"❌ Error stopping agent '{agent_name}': {e}")
            
            del self.loaded_agents[agent_name]
        print("All agents stopped.")

# Example usage (for testing purposes, not part of the core framework)
async def main():
    print("--- Agent Framework Test ---")
    
    # Ensure bus is initialized
    _ = AgentCommunicationBus.get_instance()
    
    # Create a dummy agent class for testing
    class MyTestAgent(BaseAgent):
        def __init__(self, name: str, description: str, capabilities: Optional[List[str]] = None):
            super().__init__(name, description, "1.0", capabilities)
            print(f"MyTestAgent '{self.name}' initialized.")

        async def handle_message(self, message: Message) -> Optional[Message]:
            print(f"MyTestAgent '{self.name}' handling message: {message.subject}")
            if message.subject == "ping":
                return {"response": f"pong from {self.name}", "original_id": message.message_id}
            return None

    # This part would typically be in a separate test file or an orchestrator
    # For now, let's pretend to save this as 'core/my_test_agent.py' temporarily
    # and then load it.
    
    # Temporarily create a dummy agent file for AgentLoader to find
    dummy_agent_code = """
from core.agent_framework import BaseAgent, Message
from typing import Optional, Dict, Any, List

class TerminatorDummyAgent(BaseAgent):
    AGENT_NAME = "DummyAgent"
    AGENT_DESCRIPTION = "A simple agent for testing the agent framework."
    AGENT_CAPABILITIES = ["test", "echo"]

    def __init__(self):
        super().__init__(self.AGENT_NAME, self.AGENT_DESCRIPTION, capabilities=self.AGENT_CAPABILITIES)
        print(f"DummyAgent '{self.name}' initialized via framework.")

    async def handle_message(self, message: Message) -> Optional[Message]:
        print(f"DummyAgent '{self.name}' received: {message.subject} - {message.content}")
        if message.subject == "echo":
            return {"echo_response": message.content, "agent": self.name}
        if message.subject == "status_request":
            return {"status": self.get_metadata()}
        return {"response": "DummyAgent acknowledges message."}

def create_agent():
    return TerminatorDummyAgent()
"""
    dummy_agent_path = os.path.join("core", "terminator_dummy_agent.py")
    with open(dummy_agent_path, "w") as f:
        f.write(dummy_agent_code)
    print(f"Temporary dummy agent created at {dummy_agent_path}")

    loader = AgentLoader("core")
    agents = await loader.load_and_start_agents()

    await asyncio.sleep(2) # Give agents time to register and start listening

    if "DummyAgent" in agents:
        bus = AgentCommunicationBus.get_instance()
        print("\nSending 'echo' message to DummyAgent...")
        response_id = await bus.send_message_async(
            sender_agent="TestOrchestrator",
            recipient_agent="DummyAgent",
            subject="echo",
            content={"text": "Hello DummyAgent, please echo this!"},
            requires_response=True
        )
        await asyncio.sleep(0.1) # Yield to bus loop

        # Attempt to get the response (this part would usually be more sophisticated)
        # For a true request-response, the orchestrator would listen for a message_id
        # or have a dedicated response handler.
        print("\nAttempting to retrieve response from orchestrator's perspective (simplified)...")
        # In a real system, the orchestrator would have its own message queue.
        # For this test, we'll just check the bus's internal registry for response messages if the dummy agent sends one directly.
        # This part is illustrative as orchestrator won't have a queue yet.
        
        # A more direct test: check bus status
        bus_status = bus.get_bus_status()
        print("\nBus Status after sending message:")
        print(bus_status)

    await asyncio.sleep(3) # Let messages process

    await loader.stop_all_agents()

    # Clean up dummy agent file
    os.remove(dummy_agent_path)
    print(f"Cleaned up {dummy_agent_path}")
    print("--- Test Complete ---")


if __name__ == "__main__":
    # Ensure current working directory is the project root for module imports
    # For testing, you might run this file directly from the project root.
    # If run from core/, adjust agent_dir in AgentLoader.
    # Assuming this script is run from Terminator-Project root:
    current_dir = os.path.basename(os.getcwd())
    if current_dir != "Terminator-Project":
        print(f"WARNING: Script expected to run from 'Terminator-Project' root. Current: {current_dir}")
        print("Adjusting path for test...")
        # Assuming we are in core/, go up one level
        os.chdir(os.path.dirname(os.getcwd()))
        
    asyncio.run(main())
