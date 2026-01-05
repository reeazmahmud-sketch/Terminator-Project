# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

import os
import json
import time
import math
import yaml
from typing import List, Dict, Any, Optional
from datetime import datetime

class MemorySystem:
    """
    Unified Hierarchical Memory System for Terminator.
    Manages Short-term (RAM), Long-term (JSON-based), and Global knowledge.
    """
    _instance = None

    def __init__(self, config_path: str = "core/memory_config.yaml"):
        self.config = self._load_config(config_path)
        self.base_path = self.config.get("storage", {}).get("base_path", "./memory_store")
        self.team_map = self.config.get("teams", {})
        self.global_writers = self.config.get("governance", {}).get("global_writers", [])
        
        # In-memory short-term cache: {agent_name: [messages]}
        self.short_term_memory: Dict[str, List[Dict]] = {}
        
        self._ensure_directories()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_config(self, path: str) -> Dict[str, Any]:
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print("⚠️  Memory Config not found, using defaults.")
            return {}

    def _ensure_directories(self):
        """Create storage hierarchy."""
        for scope in ["agent", "team", "global"]:
            os.makedirs(os.path.join(self.base_path, scope), exist_ok=True)

    def _get_path(self, scope: str, entity_id: str) -> str:
        """Get file path for a specific memory store."""
        # Sanitize entity_id
        safe_id = "".join(x for x in entity_id if x.isalnum() or x in "_-")
        if scope == "global":
            return os.path.join(self.base_path, "global", "knowledge.json")
        return os.path.join(self.base_path, scope, f"{safe_id}.json")

    def _load_store(self, path: str) -> List[Dict]:
        """Load memory entries from disk."""
        if not os.path.exists(path):
            return []
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading memory {path}: {e}")
            return []

    def _save_store(self, path: str, data: List[Dict]):
        """Save memory entries to disk."""
        try:
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving memory {path}: {e}")

    # --- API ---

    def store(self, agent_name: str, content: str, tags: List[str] = None, scope: str = "agent"):
        """
        Store a new memory fragment.
        
        Args:
            agent_name: Who is storing it.
            content: The text content.
            tags: Keywords for retrieval.
            scope: "agent" (private), "team" (shared role), "global" (system-wide).
        """
        # Governance Check
        if scope == "global" and agent_name not in self.global_writers:
            print(f"🛑 Access Denied: {agent_name} cannot write to Global Memory.")
            return False

        # Determine Target
        target_id = agent_name
        if scope == "team":
            target_id = self.team_map.get(agent_name, "default_team")
        elif scope == "global":
            target_id = "system"

        path = self._get_path(scope, target_id)
        entries = self._load_store(path)

        entry = {
            "id": f"{int(time.time()*1000)}",
            "timestamp": datetime.now().isoformat(),
            "author": agent_name,
            "content": content,
            "tags": tags or [],
            "embedding": [] # Placeholder for future vector support
        }
        
        entries.append(entry)
        
        # Basic Retention Policy (keep last 1000 items per file for MVP)
        if len(entries) > 1000:
            entries = entries[-1000:]
            
        self._save_store(path, entries)
        # print(f"💾 Memory Stored ({scope}): {content[:30]}...")
        return True

    def retrieve(self, agent_name: str, query: str, limit: int = 5) -> List[Dict]:
        """
        Retrieve relevant memories across all allowed scopes.
        Uses keyword matching + recency scoring (Mock RAG).
        """
        results = []
        
        # 1. Agent Scope
        agent_mem = self._load_store(self._get_path("agent", agent_name))
        results.extend(self._search(agent_mem, query, "agent"))

        # 2. Team Scope
        team_id = self.team_map.get(agent_name)
        if team_id:
            team_mem = self._load_store(self._get_path("team", team_id))
            results.extend(self._search(team_mem, query, "team"))

        # 3. Global Scope
        global_mem = self._load_store(self._get_path("global", "system"))
        results.extend(self._search(global_mem, query, "global"))

        # Sort by score and return top K
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]

    def _search(self, entries: List[Dict], query: str, source: str) -> List[Dict]:
        """Simple keyword ranking."""
        hits = []
        query_words = set(query.lower().split())
        
        for entry in entries:
            content_words = set(entry['content'].lower().split())
            tags = set(t.lower() for t in entry['tags'])
            
            # Match Score
            common = query_words.intersection(content_words.union(tags))
            if not common:
                continue
                
            score = len(common)
            
            # Recency Boost
            # (Simple decay: newer items get a small boost)
            # This is a very rough approximation
            
            hits.append({
                "content": entry['content'],
                "source": source,
                "score": score,
                "timestamp": entry['timestamp']
            })
            
        return hits

    def add_short_term(self, agent_name: str, role: str, content: str):
        """Add to RAM cache."""
        if agent_name not in self.short_term_memory:
            self.short_term_memory[agent_name] = []
        
        self.short_term_memory[agent_name].append({
            "role": role,
            "content": content,
            "timestamp": time.time()
        })
        
        # Limit RAM
        limit = self.config.get("retention", {}).get("short_term_limit", 50)
        if len(self.short_term_memory[agent_name]) > limit:
            self.short_term_memory[agent_name].pop(0)

    def get_short_term(self, agent_name: str) -> List[Dict]:
        return self.short_term_memory.get(agent_name, [])

# Helper
def get_memory_system():
    return MemorySystem.get_instance()
