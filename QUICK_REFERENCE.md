# TERMINATOR Multi-Agent System - Quick Reference

## 🚀 Quick Start (30 Seconds)

```bash
# See the system in action
./start_demo.sh

# Or take control yourself
./start_command_center.sh
```

## 📋 Essential Commands

### Task Management
```bash
# Create main task
/create-task <title> | <description> | <agents> | <priority> | <duration>

# Create sub-task
/create-subtask <parent_id> | <title> | <description> | <agents> | <duration>

# Assign task to agents
/assign <task_id>

# Start task
/start <task_id> <agent_name>

# Update progress (0-100)
/progress <task_id> <percent> [note]

# Complete task
/complete <task_id> <agent_name>
```

### Monitoring
```bash
# Show all tasks
/status

# Show specific task
/status <task_id>

# Show all agents
/agents

# Show specific agent
/agents <agent_name>

# Live monitoring (auto-refresh)
/monitor
```

### Reports
```bash
# Generate report
/report <task_id>

# Generate and save to custom location
/report <task_id> /path/to/report.json

# Show report summary
/reports
```

### System
```bash
/available  # List all agents
/bus        # Show communication bus status
/help       # Show all commands
/quit       # Exit
```

## 📝 Example Workflow

```bash
# 1. Start Command Center
./start_command_center.sh

# 2. Create a task
/create-task System Audit | Full codebase audit | qa_agent,context_awareness_agent | high | 180
# Output: task_1734400000_1234

# 3. Create sub-tasks
/create-subtask task_1734400000_1234 | Check Core | Review core modules | qa_agent | 60
/create-subtask task_1734400000_1234 | Check Tests | Review test coverage | qa_agent | 60

# 4. Assign and start
/assign task_1734400000_1234
/start task_1734400000_1234 qa_agent

# 5. Monitor live
/monitor
# Press Ctrl+C to pause monitoring

# 6. Update progress (as work proceeds)
/progress task_1734400000_1234 50 Halfway complete

# 7. Complete task
/complete task_1734400000_1234 qa_agent

# 8. Generate report
/report task_1734400000_1234 /path/to/my_audit_report.json
```

## 🎓 Key Concepts

### Task Hierarchy
```
main_task
├── sub_task_1
├── sub_task_2
│   ├── sub_sub_task_1
│   └── sub_sub_task_2
└── sub_task_3
```

### Task Lifecycle
```
PENDING → ASSIGNED → IN_PROGRESS → COMPLETED
                                 ↓
                              FAILED / BLOCKED
```

### Report Reuse
- Maximum **3 copies** per task
- Update existing reports instead of creating new ones
- Version numbers: v1 → v2 → v3

## 🔧 Available Agents

1. context_awareness_agent
2. decision_engine
3. task_executor_agent
4. error_monitor_agent
5. learning_system
6. memory_agent
7. project_monitor_agent
8. qa_agent
9. resource_manager_agent
10. market_analysis_agent
11. risk_assessment_agent
12. user_advocate_agent
13. task_prediction_agent

## 📊 Time Tracking

Every task tracks:
- **Estimated duration** (set at creation)
- **Actual duration** (measured automatically)
- **Elapsed time** (updated in real-time)
- **Time remaining** (calculated from progress)

Every agent tracks:
- **Total time worked** (across all tasks)
- **Current task time** (active task)
- **Tasks completed** (count)
- **Utilization %** (0-100%)

## 💡 Pro Tips

1. **Use descriptive task titles** - Makes monitoring easier
2. **Set realistic time estimates** - Helps with planning
3. **Update progress regularly** - Shows work is progressing
4. **Use /monitor for long tasks** - See live updates
5. **Generate reports when done** - Document your work
6. **Update reports, don't copy** - Enforces best practices

## 🚨 Common Issues

### Task Not Starting
```bash
# Check if assigned
/status <task_id>

# Assign it
/assign <task_id>

# Then start
/start <task_id> <agent_name>
```

### Report Copy Limit Error
```
ValueError: Copy limit reached (3 copies)
```
**Solution:** Update existing report instead of creating new one

### Monitoring Not Updating
- Ensure `/monitor` was run
- Check if tasks are making progress
- Press Ctrl+C to pause, then restart

## 📖 More Information

- Full Guide: `MULTI_AGENT_ORCHESTRATION_GUIDE.md`
- Implementation Summary: `SYSTEM_IMPLEMENTATION_SUMMARY.md`
- Run Demo: `./start_demo.sh`

---

**Quick Help:** Type `/help` in Command Center for full command list
