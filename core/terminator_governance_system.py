# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

import yaml
import os
import logging
import logging.handlers
from datetime import datetime
from typing import Dict, List, Any, Optional

class GovernanceSystem:
    """
    Central Governance Engine for Terminator.
    Enforces policies, risk levels, and lifecycle rules defined in governance_policy.yaml.
    """
    _instance = None

    def __init__(self, policy_path: str = "core/governance_policy.yaml"):
        self.policy_path = policy_path
        self.policy = self._load_policy()
        self.audit_log = []
        
        # Setup logging with rotation
        handler = logging.handlers.RotatingFileHandler(
            'governance_audit.log', maxBytes=5*1024*1024, backupCount=3
        )
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger = logging.getLogger('GovernanceSystem')
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        self.logger = logger

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_policy(self) -> Dict[str, Any]:
        """Load the YAML policy definition."""
        if not os.path.exists(self.policy_path):
            print(f"⚠️  Governance Policy not found at {self.policy_path}. Using defaults.")
            return {}
        try:
            with open(self.policy_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Error loading governance policy: {e}")
            return {}

    def check_permission(self, agent_name: str, action: str, params: Dict[str, Any] = None) -> bool:
        """
        Check if an agent is allowed to perform an action.
        Returns True if allowed, False if denied.
        """
        # 1. Check Global Guardrails
        if not self._check_global_guardrails(action, params):
            self._log_decision(agent_name, action, "DENIED", "Global Guardrail Violation")
            return False

        # 2. Check Agent Registration
        agent_policy = self.policy.get("agent_registry", {}).get(agent_name)
        if not agent_policy:
            # Unknown agent -> Default to Low Risk only?
            # For now, allow but log warning
            self._log_decision(agent_name, action, "WARNING", "Unregistered Agent")
            return True

        # 3. Check Risk Level & Forbidden Actions
        if action in agent_policy.get("forbidden_actions", []):
            self._log_decision(agent_name, action, "DENIED", "Explicitly Forbidden")
            return False

        # 4. Critical Action Check
        risk_level = agent_policy.get("risk_level", "low")
        if risk_level == "critical":
            # In a real system, this might trigger a human approval workflow
            pass

        self._log_decision(agent_name, action, "ALLOWED", "Policy Passed")
        return True

    def _check_global_guardrails(self, action: str, params: Dict[str, Any]) -> bool:
        """Check against system-wide banned patterns."""
        guardrails = self.policy.get("global_guardrails", {})
        
        # Check blocked commands
        for blocked in guardrails.get("blocked_commands", []):
            if blocked in action:
                return False
        
        # Check sensitive paths (if action involves file path)
        if params and "path" in params:
            path = params["path"]
            for sensitive in guardrails.get("sensitive_paths", []):
                if sensitive in path:
                    return False
                    
        return True

    def _log_decision(self, agent: str, action: str, decision: str, reason: str):
        """Log the governance decision for audit."""
        entry = f"Agent: {agent} | Action: {action} | Decision: {decision} | Reason: {reason}"
        self.logger.info(entry)
        # print(f"⚖️  Governance: {entry}") # Optional console output

    def get_agent_lifecycle_status(self, agent_name: str) -> str:
        """Get the lifecycle stage of an agent."""
        agent = self.policy.get("agent_registry", {}).get(agent_name)
        if agent:
            return agent.get("lifecycle_stage", "unknown")
        return "unregistered"

# Helper for agents
def check_action(agent_name: str, action: str, params: dict = None) -> bool:
    return GovernanceSystem.get_instance().check_permission(agent_name, action, params)
