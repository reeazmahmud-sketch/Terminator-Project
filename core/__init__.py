"""
TERMINATOR Core Module
======================

Contains all core agents, routers, and communication systems.
"""

from core.terminator_secrets_manager import get_secrets_manager, SecretType, TerminatorSecretsManager
from core.terminator_llm_router import get_llm_router, TerminatorLLMRouter, LLMProvider, LLMResponse
from core.terminator_cli_agent import get_cli_agent, TerminatorCLIAgent, chat, chat_sync

__all__ = [
    # Secrets
    'get_secrets_manager',
    'SecretType',
    'TerminatorSecretsManager',

    # LLM Router
    'get_llm_router',
    'TerminatorLLMRouter',
    'LLMProvider',
    'LLMResponse',

    # CLI Agent
    'get_cli_agent',
    'TerminatorCLIAgent',
    'chat',
    'chat_sync',
]
