# TERMINATOR Real-World Test Suite

Comprehensive testing framework that validates TERMINATOR's capabilities through realistic user scenarios.

## Overview

Instead of unit tests, this suite tests **real-world tasks** that actual users would give to TERMINATOR:
- "Read this file and summarize it"
- "Fix the bug in my code"
- "Deploy this to GitHub"
- "Learn how to convert Markdown to PDF"

## Test Categories

### 1. File Operations & Code Management
- Reading and analyzing code
- Creating project structures
- Refactoring code
- **Tests:** File I/O, code understanding, editing

### 2. Web & Research Capabilities
- Searching for solutions online
- Learning new capabilities (YouTube, PDF, etc.)
- Finding latest documentation
- **Tests:** Web search, learning system, adaptation

### 3. Shell & System Operations
- Environment setup (venv, packages)
- System diagnostics
- Automation scripts
- **Tests:** Command execution, system integration

### 4. Git & GitHub Integration
- Committing changes with good messages
- Creating pull requests
- Resolving merge conflicts
- **Tests:** Git operations, GitHub API

### 5. Multi-Step Complex Tasks
- Debug and fix bugs
- Build and deploy pipelines
- Generate documentation
- **Tests:** Autonomous reasoning, multi-tool usage

### 6. Learning & Adaptation
- Detecting capability gaps
- Consulting external AIs
- Installing packages on-demand
- **Tests:** Meta-cognition, self-improvement

### 7. Platform Control
- iOS/Android integration
- Cross-platform sync
- **Tests:** Platform connectivity

### 8. Autonomous Decision Making
- Intelligent code review
- Error recovery
- **Tests:** Autonomous reasoning, adaptation

## Running Tests

### Quick Test (5 scenarios)
```bash
python3 tests/scenario_executor.py
```

### Full Test Suite (30+ scenarios)
```bash
python3 tests/real_world_scenarios.py
```

### Custom Scenario
```bash
python3 -c "
from tests.scenario_executor import ScenarioExecutor
executor = ScenarioExecutor()
result = executor.execute_scenario('Your custom request here')
print(result)
"
```

## Test Execution Flow

```
User Scenario
    ↓
Scenario Executor
    ↓
TERMINATOR CLI (with request)
    ↓
Capture Output
    ↓
Analyze Actions:
  - What tools were used?
  - Did TERMINATOR learn something?
  - Was task completed?
    ↓
Generate Report:
  - Success/Failure
  - Learning occurred
  - Execution time
  - Actions taken
```

## Evaluation Criteria

Each scenario is evaluated on:

1. **Task Completion** - Did TERMINATOR complete the request?
2. **Learning** - Did TERMINATOR learn a new capability when needed?
3. **Tool Usage** - Were appropriate tools used?
4. **Accuracy** - Is the output correct?
5. **Efficiency** - How long did it take?

## Results

Test results are saved to `test_results/scenarios/`:

```json
{
  "request": "Read README.md and tell me what this project does",
  "status": "success",
  "execution_time": 2.34,
  "tools_used": ["read_file"],
  "learned_capabilities": [],
  "actions_detected": ["read_file", "summarize"]
}
```

## Learning Metrics

The test suite tracks:
- **New capabilities learned** during testing
- **Most frequently used tools**
- **Success rate** (direct vs learned)
- **Adaptation speed** (how fast TERMINATOR learns)

## Example Output

```
Running: Read and Summarize Code
✓ File was read
✓ Summary provided
Status: success (2.1s)

Running: YouTube Video Summary
⚠ Capability gap detected: video content extraction
→ Learning from web...
→ Installing package: yt-dlp
✓ Task completed via learning
Status: learned (8.3s)

═══════════════════════════════════════
  Learning & Adaptation Report
═══════════════════════════════════════

✓ New Capabilities Learned:
  • youtube_extract
  • pdf_processing

Most Used Tools:
  • read_file: 12 times
  • web_search: 8 times
  • bash: 6 times

Overall Success Rate: 28/30 (93.3%)
  • Direct Success: 22
  • Success via Learning: 6
```

## Adding New Scenarios

Add to `real_world_scenarios.py`:

```python
RealWorldScenario(
    name="Your Scenario Name",
    description="What this tests",
    user_request="The actual user request",
    category="Category Name",
    required_capabilities=["tool1", "tool2"],
    expected_actions=["action1", "action2"],
    success_criteria=["criterion1", "criterion2"],
    difficulty="easy|medium|hard"
)
```

## Continuous Improvement

This test suite enables TERMINATOR to:
1. **Identify weak areas** (low success rate scenarios)
2. **Learn from failures** (adapt and retry)
3. **Build knowledge base** (save learned solutions)
4. **Track progress** (improvement over time)

## Integration with CI/CD

Run automated tests:
```bash
# In GitHub Actions, Jenkins, etc.
python3 tests/scenario_executor.py --automated --json-output
```

## Philosophy

**Traditional Testing:** "Does function X return Y?"
**Real-World Testing:** "Can TERMINATOR handle real user tasks?"

This approach tests:
- ✅ Actual use cases
- ✅ Learning ability
- ✅ Multi-step reasoning
- ✅ Autonomous adaptation

NOT just:
- ❌ Individual function outputs
- ❌ Mocked responses
- ❌ Isolated components

## Future Enhancements

- [ ] Benchmark performance over time
- [ ] Automated regression testing
- [ ] User scenario recording (learn from actual usage)
- [ ] Difficulty adjustment (adaptive testing)
- [ ] Multi-agent scenario testing
- [ ] Integration testing with iOS/Android apps
