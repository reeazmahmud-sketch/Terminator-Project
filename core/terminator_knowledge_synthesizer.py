# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Knowledge Synthesizer - Insight Integration and Synthesis
==============================================================

Combines insights from multiple sources, resolves conflicts,
and generates high-level recommendations.

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


@dataclass
class SynthesizedInsight:
    insight_id: str
    topic: str
    sources: List[str] = field(default_factory=list)
    key_findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    confidence: float = 0.8
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class TerminatorKnowledgeSynthesizer:
    _instance: Optional['TerminatorKnowledgeSynthesizer'] = None
    _lock = threading.Lock()

    def __init__(self):
        self.bus = get_communication_bus()
        self.agent_name = "KnowledgeSynthesizer"
        self.insights: Dict[str, SynthesizedInsight] = {}
        self.bus.register_agent(self.agent_name, self)

    @classmethod
    def get_instance(cls) -> 'TerminatorKnowledgeSynthesizer':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def synthesize_insights(
        self,
        topic: str,
        inputs: Dict[str, Any]
    ) -> SynthesizedInsight:
        """Synthesize insights from multiple sources"""
        insight_id = str(uuid4())[:8]
        insight = SynthesizedInsight(
            insight_id=insight_id,
            topic=topic,
            sources=list(inputs.keys())
        )

        # Extract key findings
        findings = self._extract_findings(inputs)
        insight.key_findings = findings

        # Generate recommendations
        recommendations = self._generate_recommendations(topic, findings)
        insight.recommendations = recommendations

        # Calculate confidence
        insight.confidence = self._calculate_confidence(findings)

        self.insights[insight_id] = insight

        # Broadcast synthesized insight
        self.bus.broadcast_message(
            sender_agent=self.agent_name,
            message_type=MessageType.NOTIFICATION,
            subject="Insight Synthesized",
            content={
                "insight_id": insight_id,
                "topic": topic,
                "confidence": insight.confidence
            },
            priority=MessagePriority.NORMAL
        )

        return insight

    def _extract_findings(self, inputs: Dict[str, Any]) -> List[str]:
        """Extract key findings from inputs"""
        findings = []

        for source, data in inputs.items():
            if isinstance(data, dict):
                # Extract main points
                if "key_point" in data:
                    findings.append(f"From {source}: {data['key_point']}")
                elif "finding" in data:
                    findings.append(f"From {source}: {data['finding']}")

        return findings

    def _generate_recommendations(self, topic: str, findings: List[str]) -> List[str]:
        """Generate recommendations based on findings"""
        recommendations = []

        # Topic-specific recommendations
        if "performance" in topic.lower():
            recommendations.append("Monitor performance metrics continuously")
            recommendations.append("Optimize identified bottlenecks")
        elif "quality" in topic.lower():
            recommendations.append("Implement quality assurance checks")
            recommendations.append("Review and improve processes")
        elif "risk" in topic.lower():
            recommendations.append("Implement mitigation strategies")
            recommendations.append("Monitor for changes")

        return recommendations

    def _calculate_confidence(self, findings: List[str]) -> float:
        """Calculate confidence in synthesis"""
        # More findings = higher confidence
        if not findings:
            return 0.5
        if len(findings) >= 5:
            return 0.9
        if len(findings) >= 3:
            return 0.8
        return 0.6

    def get_insight(self, insight_id: str) -> Optional[SynthesizedInsight]:
        """Get a synthesized insight"""
        return self.insights.get(insight_id)

    def get_insights_by_topic(self, topic: str) -> List[SynthesizedInsight]:
        """Get insights for a topic"""
        return [i for i in self.insights.values() if i.topic == topic]


def get_knowledge_synthesizer() -> TerminatorKnowledgeSynthesizer:
    """Get the knowledge synthesizer instance"""
    return TerminatorKnowledgeSynthesizer.get_instance()
