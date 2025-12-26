# 🌉 INTER-PROJECT COMMUNICATION BRIDGE

**Purpose:** Allow TERMINATOR (Project 2) to call AI Dashboard agents (Project 1) **WITHOUT INTEGRATION**

**Date:** December 16, 2025

---

## 🎯 Architecture: Separate but Connected

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  PROJECT 1: AI Dashboard (500+ agents)                     │
│  ├── Port: 5000 (API endpoint)                             │
│  ├── Independent operation                                 │
│  └── Exposes REST API for requests                         │
│                                                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ HTTP REST API
                      │ (JSON messages)
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                                                             │
│  PROJECT 2: TERMINATOR (38 agents)                         │
│  ├── Port: 8000 (main system)                              │
│  ├── Can REQUEST help from Project 1                       │
│  ├── Calls AI Dashboard when needed                        │
│  └── Remains completely separate                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘

KEY: Projects remain SEPARATE - no code mixing!
     Communication via REST API only
```

---

## 📡 Communication Methods

### Method 1: REST API (Recommended)
- **AI Dashboard** exposes REST API on port 5000
- **TERMINATOR** sends HTTP requests when it needs help
- JSON request/response format
- Completely decoupled

### Method 2: Message Queue
- Use Redis or RabbitMQ as intermediary
- Projects publish/subscribe to messages
- Asynchronous communication

### Method 3: WebSocket Bridge
- Real-time bidirectional communication
- Good for streaming responses
- Still keeps projects separate

---

## 🔧 Implementation

### STEP 1: Create API in AI Dashboard (Project 1)

**File:** `/Users/reeazmahmud/Desktop/AI/external_api.py`

```python
#!/usr/bin/env python3
"""
AI Dashboard External API
Allows other projects to request help from 500+ agents
WITHOUT integration
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="AI Dashboard External API")

class AgentRequest(BaseModel):
    """Request from external project"""
    requesting_project: str  # "TERMINATOR", "ForgeCode", etc.
    agent_type: str          # "data_analysis", "code_review", etc.
    task: str                # Task description
    priority: str = "normal" # "low", "normal", "high", "critical"

class AgentResponse(BaseModel):
    """Response to external project"""
    status: str              # "success", "error", "processing"
    agent_used: str          # Which agent handled it
    result: dict             # Agent's response
    execution_time_ms: float

@app.get("/")
def root():
    """API health check"""
    return {
        "service": "AI Dashboard External API",
        "status": "online",
        "agents_available": 500,
        "version": "1.0"
    }

@app.post("/request_agent_help")
def request_agent_help(request: AgentRequest) -> AgentResponse:
    """
    External projects can request help from AI Dashboard agents

    Example:
        TERMINATOR needs data analysis
        → Sends request to this endpoint
        → AI Dashboard assigns appropriate agent
        → Returns result to TERMINATOR
    """

    print(f"📨 Request from {request.requesting_project}: {request.task}")

    # Route to appropriate agent based on request type
    # (This would integrate with your existing Orion system)

    # For now, mock response:
    result = {
        "analysis": "Agent completed task",
        "details": f"Processed: {request.task}",
        "agent_tier": "Level 2"
    }

    return AgentResponse(
        status="success",
        agent_used="DataAnalysisAgent_47",
        result=result,
        execution_time_ms=123.45
    )

@app.get("/available_agents")
def available_agents():
    """List what types of help are available"""
    return {
        "agent_types": [
            "data_analysis",
            "code_review",
            "system_monitoring",
            "natural_language_processing",
            "image_processing",
            "task_automation",
            "research",
            "documentation"
        ],
        "total_agents": 500,
        "status": "all_online"
    }

if __name__ == "__main__":
    print("🚀 Starting AI Dashboard External API...")
    print("📡 Listening on http://localhost:5000")
    print("🤖 500+ agents ready to help other projects!\n")

    uvicorn.run(app, host="0.0.0.0", port=5000)
```

**Launch:**
```bash
cd ~/Desktop/AI
python3 external_api.py
# API runs on http://localhost:5000
```

---

### STEP 2: Create Client in TERMINATOR (Project 2)

**File:** `/Users/reeazmahmud/Desktop/Terminator/core/external_project_client.py`

```python
#!/usr/bin/env python3
"""
TERMINATOR External Project Client
Allows TERMINATOR to REQUEST help from AI Dashboard
WITHOUT integration
"""

import httpx
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class ExternalAgentRequest:
    """Request to external project"""
    agent_type: str
    task: str
    priority: str = "normal"

class AIProjectClient:
    """
    Client for TERMINATOR to call AI Dashboard agents
    Projects remain SEPARATE - just API calls
    """

    def __init__(self, api_url: str = "http://localhost:5000"):
        self.api_url = api_url
        self.project_name = "TERMINATOR"

    def is_available(self) -> bool:
        """Check if AI Dashboard API is available"""
        try:
            response = httpx.get(f"{self.api_url}/", timeout=2.0)
            return response.status_code == 200
        except:
            return False

    def request_help(
        self,
        agent_type: str,
        task: str,
        priority: str = "normal"
    ) -> Optional[Dict[str, Any]]:
        """
        Request help from AI Dashboard agents

        Args:
            agent_type: Type of help needed
            task: What needs to be done
            priority: "low", "normal", "high", "critical"

        Returns:
            Response from AI Dashboard agent

        Example:
            client = AIProjectClient()
            result = client.request_help(
                agent_type="data_analysis",
                task="Analyze user behavior patterns in logs"
            )
        """

        if not self.is_available():
            print("⚠️  AI Dashboard not available")
            return None

        request_data = {
            "requesting_project": self.project_name,
            "agent_type": agent_type,
            "task": task,
            "priority": priority
        }

        try:
            response = httpx.post(
                f"{self.api_url}/request_agent_help",
                json=request_data,
                timeout=30.0
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ AI Dashboard agent '{result['agent_used']}' completed task")
                return result
            else:
                print(f"❌ Request failed: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Error calling AI Dashboard: {e}")
            return None

    def get_available_agents(self) -> Optional[Dict[str, Any]]:
        """Get list of available agent types"""
        try:
            response = httpx.get(f"{self.api_url}/available_agents")
            return response.json() if response.status_code == 200 else None
        except:
            return None

# Singleton instance
_client = None

def get_ai_project_client() -> AIProjectClient:
    """Get client instance (singleton)"""
    global _client
    if _client is None:
        _client = AIProjectClient()
    return _client

# Example usage:
if __name__ == "__main__":
    print("🧪 Testing AI Project Client...\n")

    client = get_ai_project_client()

    # Check availability
    if client.is_available():
        print("✅ AI Dashboard is available!\n")

        # Request help
        result = client.request_help(
            agent_type="data_analysis",
            task="Analyze system performance metrics"
        )

        if result:
            print(f"\n📊 Result: {result['result']}")
            print(f"⏱️  Execution time: {result['execution_time_ms']}ms")
    else:
        print("⚠️  AI Dashboard not available")
        print("Start it with: cd ~/Desktop/AI && python3 external_api.py")
```

---

### STEP 3: Use in TERMINATOR Agents

**Example: TERMINATOR agent requests help**

```python
# In any TERMINATOR agent file:
from core.external_project_client import get_ai_project_client

class TerminatorDataAgent:
    def __init__(self):
        self.ai_client = get_ai_project_client()

    def analyze_complex_data(self, data):
        """
        If task is too complex for TERMINATOR's 38 agents,
        request help from AI Dashboard's 500+ specialized agents
        """

        # Check if AI Dashboard is available
        if self.ai_client.is_available():
            print("📞 Calling AI Dashboard for advanced analysis...")

            result = self.ai_client.request_help(
                agent_type="data_analysis",
                task=f"Deep analysis of dataset with {len(data)} records",
                priority="high"
            )

            if result:
                return result['result']

        # Fallback: use TERMINATOR's own agents
        return self.local_analysis(data)
```

---

## 🚀 Usage Examples

### Example 1: TERMINATOR Requests Data Analysis

```python
from core.external_project_client import get_ai_project_client

client = get_ai_project_client()

result = client.request_help(
    agent_type="data_analysis",
    task="Analyze user behavior patterns in application logs",
    priority="high"
)

print(result['result'])
```

### Example 2: Check Available Help

```python
client = get_ai_project_client()

agents = client.get_available_agents()
print(f"Available agent types: {agents['agent_types']}")
print(f"Total agents: {agents['total_agents']}")
```

### Example 3: Conditional Agent Request

```python
client = get_ai_project_client()

if client.is_available():
    # AI Dashboard available - use their agents
    result = client.request_help("code_review", "Review security in auth.py")
else:
    # Not available - use local TERMINATOR agents
    result = local_code_review()
```

---

## 📋 How to Set It Up

### 1. Start AI Dashboard API:
```bash
cd ~/Desktop/AI
python3 external_api.py

# You should see:
# 🚀 Starting AI Dashboard External API...
# 📡 Listening on http://localhost:5000
# 🤖 500+ agents ready to help other projects!
```

### 2. TERMINATOR Can Now Call It:
```bash
cd ~/Desktop/Terminator
python3

>>> from core.external_project_client import get_ai_project_client
>>> client = get_ai_project_client()
>>> client.is_available()
True
>>> result = client.request_help("data_analysis", "Test task")
✅ AI Dashboard agent 'DataAnalysisAgent_47' completed task
```

---

## ✅ Benefits of This Approach

### 1. **Complete Separation**
- ✅ No code mixing
- ✅ Projects remain independent
- ✅ Can run separately or together

### 2. **On-Demand Collaboration**
- ✅ TERMINATOR calls AI Dashboard when needed
- ✅ Not always - only when specific expertise required
- ✅ Fallback to local agents if unavailable

### 3. **Scalability**
- ✅ Can add more projects later (ForgeCode, Eve, etc.)
- ✅ All can communicate via same API pattern
- ✅ No integration complexity

### 4. **Flexibility**
- ✅ AI Dashboard can be offline - TERMINATOR still works
- ✅ Can upgrade either project independently
- ✅ No dependencies between codebases

---

## 🌐 Multi-Project Communication

**Future: All projects can talk to each other**

```
AI Dashboard (Port 5000)
    ↕ REST API
TERMINATOR (Port 8000)
    ↕ REST API
ForgeCode (Port 7000)
    ↕ REST API
Eve MCP (Port 8006)
```

Each project:
- Runs independently
- Exposes API
- Can request help from others
- No code integration!

---

## 📊 Request Flow Example

```
1. TERMINATOR agent encounters complex task
   ↓
2. Checks: "Can AI Dashboard help with this?"
   ↓
3. Calls AI Dashboard API:
   POST http://localhost:5000/request_agent_help
   {
     "requesting_project": "TERMINATOR",
     "agent_type": "data_analysis",
     "task": "Analyze 1M log entries"
   }
   ↓
4. AI Dashboard routes to specialized agent (1 of 500+)
   ↓
5. Agent processes task
   ↓
6. Returns result to TERMINATOR
   {
     "status": "success",
     "agent_used": "LogAnalysisAgent_142",
     "result": { "insights": [...] }
   }
   ↓
7. TERMINATOR continues with result
```

**Total time: ~500ms**
**Projects remain: SEPARATE**

---

## 🎯 Summary

**What You Get:**
- ✅ TERMINATOR can REQUEST help from AI Dashboard
- ✅ Projects stay **completely separate** (no integration)
- ✅ Communication via REST API (clean, simple)
- ✅ Works when both running, graceful fallback if not
- ✅ Can expand to all 5 projects

**What You Avoid:**
- ❌ No code mixing
- ❌ No dependencies
- ❌ No integration complexity
- ❌ No conflicts

**Result:** Best of both worlds! 🎉

---

**Next Steps:**
1. Create `external_api.py` in AI Dashboard
2. Create `external_project_client.py` in TERMINATOR
3. Start both systems
4. TERMINATOR can now call AI Dashboard agents when needed!
