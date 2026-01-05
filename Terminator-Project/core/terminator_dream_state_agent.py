import asyncio
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

# Try to import Ollama client, handle if not available
try:
    from ollama import Client
    OLLAMA_CLIENT_AVAILABLE = True
except ImportError:
    OLLAMA_CLIENT_AVAILABLE = False
    print("⚠️  Ollama client not found. Dream State LLM functions will be disabled.")

from core.agent_framework import BaseAgent
from core.terminator_agent_communication_bus import Message, MessageType, MessagePriority
from core.terminator_memory_system import MemorySystem # For memory access

class DreamStateAgent(BaseAgent):
    """
    The Dream State Agent performs nocturnal optimization:
    - Consolidates memories (summarizes short-term into long-term).
    - Self-trains by analyzing errors and generating playbooks.
    - Runs during idle periods to improve system efficiency and intelligence.
    """
    AGENT_NAME = "DreamStateAgent"
    AGENT_DESCRIPTION = "Performs nocturnal memory consolidation and self-training."
    AGENT_CAPABILITIES = ["memory_consolidation", "self_training", "optimization"]

    def __init__(self, ollama_url: str = "http://localhost:11434"):
        super().__init__(
            name=self.AGENT_NAME,
            description=self.AGENT_DESCRIPTION,
            capabilities=self.AGENT_CAPABILITIES
        )
        self.ollama_url = ollama_url
        self.ollama_client = Client(host=ollama_url) if OLLAMA_CLIENT_AVAILABLE else None
        self.memory_system = MemorySystem.get_instance()
        self.troubleshooting_playbook_path = "./troubleshooting_playbook.json"
        
        self.logger = logging.getLogger(self.AGENT_NAME)
        self.logger.setLevel(logging.INFO)
        # Use the same RotatingFileHandler as GovernanceSystem for consistency
        handler = logging.handlers.RotatingFileHandler(
            'governance_audit.log', maxBytes=5*1024*1024, backupCount=3
        )
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    async def handle_message(self, message: Message) -> Optional[Dict[str, Any]]:
        """
        Handles incoming messages for triggering dream state activities.
        Expected subjects: "start_consolidation", "start_self_training".
        """
        subject = message.subject.lower()

        if subject == "start_consolidation":
            self.logger.info("Initiating memory consolidation...")
            await self._consolidate_memories()
            return {"status": "memory_consolidation_initiated"}
        
        elif subject == "start_self_training":
            self.logger.info("Initiating self-training through error analysis...")
            await self._perform_self_training()
            return {"status": "self_training_initiated"}
            
        elif subject == "get_playbook":
            return self._get_troubleshooting_playbook()

        return {"error": f"Unknown dream state command: {subject}"}

    async def _ollama_chat(self, prompt: str, model: str = "qwen2.5:7b") -> Optional[str]:
        """Helper to make an Ollama chat call."""
        if not self.ollama_client:
            self.logger.warning("Ollama client not available for dream state operations.")
            return None
        try:
            response = self.ollama_client.chat(model=model, messages=[{'role': 'user', 'content': prompt}])
            return response['message']['content']
        except Exception as e:
            self.logger.error(f"Ollama call failed in Dream State: {e}")
            return None

    async def _consolidate_memories(self):
        """
        Consolidates short-term memories by summarizing them into long-term.
        """
        # Iterate over all agents' short-term memories
        for agent_name, short_memories in list(self.memory_system.short_term_memory.items()):
            if not short_memories:
                continue

            self.logger.info(f"Consolidating short-term memory for agent: {agent_name}")
            
            # Prepare summary prompt
            recent_activities = "\n".join([f"- {m['role']}: {m['content']}" for m in short_memories])
            prompt = (
                f"You are the Dream State Agent. Summarize the following recent activities of agent '{agent_name}'. "
                f"Extract key learnings, decisions, and recurring patterns into a concise summary. "
                f"Format as a bulleted list of insights.\n\nRecent Activities:\n{recent_activities}\n\nSummary of Insights:"
            )
            
            summary = await self._ollama_chat(prompt)
            
            if summary:
                self.memory_system.store(agent_name, f"Consolidated Summary: {summary}", ["summary", "learnings"], "agent")
                # Optionally, store in team/global memory based on significance
                if len(short_memories) > 10: # If enough content, maybe push to team
                    self.memory_system.store(agent_name, f"Team Insight from {agent_name}: {summary}", ["team_insight"], "team")
                self.logger.info(f"Memory consolidated for {agent_name}. Summary: {summary[:100]}...")
                # Clear short-term memory for this agent after consolidation
                self.memory_system.short_term_memory[agent_name].clear()
            else:
                self.logger.warning(f"Could not generate summary for {agent_name}.")

    async def _perform_self_training(self):
        """
        Analyzes error logs to update a troubleshooting playbook.
        """
        playbook = self._get_troubleshooting_playbook()
        
        # Read recent audit logs for errors
        error_logs = self._read_recent_error_logs()
        if not error_logs:
            self.logger.info("No new error logs to analyze for self-training.")
            return

        self.logger.info(f"Analyzing {len(error_logs)} error logs for self-training...")

        error_summary_prompt = (
            "You are the Dream State Agent. Analyze the following error logs and identify common patterns, "
            "root causes, and suggest new troubleshooting steps or playbook entries. "
            "Focus on actionable advice for automated self-healing. "
            "Format as 'Problem: <desc>\nSolution: <steps>\nImpacted Agents: <list>'.\n\nError Logs:\n"
            f"{error_logs}\n\nTroubleshooting Insights:"
        )
        
        insights = await self._ollama_chat(error_summary_prompt)
        
        if insights:
            # Parse insights and update playbook
            new_entries = self._parse_playbook_insights(insights)
            if new_entries:
                for entry in new_entries:
                    playbook["entries"].append(entry)
                self._save_troubleshooting_playbook(playbook)
                self.logger.info(f"Troubleshooting playbook updated with {len(new_entries)} new entries.")
            else:
                self.logger.info("No new actionable insights from error analysis.")
        else:
            self.logger.warning("Could not generate self-training insights from error logs.")

    def _read_recent_error_logs(self, hours: int = 24) -> str:
        """Reads recent error entries from the governance_audit.log."""
        log_path = 'governance_audit.log' # Assuming this is shared
        if not os.path.exists(log_path):
            return ""

        recent_errors = []
        cutoff_time = datetime.now() - timedelta(hours=hours)

        with open(log_path, 'r') as f:
            for line in reversed(f.readlines()): # Read from end to get recent
                try:
                    # Example log format: '2025-12-17 23:53:11,529 - INFO - Agent: SentinelAgent...'
                    # We need to parse timestamp and level
                    parts = line.split(' - ', 2)
                    if len(parts) >= 2:
                        log_time_str = parts[0]
                        log_level = parts[1]
                        
                        log_time = datetime.strptime(log_time_str.split(',')[0], '%Y-%m-%d %H:%M:%S')
                        
                        if log_time < cutoff_time:
                            break # Too old
                        if "ERROR" in log_level or "ALERT" in line: # Also check for custom ALERT
                            recent_errors.append(line.strip())
                except Exception:
                    # Malformed line, skip
                    pass
        return "\n".join(reversed(recent_errors)) # Return in chronological order

    def _get_troubleshooting_playbook(self) -> Dict[str, Any]:
        """Load or create the troubleshooting playbook."""
        if os.path.exists(self.troubleshooting_playbook_path):
            try:
                with open(self.troubleshooting_playbook_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading playbook: {e}")
        return {"last_updated": datetime.now().isoformat(), "entries": []}

    def _save_troubleshooting_playbook(self, playbook: Dict[str, Any]):
        """Save the troubleshooting playbook."""
        playbook["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.troubleshooting_playbook_path, 'w') as f:
                json.dump(playbook, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving playbook: {e}")

    def _parse_playbook_insights(self, insights_text: str) -> List[Dict]:
        """Parse LLM output into playbook entries."""
        # Simple parsing for demo: expect blocks starting with "Problem:"
        entries = []
        current_entry = {}
        for line in insights_text.split('\n'):
            if line.startswith("Problem:"):
                if current_entry: # Save previous
                    entries.append(current_entry)
                current_entry = {"problem": line.replace("Problem:", "").strip(), "solution": "", "impacted_agents": []}
            elif line.startswith("Solution:"):
                current_entry["solution"] = line.replace("Solution:", "").strip()
            elif line.startswith("Impacted Agents:"):
                current_entry["impacted_agents"] = [a.strip() for a in line.replace("Impacted Agents:", "").strip().split(',')]
        if current_entry: # Add last one
            entries.append(current_entry)
        return entries

# Factory for AgentLoader
def create_agent():
    return DreamStateAgent()
