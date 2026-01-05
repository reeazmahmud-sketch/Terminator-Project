"""
TERMINATOR Agent Knowledge Base
===============================

This package contains learned patterns, fixes, and best practices
that agents can reference when building or debugging features.

Modules:
- llm_integration_patterns: LLM integration best practices and diagnostics

Usage:
    from core.agent_knowledge import LLMIntegrationPattern, LLMDiagnostics

    # Quick LLM client
    llm = LLMIntegrationPattern()
    response = llm.chat("Hello")

    # Run diagnostics
    LLMDiagnostics.print_diagnostics()
"""

from .llm_integration_patterns import (
    LLMConfig,
    LLMIntegrationPattern,
    LLMDiagnostics,
    LLMAntiPatterns,
    DiagnosticResult,
    teach_agent_llm_integration,
)

__all__ = [
    "LLMConfig",
    "LLMIntegrationPattern",
    "LLMDiagnostics",
    "LLMAntiPatterns",
    "DiagnosticResult",
    "teach_agent_llm_integration",
]
