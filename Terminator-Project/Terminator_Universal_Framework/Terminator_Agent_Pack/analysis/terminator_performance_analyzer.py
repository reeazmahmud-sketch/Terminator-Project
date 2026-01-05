# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Performance Analyzer - Continuous Performance Metrics and Optimization
=============================================================================

Analyzes system performance metrics, identifies bottlenecks, detects root causes,
generates optimization rules, and suggests improvements.

Features:
- Performance metric tracking (latency, throughput, success rates)
- Root cause analysis for failures and slowdowns
- Trend detection and anomaly identification
- Automatic optimization rule generation
- Performance visualization and reporting
- Comparative analysis across models, tools, and task types

Created: December 11, 2025
Part of: TERMINATOR Enhancement Roadmap - Tier 1 (Foundation)
"""

import json
import os
import threading
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from statistics import mean, stdev, median


# ============================================================================
# Data Structures
# ============================================================================

class PerformanceMetric(Enum):
    """Types of performance metrics"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    SUCCESS_RATE = "success_rate"
    ERROR_RATE = "error_rate"
    RESOURCE_USAGE = "resource_usage"
    CACHE_HIT_RATE = "cache_hit_rate"


class TrendType(Enum):
    """Direction of performance trends"""
    IMPROVING = "improving"
    STABLE = "stable"
    DEGRADING = "degrading"


@dataclass
class PerformanceDataPoint:
    """Single performance measurement"""
    metric_type: PerformanceMetric
    value: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    context: Dict[str, Any] = field(default_factory=dict)  # model, task_type, tool, etc.

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['metric_type'] = self.metric_type.value
        return data


@dataclass
class PerformanceAnalysis:
    """Analysis of performance data"""
    metric_type: PerformanceMetric
    current_value: float
    average_value: float
    min_value: float
    max_value: float
    std_deviation: float
    trend: TrendType
    change_percentage: float
    data_points: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class OptimizationRule:
    """An optimization rule generated from analysis"""
    rule_id: str
    title: str
    description: str
    affected_metric: PerformanceMetric
    expected_improvement: float  # 0.0-1.0 (percentage improvement)
    confidence: float  # 0.0-1.0 (confidence in rule)
    rule_type: str  # "model_selection", "tool_choice", "resource_allocation", etc.
    conditions: Dict[str, Any]  # When this rule applies
    actions: List[str]  # What to do
    priority: int  # 1-5 (5 being highest)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


# ============================================================================
# Performance Analyzer
# ============================================================================

class PerformanceAnalyzer:
    """Core performance analysis engine"""

    def __init__(self, storage_path: str = None):
        """Initialize performance analyzer"""
        if storage_path is None:
            storage_path = "/Users/reeazmahmud/Desktop/Terminator/performance/data"

        self.storage_path = storage_path
        self.data_file = os.path.join(storage_path, "performance_data.json")
        self.analysis_file = os.path.join(storage_path, "performance_analysis.json")
        os.makedirs(storage_path, exist_ok=True)

        self.data_points: List[PerformanceDataPoint] = []
        self.analyses: Dict[str, PerformanceAnalysis] = {}
        self._load_data()

    def _load_data(self) -> None:
        """Load performance data from disk"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    for item in data:
                        item['metric_type'] = PerformanceMetric(item['metric_type'])
                        self.data_points.append(PerformanceDataPoint(**item))
            except Exception as e:
                print(f"Error loading performance data: {e}")

    def _save_data(self) -> None:
        """Save performance data to disk"""
        try:
            data_dicts = [d.to_dict() for d in self.data_points]
            with open(self.data_file, 'w') as f:
                json.dump(data_dicts, f, indent=2)
        except Exception as e:
            print(f"Error saving performance data: {e}")

    def record_metric(
        self,
        metric_type: PerformanceMetric,
        value: float,
        context: Dict[str, Any] = None
    ) -> None:
        """Record a performance metric"""
        datapoint = PerformanceDataPoint(
            metric_type=metric_type,
            value=value,
            context=context or {}
        )
        self.data_points.append(datapoint)

        # Keep only last 5000 data points to manage memory
        if len(self.data_points) > 5000:
            self.data_points = self.data_points[-5000:]

        self._save_data()

    def get_recent_metrics(
        self,
        metric_type: PerformanceMetric = None,
        hours: int = 24
    ) -> List[PerformanceDataPoint]:
        """Get metrics from the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        filtered = [
            d for d in self.data_points
            if datetime.fromisoformat(d.timestamp) > cutoff_time
            and (metric_type is None or d.metric_type == metric_type)
        ]

        return filtered

    def analyze_metric(
        self,
        metric_type: PerformanceMetric,
        hours: int = 24
    ) -> PerformanceAnalysis:
        """Analyze a specific metric"""
        metrics = self.get_recent_metrics(metric_type, hours)

        if not metrics:
            return PerformanceAnalysis(
                metric_type=metric_type,
                current_value=0.0,
                average_value=0.0,
                min_value=0.0,
                max_value=0.0,
                std_deviation=0.0,
                trend=TrendType.STABLE,
                change_percentage=0.0,
                data_points=0
            )

        values = [m.value for m in metrics]
        current = values[-1]
        avg = mean(values)
        minimum = min(values)
        maximum = max(values)
        std_dev = stdev(values) if len(values) > 1 else 0.0

        # Calculate trend
        if len(values) > 10:
            first_half_avg = mean(values[:len(values)//2])
            second_half_avg = mean(values[len(values)//2:])
            change = ((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg != 0 else 0
        else:
            change = 0.0

        if change > 5:
            trend = TrendType.DEGRADING
        elif change < -5:
            trend = TrendType.IMPROVING
        else:
            trend = TrendType.STABLE

        analysis = PerformanceAnalysis(
            metric_type=metric_type,
            current_value=current,
            average_value=avg,
            min_value=minimum,
            max_value=maximum,
            std_deviation=std_dev,
            trend=trend,
            change_percentage=change,
            data_points=len(metrics)
        )

        self.analyses[metric_type.value] = analysis
        return analysis

    def compare_contexts(
        self,
        metric_type: PerformanceMetric,
        context_key: str,
        hours: int = 24
    ) -> Dict[str, float]:
        """Compare metric values across different contexts"""
        metrics = self.get_recent_metrics(metric_type, hours)

        # Group by context
        context_groups: Dict[str, List[float]] = {}
        for metric in metrics:
            context_value = metric.context.get(context_key)
            if context_value:
                if context_value not in context_groups:
                    context_groups[context_value] = []
                context_groups[context_value].append(metric.value)

        # Calculate averages
        comparison = {
            context: mean(values)
            for context, values in context_groups.items()
        }

        return sorted(comparison.items(), key=lambda x: x[1], reverse=True)

    def get_analysis_report(self) -> Dict[str, Any]:
        """Get comprehensive performance analysis report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_metrics": len(self.data_points),
            "metrics": {}
        }

        for metric_type in PerformanceMetric:
            analysis = self.analyze_metric(metric_type)
            report["metrics"][metric_type.value] = {
                "current": analysis.current_value,
                "average": analysis.average_value,
                "min": analysis.min_value,
                "max": analysis.max_value,
                "std_dev": analysis.std_deviation,
                "trend": analysis.trend.value,
                "change_pct": analysis.change_percentage,
                "data_points": analysis.data_points
            }

        return report


# ============================================================================
# Root Cause Detector
# ============================================================================

class RootCauseDetector:
    """Detects root causes of performance issues"""

    def __init__(self, analyzer: PerformanceAnalyzer):
        """Initialize root cause detector"""
        self.analyzer = analyzer

    def detect_latency_issues(self) -> List[Dict[str, Any]]:
        """Detect causes of high latency"""
        issues = []

        # Get latency analysis
        latency_analysis = self.analyzer.analyze_metric(PerformanceMetric.LATENCY)

        if latency_analysis.current_value > latency_analysis.average_value * 1.5:
            # Current latency is 50% higher than average
            issues.append({
                "issue": "High latency detected",
                "current": latency_analysis.current_value,
                "average": latency_analysis.average_value,
                "severity": "HIGH" if latency_analysis.current_value > latency_analysis.average_value * 2 else "MEDIUM",
                "possible_causes": [
                    "Model processing delay",
                    "Tool execution slowdown",
                    "Network latency",
                    "Resource contention"
                ]
            })

        return issues

    def detect_success_rate_issues(self) -> List[Dict[str, Any]]:
        """Detect causes of low success rates"""
        issues = []

        # Get success rate analysis
        success_analysis = self.analyzer.analyze_metric(PerformanceMetric.SUCCESS_RATE)

        if success_analysis.current_value < 0.9:
            # Less than 90% success rate
            issues.append({
                "issue": "Low success rate",
                "current": success_analysis.current_value,
                "target": 0.95,
                "severity": "HIGH" if success_analysis.current_value < 0.8 else "MEDIUM",
                "possible_causes": [
                    "Tool integration failures",
                    "Model selection mismatch",
                    "Resource availability issues",
                    "Invalid user input handling"
                ]
            })

        return issues

    def detect_resource_issues(self) -> List[Dict[str, Any]]:
        """Detect resource utilization issues"""
        issues = []

        # Get resource analysis
        resource_analysis = self.analyzer.analyze_metric(PerformanceMetric.RESOURCE_USAGE)

        if resource_analysis.current_value > 0.85:
            # Resource usage above 85%
            issues.append({
                "issue": "High resource utilization",
                "current": resource_analysis.current_value,
                "threshold": 0.85,
                "severity": "MEDIUM",
                "possible_causes": [
                    "Too many concurrent tasks",
                    "Memory leaks",
                    "Inefficient algorithms",
                    "Cache misses"
                ]
            })

        return issues

    def detect_trend_issues(self) -> List[Dict[str, Any]]:
        """Detect degrading trends"""
        issues = []

        for metric_type in PerformanceMetric:
            analysis = self.analyzer.analyze_metric(metric_type)

            if analysis.trend == TrendType.DEGRADING and analysis.change_percentage > 10:
                issues.append({
                    "issue": f"Degrading {metric_type.value} trend",
                    "metric": metric_type.value,
                    "change_pct": analysis.change_percentage,
                    "severity": "MEDIUM" if analysis.change_percentage < 25 else "HIGH",
                    "trend": "degrading"
                })

        return issues

    def get_all_issues(self) -> List[Dict[str, Any]]:
        """Get all detected issues"""
        all_issues = []
        all_issues.extend(self.detect_latency_issues())
        all_issues.extend(self.detect_success_rate_issues())
        all_issues.extend(self.detect_resource_issues())
        all_issues.extend(self.detect_trend_issues())
        return all_issues


# ============================================================================
# Optimization Rule Generator
# ============================================================================

class OptimizationRuleGenerator:
    """Generates optimization rules based on analysis"""

    def __init__(self, analyzer: PerformanceAnalyzer):
        """Initialize rule generator"""
        self.analyzer = analyzer
        self.rules: List[OptimizationRule] = []
        self.rule_counter = 0

    def _generate_rule_id(self) -> str:
        """Generate unique rule ID"""
        self.rule_counter += 1
        return f"rule_{self.rule_counter:04d}"

    def generate_rules(self) -> List[OptimizationRule]:
        """Generate optimization rules from current analysis"""
        self.rules = []

        # Analyze each metric
        for metric_type in PerformanceMetric:
            analysis = self.analyzer.analyze_metric(metric_type)

            if analysis.data_points == 0:
                continue

            # Generate rules based on metric type
            if metric_type == PerformanceMetric.LATENCY:
                self._generate_latency_rules(analysis)
            elif metric_type == PerformanceMetric.SUCCESS_RATE:
                self._generate_success_rules(analysis)
            elif metric_type == PerformanceMetric.RESOURCE_USAGE:
                self._generate_resource_rules(analysis)

        # Sort by priority
        self.rules.sort(key=lambda r: r.priority, reverse=True)
        return self.rules

    def _generate_latency_rules(self, analysis: PerformanceAnalysis) -> None:
        """Generate latency improvement rules"""
        if analysis.current_value > analysis.average_value * 1.5:
            rule = OptimizationRule(
                rule_id=self._generate_rule_id(),
                title="Reduce Model Latency",
                description="Current latency is 50%+ above average",
                affected_metric=PerformanceMetric.LATENCY,
                expected_improvement=0.15,  # 15% improvement expected
                confidence=0.8,
                rule_type="model_selection",
                conditions={"latency_spike": True},
                actions=[
                    "Switch to faster model for tasks",
                    "Implement response caching",
                    "Reduce model context size"
                ],
                priority=4
            )
            self.rules.append(rule)

    def _generate_success_rules(self, analysis: PerformanceAnalysis) -> None:
        """Generate success rate improvement rules"""
        if analysis.current_value < 0.9:
            rule = OptimizationRule(
                rule_id=self._generate_rule_id(),
                title="Improve Success Rate",
                description=f"Success rate is {analysis.current_value:.0%}, target is 95%",
                affected_metric=PerformanceMetric.SUCCESS_RATE,
                expected_improvement=0.08,  # 8% improvement
                confidence=0.75,
                rule_type="tool_choice",
                conditions={"low_success": True},
                actions=[
                    "Review failed task patterns",
                    "Implement input validation",
                    "Use more reliable tool combinations"
                ],
                priority=5
            )
            self.rules.append(rule)

    def _generate_resource_rules(self, analysis: PerformanceAnalysis) -> None:
        """Generate resource optimization rules"""
        if analysis.current_value > 0.8:
            rule = OptimizationRule(
                rule_id=self._generate_rule_id(),
                title="Optimize Resource Usage",
                description=f"Resource usage at {analysis.current_value:.0%}, optimize to reduce",
                affected_metric=PerformanceMetric.RESOURCE_USAGE,
                expected_improvement=0.12,  # 12% improvement
                confidence=0.7,
                rule_type="resource_allocation",
                conditions={"high_resource_usage": True},
                actions=[
                    "Implement task queuing",
                    "Add caching layer",
                    "Optimize data structures",
                    "Reduce parallel task count"
                ],
                priority=3
            )
            self.rules.append(rule)

    def get_top_rules(self, count: int = 5) -> List[OptimizationRule]:
        """Get top N optimization rules"""
        return self.rules[:count]


# ============================================================================
# Metrics Visualizer
# ============================================================================

class MetricsVisualizer:
    """Creates visualization and reporting of metrics"""

    @staticmethod
    def create_summary_report(analyzer: PerformanceAnalyzer) -> Dict[str, Any]:
        """Create a comprehensive metrics summary report"""
        detector = RootCauseDetector(analyzer)
        generator = OptimizationRuleGenerator(analyzer)

        return {
            "timestamp": datetime.now().isoformat(),
            "analysis": analyzer.get_analysis_report(),
            "issues_detected": detector.get_all_issues(),
            "optimization_rules": [
                {
                    "id": rule.rule_id,
                    "title": rule.title,
                    "description": rule.description,
                    "expected_improvement": rule.expected_improvement,
                    "confidence": rule.confidence,
                    "priority": rule.priority,
                    "actions": rule.actions
                }
                for rule in generator.generate_rules()
            ]
        }

    @staticmethod
    def create_metric_summary(analysis: PerformanceAnalysis) -> str:
        """Create human-readable metric summary"""
        return f"""
╔════════════════════════════════════════════╗
║ Performance Metric: {analysis.metric_type.value.upper()}
╠════════════════════════════════════════════╣
║ Current:         {analysis.current_value:>8.2f}
║ Average:         {analysis.average_value:>8.2f}
║ Min/Max:         {analysis.min_value:>6.2f} / {analysis.max_value:>6.2f}
║ Std Dev:         {analysis.std_deviation:>8.2f}
║ Trend:           {analysis.trend.value:>8s}
║ Change:          {analysis.change_percentage:>7.1f}%
║ Data Points:     {analysis.data_points:>8d}
╚════════════════════════════════════════════╝
"""


# ============================================================================
# Main Performance Analyzer System
# ============================================================================

class TerminatorPerformanceAnalyzer:
    """
    Main performance analysis system that tracks metrics, detects issues,
    and generates optimization rules.
    """

    _instance: Optional['TerminatorPerformanceAnalyzer'] = None
    _lock = threading.Lock()

    def __init__(self, check_interval: int = 300):
        """
        Initialize performance analyzer

        Args:
            check_interval: How often to update analysis (seconds)
        """
        self.check_interval = check_interval
        self.analyzer = PerformanceAnalyzer()
        self.detector = RootCauseDetector(self.analyzer)
        self.generator = OptimizationRuleGenerator(self.analyzer)

        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.report_file = "/Users/reeazmahmud/Desktop/Terminator/performance/data/performance_report.json"

        os.makedirs(os.path.dirname(self.report_file), exist_ok=True)

    @classmethod
    def get_instance(cls) -> 'TerminatorPerformanceAnalyzer':
        """Get singleton instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def start_monitoring(self) -> None:
        """Start the performance monitoring thread"""
        if self.monitoring:
            print("Performance analyzer already monitoring")
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        print("✅ Performance analyzer started monitoring")

    def stop_monitoring(self) -> None:
        """Stop the performance monitoring thread"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("⛔ Performance analyzer stopped")

    def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self._update_report()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"Error in performance monitoring: {e}")
                time.sleep(self.check_interval)

    def _update_report(self) -> None:
        """Update and save performance report"""
        try:
            report = MetricsVisualizer.create_summary_report(self.analyzer)
            with open(self.report_file, 'w') as f:
                json.dump(report, f, indent=2)
        except Exception as e:
            print(f"Error updating performance report: {e}")

    def record_metric(
        self,
        metric_type: PerformanceMetric,
        value: float,
        context: Dict[str, Any] = None
    ) -> None:
        """Record a performance metric"""
        self.analyzer.record_metric(metric_type, value, context)

    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        return MetricsVisualizer.create_summary_report(self.analyzer)

    def get_issues(self) -> List[Dict[str, Any]]:
        """Get detected performance issues"""
        return self.detector.get_all_issues()

    def get_recommendations(self) -> List[Dict[str, Any]]:
        """Get optimization recommendations"""
        rules = self.generator.generate_rules()
        return [
            {
                "title": rule.title,
                "description": rule.description,
                "expected_improvement": f"{rule.expected_improvement:.0%}",
                "confidence": f"{rule.confidence:.0%}",
                "priority": rule.priority,
                "actions": rule.actions
            }
            for rule in rules
        ]

    def get_metric_comparison(
        self,
        metric_type: PerformanceMetric,
        context_key: str
    ) -> List[Tuple[str, float]]:
        """Compare metric across contexts"""
        return self.analyzer.compare_contexts(metric_type, context_key)


# ============================================================================
# Module-level access functions
# ============================================================================

def get_performance_analyzer() -> TerminatorPerformanceAnalyzer:
    """Get the performance analyzer instance"""
    return TerminatorPerformanceAnalyzer.get_instance()


def record_performance_metric(
    metric_type: PerformanceMetric,
    value: float,
    context: Dict[str, Any] = None
) -> None:
    """Convenience function to record a performance metric"""
    analyzer = get_performance_analyzer()
    analyzer.record_metric(metric_type, value, context)


if __name__ == "__main__":
    # Test the performance analyzer
    analyzer = get_performance_analyzer()

    # Record some sample metrics
    record_performance_metric(PerformanceMetric.LATENCY, 1250.5, {"model": "claude-3-sonnet", "task": "search"})
    record_performance_metric(PerformanceMetric.SUCCESS_RATE, 0.95, {"task": "analysis"})
    record_performance_metric(PerformanceMetric.RESOURCE_USAGE, 0.65, {"hour": "peak"})

    # Get report
    print("\n=== Performance Report ===")
    print(json.dumps(analyzer.get_performance_report(), indent=2))

    print("\n=== Issues Detected ===")
    print(json.dumps(analyzer.get_issues(), indent=2))

    print("\n=== Recommendations ===")
    print(json.dumps(analyzer.get_recommendations(), indent=2))
