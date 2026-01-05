# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR User Advocate Agent - User Interest Representation
========================================================

Represents user interests in system decisions, ensures preferences
are respected, collects feedback, and monitors satisfaction.

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


class SatisfactionLevel(Enum):
    VERY_SATISFIED = 5
    SATISFIED = 4
    NEUTRAL = 3
    DISSATISFIED = 2
    VERY_DISSATISFIED = 1


@dataclass
class UserFeedback:
    feedback_id: str
    task_id: str
    satisfaction: SatisfactionLevel
    comments: str = ""
    suggestions: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class TerminatorUserAdvocateAgent:
    _instance: Optional['TerminatorUserAdvocateAgent'] = None
    _lock = threading.Lock()

    def __init__(self):
        self.bus = get_communication_bus()
        self.agent_name = "UserAdvocate"
        self.user_preferences: Dict[str, Any] = {}
        self.feedback_history: List[UserFeedback] = []
        self.satisfaction_threshold = 4.0  # Minimum acceptable satisfaction
        self.bus.register_agent(self.agent_name, self)

    @classmethod
    def get_instance(cls) -> 'TerminatorUserAdvocateAgent':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def set_user_preference(self, preference_key: str, value: Any) -> None:
        """Set a user preference"""
        self.user_preferences[preference_key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }

    def record_feedback(
        self,
        task_id: str,
        satisfaction: int,
        comments: str = "",
        suggestions: List[str] = None
    ) -> UserFeedback:
        """Record user feedback"""
        feedback_id = str(uuid4())[:8]
        feedback = UserFeedback(
            feedback_id=feedback_id,
            task_id=task_id,
            satisfaction=SatisfactionLevel(max(1, min(5, satisfaction))),
            comments=comments,
            suggestions=suggestions or []
        )

        self.feedback_history.append(feedback)

        # Check if satisfaction is below threshold
        if feedback.satisfaction.value < self.satisfaction_threshold:
            self.bus.send_message(
                sender_agent=self.agent_name,
                recipient_agent=None,
                message_type=MessageType.NOTIFICATION,
                subject="Low User Satisfaction",
                content={
                    "task_id": task_id,
                    "satisfaction": feedback.satisfaction.value,
                    "comments": comments
                },
                priority=MessagePriority.HIGH
            )

        return feedback

    def advocate_for_user(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """Advocate for user interests in a decision"""
        advocacy = {
            "preferences_to_honor": [],
            "concerns": [],
            "recommendations": []
        }

        # Check user preferences
        for pref_key, pref_data in self.user_preferences.items():
            advocacy["preferences_to_honor"].append(
                f"{pref_key}: {pref_data.get('value')}"
            )

        # Analyze recent satisfaction
        recent_feedback = self.feedback_history[-5:] if self.feedback_history else []
        avg_satisfaction = sum(f.satisfaction.value for f in recent_feedback) / len(recent_feedback) if recent_feedback else 3.0

        if avg_satisfaction < self.satisfaction_threshold:
            advocacy["concerns"].append(
                f"User satisfaction is {avg_satisfaction:.1f}/5, below threshold"
            )

        # Generate recommendations
        if avg_satisfaction < 3:
            advocacy["recommendations"].append("Improve response quality")
            advocacy["recommendations"].append("Respond to user feedback")

        return advocacy

    def get_satisfaction_summary(self) -> Dict[str, Any]:
        """Get satisfaction summary"""
        if not self.feedback_history:
            return {"total_feedback": 0, "average_satisfaction": 0.0}

        total = len(self.feedback_history)
        avg = sum(f.satisfaction.value for f in self.feedback_history) / total

        return {
            "total_feedback": total,
            "average_satisfaction": avg,
            "satisfaction_trend": self._calculate_trend(),
            "feedback_by_level": self._count_by_level()
        }

    def _calculate_trend(self) -> str:
        """Calculate satisfaction trend"""
        if len(self.feedback_history) < 2:
            return "insufficient_data"

        recent = self.feedback_history[-5:]
        older = self.feedback_history[-10:-5] if len(self.feedback_history) >= 10 else []

        if not older:
            return "stable"

        recent_avg = sum(f.satisfaction.value for f in recent) / len(recent)
        older_avg = sum(f.satisfaction.value for f in older) / len(older)

        if recent_avg > older_avg + 0.5:
            return "improving"
        elif recent_avg < older_avg - 0.5:
            return "declining"
        else:
            return "stable"

    def _count_by_level(self) -> Dict[str, int]:
        """Count feedback by satisfaction level"""
        counts = {level.name: 0 for level in SatisfactionLevel}

        for feedback in self.feedback_history:
            counts[feedback.satisfaction.name] += 1

        return counts

    def get_feedback(self, feedback_id: str) -> Optional[UserFeedback]:
        """Get specific feedback"""
        for feedback in self.feedback_history:
            if feedback.feedback_id == feedback_id:
                return feedback
        return None


def get_user_advocate() -> TerminatorUserAdvocateAgent:
    """Get the user advocate agent instance"""
    return TerminatorUserAdvocateAgent.get_instance()
