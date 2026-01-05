# Terminator AI Agent System

## Project Overview
The **Terminator AI Agent System** is a sophisticated, multi-interface AI orchestrator designed to bring the power of Gemini and other LLMs directly into a unified command center. It features a Universal CLI, a Web Terminal with voice capabilities, and a Terminal UI (TUI). The system orchestrates over 38 specialized agents to handle tasks ranging from system diagnostics and cross-platform control (iOS, Android, macOS) to complex multi-step reasoning.

**Key Goals:**
- **Universal Control:** Single interface for executing commands across varying platforms.
- **Agent Orchestration:** 38+ specialized agents working in concert.
- **Multi-Modal Interaction:** Voice (STT/TTS), Text, and Web-based interactions.
- **Local & Cloud Hybrid:** Supports Ollama (Local), Google Gemini, and Anthropic Claude.

## Architecture & Key Components

### Core Structure
- **`terminator.py`**: The main entry point for the system.
- **`terminator_universal_cli.py`**: Logic for the Universal CLI and slash commands.
- **`core/`**: Contains the logic for the 38+ specialized agents (e.g., `terminator_agentic_orchestrator.py`, `terminator_decision_engine.py`).
- **`terminator-web-terminal/`**: A React-based web interface for the system.
- **`terminator_tui.py`**: The Textual-based Terminal User Interface.

### Interfaces
1.  **Universal CLI:** A slash-command driven interface (e.g., `/healthCheck`, `/connectiOS`) mimicking modern chat applications.
2.  **Web Terminal:** A sci-fi themed React web app supporting voice interactions and real-time streaming (runs on port 8000).
3.  **Terminal UI (TUI):** A rich terminal interface with animations and keyboard-driven controls.
4.  **Dashboard:** A comprehensive visual interface (Mesop-based) for high-level management.

## Building and Running

### Prerequisites
- Python 3.11+
- Node.js (for Web Terminal)
- Ollama (optional, for local LLMs)

### Installation
1.  **Install Python Dependencies:**
    ```bash
    pip3 install -r requirements.txt
    ```
2.  **Setup Web Terminal (Optional but Recommended):**
    ```bash
    cd terminator-web-terminal
    npm install
    npm run build
    cd ..
    ```

### Usage
- **Interactive Menu (Recommended):**
    ```bash
    ./start_all.sh
    ```
- **Universal CLI:**
    ```bash
    ./start_cli.sh
    # or install globally:
    ./install_cli.sh
    terminator
    ```
- **Web Terminal:**
    ```bash
    ./start_web_terminal.sh
    ```
- **Terminal UI:**
    ```bash
    ./start_terminal_ui.sh
    ```

## Configuration
The system automatically detects available backends.
- **Local:** Ensure `ollama serve` is running.
- **Cloud:** Set `GOOGLE_API_KEY` or `ANTHROPIC_API_KEY` environment variables.

## Development Conventions
- **Modular Agents:** New functionality should be encapsulated within specialized agents in the `core/` directory.
- **Inter-Project Communication:** Agents communicate via a dedicated bus (`terminator_agent_communication_bus.py`).
- **Web UI:** The frontend is a standard React application using Vite; build artifacts are served by the Python backend.

## Roadmap (Master Plan)
The project aims to evolve into a "Universal AI Agent Ecosystem" including:
- **Phase 1:** Universal Command Execution & Validation (Foundation).
- **Phase 2:** Platform-Specific Co-Agents (Browser, macOS, iOS).
- **Phase 3:** Multi-AI Router (Dynamic model switching).
- **Phase 4:** MCP Server Creator (Self-extending capabilities).
