# TERMINATOR Documentation Index

This document provides an index of all documentation, troubleshooting guides, and agent knowledge modules.

## Quick Links

| Need | Document |
|------|----------|
| LLM not working | [LLM_NOT_RESPONDING.md](troubleshooting/LLM_NOT_RESPONDING.md) |
| Universal CLI fix details | [FIX_001_LLM_INTEGRATION_UNIVERSAL_CLI.md](fixes/FIX_001_LLM_INTEGRATION_UNIVERSAL_CLI.md) |
| Agent integration patterns | [llm_integration_patterns.py](../core/agent_knowledge/llm_integration_patterns.py) |
| System overview | [CLAUDE.md](../CLAUDE.md) |

## Documentation Structure

```
Terminator-Project/
├── CLAUDE.md                          # Main system documentation
├── docs/
│   ├── DOCUMENTATION_INDEX.md         # This file
│   ├── fixes/                         # Documented bug fixes
│   │   └── FIX_001_*.md              # Individual fix documents
│   └── troubleshooting/               # Issue-specific guides
│       └── LLM_NOT_RESPONDING.md     # LLM connectivity issues
└── core/
    └── agent_knowledge/               # Agent-learnable modules
        ├── __init__.py
        └── llm_integration_patterns.py
```

## Fix Documents

Fix documents follow a standard format:
- **Problem Description**: What was happening
- **Root Cause Analysis**: Why it was happening
- **Solution Implemented**: Step-by-step fix
- **Verification**: How we confirmed it worked
- **Lessons Learned**: How to prevent similar issues

### Available Fix Documents

| ID | Title | Component | Date |
|----|-------|-----------|------|
| FIX-001 | [LLM Integration Universal CLI](fixes/FIX_001_LLM_INTEGRATION_UNIVERSAL_CLI.md) | `terminator_universal_cli.py` | 2024-12-18 |

## Troubleshooting Guides

Troubleshooting guides help diagnose and fix common issues:

| Guide | Description |
|-------|-------------|
| [LLM_NOT_RESPONDING.md](troubleshooting/LLM_NOT_RESPONDING.md) | LLM connectivity, empty responses, timeouts |

## Agent Knowledge Modules

Located in `/core/agent_knowledge/`, these Python modules contain patterns and utilities that agents can import and use:

### llm_integration_patterns.py

**Purpose**: Provide working LLM integration code and diagnostics

**Key Classes**:
- `LLMConfig` - Configuration constants for Ollama
- `LLMIntegrationPattern` - Working LLM client implementation
- `LLMDiagnostics` - Diagnostic utilities and health checks
- `LLMAntiPatterns` - Documented anti-patterns to avoid

**Usage**:
```python
from core.agent_knowledge import LLMIntegrationPattern, LLMDiagnostics

# Run diagnostics
LLMDiagnostics.print_diagnostics()

# Use working LLM client
llm = LLMIntegrationPattern(system_prompt="You are a helpful assistant.")
response = llm.chat("Hello!")
print(response)
```

**Run standalone**:
```bash
python3 core/agent_knowledge/llm_integration_patterns.py
```

## How Agents Learn From This

Agents can access this knowledge in several ways:

### 1. Import Python Modules
```python
from core.agent_knowledge import teach_agent_llm_integration
knowledge = teach_agent_llm_integration()
# Returns dict with key_points, reference_implementation, etc.
```

### 2. Read Documentation Files
Agents with file reading capabilities can parse:
- Markdown fix documents for lessons learned
- Troubleshooting guides for diagnostic steps
- Anti-patterns for what to avoid

### 3. Run Diagnostics
```python
from core.agent_knowledge import LLMDiagnostics
results = LLMDiagnostics.run_all_checks()
for r in results:
    if not r.passed:
        print(f"Issue: {r.check_name} - {r.message}")
```

## Contributing New Documentation

### Adding a Fix Document

1. Create file: `docs/fixes/FIX_XXX_DESCRIPTIVE_NAME.md`
2. Use the template from FIX-001
3. Include: Problem, Root Cause, Solution, Verification, Lessons
4. Update this index

### Adding a Troubleshooting Guide

1. Create file: `docs/troubleshooting/ISSUE_NAME.md`
2. Include: Quick diagnostic checklist, common issues/solutions, component-specific sections
3. Update this index

### Adding Agent Knowledge

1. Create module: `core/agent_knowledge/pattern_name.py`
2. Include working code examples
3. Document anti-patterns
4. Add `teach_agent_*()` function for summaries
5. Update `__init__.py` exports
6. Update this index

## Related Resources

- [CLAUDE.md](../CLAUDE.md) - Complete system documentation
- [README.md](../README.md) - User-facing guide
- [VISUAL_FRAMEWORK.md](../VISUAL_FRAMEWORK.md) - System diagrams
