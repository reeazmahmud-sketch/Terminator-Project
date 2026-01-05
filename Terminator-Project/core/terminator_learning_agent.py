#!/usr/bin/env python3
"""
TERMINATOR Learning Agent
=========================

An agent that LEARNS new capabilities by:
1. Searching the web for tutorials, documentation, Stack Overflow
2. Consulting external AIs (Gemini, Claude, etc.) for code generation
3. Building a knowledge base of learned patterns
4. Teaching other agents what it learns

Instead of saying "I don't know," this agent says "Let me learn that!"
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime


class LearningAgent:
    """
    An autonomous learning agent that acquires new capabilities on-demand.
    """

    def __init__(self):
        self.knowledge_base_path = Path.home() / ".terminator_knowledge"
        self.knowledge_base_path.mkdir(exist_ok=True)
        self.learned_capabilities = self.knowledge_base_path / "capabilities.json"
        self.load_knowledge_base()

    def load_knowledge_base(self):
        """Load previously learned capabilities"""
        if self.learned_capabilities.exists():
            with open(self.learned_capabilities) as f:
                self.knowledge = json.load(f)
        else:
            self.knowledge = {
                "tutorials": [],
                "code_snippets": [],
                "api_integrations": [],
                "external_ai_consultations": [],
                "stack_overflow_solutions": []
            }

    def save_knowledge(self):
        """Persist learned knowledge"""
        with open(self.learned_capabilities, 'w') as f:
            json.dump(self.knowledge, f, indent=2)

    def learn_from_web(self, topic: str, query: str) -> str:
        """
        Search the web to learn how to implement something.

        Strategy:
        1. Search for "how to [topic] in python"
        2. Look for Stack Overflow, official docs, tutorials
        3. Extract code examples and patterns
        4. Save to knowledge base
        """
        import httpx

        search_query = f"{topic} python tutorial example"
        learning_results = {
            "topic": topic,
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "sources": [],
            "code_examples": [],
            "implementation_strategy": ""
        }

        # Search for resources
        search_sources = [
            f"https://stackoverflow.com/search?q={topic.replace(' ', '+')}+python",
            f"https://www.google.com/search?q={search_query.replace(' ', '+')}",
            f"https://pypi.org/search/?q={topic.replace(' ', '+')}"
        ]

        learning_results["sources"] = search_sources

        # For now, create a learning template
        learning_plan = f"""
📚 LEARNING PLAN: {topic}

SEARCH QUERIES TO RUN:
1. "{search_query}"
2. "python {topic} library"
3. "{topic} code example github"

RESOURCES TO CHECK:
- Stack Overflow: {search_sources[0]}
- Google Search: {search_sources[1]}
- PyPI: {search_sources[2]}

LEARNING STEPS:
1. Find the most popular Python library for {topic}
2. Read the documentation or README
3. Extract code examples
4. Adapt examples to TERMINATOR's tool format
5. Test the implementation
6. Add to permanent toolset

CONSULTATION QUESTION FOR CLAUDE CODE:
"I found resources about {topic}. Can you help me create a tool
implementation based on common patterns? The tool should integrate
with TERMINATOR's AgenticTools class."
"""

        self.knowledge["tutorials"].append(learning_results)
        self.save_knowledge()

        return learning_plan

    def consult_external_ai(self, ai_service: str, question: str) -> str:
        """
        Call external AI APIs (Gemini, Claude, ChatGPT) for guidance.

        This creates a network of AI agents helping each other!
        """
        import httpx

        consultation = {
            "service": ai_service,
            "question": question,
            "timestamp": datetime.now().isoformat()
        }

        # Check for API keys
        api_keys = {
            "gemini": os.getenv("GOOGLE_API_KEY"),
            "claude": os.getenv("ANTHROPIC_API_KEY"),
            "openai": os.getenv("OPENAI_API_KEY")
        }

        if ai_service.lower() in api_keys and api_keys[ai_service.lower()]:
            api_key = api_keys[ai_service.lower()]

            if ai_service.lower() == "gemini":
                return self._call_gemini(question, api_key)
            elif ai_service.lower() == "claude":
                return self._call_claude(question, api_key)
            elif ai_service.lower() == "openai":
                return self._call_openai(question, api_key)

        # If no API key, return instructions for manual consultation
        result = f"""
🤖 EXTERNAL AI CONSULTATION: {ai_service}

QUESTION: {question}

To enable automatic consultation, set API key:
- Gemini: export GOOGLE_API_KEY="your-key"
- Claude: export ANTHROPIC_API_KEY="your-key"
- OpenAI: export OPENAI_API_KEY="your-key"

MANUAL CONSULTATION:
1. Go to {self._get_ai_url(ai_service)}
2. Ask: "{question}"
3. Get implementation code
4. Use TERMINATOR's self-modification to add it

WHAT TO ASK:
"I'm building a tool for an autonomous AI agent called TERMINATOR.
I need Python code for: {question}

Please provide:
1. Complete Python function
2. Required imports/packages
3. Error handling
4. Usage example

The code should fit into a class method with this signature:
def tool_name(self, **params) -> str:
    # implementation
    return result_string
"
"""

        self.knowledge["external_ai_consultations"].append(consultation)
        self.save_knowledge()
        return result

    def _get_ai_url(self, service: str) -> str:
        urls = {
            "gemini": "https://gemini.google.com",
            "claude": "https://claude.ai",
            "openai": "https://chat.openai.com",
            "perplexity": "https://www.perplexity.ai",
            "grok": "https://grok.x.com"
        }
        return urls.get(service.lower(), "https://google.com")

    def _call_gemini(self, question: str, api_key: str) -> str:
        """Call Gemini API for guidance"""
        import httpx
        try:
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
            headers = {"Content-Type": "application/json"}
            data = {
                "contents": [{
                    "parts": [{
                        "text": f"You are helping TERMINATOR, an autonomous AI agent, learn a new capability. {question}\n\nProvide Python code that can be integrated as a tool method."
                    }]
                }]
            }

            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{url}?key={api_key}",
                    headers=headers,
                    json=data
                )

                if response.status_code == 200:
                    result = response.json()
                    text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    return f"🤖 Gemini Response:\n\n{text}"
                else:
                    return f"❌ Gemini API error: {response.status_code}"
        except Exception as e:
            return f"❌ Error calling Gemini: {e}"

    def _call_claude(self, question: str, api_key: str) -> str:
        """Call Claude API for guidance"""
        import httpx
        try:
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            }
            data = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 4096,
                "messages": [{
                    "role": "user",
                    "content": f"You are helping TERMINATOR, an autonomous AI agent, learn a new capability. {question}\n\nProvide Python code that can be integrated as a tool method."
                }]
            }

            with httpx.Client(timeout=60.0) as client:
                response = client.post(url, headers=headers, json=data)

                if response.status_code == 200:
                    result = response.json()
                    text = result.get("content", [{}])[0].get("text", "")
                    return f"🤖 Claude Response:\n\n{text}"
                else:
                    return f"❌ Claude API error: {response.status_code}"
        except Exception as e:
            return f"❌ Error calling Claude: {e}"

    def _call_openai(self, question: str, api_key: str) -> str:
        """Call OpenAI API for guidance"""
        import httpx
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            data = {
                "model": "gpt-4",
                "messages": [{
                    "role": "user",
                    "content": f"You are helping TERMINATOR, an autonomous AI agent, learn a new capability. {question}\n\nProvide Python code that can be integrated as a tool method."
                }]
            }

            with httpx.Client(timeout=60.0) as client:
                response = client.post(url, headers=headers, json=data)

                if response.status_code == 200:
                    result = response.json()
                    text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    return f"🤖 OpenAI Response:\n\n{text}"
                else:
                    return f"❌ OpenAI API error: {response.status_code}"
        except Exception as e:
            return f"❌ Error calling OpenAI: {e}"

    def extract_code_from_response(self, ai_response: str) -> Optional[str]:
        """Extract Python code from AI response"""
        # Look for code blocks
        code_pattern = r"```python\n(.*?)\n```"
        matches = re.findall(code_pattern, ai_response, re.DOTALL)
        if matches:
            return matches[0]
        return None

    def create_learning_sub_agent(self, topic: str) -> str:
        """
        Spawn a sub-agent dedicated to learning a specific topic.

        This sub-agent will:
        1. Search the web for resources
        2. Consult multiple AIs
        3. Synthesize the best approach
        4. Report back with implementation
        """
        learning_plan = f"""
🎓 LEARNING SUB-AGENT SPAWNED

MISSION: Learn how to implement {topic}

STRATEGY:
1. Web Research Phase
   - Search Stack Overflow for existing solutions
   - Find official library documentation
   - Look for tutorial blog posts
   - Check GitHub for code examples

2. AI Consultation Phase
   - Ask Gemini for implementation approach
   - Ask Claude for code review
   - Cross-reference responses

3. Synthesis Phase
   - Combine best practices from all sources
   - Adapt to TERMINATOR's architecture
   - Add error handling and validation

4. Implementation Phase
   - Create tool method
   - Add to CLI
   - Test with examples
   - Document in knowledge base

5. Reporting Phase
   - Report back to main agent
   - Share knowledge with other agents
   - Mark capability as "learned"

STATUS: Researching... (this would run autonomously in background)
"""
        return learning_plan


def create_learning_tool():
    """Create a tool for TERMINATOR to learn new capabilities"""
    agent = LearningAgent()

    def learn(topic: str, method: str = "web") -> str:
        if method == "web":
            return agent.learn_from_web(topic, f"How to {topic}")
        elif method == "ai":
            return agent.consult_external_ai("gemini", f"How do I implement {topic} in Python for an autonomous agent?")
        elif method == "sub_agent":
            return agent.create_learning_sub_agent(topic)
        else:
            return f"❌ Unknown learning method: {method}"

    return learn


if __name__ == "__main__":
    # Demo
    agent = LearningAgent()
    print("🎓 TERMINATOR Learning Agent Demo\n")

    # Example: Learn YouTube video processing
    result = agent.learn_from_web(
        "extract youtube video metadata and transcript",
        "How can I get YouTube video info?"
    )
    print(result)
