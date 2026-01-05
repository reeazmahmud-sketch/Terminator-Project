# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
Terminator Agentic Orchestrator
===========================

Autonomous reasoning loop that handles complex queries by:
1. Analyzing the query to determine what tools are needed
2. Automatically calling appropriate tools to gather information
3. Processing results and deciding if more information is needed
4. Iterating until sufficient information is gathered
5. Returning comprehensive final answer

This enables seamless multi-step research without user intervention.
"""

import sys
import os
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.mobile_network_query_agent import get_mobile_network_agent
from integrations.github_integration import get_github_integration
from llm_system.INTELLIGENT_LLM_ROUTER import (
    call_normal_task,
    call_critical_task,
    IntelligentLLMRouter,
    TaskPriority
)


class ToolType(Enum):
    """Available tool types"""
    # iOS tools
    IOS_GET_TEXT = "ios_get_text"
    IOS_GET_CLIPBOARD = "ios_get_clipboard"
    IOS_RUN_SHORTCUT = "ios_run_shortcut"
    IOS_CHECK_STATUS = "ios_check_status"
    # Android tools
    ANDROID_GET_TEXT = "android_get_text"
    ANDROID_GET_CLIPBOARD = "android_get_clipboard"
    ANDROID_RUN_COMMAND = "android_run_command"
    ANDROID_CHECK_STATUS = "android_check_status"
    ANDROID_LAUNCH_APP = "android_launch_app"
    # Network tools
    NETWORK_SCAN = "network_scan"
    NETWORK_LIST_DEVICES = "network_list_devices"
    NETWORK_FIND_APPLE_DEVICES = "network_find_apple_devices"
    NETWORK_FIND_ANDROID_DEVICES = "network_find_android_devices"
    NETWORK_FIND_DEVICE_NAME = "network_find_device_name"
    NETWORK_FIND_DEVICE_IP = "network_find_device_ip"
    NETWORK_FIND_BY_TYPE = "network_find_by_type"
    NETWORK_SUMMARY = "network_summary"
    # GitHub tools
    GITHUB_PUSH_PROJECT = "github_push_project"
    GITHUB_CREATE_PR = "github_create_pr"
    GITHUB_SEARCH_PROJECTS = "github_search_projects"
    GITHUB_ANALYZE_PROJECT = "github_analyze_project"
    GITHUB_TRIGGER_WORKFLOW = "github_trigger_workflow"
    # Other tools
    WEB_SEARCH = "web_search"
    CODE_EXECUTION = "code_execution"


class ToolCall:
    """Represents a tool call to execute"""

    def __init__(self, tool_type: ToolType, **kwargs):
        self.tool_type = tool_type
        self.params = kwargs
        self.result = None
        self.executed = False

    def __repr__(self):
        return f"ToolCall({self.tool_type.value}, {self.params})"


class TerminatorAgenticOrchestrator:
    """
    Autonomous agent orchestrator that reasons about queries and executes tools
    """

    def __init__(self, max_iterations: int = 5):
        self.mobile_agent = get_mobile_network_agent()
        self.github_integration = get_github_integration()
        self.router = IntelligentLLMRouter()
        self.max_iterations = max_iterations
        self.conversation_history = []
        self.tool_calls_made = []

    def _extract_intent(self, query: str) -> List[str]:
        """Use LLM to extract intent from query"""
        prompt = f"""Analyze this query and determine what the user wants.

Query: {query}

Respond with a list of intents (one per line):
- What specific information is being requested?
- What is the user trying to accomplish?
- What tools might be needed?

Keep it concise."""

        response = call_normal_task(prompt)
        return response.split('\n')

    def _determine_tools(self, query: str) -> List[ToolCall]:
        """Determine which tools need to be called"""
        query_lower = query.lower()
        tools = []

        # iOS tools
        if any(keyword in query_lower for keyword in ["iphone", "ipad", "ios", "ios device"]):
            if "clipboard" in query_lower:
                tools.append(ToolCall(ToolType.IOS_GET_CLIPBOARD, device_name="My iPhone"))
            elif "text" in query_lower and ("get" in query_lower or "extract" in query_lower):
                tools.append(ToolCall(ToolType.IOS_GET_TEXT, device_name="My iPhone", app_name="Notes"))
            elif "shortcut" in query_lower or "run" in query_lower:
                tools.append(ToolCall(ToolType.IOS_RUN_SHORTCUT, device_name="My iPhone", shortcut_name=""))
            elif "status" in query_lower or "online" in query_lower or "connected" in query_lower:
                tools.append(ToolCall(ToolType.IOS_CHECK_STATUS))

        # Android tools
        if any(keyword in query_lower for keyword in ["android", "samsung", "pixel", "android device"]):
            if "clipboard" in query_lower:
                tools.append(ToolCall(ToolType.ANDROID_GET_CLIPBOARD, device_id=""))
            elif "text" in query_lower and ("get" in query_lower or "extract" in query_lower):
                tools.append(ToolCall(ToolType.ANDROID_GET_TEXT, device_id="", app_package="com.google.android.apps.docs"))
            elif "command" in query_lower or "shell" in query_lower:
                tools.append(ToolCall(ToolType.ANDROID_RUN_COMMAND, device_id="", command=""))
            elif "app" in query_lower and "launch" in query_lower:
                tools.append(ToolCall(ToolType.ANDROID_LAUNCH_APP, device_id="", app_package=""))
            elif "status" in query_lower or "online" in query_lower or "connected" in query_lower:
                tools.append(ToolCall(ToolType.ANDROID_CHECK_STATUS))

        # Network tools
        if any(keyword in query_lower for keyword in ["network", "devices", "wifi", "connected", "home network"]):
            if "scan" in query_lower:
                tools.append(ToolCall(ToolType.NETWORK_SCAN))
            elif "list" in query_lower or "all" in query_lower:
                tools.append(ToolCall(ToolType.NETWORK_LIST_DEVICES))
            elif "apple" in query_lower or ("iphone" in query_lower and "network" in query_lower):
                tools.append(ToolCall(ToolType.NETWORK_FIND_APPLE_DEVICES))
            elif "android" in query_lower or ("android" in query_lower and "network" in query_lower):
                tools.append(ToolCall(ToolType.NETWORK_FIND_ANDROID_DEVICES))
            elif "find" in query_lower or "search" in query_lower:
                tools.append(ToolCall(ToolType.NETWORK_FIND_DEVICE_NAME, hostname=""))
            elif "summary" in query_lower or "overview" in query_lower:
                tools.append(ToolCall(ToolType.NETWORK_SUMMARY))

        # GitHub tools
        # Check for direct GitHub keywords OR GitHub-related operation keywords with context
        github_keywords = ["github", "push", "pull request", "pr", "repository", "repo", "open source"]
        operation_keywords = ["push", "upload", "pull request", "pr", "search", "find", "analyze", "review"]
        workflow_keywords = ["workflow", "action", "ci", "cd", "ci/cd", "pipeline"]
        context_keywords = ["github", "repository", "repo", "open source", "python", "framework", "library", "project"]

        is_github_query = (
            any(keyword in query_lower for keyword in github_keywords) or
            (any(keyword in query_lower for keyword in operation_keywords) and
             any(context in query_lower for context in context_keywords)) or
            (any(keyword in query_lower for keyword in workflow_keywords) and
             any(context in query_lower for context in ["github", "my", "project", "repository", "repo"]))
        )

        if is_github_query:
            if "push" in query_lower or "upload" in query_lower:
                tools.append(ToolCall(ToolType.GITHUB_PUSH_PROJECT, repo_path=""))
            elif "pull request" in query_lower or " pr " in query_lower:
                tools.append(ToolCall(ToolType.GITHUB_CREATE_PR, repo="", title="", body="", head_branch="", base_branch="main"))
            elif "search" in query_lower or "find" in query_lower or "similar" in query_lower:
                tools.append(ToolCall(ToolType.GITHUB_SEARCH_PROJECTS, keywords=[]))
            elif "analyze" in query_lower or "review" in query_lower or "examine" in query_lower:
                tools.append(ToolCall(ToolType.GITHUB_ANALYZE_PROJECT, owner="", repo=""))
            elif "workflow" in query_lower or "action" in query_lower or "ci" in query_lower or "pipeline" in query_lower:
                tools.append(ToolCall(ToolType.GITHUB_TRIGGER_WORKFLOW, repo="", workflow_id=""))

        return tools

    def _execute_tool(self, tool_call: ToolCall) -> str:
        """Execute a specific tool and return result"""
        try:
            # iOS tools
            if tool_call.tool_type == ToolType.IOS_GET_TEXT:
                return self.mobile_agent.get_ios_device_text(
                    tool_call.params.get("device_name", "My iPhone"),
                    tool_call.params.get("app_name", "Notes")
                )

            elif tool_call.tool_type == ToolType.IOS_GET_CLIPBOARD:
                return self.mobile_agent.get_ios_clipboard(
                    tool_call.params.get("device_name", "My iPhone")
                )

            elif tool_call.tool_type == ToolType.IOS_RUN_SHORTCUT:
                return self.mobile_agent.run_ios_shortcut(
                    tool_call.params.get("device_name", "My iPhone"),
                    tool_call.params.get("shortcut_name", ""),
                    tool_call.params.get("input_data")
                )

            elif tool_call.tool_type == ToolType.IOS_CHECK_STATUS:
                return self.mobile_agent.check_ios_devices_status()

            # Android tools
            elif tool_call.tool_type == ToolType.ANDROID_GET_TEXT:
                return self.mobile_agent.get_android_device_text(
                    tool_call.params.get("device_id", ""),
                    tool_call.params.get("app_package", "com.google.android.apps.docs")
                )

            elif tool_call.tool_type == ToolType.ANDROID_GET_CLIPBOARD:
                return self.mobile_agent.get_android_clipboard(
                    tool_call.params.get("device_id", "")
                )

            elif tool_call.tool_type == ToolType.ANDROID_RUN_COMMAND:
                return self.mobile_agent.run_android_command(
                    tool_call.params.get("device_id", ""),
                    tool_call.params.get("command", "")
                )

            elif tool_call.tool_type == ToolType.ANDROID_CHECK_STATUS:
                return self.mobile_agent.check_android_devices_status()

            elif tool_call.tool_type == ToolType.ANDROID_LAUNCH_APP:
                return self.mobile_agent.launch_android_app(
                    tool_call.params.get("device_id", ""),
                    tool_call.params.get("app_package", "")
                )

            # Network tools
            elif tool_call.tool_type == ToolType.NETWORK_SCAN:
                return self.mobile_agent.scan_network()

            elif tool_call.tool_type == ToolType.NETWORK_LIST_DEVICES:
                return self.mobile_agent.list_network_devices()

            elif tool_call.tool_type == ToolType.NETWORK_FIND_APPLE_DEVICES:
                return self.mobile_agent.get_apple_devices()

            elif tool_call.tool_type == ToolType.NETWORK_FIND_ANDROID_DEVICES:
                return self.mobile_agent.get_android_devices_on_network()

            elif tool_call.tool_type == ToolType.NETWORK_FIND_DEVICE_NAME:
                return self.mobile_agent.find_device_by_name(
                    tool_call.params.get("hostname", "")
                )

            elif tool_call.tool_type == ToolType.NETWORK_FIND_DEVICE_IP:
                return self.mobile_agent.find_device_by_ip(
                    tool_call.params.get("ip", "")
                )

            elif tool_call.tool_type == ToolType.NETWORK_FIND_BY_TYPE:
                return self.mobile_agent.get_network_devices_by_type(
                    tool_call.params.get("device_type", "")
                )

            elif tool_call.tool_type == ToolType.NETWORK_SUMMARY:
                return self.mobile_agent.get_network_summary()

            # GitHub tools
            elif tool_call.tool_type == ToolType.GITHUB_PUSH_PROJECT:
                repo_path = tool_call.params.get("repo_path", "")
                success, msg = self.github_integration.push_project(repo_path)
                return msg

            elif tool_call.tool_type == ToolType.GITHUB_CREATE_PR:
                repo = tool_call.params.get("repo", "")
                title = tool_call.params.get("title", "")
                body = tool_call.params.get("body", "")
                head_branch = tool_call.params.get("head_branch", "")
                base_branch = tool_call.params.get("base_branch", "main")
                success, msg = self.github_integration.create_pull_request(
                    repo, title, body, head_branch, base_branch
                )
                return msg

            elif tool_call.tool_type == ToolType.GITHUB_SEARCH_PROJECTS:
                keywords = tool_call.params.get("keywords", [])
                language = tool_call.params.get("language")

                # If no keywords provided, extract from original query
                if not keywords or keywords == []:
                    # Extract keywords from query using simple heuristics
                    query_lower = self.conversation_history[-1].get("query", "").lower() if self.conversation_history else ""

                    # Common language keywords
                    lang_map = {"python": "Python", "javascript": "JavaScript", "go": "Go",
                               "rust": "Rust", "java": "Java", "c++": "C++", "c#": "C#",
                               "ruby": "Ruby", "php": "PHP", "swift": "Swift"}

                    for lang_name, lang_code in lang_map.items():
                        if lang_name in query_lower:
                            language = lang_code
                            break

                    # Extract keywords from query
                    if "framework" in query_lower:
                        keywords = ["framework"]
                        if "rest" in query_lower or "api" in query_lower:
                            keywords.append("REST API")
                        elif "web" in query_lower:
                            keywords.append("web framework")
                        elif "testing" in query_lower:
                            keywords.append("testing")
                        elif "async" in query_lower:
                            keywords.append("async")
                    elif "library" in query_lower or "libraries" in query_lower:
                        keywords = ["library"]
                    elif "rest" in query_lower or "api" in query_lower:
                        keywords = ["REST API", "framework"]
                    elif "testing" in query_lower:
                        keywords = ["testing", "test framework"]
                    elif "async" in query_lower:
                        keywords = ["async", "asynchronous"]
                    else:
                        # Use main nouns from query
                        query_parts = query_lower.split()
                        keywords = [word for word in query_parts
                                   if word not in ["find", "popular", "on", "github", "show", "me", "the", "and", "tell"]][:3]

                if not keywords:
                    return "Please specify what type of projects you're looking for (frameworks, libraries, tools, etc.)"

                projects = self.github_integration.find_projects(keywords, language)
                if not projects:
                    return f"No projects found matching: {', '.join(keywords)}" + (f" in {language}" if language else "")

                result = "Found projects:\n"
                for proj in projects[:5]:
                    result += f"- {proj['name']} ({proj['owner']}): ⭐ {proj['stars']} stars - {proj['description'][:60] if proj.get('description') else 'No description'}\n"
                return result

            elif tool_call.tool_type == ToolType.GITHUB_ANALYZE_PROJECT:
                owner = tool_call.params.get("owner", "")
                repo = tool_call.params.get("repo", "")

                # If not provided, extract from query
                if not owner or not repo:
                    query_lower = self.conversation_history[-1].get("query", "").lower() if self.conversation_history else ""
                    query = self.conversation_history[-1].get("query", "") if self.conversation_history else ""

                    # Try to extract "by <owner>" pattern
                    if " by " in query_lower:
                        parts = query.split(" by ")
                        if len(parts) > 1:
                            owner = parts[-1].split()[0].lower()

                    # Extract repository name - look for common patterns
                    words = query.split()
                    for i, word in enumerate(words):
                        word_lower = word.lower().rstrip('.,!?')
                        if word_lower in ["repository", "repo", "project"]:
                            if i > 0:
                                repo = words[i-1].lower().rstrip('.,!?')
                            break
                        elif "flask" in word_lower:
                            repo = "flask"
                            if not owner:
                                owner = "pallets"
                        elif "django" in word_lower:
                            repo = "django"
                            if not owner:
                                owner = "django"
                        elif "fastapi" in word_lower:
                            repo = "fastapi"
                            if not owner:
                                owner = "tiangolo"
                        elif "tensorflow" in word_lower:
                            repo = "tensorflow"
                            if not owner:
                                owner = "tensorflow"

                if not owner or not repo:
                    return "Please specify the project to analyze (e.g., 'Analyze the flask repository by pallets')"

                analysis = self.github_integration.analyze_project(owner, repo)
                if "error" in analysis:
                    return f"Could not analyze {owner}/{repo}: {analysis.get('error')}"

                result = f"📦 **{analysis['name']}** by {owner}\n\n"
                result += f"⭐ **Stars:** {analysis['stars']}\n"
                result += f"🍴 **Forks:** {analysis['forks']}\n"
                result += f"🔧 **Language:** {analysis['language']}\n"
                if analysis.get('license'):
                    result += f"📜 **License:** {analysis['license']}\n"
                result += f"\n📝 **Description:**\n{analysis['description']}\n"
                if analysis.get('readme'):
                    result += f"\n📖 **README Preview:**\n{analysis['readme'][:300]}...\n"
                return result

            elif tool_call.tool_type == ToolType.GITHUB_TRIGGER_WORKFLOW:
                repo = tool_call.params.get("repo", "")
                workflow_id = tool_call.params.get("workflow_id", "")
                ref = tool_call.params.get("ref", "main")
                if not repo or not workflow_id:
                    return "Repository and workflow ID required"
                success, msg = self.github_integration.github_api.trigger_workflow(repo, workflow_id, ref)
                return msg if self.github_integration.github_api else "GitHub not authenticated"

            else:
                return f"Unknown tool: {tool_call.tool_type.value}"

        except Exception as e:
            return f"Tool execution error: {str(e)}"

    def _synthesize_answer(self, query: str, tool_results: Dict[str, str]) -> str:
        """Use LLM to synthesize final answer from tool results"""

        results_text = "\n".join([f"- {k}: {v[:200]}..." for k, v in tool_results.items()])

        prompt = f"""Based on the query and the gathered information, provide a comprehensive answer.

Query: {query}

Information gathered:
{results_text}

Provide a clear, concise answer that directly addresses the query using the gathered information."""

        return call_normal_task(prompt)

    def process_query(self, query: str) -> Tuple[str, List[ToolCall]]:
        """
        Main orchestration loop

        Returns:
            Tuple of (final_answer, tools_used)
        """

        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "type": "user_query"
        })

        print(f"\n{'='*70}")
        print(f"TERMINATOR AGENTIC ORCHESTRATOR")
        print(f"{'='*70}")
        print(f"\nQuery: {query}\n")

        # Step 1: Extract intent
        print("🧠 Step 1: Analyzing intent...")
        intents = self._extract_intent(query)
        print(f"Detected intents: {', '.join(intents[:3])}")

        # Step 2: Determine tools
        print("\n🔧 Step 2: Determining tools needed...")
        tool_calls = self._determine_tools(query)
        print(f"Planning to execute {len(tool_calls)} tools:")
        for i, tool in enumerate(tool_calls, 1):
            print(f"  {i}. {tool.tool_type.value}")

        # Step 3: Execute tools iteratively
        print("\n⚡ Step 3: Executing tools...")
        tool_results = {}

        for i, tool_call in enumerate(tool_calls, 1):
            print(f"\n  [{i}/{len(tool_calls)}] Executing {tool_call.tool_type.value}...")

            result = self._execute_tool(tool_call)
            tool_results[tool_call.tool_type.value] = result
            tool_call.result = result
            tool_call.executed = True

            # Show progress
            preview = result[:100].replace('\n', ' ') if result else "No result"
            print(f"  ✓ Result: {preview}...")

            self.tool_calls_made.append(tool_call)

        # Step 4: Synthesize answer
        print("\n📝 Step 4: Synthesizing answer...")
        final_answer = self._synthesize_answer(query, tool_results)

        print(f"\n{'='*70}")
        print("FINAL ANSWER")
        print(f"{'='*70}\n")
        print(final_answer)

        # Store in history
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "agent_response",
            "tools_used": [t.tool_type.value for t in tool_calls],
            "answer": final_answer
        })

        return final_answer, tool_calls

    def handle_message(self, message: str) -> str:
        """Handle message and return answer"""
        answer, _ = self.process_query(message)
        return answer

    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.conversation_history

    def print_summary(self):
        """Print execution summary"""
        print(f"\nExecution Summary:")
        print(f"  Tools executed: {len(self.tool_calls_made)}")
        print(f"  Conversation turns: {len(self.conversation_history) // 2}")


# Global instance
_orchestrator = None


def get_orchestrator() -> TerminatorAgenticOrchestrator:
    """Get or create orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = TerminatorAgenticOrchestrator()
    return _orchestrator


def ask_terminator(query: str) -> str:
    """Simple function to ask Terminator a question"""
    orchestrator = get_orchestrator()
    return orchestrator.handle_message(query)


if __name__ == "__main__":
    print("Terminator Agentic Orchestrator - Demo\n")

    orchestrator = get_orchestrator()

    # Test queries
    queries = [
        "What devices are connected to my home network?",
        "Show me my iOS devices and their status",
        "Scan my network and tell me about all Apple devices",
    ]

    for query in queries:
        answer, tools = orchestrator.process_query(query)
        print("\n" + "="*70 + "\n")
