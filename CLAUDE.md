# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## System Overview

TERMINATOR is a multi-interface autonomous AI agent system with 38+ specialized agents, supporting both local (Ollama) and cloud (Gemini/Claude) LLM backends. The system features voice capabilities, WebSocket communication, and multiple frontend interfaces (Web Terminal, Terminal UI, CLI).

## Requirements

- **Python 3.13+** (verify with `python3 --version`)
  - Uses modern asyncio features and type hints
  - Virtual environments in `/venv/` (Python 3.14 available)
- **Node.js** (for web terminal development)
  - npm 8.0+ recommended
- **Ollama** (for local LLM, or cloud API keys for Gemini/Claude)
  - Default backend, runs on localhost:11434
  - Must have llama3 model pulled: `ollama pull llama3`

## Quick Start Commands

### First-Time Setup

```bash
# 1. Install Python dependencies
pip3 install -r requirements.txt

# 2. Ensure Ollama is running (or set cloud API keys)
ollama serve                # In separate terminal
ollama pull llama3         # Download model

# 3. Build web terminal (if using web interface)
cd terminator-web-terminal && npm install && npm run build && cd ..

# 4. Optional: Install Universal CLI globally
./install_cli.sh           # Adds 'terminator' command to PATH
```

### Running the System

```bash
# Interactive launcher menu (recommended for first-time users)
./start_all.sh

# Direct launches
./start_web_terminal.sh    # Web UI on http://localhost:8000
./start_terminal_ui.sh     # Rich terminal interface
./start_cli.sh             # Minimal CLI

# Universal CLI (Claude-style slash commands)
terminator                 # Launch from anywhere (after ./install_cli.sh)
./terminator --help        # Without global install

# Other utilities
./start_command_center.sh  # Launch command center
./start_demo.sh            # Demo mode
```

### Development

```bash
# Web terminal development
cd terminator-web-terminal
npm install           # Install dependencies (first time)

npm run dev           # Development server with hot reload (port 5173)
                      # Use this for UI development - changes reflect instantly

npm run build         # Production build to dist/ folder
                      # Required before running ./start_web_terminal.sh

npm run lint          # Run ESLint on source files
npm run preview       # Preview production build locally

# Backend doesn't auto-reload - restart ./start_web_terminal.sh after Python changes
```

**Port Management:**
```bash
# Kill port 8000 if backend already running
lsof -ti:8000 | xargs kill

# Kill port 5173 if dev server stuck
lsof -ti:5173 | xargs kill
```

**Development Workflow:**
1. UI changes: `npm run dev` in terminator-web-terminal/ - live reload works
2. Python changes: Edit code, then restart `./start_web_terminal.sh` - no auto-reload
3. Before committing: `npm run build` to update dist/

### LLM Backend Setup

```bash
# Ollama (local, no internet required)
brew install ollama
ollama pull llama3
ollama serve

# Cloud backends (optional)
export GOOGLE_API_KEY="your-key"      # For Gemini
export ANTHROPIC_API_KEY="your-key"   # For Claude
```

## Architecture: Multi-Layer Communication System

### 1. **Agent Communication Bus** (Pub/Sub Pattern)
Located in `/core/terminator_agent_communication_bus.py`

The bus is the central nervous system enabling inter-agent messaging:
- **Async-first design** with asyncio PriorityQueues
- **Per-agent message queues** (no thundering herd problem)
- **Priority-based routing** (CRITICAL → HIGH → NORMAL → LOW)
- **Message types**: REQUEST, RESPONSE, NOTIFICATION, ERROR, STATUS
- **Hybrid sync/async bridge** for legacy agent compatibility

Key pattern: Agents register with the bus, send messages to specific agents or broadcast to all, and listen to their own queue.

```python
# Example: How agents communicate
bus = get_communication_bus()
await bus.register_agent_async("my_agent")
await bus.send_message_async(
    sender_agent="my_agent",
    recipient_agent="task_executor",
    subject="Execute Task",
    content={"task": "analyze_data"}
)
```

### 2. **Autonomous Agent Orchestrators** (Two Flavors)

#### Simple Orchestrator (`/core/terminator_agentic_orchestrator.py`)
- Single-shot tool calling with basic reasoning
- Analyzes query → selects tools → executes → returns answer
- Suitable for straightforward tasks

#### Advanced Orchestrator (`/core/advanced_agentic_orchestrator.py`)
**This is the Claude Code-like autonomous agent.**

Multi-step iterative reasoning loop with:
- **ReasoningState tracking** across iterations (max 5)
- **Confidence scoring** (0.0-1.0, threshold 0.75)
- **Tool prioritization** (CRITICAL, HIGH, MEDIUM, LOW, OPTIONAL)
- **Execution strategies** (PARALLEL, SEQUENTIAL, DEPENDENT)
- **Self-refinement** - asks "do I have enough information?"
- **Decision path logging** - tracks every choice made

Pattern: Query → Analyze → Determine Tools → Execute → Calculate Confidence → Refine if needed → Iterate or Synthesize Final Answer

**Confidence Scoring Logic:**
The orchestrator calculates confidence (0.0-1.0) based on:
- Initial base confidence from query analysis
- Tool execution success (+0.1 to +0.3 per successful tool)
- Information completeness assessment
- Error penalties (-0.2 per failed tool)
- Iteration limit (max 5 iterations to prevent infinite loops)

Threshold for completion: **0.75 confidence**

If confidence < 0.75 after iteration, the orchestrator:
1. Identifies information gaps
2. Selects additional tools
3. Re-executes and re-evaluates
4. Maximum 5 iterations before forced synthesis

### 3. **WebSocket Bridge** (`terminator_bridge.py`)
Connects web terminal to agent bus:
- FastAPI WebSocket endpoint (`/ws`)
- ConnectionManager for multiple simultaneous clients
- Bidirectional: User commands → Bus, Agent responses → WebSocket
- Serves static React build from `terminator-web-terminal/dist/`

### 4. **Frontend Layer**

#### Web Terminal (React + Vite + Tailwind)
- Location: `/terminator-web-terminal/`
- Main components: `Terminal.jsx`, `Header.jsx`, `StatusPanel.jsx`, `ArcReactor.jsx`
- Features: Voice I/O (Web Speech API), streaming responses, real-time status
- Connects via WebSocket to `ws://localhost:8000/ws`

#### Terminal UI (Textual Framework)
- Location: `/terminator_tui.py`
- Rich terminal with robot animations and eye states
- Keyboard-driven, runs entirely in terminal

#### Simple CLI
- Location: `/terminator.py`
- Direct conversational interface
- Minimal overhead, good for automation

#### Universal CLI (Claude-style)
- Location: `/terminator_universal_cli.py`
- Slash commands: `/healthCheck`, `/connectiOS`, `/agents`, `/tools`, etc.
- Universal platform control: control iOS, Android, macOS, Web, MCP from terminal
- Cross-platform messaging: `/run ios get clipboard`, `/broadcast show status`
- Launch via: `terminator` (after running `./install_cli.sh`)

## Critical Agent Types (38+ Total)

### Core Always-Running Agents (4)
1. **Project Monitor Agent** - Tracks project health
2. **Testing Agent** - Validates system operations
3. **Diagnostic Engine** - Continuous system checks
4. **Voice Assistant** - Handles speech I/O

### Key On-Demand Agents
- **Context Awareness Agent** - Maintains conversation context
- **Decision Engine** - Routes queries to appropriate handlers
- **Task Executor Agent** - Executes tasks with tool integration
- **Error Monitor Agent** - Detects and recovers from failures
- **Learning System** - Improves from user interactions
- **Memory Agent** - Persistent conversation memory
- **Advanced Agentic Orchestrator** - Autonomous multi-step reasoning

All agents live in `/core/` as separate Python modules.

## Tool Execution System

The system has 11+ integrated tools across domains:

**iOS Tools**: Get text, clipboard, run shortcuts, check status
**Android Tools**: Get text, clipboard, run commands, launch apps
**Network Tools**: Scan network, list devices, find by name/IP/type
**GitHub Tools**: Push projects, create PRs, search repos, analyze code
**Web Tools**: Search, fetch content
**Code Tools**: Execute code snippets

Tools are called via orchestrators based on query analysis. Each tool execution includes error handling and result validation.

## MCP (Model Context Protocol) Integration

### MCP Client (`/core/mcp_client.py`)
TERMINATOR integrates with Google's Vertex AI Creative Studio MCP servers:

**Available MCP Servers:**
- **Imagen** (port 9000) - Image generation
- **Veo** (port 9001) - Video creation
- **Chirp** (port 9002) - Speech synthesis
- **Lyria** (port 9003) - Music generation
- **AVTool** (port 9004) - Audio/video compositing

**Connection via Universal CLI:**
```bash
terminator
/connectMCP              # Connect to MCP servers
/run mcp imagen generate "prompt"
```

**Requirements:**
- Google Cloud project ID
- MCP servers running on localhost ports 9000-9004
- Proper GCP authentication

## LLM Router Pattern

The LLM routing logic is implemented within the orchestrators. The system automatically selects between:
- **Ollama** (local, no API key needed, default)
- **Gemini** (cloud, fast, large context)
- **Claude** (cloud, advanced reasoning)

Selection criteria: API key availability, task complexity, network status

## Message Flow Example

```
User types in Web Terminal
    ↓
WebSocket sends to terminator_bridge.py
    ↓
Bridge publishes to Agent Communication Bus
    ↓
Orchestrator agent receives message
    ↓
Analyzes query → determines tools needed
    ↓
Sends tool execution requests via bus
    ↓
Task Executor agent executes tools
    ↓
Results sent back to Orchestrator
    ↓
Orchestrator synthesizes answer
    ↓
Response published to bus
    ↓
Bridge forwards to WebSocket
    ↓
Web Terminal displays response (with streaming)
```

## Voice Integration

The web terminal uses browser Web Speech API:
- **Input**: `webkitSpeechRecognition` for speech-to-text
- **Output**: `speechSynthesis.speak()` for text-to-speech
- Toggle listening with microphone button
- Visual indicators for speaking/listening states

Backend voice handling in `/core/voice.py` and `/core/voice_chat.py`

## Critical Implementation Notes

### Message Bus Lifecycle
**IMPORTANT:** The Agent Communication Bus runs a background event loop in a daemon thread. This means:
- Agents can use sync OR async methods (`send_message()` vs `send_message_async()`)
- The bus automatically bridges between sync and async worlds
- Never manually manage the event loop - it's managed by `AgentCommunicationBus._run_loop()`
- When creating new agents, always register via `bus.register_agent_async(agent_name)` first

**Getting the Bus Instance:**
```python
from core.terminator_agent_communication_bus import get_communication_bus

# Singleton pattern - same instance everywhere
bus = get_communication_bus()
```

### Message Priority and Ordering
Messages in agent queues are ordered by:
1. **Priority** (CRITICAL=0, HIGH=1, NORMAL=2, LOW=3) - lower value = higher priority
2. **Timestamp** - earlier messages processed first within same priority

Critical messages will jump the queue ahead of normal ones.

### WebSocket Message Format
All WebSocket messages follow this JSON structure:
```json
{
  "type": "request|response|notification|error|status",
  "sender": "agent_name",
  "content": {},
  "subject": "message_subject"
}
```

From client to server:
```json
{
  "command": "user command text"
}
```

### React Component State Management
The web terminal uses React hooks for state:
- `useState` for local component state (messages, input, connection status)
- WebSocket connection managed in `Terminal.jsx` with reconnection logic
- Voice API directly accessed via browser's `webkitSpeechRecognition` and `speechSynthesis`
- No external state management library (no Redux/Zustand)

### Agent Registration Pattern
Every agent MUST follow this initialization pattern:
```python
# In agent __init__ or startup
bus = get_communication_bus()
await bus.register_agent_async("agent_name")

# Then start listening
while True:
    msg = await bus.get_message_async("agent_name", timeout=0.1)
    if msg:
        # Process message
        pass
```

## Tool Discovery

Before implementing new CLI features, always check existing capabilities:

```bash
./terminator --help           # List all Universal CLI commands
terminator                    # Launch CLI and use /help for slash commands
./start_web_terminal.sh --help  # Check web terminal options
./start_terminal_ui.sh --help   # Check TUI options
```

**Discovering Agent Capabilities:**
```bash
# From Universal CLI
terminator
/agents      # List all registered agents and their status
/tools       # List all available tools and their capabilities
```

**Checking System State:**
```bash
./terminator /healthCheck     # Comprehensive system diagnostics
```

## Common Patterns

### Adding a New Agent
1. Create module in `/core/terminator_<agent_name>.py`
2. Register with communication bus in `__init__`
3. Implement message handler loop
4. Define agent capabilities and tools
5. Add to agent ecosystem documentation

### Modifying Tool Execution
1. Locate tool in orchestrator (`advanced_agentic_orchestrator.py` or `terminator_agentic_orchestrator.py`)
2. Update `ToolType` enum if adding new tool
3. Add execution logic in `_execute_tool()` method
4. Update tool prioritization in `_determine_tools_intelligently()`
5. Adjust confidence boost values for tool results

### Debugging WebSocket Issues
1. Check FastAPI logs for connection errors
2. Verify web terminal WebSocket URL matches backend
3. Test bus registration: `await bus.register_agent_async("test")`
4. Use browser DevTools Network tab to inspect WS frames
5. Check `ConnectionManager` for active connections

### Switching LLM Backends
The system auto-detects available backends at runtime. Priority order:
1. Gemini (if `GOOGLE_API_KEY` set and valid)
2. Claude (if `ANTHROPIC_API_KEY` set and valid)
3. Ollama (default fallback, must be running on localhost:11434)

No code changes needed - just set/unset environment variables.

## State Management

### Conversation Memory
- **Short-term**: In-memory conversation history (current session)
- **Long-term**: Persistent storage via Memory Agent (`/core/terminator_memory.py`)
- **Context**: Context Awareness Agent tracks multi-turn conversations

### Agent State
Each agent maintains:
- Registration status with bus
- Message queue (asyncio.PriorityQueue)
- Local state (agent-specific)
- Health metrics (uptime, queries processed, errors)

### Data Storage Locations

**This Project (Terminator-Project):**
- **React build output**: `./terminator-web-terminal/dist/`
- **Agent modules**: `./core/`
- **Session settings**: `~/.terminator_cli_settings.json` (for Universal CLI)
- **Health checks**: `./.health_checks/`
- **Knowledge base**: `./.knowledge_base/`

**Full System** (57GB at `/Users/reeazmahmud/Desktop/Terminator/`):
- **Bus communication history**: `/Users/reeazmahmud/Desktop/Terminator/communication/data/`
- **Complete agent memory/state**: Managed by Memory Agent

**Note:** This Terminator-Project is a focused working copy. The full system with all historical data is at `/Users/reeazmahmud/Desktop/Terminator/`.

## Testing Strategy

### Running Tests

```bash
# Automated test runner (recommended)
./run-tests.sh              # Auto-detect and run all tests
./run-tests.sh --coverage   # With coverage report
./run-tests.sh -t test_auth # Run specific test pattern
./run-tests.sh --json       # JSON output for CI/CD

# Manual test discovery
python3 -m unittest discover tests

# System diagnostics via CLI
./terminator /healthCheck

# API health checks (when web terminal is running)
curl http://localhost:8000/status
curl http://localhost:8000/api/agents/health
```

**Test Location**: `/tests/` - Contains agent and integration tests

### Code Style
- **Python**: Follow PEP 8. Use `rich` for terminal output (not print statements).
- **React**: Functional components with hooks. No class components.
- **File Naming**: Agent files use `terminator_<agent_name>.py` pattern in `/core/`.

### Universal CLI Diagnostics
```bash
terminator
/healthCheck         # Complete system diagnostics
/agents              # List all agents and status
/tools               # List available tools
/connections         # Show platform connections
```

### Built-in Testing Agents
- **Testing Agent** - Validates core functionality
- **QA Agent** (`/core/terminator_qa_agent.py`) - Quality assurance
- **Code Quality Evaluator** - Reviews code changes

## Error Handling

Multi-layer error handling:
1. **Tool execution errors** - Caught in orchestrator, logged, fallback attempted
2. **Agent errors** - Error Monitor Agent detects and attempts recovery
3. **WebSocket errors** - ConnectionManager handles disconnects gracefully
4. **LLM errors** - Router falls back to alternative backend

All errors logged to `/core/terminator_safe_logging.py` with sensitive data filtering.

## File Modification Guidelines

### Never Modify
- `terminator_bridge.py` - WebSocket bridge is stable
- `terminator_agent_communication_bus.py` - Core messaging system
- Launch scripts (`start_*.sh`) unless adding new interface

### Modify with Caution
- Orchestrators - changes affect all agent interactions
- LLM router - impacts entire system intelligence
- Agent registration logic - can break message flow

### Safe to Modify
- Individual agent capabilities in `/core/terminator_*_agent.py`
- Web terminal UI in `/terminator-web-terminal/src/`
- Tool definitions and implementations
- Launch script parameters (ports, hosts)

## Performance Considerations

### High-Load Scenarios
- Bus uses PriorityQueues - messages auto-sorted by priority
- WebSocket broadcast is non-blocking (try/except per connection)
- Tool execution can be PARALLEL, SEQUENTIAL, or DEPENDENT
- LLM calls are async where possible

### Resource Management
- Connection pooling for database/external APIs handled by agents
- Resource Manager Agent (`/core/terminator_resource_manager_agent.py`) monitors usage
- Automatic cleanup of closed WebSocket connections

## Project Context & Related Documentation

**This Repository:** `/Users/reeazmahmud/Desktop/Terminator-Project`
- Focused working copy for active development
- Clean codebase without extensive history
- All core functionality and agents included

**Full System:** `/Users/reeazmahmud/Desktop/Terminator/` (57GB)
- Complete historical data and communication logs
- Full agent memory and state persistence
- Reference for deep architectural context

### Documentation Within This Project

**Getting Started:**
- `README.md` - User-facing guide with feature overview
- `START_HERE.md` - Quick start for new users
- `QUICK_START_CLI.txt` - Universal CLI quick reference
- `.cursorrules` - Development guidelines and context

**Architecture & Design:**
- `VISUAL_FRAMEWORK.md` - Complete system diagrams and flows
- `AGENT_ARCHITECTURE.md` - Agent design patterns
- `CLAUDE.md` (this file) - Claude Code guidance

**System Status & Planning:**
- `AGENT_HEALTH_REPORT.md` - Agent status and metrics
- `TERMINATOR_MASTER_PLAN.md` - Future development roadmap
- `SYSTEM_IMPLEMENTATION_SUMMARY.md` - What's been built

**Troubleshooting & Fixes:**
- `docs/troubleshooting/LLM_NOT_RESPONDING.md` - LLM integration issues
- `docs/fixes/FIX_001_*.md` - Documented bug fixes with lessons learned
- `core/agent_knowledge/llm_integration_patterns.py` - Learnable patterns

**Note:** If unclear about system architecture, check `VISUAL_FRAMEWORK.md` for diagrams or `.cursorrules` for quick context.

## Universal Platform Control

### Cross-Platform Architecture
TERMINATOR supports universal connectivity where every platform can control every other platform:

**Supported Platforms:**
- Terminal CLI (Universal CLI)
- iOS Native App
- Android Native App
- macOS Native App
- Web Interface
- MCP Servers

**Communication Pattern:**
```
Universal CLI → Agent Bus → Target Platform Agent → Target Device
```

**Example Commands:**
```bash
# From Universal CLI
terminator
/connectiOS                          # Establish iOS connection
/run ios get clipboard               # Get iPhone clipboard
/run android take screenshot         # Take Android screenshot
/run macos show notifications        # Show macOS notifications
/broadcast show system status        # Send to ALL platforms
/sync                               # Sync all connected platforms
```

### Inter-Project Communication
TERMINATOR can communicate with other desktop projects:
- **AI Dashboard** (`/Users/reeazmahmud/Desktop/AI`)
- **Main Terminator System** (`/Users/reeazmahmud/Desktop/Terminator`)
- **Eve Project** (`/Users/reeazmahmud/Desktop/Eve`)
- **ForgeCode** (`/Users/reeazmahmud/Desktop/ForgeCode`)

See `INTER_PROJECT_COMMUNICATION_BRIDGE.md` and `HOW_TO_USE_INTER_PROJECT_COMMUNICATION.md` for details.

## Key Design Principles

1. **Async-First**: All inter-agent communication uses asyncio
2. **Pub/Sub over RPC**: Agents don't call each other directly, they message via bus
3. **Priority-Based**: Critical messages jump the queue
4. **Autonomous Iteration**: Orchestrators can run multi-step research without user intervention
5. **Graceful Degradation**: System works offline (Ollama) or online (Gemini/Claude)
6. **Voice Optional**: All features work via text, voice is enhancement
7. **Multi-Interface**: Same backend serves web, terminal, and CLI frontends
8. **Universal Control**: Every platform can control every other platform through the agent bus

## Debugging and Troubleshooting

### LLM Not Responding

If any component shows "Processing..." but returns no response:

1. **Check Ollama is running:**
   ```bash
   pgrep -l ollama || ollama serve
   ```

2. **Test Ollama API directly:**
   ```bash
   curl -s http://localhost:11434/api/generate -d '{"model": "llama3", "prompt": "hi", "stream": false}'
   ```

3. **Run diagnostics:**
   ```bash
   python3 core/agent_knowledge/llm_integration_patterns.py
   ```

4. **Check documentation:**
   - `docs/troubleshooting/LLM_NOT_RESPONDING.md` - Full troubleshooting guide
   - `docs/fixes/FIX_001_LLM_INTEGRATION_UNIVERSAL_CLI.md` - Example fix

### Common Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| "Processing..." no response | LLM not integrated | Check code actually calls LLM API |
| "Cannot connect to Ollama" | Ollama not running | `ollama serve` |
| "Model not found" | Model not pulled | `ollama pull llama3` |
| Empty response | Wrong JSON path | Use `.get("message", {}).get("content")` |
| Port 8000 already in use | Previous instance running | `lsof -ti:8000 \| xargs kill` |
| React build not found | Not compiled | `cd terminator-web-terminal && npm install && npm run build` |
| WebSocket connection failed | Backend not running | Start with `./start_web_terminal.sh` |
| Import errors | Wrong Python version | Verify `python3 --version` >= 3.13 |
| Module not found | Dependencies not installed | `pip3 install -r requirements.txt` |

### Virtual Environments

The project has multiple virtual environments:
- `/venv/` - Python 3.14 environment (newer features)
- `/BanglaApp/venv/` - Separate environment for Bengali translation app

**Activation (if needed):**
```bash
source venv/bin/activate    # Activate main venv
deactivate                  # Deactivate when done
```

**Note:** Scripts typically use system Python 3. Only activate venv if encountering dependency issues.

## Agent Knowledge Base

Agents can learn from documented fixes and patterns:

### Knowledge Modules

Located in `/core/agent_knowledge/`:

- **`llm_integration_patterns.py`** - Working LLM integration code, diagnostics, and anti-patterns

### Using Knowledge Modules

```python
from core.agent_knowledge.llm_integration_patterns import (
    LLMIntegrationPattern,
    LLMDiagnostics,
    teach_agent_llm_integration
)

# Get working LLM client
llm = LLMIntegrationPattern()
response = llm.chat("Hello")

# Run diagnostics before operations
results = LLMDiagnostics.run_all_checks()

# Get learning summary
knowledge = teach_agent_llm_integration()
```

### Fix Documentation

All significant fixes are documented in `/docs/fixes/`:

- `FIX_001_LLM_INTEGRATION_UNIVERSAL_CLI.md` - Universal CLI LLM integration

Format: Problem → Root Cause → Solution → Lessons Learned

## Documentation Structure

```
docs/
├── fixes/                    # Documented bug fixes with lessons
│   └── FIX_001_*.md
├── troubleshooting/          # Issue-specific troubleshooting guides
│   └── LLM_NOT_RESPONDING.md
└── (future guides)

core/agent_knowledge/         # Learnable patterns for agents
└── llm_integration_patterns.py
```
