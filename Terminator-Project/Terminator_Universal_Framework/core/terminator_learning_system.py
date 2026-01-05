#!/usr/bin/env python3

# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Learning System
Learns from every interaction to optimize behavior, personalize responses,
and continuously improve performance.

Features:
- User preference learning
- Model performance tracking per user
- Tool effectiveness tracking
- Response style optimization
- Pattern recognition in successful interactions
- Self-optimizing behavior
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import time
from collections import defaultdict, Counter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

TERMINATOR_ROOT = Path("/Users/reeazmahmud/Desktop/Terminator")
LEARNING_DIR = TERMINATOR_ROOT / "learning" / "data"
LEARNING_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR = TERMINATOR_ROOT / "logs" / "learning_system"
LOGS_DIR.mkdir(parents=True, exist_ok=True)


class InteractionType(Enum):
    """Types of interactions"""
    QUERY = "QUERY"
    COMMAND = "COMMAND"
    CREATIVE = "CREATIVE"
    ANALYTICAL = "ANALYTICAL"
    RESEARCH = "RESEARCH"
    CODING = "CODING"


@dataclass
class UserPreference:
    """User preference tracking"""
    preference_key: str
    value: Any
    confidence: float  # 0.0-1.0
    last_updated: str
    update_count: int
    feedback_score: float


@dataclass
class ModelPerformance:
    """Model performance tracking"""
    model_name: str
    task_type: str
    success_count: int
    failure_count: int
    avg_response_time: float
    user_satisfaction: float  # 0.0-5.0
    last_used: str


@dataclass
class ToolUsagePattern:
    """Tool usage learning"""
    tool_name: str
    success_count: int
    failure_count: int
    avg_effectiveness: float  # 0.0-1.0
    common_context: str
    preferred_order: List[str]


@dataclass
class InteractionRecord:
    """Complete interaction record for learning"""
    timestamp: str
    interaction_type: str
    query: str
    model_used: str
    tools_used: List[str]
    response_length: int
    user_satisfaction: float
    success: bool
    duration_ms: float
    outcome: str


class UserProfileManager:
    """Manages user-specific preferences and profiles"""

    def __init__(self, db_dir: Path = LEARNING_DIR):
        self.db_dir = db_dir
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.preferences_file = self.db_dir / "user_preferences.json"
        self.preferences = self._load_preferences()

    def _load_preferences(self) -> Dict[str, UserPreference]:
        """Load preferences from disk"""
        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, 'r') as f:
                    data = json.load(f)
                return {k: UserPreference(**v) for k, v in data.items()}
            except Exception as e:
                logger.error(f"Error loading preferences: {e}")
        return {}

    def _save_preferences(self) -> None:
        """Save preferences to disk"""
        try:
            data = {k: asdict(v) for k, v in self.preferences.items()}
            with open(self.preferences_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving preferences: {e}")

    def learn_preference(self, key: str, value: Any, feedback: float = 0.5) -> None:
        """Learn a user preference"""
        if key in self.preferences:
            pref = self.preferences[key]
            pref.update_count += 1
            pref.last_updated = datetime.now().isoformat()
            pref.feedback_score = (pref.feedback_score + feedback) / 2
            pref.confidence = min(1.0, pref.confidence + 0.05)
        else:
            pref = UserPreference(
                preference_key=key,
                value=value,
                confidence=0.3,
                last_updated=datetime.now().isoformat(),
                update_count=1,
                feedback_score=feedback
            )
            self.preferences[key] = pref

        self._save_preferences()
        logger.info(f"Learned preference: {key}={value} (confidence: {pref.confidence:.2f})")

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get learned preference"""
        if key in self.preferences:
            pref = self.preferences[key]
            if pref.confidence > 0.5:  # Only return high-confidence preferences
                return pref.value
        return default

    def get_all_preferences(self, min_confidence: float = 0.5) -> Dict[str, Any]:
        """Get all preferences above confidence threshold"""
        return {
            k: v.value for k, v in self.preferences.items()
            if v.confidence >= min_confidence
        }


class ModelPerformanceTracker:
    """Tracks model performance per user and task type"""

    def __init__(self, db_dir: Path = LEARNING_DIR):
        self.db_dir = db_dir
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.performance_file = self.db_dir / "model_performance.json"
        self.performance = self._load_performance()

    def _load_performance(self) -> Dict[str, ModelPerformance]:
        """Load performance data"""
        if self.performance_file.exists():
            try:
                with open(self.performance_file, 'r') as f:
                    data = json.load(f)
                return {k: ModelPerformance(**v) for k, v in data.items()}
            except Exception as e:
                logger.error(f"Error loading performance: {e}")
        return {}

    def _save_performance(self) -> None:
        """Save performance data"""
        try:
            data = {k: asdict(v) for k, v in self.performance.items()}
            with open(self.performance_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving performance: {e}")

    def record_performance(self, model: str, task_type: str, success: bool,
                          response_time: float, satisfaction: float) -> None:
        """Record model performance"""
        key = f"{model}_{task_type}"

        if key in self.performance:
            perf = self.performance[key]
            if success:
                perf.success_count += 1
            else:
                perf.failure_count += 1
            perf.avg_response_time = (perf.avg_response_time + response_time) / 2
            perf.user_satisfaction = (perf.user_satisfaction + satisfaction) / 2
        else:
            perf = ModelPerformance(
                model_name=model,
                task_type=task_type,
                success_count=1 if success else 0,
                failure_count=0 if success else 1,
                avg_response_time=response_time,
                user_satisfaction=satisfaction,
                last_used=datetime.now().isoformat()
            )
            self.performance[key] = perf

        perf.last_used = datetime.now().isoformat()
        self._save_performance()

    def get_best_model(self, task_type: str) -> Optional[str]:
        """Get best performing model for task type"""
        candidates = [
            (k.split('_')[0], v) for k, v in self.performance.items()
            if v.task_type == task_type
        ]

        if not candidates:
            return None

        # Score based on satisfaction, success rate, and speed
        def score(model_name, perf):
            total = perf.success_count + perf.failure_count
            success_rate = perf.success_count / total if total > 0 else 0
            return perf.user_satisfaction * success_rate / (perf.avg_response_time / 1000 + 1)

        return max(candidates, key=lambda x: score(x[0], x[1]))[0]

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.performance:
            return {'models': 0, 'avg_satisfaction': 0}

        satisfactions = [p.user_satisfaction for p in self.performance.values()]
        success_rates = [
            (p.success_count / (p.success_count + p.failure_count))
            for p in self.performance.values()
            if (p.success_count + p.failure_count) > 0
        ]

        return {
            'models_tracked': len(set(k.split('_')[0] for k in self.performance.keys())),
            'avg_satisfaction': sum(satisfactions) / len(satisfactions) if satisfactions else 0,
            'avg_success_rate': sum(success_rates) / len(success_rates) if success_rates else 0,
            'avg_response_time_ms': sum(p.avg_response_time for p in self.performance.values()) / len(self.performance)
        }


class ToolEffectivenessTracker:
    """Tracks tool effectiveness for different contexts"""

    def __init__(self, db_dir: Path = LEARNING_DIR):
        self.db_dir = db_dir
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.tools_file = self.db_dir / "tool_effectiveness.json"
        self.tools = self._load_tools()

    def _load_tools(self) -> Dict[str, ToolUsagePattern]:
        """Load tool data"""
        if self.tools_file.exists():
            try:
                with open(self.tools_file, 'r') as f:
                    data = json.load(f)
                return {k: ToolUsagePattern(**v) for k, v in data.items()}
            except Exception as e:
                logger.error(f"Error loading tools: {e}")
        return {}

    def _save_tools(self) -> None:
        """Save tool data"""
        try:
            data = {k: asdict(v) for k, v in self.tools.items()}
            with open(self.tools_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving tools: {e}")

    def record_tool_usage(self, tool: str, success: bool, context: str) -> None:
        """Record tool usage"""
        if tool in self.tools:
            t = self.tools[tool]
            if success:
                t.success_count += 1
            else:
                t.failure_count += 1
            total = t.success_count + t.failure_count
            t.avg_effectiveness = t.success_count / total
        else:
            self.tools[tool] = ToolUsagePattern(
                tool_name=tool,
                success_count=1 if success else 0,
                failure_count=0 if success else 1,
                avg_effectiveness=1.0 if success else 0.0,
                common_context=context,
                preferred_order=[]
            )

        self._save_tools()

    def get_recommended_tools(self, context: str, count: int = 3) -> List[str]:
        """Get recommended tools for context"""
        candidates = [
            (k, v.avg_effectiveness) for k, v in self.tools.items()
            if v.success_count > 0 and context.lower() in v.common_context.lower()
        ]

        candidates.sort(key=lambda x: x[1], reverse=True)
        return [c[0] for c in candidates[:count]]


class ResponseStyleOptimizer:
    """Learns and optimizes response styles"""

    def __init__(self, db_dir: Path = LEARNING_DIR):
        self.db_dir = db_dir
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.styles_file = self.db_dir / "response_styles.json"
        self.styles = self._load_styles()

    def _load_styles(self) -> Dict[str, Any]:
        """Load style preferences"""
        if self.styles_file.exists():
            try:
                with open(self.styles_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading styles: {e}")
        return {}

    def _save_styles(self) -> None:
        """Save style preferences"""
        try:
            with open(self.styles_file, 'w') as f:
                json.dump(self.styles, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving styles: {e}")

    def learn_style_preference(self, style_key: str, value: Any, feedback: float) -> None:
        """Learn a style preference"""
        if style_key in self.styles:
            self.styles[style_key]['count'] += 1
            self.styles[style_key]['feedback'] = (self.styles[style_key]['feedback'] + feedback) / 2
        else:
            self.styles[style_key] = {
                'value': value,
                'count': 1,
                'feedback': feedback,
                'learned_at': datetime.now().isoformat()
            }

        self._save_styles()

    def get_optimal_style(self, style_key: str) -> Optional[Any]:
        """Get optimal style for key"""
        if style_key in self.styles:
            return self.styles[style_key].get('value')
        return None

    def get_all_styles(self) -> Dict[str, Any]:
        """Get all learned styles"""
        return {k: v['value'] for k, v in self.styles.items()}


class TerminatorLearningSystem:
    """Main learning system orchestrator"""

    def __init__(self):
        self.user_profile = UserProfileManager()
        self.model_tracker = ModelPerformanceTracker()
        self.tool_tracker = ToolEffectivenessTracker()
        self.style_optimizer = ResponseStyleOptimizer()
        self.interaction_history: List[InteractionRecord] = []
        self.max_history = 10000

    def record_interaction(self, interaction: InteractionRecord) -> None:
        """Record an interaction for learning"""
        self.interaction_history.append(interaction)

        # Learn from the interaction
        if interaction.success:
            # Reinforce successful approaches
            if interaction.model_used:
                self.model_tracker.record_performance(
                    interaction.model_used,
                    interaction.interaction_type,
                    True,
                    interaction.duration_ms,
                    interaction.user_satisfaction
                )

            # Learn tool effectiveness
            for tool in interaction.tools_used:
                self.tool_tracker.record_tool_usage(tool, True, interaction.interaction_type)

            # Learn successful patterns
            self.user_profile.learn_preference(
                f"successful_{interaction.interaction_type}_pattern",
                {
                    'model': interaction.model_used,
                    'tools': interaction.tools_used,
                    'response_length': interaction.response_length
                },
                interaction.user_satisfaction
            )

        # Trim history
        if len(self.interaction_history) > self.max_history:
            self.interaction_history = self.interaction_history[-self.max_history:]

    def get_recommendations(self) -> Dict[str, Any]:
        """Get learning-based recommendations"""
        return {
            'model_suggestions': {
                'coding': self.model_tracker.get_best_model('CODING'),
                'creative': self.model_tracker.get_best_model('CREATIVE'),
                'analytical': self.model_tracker.get_best_model('ANALYTICAL'),
            },
            'tool_suggestions': {
                'research': self.tool_tracker.get_recommended_tools('research'),
                'coding': self.tool_tracker.get_recommended_tools('coding'),
                'general': self.tool_tracker.get_recommended_tools('general'),
            },
            'response_style': self.style_optimizer.get_all_styles(),
            'preferences': self.user_profile.get_all_preferences(),
        }

    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of learning progress"""
        return {
            'timestamp': datetime.now().isoformat(),
            'interactions_recorded': len(self.interaction_history),
            'preferences_learned': len(self.user_profile.preferences),
            'model_performance': self.model_tracker.get_performance_summary(),
            'tools_tracked': len(self.tool_tracker.tools),
            'response_styles': len(self.style_optimizer.styles),
        }

    def export_learning_data(self, export_path: Path = None) -> bool:
        """Export all learning data"""
        if export_path is None:
            export_path = LOGS_DIR / f"learning_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'preferences': {k: asdict(v) for k, v in self.user_profile.preferences.items()},
                'model_performance': {k: asdict(v) for k, v in self.model_tracker.performance.items()},
                'tool_effectiveness': {k: asdict(v) for k, v in self.tool_tracker.tools.items()},
                'response_styles': self.style_optimizer.styles,
                'summary': self.get_learning_summary(),
            }

            with open(export_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"Learning data exported to {export_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting learning data: {e}")
            return False


# Global instance
_learning_system: Optional[TerminatorLearningSystem] = None


def get_learning_system() -> TerminatorLearningSystem:
    """Get or create global learning system"""
    global _learning_system
    if _learning_system is None:
        _learning_system = TerminatorLearningSystem()
    return _learning_system


if __name__ == "__main__":
    # Test the learning system
    system = get_learning_system()

    # Record a sample interaction
    interaction = InteractionRecord(
        timestamp=datetime.now().isoformat(),
        interaction_type="CODING",
        query="Help me write a Python function",
        model_used="codestral",
        tools_used=["web_search"],
        response_length=500,
        user_satisfaction=4.5,
        success=True,
        duration_ms=2500.0,
        outcome="Successfully wrote function"
    )

    system.record_interaction(interaction)
    print(json.dumps(system.get_learning_summary(), indent=2, default=str))
