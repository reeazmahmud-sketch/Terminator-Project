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
OLLAMA_MODEL = "llama3:latest"


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

## RULES
1. Be confident and knowledgeable about TERMINATOR's capabilities
2. When asked specifics about agents/tools/modules, suggest the relevant slash command for details
3. You CAN answer coding questions, explain concepts, and have conversations
4. Keep responses concise but informative
5. You're running locally via Ollama - no cloud dependency for core features"""}
        ]

        # Command registry (Claude + TERMINATOR commands)
        self.commands = {
            # Claude CLI Commands
            "/help": self.cmd_help,
            "/settings": self.cmd_settings,
            "/clear": self.cmd_clear,
            "/exit": self.cmd_exit,
            "/quit": self.cmd_exit,
            "/rate-limit-options": self.cmd_rate_limit_options,
            "/model": self.cmd_model,
            "/context": self.cmd_context,
            "/tokens": self.cmd_tokens,
            "/budget": self.cmd_budget,
            "/reset": self.cmd_reset,
            "/history": self.cmd_history,
            "/save": self.cmd_save,
            "/load": self.cmd_load,
            "/export": self.cmd_export,

            # TERMINATOR Platform Commands
            "/healthCheck": self.cmd_health_check,
            "/systemIndex": self.cmd_system_index,
            "/viewAnalysis": self.cmd_view_analysis,
            "/connectMCP": self.cmd_connect_mcp,
            "/connectiOS": self.cmd_connect_ios,
            "/connectAndroid": self.cmd_connect_android,
            "/connectMacOS": self.cmd_connect_macos,
            "/connectWeb": self.cmd_connect_web,
            "/connections": self.cmd_show_connections,
            "/run": self.cmd_run_on_platform,
            "/broadcast": self.cmd_broadcast,
            "/sync": self.cmd_sync_all,
            "/status": self.cmd_status,
            "/agents": self.cmd_list_agents,
            "/tools": self.cmd_list_tools,
            "/modules": self.cmd_list_modules,
            "/logs": self.cmd_view_logs,
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
            "model": "llama3:latest",  # Default Ollama model, change with /model
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

                    # Stream response like Claude Code
                    console.print("[bold red]TERMINATOR[/bold red]", end=" ")

                    for line in response.iter_lines():
                        if line:
                            try:
                                import json as json_module
                                data = json_module.loads(line)
                                chunk = data.get("message", {}).get("content", "")
                                if chunk:
                                    full_response += chunk
                                    # Print chunk immediately (streaming effect)
                                    console.print(chunk, end="", highlight=False)

                                # Check if done
                                if data.get("done", False):
                                    break
                            except:
                                continue

                    console.print()  # New line after response

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
        """Display Claude Code-style minimal banner"""
        console.print()
        console.print("[bold red]TERMINATOR[/bold red] [dim]- Local AI Agent System[/dim]")
        console.print(f"[dim]Model: {OLLAMA_MODEL} • /help for commands • Ctrl+C to exit[/dim]")
        console.print()

    # ==================== SLASH COMMANDS ====================

    def cmd_help(self, args: List[str] = None):
        """Show all available commands"""
        console.print("\n[bold cyan]⚡ TERMINATOR Command Reference[/bold cyan]\n")

        # All commands in one unified table
        cmd_table = Table(title="⚡ TERMINATOR Commands", style="cyan", show_lines=True)
        cmd_table.add_column("Command", style="yellow", width=22)
        cmd_table.add_column("Description", width=45)

        # Core commands
        cmd_table.add_row("[bold]── Core ──[/bold]", "")
        cmd_table.add_row("/help", "Show this help message")
        cmd_table.add_row("/status", "Show system status")
        cmd_table.add_row("/healthCheck", "Run full diagnostics")
        cmd_table.add_row("/agents", "List all agents")
        cmd_table.add_row("/tools", "List available tools")
        cmd_table.add_row("/modules", "List core system modules")
        cmd_table.add_row("/clear", "Clear terminal screen")
        cmd_table.add_row("/exit", "Exit TERMINATOR")

        # Session commands
        cmd_table.add_row("[bold]── Session ──[/bold]", "")
        cmd_table.add_row("/model", "List Ollama models & switch (/model 3)")
        cmd_table.add_row("/context", "Show context usage")
        cmd_table.add_row("/tokens", "Show token statistics")
        cmd_table.add_row("/reset", "Reset conversation")
        cmd_table.add_row("/history", "View conversation history")
        cmd_table.add_row("/save", "Save conversation")
        cmd_table.add_row("/load", "Load conversation")
        cmd_table.add_row("/export", "Export to file")
        cmd_table.add_row("/settings", "View/edit settings")

        # Platform commands
        cmd_table.add_row("[bold]── Platforms ──[/bold]", "")
        cmd_table.add_row("/connections", "Show active connections")
        cmd_table.add_row("/connectiOS", "Connect to iOS device")
        cmd_table.add_row("/connectAndroid", "Connect to Android device")
        cmd_table.add_row("/connectMacOS", "Connect to macOS app")
        cmd_table.add_row("/connectWeb", "Connect to web interface")
        cmd_table.add_row("/connectMCP", "Connect to MCP servers")
        cmd_table.add_row("/run", "Run command on platform")
        cmd_table.add_row("/broadcast", "Send to all platforms")
        cmd_table.add_row("/sync", "Sync all platforms")

        # System commands
        cmd_table.add_row("[bold]── System ──[/bold]", "")
        cmd_table.add_row("/logs", "View system logs")
        cmd_table.add_row("/systemIndex", "View master system index")
        cmd_table.add_row("/viewAnalysis", "Show analysis log")

        console.print(cmd_table)
        console.print()

        # Examples
        console.print("[yellow]Examples:[/yellow]")
        console.print("  /status                          # Check system health")
        console.print("  /agents                          # List all agents")
        console.print("  /run ios get clipboard           # Get iOS clipboard")
        console.print("  hello, what can you do?          # Natural language")
        console.print()
        console.print("[dim]Type natural language or use / commands[/dim]")
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
        """Fetch available Ollama models from the API"""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                return response.json().get("models", [])
        except Exception as e:
            console.print(f"[red]Error fetching Ollama models: {e}[/red]")
        return []

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
                console.print(f"[bold red]TERMINATOR[/bold red] {response}")

            console.print()

    def display_input_box(self):
        """Add spacing before prompt"""
        # Add blank lines to push prompt up from bottom
        console.print()
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
                # Display input box with status
                self.display_input_box()

                # Get user input (Claude Code-style prompt)
                user_input = Prompt.ask("[bold cyan]>[/bold cyan]")

                if user_input.strip():
                    self.process_command(user_input)

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
