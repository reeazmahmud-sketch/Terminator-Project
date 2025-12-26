# TERMINATOR Agent Architecture

> Complete overview of the dual-layer agent system combining Claude Code subagents with TERMINATOR native agents.

---

## System Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                  │
│         (Web Terminal / Terminal UI / CLI / Universal CLI)                  │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MAIN ORCHESTRATOR AGENT                            │
│                    (Advanced Agentic Orchestrator)                          │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Plan      │  │   Delegate   │  │   Execute    │  │   Report     │     │
│  │   Tasks     │  │   to Agents  │  │   Tools      │  │   Results    │     │
│  └─────────────┘  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────┬────────────────┬────────────────┬────────────────┬─────────────────┘
         │                │                │                │
         ▼                ▼                ▼                ▼
┌─────────────┐  ┌─────────────────────────────────────┐  ┌─────────────────┐
│   Memory/   │  │         SUB-AGENT LAYER             │  │   Tool Layer    │
│   State     │  │                                     │  │                 │
│  Management │  │  Claude Code      TERMINATOR        │  │  • MCP Servers  │
│             │  │  Subagents        Native Agents     │  │  • Bash/Shell   │
│  • Context  │  │                                     │  │  • File System  │
│  • History  │  │  ┌────────────┐  ┌──────────────┐  │  │  • Web/API      │
│  • Learning │  │  │test-runner │  │Task Executor │  │  │  • iOS/Android  │
│             │  │  │code-review │  │Error Monitor │  │  │  • GitHub       │
└─────────────┘  │  │debugger    │  │Test Runner   │  │  └─────────────────┘
                 │  │shell-valid │  │Config Guard  │  │
                 │  │config-guard│  │Memory Agent  │  │
                 │  └────────────┘  └──────────────┘  │
                 │                                     │
                 │  ← Report Results to Orchestrator → │
                 └─────────────────────────────────────┘
```

---

## Two-Layer Agent System

### Layer 1: Claude Code Subagents
**Location:** `.claude/agents/` (project) and `~/.claude/agents/` (global)
**Format:** Markdown files with YAML frontmatter
**Execution:** Within Claude Code CLI sessions

### Layer 2: TERMINATOR Native Agents
**Location:** `core/terminator_*.py`
**Format:** Python modules with async support
**Execution:** Via Agent Communication Bus (standalone or with Claude Code)

---

## Claude Code Subagents

### Project-Level (Terminator-Project/.claude/agents/)

| Agent | File | Purpose |
|-------|------|---------|
| **test-runner** | `test-runner.md` | Run tests after code changes, fix failures |
| **code-reviewer** | `code-reviewer.md` | Security, performance, best practices review |
| **config-guardian** | `config-guardian.md` | Fix Claude Code settings.json errors |
| **debugger** | `debugger.md` | Diagnose errors and implement fixes |
| **shell-validator** | `shell-validator.md` | Validate .zshrc, .bashrc, shell scripts |

### Global/User-Level (~/.claude/agents/)

| Agent | File | Purpose |
|-------|------|---------|
| **project-scanner** | `project-scanner.md` | Scan all ~/Desktop projects for issues |
| **terminator-expert** | `terminator-expert.md` | Answer TERMINATOR architecture questions |
| **test-automation-expert** | `test-automation-expert.md` | Write comprehensive tests |
| **debugging-specialist** | `debugging-specialist.md` | Deep error analysis |
| **code-reviewer** | `code-reviewer.md` | Detailed code review |
| **shell-config-validator** | `shell-config-validator.md` | Shell config validation |
| **agent-monitor** | `agent-monitor.md` | Monitor agent configurations |
| **macos-app-error-monitor** | `macos-app-error-monitor.md` | macOS app monitoring |
| **macos-shortcut-organizer** | `macos-shortcut-organizer.md` | Keyboard shortcut management |

---

## TERMINATOR Native Agents

### Core Infrastructure Agents

| Agent | File | Purpose |
|-------|------|---------|
| Agent Communication Bus | `terminator_agent_communication_bus.py` | Central pub/sub messaging |
| Advanced Orchestrator | `advanced_agentic_orchestrator.py` | Multi-step autonomous reasoning |
| Simple Orchestrator | `terminator_agentic_orchestrator.py` | Single-shot tool calling |
| Decision Engine | `terminator_decision_engine.py` | Query routing |

### Execution Agents

| Agent | File | Purpose |
|-------|------|---------|
| Task Executor | `terminator_task_executor_agent.py` | Execute tasks with tools |
| Test Runner | `terminator_test_runner_agent.py` | Execute test suites |
| Config Guardian | `terminator_claude_config_guardian.py` | Fix Claude configs |

### Monitoring Agents

| Agent | File | Purpose |
|-------|------|---------|
| Error Monitor | `terminator_error_monitor_agent.py` | Detect and recover from errors |
| Sentinel | `terminator_sentinel_agent.py` | System watchdog |
| Infinite Loop Guardian | `terminator_infinite_loop_guardian_agent.py` | Prevent runaway processes |
| Resource Manager | `terminator_resource_manager_agent.py` | Monitor resource usage |

### Specialized Agents

| Agent | File | Purpose |
|-------|------|---------|
| Memory Agent | `terminator_memory_agent.py` | Persistent conversation memory |
| Context Awareness | `terminator_context_awareness_agent.py` | Multi-turn context tracking |
| QA Agent | `terminator_qa_agent.py` | Quality assurance |
| MCP Agent | `terminator_mcp_agent.py` | MCP server integration |
| Bengali Translation | `terminator_bengali_translation_agent.py` | Language translation |
| Market Analysis | `terminator_market_analysis_agent.py` | Market data analysis |
| Risk Assessment | `terminator_risk_assessment_agent.py` | Risk evaluation |

---

## Message Flow

```
User types in Web Terminal
    │
    ▼
WebSocket → terminator_bridge.py
    │
    ▼
Agent Communication Bus (pub/sub)
    │
    ├──→ Orchestrator receives message
    │       │
    │       ├──→ Analyzes query
    │       ├──→ Determines tools needed
    │       ├──→ Delegates to sub-agents
    │       │
    │       ▼
    │    Sub-agents execute
    │       │
    │       ▼
    │    Results returned to Orchestrator
    │       │
    │       ▼
    │    Orchestrator synthesizes answer
    │
    ▼
Response published to bus
    │
    ▼
Bridge forwards to WebSocket
    │
    ▼
Web Terminal displays response
```

---

## How They Work Together

### Example: "Build a web app feature"

1. **User Request** → Main Orchestrator

2. **Orchestrator Plans:**
   - Break down into subtasks
   - Identify which agents needed

3. **Delegate to Sub-Agents:**
   - `code-reviewer` (Claude Code) → Review existing code
   - `test-runner` (Claude Code) → Run existing tests
   - `Task Executor` (TERMINATOR) → Implement changes

4. **Tool Layer Execution:**
   - MCP servers for AI generation
   - Bash for shell commands
   - File system for code changes

5. **Sub-Agents Report Back:**
   - Results aggregated by Orchestrator
   - Confidence scoring applied

6. **Final Result** → User Interface

---

## Creating New Subagents

### Claude Code Subagent (Markdown)

```markdown
---
name: my-agent
description: When to use this agent
tools:
  - Bash
  - Read
  - Edit
---

You are a specialist in [domain].

## Your Responsibilities
1. ...
2. ...

## Workflow
1. First, do X
2. Then, do Y
3. Finally, do Z
```

Save to:
- `.claude/agents/my-agent.md` (project-specific)
- `~/.claude/agents/my-agent.md` (global)

### TERMINATOR Native Agent (Python)

```python
from core.terminator_agent_communication_bus import get_communication_bus

class MyAgent:
    AGENT_NAME = "my_agent"

    async def register(self):
        bus = get_communication_bus()
        await bus.register_agent_async(self.AGENT_NAME)

    async def listen(self):
        bus = get_communication_bus()
        while True:
            msg = await bus.get_message_async(self.AGENT_NAME, timeout=0.1)
            if msg:
                result = await self.process(msg)
                await bus.send_message_async(
                    sender_agent=self.AGENT_NAME,
                    recipient_agent=msg.sender,
                    subject="Response",
                    content=result
                )
```

Save to: `core/terminator_my_agent.py`

---

## Quick Commands

```bash
# Claude Code subagents
ls .claude/agents/          # Project-level agents
ls ~/.claude/agents/        # Global agents

# TERMINATOR agents
ls core/terminator_*_agent.py

# Test the test runner
./run-tests.sh

# Check Claude configs
claude-check
claude-scan

# Run TERMINATOR
./start_web_terminal.sh
```

---

## See Also

- `CLAUDE.md` - Full system documentation
- `CLAUDE_CODE_AGENTS.md` - Claude Code agent reference
- `VISUAL_FRAMEWORK.md` - Visual diagrams
