#!/usr/bin/env python3

# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
Terminator Model Manager - Intelligent Multi-Model LLM Integration
Automatically selects the best local model for each task
"""

import json
import os
import subprocess
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple


# Colors for terminal output
class Colors:
    BLUE = "\033[0;34m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    RED = "\033[0;31m"
    CYAN = "\033[0;36m"
    MAGENTA = "\033[0;35m"
    BOLD = "\033[1m"
    NC = "\033[0m"  # No Color


class TaskType(Enum):
    """Different types of tasks Terminator can handle"""

    GENERAL = "general"
    CODING = "coding"
    REASONING = "reasoning"
    FAST = "fast"
    CREATIVE = "creative"
    ANALYSIS = "analysis"
    MATH = "math"
    CONVERSATION = "conversation"
    TRANSLATION = "translation"


@dataclass
class ModelInfo:
    """Information about an LLM model"""

    name: str
    size_gb: float
    parameters: str
    strengths: List[TaskType]
    speed: str  # "fast", "medium", "slow"
    context_length: int
    quantization: str
    description: str
    priority: int  # Higher is better for default selection


class TerminatorModelManager:
    """Intelligent model manager for Terminator AI Assistant"""

    # Model database with capabilities and recommendations
    MODEL_DATABASE = {
        "phi4": ModelInfo(
            name="phi4",
            size_gb=9.1,
            parameters="14.7B",
            strengths=[
                TaskType.REASONING,
                TaskType.MATH,
                TaskType.FAST,
                TaskType.ANALYSIS,
            ],
            speed="fast",
            context_length=16384,
            quantization="Q4_K_M",
            description="Microsoft Phi-4: Excellent reasoning, fast, efficient",
            priority=95,
        ),
        "codestral": ModelInfo(
            name="Codestral",
            size_gb=12.0,
            parameters="22B",
            strengths=[TaskType.CODING, TaskType.ANALYSIS],
            speed="medium",
            context_length=32768,
            quantization="Q4_K_M",
            description="Mistral Codestral: Best for coding tasks",
            priority=90,
        ),
        "qwen2": ModelInfo(
            name="qwen2",
            size_gb=4.4,
            parameters="7B",
            strengths=[
                TaskType.GENERAL,
                TaskType.FAST,
                TaskType.CONVERSATION,
                TaskType.CODING,
            ],
            speed="fast",
            context_length=32768,
            quantization="Q4_K_M",
            description="Qwen2: Fast, versatile, great all-rounder",
            priority=85,
        ),
        "llama3": ModelInfo(
            name="llama3",
            size_gb=4.7,
            parameters="8B",
            strengths=[TaskType.GENERAL, TaskType.CONVERSATION, TaskType.CREATIVE],
            speed="fast",
            context_length=8192,
            quantization="Q4_K_M",
            description="Llama 3: Excellent general purpose model",
            priority=80,
        ),
        "gpt-oss": ModelInfo(
            name="gpt-oss",
            size_gb=13.0,
            parameters="22B",
            strengths=[TaskType.GENERAL, TaskType.REASONING, TaskType.CREATIVE],
            speed="medium",
            context_length=8192,
            quantization="Q4_K_M",
            description="GPT-OSS: Open source GPT-like model",
            priority=75,
        ),
        "gemma3:12b": ModelInfo(
            name="gemma3:12b",
            size_gb=8.1,
            parameters="12B",
            strengths=[TaskType.GENERAL, TaskType.REASONING, TaskType.CONVERSATION],
            speed="medium",
            context_length=8192,
            quantization="Q4_K_M",
            description="Google Gemma 3: Efficient and capable",
            priority=70,
        ),
        "opencoder": ModelInfo(
            name="opencoder",
            size_gb=4.7,
            parameters="8B",
            strengths=[TaskType.CODING],
            speed="fast",
            context_length=8192,
            quantization="Q4_K_M",
            description="OpenCoder: Specialized coding model",
            priority=65,
        ),
        "codellama": ModelInfo(
            name="codellama",
            size_gb=3.8,
            parameters="7B",
            strengths=[TaskType.CODING],
            speed="fast",
            context_length=16384,
            quantization="Q4_K_M",
            description="Code Llama: Meta's coding specialist",
            priority=60,
        ),
        "samantha-mistral:7b": ModelInfo(
            name="samantha-mistral:7b",
            size_gb=4.1,
            parameters="7B",
            strengths=[TaskType.CONVERSATION, TaskType.CREATIVE],
            speed="fast",
            context_length=8192,
            quantization="Q4_K_M",
            description="Samantha: Conversational and empathetic",
            priority=55,
        ),
        "llava:13b": ModelInfo(
            name="llava:13b",
            size_gb=8.0,
            parameters="13B",
            strengths=[TaskType.ANALYSIS, TaskType.CREATIVE],
            speed="medium",
            context_length=4096,
            quantization="Q4_K_M",
            description="LLaVA: Vision-language model",
            priority=50,
        ),
    }

    def __init__(self, config_file: str = None):
        """Initialize the model manager"""
        self.config_file = config_file or os.path.expanduser(
            "~/.terminator_model_config.json"
        )
        self.config = self._load_config()
        self.available_models = self._get_available_models()

    def _load_config(self) -> Dict:
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except:
                pass

        # Default configuration
        return {
            "default_model": "phi4",
            "auto_select": True,
            "task_preferences": {},
            "fallback_model": "qwen2",
            "min_speed_preference": "medium",  # "fast", "medium", "slow"
        }

    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, indent=2, fp=f)
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not save config: {e}{Colors.NC}")

    def _get_available_models(self) -> List[str]:
        """Get list of models available in Ollama"""
        try:
            result = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True, timeout=5
            )

            if result.returncode != 0:
                return []

            lines = result.stdout.strip().split("\n")[1:]  # Skip header
            models = []

            for line in lines:
                if line.strip():
                    parts = line.split()
                    if parts:
                        model_name = parts[0].lower()
                        # Normalize model names
                        if ":" in model_name:
                            base_name = model_name.split(":")[0]
                            if (
                                base_name in self.MODEL_DATABASE
                                or model_name in self.MODEL_DATABASE
                            ):
                                models.append(model_name)
                        elif model_name in self.MODEL_DATABASE:
                            models.append(model_name)

            return models
        except Exception as e:
            print(f"{Colors.RED}Error getting models: {e}{Colors.NC}")
            return []

    def select_model_for_task(self, task_type: TaskType, query: str = "") -> str:
        """
        Intelligently select the best model for a given task

        Args:
            task_type: Type of task to perform
            query: Optional query text for additional context

        Returns:
            Best model name for the task
        """
        if not self.config.get("auto_select", True):
            return self.config.get("default_model", "phi4")

        # Check if user has a preference for this task
        if task_type.value in self.config.get("task_preferences", {}):
            preferred = self.config["task_preferences"][task_type.value]
            if preferred in self.available_models:
                return preferred

        # Find best available model for this task
        best_model = None
        best_score = -1

        for model_name in self.available_models:
            # Normalize model name for lookup
            lookup_name = model_name.split(":")[0] if ":" in model_name else model_name

            if (
                lookup_name not in self.MODEL_DATABASE
                and model_name not in self.MODEL_DATABASE
            ):
                continue

            model_info = self.MODEL_DATABASE.get(model_name) or self.MODEL_DATABASE.get(
                lookup_name
            )

            # Calculate score
            score = 0

            # Task match bonus
            if task_type in model_info.strengths:
                score += 50

            # Priority bonus
            score += model_info.priority

            # Speed preference
            speed_pref = self.config.get("min_speed_preference", "medium")
            if speed_pref == "fast" and model_info.speed == "fast":
                score += 20
            elif speed_pref == "medium" and model_info.speed in ["fast", "medium"]:
                score += 10

            # Context length bonus for long queries
            if len(query) > 2000 and model_info.context_length > 16000:
                score += 15

            if score > best_score:
                best_score = score
                best_model = model_name

        # Fallback to default or first available
        if not best_model:
            best_model = self.config.get("default_model", "phi4")
            if best_model not in self.available_models and self.available_models:
                best_model = self.available_models[0]

        return best_model

    def detect_task_type(self, query: str) -> TaskType:
        """
        Analyze query and detect the task type

        Args:
            query: User's query text

        Returns:
            Detected task type
        """
        query_lower = query.lower()

        # Coding indicators
        coding_keywords = [
            "code",
            "program",
            "function",
            "class",
            "debug",
            "error",
            "python",
            "javascript",
            "java",
            "bug",
            "syntax",
            "compile",
            "algorithm",
            "implement",
            "refactor",
        ]
        if any(word in query_lower for word in coding_keywords):
            return TaskType.CODING

        # Math indicators
        math_keywords = [
            "calculate",
            "math",
            "equation",
            "solve",
            "algebra",
            "geometry",
            "statistics",
            "probability",
            "compute",
        ]
        if any(word in query_lower for word in math_keywords):
            return TaskType.MATH

        # Reasoning indicators
        reasoning_keywords = [
            "analyze",
            "compare",
            "evaluate",
            "why",
            "how",
            "explain",
            "reason",
            "logic",
            "argument",
            "proof",
        ]
        if any(word in query_lower for word in reasoning_keywords):
            return TaskType.REASONING

        # Creative indicators
        creative_keywords = [
            "write",
            "story",
            "creative",
            "poem",
            "imagine",
            "design",
            "create",
            "generate",
            "compose",
        ]
        if any(word in query_lower for word in creative_keywords):
            return TaskType.CREATIVE

        # Translation indicators
        translation_keywords = [
            "translate",
            "translation",
            "bengali",
            "bangla",
            "language",
            "বাংলা",
        ]
        if any(word in query_lower for word in translation_keywords):
            return TaskType.TRANSLATION

        # Default to conversation for short queries
        if len(query.split()) < 10:
            return TaskType.FAST

        # Default to general for everything else
        return TaskType.GENERAL

    def get_best_model(self, query: str) -> Tuple[str, TaskType]:
        """
        Get the best model for a query

        Args:
            query: User's query

        Returns:
            Tuple of (model_name, detected_task_type)
        """
        task_type = self.detect_task_type(query)
        model = self.select_model_for_task(task_type, query)
        return model, task_type

    def set_default_model(self, model_name: str):
        """Set the default model"""
        if model_name in self.available_models:
            self.config["default_model"] = model_name
            self._save_config()
            print(f"{Colors.GREEN}✅ Default model set to: {model_name}{Colors.NC}")
        else:
            print(f"{Colors.RED}❌ Model '{model_name}' not found{Colors.NC}")

    def set_task_preference(self, task_type: TaskType, model_name: str):
        """Set preferred model for a specific task type"""
        if model_name in self.available_models:
            if "task_preferences" not in self.config:
                self.config["task_preferences"] = {}
            self.config["task_preferences"][task_type.value] = model_name
            self._save_config()
            print(
                f"{Colors.GREEN}✅ Set {task_type.value} tasks to use: {model_name}{Colors.NC}"
            )
        else:
            print(f"{Colors.RED}❌ Model '{model_name}' not found{Colors.NC}")

    def toggle_auto_select(self):
        """Toggle automatic model selection"""
        self.config["auto_select"] = not self.config.get("auto_select", True)
        self._save_config()
        status = "enabled" if self.config["auto_select"] else "disabled"
        print(f"{Colors.CYAN}Auto-select {status}{Colors.NC}")

    def show_status(self):
        """Display current configuration and available models"""
        print(
            f"\n{Colors.BOLD}{Colors.BLUE}╔══════════════════════════════════════════════════════════╗{Colors.NC}"
        )
        print(
            f"{Colors.BOLD}{Colors.BLUE}║       🤖  TERMINATOR MODEL MANAGER STATUS  🤖               ║{Colors.NC}"
        )
        print(
            f"{Colors.BOLD}{Colors.BLUE}╚══════════════════════════════════════════════════════════╝{Colors.NC}\n"
        )

        print(f"{Colors.CYAN}Configuration:{Colors.NC}")
        print(
            f"  Default Model: {Colors.GREEN}{self.config.get('default_model', 'phi4')}{Colors.NC}"
        )
        print(
            f"  Auto-Select: {Colors.GREEN if self.config.get('auto_select', True) else Colors.RED}"
            f"{'Enabled' if self.config.get('auto_select', True) else 'Disabled'}{Colors.NC}"
        )
        print(
            f"  Fallback Model: {Colors.YELLOW}{self.config.get('fallback_model', 'qwen2')}{Colors.NC}"
        )

        print(f"\n{Colors.CYAN}Task Preferences:{Colors.NC}")
        task_prefs = self.config.get("task_preferences", {})
        if task_prefs:
            for task, model in task_prefs.items():
                print(f"  {task}: {Colors.GREEN}{model}{Colors.NC}")
        else:
            print(f"  {Colors.YELLOW}None set (using auto-detection){Colors.NC}")

        print(
            f"\n{Colors.CYAN}Available Models ({len(self.available_models)}):{Colors.NC}"
        )
        for model_name in sorted(self.available_models):
            lookup_name = model_name.split(":")[0] if ":" in model_name else model_name
            model_info = self.MODEL_DATABASE.get(model_name) or self.MODEL_DATABASE.get(
                lookup_name
            )

            if model_info:
                strengths = ", ".join([t.value for t in model_info.strengths[:3]])
                print(
                    f"  {Colors.GREEN}✓{Colors.NC} {Colors.BOLD}{model_name}{Colors.NC}"
                )
                print(
                    f"    Size: {model_info.size_gb}GB | Params: {model_info.parameters} | "
                    f"Speed: {model_info.speed}"
                )
                print(f"    Best for: {Colors.CYAN}{strengths}{Colors.NC}")
                print(f"    {model_info.description}")
            else:
                print(f"  {Colors.YELLOW}•{Colors.NC} {model_name} (custom model)")

        print()

    def benchmark_model(self, model_name: str, test_type: str = "quick") -> Dict:
        """
        Benchmark a model's performance

        Args:
            model_name: Name of model to benchmark
            test_type: "quick" or "full"

        Returns:
            Dictionary with benchmark results
        """
        if model_name not in self.available_models:
            return {"error": "Model not found"}

        print(f"\n{Colors.CYAN}Benchmarking {model_name}...{Colors.NC}")

        test_prompts = {
            "simple": "What is 2+2?",
            "reasoning": "If a train travels 60 miles per hour for 2.5 hours, how far does it go?",
            "coding": "Write a Python function to calculate fibonacci numbers.",
        }

        results = {"model": model_name, "timestamp": time.time(), "tests": {}}

        for test_name, prompt in test_prompts.items():
            if test_type == "quick" and test_name not in ["simple", "reasoning"]:
                continue

            print(f"  Testing: {test_name}...", end=" ", flush=True)
            start = time.time()

            try:
                result = subprocess.run(
                    ["ollama", "run", model_name, prompt],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                elapsed = time.time() - start
                response_length = len(result.stdout)

                results["tests"][test_name] = {
                    "time": round(elapsed, 2),
                    "response_length": response_length,
                    "tokens_per_second": round(response_length / elapsed, 2)
                    if elapsed > 0
                    else 0,
                    "success": result.returncode == 0,
                }

                print(f"{Colors.GREEN}✓{Colors.NC} ({elapsed:.2f}s)")
            except Exception as e:
                results["tests"][test_name] = {"error": str(e), "success": False}
                print(f"{Colors.RED}✗{Colors.NC}")

        # Calculate overall score
        successful_tests = [
            t for t in results["tests"].values() if t.get("success", False)
        ]
        if successful_tests:
            avg_time = sum(t["time"] for t in successful_tests) / len(successful_tests)
            avg_tps = sum(t["tokens_per_second"] for t in successful_tests) / len(
                successful_tests
            )

            results["summary"] = {
                "avg_response_time": round(avg_time, 2),
                "avg_tokens_per_second": round(avg_tps, 2),
                "success_rate": len(successful_tests) / len(results["tests"]),
            }

            print(f"\n{Colors.CYAN}Summary:{Colors.NC}")
            print(f"  Avg Response Time: {Colors.YELLOW}{avg_time:.2f}s{Colors.NC}")
            print(f"  Avg Tokens/Second: {Colors.YELLOW}{avg_tps:.2f}{Colors.NC}")
            print(
                f"  Success Rate: {Colors.GREEN}{results['summary']['success_rate'] * 100:.0f}%{Colors.NC}"
            )

        return results

    def recommend_models(self):
        """Recommend best models to download based on current setup"""
        print(
            f"\n{Colors.BOLD}{Colors.MAGENTA}🌟 RECOMMENDED MODELS TO DOWNLOAD 🌟{Colors.NC}\n"
        )

        recommendations = [
            {
                "name": "qwen2.5:32b",
                "reason": "Best all-around model, excellent coding and reasoning",
                "command": "ollama pull qwen2.5:32b",
                "priority": "HIGH",
            },
            {
                "name": "deepseek-r1:14b",
                "reason": "Latest reasoning model, excellent for complex tasks",
                "command": "ollama pull deepseek-r1:14b",
                "priority": "HIGH",
            },
            {
                "name": "llama3.3:70b",
                "reason": "Meta's best open model, great for general tasks",
                "command": "ollama pull llama3.3:70b",
                "priority": "MEDIUM",
            },
            {
                "name": "qwen2.5-coder:32b",
                "reason": "Specialized coding model, beats many commercial models",
                "command": "ollama pull qwen2.5-coder:32b",
                "priority": "MEDIUM",
            },
            {
                "name": "gemma2:27b",
                "reason": "Google's efficient model, good balance",
                "command": "ollama pull gemma2:27b",
                "priority": "LOW",
            },
        ]

        for rec in recommendations:
            priority_color = (
                Colors.RED
                if rec["priority"] == "HIGH"
                else (Colors.YELLOW if rec["priority"] == "MEDIUM" else Colors.GREEN)
            )

            print(
                f"{priority_color}[{rec['priority']}]{Colors.NC} {Colors.BOLD}{rec['name']}{Colors.NC}"
            )
            print(f"  Reason: {rec['reason']}")
            print(f"  Command: {Colors.CYAN}{rec['command']}{Colors.NC}\n")

    def install_model(self, model_name: str):
        """Download and install a model"""
        print(f"\n{Colors.CYAN}Installing {model_name}...{Colors.NC}")
        print(
            f"{Colors.YELLOW}This may take several minutes depending on model size.{Colors.NC}\n"
        )

        try:
            subprocess.run(["ollama", "pull", model_name], check=True)
            print(f"\n{Colors.GREEN}✅ Successfully installed {model_name}{Colors.NC}")

            # Refresh available models
            self.available_models = self._get_available_models()
        except subprocess.CalledProcessError:
            print(f"\n{Colors.RED}❌ Failed to install {model_name}{Colors.NC}")
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Installation cancelled{Colors.NC}")


def main():
    """CLI interface for model manager"""
    import sys

    manager = TerminatorModelManager()

    if len(sys.argv) < 2:
        manager.show_status()
        print(f"{Colors.CYAN}Commands:{Colors.NC}")
        print(f"  status              - Show current status")
        print(f"  select <query>      - Get best model for query")
        print(f"  set <model>         - Set default model")
        print(f"  prefer <task> <model> - Set task preference")
        print(f"  toggle              - Toggle auto-select")
        print(f"  benchmark <model>   - Benchmark a model")
        print(f"  recommend           - Show recommended models")
        print(f"  install <model>     - Install a model")
        return

    command = sys.argv[1]

    if command == "status":
        manager.show_status()

    elif command == "select" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        model, task_type = manager.get_best_model(query)
        print(
            f"\n{Colors.GREEN}Best model for query:{Colors.NC} {Colors.BOLD}{model}{Colors.NC}"
        )
        print(f"{Colors.CYAN}Detected task type:{Colors.NC} {task_type.value}")

    elif command == "set" and len(sys.argv) > 2:
        manager.set_default_model(sys.argv[2])

    elif command == "prefer" and len(sys.argv) > 3:
        try:
            task = TaskType(sys.argv[2])
            manager.set_task_preference(task, sys.argv[3])
        except ValueError:
            print(f"{Colors.RED}Invalid task type. Valid types:{Colors.NC}")
            for task in TaskType:
                print(f"  - {task.value}")

    elif command == "toggle":
        manager.toggle_auto_select()

    elif command == "benchmark" and len(sys.argv) > 2:
        manager.benchmark_model(sys.argv[2])

    elif command == "recommend":
        manager.recommend_models()

    elif command == "install" and len(sys.argv) > 2:
        manager.install_model(sys.argv[2])

    else:
        print(f"{Colors.RED}Unknown command or missing arguments{Colors.NC}")


if __name__ == "__main__":
    main()

def get_model_manager():
    """Module-level access to model manager"""
    return TerminatorModelManager()
