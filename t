#!/usr/bin/env python3
"""
TERMINATOR - Quick Command (New Architecture)
==============================================

Just type 't' in terminal to start.

Uses the new module-based architecture with:
- Auto-detected LLM provider (Gemini/Claude/OpenAI/Grok/Ollama)
- Unified agent system
- Auto-solution coding agent

Usage:
    t                    # Interactive CLI
    t "your question"    # Quick query
    t --status           # Show status
    t --set-key gemini   # Set API key
    t --solve "problem"  # Auto-solve coding problem
"""

import os
import sys
import asyncio
import argparse

# Add current directory to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)


def show_banner():
    """Show startup banner"""
    from rich.console import Console
    from rich.panel import Panel

    console = Console()

    # Get provider info
    try:
        from core.terminator_llm_router import get_llm_router
        router = get_llm_router()
        provider = router.get_current_provider()
        model = router.DEFAULT_MODELS[provider]
        provider_text = f"[cyan]{provider.value}[/cyan] ({model})"
    except:
        provider_text = "[yellow]ollama[/yellow] (local)"

    console.print(Panel(
        f"[bold red]TERMINATOR[/bold red] [dim]- New Architecture[/dim]\n\n"
        f"Provider: {provider_text}\n"
        f"[dim]Type /help for commands • /status for info • exit to quit[/dim]",
        title="🤖",
        border_style="red"
    ))


async def interactive_mode():
    """Run interactive CLI"""
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown

    console = Console()
    show_banner()

    # Import CLI agent
    from core.terminator_cli_agent import get_cli_agent
    agent = get_cli_agent()

    while True:
        try:
            # Prompt
            console.print()
            user_input = console.input("[bold red]>[/bold red] ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "/exit", "/quit"]:
                console.print("[dim]Goodbye![/dim]")
                break

            # Process input
            console.print("[dim]Processing...[/dim]")
            response = await agent.process_input(user_input)

            # Display response
            console.print(Panel(
                Markdown(response),
                title="TERMINATOR",
                border_style="green"
            ))

        except KeyboardInterrupt:
            console.print("\n[dim]Use 'exit' to quit.[/dim]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="TERMINATOR - Autonomous AI Agent (New Architecture)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  t                        # Start interactive CLI
  t "Hello"                # Quick query
  t --status               # Show system status
  t --set-key gemini       # Set API key
  t --solve "Fix the bug"  # Auto-solve coding problem
        """
    )

    parser.add_argument("query", nargs="?", help="Query to process")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--set-key", metavar="PROVIDER", help="Set API key")
    parser.add_argument("--solve", metavar="PROBLEM", help="Auto-solve problem")

    args = parser.parse_args()

    # Handle --status
    if args.status:
        from core.terminator_llm_router import get_llm_router
        from core.terminator_secrets_manager import get_secrets_manager, SecretType

        router = get_llm_router()
        secrets = get_secrets_manager()
        provider = router.get_current_provider()

        print("=" * 50)
        print("TERMINATOR STATUS (New Architecture)")
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
            status = "✓ SET" if key else "✗ NOT SET"
            print(f"{name}: {status}")
        print()
        print("Commands: t --set-key <provider> to add API key")
        return

    # Handle --set-key
    if args.set_key:
        import getpass
        from core.terminator_secrets_manager import get_secrets_manager, SecretType

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
            print(f"✓ {provider.title()} API key saved!")
            print(f"Run 't --status' to verify.")
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

        print(f"\n✓ Success: {result['success']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Iterations: {result['iterations']}")
        print(f"  Files Modified: {', '.join(result['files_modified']) or 'None'}")
        print(f"\nSolution:\n{result['solution']}")
        return

    # Handle single query
    if args.query:
        from core.terminator_cli_agent import get_cli_agent
        agent = get_cli_agent()
        response = await agent.process_input(args.query)
        print(response)
        return

    # Interactive mode
    await interactive_mode()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
