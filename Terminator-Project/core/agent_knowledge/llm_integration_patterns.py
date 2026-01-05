"""
TERMINATOR Agent Knowledge Module: LLM Integration Patterns
============================================================

This module contains learned patterns for LLM integration that agents
can reference when building or debugging LLM-powered features.

Knowledge Source: FIX-001 (2024-12-18)
- Issue: Universal CLI not responding to natural language
- Root Cause: Placeholder code, no actual LLM call
- Resolution: Implemented proper Ollama integration

Agents can import this module to:
1. Get working LLM integration code patterns
2. Diagnose LLM connectivity issues
3. Validate their own LLM implementations
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# =============================================================================
# CONFIGURATION PATTERNS
# =============================================================================

class LLMConfig:
    """Standard LLM configuration for TERMINATOR components"""

    # Ollama (Local, Default)
    OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
    OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
    OLLAMA_DEFAULT_MODEL = "llama3:latest"

    # Timeouts
    DEFAULT_TIMEOUT = 60.0  # seconds
    FIRST_LOAD_TIMEOUT = 120.0  # First model load takes longer

    # Context management
    MAX_HISTORY_MESSAGES = 10  # Keep last N messages for context
    MAX_TOKENS = 500  # Default max response tokens

    @classmethod
    def get_ollama_url(cls) -> str:
        """Get Ollama URL, allowing environment override"""
        return os.environ.get("OLLAMA_URL", cls.OLLAMA_CHAT_URL)

    @classmethod
    def get_model(cls) -> str:
        """Get model name, allowing environment override"""
        return os.environ.get("OLLAMA_MODEL", cls.OLLAMA_DEFAULT_MODEL)


# =============================================================================
# LLM INTEGRATION PATTERN (PROVEN WORKING)
# =============================================================================

class LLMIntegrationPattern:
    """
    Working LLM integration pattern extracted from FIX-001.

    Usage:
        llm = LLMIntegrationPattern()
        response = llm.chat("Hello, how are you?")
        print(response)

    Agents building new features should use this pattern as reference.
    """

    def __init__(self, model: str = None, system_prompt: str = None):
        self.model = model or LLMConfig.get_model()
        self.url = LLMConfig.get_ollama_url()
        self.messages: List[Dict[str, str]] = []

        # Initialize with system prompt
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})
        else:
            self.messages.append({
                "role": "system",
                "content": "You are TERMINATOR, an advanced AI assistant. Be helpful and concise."
            })

    def chat(self, user_input: str) -> str:
        """
        Send message to LLM and get response.

        This is the CORRECT pattern - actually calls the API and returns response.

        ANTI-PATTERN (what NOT to do):
            print("Processing...")  # This does nothing!

        CORRECT PATTERN (what TO do):
            response = self.chat(user_input)
            print(response)
        """
        try:
            import httpx
        except ImportError:
            return "Error: httpx not installed. Run: pip install httpx"

        # Add user message to history
        self.messages.append({"role": "user", "content": user_input})

        try:
            with httpx.Client(timeout=LLMConfig.DEFAULT_TIMEOUT) as client:
                response = client.post(
                    self.url,
                    json={
                        "model": self.model,
                        "messages": self.messages[-LLMConfig.MAX_HISTORY_MESSAGES:],
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "num_predict": LLMConfig.MAX_TOKENS
                        }
                    }
                )

                if response.status_code == 200:
                    assistant_message = (
                        response.json()
                        .get("message", {})
                        .get("content", "I couldn't process that.")
                    )
                    # Add to history for context
                    self.messages.append({"role": "assistant", "content": assistant_message})
                    return assistant_message

                elif response.status_code == 404:
                    return f"Error: Model '{self.model}' not found. Run: ollama pull {self.model}"

                else:
                    return f"Error: Ollama returned status {response.status_code}"

        except Exception as e:
            return self._handle_error(e)

    def _handle_error(self, error: Exception) -> str:
        """Convert exceptions to user-friendly messages"""
        error_type = type(error).__name__

        error_messages = {
            "ConnectError": "Cannot connect to Ollama. Is it running? (ollama serve)",
            "TimeoutException": "Request timed out. Model may be loading - try again.",
            "ReadTimeout": "Read timeout. The model is taking too long.",
        }

        return f"Error: {error_messages.get(error_type, str(error))}"

    def clear_history(self):
        """Clear conversation history, keeping system prompt"""
        system_msg = self.messages[0] if self.messages else None
        self.messages = [system_msg] if system_msg else []


# =============================================================================
# DIAGNOSTIC UTILITIES
# =============================================================================

@dataclass
class DiagnosticResult:
    """Result of a diagnostic check"""
    check_name: str
    passed: bool
    message: str
    details: Optional[Dict[str, Any]] = None


class LLMDiagnostics:
    """
    Diagnostic utilities for LLM connectivity.

    Agents can use these to verify LLM is working before attempting operations.
    """

    @staticmethod
    def check_ollama_running() -> DiagnosticResult:
        """Check if Ollama process is running"""
        import subprocess

        result = subprocess.run(['pgrep', '-l', 'ollama'], capture_output=True, text=True)
        if result.stdout.strip():
            return DiagnosticResult(
                check_name="Ollama Process",
                passed=True,
                message="Ollama is running",
                details={"process": result.stdout.strip()}
            )
        return DiagnosticResult(
            check_name="Ollama Process",
            passed=False,
            message="Ollama not running. Start with: ollama serve"
        )

    @staticmethod
    def check_ollama_api() -> DiagnosticResult:
        """Check if Ollama API is responding"""
        try:
            import httpx

            response = httpx.get(
                "http://localhost:11434/api/tags",
                timeout=5.0
            )

            if response.status_code == 200:
                models = response.json().get("models", [])
                return DiagnosticResult(
                    check_name="Ollama API",
                    passed=True,
                    message=f"API responding. {len(models)} models available.",
                    details={"models": [m["name"] for m in models]}
                )
        except Exception as e:
            pass

        return DiagnosticResult(
            check_name="Ollama API",
            passed=False,
            message="Cannot reach Ollama API at localhost:11434"
        )

    @staticmethod
    def check_model_available(model: str = None) -> DiagnosticResult:
        """Check if specific model is available"""
        model = model or LLMConfig.get_model()

        try:
            import httpx

            response = httpx.get("http://localhost:11434/api/tags", timeout=5.0)

            if response.status_code == 200:
                models = [m["name"] for m in response.json().get("models", [])]

                # Check exact match or base name match
                if model in models or model.split(":")[0] in [m.split(":")[0] for m in models]:
                    return DiagnosticResult(
                        check_name=f"Model '{model}'",
                        passed=True,
                        message=f"Model {model} is available"
                    )

                return DiagnosticResult(
                    check_name=f"Model '{model}'",
                    passed=False,
                    message=f"Model {model} not found. Run: ollama pull {model}",
                    details={"available_models": models}
                )
        except Exception as e:
            pass

        return DiagnosticResult(
            check_name=f"Model '{model}'",
            passed=False,
            message="Cannot check model availability"
        )

    @staticmethod
    def run_all_checks() -> List[DiagnosticResult]:
        """Run all diagnostic checks"""
        return [
            LLMDiagnostics.check_ollama_running(),
            LLMDiagnostics.check_ollama_api(),
            LLMDiagnostics.check_model_available(),
        ]

    @staticmethod
    def print_diagnostics():
        """Print diagnostic results to console"""
        print("=" * 50)
        print("TERMINATOR LLM Diagnostics")
        print("=" * 50)

        results = LLMDiagnostics.run_all_checks()
        passed = 0

        for result in results:
            status = "PASS" if result.passed else "FAIL"
            print(f"\n[{status}] {result.check_name}")
            print(f"      {result.message}")
            if result.details:
                for key, value in result.details.items():
                    print(f"      {key}: {value}")
            if result.passed:
                passed += 1

        print("\n" + "=" * 50)
        print(f"Results: {passed}/{len(results)} checks passed")
        print("=" * 50)

        return passed == len(results)


# =============================================================================
# ANTI-PATTERNS (What NOT to do)
# =============================================================================

class LLMAntiPatterns:
    """
    Document of anti-patterns discovered through debugging.

    Agents should review these to avoid common mistakes.
    """

    ANTI_PATTERNS = {
        "placeholder_only": {
            "description": "Code that prints status but doesn't actually call LLM",
            "bad_code": '''
                # BAD - This does nothing useful!
                print("Processing...")
                # TODO: integrate with LLM
            ''',
            "good_code": '''
                # GOOD - Actually calls the LLM
                response = self.call_llm(user_input)
                print(response)
            ''',
            "lesson": "TODO comments don't execute. Implement the actual functionality."
        },

        "missing_error_handling": {
            "description": "LLM calls without try/except",
            "bad_code": '''
                # BAD - Will crash on any error
                response = client.post(url, json=data)
                return response.json()["message"]["content"]
            ''',
            "good_code": '''
                # GOOD - Handles errors gracefully
                try:
                    response = client.post(url, json=data)
                    if response.status_code == 200:
                        return response.json().get("message", {}).get("content", "")
                except Exception as e:
                    return f"Error: {e}"
            ''',
            "lesson": "LLM calls can fail for many reasons. Always handle errors."
        },

        "wrong_response_path": {
            "description": "Incorrect JSON path to extract response",
            "bad_code": '''
                # BAD - Wrong path for /api/chat endpoint
                content = response.json()["response"]  # This is for /api/generate
            ''',
            "good_code": '''
                # GOOD - Correct path for /api/chat endpoint
                content = response.json()["message"]["content"]

                # OR for /api/generate endpoint
                content = response.json()["response"]
            ''',
            "lesson": "Different endpoints have different response structures."
        },

        "no_conversation_history": {
            "description": "Not maintaining context between messages",
            "bad_code": '''
                # BAD - Each message is isolated
                def chat(self, msg):
                    return call_llm([{"role": "user", "content": msg}])
            ''',
            "good_code": '''
                # GOOD - Maintains conversation context
                def chat(self, msg):
                    self.messages.append({"role": "user", "content": msg})
                    response = call_llm(self.messages[-10:])
                    self.messages.append({"role": "assistant", "content": response})
                    return response
            ''',
            "lesson": "Maintain message history for coherent conversations."
        }
    }

    @classmethod
    def get_anti_pattern(cls, name: str) -> Optional[Dict]:
        """Get specific anti-pattern by name"""
        return cls.ANTI_PATTERNS.get(name)

    @classmethod
    def list_anti_patterns(cls) -> List[str]:
        """List all documented anti-patterns"""
        return list(cls.ANTI_PATTERNS.keys())


# =============================================================================
# AGENT LEARNING INTERFACE
# =============================================================================

def teach_agent_llm_integration():
    """
    Entry point for agents to learn LLM integration patterns.

    Call this function to get a summary of best practices.
    """
    return {
        "summary": "LLM Integration Best Practices for TERMINATOR Agents",
        "key_points": [
            "Always use httpx or requests for HTTP calls to Ollama",
            "Ollama chat endpoint: http://localhost:11434/api/chat",
            "Response path for chat: response.json()['message']['content']",
            "Maintain conversation history for context (last 10 messages)",
            "Handle ConnectError, TimeoutException, and HTTP errors",
            "Include system prompt for consistent agent personality",
            "Test with LLMDiagnostics.run_all_checks() before deploying",
        ],
        "reference_implementation": "LLMIntegrationPattern class in this module",
        "troubleshooting_doc": "docs/troubleshooting/LLM_NOT_RESPONDING.md",
        "fix_history": "docs/fixes/FIX_001_LLM_INTEGRATION_UNIVERSAL_CLI.md",
    }


# =============================================================================
# QUICK TEST
# =============================================================================

if __name__ == "__main__":
    # Run diagnostics
    print("\n=== Running Diagnostics ===\n")
    LLMDiagnostics.print_diagnostics()

    # Show learning summary
    print("\n=== Agent Learning Summary ===\n")
    learning = teach_agent_llm_integration()
    print(f"Topic: {learning['summary']}\n")
    print("Key Points:")
    for i, point in enumerate(learning['key_points'], 1):
        print(f"  {i}. {point}")

    # Test LLM if diagnostics pass
    print("\n=== Testing LLM Integration ===\n")
    llm = LLMIntegrationPattern()
    response = llm.chat("Say 'Hello, I am working correctly!' in exactly those words.")
    print(f"LLM Response: {response}")
