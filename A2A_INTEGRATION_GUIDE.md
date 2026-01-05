# Agent2Agent (A2A) Protocol Integration Guide

## Overview

The Terminator system now supports the **Agent2Agent (A2A) Protocol**, an open standard for AI agent interoperability developed by Google and now governed by the Linux Foundation.

This integration allows Terminator's 38+ specialized agents to communicate with external A2A-compliant agents across different platforms, frameworks, and organizations.

## What is A2A?

The A2A protocol enables:
- **Agent Discovery**: Find and connect to agents on other platforms
- **Capability Negotiation**: Agents advertise what they can do via Agent Cards
- **Secure Collaboration**: Long-running task coordination
- **Platform Agnostic**: Works with LangGraph, CrewAI, Semantic Kernel, custom solutions, and more

### Key Standards
- **Communication**: JSON-RPC 2.0 over HTTP/HTTPS
- **Discovery**: Agent Cards (JSON metadata files)
- **Modalities**: Text, forms, media
- **Complementary**: Works alongside Anthropic's MCP (Model Context Protocol)

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Terminator A2A Server                  │
│                     (Port 8001)                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐    ┌──────────────┐   ┌────────────┐ │
│  │ Agent Cards │    │  JSON-RPC    │   │ Discovery  │ │
│  │  Endpoint   │───▶│   Endpoint   │◀──│  Endpoint  │ │
│  └─────────────┘    └──────────────┘   └────────────┘ │
│         │                  │                   │       │
│         └──────────────────┼───────────────────┘       │
│                            │                           │
│                   ┌────────▼────────┐                  │
│                   │ Terminator Bus  │                  │
│                   │  (Pub/Sub)      │                  │
│                   └────────┬────────┘                  │
│                            │                           │
│         ┌──────────────────┼──────────────────┐        │
│         │                  │                  │        │
│    ┌────▼─────┐     ┌─────▼──────┐    ┌─────▼────┐   │
│    │Advanced  │     │   Task     │    │ Context  │   │
│    │Orchestr. │     │ Executor   │    │Awareness │   │
│    └──────────┘     └────────────┘    └──────────┘   │
│         ... 35+ more specialized agents ...           │
└─────────────────────────────────────────────────────────┘
```

## Getting Started

### 1. Install Dependencies

The A2A server uses Python's `aiohttp` library:

```bash
pip3 install aiohttp
```

### 2. Start the A2A Server

```bash
./start_a2a_server.sh
```

The server will start on `http://localhost:8001` with the following endpoints:

- **Agent List**: `GET http://localhost:8001/a2a/agents`
- **Agent Card**: `GET http://localhost:8001/a2a/agents/{agent_name}/card`
- **JSON-RPC**: `POST http://localhost:8001/a2a/rpc`
- **Discovery**: `POST http://localhost:8001/a2a/discover`

### 3. Test the Integration

#### List Available Agents

```bash
curl http://localhost:8001/a2a/agents
```

Expected response:
```json
{
  "agents": [
    {
      "name": "advanced_orchestrator",
      "description": "Claude Code-like autonomous agent with multi-step reasoning",
      "capabilities": ["multi_step_reasoning", "tool_execution", "confidence_scoring"],
      "endpoint": "/a2a/agents/advanced_orchestrator/card"
    },
    ...
  ]
}
```

#### Get an Agent Card

```bash
curl http://localhost:8001/a2a/agents/advanced_orchestrator/card
```

#### Call an Agent (JSON-RPC)

```bash
curl -X POST http://localhost:8001/a2a/rpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "agent.call",
    "params": {
      "agent": "task_executor",
      "message": "Execute a system health check"
    },
    "id": 1
  }'
```

#### Discover Agents by Capability

```bash
curl -X POST http://localhost:8001/a2a/discover \
  -H "Content-Type: application/json" \
  -d '{
    "capabilities": ["error_detection", "auto_recovery"]
  }'
```

## Available Terminator Agents via A2A

The following Terminator agents are exposed via A2A:

### Orchestrators
- **advanced_orchestrator**: Multi-step reasoning, confidence scoring, self-refinement
- **decision_engine**: Query routing, strategic decision making

### Execution
- **task_executor**: Task execution, iOS/Android control, tool calling

### Cognitive
- **context_awareness**: Conversation tracking, memory management

### Infrastructure
- **error_monitor**: Error detection, auto-recovery, health monitoring

*Note: Additional agents can be registered by modifying `core/terminator_a2a_integration.py`*

## JSON-RPC Methods

The A2A server supports the following JSON-RPC 2.0 methods:

### agent.call
Invoke a Terminator agent with a message.

```json
{
  "jsonrpc": "2.0",
  "method": "agent.call",
  "params": {
    "agent": "agent_name",
    "message": "your message here"
  },
  "id": 1
}
```

### agent.discover
Discover agents by capabilities.

```json
{
  "jsonrpc": "2.0",
  "method": "agent.discover",
  "params": {
    "capabilities": ["capability1", "capability2"]
  },
  "id": 2
}
```

### task.create
Create a long-running task.

```json
{
  "jsonrpc": "2.0",
  "method": "task.create",
  "params": {
    "agent": "agent_name",
    "description": "task description"
  },
  "id": 3
}
```

### task.status
Get task status.

```json
{
  "jsonrpc": "2.0",
  "method": "task.status",
  "params": {
    "task_id": "task_12345"
  },
  "id": 4
}
```

### task.cancel
Cancel a running task.

```json
{
  "jsonrpc": "2.0",
  "method": "task.cancel",
  "params": {
    "task_id": "task_12345"
  },
  "id": 5
}
```

## Using the A2A Client

Terminator also includes an A2A client for calling external A2A agents:

```python
from core.terminator_a2a_integration import A2AClient
import asyncio

async def main():
    client = A2AClient()

    # Discover an external agent
    card = await client.discover_agent("https://external-agent.com")

    # Call the external agent
    result = await client.call_agent(
        endpoint="https://external-agent.com",
        agent_name="external_agent",
        message="Hello from Terminator!"
    )
    print(result)

asyncio.run(main())
```

## Integration with Existing Systems

### With MCP (Model Context Protocol)

A2A complements Terminator's existing MCP integration:

- **MCP**: Agent-to-tool communication (Imagen, Veo, Chirp, etc.)
- **A2A**: Agent-to-agent communication (cross-platform collaboration)

### With Terminator Communication Bus

The A2A server automatically integrates with Terminator's internal agent communication bus:

1. External A2A requests arrive via HTTP/JSON-RPC
2. A2A server translates to Terminator bus messages
3. Target agent receives message via bus
4. Agent response flows back through A2A server
5. JSON-RPC response sent to external caller

## Advanced Configuration

### Adding New Agents

To register additional Terminator agents for A2A access:

1. Edit `core/terminator_a2a_integration.py`
2. Add a new agent card in `generate_terminator_agent_cards()`:

```python
self.register_agent_card(AgentCard(
    name="your_agent",
    description="Description of your agent",
    version="1.0.0",
    service_endpoint=f"http://{self.host}:{self.port}/a2a/rpc",
    supported_modalities=["text"],
    authentication={"type": "none"},
    capabilities=["capability1", "capability2"],
    metadata={"agent_type": "category"}
))
```

3. Restart the A2A server

### Authentication (TODO)

Current implementation uses `authentication: {"type": "none"}`. Future versions will support:
- API key authentication
- OAuth 2.0
- JWT tokens
- Mutual TLS

### Custom Port

To run A2A server on a different port, edit `core/terminator_a2a_integration.py`:

```python
server = A2AProtocolServer(host="0.0.0.0", port=YOUR_PORT)
```

## Ecosystem Integration

The A2A protocol is supported by 150+ organizations including:

**Technology Partners:**
- Google
- Atlassian, Box, Cohere, Intuit
- LangChain, MongoDB, PayPal
- Salesforce, SAP, ServiceNow, Workday

**Service Providers:**
- Accenture, BCG, Deloitte

**Frameworks:**
- LangGraph
- CrewAI
- Semantic Kernel
- Custom solutions

## Resources

### Official Documentation
- A2A Protocol Spec: https://a2a-protocol.org/
- GitHub Repository: https://github.com/a2aproject/A2A
- Linux Foundation: https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project

### Terminator Documentation
- `CLAUDE.md` - System architecture
- `VISUAL_FRAMEWORK.md` - System diagrams
- `INTER_PROJECT_COMMUNICATION_BRIDGE.md` - Inter-project messaging

### Community
- GitHub Discussions: https://github.com/a2aproject/A2A/discussions
- GitHub Issues: https://github.com/a2aproject/A2A/issues

## Troubleshooting

### Server Won't Start

**Problem**: `ModuleNotFoundError: No module named 'aiohttp'`

**Solution**:
```bash
pip3 install aiohttp
```

### Can't Connect to Terminator Bus

**Problem**: "Could not connect to Terminator bus"

**Solution**: The A2A server can run standalone or integrated. For full integration:
1. Ensure Terminator main system is running
2. Check `core/terminator_agent_communication_bus.py` is accessible

### Port Already in Use

**Problem**: `OSError: [Errno 48] Address already in use`

**Solution**:
```bash
lsof -ti:8001 | xargs kill
./start_a2a_server.sh
```

### JSON-RPC Errors

**Problem**: `{"error": {"code": -32601, "message": "Method not found"}}`

**Solution**: Check method name. Supported methods:
- `agent.call`
- `agent.discover`
- `task.create`
- `task.status`
- `task.cancel`

## Next Steps

1. **Explore Agent Cards**: Visit `http://localhost:8001/a2a/agents` to see all available agents
2. **Test JSON-RPC calls**: Use the examples above to interact with agents
3. **Connect external agents**: Use the A2AClient to call agents on other platforms
4. **Build integrations**: Create custom workflows combining Terminator + external A2A agents

## Contributing

To extend A2A functionality:

1. Fork the repository
2. Add features to `core/terminator_a2a_integration.py`
3. Update this documentation
4. Test with external A2A agents
5. Submit pull request

## License

The A2A protocol is open source. Terminator's implementation follows the project's existing license.

---

**Last Updated**: 2025-01-04
**Terminator Version**: 1.0.0 with A2A support
**A2A Protocol Version**: 0.3+
