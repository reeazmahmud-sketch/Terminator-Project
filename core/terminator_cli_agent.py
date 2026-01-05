#!/usr/bin/env python3
"""
TERMINATOR CLI Agent
====================

The bridge between the CLI interface and the agent communication bus.
Routes user commands to appropriate agents and returns responses.

This agent:
1. Receives user input from CLI
2. Analyzes intent and routes to specialized agents
3. Coordinates multi-agent responses
4. Returns unified response to user
"""

import os
import sys
import asyncio
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

# Add project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.terminator_llm_router import get_llm_router, LLMProvider, LLMResponse
from core.terminator_secrets_manager import get_secrets_manager, SecretType


@dataclass
class AgentCapability:
    """Describes what an agent can do"""
    name: str
    description: str
    keywords: List[str]
    priority: int = 5  # 1-10, higher = more preferred


class TerminatorCLIAgent:
    """
    Main CLI agent - the brain of the terminal interface.

    Handles:
    - User input processing
    - Intent detection
    - Agent routing
    - Response synthesis
    - Tool execution
    """

    AGENT_NAME = "cli_agent"
    AGENT_DESCRIPTION = "Main CLI interface agent - routes commands and manages conversation"
    AGENT_CAPABILITIES = ["chat", "route", "tools", "code", "search"]

    # System prompt for the CLI agent
    SYSTEM_PROMPT = """You are TERMINATOR, an autonomous AI coding agent with access to tools.

## YOUR CAPABILITIES
1. **Code Operations**: Read, write, edit files. Search codebases. Run commands.
2. **Web Operations**: Search the web, fetch URLs, analyze content.
3. **System Operations**: Check system status, manage processes.
4. **Agent Coordination**: Route complex tasks to specialized agents.

## TOOL USAGE
When you need to perform an action, output a tool call in this format:
<tool_call>
{"tool": "tool_name", "params": {"param1": "value1"}}
</tool_call>

Available tools:
- read_file: {"path": "file/path"}
- write_file: {"path": "file/path", "content": "content"}
- edit_file: {"path": "file/path", "old_text": "find", "new_text": "replace"}
- bash: {"command": "shell command"}
- glob: {"pattern": "**/*.py"}
- grep: {"pattern": "search text", "path": "optional/dir"}
- web_search: {"query": "search terms"}
- fetch_web: {"url": "https://..."}

## RULES
1. Use tools for file/web/system operations - don't guess
2. Read files before editing them
3. Be concise but helpful
4. If a task is complex, break it into steps
5. For coding tasks, actually write the code - don't just describe it
"""

    def __init__(self):
        self._router = get_llm_router()
        self._secrets = get_secrets_manager()
        self._conversation_history: List[Dict[str, str]] = []
        self._tools = self._initialize_tools()
        self._project_path = os.getcwd()

    def _initialize_tools(self) -> Dict[str, callable]:
        """Initialize available tools"""
        return {
            "read_file": self._tool_read_file,
            "write_file": self._tool_write_file,
            "edit_file": self._tool_edit_file,
            "bash": self._tool_bash,
            "glob": self._tool_glob,
            "grep": self._tool_grep,
            "web_search": self._tool_web_search,
            "fetch_web": self._tool_fetch_web,
            "list_dir": self._tool_list_dir,
        }

    # =========================================================================
    # MAIN INTERFACE
    # =========================================================================

    async def process_input(self, user_input: str) -> str:
        """
        Main entry point - process user input and return response.

        Args:
            user_input: Raw user input from CLI

        Returns:
            Response string to display
        """
        # Check for slash commands first
        if user_input.startswith("/"):
            return await self._handle_slash_command(user_input)

        # Regular chat/task processing
        return await self._process_chat(user_input)

    async def _process_chat(self, user_input: str) -> str:
        """Process regular chat input"""
        # Add to history
        self._conversation_history.append({"role": "user", "content": user_input})

        # Get LLM response
        response = await self._router.chat(
            user_input,
            system_prompt=self.SYSTEM_PROMPT,
            use_history=True
        )

        content = response.content

        # Check for tool calls in response
        if "<tool_call>" in content:
            content = await self._execute_tool_calls(content)

        # Add response to history
        self._conversation_history.append({"role": "assistant", "content": content})

        return content

    async def _execute_tool_calls(self, response: str) -> str:
        """Extract and execute tool calls from response"""
        import re

        # Find all tool calls
        pattern = r'<tool_call>\s*({.*?})\s*</tool_call>'
        matches = re.findall(pattern, response, re.DOTALL)

        if not matches:
            return response

        results = []
        for match in matches:
            try:
                tool_call = json.loads(match)
                tool_name = tool_call.get("tool", "")
                params = tool_call.get("params", {})

                if tool_name in self._tools:
                    result = await self._tools[tool_name](**params)
                    results.append(f"**{tool_name}**: {result}")
                else:
                    results.append(f"**{tool_name}**: Unknown tool")

            except json.JSONDecodeError:
                results.append(f"Error parsing tool call: {match[:50]}...")
            except Exception as e:
                results.append(f"Error executing tool: {e}")

        # Combine original response with tool results
        tool_output = "\n\n".join(results)

        # Get follow-up from LLM with tool results
        follow_up = await self._router.chat(
            f"Tool execution results:\n{tool_output}\n\nBased on these results, provide your final response to the user.",
            system_prompt="You are reviewing tool execution results. Synthesize them into a helpful response.",
            use_history=False
        )

        return follow_up.content

    # =========================================================================
    # SLASH COMMANDS
    # =========================================================================

    async def _handle_slash_command(self, command: str) -> str:
        """Handle slash commands"""
        parts = command[1:].split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        commands = {
            "help": self._cmd_help,
            "status": self._cmd_status,
            "provider": self._cmd_provider,
            "model": self._cmd_model,
            "clear": self._cmd_clear,
            "solve": self._cmd_solve,
            "agents": self._cmd_agents,
            "api-keys": self._cmd_api_keys,
        }

        if cmd in commands:
            return await commands[cmd](args)
        else:
            return f"Unknown command: /{cmd}\nType /help for available commands."

    async def _cmd_help(self, args: str) -> str:
        """Show help"""
        return """
TERMINATOR CLI Commands
=======================

/help           - Show this help
/status         - Show system status
/provider       - Show/set LLM provider
/model          - Show current model
/clear          - Clear conversation history
/solve <desc>   - Auto-solve a coding problem
/agents         - List available agents
/api-keys       - Manage API keys

Just type naturally to chat or give tasks!
"""

    async def _cmd_status(self, args: str) -> str:
        """Show system status"""
        provider = self._router.get_current_provider()
        history_len = len(self._conversation_history)

        return f"""
TERMINATOR Status
=================
Provider: {provider.value}
Model: {self._router.DEFAULT_MODELS[provider]}
History: {history_len} messages
Project: {self._project_path}
"""

    async def _cmd_provider(self, args: str) -> str:
        """Show or set provider"""
        if args:
            try:
                new_provider = LLMProvider(args.lower())
                self._router = get_llm_router()
                self._router.preferred_provider = new_provider
                self._router._provider = new_provider
                return f"Provider set to: {new_provider.value}"
            except ValueError:
                return f"Unknown provider: {args}\nAvailable: gemini, claude, openai, grok, ollama"
        else:
            provider = self._router.get_current_provider()
            return f"Current provider: {provider.value}"

    async def _cmd_model(self, args: str) -> str:
        """Show current model"""
        provider = self._router.get_current_provider()
        model = self._router.DEFAULT_MODELS[provider]
        return f"Provider: {provider.value}\nModel: {model}"

    async def _cmd_clear(self, args: str) -> str:
        """Clear history"""
        self._conversation_history = []
        self._router.clear_history()
        return "Conversation history cleared."

    async def _cmd_solve(self, args: str) -> str:
        """Auto-solve a coding problem"""
        if not args:
            return "Usage: /solve <problem description>\nExample: /solve Fix the login bug in auth.py"

        try:
            from core.terminator_auto_solution_agent import solve_coding_problem
            result = await solve_coding_problem(args, self._project_path)

            output = f"""
Auto-Solution Result
====================
Success: {result['success']}
Confidence: {result['confidence']:.2f}
Iterations: {result['iterations']}
Files Modified: {', '.join(result['files_modified']) or 'None'}

Solution:
{result['solution']}
"""
            if result['errors']:
                output += f"\nErrors encountered:\n" + "\n".join(f"- {e}" for e in result['errors'])

            return output

        except Exception as e:
            return f"Error running auto-solve: {e}"

    async def _cmd_agents(self, args: str) -> str:
        """List available agents"""
        return """
Available Agents
================
- cli_agent: Main CLI interface
- auto_solution_agent: Autonomous coding solver
- error_monitor_agent: Error detection and recovery
- task_executor_agent: Task execution
- context_awareness_agent: Context tracking

(More agents available in core/ directory)
"""

    async def _cmd_api_keys(self, args: str) -> str:
        """Manage API keys"""
        if not args:
            # Show status
            secrets = self._secrets
            status = []
            for name, secret_type in [
                ("Gemini", SecretType.GEMINI_API_KEY),
                ("Claude", SecretType.ANTHROPIC_API_KEY),
                ("OpenAI", SecretType.OPENAI_API_KEY),
                ("Grok", SecretType.GROK_API_KEY),
            ]:
                key = secrets.get_secret(secret_type)
                if key:
                    masked = f"{key[:8]}...{key[-4:]}" if len(key) > 12 else "***"
                    status.append(f"  {name}: SET ({masked})")
                else:
                    status.append(f"  {name}: NOT SET")

            return "API Keys Status:\n" + "\n".join(status) + "\n\nUsage: /api-keys set <provider>"

        parts = args.split(maxsplit=1)
        if parts[0] == "set" and len(parts) > 1:
            provider = parts[1].lower()
            provider_map = {
                "gemini": SecretType.GEMINI_API_KEY,
                "claude": SecretType.ANTHROPIC_API_KEY,
                "openai": SecretType.OPENAI_API_KEY,
                "grok": SecretType.GROK_API_KEY,
            }
            if provider in provider_map:
                import getpass
                key = getpass.getpass(f"Enter {provider} API key: ")
                self._secrets.set_secret(provider_map[provider], key)
                return f"{provider.title()} API key saved!"
            else:
                return f"Unknown provider: {provider}"

        return "Usage: /api-keys or /api-keys set <provider>"

    # =========================================================================
    # TOOLS
    # =========================================================================

    async def _tool_read_file(self, path: str, limit: int = 500) -> str:
        """Read a file"""
        try:
            full_path = os.path.join(self._project_path, path) if not os.path.isabs(path) else path
            with open(full_path, 'r') as f:
                lines = f.readlines()
            content = ''.join(lines[:limit])
            if len(lines) > limit:
                content += f"\n... ({len(lines) - limit} more lines)"
            return f"File: {path} ({len(lines)} lines)\n```\n{content}\n```"
        except Exception as e:
            return f"Error reading file: {e}"

    async def _tool_write_file(self, path: str, content: str) -> str:
        """Write a file"""
        try:
            full_path = os.path.join(self._project_path, path) if not os.path.isabs(path) else path
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
            return f"Wrote {len(content)} chars to {path}"
        except Exception as e:
            return f"Error writing file: {e}"

    async def _tool_edit_file(self, path: str, old_text: str, new_text: str) -> str:
        """Edit a file"""
        try:
            full_path = os.path.join(self._project_path, path) if not os.path.isabs(path) else path
            with open(full_path, 'r') as f:
                content = f.read()
            if old_text not in content:
                return f"Text not found in {path}"
            count = content.count(old_text)
            new_content = content.replace(old_text, new_text)
            with open(full_path, 'w') as f:
                f.write(new_content)
            return f"Replaced {count} occurrence(s) in {path}"
        except Exception as e:
            return f"Error editing file: {e}"

    async def _tool_bash(self, command: str, timeout: int = 30) -> str:
        """Run a shell command"""
        import subprocess
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self._project_path
            )
            output = result.stdout + result.stderr
            status = "OK" if result.returncode == 0 else f"FAILED (exit {result.returncode})"
            return f"{status}: {output[:2000]}"
        except subprocess.TimeoutExpired:
            return f"Command timed out after {timeout}s"
        except Exception as e:
            return f"Command error: {e}"

    async def _tool_glob(self, pattern: str, path: str = None) -> str:
        """Find files matching pattern"""
        import glob as glob_module
        try:
            search_path = path or self._project_path
            full_pattern = os.path.join(search_path, pattern)
            matches = glob_module.glob(full_pattern, recursive=True)
            if not matches:
                return f"No files matching: {pattern}"
            return f"Found {len(matches)} files:\n" + "\n".join(matches[:30])
        except Exception as e:
            return f"Glob error: {e}"

    async def _tool_grep(self, pattern: str, path: str = None, file_pattern: str = "*") -> str:
        """Search for text in files"""
        import subprocess
        try:
            search_path = path or self._project_path
            cmd = f'grep -rn --include="{file_pattern}" "{pattern}" .'
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=search_path
            )
            if result.stdout:
                lines = result.stdout.strip().split('\n')[:20]
                return f"Found {len(lines)} matches:\n" + "\n".join(lines)
            return f"No matches for: {pattern}"
        except Exception as e:
            return f"Grep error: {e}"

    async def _tool_web_search(self, query: str) -> str:
        """Search the web"""
        try:
            import httpx
            url = "https://html.duckduckgo.com/html/"
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, data={"q": query})
                if response.status_code == 200:
                    return f"Web search for '{query}' completed. Use fetch_web to get specific pages."
                return f"Search failed: {response.status_code}"
        except Exception as e:
            return f"Web search error: {e}"

    async def _tool_fetch_web(self, url: str) -> str:
        """Fetch a URL"""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    content = response.text[:5000]
                    return f"Fetched {url}:\n{content}"
                return f"Failed to fetch: HTTP {response.status_code}"
        except Exception as e:
            return f"Fetch error: {e}"

    async def _tool_list_dir(self, path: str = ".") -> str:
        """List directory contents"""
        try:
            full_path = os.path.join(self._project_path, path) if not os.path.isabs(path) else path
            items = os.listdir(full_path)
            dirs = [f"📁 {i}/" for i in items if os.path.isdir(os.path.join(full_path, i))]
            files = [f"📄 {i}" for i in items if os.path.isfile(os.path.join(full_path, i))]
            return f"Directory: {path}\n" + "\n".join(sorted(dirs) + sorted(files))
        except Exception as e:
            return f"Error listing directory: {e}"


# =========================================================================
# SINGLETON & CONVENIENCE
# =========================================================================

_cli_agent: Optional[TerminatorCLIAgent] = None


def get_cli_agent() -> TerminatorCLIAgent:
    """Get singleton CLI agent"""
    global _cli_agent
    if _cli_agent is None:
        _cli_agent = TerminatorCLIAgent()
    return _cli_agent


async def chat(message: str) -> str:
    """Quick chat function"""
    agent = get_cli_agent()
    return await agent.process_input(message)


def chat_sync(message: str) -> str:
    """Synchronous chat"""
    return asyncio.run(chat(message))


# =========================================================================
# CLI RUNNER
# =========================================================================

async def run_cli():
    """Run interactive CLI"""
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown

    console = Console()
    agent = get_cli_agent()

    # Show startup banner
    provider = agent._router.get_current_provider()
    console.print(Panel(
        f"[bold cyan]TERMINATOR[/bold cyan] - Autonomous AI Agent\n"
        f"[dim]Provider: {provider.value} | Model: {agent._router.DEFAULT_MODELS[provider]}[/dim]\n"
        f"[dim]Type /help for commands, or just chat![/dim]",
        title="🤖 TERMINATOR",
        border_style="cyan"
    ))

    while True:
        try:
            user_input = console.input("\n[bold cyan]>[/bold cyan] ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "/exit", "/quit"]:
                console.print("[dim]Goodbye![/dim]")
                break

            # Process input
            console.print("[dim]Processing...[/dim]")
            response = await agent.process_input(user_input)

            # Display response
            console.print(Panel(
                Markdown(response),
                title="TERMINATOR",
                border_style="green"
            ))

        except KeyboardInterrupt:
            console.print("\n[dim]Use 'exit' to quit.[/dim]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    asyncio.run(run_cli())
