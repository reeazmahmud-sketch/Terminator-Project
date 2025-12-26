#!/usr/bin/env python3
"""
TERMINATOR Full Agentic System
==============================

Complete orchestrator + sub-agents + tool harness implementation.
Integrates with the Agent Communication Bus and supports multiple LLM backends.

Architecture:
    User Request
         │
         ▼
    ┌─────────────────────────────────────────┐
    │           MAIN ORCHESTRATOR             │
    │  (Plans, Delegates, Synthesizes)        │
    └────────┬──────────────┬─────────────────┘
             │              │
    ┌────────▼────────┐  ┌──▼──────────────────┐
    │  SUB-AGENTS     │  │    TOOL LAYER       │
    │  (Specialists)  │  │  (Bash, MCP, Files) │
    └─────────────────┘  └─────────────────────┘

Usage:
    from core.terminator_agentic_system import AgenticSystem

    system = AgenticSystem()
    result = await system.orchestrate("Build a REST API with authentication")
"""

import os
import asyncio
import subprocess
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod

# Try to import LLM clients
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

import requests  # For Ollama and web fetching
HAS_OLLAMA = True

# Import communication bus if available
try:
    from core.terminator_agent_communication_bus import get_communication_bus
    HAS_BUS = True
except ImportError:
    HAS_BUS = False


class LLMBackend(Enum):
    """Supported LLM backends."""
    CLAUDE = "claude"
    GEMINI = "gemini"
    OLLAMA = "ollama"


class ToolType(Enum):
    """Available tool types."""
    BASH = "bash"
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    WEB_SEARCH = "web_search"
    WEB_FETCH = "web_fetch"
    MCP = "mcp"


class AgentRole(Enum):
    """Pre-defined specialist roles."""
    SECURITY_ENGINEER = "Senior Security Engineer specializing in code audits and vulnerability detection"
    FRONTEND_SPECIALIST = "Expert Frontend Developer with React, Vue, and modern CSS expertise"
    BACKEND_SPECIALIST = "Senior Backend Engineer experienced in APIs, databases, and system design"
    DEVOPS_ENGINEER = "DevOps specialist with expertise in CI/CD, Docker, Kubernetes, and cloud platforms"
    CODE_REVIEWER = "Senior Code Reviewer focused on quality, performance, and best practices"
    TEST_ENGINEER = "QA Engineer specializing in test automation and coverage analysis"
    ARCHITECT = "Software Architect with expertise in system design and scalability"
    DOCUMENTATION = "Technical Writer specializing in clear, comprehensive documentation"


@dataclass
class ToolResult:
    """Result from tool execution."""
    tool: ToolType
    command: str
    success: bool
    output: str
    error: Optional[str] = None
    duration: float = 0.0


@dataclass
class SubAgentResult:
    """Result from sub-agent execution."""
    role: str
    task: str
    response: str
    model: str
    tokens_used: int = 0


@dataclass
class OrchestrationResult:
    """Complete orchestration result."""
    goal: str
    plan: List[str]
    sub_agent_results: List[SubAgentResult]
    tool_results: List[ToolResult]
    final_synthesis: str
    total_duration: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    async def generate(self, prompt: str, system: Optional[str] = None) -> str:
        pass


class ClaudeClient(LLMClient):
    """Anthropic Claude client."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    async def generate(self, prompt: str, system: Optional[str] = None) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            system=system or "You are a helpful AI assistant.",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text


class GeminiClient(LLMClient):
    """Google Gemini client."""

    def __init__(self, api_key: str, model: str = "gemini-pro"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    async def generate(self, prompt: str, system: Optional[str] = None) -> str:
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        response = await asyncio.to_thread(
            self.model.generate_content, full_prompt
        )
        return response.text


class OllamaClient(LLMClient):
    """Local Ollama client."""

    def __init__(self, model: str = "llama3", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host

    async def generate(self, prompt: str, system: Optional[str] = None) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system or "",
            "stream": False
        }

        response = await asyncio.to_thread(
            requests.post,
            f"{self.host}/api/generate",
            json=payload,
            timeout=120
        )

        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            raise Exception(f"Ollama error: {response.status_code}")


class ToolHarness:
    """
    Tool Layer - Executes system commands and integrations.
    """

    def __init__(self, working_dir: Optional[str] = None):
        self.working_dir = working_dir or os.getcwd()
        self.execution_log: List[ToolResult] = []

    async def execute(self, tool: ToolType, command: str, **kwargs) -> ToolResult:
        """Execute a tool and return the result."""
        start_time = datetime.now()

        try:
            if tool == ToolType.BASH:
                result = await self._execute_bash(command)
            elif tool == ToolType.FILE_READ:
                result = await self._read_file(command)
            elif tool == ToolType.FILE_WRITE:
                content = kwargs.get("content", "")
                result = await self._write_file(command, content)
            elif tool == ToolType.WEB_FETCH:
                result = await self._fetch_url(command)
            else:
                result = ToolResult(
                    tool=tool,
                    command=command,
                    success=False,
                    output="",
                    error=f"Tool {tool.value} not implemented"
                )

            result.duration = (datetime.now() - start_time).total_seconds()
            self.execution_log.append(result)
            return result

        except Exception as e:
            result = ToolResult(
                tool=tool,
                command=command,
                success=False,
                output="",
                error=str(e),
                duration=(datetime.now() - start_time).total_seconds()
            )
            self.execution_log.append(result)
            return result

    async def _execute_bash(self, command: str) -> ToolResult:
        """Execute a bash command."""
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.working_dir
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60)

            return ToolResult(
                tool=ToolType.BASH,
                command=command,
                success=process.returncode == 0,
                output=stdout.decode("utf-8", errors="replace"),
                error=stderr.decode("utf-8", errors="replace") if stderr else None
            )
        except asyncio.TimeoutError:
            return ToolResult(
                tool=ToolType.BASH,
                command=command,
                success=False,
                output="",
                error="Command timed out after 60 seconds"
            )

    async def _read_file(self, path: str) -> ToolResult:
        """Read a file."""
        try:
            with open(path, 'r') as f:
                content = f.read()
            return ToolResult(
                tool=ToolType.FILE_READ,
                command=path,
                success=True,
                output=content
            )
        except Exception as e:
            return ToolResult(
                tool=ToolType.FILE_READ,
                command=path,
                success=False,
                output="",
                error=str(e)
            )

    async def _write_file(self, path: str, content: str) -> ToolResult:
        """Write to a file."""
        try:
            with open(path, 'w') as f:
                f.write(content)
            return ToolResult(
                tool=ToolType.FILE_WRITE,
                command=path,
                success=True,
                output=f"Written {len(content)} bytes to {path}"
            )
        except Exception as e:
            return ToolResult(
                tool=ToolType.FILE_WRITE,
                command=path,
                success=False,
                output="",
                error=str(e)
            )

    async def _fetch_url(self, url: str) -> ToolResult:
        """Fetch content from a URL."""
        try:
            response = await asyncio.to_thread(
                requests.get, url, timeout=30
            )
            return ToolResult(
                tool=ToolType.WEB_FETCH,
                command=url,
                success=response.status_code == 200,
                output=response.text[:5000],  # Limit output
                error=None if response.status_code == 200 else f"HTTP {response.status_code}"
            )
        except Exception as e:
            return ToolResult(
                tool=ToolType.WEB_FETCH,
                command=url,
                success=False,
                output="",
                error=str(e)
            )


class SubAgentManager:
    """
    Sub-Agent Layer - Spawns and manages specialist agents.
    """

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.results: List[SubAgentResult] = []

    async def spawn(
        self,
        task: str,
        role: AgentRole | str,
        additional_context: Optional[str] = None
    ) -> SubAgentResult:
        """Spawn a specialist sub-agent to handle a specific task."""

        role_prompt = role.value if isinstance(role, AgentRole) else role

        system_prompt = f"""You are a {role_prompt}.

Your task is to analyze the following and provide expert guidance.
Be precise, actionable, and thorough in your response.
Focus only on your area of expertise.

{f'Additional Context: {additional_context}' if additional_context else ''}"""

        print(f"\n[SUB-AGENT] Spawning: {role_prompt[:50]}...")

        response = await self.llm.generate(task, system=system_prompt)

        result = SubAgentResult(
            role=role_prompt,
            task=task,
            response=response,
            model=getattr(self.llm, 'model', 'unknown')
        )

        self.results.append(result)
        return result

    async def spawn_multiple(
        self,
        tasks: List[tuple[str, AgentRole | str]]
    ) -> List[SubAgentResult]:
        """Spawn multiple sub-agents in parallel."""
        coroutines = [
            self.spawn(task, role)
            for task, role in tasks
        ]
        return await asyncio.gather(*coroutines)


class AgenticSystem:
    """
    MAIN ORCHESTRATOR

    The 'Brain' that coordinates tools, memory, and sub-agents.
    Implements the full agentic loop: Plan → Delegate → Execute → Synthesize
    """

    def __init__(
        self,
        backend: LLMBackend = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        working_dir: Optional[str] = None
    ):
        # Auto-detect backend if not specified
        if backend is None:
            backend = self._detect_backend()

        self.backend = backend
        self.llm = self._init_llm(backend, api_key, model)
        self.tools = ToolHarness(working_dir)
        self.sub_agents = SubAgentManager(self.llm)

        # State management
        self.project_state: Dict[str, Any] = {}
        self.conversation_history: List[Dict] = []

        # Communication bus integration
        self.bus = get_communication_bus() if HAS_BUS else None
        self._registered = False

    def _detect_backend(self) -> LLMBackend:
        """Auto-detect available LLM backend."""
        if os.getenv("ANTHROPIC_API_KEY") and HAS_ANTHROPIC:
            return LLMBackend.CLAUDE
        elif os.getenv("GOOGLE_API_KEY") and HAS_GEMINI:
            return LLMBackend.GEMINI
        elif HAS_OLLAMA:
            # Check if Ollama is running
            try:
                resp = requests.get("http://localhost:11434/api/tags", timeout=2)
                if resp.status_code == 200:
                    return LLMBackend.OLLAMA
            except:
                pass

        # Default to Ollama (might need to start it)
        return LLMBackend.OLLAMA

    def _init_llm(
        self,
        backend: LLMBackend,
        api_key: Optional[str],
        model: Optional[str]
    ) -> LLMClient:
        """Initialize the LLM client."""
        if backend == LLMBackend.CLAUDE:
            key = api_key or os.getenv("ANTHROPIC_API_KEY")
            return ClaudeClient(key, model or "claude-sonnet-4-20250514")
        elif backend == LLMBackend.GEMINI:
            key = api_key or os.getenv("GOOGLE_API_KEY")
            return GeminiClient(key, model or "gemini-pro")
        else:  # OLLAMA
            return OllamaClient(model or "llama3")

    async def register(self):
        """Register with the communication bus."""
        if self.bus and not self._registered:
            await self.bus.register_agent_async("agentic_system")
            self._registered = True

    async def orchestrate(
        self,
        goal: str,
        specialists: Optional[List[AgentRole]] = None,
        tools_to_use: Optional[List[ToolType]] = None
    ) -> OrchestrationResult:
        """
        Main orchestration loop.

        1. Plan - Break down the goal
        2. Delegate - Send to specialists
        3. Execute - Use tools
        4. Synthesize - Combine results
        """
        start_time = datetime.now()
        print(f"\n{'='*60}")
        print(f"[ORCHESTRATOR] Goal: {goal}")
        print('='*60)

        # Register with bus if available
        await self.register()

        # ===== PHASE 1: PLANNING =====
        print("\n[PHASE 1] Planning...")
        plan = await self._create_plan(goal)
        self.project_state["plan"] = plan
        print(f"Plan created with {len(plan)} steps")

        # ===== PHASE 2: DELEGATE TO SUB-AGENTS =====
        print("\n[PHASE 2] Delegating to specialists...")

        # Default specialists if not specified
        if specialists is None:
            specialists = [AgentRole.SECURITY_ENGINEER, AgentRole.ARCHITECT]

        sub_agent_tasks = [
            (f"Analyze this goal and provide expert input: {goal}\n\nCurrent Plan:\n" + "\n".join(plan), role)
            for role in specialists
        ]

        sub_results = await self.sub_agents.spawn_multiple(sub_agent_tasks)

        for result in sub_results:
            print(f"  ✓ {result.role[:40]}... responded")

        # ===== PHASE 3: EXECUTE TOOLS =====
        print("\n[PHASE 3] Executing tools...")
        tool_results = []

        if tools_to_use is None:
            # Auto-determine tools based on goal
            tools_to_use = self._determine_tools(goal)

        for tool in tools_to_use:
            command = self._generate_tool_command(tool, goal)
            if command:
                result = await self.tools.execute(tool, command)
                tool_results.append(result)
                status = "✓" if result.success else "✗"
                print(f"  {status} {tool.value}: {command[:50]}...")

        # ===== PHASE 4: FINAL SYNTHESIS =====
        print("\n[PHASE 4] Synthesizing final response...")

        synthesis_prompt = self._build_synthesis_prompt(
            goal, plan, sub_results, tool_results
        )

        final_response = await self.llm.generate(
            synthesis_prompt,
            system="""You are the Lead Orchestrator of a multi-agent system.
Synthesize all specialist reports and tool outputs into a coherent, actionable response.
Be comprehensive but concise. Highlight key insights and recommended next steps."""
        )

        # Build final result
        duration = (datetime.now() - start_time).total_seconds()

        result = OrchestrationResult(
            goal=goal,
            plan=plan,
            sub_agent_results=sub_results,
            tool_results=tool_results,
            final_synthesis=final_response,
            total_duration=duration
        )

        # Notify via bus
        if self.bus and self._registered:
            await self.bus.send_message_async(
                sender_agent="agentic_system",
                recipient_agent="*",
                subject="Orchestration Complete",
                content={
                    "goal": goal,
                    "duration": duration,
                    "specialists_used": len(sub_results),
                    "tools_used": len(tool_results)
                }
            )

        print(f"\n[COMPLETE] Total time: {duration:.2f}s")
        return result

    async def _create_plan(self, goal: str) -> List[str]:
        """Create a step-by-step plan for the goal."""
        planning_prompt = f"""Create a step-by-step plan for this goal:

GOAL: {goal}

Provide 3-7 clear, actionable steps. Format as a numbered list.
Focus on what needs to be done, not how long it takes."""

        response = await self.llm.generate(
            planning_prompt,
            system="You are a project planner. Create clear, actionable plans."
        )

        # Parse steps from response
        lines = response.strip().split('\n')
        steps = [
            line.strip().lstrip('0123456789.-) ')
            for line in lines
            if line.strip() and any(c.isalpha() for c in line)
        ]

        return steps[:7]  # Limit to 7 steps

    def _determine_tools(self, goal: str) -> List[ToolType]:
        """Determine which tools to use based on the goal."""
        tools = []
        goal_lower = goal.lower()

        if any(word in goal_lower for word in ['file', 'read', 'check', 'analyze']):
            tools.append(ToolType.FILE_READ)

        if any(word in goal_lower for word in ['create', 'write', 'generate', 'build']):
            tools.append(ToolType.FILE_WRITE)

        if any(word in goal_lower for word in ['run', 'execute', 'install', 'test']):
            tools.append(ToolType.BASH)

        if any(word in goal_lower for word in ['search', 'find', 'look up', 'research']):
            tools.append(ToolType.WEB_SEARCH)

        return tools or [ToolType.BASH]  # Default to bash

    def _generate_tool_command(self, tool: ToolType, goal: str) -> Optional[str]:
        """Generate appropriate command for a tool."""
        if tool == ToolType.BASH:
            return "ls -la"  # Safe default; in production, generate from goal
        elif tool == ToolType.FILE_READ:
            return "./README.md" if os.path.exists("./README.md") else None
        return None

    def _build_synthesis_prompt(
        self,
        goal: str,
        plan: List[str],
        sub_results: List[SubAgentResult],
        tool_results: List[ToolResult]
    ) -> str:
        """Build the prompt for final synthesis."""
        parts = [
            f"# Original Goal\n{goal}\n",
            f"# Plan\n" + "\n".join(f"- {step}" for step in plan) + "\n",
            "# Specialist Reports\n"
        ]

        for result in sub_results:
            parts.append(f"## {result.role}\n{result.response[:500]}...\n")

        parts.append("# Tool Execution Results\n")
        for result in tool_results:
            status = "SUCCESS" if result.success else "FAILED"
            parts.append(f"- {result.tool.value} ({status}): {result.output[:200]}\n")

        parts.append("\n# Your Task\nSynthesize all of the above into a comprehensive response that addresses the original goal.")

        return "\n".join(parts)

    def format_result(self, result: OrchestrationResult) -> str:
        """Format the orchestration result for display."""
        output = [
            "",
            "=" * 60,
            "ORCHESTRATION RESULT",
            "=" * 60,
            f"\nGoal: {result.goal}",
            f"Duration: {result.total_duration:.2f}s",
            f"\n--- Plan ({len(result.plan)} steps) ---"
        ]

        for i, step in enumerate(result.plan, 1):
            output.append(f"  {i}. {step}")

        output.append(f"\n--- Specialists ({len(result.sub_agent_results)}) ---")
        for sub in result.sub_agent_results:
            output.append(f"  • {sub.role[:40]}...")

        output.append(f"\n--- Tools ({len(result.tool_results)}) ---")
        for tool in result.tool_results:
            status = "✓" if tool.success else "✗"
            output.append(f"  {status} {tool.tool.value}")

        output.extend([
            "\n--- Final Synthesis ---",
            result.final_synthesis,
            "",
            "=" * 60
        ])

        return "\n".join(output)


# =================================================================
# CLI INTERFACE
# =================================================================

async def main():
    """Command-line interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description="TERMINATOR Agentic System - Multi-agent orchestration"
    )
    parser.add_argument(
        "goal",
        nargs="?",
        default="Analyze the current project structure and suggest improvements",
        help="The goal to accomplish"
    )
    parser.add_argument(
        "--backend", "-b",
        choices=["claude", "gemini", "ollama"],
        help="LLM backend to use (auto-detected if not specified)"
    )
    parser.add_argument(
        "--model", "-m",
        help="Specific model to use"
    )

    args = parser.parse_args()

    backend = None
    if args.backend:
        backend = LLMBackend(args.backend)

    system = AgenticSystem(backend=backend, model=args.model)

    print(f"\nUsing backend: {system.backend.value}")

    result = await system.orchestrate(args.goal)
    print(system.format_result(result))


if __name__ == "__main__":
    asyncio.run(main())
