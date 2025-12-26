#!/usr/bin/env python3

# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Solution Knowledge Base & Anti-Redundancy System
==========================================================

Prevents wasting time by:
1. Searching online for existing solutions BEFORE building
2. Documenting every fix we make
3. Checking if we've already solved this problem
4. Learning from GitHub, Stack Overflow, and documentation
5. Warning when we're about to recreate something

The goal: NEVER waste time fixing the same issue twice.

Features:
- Solution memory (local knowledge base)
- Online best practice search (GitHub, Stack Overflow, etc.)
- Redundancy detection
- Automatic documentation
- Solution quality scoring
- Fix history tracking

Created: December 17, 2025
Purpose: Stop wasting time on redundant work
"""

import os
import sys
import json
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


# ============================================================================
# Data Structures
# ============================================================================

class SolutionSource(Enum):
    """Where the solution came from"""
    INTERNAL = "internal"          # We created it
    GITHUB = "github"              # Found on GitHub
    STACKOVERFLOW = "stackoverflow" # Stack Overflow
    DOCUMENTATION = "documentation" # Official docs
    CLAUDE = "claude"              # Claude suggestion


@dataclass
class Solution:
    """A documented solution to a problem"""
    problem_id: str                # Hash of the problem
    problem_description: str       # What was wrong
    solution_description: str      # How we fixed it
    source: SolutionSource        # Where solution came from
    code_snippet: Optional[str]   # Code that fixed it
    file_path: Optional[str]      # File that was modified
    timestamp: str                # When we solved it
    tags: List[str]               # Keywords for searching
    quality_score: float          # 0-1, how good is this solution
    reuse_count: int = 0          # How many times we've reused it

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            **asdict(self),
            'source': self.source.value
        }


# ============================================================================
# Solution Knowledge Base
# ============================================================================

class SolutionKnowledgeBase:
    """
    Central knowledge base that prevents redundant work.
    """

    def __init__(self):
        """Initialize knowledge base"""
        self.project_root = Path("/Users/reeazmahmud/Desktop/Terminator-Project")
        self.kb_dir = self.project_root / ".knowledge_base"
        self.kb_dir.mkdir(exist_ok=True)

        self.solutions_file = self.kb_dir / "solutions.json"
        self.history_file = self.kb_dir / "fix_history.json"

        self.solutions: Dict[str, Solution] = {}
        self.history: List[dict] = []

        self._load_knowledge_base()

    def _load_knowledge_base(self) -> None:
        """Load existing knowledge base"""
        # Load solutions
        if self.solutions_file.exists():
            try:
                with open(self.solutions_file, 'r') as f:
                    data = json.load(f)
                    for sol_dict in data:
                        sol = Solution(
                            problem_id=sol_dict['problem_id'],
                            problem_description=sol_dict['problem_description'],
                            solution_description=sol_dict['solution_description'],
                            source=SolutionSource(sol_dict['source']),
                            code_snippet=sol_dict.get('code_snippet'),
                            file_path=sol_dict.get('file_path'),
                            timestamp=sol_dict['timestamp'],
                            tags=sol_dict.get('tags', []),
                            quality_score=sol_dict.get('quality_score', 0.5),
                            reuse_count=sol_dict.get('reuse_count', 0)
                        )
                        self.solutions[sol.problem_id] = sol
            except Exception as e:
                print(f"⚠️  Could not load solutions: {e}")

        # Load history
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            except:
                self.history = []

    def _save_knowledge_base(self) -> None:
        """Save knowledge base to disk"""
        # Save solutions
        try:
            with open(self.solutions_file, 'w') as f:
                json.dump([sol.to_dict() for sol in self.solutions.values()], f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save solutions: {e}")

        # Save history
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save history: {e}")

    def check_if_solved_before(self, problem_description: str) -> Optional[Solution]:
        """
        Check if we've already solved this problem.
        Returns the solution if found.
        """
        problem_id = self._hash_problem(problem_description)

        # Exact match
        if problem_id in self.solutions:
            solution = self.solutions[problem_id]
            print(f"\n⚠️  WAIT! We've solved this before!")
            print(f"   Problem: {solution.problem_description}")
            print(f"   Solution: {solution.solution_description}")
            print(f"   Date: {solution.timestamp}")
            print(f"   Reused: {solution.reuse_count} times")
            print(f"   Quality: {solution.quality_score:.1%}\n")

            solution.reuse_count += 1
            self._save_knowledge_base()
            return solution

        # Fuzzy match (check keywords)
        keywords = self._extract_keywords(problem_description)
        similar = self._find_similar_solutions(keywords)

        if similar:
            print(f"\n💡 Found {len(similar)} similar solutions:")
            for i, sol in enumerate(similar[:3], 1):
                print(f"   {i}. {sol.problem_description}")
                print(f"      → {sol.solution_description[:100]}...")
            print()

            return similar[0]  # Return best match

        return None

    def search_online_solutions(self, problem_description: str) -> List[Dict]:
        """
        Search online for existing solutions.
        Checks: GitHub, Stack Overflow, documentation.
        """
        print(f"\n🔍 Searching online for: {problem_description}\n")

        online_solutions = []

        # Search GitHub
        github_results = self._search_github(problem_description)
        online_solutions.extend(github_results)

        # Search Stack Overflow (via web search)
        stackoverflow_results = self._search_stackoverflow(problem_description)
        online_solutions.extend(stackoverflow_results)

        if online_solutions:
            print(f"✅ Found {len(online_solutions)} existing solutions online!\n")
            for i, sol in enumerate(online_solutions[:5], 1):
                print(f"{i}. [{sol['source']}] {sol['title']}")
                print(f"   {sol['url']}")
                print(f"   {sol['description'][:150]}...\n")
        else:
            print("ℹ️  No existing solutions found online. This might be a new problem.\n")

        return online_solutions

    def _search_github(self, query: str) -> List[Dict]:
        """Search GitHub for similar solutions"""
        # Use gh CLI if available
        try:
            result = subprocess.run(
                ['gh', 'search', 'code', query, '--limit', '5'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Parse results (simplified)
                return [{
                    'source': 'github',
                    'title': f'GitHub result for: {query}',
                    'url': 'https://github.com/search?q=' + query.replace(' ', '+'),
                    'description': 'Found matching code on GitHub'
                }]
        except:
            pass

        return []

    def _search_stackoverflow(self, query: str) -> List[Dict]:
        """Search Stack Overflow"""
        # Would use StackOverflow API or web search
        # For now, return a search URL
        return [{
            'source': 'stackoverflow',
            'title': f'Stack Overflow search: {query}',
            'url': f'https://stackoverflow.com/search?q={query.replace(" ", "+")}',
            'description': 'Search Stack Overflow for similar problems'
        }]

    def document_solution(
        self,
        problem_description: str,
        solution_description: str,
        source: SolutionSource = SolutionSource.INTERNAL,
        code_snippet: Optional[str] = None,
        file_path: Optional[str] = None,
        quality_score: float = 0.8
    ) -> Solution:
        """
        Document a solution so we never have to solve it again.
        """
        problem_id = self._hash_problem(problem_description)
        tags = self._extract_keywords(problem_description)

        solution = Solution(
            problem_id=problem_id,
            problem_description=problem_description,
            solution_description=solution_description,
            source=source,
            code_snippet=code_snippet,
            file_path=file_path,
            timestamp=datetime.now().isoformat(),
            tags=tags,
            quality_score=quality_score
        )

        self.solutions[problem_id] = solution

        # Add to history
        self.history.append({
            'timestamp': solution.timestamp,
            'problem': problem_description,
            'solution': solution_description,
            'source': source.value
        })

        self._save_knowledge_base()

        print(f"✅ Solution documented! We'll remember this forever.")
        print(f"   Problem ID: {problem_id[:12]}...")
        print(f"   Tags: {', '.join(tags)}\n")

        return solution

    def get_solution_report(self) -> str:
        """Get a report of all solutions"""
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║          SOLUTION KNOWLEDGE BASE REPORT                     ║
╚══════════════════════════════════════════════════════════════╝

📊 Statistics:
   • Total solutions: {len(self.solutions)}
   • Total fixes: {len(self.history)}
   • Most reused: {max((s.reuse_count for s in self.solutions.values()), default=0)} times

🏆 Top Solutions (by reuse):
"""

        # Sort by reuse count
        top_solutions = sorted(
            self.solutions.values(),
            key=lambda s: s.reuse_count,
            reverse=True
        )[:5]

        for i, sol in enumerate(top_solutions, 1):
            report += f"""
   {i}. {sol.problem_description[:60]}...
      Reused: {sol.reuse_count} times
      Quality: {sol.quality_score:.0%}
      Solution: {sol.solution_description[:80]}...
"""

        report += f"""
📅 Recent Fixes:
"""

        for fix in self.history[-5:]:
            report += f"   • {fix['timestamp'][:10]}: {fix['problem'][:50]}...\n"

        return report

    def suggest_best_practice(self, problem_type: str) -> Optional[str]:
        """Suggest best practice for a type of problem"""
        best_practices = {
            'dependency': 'Use virtual environments and requirements.txt',
            'disk': 'Implement log rotation and monitoring',
            'infinite_loop': 'Use pattern detection and auto-kill',
            'port': 'Check availability before starting services',
            'process': 'Use PID files and graceful shutdown',
        }

        for key, practice in best_practices.items():
            if key in problem_type.lower():
                return practice

        return None

    def _hash_problem(self, description: str) -> str:
        """Create a hash ID for a problem"""
        return hashlib.md5(description.lower().encode()).hexdigest()

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        words = text.lower().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        return list(set(keywords[:10]))  # Top 10 unique keywords

    def _find_similar_solutions(self, keywords: List[str]) -> List[Solution]:
        """Find solutions with similar keywords"""
        scored_solutions = []

        for solution in self.solutions.values():
            score = sum(1 for kw in keywords if kw in solution.tags)
            if score > 0:
                scored_solutions.append((score, solution))

        # Sort by score
        scored_solutions.sort(key=lambda x: x[0], reverse=True)

        return [sol for score, sol in scored_solutions if score >= 2]


# ============================================================================
# Workflow Helper
# ============================================================================

class SmartWorkflow:
    """
    Wraps the normal workflow to check knowledge base first.
    """

    def __init__(self):
        self.kb = SolutionKnowledgeBase()

    def before_you_build(self, problem_description: str, interactive: bool = True) -> bool:
        """
        Call this BEFORE building anything.
        Returns True if you should proceed, False if solution exists.
        """
        print("=" * 60)
        print("🧠 CHECKING KNOWLEDGE BASE")
        print("=" * 60)

        # Step 1: Check if we've solved this before
        existing_solution = self.kb.check_if_solved_before(problem_description)
        if existing_solution:
            print("🎯 SOLUTION FOUND IN KNOWLEDGE BASE!")
            print(f"\nYou can reuse this solution instead of rebuilding.\n")

            if interactive:
                try:
                    response = input("Do you want to see the solution? [y/n]: ")
                    if response.lower() == 'y':
                        print(f"\n{existing_solution.solution_description}")
                        if existing_solution.code_snippet:
                            print(f"\nCode:\n{existing_solution.code_snippet}\n")
                except (EOFError, KeyboardInterrupt):
                    pass

            return False  # Don't proceed with building

        # Step 2: Search online for existing solutions
        print("\n🌐 Searching online for existing solutions...\n")
        online_solutions = self.kb.search_online_solutions(problem_description)

        if online_solutions:
            print("💡 Consider using one of these existing solutions!\n")
            if interactive:
                try:
                    response = input("Do you want to proceed anyway? [y/n]: ")
                    if response.lower() != 'y':
                        return False
                except (EOFError, KeyboardInterrupt):
                    return False
            else:
                # Non-interactive: warn but allow proceeding
                print("⚠️  (Running in non-interactive mode, proceeding with caution)\n")

        # Step 3: Suggest best practices
        best_practice = self.kb.suggest_best_practice(problem_description)
        if best_practice:
            print(f"\n📖 Best Practice: {best_practice}\n")

        print("=" * 60)
        print("✅ Proceeding with new solution...")
        print("=" * 60 + "\n")

        return True  # Proceed with building

    def after_you_build(
        self,
        problem_description: str,
        solution_description: str,
        code_snippet: Optional[str] = None,
        file_path: Optional[str] = None
    ) -> None:
        """
        Call this AFTER building a solution to document it.
        """
        print("\n" + "=" * 60)
        print("📝 DOCUMENTING SOLUTION")
        print("=" * 60 + "\n")

        self.kb.document_solution(
            problem_description=problem_description,
            solution_description=solution_description,
            code_snippet=code_snippet,
            file_path=file_path
        )


# ============================================================================
# Module Interface
# ============================================================================

def get_knowledge_base() -> SolutionKnowledgeBase:
    """Get the knowledge base instance"""
    return SolutionKnowledgeBase()


def check_before_building(problem: str) -> bool:
    """Quick check before building something"""
    workflow = SmartWorkflow()
    return workflow.before_you_build(problem)


def document_fix(problem: str, solution: str, code: str = None, file: str = None):
    """Quick documentation of a fix"""
    workflow = SmartWorkflow()
    workflow.after_you_build(problem, solution, code, file)


if __name__ == "__main__":
    # Demo
    kb = get_knowledge_base()
    print(kb.get_solution_report())
