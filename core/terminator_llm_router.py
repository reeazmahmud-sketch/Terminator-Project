#!/usr/bin/env python3
"""
TERMINATOR Unified LLM Router
==============================

Single interface for ALL LLM providers:
- Gemini (Google) - Fast, good for general tasks
- Claude (Anthropic) - Best reasoning
- OpenAI (GPT-4) - Versatile
- Grok (xAI) - Real-time knowledge
- Ollama (Local) - Offline fallback

Auto-detects best provider based on available API keys.
Supports both sync and async operations.
"""

import os
import sys
import asyncio
from typing import Optional, List, Dict, Any, AsyncGenerator
from dataclasses import dataclass
from enum import Enum

# Add project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class LLMProvider(Enum):
    """Available LLM providers"""
    GEMINI = "gemini"
    CLAUDE = "claude"
    OPENAI = "openai"
    GROK = "grok"
    OLLAMA = "ollama"


@dataclass
class LLMResponse:
    """Standardized response from any LLM"""
    content: str
    provider: LLMProvider
    model: str
    tokens_used: int = 0
    finish_reason: str = "complete"
    raw_response: Any = None


class TerminatorLLMRouter:
    """
    Unified LLM router with automatic provider selection.

    Usage:
        router = TerminatorLLMRouter()
        response = await router.chat("Hello, how are you?")
        print(response.content)
    """

    # Default models for each provider
    DEFAULT_MODELS = {
        LLMProvider.GEMINI: "gemini-2.0-flash-exp",
        LLMProvider.CLAUDE: "claude-3-5-sonnet-20241022",
        LLMProvider.OPENAI: "gpt-4o-mini",
        LLMProvider.GROK: "grok-2-latest",
        LLMProvider.OLLAMA: "llama3",
    }

    def __init__(self, preferred_provider: Optional[LLMProvider] = None):
        """
        Initialize the router.

        Args:
            preferred_provider: Force a specific provider (optional)
        """
        self.preferred_provider = preferred_provider
        self._provider = None
        self._clients = {}
        self._conversation_history: List[Dict[str, str]] = []

    def _get_secrets_manager(self):
        """Get the secrets manager"""
        try:
            from core.terminator_secrets_manager import get_secrets_manager
            return get_secrets_manager()
        except ImportError:
            return None

    def _detect_provider(self) -> LLMProvider:
        """Auto-detect the best available provider"""
        if self._provider:
            return self._provider

        if self.preferred_provider:
            self._provider = self.preferred_provider
            return self._provider

        secrets = self._get_secrets_manager()
        if secrets:
            from core.terminator_secrets_manager import SecretType

            # Priority order: Gemini > Claude > OpenAI > Grok > Ollama
            if secrets.get_secret(SecretType.GEMINI_API_KEY):
                self._provider = LLMProvider.GEMINI
            elif secrets.get_secret(SecretType.ANTHROPIC_API_KEY):
                self._provider = LLMProvider.CLAUDE
            elif secrets.get_secret(SecretType.OPENAI_API_KEY):
                self._provider = LLMProvider.OPENAI
            elif secrets.get_secret(SecretType.GROK_API_KEY):
                self._provider = LLMProvider.GROK
            else:
                self._provider = LLMProvider.OLLAMA
        else:
            # Check environment variables directly
            if os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY"):
                self._provider = LLMProvider.GEMINI
            elif os.environ.get("ANTHROPIC_API_KEY"):
                self._provider = LLMProvider.CLAUDE
            elif os.environ.get("OPENAI_API_KEY"):
                self._provider = LLMProvider.OPENAI
            else:
                self._provider = LLMProvider.OLLAMA

        return self._provider

    def get_current_provider(self) -> LLMProvider:
        """Get the currently active provider"""
        return self._detect_provider()

    def _get_api_key(self, provider: LLMProvider) -> Optional[str]:
        """Get API key for a provider"""
        secrets = self._get_secrets_manager()

        if provider == LLMProvider.GEMINI:
            if secrets:
                from core.terminator_secrets_manager import SecretType
                key = secrets.get_secret(SecretType.GEMINI_API_KEY)
                if key:
                    return key
            return os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")

        elif provider == LLMProvider.CLAUDE:
            if secrets:
                from core.terminator_secrets_manager import SecretType
                key = secrets.get_secret(SecretType.ANTHROPIC_API_KEY)
                if key:
                    return key
            return os.environ.get("ANTHROPIC_API_KEY")

        elif provider == LLMProvider.OPENAI:
            if secrets:
                from core.terminator_secrets_manager import SecretType
                key = secrets.get_secret(SecretType.OPENAI_API_KEY)
                if key:
                    return key
            return os.environ.get("OPENAI_API_KEY")

        elif provider == LLMProvider.GROK:
            if secrets:
                from core.terminator_secrets_manager import SecretType
                key = secrets.get_secret(SecretType.GROK_API_KEY)
                if key:
                    return key
            return os.environ.get("GROK_API_KEY") or os.environ.get("XAI_API_KEY")

        return None

    # =========================================================================
    # MAIN CHAT METHODS
    # =========================================================================

    async def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        use_history: bool = True
    ) -> LLMResponse:
        """
        Send a message and get a response.

        Args:
            message: User message
            system_prompt: Optional system prompt
            temperature: Creativity (0.0-1.0)
            max_tokens: Maximum response length
            use_history: Include conversation history

        Returns:
            LLMResponse with content and metadata
        """
        provider = self._detect_provider()

        # Add to history
        if use_history:
            self._conversation_history.append({"role": "user", "content": message})

        try:
            if provider == LLMProvider.GEMINI:
                response = await self._call_gemini(message, system_prompt, temperature, max_tokens, use_history)
            elif provider == LLMProvider.CLAUDE:
                response = await self._call_claude(message, system_prompt, temperature, max_tokens, use_history)
            elif provider == LLMProvider.OPENAI:
                response = await self._call_openai(message, system_prompt, temperature, max_tokens, use_history)
            elif provider == LLMProvider.GROK:
                response = await self._call_grok(message, system_prompt, temperature, max_tokens, use_history)
            else:
                response = await self._call_ollama(message, system_prompt, temperature, max_tokens, use_history)

            # Add response to history
            if use_history and response.content:
                self._conversation_history.append({"role": "assistant", "content": response.content})

            return response

        except Exception as e:
            # Fallback to Ollama on error
            if provider != LLMProvider.OLLAMA:
                print(f"[LLM Router] {provider.value} failed: {e}, falling back to Ollama")
                return await self._call_ollama(message, system_prompt, temperature, max_tokens, use_history)
            raise

    def chat_sync(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        use_history: bool = True
    ) -> LLMResponse:
        """Synchronous version of chat()"""
        return asyncio.run(self.chat(message, system_prompt, temperature, max_tokens, use_history))

    def clear_history(self):
        """Clear conversation history"""
        self._conversation_history = []

    # =========================================================================
    # PROVIDER-SPECIFIC IMPLEMENTATIONS
    # =========================================================================

    async def _call_gemini(
        self,
        message: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        use_history: bool
    ) -> LLMResponse:
        """Call Google Gemini API"""
        import google.generativeai as genai

        api_key = self._get_api_key(LLMProvider.GEMINI)
        if not api_key:
            raise ValueError("Gemini API key not found")

        genai.configure(api_key=api_key)

        model = genai.GenerativeModel(
            self.DEFAULT_MODELS[LLMProvider.GEMINI],
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
        )

        # Build prompt with history
        if use_history and self._conversation_history:
            history_text = "\n".join([
                f"{msg['role'].upper()}: {msg['content']}"
                for msg in self._conversation_history[:-1]  # Exclude current message
            ])
            full_prompt = f"{history_text}\nUSER: {message}"
        else:
            full_prompt = message

        if system_prompt:
            full_prompt = f"SYSTEM: {system_prompt}\n\n{full_prompt}"

        response = model.generate_content(full_prompt)

        return LLMResponse(
            content=response.text,
            provider=LLMProvider.GEMINI,
            model=self.DEFAULT_MODELS[LLMProvider.GEMINI],
            raw_response=response
        )

    async def _call_claude(
        self,
        message: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        use_history: bool
    ) -> LLMResponse:
        """Call Anthropic Claude API"""
        try:
            import anthropic
        except ImportError:
            import subprocess
            subprocess.run([sys.executable, "-m", "pip", "install", "anthropic"], capture_output=True)
            import anthropic

        api_key = self._get_api_key(LLMProvider.CLAUDE)
        if not api_key:
            raise ValueError("Claude API key not found")

        client = anthropic.Anthropic(api_key=api_key)

        # Build messages
        messages = []
        if use_history:
            messages = [msg for msg in self._conversation_history[:-1]]  # Exclude current
        messages.append({"role": "user", "content": message})

        response = client.messages.create(
            model=self.DEFAULT_MODELS[LLMProvider.CLAUDE],
            max_tokens=max_tokens,
            system=system_prompt or "You are TERMINATOR, a helpful AI assistant.",
            messages=messages
        )

        return LLMResponse(
            content=response.content[0].text,
            provider=LLMProvider.CLAUDE,
            model=self.DEFAULT_MODELS[LLMProvider.CLAUDE],
            tokens_used=response.usage.input_tokens + response.usage.output_tokens,
            finish_reason=response.stop_reason,
            raw_response=response
        )

    async def _call_openai(
        self,
        message: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        use_history: bool
    ) -> LLMResponse:
        """Call OpenAI API"""
        try:
            import openai
        except ImportError:
            import subprocess
            subprocess.run([sys.executable, "-m", "pip", "install", "openai"], capture_output=True)
            import openai

        api_key = self._get_api_key(LLMProvider.OPENAI)
        if not api_key:
            raise ValueError("OpenAI API key not found")

        client = openai.OpenAI(api_key=api_key)

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if use_history:
            messages.extend([msg for msg in self._conversation_history[:-1]])
        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model=self.DEFAULT_MODELS[LLMProvider.OPENAI],
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return LLMResponse(
            content=response.choices[0].message.content,
            provider=LLMProvider.OPENAI,
            model=self.DEFAULT_MODELS[LLMProvider.OPENAI],
            tokens_used=response.usage.total_tokens if response.usage else 0,
            finish_reason=response.choices[0].finish_reason,
            raw_response=response
        )

    async def _call_grok(
        self,
        message: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        use_history: bool
    ) -> LLMResponse:
        """Call xAI Grok API (OpenAI-compatible)"""
        try:
            import openai
        except ImportError:
            import subprocess
            subprocess.run([sys.executable, "-m", "pip", "install", "openai"], capture_output=True)
            import openai

        api_key = self._get_api_key(LLMProvider.GROK)
        if not api_key:
            raise ValueError("Grok API key not found")

        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if use_history:
            messages.extend([msg for msg in self._conversation_history[:-1]])
        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model=self.DEFAULT_MODELS[LLMProvider.GROK],
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return LLMResponse(
            content=response.choices[0].message.content,
            provider=LLMProvider.GROK,
            model=self.DEFAULT_MODELS[LLMProvider.GROK],
            tokens_used=response.usage.total_tokens if response.usage else 0,
            finish_reason=response.choices[0].finish_reason,
            raw_response=response
        )

    async def _call_ollama(
        self,
        message: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        use_history: bool
    ) -> LLMResponse:
        """Call local Ollama API"""
        import httpx

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if use_history:
            messages.extend([msg for msg in self._conversation_history[:-1]])
        messages.append({"role": "user", "content": message})

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": self.DEFAULT_MODELS[LLMProvider.OLLAMA],
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                }
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get("message", {}).get("content", "")
                return LLMResponse(
                    content=content,
                    provider=LLMProvider.OLLAMA,
                    model=self.DEFAULT_MODELS[LLMProvider.OLLAMA],
                    raw_response=data
                )
            else:
                raise Exception(f"Ollama returned status {response.status_code}")


# =========================================================================
# SINGLETON & CONVENIENCE FUNCTIONS
# =========================================================================

_router_instance: Optional[TerminatorLLMRouter] = None


def get_llm_router() -> TerminatorLLMRouter:
    """Get singleton router instance"""
    global _router_instance
    if _router_instance is None:
        _router_instance = TerminatorLLMRouter()
    return _router_instance


async def quick_chat(message: str, system_prompt: str = None) -> str:
    """Quick async chat - returns just the content"""
    router = get_llm_router()
    response = await router.chat(message, system_prompt, use_history=False)
    return response.content


def quick_chat_sync(message: str, system_prompt: str = None) -> str:
    """Quick sync chat - returns just the content"""
    return asyncio.run(quick_chat(message, system_prompt))


# =========================================================================
# CLI TEST
# =========================================================================

if __name__ == "__main__":
    async def main():
        print("=" * 60)
        print("TERMINATOR LLM ROUTER TEST")
        print("=" * 60)

        router = TerminatorLLMRouter()
        provider = router.get_current_provider()
        print(f"Detected Provider: {provider.value}")
        print(f"Model: {router.DEFAULT_MODELS[provider]}")
        print("-" * 60)

        # Test chat
        print("\nSending test message...")
        response = await router.chat(
            "What is 2+2? Reply in one word.",
            system_prompt="You are a helpful assistant. Be concise."
        )

        print(f"\nResponse: {response.content}")
        print(f"Provider: {response.provider.value}")
        print(f"Model: {response.model}")
        print(f"Tokens: {response.tokens_used}")

    asyncio.run(main())
