#!/usr/bin/env python3
"""
TERMINATOR Pre-flight Health Check
===================================

Runs comprehensive system diagnostics before starting TERMINATOR.
Checks: Ollama, Python deps, core agents, disk space, ports, etc.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    console = Console()
except ImportError:
    class Console:
        def print(self, *args, **kwargs):
            print(*[str(a).replace('[bold', '').replace('[/bold', '').replace(']', '').replace('[green', '').replace('[red', '').replace('[yellow', '').replace('[cyan', '') for a in args])
    console = Console()


class HealthChecker:
    """Comprehensive TERMINATOR health checker."""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.results = {}
        self.all_passed = True

    def check_ollama(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                self.results["ollama"] = {
                    "status": "running",
                    "models": [m.get("name") for m in models[:5]]
                }
                return True
        except Exception as e:
            self.results["ollama"] = {"status": "not running", "error": str(e)}
        return False

    def check_python_deps(self) -> bool:
        """Check required Python dependencies."""
        required = ["rich", "requests", "asyncio"]
        missing = []

        for pkg in required:
            try:
                __import__(pkg)
            except ImportError:
                missing.append(pkg)

        self.results["python_deps"] = {
            "required": required,
            "missing": missing,
            "status": "ok" if not missing else "missing"
        }
        return len(missing) == 0

    def check_core_agents(self) -> bool:
        """Check if core agent files exist."""
        core_agents = [
            "terminator_agent_communication_bus.py",
            "terminator_agentic_orchestrator.py",
            "advanced_agentic_orchestrator.py",
            "terminator_decision_engine.py",
        ]

        core_dir = self.project_root / "core"
        found = []
        missing = []

        for agent in core_agents:
            if (core_dir / agent).exists():
                found.append(agent)
            else:
                missing.append(agent)

        self.results["core_agents"] = {
            "found": len(found),
            "missing": missing,
            "status": "ok" if not missing else "incomplete"
        }
        return len(missing) == 0

    def check_disk_space(self) -> bool:
        """Check available disk space."""
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            free_gb = free // (1024**3)
            used_percent = (used / total) * 100

            self.results["disk"] = {
                "free_gb": free_gb,
                "used_percent": round(used_percent, 1),
                "status": "ok" if free_gb > 5 else "low"
            }
            return free_gb > 5
        except:
            self.results["disk"] = {"status": "unknown"}
            return True

    def check_ports(self) -> bool:
        """Check if required ports are available."""
        import socket
        ports = {8000: "Web Terminal", 11434: "Ollama"}
        results = {}

        for port, name in ports.items():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()

            if port == 11434:  # Ollama should be running
                results[port] = {"name": name, "status": "active" if result == 0 else "inactive"}
            else:  # Web terminal port should be available
                results[port] = {"name": name, "status": "available" if result != 0 else "in use"}

        self.results["ports"] = results
        return True

    def check_config_files(self) -> bool:
        """Check critical config files."""
        configs = {
            "CLAUDE.md": self.project_root / "CLAUDE.md",
            ".claude/settings.json": self.project_root / ".claude" / "settings.json",
        }

        found = {}
        for name, path in configs.items():
            found[name] = path.exists()

        self.results["configs"] = found
        return all(found.values())

    def run_all_checks(self) -> bool:
        """Run all health checks."""
        console.print("\n[bold cyan]🏥 TERMINATOR Health Check[/bold cyan]\n")

        checks = [
            ("Ollama LLM", self.check_ollama),
            ("Python Dependencies", self.check_python_deps),
            ("Core Agents", self.check_core_agents),
            ("Disk Space", self.check_disk_space),
            ("Network Ports", self.check_ports),
            ("Config Files", self.check_config_files),
        ]

        table = Table(show_header=True)
        table.add_column("Check", style="cyan", width=25)
        table.add_column("Status", width=15)
        table.add_column("Details", width=40)

        for name, check_func in checks:
            try:
                passed = check_func()
                status = "[green]✓ PASS[/green]" if passed else "[red]✗ FAIL[/red]"
                if not passed:
                    self.all_passed = False
            except Exception as e:
                status = "[yellow]⚠ WARN[/yellow]"
                self.results[name.lower().replace(" ", "_")] = {"error": str(e)}

            # Get details
            key = name.lower().replace(" ", "_")
            if key == "ollama_llm":
                key = "ollama"
            result = self.results.get(key, {})

            if isinstance(result, dict):
                if "models" in result:
                    details = f"Models: {', '.join(result['models'][:3])}"
                elif "missing" in result and result["missing"]:
                    details = f"Missing: {', '.join(result['missing'][:3])}"
                elif "free_gb" in result:
                    details = f"{result['free_gb']}GB free ({result['used_percent']}% used)"
                elif "error" in result:
                    details = f"Error: {result['error'][:30]}..."
                else:
                    details = result.get("status", "checked")
            else:
                details = str(result)

            table.add_row(name, status, details)

        console.print(table)
        console.print()

        # Summary
        if self.all_passed:
            console.print("[bold green]✅ All checks passed! TERMINATOR is ready.[/bold green]\n")
        else:
            console.print("[bold yellow]⚠️  Some checks failed. Review above for details.[/bold yellow]\n")

        # Save results
        self.save_results()

        return self.all_passed

    def save_results(self):
        """Save health check results to file."""
        results_dir = self.project_root / ".health_checks"
        results_dir.mkdir(exist_ok=True)

        results_file = results_dir / "latest_health_report.json"
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "all_passed": self.all_passed,
                "results": self.results
            }, f, indent=2)

        # Also create readable text report
        text_file = results_dir / "latest_health_report.txt"
        with open(text_file, 'w') as f:
            f.write(f"TERMINATOR Health Report\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Status: {'HEALTHY' if self.all_passed else 'ISSUES DETECTED'}\n\n")
            for key, value in self.results.items():
                f.write(f"{key}: {json.dumps(value)}\n")


def main():
    """Run health check."""
    checker = HealthChecker()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
