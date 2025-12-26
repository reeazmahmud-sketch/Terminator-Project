#!/usr/bin/env python3

# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Session Manager - Automatic Documentation & Quality Gates
====================================================================

Automatically creates and manages:
1. Session log files (CLAUDE_ANALYSIS_LOG_*.md)
2. Complete test cases
3. Test case guides
4. Test suite summaries
5. Quality gate enforcement
6. Progress monitoring

Features:
- Auto-creates log file at session start
- Tracks all changes and actions
- Generates test cases automatically
- Enforces task completion before progression
- Assigns monitoring agents
- Prevents incomplete work

Created: December 17, 2025
"""

import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum

from core.terminator_agent_communication_bus import get_communication_bus, MessageType, MessagePriority
from terminator_multi_agent_orchestrator import get_orchestrator, TaskPriority, TaskStatus


# ============================================================================
# Data Structures
# ============================================================================

class SessionPhase(str, Enum):
    """Phases of a work session"""
    INITIALIZATION = "initialization"
    PLANNING = "planning"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    QUALITY_CHECK = "quality_check"
    COMPLETION = "completion"


class QualityGateStatus(str, Enum):
    """Status of quality gates"""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class QualityGate:
    """Represents a quality gate that must pass before progression"""
    gate_id: str
    name: str
    description: str
    required_for_phase: SessionPhase
    status: QualityGateStatus = QualityGateStatus.PENDING
    checks: List[str] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)
    assigned_agent: Optional[str] = None
    checked_at: Optional[str] = None


@dataclass
class TestCase:
    """Represents a test case"""
    test_id: str
    name: str
    description: str
    category: str  # unit, integration, e2e, manual
    steps: List[str] = field(default_factory=list)
    expected_result: str = ""
    actual_result: str = ""
    status: str = "pending"  # pending, passed, failed, skipped
    assigned_agent: Optional[str] = None
    executed_at: Optional[str] = None


@dataclass
class SessionLog:
    """Complete session log"""
    session_id: str
    date: str
    start_time: str
    end_time: Optional[str] = None
    project_name: str = "TERMINATOR"
    developer: str = "Claude Sonnet 4.5"

    current_phase: SessionPhase = SessionPhase.INITIALIZATION
    tasks_completed: List[str] = field(default_factory=list)
    files_created: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)

    quality_gates: List[QualityGate] = field(default_factory=list)
    test_cases: List[TestCase] = field(default_factory=list)

    agents_assigned: List[str] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)

    notes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Session Manager
# ============================================================================

class SessionManager:
    """
    Manages work sessions with automatic documentation and quality gates.
    Ensures nothing is missed and enforces completion before progression.
    """

    def __init__(self, project_name: str = "TERMINATOR"):
        self.project_name = project_name
        self.bus = get_communication_bus()
        self.orchestrator = get_orchestrator()

        # Session tracking
        self.current_session: Optional[SessionLog] = None
        self.session_file_path: Optional[str] = None

        # Monitoring agents
        self.monitoring_agents = [
            "qa_agent",
            "error_monitor_agent",
            "context_awareness_agent",
            "project_monitor_agent"
        ]

        # Quality gates (defined per phase)
        self.standard_quality_gates = self._define_quality_gates()

        # Directories
        self.logs_dir = "/Users/reeazmahmud/Desktop/Terminator-Project"
        self.test_dir = "/Users/reeazmahmud/Desktop/Terminator-Project/tests"
        os.makedirs(self.test_dir, exist_ok=True)

    def _define_quality_gates(self) -> List[QualityGate]:
        """Define standard quality gates for each phase"""
        return [
            # Planning Phase Gates
            QualityGate(
                gate_id="gate_requirements",
                name="Requirements Complete",
                description="All requirements documented and understood",
                required_for_phase=SessionPhase.PLANNING,
                checks=[
                    "Requirements listed",
                    "Success criteria defined",
                    "Dependencies identified",
                    "Acceptance criteria clear"
                ]
            ),
            QualityGate(
                gate_id="gate_design",
                name="Design Approved",
                description="Architecture and design reviewed",
                required_for_phase=SessionPhase.PLANNING,
                checks=[
                    "Architecture documented",
                    "Component design complete",
                    "Data structures defined",
                    "Integration points identified"
                ]
            ),

            # Implementation Phase Gates
            QualityGate(
                gate_id="gate_code_complete",
                name="Code Complete",
                description="All code written and reviewed",
                required_for_phase=SessionPhase.IMPLEMENTATION,
                checks=[
                    "All functions implemented",
                    "Error handling added",
                    "Code commented",
                    "No TODOs remaining"
                ],
                assigned_agent="qa_agent"
            ),
            QualityGate(
                gate_id="gate_integration",
                name="Integration Verified",
                description="Code integrates with existing system",
                required_for_phase=SessionPhase.IMPLEMENTATION,
                checks=[
                    "Imports work correctly",
                    "APIs compatible",
                    "No conflicts with existing code",
                    "Dependencies resolved"
                ],
                assigned_agent="context_awareness_agent"
            ),

            # Testing Phase Gates
            QualityGate(
                gate_id="gate_tests_written",
                name="Tests Written",
                description="Test cases created for all features",
                required_for_phase=SessionPhase.TESTING,
                checks=[
                    "Unit tests written",
                    "Integration tests written",
                    "Edge cases covered",
                    "Test data prepared"
                ],
                assigned_agent="qa_agent"
            ),
            QualityGate(
                gate_id="gate_tests_passed",
                name="Tests Passed",
                description="All tests execute successfully",
                required_for_phase=SessionPhase.TESTING,
                checks=[
                    "All tests pass",
                    "No critical failures",
                    "Performance acceptable",
                    "Coverage > 80%"
                ],
                assigned_agent="qa_agent"
            ),

            # Documentation Phase Gates
            QualityGate(
                gate_id="gate_docs_complete",
                name="Documentation Complete",
                description="All documentation written",
                required_for_phase=SessionPhase.DOCUMENTATION,
                checks=[
                    "User guide written",
                    "API docs complete",
                    "Examples provided",
                    "README updated"
                ],
                assigned_agent="project_monitor_agent"
            ),
            QualityGate(
                gate_id="gate_log_file",
                name="Log File Created",
                description="Session log file generated",
                required_for_phase=SessionPhase.DOCUMENTATION,
                checks=[
                    "Log file created",
                    "All changes documented",
                    "Timestamp recorded",
                    "Status updated"
                ],
                assigned_agent="context_awareness_agent"
            ),

            # Quality Check Phase Gates
            QualityGate(
                gate_id="gate_code_review",
                name="Code Review Passed",
                description="Code reviewed for quality",
                required_for_phase=SessionPhase.QUALITY_CHECK,
                checks=[
                    "No security issues",
                    "Best practices followed",
                    "Code style consistent",
                    "Performance optimized"
                ],
                assigned_agent="qa_agent"
            ),
            QualityGate(
                gate_id="gate_errors_resolved",
                name="All Errors Resolved",
                description="No blocking errors remain",
                required_for_phase=SessionPhase.QUALITY_CHECK,
                checks=[
                    "No syntax errors",
                    "No runtime errors",
                    "No logical errors",
                    "All warnings addressed"
                ],
                assigned_agent="error_monitor_agent"
            )
        ]

    def start_session(self, session_name: Optional[str] = None) -> SessionLog:
        """Start a new work session with automatic logging"""

        # Generate session ID
        timestamp = datetime.now()
        session_id = f"session_{timestamp.strftime('%Y%m%d_%H%M%S')}"

        # Create session log
        self.current_session = SessionLog(
            session_id=session_id,
            date=timestamp.strftime("%Y-%m-%d"),
            start_time=timestamp.strftime("%H:%M:%S"),
            project_name=self.project_name,
            developer="Claude Sonnet 4.5",
            current_phase=SessionPhase.INITIALIZATION,
            quality_gates=self.standard_quality_gates.copy()
        )

        # Create log file
        log_filename = f"CLAUDE_ANALYSIS_LOG_{timestamp.strftime('%Y-%m-%d')}.md"
        self.session_file_path = os.path.join(self.logs_dir, log_filename)

        # Add note
        self.add_note(f"Session started: {session_name or 'Work Session'}")

        # Register monitoring agents
        for agent in self.monitoring_agents:
            try:
                self.bus.register_agent(agent)
                self.current_session.agents_assigned.append(agent)
            except Exception as e:
                self.add_note(f"Warning: Could not register {agent}: {e}")

        # Create initial log entry
        self._update_log_file()

        print(f"\n✅ Session started: {session_id}")
        print(f"📄 Log file: {self.session_file_path}")
        print(f"👥 Monitoring agents: {len(self.current_session.agents_assigned)}")
        print(f"🚧 Quality gates: {len(self.current_session.quality_gates)}\n")

        return self.current_session

    def end_session(self):
        """End the current session and finalize documentation"""
        if not self.current_session:
            print("⚠️  No active session")
            return

        self.current_session.end_time = datetime.now().strftime("%H:%M:%S")
        self.current_session.current_phase = SessionPhase.COMPLETION

        # Check if all quality gates passed
        pending_gates = [g for g in self.current_session.quality_gates
                        if g.status == QualityGateStatus.PENDING]
        failed_gates = [g for g in self.current_session.quality_gates
                       if g.status == QualityGateStatus.FAILED]

        if pending_gates or failed_gates:
            print("\n⚠️  WARNING: Session ending with incomplete quality gates:")
            for gate in pending_gates:
                print(f"   ⏸️  PENDING: {gate.name}")
            for gate in failed_gates:
                print(f"   ❌ FAILED: {gate.name}")

        # Generate final documentation
        self._generate_test_summary()
        self._update_log_file()

        print(f"\n✅ Session ended: {self.current_session.session_id}")
        print(f"📄 Log file: {self.session_file_path}")
        print(f"📊 Tasks completed: {len(self.current_session.tasks_completed)}")
        print(f"📁 Files created: {len(self.current_session.files_created)}")

        self.current_session = None

    def advance_phase(self, next_phase: SessionPhase) -> bool:
        """
        Advance to next phase. Blocks if current phase quality gates not passed.
        """
        if not self.current_session:
            print("❌ No active session")
            return False

        # Check quality gates for current phase
        current_phase_gates = [
            g for g in self.current_session.quality_gates
            if g.required_for_phase == self.current_session.current_phase
        ]

        blocking_gates = [
            g for g in current_phase_gates
            if g.status != QualityGateStatus.PASSED
        ]

        if blocking_gates:
            print(f"\n🚫 BLOCKED: Cannot advance to {next_phase.value}")
            print(f"   Current phase: {self.current_session.current_phase.value}")
            print(f"   Blocking gates ({len(blocking_gates)}):")

            for gate in blocking_gates:
                print(f"\n   ⛔ {gate.name}")
                print(f"      Status: {gate.status.value}")
                print(f"      Required checks:")
                for check in gate.checks:
                    status = "✅" if check in gate.failures else "⏸️"
                    print(f"        {status} {check}")
                if gate.failures:
                    print(f"      Failures:")
                    for failure in gate.failures:
                        print(f"        ❌ {failure}")

            print("\n   ⚠️  Fix these issues before advancing!")

            # Create blocker task
            blocker_msg = f"Phase advancement blocked: {blocking_gates[0].name}"
            self.current_session.blockers.append(blocker_msg)

            return False

        # All gates passed - advance
        old_phase = self.current_session.current_phase
        self.current_session.current_phase = next_phase
        self.add_note(f"Advanced from {old_phase.value} to {next_phase.value}")

        print(f"\n✅ Phase advanced: {old_phase.value} → {next_phase.value}")

        return True

    def check_quality_gate(self, gate_id: str, checks_passed: List[str],
                          failures: Optional[List[str]] = None) -> bool:
        """Check a quality gate and update status"""
        if not self.current_session:
            return False

        gate = next((g for g in self.current_session.quality_gates
                    if g.gate_id == gate_id), None)

        if not gate:
            print(f"❌ Quality gate not found: {gate_id}")
            return False

        # Update gate
        gate.checked_at = datetime.now().isoformat()
        gate.failures = failures or []

        # Determine status
        all_checks_passed = all(check in checks_passed for check in gate.checks)
        has_failures = len(gate.failures) > 0

        if all_checks_passed and not has_failures:
            gate.status = QualityGateStatus.PASSED
            print(f"✅ Quality gate PASSED: {gate.name}")
            return True
        else:
            gate.status = QualityGateStatus.FAILED
            print(f"❌ Quality gate FAILED: {gate.name}")
            if gate.failures:
                for failure in gate.failures:
                    print(f"   • {failure}")
            return False

    def record_file_created(self, file_path: str):
        """Record a file creation"""
        if self.current_session:
            self.current_session.files_created.append(file_path)
            self.add_note(f"Created file: {file_path}")

    def record_file_modified(self, file_path: str):
        """Record a file modification"""
        if self.current_session:
            if file_path not in self.current_session.files_modified:
                self.current_session.files_modified.append(file_path)
            self.add_note(f"Modified file: {file_path}")

    def record_task_completed(self, task_name: str):
        """Record task completion"""
        if self.current_session:
            self.current_session.tasks_completed.append(task_name)
            self.add_note(f"Completed task: {task_name}")

    def add_test_case(self, test_case: TestCase):
        """Add a test case to the session"""
        if self.current_session:
            self.current_session.test_cases.append(test_case)
            self.add_note(f"Added test case: {test_case.name}")

    def add_note(self, note: str):
        """Add a note to the session log"""
        if self.current_session:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.current_session.notes.append(f"[{timestamp}] {note}")

    def add_blocker(self, blocker: str):
        """Add a blocker that prevents progression"""
        if self.current_session:
            self.current_session.blockers.append(blocker)
            print(f"🚫 BLOCKER: {blocker}")

    def generate_test_cases(self, feature_name: str,
                           test_scenarios: List[str]) -> List[TestCase]:
        """Auto-generate test cases for a feature"""
        test_cases = []

        for i, scenario in enumerate(test_scenarios, 1):
            test_case = TestCase(
                test_id=f"test_{feature_name}_{i}",
                name=f"{feature_name} - {scenario}",
                description=f"Test {scenario.lower()} for {feature_name}",
                category="integration",
                steps=[
                    "Setup test environment",
                    f"Execute {scenario}",
                    "Verify results",
                    "Cleanup"
                ],
                expected_result=f"{scenario} should work correctly",
                assigned_agent="qa_agent"
            )
            test_cases.append(test_case)
            self.add_test_case(test_case)

        print(f"✅ Generated {len(test_cases)} test cases for {feature_name}")
        return test_cases

    def _update_log_file(self):
        """Update the session log file"""
        if not self.current_session or not self.session_file_path:
            return

        content = self._generate_log_content()

        with open(self.session_file_path, 'w') as f:
            f.write(content)

    def _generate_log_content(self) -> str:
        """Generate markdown content for log file"""
        session = self.current_session

        lines = [
            "# 🔍 CLAUDE DEVELOPMENT LOG",
            f"## {session.project_name} - Session {session.session_id}",
            "",
            f"**Developer:** {session.developer}",
            f"**Date:** {session.date}",
            f"**Start Time:** {session.start_time}",
            f"**End Time:** {session.end_time or 'In Progress'}",
            f"**Current Phase:** {session.current_phase.value}",
            "",
            "---",
            "",
            "## 📊 SESSION SUMMARY",
            "",
            f"**Tasks Completed:** {len(session.tasks_completed)}",
            f"**Files Created:** {len(session.files_created)}",
            f"**Files Modified:** {len(session.files_modified)}",
            f"**Test Cases:** {len(session.test_cases)}",
            f"**Quality Gates Passed:** {sum(1 for g in session.quality_gates if g.status == QualityGateStatus.PASSED)}/{len(session.quality_gates)}",
            "",
            "---",
            "",
            "## ✅ TASKS COMPLETED",
            ""
        ]

        if session.tasks_completed:
            for task in session.tasks_completed:
                lines.append(f"- {task}")
        else:
            lines.append("- No tasks completed yet")

        lines.extend([
            "",
            "---",
            "",
            "## 📁 FILES CREATED",
            ""
        ])

        if session.files_created:
            for file_path in session.files_created:
                lines.append(f"- `{file_path}`")
        else:
            lines.append("- No files created yet")

        lines.extend([
            "",
            "---",
            "",
            "## 🚧 QUALITY GATES",
            ""
        ])

        for gate in session.quality_gates:
            status_icon = {
                QualityGateStatus.PASSED: "✅",
                QualityGateStatus.FAILED: "❌",
                QualityGateStatus.PENDING: "⏸️",
                QualityGateStatus.BLOCKED: "🚫"
            }[gate.status]

            lines.append(f"### {status_icon} {gate.name}")
            lines.append(f"**Phase:** {gate.required_for_phase.value}")
            lines.append(f"**Status:** {gate.status.value}")
            if gate.assigned_agent:
                lines.append(f"**Assigned Agent:** {gate.assigned_agent}")
            lines.append("")
            lines.append("**Required Checks:**")
            for check in gate.checks:
                lines.append(f"- {check}")
            if gate.failures:
                lines.append("")
                lines.append("**Failures:**")
                for failure in gate.failures:
                    lines.append(f"- ❌ {failure}")
            lines.append("")

        if session.blockers:
            lines.extend([
                "---",
                "",
                "## 🚫 BLOCKERS",
                ""
            ])
            for blocker in session.blockers:
                lines.append(f"- {blocker}")
            lines.append("")

        lines.extend([
            "---",
            "",
            "## 📝 SESSION NOTES",
            ""
        ])

        for note in session.notes[-20:]:  # Last 20 notes
            lines.append(f"- {note}")

        lines.extend([
            "",
            "---",
            "",
            "**End of Log**",
            ""
        ])

        return "\n".join(lines)

    def _generate_test_summary(self):
        """Generate test suite summary"""
        if not self.current_session or not self.current_session.test_cases:
            return

        summary_path = os.path.join(
            self.test_dir,
            f"TEST_SUITE_SUMMARY_{self.current_session.date}.md"
        )

        lines = [
            "# 🧪 TEST SUITE SUMMARY",
            f"## {self.current_session.project_name}",
            "",
            f"**Date:** {self.current_session.date}",
            f"**Session:** {self.current_session.session_id}",
            "",
            "---",
            "",
            "## 📊 TEST STATISTICS",
            "",
            f"**Total Tests:** {len(self.current_session.test_cases)}",
            f"**Passed:** {sum(1 for t in self.current_session.test_cases if t.status == 'passed')}",
            f"**Failed:** {sum(1 for t in self.current_session.test_cases if t.status == 'failed')}",
            f"**Pending:** {sum(1 for t in self.current_session.test_cases if t.status == 'pending')}",
            "",
            "---",
            "",
            "## 🧪 TEST CASES",
            ""
        ]

        for test in self.current_session.test_cases:
            status_icon = {
                "passed": "✅",
                "failed": "❌",
                "pending": "⏸️",
                "skipped": "⏭️"
            }.get(test.status, "❓")

            lines.append(f"### {status_icon} {test.name}")
            lines.append(f"**ID:** {test.test_id}")
            lines.append(f"**Category:** {test.category}")
            lines.append(f"**Status:** {test.status}")
            if test.assigned_agent:
                lines.append(f"**Assigned:** {test.assigned_agent}")
            lines.append("")
            lines.append("**Steps:**")
            for step in test.steps:
                lines.append(f"1. {step}")
            lines.append("")
            lines.append(f"**Expected:** {test.expected_result}")
            if test.actual_result:
                lines.append(f"**Actual:** {test.actual_result}")
            lines.append("")

        with open(summary_path, 'w') as f:
            f.write("\n".join(lines))

        print(f"📄 Test summary created: {summary_path}")


# ============================================================================
# Module Functions
# ============================================================================

_session_manager_instance = None

def get_session_manager() -> SessionManager:
    """Get or create session manager instance"""
    global _session_manager_instance
    if _session_manager_instance is None:
        _session_manager_instance = SessionManager()
    return _session_manager_instance


if __name__ == "__main__":
    print("\n=== Session Manager Test ===\n")

    # Create session manager
    mgr = get_session_manager()

    # Start session
    session = mgr.start_session("Test Multi-Agent System")

    # Simulate work
    mgr.add_note("Starting implementation phase")
    mgr.record_file_created("core/test_module.py")
    mgr.record_task_completed("Implement core functionality")

    # Generate test cases
    test_scenarios = [
        "Normal operation",
        "Error handling",
        "Edge cases",
        "Performance under load"
    ]
    mgr.generate_test_cases("CoreModule", test_scenarios)

    # Check quality gate
    mgr.check_quality_gate(
        "gate_code_complete",
        checks_passed=["All functions implemented", "Error handling added"],
        failures=["Code not fully commented"]
    )

    # Try to advance (should be blocked)
    success = mgr.advance_phase(SessionPhase.TESTING)

    # Fix the blocker
    mgr.add_note("Added missing comments")
    mgr.check_quality_gate(
        "gate_code_complete",
        checks_passed=["All functions implemented", "Error handling added",
                      "Code commented", "No TODOs remaining"],
        failures=[]
    )

    # Try again
    success = mgr.advance_phase(SessionPhase.TESTING)

    # End session
    mgr.end_session()

    print("\n=== Test Complete ===\n")
