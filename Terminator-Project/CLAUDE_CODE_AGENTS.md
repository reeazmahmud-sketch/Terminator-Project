# Claude Code Agents & Sub-Agents Reference

> Complete list of all Claude Code (claude.ai/code) agents available in this system.
> Last updated: 2025-12-21

---

## Overview

Claude Code uses a **Task tool** to spawn specialized sub-agents for different purposes. Each agent runs autonomously and returns results to the main conversation. Agents can run in parallel for maximum efficiency.

---

## Core Agents

### 1. General-Purpose Agent
| Property | Value |
|----------|-------|
| **Type** | `general-purpose` |
| **Purpose** | Research complex questions, search for code, execute multi-step tasks |
| **Tools** | All tools available |
| **When to Use** | Open-ended searches, complex multi-file operations, tasks requiring multiple rounds of exploration |

**Example:**
```
"Find all API endpoints in this codebase and explain how authentication works"
```

---

### 2. Explore Agent
| Property | Value |
|----------|-------|
| **Type** | `Explore` |
| **Purpose** | Fast codebase exploration - find files, search code, answer architecture questions |
| **Tools** | All tools |
| **Thoroughness Levels** | `quick`, `medium`, `very thorough` |

**When to Use:**
- Find files by patterns (e.g., `src/components/**/*.tsx`)
- Search code for keywords (e.g., "API endpoints")
- Answer questions about codebase structure

**Example:**
```
"Find all React components that use the useAuth hook"
```

---

### 3. Plan Agent
| Property | Value |
|----------|-------|
| **Type** | `Plan` |
| **Purpose** | Software architect agent for designing implementation strategies |
| **Tools** | All tools |
| **Output** | Step-by-step plans, critical file identification, architectural trade-offs |

**When to Use:**
- Planning complex feature implementations
- Designing system architecture
- Evaluating multiple implementation approaches

**Example:**
```
"Plan the implementation of a real-time notification system"
```

---

## Specialized Agents

### 4. Claude Code Guide Agent
| Property | Value |
|----------|-------|
| **Type** | `claude-code-guide` |
| **Purpose** | Answer questions about Claude Code, Claude Agent SDK, and Claude API |
| **Tools** | Glob, Grep, Read, WebFetch, WebSearch |

**Handles Questions About:**
- Claude Code CLI features, hooks, slash commands
- MCP server configuration
- IDE integrations and keyboard shortcuts
- Claude Agent SDK for building custom agents
- Anthropic API usage and tool use

**Example:**
```
"How do I set up a custom slash command in Claude Code?"
```

---

### 5. Test Automation Expert
| Property | Value |
|----------|-------|
| **Type** | `test-automation-expert` |
| **Purpose** | Create comprehensive unit tests and run test suites |
| **Tools** | All tools |

**When to Use:**
- After new code is written or modified
- Feature implementation is complete
- Bug fixes need regression tests
- Test coverage gaps identified

**Example:**
```
"Write unit tests for the new validateToken function and run the test suite"
```

---

### 6. Debugging Specialist
| Property | Value |
|----------|-------|
| **Type** | `debugging-specialist` |
| **Purpose** | Diagnose and resolve errors, exceptions, and bugs |
| **Tools** | All tools |

**Handles:**
- Analyzing error logs and stack traces
- Investigating unexpected behavior
- Debugging failed tests
- Resolving runtime errors
- Troubleshooting integration issues

**Example:**
```
"Debug this WebSocket connection error: 'Event loop is closed'"
```

---

### 7. Code Reviewer
| Property | Value |
|----------|-------|
| **Type** | `code-reviewer` |
| **Purpose** | Review code for quality, security, and best practices |
| **Tools** | All tools |

**When to Use:**
- After implementing a new feature
- After fixing a bug
- After refactoring code
- Before committing significant changes

**Reviews For:**
- Security vulnerabilities
- Performance issues
- Code quality and maintainability
- Adherence to project standards

**Example:**
```
"Review the authentication module for security issues"
```

---

### 8. Shell Config Validator
| Property | Value |
|----------|-------|
| **Type** | `shell-config-validator` |
| **Purpose** | Validate shell configuration files for errors |
| **Tools** | All tools |

**Files It Validates:**
- `.zshrc`, `.bashrc`, `.bash_profile`
- Terminal scripts
- Shell-related configuration files

**When to Use:**
- After modifying shell config files
- Adding new aliases or PATH entries
- Creating shell scripts

**Example:**
```
"Validate my .zshrc after adding the new PATH entry"
```

---

### 9. Agent Monitor
| Property | Value |
|----------|-------|
| **Type** | `agent-monitor` |
| **Purpose** | Organize, monitor, and troubleshoot agent configurations |
| **Tools** | All tools |

**Capabilities:**
- Review agent definitions for errors
- Catalog existing agents
- Identify duplicate functionality
- Diagnose agent behavior issues

**Example:**
```
"Review all my agent configurations for inconsistencies"
```

---

## macOS-Specific Agents

### 10. macOS App Error Monitor
| Property | Value |
|----------|-------|
| **Type** | `macos-app-error-monitor` |
| **Purpose** | Continuous monitoring and remediation of macOS native app errors |
| **Tools** | All tools |
| **Target Apps** | Jarvis, AI & Agents Dashboard (`~/Desktop/AI`) |

**Monitors For:**
- Runtime errors and crashes
- Compilation issues
- Logic bugs
- Performance problems

**Example:**
```
"Monitor the Jarvis app for errors over the next hour"
```

---

### 11. macOS Shortcut Organizer
| Property | Value |
|----------|-------|
| **Type** | `macos-shortcut-organizer` |
| **Purpose** | Organize, document, and troubleshoot macOS keyboard shortcuts |
| **Tools** | All tools |

**Handles:**
- System shortcuts
- Application-specific shortcuts
- Custom shortcuts in System Settings
- Resolving shortcut conflicts

**Example:**
```
"Cmd+Shift+4 isn't working for screenshots - help me fix it"
```

---

## Configuration Agent

### 12. Statusline Setup Agent
| Property | Value |
|----------|-------|
| **Type** | `statusline-setup` |
| **Purpose** | Configure Claude Code status line settings |
| **Tools** | Read, Edit |

**Example:**
```
"Configure my Claude Code status line to show git branch"
```

---

## Agent Execution Patterns

### Running Agents in Parallel
Multiple independent agents can run simultaneously:
```
Task 1: Explore agent searching for auth files
Task 2: Code reviewer checking security
Task 3: Test automation writing tests
```

### Running Agents in Background
Agents can run in background while you continue working:
```python
run_in_background=True  # Agent runs async
TaskOutput(task_id)     # Retrieve results later
```

### Resuming Agents
Agents can be resumed with their full context preserved:
```python
resume="agent_id_from_previous_run"
```

---

## Quick Reference Table

| Agent | Type | Primary Use |
|-------|------|-------------|
| General-Purpose | `general-purpose` | Complex multi-step research |
| Explore | `Explore` | Fast codebase search |
| Plan | `Plan` | Architecture & implementation planning |
| Claude Code Guide | `claude-code-guide` | Claude Code/SDK/API questions |
| Test Automation | `test-automation-expert` | Write and run tests |
| Debugging | `debugging-specialist` | Error diagnosis & fixes |
| Code Reviewer | `code-reviewer` | Code quality review |
| Shell Validator | `shell-config-validator` | Shell config validation |
| Agent Monitor | `agent-monitor` | Agent config management |
| macOS Error Monitor | `macos-app-error-monitor` | macOS app monitoring |
| macOS Shortcuts | `macos-shortcut-organizer` | Keyboard shortcut help |
| Statusline Setup | `statusline-setup` | Status line config |

---

## Integration with TERMINATOR

These Claude Code agents complement the 38+ TERMINATOR agents in `/core/`.

**Key Difference:**
- **Claude Code Agents**: Run within Claude Code CLI sessions
- **TERMINATOR Agents**: Run via the Agent Communication Bus independently

**Synergy Example:**
1. Use `Explore` agent to understand codebase
2. Use `Plan` agent to design implementation
3. Write code with Claude Code
4. Use `code-reviewer` to check quality
5. Use `test-automation-expert` to write tests
6. Use TERMINATOR's `Test Runner Agent` to execute tests
7. TERMINATOR's Error Monitor Agent catches runtime issues

---

## TERMINATOR Native Agents (Complement Claude Code)

### Test Runner Agent
| Property | Value |
|----------|-------|
| **File** | `core/terminator_test_runner_agent.py` |
| **Purpose** | Execute test suites and analyze results |
| **CLI** | `./run-tests.sh` |

**Supported Frameworks:**
- Python: pytest, unittest
- JavaScript: Jest, Vitest, Mocha
- Go: go test
- Rust: cargo test
- npm test (auto-detects wrapper)

**Features:**
- Auto-detects test framework
- Parses output for failures
- Suggests fixes based on error patterns
- Coverage reporting support
- JSON output for CI/CD
- Integrates with Agent Communication Bus

**Usage:**
```bash
./run-tests.sh                    # Auto-detect and run
./run-tests.sh --coverage         # With coverage
./run-tests.sh -t "test_auth*"    # Pattern match
./run-tests.sh --json             # CI-friendly output
```

**Python API:**
```python
from core.terminator_test_runner_agent import TestRunnerAgent

agent = TestRunnerAgent()
result = await agent.run_tests(coverage=True)
print(agent.format_report(result))
```

---

### Claude Config Guardian
| Property | Value |
|----------|-------|
| **File** | `core/terminator_claude_config_guardian.py` |
| **Purpose** | Auto-fix Claude Code settings.json errors |
| **CLI** | `claude-check`, `claude-scan`, `claude-guard` |

**Features:**
- Validates `.claude/settings.json`
- Fixes common permission pattern errors
- Scans all projects in ~/Desktop
- Creates backup before changes

---

## See Also

- `CLAUDE.md` - Project-specific Claude Code instructions
- `core/terminator_agent_communication_bus.py` - TERMINATOR agent messaging
- `core/advanced_agentic_orchestrator.py` - Autonomous multi-step reasoning
- `core/terminator_test_runner_agent.py` - Test execution agent
- `core/terminator_claude_config_guardian.py` - Config validation agent
