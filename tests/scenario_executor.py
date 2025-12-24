#!/usr/bin/env python3
"""
TERMINATOR Scenario Executor
=============================

Executes real-world scenarios against TERMINATOR and evaluates:
1. Can TERMINATOR complete the task?
2. Did TERMINATOR learn a new capability?
3. What actions were taken?
4. How long did it take?

This creates a feedback loop for continuous improvement.
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.progress import track

console = Console()


class ScenarioExecutor:
    """Executes scenarios and evaluates TERMINATOR's performance"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.terminator_cli = self.project_root / "terminator_universal_cli.py"
        self.results_dir = self.project_root / "test_results" / "scenarios"
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.capability_log = Path.home() / ".terminator_capabilities.json"
        self.knowledge_base = Path.home() / ".terminator_knowledge"

    def execute_scenario(self, scenario_request: str, timeout: int = 60) -> Dict[str, Any]:
        """
        Execute a scenario by sending request to TERMINATOR
        and capturing the response
        """
        console.print(f"\n[cyan]Executing:[/cyan] {scenario_request[:60]}...")

        start_time = time.time()
        result = {
            "request": scenario_request,
            "status": "unknown",
            "output": "",
            "actions_detected": [],
            "tools_used": [],
            "learned_capabilities": [],
            "errors": [],
            "execution_time": 0
        }

        try:
            # Create input for TERMINATOR
            input_text = f"{scenario_request}\nexit\n"

            # Run TERMINATOR with the scenario
            process = subprocess.Popen(
                [sys.executable, str(self.terminator_cli)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Send input and get output
            stdout, stderr = process.communicate(input=input_text, timeout=timeout)

            result["output"] = stdout
            result["execution_time"] = time.time() - start_time

            # Analyze output for actions taken
            result["actions_detected"] = self.analyze_actions(stdout)
            result["tools_used"] = self.analyze_tools_used(stdout)

            # Check if TERMINATOR learned something new
            learned = self.check_for_learning(stdout)
            if learned:
                result["learned_capabilities"] = learned
                result["status"] = "learned"
            else:
                # Check if task was completed successfully
                if self.check_success(stdout, scenario_request):
                    result["status"] = "success"
                else:
                    result["status"] = "partial"

        except subprocess.TimeoutExpired:
            result["status"] = "timeout"
            result["errors"].append("Execution timed out")
            process.kill()

        except Exception as e:
            result["status"] = "error"
            result["errors"].append(str(e))

        return result

    def analyze_actions(self, output: str) -> List[str]:
        """Detect what actions TERMINATOR took"""
        actions = []

        # Look for tool calls
        tool_indicators = {
            "read_file": ["Reading file", "File contents:", "read_file"],
            "write_file": ["Writing to file", "Created file", "write_file"],
            "bash": ["Executing:", "Command:", "bash"],
            "web_search": ["Searching web", "Search results", "web_search"],
            "git": ["git status", "git commit", "git push"],
            "install_package": ["Installing", "pip install", "Successfully installed"]
        }

        for tool, indicators in tool_indicators.items():
            if any(indicator in output for indicator in indicators):
                actions.append(tool)

        return actions

    def analyze_tools_used(self, output: str) -> List[str]:
        """Extract which tools were actually used"""
        tools = []

        # Look for tool call patterns
        if "<tool_call>" in output or "tool_call" in output:
            # Extract JSON tool calls
            import re
            tool_pattern = r'"tool":\s*"([^"]+)"'
            matches = re.findall(tool_pattern, output)
            tools.extend(matches)

        return list(set(tools))

    def check_for_learning(self, output: str) -> List[str]:
        """Check if TERMINATOR learned a new capability"""
        learned = []

        learning_indicators = [
            "detect_and_learn",
            "Capability gap detected",
            "consult_claude",
            "install_package",
            "learning from web",
            "consulting external AI",
            "Let me learn that"
        ]

        if any(indicator in output for indicator in learning_indicators):
            # Check capability log for new entries
            if self.capability_log.exists():
                with open(self.capability_log) as f:
                    caps = json.load(f)
                    learned = caps.get("tools_added", [])

        return learned

    def check_success(self, output: str, request: str) -> bool:
        """Heuristically determine if task was successful"""
        # Success indicators
        success_patterns = [
            "✅",
            "Success",
            "completed",
            "done",
            "finished",
            "Task complete"
        ]

        # Failure indicators
        failure_patterns = [
            "❌",
            "Error",
            "failed",
            "cannot",
            "I can't",
            "I don't know"
        ]

        # Count indicators
        success_count = sum(1 for pattern in success_patterns if pattern in output)
        failure_count = sum(1 for pattern in failure_patterns if pattern in output)

        return success_count > failure_count

    def save_result(self, scenario_name: str, result: Dict[str, Any]):
        """Save scenario execution result"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Sanitize scenario name for filename
        safe_name = "".join(c if c.isalnum() else "_" for c in scenario_name)
        filename = f"{safe_name}_{timestamp}.json"

        filepath = self.results_dir / filename

        with open(filepath, 'w') as f:
            json.dump(result, f, indent=2)

        console.print(f"[dim]Result saved: {filepath}[/dim]")

    def generate_learning_report(self, all_results: List[Dict[str, Any]]):
        """Generate report on what TERMINATOR learned"""
        console.print("\n[bold cyan]═══════════════════════════════════════[/bold cyan]")
        console.print("[bold cyan]  Learning & Adaptation Report[/bold cyan]")
        console.print("[bold cyan]═══════════════════════════════════════[/bold cyan]\n")

        # Capabilities learned
        all_learned = set()
        for result in all_results:
            all_learned.update(result.get("learned_capabilities", []))

        if all_learned:
            console.print("[bold green]✓ New Capabilities Learned:[/bold green]")
            for cap in all_learned:
                console.print(f"  • {cap}")
        else:
            console.print("[yellow]No new capabilities learned in this session[/yellow]")

        # Tools most used
        tool_usage = {}
        for result in all_results:
            for tool in result.get("tools_used", []):
                tool_usage[tool] = tool_usage.get(tool, 0) + 1

        if tool_usage:
            console.print("\n[bold cyan]Most Used Tools:[/bold cyan]")
            sorted_tools = sorted(tool_usage.items(), key=lambda x: x[1], reverse=True)
            for tool, count in sorted_tools[:5]:
                console.print(f"  • {tool}: {count} times")

        # Success rate
        success_count = sum(1 for r in all_results if r["status"] == "success")
        learning_count = sum(1 for r in all_results if r["status"] == "learned")
        total = len(all_results)

        console.print(f"\n[bold]Overall Success Rate:[/bold] {success_count + learning_count}/{total} ({(success_count + learning_count)/total*100:.1f}%)")
        console.print(f"  • Direct Success: {success_count}")
        console.print(f"  • Success via Learning: {learning_count}")


def run_quick_tests():
    """Run a quick subset of important scenarios"""
    executor = ScenarioExecutor()

    quick_scenarios = [
        ("File Read Test", "Read README.md and tell me what this project does"),
        ("Web Search Test", "Search for Python 3.13 new features"),
        ("Learning Test", "Convert this markdown to PDF: test.md"),
        ("Git Test", "Show me my recent git commits"),
        ("Shell Test", "Check disk space on my system"),
    ]

    results = []

    for name, request in track(quick_scenarios, description="Running quick tests..."):
        console.print(f"\n[bold cyan]Test:[/bold cyan] {name}")
        result = executor.execute_scenario(request, timeout=30)
        result["scenario_name"] = name
        results.append(result)

        # Show quick status
        status_color = {
            "success": "green",
            "learned": "blue",
            "partial": "yellow",
            "error": "red",
            "timeout": "red"
        }.get(result["status"], "white")

        console.print(f"[{status_color}]Status: {result['status']}[/{status_color}]")
        executor.save_result(name, result)

    # Generate learning report
    executor.generate_learning_report(results)


if __name__ == "__main__":
    console.print("[bold green]TERMINATOR Scenario Executor[/bold green]")
    console.print("[dim]Testing real-world capabilities...[/dim]\n")

    run_quick_tests()

    console.print("\n[bold green]✓ Quick tests complete![/bold green]")
