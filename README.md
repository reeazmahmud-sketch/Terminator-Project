# TERMINATOR AI Agent System

A sophisticated multi-interface AI agent system with voice capabilities, local and cloud LLM support, and multiple agent orchestration.

## ✨ NEW: Universal CLI (Just Like Claude!)

**Run TERMINATOR from terminal with slash commands:**

```bash
# Install once
./install_cli.sh

# Launch from anywhere
terminator

# Use slash commands
/healthCheck       # Run system diagnostics
/connectiOS        # Connect to iPhone
/run ios get clipboard
/broadcast show status
```

**One Terminal → All Platforms:** Control iOS, Android, macOS, Web, and MCP servers from one CLI!

📚 **[Read Full CLI Guide](UNIVERSAL_CLI_GUIDE.md)** | 📋 **[Quick Start](QUICK_START_CLI.txt)**

---

## Features

- **🆕 Universal CLI** - Claude-style slash commands, control all platforms from terminal
- **4 Different Interfaces** - Web Terminal, Terminal UI, Simple CLI, Dashboard
- **Voice Interaction** - Speech-to-text input and text-to-speech output
- **Multi-Agent System** - 38+ specialized agents for different tasks
- **Local-First** - Runs offline with Ollama, online with Gemini/Claude
- **WebSocket Communication** - Real-time bidirectional messaging
- **Cross-Platform** - Works on macOS, iOS, Android, Web
- **Universal Connectivity** - Every platform can control every other platform

## Quick Start

### 1. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 2. Choose Your Interface

```bash
./start_all.sh  # Interactive menu
```

Or launch directly:

```bash
./start_web_terminal.sh    # Web UI with voice (port 8000)
./start_terminal_ui.sh     # Terminal UI with animations
./start_cli.sh             # Simple command-line interface
```

## Interfaces

### Web Terminal (Recommended)
- Beautiful React-based web interface
- Voice input (speech-to-text) and output (text-to-speech)
- Real-time streaming responses
- Accessible from any device on your network

**Access:** http://localhost:8000

### Terminal UI
- Rich terminal interface with robot animations
- Eye states and blinking effects
- Keyboard-driven interaction
- Runs in your terminal

### Simple CLI
- Minimal command-line interface
- Direct conversational AI
- Lightweight and fast

## Configuration

### LLM Backends

The system supports multiple LLM backends:

1. **Ollama (Local)** - Default, runs without internet
   ```bash
   brew install ollama
   ollama pull llama3
   ollama serve
   ```

2. **Google Gemini (Cloud)** - Requires API key
   ```bash
   export GOOGLE_API_KEY="your-key-here"
   ```

3. **Claude (Cloud)** - Requires API key
   ```bash
   export ANTHROPIC_API_KEY="your-key-here"
   ```

The system automatically switches between available backends.

## Project Structure

```
Terminator/
├── terminator.py                # Main entry point
├── terminator_bridge.py         # WebSocket bridge for web UI
├── terminator_tui.py            # Terminal UI application
├── core/                        # Core agent modules (38+ agents)
│   ├── terminator_agent_communication_bus.py
│   ├── terminator_agentic_orchestrator.py
│   └── ...
├── autonomous/                  # Autonomous agent systems
│   └── terminator_master.py    # Master autonomous controller
├── terminator-web-terminal/     # React web UI
│   ├── src/
│   │   ├── components/
│   │   │   ├── Terminal.tsx    # Main terminal component
│   │   │   ├── Header.tsx
│   │   │   └── StatusPanel.tsx
│   │   └── App.tsx
│   └── dist/                   # Built React app
├── start_web_terminal.sh       # Web UI launcher
├── start_terminal_ui.sh        # Terminal UI launcher
├── start_cli.sh                # CLI launcher
├── start_all.sh                # Interactive menu
└── requirements.txt            # Python dependencies
```

## Agent System

The system includes 38+ specialized agents:

- **Context Awareness Agent** - Understands conversation context
- **Decision Engine** - Makes intelligent routing decisions
- **Task Executor Agent** - Executes tasks and tools
- **Error Monitor Agent** - Tracks and recovers from errors
- **Learning System** - Improves from interactions
- **Memory Agent** - Persistent conversation memory
- **Market Analysis Agent** - Analyzes data and trends
- And 30+ more...

## Web Terminal Features

- **Voice Commands**: Click microphone to speak
- **Streaming Responses**: See AI responses as they're generated
- **Real-time Status**: Connection, speaking, and listening indicators
- **Beautiful UI**: Sci-fi inspired "Terminator" theme
- **Mobile Friendly**: Accessible from phones and tablets

## Troubleshooting

### Port 8000 already in use
```bash
lsof -ti:8000 | xargs kill
```

### React build not found
```bash
cd terminator-web-terminal
npm install
npm run build
```

### Ollama not running
```bash
ollama serve
```

## Development

### Build Web Terminal
```bash
cd terminator-web-terminal
npm install
npm run dev  # Development mode with hot reload
npm run build  # Production build
```

### Run Tests
```bash
python3 -m pytest
```

## Documentation

See the complete Terminator system documentation at:
`/Users/reeazmahmud/Desktop/Terminator/README_PROJECT_START_HERE.md`

## License

Private Project

## Author

Reeaz Mahmud
