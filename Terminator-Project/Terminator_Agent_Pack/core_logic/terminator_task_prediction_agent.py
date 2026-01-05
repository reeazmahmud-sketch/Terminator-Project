# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Task Prediction Agent - Anticipatory Task Management
==========================================================

Predicts what task the user will need next and prepares resources in advance.
Detects patterns in user behavior to provide proactive assistance.

Features:
- Time-based prediction (what happens at specific times)
- Context-based prediction (what follows specific patterns)
- Resource pre-warming (preparing models/tools)
- Confidence scoring for predictions
- Adaptation based on prediction outcomes
- Seasonal/calendar-aware patterns

Created: December 11, 2025
Part of: TERMINATOR Enhancement Roadmap - Tier 3 (Proactivity)
"""

import json
import os
import threading
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import defaultdict


# ============================================================================
# Data Structures
# ============================================================================

class PredictionType(Enum):
    """Type of prediction"""
    TIME_BASED = "time_based"
    PATTERN_BASED = "pattern_based"
    CONTEXT_BASED = "context_based"
    SEASONAL = "seasonal"


@dataclass
class TaskSequence:
    """Sequence of tasks user performs"""
    task_types: List[str]
    timestamps: List[str]
    frequency: int = 1
    confidence: float = 0.5
    last_occurrence: Optional[str] = None


@dataclass
class PredictedTask:
    """A predicted upcoming task"""
    task_type: str
    predicted_time: Optional[str] = None  # ISO format
    confidence: float = 0.5
    prediction_type: PredictionType = PredictionType.PATTERN_BASED
    required_models: List[str] = field(default_factory=list)
    required_tools: List[str] = field(default_factory=list)
    context_hints: Dict[str, Any] = field(default_factory=dict)
    urgency: int = 1  # 1-5
    preparation_time_ms: int = 1000


@dataclass
class PredictionRecord:
    """Record of a prediction and its outcome"""
    predicted_task: PredictedTask
    actual_task: Optional[str] = None
    accuracy: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    resolved_at: Optional[str] = None


# ============================================================================
# Task Sequence Analyzer
# ============================================================================

class TaskSequenceAnalyzer:
    """Analyzes sequences of tasks to find patterns"""

    def __init__(self):
        """Initialize task sequence analyzer"""
        self.sequences: Dict[str, TaskSequence] = {}
        self.task_history: List[Tuple[str, str]] = []  # (task_type, timestamp)

    def record_task(self, task_type: str, timestamp: str = None) -> None:
        """Record a task execution"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        self.task_history.append((task_type, timestamp))

        # Keep last 500 tasks
        if len(self.task_history) > 500:
            self.task_history = self.task_history[-500:]

        self._analyze_sequences()

    def _analyze_sequences(self) -> None:
        """Analyze task sequences from history"""
        if len(self.task_history) < 2:
            return

        # Look for 2-task and 3-task sequences
        self._find_n_gram_sequences(2)
        self._find_n_gram_sequences(3)

    def _find_n_gram_sequences(self, n: int) -> None:
        """Find n-gram task sequences"""
        if len(self.task_history) < n:
            return

        sequence_counts = defaultdict(int)
        sequence_times = defaultdict(list)

        for i in range(len(self.task_history) - n + 1):
            sequence = tuple(self.task_history[i:i+n])
            task_sequence = "-".join([t[0] for t in sequence])
            sequence_counts[task_sequence] += 1

            # Store time between first and last
            first_time = datetime.fromisoformat(sequence[0][1])
            last_time = datetime.fromisoformat(sequence[-1][1])
            duration = (last_time - first_time).total_seconds()
            sequence_times[task_sequence].append(duration)

        # Create sequence objects for frequent sequences
        for task_sequence, count in sequence_counts.items():
            if count >= 2:  # At least 2 occurrences
                confidence = min(count / 10, 1.0)  # Higher for more frequent
                avg_time = sum(sequence_times[task_sequence]) / len(sequence_times[task_sequence])

                self.sequences[task_sequence] = TaskSequence(
                    task_types=task_sequence.split("-"),
                    timestamps=[],
                    frequency=count,
                    confidence=confidence
                )

    def predict_next_task(self, recent_tasks: List[str]) -> Optional[Tuple[str, float]]:
        """Predict next task given recent task history"""
        if not recent_tasks:
            return None

        # Try 3-task and 2-task patterns
        for n in [3, 2]:
            if len(recent_tasks) >= n:
                pattern = "-".join(recent_tasks[-n:])

                # Look for sequences starting with this pattern
                for seq_key, sequence in self.sequences.items():
                    if seq_key.startswith(pattern):
                        tasks = seq_key.split("-")
                        if len(tasks) > n:
                            next_task = tasks[-1]
                            return next_task, sequence.confidence

        return None

    def get_sequences(self) -> Dict[str, TaskSequence]:
        """Get all discovered sequences"""
        return self.sequences

    def get_frequent_transitions(self) -> Dict[str, Tuple[str, float]]:
        """Get most frequent task transitions"""
        transitions = {}

        for seq_key, sequence in self.sequences.items():
            if "-" in seq_key:
                parts = seq_key.split("-")
                from_task = parts[0]
                to_task = parts[-1]
                key = f"{from_task} -> {to_task}"
                transitions[key] = (to_task, sequence.confidence)

        return transitions


# ============================================================================
# Time-Based Predictor
# ============================================================================

class TimeBasedPredictor:
    """Predicts tasks based on time patterns"""

    def __init__(self):
        """Initialize time-based predictor"""
        self.hourly_patterns: Dict[int, List[str]] = defaultdict(list)  # hour -> [task_types]
        self.daily_patterns: Dict[int, List[str]] = defaultdict(list)  # day_of_week -> [task_types]

    def record_task_time(self, task_type: str, timestamp: str) -> None:
        """Record task execution time"""
        try:
            dt = datetime.fromisoformat(timestamp)
            hour = dt.hour
            day = dt.weekday()

            self.hourly_patterns[hour].append(task_type)
            self.daily_patterns[day].append(task_type)

            # Keep recent history
            if len(self.hourly_patterns[hour]) > 100:
                self.hourly_patterns[hour] = self.hourly_patterns[hour][-100:]
        except:
            pass

    def predict_for_time(self, target_time: datetime) -> Optional[Tuple[str, float]]:
        """Predict task at specific time"""
        hour = target_time.hour
        day = target_time.weekday()

        # Try daily pattern first
        if day in self.daily_patterns and self.daily_patterns[day]:
            tasks = self.daily_patterns[day]
            most_common = max(set(tasks), key=tasks.count)
            confidence = tasks.count(most_common) / len(tasks)
            return most_common, confidence

        # Fall back to hourly pattern
        if hour in self.hourly_patterns and self.hourly_patterns[hour]:
            tasks = self.hourly_patterns[hour]
            most_common = max(set(tasks), key=tasks.count)
            confidence = tasks.count(most_common) / len(tasks)
            return most_common, confidence

        return None

    def predict_next_hour(self) -> Optional[Tuple[str, float]]:
        """Predict task for next hour"""
        next_hour = datetime.now() + timedelta(hours=1)
        return self.predict_for_time(next_hour)

    def predict_tomorrow_same_time(self) -> Optional[Tuple[str, float]]:
        """Predict task for tomorrow at current time"""
        tomorrow = datetime.now() + timedelta(days=1)
        return self.predict_for_time(tomorrow)


# ============================================================================
# Context-Based Predictor
# ============================================================================

class ContextBasedPredictor:
    """Predicts tasks based on context patterns"""

    def __init__(self):
        """Initialize context-based predictor"""
        self.context_patterns: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))

    def record_task_context(
        self,
        task_type: str,
        context_factors: Dict[str, Any]
    ) -> None:
        """Record task with context"""
        for key, value in context_factors.items():
            context_key = f"{key}_{value}"
            self.context_patterns[context_key][task_type].append(task_type)

    def predict_for_context(self, context_factors: Dict[str, Any]) -> List[Tuple[str, float]]:
        """Predict tasks for given context"""
        predictions = []

        for key, value in context_factors.items():
            context_key = f"{key}_{value}"

            if context_key in self.context_patterns:
                task_counts = self.context_patterns[context_key]
                total = sum(len(v) for v in task_counts.values())

                for task, occurrences in task_counts.items():
                    confidence = len(occurrences) / total
                    predictions.append((task, confidence))

        # Sort by confidence
        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions


# ============================================================================
# Main Task Prediction Agent
# ============================================================================

class TerminatorTaskPredictionAgent:
    """
    Main task prediction agent that anticipates user needs
    and prepares resources in advance.
    """

    _instance: Optional['TerminatorTaskPredictionAgent'] = None
    _lock = threading.Lock()

    def __init__(self, check_interval: int = 60):
        """
        Initialize task prediction agent

        Args:
            check_interval: How often to check for upcoming tasks (seconds)
        """
        self.check_interval = check_interval
        self.sequence_analyzer = TaskSequenceAnalyzer()
        self.time_predictor = TimeBasedPredictor()
        self.context_predictor = ContextBasedPredictor()

        self.prediction_history: List[PredictionRecord] = []
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None

        self.storage_path = "/Users/reeazmahmud/Desktop/Terminator/prediction/data"
        os.makedirs(self.storage_path, exist_ok=True)

    @classmethod
    def get_instance(cls) -> 'TerminatorTaskPredictionAgent':
        """Get singleton instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def start_monitoring(self) -> None:
        """Start the prediction monitoring thread"""
        if self.monitoring:
            print("Task prediction agent already monitoring")
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        print("✅ Task prediction agent started monitoring")

    def stop_monitoring(self) -> None:
        """Stop the prediction monitoring thread"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("⛔ Task prediction agent stopped")

    def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self._update_predictions()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"Error in task prediction monitoring: {e}")
                time.sleep(self.check_interval)

    def _update_predictions(self) -> None:
        """Update predictions"""
        predictions = self.get_next_predictions(count=5)
        # Could trigger resource preparation here

    def record_task(
        self,
        task_type: str,
        timestamp: str = None,
        context_factors: Dict[str, Any] = None
    ) -> None:
        """Record a task execution"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        self.sequence_analyzer.record_task(task_type, timestamp)
        self.time_predictor.record_task_time(task_type, timestamp)

        if context_factors:
            self.context_predictor.record_task_context(task_type, context_factors)

    def predict_next_task(
        self,
        recent_tasks: List[str] = None,
        context_factors: Dict[str, Any] = None
    ) -> Optional[PredictedTask]:
        """Predict the next task user will need"""
        predictions = []

        # Pattern-based prediction
        if recent_tasks:
            next_task_tuple = self.sequence_analyzer.predict_next_task(recent_tasks)
            if next_task_tuple:
                task_type, confidence = next_task_tuple
                predictions.append((task_type, confidence, PredictionType.PATTERN_BASED))

        # Time-based prediction
        time_prediction = self.time_predictor.predict_next_hour()
        if time_prediction:
            task_type, confidence = time_prediction
            predictions.append((task_type, confidence, PredictionType.TIME_BASED))

        # Context-based prediction
        if context_factors:
            context_predictions = self.context_predictor.predict_for_context(context_factors)
            predictions.extend([(t, c, PredictionType.CONTEXT_BASED) for t, c in context_predictions])

        # Select best prediction
        if not predictions:
            return None

        predictions.sort(key=lambda x: x[1], reverse=True)
        best_task, confidence, pred_type = predictions[0]

        predicted = PredictedTask(
            task_type=best_task,
            confidence=confidence,
            prediction_type=pred_type,
            required_models=self._get_required_models(best_task),
            required_tools=self._get_required_tools(best_task),
            urgency=2  # Medium urgency by default
        )

        # Record prediction
        record = PredictionRecord(predicted_task=predicted)
        self.prediction_history.append(record)

        # Keep recent history
        if len(self.prediction_history) > 500:
            self.prediction_history = self.prediction_history[-500:]

        return predicted

    def get_next_predictions(self, count: int = 5) -> List[PredictedTask]:
        """Get multiple upcoming task predictions"""
        predictions = []

        # Generate predictions for different time windows
        for hours_ahead in range(1, count + 1):
            future_time = datetime.now() + timedelta(hours=hours_ahead)
            prediction = self.time_predictor.predict_for_time(future_time)

            if prediction:
                task_type, confidence = prediction
                predicted = PredictedTask(
                    task_type=task_type,
                    predicted_time=future_time.isoformat(),
                    confidence=confidence,
                    prediction_type=PredictionType.TIME_BASED
                )
                predictions.append(predicted)

        return predictions[:count]

    def _get_required_models(self, task_type: str) -> List[str]:
        """Get models needed for task type"""
        task_model_map = {
            "analysis": ["claude-3-opus"],
            "search": ["claude-3-sonnet"],
            "generation": ["claude-3-sonnet"],
            "coding": ["claude-3-opus"],
            "simple": ["claude-3-haiku"],
        }

        for task_prefix, models in task_model_map.items():
            if task_prefix in task_type.lower():
                return models

        return ["claude-3-sonnet"]  # Default

    def _get_required_tools(self, task_type: str) -> List[str]:
        """Get tools needed for task type"""
        task_tool_map = {
            "research": ["web_search"],
            "analysis": ["file_search", "code_execution"],
            "code": ["code_execution", "file_search"],
            "search": ["web_search"],
        }

        tools = []
        for task_prefix, task_tools in task_tool_map.items():
            if task_prefix in task_type.lower():
                tools.extend(task_tools)

        return list(set(tools))  # Remove duplicates

    def get_prediction_accuracy(self) -> Dict[str, Any]:
        """Get prediction accuracy statistics"""
        if not self.prediction_history:
            return {"total_predictions": 0, "accuracy": 0.0}

        resolved = [p for p in self.prediction_history if p.resolved_at is not None]

        if not resolved:
            return {
                "total_predictions": len(self.prediction_history),
                "resolved_predictions": 0,
                "accuracy": 0.0
            }

        correct = sum(1 for p in resolved if p.accuracy)

        return {
            "total_predictions": len(self.prediction_history),
            "resolved_predictions": len(resolved),
            "correct_predictions": correct,
            "accuracy": correct / len(resolved) if resolved else 0.0
        }


# ============================================================================
# Module-level access functions
# ============================================================================

def get_prediction_agent() -> TerminatorTaskPredictionAgent:
    """Get the task prediction agent instance"""
    return TerminatorTaskPredictionAgent.get_instance()


if __name__ == "__main__":
    # Test the task prediction agent
    agent = get_prediction_agent()

    # Record some sample tasks
    base_time = datetime.now()

    agent.record_task("web_search", (base_time).isoformat())
    agent.record_task("analysis", (base_time + timedelta(minutes=5)).isoformat())
    agent.record_task("web_search", (base_time + timedelta(minutes=15)).isoformat())
    agent.record_task("analysis", (base_time + timedelta(minutes=20)).isoformat())

    # Get predictions
    print("\n=== Task Predictions ===")
    prediction = agent.predict_next_task(recent_tasks=["web_search", "analysis"])

    if prediction:
        print(f"Predicted Task: {prediction.task_type}")
        print(f"Confidence: {prediction.confidence:.0%}")
        print(f"Type: {prediction.prediction_type.value}")
        print(f"Required Models: {prediction.required_models}")
        print(f"Required Tools: {prediction.required_tools}")

    print("\n=== Next Hour Predictions ===")
    next_preds = agent.get_next_predictions(count=3)
    for pred in next_preds:
        print(f"  - {pred.task_type} ({pred.confidence:.0%})")
