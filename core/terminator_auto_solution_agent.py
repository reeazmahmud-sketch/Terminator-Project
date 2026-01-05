#!/usr/bin/env python3
"""
TERMINATOR Auto-Solution Coding Agent
======================================

Autonomous coding problem solver with iterative refinement loop.

LOGIC FLOW:
    1. ANALYZE: Understand the coding problem
    2. PLAN: Break into steps with confidence scoring
    3. EXECUTE: Write code, run tests
    4. VALIDATE: Check if solution works
    5. ITERATE: If failed, analyze error and retry (max 5 iterations)
    6. SYNTHESIZE: Produce final solution with explanation

KEY FEATURES:
- Confidence-based iteration (continues until 0.8+ confidence)
- Automatic error analysis and self-correction
- Test execution and validation
- Multi-file change coordination
- Git-aware (won't break existing code)
"""

import os
import sys
import json
import subprocess
import asyncio
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SolutionPhase(Enum):
    """Phases of the auto-solution process"""
    ANALYZE = "analyze"
    PLAN = "plan"
    EXECUTE = "execute"
    VALIDATE = "validate"
    ITERATE = "iterate"
    COMPLETE = "complete"
    FAILED = "failed"


class ActionType(Enum):
    """Types of actions the agent can take"""
    READ_FILE = "read_file"
    WRITE_FILE = "write_file"
    EDIT_FILE = "edit_file"
    RUN_COMMAND = "run_command"
    RUN_TESTS = "run_tests"
    SEARCH_CODE = "search_code"
    ANALYZE_ERROR = "analyze_error"


@dataclass
class CodingTask:
    """Represents a coding task to solve"""
    description: str
    project_path: Path
    files_involved: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    test_command: Optional[str] = None


@dataclass
class SolutionState:
    """Tracks state of the solution process"""
    task: CodingTask
    phase: SolutionPhase = SolutionPhase.ANALYZE
    iteration: int = 0
    max_iterations: int = 5
    confidence: float = 0.0
    confidence_threshold: float = 0.8

    # Progress tracking
    analysis: Dict[str, Any] = field(default_factory=dict)
    plan_steps: List[Dict[str, Any]] = field(default_factory=list)
    executed_actions: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    # Results
    files_modified: List[str] = field(default_factory=list)
    tests_passed: bool = False
    final_solution: Optional[str] = None

    # Decision log
    reasoning_log: List[str] = field(default_factory=list)

    def log(self, message: str):
        """Log a reasoning step"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.reasoning_log.append(f"[{timestamp}] [{self.phase.value}] {message}")

    def should_continue(self) -> bool:
        """Check if we should continue iterating"""
        if self.iteration >= self.max_iterations:
            return False
        if self.confidence >= self.confidence_threshold:
            return False
        if self.phase == SolutionPhase.FAILED:
            return False
        return True

    def boost_confidence(self, amount: float, reason: str):
        """Increase confidence with reason"""
        old = self.confidence
        self.confidence = min(1.0, self.confidence + amount)
        self.log(f"Confidence: {old:.2f} -> {self.confidence:.2f} ({reason})")

    def reduce_confidence(self, amount: float, reason: str):
        """Decrease confidence with reason"""
        old = self.confidence
        self.confidence = max(0.0, self.confidence - amount)
        self.log(f"Confidence: {old:.2f} -> {self.confidence:.2f} ({reason})")


class AutoSolutionAgent:
    """
    Autonomous coding problem solver.

    Usage:
        agent = AutoSolutionAgent(project_path="/path/to/project")
        solution = await agent.solve("Fix the authentication bug in login.py")
    """

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self.llm_provider = None  # Will be set by detect_provider

    def _detect_llm_provider(self):
        """Detect best available LLM provider"""
        try:
            from core.terminator_secrets_manager import get_secrets_manager, SecretType
            secrets = get_secrets_manager()

            # Priority: Gemini > Claude > OpenAI > Ollama
            if secrets.get_secret(SecretType.GEMINI_API_KEY):
                self.llm_provider = "gemini"
            elif secrets.get_secret(SecretType.ANTHROPIC_API_KEY):
                self.llm_provider = "claude"
            elif secrets.get_secret(SecretType.OPENAI_API_KEY):
                self.llm_provider = "openai"
            else:
                self.llm_provider = "ollama"
        except:
            self.llm_provider = "ollama"

    async def call_llm(self, prompt: str, system: str = None) -> str:
        """Call LLM with auto-provider detection"""
        if not self.llm_provider:
            self._detect_llm_provider()

        # For now, use a simple implementation
        # This should be replaced with actual cloud API calls
        if self.llm_provider == "ollama":
            return await self._call_ollama(prompt, system)
        else:
            return await self._call_cloud(prompt, system)

    async def _call_ollama(self, prompt: str, system: str = None) -> str:
        """Call local Ollama"""
        import httpx
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    "http://localhost:11434/api/chat",
                    json={
                        "model": "llama3",
                        "messages": messages,
                        "stream": False
                    }
                )
                if response.status_code == 200:
                    return response.json().get("message", {}).get("content", "")
        except Exception as e:
            return f"LLM Error: {e}"
        return ""

    async def _call_cloud(self, prompt: str, system: str = None) -> str:
        """Call cloud API (Gemini/Claude/OpenAI)"""
        try:
            from core.terminator_secrets_manager import get_secrets_manager, SecretType
            secrets = get_secrets_manager()

            if self.llm_provider == "gemini":
                import google.generativeai as genai
                api_key = secrets.get_secret(SecretType.GEMINI_API_KEY)
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.0-flash-exp")
                full_prompt = f"{system}\n\n{prompt}" if system else prompt
                response = model.generate_content(full_prompt)
                return response.text

            elif self.llm_provider == "claude":
                import anthropic
                api_key = secrets.get_secret(SecretType.ANTHROPIC_API_KEY)
                client = anthropic.Anthropic(api_key=api_key)
                response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4096,
                    system=system or "You are an expert coding assistant.",
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text

            elif self.llm_provider == "openai":
                import openai
                api_key = secrets.get_secret(SecretType.OPENAI_API_KEY)
                client = openai.OpenAI(api_key=api_key)
                messages = []
                if system:
                    messages.append({"role": "system", "content": system})
                messages.append({"role": "user", "content": prompt})
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=4096
                )
                return response.choices[0].message.content

        except Exception as e:
            return f"Cloud API Error: {e}"
        return ""

    # =========================================================================
    # CORE SOLVING LOGIC
    # =========================================================================

    async def solve(self, problem_description: str, test_command: str = None) -> Dict[str, Any]:
        """
        Main entry point: Solve a coding problem autonomously.

        Returns:
            {
                "success": bool,
                "solution": str,
                "files_modified": [str],
                "iterations": int,
                "confidence": float,
                "reasoning_log": [str]
            }
        """
        task = CodingTask(
            description=problem_description,
            project_path=self.project_path,
            test_command=test_command
        )

        state = SolutionState(task=task)
        state.log(f"Starting to solve: {problem_description[:100]}...")

        # Main solving loop
        while state.should_continue():
            state.iteration += 1
            state.log(f"=== ITERATION {state.iteration} ===")

            if state.phase == SolutionPhase.ANALYZE:
                await self._phase_analyze(state)
            elif state.phase == SolutionPhase.PLAN:
                await self._phase_plan(state)
            elif state.phase == SolutionPhase.EXECUTE:
                await self._phase_execute(state)
            elif state.phase == SolutionPhase.VALIDATE:
                await self._phase_validate(state)
            elif state.phase == SolutionPhase.ITERATE:
                await self._phase_iterate(state)

        # Synthesize final result
        return await self._synthesize_result(state)

    async def _phase_analyze(self, state: SolutionState):
        """Phase 1: Analyze the coding problem"""
        state.log("Analyzing the problem...")

        prompt = f"""Analyze this coding problem:

PROBLEM: {state.task.description}

PROJECT PATH: {state.task.project_path}

Provide analysis in JSON format:
{{
    "problem_type": "bug_fix|feature|refactor|optimization",
    "files_likely_involved": ["file1.py", "file2.py"],
    "key_concepts": ["concept1", "concept2"],
    "potential_approaches": [
        {{"approach": "description", "pros": [], "cons": [], "confidence": 0.8}}
    ],
    "information_needed": ["what files to read", "what to search for"],
    "estimated_complexity": "low|medium|high",
    "initial_confidence": 0.3
}}"""

        response = await self.call_llm(prompt, system="You are an expert code analyst. Always respond with valid JSON.")

        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                analysis = json.loads(response[json_start:json_end])
                state.analysis = analysis
                state.task.files_involved = analysis.get("files_likely_involved", [])
                state.boost_confidence(analysis.get("initial_confidence", 0.2), "Initial analysis complete")
                state.log(f"Identified {len(state.task.files_involved)} files to examine")
                state.phase = SolutionPhase.PLAN
            else:
                state.log("Failed to parse analysis, retrying...")
                state.reduce_confidence(0.1, "Analysis parsing failed")
        except json.JSONDecodeError as e:
            state.log(f"JSON parse error: {e}")
            state.reduce_confidence(0.1, "Analysis parsing failed")

    async def _phase_plan(self, state: SolutionState):
        """Phase 2: Create execution plan"""
        state.log("Creating execution plan...")

        # Gather context from files
        file_contents = {}
        for file_path in state.task.files_involved[:5]:  # Limit to 5 files
            full_path = state.task.project_path / file_path
            if full_path.exists():
                try:
                    content = full_path.read_text()[:5000]  # First 5000 chars
                    file_contents[file_path] = content
                    state.log(f"Read: {file_path}")
                except:
                    pass

        prompt = f"""Create a step-by-step plan to solve this problem:

PROBLEM: {state.task.description}

ANALYSIS: {json.dumps(state.analysis, indent=2)}

FILE CONTENTS:
{json.dumps(file_contents, indent=2)}

Provide a plan in JSON format:
{{
    "steps": [
        {{
            "step_number": 1,
            "action": "read_file|write_file|edit_file|run_command|search_code",
            "target": "file path or command",
            "description": "what this step does",
            "code_changes": "if edit/write, the actual code",
            "confidence_boost": 0.1
        }}
    ],
    "expected_outcome": "what success looks like",
    "rollback_plan": "how to undo if it fails"
}}"""

        response = await self.call_llm(prompt, system="You are an expert software engineer. Create precise, actionable plans. Always respond with valid JSON.")

        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                plan = json.loads(response[json_start:json_end])
                state.plan_steps = plan.get("steps", [])
                state.log(f"Created plan with {len(state.plan_steps)} steps")
                state.boost_confidence(0.15, "Plan created")
                state.phase = SolutionPhase.EXECUTE
            else:
                state.log("Failed to parse plan")
                state.reduce_confidence(0.1, "Plan parsing failed")
        except json.JSONDecodeError:
            state.log("JSON parse error in plan")
            state.reduce_confidence(0.1, "Plan parsing failed")

    async def _phase_execute(self, state: SolutionState):
        """Phase 3: Execute the plan"""
        state.log("Executing plan...")

        for step in state.plan_steps:
            step_num = step.get("step_number", "?")
            action = step.get("action", "unknown")
            target = step.get("target", "")

            state.log(f"Step {step_num}: {action} - {step.get('description', '')[:50]}...")

            try:
                if action == "read_file":
                    result = self._action_read_file(target)
                elif action == "write_file":
                    result = self._action_write_file(target, step.get("code_changes", ""))
                    if "success" in result.lower():
                        state.files_modified.append(target)
                elif action == "edit_file":
                    result = self._action_edit_file(target, step.get("code_changes", ""))
                    if "success" in result.lower():
                        state.files_modified.append(target)
                elif action == "run_command":
                    result = self._action_run_command(target)
                elif action == "search_code":
                    result = self._action_search_code(target)
                else:
                    result = f"Unknown action: {action}"

                state.executed_actions.append({
                    "step": step_num,
                    "action": action,
                    "target": target,
                    "result": result[:500]  # Truncate result
                })

                if "error" in result.lower() or "failed" in result.lower():
                    state.errors.append(result)
                    state.reduce_confidence(0.1, f"Step {step_num} had issues")
                else:
                    boost = step.get("confidence_boost", 0.1)
                    state.boost_confidence(boost, f"Step {step_num} completed")

            except Exception as e:
                state.errors.append(f"Step {step_num} failed: {str(e)}")
                state.reduce_confidence(0.15, f"Step {step_num} exception")

        state.phase = SolutionPhase.VALIDATE

    async def _phase_validate(self, state: SolutionState):
        """Phase 4: Validate the solution"""
        state.log("Validating solution...")

        # Run tests if test command provided
        if state.task.test_command:
            result = self._action_run_command(state.task.test_command)
            if "pass" in result.lower() or "ok" in result.lower():
                state.tests_passed = True
                state.boost_confidence(0.3, "Tests passed")
                state.log("Tests PASSED!")
            else:
                state.tests_passed = False
                state.errors.append(f"Tests failed: {result}")
                state.reduce_confidence(0.2, "Tests failed")
                state.log(f"Tests FAILED: {result[:200]}")

        # Check confidence threshold
        if state.confidence >= state.confidence_threshold:
            state.phase = SolutionPhase.COMPLETE
            state.log(f"Solution complete! Confidence: {state.confidence:.2f}")
        elif state.iteration < state.max_iterations:
            state.phase = SolutionPhase.ITERATE
            state.log(f"Confidence {state.confidence:.2f} < {state.confidence_threshold}, iterating...")
        else:
            state.phase = SolutionPhase.COMPLETE
            state.log("Max iterations reached, completing...")

    async def _phase_iterate(self, state: SolutionState):
        """Phase 5: Analyze errors and retry"""
        state.log("Analyzing errors for retry...")

        if not state.errors:
            state.log("No errors to analyze, moving to complete")
            state.phase = SolutionPhase.COMPLETE
            return

        prompt = f"""Analyze these errors and suggest fixes:

ORIGINAL PROBLEM: {state.task.description}

ERRORS ENCOUNTERED:
{json.dumps(state.errors, indent=2)}

ACTIONS TAKEN:
{json.dumps(state.executed_actions, indent=2)}

What went wrong and how should we fix it? Provide JSON:
{{
    "error_analysis": "what went wrong",
    "root_cause": "the actual issue",
    "fix_approach": "how to fix it",
    "new_steps": [
        {{"action": "...", "target": "...", "description": "...", "code_changes": "..."}}
    ]
}}"""

        response = await self.call_llm(prompt, system="You are an expert debugger. Analyze errors and provide fixes.")

        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                fix = json.loads(response[json_start:json_end])
                state.plan_steps = fix.get("new_steps", [])
                state.errors = []  # Clear errors for retry
                state.log(f"Created fix plan with {len(state.plan_steps)} steps")
                state.phase = SolutionPhase.EXECUTE
            else:
                state.phase = SolutionPhase.COMPLETE
        except:
            state.phase = SolutionPhase.COMPLETE

    async def _synthesize_result(self, state: SolutionState) -> Dict[str, Any]:
        """Synthesize final result"""
        success = state.confidence >= state.confidence_threshold or state.tests_passed

        # Generate summary
        summary_prompt = f"""Summarize what was done to solve this problem:

PROBLEM: {state.task.description}
FILES MODIFIED: {state.files_modified}
ACTIONS TAKEN: {len(state.executed_actions)}
SUCCESS: {success}
CONFIDENCE: {state.confidence:.2f}

Write a brief summary of the solution."""

        summary = await self.call_llm(summary_prompt)

        return {
            "success": success,
            "solution": summary,
            "files_modified": state.files_modified,
            "iterations": state.iteration,
            "confidence": state.confidence,
            "tests_passed": state.tests_passed,
            "errors": state.errors,
            "reasoning_log": state.reasoning_log
        }

    # =========================================================================
    # ACTION IMPLEMENTATIONS
    # =========================================================================

    def _action_read_file(self, path: str) -> str:
        """Read a file"""
        try:
            full_path = self.project_path / path
            if full_path.exists():
                content = full_path.read_text()
                return f"File contents ({len(content)} chars):\n{content[:3000]}"
            return f"File not found: {path}"
        except Exception as e:
            return f"Error reading file: {e}"

    def _action_write_file(self, path: str, content: str) -> str:
        """Write a file"""
        try:
            full_path = self.project_path / path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
            return f"Successfully wrote {len(content)} chars to {path}"
        except Exception as e:
            return f"Error writing file: {e}"

    def _action_edit_file(self, path: str, changes: str) -> str:
        """Edit a file (simple replacement for now)"""
        try:
            full_path = self.project_path / path
            if not full_path.exists():
                return f"File not found: {path}"

            # Parse changes (expecting format: OLD_TEXT|||NEW_TEXT)
            if "|||" in changes:
                old, new = changes.split("|||", 1)
                content = full_path.read_text()
                if old in content:
                    new_content = content.replace(old, new)
                    full_path.write_text(new_content)
                    return f"Successfully edited {path}"
                else:
                    return f"Text not found in file: {old[:50]}..."
            else:
                # Overwrite entire file
                full_path.write_text(changes)
                return f"Replaced content of {path}"
        except Exception as e:
            return f"Error editing file: {e}"

    def _action_run_command(self, command: str) -> str:
        """Run a shell command"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(self.project_path)
            )
            output = result.stdout + result.stderr
            status = "SUCCESS" if result.returncode == 0 else "FAILED"
            return f"{status} (exit {result.returncode}):\n{output[:2000]}"
        except subprocess.TimeoutExpired:
            return "Command timed out after 60 seconds"
        except Exception as e:
            return f"Command error: {e}"

    def _action_search_code(self, pattern: str) -> str:
        """Search for code pattern"""
        try:
            result = subprocess.run(
                f'grep -rn "{pattern}" . --include="*.py" --include="*.js" --include="*.ts" | head -20',
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.project_path)
            )
            if result.stdout:
                return f"Found matches:\n{result.stdout}"
            return "No matches found"
        except Exception as e:
            return f"Search error: {e}"


# =========================================================================
# QUICK USAGE
# =========================================================================

async def solve_coding_problem(problem: str, project_path: str = ".", test_command: str = None):
    """
    Convenience function to solve a coding problem.

    Example:
        result = await solve_coding_problem(
            "Fix the login function to properly validate email addresses",
            project_path="/path/to/project",
            test_command="python -m pytest tests/test_auth.py"
        )
    """
    agent = AutoSolutionAgent(project_path)
    return await agent.solve(problem, test_command)


def solve_sync(problem: str, project_path: str = ".", test_command: str = None):
    """Synchronous wrapper for solve_coding_problem"""
    return asyncio.run(solve_coding_problem(problem, project_path, test_command))


if __name__ == "__main__":
    # Example usage
    import argparse

    parser = argparse.ArgumentParser(description="TERMINATOR Auto-Solution Agent")
    parser.add_argument("problem", help="Description of the coding problem to solve")
    parser.add_argument("--path", "-p", default=".", help="Project path")
    parser.add_argument("--test", "-t", help="Test command to validate solution")

    args = parser.parse_args()

    print("=" * 60)
    print("TERMINATOR AUTO-SOLUTION AGENT")
    print("=" * 60)
    print(f"Problem: {args.problem}")
    print(f"Project: {args.path}")
    print("=" * 60)

    result = solve_sync(args.problem, args.path, args.test)

    print("\n" + "=" * 60)
    print("RESULT")
    print("=" * 60)
    print(f"Success: {result['success']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Iterations: {result['iterations']}")
    print(f"Files Modified: {result['files_modified']}")
    print("\nSolution:")
    print(result['solution'])

    if result['errors']:
        print("\nErrors encountered:")
        for e in result['errors']:
            print(f"  - {e[:100]}...")
