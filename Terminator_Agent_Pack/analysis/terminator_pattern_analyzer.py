# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Pattern Analyzer - Behavioral Pattern Detection and Analysis
==================================================================

Detects patterns in user behavior, system performance, and task execution.
Identifies trends, anomalies, and recurrent patterns.

Features:
- Pattern detection across multiple dimensions
- Trend analysis (improving, degrading, stable)
- Anomaly detection
- Behavioral clustering
- Seasonal pattern recognition
- Predictive insights from patterns

Created: December 11, 2025
Part of: TERMINATOR Enhancement Roadmap - Tier 3 (Proactivity)
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import defaultdict
from statistics import mean, stdev, median


# ============================================================================
# Data Structures
# ============================================================================

class TrendDirection(Enum):
    """Direction of trend"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    CYCLICAL = "cyclical"


class AnomalyType(Enum):
    """Type of anomaly"""
    STATISTICAL_OUTLIER = "statistical_outlier"
    BEHAVIORAL_CHANGE = "behavioral_change"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    UNUSUAL_SEQUENCE = "unusual_sequence"


@dataclass
class Pattern:
    """A detected pattern"""
    pattern_id: str
    pattern_type: str  # "behavior", "performance", "temporal", etc.
    description: str
    frequency: int  # How many times observed
    confidence: float  # 0.0-1.0
    examples: List[Any] = field(default_factory=list)
    first_observed: str = field(default_factory=lambda: datetime.now().isoformat())
    last_observed: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Trend:
    """A detected trend"""
    metric_name: str
    direction: TrendDirection
    magnitude: float  # How strong the trend
    duration_days: int
    start_value: float
    end_value: float
    confidence: float  # 0.0-1.0
    projection: Optional[float] = None  # Projected future value


@dataclass
class Anomaly:
    """A detected anomaly"""
    anomaly_id: str
    anomaly_type: AnomalyType
    severity: int  # 1-5
    description: str
    value: Any
    expected_value: Optional[Any] = None
    deviation_percent: Optional[float] = None
    detected_at: str = field(default_factory=lambda: datetime.now().isoformat())
    resolved: bool = False


# ============================================================================
# Pattern Detector
# ============================================================================

class PatternDetector:
    """Detects patterns in data"""

    def __init__(self):
        """Initialize pattern detector"""
        self.patterns: Dict[str, Pattern] = {}
        self.pattern_counter = 0
        self.data_history: List[Tuple[str, Any, datetime]] = []

    def record_data(self, category: str, value: Any, timestamp: str = None) -> None:
        """Record data point"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        dt = datetime.fromisoformat(timestamp)
        self.data_history.append((category, value, dt))

        # Keep last 1000 data points
        if len(self.data_history) > 1000:
            self.data_history = self.data_history[-1000:]

    def detect_patterns(self) -> List[Pattern]:
        """Detect all patterns in current data"""
        if len(self.data_history) < 3:
            return []

        patterns = []

        # Detect recurring sequences
        patterns.extend(self._detect_recurring_patterns())

        # Detect repeated values
        patterns.extend(self._detect_frequent_values())

        # Detect temporal patterns
        patterns.extend(self._detect_temporal_patterns())

        return patterns

    def _detect_recurring_patterns(self) -> List[Pattern]:
        """Detect sequences that repeat"""
        patterns = []

        # Look for repeating 3-sequences
        sequence_counts = defaultdict(int)

        for i in range(len(self.data_history) - 2):
            sequence = tuple(self.data_history[i:i+3])
            category_seq = "-".join([s[0] for s in sequence])
            sequence_counts[category_seq] += 1

        # Create patterns for frequent sequences
        for seq_key, count in sequence_counts.items():
            if count >= 2:  # At least 2 occurrences
                self.pattern_counter += 1
                pattern = Pattern(
                    pattern_id=f"pattern_{self.pattern_counter:04d}",
                    pattern_type="recurring_sequence",
                    description=f"Sequence: {seq_key}",
                    frequency=count,
                    confidence=min(count / 10, 1.0)
                )
                patterns.append(pattern)

        return patterns

    def _detect_frequent_values(self) -> List[Pattern]:
        """Detect frequently occurring values"""
        patterns = []

        # Count values by category
        category_values = defaultdict(list)
        for category, value, _ in self.data_history:
            category_values[category].append(value)

        # Find frequent values
        for category, values in category_values.items():
            value_counts = defaultdict(int)
            for v in values:
                if isinstance(v, (str, int)):
                    value_counts[v] += 1

            for value, count in value_counts.items():
                if count >= 3:
                    self.pattern_counter += 1
                    pattern = Pattern(
                        pattern_id=f"pattern_{self.pattern_counter:04d}",
                        pattern_type="frequent_value",
                        description=f"{category} frequently has value {value}",
                        frequency=count,
                        confidence=min(count / 15, 1.0),
                        examples=[value]
                    )
                    patterns.append(pattern)

        return patterns

    def _detect_temporal_patterns(self) -> List[Pattern]:
        """Detect time-based patterns"""
        patterns = []

        # Group by hour and day
        hourly_distribution = defaultdict(list)
        daily_distribution = defaultdict(list)

        for category, value, dt in self.data_history:
            hour = dt.hour
            day = dt.weekday()

            hourly_distribution[hour].append((category, value))
            daily_distribution[day].append((category, value))

        # Detect regular hourly activity
        for hour, activities in hourly_distribution.items():
            if len(activities) >= 3:
                self.pattern_counter += 1
                pattern = Pattern(
                    pattern_id=f"pattern_{self.pattern_counter:04d}",
                    pattern_type="temporal_hourly",
                    description=f"Activity regularly occurs at hour {hour}",
                    frequency=len(activities),
                    confidence=0.7
                )
                patterns.append(pattern)

        return patterns


# ============================================================================
# Trend Analyzer
# ============================================================================

class TrendAnalyzer:
    """Analyzes trends in metrics"""

    def __init__(self):
        """Initialize trend analyzer"""
        self.metrics: Dict[str, List[Tuple[float, str]]] = defaultdict(list)

    def record_metric(self, metric_name: str, value: float, timestamp: str = None) -> None:
        """Record a metric value"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        self.metrics[metric_name].append((value, timestamp))

        # Keep last 500 values per metric
        if len(self.metrics[metric_name]) > 500:
            self.metrics[metric_name] = self.metrics[metric_name][-500:]

    def analyze_trend(self, metric_name: str, window_days: int = 7) -> Optional[Trend]:
        """Analyze trend in a metric"""
        if metric_name not in self.metrics or len(self.metrics[metric_name]) < 2:
            return None

        values_with_time = self.metrics[metric_name]

        # Filter to window
        cutoff = datetime.now() - timedelta(days=window_days)
        filtered = [
            (v, dt) for v, dt in values_with_time
            if datetime.fromisoformat(dt) > cutoff
        ]

        if len(filtered) < 2:
            return None

        values = [v for v, _ in filtered]
        timestamps = [datetime.fromisoformat(dt) for _, dt in filtered]

        # Calculate trend
        start_value = values[0]
        end_value = values[-1]
        change_percent = ((end_value - start_value) / start_value * 100) if start_value != 0 else 0

        # Determine direction
        if change_percent > 10:
            direction = TrendDirection.INCREASING
            magnitude = change_percent / 100
        elif change_percent < -10:
            direction = TrendDirection.DECREASING
            magnitude = abs(change_percent) / 100
        else:
            direction = TrendDirection.STABLE
            magnitude = 0.0

        # Project future value
        if len(values) > 2:
            recent_values = values[-5:]  # Last 5 values
            avg_change = (recent_values[-1] - recent_values[0]) / len(recent_values) if recent_values else 0
            projection = end_value + avg_change
        else:
            projection = None

        duration = (timestamps[-1] - timestamps[0]).days

        trend = Trend(
            metric_name=metric_name,
            direction=direction,
            magnitude=magnitude,
            duration_days=max(duration, 1),
            start_value=start_value,
            end_value=end_value,
            confidence=min(len(values) / 50, 1.0),
            projection=projection
        )

        return trend

    def get_all_trends(self) -> Dict[str, Trend]:
        """Get trends for all metrics"""
        trends = {}

        for metric_name in self.metrics.keys():
            trend = self.analyze_trend(metric_name)
            if trend:
                trends[metric_name] = trend

        return trends


# ============================================================================
# Anomaly Detector
# ============================================================================

class AnomalyDetector:
    """Detects anomalies in data"""

    _anomaly_counter = 0

    def __init__(self):
        """Initialize anomaly detector"""
        self.anomalies: List[Anomaly] = []

    def detect_statistical_outliers(
        self,
        metric_name: str,
        values: List[float],
        threshold_stdev: float = 2.0
    ) -> List[Anomaly]:
        """Detect statistical outliers"""
        detected = []

        if len(values) < 3:
            return detected

        avg = mean(values)
        std = stdev(values)

        for value in values:
            z_score = abs(value - avg) / std if std > 0 else 0

            if z_score > threshold_stdev:
                AnomalyDetector._anomaly_counter += 1
                anomaly = Anomaly(
                    anomaly_id=f"anomaly_{AnomalyDetector._anomaly_counter:06d}",
                    anomaly_type=AnomalyType.STATISTICAL_OUTLIER,
                    severity=min(int(z_score), 5),
                    description=f"{metric_name} value {value} is {z_score:.1f} std devs from mean",
                    value=value,
                    expected_value=avg,
                    deviation_percent=((value - avg) / avg * 100) if avg != 0 else 0
                )
                detected.append(anomaly)

        return detected

    def detect_behavioral_changes(
        self,
        values: List[float],
        sensitivity: float = 0.3  # 0.0-1.0
    ) -> List[Anomaly]:
        """Detect sudden behavioral changes"""
        detected = []

        if len(values) < 3:
            return detected

        # Compare consecutive pairs
        for i in range(1, len(values)):
            prev_avg = mean(values[max(0, i-5):i])
            curr_value = values[i]

            change_percent = abs(curr_value - prev_avg) / prev_avg if prev_avg != 0 else 0

            threshold = 0.5 * sensitivity

            if change_percent > threshold:
                AnomalyDetector._anomaly_counter += 1
                anomaly = Anomaly(
                    anomaly_id=f"anomaly_{AnomalyDetector._anomaly_counter:06d}",
                    anomaly_type=AnomalyType.BEHAVIORAL_CHANGE,
                    severity=min(int(change_percent * 5), 5),
                    description=f"Value changed by {change_percent*100:.0f}%",
                    value=curr_value,
                    expected_value=prev_avg,
                    deviation_percent=change_percent * 100
                )
                detected.append(anomaly)

        return detected

    def resolve_anomaly(self, anomaly_id: str) -> None:
        """Mark anomaly as resolved"""
        for anomaly in self.anomalies:
            if anomaly.anomaly_id == anomaly_id:
                anomaly.resolved = True
                break


# ============================================================================
# Sequence Analyzer
# ============================================================================

class SequenceAnalyzer:
    """Analyzes sequences of events"""

    def __init__(self):
        """Initialize sequence analyzer"""
        self.sequences: List[List[str]] = []
        self.sequence_patterns: Dict[str, int] = defaultdict(int)

    def record_sequence(self, events: List[str]) -> None:
        """Record a sequence of events"""
        self.sequences.append(events)

        # Track sequence patterns
        for i in range(len(events) - 1):
            pair = f"{events[i]} -> {events[i+1]}"
            self.sequence_patterns[pair] += 1

    def find_common_sequences(self, min_length: int = 2) -> Dict[str, int]:
        """Find commonly occurring sequences"""
        common = {}

        for seq_key, count in self.sequence_patterns.items():
            if count >= 2:  # At least 2 occurrences
                common[seq_key] = count

        return dict(sorted(common.items(), key=lambda x: x[1], reverse=True))

    def find_sequence_after_event(self, event: str) -> List[Tuple[str, float]]:
        """Find what events typically follow another event"""
        following = defaultdict(int)

        for pair, count in self.sequence_patterns.items():
            if pair.startswith(f"{event} ->"):
                next_event = pair.split(" -> ")[1]
                following[next_event] += count

        total = sum(following.values())

        result = [
            (event, count / total)
            for event, count in following.items()
        ]

        return sorted(result, key=lambda x: x[1], reverse=True)


# ============================================================================
# Main Pattern Analyzer
# ============================================================================

class TerminatorPatternAnalyzer:
    """
    Main pattern analyzer that detects patterns, trends, anomalies
    and provides insights for prediction and optimization.
    """

    _instance: Optional['TerminatorPatternAnalyzer'] = None
    _lock = __import__('threading').Lock()

    def __init__(self):
        """Initialize pattern analyzer"""
        self.pattern_detector = PatternDetector()
        self.trend_analyzer = TrendAnalyzer()
        self.anomaly_detector = AnomalyDetector()
        self.sequence_analyzer = SequenceAnalyzer()

        self.storage_path = "/Users/reeazmahmud/Desktop/Terminator/patterns/data"
        os.makedirs(self.storage_path, exist_ok=True)

    @classmethod
    def get_instance(cls) -> 'TerminatorPatternAnalyzer':
        """Get singleton instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def analyze(self) -> Dict[str, Any]:
        """Perform comprehensive pattern analysis"""
        return {
            "patterns": self._get_patterns_summary(),
            "trends": self._get_trends_summary(),
            "anomalies": self._get_anomalies_summary(),
            "sequences": self.sequence_analyzer.find_common_sequences()
        }

    def _get_patterns_summary(self) -> List[Dict[str, Any]]:
        """Get summary of detected patterns"""
        patterns = self.pattern_detector.detect_patterns()
        return [
            {
                "pattern_id": p.pattern_id,
                "type": p.pattern_type,
                "description": p.description,
                "frequency": p.frequency,
                "confidence": p.confidence
            }
            for p in patterns
        ]

    def _get_trends_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary of detected trends"""
        trends = self.trend_analyzer.get_all_trends()
        return {
            name: {
                "direction": trend.direction.value,
                "magnitude": trend.magnitude,
                "duration_days": trend.duration_days,
                "projection": trend.projection
            }
            for name, trend in trends.items()
        }

    def _get_anomalies_summary(self) -> List[Dict[str, Any]]:
        """Get summary of detected anomalies"""
        return [
            {
                "anomaly_id": a.anomaly_id,
                "type": a.anomaly_type.value,
                "severity": a.severity,
                "description": a.description,
                "resolved": a.resolved
            }
            for a in self.anomaly_detector.anomalies
        ]

    def record_data_point(self, category: str, value: Any) -> None:
        """Record a data point for analysis"""
        self.pattern_detector.record_data(category, value)

    def record_metric(self, metric_name: str, value: float) -> None:
        """Record a metric for trend analysis"""
        self.trend_analyzer.record_metric(metric_name, value)

    def record_sequence(self, events: List[str]) -> None:
        """Record a sequence of events"""
        self.sequence_analyzer.record_sequence(events)

    def detect_anomalies(
        self,
        metric_name: str,
        values: List[float]
    ) -> List[Anomaly]:
        """Detect anomalies in metric values"""
        anomalies = self.anomaly_detector.detect_statistical_outliers(metric_name, values)
        anomalies.extend(self.anomaly_detector.detect_behavioral_changes(values))
        self.anomaly_detector.anomalies.extend(anomalies)
        return anomalies


# ============================================================================
# Module-level access functions
# ============================================================================

def get_pattern_analyzer() -> TerminatorPatternAnalyzer:
    """Get the pattern analyzer instance"""
    return TerminatorPatternAnalyzer.get_instance()


if __name__ == "__main__":
    # Test the pattern analyzer
    analyzer = get_pattern_analyzer()

    # Record some data
    for i in range(20):
        analyzer.record_metric("response_time", 100 + i * 5)
        analyzer.record_data_point("task_type", "search" if i % 3 == 0 else "analysis")

    # Record sequences
    analyzer.record_sequence(["search", "analysis", "summary"])
    analyzer.record_sequence(["search", "analysis", "summary"])

    # Perform analysis
    print("\n=== Pattern Analysis ===")
    analysis = analyzer.analyze()
    print(json.dumps(analysis, indent=2, default=str))

    # Detect anomalies
    print("\n=== Anomaly Detection ===")
    anomalies = analyzer.detect_anomalies(
        "response_time",
        [100, 105, 110, 115, 500, 120, 125]  # 500 is anomaly
    )

    for anomaly in anomalies:
        print(f"  - {anomaly.description} (Severity: {anomaly.severity})")
