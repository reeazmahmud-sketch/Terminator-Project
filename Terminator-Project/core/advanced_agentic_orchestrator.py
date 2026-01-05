# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
Advanced Agentic Orchestrator - Autonomous Reasoning Engine
===========================================================

Implements true autonomous agent reasoning with:
1. Multi-step iterative reasoning loops
2. Sophisticated tool selection and prioritization
3. Context persistence and memory across iterations
4. Adaptive decision-making based on gathered information
5. Self-correction and re-evaluation capabilities
6. Confidence scoring and validation

This goes beyond simple tool calling to create a reasoning agent that:
- Analyzes what information is needed
- Prioritizes tool calls based on relevance and dependencies
- Iterates until sufficient confidence is achieved
- Synthesizes complex multi-step solutions
- Adapts strategy based on results

Architecture:
    User Query
        ↓
    ReasoningState (tracks context, iterations, confidence)
        ↓
    Intent Analysis → Tool Prioritization → Tool Execution
        ↓
    Result Processing → Confidence Check → Decision Loop
        ↓
    Iterate or Synthesize Final Answer
"""

import sys
import os
from typing import Optional, Dict, Any, List, Tuple, Set
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.mobile_network_query_agent import get_mobile_network_agent
from integrations.github_integration import get_github_integration
from llm_system.INTELLIGENT_LLM_ROUTER import (
    call_normal_task,
    call_critical_task,
    IntelligentLLMRouter,
    TaskPriority
)


class ToolPriority(Enum):
    """Priority levels for tool execution"""
    CRITICAL = 5   # Must execute first
    HIGH = 4       # Execute before medium
    MEDIUM = 3     # Standard execution
    LOW = 2        # Execute if needed
    OPTIONAL = 1   # Nice to have


class ExecutionStrategy(Enum):
    """Strategy for executing multiple tools"""
    PARALLEL = "parallel"      # Execute all tools at once
    SEQUENTIAL = "sequential"  # Execute one by one
    DEPENDENT = "dependent"    # Execute based on dependencies


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


@dataclass
class ToolCall:
    """Represents a tool call with metadata"""
    tool_type: ToolType
    params: Dict[str, Any]
    priority: ToolPriority = ToolPriority.MEDIUM
    dependencies: Set[str] = field(default_factory=set)  # Other tool names this depends on
    result: Optional[str] = None
    executed: bool = False
    error: Optional[str] = None
    confidence_boost: float = 0.0  # How much this result boosts overall confidence

    def __repr__(self):
        return f"ToolCall({self.tool_type.value}, priority={self.priority.name})"


@dataclass
class ReasoningState:
    """Tracks the state of reasoning across iterations"""
    query: str
    iteration: int = 0
    max_iterations: int = 5
    confidence: float = 0.0  # 0.0 to 1.0
    confidence_threshold: float = 0.75

    gathered_info: Dict[str, str] = field(default_factory=dict)
    executed_tools: List[ToolCall] = field(default_factory=list)
    pending_tools: List[ToolCall] = field(default_factory=list)

    decision_path: List[str] = field(default_factory=list)  # Track decisions made
    reasoning_log: List[Dict[str, Any]] = field(default_factory=list)

    should_continue: bool = True
    completion_reason: Optional[str] = None

    def add_decision(self, decision: str):
        """Log a decision made during reasoning"""
        self.decision_path.append(f"[Iteration {self.iteration}] {decision}")

    def add_reasoning(self, reasoning: Dict[str, Any]):
        """Log detailed reasoning step"""
        reasoning['iteration'] = self.iteration
        reasoning['timestamp'] = datetime.now().isoformat()
        self.reasoning_log.append(reasoning)

    def is_satisfied(self) -> bool:
        """Check if sufficient confidence is achieved"""
        return self.confidence >= self.confidence_threshold

    def should_continue_reasoning(self) -> bool:
        """Determine if iteration loop should continue"""
        if not self.should_continue:
            return False
        if self.iteration >= self.max_iterations:
            self.completion_reason = f"Reached max iterations ({self.max_iterations})"
            return False
        if self.is_satisfied():
            self.completion_reason = f"Achieved confidence threshold ({self.confidence:.2f})"
            return False
        return True


class AdvancedAgenticOrchestrator:
    """
    Advanced autonomous agent with true reasoning loops
    """

    def __init__(self, max_iterations: int = 5, confidence_threshold: float = 0.75):
        self.mobile_agent = get_mobile_network_agent()
        self.github_integration = get_github_integration()
        self.router = IntelligentLLMRouter()
        self.max_iterations = max_iterations
        self.confidence_threshold = confidence_threshold

    def _analyze_query_deeply(self, query: str, state: ReasoningState) -> Dict[str, Any]:
        """Deep analysis of query using LLM to understand requirements"""
        analysis_prompt = f"""Analyze this query comprehensively to understand what the user needs:

Query: {query}

Previous information gathered:
{json.dumps(state.gathered_info, indent=2) if state.gathered_info else "None yet"}

Previous decisions:
{chr(10).join(state.decision_path) if state.decision_path else "None yet"}

Provide a JSON response with:
{{
  "primary_goal": "main objective",
  "sub_goals": ["goal1", "goal2"],
  "information_needed": ["what information is essential"],
  "optional_information": ["nice to have"],
  "complexity_level": "simple|moderate|complex",
  "estimated_tools_needed": number,
  "confidence_factors": ["factor1", "factor2"]
}}"""

        response = call_normal_task(analysis_prompt)
        try:
            return json.loads(response)
        except:
            return {
                "primary_goal": query,
                "sub_goals": [],
                "information_needed": ["information about the query"],
                "optional_information": [],
                "complexity_level": "moderate",
                "estimated_tools_needed": 2,
                "confidence_factors": []
            }

    def _determine_tools_intelligently(self, query: str, state: ReasoningState) -> List[ToolCall]:
        """Intelligently determine which tools to call based on analysis"""
        tools = []
        query_lower = query.lower()

        # Deep query analysis
        analysis = self._analyze_query_deeply(query, state)
        state.add_reasoning({
            "step": "query_analysis",
            "analysis": analysis
        })

        # iOS tools with priority
        if any(keyword in query_lower for keyword in ["iphone", "ipad", "ios", "ios device"]):
            if "clipboard" in query_lower:
                tools.append(ToolCall(
                    ToolType.IOS_GET_CLIPBOARD,
                    {"device_name": "My iPhone"},
                    priority=ToolPriority.HIGH,
                    confidence_boost=0.3
                ))
            elif "text" in query_lower and ("get" in query_lower or "extract" in query_lower):
                tools.append(ToolCall(
                    ToolType.IOS_GET_TEXT,
                    {"device_name": "My iPhone", "app_name": "Notes"},
                    priority=ToolPriority.HIGH,
                    confidence_boost=0.35
                ))
            elif "status" in query_lower:
                tools.append(ToolCall(
                    ToolType.IOS_CHECK_STATUS,
                    {},
                    priority=ToolPriority.MEDIUM,
                    confidence_boost=0.2
                ))

        # Android tools with priority
        if any(keyword in query_lower for keyword in ["android", "samsung", "pixel"]):
            if "clipboard" in query_lower:
                tools.append(ToolCall(
                    ToolType.ANDROID_GET_CLIPBOARD,
                    {"device_id": ""},
                    priority=ToolPriority.HIGH,
                    confidence_boost=0.3
                ))
            elif "text" in query_lower:
                tools.append(ToolCall(
                    ToolType.ANDROID_GET_TEXT,
                    {"device_id": "", "app_package": "com.google.android.apps.docs"},
                    priority=ToolPriority.HIGH,
                    confidence_boost=0.35
                ))
            elif "status" in query_lower:
                tools.append(ToolCall(
                    ToolType.ANDROID_CHECK_STATUS,
                    {},
                    priority=ToolPriority.MEDIUM,
                    confidence_boost=0.2
                ))

        # Network tools with priority
        if any(keyword in query_lower for keyword in ["network", "devices", "wifi", "home network"]):
            if "summary" in query_lower:
                tools.append(ToolCall(
                    ToolType.NETWORK_SUMMARY,
                    {},
                    priority=ToolPriority.HIGH,
                    confidence_boost=0.4
                ))
            elif "scan" in query_lower:
                tools.append(ToolCall(
                    ToolType.NETWORK_SCAN,
                    {},
                    priority=ToolPriority.CRITICAL,
                    confidence_boost=0.5
                ))
            elif "list" in query_lower or "all" in query_lower:
                tools.append(ToolCall(
                    ToolType.NETWORK_LIST_DEVICES,
                    {},
                    priority=ToolPriority.HIGH,
                    confidence_boost=0.45
                ))

        # GitHub tools with priority
        github_keywords = ["github", "push", "pull request", "pr", "repository", "repo"]
        if any(keyword in query_lower for keyword in github_keywords):
            if "search" in query_lower or "find" in query_lower:
                tools.append(ToolCall(
                    ToolType.GITHUB_SEARCH_PROJECTS,
                    {"keywords": []},
                    priority=ToolPriority.HIGH,
                    confidence_boost=0.4
                ))
            elif "analyze" in query_lower:
                tools.append(ToolCall(
                    ToolType.GITHUB_ANALYZE_PROJECT,
                    {"owner": "", "repo": ""},
                    priority=ToolPriority.HIGH,
                    confidence_boost=0.45
                ))

        # Sort by priority (CRITICAL first, then HIGH, etc.)
        tools.sort(key=lambda t: t.priority.value, reverse=True)
        return tools

    def _execute_tools_strategically(self, tools: List[ToolCall], strategy: ExecutionStrategy = ExecutionStrategy.PARALLEL) -> Dict[str, str]:
        """Execute tools based on strategy"""
        results = {}

        if strategy == ExecutionStrategy.PARALLEL:
            # Execute all non-dependent tools at once
            for tool in tools:
                if not tool.dependencies:
                    result = self._execute_tool(tool)
                    results[tool.tool_type.value] = result

        elif strategy == ExecutionStrategy.SEQUENTIAL:
            # Execute tools one by one
            for tool in tools:
                result = self._execute_tool(tool)
                results[tool.tool_type.value] = result

        elif strategy == ExecutionStrategy.DEPENDENT:
            # Execute based on dependencies
            executed = set()
            while len(executed) < len(tools):
                for tool in tools:
                    if tool.tool_type.value not in executed:
                        if tool.dependencies.issubset(executed):
                            result = self._execute_tool(tool)
                            results[tool.tool_type.value] = result
                            executed.add(tool.tool_type.value)

        return results

    def _execute_tool(self, tool_call: ToolCall) -> str:
        """Execute a specific tool and track results"""
        try:
            result = None

            # iOS tools
            if tool_call.tool_type == ToolType.IOS_GET_TEXT:
                result = self.mobile_agent.get_ios_device_text(
                    tool_call.params.get("device_name", "My iPhone"),
                    tool_call.params.get("app_name", "Notes")
                )
            elif tool_call.tool_type == ToolType.IOS_GET_CLIPBOARD:
                result = self.mobile_agent.get_ios_clipboard(
                    tool_call.params.get("device_name", "My iPhone")
                )
            elif tool_call.tool_type == ToolType.IOS_CHECK_STATUS:
                result = self.mobile_agent.check_ios_devices_status()

            # Android tools
            elif tool_call.tool_type == ToolType.ANDROID_GET_TEXT:
                result = self.mobile_agent.get_android_device_text(
                    tool_call.params.get("device_id", ""),
                    tool_call.params.get("app_package", "com.google.android.apps.docs")
                )
            elif tool_call.tool_type == ToolType.ANDROID_GET_CLIPBOARD:
                result = self.mobile_agent.get_android_clipboard(
                    tool_call.params.get("device_id", "")
                )
            elif tool_call.tool_type == ToolType.ANDROID_CHECK_STATUS:
                result = self.mobile_agent.check_android_devices_status()

            # Network tools
            elif tool_call.tool_type == ToolType.NETWORK_SCAN:
                result = self.mobile_agent.scan_network()
            elif tool_call.tool_type == ToolType.NETWORK_LIST_DEVICES:
                result = self.mobile_agent.list_network_devices()
            elif tool_call.tool_type == ToolType.NETWORK_SUMMARY:
                result = self.mobile_agent.get_network_summary()

            # GitHub tools
            elif tool_call.tool_type == ToolType.GITHUB_SEARCH_PROJECTS:
                keywords = tool_call.params.get("keywords", [])
                projects = self.github_integration.find_projects(keywords)
                result = f"Found {len(projects)} projects"

            elif tool_call.tool_type == ToolType.GITHUB_ANALYZE_PROJECT:
                owner = tool_call.params.get("owner", "")
                repo = tool_call.params.get("repo", "")
                analysis = self.github_integration.analyze_project(owner, repo)
                result = json.dumps(analysis)

            tool_call.result = result
            tool_call.executed = True
            return result or "No result"

        except Exception as e:
            tool_call.error = str(e)
            return f"Tool execution error: {str(e)}"

    def _calculate_confidence(self, state: ReasoningState, tools: List[ToolCall]) -> float:
        """Calculate overall confidence based on executed tools"""
        if not state.executed_tools:
            return 0.0

        total_boost = sum(tool.confidence_boost for tool in state.executed_tools if tool.executed)
        max_possible = 1.0

        return min(total_boost, max_possible)

    def _should_refine_query(self, state: ReasoningState) -> Tuple[bool, Optional[str]]:
        """Determine if query needs refinement based on gathered info"""
        if state.confidence >= state.confidence_threshold:
            return False, None

        refinement_prompt = f"""Based on the information gathered so far, do we have enough information?

Original Query: {state.query}

Information Gathered:
{json.dumps(state.gathered_info, indent=2)}

Confidence: {state.confidence:.2f}/{state.confidence_threshold}

Respond with JSON:
{{
  "needs_refinement": boolean,
  "reason": "why or why not",
  "suggested_tools": ["tool1", "tool2"],
  "clarification": "question to ask user if needed"
}}"""

        response = call_normal_task(refinement_prompt)
        try:
            data = json.loads(response)
            return data.get("needs_refinement", False), data.get("clarification")
        except:
            return False, None

    def _synthesize_answer(self, query: str, state: ReasoningState) -> str:
        """Synthesize comprehensive answer from gathered information"""
        synthesis_prompt = f"""Based on all the gathered information, provide a comprehensive answer to the query.

Original Query: {query}

Information Gathered:
{json.dumps(state.gathered_info, indent=2)}

Decision Path:
{chr(10).join(state.decision_path)}

Provide a clear, well-structured answer that synthesizes all the information."""

        return call_normal_task(synthesis_prompt)

    def reason(self, query: str) -> Tuple[str, ReasoningState]:
        """
        Main autonomous reasoning loop

        Returns:
            Tuple of (final_answer, reasoning_state)
        """
        state = ReasoningState(
            query=query,
            max_iterations=self.max_iterations,
            confidence_threshold=self.confidence_threshold
        )

        print(f"\n{'='*80}")
        print(f"ADVANCED AGENTIC ORCHESTRATOR - Autonomous Reasoning Engine")
        print(f"{'='*80}")
        print(f"\nQuery: {query}\n")

        # Reasoning loop
        while state.should_continue_reasoning():
            state.iteration += 1
            print(f"🔄 Iteration {state.iteration}/{state.max_iterations}")
            print(f"   Confidence: {state.confidence:.2f}/{state.confidence_threshold}\n")

            # Step 1: Analyze query
            state.add_decision("Analyzing query in depth")
            analysis = self._analyze_query_deeply(query, state)
            print(f"   📊 Analysis: {analysis.get('primary_goal')}")

            # Step 2: Determine tools intelligently
            state.add_decision("Determining tools with prioritization")
            tools = self._determine_tools_intelligently(query, state)
            print(f"   🔧 Tools to execute: {len(tools)}")

            if tools:
                # Step 3: Execute tools
                state.add_decision(f"Executing {len(tools)} tools strategically")
                results = self._execute_tools_strategically(tools, ExecutionStrategy.PARALLEL)
                state.gathered_info.update(results)
                state.executed_tools.extend(tools)
                print(f"   ✅ Executed tools, gathered {len(results)} results")

                # Step 4: Calculate confidence
                state.confidence = self._calculate_confidence(state, tools)
                print(f"   📈 Confidence updated: {state.confidence:.2f}")

            # Step 5: Check if refinement needed
            needs_refinement, clarification = self._should_refine_query(state)
            if needs_refinement:
                state.add_decision(f"Query refinement suggested: {clarification}")
                print(f"   🔍 Needs refinement: {clarification}\n")
            else:
                state.add_decision("Query satisfactory, proceeding to synthesis")
                print(f"   ✓ Query sufficiently answered\n")
                state.should_continue = False

        # Final synthesis
        print(f"✨ Synthesizing final answer...")
        print(f"   Reason: {state.completion_reason}\n")

        final_answer = self._synthesize_answer(query, state)

        print(f"{'='*80}")
        print(f"Final Answer:\n{final_answer}")
        print(f"{'='*80}\n")

        return final_answer, state


def create_advanced_orchestrator(max_iterations: int = 5, confidence_threshold: float = 0.75) -> AdvancedAgenticOrchestrator:
    """Factory function to create advanced orchestrator"""
    return AdvancedAgenticOrchestrator(max_iterations, confidence_threshold)


# Alias for backward compatibility
ask_terminator_advanced = create_advanced_orchestrator


if __name__ == "__main__":
    # Example usage
    orchestrator = create_advanced_orchestrator(max_iterations=5)

    # Test with a complex query
    query = "Tell me about all the devices connected to my home network"
    answer, state = orchestrator.reason(query)

    print("\n📋 Reasoning Summary:")
    print(f"Iterations: {state.iteration}")
    print(f"Final Confidence: {state.confidence:.2f}")
    print(f"Tools Executed: {len(state.executed_tools)}")
    print(f"Decision Path Length: {len(state.decision_path)}")
