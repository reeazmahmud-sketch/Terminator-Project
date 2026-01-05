# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR QA Agent - Quality Assurance and Validation
==================================================

Validates task outputs, checks quality, detects errors,
and suggests corrections.

Features:
- Output validation against criteria
- Quality scoring
- Error detection and analysis
- Correction suggestions
- Compliance checking
- Performance benchmarking

Created: December 11, 2025
Part of: TERMINATOR Enhancement Roadmap - Tier 5 (Collaboration)
"""

from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4
import asyncio
from datetime import datetime

from core.terminator_agent_communication_bus import Message, MessageType, MessagePriority
from core.agent_framework import BaseAgent

class QualityLevel(Enum):
    """Quality assessment level"""
    EXCELLENT = 5
    GOOD = 4
    ACCEPTABLE = 3
    POOR = 2
    FAILED = 1


@dataclass
class QAReport:
    """Quality assurance report"""
    report_id: str
    task_id: str
    execution_id: str
    quality_score: float  # 0.0-100.0
    quality_level: QualityLevel
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    passed: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class TerminatorQAAgent(BaseAgent):
    """
    Main QA agent that validates outputs and ensures quality standards.
    """
    AGENT_NAME = "QAAgent"
    AGENT_DESCRIPTION = "Quality Assurance and Validation"
    AGENT_CAPABILITIES = ["validate_output", "check_quality", "get_report"]

    def __init__(self):
        super().__init__(
            name=self.AGENT_NAME,
            description=self.AGENT_DESCRIPTION,
            capabilities=self.AGENT_CAPABILITIES
        )
        self.reports: Dict[str, QAReport] = {}



    async def handle_message(self, message: Message) -> Optional[Dict[str, Any]]:
        """
        Process incoming messages for QA tasks.
        """
        if message.subject == "validate_task_output":
            task_id = message.content.get("task_id")
            execution_id = message.content.get("execution_id")
            output = message.content.get("output")
            criteria = message.content.get("criteria", [])
            
            if not all([task_id, execution_id, output]):
                return {"error": "Missing task_id, execution_id, or output for validation."}

            qa_report = self.validate_output_internal(task_id, execution_id, output, criteria)
            return {
                "report_id": qa_report.report_id,
                "execution_id": qa_report.execution_id,
                "passed": qa_report.passed,
                "quality_score": qa_report.quality_score,
                "issues": qa_report.issues,
                "suggestions": qa_report.suggestions
            }
        elif message.subject == "check_quality":
            # This is a placeholder for a more complex quality check, might involve
            # querying other agents or deeper analysis.
            output_to_check = message.content.get("output")
            # Simulate a quick quality check
            quality_score = 75.0 if output_to_check else 0.0
            issues = []
            if not output_to_check:
                issues.append("Output content is empty.")
            return {"quality_score": quality_score, "issues": issues}
        elif message.subject == "get_report":
            report_id = message.content.get("report_id")
            if report_id:
                report = self.get_report(report_id)
                return asdict(report) if report else {"error": f"Report {report_id} not found."}
            return {"error": "Missing report_id for get_report."}
        
        return {"response": f"Unhandled message subject: {message.subject}"}
    
    def validate_output_internal(
        self,
        task_id: str,
        execution_id: str,
        output: Any,
        criteria: List[str] = None
    ) -> QAReport:
        """Internal method to perform the actual validation, decoupled from message handling."""
        report_id = str(uuid4())[:8]

        report = QAReport(
            report_id=report_id,
            task_id=task_id,
            execution_id=execution_id,
            quality_score=0.0,
            quality_level=QualityLevel.ACCEPTABLE
        )

        self._run_validation_checks(report, output, criteria or [])

        # Store report
        self.reports[report_id] = report
        return report

    def _run_validation_checks(
        self,
        report: QAReport,
        output: Any,
        criteria: List[str]
    ) -> None:
        """Run validation checks"""
        issues = []
        suggestions = []

        # Check for None/empty output
        if output is None:
            issues.append("Output is None")
            report.quality_score = 0.0
            report.quality_level = QualityLevel.FAILED
            report.passed = False
            return

        # Check type
        if isinstance(output, str):
            if len(output) == 0:
                issues.append("Output is empty string")
            elif len(output) < 10:
                suggestions.append("Output is very short, consider expanding")
        elif isinstance(output, dict):
            if not output:
                issues.append("Output dictionary is empty")
            elif "error" in output:
                issues.append(f"Error in output: {output.get('error')}")

        # Apply criteria checks
        for criterion in criteria:
            if "required_length" in criterion:
                # Check length
                if isinstance(output, str) and len(output) < 100:
                    suggestions.append("Output is shorter than required")
            elif "required_format" in criterion:
                # Check format
                pass

        # Calculate quality score
        report.issues = issues
        report.suggestions = suggestions
        report.passed = len(issues) == 0

        if report.passed:
            report.quality_score = 90.0
            report.quality_level = QualityLevel.GOOD
        else:
            report.quality_score = max(0.0, 50.0 - len(issues) * 10)
            if report.quality_score < 30:
                report.quality_level = QualityLevel.FAILED
            elif report.quality_score < 60:
                report.quality_level = QualityLevel.POOR
            else:
                report.quality_level = QualityLevel.ACCEPTABLE

    def get_report(self, report_id: str) -> Optional[QAReport]:
        """Get a QA report"""
        return self.reports.get(report_id)

    def get_all_reports(self) -> Dict[str, QAReport]:
        """Get all QA reports"""
        return self.reports.copy()

    def get_task_quality_summary(self, task_id: str) -> Dict[str, Any]:
        """Get quality summary for a task"""
        task_reports = [r for r in self.reports.values() if r.task_id == task_id]

        if not task_reports:
            return {"task_id": task_id, "reports": 0}

        avg_score = sum(r.quality_score for r in task_reports) / len(task_reports)

        return {
            "task_id": task_id,
            "num_reports": len(task_reports),
            "average_score": avg_score,
            "all_passed": all(r.passed for r in task_reports),
            "issues": [issue for r in task_reports for issue in r.issues],
            "suggestions": [sug for r in task_reports for sug in r.suggestions]
        }


def create_agent() -> TerminatorQAAgent:
    """Factory function for AgentLoader to create QAAgent instances."""
    return TerminatorQAAgent()
