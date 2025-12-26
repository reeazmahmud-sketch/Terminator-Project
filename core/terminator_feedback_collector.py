# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Feedback Collector - Autonomous Feedback Collection and Analysis
=========================================================================

Continuously collects feedback on task outcomes, user satisfaction, and system performance
to drive the continuous improvement loop.

Features:
- Real-time feedback collection on task execution
- User satisfaction rating capture (1-5 scale)
- Outcome success/failure classification
- Root cause analysis for failures
- Correlation analysis with system variables
- Recommendation generation based on feedback patterns
- Automatic optimization rule generation

Created: December 11, 2025
Part of: TERMINATOR Enhancement Roadmap - Tier 1 (Foundation)
"""

import json
import os
import threading
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict, field
from enum import Enum


# ============================================================================
# Data Structures
# ============================================================================

class OutcomeType(Enum):
    """Classification of task outcomes"""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class FeedbackRating(Enum):
    """User satisfaction ratings"""
    POOR = 1
    FAIR = 2
    GOOD = 3
    VERY_GOOD = 4
    EXCELLENT = 5


@dataclass
class TaskFeedback:
    """Feedback on a completed task"""
    task_id: str
    task_type: str
    outcome: OutcomeType
    user_rating: Optional[int] = None  # 1-5
    execution_time_ms: Optional[float] = None
    model_used: Optional[str] = None
    tools_used: List[str] = field(default_factory=list)
    user_feedback_text: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['outcome'] = self.outcome.value
        return data


@dataclass
class OutcomeAnalysis:
    """Analysis results for an outcome"""
    task_type: str
    outcome_type: OutcomeType
    success_rate: float  # 0.0-1.0
    average_rating: float  # 1.0-5.0
    average_time_ms: float
    most_used_models: List[tuple]  # [(model, count), ...]
    most_used_tools: List[tuple]  # [(tool, count), ...]
    common_failure_reasons: List[str]
    recommendations: List[str]
    analyzed_count: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ============================================================================
# Feedback Gatherer
# ============================================================================

class FeedbackGatherer:
    """Collects feedback from task executions"""

    def __init__(self, storage_path: str = None):
        """Initialize feedback gatherer"""
        if storage_path is None:
            storage_path = "/Users/reeazmahmud/Desktop/Terminator/feedback/data"

        self.storage_path = storage_path
        self.feedback_file = os.path.join(storage_path, "feedback_history.json")
        os.makedirs(storage_path, exist_ok=True)

        self.feedback_cache: List[TaskFeedback] = []
        self._load_feedback_history()

    def _load_feedback_history(self) -> None:
        """Load existing feedback from disk"""
        if os.path.exists(self.feedback_file):
            try:
                with open(self.feedback_file, 'r') as f:
                    data = json.load(f)
                    for item in data:
                        item['outcome'] = OutcomeType(item['outcome'])
                        self.feedback_cache.append(TaskFeedback(**item))
            except Exception as e:
                print(f"Error loading feedback history: {e}")

    def _save_feedback_history(self) -> None:
        """Save feedback to disk"""
        try:
            feedback_dicts = [f.to_dict() for f in self.feedback_cache]
            with open(self.feedback_file, 'w') as f:
                json.dump(feedback_dicts, f, indent=2)
        except Exception as e:
            print(f"Error saving feedback history: {e}")

    def record_feedback(self, feedback: TaskFeedback) -> None:
        """Record feedback for a task"""
        self.feedback_cache.append(feedback)

        # Keep only last 1000 feedback items to manage memory
        if len(self.feedback_cache) > 1000:
            self.feedback_cache = self.feedback_cache[-1000:]

        self._save_feedback_history()

    def get_recent_feedback(self, task_type: str = None, hours: int = 24) -> List[TaskFeedback]:
        """Get feedback from the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        filtered = [
            f for f in self.feedback_cache
            if datetime.fromisoformat(f.timestamp) > cutoff_time
            and (task_type is None or f.task_type == task_type)
        ]

        return filtered

    def get_feedback_by_outcome(self, outcome_type: OutcomeType) -> List[TaskFeedback]:
        """Get all feedback for a specific outcome type"""
        return [f for f in self.feedback_cache if f.outcome == outcome_type]

    def get_feedback_summary(self) -> Dict[str, Any]:
        """Get summary of all feedback collected"""
        if not self.feedback_cache:
            return {
                "total_feedback": 0,
                "outcomes": {},
                "average_rating": 0.0,
                "success_rate": 0.0
            }

        outcomes = {}
        total_rating = 0
        rated_count = 0

        for feedback in self.feedback_cache:
            outcome = feedback.outcome.value
            outcomes[outcome] = outcomes.get(outcome, 0) + 1

            if feedback.user_rating:
                total_rating += feedback.user_rating
                rated_count += 1

        return {
            "total_feedback": len(self.feedback_cache),
            "outcomes": outcomes,
            "average_rating": total_rating / rated_count if rated_count > 0 else 0.0,
            "success_rate": outcomes.get("success", 0) / len(self.feedback_cache),
            "date_range": {
                "earliest": min(f.timestamp for f in self.feedback_cache),
                "latest": max(f.timestamp for f in self.feedback_cache)
            }
        }


# ============================================================================
# Outcome Evaluator
# ============================================================================

class OutcomeEvaluator:
    """Evaluates and analyzes task outcomes"""

    def __init__(self, feedback_gatherer: FeedbackGatherer):
        """Initialize outcome evaluator"""
        self.gatherer = feedback_gatherer
        self.analysis_cache: Dict[str, OutcomeAnalysis] = {}

    def analyze_task_type(self, task_type: str) -> OutcomeAnalysis:
        """Analyze all outcomes for a specific task type"""
        feedback_list = [f for f in self.gatherer.feedback_cache if f.task_type == task_type]

        if not feedback_list:
            return OutcomeAnalysis(
                task_type=task_type,
                outcome_type=OutcomeType.SUCCESS,
                success_rate=0.0,
                average_rating=0.0,
                average_time_ms=0.0,
                most_used_models=[],
                most_used_tools=[],
                common_failure_reasons=[],
                recommendations=["No feedback data yet"],
                analyzed_count=0
            )

        # Calculate success rate
        successes = len([f for f in feedback_list if f.outcome == OutcomeType.SUCCESS])
        success_rate = successes / len(feedback_list)

        # Calculate average rating
        rated = [f for f in feedback_list if f.user_rating]
        average_rating = sum(f.user_rating for f in rated) / len(rated) if rated else 0.0

        # Calculate average execution time
        timed = [f for f in feedback_list if f.execution_time_ms is not None]
        average_time = sum(f.execution_time_ms for f in timed) / len(timed) if timed else 0.0

        # Get most used models
        model_counts = {}
        for f in feedback_list:
            if f.model_used:
                model_counts[f.model_used] = model_counts.get(f.model_used, 0) + 1
        most_used_models = sorted(model_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        # Get most used tools
        tool_counts = {}
        for f in feedback_list:
            for tool in f.tools_used:
                tool_counts[tool] = tool_counts.get(tool, 0) + 1
        most_used_tools = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        # Analyze failures
        failures = [f for f in feedback_list if f.outcome in [OutcomeType.FAILURE, OutcomeType.ERROR]]
        failure_reasons = []
        for failure in failures:
            if failure.user_feedback_text:
                failure_reasons.append(failure.user_feedback_text)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            task_type, success_rate, average_rating, failures, most_used_models
        )

        analysis = OutcomeAnalysis(
            task_type=task_type,
            outcome_type=OutcomeType.SUCCESS,
            success_rate=success_rate,
            average_rating=average_rating,
            average_time_ms=average_time,
            most_used_models=most_used_models,
            most_used_tools=most_used_tools,
            common_failure_reasons=failure_reasons[:10],  # Top 10
            recommendations=recommendations,
            analyzed_count=len(feedback_list)
        )

        self.analysis_cache[task_type] = analysis
        return analysis

    def _generate_recommendations(
        self,
        task_type: str,
        success_rate: float,
        average_rating: float,
        failures: List[TaskFeedback],
        models_used: List[tuple]
    ) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []

        # Success-based recommendations
        if success_rate < 0.7:
            recommendations.append(f"Low success rate ({success_rate:.0%}) - Consider retraining or different approach")

        # Rating-based recommendations
        if average_rating < 2.5:
            recommendations.append(f"Low user satisfaction ({average_rating:.1f}/5) - Review output quality")
        elif average_rating < 3.5:
            recommendations.append(f"Below target rating ({average_rating:.1f}/5) - Minor improvements needed")

        # Failure analysis
        if failures:
            recommendations.append(f"Found {len(failures)} failures - Analyze error patterns")

        # Model recommendations
        if models_used and success_rate < 0.8:
            best_model = models_used[0][0]
            recommendations.append(f"Consider prioritizing {best_model} for this task type")

        # Default if no issues
        if not recommendations:
            recommendations.append("Performance is good - Monitor for changes")

        return recommendations

    def get_analysis_report(self, task_type: str = None) -> Dict[str, Any]:
        """Get comprehensive analysis report"""
        if task_type:
            analysis = self.analyze_task_type(task_type)
            return {
                "task_type": analysis.task_type,
                "analyzed_count": analysis.analyzed_count,
                "success_rate": analysis.success_rate,
                "average_rating": analysis.average_rating,
                "average_execution_time_ms": analysis.average_time_ms,
                "most_used_models": analysis.most_used_models,
                "most_used_tools": analysis.most_used_tools,
                "failure_count": len(analysis.common_failure_reasons),
                "recommendations": analysis.recommendations,
                "timestamp": analysis.timestamp
            }
        else:
            # Report on all task types
            all_task_types = set(f.task_type for f in self.gatherer.feedback_cache)
            reports = {task_type: self.get_analysis_report(task_type) for task_type in all_task_types}
            return {
                "total_task_types": len(reports),
                "total_feedback_items": len(self.gatherer.feedback_cache),
                "reports": reports
            }


# ============================================================================
# Main Feedback Collector
# ============================================================================

class TerminatorFeedbackCollector:
    """
    Main feedback collection system that continuously gathers and analyzes
    feedback from task executions to drive improvements.
    """

    _instance: Optional['TerminatorFeedbackCollector'] = None
    _lock = threading.Lock()

    def __init__(self, check_interval: int = 300):
        """
        Initialize feedback collector

        Args:
            check_interval: How often to update analysis (seconds)
        """
        self.check_interval = check_interval
        self.gatherer = FeedbackGatherer()
        self.evaluator = OutcomeEvaluator(self.gatherer)

        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.stats_file = "/Users/reeazmahmud/Desktop/Terminator/feedback/data/feedback_stats.json"

        # Ensure directory exists
        os.makedirs(os.path.dirname(self.stats_file), exist_ok=True)

    @classmethod
    def get_instance(cls) -> 'TerminatorFeedbackCollector':
        """Get singleton instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def start_monitoring(self) -> None:
        """Start the feedback monitoring thread"""
        if self.monitoring:
            print("Feedback collector already monitoring")
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        print("✅ Feedback collector started monitoring")

    def stop_monitoring(self) -> None:
        """Stop the feedback monitoring thread"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("⛔ Feedback collector stopped")

    def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self._update_statistics()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"Error in feedback monitoring: {e}")
                time.sleep(self.check_interval)

    def _update_statistics(self) -> None:
        """Update and save feedback statistics"""
        try:
            summary = self.gatherer.get_feedback_summary()
            analysis = self.evaluator.get_analysis_report()

            stats = {
                "timestamp": datetime.now().isoformat(),
                "summary": summary,
                "analysis": analysis
            }

            with open(self.stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
        except Exception as e:
            print(f"Error updating feedback statistics: {e}")

    def record_task_feedback(self, feedback: TaskFeedback) -> None:
        """Record feedback for a completed task"""
        self.gatherer.record_feedback(feedback)

    def get_feedback_summary(self) -> Dict[str, Any]:
        """Get summary of all feedback"""
        return self.gatherer.get_feedback_summary()

    def get_task_analysis(self, task_type: str) -> Dict[str, Any]:
        """Get analysis for a specific task type"""
        return self.evaluator.get_analysis_report(task_type)

    def get_all_analysis(self) -> Dict[str, Any]:
        """Get analysis for all task types"""
        return self.evaluator.get_analysis_report()

    def get_improvement_opportunities(self) -> List[str]:
        """Get list of all improvement opportunities identified"""
        opportunities = []
        analysis = self.get_all_analysis()

        if "reports" in analysis:
            for task_type, report in analysis["reports"].items():
                opportunities.extend(report.get("recommendations", []))

        return list(set(opportunities))  # Remove duplicates


# ============================================================================
# Module-level access functions
# ============================================================================

def get_feedback_collector() -> TerminatorFeedbackCollector:
    """Get the feedback collector instance"""
    return TerminatorFeedbackCollector.get_instance()


def record_feedback(
    task_id: str,
    task_type: str,
    outcome: OutcomeType,
    user_rating: Optional[int] = None,
    execution_time_ms: Optional[float] = None,
    model_used: Optional[str] = None,
    tools_used: List[str] = None,
    user_feedback_text: Optional[str] = None,
    context: Dict[str, Any] = None
) -> None:
    """
    Convenience function to record feedback

    Args:
        task_id: Unique task identifier
        task_type: Type of task (e.g., "search", "analysis", "generation")
        outcome: OutcomeType enum value
        user_rating: 1-5 rating from user
        execution_time_ms: How long task took
        model_used: Which model was used
        tools_used: List of tools employed
        user_feedback_text: User's feedback text
        context: Additional context data
    """
    feedback = TaskFeedback(
        task_id=task_id,
        task_type=task_type,
        outcome=outcome,
        user_rating=user_rating,
        execution_time_ms=execution_time_ms,
        model_used=model_used,
        tools_used=tools_used or [],
        user_feedback_text=user_feedback_text,
        context=context or {}
    )

    collector = get_feedback_collector()
    collector.record_task_feedback(feedback)


if __name__ == "__main__":
    # Test the feedback collector
    collector = get_feedback_collector()

    # Record some sample feedback
    record_feedback(
        task_id="task_001",
        task_type="web_search",
        outcome=OutcomeType.SUCCESS,
        user_rating=4,
        execution_time_ms=1250.5,
        model_used="claude-3-sonnet",
        tools_used=["web_search"],
        user_feedback_text="Great results"
    )

    record_feedback(
        task_id="task_002",
        task_type="code_analysis",
        outcome=OutcomeType.PARTIAL_SUCCESS,
        user_rating=3,
        execution_time_ms=3400.0,
        model_used="claude-3-opus",
        tools_used=["file_search", "grep"],
        user_feedback_text="Results were incomplete"
    )

    # Get summary
    print("\n=== Feedback Summary ===")
    print(json.dumps(collector.get_feedback_summary(), indent=2))

    print("\n=== All Analysis ===")
    print(json.dumps(collector.get_all_analysis(), indent=2))
