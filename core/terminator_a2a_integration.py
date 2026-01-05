#!/usr/bin/env python3
"""
Terminator A2A (Agent2Agent) Protocol Integration
=================================================

Integrates the Agent2Agent (A2A) protocol into the Terminator system,
enabling seamless agent-to-agent communication across platforms.

Features:
- Agent Card generation for all Terminator agents
- JSON-RPC 2.0 communication over HTTP/HTTPS
- Discovery mechanism for external A2A agents
- Task coordination and long-running collaboration
- Complements existing MCP integration

References:
- A2A Protocol: https://a2a-protocol.org/
- GitHub: https://github.com/a2aproject/A2A
- Linux Foundation Project: https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import aiohttp
from aiohttp import web

# Import Terminator components
try:
    from core.terminator_agent_communication_bus import get_communication_bus, MessageType, MessagePriority
except ImportError:
    # Fallback for standalone testing
    pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AgentCard:
    """
    Agent Card for A2A discovery.
    JSON file that outlines agent metadata and capabilities.
    """
    name: str
    description: str
    version: str
    service_endpoint: str
    supported_modalities: List[str]  # ["text", "forms", "media"]
    authentication: Dict[str, Any]
    capabilities: List[str]
    metadata: Optional[Dict[str, Any]] = None

    def to_json(self) -> str:
        """Convert agent card to JSON format"""
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'AgentCard':
        """Load agent card from JSON"""
        data = json.loads(json_str)
        return cls(**data)


class A2AProtocolServer:
    """
    A2A Protocol Server for Terminator agents.
    Implements JSON-RPC 2.0 over HTTP for agent-to-agent communication.
    """

    def __init__(self, host: str = "localhost", port: int = 8001):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.agent_cards: Dict[str, AgentCard] = {}
        self.bus = None
        self.active_tasks: Dict[str, Dict[str, Any]] = {}

        # Setup routes
        self.app.router.add_post('/a2a/rpc', self.handle_jsonrpc)
        self.app.router.add_get('/a2a/agents', self.list_agents)
        self.app.router.add_get('/a2a/agents/{agent_name}/card', self.get_agent_card)
        self.app.router.add_post('/a2a/discover', self.discover_agents)

    async def initialize(self):
        """Initialize A2A server and register Terminator agents"""
        try:
            self.bus = get_communication_bus()
            await self.bus.register_agent_async("a2a_server")
            logger.info("A2A Server registered with Terminator bus")
        except Exception as e:
            logger.warning(f"Could not connect to Terminator bus: {e}")
            logger.info("Running in standalone mode")

        # Generate agent cards for all known Terminator agents
        await self.generate_terminator_agent_cards()

    async def generate_terminator_agent_cards(self):
        """Generate A2A Agent Cards for all Terminator agents"""

        # Core orchestrators
        self.register_agent_card(AgentCard(
            name="advanced_orchestrator",
            description="Claude Code-like autonomous agent with multi-step reasoning",
            version="1.0.0",
            service_endpoint=f"http://{self.host}:{self.port}/a2a/rpc",
            supported_modalities=["text", "forms"],
            authentication={"type": "none"},  # TODO: Add proper auth
            capabilities=[
                "multi_step_reasoning",
                "tool_execution",
                "confidence_scoring",
                "self_refinement"
            ],
            metadata={"agent_type": "orchestrator", "priority": "high"}
        ))

        # Task execution
        self.register_agent_card(AgentCard(
            name="task_executor",
            description="Executes tasks with integrated tool calling",
            version="1.0.0",
            service_endpoint=f"http://{self.host}:{self.port}/a2a/rpc",
            supported_modalities=["text"],
            authentication={"type": "none"},
            capabilities=["task_execution", "tool_calling", "ios_control", "android_control"],
            metadata={"agent_type": "executor"}
        ))

        # Context awareness
        self.register_agent_card(AgentCard(
            name="context_awareness",
            description="Maintains conversation context and multi-turn memory",
            version="1.0.0",
            service_endpoint=f"http://{self.host}:{self.port}/a2a/rpc",
            supported_modalities=["text"],
            authentication={"type": "none"},
            capabilities=["context_tracking", "memory_management", "conversation_history"],
            metadata={"agent_type": "cognitive"}
        ))

        # Decision engine
        self.register_agent_card(AgentCard(
            name="decision_engine",
            description="Routes queries to appropriate handlers and makes strategic decisions",
            version="1.0.0",
            service_endpoint=f"http://{self.host}:{self.port}/a2a/rpc",
            supported_modalities=["text"],
            authentication={"type": "none"},
            capabilities=["query_routing", "decision_making", "strategy"],
            metadata={"agent_type": "orchestrator"}
        ))

        # Error monitoring
        self.register_agent_card(AgentCard(
            name="error_monitor",
            description="Detects and recovers from system failures",
            version="1.0.0",
            service_endpoint=f"http://{self.host}:{self.port}/a2a/rpc",
            supported_modalities=["text"],
            authentication={"type": "none"},
            capabilities=["error_detection", "auto_recovery", "health_monitoring"],
            metadata={"agent_type": "infrastructure"}
        ))

        logger.info(f"Generated {len(self.agent_cards)} agent cards")

    def register_agent_card(self, card: AgentCard):
        """Register an agent card"""
        self.agent_cards[card.name] = card
        logger.info(f"Registered agent card: {card.name}")

    async def handle_jsonrpc(self, request: web.Request) -> web.Response:
        """
        Handle JSON-RPC 2.0 requests.
        Format: {"jsonrpc": "2.0", "method": "...", "params": {...}, "id": 1}
        """
        try:
            data = await request.json()

            if data.get("jsonrpc") != "2.0":
                return web.json_response({
                    "jsonrpc": "2.0",
                    "error": {"code": -32600, "message": "Invalid Request"},
                    "id": data.get("id")
                })

            method = data.get("method")
            params = data.get("params", {})
            request_id = data.get("id")

            # Route to appropriate handler
            if method == "agent.call":
                result = await self.handle_agent_call(params)
            elif method == "agent.discover":
                result = await self.handle_agent_discover(params)
            elif method == "task.create":
                result = await self.handle_task_create(params)
            elif method == "task.status":
                result = await self.handle_task_status(params)
            elif method == "task.cancel":
                result = await self.handle_task_cancel(params)
            else:
                return web.json_response({
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": "Method not found"},
                    "id": request_id
                })

            return web.json_response({
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id
            })

        except json.JSONDecodeError:
            return web.json_response({
                "jsonrpc": "2.0",
                "error": {"code": -32700, "message": "Parse error"},
                "id": None
            })
        except Exception as e:
            logger.error(f"Error handling JSON-RPC request: {e}")
            return web.json_response({
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
                "id": data.get("id")
            })

    async def handle_agent_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle agent.call method - invoke a Terminator agent"""
        agent_name = params.get("agent")
        message = params.get("message")

        if not agent_name or not message:
            raise ValueError("Missing required params: agent, message")

        if agent_name not in self.agent_cards:
            raise ValueError(f"Unknown agent: {agent_name}")

        # Send message via Terminator bus
        if self.bus:
            await self.bus.send_message_async(
                sender_agent="a2a_server",
                recipient_agent=agent_name,
                subject="A2A Request",
                content={"message": message, "source": "a2a"},
                message_type=MessageType.REQUEST,
                priority=MessagePriority.HIGH
            )

            # Wait for response (with timeout)
            response_msg = await self.bus.get_message_async("a2a_server", timeout=10.0)

            if response_msg:
                return {
                    "agent": agent_name,
                    "response": response_msg.get("content", {}),
                    "timestamp": datetime.now().isoformat()
                }

        return {
            "agent": agent_name,
            "response": "Agent communication not available",
            "timestamp": datetime.now().isoformat()
        }

    async def handle_agent_discover(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle agent.discover method - list available agents"""
        capabilities = params.get("capabilities", [])

        # Filter agents by capabilities if specified
        matching_agents = []
        for name, card in self.agent_cards.items():
            if not capabilities or any(cap in card.capabilities for cap in capabilities):
                matching_agents.append({
                    "name": card.name,
                    "description": card.description,
                    "capabilities": card.capabilities,
                    "endpoint": card.service_endpoint
                })

        return {"agents": matching_agents}

    async def handle_task_create(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task.create method - create a long-running task"""
        task_id = f"task_{datetime.now().timestamp()}"
        agent_name = params.get("agent")
        task_description = params.get("description")

        self.active_tasks[task_id] = {
            "id": task_id,
            "agent": agent_name,
            "description": task_description,
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        logger.info(f"Created task {task_id} for agent {agent_name}")

        return {"task_id": task_id, "status": "created"}

    async def handle_task_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task.status method - get task status"""
        task_id = params.get("task_id")

        if task_id not in self.active_tasks:
            raise ValueError(f"Unknown task: {task_id}")

        return self.active_tasks[task_id]

    async def handle_task_cancel(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task.cancel method - cancel a task"""
        task_id = params.get("task_id")

        if task_id not in self.active_tasks:
            raise ValueError(f"Unknown task: {task_id}")

        self.active_tasks[task_id]["status"] = "cancelled"
        self.active_tasks[task_id]["updated_at"] = datetime.now().isoformat()

        return {"task_id": task_id, "status": "cancelled"}

    async def list_agents(self, request: web.Request) -> web.Response:
        """HTTP GET /a2a/agents - List all registered agents"""
        agents = [
            {
                "name": card.name,
                "description": card.description,
                "capabilities": card.capabilities,
                "endpoint": f"/a2a/agents/{card.name}/card"
            }
            for card in self.agent_cards.values()
        ]
        return web.json_response({"agents": agents})

    async def get_agent_card(self, request: web.Request) -> web.Response:
        """HTTP GET /a2a/agents/{agent_name}/card - Get agent card"""
        agent_name = request.match_info['agent_name']

        if agent_name not in self.agent_cards:
            return web.json_response(
                {"error": f"Agent not found: {agent_name}"},
                status=404
            )

        card = self.agent_cards[agent_name]
        return web.Response(
            text=card.to_json(),
            content_type='application/json'
        )

    async def discover_agents(self, request: web.Request) -> web.Response:
        """HTTP POST /a2a/discover - Discover agents by capabilities"""
        data = await request.json()
        capabilities = data.get("capabilities", [])

        result = await self.handle_agent_discover({"capabilities": capabilities})
        return web.json_response(result)

    async def start(self):
        """Start the A2A server"""
        await self.initialize()
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        logger.info(f"A2A Protocol Server started at http://{self.host}:{self.port}")
        logger.info(f"Agent Cards: http://{self.host}:{self.port}/a2a/agents")
        logger.info(f"JSON-RPC Endpoint: http://{self.host}:{self.port}/a2a/rpc")


class A2AClient:
    """
    A2A Protocol Client for communicating with external A2A agents.
    """

    def __init__(self):
        self.discovered_agents: Dict[str, AgentCard] = {}

    async def discover_agent(self, endpoint: str) -> Optional[AgentCard]:
        """Discover an external A2A agent"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{endpoint}/card") as response:
                    if response.status == 200:
                        card_json = await response.text()
                        card = AgentCard.from_json(card_json)
                        self.discovered_agents[card.name] = card
                        logger.info(f"Discovered agent: {card.name}")
                        return card
        except Exception as e:
            logger.error(f"Failed to discover agent at {endpoint}: {e}")
        return None

    async def call_agent(
        self,
        endpoint: str,
        agent_name: str,
        message: str
    ) -> Optional[Dict[str, Any]]:
        """Call an external A2A agent via JSON-RPC"""
        try:
            async with aiohttp.ClientSession() as session:
                rpc_request = {
                    "jsonrpc": "2.0",
                    "method": "agent.call",
                    "params": {
                        "agent": agent_name,
                        "message": message
                    },
                    "id": 1
                }

                async with session.post(
                    f"{endpoint}/a2a/rpc",
                    json=rpc_request
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("result")
        except Exception as e:
            logger.error(f"Failed to call agent {agent_name}: {e}")
        return None


async def main():
    """Main entry point for A2A server"""
    server = A2AProtocolServer(host="0.0.0.0", port=8001)
    await server.start()

    # Keep server running
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        logger.info("A2A Server shutting down...")


if __name__ == "__main__":
    asyncio.run(main())
