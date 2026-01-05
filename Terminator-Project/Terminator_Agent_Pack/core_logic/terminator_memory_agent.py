#!/usr/bin/env python3

# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Memory Management Agent
Specialized agent for monitoring, optimizing, and managing Terminator conversation memory.

Features:
- Real-time memory usage tracking
- Conversation analytics and insights
- Memory optimization and pruning
- Preference management
- Learned facts organization
- Memory health monitoring
- Performance optimization
"""

import os
import sys
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import time
from collections import defaultdict, Counter

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

TERMINATOR_ROOT = Path("/Users/reeazmahmud/Desktop/Terminator")
MEMORY_DIR = Path.home() / ".terminator" / "memory"
MEMORY_DB = MEMORY_DIR / "terminator_memory.db"
LOGS_DIR = TERMINATOR_ROOT / "logs" / "memory_agent"
LOGS_DIR.mkdir(parents=True, exist_ok=True)


class MemoryHealth(Enum):
    """Memory health status levels"""
    EXCELLENT = "EXCELLENT"  # < 50% capacity
    GOOD = "GOOD"            # 50-70% capacity
    WARNING = "WARNING"      # 70-85% capacity
    CRITICAL = "CRITICAL"    # > 85% capacity


class OptimizationAction(Enum):
    """Types of memory optimization actions"""
    PRUNE_OLD = "PRUNE_OLD"           # Remove conversations older than threshold
    COMPRESS = "COMPRESS"              # Compress old entries
    DEDUPLICATE = "DEDUPLICATE"        # Remove duplicate preferences
    ARCHIVE = "ARCHIVE"                # Archive to external storage
    CLEANUP_FACTS = "CLEANUP_FACTS"    # Remove low-confidence facts


@dataclass
class MemoryStats:
    """Memory statistics"""
    timestamp: str
    total_conversations: int
    total_preferences: int
    total_learned_facts: int
    database_size_mb: float
    oldest_conversation: Optional[str]
    newest_conversation: Optional[str]
    avg_conversation_length: float
    memory_health: str
    optimization_recommended: bool


@dataclass
class ConversationMetrics:
    """Conversation analysis metrics"""
    total_conversations: int
    conversations_last_24h: int
    conversations_last_7d: int
    avg_response_length: float
    most_used_tools: List[Tuple[str, int]]
    sentiment_distribution: Dict[str, int]
    language_distribution: Dict[str, int]
    average_interaction_time: Optional[float]


@dataclass
class PreferenceSnapshot:
    """User preference snapshot"""
    language: str
    timezone: str
    notification_style: str
    voice_settings: Dict[str, Any]
    other_preferences: Dict[str, Any]


class MemoryDatabaseManager:
    """Manages direct database operations"""

    def __init__(self, db_path: Path = MEMORY_DB):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(str(self.db_path))

    def get_database_size_mb(self) -> float:
        """Get database file size in MB"""
        if self.db_path.exists():
            return self.db_path.stat().st_size / (1024 * 1024)
        return 0.0

    def count_conversations(self) -> int:
        """Count total conversations"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM conversations")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            logger.error(f"Error counting conversations: {e}")
            return 0

    def count_preferences(self) -> int:
        """Count total preferences"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM preferences")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            logger.error(f"Error counting preferences: {e}")
            return 0

    def count_learned_facts(self) -> int:
        """Count total learned facts"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM learned_facts")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            logger.error(f"Error counting learned facts: {e}")
            return 0

    def get_conversation_date_range(self) -> Tuple[Optional[str], Optional[str]]:
        """Get oldest and newest conversation dates"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT timestamp FROM conversations ORDER BY timestamp ASC LIMIT 1")
            oldest = cursor.fetchone()
            oldest_date = oldest[0] if oldest else None

            cursor.execute("SELECT timestamp FROM conversations ORDER BY timestamp DESC LIMIT 1")
            newest = cursor.fetchone()
            newest_date = newest[0] if newest else None

            conn.close()
            return oldest_date, newest_date
        except Exception as e:
            logger.error(f"Error getting conversation date range: {e}")
            return None, None

    def get_tools_usage(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get most used tools"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT tools_used FROM conversations WHERE tools_used IS NOT NULL")
            rows = cursor.fetchall()
            conn.close()

            tool_counter = Counter()
            for row in rows:
                try:
                    tools = json.loads(row[0]) if isinstance(row[0], str) else row[0]
                    if isinstance(tools, list):
                        tool_counter.update(tools)
                except:
                    pass

            return tool_counter.most_common(limit)
        except Exception as e:
            logger.error(f"Error getting tools usage: {e}")
            return []

    def get_language_distribution(self) -> Dict[str, int]:
        """Get language distribution"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT language, COUNT(*) FROM conversations GROUP BY language")
            rows = cursor.fetchall()
            conn.close()
            return {lang: count for lang, count in rows}
        except Exception as e:
            logger.error(f"Error getting language distribution: {e}")
            return {}

    def get_conversations_in_timeframe(self, hours: int = 24) -> int:
        """Get conversation count in last N hours"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            threshold = datetime.now() - timedelta(hours=hours)
            cursor.execute(
                "SELECT COUNT(*) FROM conversations WHERE timestamp > ?",
                (threshold.isoformat(),)
            )
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            logger.error(f"Error getting conversations in timeframe: {e}")
            return 0

    def get_average_response_length(self) -> float:
        """Get average response length"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT AVG(LENGTH(terminator_response)) FROM conversations WHERE terminator_response IS NOT NULL"
            )
            avg = cursor.fetchone()[0]
            conn.close()
            return avg if avg else 0.0
        except Exception as e:
            logger.error(f"Error getting average response length: {e}")
            return 0.0

    def prune_conversations(self, days: int = 90) -> int:
        """Delete conversations older than N days"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            threshold = datetime.now() - timedelta(days=days)
            cursor.execute(
                "DELETE FROM conversations WHERE timestamp < ?",
                (threshold.isoformat(),)
            )
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            logger.info(f"Pruned {deleted} conversations older than {days} days")
            return deleted
        except Exception as e:
            logger.error(f"Error pruning conversations: {e}")
            return 0

    def cleanup_low_confidence_facts(self, min_confidence: float = 0.3) -> int:
        """Remove learned facts below confidence threshold"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM learned_facts WHERE confidence < ?",
                (min_confidence,)
            )
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            logger.info(f"Cleaned up {deleted} low-confidence facts")
            return deleted
        except Exception as e:
            logger.error(f"Error cleaning up facts: {e}")
            return 0

    def export_memory_snapshot(self, export_path: Path) -> bool:
        """Export memory to JSON file"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Get conversations
            cursor.execute("SELECT * FROM conversations ORDER BY timestamp DESC LIMIT 100")
            conversations = [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]

            # Get preferences
            cursor.execute("SELECT * FROM preferences")
            preferences = {}
            for row in cursor.fetchall():
                try:
                    preferences[row[1]] = json.loads(row[2]) if row[2] else None
                except:
                    preferences[row[1]] = row[2]

            # Get learned facts
            cursor.execute("SELECT * FROM learned_facts ORDER BY confidence DESC LIMIT 100")
            facts = [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]

            conn.close()

            snapshot = {
                'timestamp': datetime.now().isoformat(),
                'conversations': conversations,
                'preferences': preferences,
                'learned_facts': facts
            }

            with open(export_path, 'w') as f:
                json.dump(snapshot, f, indent=2, default=str)

            logger.info(f"Exported memory snapshot to {export_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting memory: {e}")
            return False


class MemoryAnalyzer:
    """Analyzes memory data and generates insights"""

    def __init__(self, db_manager: MemoryDatabaseManager):
        self.db_manager = db_manager

    def get_memory_stats(self) -> MemoryStats:
        """Get comprehensive memory statistics"""
        total_conversations = self.db_manager.count_conversations()
        total_preferences = self.db_manager.count_preferences()
        total_facts = self.db_manager.count_learned_facts()
        db_size = self.db_manager.get_database_size_mb()

        oldest, newest = self.db_manager.get_conversation_date_range()
        avg_response_length = self.db_manager.get_average_response_length()

        # Calculate health
        health = self._calculate_health(db_size, total_conversations)

        return MemoryStats(
            timestamp=datetime.now().isoformat(),
            total_conversations=total_conversations,
            total_preferences=total_preferences,
            total_learned_facts=total_facts,
            database_size_mb=round(db_size, 2),
            oldest_conversation=oldest,
            newest_conversation=newest,
            avg_conversation_length=round(avg_response_length, 2),
            memory_health=health.value,
            optimization_recommended=health in [MemoryHealth.WARNING, MemoryHealth.CRITICAL]
        )

    def get_conversation_metrics(self) -> ConversationMetrics:
        """Get conversation analysis metrics"""
        total = self.db_manager.count_conversations()
        last_24h = self.db_manager.get_conversations_in_timeframe(hours=24)
        last_7d = self.db_manager.get_conversations_in_timeframe(hours=168)
        avg_length = self.db_manager.get_average_response_length()
        tools = self.db_manager.get_tools_usage()
        languages = self.db_manager.get_language_distribution()

        return ConversationMetrics(
            total_conversations=total,
            conversations_last_24h=last_24h,
            conversations_last_7d=last_7d,
            avg_response_length=avg_length,
            most_used_tools=tools,
            sentiment_distribution={},  # Would require sentiment analysis
            language_distribution=languages,
            average_interaction_time=None
        )

    def _calculate_health(self, db_size_mb: float, conversation_count: int) -> MemoryHealth:
        """Calculate memory health based on size and count"""
        # Estimate: ~0.5MB per 100 conversations, max ~500MB recommended
        estimated_capacity = (db_size_mb / 500.0) * 100

        if estimated_capacity < 50:
            return MemoryHealth.EXCELLENT
        elif estimated_capacity < 70:
            return MemoryHealth.GOOD
        elif estimated_capacity < 85:
            return MemoryHealth.WARNING
        else:
            return MemoryHealth.CRITICAL

    def get_optimization_recommendations(self) -> List[Tuple[OptimizationAction, str]]:
        """Get memory optimization recommendations"""
        recommendations = []
        stats = self.get_memory_stats()

        # Check age of conversations
        if stats.oldest_conversation:
            oldest_date = datetime.fromisoformat(stats.oldest_conversation)
            age_days = (datetime.now() - oldest_date).days
            if age_days > 90:
                recommendations.append((
                    OptimizationAction.PRUNE_OLD,
                    f"Conversations older than 90 days found ({age_days} days oldest). Consider pruning."
                ))

        # Check database size
        if stats.database_size_mb > 100:
            recommendations.append((
                OptimizationAction.COMPRESS,
                f"Database size is {stats.database_size_mb}MB. Consider compression."
            ))

        # Check memory health
        if stats.memory_health == MemoryHealth.WARNING.value:
            recommendations.append((
                OptimizationAction.ARCHIVE,
                "Memory capacity approaching limit. Consider archiving old data."
            ))

        if stats.memory_health == MemoryHealth.CRITICAL.value:
            recommendations.append((
                OptimizationAction.PRUNE_OLD,
                "CRITICAL: Memory at capacity. Immediate pruning required."
            ))

        return recommendations


class TerminatorMemoryAgent:
    """Main memory management agent"""

    def __init__(self, check_interval: int = 300):
        """
        Initialize memory management agent

        Args:
            check_interval: Memory check interval in seconds (default 5 minutes)
        """
        self.check_interval = check_interval
        self.running = False
        self.monitor_thread = None

        self.db_manager = MemoryDatabaseManager()
        self.analyzer = MemoryAnalyzer(self.db_manager)

        self.optimization_history: List[Tuple[datetime, str, int]] = []

    def start_monitoring(self) -> None:
        """Start memory monitoring"""
        if self.running:
            logger.warning("Memory monitoring already running")
            return

        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("Memory Agent started")

    def stop_monitoring(self) -> None:
        """Stop memory monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Memory Agent stopped")

    def _monitor_loop(self) -> None:
        """Main monitoring loop"""
        while self.running:
            try:
                stats = self.analyzer.get_memory_stats()
                self._log_stats(stats)

                # Get recommendations
                recommendations = self.analyzer.get_optimization_recommendations()
                if recommendations:
                    self._log_recommendations(recommendations)

                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in memory monitoring loop: {e}")

    def _log_stats(self, stats: MemoryStats) -> None:
        """Log memory statistics"""
        log_file = LOGS_DIR / f"memory_stats_{datetime.now().strftime('%Y%m%d')}.json"

        try:
            # Read existing logs
            if log_file.exists():
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []

            # Append new stats
            logs.append(asdict(stats))

            # Write back
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)

        except Exception as e:
            logger.error(f"Error logging stats: {e}")

    def _log_recommendations(self, recommendations: List[Tuple[OptimizationAction, str]]) -> None:
        """Log optimization recommendations"""
        log_file = LOGS_DIR / "memory_recommendations.json"

        try:
            entry = {
                'timestamp': datetime.now().isoformat(),
                'recommendations': [
                    {'action': action.value, 'description': desc}
                    for action, desc in recommendations
                ]
            }

            # Read existing logs
            if log_file.exists():
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []

            logs.append(entry)

            # Write back
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)

        except Exception as e:
            logger.error(f"Error logging recommendations: {e}")

    def get_memory_status(self) -> Dict[str, Any]:
        """Get current memory status"""
        stats = self.analyzer.get_memory_stats()
        metrics = self.analyzer.get_conversation_metrics()
        recommendations = self.analyzer.get_optimization_recommendations()

        return {
            'timestamp': datetime.now().isoformat(),
            'stats': asdict(stats),
            'metrics': asdict(metrics),
            'recommendations': [
                {'action': action.value, 'description': desc}
                for action, desc in recommendations
            ]
        }

    def optimize_memory(self, aggressive: bool = False) -> Dict[str, Any]:
        """
        Optimize memory

        Args:
            aggressive: Perform more aggressive cleanup if True

        Returns:
            Optimization results
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'actions': []
        }

        # Prune old conversations
        pruned = self.db_manager.prune_conversations(days=30 if aggressive else 90)
        results['actions'].append({
            'action': 'PRUNE_OLD',
            'items_affected': pruned
        })

        # Clean low-confidence facts
        cleaned = self.db_manager.cleanup_low_confidence_facts(
            min_confidence=0.2 if aggressive else 0.3
        )
        results['actions'].append({
            'action': 'CLEANUP_FACTS',
            'items_affected': cleaned
        })

        logger.info(f"Memory optimization completed. Pruned: {pruned}, Cleaned: {cleaned}")

        return results

    def export_memory(self, export_path: Optional[Path] = None) -> bool:
        """Export memory to file"""
        if export_path is None:
            export_path = LOGS_DIR / f"memory_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        return self.db_manager.export_memory_snapshot(export_path)


# Global agent instance
_agent_instance: Optional[TerminatorMemoryAgent] = None


def get_memory_agent() -> TerminatorMemoryAgent:
    """Get or create global memory agent"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = TerminatorMemoryAgent(check_interval=300)
    return _agent_instance


def start_memory_monitoring() -> None:
    """Start memory monitoring"""
    agent = get_memory_agent()
    agent.start_monitoring()


def stop_memory_monitoring() -> None:
    """Stop memory monitoring"""
    agent = get_memory_agent()
    agent.stop_monitoring()


def get_memory_status() -> Dict[str, Any]:
    """Get memory status"""
    agent = get_memory_agent()
    return agent.get_memory_status()


if __name__ == "__main__":
    # Test the memory agent
    agent = get_memory_agent()
    agent.start_monitoring()

    logger.info("Memory Agent is running. Press Ctrl+C to stop.")

    try:
        while True:
            status = agent.get_memory_status()
            print(json.dumps(status, indent=2, default=str))
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("Stopping memory agent...")
        agent.stop_monitoring()
