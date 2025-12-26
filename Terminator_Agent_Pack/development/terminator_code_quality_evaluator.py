#!/usr/bin/env python3

# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Code Quality Evaluator
Evaluates agent code quality on 4 characteristics:
1. Correctness (0-1 pt) - Task completion success
2. Documentation (0-1 pt) - Code quality, comments
3. Testing Coverage (0-1 pt) - Tests exist and pass
4. Security (0-1 pt) - Safe operations

Uses: Gemini 2.0 Flash (FREE, 15 RPM limit)
Fallback: phi4 local
"""

import json
import sys
from typing import Dict, Optional
from pathlib import Path

sys.path.insert(0, '/Users/reeazmahmud/Desktop/Terminator')

from llm_system.INTELLIGENT_LLM_ROUTER import IntelligentLLMRouter, TaskPriority
from core.terminator_model_manager import get_model_manager


class CodeQualityEvaluator:
    """Evaluates code quality of agents"""

    def __init__(self):
        self.evaluator_name = "CodeQualityEvaluator"
        self.base_path = Path("/Users/reeazmahmud/Desktop/Terminator")

        # LLM setup
        self.llm_router = IntelligentLLMRouter()
        self.model_manager = get_model_manager()

        self.primary_model = "gemini-2.0-flash"  # FREE tier
        self.fallback_model = "phi4"  # Local fallback

        print(f"✅ Code Quality Evaluator initialized (Primary: {self.primary_model}, Fallback: {self.fallback_model})")

    async def evaluate(self, request) -> Dict:
        """
        Evaluate agent on 4 code quality characteristics
        Returns: {
            "scores": {
                "correctness": 0.8,
                "documentation": 0.7,
                "testing_coverage": 0.9,
                "security": 0.85,
            },
            "models_used": {
                "gemini-2.0-flash": True
            }
        }
        """
        agent_name = request.agent_name
        task_success = request.success

        # Get agent source code
        agent_code = self._get_agent_source(agent_name)

        if not agent_code:
            # Return default scores if agent source not found
            return {
                "scores": {
                    "correctness": 0.5,
                    "documentation": 0.5,
                    "testing_coverage": 0.5,
                    "security": 0.5,
                },
                "models_used": {}
            }

        # Build evaluation prompt
        prompt = f"""
You are an expert code quality evaluator. Evaluate the following agent code on 4 characteristics.
Each should be rated 0.0-1.0 (0=poor, 0.5=average, 1.0=excellent).

AGENT: {agent_name}
TASK SUCCESS: {task_success}
TASK: {request.task_name}

CODE SAMPLE (first 2000 chars):
{agent_code[:2000]}

Evaluate on these 4 characteristics:

1. **Correctness (0.0-1.0)**: Did the agent successfully complete the task? Is the logic sound? Are edge cases handled?
   - 1.0: Perfect correctness, task completed successfully
   - 0.8: Minor issues but task mostly complete
   - 0.5: Significant issues, incomplete task
   - 0.0: Failed or broken code

2. **Documentation (0.0-1.0)**: Is the code well-documented? Are there docstrings, comments, clear variable names?
   - 1.0: Excellent documentation, very clear
   - 0.8: Good documentation with most areas covered
   - 0.5: Basic documentation, some unclear parts
   - 0.0: No documentation or very unclear

3. **Testing Coverage (0.0-1.0)**: Are there tests? Do they pass? Is coverage adequate?
   - 1.0: Comprehensive tests with good coverage
   - 0.8: Good test coverage with minor gaps
   - 0.5: Some tests but incomplete
   - 0.0: No tests or tests fail

4. **Security (0.0-1.0)**: Is the code secure? Any vulnerabilities? Proper input validation?
   - 1.0: Very secure, proper validation and error handling
   - 0.8: Secure with minor concerns
   - 0.5: Some security risks identified
   - 0.0: Major security vulnerabilities

IMPORTANT: Return ONLY a valid JSON object with scores for each characteristic:
{{
  "correctness": 0.8,
  "documentation": 0.7,
  "testing_coverage": 0.9,
  "security": 0.85
}}

Do NOT include any other text or explanation.
"""

        # Call LLM
        try:
            response = await self._call_llm(prompt, task_success)
            scores = self._parse_scores(response)

            return {
                "scores": scores,
                "models_used": {self.primary_model: True}
            }

        except Exception as e:
            print(f"   ⚠️  Code Quality evaluation error: {e}")
            # Return default scores on error
            return {
                "scores": {
                    "correctness": 0.5,
                    "documentation": 0.5,
                    "testing_coverage": 0.5,
                    "security": 0.5,
                },
                "models_used": {}
            }

    async def _call_llm(self, prompt: str, task_success: bool) -> str:
        """Call LLM with fallback logic"""
        # Use NORMAL priority to route to free Gemini tier
        try:
            response = self.llm_router.call_llm(
                message=prompt,
                priority=TaskPriority.NORMAL,  # Routes to free Gemini
                max_retries=2
            )
            return response if response else ""
        except Exception as e:
            print(f"   ⚠️  Gemini error, trying local fallback: {e}")
            try:
                # Fallback to local phi4
                response = self.llm_router.call_llm(
                    message=prompt,
                    priority=TaskPriority.LOW,  # Routes to local only
                    max_retries=1
                )
                return response if response else ""
            except Exception as e2:
                print(f"   ❌ LLM error: {e2}")
                return ""

    def _get_agent_source(self, agent_name: str) -> str:
        """Get agent source code"""
        # Try multiple locations
        possible_paths = [
            self.base_path / "core" / f"{agent_name}.py",
            self.base_path / "core" / f"{agent_name.replace('terminator_', '')}.py",
            self.base_path / "agents" / f"{agent_name}.py",
            self.base_path / "integrations" / f"{agent_name}.py",
        ]

        for path in possible_paths:
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        return f.read()
                except Exception as e:
                    print(f"   ⚠️  Error reading {path}: {e}")

        # If not found, return empty string
        return ""

    def _parse_scores(self, response: str) -> Dict[str, float]:
        """Parse LLM response to extract scores"""
        scores = {
            "correctness": 0.5,
            "documentation": 0.5,
            "testing_coverage": 0.5,
            "security": 0.5,
        }

        if not response:
            return scores

        try:
            # Try to find and parse JSON
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                parsed = json.loads(json_str)

                # Extract scores with validation
                for key in scores.keys():
                    if key in parsed:
                        score = float(parsed[key])
                        scores[key] = max(0.0, min(1.0, score))  # Clamp 0-1

            return scores

        except Exception as e:
            print(f"   ⚠️  Error parsing scores: {e}")
            return scores


# Global instance
_evaluator = None

def get_code_quality_evaluator() -> CodeQualityEvaluator:
    """Get or create global instance"""
    global _evaluator
    if _evaluator is None:
        _evaluator = CodeQualityEvaluator()
    return _evaluator


# Example usage
if __name__ == "__main__":
    import asyncio

    evaluator = CodeQualityEvaluator()

    # Mock evaluation request
    class MockRequest:
        agent_name = "terminator_task_executor_agent"
        task_id = "TASK-001"
        task_name = "Execute critical task"
        success = True

    async def test():
        result = await evaluator.evaluate(MockRequest())
        print("Code Quality Evaluation Result:")
        print(json.dumps(result, indent=2))

    asyncio.run(test())
