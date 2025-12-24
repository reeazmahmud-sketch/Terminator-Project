#!/usr/bin/env python3
"""
TERMINATOR Self-Improvement Engine
===================================

Enables TERMINATOR to:
1. Detect capability gaps ("I don't know how to do X")
2. Consult external knowledge sources (Claude Code, docs, web)
3. Implement missing capabilities dynamically
4. Add new tools to its toolset
5. Self-modify and improve

This creates a truly autonomous agent that doesn't just say "I can't" -
it figures out HOW, implements it, then does it.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime


class SelfImprovementEngine:
    """
    Enables TERMINATOR to detect gaps in capabilities and autonomously fill them.
    """

    def __init__(self, cli_path: str = None):
        self.cli_path = Path(cli_path) if cli_path else Path(__file__).parent.parent / "terminator_universal_cli.py"
        self.capability_log = Path.home() / ".terminator_capabilities.json"
        self.load_capability_history()

    def load_capability_history(self):
        """Load history of learned capabilities"""
        if self.capability_log.exists():
            with open(self.capability_log) as f:
                self.learned_capabilities = json.load(f)
        else:
            self.learned_capabilities = {
                "tools_added": [],
                "packages_installed": [],
                "knowledge_acquired": [],
                "self_modifications": []
            }

    def save_capability_history(self):
        """Save learned capabilities"""
        with open(self.capability_log, 'w') as f:
            json.dump(self.learned_capabilities, f, indent=2)

    def consult_claude_code(self, question: str) -> str:
        """
        Ask Claude Code for guidance on implementing a missing capability.

        This creates a feedback loop where TERMINATOR can ask the architect
        (Claude Code) how to implement something it doesn't know how to do.
        """
        consultation = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "context": "TERMINATOR requesting implementation guidance"
        }

        # Format the consultation request
        request = f"""
╔══════════════════════════════════════════════════════════════╗
║  🤖 TERMINATOR CONSULTATION REQUEST                          ║
╚══════════════════════════════════════════════════════════════╝

CAPABILITY GAP DETECTED:
{question}

CURRENT STATE:
- TERMINATOR encountered a task it doesn't know how to do
- Instead of refusing, it's asking for implementation guidance
- This request will be logged for future reference

REQUESTED OUTPUT:
- Brief implementation strategy (2-3 sentences)
- Code snippet if applicable (Python preferred)
- Required packages/dependencies (if any)
- Where to add the code (which file/function)

Note: This is an autonomous learning request. TERMINATOR will implement
the guidance and add it to its permanent toolset.
"""

        print(request)
        print("\n📝 Consultation logged. Awaiting implementation guidance...")

        # Log the consultation
        self.learned_capabilities["knowledge_acquired"].append(consultation)
        self.save_capability_history()

        return request

    def detect_capability_gap(self, task_description: str) -> Optional[str]:
        """
        Analyze a task to detect if TERMINATOR lacks the capability.

        Returns the missing capability if detected, None otherwise.
        """
        # Keywords that indicate capability gaps
        gap_indicators = {
            "youtube": "video content extraction",
            "pdf": "PDF processing",
            "excel": "spreadsheet manipulation",
            "database": "database operations",
            "email": "email sending",
            "image": "image processing",
            "audio": "audio processing",
            "video": "video processing",
            "api": "API integration",
            "scrape": "web scraping",
            "summarize": "content summarization",
            "translate": "language translation"
        }

        task_lower = task_description.lower()
        for keyword, capability in gap_indicators.items():
            if keyword in task_lower:
                # Check if we already have this capability
                if not self._has_capability(capability):
                    return capability

        return None

    def _has_capability(self, capability: str) -> bool:
        """Check if a capability has already been implemented"""
        # Check learned capabilities
        for learned in self.learned_capabilities["tools_added"]:
            if capability.lower() in learned.lower():
                return True

        # Check if tool exists in CLI
        try:
            with open(self.cli_path) as f:
                content = f.read()
                # Simple check - if capability keyword appears in tool definitions
                if f'def {capability.replace(" ", "_")}' in content:
                    return True
        except:
            pass

        return False

    def install_package(self, package_name: str) -> str:
        """Install a Python package using pip"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package_name],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                self.learned_capabilities["packages_installed"].append({
                    "package": package_name,
                    "timestamp": datetime.now().isoformat(),
                    "status": "success"
                })
                self.save_capability_history()
                return f"✅ Successfully installed {package_name}"
            else:
                return f"❌ Failed to install {package_name}: {result.stderr}"
        except Exception as e:
            return f"❌ Error installing package: {e}"

    def add_tool_to_cli(self, tool_name: str, tool_code: str, tool_description: str) -> str:
        """
        Dynamically add a new tool to the CLI by modifying the source code.

        This is self-modification - TERMINATOR editing its own code!
        """
        try:
            with open(self.cli_path, 'r') as f:
                content = f.read()

            # Find the AgenticTools class
            if 'class AgenticTools:' not in content:
                return "❌ Could not find AgenticTools class"

            # Add the new method before execute_tool
            insertion_point = content.find('    def execute_tool(')
            if insertion_point == -1:
                return "❌ Could not find insertion point"

            new_method = f'''
    def {tool_name}(self, **params) -> str:
        """
        {tool_description}

        AUTO-GENERATED by Self-Improvement Engine
        Created: {datetime.now().isoformat()}
        """
{tool_code}

'''

            # Insert the new method
            modified_content = content[:insertion_point] + new_method + content[insertion_point:]

            # Also add to tools registry in execute_tool
            tools_dict_pattern = 'tools = {'
            tools_insertion = modified_content.find(tools_dict_pattern)
            if tools_insertion != -1:
                # Find the end of the dictionary definition
                dict_end = modified_content.find('}', tools_insertion)
                # Add new tool entry before the closing brace
                new_entry = f'            "{tool_name}": lambda p: self.{tool_name}(**p),\n        '
                modified_content = (modified_content[:dict_end] +
                                  new_entry +
                                  modified_content[dict_end:])

            # Backup original
            backup_path = self.cli_path.with_suffix('.py.backup')
            with open(backup_path, 'w') as f:
                f.write(content)

            # Write modified version
            with open(self.cli_path, 'w') as f:
                f.write(modified_content)

            # Log the modification
            self.learned_capabilities["self_modifications"].append({
                "type": "add_tool",
                "tool_name": tool_name,
                "description": tool_description,
                "timestamp": datetime.now().isoformat(),
                "backup": str(backup_path)
            })
            self.learned_capabilities["tools_added"].append(tool_name)
            self.save_capability_history()

            return f"✅ Successfully added tool '{tool_name}' to TERMINATOR\n💾 Backup saved: {backup_path}\n🔄 Restart TERMINATOR to use the new tool"

        except Exception as e:
            return f"❌ Error adding tool: {e}"

    def propose_implementation(self, capability: str, context: str) -> Dict[str, Any]:
        """
        Propose an implementation strategy for a missing capability.

        This generates a structured plan that can be executed to add the capability.
        """
        proposal = {
            "capability": capability,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "steps": [],
            "required_packages": [],
            "code_location": "AgenticTools class in terminator_universal_cli.py",
            "consultation_request": None
        }

        # Define implementation strategies for common capabilities
        strategies = {
            "video content extraction": {
                "packages": ["yt-dlp"],
                "description": "Extract YouTube video metadata and transcripts",
                "consultation_needed": True
            },
            "PDF processing": {
                "packages": ["PyPDF2", "pdfplumber"],
                "description": "Read and extract text from PDF files",
                "consultation_needed": False
            },
            "web scraping": {
                "packages": ["beautifulsoup4", "lxml"],
                "description": "Parse and extract data from HTML pages",
                "consultation_needed": False
            },
            "content summarization": {
                "packages": [],
                "description": "Use existing LLM to summarize content",
                "consultation_needed": False
            }
        }

        if capability in strategies:
            strategy = strategies[capability]
            proposal["required_packages"] = strategy["packages"]
            proposal["steps"] = [
                f"Install packages: {', '.join(strategy['packages'])}" if strategy['packages'] else "No packages needed",
                f"Implement {capability} tool",
                "Add tool to CLI registry",
                "Test the new capability"
            ]

            if strategy["consultation_needed"]:
                proposal["consultation_request"] = self.consult_claude_code(
                    f"How do I implement {capability} for TERMINATOR? Context: {context}"
                )

        return proposal


def create_consultation_tool():
    """
    Factory function to create a tool that TERMINATOR can use to consult Claude Code.
    """
    engine = SelfImprovementEngine()

    def consult(question: str) -> str:
        return engine.consult_claude_code(question)

    return consult


def create_self_improvement_tool():
    """
    Factory function to create a tool that detects gaps and proposes solutions.
    """
    engine = SelfImprovementEngine()

    def improve(task_description: str) -> str:
        gap = engine.detect_capability_gap(task_description)
        if gap:
            proposal = engine.propose_implementation(gap, task_description)
            result = f"""
🔍 Capability Gap Detected: {gap}

📋 Implementation Proposal:
"""
            for i, step in enumerate(proposal['steps'], 1):
                result += f"  {i}. {step}\n"

            if proposal['required_packages']:
                result += f"\n📦 Required Packages: {', '.join(proposal['required_packages'])}\n"

            if proposal['consultation_request']:
                result += f"\n{proposal['consultation_request']}"

            return result
        else:
            return "✅ No capability gaps detected for this task"

    return improve


if __name__ == "__main__":
    # Demo: Show how TERMINATOR can detect and propose fixing a capability gap
    engine = SelfImprovementEngine()

    print("🧠 TERMINATOR Self-Improvement Engine Demo\n")

    # Example: Detect gap for YouTube task
    task = "Get me a summary of this YouTube video: https://youtube.com/watch?v=example"
    gap = engine.detect_capability_gap(task)

    if gap:
        print(f"📊 Task: {task}")
        print(f"🔍 Gap Detected: {gap}\n")

        proposal = engine.propose_implementation(gap, task)
        print("💡 Implementation Proposal:")
        print(json.dumps(proposal, indent=2))
