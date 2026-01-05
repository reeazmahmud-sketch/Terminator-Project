# TerminalAI Agent Test Cases

**Test Suite Version:** 1.0
**Created:** 2025-11-16
**Total Test Cases:** 9 (covering all agents)
**Test Dashboard:** http://localhost:5002

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Test Cases Index](#test-cases-index)
3. [Running Tests](#running-tests)
4. [Test Dashboard](#test-dashboard)
5. [Test Steps Format](#test-steps-format)
6. [Reporting Results](#reporting-results)

---

## Overview

This directory contains comprehensive test cases for all TerminalAI agents. Each test case document includes detailed step-by-step instructions for testing individual agents and their integrations.

### Test Coverage:
- **7 Sub-Agents**: Individual functionality tests
- **1 Main Agent**: Routing and integration tests
- **1 Alaina GUI**: Interface and voice capability tests

### Test Types:
- **Functional Testing**: Core features verification
- **Integration Testing**: Agent-to-agent communication
- **Error Handling**: Resilience and stability
- **Syntax Validation**: Code quality checks

---

## Test Cases Index

### Sub-Agent Tests

| # | Test Case File | Agent | Purpose | Graduation | Tests |
|---|----------------|-------|---------|------------|-------|
| 001 | [TEST_CASE_001_AI_Terminal.md](TEST_CASE_001_AI_Terminal.md) | AI Terminal Agent | Executes terminal commands | 90% | 5 |
| 002 | [TEST_CASE_002_Bangla_Text_Processor.md](TEST_CASE_002_Bangla_Text_Processor.md) | Bangla Text Processor | Processes/summarizes Bangla text | 80% | 6 |
| 003 | [TEST_CASE_003_Smarter_Planner.md](TEST_CASE_003_Smarter_Planner.md) | Smarter Planner | Plans tasks, manages projects | 85% | 6 |
| 004 | [TEST_CASE_004_File_Organizer.md](TEST_CASE_004_File_Organizer.md) | File Organizer | Organizes files and folders | 70% | 6 |
| 005 | [TEST_CASE_005_Supervisor_Creator.md](TEST_CASE_005_Supervisor_Creator.md) | Supervisor Creator | Creates new supervisor agents | 75% | 7 |
| 006 | [TEST_CASE_006_The_Archivist.md](TEST_CASE_006_The_Archivist.md) | The Archivist | Archives and documents projects | 80% | 6 |
| 007 | [TEST_CASE_007_YouTube_Agent.md](TEST_CASE_007_YouTube_Agent.md) | YouTube Agent (TubeScribe) | Summarizes YouTube videos | 95% | 8 |

### Core System Tests

| # | Test Case File | Component | Purpose | Tests |
|---|----------------|-----------|---------|-------|
| 008 | [TEST_CASE_008_Main_Agent.md](TEST_CASE_008_Main_Agent.md) | Main Agent | Task routing and delegation | 7 |
| 009 | [TEST_CASE_009_Alaina_GUI.md](TEST_CASE_009_Alaina_GUI.md) | Alaina GUI | Supervisor interface with voice | 9 |

---

## Running Tests

### Manual Testing

Each test case can be run manually by following the step-by-step instructions in the markdown files:

```bash
# Open a test case
cat test_cases/TEST_CASE_001_AI_Terminal.md

# Follow the steps, marking checkboxes as you go:
# [ ] Pass [ ] Fail  →  [x] Pass [ ] Fail  (if passed)
```

### Using Test Dashboard

Launch the visual test dashboard to track progress:

```bash
# From project root
./Run\ Test\ Dashboard.command

# Or manually:
cd project_files/dashboard
/Users/reeazmahmud/terminalai/project_files/ai_env/bin/python test_dashboard.py

# Access at: http://localhost:5002
```

The dashboard provides:
- Real-time test status visualization
- Pass/fail statistics
- Progress tracking
- Individual test details

### Automated Testing

Run the comprehensive workflow test:

```bash
/Users/reeazmahmud/terminalai/project_files/ai_env/bin/python \
/Users/reeazmahmud/terminalai/test_agent_workflow.py
```

This automated script tests:
- Python environment
- Package imports
- Agent file existence
- Main agent dependencies
- Launcher commands

---

## Test Steps Format

Each test case follows this structure:

```markdown
## Test Case X.Y: Test Name

**Objective:** What this test verifies

**Prerequisites:**
- Required setup
- Dependencies
- Environmental conditions

**Test Steps:**

1. **Step 1:** Action to perform
   ```bash
   command to execute
   ```
   - **Expected Result:** What should happen
   - **Status:** [ ] Pass [ ] Fail

2. **Step 2:** Next action
   - **Input:** Data to provide
   - **Expected Result:** Expected outcome
   - **Status:** [ ] Pass [ ] Fail

**Expected Overall Result:** Summary of what success looks like

**Actual Result:** ___ (Fill in after testing)

**Pass/Fail:** [ ] Pass [ ] Fail
```

---

## Reporting Results

### During Testing

1. **Mark Checkboxes**: As you complete each step, mark it:
   - `[x] Pass` or `[X] Pass` for passing steps
   - `[x] Fail` or `[X] Fail` for failing steps

2. **Document Issues**: Fill in "Actual Result" fields with what actually happened

3. **Overall Assessment**: Mark the overall Pass/Fail for each test case

### After Testing

1. **Update Summary Section**: Fill in:
   ```markdown
   **Total Test Cases:** 6
   **Passed:** 5
   **Failed:** 1
   **Pass Rate:** 83.3%
   ```

2. **Document Critical Issues**:
   ```markdown
   **Critical Issues Found:**
   - Agent fails to start when Ollama is not running
   - File permissions error in /tmp/test_directory
   ```

3. **Add Recommendations**:
   ```markdown
   **Recommendations:**
   - Add better error messages for missing dependencies
   - Implement retry logic for network calls
   ```

4. **Sign Off**:
   ```markdown
   **Tested By:** Your Name
   **Date:** 2025-11-16
   **Sign-off:** Approved / Needs Review
   ```

---

## Test Statuses

- **✅ Passing**: All test steps completed successfully
- **❌ Failing**: One or more test steps failed
- **⏳ Not Run**: Test has not been executed yet
- **⚠️ Partial**: Some steps passed, investigation needed

---

## Test Environment

**Python Version:** 3.14.0 (ai_env)
**Virtual Environment:** `/Users/reeazmahmud/terminalai/project_files/ai_env`
**Platform:** macOS (Darwin 24.6.0)
**Required Services:** Ollama (for LLM features)

### Key Dependencies:
- langchain-ollama 1.0.0
- langchain-core 1.0.3
- Flask 3.1.2
- gTTS 2.5.4
- SpeechRecognition 3.14.3
- translators 6.0.1
- langdetect 1.0.9
- pytube 15.0.0

---

## Quick Reference

### Agent Locations

```
AI Terminal:          project_files/ai_terminal/ai-terminal.py
Bangla Processor:     project_files/terminalcontrol/bangla_text_processor/agent.py
Smarter Planner:      project_files/terminalcontrol/smarter_planner_agent/smart_agent.py
File Organizer:       project_files/terminalcontrol/file_organizer_agent/organizer_agent.py
Supervisor Creator:   project_files/terminalcontrol/Alaina_supervisor_creator_agent/creator_agent.py
The Archivist:        project_files/terminalcontrol/the_archivist_agent/the_archivist.py
YouTube Agent:        project_files/youtube_agent/agent.py
Main Agent:           project_files/terminalcontrol/main_agent/main_agent.py
Alaina GUI:           project_files/alaina_gui/gui.py
```

### Launchers

```
./Run\ AI\ Terminal.command
./Run\ Bangla\ Text\ Processor.command
./Run\ Smarter\ Planner\ Agent.command
./Run\ File\ Organizer.command
./Run\ Supervisor\ Creator\ Agent.command
./Run\ The\ Archivist.command
./Run\ Main\ Agent.command
./Run\ Alaina\ GUI\ \(Tkinter\).command
./Run\ Test\ Dashboard.command
```

---

## Support & Feedback

For issues or questions about the test cases:

1. Check the [BROKEN_VS_FIXED_REPORT.md](../BROKEN_VS_FIXED_REPORT.md) for known issues
2. Review the [FILE_ORGANIZATION_AUDIT_REPORT.md](../FILE_ORGANIZATION_AUDIT_REPORT.md) for system status
3. Consult [CLAUDE.md](../CLAUDE.md) for project documentation

---

**Last Updated:** 2025-11-16
**Test Suite Status:** ✅ Ready for Testing
**Dashboard Status:** ✅ Operational
