#!/usr/bin/env python3
"""
TERMINATOR - New Architecture
=============================

Uses the proper module-based agent architecture with:
- Unified LLM Router (Gemini/Claude/OpenAI/Grok/Ollama)
- CLI Agent with tool execution
- Auto-solution coding agent
- Secrets management

Usage:
    python3 terminator_new.py              # Interactive CLI
    python3 terminator_new.py "message"    # Single query
    python3 terminator_new.py --status     # Show status
"""

import os
import sys
import asyncio
import argparse

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="TERMINATOR - Autonomous AI Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 terminator_new.py                    # Start interactive CLI
  python3 terminator_new.py "Hello"            # Quick query
  python3 terminator_new.py --status           # Show system status
  python3 terminator_new.py --set-key gemini   # Set API key
        """
    )

    parser.add_argument("query", nargs="?", help="Optional query to process")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--set-key", metavar="PROVIDER", help="Set API key for provider")
    parser.add_argument("--provider", help="Force specific LLM provider")
    parser.add_argument("--solve", metavar="PROBLEM", help="Auto-solve a coding problem")

    args = parser.parse_args()

    # Import after path setup
    from core.terminator_llm_router import get_llm_router, LLMProvider
    from core.terminator_cli_agent import get_cli_agent, run_cli
    from core.terminator_secrets_manager import get_secrets_manager, SecretType

    # Handle --status
    if args.status:
        router = get_llm_router()
        secrets = get_secrets_manager()
        provider = router.get_current_provider()

        print("=" * 50)
        print("TERMINATOR STATUS")
        print("=" * 50)
        print(f"Provider: {provider.value}")
        print(f"Model: {router.DEFAULT_MODELS[provider]}")
        print(f"Project: {PROJECT_ROOT}")
        print()
        print("API Keys:")
        for name, secret_type in [
            ("  Gemini", SecretType.GEMINI_API_KEY),
            ("  Claude", SecretType.ANTHROPIC_API_KEY),
            ("  OpenAI", SecretType.OPENAI_API_KEY),
            ("  Grok", SecretType.GROK_API_KEY),
        ]:
            key = secrets.get_secret(secret_type)
            status = "SET" if key else "NOT SET"
            print(f"{name}: {status}")
        return

    # Handle --set-key
    if args.set_key:
        import getpass
        secrets = get_secrets_manager()
        provider_map = {
            "gemini": SecretType.GEMINI_API_KEY,
            "claude": SecretType.ANTHROPIC_API_KEY,
            "openai": SecretType.OPENAI_API_KEY,
            "grok": SecretType.GROK_API_KEY,
        }
        provider = args.set_key.lower()
        if provider not in provider_map:
            print(f"Unknown provider: {provider}")
            print(f"Available: {', '.join(provider_map.keys())}")
            return

        key = getpass.getpass(f"Enter {provider.title()} API key: ")
        if key:
            secrets.set_secret(provider_map[provider], key)
            print(f"{provider.title()} API key saved!")
        return

    # Handle --solve
    if args.solve:
        from core.terminator_auto_solution_agent import solve_coding_problem
        print("=" * 50)
        print("TERMINATOR AUTO-SOLVE")
        print("=" * 50)
        print(f"Problem: {args.solve}")
        print("-" * 50)

        result = await solve_coding_problem(args.solve, PROJECT_ROOT)

        print(f"\nSuccess: {result['success']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Iterations: {result['iterations']}")
        print(f"Files Modified: {', '.join(result['files_modified']) or 'None'}")
        print(f"\nSolution:\n{result['solution']}")

        if result['errors']:
            print("\nErrors:")
            for e in result['errors']:
                print(f"  - {e[:100]}")
        return

    # Handle single query
    if args.query:
        agent = get_cli_agent()

        # Set provider if specified
        if args.provider:
            try:
                provider = LLMProvider(args.provider.lower())
                agent._router.preferred_provider = provider
                agent._router._provider = provider
            except ValueError:
                print(f"Unknown provider: {args.provider}")
                return

        response = await agent.process_input(args.query)
        print(response)
        return

    # Interactive mode
    await run_cli()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
