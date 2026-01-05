# Complete Agentic System Architecture

> Full implementation of the Claude Agent architecture across TERMINATOR and Claude Code.

---

## The Four Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│    ┌─────────────────┐                           ┌─────────────────┐        │
│    │   CLI AGENT     │                           │  TOOLS & MCP    │        │
│    │   (The Body)    │                           │  (The Hands)    │        │
│    │                 │                           │                 │        │
│    │ • File access   │                           │ • Bash/Shell    │        │
│    │ • Command exec  │◄─────────────────────────►│ • File R/W      │        │
│    │ • Output capture│                           │ • Web/API       │        │
│    │ • Permissions   │                           │ • MCP Servers   │        │
│    └────────┬────────┘                           └────────┬────────┘        │
│             │                                             │                 │
│             │         ┌─────────────────────┐             │                 │
│             │         │  MAIN ORCHESTRATOR  │             │                 │
│             └────────►│    (The Brain)      │◄────────────┘                 │
│                       │                     │                               │
│                       │ • Decompose goals   │                               │
│                       │ • Manage state      │                               │
│                       │ • Delegate tasks    │                               │
│                       │ • Synthesize results│                               │
│                       └──────────┬──────────┘                               │
│                                  │                                          │
│                    ┌─────────────┼─────────────┐                            │
│                    │             │             │                            │
│                    ▼             ▼             ▼                            │
│             ┌───────────┐ ┌───────────┐ ┌───────────┐                       │
│             │ SUB-AGENT │ │ SUB-AGENT │ │ SUB-AGENT │                       │
│             │ Frontend  │ │ Security  │ │ Testing   │                       │
│             │           │ │           │ │           │                       │
│             │ Fresh     │ │ Fresh     │ │ Fresh     │                       │
│             │ Context   │ │ Context   │ │ Context   │                       │
│             └───────────┘ └───────────┘ └───────────┘                       │
│                                                                             │
│                         (The Specialists)                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component 1: CLI Agent (The Body)

### Implementation

| System | File | Description |
|--------|------|-------------|
| **TERMINATOR** | `terminator_bridge.py` | WebSocket bridge to agent bus |
| **TERMINATOR** | `terminator.py` | Direct CLI interface |
| **TERMINATOR** | `terminator_universal_cli.py` | Universal CLI with slash commands |
| **Claude Code** | Built-in | The `claude` command itself |

### Capabilities

```python
# The CLI Agent can:

# 1. Read/Write Files
await tools.execute(ToolType.FILE_READ, "src/main.py")
await tools.execute(ToolType.FILE_WRITE, "output.txt", content=data)

# 2. Run Terminal Commands
await tools.execute(ToolType.BASH, "npm install")

# 3. Capture Output (for self-correction)
result = await tools.execute(ToolType.BASH, "npm test")
if not result.success:
    # Feed error back to brain for fixing
    await orchestrator.fix_error(result.error)
```

### The Sense → Think → Act Loop

```
┌──────────────────────────────────────────────────────────────┐
│                     CLI AGENT LOOP                           │
│                                                              │
│   ┌─────────┐     ┌─────────┐     ┌─────────┐               │
│   │  SENSE  │────►│  THINK  │────►│   ACT   │───┐           │
│   │         │     │         │     │         │   │           │
│   │ Read    │     │ Send to │     │ Execute │   │           │
│   │ files,  │     │ Claude  │     │ tool    │   │           │
│   │ check   │     │ "What   │     │ command │   │           │
│   │ state   │     │ next?"  │     │         │   │           │
│   └─────────┘     └─────────┘     └─────────┘   │           │
│        ▲                                        │           │
│        │                                        │           │
│        └────────────────────────────────────────┘           │
│                     (Loop continues)                        │
└──────────────────────────────────────────────────────────────┘
```

---

## Component 2: Main Orchestrator (The Brain)

### Implementation

| System | File | Description |
|--------|------|-------------|
| **TERMINATOR** | `core/terminator_agentic_system.py` | Full Python orchestrator |
| **TERMINATOR** | `core/advanced_agentic_orchestrator.py` | Multi-step reasoning |
| **Claude Code** | `~/.claude/agents/orchestrator.md` | Orchestrator subagent |
| **Claude Code** | `~/.claude/agents/state-manager.md` | State persistence |

### The Four Phases

```python
class AgenticSystem:
    async def orchestrate(self, goal: str):

        # PHASE 1: DECOMPOSE
        # Break "Build auth system" into steps
        plan = await self._create_plan(goal)
        # Result: ["Design flow", "Create model", "Implement routes", "Write tests"]

        # PHASE 2: STATE MANAGEMENT
        # Save progress for crash recovery
        self.project_state = {
            "goal": goal,
            "plan": plan,
            "completed": [],
            "current": 0
        }
        await self.save_state()

        # PHASE 3: DELEGATE
        # Send tasks to specialists (with FRESH context each)
        security_report = await self.sub_agents.spawn(
            "Audit this auth design",
            AgentRole.SECURITY_ENGINEER
        )

        # PHASE 4: SYNTHESIZE
        # Combine all results, check against original goal
        final = await self.synthesize(goal, all_results)
        if not meets_goal(final):
            return await self.retry_failed_tasks()

        return final
```

### State File Structure

```json
// .orchestrator_state.json
{
  "goal": "Build REST API with authentication",
  "plan": {
    "steps": [
      {"id": 1, "task": "Design auth flow", "status": "completed"},
      {"id": 2, "task": "Create User model", "status": "in_progress"},
      {"id": 3, "task": "Implement routes", "status": "pending"}
    ],
    "current_step": 2
  },
  "context": {
    "tech_stack": "Node.js + Express",
    "decisions": ["Using JWT", "PostgreSQL database"]
  }
}
```

---

## Component 3: Sub-Agents (The Specialists)

### Implementation

| System | Location | Count |
|--------|----------|-------|
| **TERMINATOR** | `core/terminator_*_agent.py` | 40+ agents |
| **Claude Code** | `~/.claude/agents/*.md` | 22 agents |
| **Claude Code** | `.claude/agents/*.md` | 5 project agents |

### Why Sub-Agents Work

```
┌────────────────────────────────────────────────────────────────┐
│                    CONTEXT POLLUTION                           │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  WITHOUT Sub-Agents:                                           │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Context Window (128K tokens)                             │ │
│  │                                                          │ │
│  │ [Old CSS] [Failed attempt] [Debug logs] [Irrelevant     │ │
│  │ code] [Discarded ideas] [Previous errors] [Random       │ │
│  │ tangents] [User chat history] [More old stuff]...       │ │
│  │                                                          │ │
│  │ AI: *confused* *hallucinating* *making mistakes*        │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  WITH Sub-Agents:                                              │
│  ┌─────────────────────┐                                       │
│  │ FRESH Context       │                                       │
│  │                     │                                       │
│  │ Task: "Fix auth.py" │                                       │
│  │ File: [auth.py]     │                                       │
│  │                     │                                       │
│  │ AI: *focused*       │                                       │
│  │     *accurate*      │                                       │
│  │     *fast*          │                                       │
│  └─────────────────────┘                                       │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Sub-Agent Categories

```
SPECIALISTS (Do the work)
├── frontend-specialist    → React, CSS, UI
├── backend-specialist     → APIs, databases
├── security-specialist    → Auth, vulnerabilities
├── test-specialist        → Unit tests, coverage
├── devops-specialist      → Docker, CI/CD
└── docs-specialist        → README, API docs

AGGRESSIVE REVIEWERS (Specialized prompts)
├── security-redteam       → "Think like a hacker"
├── performance-critic     → "Find every bottleneck"
├── code-nitpicker        → "Catch every typo"
└── quick-fixer           → "Fix one bug, fast"

COORDINATORS
├── orchestrator          → The PM brain
├── parallel-coordinator  → Spawn multiple agents
└── state-manager         → Track progress
```

### Parallel Processing

```python
# Sequential (Slow): 90 seconds
await security_check()    # 30s
await write_tests()       # 30s
await write_docs()        # 30s

# Parallel (Fast): 30 seconds
await asyncio.gather(
    security_check(),     # 30s ─┐
    write_tests(),        # 30s ─┼─ All run together
    write_docs()          # 30s ─┘
)
```

---

## Component 4: Tools & MCP (The Hands)

### Implementation

| System | File | Description |
|--------|------|-------------|
| **TERMINATOR** | `core/terminator_agentic_system.py` | ToolHarness class |
| **TERMINATOR** | `core/mcp_client.py` | MCP integration |
| **TERMINATOR** | `core/terminator_mcp_agent.py` | MCP agent |
| **Claude Code** | Built-in tools | Bash, Read, Write, Edit, etc. |

### Tool Types

```python
class ToolType(Enum):
    # FILE SYSTEM (Senses)
    FILE_READ = "file_read"      # See file contents
    FILE_WRITE = "file_write"    # Create/modify files
    GLOB = "glob"                # Find files by pattern
    GREP = "grep"                # Search within files

    # EXECUTION (Hands)
    BASH = "bash"                # Run commands

    # EXTERNAL (Extended Senses)
    WEB_FETCH = "web_fetch"      # Read web pages
    WEB_SEARCH = "web_search"    # Search the internet

    # MCP (Universal Connector)
    MCP = "mcp"                  # Any MCP server
```

### How Tools Work

```
┌─────────────────────────────────────────────────────────────┐
│                    TOOL EXECUTION FLOW                      │
│                                                             │
│  Claude thinks: "I need to see what's in config.json"       │
│                                                             │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Claude outputs structured command:                 │   │
│  │  {                                                  │   │
│  │    "tool": "file_read",                            │   │
│  │    "path": "config.json"                           │   │
│  │  }                                                  │   │
│  └─────────────────────────────────────────────────────┘   │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  CLI Agent intercepts, runs actual code:            │   │
│  │                                                     │   │
│  │  with open("config.json") as f:                     │   │
│  │      content = f.read()                             │   │
│  └─────────────────────────────────────────────────────┘   │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Result sent back to Claude:                        │   │
│  │                                                     │   │
│  │  "Here's the content of config.json: {...}"         │   │
│  │                                                     │   │
│  │  Claude continues thinking with new information     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### MCP - Universal Connector

```
BEFORE MCP (Custom code for everything):
┌────────────┐   ┌────────────┐   ┌────────────┐
│  Google    │   │   Jira     │   │   Local    │
│  Calendar  │   │  Tickets   │   │   Files    │
└─────┬──────┘   └─────┬──────┘   └─────┬──────┘
      │                │                │
      ▼                ▼                ▼
┌──────────┐    ┌──────────┐    ┌──────────┐
│ Custom   │    │ Custom   │    │ Custom   │
│ Code #1  │    │ Code #2  │    │ Code #3  │
└──────────┘    └──────────┘    └──────────┘
      │                │                │
      └────────────────┼────────────────┘
                       ▼
                  ┌─────────┐
                  │  Agent  │
                  └─────────┘


AFTER MCP (Universal protocol):
┌────────────┐   ┌────────────┐   ┌────────────┐
│  Google    │   │   Jira     │   │   Local    │
│  Calendar  │   │  Tickets   │   │   Files    │
└─────┬──────┘   └─────┬──────┘   └─────┬──────┘
      │                │                │
      ▼                ▼                ▼
┌─────────────────────────────────────────────┐
│              MCP SERVER                      │
│         (One universal connector)            │
└─────────────────────┬───────────────────────┘
                      │
                      ▼
                 ┌─────────┐
                 │  Agent  │
                 └─────────┘
```

### TERMINATOR MCP Integration

```python
# Available MCP Servers (Vertex AI Creative Studio)
MCP_SERVERS = {
    "imagen": 9000,  # Image generation
    "veo": 9001,     # Video creation
    "chirp": 9002,   # Speech synthesis
    "lyria": 9003,   # Music generation
    "avtool": 9004   # Audio/video compositing
}

# Usage
await mcp_client.connect("imagen")
result = await mcp_client.call("generate", prompt="A sunset over mountains")
```

### Safety Layer

```
┌─────────────────────────────────────────────────────────────┐
│                     SAFETY MECHANISMS                        │
│                                                             │
│  1. READ-ONLY TOOLS                                         │
│     └─ Can see files but not delete them                    │
│                                                             │
│  2. PERMISSION PROMPTS                                      │
│     ┌──────────────────────────────────────────────────┐   │
│     │  Claude wants to run:                            │   │
│     │  rm -rf ./temp                                   │   │
│     │                                                  │   │
│     │  [Allow]  [Deny]  [Allow for this session]      │   │
│     └──────────────────────────────────────────────────┘   │
│                                                             │
│  3. SANDBOXING                                              │
│     └─ Commands run in isolated environment                 │
│                                                             │
│  4. ALLOWLIST (.claude/settings.json)                       │
│     {                                                       │
│       "permissions": {                                      │
│         "allow": ["Bash(git:*)", "Read"],                  │
│         "deny": ["Bash(rm -rf:*)"]                         │
│       }                                                     │
│     }                                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Complete System Summary

| Component | Role | TERMINATOR | Claude Code |
|-----------|------|------------|-------------|
| **CLI Agent** | The Body | `terminator_bridge.py` | `claude` CLI |
| **Orchestrator** | The Brain | `terminator_agentic_system.py` | `orchestrator.md` |
| **Sub-Agents** | Specialists | 40+ Python agents | 22 markdown agents |
| **Tools & MCP** | The Hands | `ToolHarness` + `mcp_client.py` | Built-in tools |

---

## Quick Start

### TERMINATOR
```bash
./run-agent.sh "Build a REST API with authentication"
```

### Claude Code
```
Use the orchestrator agent to build a complete authentication system.
```

---

## Files Reference

```
TERMINATOR (Python-based)
├── core/
│   ├── terminator_agentic_system.py      # Full orchestrator
│   ├── terminator_agent_communication_bus.py
│   ├── terminator_test_runner_agent.py
│   ├── terminator_claude_config_guardian.py
│   ├── mcp_client.py
│   └── 40+ more agents...
├── run-agent.sh
├── run-tests.sh
└── claude-guard.sh

CLAUDE CODE (Markdown-based)
├── ~/.claude/
│   ├── AGENTS_REFERENCE.md
│   └── agents/
│       ├── orchestrator.md
│       ├── state-manager.md
│       ├── parallel-coordinator.md
│       ├── frontend-specialist.md
│       ├── backend-specialist.md
│       ├── security-specialist.md
│       ├── security-redteam.md
│       ├── performance-critic.md
│       ├── code-nitpicker.md
│       ├── quick-fixer.md
│       └── 12 more...
└── .claude/agents/
    └── (project-specific agents)
```

---

## The Complete Picture

```
                         YOU (Human)
                             │
                             │ "Build me a weather app"
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLI AGENT (The Body)                              │
│                    Permissions │ Safety │ Sandboxing                        │
└─────────────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATOR (The Brain)                             │
│                                                                             │
│   1. DECOMPOSE: Weather app → [API, UI, Logic, Tests]                       │
│   2. STATE: Save progress to .orchestrator_state.json                       │
│   3. DELEGATE: Send tasks to specialists                                    │
│   4. SYNTHESIZE: Combine results, verify against goal                       │
│                                                                             │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
    ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
    │   SUB-AGENT      │ │   SUB-AGENT      │ │   SUB-AGENT      │
    │   Frontend       │ │   Backend        │ │   Security       │
    │   (Fresh Ctx)    │ │   (Fresh Ctx)    │ │   (Red Team)     │
    └────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TOOLS & MCP (The Hands)                             │
│                                                                             │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│   │    Bash     │  │  File R/W   │  │  Web/API    │  │    MCP      │       │
│   │   Execute   │  │   Access    │  │   Fetch     │  │  Servers    │       │
│   └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
                           WEATHER APP ✅
```

---

**The complete Claude Agent architecture is now implemented!** 🚀
