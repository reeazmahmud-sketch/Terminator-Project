# Gemini Tools & MCP Servers Reference

**Complete Guide to Gemini CLI Tools and MCP Integration**
**Date:** December 17, 2025

---

## 📦 Gemini CLI Tools (11 Available)

All tools are now wrapped in the `terminator_gemini_tools.py` module for easy webapp integration.

### 1. Codebase Investigator Agent

**ID:** `codebase_investigator`
**Purpose:** Deep AI-powered codebase analysis

**Usage:**
```python
from core.terminator_gemini_tools import get_gemini_tools

tools = get_gemini_tools()
result = await tools.investigate_codebase(
    query="How does authentication work?",
    path="/path/to/codebase",
    depth="medium"  # quick, medium, thorough
)
```

**Returns:**
- Query analyzed
- Files analyzed count
- Key insights
- Code patterns found
- Architectural overview

---

### 2. Edit (Replace)

**ID:** `replace`
**Purpose:** Replace content in files

**Usage:**
```python
result = await tools.edit_file(
    file_path="/path/to/file.py",
    old_content="old code",
    new_content="new code",
    replace_all=False  # True to replace all occurrences
)
```

**Returns:**
- File path
- Occurrences replaced
- Success status

---

### 3. FindFiles (Glob)

**ID:** `glob`
**Purpose:** Find files using glob patterns

**Usage:**
```python
result = await tools.find_files(
    pattern="**/*.py",  # Glob pattern
    path="/path/to/search",
    limit=100
)
```

**Patterns:**
- `*.py` - All Python files in directory
- `**/*.py` - All Python files recursively
- `src/**/*.js` - All JS files in src/
- `test_*.py` - All test files

**Returns:**
- Matching files (sorted by modification time)
- Count
- Full paths

---

### 4. GoogleSearch

**ID:** `google_web_search`
**Purpose:** Search the web via Google

**Usage:**
```python
result = await tools.google_search(
    query="best python logging practices",
    num_results=10
)
```

**Returns:**
- Search results with titles, URLs, snippets
- Result count

---

### 5. ReadFile

**ID:** `read_file`
**Purpose:** Read file contents with line control

**Usage:**
```python
result = await tools.read_file(
    file_path="/path/to/file.py",
    offset=0,      # Start from line 0
    limit=100      # Read 100 lines
)
```

**Returns:**
- File content
- Lines as list
- Total line count
- Lines returned

---

### 6. ReadFolder

**ID:** `list_directory`
**Purpose:** List directory contents

**Usage:**
```python
result = await tools.read_folder(
    folder_path="/path/to/dir",
    recursive=True,        # Include subdirectories
    include_hidden=False   # Include hidden files
)
```

**Returns:**
- List of items with:
  - Name
  - Full path
  - Type (file/directory)
  - Size (bytes)

---

### 7. SaveMemory

**ID:** `save_memory`
**Purpose:** Save information to persistent memory

**Usage:**
```python
result = await tools.save_memory(
    key="user_preference",
    value="dark_mode",
    context="UI settings"
)

# Retrieve memory
memory = await tools.get_memory("user_preference")
all_memory = await tools.get_memory()  # Get all
```

**Storage:** `.gemini_memory/agent_memory.json`

**Returns:**
- Key saved
- Context
- Timestamp

---

### 8. SearchText

**ID:** `search_file_content`
**Purpose:** Search for text patterns in files (regex supported)

**Usage:**
```python
result = await tools.search_text(
    pattern="def.*authenticate",  # Regex pattern
    path="/path/to/search",
    file_type="py",               # Filter by extension
    case_sensitive=False,
    limit=100
)
```

**Returns:**
- Matches with:
  - File path
  - Line number
  - Matched text
  - Context (50 chars before/after)

---

### 9. Shell

**ID:** `run_shell_command`
**Purpose:** Execute shell commands

**Usage:**
```python
result = await tools.run_shell(
    command="ls -la /tmp",
    timeout=30  # seconds
)
```

**Returns:**
- Command executed
- stdout
- stderr
- Return code

**⚠️ Use with caution:** Direct shell access

---

### 10. WebFetch

**ID:** `web_fetch`
**Purpose:** Fetch web content

**Usage:**
```python
result = await tools.web_fetch(
    url="https://example.com/api/data",
    timeout=10
)
```

**Returns:**
- URL
- HTTP status
- Content
- Content length

---

### 11. WriteTodos

**ID:** `write_todos`
**Purpose:** Manage todo lists

**Usage:**
```python
todos = [
    {
        "content": "Fix authentication bug",
        "status": "pending",
        "activeForm": "Fixing authentication bug"
    },
    {
        "content": "Update documentation",
        "status": "completed",
        "activeForm": "Updating documentation"
    }
]

result = await tools.write_todos(todos)

# Retrieve todos
all_todos = await tools.get_todos()
```

**Storage:** `.gemini_todos/todos.json`

**Todo Statuses:**
- `pending` - Not started
- `in_progress` - Currently working
- `completed` - Done

---

## 🎨 MCP Servers (Model Context Protocol)

**MCP Integration via Google Vertex AI Creative Studio**

### Overview

TERMINATOR integrates with 5 Google MCP servers for creative content generation:

| Server | Port | Purpose | Status |
|--------|------|---------|--------|
| Imagen | 9000 | Image generation | ✅ Ready |
| Veo | 9001 | Video creation | ✅ Ready |
| Chirp | 9002 | Speech synthesis | ✅ Ready |
| Lyria | 9003 | Music generation | ✅ Ready |
| AVTool | 9004 | Audio/video compositing | ✅ Ready |

### 1. Imagen Server (Image Generation)

**Port:** 9000
**Endpoint:** `localhost:9000`

**Capabilities:**
- Text-to-image generation
- Image editing
- Style transfer
- Inpainting/outpainting
- Image variations

**Example Request:**
```json
{
  "prompt": "A futuristic AI agent interface with neon blue theme",
  "size": "1024x1024",
  "style": "digital_art",
  "count": 4
}
```

---

### 2. Veo Server (Video Creation)

**Port:** 9001
**Endpoint:** `localhost:9001`

**Capabilities:**
- Text-to-video generation
- Video editing
- Scene transitions
- Motion control
- Video enhancement

**Example Request:**
```json
{
  "prompt": "An AI agent working autonomously, smooth camera pan",
  "duration": "5s",
  "resolution": "1920x1080",
  "fps": 30
}
```

---

### 3. Chirp Server (Speech Synthesis)

**Port:** 9002
**Endpoint:** `localhost:9002`

**Capabilities:**
- Text-to-speech
- Voice cloning
- Multi-language support
- Emotion control
- SSML support

**Example Request:**
```json
{
  "text": "Welcome to TERMINATOR autonomous system",
  "voice": "en-US-Neural2-A",
  "speed": 1.0,
  "pitch": 0,
  "emotion": "neutral"
}
```

---

### 4. Lyria Server (Music Generation)

**Port:** 9003
**Endpoint:** `localhost:9003`

**Capabilities:**
- Text-to-music generation
- Melody creation
- Instrumental composition
- Style mixing
- Audio extension

**Example Request:**
```json
{
  "prompt": "Upbeat electronic music for AI interface",
  "duration": "30s",
  "style": "electronic",
  "tempo": 120
}
```

---

### 5. AVTool Server (Audio/Video Compositing)

**Port:** 9004
**Endpoint:** `localhost:9004`

**Capabilities:**
- Audio/video mixing
- Multi-track composition
- Effects application
- Format conversion
- Timeline editing

**Example Request:**
```json
{
  "operation": "composite",
  "video_tracks": ["video1.mp4", "video2.mp4"],
  "audio_tracks": ["audio1.mp3", "narration.mp3"],
  "effects": ["fade_in", "crossfade"],
  "output_format": "mp4"
}
```

---

## 🔗 MCP Integration Module

**File:** `core/terminator_mcp_integration.py` (created next)

### Connection Management

```python
from core.terminator_mcp_integration import get_mcp_client

mcp = get_mcp_client()

# Connect to specific server
await mcp.connect_imagen()
await mcp.connect_veo()
await mcp.connect_chirp()
await mcp.connect_lyria()
await mcp.connect_avtool()

# Or connect to all
await mcp.connect_all()
```

### Generate Content

```python
# Generate image
result = await mcp.generate_image(
    prompt="A futuristic AI dashboard",
    size="1024x1024"
)

# Generate video
result = await mcp.generate_video(
    prompt="Autonomous agents working together",
    duration="5s"
)

# Generate speech
result = await mcp.text_to_speech(
    text="System initialized successfully",
    voice="en-US-Neural2-A"
)

# Generate music
result = await mcp.generate_music(
    prompt="Calm ambient music for productivity",
    duration="60s"
)

# Composite audio/video
result = await mcp.composite_media(
    video_tracks=["intro.mp4"],
    audio_tracks=["music.mp3", "narration.mp3"]
)
```

---

## 🌐 Webapp Integration

### FastAPI Endpoints (Example)

```python
from fastapi import FastAPI, HTTPException
from core.terminator_gemini_tools import get_gemini_tools
from core.terminator_mcp_integration import get_mcp_client

app = FastAPI()
gemini = get_gemini_tools()
mcp = get_mcp_client()

# Gemini Tools Endpoints

@app.post("/api/gemini/find-files")
async def find_files(pattern: str, path: str = None):
    result = await gemini.find_files(pattern, path)
    return result.to_dict()

@app.post("/api/gemini/read-file")
async def read_file(file_path: str, offset: int = 0, limit: int = None):
    result = await gemini.read_file(file_path, offset, limit)
    return result.to_dict()

@app.post("/api/gemini/search")
async def search_text(pattern: str, path: str = None):
    result = await gemini.search_text(pattern, path)
    return result.to_dict()

@app.post("/api/gemini/memory")
async def save_memory(key: str, value: str, context: str = None):
    result = await gemini.save_memory(key, value, context)
    return result.to_dict()

@app.get("/api/gemini/memory/{key}")
async def get_memory(key: str):
    memory = await gemini.get_memory(key)
    return memory

# MCP Endpoints

@app.post("/api/mcp/generate-image")
async def generate_image(prompt: str, size: str = "1024x1024"):
    result = await mcp.generate_image(prompt, size)
    return result

@app.post("/api/mcp/generate-video")
async def generate_video(prompt: str, duration: str = "5s"):
    result = await mcp.generate_video(prompt, duration)
    return result

@app.post("/api/mcp/text-to-speech")
async def text_to_speech(text: str, voice: str = "en-US-Neural2-A"):
    result = await mcp.text_to_speech(text, voice)
    return result

@app.get("/api/gemini/tools")
async def list_tools():
    return gemini.get_available_tools()

@app.get("/api/gemini/stats")
async def get_stats():
    return gemini.get_stats()

@app.get("/api/mcp/status")
async def mcp_status():
    return await mcp.get_status()
```

### React Frontend Integration

```javascript
// Gemini Tools API Client

class GeminiToolsAPI {
  async findFiles(pattern, path = null) {
    const response = await fetch('/api/gemini/find-files', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({pattern, path})
    });
    return response.json();
  }

  async readFile(filePath, offset = 0, limit = null) {
    const response = await fetch('/api/gemini/read-file', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({file_path: filePath, offset, limit})
    });
    return response.json();
  }

  async searchText(pattern, path = null) {
    const response = await fetch('/api/gemini/search', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({pattern, path})
    });
    return response.json();
  }

  async saveMemory(key, value, context = null) {
    const response = await fetch('/api/gemini/memory', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({key, value, context})
    });
    return response.json();
  }

  async getMemory(key) {
    const response = await fetch(`/api/gemini/memory/${key}`);
    return response.json();
  }

  async getAvailableTools() {
    const response = await fetch('/api/gemini/tools');
    return response.json();
  }
}

// MCP API Client

class MCPAPI {
  async generateImage(prompt, size = "1024x1024") {
    const response = await fetch('/api/mcp/generate-image', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({prompt, size})
    });
    return response.json();
  }

  async generateVideo(prompt, duration = "5s") {
    const response = await fetch('/api/mcp/generate-video', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({prompt, duration})
    });
    return response.json();
  }

  async textToSpeech(text, voice = "en-US-Neural2-A") {
    const response = await fetch('/api/mcp/text-to-speech', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text, voice})
    });
    return response.json();
  }

  async getStatus() {
    const response = await fetch('/api/mcp/status');
    return response.json();
  }
}

// Usage Example

const gemini = new GeminiToolsAPI();
const mcp = new MCPAPI();

// Find Python files
const files = await gemini.findFiles("**/*.py");
console.log(`Found ${files.data.count} files`);

// Generate image
const image = await mcp.generateImage("AI agent interface");
console.log("Image generated:", image.url);
```

---

## 📊 Tool Statistics & Monitoring

```python
# Get tool usage statistics
stats = gemini.get_stats()

# Returns:
{
  'total_calls': 150,
  'successful_calls': 145,
  'failed_calls': 5,
  'tools_used': {
    'read_file': {'success': 50, 'failed': 0},
    'find_files': {'success': 30, 'failed': 1},
    'search_text': {'success': 25, 'failed': 2},
    ...
  }
}
```

---

## 🔒 Security Considerations

1. **Shell Command Execution**: Requires explicit permission
2. **File Access**: Limited to project directories
3. **MCP Servers**: Require Google Cloud authentication
4. **Memory Storage**: Local file system only
5. **Web Requests**: Rate limiting recommended

---

## 🚀 Quick Start

### 1. Setup Gemini Tools

```bash
# Already included in TERMINATOR
# No additional setup needed
```

### 2. Setup MCP Servers

```bash
# Requires Google Cloud project
export GOOGLE_CLOUD_PROJECT="your-project-id"

# Start MCP servers (separate terminal for each)
vertex-mcp-server imagen --port 9000
vertex-mcp-server veo --port 9001
vertex-mcp-server chirp --port 9002
vertex-mcp-server lyria --port 9003
vertex-mcp-server avtool --port 9004
```

### 3. Test Tools

```bash
cd /Users/reeazmahmud/Desktop/Terminator-Project
python3 core/terminator_gemini_tools.py
```

### 4. Integrate with Webapp

See integration examples above.

---

## 📚 Additional Resources

**Documentation:**
- Gemini CLI: `core/terminator_gemini_tools.py`
- MCP Integration: `core/terminator_mcp_integration.py` (next)
- Agent Communication: `core/terminator_agent_communication_bus.py`

**Related Files:**
- Web Terminal: `terminator-web-terminal/`
- Universal CLI: `terminator_universal_cli.py`
- Agent Orchestrator: `core/advanced_agentic_orchestrator.py`

---

**Status:** ✅ Gemini Tools Module Ready | ⏳ MCP Integration Module Next
**Date:** December 17, 2025
