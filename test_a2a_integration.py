#!/usr/bin/env python3
"""
Test script for Terminator A2A Protocol Integration
"""

import asyncio
import aiohttp
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


async def test_list_agents():
    """Test listing all agents"""
    console.print("\n[bold cyan]Test 1: List All Agents[/bold cyan]")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8001/a2a/agents") as response:
                if response.status == 200:
                    data = await response.json()

                    table = Table(title="Available A2A Agents")
                    table.add_column("Agent Name", style="cyan")
                    table.add_column("Description", style="green")
                    table.add_column("Capabilities", style="yellow")

                    for agent in data.get("agents", []):
                        capabilities = ", ".join(agent.get("capabilities", [])[:3])
                        if len(agent.get("capabilities", [])) > 3:
                            capabilities += "..."

                        table.add_row(
                            agent.get("name", ""),
                            agent.get("description", "")[:50] + "...",
                            capabilities
                        )

                    console.print(table)
                    console.print(f"[green]✓ Found {len(data.get('agents', []))} agents[/green]")
                    return True
                else:
                    console.print(f"[red]✗ Failed with status {response.status}[/red]")
                    return False
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        console.print("[yellow]Make sure A2A server is running: ./start_a2a_server.sh[/yellow]")
        return False


async def test_get_agent_card():
    """Test getting a specific agent card"""
    console.print("\n[bold cyan]Test 2: Get Agent Card[/bold cyan]")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "http://localhost:8001/a2a/agents/advanced_orchestrator/card"
            ) as response:
                if response.status == 200:
                    card = await response.json()

                    console.print(Panel(
                        json.dumps(card, indent=2),
                        title="Advanced Orchestrator Card",
                        border_style="green"
                    ))
                    console.print("[green]✓ Agent card retrieved successfully[/green]")
                    return True
                else:
                    console.print(f"[red]✗ Failed with status {response.status}[/red]")
                    return False
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        return False


async def test_agent_call():
    """Test calling an agent via JSON-RPC"""
    console.print("\n[bold cyan]Test 3: Agent Call (JSON-RPC)[/bold cyan]")

    rpc_request = {
        "jsonrpc": "2.0",
        "method": "agent.call",
        "params": {
            "agent": "task_executor",
            "message": "Perform a system health check"
        },
        "id": 1
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8001/a2a/rpc",
                json=rpc_request
            ) as response:
                if response.status == 200:
                    result = await response.json()

                    console.print(Panel(
                        json.dumps(result, indent=2),
                        title="JSON-RPC Response",
                        border_style="green"
                    ))
                    console.print("[green]✓ Agent call successful[/green]")
                    return True
                else:
                    console.print(f"[red]✗ Failed with status {response.status}[/red]")
                    return False
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        return False


async def test_discover_agents():
    """Test agent discovery by capabilities"""
    console.print("\n[bold cyan]Test 4: Discover Agents by Capability[/bold cyan]")

    discovery_request = {
        "capabilities": ["error_detection", "auto_recovery"]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8001/a2a/discover",
                json=discovery_request
            ) as response:
                if response.status == 200:
                    result = await response.json()

                    console.print(Panel(
                        json.dumps(result, indent=2),
                        title="Discovery Results",
                        border_style="green"
                    ))
                    console.print(f"[green]✓ Found {len(result.get('agents', []))} matching agents[/green]")
                    return True
                else:
                    console.print(f"[red]✗ Failed with status {response.status}[/red]")
                    return False
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        return False


async def test_task_create():
    """Test creating a long-running task"""
    console.print("\n[bold cyan]Test 5: Create Task[/bold cyan]")

    rpc_request = {
        "jsonrpc": "2.0",
        "method": "task.create",
        "params": {
            "agent": "task_executor",
            "description": "Monitor system resources for 1 hour"
        },
        "id": 2
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8001/a2a/rpc",
                json=rpc_request
            ) as response:
                if response.status == 200:
                    result = await response.json()

                    console.print(Panel(
                        json.dumps(result, indent=2),
                        title="Task Creation Response",
                        border_style="green"
                    ))

                    task_id = result.get("result", {}).get("task_id")
                    if task_id:
                        # Test task status
                        await asyncio.sleep(0.5)

                        status_request = {
                            "jsonrpc": "2.0",
                            "method": "task.status",
                            "params": {"task_id": task_id},
                            "id": 3
                        }

                        async with session.post(
                            "http://localhost:8001/a2a/rpc",
                            json=status_request
                        ) as status_response:
                            if status_response.status == 200:
                                status_result = await status_response.json()
                                console.print(Panel(
                                    json.dumps(status_result, indent=2),
                                    title="Task Status",
                                    border_style="blue"
                                ))

                    console.print("[green]✓ Task created successfully[/green]")
                    return True
                else:
                    console.print(f"[red]✗ Failed with status {response.status}[/red]")
                    return False
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        return False


async def main():
    """Run all tests"""
    console.print(Panel(
        "[bold]Terminator A2A Protocol Integration Tests[/bold]\n\n"
        "Testing Agent2Agent (A2A) protocol implementation",
        border_style="cyan",
        padding=(1, 2)
    ))

    tests = [
        ("List Agents", test_list_agents),
        ("Get Agent Card", test_get_agent_card),
        ("Agent Call", test_agent_call),
        ("Discover Agents", test_discover_agents),
        ("Create Task", test_task_create),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            console.print(f"[red]Test '{test_name}' crashed: {e}[/red]")
            results.append((test_name, False))

    # Summary
    console.print("\n" + "="*60)
    console.print("[bold]Test Summary[/bold]")
    console.print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[green]✓ PASS[/green]" if result else "[red]✗ FAIL[/red]"
        console.print(f"{status} - {test_name}")

    console.print(f"\n[bold]Results: {passed}/{total} tests passed[/bold]")

    if passed == total:
        console.print("[bold green]All tests passed! A2A integration is working correctly.[/bold green]")
    else:
        console.print("[bold yellow]Some tests failed. Check the output above for details.[/bold yellow]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Tests interrupted by user[/yellow]")
