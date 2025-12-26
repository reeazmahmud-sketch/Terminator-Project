# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Risk Assessment Agent - Risk Detection and Mitigation
===========================================================

Identifies risks, assesses severity, suggests mitigations,
and monitors for emerging issues.

Created: December 11, 2025
Part of: TERMINATOR Enhancement Roadmap - Tier 5 (Collaboration)
"""

import threading
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4

from core.terminator_agent_communication_bus import get_communication_bus, MessageType, MessagePriority


class RiskLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class RiskAssessment:
    assessment_id: str
    task_id: str
    risks_identified: List[Dict[str, Any]] = field(default_factory=list)
    overall_risk_level: RiskLevel = RiskLevel.LOW
    mitigation_strategies: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class TerminatorRiskAssessmentAgent:
    _instance: Optional['TerminatorRiskAssessmentAgent'] = None
    _lock = threading.Lock()

    def __init__(self):
        self.bus = get_communication_bus()
        self.agent_name = "RiskAssessment"
        self.assessments: Dict[str, RiskAssessment] = {}
        self.bus.register_agent(self.agent_name, self)

    @classmethod
    def get_instance(cls) -> 'TerminatorRiskAssessmentAgent':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def assess_task_risk(
        self,
        task_id: str,
        task_type: str,
        task_data: Dict[str, Any]
    ) -> RiskAssessment:
        """Assess risks for a task"""
        assessment_id = str(uuid4())[:8]
        assessment = RiskAssessment(
            assessment_id=assessment_id,
            task_id=task_id
        )

        # Identify risks
        risks = self._identify_risks(task_type, task_data)
        assessment.risks_identified = risks

        # Calculate overall risk level
        if not risks:
            assessment.overall_risk_level = RiskLevel.LOW
        else:
            max_severity = max(r.get("severity", 1) for r in risks)
            if max_severity >= 4:
                assessment.overall_risk_level = RiskLevel.CRITICAL
            elif max_severity >= 3:
                assessment.overall_risk_level = RiskLevel.HIGH
            elif max_severity >= 2:
                assessment.overall_risk_level = RiskLevel.MEDIUM
            else:
                assessment.overall_risk_level = RiskLevel.LOW

        # Generate mitigation strategies
        assessment.mitigation_strategies = self._generate_mitigations(risks)

        self.assessments[assessment_id] = assessment

        # Notify if high risk
        if assessment.overall_risk_level.value >= 3:
            self.bus.send_message(
                sender_agent=self.agent_name,
                recipient_agent=None,
                message_type=MessageType.NOTIFICATION,
                subject="High Risk Detected",
                content={"task_id": task_id, "risk_level": assessment.overall_risk_level.name},
                priority=MessagePriority.HIGH
            )

        return assessment

    def _identify_risks(self, task_type: str, task_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify potential risks"""
        risks = []

        # Task-specific risks
        if "delete" in task_type.lower() or "remove" in task_type.lower():
            risks.append({"risk": "Data loss risk", "severity": 4, "type": "data_loss"})

        if "modify" in task_type.lower():
            risks.append({"risk": "Unintended modification", "severity": 3, "type": "modification"})

        if task_data.get("critical", False):
            risks.append({"risk": "Critical system impact", "severity": 4, "type": "critical"})

        # Time-based risks
        estimated_time = task_data.get("estimated_duration_hours", 0)
        if estimated_time > 8:
            risks.append({"risk": "Long execution time", "severity": 2, "type": "timing"})

        return risks

    def _generate_mitigations(self, risks: List[Dict[str, Any]]) -> List[str]:
        """Generate mitigation strategies"""
        mitigations = []

        for risk in risks:
            risk_type = risk.get("type", "")

            if risk_type == "data_loss":
                mitigations.append("Create backup before operation")
                mitigations.append("Implement rollback capability")
            elif risk_type == "modification":
                mitigations.append("Review changes before committing")
                mitigations.append("Test in staging environment")
            elif risk_type == "critical":
                mitigations.append("Get approval before proceeding")
                mitigations.append("Monitor system during execution")
            elif risk_type == "timing":
                mitigations.append("Schedule for low-load period")
                mitigations.append("Implement checkpoints")

        return list(set(mitigations))

    def get_assessment(self, assessment_id: str) -> Optional[RiskAssessment]:
        """Get a risk assessment"""
        return self.assessments.get(assessment_id)


def get_risk_assessor() -> TerminatorRiskAssessmentAgent:
    """Get the risk assessment agent instance"""
    return TerminatorRiskAssessmentAgent.get_instance()
