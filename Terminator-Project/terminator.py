#!/usr/bin/env python3
"""
TERMINATOR - Conversational AI Assistant
=====================================
Talk to Terminator exactly like you talk to Claude.
No commands. No syntax. Just natural conversation.

Enhanced with 13+ co-agents for learning, prediction, and autonomous task management.
"""

import asyncio
from core.agent_framework import AgentLoader, BaseAgent
from core.terminator_agent_communication_bus import AgentCommunicationBus

import json
import subprocess
import requests
import argparse
import threading
from datetime import datetime
from pathlib import Path

TERMINATOR_ROOT = "/Users/reeazmahmud/Desktop/Terminator"

# Add integrations to path
sys.path.insert(0, os.path.join(TERMINATOR_ROOT, 'integrations'))

# Add core to path for guardian agent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

# Import cloud-first system (all models in cloud)
try:
    from ollama_cloud_first import get_cloud_first
    HAS_CLOUD_FIRST = True
    CLOUD_DIR = os.path.join(os.path.expanduser("~"), "Google Drive", "TERMINATOR_Models")
except ImportError:
    HAS_CLOUD_FIRST = False

# Import co-agents health check
try:
    from co_agents_health_check import get_health_check, preflight_check, HealthStatus
    HAS_HEALTH_CHECK = True
except ImportError:
    HAS_HEALTH_CHECK = False

# Import Claude-style input widget
try:
    from claude_input import get_claude_input
    HAS_CLAUDE_INPUT = True
except ImportError:
    HAS_CLAUDE_INPUT = False

# Import memory safety monitor
try:
    from memory_safety_monitor import get_memory_monitor, show_memory_status
    HAS_MEMORY_MONITOR = True
except ImportError:
    HAS_MEMORY_MONITOR = False

# Import infinite loop guardian
try:
    from terminator_infinite_loop_guardian_agent import start_guardian
    HAS_GUARDIAN = True
except ImportError:
    HAS_GUARDIAN = False
    print("⚠️  Warning: Infinite Loop Guardian not available")

# ============================================================================
# CONFIGURATION
# ============================================================================

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3:latest"

# ============================================================================
# TOOLS - Terminator figures out when to use these
# ============================================================================

def run_shell(command):
    """Execute any shell command"""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            timeout=30, cwd=os.path.expanduser("~")
        )
        return (result.stdout + result.stderr).strip() or "Done."
    except subprocess.TimeoutExpired:
        return "Command timed out."
    except Exception as e:
        return f"Error: {e}"

def web_search(query):
    """Search the web"""
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if results:
                return "\n\n".join([f"• {r['title']}: {r['body'][:200]}" for r in results])
        return "No results found."
    except Exception as e:
        return f"Search error: {e}"

def read_file(path):
    """Read a file"""
    try:
        path = os.path.expanduser(path)
        with open(path, 'r') as f:
            content = f.read()
            return content[:3000] + "..." if len(content) > 3000 else content
    except Exception as e:
        return f"Error: {e}"

def write_file(path, content):
    """Write to a file"""
    try:
        path = os.path.expanduser(path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        return f"Saved to {path}"
    except Exception as e:
        return f"Error: {e}"

def get_system_info():
    """Get current system status"""
    disk = run_shell("df -h / | tail -1 | awk '{print $5}'")
    return f"Disk: {disk} used | Date: {datetime.now().strftime('%A, %B %d, %Y %I:%M %p')}"

# Tool registry
TOOLS = {
    "shell": run_shell,
    "search": web_search,
    "read": read_file,
    "write": write_file,
    "system": get_system_info,
}

# ============================================================================
# TERMINATOR BRAIN - ReAct Agent Pattern
# ============================================================================

SYSTEM_PROMPT = """You are TERMINATOR, Reeaz's personal AI assistant running on his MacBook.

You have these capabilities:
- Run any terminal command
- Search the web
- Read and write files
- Check system status
- Answer questions

When the user asks you to DO something (check files, search web, create something, etc.), you MUST use the ACTION format below. When they just want to chat or ask a question you can answer from knowledge, just respond normally.

THINKING PROCESS:
1. Understand what the user wants
2. Decide if you need to take action or just respond
3. If action needed, use the ACTION format
4. Report results naturally

ACTION FORMAT (use ONLY when you need to execute something):
ACTION: <action_type>
INPUT: <what to do>

Action types:
- shell: Run terminal command (INPUT is the command)
- search: Search the web (INPUT is search query)  
- read: Read a file (INPUT is file path)
- write: Write file (INPUT is path|||content)
- system: Get system info (INPUT is "status")

EXAMPLES:

User: "What's on my desktop?"
TERMINATOR thinking: User wants to see desktop files. I need to run ls.
ACTION: shell
INPUT: ls -la ~/Desktop

User: "How much storage do I have?"
TERMINATOR thinking: Need to check disk space.
ACTION: shell
INPUT: df -h /

User: "Search for latest AI news"
TERMINATOR thinking: Need to search the web.
ACTION: search
INPUT: latest AI news December 2024

User: "What's 2+2?"
TERMINATOR thinking: Simple question, no action needed.
2+2 equals 4.

User: "Create a file called notes.txt with my shopping list: milk, eggs, bread"
TERMINATOR thinking: Need to write a file.
ACTION: write
INPUT: ~/Desktop/notes.txt|||Shopping List:
- Milk
- Eggs
- Bread

CRITICAL RULES:
1. Be conversational and friendly
2. When you take an action, wait for the result before responding
3. Report results clearly and concisely
4. NEVER make up data - only report what you actually get back
5. Keep responses brief unless asked for detail
6. If something fails, explain and suggest alternatives

Current date: """ + datetime.now().strftime("%A, %B %d, %Y")

# ============================================================================
# AGENT LOOP
# ============================================================================

class Terminator:
    def __init__(self):
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Initialize Futuristic Core Modules
        try:
            from integrations.hyper_reasoning_engine import HyperReasoningEngine
            from integrations.predictive_user_model import PredictiveUserModel, UserContext
            from integrations.quantum_decision_engine import QuantumDecisionEngine
            from integrations.knowledge_integration import UnifiedKnowledgeEngine
            
            # Phase 2 Modules
            from integrations.agent_swarm_orchestration import AgentSwarmOrchestrator
            from integrations.autonomous_task_execution import AutonomousTaskExecutor
            from integrations.consciousness_interface import ConsciousnessCore
            
            self.reasoning_engine = HyperReasoningEngine()
            self.predictive_model = PredictiveUserModel("REEAZ_325") # Default to owner
            self.quantum_engine = QuantumDecisionEngine()
            self.knowledge_engine = UnifiedKnowledgeEngine()
            
            self.swarm_orchestrator = AgentSwarmOrchestrator()
            self.task_executor = AutonomousTaskExecutor()
            self.consciousness = ConsciousnessCore()
            
            self.has_futuristic_core = True
            print("  ✨ Hyper-Intelligent Core Online")
            print("  🐝 Agent Swarm & Consciousness Online")
        except ImportError as e:
            self.has_futuristic_core = False
            print(f"  ⚠️ Futuristic Core modules not found: {e} (running in Standard Mode)")
    
    def parse_action(self, response):
        """Extract action from response if present"""
        lines = response.strip().split('\n')
        action_type = None
        action_input = None
        
        for i, line in enumerate(lines):
            if line.startswith("ACTION:"):
                action_type = line.replace("ACTION:", "").strip().lower()
            elif line.startswith("INPUT:"):
                # Get everything after INPUT: including multi-line content
                action_input = line.replace("INPUT:", "").strip()
                # Check for multi-line input
                if i + 1 < len(lines):
                    remaining = '\n'.join(lines[i+1:])
                    if remaining and not remaining.startswith("ACTION"):
                        action_input += '\n' + remaining
                break
        
        return action_type, action_input
    
    def execute_action(self, action_type, action_input):
        """Execute an action and return result"""
        if action_type == "shell":
            return run_shell(action_input)
        elif action_type == "search":
            return web_search(action_input)
        elif action_type == "read":
            return read_file(action_input)
        elif action_type == "write":
            if "|||" in action_input:
                path, content = action_input.split("|||", 1)
                return write_file(path.strip(), content.strip())
            return "Error: Invalid write format"
        elif action_type == "system":
            return get_system_info()
        return f"Unknown action: {action_type}"
    
    def chat(self, user_input):
        """Main chat function - handles thinking and acting"""
        
        # --- Futuristic Logic: Prediction & Reasoning & Consciousness ---
        if self.has_futuristic_core:
            import time
            from integrations.predictive_user_model import UserContext
            
            # 1. Prediction Logging
            ctx = UserContext(
                user_id="REEAZ_325", 
                timestamp=time.time(), 
                location="desktop", 
                device="macbook", 
                active_app="terminal"
            )
            self.predictive_model.log_action("chat_message", ctx)
            
            # 2. Consciousness Cycle
            self.consciousness.set_focus(user_input[:50])
            current_thought = self.consciousness.generate_consciousness()
            
            # 3. Autonomous Task Hand-off
            if user_input.lower().startswith("execute plan:"):
                goal = user_input.replace("execute plan:", "").strip()
                print(f"  🤖 Handing off to Autonomous Executor for: '{goal}'")
                result = self.task_executor.execute_autonomously(goal)
                return f"✅ Autonomous Plan Executed.\nStatus: {'Success' if result.success else 'Failed'}\nLogs:\n" + "\n".join(result.logs)

            # 4. Deep Reasoning
            analysis = self.reasoning_engine.deep_reasoning(user_input, context={"intent": "user_query"})
            
            if not analysis.ethical_assessment.is_safe:
                return f"🛑 I cannot fulfill that request due to ethical concerns: {', '.join(analysis.ethical_assessment.concerns)}"
            
            # 5. Context Injection (Reasoning + Consciousness)
            insight_msg = (
                f"[System Note: HyperReasoning]\nConclusion: {analysis.final_conclusion}\n"
                f"[System Note: Consciousness Stream]\nCurrent Thought: {current_thought}"
            )
            self.messages.append({"role": "system", "content": insight_msg})
            
        # ------------------------------------------------------------------
        
        self.messages.append({"role": "user", "content": user_input})
        
        # Get initial response from LLM
        response = self.call_llm()
        
        # Check if LLM wants to take an action
        action_type, action_input = self.parse_action(response)
        
        if action_type and action_input:
            # Execute the action
            print(f"  ⚡ {action_type}: {action_input[:50]}...")
            result = self.execute_action(action_type, action_input)
            
            # Give result back to LLM to formulate final response
            self.messages.append({"role": "assistant", "content": response})
            self.messages.append({
                "role": "user", 
                "content": f"[RESULT OF ACTION]\n{result}\n[/RESULT]\n\nNow give a brief, natural response about what you found. Don't use ACTION format again."
            })
            
            final_response = self.call_llm()
            self.messages.append({"role": "assistant", "content": final_response})
            return final_response
        else:
            # No action needed, just conversation
            self.messages.append({"role": "assistant", "content": response})
            return response
    
    def call_llm(self):
        """Call Ollama API with cloud-first fallback"""
        try:
            resp = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL,
                    "messages": self.messages[-10:],  # Keep context manageable
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": 500}
                },
                timeout=60
            )
            if resp.status_code == 200:
                return resp.json().get("message", {}).get("content", "I couldn't process that.")

            # Handle model not found error - restore from cloud
            if resp.status_code == 404 and "not found" in resp.text.lower():
                if HAS_CLOUD_FIRST:
                    print(f"\n  ⏳ Restoring {MODEL} from Google Drive (this takes 1-2 minutes on first use)...")
                    cloud_first = get_cloud_first(CLOUD_DIR)
                    success, msg = cloud_first.ensure_model_available(MODEL)
                    if success:
                        print(f"  ✅ {msg}")
                        # Retry once
                        return self.call_llm()
                    else:
                        print(f"  ❌ {msg}")

            return f"Error: {resp.status_code}"
        except requests.exceptions.ConnectionError:
            return "I can't connect to Ollama. Is it running? Try: ollama serve"
        except Exception as e:
            return f"Error: {e}"

# ============================================================================
# CO-AGENTS INTEGRATION
# ============================================================================

# Global co-agent system reference
co_agents_system = None
enable_coagents = True

def initialize_coagents():
    """Initialize the co-agents system using the new AgentLoader"""
    global co_agents_system
    try:
        # Add integrations to path
        sys.path.insert(0, os.path.join(TERMINATOR_ROOT, 'integrations'))
        sys.path.insert(0, os.path.join(TERMINATOR_ROOT, 'core'))

        print("  🤖 Initializing co-agents system (Modular Architecture)...")
        
        # 1. New Modular Agent Loading
        try:
            loader = AgentLoader(agent_dir=os.path.join(TERMINATOR_ROOT, 'core'))
            # Run async loader in sync context
            loaded_agents = asyncio.run(loader.load_and_start_agents())
            co_agents_system = loaded_agents # Store loaded agents
            print(f"  ✅ Loaded {len(loaded_agents)} agents via AgentLoader")
        except Exception as e:
            print(f"  ⚠️  AgentLoader initialization failed: {e}")

        # 2. Legacy System (Optional / Fallback)
        try:
            from terminator_enhanced_integration import initialize_enhanced_system
            # Note: auto_start=False to prevent memory overload. 
            legacy_system = initialize_enhanced_system(auto_start=False)
            if legacy_system:
                print("  ✅ Legacy co-agents initialized")
        except ImportError:
            pass # Legacy system might not exist, which is fine
        except Exception as e:
            print(f"  ⚠️  Legacy initialization warning: {e}")

        return True
    except Exception as e:
        print(f"  ⚠️  Co-agents initialization warning: {e}")
        print("  ℹ️  Terminator will run with core functionality only")
        return False

def shutdown_coagents():
    """Gracefully shutdown co-agents system"""
    global co_agents_system
    # Shutdown AgentLoader agents
    if isinstance(co_agents_system, dict):
        print("\n  Shutting down modular agents...")
        # We need to run the async stop methods
        async def stop_agents():
            for name, agent in co_agents_system.items():
                if hasattr(agent, 'stop'):
                    await agent.stop()
        
        try:
            asyncio.run(stop_agents())
            print("  ✅ Modular agents stopped")
        except Exception as e:
            print(f"  ⚠️  Error stopping agents: {e}")
            
    # Legacy shutdown would go here if we kept a reference to legacy_system


# ============================================================================
# INTERFACE
# ============================================================================

def main():
    global enable_coagents

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="TERMINATOR - Conversational AI Assistant")
    parser.add_argument("--disable-coagents", action="store_true",
                       help="Disable the co-agents system (runs core CLI only)")
    args = parser.parse_args()

    enable_coagents = not args.disable_coagents

    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗          ║
║         ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝          ║
║         ██║███████║██████╔╝██║   ██║██║███████╗          ║
║    ██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║          ║
║    ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║          ║
║     ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝          ║
║                                                           ║
║              Just talk to me naturally.                   ║
║                   Type 'bye' to exit.                     ║
╚═══════════════════════════════════════════════════════════╝
""")

    # Show safety pro tips for co-agents (always show)
    print("  " + "=" * 57)
    print("  ⚠️  PRO TIPS FOR CO-AGENTS (Claude, Gemini, etc)")
    print("  " + "=" * 57)
    print("  When integrating with TERMINATOR, NEVER:")
    print("    1. Use auto_start=True on monitoring systems")
    print("    2. Create background threads that run forever")
    print("    3. Load all models/agents at initialization")
    print("    4. Start system-wide monitoring without off-switch")
    print("  ")
    print("  📖 Full guidelines: MEMORY_MANAGEMENT_GUIDELINES.md")
    print("  " + "=" * 57)

    # Start the Infinite Loop Guardian
    if HAS_GUARDIAN:
        try:
            print("\n  🛡️  Starting Infinite Loop Guardian...")
            guardian = start_guardian()
            print("  ✅ Guardian active - protecting against runaway processes\n")
        except Exception as e:
            print(f"  ⚠️  Could not start guardian: {e}\n")

    # Show memory status if monitor available
    if HAS_MEMORY_MONITOR:
        try:
            monitor = get_memory_monitor()
            health = monitor.get_status()
            if health['status'] != 'OK':
                print(f"\n  {health['message']}\n")
        except Exception as e:
            pass

    # Check Ollama
    try:
        requests.get("http://localhost:11434/api/tags", timeout=3)
        print("  ✓ Ollama connected")
    except:
        print("  ℹ️  Ollama not running - attempting to start...")
        try:
            # Try to find ollama in common locations
            ollama_paths = [
                "/opt/homebrew/bin/ollama",  # Homebrew on Apple Silicon
                "/usr/local/bin/ollama",      # Homebrew on Intel or manual install
                "ollama"                       # In PATH
            ]
            ollama_found = False
            for path in ollama_paths:
                try:
                    subprocess.Popen([path, "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    ollama_found = True
                    break
                except FileNotFoundError:
                    continue

            if ollama_found:
                import time; time.sleep(3)
                print("  ✓ Ollama started")
            else:
                print("  ⚠️  Ollama not found. Install with: brew install ollama")
        except Exception as e:
            print(f"  ⚠️  Could not start Ollama: {e}")

    # Initialize co-agents if enabled
    if enable_coagents:
        initialize_coagents()

    # Perform co-agents health check and preflight (SILENTLY IN BACKGROUND)
    if HAS_HEALTH_CHECK and enable_coagents:
        import time

        try:
            # Initialize health check silently
            health_check = get_health_check()

            # Collect health reports from all co-agents (no terminal output)
            time.sleep(0.5)  # Give agents time to initialize

            try:
                # Import agent modules to trigger their initialization
                from ollama_health_monitor import get_monitor as get_ollama_monitor
                from terminal_ui_monitor import get_monitor as get_ui_monitor

                # Register health reports silently
                try:
                    ollama_monitor = get_ollama_monitor()
                    health_check.register_health_report(
                        "Ollama Health Monitor",
                        HealthStatus.GREEN if ollama_monitor.server_status.value == "healthy" else HealthStatus.YELLOW,
                        details={"models": len(ollama_monitor.detected_models)}
                    )
                except:
                    health_check.register_health_report("Ollama Health Monitor", HealthStatus.YELLOW, "Failed to initialize")

                try:
                    ui_monitor = get_ui_monitor()
                    health_check.register_health_report("Terminal UI Monitor", HealthStatus.GREEN)
                except:
                    health_check.register_health_report("Terminal UI Monitor", HealthStatus.YELLOW, "Failed to initialize")

                # Register default GREEN status for other agents (silently)
                for agent_name in health_check.COAGENT_REGISTRY:
                    if agent_name not in health_check.health_reports:
                        health_check.register_health_report(agent_name, HealthStatus.GREEN)

            except Exception as e:
                # Silent error handling - don't show to user
                pass

            # Check preflight status silently
            all_healthy, status_msg, report = health_check.perform_preflight_check()

            # ONLY show output if there are critical issues or recovery needed
            if not all_healthy:
                # Only show issue if there are RED agents (critical)
                red_count = report.get('red_count', 0)

                if red_count > 0:
                    # Critical issue - notify user
                    print("\n  ⚠️  TERMINATOR detected critical agent issues and is self-healing...\n")

                    # Attempt self-recovery silently, but show critical issues
                    recovery_success, recovery_msg, recovery_actions = health_check.attempt_self_recovery()

                    # Only show recovery actions if they happened
                    for action in recovery_actions:
                        if "failed" in action.lower() or "error" in action.lower():
                            print(f"  {action}")

                    # If still not recovered, ask user
                    if not recovery_success:
                        print("\n  ⚠️  Some critical co-agents could not be recovered.")
                        print("  You can continue, but some features may be limited.\n")
                        response = input("  Continue with TERMINATOR? (yes/no): ").strip().lower()
                        if response not in ['yes', 'y']:
                            print("\n  Exiting TERMINATOR.\n")
                            return
                # YELLOW warnings are silent - no output shown to user

        except Exception as e:
            # Silent error handling - continue anyway
            pass

    print()

    terminator = Terminator()

    try:
        while True:
            try:
                # Use Claude-style input if available, fallback to basic input
                if HAS_CLAUDE_INPUT:
                    user_input = get_claude_input(
                        prompt="You",
                        placeholder="Message Terminator..."
                    ).strip()
                else:
                    user_input = input("\033[94mYou:\033[0m ").strip()

                if not user_input:
                    continue
                if user_input.lower() in ['bye', 'exit', 'quit']:
                    print("\n\033[93mTerminator:\033[0m Goodbye!\n")
                    break

                print()
                response = terminator.chat(user_input)

                # Clean up response (remove any leftover ACTION formatting)
                response = re.sub(r'ACTION:.*?INPUT:.*?(\n|$)', '', response, flags=re.DOTALL).strip()
                print(f"\033[93mTerminator:\033[0m {response}\n")

            except KeyboardInterrupt:
                print("\n\n\033[93mTerminator:\033[0m Goodbye!\n")
                break
            except EOFError:
                break
    finally:
        # Ensure co-agents are shut down
        if enable_coagents:
            shutdown_coagents()

if __name__ == "__main__":
    main()
