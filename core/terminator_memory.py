#!/usr/bin/env python3

# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
🧠 TERMINATOR MEMORY BANK
Persistent memory system for Terminator to learn, remember, and improve
Core Identity: Helpful, intelligent AI assistant that learns from interactions
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path
import sqlite3
from collections import Counter
import re

# ============================================================================
# MEMORY STORAGE CONFIGURATION
# ============================================================================

MEMORY_DIR = Path.home() / ".terminator" / "memory"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

MEMORY_DB = MEMORY_DIR / "terminator_memory.db"
CONVERSATIONS_FILE = MEMORY_DIR / "conversations.json"
PREFERENCES_FILE = MEMORY_DIR / "preferences.json"
LEARNED_FACTS_FILE = MEMORY_DIR / "learned_facts.json"

# ============================================================================
# MEMORY DATA MODELS
# ============================================================================

class Conversation:
    """Single conversation turn"""
    def __init__(self, user_query: str, terminator_response: str, tools_used: List[str] = None, language: str = "en"):
        self.timestamp = datetime.now().isoformat()
        self.user_query = user_query
        self.terminator_response = terminator_response
        self.tools_used = tools_used or []
        self.language = language
        self.useful = None  # Will be set by user feedback

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "user_query": self.user_query,
            "terminator_response": self.terminator_response,
            "tools_used": self.tools_used,
            "language": self.language,
            "useful": self.useful
        }

class UserPreference:
    """User preference record"""
    def __init__(self, key: str, value: Any):
        self.key = key
        self.value = value
        self.created_at = datetime.now().isoformat()
        self.last_updated = self.created_at

    def to_dict(self) -> Dict:
        return {
            "key": self.key,
            "value": self.value,
            "created_at": self.created_at,
            "last_updated": self.last_updated
        }

class LearnedFact:
    """Fact learned by Terminator"""
    def __init__(self, fact: str, context: str, source: str = "conversation"):
        self.fact = fact
        self.context = context
        self.source = source
        self.confidence = 0.8
        self.learned_at = datetime.now().isoformat()
        self.usage_count = 0

    def to_dict(self) -> Dict:
        return {
            "fact": self.fact,
            "context": self.context,
            "source": self.source,
            "confidence": self.confidence,
            "learned_at": self.learned_at,
            "usage_count": self.usage_count
        }

# ============================================================================
# TERMINATOR MEMORY BANK
# ============================================================================

class TerminatorMemoryBank:
    """
    Persistent memory system for Terminator
    Stores conversations, preferences, and learned facts
    """

    def __init__(self):
        self.init_database()
        self.conversations = []
        self.preferences = {}
        self.learned_facts = []
        self.load_all()

    # ========================================================================
    # DATABASE INITIALIZATION
    # ========================================================================

    def init_database(self):
        """Initialize SQLite database for efficient queries"""
        try:
            conn = sqlite3.connect(str(MEMORY_DB))
            cursor = conn.cursor()

            # Conversations table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_query TEXT,
                terminator_response TEXT,
                tools_used TEXT,
                language TEXT,
                useful INTEGER,
                created_at TEXT
            )
            """)

            # Preferences table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                value TEXT,
                created_at TEXT,
                last_updated TEXT
            )
            """)

            # Learned facts table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS learned_facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fact TEXT,
                context TEXT,
                source TEXT,
                confidence REAL,
                learned_at TEXT,
                usage_count INTEGER
            )
            """)

            # User profile table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                language TEXT,
                timezone TEXT,
                created_at TEXT,
                last_seen TEXT
            )
            """)

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Database initialization warning: {e}")

    # ========================================================================
    # CONVERSATION MEMORY
    # ========================================================================

    def add_conversation(self, user_query: str, terminator_response: str, tools_used: List[str] = None, language: str = "en") -> bool:
        """
        Add a conversation turn to memory
        """
        try:
            conv = Conversation(user_query, terminator_response, tools_used, language)
            self.conversations.append(conv)

            # Save to database
            conn = sqlite3.connect(str(MEMORY_DB))
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO conversations
            (timestamp, user_query, terminator_response, tools_used, language, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                conv.timestamp,
                user_query,
                terminator_response,
                json.dumps(tools_used or []),
                language,
                datetime.now().isoformat()
            ))
            conn.commit()
            conn.close()

            return True
        except Exception as e:
            print(f"❌ Error adding conversation: {e}")
            return False

    def get_conversation_history(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation history"""
        try:
            conn = sqlite3.connect(str(MEMORY_DB))
            cursor = conn.cursor()
            cursor.execute("""
            SELECT user_query, terminator_response, timestamp, language
            FROM conversations
            ORDER BY timestamp DESC
            LIMIT ?
            """, (limit,))

            results = []
            for row in cursor.fetchall():
                results.append({
                    "user_query": row[0],
                    "terminator_response": row[1],
                    "timestamp": row[2],
                    "language": row[3]
                })

            conn.close()
            return results
        except Exception as e:
            print(f"❌ Error retrieving conversation history: {e}")
            return []

    def search_conversations(self, keyword: str, limit: int = 5) -> List[Dict]:
        """Search conversation history by keyword"""
        try:
            conn = sqlite3.connect(str(MEMORY_DB))
            cursor = conn.cursor()
            cursor.execute("""
            SELECT user_query, terminator_response, timestamp
            FROM conversations
            WHERE user_query LIKE ? OR terminator_response LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
            """, (f"%{keyword}%", f"%{keyword}%", limit))

            results = []
            for row in cursor.fetchall():
                results.append({
                    "user_query": row[0],
                    "terminator_response": row[1],
                    "timestamp": row[2]
                })

            conn.close()
            return results
        except Exception as e:
            print(f"❌ Error searching conversations: {e}")
            return []

    # ========================================================================
    # USER PREFERENCES
    # ========================================================================

    def set_preference(self, key: str, value: Any) -> bool:
        """
        Set a user preference
        Examples: language, timezone, notification_style, etc.
        """
        try:
            self.preferences[key] = value

            conn = sqlite3.connect(str(MEMORY_DB))
            cursor = conn.cursor()

            # Upsert (insert or update)
            cursor.execute("""
            INSERT OR REPLACE INTO preferences (key, value, created_at, last_updated)
            VALUES (?, ?, ?, ?)
            """, (key, json.dumps(value), datetime.now().isoformat(), datetime.now().isoformat()))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error setting preference: {e}")
            return False

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference"""
        if key in self.preferences:
            return self.preferences[key]

        try:
            conn = sqlite3.connect(str(MEMORY_DB))
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM preferences WHERE key = ?", (key,))
            result = cursor.fetchone()
            conn.close()

            if result:
                return json.loads(result[0])
        except Exception:
            pass

        return default

    def get_all_preferences(self) -> Dict:
        """Get all user preferences"""
        return self.preferences.copy()

    # ========================================================================
    # LEARNED FACTS
    # ========================================================================

    def learn_fact(self, fact: str, context: str, source: str = "conversation", confidence: float = 0.8) -> bool:
        """
        Store a learned fact
        Example: "User prefers Bengali responses", "User works in AI/ML"
        """
        try:
            learned = LearnedFact(fact, context, source)
            learned.confidence = confidence
            self.learned_facts.append(learned)

            conn = sqlite3.connect(str(MEMORY_DB))
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO learned_facts
            (fact, context, source, confidence, learned_at, usage_count)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (fact, context, source, confidence, learned.learned_at, 0))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error learning fact: {e}")
            return False

    def get_learned_facts(self, limit: int = 10) -> List[Dict]:
        """Get learned facts ordered by confidence and usage"""
        try:
            conn = sqlite3.connect(str(MEMORY_DB))
            cursor = conn.cursor()
            cursor.execute("""
            SELECT fact, context, confidence, usage_count, learned_at
            FROM learned_facts
            ORDER BY confidence DESC, usage_count DESC
            LIMIT ?
            """, (limit,))

            results = []
            for row in cursor.fetchall():
                results.append({
                    "fact": row[0],
                    "context": row[1],
                    "confidence": row[2],
                    "usage_count": row[3],
                    "learned_at": row[4]
                })

            conn.close()
            return results
        except Exception as e:
            print(f"❌ Error retrieving learned facts: {e}")
            return []

    # ========================================================================
    # MEMORY ANALYSIS
    # ========================================================================

    def get_memory_stats(self) -> Dict:
        """Get memory bank statistics"""
        try:
            conn = sqlite3.connect(str(MEMORY_DB))
            cursor = conn.cursor()

            # Conversation count
            cursor.execute("SELECT COUNT(*) FROM conversations")
            conv_count = cursor.fetchone()[0]

            # Preferences count
            cursor.execute("SELECT COUNT(*) FROM preferences")
            pref_count = cursor.fetchone()[0]

            # Learned facts count
            cursor.execute("SELECT COUNT(*) FROM learned_facts")
            facts_count = cursor.fetchone()[0]

            # Most used tools
            cursor.execute("""
            SELECT tools_used, COUNT(*) as count
            FROM conversations
            GROUP BY tools_used
            ORDER BY count DESC
            LIMIT 5
            """)
            most_used_tools = cursor.fetchall()

            conn.close()

            return {
                "total_conversations": conv_count,
                "total_preferences": pref_count,
                "total_learned_facts": facts_count,
                "most_used_tools": [{"tools": t[0], "count": t[1]} for t in most_used_tools],
                "memory_file_size": MEMORY_DB.stat().st_size if MEMORY_DB.exists() else 0
            }
        except Exception as e:
            print(f"❌ Error getting memory stats: {e}")
            return {}

    def get_context_summary(self) -> str:
        """
        Generate a summary of user context for Terminator to use
        Helps maintain consistent personality and behavior
        """
        stats = self.get_memory_stats()
        prefs = self.get_all_preferences()
        facts = self.get_learned_facts(limit=5)

        summary = f"""
        📊 TERMINATOR MEMORY CONTEXT:

        User Profile:
        - Conversations: {stats.get('total_conversations', 0)}
        - Preferred Language: {prefs.get('language', 'English')}
        - Timezone: {prefs.get('timezone', 'Not set')}

        Key Facts About User:
        {chr(10).join([f"  • {f['fact']} (confidence: {f['confidence']:.0%})" for f in facts])}

        User Preferences:
        {chr(10).join([f"  • {k}: {v}" for k, v in prefs.items()])}
        """

        return summary

    # ========================================================================
    # PERSISTENCE
    # ========================================================================

    def load_all(self):
        """Load all memory from storage"""
        try:
            # Load preferences
            if os.path.exists(PREFERENCES_FILE):
                with open(PREFERENCES_FILE, 'r') as f:
                    self.preferences = json.load(f)
        except Exception as e:
            print(f"⚠️ Could not load preferences: {e}")

    def save_all(self):
        """Save all memory to storage"""
        try:
            with open(PREFERENCES_FILE, 'w') as f:
                json.dump(self.preferences, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving memory: {e}")

    def clear_memory(self, confirm: bool = False) -> bool:
        """
        Clear all memory (use with caution!)
        Requires confirmation
        """
        if not confirm:
            return False

        try:
            conn = sqlite3.connect(str(MEMORY_DB))
            cursor = conn.cursor()

            cursor.execute("DELETE FROM conversations")
            cursor.execute("DELETE FROM preferences")
            cursor.execute("DELETE FROM learned_facts")

            conn.commit()
            conn.close()

            self.conversations = []
            self.preferences = {}
            self.learned_facts = []

            return True
        except Exception as e:
            print(f"❌ Error clearing memory: {e}")
            return False

    def export_memory(self, filepath: str) -> bool:
        """Export memory to JSON file for backup"""
        try:
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "stats": self.get_memory_stats(),
                "preferences": self.preferences,
                "recent_conversations": self.get_conversation_history(limit=50),
                "learned_facts": self.get_learned_facts(limit=100)
            }

            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)

            return True
        except Exception as e:
            print(f"❌ Error exporting memory: {e}")
            return False

    # ========================================================================
    # ADVANCED FEATURES
    # ========================================================================

    def prune_old_conversations(self, days: int = 90) -> int:
        """Delete conversations older than specified days (memory pruning)"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

            conn = sqlite3.connect(str(MEMORY_DB))
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM conversations WHERE timestamp < ?", (cutoff_date,))
            count_before = cursor.fetchone()[0]

            cursor.execute("DELETE FROM conversations WHERE timestamp < ?", (cutoff_date,))
            conn.commit()
            conn.close()

            print(f"✅ Pruned {count_before} conversations older than {days} days")
            return count_before
        except Exception as e:
            print(f"❌ Error pruning conversations: {e}")
            return 0

    def analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text (positive, negative, neutral)"""
        try:
            # Simple sentiment analysis based on keywords
            positive_words = {'good', 'great', 'excellent', 'love', 'perfect', 'amazing', 'wonderful', 'happy', 'thanks'}
            negative_words = {'bad', 'terrible', 'awful', 'hate', 'worst', 'poor', 'sad', 'angry', 'disappointing'}

            text_lower = text.lower()
            words = set(text_lower.split())

            positive_count = len(words & positive_words)
            negative_count = len(words & negative_words)

            if positive_count > negative_count:
                return "positive"
            elif negative_count > positive_count:
                return "negative"
            else:
                return "neutral"
        except Exception as e:
            return "neutral"

    def extract_facts_from_text(self, text: str) -> List[str]:
        """Automatically extract potential facts from conversation text"""
        try:
            facts = []

            # Pattern: "User prefers X"
            user_prefs = re.findall(r'(?:user|i) (?:prefer|like|enjoy|want)s? ([^.!?,]+)', text.lower())
            for pref in user_prefs:
                facts.append(f"User prefers {pref.strip()}")

            # Pattern: "User works with/on X"
            work_patterns = re.findall(r'(?:work|works) (?:with|on|in) ([^.!?,]+)', text.lower())
            for work in work_patterns:
                facts.append(f"User works with {work.strip()}")

            # Pattern: "User is X" (profession/role)
            role_patterns = re.findall(r'(?:user|i|am|\'m) (?:a|an) ([^.!?,]+)', text.lower())
            for role in role_patterns:
                if len(role) < 50:  # Filter out overly long matches
                    facts.append(f"User is a {role.strip()}")

            return list(set(facts))  # Remove duplicates
        except Exception as e:
            return []

    def get_trending_topics(self, limit: int = 10) -> List[Dict]:
        """Get trending topics from conversations based on word frequency"""
        try:
            conn = sqlite3.connect(str(MEMORY_DB))
            cursor = conn.cursor()
            cursor.execute("SELECT user_query FROM conversations ORDER BY timestamp DESC LIMIT 100")

            conversations = cursor.fetchall()
            conn.close()

            # Extract and count words
            all_words = []
            stop_words = {'the', 'a', 'an', 'is', 'are', 'what', 'how', 'why', 'and', 'or', 'but', 'in', 'on', 'at'}

            for conv in conversations:
                words = conv[0].lower().split()
                all_words.extend([w.strip('.,!?;:') for w in words if w.lower() not in stop_words and len(w) > 3])

            word_freq = Counter(all_words).most_common(limit)

            return [{"word": word, "frequency": count} for word, count in word_freq]
        except Exception as e:
            return []

    def advanced_search(self, keyword: str = None, sentiment: str = None,
                       date_from: str = None, date_to: str = None,
                       limit: int = 10) -> List[Dict]:
        """Advanced search with filters: keyword, sentiment, date range"""
        try:
            conn = sqlite3.connect(str(MEMORY_DB))
            cursor = conn.cursor()

            query = "SELECT user_query, terminator_response, timestamp FROM conversations WHERE 1=1"
            params = []

            if keyword:
                query += " AND (user_query LIKE ? OR terminator_response LIKE ?)"
                params.extend([f"%{keyword}%", f"%{keyword}%"])

            if date_from:
                query += " AND timestamp >= ?"
                params.append(date_from)

            if date_to:
                query += " AND timestamp <= ?"
                params.append(date_to)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()

            # Filter by sentiment if specified
            filtered_results = []
            for result in results:
                user_query, response, timestamp = result
                sentiment_analysis = self.analyze_sentiment(user_query + " " + response)

                if sentiment is None or sentiment_analysis == sentiment:
                    filtered_results.append({
                        "user_query": user_query,
                        "terminator_response": response,
                        "timestamp": timestamp,
                        "sentiment": sentiment_analysis
                    })

            return filtered_results
        except Exception as e:
            print(f"❌ Error in advanced search: {e}")
            return []

    def import_memory(self, filepath: str) -> bool:
        """Import memory from JSON file (backup restore)"""
        try:
            with open(filepath, 'r') as f:
                import_data = json.load(f)

            # Import preferences
            for key, value in import_data.get('preferences', {}).items():
                self.set_preference(key, value)

            # Import conversations
            for conv in import_data.get('recent_conversations', []):
                self.add_conversation(
                    user_query=conv.get('user_query', ''),
                    terminator_response=conv.get('terminator_response', ''),
                    language=conv.get('language', 'en')
                )

            # Import learned facts
            for fact in import_data.get('learned_facts', []):
                self.learn_fact(
                    fact=fact.get('fact', ''),
                    context=fact.get('context', ''),
                    confidence=fact.get('confidence', 0.8)
                )

            print(f"✅ Memory imported successfully from {filepath}")
            return True
        except Exception as e:
            print(f"❌ Error importing memory: {e}")
            return False

    def get_memory_dashboard(self) -> Dict:
        """Get comprehensive dashboard data for visualization"""
        try:
            stats = self.get_memory_stats()
            trending = self.get_trending_topics(limit=5)

            # Get sentiment distribution
            conn = sqlite3.connect(str(MEMORY_DB))
            cursor = conn.cursor()
            cursor.execute("SELECT user_query, terminator_response FROM conversations LIMIT 50")
            conversations = cursor.fetchall()
            conn.close()

            sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
            for user_query, response in conversations:
                sentiment = self.analyze_sentiment(user_query + " " + response)
                sentiment_counts[sentiment] += 1

            # Get last 7 days activity
            days_activity = {}
            for i in range(7):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                conn = sqlite3.connect(str(MEMORY_DB))
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM conversations WHERE timestamp LIKE ?", (f"{date}%",))
                count = cursor.fetchone()[0]
                conn.close()
                days_activity[date] = count

            return {
                "stats": stats,
                "trending_topics": trending,
                "sentiment_distribution": sentiment_counts,
                "last_7_days_activity": days_activity,
                "dashboard_generated": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ Error generating dashboard: {e}")
            return {}

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("🧠 TERMINATOR MEMORY BANK - Test\n")
    print("=" * 70)

    # Initialize memory
    memory = TerminatorMemoryBank()

    # Example 1: Add conversation
    print("\n📝 Example 1: Adding Conversation")
    memory.add_conversation(
        user_query="What is Python?",
        terminator_response="Python is a versatile programming language...",
        tools_used=["web_search"],
        language="en"
    )
    print("✅ Conversation added")

    # Example 2: Set preferences
    print("\n⚙️ Example 2: Setting User Preferences")
    memory.set_preference("language", "English")
    memory.set_preference("timezone", "UTC")
    memory.set_preference("notification_style", "minimal")
    print(f"✅ Preferences set: {memory.get_all_preferences()}")

    # Example 3: Learn facts
    print("\n🧠 Example 3: Learning Facts")
    memory.learn_fact(
        fact="User prefers concise responses",
        context="Observed from multiple conversations",
        confidence=0.85
    )
    memory.learn_fact(
        fact="User works with AI/ML projects",
        context="Based on search queries and file operations",
        confidence=0.9
    )
    print("✅ Facts learned")

    # Example 4: Get stats
    print("\n📊 Example 4: Memory Statistics")
    stats = memory.get_memory_stats()
    print(f"Total Conversations: {stats['total_conversations']}")
    print(f"Total Preferences: {stats['total_preferences']}")
    print(f"Total Learned Facts: {stats['total_learned_facts']}")

    # Example 5: Context summary
    print("\n📋 Example 5: Context Summary")
    print(memory.get_context_summary())

    # Example 6: Export memory
    print("\n💾 Example 6: Exporting Memory")
    export_path = str(MEMORY_DIR / "terminator_memory_export.json")
    if memory.export_memory(export_path):
        print(f"✅ Memory exported to {export_path}")

    print("\n✅ Memory Bank Test Complete!")
    print("=" * 70)
