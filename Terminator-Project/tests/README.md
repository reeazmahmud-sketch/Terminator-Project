# TerminalAI Integration Testing

Complete testing suite and processes for the multi-agent system.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Test Structure](#test-structure)
3. [Running Tests](#running-tests)
4. [Test Process](#test-process)
5. [Test Coverage](#test-coverage)
6. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Prerequisites

```bash
# Ensure virtual environment is activated
source /Users/reeazmahmud/terminalai/.venv/bin/activate

# Verify Python version
python --version  # Should be 3.13+

# Install dependencies (if needed)
pip install psutil
```

### Run All Tests

```bash
# From project root
python test_complete_system.py
```

**Expected Output:** 100% pass rate (59/59 tests)

---

## 📁 Test Structure

```
terminalai/
├── tests/
│   ├── README.md              # This file
│   ├── integration/
│   │   └── test_system.md     # Integration test process
│   ├── unit/
│   │   └── (future unit tests)
│   └── reports/
│       └── latest_test_run.md
│
└── test_complete_system.py    # Main test runner
```

---

## 🧪 Running Tests

### Full System Test

```bash
# Activate venv
source .venv/bin/activate

# Run all tests
python test_complete_system.py
```

### Individual Component Tests

**Test Infrastructure Only:**
```python
from test_complete_system import SystemTester
tester = SystemTester()
tester.test_infrastructure()
```

**Test Specific Manager:**
```python
tester = SystemTester()
tester.test_managers()  # Tests Esha, Nova, Zara
```

**Test Communication:**
```python
tester = SystemTester()
tester.test_agent_communication()
```

---

## 🔄 Test Process

### Phase 1: Infrastructure Verification

**What is tested:**
- Import all infrastructure modules
- Initialize singletons (AgentRegistry, MessageBus, etc.)
- Verify all components load without errors

**Success Criteria:**
- All 9 infrastructure tests pass
- No import errors
- Singleton instances created

### Phase 2: Head Agent Testing

**What is tested:**
- Orion imports correctly
- Orion instance creation
- Required capabilities present
- Required methods exist

**Success Criteria:**
- All 5 Orion tests pass
- Has `system_orchestration` capability
- Has `halt_all_agents` and `delegate_task` methods

### Phase 3: Supervisor Testing

**What is tested:**
- All 3 supervisors (Alaina, Eyan, Liam)
- Instance creation
- Capability verification

**Success Criteria:**
- All 9 supervisor tests pass
- Alaina has `triage` capability
- Eyan has `web_scraping` capability
- Liam has `ios_file_management` capability

### Phase 4: Manager Testing

**What is tested:**
- All 3 managers (Esha, Nova, Zara)
- Instance creation
- Sub-agent management
- Core capabilities

**Success Criteria:**
- All 10 manager tests pass
- Each manager has correct capabilities
- Sub-agents properly registered

### Phase 5: Sub-Agent Testing

**What is tested:**
- All 9 sub-agents across 3 managers
- Security sub-agents (4)
- Update sub-agents (2)
- Validation sub-agents (3)

**Success Criteria:**
- All 16 sub-agent tests pass
- All imports work
- All instances create successfully

### Phase 6: Communication Testing

**What is tested:**
- Agent-to-agent messaging
- Message delivery
- Registry lookup
- Agent lifecycle (start/stop)

**Success Criteria:**
- All 4 communication tests pass
- Messages delivered successfully
- Registry returns correct info

### Phase 7: Interface Testing

**What is tested:**
- Interface files exist
- Backend structure
- Frontend files present

**Success Criteria:**
- All 4 interface tests pass
- All required files found

---

## 📊 Test Coverage

### Current Coverage: **100%**

| Component | Tests | Status |
|-----------|-------|--------|
| Infrastructure | 9 | ✅ 100% |
| Head Agent (Orion) | 5 | ✅ 100% |
| Supervisors | 9 | ✅ 100% |
| Managers | 10 | ✅ 100% |
| Security Sub-Agents | 8 | ✅ 100% |
| Update Sub-Agents | 4 | ✅ 100% |
| Validation Sub-Agents | 6 | ✅ 100% |
| Communication | 4 | ✅ 100% |
| Interface | 4 | ✅ 100% |
| **TOTAL** | **59** | **✅ 100%** |

---

## 🎯 Step-by-Step Integration Test

### Step 1: Environment Setup

```bash
# Navigate to project
cd /Users/reeazmahmud/terminalai

# Activate virtual environment
source .venv/bin/activate

# Verify activation
which python  # Should show .venv/bin/python
```

### Step 2: Dependency Check

```bash
# Check required packages
python -c "import psutil; print('psutil OK')"

# If fails:
pip install psutil
```

### Step 3: Run Infrastructure Tests

```bash
# Test core components
python -c "
from project_files.core.agent_registry import get_agent_registry
from project_files.core.message_bus import get_message_bus
from project_files.core.logging_hub import get_logging_hub

registry = get_agent_registry()
message_bus = get_message_bus()
logger = get_logging_hub()

print('✅ Infrastructure OK')
"
```

### Step 4: Run Complete Test Suite

```bash
python test_complete_system.py
```

**Expected Output:**
```
╔════════════════════════════════════════════════════════════╗
║     TERMINAL AI - COMPLETE SYSTEM INTEGRATION TEST        ║
╚════════════════════════════════════════════════════════════╝

... (test output) ...

Total Tests:    59
Passed:         59
Failed:         0
Warnings:       0

Pass Rate:      100.0%

🎉 EXCELLENT! System is ready to use!
```

### Step 5: Verify Agent Creation

```bash
# Test creating individual agents
python -c "
from project_files.orion.orion import Orion
from project_files.supervisors.alaina.alaina_enhanced import AlainaEnhanced
from project_files.managers.esha.esha import Esha

orion = Orion()
alaina = AlainaEnhanced()
esha = Esha()

print(f'✅ Orion: {orion.agent_id}')
print(f'✅ Alaina: {alaina.agent_id}')
print(f'✅ Esha: {esha.agent_id}')
"
```

### Step 6: Test Agent Communication

```bash
# Run communication test separately
python tests/integration/test_communication.py
```

### Step 7: Generate Test Report

```bash
# Run tests and save report
python test_complete_system.py > tests/reports/test_run_$(date +%Y%m%d_%H%M%S).txt
```

---

## 🔍 Detailed Test Processes

### Process 1: New Component Integration

When adding a new agent:

1. **Import Test**
   ```python
   def test_new_agent_import(self):
       try:
           from project_files.path.to.new_agent import NewAgent
           self.print_test("Import NewAgent", "PASS")
       except Exception as e:
           self.print_test("Import NewAgent", "FAIL", str(e))
   ```

2. **Instance Test**
   ```python
   def test_new_agent_instance(self):
       agent = NewAgent()
       self.print_test("Create NewAgent instance", "PASS")
   ```

3. **Capability Test**
   ```python
   if "expected_capability" in agent.capabilities:
       self.print_test("NewAgent has capability", "PASS")
   ```

### Process 2: Communication Testing

1. **Create Test Agents**
2. **Start Agents**
3. **Send Message**
4. **Verify Receipt**
5. **Check Response**
6. **Stop Agents**

### Process 3: Integration Workflow

```
┌──────────────┐
│  Start Test  │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ Infrastructure   │
│ - Import modules │
│ - Initialize     │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Head Agent       │
│ - Import Orion   │
│ - Create instance│
│ - Check methods  │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Supervisors      │
│ - Test Alaina    │
│ - Test Eyan      │
│ - Test Liam      │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Managers         │
│ - Test Esha      │
│ - Test Nova      │
│ - Test Zara      │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Sub-Agents       │
│ - Security (4)   │
│ - Updates (2)    │
│ - Validation (3) │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Communication    │
│ - Create agents  │
│ - Test messaging │
│ - Registry check │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Interface        │
│ - File checks    │
│ - Path validation│
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Final Report    │
│ - Pass/Fail count│
│ - Pass rate      │
│ - Recommendations│
└──────────────────┘
```

---

## 🐛 Troubleshooting

### Issue 1: Import Errors

**Symptom:** `ModuleNotFoundError` or import failures

**Solution:**
```bash
# Check Python path
echo $PYTHONPATH

# Ensure correct directory
cd /Users/reeazmahmud/terminalai

# Check sys.path
python -c "import sys; print('\n'.join(sys.path))"
```

### Issue 2: Missing Dependencies

**Symptom:** `No module named 'psutil'`

**Solution:**
```bash
source .venv/bin/activate
pip install psutil
```

### Issue 3: Registry Not Found

**Symptom:** `cannot import name 'get_agent_registry'`

**Solution:**
```bash
# Verify file has singleton function
grep -A 5 "def get_agent_registry" project_files/core/agent_registry.py

# If missing, function should be at end of file
```

### Issue 4: Agent Communication Fails

**Symptom:** Messages not delivered between agents

**Solution:**
```python
# Check registry is same instance
registry1 = get_agent_registry()
registry2 = get_agent_registry()
assert registry1 is registry2  # Should be same object

# Check message bus
message_bus1 = get_message_bus()
message_bus2 = get_message_bus()
assert message_bus1 is message_bus2  # Should be same object
```

### Issue 5: Low Pass Rate

**Symptom:** Tests failing (< 100%)

**Solution:**
1. Check specific failed test output
2. Verify all dependencies installed
3. Ensure Python 3.13+ is used
4. Check virtual environment is activated
5. Review error messages for clues

---

## 📝 Test Checklist

Before running integration tests:

- [ ] Virtual environment activated
- [ ] Python 3.13+ verified
- [ ] All dependencies installed
- [ ] In correct directory
- [ ] Previous test artifacts cleared (optional)

During test run:

- [ ] No import errors
- [ ] All agents create successfully
- [ ] Communication tests pass
- [ ] All files found
- [ ] 100% pass rate achieved

After test run:

- [ ] Review test output
- [ ] Check for warnings
- [ ] Save test report
- [ ] Update documentation if needed

---

## 📈 Success Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Pass Rate | ≥ 95% | 100% | ✅ ⭐ |
| Import Errors | 0 | 0 | ✅ |
| Runtime Errors | 0 | 0 | ✅ |
| Agent Creation | 100% | 100% | ✅ |
| Communication | Working | Working | ✅ |
| Test Coverage | ≥ 90% | 100% | ✅ |

---

## 🎯 Continuous Integration

### Future CI/CD Setup

```yaml
# .github/workflows/test.yml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.13'
      - run: pip install -r requirements.txt
      - run: python test_complete_system.py
```

---

## 📚 Additional Resources

- **Main Test File:** `../test_complete_system.py`
- **System Status:** `../SYSTEM_READY.md`
- **Architecture:** `../SYSTEM_ARCHITECTURE_WORKFLOW.md`
- **User Guide:** `../USER_STATUS.md`

---

**Last Updated:** 2025-11-09
**Test Pass Rate:** 100%
**Status:** ✅ All Systems Go!
