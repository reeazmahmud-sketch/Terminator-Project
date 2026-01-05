#!/usr/bin/env python3
"""
TERMINATOR Test Runner Agent

Executes test suites, analyzes results, and provides actionable feedback.
Supports multiple test frameworks: pytest, jest, npm test, unittest, etc.

Usage:
    from core.terminator_test_runner_agent import TestRunnerAgent

    agent = TestRunnerAgent()
    result = await agent.run_tests()
"""

import asyncio
import subprocess
import json
import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

# Import communication bus if available
try:
    from core.terminator_agent_communication_bus import get_communication_bus
    HAS_BUS = True
except ImportError:
    HAS_BUS = False


class TestFramework(Enum):
    """Supported test frameworks."""
    PYTEST = "pytest"
    JEST = "jest"
    NPM_TEST = "npm test"
    UNITTEST = "unittest"
    MOCHA = "mocha"
    VITEST = "vitest"
    GO_TEST = "go test"
    CARGO_TEST = "cargo test"
    UNKNOWN = "unknown"


class TestStatus(Enum):
    """Test execution status."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class TestResult:
    """Individual test result."""
    name: str
    status: TestStatus
    duration: float = 0.0
    error_message: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class TestSuiteResult:
    """Complete test suite result."""
    framework: TestFramework
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    duration: float = 0.0
    tests: List[TestResult] = field(default_factory=list)
    raw_output: str = ""
    exit_code: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class TestRunnerAgent:
    """
    Autonomous test execution agent.

    Detects test frameworks, runs tests, parses output, and provides
    actionable feedback for failures.
    """

    AGENT_NAME = "test_runner_agent"

    # Framework detection patterns
    FRAMEWORK_FILES = {
        TestFramework.PYTEST: ["pytest.ini", "pyproject.toml", "setup.cfg", "conftest.py"],
        TestFramework.JEST: ["jest.config.js", "jest.config.ts", "jest.config.json"],
        TestFramework.VITEST: ["vitest.config.js", "vitest.config.ts"],
        TestFramework.MOCHA: [".mocharc.js", ".mocharc.json", ".mocharc.yaml"],
        TestFramework.GO_TEST: ["go.mod"],
        TestFramework.CARGO_TEST: ["Cargo.toml"],
    }

    # Test commands by framework
    TEST_COMMANDS = {
        TestFramework.PYTEST: ["python3", "-m", "pytest", "-v", "--tb=short"],
        TestFramework.JEST: ["npx", "jest", "--verbose"],
        TestFramework.NPM_TEST: ["npm", "test"],
        TestFramework.VITEST: ["npx", "vitest", "run"],
        TestFramework.MOCHA: ["npx", "mocha"],
        TestFramework.UNITTEST: ["python3", "-m", "unittest", "discover", "-v"],
        TestFramework.GO_TEST: ["go", "test", "-v", "./..."],
        TestFramework.CARGO_TEST: ["cargo", "test"],
    }

    def __init__(self, project_path: Optional[str] = None):
        """Initialize with optional project path."""
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.bus = get_communication_bus() if HAS_BUS else None
        self._registered = False

    async def register(self) -> None:
        """Register with the communication bus."""
        if self.bus and not self._registered:
            await self.bus.register_agent_async(self.AGENT_NAME)
            self._registered = True

    def detect_framework(self) -> TestFramework:
        """Auto-detect the test framework used in the project."""
        # Check for framework-specific config files
        for framework, files in self.FRAMEWORK_FILES.items():
            for file in files:
                if (self.project_path / file).exists():
                    return framework

        # Check package.json for npm-based projects
        package_json = self.project_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    pkg = json.load(f)
                    scripts = pkg.get("scripts", {})
                    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

                    if "vitest" in deps:
                        return TestFramework.VITEST
                    if "jest" in deps:
                        return TestFramework.JEST
                    if "mocha" in deps:
                        return TestFramework.MOCHA
                    if "test" in scripts:
                        return TestFramework.NPM_TEST
            except json.JSONDecodeError:
                pass

        # Check for Python test files
        if list(self.project_path.rglob("test_*.py")) or list(self.project_path.rglob("*_test.py")):
            if (self.project_path / "pytest.ini").exists() or (self.project_path / "conftest.py").exists():
                return TestFramework.PYTEST
            return TestFramework.UNITTEST

        return TestFramework.UNKNOWN

    async def run_tests(
        self,
        framework: Optional[TestFramework] = None,
        test_path: Optional[str] = None,
        pattern: Optional[str] = None,
        timeout: int = 300,
        coverage: bool = False
    ) -> TestSuiteResult:
        """
        Run tests and return parsed results.

        Args:
            framework: Override auto-detected framework
            test_path: Specific test file or directory
            pattern: Test name pattern to match (e.g., "test_auth*")
            timeout: Maximum execution time in seconds
            coverage: Enable coverage reporting

        Returns:
            TestSuiteResult with parsed test outcomes
        """
        if framework is None:
            framework = self.detect_framework()

        if framework == TestFramework.UNKNOWN:
            return TestSuiteResult(
                framework=framework,
                raw_output="No test framework detected",
                exit_code=1,
                errors=1
            )

        # Build command
        cmd = self.TEST_COMMANDS.get(framework, ["echo", "Unknown framework"])
        cmd = list(cmd)  # Copy to avoid modifying original

        # Add coverage if requested
        if coverage:
            if framework == TestFramework.PYTEST:
                cmd.extend(["--cov", "--cov-report=term-missing"])
            elif framework in [TestFramework.JEST, TestFramework.VITEST]:
                cmd.append("--coverage")

        # Add specific test path
        if test_path:
            cmd.append(test_path)

        # Add pattern filter
        if pattern:
            if framework == TestFramework.PYTEST:
                cmd.extend(["-k", pattern])
            elif framework == TestFramework.JEST:
                cmd.extend(["-t", pattern])

        # Execute tests
        result = await self._execute_command(cmd, timeout)

        # Parse results based on framework
        parsed = self._parse_output(framework, result)

        # Notify via bus if available
        if self.bus and self._registered:
            await self._notify_results(parsed)

        return parsed

    async def _execute_command(
        self,
        cmd: List[str],
        timeout: int
    ) -> Tuple[str, int]:
        """Execute test command and return output + exit code."""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=str(self.project_path)
            )

            try:
                stdout, _ = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                return stdout.decode("utf-8", errors="replace"), process.returncode or 0
            except asyncio.TimeoutError:
                process.kill()
                return f"Test execution timed out after {timeout}s", -1

        except FileNotFoundError as e:
            return f"Command not found: {cmd[0]}. Error: {e}", 127
        except Exception as e:
            return f"Execution error: {e}", 1

    def _parse_output(
        self,
        framework: TestFramework,
        result: Tuple[str, int]
    ) -> TestSuiteResult:
        """Parse test output based on framework."""
        output, exit_code = result

        suite = TestSuiteResult(
            framework=framework,
            raw_output=output,
            exit_code=exit_code
        )

        if framework == TestFramework.PYTEST:
            suite = self._parse_pytest(output, suite)
        elif framework in [TestFramework.JEST, TestFramework.VITEST]:
            suite = self._parse_jest(output, suite)
        elif framework == TestFramework.NPM_TEST:
            suite = self._parse_npm_test(output, suite)
        elif framework == TestFramework.GO_TEST:
            suite = self._parse_go_test(output, suite)
        else:
            # Generic parsing
            suite = self._parse_generic(output, suite)

        return suite

    def _parse_pytest(self, output: str, suite: TestSuiteResult) -> TestSuiteResult:
        """Parse pytest output."""
        # Summary line: "5 passed, 2 failed, 1 skipped in 2.34s"
        summary_match = re.search(
            r"=+ ([\d\w\s,]+) in ([\d.]+)s =+",
            output
        )

        if summary_match:
            summary = summary_match.group(1)
            suite.duration = float(summary_match.group(2))

            for part in summary.split(","):
                part = part.strip()
                if "passed" in part:
                    suite.passed = int(re.search(r"(\d+)", part).group(1))
                elif "failed" in part:
                    suite.failed = int(re.search(r"(\d+)", part).group(1))
                elif "skipped" in part:
                    suite.skipped = int(re.search(r"(\d+)", part).group(1))
                elif "error" in part:
                    suite.errors = int(re.search(r"(\d+)", part).group(1))

        suite.total = suite.passed + suite.failed + suite.skipped + suite.errors

        # Parse individual failures
        failure_pattern = re.compile(
            r"FAILED ([\w/_.]+)::(\w+).*?\n(.*?)(?=FAILED|=====)",
            re.DOTALL
        )

        for match in failure_pattern.finditer(output):
            file_path, test_name, error = match.groups()
            suite.tests.append(TestResult(
                name=test_name,
                status=TestStatus.FAILED,
                file_path=file_path,
                error_message=error.strip()[:500],
                suggestion=self._suggest_fix(error)
            ))

        return suite

    def _parse_jest(self, output: str, suite: TestSuiteResult) -> TestSuiteResult:
        """Parse Jest/Vitest output."""
        # Test Suites: 2 passed, 1 failed, 3 total
        # Tests: 10 passed, 2 failed, 12 total
        tests_match = re.search(
            r"Tests:\s+(\d+)\s+passed,\s*(\d+)?\s*failed?,?\s*(\d+)?\s*skipped?,?\s*(\d+)\s+total",
            output
        )

        if tests_match:
            suite.passed = int(tests_match.group(1) or 0)
            suite.failed = int(tests_match.group(2) or 0)
            suite.skipped = int(tests_match.group(3) or 0)
            suite.total = int(tests_match.group(4) or 0)

        # Time
        time_match = re.search(r"Time:\s+([\d.]+)\s*s", output)
        if time_match:
            suite.duration = float(time_match.group(1))

        # Parse failures
        failure_pattern = re.compile(
            r"✕ (.+?)\n\s+(.+?)(?=✓|✕|$)",
            re.DOTALL
        )

        for match in failure_pattern.finditer(output):
            test_name, error = match.groups()
            suite.tests.append(TestResult(
                name=test_name.strip(),
                status=TestStatus.FAILED,
                error_message=error.strip()[:500],
                suggestion=self._suggest_fix(error)
            ))

        return suite

    def _parse_npm_test(self, output: str, suite: TestSuiteResult) -> TestSuiteResult:
        """Parse npm test output (usually wraps another framework)."""
        # Check if it's wrapping Jest
        if "PASS" in output or "FAIL" in output:
            return self._parse_jest(output, suite)

        # Check if it's wrapping Mocha
        if "passing" in output.lower():
            passing_match = re.search(r"(\d+)\s+passing", output)
            failing_match = re.search(r"(\d+)\s+failing", output)

            suite.passed = int(passing_match.group(1)) if passing_match else 0
            suite.failed = int(failing_match.group(1)) if failing_match else 0
            suite.total = suite.passed + suite.failed

        return suite

    def _parse_go_test(self, output: str, suite: TestSuiteResult) -> TestSuiteResult:
        """Parse go test output."""
        passed = len(re.findall(r"--- PASS:", output))
        failed = len(re.findall(r"--- FAIL:", output))
        skipped = len(re.findall(r"--- SKIP:", output))

        suite.passed = passed
        suite.failed = failed
        suite.skipped = skipped
        suite.total = passed + failed + skipped

        # Parse failures
        failure_pattern = re.compile(
            r"--- FAIL: (\w+).*?\n(.*?)(?=--- |FAIL\t|PASS\t|ok\t)",
            re.DOTALL
        )

        for match in failure_pattern.finditer(output):
            test_name, error = match.groups()
            suite.tests.append(TestResult(
                name=test_name,
                status=TestStatus.FAILED,
                error_message=error.strip()[:500]
            ))

        return suite

    def _parse_generic(self, output: str, suite: TestSuiteResult) -> TestSuiteResult:
        """Generic parser for unknown frameworks."""
        # Count common patterns
        suite.passed = len(re.findall(r"(PASS|OK|✓|passed)", output, re.IGNORECASE))
        suite.failed = len(re.findall(r"(FAIL|ERROR|✗|failed)", output, re.IGNORECASE))
        suite.total = suite.passed + suite.failed

        return suite

    def _suggest_fix(self, error: str) -> Optional[str]:
        """Generate fix suggestions based on error patterns."""
        error_lower = error.lower()

        suggestions = {
            "assertionerror": "Check expected vs actual values. Verify test data is correct.",
            "importerror": "Verify module is installed and import path is correct.",
            "modulenotfounderror": "Run 'pip install <module>' or check PYTHONPATH.",
            "typeerror": "Check function arguments and types match expectations.",
            "attributeerror": "Verify object has the expected attribute or method.",
            "keyerror": "Check dictionary key exists before accessing.",
            "indexerror": "Verify list/array index is within bounds.",
            "timeout": "Consider increasing timeout or optimizing the test.",
            "connection": "Check network connectivity or mock external services.",
            "undefined": "Verify variable is defined before use.",
            "null": "Add null checks or ensure value is initialized.",
            "cannot read propert": "Object may be undefined. Add null checks.",
        }

        for pattern, suggestion in suggestions.items():
            if pattern in error_lower:
                return suggestion

        return None

    async def _notify_results(self, result: TestSuiteResult) -> None:
        """Send test results to the communication bus."""
        if not self.bus:
            return

        await self.bus.send_message_async(
            sender_agent=self.AGENT_NAME,
            recipient_agent="orchestrator",
            subject="Test Results",
            content={
                "framework": result.framework.value,
                "total": result.total,
                "passed": result.passed,
                "failed": result.failed,
                "duration": result.duration,
                "status": "passed" if result.failed == 0 else "failed"
            }
        )

    def format_report(self, result: TestSuiteResult) -> str:
        """Generate human-readable test report."""
        status_icon = "✅" if result.failed == 0 and result.errors == 0 else "❌"

        report = [
            "",
            "═" * 60,
            f"   TEST RESULTS {status_icon}",
            "═" * 60,
            f"Framework:  {result.framework.value}",
            f"Duration:   {result.duration:.2f}s",
            f"Exit Code:  {result.exit_code}",
            "",
            f"  ✅ Passed:  {result.passed}",
            f"  ❌ Failed:  {result.failed}",
            f"  ⏭️  Skipped: {result.skipped}",
            f"  💥 Errors:  {result.errors}",
            f"  ━━━━━━━━━━━━",
            f"  📊 Total:   {result.total}",
        ]

        if result.tests:
            report.append("")
            report.append("─" * 60)
            report.append("FAILURES:")
            report.append("─" * 60)

            for test in result.tests:
                if test.status == TestStatus.FAILED:
                    report.append(f"\n❌ {test.name}")
                    if test.file_path:
                        report.append(f"   File: {test.file_path}")
                    if test.error_message:
                        # Truncate long errors
                        error_lines = test.error_message.split("\n")[:5]
                        for line in error_lines:
                            report.append(f"   {line[:80]}")
                    if test.suggestion:
                        report.append(f"   💡 Suggestion: {test.suggestion}")

        report.append("")
        report.append("═" * 60)

        return "\n".join(report)


# CLI interface
async def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="TERMINATOR Test Runner Agent - Execute and analyze tests"
    )
    parser.add_argument(
        "--path", "-p",
        help="Project path (default: current directory)"
    )
    parser.add_argument(
        "--framework", "-f",
        choices=[f.value for f in TestFramework if f != TestFramework.UNKNOWN],
        help="Override auto-detected framework"
    )
    parser.add_argument(
        "--test", "-t",
        help="Specific test file or pattern"
    )
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Enable coverage reporting"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout in seconds (default: 300)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    agent = TestRunnerAgent(args.path)

    framework = None
    if args.framework:
        framework = TestFramework(args.framework)

    result = await agent.run_tests(
        framework=framework,
        test_path=args.test,
        coverage=args.coverage,
        timeout=args.timeout
    )

    if args.json:
        output = {
            "framework": result.framework.value,
            "total": result.total,
            "passed": result.passed,
            "failed": result.failed,
            "skipped": result.skipped,
            "errors": result.errors,
            "duration": result.duration,
            "exit_code": result.exit_code,
            "tests": [
                {
                    "name": t.name,
                    "status": t.status.value,
                    "error": t.error_message,
                    "suggestion": t.suggestion
                }
                for t in result.tests
            ]
        }
        print(json.dumps(output, indent=2))
    else:
        print(agent.format_report(result))

    # Exit with test status
    exit(0 if result.failed == 0 and result.errors == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
