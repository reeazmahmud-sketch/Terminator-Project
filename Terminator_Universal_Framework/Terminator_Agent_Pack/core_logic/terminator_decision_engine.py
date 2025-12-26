# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Decision Engine - Intelligent Decision Making System
===========================================================

Makes intelligent decisions about model selection, tool usage, response approaches,
and risk handling based on context, analysis, and learned patterns.

Features:
- Model selection optimization
- Tool combination selection
- Response approach determination
- Risk handling strategies
- Decision explanation and justification
- Continuous learning from decision outcomes

Created: December 11, 2025
Part of: TERMINATOR Enhancement Roadmap - Tier 2 (Intelligence)
"""

import json
import os
import threading
from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum


# ============================================================================
# Data Structures
# ============================================================================

class ResponseApproach(Enum):
    """Different response approaches"""
    CONCISE = "concise"
    DETAILED = "detailed"
    STEP_BY_STEP = "step_by_step"
    INTERACTIVE = "interactive"
    CODE_FIRST = "code_first"
    EXPLANATION_FIRST = "explanation_first"


@dataclass
class DecisionOption:
    """A decision option with scoring"""
    option_id: str
    option_name: str
    option_type: str  # "model", "tool", "approach", etc.
    score: float  # 0.0-1.0
    reasoning: str
    risks: List[str] = field(default_factory=list)
    benefits: List[str] = field(default_factory=list)


@dataclass
class Decision:
    """A decision made by the engine"""
    decision_id: str
    decision_type: str  # "model_selection", "tool_choice", "approach", etc.
    selected_option: DecisionOption
    alternatives: List[DecisionOption] = field(default_factory=list)
    confidence: float = 0.8  # 0.0-1.0
    reasoning: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    success: Optional[bool] = None  # Set after outcome known
    context_factors: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Model Decision Maker
# ============================================================================

class ModelSelector:
    """Selects best model for task"""

    # Model characteristics (you can customize based on your models)
    MODEL_PROFILES = {
        "claude-3-haiku": {
            "speed": 0.95,
            "cost": 0.95,
            "quality": 0.75,
            "best_for": ["quick_analysis", "simple_tasks", "drafting"],
            "reasoning_time": 0.2
        },
        "claude-3-sonnet": {
            "speed": 0.7,
            "cost": 0.6,
            "quality": 0.85,
            "best_for": ["general_tasks", "analysis", "coding"],
            "reasoning_time": 0.5
        },
        "claude-3-opus": {
            "speed": 0.4,
            "cost": 0.3,
            "quality": 0.95,
            "best_for": ["complex_tasks", "deep_analysis", "difficult_problems"],
            "reasoning_time": 1.0
        }
    }

    def select_model(
        self,
        task_type: str,
        available_time_ms: Optional[int],
        complexity: float,  # 0.0-1.0
        cost_sensitive: bool = False
    ) -> Tuple[str, float, str]:
        """
        Select best model for task

        Returns:
            Tuple of (model_name, confidence, reasoning)
        """
        scores = {}

        for model_name, profile in self.MODEL_PROFILES.items():
            score = self._score_model(
                model_name,
                profile,
                task_type,
                available_time_ms,
                complexity,
                cost_sensitive
            )
            scores[model_name] = score

        # Find best model
        best_model = max(scores, key=scores.get)
        best_score = scores[best_model]

        reasoning = self._explain_model_choice(best_model, best_score, task_type)

        return best_model, best_score, reasoning

    def _score_model(
        self,
        model_name: str,
        profile: Dict[str, Any],
        task_type: str,
        available_time_ms: Optional[int],
        complexity: float,
        cost_sensitive: bool
    ) -> float:
        """Score a model for the task"""
        score = 0.5  # Base score

        # Quality score based on complexity
        quality_needed = 0.5 + (complexity * 0.5)
        score += abs(profile["quality"] - quality_needed) * -0.2 + 0.2

        # Speed score based on available time
        if available_time_ms:
            speed_needed = 1.0 if available_time_ms < 5000 else 0.0
            if available_time_ms < 1000:
                speed_needed = 1.0
            score += (profile["speed"] if available_time_ms < 5000 else 0) * 0.2

        # Cost consideration
        if cost_sensitive:
            score += (1.0 - profile["cost"]) * 0.15

        # Task suitability
        if any(best in task_type.lower() for best in profile.get("best_for", [])):
            score += 0.2

        return min(score, 1.0)

    def _explain_model_choice(self, model: str, score: float, task_type: str) -> str:
        """Explain why model was chosen"""
        profile = self.MODEL_PROFILES.get(model, {})

        reasons = []
        reasons.append(f"{model} is well-suited for {task_type}")

        if profile.get("quality", 0) > 0.85:
            reasons.append("High quality output expected")

        if profile.get("speed", 0) > 0.7:
            reasons.append("Fast response time")

        return " - ".join(reasons)


# ============================================================================
# Tool Decision Maker
# ============================================================================

class ToolSelector:
    """Selects best tools for task"""

    # Tool profiles
    TOOL_PROFILES = {
        "web_search": {
            "reliability": 0.85,
            "speed": 0.9,
            "cost": 0.6,
            "good_for": ["research", "current_info", "verification"],
            "limitation": "Needs internet, may return irrelevant results"
        },
        "file_search": {
            "reliability": 0.95,
            "speed": 0.8,
            "cost": 0.95,
            "good_for": ["local_analysis", "code_search", "documentation"],
            "limitation": "Only searches local files"
        },
        "code_execution": {
            "reliability": 0.9,
            "speed": 0.7,
            "cost": 0.8,
            "good_for": ["calculation", "algorithm", "verification"],
            "limitation": "Requires safe sandbox"
        },
        "image_generation": {
            "reliability": 0.8,
            "speed": 0.4,
            "cost": 0.5,
            "good_for": ["visualization", "creative", "illustration"],
            "limitation": "May be slow, requires specific models"
        },
    }

    def select_tools(
        self,
        task_description: str,
        available_tools: List[str]
    ) -> List[Tuple[str, float, str]]:
        """
        Select best tools for task

        Returns:
            List of (tool_name, confidence, reasoning) tuples
        """
        scores = {}

        for tool in available_tools:
            if tool not in self.TOOL_PROFILES:
                scores[tool] = 0.0
                continue

            score = self._score_tool(tool, task_description)
            scores[tool] = score

        # Sort by score
        ranked_tools = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Return top tools with scores > 0.5
        selected = [
            (tool, score, self._explain_tool_choice(tool, score))
            for tool, score in ranked_tools
            if score > 0.5
        ]

        return selected

    def _score_tool(self, tool: str, task_description: str) -> float:
        """Score a tool for the task"""
        profile = self.TOOL_PROFILES.get(tool, {})

        score = 0.5  # Base score

        # Check if task mentions what tool is good for
        task_lower = task_description.lower()
        for good_use in profile.get("good_for", []):
            if good_use in task_lower:
                score += 0.25

        # Reliability and speed
        score += (profile.get("reliability", 0.5) * 0.2)
        score += (profile.get("speed", 0.5) * 0.1)

        return min(score, 1.0)

    def _explain_tool_choice(self, tool: str, score: float) -> str:
        """Explain why tool was chosen"""
        profile = self.TOOL_PROFILES.get(tool, {})

        reasons = [f"{tool} is a good fit"]

        if profile.get("reliability", 0) > 0.85:
            reasons.append("high reliability")

        if profile.get("speed", 0) > 0.75:
            reasons.append("fast execution")

        return f"{reasons[0]} - {', '.join(reasons[1:])}" if len(reasons) > 1 else reasons[0]


# ============================================================================
# Response Approach Selector
# ============================================================================

class ResponseApproachSelector:
    """Selects appropriate response approach"""

    def select_approach(
        self,
        task_complexity: float,
        user_expertise: str,
        available_time_ms: Optional[int],
        has_steps: bool = False
    ) -> Tuple[ResponseApproach, float]:
        """
        Select response approach

        Returns:
            Tuple of (ResponseApproach, confidence)
        """
        if has_steps and available_time_ms and available_time_ms > 10000:
            return ResponseApproach.STEP_BY_STEP, 0.9

        if task_complexity > 0.7 and user_expertise == "beginner":
            return ResponseApproach.EXPLANATION_FIRST, 0.85

        if user_expertise == "expert" and task_complexity > 0.5:
            return ResponseApproach.CODE_FIRST, 0.8

        if available_time_ms and available_time_ms < 5000:
            return ResponseApproach.CONCISE, 0.9

        if task_complexity > 0.6:
            return ResponseApproach.DETAILED, 0.8

        return ResponseApproach.CONCISE, 0.75


# ============================================================================
# Risk Handler
# ============================================================================

class RiskHandler:
    """Handles risk in decisions"""

    def determine_risk_handling(
        self,
        risk_level: str,
        is_reversible: bool = True
    ) -> Dict[str, Any]:
        """
        Determine how to handle risk

        Returns:
            Dictionary with risk handling strategy
        """
        strategy = {
            "require_confirmation": False,
            "create_backup": False,
            "proceed_cautiously": False,
            "additional_validation": False,
            "monitoring_required": False
        }

        if risk_level == "low":
            strategy["proceed_cautiously"] = False
        elif risk_level == "medium":
            strategy["proceed_cautiously"] = True
            if not is_reversible:
                strategy["create_backup"] = True
        elif risk_level == "high":
            strategy["require_confirmation"] = True
            strategy["create_backup"] = True
            strategy["additional_validation"] = True
        elif risk_level == "critical":
            strategy["require_confirmation"] = True
            strategy["create_backup"] = True
            strategy["additional_validation"] = True
            strategy["monitoring_required"] = True

        return strategy


# ============================================================================
# Main Decision Engine
# ============================================================================

class TerminatorDecisionEngine:
    """
    Main decision engine that makes intelligent decisions about
    models, tools, approaches, and risk handling.
    """

    _instance: Optional['TerminatorDecisionEngine'] = None
    _lock = threading.Lock()
    _decision_counter = 0

    def __init__(self):
        """Initialize decision engine"""
        self.model_selector = ModelSelector()
        self.tool_selector = ToolSelector()
        self.approach_selector = ResponseApproachSelector()
        self.risk_handler = RiskHandler()

        self.decisions: Dict[str, Decision] = {}
        self.storage_path = "/Users/reeazmahmud/Desktop/Terminator/decisions/data"
        os.makedirs(self.storage_path, exist_ok=True)

    @classmethod
    def get_instance(cls) -> 'TerminatorDecisionEngine':
        """Get singleton instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _generate_decision_id(self) -> str:
        """Generate unique decision ID"""
        TerminatorDecisionEngine._decision_counter += 1
        return f"decision_{TerminatorDecisionEngine._decision_counter:06d}"

    def decide_model(
        self,
        task_type: str,
        available_time_ms: Optional[int] = None,
        complexity: float = 0.5,
        cost_sensitive: bool = False
    ) -> Decision:
        """Make model selection decision"""
        decision_id = self._generate_decision_id()

        # Select model
        selected_model, confidence, reasoning = self.model_selector.select_model(
            task_type, available_time_ms, complexity, cost_sensitive
        )

        # Create decision option
        selected_option = DecisionOption(
            option_id=f"{decision_id}_selected",
            option_name=selected_model,
            option_type="model",
            score=confidence,
            reasoning=reasoning,
            benefits=self._get_model_benefits(selected_model),
            risks=[]
        )

        # Create decision
        decision = Decision(
            decision_id=decision_id,
            decision_type="model_selection",
            selected_option=selected_option,
            confidence=confidence,
            reasoning=reasoning,
            context_factors={
                "task_type": task_type,
                "complexity": complexity,
                "cost_sensitive": cost_sensitive,
                "available_time_ms": available_time_ms
            }
        )

        self.decisions[decision_id] = decision
        return decision

    def decide_tools(
        self,
        task_description: str,
        available_tools: List[str]
    ) -> Decision:
        """Make tool selection decision"""
        decision_id = self._generate_decision_id()

        # Select tools
        selected_tools = self.tool_selector.select_tools(task_description, available_tools)

        if not selected_tools:
            # Default to empty tool list
            selected_option = DecisionOption(
                option_id=f"{decision_id}_selected",
                option_name="no_tools",
                option_type="tool_combination",
                score=0.5,
                reasoning="No tools needed for this task"
            )
        else:
            tool_names = [t[0] for t in selected_tools]
            selected_option = DecisionOption(
                option_id=f"{decision_id}_selected",
                option_name=", ".join(tool_names),
                option_type="tool_combination",
                score=selected_tools[0][1],
                reasoning=selected_tools[0][2],
                benefits=[f"Use {name}" for name, _, _ in selected_tools]
            )

        decision = Decision(
            decision_id=decision_id,
            decision_type="tool_selection",
            selected_option=selected_option,
            confidence=selected_option.score,
            reasoning=selected_option.reasoning,
            context_factors={"task_description": task_description[:100]}
        )

        self.decisions[decision_id] = decision
        return decision

    def decide_approach(
        self,
        task_complexity: float,
        user_expertise: str,
        available_time_ms: Optional[int],
        has_steps: bool = False
    ) -> Decision:
        """Make response approach decision"""
        decision_id = self._generate_decision_id()

        approach, confidence = self.approach_selector.select_approach(
            task_complexity, user_expertise, available_time_ms, has_steps
        )

        selected_option = DecisionOption(
            option_id=f"{decision_id}_selected",
            option_name=approach.value,
            option_type="response_approach",
            score=confidence,
            reasoning=f"Selected {approach.value} approach based on complexity and time constraints"
        )

        decision = Decision(
            decision_id=decision_id,
            decision_type="response_approach",
            selected_option=selected_option,
            confidence=confidence,
            context_factors={
                "complexity": task_complexity,
                "expertise": user_expertise,
                "available_time_ms": available_time_ms
            }
        )

        self.decisions[decision_id] = decision
        return decision

    def decide_risk_handling(
        self,
        risk_level: str,
        is_reversible: bool = True
    ) -> Dict[str, Any]:
        """Determine risk handling strategy"""
        return self.risk_handler.determine_risk_handling(risk_level, is_reversible)

    def record_decision_outcome(
        self,
        decision_id: str,
        success: bool,
        notes: str = ""
    ) -> None:
        """Record outcome of a decision"""
        if decision_id in self.decisions:
            decision = self.decisions[decision_id]
            decision.success = success
            # Could analyze patterns and improve future decisions

    def get_decision(self, decision_id: str) -> Optional[Decision]:
        """Get a specific decision"""
        return self.decisions.get(decision_id)

    def _get_model_benefits(self, model_name: str) -> List[str]:
        """Get benefits of selected model"""
        profile = self.model_selector.MODEL_PROFILES.get(model_name, {})
        benefits = []

        if profile.get("quality", 0) > 0.8:
            benefits.append("High quality output")
        if profile.get("speed", 0) > 0.7:
            benefits.append("Fast response")
        if profile.get("cost", 0) > 0.8:
            benefits.append("Cost effective")

        return benefits


# ============================================================================
# Module-level access functions
# ============================================================================

def get_decision_engine() -> TerminatorDecisionEngine:
    """Get the decision engine instance"""
    return TerminatorDecisionEngine.get_instance()


if __name__ == "__main__":
    # Test the decision engine
    engine = get_decision_engine()

    # Test model decision
    print("\n" + "="*60)
    print("MODEL SELECTION DECISION")
    print("="*60)
    model_decision = engine.decide_model(
        task_type="code_analysis",
        available_time_ms=5000,
        complexity=0.7
    )
    print(f"Decision: {model_decision.selected_option.option_name}")
    print(f"Confidence: {model_decision.confidence:.0%}")
    print(f"Reasoning: {model_decision.reasoning}")

    # Test tool decision
    print("\n" + "="*60)
    print("TOOL SELECTION DECISION")
    print("="*60)
    tool_decision = engine.decide_tools(
        task_description="Search the web for recent Python developments",
        available_tools=["web_search", "file_search", "code_execution"]
    )
    print(f"Tools: {tool_decision.selected_option.option_name}")
    print(f"Confidence: {tool_decision.confidence:.0%}")

    # Test approach decision
    print("\n" + "="*60)
    print("RESPONSE APPROACH DECISION")
    print("="*60)
    approach_decision = engine.decide_approach(
        task_complexity=0.8,
        user_expertise="beginner",
        available_time_ms=30000,
        has_steps=True
    )
    print(f"Approach: {approach_decision.selected_option.option_name}")
    print(f"Confidence: {approach_decision.confidence:.0%}")
