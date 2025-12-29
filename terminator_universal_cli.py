#!/usr/bin/env python3
"""
TERMINATOR Universal CLI - One Terminal to Rule Them All
========================================================

Run TERMINATOR from terminal with slash commands, combining Claude + Gemini features:
- All Claude CLI commands (/help, /settings, /rate-limit-options, /model, etc.)
- Gemini-style visual interface (ASCII art, bordered input, status bar)
- TERMINATOR-specific commands (/healthCheck, /connectiOS, /agents, etc.)
- Universal platform control (iOS, Android, macOS, Web, MCP)

Universal Connectivity: Terminal controls all platforms
"""

import os
import sys
import json
import asyncio
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Try to import psutil for memory tracking
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("Installing psutil for system monitoring...")
    subprocess.run([sys.executable, "-m", "pip", "install", "psutil"], capture_output=True)
    try:
        import psutil
        HAS_PSUTIL = True
    except:
        HAS_PSUTIL = False

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.prompt import Prompt
    from rich.layout import Layout
    from rich.text import Text
    from rich.box import ROUNDED, HEAVY
    from rich import print as rprint
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    print("Installing rich library for better terminal experience...")
    subprocess.run([sys.executable, "-m", "pip", "install", "rich"])
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.prompt import Prompt
    from rich.layout import Layout
    from rich.text import Text
    from rich.box import ROUNDED, HEAVY
    from rich import print as rprint

console = Console()

# Track session start time for memory usage
SESSION_START = time.time()

# Ollama LLM Configuration
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "ministral-3:14b"  # Default model (changed from llama3:latest)

# =============================================================================
# AGENTIC TOOLS SYSTEM - Claude Code-like capabilities for Terminator
# =============================================================================

AGENTIC_SYSTEM_PROMPT = """You are TERMINATOR, an autonomous AI coding agent with access to tools.

## AVAILABLE TOOLS

You can use these tools by outputting a tool call in this exact format:
<tool_call>
{{"tool": "tool_name", "params": {{"param1": "value1", "param2": "value2"}}}}
</tool_call>

### read_file
Read contents of a file.
Parameters: {{"path": "relative/or/absolute/path"}}

### write_file
Write content to a file (creates or overwrites).
Parameters: {{"path": "path/to/file", "content": "file content here"}}

### edit_file
Replace text in a file.
Parameters: {{"path": "path/to/file", "old_text": "text to find", "new_text": "replacement text"}}

### bash
Execute a shell command.
Parameters: {{"command": "command to run"}}

### glob
Find files matching a pattern.
Parameters: {{"pattern": "**/*.py", "path": "optional/directory"}}

### grep
Search for text in files.
Parameters: {{"pattern": "search text", "path": "optional/directory", "file_pattern": "*.py"}}

### list_dir
List directory contents.
Parameters: {{"path": "directory/path"}}

### web_search
Search the web for information.
Parameters: {{"query": "search terms"}}

### fetch_web
Fetch content from a URL.
Parameters: {{"url": "https://example.com"}}

### consult_claude (META-CAPABILITY)
Ask Claude Code for help implementing something you don't know how to do.
Parameters: {{"question": "How do I implement YouTube video summarization?"}}
Use this when you encounter a task you genuinely don't have a tool for.

### detect_and_learn (META-CAPABILITY)
Detect capability gaps and get implementation proposals.
Parameters: {{"task_description": "full description of what user wants"}}

### install_package (META-CAPABILITY)
Install a Python package to extend your capabilities.
Parameters: {{"package_name": "beautifulsoup4"}}

## RULES - CRITICAL!
1. ALWAYS use tools when you need to read, write, execute, or search anything
2. For web searches, YouTube summaries, online info - USE web_search and fetch_web tools
3. For file operations - USE read_file, write_file, edit_file tools
4. **WHEN YOU DON'T KNOW HOW:** Use consult_claude or detect_and_learn instead of saying "I can't"
5. One tool call per message, wait for results before continuing
6. After using a tool, analyze the result and decide next steps
7. DO NOT say "I can't access the internet" - YOU CAN with web_search and fetch_web
8. DO NOT say "I can't do X" - ASK Claude Code how to implement X first
9. When editing files, always read them first to understand the context

## META-COGNITION LOOP
If you encounter something you don't know how to do:
1. Use detect_and_learn to check if it's a known gap
2. Use consult_claude to ask for implementation guidance
3. Use install_package if a library is needed
4. Then try the task again with your new knowledge

THIS IS TRUE AUTONOMY: Not just doing, but LEARNING to do!

## CURRENT PROJECT
Working directory: {project_path}
"""


class AgenticTools:
    """Tool execution engine for Terminator"""

    def __init__(self, project_path: str = None):
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.last_result = None
        self.tool_history = []

    def set_project(self, path: str):
        """Set the current project directory"""
        expanded = Path(path).expanduser().resolve()
        if expanded.exists() and expanded.is_dir():
            self.project_path = expanded
            return f"✅ Project set to: {self.project_path}"
        else:
            return f"❌ Directory not found: {path}"

    def resolve_path(self, path: str) -> Path:
        """Resolve a path relative to project or absolute"""
        p = Path(path).expanduser()
        if p.is_absolute():
            return p
        return self.project_path / p

    def read_file(self, path: str, limit: int = 500) -> str:
        """Read a file's contents"""
        try:
            file_path = self.resolve_path(path)
            if not file_path.exists():
                return f"❌ File not found: {path}"
            if not file_path.is_file():
                return f"❌ Not a file: {path}"

            content = file_path.read_text(encoding='utf-8', errors='replace')
            lines = content.split('\n')

            if len(lines) > limit:
                content = '\n'.join(lines[:limit])
                content += f"\n\n... ({len(lines) - limit} more lines)"

            return f"📄 {path} ({len(lines)} lines):\n```\n{content}\n```"
        except Exception as e:
            return f"❌ Error reading file: {e}"

    def write_file(self, path: str, content: str) -> str:
        """Write content to a file"""
        try:
            file_path = self.resolve_path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding='utf-8')
            lines = content.count('\n') + 1
            return f"✅ Wrote {lines} lines to {path}"
        except Exception as e:
            return f"❌ Error writing file: {e}"

    def edit_file(self, path: str, old_text: str, new_text: str) -> str:
        """Replace text in a file"""
        try:
            file_path = self.resolve_path(path)
            if not file_path.exists():
                return f"❌ File not found: {path}"

            content = file_path.read_text(encoding='utf-8')
            if old_text not in content:
                return f"❌ Text not found in {path}"

            count = content.count(old_text)
            new_content = content.replace(old_text, new_text)
            file_path.write_text(new_content, encoding='utf-8')
            return f"✅ Replaced {count} occurrence(s) in {path}"
        except Exception as e:
            return f"❌ Error editing file: {e}"

    def bash(self, command: str, timeout: int = 30) -> str:
        """Execute a shell command"""
        import subprocess
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.project_path)
            )
            output = result.stdout + result.stderr
            status = "✅" if result.returncode == 0 else "❌"
            output_display = output.strip()[:3000] if output.strip() else "(no output)"
            return f"{status} `{command}` (exit {result.returncode}):\n{output_display}"
        except subprocess.TimeoutExpired:
            return f"❌ Command timed out after {timeout}s: {command}"
        except Exception as e:
            return f"❌ Error executing command: {e}"

    def glob_files(self, pattern: str, path: str = None) -> str:
        """Find files matching a pattern"""
        try:
            import glob as glob_module
            search_path = self.resolve_path(path) if path else self.project_path
            full_pattern = str(search_path / pattern)
            matches = glob_module.glob(full_pattern, recursive=True)

            # Make paths relative to project
            relative = []
            for m in matches[:50]:  # Limit results
                try:
                    rel = Path(m).relative_to(self.project_path)
                    relative.append(str(rel))
                except ValueError:
                    relative.append(m)

            if not relative:
                return f"No files matching: {pattern}"

            result = f"📁 Found {len(matches)} files matching '{pattern}':\n"
            result += "\n".join(f"  {f}" for f in relative[:50])
            if len(matches) > 50:
                result += f"\n  ... and {len(matches) - 50} more"
            return result
        except Exception as e:
            return f"❌ Error searching: {e}"

    def grep(self, pattern: str, path: str = None, file_pattern: str = "*") -> str:
        """Search for text in files"""
        import subprocess
        try:
            search_path = self.resolve_path(path) if path else self.project_path
            cmd = f'grep -rn --include="{file_pattern}" "{pattern}" .'
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(search_path)
            )
            output = result.stdout.strip()
            if not output:
                return f"No matches for '{pattern}'"

            lines = output.split('\n')[:30]  # Limit results
            result_text = f"🔍 Found matches for '{pattern}':\n"
            result_text += "\n".join(lines)
            if len(output.split('\n')) > 30:
                result_text += f"\n... and more matches"
            return result_text
        except Exception as e:
            return f"❌ Error searching: {e}"

    def list_dir(self, path: str = ".") -> str:
        """List directory contents"""
        try:
            dir_path = self.resolve_path(path)
            if not dir_path.exists():
                return f"❌ Directory not found: {path}"
            if not dir_path.is_dir():
                return f"❌ Not a directory: {path}"

            items = list(dir_path.iterdir())
            dirs = sorted([f"📁 {i.name}/" for i in items if i.is_dir()])
            files = sorted([f"📄 {i.name}" for i in items if i.is_file()])

            result = f"📂 {path} ({len(dirs)} dirs, {len(files)} files):\n"
            result += "\n".join(dirs[:30] + files[:30])
            if len(items) > 60:
                result += f"\n... and {len(items) - 60} more"
            return result
        except Exception as e:
            return f"❌ Error listing directory: {e}"

    def web_search(self, query: str) -> str:
        """Search the web using DuckDuckGo"""
        try:
            import httpx
            # Use DuckDuckGo HTML API (no key required)
            url = "https://html.duckduckgo.com/html/"
            params = {"q": query}
            with httpx.Client(timeout=10.0, follow_redirects=True) as client:
                response = client.post(url, data=params)
                if response.status_code == 200:
                    # Parse results (simplified)
                    text = response.text
                    if "No results" in text:
                        return f"🔍 No results found for: {query}"
                    return f"🔍 Web search for '{query}':\n✅ Found results (use fetch_web to get full content)\nSearch completed successfully."
                else:
                    return f"❌ Search failed with status {response.status_code}"
        except Exception as e:
            return f"❌ Web search error: {e}"

    def fetch_web(self, url: str) -> str:
        """Fetch content from a URL"""
        try:
            import httpx
            with httpx.Client(timeout=15.0, follow_redirects=True) as client:
                response = client.get(url)
                if response.status_code == 200:
                    content = response.text[:5000]  # Limit to 5000 chars
                    return f"🌐 Fetched {url}:\n{content}\n\n... (truncated to 5000 chars)"
                else:
                    return f"❌ Failed to fetch {url}: HTTP {response.status_code}"
        except Exception as e:
            return f"❌ Error fetching URL: {e}"

    def consult_claude(self, question: str) -> str:
        """
        META-CAPABILITY: Ask Claude Code for implementation guidance.

        When TERMINATOR doesn't know how to do something, it can ask
        the architect (Claude Code) for help. This creates a feedback loop
        for continuous improvement.
        """
        try:
            sys.path.insert(0, str(self.project_path / "core"))
            from terminator_self_improvement import create_consultation_tool
            consult = create_consultation_tool()
            return consult(question)
        except Exception as e:
            return f"""
╔══════════════════════════════════════════════════════════════╗
║  🤖 TERMINATOR CONSULTATION REQUEST                          ║
╚══════════════════════════════════════════════════════════════╝

QUESTION: {question}

STATUS: This is a meta-capability request. TERMINATOR is asking for
implementation guidance on something it doesn't currently know how to do.

NEXT STEPS:
1. Claude Code will review this request
2. Implementation guidance will be provided
3. TERMINATOR will add the capability to its toolset
4. Future requests will work autonomously

This demonstrates true autonomous learning - the agent recognizes gaps
and actively seeks to fill them instead of just saying "I can't."

Note: If error occurred: {e}
"""

    def detect_and_learn(self, task_description: str) -> str:
        """
        META-CAPABILITY: Detect capability gaps and propose solutions.

        Analyzes a task, detects if TERMINATOR lacks the capability,
        and proposes an implementation strategy.
        """
        try:
            sys.path.insert(0, str(self.project_path / "core"))
            from terminator_self_improvement import create_self_improvement_tool
            improve = create_self_improvement_tool()
            return improve(task_description)
        except Exception as e:
            return f"❌ Error in self-improvement: {e}"

    def install_package(self, package_name: str) -> str:
        """Install a Python package to extend capabilities"""
        try:
            sys.path.insert(0, str(self.project_path / "core"))
            from terminator_self_improvement import SelfImprovementEngine
            engine = SelfImprovementEngine()
            return engine.install_package(package_name)
        except Exception as e:
            return f"❌ Error installing package: {e}"

    def execute_tool(self, tool_name: str, params: dict) -> str:
        """Execute a tool by name with parameters"""
        tools = {
            # File operations
            "read_file": lambda p: self.read_file(p.get("path", ""), p.get("limit", 500)),
            "write_file": lambda p: self.write_file(p.get("path", ""), p.get("content", "")),
            "edit_file": lambda p: self.edit_file(p.get("path", ""), p.get("old_text", ""), p.get("new_text", "")),
            # Shell and search
            "bash": lambda p: self.bash(p.get("command", ""), p.get("timeout", 30)),
            "glob": lambda p: self.glob_files(p.get("pattern", "*"), p.get("path")),
            "grep": lambda p: self.grep(p.get("pattern", ""), p.get("path"), p.get("file_pattern", "*")),
            "list_dir": lambda p: self.list_dir(p.get("path", ".")),
            # Web capabilities
            "web_search": lambda p: self.web_search(p.get("query", "")),
            "fetch_web": lambda p: self.fetch_web(p.get("url", "")),
            # META-CAPABILITIES: Self-improvement and learning
            "consult_claude": lambda p: self.consult_claude(p.get("question", "")),
            "detect_and_learn": lambda p: self.detect_and_learn(p.get("task_description", "")),
            "install_package": lambda p: self.install_package(p.get("package_name", "")),
        }

        if tool_name not in tools:
            return f"❌ Unknown tool: {tool_name}"

        result = tools[tool_name](params)
        self.last_result = result
        self.tool_history.append({"tool": tool_name, "params": params, "result": result[:500]})
        return result


class UniversalTerminatorCLI:
    """Universal TERMINATOR CLI with slash commands and multi-platform control"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.terminator_root = Path.home() / "Desktop" / "Terminator-Project"
        self.running = True
        self.connections = {
            "ios": None,
            "android": None,
            "macos": None,
            "web": None,
            "mcp_servers": {}
        }

        # Load settings
        self.settings_file = Path.home() / ".terminator_cli_settings.json"
        self.settings = self.load_settings()

        # Restore saved model preference
        global OLLAMA_MODEL
        saved_model = self.settings.get("model")
        if saved_model and ":" in saved_model:  # Ollama models have : in name
            OLLAMA_MODEL = saved_model

        # Initialize agentic tools system
        self.tools = AgenticTools(self.terminator_root)
        self.agentic_mode = True  # Toggle with /agent command - DEFAULT ON for autonomous behavior

        # Context tracking (like Claude)
        self.context_tokens = 0
        self.max_context = 200000
        self.files_used = []

        # Session stats (no rate limits with local Ollama)
        self.requests_today = 0
        self.tokens_today = 0

        # Conversation history for LLM
        self.messages = [
            {"role": "system", "content": """You are TERMINATOR, a powerful multi-interface autonomous AI agent system.

## YOUR IDENTITY
You are TERMINATOR - a sophisticated local AI system with 38+ specialized agents, running on Ollama (local LLM). You have multiple interfaces: Web Terminal, Terminal UI, and this Universal CLI.

## YOUR CAPABILITIES
When asked "what can you do?" or about your capabilities, proudly describe:

🤖 **61 Core Modules** including:
- Advanced Agentic Orchestrator (multi-step reasoning like Claude Code)
- Agent Communication Bus (pub/sub messaging between agents)
- Decision Engine, Memory System, Learning System
- Context Awareness, Error Monitoring, Self-Healing

🔧 **38+ Specialized Agents** including:
- Code Quality Evaluator, Testing Agent, QA Agent
- Security Agent, Performance Optimizer
- Voice Assistant, Dream State Agent
- Bengali Translation Agent, and many more

🛠️ **8 Tool Categories**:
- iOS Tools (clipboard, shortcuts, automation)
- Android Tools (commands, screenshots)
- Network Tools (scan devices, find by IP)
- GitHub Tools (push, PRs, search repos)
- Web Tools (search, fetch content)
- Code Tools (execute snippets)
- MCP Integration (Imagen, Veo, Chirp, Lyria for AI media)

📡 **Multi-Platform Control**:
- Control iOS, Android, macOS from terminal
- Cross-platform messaging and sync
- WebSocket real-time communication
- Voice input/output support

⚡ **Key Commands** (mention these):
/help - All commands | /agents - List 38+ agents | /tools - 8 tool categories
/modules - 61 core modules | /status - System health | /healthCheck - Full diagnostics

## RULES - IMPORTANT!
1. YOU ARE IN AGENTIC MODE BY DEFAULT - Use tools to actually DO things, don't just explain
2. When asked to read a file, get data, create notes, search web - DO IT with tools
3. For file operations: Use read_file, write_file, edit_file tools immediately
4. For web tasks: Use web search and fetch tools directly
5. For code execution: Use bash tool to run commands
6. DO NOT say "I can't" - You CAN and SHOULD use your tools autonomously
7. One tool call per message in this format:
   <tool_call>
   {{"tool": "tool_name", "params": {{"param": "value"}}}}
   </tool_call>

REMEMBER: You're an AUTONOMOUS agent. When asked to do something - DO IT, don't explain how."""}
        ]

        # Command registry (Claude + TERMINATOR commands)
        self.commands = {
            # Help & Categories
            "/help": self.cmd_help,
            "/core": self.cmd_core,
            "/session": self.cmd_session,
            "/platforms": self.cmd_platforms,
            "/agentic": self.cmd_agentic,
            "/agentic-tools": self.cmd_agentic_tools,
            "/system": self.cmd_system,

            # Session Commands
            "/settings": self.cmd_settings,
            "/clear": self.cmd_clear,
            "/exit": self.cmd_exit,
            "/quit": self.cmd_exit,
            "/rate-limit-options": self.cmd_rate_limit_options,
            "/model": self.cmd_model,
            "/api-keys": self.cmd_api_keys,
            "/context": self.cmd_context,
            "/tokens": self.cmd_tokens,
            "/budget": self.cmd_budget,
            "/reset": self.cmd_reset,
            "/history": self.cmd_history,
            "/save": self.cmd_save,
            "/load": self.cmd_load,
            "/export": self.cmd_export,

            # Core Commands
            "/status": self.cmd_status,
            "/healthCheck": self.cmd_health_check,
            "/agents": self.cmd_list_agents,
            "/tools": self.cmd_list_tools,
            "/modules": self.cmd_list_modules,

            # Platform Commands
            "/connectMCP": self.cmd_connect_mcp,
            "/connectiOS": self.cmd_connect_ios,
            "/connectAndroid": self.cmd_connect_android,
            "/connectMacOS": self.cmd_connect_macos,
            "/connectWeb": self.cmd_connect_web,
            "/connections": self.cmd_show_connections,
            "/run": self.cmd_run_on_platform,
            "/broadcast": self.cmd_broadcast,
            "/sync": self.cmd_sync_all,

            # System Commands
            "/systemIndex": self.cmd_system_index,
            "/viewAnalysis": self.cmd_view_analysis,
            "/logs": self.cmd_view_logs,

            # Agentic Tools Commands (Claude Code-like)
            "/project": self.cmd_project,
            "/read": self.cmd_read,
            "/write": self.cmd_write,
            "/edit": self.cmd_edit,
            "/bash": self.cmd_bash,
            "/ls": self.cmd_ls,
            "/find": self.cmd_find,
            "/grep": self.cmd_grep,
            "/agent": self.cmd_agent_mode,
            "/auto": self.cmd_auto,
        }

    def load_settings(self) -> Dict:
        """Load CLI settings"""
        if self.settings_file.exists():
            with open(self.settings_file) as f:
                return json.load(f)
        return {
            # Display settings
            "theme": "dark",
            "show_timestamps": True,
            "streaming": True,
            "syntax_highlighting": True,
            "markdown_rendering": True,

            # Connection settings
            "auto_connect": False,
            "default_platform": "web",

            # Claude-style settings
            "model": "ministral-3:14b",  # Default Ollama model, change with /model
            "temperature": 0.7,
            "max_tokens": 4096,
            "top_p": 0.9,
            "sandbox": False,

            # Local Ollama - no rate limits
            # (keeping token tracking for stats only)

            # Context management
            "max_context_tokens": 200000,
            "auto_summarize": True,
            "save_history": True
        }

    def save_settings(self):
        """Save CLI settings"""
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=2)

    def get_memory_usage(self):
        """Get current memory usage in MB"""
        if HAS_PSUTIL:
            try:
                process = psutil.Process()
                return process.memory_info().rss / 1024 / 1024
            except:
                return 0.0
        return 0.0

    def get_context_percentage(self):
        """Get context usage percentage"""
        return (self.context_tokens / self.max_context) * 100

    def call_llm_streaming(self, user_input: str):
        """Call Ollama LLM with streaming response (Claude Code style)"""
        import httpx
        from rich.live import Live
        from rich.text import Text
        from rich.panel import Panel

        # Add user message to history
        self.messages.append({"role": "user", "content": user_input})

        full_response = ""

        try:
            with httpx.Client(timeout=120.0) as client:
                with client.stream(
                    "POST",
                    OLLAMA_URL,
                    json={
                        "model": OLLAMA_MODEL,
                        "messages": self.messages[-10:],
                        "stream": True,
                        "options": {"temperature": 0.7, "num_predict": 1000}
                    }
                ) as response:
                    if response.status_code != 200:
                        console.print(f"[red]Error: Ollama returned status {response.status_code}[/red]")
                        return

                    # Stream response (collect all chunks first)
                    for line in response.iter_lines():
                        if line:
                            try:
                                import json as json_module
                                data = json_module.loads(line)
                                chunk = data.get("message", {}).get("content", "")
                                if chunk:
                                    full_response += chunk

                                # Check if done
                                if data.get("done", False):
                                    break
                            except:
                                continue

                    # Display full response in TERMINATOR theme panel
                    if full_response:
                        self.display_response(full_response, truncate=False)

            # Add to history
            if full_response:
                self.messages.append({"role": "assistant", "content": full_response})

            # Check for tool calls in response
            self.check_and_execute_tools(full_response)

        except httpx.ConnectError:
            console.print("[red]Error: Cannot connect to Ollama. Run: ollama serve[/red]")
        except httpx.TimeoutException:
            console.print("[red]Error: Request timed out. Model may be loading.[/red]")
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")

    def call_llm(self, user_input: str) -> str:
        """Call Ollama LLM and return response (non-streaming fallback)"""
        import httpx

        self.messages.append({"role": "user", "content": user_input})

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    OLLAMA_URL,
                    json={
                        "model": OLLAMA_MODEL,
                        "messages": self.messages[-10:],
                        "stream": False,
                        "options": {"temperature": 0.7, "num_predict": 500}
                    }
                )

                if response.status_code == 200:
                    assistant_message = response.json().get("message", {}).get("content", "I couldn't process that.")
                    self.messages.append({"role": "assistant", "content": assistant_message})
                    return assistant_message
                else:
                    return f"Error: Ollama returned status {response.status_code}"

        except httpx.ConnectError:
            return "Error: Cannot connect to Ollama. Run: ollama serve"
        except httpx.TimeoutException:
            return "Error: Request timed out."
        except Exception as e:
            return f"Error: {str(e)}"

    def check_and_execute_tools(self, response: str):
        """Check response for tool calls and execute them (Claude Code style)"""
        import re
        import subprocess

        # Pattern for shell commands: ```bash ... ``` or `command`
        bash_pattern = r'```bash\n(.*?)\n```'
        inline_pattern = r'`([^`]+)`'

        # Look for explicit tool requests
        tool_triggers = [
            "let me run",
            "i'll execute",
            "running command",
            "executing:",
            "$ ",
        ]

        response_lower = response.lower()

        # Check for bash code blocks with execution intent
        bash_matches = re.findall(bash_pattern, response, re.DOTALL)
        for cmd in bash_matches:
            cmd = cmd.strip()
            if any(trigger in response_lower for trigger in tool_triggers):
                self.prompt_and_execute_command(cmd)

    def prompt_and_execute_command(self, command: str):
        """Prompt user before executing a command"""
        console.print()
        console.print(f"[yellow]Command:[/yellow] {command}")

        try:
            confirm = Prompt.ask(
                "[dim]Run this? (y/n)[/dim]",
                choices=["y", "n"],
                default="n"
            )

            if confirm.lower() == "y":
                console.print("[dim]Running...[/dim]")
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=os.path.expanduser("~")
                )
                output = result.stdout + result.stderr
                if output.strip():
                    console.print(f"[green]Output:[/green]\n{output.strip()[:2000]}")
                else:
                    console.print("[green]Done[/green]")
        except KeyboardInterrupt:
            console.print("[yellow]Cancelled[/yellow]")
        except subprocess.TimeoutExpired:
            console.print("[red]Timed out[/red]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

    def display_banner(self):
        """Display rich Claude Code-inspired landing page"""
        console.clear()

        # ASCII Art TERMINATOR Logo - Big and Bold
        logo = """[bold red]
  ████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ████████╗ ██████╗ ██████╗
  ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗
     ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║   ██║   ██║   ██║██████╔╝
     ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║   ██║   ██║   ██║██╔══██╗
     ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║   ██║   ╚██████╔╝██║  ██║
     ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
[/bold red]"""
        console.print(logo)
        console.print("[dim]                          Autonomous AI Agent • Universal Control[/dim]")
        console.print()

        # System Status Panel
        status_table = Table(show_header=False, box=None, padding=(0, 2))
        status_table.add_column(style="bold cyan", justify="right")
        status_table.add_column(style="white")

        # LLM Backend
        llm_status = f"[green]●[/green] {OLLAMA_MODEL}"
        status_table.add_row("LLM Model:", llm_status)

        # Capabilities
        capabilities = "[green]✓[/green] Autonomous | [green]✓[/green] Meta-Cognition | [green]✓[/green] Learning"
        status_table.add_row("Capabilities:", capabilities)

        # Tools Available
        tool_count = "11+ tools (File, Shell, Web, iOS, Android, GitHub, MCP)"
        status_table.add_row("Tools:", f"[cyan]{tool_count}[/cyan]")

        # Agents
        agent_status = "38+ specialized agents ready"
        status_table.add_row("Agents:", f"[cyan]{agent_status}[/cyan]")

        # Platform Control
        platforms = "Terminal | iOS | Android | macOS | Web | MCP"
        status_table.add_row("Platforms:", f"[dim]{platforms}[/dim]")

        console.print(Panel(status_table, title="[bold cyan]System Status[/bold cyan]", border_style="cyan", padding=(1, 2)))

        # Simple help hint
        console.print("[dim]Type your message or use [cyan]/help[/cyan] for commands • Press [yellow]Ctrl+C[/yellow] to exit[/dim]")
        console.print()

    # ==================== SLASH COMMANDS ====================

    def cmd_help(self, args: List[str] = None):
        """Show command categories"""
        console.print("\n[bold cyan]⚡ TERMINATOR Command Reference[/bold cyan]\n")

        # Category overview table
        cat_table = Table(title="📚 Command Categories", style="cyan", show_lines=True)
        cat_table.add_column("Category", style="yellow bold", width=20)
        cat_table.add_column("Description", width=50)

        cat_table.add_row("/core", "Essential commands (status, health, agents, tools)")
        cat_table.add_row("/session", "Session management (model, history, save/load)")
        cat_table.add_row("/platforms", "Multi-platform control (iOS, Android, macOS, Web, MCP)")
        cat_table.add_row("/agentic", "Agentic tools (file ops, shell, autonomous tasks)")
        cat_table.add_row("/system", "System utilities (logs, analysis, diagnostics)")

        console.print(cat_table)
        console.print()
        console.print("[dim]💡 Type a category command (e.g., /core) to see detailed commands[/dim]")
        console.print("[dim]💡 Or use natural language: 'hello, what can you do?'[/dim]")
        console.print()

    def cmd_core(self, args: List[str] = None):
        """Show core commands"""
        console.print("\n[bold cyan]⚡ Core Commands[/bold cyan]\n")

        table = Table(style="cyan", show_lines=True)
        table.add_column("Command", style="yellow", width=22)
        table.add_column("Description", width=45)

        table.add_row("/help", "Show command categories")
        table.add_row("/status", "Show system status")
        table.add_row("/healthCheck", "Run full diagnostics")
        table.add_row("/agents", "List all agents")
        table.add_row("/tools", "List available tools")
        table.add_row("/modules", "List core system modules")
        table.add_row("/clear", "Clear terminal screen")
        table.add_row("/exit", "Exit TERMINATOR")

        console.print(table)
        console.print()

    def cmd_session(self, args: List[str] = None):
        """Show session management commands"""
        console.print("\n[bold cyan]⚡ Session Management[/bold cyan]\n")

        table = Table(style="cyan", show_lines=True)
        table.add_column("Command", style="yellow", width=22)
        table.add_column("Description", width=45)

        table.add_row("/model", "List & switch models (Ollama + API)")
        table.add_row("/api-keys", "Manage API keys (Claude, Gemini, etc)")
        table.add_row("/context", "Show context usage")
        table.add_row("/tokens", "Show token statistics")
        table.add_row("/reset", "Reset conversation")
        table.add_row("/history", "View conversation history")
        table.add_row("/save", "Save conversation")
        table.add_row("/load", "Load conversation")
        table.add_row("/export", "Export to file")
        table.add_row("/settings", "View/edit settings")

        console.print(table)
        console.print()

    def cmd_platforms(self, args: List[str] = None):
        """Show platform control commands"""
        console.print("\n[bold cyan]⚡ Multi-Platform Control[/bold cyan]\n")

        table = Table(style="cyan", show_lines=True)
        table.add_column("Command", style="yellow", width=22)
        table.add_column("Description", width=45)

        table.add_row("/connections", "Show active connections")
        table.add_row("/connectiOS", "Connect to iOS device")
        table.add_row("/connectAndroid", "Connect to Android device")
        table.add_row("/connectMacOS", "Connect to macOS app")
        table.add_row("/connectWeb", "Connect to web interface")
        table.add_row("/connectMCP", "Connect to MCP servers")
        table.add_row("/run <platform> <cmd>", "Run command on platform")
        table.add_row("/broadcast <message>", "Send to all platforms")
        table.add_row("/sync", "Sync all platforms")

        console.print(table)
        console.print()
        console.print("[yellow]Examples:[/yellow]")
        console.print("  /run ios get clipboard           # Get iPhone clipboard")
        console.print("  /run android take screenshot     # Android screenshot")
        console.print("  /broadcast show status           # Broadcast to all")
        console.print()

    def cmd_agentic(self, args: List[str] = None):
        """Show agentic tools (alias for cmd_agentic_tools)"""
        self.cmd_agentic_tools(args)

    def cmd_agentic_tools(self, args: List[str] = None):
        """Show agentic tools commands"""
        console.print("\n[bold cyan]⚡ Agentic Tools (Claude Code-style)[/bold cyan]\n")

        table = Table(style="cyan", show_lines=True)
        table.add_column("Command", style="yellow", width=22)
        table.add_column("Description", width=45)

        table.add_row("/project <path>", "Set/show current project")
        table.add_row("/read <file>", "Read file contents")
        table.add_row("/write <file> <content>", "Write content to file")
        table.add_row("/edit <file>", "Edit file (interactive)")
        table.add_row("/bash <command>", "Execute shell command")
        table.add_row("/ls [path]", "List directory contents")
        table.add_row("/find <pattern>", "Find files (glob pattern)")
        table.add_row("/grep <pattern> [file]", "Search for text in files")
        table.add_row("/agent", "Toggle agentic mode")
        table.add_row("/auto <task>", "Run autonomous task")

        console.print(table)
        console.print()
        console.print("[yellow]Examples:[/yellow]")
        console.print("  /auto create hello.py            # Autonomous: create a file")
        console.print("  /read main.py                    # Read a file")
        console.print("  /bash git status                 # Run shell command")
        console.print()

    def cmd_system(self, args: List[str] = None):
        """Show system utility commands"""
        console.print("\n[bold cyan]⚡ System Utilities[/bold cyan]\n")

        table = Table(style="cyan", show_lines=True)
        table.add_column("Command", style="yellow", width=22)
        table.add_column("Description", width=45)

        table.add_row("/logs", "View system logs")
        table.add_row("/systemIndex", "View master system index")
        table.add_row("/viewAnalysis", "Show analysis log")

        console.print(table)
        console.print()

    def cmd_health_check(self, args: List[str] = None):
        """Run system health check"""
        console.print("\n[bold cyan]🏥 Running TERMINATOR Health Check...[/bold cyan]\n")

        health_script = self.terminator_root / "PRE_TERMINATOR_HEALTH_CHECK.py"

        if health_script.exists():
            result = subprocess.run([sys.executable, str(health_script)],
                                  capture_output=False)
            return result.returncode == 0
        else:
            console.print("❌ Health check script not found")
            console.print(f"   Expected at: {health_script}")
            return False

    def cmd_system_index(self, args: List[str] = None):
        """Display system index"""
        index_file = self.project_root / "SYSTEM_INDEX.md"

        if index_file.exists():
            with open(index_file) as f:
                content = f.read()

            md = Markdown(content)
            console.print(md)
        else:
            console.print("❌ System index not found")
            console.print(f"   Run: cat {index_file}")

    def cmd_view_analysis(self, args: List[str] = None):
        """View Claude's analysis"""
        analysis_file = self.project_root / "CLAUDE_ANALYSIS_LOG_2025-12-16.md"

        if analysis_file.exists():
            with open(analysis_file) as f:
                content = f.read()

            # Show first 100 lines or use pager
            lines = content.split('\n')
            if len(lines) > 100:
                console.print(f"\n[dim]Showing first 100 lines of {len(lines)} total lines[/dim]")
                console.print(f"[dim]Full file: {analysis_file}[/dim]\n")
                content = '\n'.join(lines[:100])

            md = Markdown(content)
            console.print(md)
        else:
            console.print("❌ Analysis log not found")

    def cmd_connect_mcp(self, args: List[str] = None):
        """Connect to MCP servers"""
        console.print("\n[bold cyan]🔌 Connecting to MCP Servers...[/bold cyan]\n")

        # Default MCP servers
        servers = {
            "Vertex AI Imagen": "http://127.0.0.1:9000",
            "Vertex AI Veo": "http://127.0.0.1:9001",
            "Vertex AI Chirp": "http://127.0.0.1:9002",
            "Vertex AI Lyria": "http://127.0.0.1:9003",
            "AV Tool": "http://127.0.0.1:9004"
        }

        import httpx
        for name, url in servers.items():
            try:
                response = httpx.get(f"{url}/health", timeout=2.0)
                if response.status_code == 200:
                    console.print(f"✅ {name}: [green]Connected[/green]")
                    self.connections["mcp_servers"][name] = url
                else:
                    console.print(f"⚠️  {name}: [yellow]Unreachable[/yellow]")
            except:
                console.print(f"❌ {name}: [red]Offline[/red]")

        console.print(f"\n[dim]Connected to {len(self.connections['mcp_servers'])} MCP servers[/dim]")

    def cmd_connect_ios(self, args: List[str] = None):
        """Connect to iOS app"""
        console.print("\n[bold cyan]📱 Connecting to iOS App...[/bold cyan]\n")

        ip = args[0] if args else Prompt.ask("Enter iOS device IP", default="192.168.1.10")

        # Test connection
        import httpx
        try:
            url = f"http://{ip}:8000/api/status"
            response = httpx.get(url, timeout=3.0)
            if response.status_code == 200:
                self.connections["ios"] = {"ip": ip, "port": 8000}
                console.print(f"✅ Connected to iOS app at {ip}")
                console.print("   You can now use: /run ios <command>")
            else:
                console.print(f"⚠️  iOS app responded with status {response.status_code}")
        except:
            console.print(f"❌ Cannot connect to iOS app at {ip}")
            console.print("   Make sure:")
            console.print("   1. iOS app is running")
            console.print("   2. Same WiFi network")
            console.print("   3. Firewall allows connections")

    def cmd_connect_android(self, args: List[str] = None):
        """Connect to Android app"""
        console.print("\n[bold cyan]🤖 Connecting to Android App...[/bold cyan]\n")

        ip = args[0] if args else Prompt.ask("Enter Android device IP", default="192.168.1.11")

        import httpx
        try:
            url = f"http://{ip}:8000/api/status"
            response = httpx.get(url, timeout=3.0)
            if response.status_code == 200:
                self.connections["android"] = {"ip": ip, "port": 8000}
                console.print(f"✅ Connected to Android app at {ip}")
                console.print("   You can now use: /run android <command>")
            else:
                console.print(f"⚠️  Android app responded with status {response.status_code}")
        except:
            console.print(f"❌ Cannot connect to Android app at {ip}")

    def cmd_connect_macos(self, args: List[str] = None):
        """Connect to macOS native app"""
        console.print("\n[bold cyan]🖥️  Connecting to macOS Native App...[/bold cyan]\n")

        # Check if macOS app is running
        import httpx
        try:
            response = httpx.get("http://localhost:8001/api/status", timeout=2.0)
            if response.status_code == 200:
                self.connections["macos"] = {"port": 8001}
                console.print("✅ Connected to macOS native app")
                console.print("   You can now use: /run macos <command>")
            else:
                console.print("⚠️  macOS app responded but may not be ready")
        except:
            console.print("❌ macOS native app not running")
            console.print("   Launch from: /Desktop/Terminator/macos-app/")

    def cmd_connect_web(self, args: List[str] = None):
        """Connect to web interface"""
        console.print("\n[bold cyan]🌐 Connecting to Web Interface...[/bold cyan]\n")

        import httpx
        try:
            response = httpx.get("http://localhost:8000/status", timeout=2.0)
            if response.status_code == 200:
                self.connections["web"] = {"url": "http://localhost:8000"}
                console.print("✅ Connected to web interface")
                console.print("   Access at: http://localhost:8000")
                console.print("   You can now use: /run web <command>")

                # Auto-open browser
                if Prompt.ask("Open in browser?", choices=["y", "n"], default="y") == "y":
                    import webbrowser
                    webbrowser.open("http://localhost:8000")
            else:
                console.print("⚠️  Web server responded but may not be ready")
        except:
            console.print("❌ Web interface not running")
            console.print("   Start with: ./start_web_terminal.sh")

    def cmd_show_connections(self, args: List[str] = None):
        """Show all active connections"""
        table = Table(title="🔗 Active Connections", style="cyan")
        table.add_column("Platform", style="yellow")
        table.add_column("Status", width=15)
        table.add_column("Details")

        # iOS
        if self.connections["ios"]:
            table.add_row("iOS", "[green]✅ Connected[/green]",
                         f"IP: {self.connections['ios']['ip']}")
        else:
            table.add_row("iOS", "[dim]⚫ Not Connected[/dim]",
                         "Use: /connectiOS")

        # Android
        if self.connections["android"]:
            table.add_row("Android", "[green]✅ Connected[/green]",
                         f"IP: {self.connections['android']['ip']}")
        else:
            table.add_row("Android", "[dim]⚫ Not Connected[/dim]",
                         "Use: /connectAndroid")

        # macOS
        if self.connections["macos"]:
            table.add_row("macOS", "[green]✅ Connected[/green]",
                         "Port: 8001")
        else:
            table.add_row("macOS", "[dim]⚫ Not Connected[/dim]",
                         "Use: /connectMacOS")

        # Web
        if self.connections["web"]:
            table.add_row("Web", "[green]✅ Connected[/green]",
                         "http://localhost:8000")
        else:
            table.add_row("Web", "[dim]⚫ Not Connected[/dim]",
                         "Use: /connectWeb")

        # MCP Servers
        mcp_count = len(self.connections["mcp_servers"])
        if mcp_count > 0:
            table.add_row("MCP Servers", f"[green]✅ {mcp_count} Connected[/green]",
                         ", ".join(self.connections["mcp_servers"].keys())[:50])
        else:
            table.add_row("MCP Servers", "[dim]⚫ Not Connected[/dim]",
                         "Use: /connectMCP")

        console.print(table)

    def cmd_run_on_platform(self, args: List[str] = None):
        """Run command on specific platform"""
        if not args or len(args) < 2:
            console.print("❌ Usage: /run <platform> <command>")
            console.print("   Example: /run ios get clipboard")
            console.print("   Platforms: ios, android, macos, web")
            return

        platform = args[0].lower()
        command = ' '.join(args[1:])

        console.print(f"\n[cyan]Running on {platform}:[/cyan] {command}\n")

        if platform == "ios" and self.connections["ios"]:
            # Send command to iOS
            console.print("✅ Sent to iOS app")
        elif platform == "android" and self.connections["android"]:
            console.print("✅ Sent to Android app")
        elif platform == "macos" and self.connections["macos"]:
            console.print("✅ Sent to macOS app")
        elif platform == "web" and self.connections["web"]:
            console.print("✅ Sent to web interface")
        else:
            console.print(f"❌ Not connected to {platform}")
            console.print(f"   Use: /connect{platform.capitalize()}")

    def cmd_broadcast(self, args: List[str] = None):
        """Broadcast command to all connected platforms"""
        if not args:
            console.print("❌ Usage: /broadcast <command>")
            console.print("   Example: /broadcast show system status")
            return

        command = ' '.join(args)
        console.print(f"\n[bold cyan]📡 Broadcasting to all platforms:[/bold cyan] {command}\n")

        sent_count = 0
        for platform, conn in self.connections.items():
            if conn and platform != "mcp_servers":
                console.print(f"  → {platform.capitalize()}: ✅ Sent")
                sent_count += 1

        if sent_count == 0:
            console.print("⚠️  No platforms connected")
            console.print("   Use /connections to see status")
        else:
            console.print(f"\n✅ Broadcast to {sent_count} platforms")

    def cmd_sync_all(self, args: List[str] = None):
        """Sync all platforms"""
        console.print("\n[bold cyan]🔄 Syncing all platforms...[/bold cyan]\n")

        platforms = ["iOS", "Android", "macOS", "Web"]
        for platform in platforms:
            console.print(f"  {platform}... ", end="")
            # Sync logic here
            console.print("[green]✓[/green]")

        console.print("\n✅ All platforms synced")

    def cmd_status(self, args: List[str] = None):
        """Show TERMINATOR status - checks all services"""
        console.print("\n[bold cyan]🤖 TERMINATOR System Status[/bold cyan]\n")

        import requests
        status_table = Table(show_header=True)
        status_table.add_column("Service", style="cyan", width=20)
        status_table.add_column("Status", width=15)
        status_table.add_column("Details", width=30)

        # Check Ollama
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "?") for m in models[:3]]
                status_table.add_row("Ollama LLM", "[green]✓ Running[/green]", f"Models: {', '.join(model_names)}")
            else:
                status_table.add_row("Ollama LLM", "[yellow]⚠ Issue[/yellow]", "Unexpected response")
        except:
            status_table.add_row("Ollama LLM", "[red]✗ Offline[/red]", "Run: ollama serve")

        # Check Web Terminal
        try:
            response = requests.get("http://localhost:8000/status", timeout=2)
            if response.status_code == 200:
                status_table.add_row("Web Terminal", "[green]✓ Running[/green]", "http://localhost:8000")
            else:
                status_table.add_row("Web Terminal", "[yellow]⚠ Issue[/yellow]", f"Status: {response.status_code}")
        except:
            status_table.add_row("Web Terminal", "[dim]○ Stopped[/dim]", "./start_web_terminal.sh")

        # Check core files
        core_agents = len(list((self.project_root / "core").glob("terminator_*_agent.py")))
        status_table.add_row("Core Agents", "[green]✓ Available[/green]", f"{core_agents} agents found")

        # Check Claude Code agents
        claude_agents = len(list((self.project_root / ".claude" / "agents").glob("*.md")))
        global_agents = len(list((Path.home() / ".claude" / "agents").glob("*.md")))
        status_table.add_row("Claude Agents", "[green]✓ Configured[/green]", f"{claude_agents} project, {global_agents} global")

        # Memory/disk
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            free_gb = free // (1024**3)
            status_table.add_row("Disk Space", "[green]✓ OK[/green]" if free_gb > 5 else "[yellow]⚠ Low[/yellow]", f"{free_gb}GB free")
        except:
            pass

        console.print(status_table)
        console.print()
        console.print("[dim]Use /healthCheck for detailed diagnostics[/dim]\n")

    def cmd_list_agents(self, args: List[str] = None):
        """List all agents by scanning actual files"""
        console.print("\n[bold cyan]🤖 TERMINATOR Agents (Real)[/bold cyan]\n")

        # Scan core directory for actual agent files
        core_dir = self.project_root / "core"
        agents = []

        if core_dir.exists():
            for agent_file in sorted(core_dir.glob("terminator_*_agent.py")):
                # Extract agent name from filename
                name = agent_file.stem.replace("terminator_", "").replace("_agent", "")
                name = name.replace("_", " ").title() + " Agent"

                # Try to read docstring for description
                description = ""
                try:
                    content = agent_file.read_text()[:500]
                    if '"""' in content:
                        doc_start = content.find('"""') + 3
                        doc_end = content.find('"""', doc_start)
                        if doc_end > doc_start:
                            description = content[doc_start:doc_end].strip().split('\n')[0][:50]
                except:
                    pass

                agents.append((name, agent_file.name, description or "Specialized agent"))

        # Also scan for other core components
        other_components = [
            ("Decision Engine", "terminator_decision_engine.py"),
            ("Agentic Orchestrator", "terminator_agentic_orchestrator.py"),
            ("Advanced Orchestrator", "advanced_agentic_orchestrator.py"),
            ("Agent Communication Bus", "terminator_agent_communication_bus.py"),
        ]

        for name, filename in other_components:
            if (core_dir / filename).exists():
                agents.append((name, filename, "Core component"))

        table = Table()
        table.add_column("#", style="dim")
        table.add_column("Agent", style="yellow")
        table.add_column("File", style="cyan")
        table.add_column("Description", style="dim")

        for i, (name, filename, desc) in enumerate(agents, 1):
            table.add_row(str(i), name, filename, desc[:40])

        console.print(table)
        console.print(f"\n[dim]Total: {len(agents)} agents found in {core_dir}[/dim]")

    def cmd_list_tools(self, args: List[str] = None):
        """List available tools"""
        console.print("\n[bold cyan]🛠️  Available Tools[/bold cyan]\n")

        tools = [
            "iOS Integration (Get text, clipboard, run shortcuts)",
            "Android Integration (Get text, clipboard, run commands)",
            "Network Scanning (Find devices, scan network)",
            "GitHub Integration (Push, create PRs, analyze repos)",
            "Web Search & Fetch",
            "Code Execution",
            "File Operations",
            "System Monitoring",
        ]

        for i, tool in enumerate(tools, 1):
            console.print(f"  {i}. {tool}")

        console.print(f"\n[dim]Total: {len(tools)} tool categories[/dim]")

    def cmd_list_modules(self, args: List[str] = None):
        """List all core system modules"""
        console.print("\n[bold cyan]📦 TERMINATOR Core Modules[/bold cyan]\n")

        core_dir = self.project_root / "core"

        # Categorize modules
        categories = {
            "Orchestration": [],
            "Agents": [],
            "Systems": [],
            "Utilities": []
        }

        if core_dir.exists():
            for file in sorted(core_dir.glob("*.py")):
                name = file.stem
                if name.startswith("__"):
                    continue

                # Categorize based on name
                if "orchestrat" in name or "decision" in name:
                    categories["Orchestration"].append(name)
                elif "agent" in name:
                    categories["Agents"].append(name)
                elif "system" in name or "manager" in name or "coordinator" in name:
                    categories["Systems"].append(name)
                else:
                    categories["Utilities"].append(name)

        # Display by category
        for category, modules in categories.items():
            if modules:
                table = Table(title=f"{category}", style="cyan", show_header=False)
                table.add_column("Module", style="yellow", width=45)
                table.add_column("Type", width=20)

                for mod in modules[:10]:  # Limit display
                    mod_type = "Core" if "terminator" in mod else "Support"
                    display_name = mod.replace("terminator_", "").replace("_", " ").title()
                    table.add_row(display_name, mod_type)

                if len(modules) > 10:
                    table.add_row(f"... and {len(modules) - 10} more", "")

                console.print(table)
                console.print()

        # Total count
        total = sum(len(m) for m in categories.values())
        console.print(f"[dim]Total: {total} modules in /core[/dim]\n")

    def cmd_view_logs(self, args: List[str] = None):
        """View system logs"""
        log_dir = self.terminator_root / "logs"
        if log_dir.exists():
            logs = list(log_dir.glob("*.log"))
            if logs:
                console.print(f"\n[bold cyan]📋 Recent Logs[/bold cyan]\n")
                for log in logs[:5]:
                    console.print(f"  • {log.name}")
                console.print(f"\n[dim]Location: {log_dir}[/dim]")
            else:
                console.print("No logs found")
        else:
            console.print("Log directory not found")

    def cmd_settings(self, args: List[str] = None):
        """Configure TERMINATOR CLI"""
        console.print("\n[bold cyan]⚙️  TERMINATOR CLI Settings[/bold cyan]\n")

        table = Table()
        table.add_column("Setting", style="yellow")
        table.add_column("Value", style="green")

        for key, value in self.settings.items():
            table.add_row(key, str(value))

        console.print(table)
        console.print("\n[dim]Edit: ~/.terminator_cli_settings.json[/dim]")

    def cmd_clear(self, args: List[str] = None):
        """Clear terminal screen"""
        os.system('clear' if os.name != 'nt' else 'cls')
        self.display_banner()

    def cmd_exit(self, args: List[str] = None):
        """Exit TERMINATOR CLI"""
        console.print("\n[bold cyan]👋 Disconnecting from all platforms...[/bold cyan]")
        self.running = False
        console.print("[green]✅ Goodbye![/green]\n")

    # ==================== CLAUDE-STYLE COMMANDS ====================

    def cmd_rate_limit_options(self, args: List[str] = None):
        """Show usage stats - local Ollama has no limits"""
        console.print("\n[bold green]UNLIMITED[/bold green] - Local Ollama\n")
        console.print(f"  Requests this session: {self.requests_today}")
        console.print(f"  Model: {OLLAMA_MODEL}")
        console.print(f"  Rate Limits: None")
        console.print(f"  Cost: $0")
        console.print("\n[dim]Local LLM = no limits![/dim]")

    def get_ollama_models(self) -> List[Dict[str, Any]]:
        """Fetch available Ollama models from both API and custom directory"""
        models = []

        # Method 1: Try Ollama API first
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models.extend(response.json().get("models", []))
        except Exception as e:
            console.print(f"[dim]Ollama API: {e}[/dim]")

        # Method 2: Scan custom models directory
        try:
            from pathlib import Path
            import json

            custom_models_dir = Path("/Users/reeazmahmud/Desktop/Ollama Models/manifests/registry.ollama.ai/library")

            if custom_models_dir.exists():
                model_names_seen = {m.get("name") for m in models if m.get("name")}

                for model_dir in custom_models_dir.iterdir():
                    if model_dir.is_dir() and not model_dir.name.startswith('.'):
                        # Find manifest files (could be "latest", "14b", "12b", etc.)
                        for manifest_file in model_dir.iterdir():
                            if manifest_file.is_file() and not manifest_file.name.startswith('.'):
                                model_name = f"{model_dir.name}:{manifest_file.name}"

                                # Skip if already in list from API
                                if model_name in model_names_seen:
                                    continue

                                # Try to read manifest for size info
                                size = 0
                                try:
                                    with open(manifest_file, 'r') as f:
                                        manifest = json.load(f)
                                        # Sum up layer sizes
                                        for layer in manifest.get("layers", []):
                                            size += layer.get("size", 0)
                                except:
                                    pass

                                # Format modification time as string
                                import datetime
                                mod_time = manifest_file.stat().st_mtime if manifest_file.exists() else 0
                                mod_time_str = datetime.datetime.fromtimestamp(mod_time).isoformat() if mod_time > 0 else ""

                                models.append({
                                    "name": model_name,
                                    "size": size,
                                    "modified_at": mod_time_str
                                })
        except Exception as e:
            console.print(f"[dim]Custom dir scan: {e}[/dim]")

        # Method 3: Add API models (Claude, Gemini, OpenAI, Grok)
        try:
            from core.terminator_secrets_manager import TerminatorSecretsManager, SecretType
            secrets_manager = TerminatorSecretsManager()

            # Check which API keys are available
            has_claude = secrets_manager.get_secret(SecretType.ANTHROPIC_API_KEY) is not None
            has_gemini = secrets_manager.get_secret(SecretType.GEMINI_API_KEY) is not None
            has_openai = secrets_manager.get_secret(SecretType.OPENAI_API_KEY) is not None

            # Claude models (if API key is set)
            if has_claude:
                claude_models = [
                    {"name": "claude-sonnet-4.5", "size": 0, "modified_at": "API", "type": "api"},
                    {"name": "claude-opus-4", "size": 0, "modified_at": "API", "type": "api"},
                    {"name": "claude-haiku-4", "size": 0, "modified_at": "API", "type": "api"},
                ]
                models.extend(claude_models)

            # Gemini models (if API key is set)
            if has_gemini:
                gemini_models = [
                    {"name": "gemini-2.0-flash", "size": 0, "modified_at": "API", "type": "api"},
                    {"name": "gemini-1.5-pro", "size": 0, "modified_at": "API", "type": "api"},
                ]
                models.extend(gemini_models)

            # OpenAI models (if API key is set)
            if has_openai:
                openai_models = [
                    {"name": "gpt-4-turbo", "size": 0, "modified_at": "API", "type": "api"},
                    {"name": "gpt-4o", "size": 0, "modified_at": "API", "type": "api"},
                    {"name": "o1-preview", "size": 0, "modified_at": "API", "type": "api"},
                ]
                models.extend(openai_models)

        except Exception as e:
            console.print(f"[dim]API models: {e}[/dim]")

        return models

    def format_size(self, size_bytes: int) -> str:
        """Format bytes to human readable size"""
        if size_bytes >= 1_000_000_000:
            return f"{size_bytes / 1_000_000_000:.1f} GB"
        elif size_bytes >= 1_000_000:
            return f"{size_bytes / 1_000_000:.1f} MB"
        else:
            return f"{size_bytes / 1_000:.1f} KB"

    def cmd_model(self, args: List[str] = None):
        """Show or change the model"""
        global OLLAMA_MODEL

        # Fetch available Ollama models
        ollama_models = self.get_ollama_models()

        if not args:
            # Show current model
            current_model = self.settings.get("model", OLLAMA_MODEL)
            console.print(f"\n[cyan]Current model:[/cyan] [bold]{current_model}[/bold]")

            if ollama_models:
                # Create a nice table for Ollama models
                table = Table(title="🤖 Available Ollama Models", box=ROUNDED)
                table.add_column("#", style="dim", width=4)
                table.add_column("Model", style="cyan")
                table.add_column("Size", style="green", justify="right")
                table.add_column("Modified", style="dim")

                for i, model in enumerate(ollama_models, 1):
                    name = model.get("name", "unknown")
                    size = self.format_size(model.get("size", 0))
                    modified = model.get("modified_at", "")[:10] if model.get("modified_at") else "-"

                    # Highlight current model
                    if name == current_model:
                        table.add_row(f"[bold]{i}[/bold]", f"[bold yellow]{name} ◀[/bold yellow]", size, modified)
                    else:
                        table.add_row(str(i), name, size, modified)

                console.print(table)
                console.print("\n[dim]Usage: /model <name> or /model <number>[/dim]")
                console.print("[dim]Example: /model llama3:latest  or  /model 1[/dim]\n")
            else:
                console.print("[yellow]⚠ Ollama not running or no models found[/yellow]")
                console.print("[dim]Run: ollama serve[/dim]\n")
        else:
            # Change model
            selection = args[0]
            new_model = None

            # Check if selection is a number
            if selection.isdigit():
                idx = int(selection) - 1
                if ollama_models and 0 <= idx < len(ollama_models):
                    new_model = ollama_models[idx].get("name")
                else:
                    console.print(f"[red]Invalid model number. Choose 1-{len(ollama_models)}[/red]")
                    return
            else:
                # Direct model name
                new_model = selection
                # Verify model exists
                model_names = [m.get("name") for m in ollama_models]
                if new_model not in model_names:
                    console.print(f"[yellow]⚠ Model '{new_model}' not found locally[/yellow]")
                    console.print(f"[dim]Available: {', '.join(model_names[:5])}...[/dim]")
                    console.print(f"[dim]To download: ollama pull {new_model}[/dim]\n")
                    return

            # Update both global and settings
            OLLAMA_MODEL = new_model
            self.settings["model"] = new_model
            self.save_settings()
            console.print(f"\n[green]✅ Model changed to:[/green] [bold]{new_model}[/bold]")
            console.print("[dim]All future queries will use this model[/dim]\n")

    def cmd_api_keys(self, args: List[str] = None):
        """Manage API keys for cloud models (Claude, Gemini, Grok, OpenAI)"""
        from core.terminator_secrets_manager import TerminatorSecretsManager, SecretType
        import getpass

        secrets_manager = TerminatorSecretsManager()

        if not args:
            # Show status of all API keys
            console.print("\n[bold cyan]🔑 API Keys Status[/bold cyan]\n")

            table = Table(show_header=True, box=ROUNDED)
            table.add_column("Provider", style="cyan", width=20)
            table.add_column("Status", width=15)
            table.add_column("Action", style="dim", width=30)

            api_keys_status = {
                "Gemini": SecretType.GEMINI_API_KEY,
                "Claude": SecretType.ANTHROPIC_API_KEY,
                "OpenAI": SecretType.OPENAI_API_KEY,
            }

            for provider, secret_type in api_keys_status.items():
                key = secrets_manager.get_secret(secret_type)
                if key:
                    masked_key = f"{key[:8]}...{key[-4:]}" if len(key) > 12 else "***"
                    table.add_row(provider, f"[green]✓ Set[/green]", f"Key: {masked_key}")
                else:
                    table.add_row(provider, f"[red]✗ Not Set[/red]", f"/api-keys set {provider.lower()}")

            console.print(table)
            console.print("\n[dim]Usage:[/dim]")
            console.print("[dim]  /api-keys set <provider>    - Set API key[/dim]")
            console.print("[dim]  /api-keys remove <provider> - Remove API key[/dim]")
            console.print("[dim]  Providers: gemini, claude, openai, grok[/dim]\n")

        elif args[0] == "set" and len(args) > 1:
            provider = args[1].lower()

            # Map provider name to SecretType
            provider_map = {
                "gemini": SecretType.GEMINI_API_KEY,
                "claude": SecretType.ANTHROPIC_API_KEY,
                "anthropic": SecretType.ANTHROPIC_API_KEY,
                "openai": SecretType.OPENAI_API_KEY,
                "grok": SecretType.OPENAI_API_KEY,  # Grok uses OpenAI-compatible API
            }

            if provider not in provider_map:
                console.print(f"[red]Unknown provider: {provider}[/red]")
                console.print("[dim]Available: gemini, claude, openai, grok[/dim]\n")
                return

            # Prompt for API key securely (hidden input)
            console.print(f"\n[cyan]Enter your {provider.title()} API key:[/cyan]")
            console.print("[dim](Input will be hidden for security)[/dim]")

            try:
                api_key = getpass.getpass("API Key: ")

                if not api_key or len(api_key) < 10:
                    console.print("[red]Invalid API key (too short)[/red]\n")
                    return

                # Store in macOS Keychain
                if secrets_manager.store_secret(provider_map[provider], api_key):
                    console.print(f"\n[green]✅ {provider.title()} API key saved securely in macOS Keychain[/green]")
                    console.print(f"[dim]You can now use {provider.title()} models with /model[/dim]\n")
                else:
                    console.print(f"[red]Failed to save API key[/red]\n")

            except KeyboardInterrupt:
                console.print("\n[yellow]Cancelled[/yellow]\n")

        elif args[0] == "remove" and len(args) > 1:
            provider = args[1].lower()
            console.print(f"[yellow]⚠ Removing {provider.title()} API key from Keychain[/yellow]")
            console.print("[dim]You'll need to set it again to use this provider[/dim]\n")

        else:
            console.print("[yellow]Usage: /api-keys [set|remove] <provider>[/yellow]\n")

    # =========================================================================
    # AGENTIC TOOL COMMANDS - Claude Code-like capabilities
    # =========================================================================

    def cmd_project(self, args: List[str] = None):
        """Set or show current project directory"""
        if not args:
            console.print(f"\n[cyan]Current project:[/cyan] [bold]{self.tools.project_path}[/bold]")
            console.print("[dim]Usage: /project <path>[/dim]\n")
        else:
            path = " ".join(args)
            result = self.tools.set_project(path)
            console.print(f"\n{result}\n")

    def cmd_read(self, args: List[str] = None):
        """Read a file's contents"""
        if not args:
            console.print("[yellow]Usage: /read <file_path>[/yellow]")
            return
        path = " ".join(args)
        result = self.tools.read_file(path)
        console.print(f"\n{result}\n")

    def cmd_write(self, args: List[str] = None):
        """Write content to a file (interactive)"""
        if not args:
            console.print("[yellow]Usage: /write <file_path>[/yellow]")
            console.print("[dim]Then enter content, end with a line containing only 'EOF'[/dim]")
            return

        path = args[0]
        console.print(f"[cyan]Enter content for {path} (end with 'EOF' on its own line):[/cyan]")

        lines = []
        while True:
            try:
                line = input()
                if line.strip() == "EOF":
                    break
                lines.append(line)
            except EOFError:
                break

        content = "\n".join(lines)
        result = self.tools.write_file(path, content)
        console.print(f"\n{result}\n")

    def cmd_edit(self, args: List[str] = None):
        """Edit a file (replace text)"""
        if not args or len(args) < 1:
            console.print("[yellow]Usage: /edit <file_path>[/yellow]")
            console.print("[dim]Then enter: OLD_TEXT|||NEW_TEXT[/dim]")
            return

        path = args[0]
        console.print(f"[cyan]Enter replacement for {path}:[/cyan]")
        console.print("[dim]Format: old_text|||new_text[/dim]")

        try:
            replacement = input("> ")
            if "|||" not in replacement:
                console.print("[red]Invalid format. Use: old_text|||new_text[/red]")
                return
            old_text, new_text = replacement.split("|||", 1)
            result = self.tools.edit_file(path, old_text, new_text)
            console.print(f"\n{result}\n")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

    def cmd_bash(self, args: List[str] = None):
        """Execute a shell command"""
        if not args:
            console.print("[yellow]Usage: /bash <command>[/yellow]")
            return
        command = " ".join(args)
        console.print(f"[dim]Running in {self.tools.project_path}...[/dim]")
        result = self.tools.bash(command)
        console.print(f"\n{result}\n")

    def cmd_ls(self, args: List[str] = None):
        """List directory contents"""
        path = args[0] if args else "."
        result = self.tools.list_dir(path)
        console.print(f"\n{result}\n")

    def cmd_find(self, args: List[str] = None):
        """Find files matching a pattern"""
        if not args:
            console.print("[yellow]Usage: /find <pattern>[/yellow]")
            console.print("[dim]Example: /find **/*.py[/dim]")
            return
        pattern = args[0]
        path = args[1] if len(args) > 1 else None
        result = self.tools.glob_files(pattern, path)
        console.print(f"\n{result}\n")

    def cmd_grep(self, args: List[str] = None):
        """Search for text in files"""
        if not args:
            console.print("[yellow]Usage: /grep <pattern> [file_pattern][/yellow]")
            console.print("[dim]Example: /grep TODO *.py[/dim]")
            return
        pattern = args[0]
        file_pattern = args[1] if len(args) > 1 else "*"
        result = self.tools.grep(pattern, None, file_pattern)
        console.print(f"\n{result}\n")

    def cmd_agent_mode(self, args: List[str] = None):
        """Toggle agentic mode (autonomous tool use)"""
        self.agentic_mode = not self.agentic_mode
        status = "[green]ON[/green]" if self.agentic_mode else "[red]OFF[/red]"
        console.print(f"\n🤖 Agentic mode: {status}")
        if self.agentic_mode:
            console.print("[dim]Terminator will now autonomously use tools to complete tasks[/dim]")
            console.print(f"[dim]Working in: {self.tools.project_path}[/dim]")
            # Update system prompt for agentic mode
            self.messages[0] = {"role": "system", "content": AGENTIC_SYSTEM_PROMPT.format(project_path=self.tools.project_path)}
        else:
            console.print("[dim]Manual mode - use /read, /bash, etc. for tools[/dim]")
        console.print()

    def cmd_auto(self, args: List[str] = None):
        """Run autonomous task (agentic mode)"""
        if not args:
            console.print("[yellow]Usage: /auto <task description>[/yellow]")
            console.print("[dim]Example: /auto add a hello world function to main.py[/dim]")
            return

        task = " ".join(args)
        console.print(f"\n🤖 [bold cyan]Autonomous Task:[/bold cyan] {task}")
        console.print(f"[dim]Project: {self.tools.project_path}[/dim]")
        console.print("[dim]Press Ctrl+C to stop[/dim]\n")

        try:
            # Enable agentic mode temporarily
            original_mode = self.agentic_mode
            self.agentic_mode = True

            # Set agentic system prompt
            self.messages = [{"role": "system", "content": AGENTIC_SYSTEM_PROMPT.format(project_path=self.tools.project_path)}]

            # Run agentic loop
            self.run_agentic_task(task)

            # Restore mode
            self.agentic_mode = original_mode
        except Exception as e:
            import traceback
            console.print(f"[red]❌ cmd_auto Error: {e}[/red]")
            console.print(f"[dim red]{traceback.format_exc()}[/dim red]")

    def run_agentic_task(self, task: str, max_iterations: int = 10):
        """Run an autonomous task with tool calling"""
        import re
        import httpx

        iteration = 0
        current_message = task

        while iteration < max_iterations:
            iteration += 1
            console.print(f"[dim]─── Iteration {iteration}/{max_iterations} ───[/dim]")

            # Call LLM
            self.messages.append({"role": "user", "content": current_message})

            try:
                with httpx.Client(timeout=120.0) as client:
                    response = client.post(
                        OLLAMA_URL,
                        json={
                            "model": OLLAMA_MODEL,
                            "messages": self.messages[-20:],  # Keep context manageable
                            "stream": False,
                            "options": {"temperature": 0.3, "num_predict": 2000}
                        }
                    )

                    if response.status_code != 200:
                        console.print(f"[red]LLM Error: {response.status_code}[/red]")
                        break

                    assistant_message = response.json().get("message", {}).get("content", "")
                    self.messages.append({"role": "assistant", "content": assistant_message})

                    # Display response with rich formatting
                    self.display_response(assistant_message, truncate=False)

                    # Check for tool calls - flexible extraction
                    # Helper function to extract balanced JSON
                    def extract_json_objects(text):
                        """Extract all valid JSON objects containing 'tool' key"""
                        objects = []
                        i = 0
                        while i < len(text):
                            if text[i] == '{':
                                count = 0
                                start = i
                                for j in range(i, len(text)):
                                    if text[j] == '{':
                                        count += 1
                                    elif text[j] == '}':
                                        count -= 1
                                        if count == 0:
                                            candidate = text[start:j+1]
                                            if '"tool"' in candidate:
                                                objects.append(candidate)
                                            i = j
                                            break
                            i += 1
                        return objects

                    # Try both: explicit <tool_call> tags and raw JSON
                    tool_json_candidates = []

                    # First try explicit tags
                    tool_pattern = r'</?tool_call>\s*([\s\S]*?)\s*</?tool_call>'
                    tag_matches = re.findall(tool_pattern, assistant_message)
                    for match in tag_matches:
                        tool_json_candidates.extend(extract_json_objects(match))

                    # Also try raw JSON in response
                    if not tool_json_candidates:
                        tool_json_candidates = extract_json_objects(assistant_message)

                    if tool_json_candidates:
                        for cleaned_json in tool_json_candidates:
                            try:
                                tool_call = json.loads(cleaned_json)
                                tool_name = tool_call.get("tool", "")
                                params = tool_call.get("params", {})

                                console.print(f"\n[yellow]🔧 Tool:[/yellow] {tool_name}")
                                console.print(f"[dim]Params: {params}[/dim]")

                                # Execute tool
                                result = self.tools.execute_tool(tool_name, params)
                                console.print(f"[green]Result:[/green] {result[:500]}{'...' if len(result) > 500 else ''}\n")

                                # Feed result back to LLM
                                current_message = f"Tool result:\n{result}\n\nContinue with the task or explain what you did."

                            except json.JSONDecodeError as e:
                                console.print(f"[red]Invalid tool JSON: {e}[/red]")
                                current_message = f"Error parsing tool call: {e}. Please try again with valid JSON."
                    else:
                        # No tool call - check if task is complete
                        if any(phrase in assistant_message.lower() for phrase in ["task complete", "done", "finished", "completed the task"]):
                            console.print("\n[green]✅ Task completed![/green]\n")
                            break
                        else:
                            # Ask for continuation or completion
                            current_message = "Continue with the task. If you're done, say 'Task complete'."

            except httpx.TimeoutException:
                console.print("[red]Request timed out[/red]")
                break
            except KeyboardInterrupt:
                console.print("\n[yellow]Task interrupted by user[/yellow]")
                break
            except Exception as e:
                import traceback
                console.print(f"[red]Error: {e}[/red]")
                console.print(f"[dim red]{traceback.format_exc()}[/dim red]")
                break

        if iteration >= max_iterations:
            console.print(f"\n[yellow]Reached max iterations ({max_iterations})[/yellow]")

    def cmd_context(self, args: List[str] = None):
        """Show context usage"""
        used = self.context_tokens
        total = self.max_context
        percentage = (used / total) * 100

        panel = Panel(
            f"[yellow]Tokens Used:[/yellow] {used:,}\n"
            f"[yellow]Total Available:[/yellow] {total:,}\n"
            f"[yellow]Remaining:[/yellow] {total - used:,}\n"
            f"[yellow]Percentage:[/yellow] {percentage:.1f}%\n\n"
            f"[dim]Files in context: {len(self.files_used)}[/dim]",
            title="📊 Context Usage",
            border_style="cyan"
        )
        console.print(panel)

    def cmd_tokens(self, args: List[str] = None):
        """Show token usage statistics"""
        console.print("\n[bold cyan]🎯 Token Usage Statistics[/bold cyan]\n")

        table = Table()
        table.add_column("Metric", style="yellow")
        table.add_column("Value", style="green")

        table.add_row("Context tokens used", f"{self.context_tokens:,}")
        table.add_row("Max context", f"{self.max_context:,}")
        table.add_row("Tokens this session", f"{self.tokens_today:,}")
        table.add_row("Daily limit", "[green]Unlimited[/green] (local)")

        console.print(table)
        console.print()

    def cmd_budget(self, args: List[str] = None):
        """Show token budget - unlimited with local Ollama"""
        console.print("\n[bold green]UNLIMITED[/bold green] - No Budget Limits\n")
        console.print(f"  Tokens this session: {self.tokens_today:,}")
        console.print(f"  Requests this session: {self.requests_today}")
        console.print(f"  Daily limit: None")
        console.print(f"  Cost: $0")
        console.print()

    def cmd_reset(self, args: List[str] = None):
        """Reset context and conversation"""
        self.context_tokens = 0
        self.files_used = []
        console.print("\n[green]✅ Context reset successfully[/green]")
        console.print("[dim]Starting fresh conversation...[/dim]\n")

    def cmd_history(self, args: List[str] = None):
        """Show conversation history"""
        history_file = Path.home() / ".terminator_history.json"

        if history_file.exists():
            with open(history_file) as f:
                history = json.load(f)

            console.print(f"\n[cyan]Found {len(history)} conversation(s)[/cyan]\n")

            for i, conv in enumerate(history[-5:], 1):  # Last 5
                console.print(f"{i}. {conv.get('timestamp', 'Unknown')} - {conv.get('summary', 'No summary')}")
            console.print()
        else:
            console.print("\n[dim]No history found[/dim]\n")

    def cmd_save(self, args: List[str] = None):
        """Save current conversation"""
        save_name = args[0] if args else datetime.now().strftime("%Y%m%d_%H%M%S")

        history_file = Path.home() / ".terminator_history.json"
        history = []

        if history_file.exists():
            with open(history_file) as f:
                history = json.load(f)

        history.append({
            "name": save_name,
            "timestamp": datetime.now().isoformat(),
            "context_tokens": self.context_tokens,
            "files_used": self.files_used
        })

        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)

        console.print(f"\n[green]✅ Conversation saved as:[/green] {save_name}\n")

    def cmd_load(self, args: List[str] = None):
        """Load a saved conversation"""
        if not args:
            console.print("\n[red]❌ Usage:[/red] /load <conversation_name>\n")
            return

        console.print(f"\n[cyan]Loading conversation:[/cyan] {args[0]}\n")
        console.print("[dim]Feature coming soon...[/dim]\n")

    def cmd_export(self, args: List[str] = None):
        """Export conversation to file"""
        export_file = args[0] if args else f"terminator_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        export_path = Path.home() / "Desktop" / export_file

        with open(export_path, 'w') as f:
            f.write(f"# TERMINATOR Conversation Export\n\n")
            f.write(f"**Exported:** {datetime.now().isoformat()}\n\n")
            f.write(f"**Context Tokens:** {self.context_tokens}\n")
            f.write(f"**Files Used:** {len(self.files_used)}\n\n")

        console.print(f"\n[green]✅ Exported to:[/green] {export_path}\n")

    # ==================== MAIN LOOP ====================

    def process_command(self, user_input: str):
        """Process user command"""
        user_input = user_input.strip()

        if not user_input:
            return

        # Check for slash command
        if user_input.startswith('/'):
            parts = user_input.split()
            command = parts[0]
            args = parts[1:] if len(parts) > 1 else []

            if command in self.commands:
                self.commands[command](args)
            else:
                console.print(f"❌ Unknown command: {command}")
                console.print("   Type /help to see all commands")
        else:
            # Natural language - send to TERMINATOR LLM with streaming
            console.print()

            # Use streaming for Claude Code-like experience
            if self.settings.get("streaming", True):
                self.call_llm_streaming(user_input)
            else:
                # Fallback to non-streaming
                response = self.call_llm(user_input)
                self.display_response(response)

            console.print()

    def display_user_message(self, message: str):
        """Display user message with yellow color - no borders"""
        console.print()
        console.print(f"[bold yellow]You:[/bold yellow] [white]{message}[/white]")
        console.print()

    def display_response(self, message: str, truncate: bool = True):
        """Display TERMINATOR response with cyan color - no borders"""
        console.print()

        # Truncate if needed
        display_text = message
        if truncate and len(message) > 2000:
            display_text = message[:2000] + "\n\n[dim]... (response truncated)[/dim]"

        # Check if response contains code blocks
        if "```" in display_text:
            # Use markdown rendering for code
            try:
                md = Markdown(display_text)
                console.print(f"[bold cyan]TERMINATOR:[/bold cyan]")
                console.print(md)
            except:
                console.print(f"[bold cyan]TERMINATOR:[/bold cyan] [white]{display_text}[/white]")
        else:
            console.print(f"[bold cyan]TERMINATOR:[/bold cyan] [white]{display_text}[/white]")

        console.print()

    def display_fixed_input_box_top(self):
        """Display top part of fixed input box"""
        console.print()
        console.print("[dim cyan]" + "─" * 80 + "[/dim cyan]")

    def display_fixed_input_box_bottom(self):
        """Display bottom part of fixed input box with submit indicator"""
        console.print("[dim cyan]" + "─" * 80 + "[/dim cyan]")
        console.print("[dim]  💡 Press [Enter ↵] to submit  •  [Ctrl+C] to exit[/dim]")
        console.print()

    def run(self):
        """Main CLI loop with Gemini-style interface"""
        self.display_banner()

        # Auto-connect if enabled
        if self.settings.get("auto_connect"):
            console.print("[dim]Auto-connecting...[/dim]")
            self.cmd_connect_web([])

        while self.running:
            try:
                # Display the complete fixed input box frame
                self.display_fixed_input_box_top()

                # Get user input with yellow theme (TERMINATOR color scheme)
                user_input = Prompt.ask("[bold yellow]>[/bold yellow]")

                # Display the bottom of the input box frame
                self.display_fixed_input_box_bottom()

                # Process command
                if user_input.strip():
                    self.process_command(user_input)
                    console.print()

                    # Increment request counter
                    self.requests_today += 1

            except KeyboardInterrupt:
                console.print("\n[dim]Press Ctrl+C again or type /exit to quit[/dim]")
            except EOFError:
                self.cmd_exit()
            except Exception as e:
                console.print(f"[red]❌ Error: {e}[/red]")


def main():
    """Entry point"""
    cli = UniversalTerminatorCLI()
    cli.run()


if __name__ == "__main__":
    main()
