#!/usr/bin/env python3
"""
Agent Spec Transpiler
Converts universal agent specs to platform-specific formats.
One source of truth → multiple targets.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any


class AgentTranspiler:
    """Transpile agent specs to Claude, OpenAI, and llama.cpp formats."""

    def __init__(self, source_dir: str = "~/.agents"):
        self.source_dir = Path(source_dir).expanduser()
        self.output_dir = Path("~/.agents/transpiled").expanduser()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def read_source(self, filename: str) -> str:
        """Read source agent spec."""
        filepath = self.source_dir / filename
        with open(filepath, 'r') as f:
            return f.read().strip()

    def transpile_to_claude(self, content: str, name: str) -> Dict[str, Any]:
        """Convert to Claude format."""
        return {
            "name": name,
            "description": f"Auto-generated from {name}",
            "system_prompt": content,
            "tools": ["bash", "filesystem"]
        }

    def transpile_to_openai(self, content: str, name: str) -> Dict[str, Any]:
        """Convert to OpenAI format."""
        return {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": content}
            ],
            "temperature": 0.7
        }

    def transpile_to_llama(self, content: str, name: str) -> str:
        """Convert to llama.cpp format."""
        return f"""<|im_start|>system
{content}
<|im_end|>"""

    def transpile_to_ollama(self, content: str, name: str) -> Dict[str, Any]:
        """Convert to Ollama Modelfile format."""
        return {
            "modelfile": f"""FROM llama3

SYSTEM \"\"\"
{content}
\"\"\"

PARAMETER temperature 0.7
PARAMETER top_p 0.9
"""
        }

    def transpile_all(self, source_file: str):
        """Transpile one source file to all formats."""
        name = Path(source_file).stem
        content = self.read_source(source_file)

        # Claude format
        claude_output = self.output_dir / "claude" / f"{name}.yaml"
        claude_output.parent.mkdir(parents=True, exist_ok=True)
        with open(claude_output, 'w') as f:
            yaml.dump(self.transpile_to_claude(content, name), f, default_flow_style=False)

        # OpenAI format
        openai_output = self.output_dir / "openai" / f"{name}.json"
        openai_output.parent.mkdir(parents=True, exist_ok=True)
        with open(openai_output, 'w') as f:
            json.dump(self.transpile_to_openai(content, name), f, indent=2)

        # llama.cpp format
        llama_output = self.output_dir / "llama" / f"{name}.txt"
        llama_output.parent.mkdir(parents=True, exist_ok=True)
        with open(llama_output, 'w') as f:
            f.write(self.transpile_to_llama(content, name))

        # Ollama format
        ollama_output = self.output_dir / "ollama" / f"{name}.modelfile"
        ollama_output.parent.mkdir(parents=True, exist_ok=True)
        with open(ollama_output, 'w') as f:
            f.write(self.transpile_to_ollama(content, name)["modelfile"])

        return {
            "claude": str(claude_output),
            "openai": str(openai_output),
            "llama": str(llama_output),
            "ollama": str(ollama_output)
        }

    def transpile_directory(self):
        """Transpile all agent specs in source directory."""
        results = {}

        for filepath in self.source_dir.glob("*.txt"):
            name = filepath.name
            print(f"Transpiling {name}...")
            results[name] = self.transpile_all(name)

        for filepath in self.source_dir.glob("*.yaml"):
            # Skip YAML files that are already formatted
            if filepath.name not in ["coding.yaml"]:
                continue
            name = filepath.name
            # Read YAML and extract system_prompt or role description
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)

            # Build content from YAML structure
            if isinstance(data, dict):
                content_parts = []
                if "role" in data:
                    content_parts.append(f"You are a {data['role']}.")
                if "principles" in data:
                    content_parts.extend(data["principles"])
                content = "\n".join(content_parts)

                # Write as .txt for consistency
                txt_path = self.source_dir / f"{filepath.stem}.txt"
                if not txt_path.exists():
                    with open(txt_path, 'w') as f:
                        f.write(content)
                    print(f"Converted {name} to {txt_path.name}")
                    results[txt_path.name] = self.transpile_all(txt_path.name)

        return results


def main():
    """CLI entry point."""
    transpiler = AgentTranspiler()

    print("Agent Spec Transpiler")
    print("=" * 50)
    print(f"Source: {transpiler.source_dir}")
    print(f"Output: {transpiler.output_dir}")
    print()

    results = transpiler.transpile_directory()

    print()
    print("Transpilation complete!")
    print(f"Total agents: {len(results)}")
    print()

    for agent, outputs in results.items():
        print(f"✓ {agent}")
        for platform, path in outputs.items():
            print(f"  → {platform}: {path}")


if __name__ == "__main__":
    main()
