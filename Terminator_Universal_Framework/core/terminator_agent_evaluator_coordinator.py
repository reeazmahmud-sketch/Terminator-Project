#!/usr/bin/env python3

# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Agent Performance Evaluator Coordinator
Manages real-time evaluation of agent performance (1-10 scale)
Coordinates 4 specialized evaluators and aggregates scores
Triggers retraining for low performers (<6.0)
"""

import json
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import sys

sys.path.insert(0, '/Users/reeazmahmud/Desktop/Terminator')

from integrations.agent_activity_tracker import log_agent_activity, complete_agent_activity
from integrations.detailed_agent_audit import get_audit_logger
from core.terminator_agent_communication_bus import AgentCommunicationBus, Message, MessageType, MessagePriority


class EvaluationStatus(Enum):
    """Evaluation status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRAINING_TRIGGERED = "retraining_triggered"


@dataclass
class AgentEvaluation:
    """Complete agent evaluation result with 10-point scoring"""
    evaluation_id: str
    agent_name: str
    agent_type: str
    task_id: str
    timestamp: str

    # Individual scores (0.0-1.0 each) = 10 points total
    correctness_score: float  # Task completion success
    speed_score: float  # Execution time vs baseline
    resource_efficiency_score: float  # CPU/memory usage
    error_handling_score: float  # Graceful failure recovery
    communication_quality_score: float  # Clear bus messaging
    reliability_score: float  # Consistency across runs
    documentation_score: float  # Code quality/comments
    testing_coverage_score: float  # Tests exist & pass
    security_score: float  # Safe operations
    integration_score: float  # Proper infrastructure use

    # Aggregate
    total_score: float  # 0-10
    passed: bool  # >= 6.0

    # Metadata
    evaluated_by: List[str] = field(default_factory=list)
    llm_models_used: Dict[str, str] = field(default_factory=dict)
    evaluation_duration_seconds: float = 0.0

    # Weak areas (scored < 0.6)
    weak_characteristics: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)

    # Status
    status: str = EvaluationStatus.COMPLETED.value

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

    def get_score_breakdown(self) -> Dict[str, float]:
        """Get breakdown of all 10 scores"""
        return {
            "correctness": self.correctness_score,
            "speed": self.speed_score,
            "resource_efficiency": self.resource_efficiency_score,
            "error_handling": self.error_handling_score,
            "communication_quality": self.communication_quality_score,
            "reliability": self.reliability_score,
            "documentation": self.documentation_score,
            "testing_coverage": self.testing_coverage_score,
            "security": self.security_score,
            "integration": self.integration_score,
        }

    def get_weak_areas(self) -> List[str]:
        """Get characteristics with score < 0.6"""
        scores = self.get_score_breakdown()
        return [name for name, score in scores.items() if score < 0.6]


@dataclass
class EvaluationRequest:
    """Request to evaluate an agent"""
    request_id: str
    agent_name: str
    agent_type: str
    task_id: str
    task_name: str

    # Task data
    success: bool
    actual_duration_seconds: float
    estimated_duration_seconds: float
    output: str = ""
    error_message: str = ""

    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class AgentEvaluatorCoordinator:
    """Coordinates evaluation of agents using 4 specialized evaluators"""

    def __init__(self):
        self.base_path = Path("/Users/reeazmahmud/Desktop/Terminator")
        self.logs_path = self.base_path / "logs" / "agent_evaluations"
        self.logs_path.mkdir(parents=True, exist_ok=True)

        # Evaluation files
        self.evaluations_file = self.logs_path / "evaluations.jsonl"
        self.summary_file = self.logs_path / "evaluation_summary.json"
        self.dashboard_file = self.logs_path / "dashboard.json"

        # Load evaluators
        self.evaluators = {}
        self.initialize_evaluators()

        # Communication
        self.comm_bus = AgentCommunicationBus.get_instance()

        # Audit
        self.audit_logger = get_audit_logger()

        # Statistics
        self.evaluation_queue = asyncio.Queue()
        self.evaluations_completed = 0
        self.low_performance_count = 0
        self.retraining_triggered_count = 0

        print("✅ Agent Evaluator Coordinator initialized")

    def initialize_evaluators(self):
        """Load all 4 specialized evaluators"""
        evaluators_to_load = [
            "CodeQualityEvaluator",
            "PerformanceEvaluator",
            "ReliabilityEvaluator",
            "IntegrationEvaluator"
        ]

        for evaluator_name in evaluators_to_load:
            try:
                # Dynamic import pattern
                if evaluator_name == "CodeQualityEvaluator":
                    from core.terminator_code_quality_evaluator import CodeQualityEvaluator
                    self.evaluators[evaluator_name] = CodeQualityEvaluator()
                elif evaluator_name == "PerformanceEvaluator":
                    from core.terminator_performance_evaluator import PerformanceEvaluator
                    self.evaluators[evaluator_name] = PerformanceEvaluator()
                elif evaluator_name == "ReliabilityEvaluator":
                    from core.terminator_reliability_evaluator import ReliabilityEvaluator
                    self.evaluators[evaluator_name] = ReliabilityEvaluator()
                elif evaluator_name == "IntegrationEvaluator":
                    from core.terminator_integration_evaluator import IntegrationEvaluator
                    self.evaluators[evaluator_name] = IntegrationEvaluator()

                print(f"   ✅ {evaluator_name} loaded")
            except ImportError as e:
                print(f"   ⚠️  {evaluator_name} not yet implemented: {e}")

    async def evaluate_agent(self, request: EvaluationRequest) -> Optional[AgentEvaluation]:
        """
        Evaluate an agent on all 10 characteristics
        Returns aggregated score (0-10)
        """
        evaluation_id = str(uuid.uuid4())[:8]
        start_time = datetime.now()

        # Log activity
        log_agent_activity(
            "evaluator_coordinator",
            f"Evaluating agent {request.agent_name} on task {request.task_id}"
        )

        # Collect scores from all 4 evaluators in parallel
        scores = {}
        models_used = {}
        evaluated_by = []

        try:
            # Run all evaluators in parallel
            evaluation_tasks = []

            if "CodeQualityEvaluator" in self.evaluators:
                evaluation_tasks.append(
                    self.evaluators["CodeQualityEvaluator"].evaluate(request)
                )
                evaluated_by.append("CodeQualityEvaluator")

            if "PerformanceEvaluator" in self.evaluators:
                evaluation_tasks.append(
                    self.evaluators["PerformanceEvaluator"].evaluate(request)
                )
                evaluated_by.append("PerformanceEvaluator")

            if "ReliabilityEvaluator" in self.evaluators:
                evaluation_tasks.append(
                    self.evaluators["ReliabilityEvaluator"].evaluate(request)
                )
                evaluated_by.append("ReliabilityEvaluator")

            if "IntegrationEvaluator" in self.evaluators:
                evaluation_tasks.append(
                    self.evaluators["IntegrationEvaluator"].evaluate(request)
                )
                evaluated_by.append("IntegrationEvaluator")

            # Wait for all evaluations
            if evaluation_tasks:
                results = await asyncio.gather(*evaluation_tasks, return_exceptions=True)

                for result in results:
                    if isinstance(result, Exception):
                        print(f"   ⚠️  Evaluator error: {result}")
                        continue

                    if result:
                        scores.update(result.get("scores", {}))
                        models_used.update(result.get("models_used", {}))

        except Exception as e:
            print(f"❌ Evaluation failed: {e}")
            complete_agent_activity("evaluator_coordinator", "FAILED")
            return None

        # Aggregate 10 individual scores (0.0-1.0 each)
        evaluation = AgentEvaluation(
            evaluation_id=evaluation_id,
            agent_name=request.agent_name,
            agent_type=request.agent_type,
            task_id=request.task_id,
            timestamp=datetime.now().isoformat(),

            # Unpack scores (each 0.0-1.0)
            correctness_score=scores.get("correctness", 0.5),
            speed_score=scores.get("speed", 0.5),
            resource_efficiency_score=scores.get("resource_efficiency", 0.5),
            error_handling_score=scores.get("error_handling", 0.5),
            communication_quality_score=scores.get("communication_quality", 0.5),
            reliability_score=scores.get("reliability", 0.5),
            documentation_score=scores.get("documentation", 0.5),
            testing_coverage_score=scores.get("testing_coverage", 0.5),
            security_score=scores.get("security", 0.5),
            integration_score=scores.get("integration", 0.5),

            # Metadata
            evaluated_by=evaluated_by,
            llm_models_used=models_used,
            evaluation_duration_seconds=(datetime.now() - start_time).total_seconds()
        )

        # Calculate total score
        evaluation.total_score = sum([
            evaluation.correctness_score,
            evaluation.speed_score,
            evaluation.resource_efficiency_score,
            evaluation.error_handling_score,
            evaluation.communication_quality_score,
            evaluation.reliability_score,
            evaluation.documentation_score,
            evaluation.testing_coverage_score,
            evaluation.security_score,
            evaluation.integration_score,
        ])

        # Check pass/fail
        evaluation.passed = evaluation.total_score >= 6.0

        # Get weak areas
        evaluation.weak_characteristics = evaluation.get_weak_areas()

        # Generate improvement suggestions
        if not evaluation.passed:
            evaluation.improvement_suggestions = self._generate_suggestions(evaluation)

        # Log evaluation
        self._log_evaluation(evaluation)

        # Update statistics
        self.evaluations_completed += 1
        if not evaluation.passed:
            self.low_performance_count += 1

        # Complete activity
        complete_agent_activity("evaluator_coordinator", "COMPLETED")

        return evaluation

    def _generate_suggestions(self, evaluation: AgentEvaluation) -> List[str]:
        """Generate improvement suggestions based on weak areas"""
        suggestions = []

        weak_areas = evaluation.get_weak_areas()

        if "correctness" in weak_areas:
            suggestions.append("Improve task correctness - review logic and validation")

        if "speed" in weak_areas:
            suggestions.append("Optimize execution speed - profile and reduce bottlenecks")

        if "resource_efficiency" in weak_areas:
            suggestions.append("Reduce resource usage - optimize memory and CPU")

        if "error_handling" in weak_areas:
            suggestions.append("Enhance error handling - add graceful failure recovery")

        if "communication_quality" in weak_areas:
            suggestions.append("Improve communication - use bus messages more effectively")

        if "reliability" in weak_areas:
            suggestions.append("Increase reliability - ensure consistent performance")

        if "documentation" in weak_areas:
            suggestions.append("Improve documentation - add comments and docstrings")

        if "testing_coverage" in weak_areas:
            suggestions.append("Increase test coverage - add comprehensive tests")

        if "security" in weak_areas:
            suggestions.append("Enhance security - audit for vulnerabilities")

        if "integration" in weak_areas:
            suggestions.append("Improve integration - use infrastructure more effectively")

        return suggestions

    def _log_evaluation(self, evaluation: AgentEvaluation):
        """Log evaluation to append-only JSONL file"""
        entry = {
            "evaluation_id": evaluation.evaluation_id,
            "timestamp": evaluation.timestamp,
            "agent_name": evaluation.agent_name,
            "agent_type": evaluation.agent_type,
            "task_id": evaluation.task_id,
            "total_score": evaluation.total_score,
            "passed": evaluation.passed,
            "scores": evaluation.get_score_breakdown(),
            "weak_characteristics": evaluation.weak_characteristics,
            "suggestions": evaluation.improvement_suggestions,
            "evaluated_by": evaluation.evaluated_by,
            "duration_seconds": evaluation.evaluation_duration_seconds
        }

        with open(self.evaluations_file, 'a') as f:
            f.write(json.dumps(entry) + "\n")

        # Update audit log
        self.audit_logger.log_detailed_activity(
            agent_name="evaluator_coordinator",
            activity_type="AGENT_EVALUATION",
            description=f"Evaluated {evaluation.agent_name}: {evaluation.total_score:.1f}/10",
            details={
                "agent_name": evaluation.agent_name,
                "total_score": evaluation.total_score,
                "passed": evaluation.passed,
                "weak_areas": evaluation.weak_characteristics
            }
        )

    def handle_low_performance(self, evaluation: AgentEvaluation):
        """Handle agent with low performance score (<6.0)"""
        print(f"\n🚨 LOW PERFORMANCE ALERT: {evaluation.agent_name}")
        print(f"   Score: {evaluation.total_score:.1f}/10")
        print(f"   Weak areas: {', '.join(evaluation.weak_characteristics)}")

        # Notify via communication bus
        self.comm_bus.broadcast_message(
            sender_agent="EvaluatorCoordinator",
            message_type=MessageType.NOTIFICATION,
            priority=MessagePriority.HIGH,
            subject="Low Performance Alert",
            content={
                "evaluation_id": evaluation.evaluation_id,
                "agent_name": evaluation.agent_name,
                "score": evaluation.total_score,
                "weak_areas": evaluation.weak_characteristics,
                "suggestions": evaluation.improvement_suggestions,
                "action": "retraining_scheduled"
            }
        )

        # Trigger retraining (will be implemented in phase 4)
        self.retraining_triggered_count += 1

        # Log
        print(f"   → Retraining scheduled\n")

    def get_agent_evaluation_history(self, agent_name: str, limit: int = 100) -> List[Dict]:
        """Get recent evaluations for an agent"""
        evaluations = []

        if not self.evaluations_file.exists():
            return evaluations

        try:
            with open(self.evaluations_file, 'r') as f:
                for line in f:
                    entry = json.loads(line)
                    if entry.get("agent_name") == agent_name:
                        evaluations.append(entry)
                        if len(evaluations) >= limit:
                            break
        except Exception as e:
            print(f"Error reading evaluations: {e}")

        return list(reversed(evaluations))  # Return newest first

    def get_evaluation_summary(self) -> Dict:
        """Get overall evaluation statistics"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_evaluations": self.evaluations_completed,
            "low_performance_count": self.low_performance_count,
            "retraining_triggered": self.retraining_triggered_count,
            "pass_rate": (1 - self.low_performance_count / max(1, self.evaluations_completed)) * 100,
            "average_score": 0.0
        }

        # Calculate average score from all evaluations
        if self.evaluations_file.exists():
            scores = []
            try:
                with open(self.evaluations_file, 'r') as f:
                    for line in f:
                        entry = json.loads(line)
                        scores.append(entry.get("total_score", 0))

                if scores:
                    summary["average_score"] = sum(scores) / len(scores)
            except Exception as e:
                print(f"Error calculating summary: {e}")

        return summary

    def print_evaluation_dashboard(self):
        """Print evaluation dashboard"""
        summary = self.get_evaluation_summary()

        print("\n" + "=" * 100)
        print("📊 AGENT EVALUATION DASHBOARD")
        print("=" * 100 + "\n")

        print(f"Total Evaluations: {summary['total_evaluations']}")
        print(f"Pass Rate: {summary['pass_rate']:.1f}%")
        print(f"Low Performance: {summary['low_performance_count']}")
        print(f"Retraining Triggered: {summary['retraining_triggered']}")
        print(f"Average Score: {summary['average_score']:.2f}/10.0")

        print("\n" + "=" * 100 + "\n")


# Global instance
_coordinator = None

def get_evaluator_coordinator() -> AgentEvaluatorCoordinator:
    """Get or create global evaluator coordinator instance"""
    global _coordinator
    if _coordinator is None:
        _coordinator = AgentEvaluatorCoordinator()
    return _coordinator


def trigger_evaluation(agent_name: str, agent_type: str, task_id: str, task_name: str,
                     success: bool, actual_duration: float, estimated_duration: float,
                     output: str = "", error_message: str = ""):
    """
    Trigger evaluation of an agent after task completion
    Called from live_task_monitor.py
    """
    coordinator = get_evaluator_coordinator()

    request = EvaluationRequest(
        request_id=str(uuid.uuid4())[:8],
        agent_name=agent_name,
        agent_type=agent_type,
        task_id=task_id,
        task_name=task_name,
        success=success,
        actual_duration_seconds=actual_duration,
        estimated_duration_seconds=estimated_duration,
        output=output,
        error_message=error_message
    )

    # Run evaluation asynchronously
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Create task to run evaluation
    eval_task = asyncio.create_task(coordinator.evaluate_agent(request))

    # Handle completion
    def on_evaluation_complete(future):
        try:
            evaluation = future.result()
            if evaluation:
                if not evaluation.passed:
                    coordinator.handle_low_performance(evaluation)
        except Exception as e:
            print(f"Evaluation error: {e}")

    eval_task.add_done_callback(on_evaluation_complete)

    return eval_task


# Example usage
if __name__ == "__main__":
    coordinator = get_evaluator_coordinator()
    coordinator.print_evaluation_dashboard()
