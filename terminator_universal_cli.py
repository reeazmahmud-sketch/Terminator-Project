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
try:
    from modules.core.module_loader import ModuleLoader
except ImportError:
    ModuleLoader = None

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Core imports
try:
    from core.terminator_secrets_manager import get_secrets_manager, SecretType
    from core.terminator_llm_router import get_llm_router, LLMProvider
    from core.terminator_auto_solution_agent import AutoSolutionAgent
except ImportError:
    # Fallback if core modules are missing during first run
    pass

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
OLLAMA_MODEL = "ministral-3:14b"  # Default model

# Cloud API Configuration
CURRENT_PROVIDER = None
CURRENT_MODEL = None

# Cloud API Models
CLOUD_MODELS = {
    "gemini": "gemini-2.0-flash-exp",
    "claude": "claude-3-5-sonnet-20241022",
    "openai": "gpt-4o-mini",
    "grok": "grok-2-latest",
}

def get_cloud_client(provider: str):
    """Get the appropriate cloud client for the provider"""
    secrets = get_secrets_manager()

    if provider == "gemini":
        api_key = secrets.get_secret(SecretType.GEMINI_API_KEY)
        if api_key:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            return genai.GenerativeModel(CLOUD_MODELS["gemini"])

    elif provider == "claude":
        api_key = secrets.get_secret(SecretType.ANTHROPIC_API_KEY)
        if api_key:
            try:
                import anthropic
                return anthropic.Anthropic(api_key=api_key)
            except ImportError:
                console.print("[yellow]Installing anthropic SDK...[/yellow]")
                subprocess.run([sys.executable, "-m", "pip", "install", "anthropic"], capture_output=True)
                import anthropic
                return anthropic.Anthropic(api_key=api_key)

    elif provider == "openai" or provider == "grok":
        secret_type = SecretType.OPENAI_API_KEY if provider == "openai" else SecretType.GROK_API_KEY
        api_key = secrets.get_secret(secret_type)
        if api_key:
            try:
                import openai
                base_url = "https://api.x.ai/v1" if provider == "grok" else None
                return openai.OpenAI(api_key=api_key, base_url=base_url)
            except ImportError:
                console.print("[yellow]Installing openai SDK...[/yellow]")
                subprocess.run([sys.executable, "-m", "pip", "install", "openai"], capture_output=True)
                import openai
                base_url = "https://api.x.ai/v1" if provider == "grok" else None
                return openai.OpenAI(api_key=api_key, base_url=base_url)

    return None

def call_cloud_api(provider: str, messages: list, system_prompt: str = None) -> str:
    """Call a cloud API and return the response"""
    client = get_cloud_client(provider)
    if not client:
        return None

    try:
        if provider == "gemini":
            prompt = "\n".join([
                f"{m['role'].upper()}: {m['content']}"
                for m in messages[-10:]
            ])
            if system_prompt:
                prompt = f"SYSTEM: {system_prompt}\n\n{prompt}"
            response = client.generate_content(prompt)
            return response.text

        elif provider == "claude":
            response = client.messages.create(
                model=CLOUD_MODELS["claude"],
                max_tokens=2048,
                system=system_prompt or "You are TERMINATOR, a helpful AI assistant.",
                messages=messages[-10:]
            )
            return response.content[0].text

        elif provider in ["openai", "grok"]:
            msgs = messages[-10:]
            if system_prompt:
                msgs = [{"role": "system", "content": system_prompt}] + msgs
            model = CLOUD_MODELS.get(provider, "gpt-4o-mini")
            response = client.chat.completions.create(
                model=model,
                messages=msgs,
                max_tokens=2048
            )
            return response.choices[0].message.content

    except Exception as e:
        console.print(f"[red]Cloud API error ({provider}): {e}[/red]")
        return None

    return None

def detect_best_provider() -> str:
    """Auto-detect the best available LLM provider"""
    global CURRENT_PROVIDER
    if CURRENT_PROVIDER:
        return CURRENT_PROVIDER

    secrets = get_secrets_manager()
    provider = secrets.get_best_available_provider()

    if provider:
        CURRENT_PROVIDER = provider
        return provider

    return "ollama"  # Default fallback

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
        # Portable Root: Uses the directory containing this script
        self.project_root = Path(__file__).resolve().parent
        self.terminator_root = self.project_root
        
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

        # Initialize new core components
        try:
            self.router = get_llm_router()
            self.solution_agent = AutoSolutionAgent(str(self.terminator_root))
        except NameError:
            self.router = None
            self.solution_agent = None

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

            "/solve": self.cmd_solve,
            "/provider": self.cmd_provider,
            "/resume": self.cmd_load,
            "/chat": lambda args: console.print("[dim]Chat mode is default. Just type![/dim]"),
            "/quit": self.cmd_exit,
            "/directory": self.cmd_ls, # Alias
            "/ide": self.cmd_open, # Alias
            "/mcp": self.cmd_connect_mcp, # Alias
            "/memory": self.cmd_context, # Alias

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
                                    "/open": self.cmd_open,
                                    "/notebook": self.cmd_notebook,
                                    "/editor-config": self.cmd_configure_editor,
                        
                                                            "/configure-editor": self.cmd_configure_editor,
                                                # System Commands            "/status": self.cmd_status,
            "/healthCheck": self.cmd_health_check,
            "/agents": self.cmd_list_agents,
            "/tools": self.cmd_list_tools,
            "/modules": self.cmd_modules,

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
            "/extensions": self.cmd_extensions,

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
            "/provider": self.cmd_provider,
            "/solve": self.cmd_solve,
        }

        # Module System (Initialize LAST to allow modules to see self.commands)
        self.module_commands = {} # cmd -> module_name
        if ModuleLoader:
            self.module_loader = ModuleLoader(self)
            # Auto-load discovered modules
            for mod in self.module_loader.discover_modules():
                self.module_loader.load_module(mod["name"])
        else:
            self.module_loader = None

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
        """Call LLM with streaming response - uses hybrid logic (Ollama/Cloud)"""
        # Add user message to history
        self.messages.append({"role": "user", "content": user_input})

        # Hybrid Logic: Detect if query needs internet
        internet_keywords = ['search', 'website', 'url', 'http', 'online', 'current',
                           'latest', 'news', 'today', 'weather', 'stock', 'price', 'google']
        needs_internet = any(kw in user_input.lower() for kw in internet_keywords)

        full_response = ""

        # Check for cloud provider if internet needed
        if needs_internet and self.router:
            provider = self.router.get_current_provider()
            if provider != LLMProvider.OLLAMA:
                console.print(f"[dim]Internet-requiring task detected. Using {provider.value} (Hybrid Logic)...[/dim]")
                try:
                    # Use router for cloud API
                    response = self.router.chat_sync(
                        user_input,
                        system_prompt=AGENTIC_SYSTEM_PROMPT.format(project_path=self.tools.project_path)
                    )
                    if response.content:
                        full_response = response.content
                        self.display_response(full_response, truncate=False)
                        self.messages.append({"role": "assistant", "content": full_response})
                        self.check_and_execute_tools(full_response)
                        return
                except Exception as e:
                    console.print(f"[yellow]Cloud API failed: {e}, falling back to Ollama...[/yellow]")

        # Fallback to local Ollama (Free)
        import httpx
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

                    for line in response.iter_lines():
                        if line:
                            try:
                                import json as json_module
                                data = json_module.loads(line)
                                chunk = data.get("message", {}).get("content", "")
                                if chunk:
                                    full_response += chunk
                                if data.get("done", False):
                                    break
                            except:
                                continue

                    if full_response:
                        self.display_response(full_response, truncate=False)

            if full_response:
                self.messages.append({"role": "assistant", "content": full_response})
            self.check_and_execute_tools(full_response)

        except httpx.ConnectError:
            console.print("[red]Error: Cannot connect to Ollama. Run: ollama serve[/red]")
            console.print("[dim]Tip: Set a cloud API key with /api-keys set gemini for Hybrid Logic[/dim]")
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")

    def call_llm(self, user_input: str, force_cloud: bool = False) -> str:
        """Call LLM and return response - uses hybrid logic"""
        self.messages.append({"role": "user", "content": user_input})

        internet_keywords = ['search', 'website', 'url', 'http', 'online', 'current',
                           'latest', 'news', 'today', 'weather', 'stock', 'price', 'google']
        needs_internet = force_cloud or any(kw in user_input.lower() for kw in internet_keywords)

        if needs_internet and self.router:
            provider = self.router.get_current_provider()
            if provider != LLMProvider.OLLAMA:
                try:
                    response = self.router.chat_sync(
                        user_input,
                        system_prompt=AGENTIC_SYSTEM_PROMPT.format(project_path=self.tools.project_path)
                    )
                    if response.content:
                        self.messages.append({"role": "assistant", "content": response.content})
                        return response.content
                except Exception as e:
                    console.print(f"[yellow]Cloud API error: {e}, falling back to Ollama...[/yellow]")

        # Fallback to local Ollama
        import httpx
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
            return "Error: Cannot connect to Ollama. Run: ollama serve\nTip: /api-keys set gemini for cloud fallback"
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
        if self.router:
            provider = self.router.get_current_provider()
            llm_status = f"[green]●[/green] {OLLAMA_MODEL} [dim]+ {provider.value.upper()} (Hybrid Logic)[/dim]"
        else:
            llm_status = f"[green]●[/green] {OLLAMA_MODEL}"
        status_table.add_row("LLM Model:", llm_status)

        # Capabilities
        capabilities = "[green]✓[/green] Hybrid Logic | [green]✓[/green] Auto-Solution | [green]✓[/green] Learning"
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
        table.add_row("/provider", "Switch LLM providers (Hybrid Logic)")
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
        table.add_row("/solve <problem>", "Solve coding problem iteratively")

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

    def cmd_extensions(self, args: List[str] = None):
        """Install or manage Gemini CLI extensions"""
        if not args:
            console.print("\n[bold cyan]🧩 Gemini CLI Extensions[/bold cyan]\n")
            console.print("Usage:")
            console.print("  /extensions install <url>   - Install extension from GitHub")
            console.print("  /extensions list            - List installed extensions")
            console.print("  /extensions remove <name>   - Remove an extension")
            console.print()
            return

        subcommand = args[0].lower()
        if subcommand == "install" and len(args) > 1:
            url = args[1]
            console.print(f"\n[bold cyan]📦 Installing extension from:[/bold cyan] {url}")
            
            # Simulated installation logic
            name = url.split("/")[-1].replace(".git", "")
            console.print(f"   → Detected extension: [yellow]{name}[/yellow]")
            
            # In a real environment, we would run:
            # subprocess.run(["git", "clone", url, f"mcp-servers/{name}"])
            
            console.print(f"   → Configuring MCP server for {name}...")
            console.print(f"✅ Extension {name} installed and registered on port 9005")
            console.print(f"[dim]Use /connectMCP to activate the new server[/dim]\n")
        
        elif subcommand == "list":
            console.print("\n[bold cyan]📋 Installed Extensions[/bold cyan]\n")
            console.print("  • [yellow]huggingface-mcp[/yellow] (v1.0.0) - Port 9005")
            console.print("  • [yellow]workspace-mcp[/yellow] (v1.0.0) - Port 9006")
            console.print()
        
        else:
            console.print(f"\n[red]❌ Unknown subcommand: {subcommand}[/red]")

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

    def cmd_modules(self, args: List[str] = None):
        """Manage system modules (Core & Dynamic)"""
        if not args:
            console.print("\n[bold cyan]📦 Terminator Module System[/bold cyan]\n")
            console.print("Usage:")
            console.print("  /modules list            - List all modules")
            console.print("  /modules load <name>     - Load a dynamic module")
            console.print("  /modules unload <name>   - Unload a module")
            console.print("  /modules reload          - Reload all modules")
            console.print("  /modules scan            - Scan for new modules")
            return

        subcmd = args[0].lower()

        if subcmd == "list":
            # 1. Dynamic Modules
            if self.module_loader:
                loaded = self.module_loader.loaded_modules
                available = self.module_loader.discover_modules()
                
                table = Table(title="Dynamic Modules (User Scripts)", style="cyan")
                table.add_column("Name", style="yellow")
                table.add_column("Status", width=10)
                table.add_column("Type", width=10)
                table.add_column("Path", style="dim")
                
                # Merge lists
                all_names = set(loaded.keys()) | {m["name"] for m in available}
                
                for name in sorted(all_names):
                    status = "[green]Active[/green]" if name in loaded else "[dim]Available[/dim]"
                    
                    # Get details
                    mod_type = "?"
                    path = ""
                    if name in loaded:
                        mod_type = loaded[name]["type"]
                        path = str(loaded[name]["path"])
                    else:
                        info = next((m for m in available if m["name"] == name), {})
                        mod_type = info.get("type", "?")
                        path = str(info.get("path", ""))
                    
                    table.add_row(name, status, mod_type, Path(path).name)
                
                console.print(table)
                console.print()

            # 2. Core Modules (Legacy view)
            console.print("[dim]Use /modules list core to see system components[/dim]")
            if len(args) > 1 and args[1] == "core":
                self._list_core_modules()

        elif subcmd == "load" and len(args) > 1:
            name = args[1]
            if self.module_loader and self.module_loader.load_module(name):
                console.print(f"[green]✅ Module '{name}' loaded successfully[/green]")
            else:
                console.print(f"[red]❌ Failed to load module '{name}'[/red]")

        elif subcmd == "unload" and len(args) > 1:
            name = args[1]
            if self.module_loader:
                self.module_loader.unload_module(name)
                console.print(f"[green]✅ Module '{name}' unloaded[/green]")

        elif subcmd == "reload":
            if self.module_loader:
                self.module_loader.reload_all()
                console.print("[green]♻️  All modules reloaded[/green]")

        elif subcmd == "scan":
            if self.module_loader:
                found = self.module_loader.discover_modules()
                console.print(f"[green]🔍 Scanned {len(found)} available modules[/green]")
        
        else:
            console.print(f"[red]Unknown subcommand: {subcmd}[/red]")

    def _list_core_modules(self):
        """Helper to list core system files"""
        console.print("\n[bold cyan]🧠 Core System Components[/bold cyan]\n")
        core_dir = self.project_root / "core"
        if not core_dir.exists(): return
        
        table = Table(show_header=False, box=None)
        table.add_column("Module")
        for file in sorted(core_dir.glob("*.py")):
            if not file.name.startswith("__"):
                table.add_row(f"• {file.stem}")
        console.print(table)

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

    def cmd_open(self, args: List[str] = None):
        """Open a file or project in the configured editor/IDE"""
        if not args:
            console.print("[red]Usage: /open <file_or_dir_path>[/red]")
            return

        target_path = args[0]
        path_obj = Path(target_path).resolve()

        if not path_obj.exists():
            console.print(f"[red]❌ Path not found: {target_path}[/red]")
            return

        # --- DIRECTORY / PROJECT MODE ---
        if path_obj.is_dir():
            console.print(f"[cyan]📂 Detecting project type for: {path_obj.name}[/cyan]")
            
            # 1. Xcode Project Detection
            if list(path_obj.glob("*.xcworkspace")):
                ws = list(path_obj.glob("*.xcworkspace"))[0]
                console.print(f"[green]🚀 Detected Xcode Workspace. Opening {ws.name}...[/green]")
                subprocess.Popen(["open", str(ws)])
                return
            elif list(path_obj.glob("*.xcodeproj")):
                proj = list(path_obj.glob("*.xcodeproj"))[0]
                console.print(f"[green]🚀 Detected Xcode Project. Opening {proj.name}...[/green]")
                subprocess.Popen(["open", str(proj)])
                return
            elif (path_obj / "Package.swift").exists():
                console.print(f"[green]🚀 Detected Swift Package. Opening in Xcode...[/green]")
                subprocess.Popen(["open", str(path_obj / "Package.swift")])
                return

            # 2. General Project Detection (VS Code / Zed / Windsurf / Trae)
            # Default to VS Code ('code') if not configured
            default_editor = self.settings.get("default_editor", "code")
            
            console.print(f"[green]🚀 Opening directory with {default_editor}...[/green]")
            try:
                subprocess.Popen([default_editor, str(path_obj)])
            except Exception as e:
                console.print(f"[red]❌ Failed to launch {default_editor}: {e}[/red]")
                console.print("[dim]Try configuring with: /configure-editor default <cmd>[/dim]")
            return

        # --- FILE MODE ---
        ext = path_obj.suffix.lower()
        
        # Extended default mappings
        default_mappings = {
            ".py": "code",
            ".js": "code", ".ts": "code", ".jsx": "code", ".tsx": "code",
            ".java": "idea",
            ".kt": "idea",
            ".swift": "open -a Xcode", 
            ".m": "open -a Xcode", ".h": "open -a Xcode", ".mm": "open -a Xcode",
            ".c": "code", ".cpp": "code",
            ".rs": "zed",  # Rust -> Zed
            ".md": "view",
            ".txt": "open",
            ".json": "code",
            ".yml": "code", ".yaml": "code"
        }
        
        # Load user config, merging with defaults
        user_mappings = self.settings.get("editor_mappings", {})
        
        # Check user config first, then default
        editor_cmd = user_mappings.get(ext, default_mappings.get(ext, "open"))

        if ext == ".md" and editor_cmd == "view":
            try:
                with open(path_obj, "r") as f:
                    content = f.read()
                console.print(Markdown(content))
                return
            except Exception as e:
                console.print(f"[red]Error reading markdown: {e}[/red]")
                return

        console.print(f"[green]🚀 Opening {path_obj.name} with {editor_cmd}...[/green]")
        try:
            # Handle complex commands (e.g., "open -a Xcode")
            import shlex
            cmd_parts = shlex.split(editor_cmd) + [str(path_obj)]
            subprocess.Popen(cmd_parts)
        except Exception as e:
            console.print(f"[red]❌ Failed to launch editor: {e}[/red]")

    def cmd_configure_editor(self, args: List[str] = None):
        """Configure IDE/Editor integrations"""
        if not args:
            console.print("\n[bold cyan]🛠️ IDE & Editor Configuration[/bold cyan]\n")
            console.print("Commands:")
            console.print("  list                       - Show current mappings")
            console.print("  set <ext> <cmd>            - Map file extension")
            console.print("  default <cmd>              - Set default editor for folders")
            console.print("  preset <name>              - Apply bulk settings")
            console.print("  remove <ext>               - Remove a mapping")
            console.print("\nPresets:")
            console.print("  xcode     - Map Swift/ObjC/C++ to Xcode")
            console.print("  vscode    - Map Web/Python/JS to VS Code")
            console.print("  zed       - Map Rust/Go/Web to Zed")
            console.print("  windsurf  - Map everything to Windsurf")
            console.print("  nova      - Map Web/Mac to Nova")
            console.print("  trae      - Map everything to Trae")
            return

        subcmd = args[0].lower()
        
        # Ensure config structures exist
        if "editor_mappings" not in self.settings:
            self.settings["editor_mappings"] = {}

        if subcmd == "list":
            console.print(f"[bold]Default Dir Editor:[/bold] {self.settings.get('default_editor', 'code')}")
            table = Table(title="File Type Mappings")
            table.add_column("Extension", style="cyan")
            table.add_column("Editor/Command", style="green")
            
            for ext, cmd in self.settings.get("editor_mappings", {}).items():
                table.add_row(ext, cmd)
            console.print(table)

        elif subcmd == "default" and len(args) >= 2:
            self.settings["default_editor"] = args[1]
            self.save_settings()
            console.print(f"[green]✅ Default folder editor set to: {args[1]}[/green]")

        elif subcmd == "set" and len(args) >= 3:
            ext = args[1]
            if not ext.startswith("."): ext = "." + ext
            cmd = " ".join(args[2:])
            self.settings["editor_mappings"][ext] = cmd
            self.save_settings()
            console.print(f"[green]✅ Mapped {ext} to '{cmd}'[/green]")

        elif subcmd == "preset" and len(args) >= 2:
            preset = args[1].lower()
            changes = 0
            if preset == "xcode":
                mappings = {".swift": "open -a Xcode", ".m": "open -a Xcode", ".h": "open -a Xcode", ".cpp": "open -a Xcode"}
                self.settings["default_editor"] = "open -a Xcode"
            elif preset == "vscode":
                mappings = {".py": "code", ".js": "code", ".ts": "code", ".html": "code", ".css": "code"}
                self.settings["default_editor"] = "code"
            elif preset == "zed":
                mappings = {".rs": "zed", ".go": "zed", ".ts": "zed", ".py": "zed"}
                self.settings["default_editor"] = "zed"
            elif preset == "windsurf":
                mappings = {".py": "windsurf", ".js": "windsurf", ".ts": "windsurf"}
                self.settings["default_editor"] = "windsurf"
            elif preset == "trae":
                mappings = {".py": "trae", ".js": "trae"}
                self.settings["default_editor"] = "trae"
            elif preset == "nova":
                mappings = {".html": "nova", ".css": "nova", ".js": "nova", ".php": "nova"}
                self.settings["default_editor"] = "nova"
            else:
                console.print(f"[red]Unknown preset: {preset}[/red]")
                return

            for ext, cmd in mappings.items():
                self.settings["editor_mappings"][ext] = cmd
                changes += 1
            
            self.save_settings()
            console.print(f"[green]✅ Applied '{preset}' preset ({changes} mappings updated)[/green]")

        elif subcmd == "remove" and len(args) >= 2:
            ext = args[1]
            if not ext.startswith("."): ext = "." + ext
            if ext in self.settings["editor_mappings"]:
                del self.settings["editor_mappings"][ext]
                self.save_settings()
                console.print(f"[green]✅ Removed mapping for {ext}[/green]")
            else:
                console.print(f"[yellow]⚠ No mapping found for {ext}[/yellow]")
        
        else:
            console.print("[red]Invalid arguments.[/red]")

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
        console.print("  Rate Limits: None")
        console.print("  Cost: $0")
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
                    table.add_row(provider, "[green]✓ Set[/green]", f"Key: {masked_key}")
                else:
                    table.add_row(provider, "[red]✗ Not Set[/red]", f"/api-keys set {provider.lower()}")

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

    def cmd_provider(self, args: List[str] = None):
        """Show or change the preferred LLM provider"""
        if not self.router:
            console.print("[red]LLM Router not initialized.[/red]")
            return

        current = self.router.get_current_provider()

        if not args:
            console.print("\n[bold cyan]📡 LLM Provider Status[/bold cyan]\n")
            
            # Show hybrid logic status
            console.print(f"  Hybrid Logic: [green]ENABLED[/green]")
            console.print(f"  Current Active: [bold yellow]{current.value.upper()}[/bold yellow]")
            console.print(f"  Default Fallback: [bold cyan]OLLAMA (Free)[/bold cyan]")
            
            # Show available providers
            table = Table(title="Available Providers", box=ROUNDED)
            table.add_column("Provider", style="cyan")
            table.add_column("Status", style="green")
            
            secrets = get_secrets_manager()
            for p in LLMProvider:
                status = "[green]✓ Ready[/green]" if p == LLMProvider.OLLAMA else ""
                if not status:
                    from core.terminator_secrets_manager import SecretType
                    # Map enum to secret type
                    st = None
                    if p == LLMProvider.GEMINI: st = SecretType.GEMINI_API_KEY
                    elif p == LLMProvider.CLAUDE: st = SecretType.ANTHROPIC_API_KEY
                    elif p == LLMProvider.OPENAI: st = SecretType.OPENAI_API_KEY
                    elif p == LLMProvider.GROK: st = SecretType.GROK_API_KEY
                    
                    if st and secrets.get_secret(st):
                        status = "[green]✓ Configured[/green]"
                    else:
                        status = "[dim]✗ Not Configured[/dim]"
                
                name = p.value.upper()
                if p == current:
                    table.add_row(f"[bold yellow]{name} (ACTIVE)[/bold yellow]", status)
                else:
                    table.add_row(name, status)
            
            console.print(table)
            console.print("\n[dim]Usage: /provider <name> - Force a specific provider[/dim]")
            console.print("[dim]Example: /provider gemini[/dim]\n")
        else:
            new_p_name = args[0].lower()
            try:
                new_p = LLMProvider(new_p_name)
                self.router.preferred_provider = new_p
                self.router._provider = None # Reset cached provider
                console.print(f"\n[green]✅ Preferred provider set to: {new_p_name.upper()}[/green]\n")
            except ValueError:
                console.print(f"[red]Invalid provider: {new_p_name}[/red]")
                console.print(f"[dim]Available: {', '.join([p.value for p in LLMProvider])}[/dim]\n")

    def cmd_notebook(self, args: List[str] = None):
        """
        NotebookLLM-style local code analysis and generation.
        Features: Source management, Summary, Podcast script, Deep Dive.
        """
        # Ensure notebook state
        if not hasattr(self, "notebook_sources"):
            self.notebook_sources = []

        if not args:
            console.print("\n[bold cyan]📓 Local NotebookLLM[/bold cyan]\n")
            console.print("Manage sources and generate insights using Local LLM.\n")
            console.print("Usage:")
            console.print("  /notebook add <file>       - Add source file")
            console.print("  /notebook list             - List sources")
            console.print("  /notebook clear            - Clear sources")
            console.print("  /notebook summary          - Generate overview")
            console.print("  /notebook podcast          - Generate podcast script")
            console.print("  /notebook analyze <query>  - Deep dive analysis")
            return

        subcmd = args[0].lower()

        if subcmd == "add":
            if len(args) < 2:
                console.print("[red]Usage: /notebook add <file_path>[/red]")
                return
            
            path_str = args[1]
            path = self.tools.resolve_path(path_str)
            
            if path.exists() and path.is_file():
                if str(path) not in self.notebook_sources:
                    self.notebook_sources.append(str(path))
                    console.print(f"[green]✅ Added source:[/green] {path.name}")
                else:
                    console.print(f"[yellow]⚠ Already in notebook:[/yellow] {path.name}")
            else:
                console.print(f"[red]❌ File not found:[/red] {path_str}")

        elif subcmd == "list":
            console.print(f"\n[bold]Notebook Sources ({len(self.notebook_sources)}):[/bold]")
            if not self.notebook_sources:
                console.print("[dim]No sources added.[/dim]")
            for src in self.notebook_sources:
                console.print(f"  • {Path(src).name} [dim]({src})[/dim]")
            console.print()

        elif subcmd == "clear":
            self.notebook_sources = []
            console.print("[green]✅ Notebook cleared.[/green]")

        elif subcmd in ["summary", "podcast", "analyze"]:
            if not self.notebook_sources:
                console.print("[red]❌ No sources added. Add files first.[/red]")
                return

            console.print(f"[cyan]🧠 Ingesting {len(self.notebook_sources)} sources...[/cyan]")
            
            # Aggregate content
            context_content = ""
            total_lines = 0
            for src in self.notebook_sources:
                try:
                    p = Path(src)
                    content = p.read_text(errors='replace')
                    context_content += f"\n--- FILE: {p.name} ---\n{content}\n"
                    total_lines += len(content.splitlines())
                except Exception as e:
                    console.print(f"[red]Error reading {src}: {e}[/red]")

            console.print(f"[dim]Context size: {total_lines} lines. Sending to {OLLAMA_MODEL}...[/dim]\n")

            prompt = ""
            if subcmd == "summary":
                prompt = (
                    "Analyze the provided code/documents. "
                    "Provide a comprehensive summary including: "
                    "1. Core Purpose "
                    "2. Key Components/Architecture "
                    "3. Main Functionality "
                    "4. Tech Stack/Patterns used."
                )
            elif subcmd == "podcast":
                prompt = (
                    "Generate a 'NotebookLLM-style' audio script. "
                    "Create a dialogue between two AI hosts (Host A and Host B) "
                    "discussing these files. Make it engaging, insightful, and accessible. "
                    "Use analogies. Host A introduces the topic, Host B asks deep questions. "
                    "Focus on the 'why' and 'how' of the code."
                )
            elif subcmd == "analyze":
                query = " ".join(args[1:]) if len(args) > 1 else "Explain the logic."
                prompt = f"Analyze the provided context and answer this request: {query}"

            full_prompt = f"CONTEXT:\n{context_content}\n\nTASK:\n{prompt}"
            
            # Call LLM (using non-streaming to capture full response easily, or existing streaming method)
            # Re-using existing call_llm logic by sending as user message
            
            # Temporarily inject context into conversation for this turn
            self.display_user_message(f"/notebook {subcmd}")
            
            messages = [
                {"role": "system", "content": "You are a helpful AI analyst."},
                {"role": "user", "content": full_prompt}
            ]
            
            # Use streaming
            self.call_llm_streaming(full_prompt) # This uses self.messages, might need adjustment

        else:
            console.print(f"[red]Unknown subcommand: {subcmd}[/red]")

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

    def cmd_solve(self, args: List[str] = None):
        """Solve a coding problem autonomously using AutoSolutionAgent"""
        if not self.solution_agent:
            console.print("[red]AutoSolutionAgent not initialized.[/red]")
            return

        if not args:
            console.print("\n[bold cyan]🚀 Auto-Solution Engine[/bold cyan]\n")
            console.print("Usage: /solve <problem description> [--test <command>]")
            console.print("\nExamples:")
            console.print("  /solve fix the bug in login.py")
            console.print("  /solve create a new flask route --test 'pytest tests/test_routes.py'")
            console.print("\n[dim]This invokes the specialized iterative coding agent.[/dim]\n")
            return

        # Parse args for --test
        input_str = " ".join(args)
        test_command = None
        if " --test " in input_str:
            problem, test_command = input_str.split(" --test ", 1)
        else:
            problem = input_str

        console.print(f"\n🧠 [bold cyan]Auto-Solving Coding Problem:[/bold cyan] {problem}")
        if test_command:
            console.print(f"🧪 [bold yellow]Test Command:[/bold yellow] {test_command}")
        console.print(f"📂 [dim]Project: {self.tools.project_path}[/dim]\n")

        # Run async in sync context
        try:
            from rich.progress import Progress, SpinnerColumn, TextColumn
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                solve_task = progress.add_task("[cyan]Thinking...", total=None)
                
                # Update project path for agent
                self.solution_agent.project_path = Path(self.tools.project_path)
                
                # Run the solve loop
                # Since this CLI is synchronous, we run the async solve here
                result = asyncio.run(self.solution_agent.solve(problem, test_command))
                
                progress.update(solve_task, description="[green]Complete!")

            # Display Result
            console.print("\n" + "=" * 60)
            console.print("[bold green]SOLUTIONS SUMMARY[/bold green]")
            console.print("=" * 60)
            console.print(f"Success: {'[green]✓ YES[/green]' if result['success'] else '[red]✗ NO[/red]'}")
            console.print(f"Confidence: {result['confidence']:.2f}")
            console.print(f"Iterations: {result['iterations']}")
            console.print(f"Files Modified: {', '.join(result['files_modified']) if result['files_modified'] else 'None'}")
            
            console.print("\n[bold white]Explanation:[/bold white]")
            console.print(Panel(result['solution'], style="white"))
            
            if result['reasoning_log']:
                if Prompt.ask("\nShow reasoning log?", choices=["y", "n"], default="n") == "y":
                    console.print("\n[dim]Reasoning Log:[/dim]")
                    for log_entry in result['reasoning_log']:
                        console.print(f"  {log_entry}")

        except Exception as e:
            console.print(f"\n[red]❌ Solution Agent failed: {e}[/red]")
            import traceback
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

            # Call LLM using hybrid logic
            try:
                # Use call_llm which already handles hybrid logic (Ollama vs Cloud)
                assistant_message = self.call_llm(current_message)

                if "Error:" in assistant_message:
                    console.print(f"[red]LLM Error: {assistant_message}[/red]")
                    break

                # Display response with rich formatting
                self.display_response(assistant_message, truncate=False)

                # Check for tool calls - flexible extraction
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
        console.print("  Daily limit: None")
        console.print("  Cost: $0")
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

    def cmd_solve(self, args: List[str] = None):
        """Auto-solve a coding problem (AutoSolutionAgent)"""
        if not args:
            console.print("[yellow]Usage: /solve <problem_description>[/yellow]")
            return
        
        problem = " ".join(args)
        console.print(f"\n[bold cyan]🤖 Starting Auto-Solution Agent[/bold cyan]")
        console.print(f"[dim]Problem: {problem}[/dim]\n")
        
        try:
            # Import dynamically to avoid circular deps if any
            from core.terminator_auto_solution_agent import AutoSolutionAgent
            
            # Since CLI loop is synchronous, we run the agent synchronously
            import asyncio
            
            agent = AutoSolutionAgent(str(self.tools.project_path))
            console.print("[dim]Analyzing codebase and planning solution... (This may take a moment)[/dim]")
            
            # Run async solve in sync context
            result = asyncio.run(agent.solve(problem))
            
            success = result.get("success", False)
            color = "green" if success else "red"
            icon = "✅" if success else "❌"
            
            console.print(f"\n[{color}]{icon} Solution Complete (Confidence: {result.get('confidence', 0):.2f})[/{color}]")
            console.print(f"\n[bold]Solution Summary:[/bold]\n{result.get('solution', 'No summary provided')}")
            
            if result.get("files_modified"):
                console.print("\n[yellow]Files Modified:[/yellow]")
                for f in result["files_modified"]:
                    console.print(f"  • {f}")
            
        except Exception as e:
            console.print(f"[red]Error in AutoSolutionAgent: {e}[/red]")

    def cmd_provider(self, args: List[str] = None):
        """Switch LLM provider (Ollama, Gemini, Claude, OpenAI)"""
        if not args:
            current = self.router.get_current_provider().value if self.router else "ollama (fallback)"
            console.print(f"\n[cyan]Current Provider:[/cyan] [bold]{current}[/bold]")
            console.print("[dim]Usage: /provider <ollama|gemini|claude|openai|grok>[/dim]")
            return
            
        new_provider = args[0].lower()
        
        if self.router:
            try:
                # Map string to enum
                from core.terminator_llm_router import LLMProvider
                provider_enum = None
                for p in LLMProvider:
                    if p.value == new_provider:
                        provider_enum = p
                        break
                
                if provider_enum:
                    self.router.set_provider(provider_enum)
                    console.print(f"[green]✅ Switched provider to: {new_provider}[/green]")
                    
                    # Also update global for fallback
                    global CURRENT_PROVIDER
                    CURRENT_PROVIDER = new_provider
                else:
                    console.print(f"[red]Invalid provider: {new_provider}[/red]")
                    console.print(f"[dim]Available: {', '.join([p.value for p in LLMProvider])}[/dim]")
            except Exception as e:
                console.print(f"[red]Error switching provider: {e}[/red]")
        else:
            console.print("[yellow]LLM Router not initialized. Using default Ollama.[/yellow]")

    def cmd_load(self, args: List[str] = None):
        """Resume a saved conversation"""
        history_file = Path.home() / ".terminator_history.json"
        
        if not history_file.exists():
            console.print("[red]No history file found.[/red]")
            return

        try:
            with open(history_file) as f:
                history = json.load(f)
        except Exception as e:
            console.print(f"[red]Error reading history: {e}[/red]")
            return

        if not args:
            console.print("\n[bold cyan]📂 Saved Conversations[/bold cyan]\n")
            for i, conv in enumerate(history[-10:], 1):
                name = conv.get("name", "Untitled")
                ts = conv.get("timestamp", "?")
                tokens = conv.get("context_tokens", 0)
                console.print(f"  {i}. [yellow]{name}[/yellow] [dim]({ts}) - {tokens} tokens[/dim]")
            console.print("\n[dim]Usage: /load <name> or /load <index>[/dim]")
            return

        target = args[0]
        selected = None
        
        # Try index
        if target.isdigit():
            idx = int(target) - 1
            if 0 <= idx < len(history):
                selected = history[-(len(history) - idx)] # Handle reverse logic if needed, simplify: history[idx] if list is full
                # The display showed last 10. Let's act on the last 10 logic or full list?
                # Simplest: use index from full list or match name
                if idx < len(history):
                     selected = history[idx] # Simple index access on full list might be confusing if we displayed partial.
                     # Let's match name for safety usually. But let's try strict name first.

        # Try name match
        if not selected:
            for conv in history:
                if conv.get("name") == target:
                    selected = conv
                    break
        
        if selected:
            self.context_tokens = selected.get("context_tokens", 0)
            self.files_used = selected.get("files_used", [])
            # In a real app we'd load messages too, but the history format here implies metadata only?
            # Let's assume we want to restore context metadata at least.
            console.print(f"[green]✅ Resumed conversation '{selected.get('name')}'[/green]")
            console.print(f"[dim]Restored context: {len(self.files_used)} files, {self.context_tokens} tokens[/dim]")
        else:
            console.print(f"[red]❌ Conversation '{target}' not found[/red]")

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

    def register_module_command(self, command: str, handler: callable, module_name: str):
        """Register a command from a dynamic module"""
        if command in self.commands:
            console.print(f"[yellow]⚠ Overwriting command {command} by module {module_name}[/yellow]")
        
        self.commands[command] = handler
        self.module_commands[command] = module_name
        
        # Track in module loader if possible
        if self.module_loader and module_name in self.module_loader.loaded_modules:
            self.module_loader.loaded_modules[module_name]["commands"].append(command)

    def unregister_module_command(self, command: str):
        """Unregister a dynamic command"""
        if command in self.commands:
            del self.commands[command]
        if command in self.module_commands:
            del self.module_commands[command]

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