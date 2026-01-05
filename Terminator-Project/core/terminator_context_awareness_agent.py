# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Context Awareness Agent - Deep Situational Understanding
===============================================================

Analyzes context to understand emotional state, urgency, resource availability,
and other situational factors that inform better decision-making.

Features:
- Emotional state detection from language patterns
- Task urgency assessment
- Resource availability checking
- Risk assessment and mitigation
- Clarifying question generation
- Contextual recommendations

Created: December 11, 2025
Part of: TERMINATOR Enhancement Roadmap - Tier 2 (Intelligence)
"""

import json
import os
import re
import threading
import time
from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum


# ============================================================================
# Data Structures
# ============================================================================

class EmotionalState(Enum):
    """User's emotional state"""
    FRUSTRATED = "frustrated"
    CALM = "calm"
    URGENT = "urgent"
    CURIOUS = "curious"
    CONFIDENT = "confident"
    UNCERTAIN = "uncertain"


class UrgencyLevel(Enum):
    """Task urgency level"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class RiskLevel(Enum):
    """Risk assessment level"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ContextSnapshot:
    """Current context snapshot"""
    emotional_state: EmotionalState
    urgency: UrgencyLevel
    resource_availability: float  # 0.0-1.0
    risk_level: RiskLevel
    confidence_needed: float  # 0.0-1.0
    available_time_ms: Optional[int] = None
    user_expertise: str = "intermediate"  # beginner, intermediate, expert
    task_type: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['emotional_state'] = self.emotional_state.value
        data['urgency'] = self.urgency.value
        data['risk_level'] = self.risk_level.value
        return data


@dataclass
class ClarifyingQuestion:
    """A clarifying question to ask the user"""
    question: str
    priority: int  # 1-5
    field_to_clarify: str
    response_type: str  # "text", "choice", "number", etc.
    choices: Optional[List[str]] = None


# ============================================================================
# Emotional State Detector
# ============================================================================

class EmotionalStateDetector:
    """Detects emotional state from user language"""

    # Patterns for detecting emotional states
    FRUSTRATED_PATTERNS = [
        r"frustrated", r"annoyed", r"angry", r"mad", r"not working",
        r"broken", r"fail", r"doesn't work", r"problem", r"issue",
        r"terrible", r"awful", r"horrible", r"can't get"
    ]

    URGENT_PATTERNS = [
        r"urgent", r"asap", r"rush", r"immediately", r"quick",
        r"deadline", r"time-sensitive", r"must", r"critical",
        r"now", r"hurry", r"quick", r"fast"
    ]

    CURIOUS_PATTERNS = [
        r"why", r"how does", r"explain", r"curious",
        r"wonder", r"interested", r"learn", r"understand"
    ]

    CONFIDENT_PATTERNS = [
        r"sure", r"confident", r"know", r"experienced",
        r"familiar", r"expert", r"professional"
    ]

    UNCERTAIN_PATTERNS = [
        r"not sure", r"uncertain", r"maybe", r"perhaps",
        r"think", r"guess", r"unsure", r"confused"
    ]

    def detect_emotion(self, text: str) -> Tuple[EmotionalState, float]:
        """
        Detect emotional state from text

        Returns:
            Tuple of (EmotionalState, confidence 0.0-1.0)
        """
        text_lower = text.lower()
        scores = {
            EmotionalState.FRUSTRATED: self._score_patterns(text_lower, self.FRUSTRATED_PATTERNS),
            EmotionalState.URGENT: self._score_patterns(text_lower, self.URGENT_PATTERNS),
            EmotionalState.CURIOUS: self._score_patterns(text_lower, self.CURIOUS_PATTERNS),
            EmotionalState.CONFIDENT: self._score_patterns(text_lower, self.CONFIDENT_PATTERNS),
            EmotionalState.UNCERTAIN: self._score_patterns(text_lower, self.UNCERTAIN_PATTERNS),
        }

        # Find highest score
        max_state = max(scores, key=scores.get)
        max_score = scores[max_state]

        # Default to calm if no strong emotion detected
        if max_score < 0.3:
            return EmotionalState.CALM, 0.5

        return max_state, min(max_score, 1.0)

    @staticmethod
    def _score_patterns(text: str, patterns: List[str]) -> float:
        """Score how well text matches patterns"""
        matches = sum(1 for pattern in patterns if re.search(pattern, text))
        return min(matches / max(len(patterns), 1) * 2, 1.0)


# ============================================================================
# Urgency Assessor
# ============================================================================

class UrgencyAssessor:
    """Assesses task urgency from language and context"""

    def assess_urgency(
        self,
        text: str,
        available_time: Optional[int] = None,
        deadline: Optional[str] = None
    ) -> UrgencyLevel:
        """
        Assess urgency level

        Args:
            text: User input text
            available_time: Time available in milliseconds
            deadline: Deadline timestamp

        Returns:
            UrgencyLevel
        """
        text_lower = text.lower()
        urgency_score = 0

        # Check text patterns
        urgent_keywords = ["asap", "urgent", "rush", "now", "immediately", "critical", "deadline"]
        urgent_count = sum(1 for kw in urgent_keywords if kw in text_lower)
        urgency_score += urgent_count * 2

        # Check available time
        if available_time is not None:
            if available_time < 1000:  # Less than 1 second
                urgency_score += 3
            elif available_time < 5000:  # Less than 5 seconds
                urgency_score += 2
            elif available_time > 300000:  # More than 5 minutes
                urgency_score -= 1

        # Check deadline
        if deadline:
            import datetime as dt
            try:
                deadline_time = dt.datetime.fromisoformat(deadline)
                time_until = (deadline_time - dt.datetime.now()).total_seconds()

                if time_until < 3600:  # Less than 1 hour
                    urgency_score += 3
                elif time_until < 86400:  # Less than 1 day
                    urgency_score += 1
            except:
                pass

        # Convert to urgency level
        if urgency_score >= 6:
            return UrgencyLevel.CRITICAL
        elif urgency_score >= 4:
            return UrgencyLevel.HIGH
        elif urgency_score >= 2:
            return UrgencyLevel.NORMAL
        else:
            return UrgencyLevel.LOW


# ============================================================================
# Resource Checker
# ============================================================================

class ResourceChecker:
    """Checks resource availability"""

    def __init__(self):
        """Initialize resource checker"""
        self.last_check = {}

    def check_resources(self) -> float:
        """
        Check system resource availability

        Returns:
            Availability score 0.0-1.0 (1.0 = fully available)
        """
        try:
            import psutil
            # Check CPU, memory, disk
            cpu_percent = psutil.cpu_percent(interval=0.1) / 100.0
            memory_percent = psutil.virtual_memory().percent / 100.0
            disk_percent = psutil.disk_usage('/').percent / 100.0

            # Average availability (invert percentages)
            availability = 1.0 - (cpu_percent + memory_percent + disk_percent) / 3
            return max(0.0, min(1.0, availability))
        except:
            # If psutil not available, assume good resources
            return 0.8

    def get_resource_details(self) -> Dict[str, Any]:
        """Get detailed resource information"""
        try:
            import psutil
            return {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "memory_available_mb": psutil.virtual_memory().available / 1024 / 1024,
                "disk_percent": psutil.disk_usage('/').percent,
                "process_count": len(psutil.pids())
            }
        except:
            return {"status": "unavailable"}


# ============================================================================
# Risk Assessor
# ============================================================================

class RiskAssessor:
    """Assesses risks in tasks"""

    RISK_KEYWORDS = {
        "delete": 3,
        "drop": 3,
        "remove": 2,
        "modify": 2,
        "change": 1,
        "reset": 3,
        "clear": 2,
        "erase": 3,
        "permanent": 3,
        "irreversible": 3,
        "critical": 2,
        "production": 2,
        "live": 2
    }

    def assess_risk(self, task_description: str, task_type: str = None) -> RiskLevel:
        """
        Assess risk level of a task

        Args:
            task_description: Description of the task
            task_type: Type of task being performed

        Returns:
            RiskLevel
        """
        risk_score = 0
        text_lower = task_description.lower()

        # Check keywords
        for keyword, weight in self.RISK_KEYWORDS.items():
            if keyword in text_lower:
                risk_score += weight

        # Check task type
        if task_type:
            if task_type in ["file_deletion", "database_modification", "system_configuration"]:
                risk_score += 2

        # Convert to risk level
        if risk_score >= 7:
            return RiskLevel.CRITICAL
        elif risk_score >= 5:
            return RiskLevel.HIGH
        elif risk_score >= 2:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def get_risk_mitigation(self, risk_level: RiskLevel) -> List[str]:
        """Get mitigation strategies for risk level"""
        mitigation_map = {
            RiskLevel.LOW: [
                "Proceed with task"
            ],
            RiskLevel.MEDIUM: [
                "Review task carefully",
                "Create backup if applicable",
                "Proceed with caution"
            ],
            RiskLevel.HIGH: [
                "Request user confirmation",
                "Create backup first",
                "Have rollback plan ready",
                "Log all actions"
            ],
            RiskLevel.CRITICAL: [
                "STOP - Request explicit user confirmation",
                "Create full backup",
                "Have detailed rollback plan",
                "Consider expert review",
                "Log all actions with audit trail"
            ]
        }
        return mitigation_map.get(risk_level, [])


# ============================================================================
# Context Analyzer
# ============================================================================

class ContextAnalyzer:
    """Main context analysis engine"""

    def __init__(self):
        """Initialize context analyzer"""
        self.emotion_detector = EmotionalStateDetector()
        self.urgency_assessor = UrgencyAssessor()
        self.resource_checker = ResourceChecker()
        self.risk_assessor = RiskAssessor()
        self.storage_path = "/Users/reeazmahmud/Desktop/Terminator/context/data"
        os.makedirs(self.storage_path, exist_ok=True)

    def analyze_context(
        self,
        user_input: str,
        task_type: Optional[str] = None,
        available_time: Optional[int] = None,
        deadline: Optional[str] = None
    ) -> ContextSnapshot:
        """
        Analyze full context from user input and system state

        Args:
            user_input: User's input text
            task_type: Type of task
            available_time: Time available in milliseconds
            deadline: Deadline timestamp

        Returns:
            ContextSnapshot with all analysis
        """
        # Detect emotional state
        emotional_state, emotion_confidence = self.emotion_detector.detect_emotion(user_input)

        # Assess urgency
        urgency = self.urgency_assessor.assess_urgency(user_input, available_time, deadline)

        # Check resources
        resource_availability = self.resource_checker.check_resources()

        # Assess risk
        risk_level = self.risk_assessor.assess_risk(user_input, task_type)

        # Determine confidence needed (inverse of user certainty)
        confidence_needed = 1.0 if emotional_state == EmotionalState.UNCERTAIN else 0.5

        snapshot = ContextSnapshot(
            emotional_state=emotional_state,
            urgency=urgency,
            resource_availability=resource_availability,
            risk_level=risk_level,
            confidence_needed=confidence_needed,
            available_time_ms=available_time,
            task_type=task_type,
            metadata={
                "emotion_confidence": emotion_confidence,
                "resource_details": self.resource_checker.get_resource_details()
            }
        )

        return snapshot

    def get_context_summary(self, snapshot: ContextSnapshot) -> str:
        """Get human-readable context summary"""
        return f"""
╔═══════════════════════════════════════════╗
║         CONTEXT ANALYSIS SUMMARY          ║
╠═══════════════════════════════════════════╣
║ Emotional State:    {snapshot.emotional_state.value:>20}
║ Urgency Level:      {snapshot.urgency.name:>20}
║ Risk Level:         {snapshot.risk_level.name:>20}
║ Resource Avail:     {snapshot.resource_availability:>20.0%}
║ Confidence Needed:  {snapshot.confidence_needed:>20.0%}
╚═══════════════════════════════════════════╝
"""

    def should_ask_clarification(self, snapshot: ContextSnapshot) -> bool:
        """Determine if clarification is needed"""
        # Need clarification if uncertain, urgent, or high risk
        return (
            snapshot.emotional_state == EmotionalState.UNCERTAIN or
            snapshot.urgency == UrgencyLevel.CRITICAL or
            snapshot.risk_level == RiskLevel.HIGH
        )

    def generate_clarifying_questions(self, snapshot: ContextSnapshot) -> List[ClarifyingQuestion]:
        """Generate clarifying questions based on context"""
        questions = []

        # If urgent, ask about deadline
        if snapshot.urgency == UrgencyLevel.CRITICAL:
            questions.append(ClarifyingQuestion(
                question="What's the exact deadline for this task?",
                priority=5,
                field_to_clarify="deadline",
                response_type="datetime"
            ))

        # If uncertain, ask for more detail
        if snapshot.emotional_state == EmotionalState.UNCERTAIN:
            questions.append(ClarifyingQuestion(
                question="Can you provide more details about what you're trying to accomplish?",
                priority=4,
                field_to_clarify="task_details",
                response_type="text"
            ))

        # If high risk, ask for confirmation
        if snapshot.risk_level == RiskLevel.HIGH:
            questions.append(ClarifyingQuestion(
                question="This task involves risky operations. Do you want me to create a backup first?",
                priority=5,
                field_to_clarify="backup_preference",
                response_type="choice",
                choices=["Yes, create backup", "No, proceed", "Cancel task"]
            ))

        # If frustrated, offer help
        if snapshot.emotional_state == EmotionalState.FRUSTRATED:
            questions.append(ClarifyingQuestion(
                question="It sounds like you're having trouble. Would you like me to explain the process step-by-step?",
                priority=3,
                field_to_clarify="help_preference",
                response_type="choice",
                choices=["Yes, step-by-step", "Just fix it", "Cancel"]
            ))

        return questions


# ============================================================================
# Main Context Awareness Agent
# ============================================================================

class TerminatorContextAwarenessAgent:
    """
    Main context awareness agent that understands situational factors
    to inform better decision-making.
    """

    _instance: Optional['TerminatorContextAwarenessAgent'] = None
    _lock = threading.Lock()

    def __init__(self):
        """Initialize context awareness agent"""
        self.analyzer = ContextAnalyzer()
        self.context_history: List[ContextSnapshot] = []

    @classmethod
    def get_instance(cls) -> 'TerminatorContextAwarenessAgent':
        """Get singleton instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def analyze(
        self,
        user_input: str,
        task_type: Optional[str] = None,
        available_time: Optional[int] = None,
        deadline: Optional[str] = None
    ) -> ContextSnapshot:
        """Analyze current context"""
        snapshot = self.analyzer.analyze_context(user_input, task_type, available_time, deadline)
        self.context_history.append(snapshot)

        # Keep last 100 contexts
        if len(self.context_history) > 100:
            self.context_history = self.context_history[-100:]

        return snapshot

    def should_ask_clarification(self, snapshot: ContextSnapshot) -> bool:
        """Check if clarification is needed"""
        return self.analyzer.should_ask_clarification(snapshot)

    def get_clarifying_questions(self, snapshot: ContextSnapshot) -> List[ClarifyingQuestion]:
        """Get clarifying questions"""
        return self.analyzer.generate_clarifying_questions(snapshot)

    def get_risk_mitigation(self, snapshot: ContextSnapshot) -> List[str]:
        """Get risk mitigation strategies"""
        return self.analyzer.risk_assessor.get_risk_mitigation(snapshot.risk_level)

    def get_context_summary(self, snapshot: ContextSnapshot) -> str:
        """Get context summary"""
        return self.analyzer.get_context_summary(snapshot)

    def get_context_history(self, hours: int = 24) -> List[ContextSnapshot]:
        """Get context history from last N hours"""
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(hours=hours)
        return [
            c for c in self.context_history
            if datetime.fromisoformat(c.timestamp) > cutoff
        ]


# ============================================================================
# Module-level access functions
# ============================================================================

def get_context_agent() -> TerminatorContextAwarenessAgent:
    """Get the context awareness agent instance"""
    return TerminatorContextAwarenessAgent.get_instance()


def analyze_context(
    user_input: str,
    task_type: Optional[str] = None,
    available_time: Optional[int] = None,
    deadline: Optional[str] = None
) -> ContextSnapshot:
    """Convenience function to analyze context"""
    agent = get_context_agent()
    return agent.analyze(user_input, task_type, available_time, deadline)


if __name__ == "__main__":
    # Test the context awareness agent
    agent = get_context_agent()

    # Test scenarios
    test_cases = [
        ("I'm frustrated with this broken search feature", None, 5000, None),
        ("URGENT: I need this analysis done ASAP, deadline is in 2 hours", "analysis", 120000, None),
        ("How does this work? I'm curious to understand the mechanism", "learning", 600000, None),
        ("Can you delete all the old files? The directory is too cluttered", "file_management", 10000, None),
    ]

    for user_input, task_type, time_available, deadline in test_cases:
        print(f"\n{'='*60}")
        print(f"Input: {user_input}")

        snapshot = agent.analyze(user_input, task_type, time_available, deadline)
        print(agent.get_context_summary(snapshot))

        if agent.should_ask_clarification(snapshot):
            print("\n❓ Clarifying Questions:")
            for q in agent.get_clarifying_questions(snapshot):
                print(f"  - {q.question} (Priority: {q.priority})")

        if snapshot.risk_level != RiskLevel.LOW:
            print("\n⚠️ Risk Mitigation:")
            for action in agent.get_risk_mitigation(snapshot):
                print(f"  - {action}")
