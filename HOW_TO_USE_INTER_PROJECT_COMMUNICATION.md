# 🚀 HOW TO USE INTER-PROJECT COMMUNICATION

**Quick Guide:** Let TERMINATOR call AI Dashboard agents (without integration!)

---

## ✅ What You Have Now:

1. **AI Dashboard** (500+ agents) - Independent system
2. **TERMINATOR** (38 agents) - Independent system
3. **Communication Bridge** - Lets them talk via REST API
4. **No Integration** - Projects remain completely separate!

---

## 🎯 Step-by-Step Setup

### STEP 1: Start AI Dashboard API

Open **Terminal 1:**
```bash
cd ~/Desktop/AI
python3 external_api.py
```

You should see:
```
🚀 AI DASHBOARD EXTERNAL API
====================================================================
📡 Starting API server...
🌐 URL: http://localhost:5000
📖 Docs: http://localhost:5000/docs
🤖 500+ agents ready to help other projects!

✅ Projects can now REQUEST help (no integration needed)
```

**Keep this running** (don't close the terminal)

---

### STEP 2: Test from TERMINATOR

Open **Terminal 2:**
```bash
cd ~/Desktop/Terminator
python3 core/external_project_client.py
```

You should see:
```
🧪 TESTING TERMINATOR → AI DASHBOARD COMMUNICATION
====================================================================

1️⃣  Checking if AI Dashboard is available...
   ✅ AI Dashboard is ONLINE!

2️⃣  Getting available agent types...
   📊 Total agents: 500
   🤖 Agent types: 8

3️⃣  Requesting help from AI Dashboard...

📞 Calling AI Dashboard...
   Type: data_analysis
   Task: Analyze TERMINATOR system performance metrics
   ✅ DataAnalysisAgent_47 completed (123.45ms)

   📊 Result Details:
      Status: success
      Agent Used: DataAnalysisAgent_47
      Execution Time: 123.45ms

====================================================================
✅ SUCCESS! TERMINATOR can call AI Dashboard agents
   Projects remain SEPARATE - no integration!
====================================================================
```

---

## 🤖 How TERMINATOR Agents Use It

### Example 1: Simple Request

```python
# In any TERMINATOR agent file:
from core.external_project_client import get_ai_project_client

# Get client
client = get_ai_project_client()

# Request help
if client.is_available():
    result = client.request_help(
        agent_type="data_analysis",
        task="Analyze user behavior in logs"
    )

    if result:
        print(f"Agent used: {result['agent_used']}")
        print(f"Result: {result['result']}")
```

### Example 2: Check What's Available

```python
client = get_ai_project_client()

if client.is_available():
    agents = client.get_available_agents()

    print(f"Total agents: {agents['total_agents']}")

    for agent_type in agents['agent_types']:
        print(f"- {agent_type['type']}: {agent_type['description']}")
```

### Example 3: Conditional Usage (Smart!)

```python
class TerminatorDataAgent:
    def __init__(self):
        self.ai_client = get_ai_project_client()

    def analyze_complex_dataset(self, data):
        """
        Use AI Dashboard for complex analysis,
        fallback to local if not available
        """

        # Try AI Dashboard first (has 500+ specialized agents)
        if self.ai_client.is_available():
            print("Using AI Dashboard (500+ agents)...")

            result = self.ai_client.request_help(
                agent_type="data_analysis",
                task=f"Deep analysis of {len(data)} records",
                priority="high"
            )

            if result:
                return result['result']

        # Fallback to TERMINATOR's local agents
        print("AI Dashboard unavailable, using local agents...")
        return self.local_analysis(data)
```

---

## 📊 Available Agent Types

| Agent Type | Description | Use For |
|-----------|-------------|---------|
| **data_analysis** | Analyze datasets, patterns, trends | Large dataset analysis |
| **code_review** | Review code quality, security | Code quality checks |
| **system_monitoring** | Monitor system health | Performance monitoring |
| **natural_language_processing** | Text analysis, sentiment | NLP tasks |
| **image_processing** | Image analysis, recognition | Image tasks |
| **task_automation** | Automate workflows | Automation |
| **research** | Research topics, gather info | Information gathering |
| **documentation** | Generate, review docs | Documentation |

---

## 🔍 Real-World Usage Examples

### Use Case 1: Performance Monitoring

**TERMINATOR's monitoring agent** needs to analyze complex performance data:

```python
# TERMINATOR monitoring agent
result = client.request_help(
    agent_type="system_monitoring",
    task="Analyze CPU, memory, disk patterns over 24 hours",
    priority="high",
    metadata={"timeframe": "24h", "metrics": ["cpu", "memory", "disk"]}
)

# AI Dashboard sends back detailed analysis
# from its specialized monitoring agents
```

### Use Case 2: Code Quality

**TERMINATOR needs code review** but doesn't have specialized code review agents:

```python
result = client.request_help(
    agent_type="code_review",
    task="Security review of authentication module",
    priority="critical",
    metadata={"file": "auth.py", "focus": "security"}
)
```

### Use Case 3: Natural Language Understanding

**TERMINATOR gets complex user input** that needs NLP:

```python
result = client.request_help(
    agent_type="natural_language_processing",
    task="Analyze sentiment and extract key topics from user feedback",
    priority="normal",
    metadata={"text_length": 500, "language": "en"}
)
```

---

## ⚙️ Configuration

### Change API URL (if needed):

```python
# Default: http://localhost:5000
client = get_ai_project_client(api_url="http://192.168.1.100:5000")
```

### Set Priority Levels:

- **"low"** - Non-urgent tasks
- **"normal"** - Regular tasks (default)
- **"high"** - Important tasks
- **"critical"** - Urgent, time-sensitive

---

## 🛠️ Troubleshooting

### Problem: "AI Dashboard not available"

**Solution:**
```bash
# Check if AI Dashboard API is running
curl http://localhost:5000/health

# If not, start it:
cd ~/Desktop/AI
python3 external_api.py
```

### Problem: Connection timeout

**Solution:**
```python
# Increase timeout
import httpx
response = httpx.post(url, json=data, timeout=60.0)  # 60 seconds
```

### Problem: Want to see API docs

**Solution:**
```bash
# Start AI Dashboard API, then visit:
open http://localhost:5000/docs

# Interactive API documentation (Swagger UI)
```

---

## 🎯 Quick Commands

### Start AI Dashboard:
```bash
cd ~/Desktop/AI && python3 external_api.py
```

### Test Connection:
```bash
cd ~/Desktop/Terminator && python3 core/external_project_client.py
```

### Check API Health:
```bash
curl http://localhost:5000/health
```

### See Available Agents:
```bash
curl http://localhost:5000/available_agents
```

---

## ✅ Benefits

**What You Get:**
1. ✅ TERMINATOR can REQUEST help when needed
2. ✅ Access to 500+ specialized AI Dashboard agents
3. ✅ Projects stay completely SEPARATE
4. ✅ No code integration or dependencies
5. ✅ Graceful fallback if AI Dashboard offline
6. ✅ Can expand to all 5 projects

**What You Avoid:**
1. ❌ No code mixing between projects
2. ❌ No integration complexity
3. ❌ No dependencies
4. ❌ No conflicts

---

## 🌐 Future: Multi-Project Network

Eventually, all projects can communicate:

```
AI Dashboard (500+ agents) ←→ TERMINATOR (38 agents)
         ↕                            ↕
    ForgeCode              ←→       Eve MCP
```

Each project:
- Runs independently
- Exposes REST API
- Can request help from others
- No integration needed!

---

## 📚 Documentation

- **Full Guide:** `INTER_PROJECT_COMMUNICATION_BRIDGE.md`
- **API Code:** `~/Desktop/AI/external_api.py`
- **Client Code:** `~/Desktop/Terminator/core/external_project_client.py`
- **This Guide:** `HOW_TO_USE_INTER_PROJECT_COMMUNICATION.md`

---

**🎉 You're all set! TERMINATOR can now call AI Dashboard agents when needed, and projects remain completely separate!**
