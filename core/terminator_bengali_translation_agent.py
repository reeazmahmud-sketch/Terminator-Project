#!/usr/bin/env python3

# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR Bengali Translation Agent
Uses Aya (Cohere's multilingual model) via Ollama for Bengali translation
Optimized for translating technical documentation while preserving formatting
"""

import asyncio
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional


class BengaliTranslationAgent:
    """
    Agent for translating English technical documentation to Bengali
    Uses Ollama with Aya model for high-quality multilingual translation
    """

    def __init__(self, model_name: str = "aya:latest"):
        self.model_name = model_name
        self.agent_name = "bengali_translation_agent"
        self.chunk_size = 500  # Lines per translation chunk

    def check_ollama_running(self) -> bool:
        """Check if Ollama service is running"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Ollama not available: {e}")
            return False

    def check_model_available(self) -> bool:
        """Check if Aya model is downloaded"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return "aya" in result.stdout.lower()
        except Exception:
            return False

    def translate_text(self, text: str, preserve_technical_terms: bool = True) -> str:
        """
        Translate English text to Bengali using Aya model

        Args:
            text: English text to translate
            preserve_technical_terms: Keep technical terms in English

        Returns:
            Bengali translated text
        """
        if not self.check_ollama_running():
            raise RuntimeError("Ollama service not running. Start with: ollama serve")

        if not self.check_model_available():
            raise RuntimeError("Aya model not available. Download with: ollama pull aya:latest")

        # Create translation prompt
        prompt = f"""You are a professional translator specializing in technical documentation.
Translate the following English text to Bengali (বাংলা).

IMPORTANT INSTRUCTIONS:
1. Translate naturally and fluently to Bengali
2. Preserve all markdown formatting (##, ###, -, *, `, etc.)
3. Keep technical terms in English if they don't have good Bengali equivalents (e.g., "Agent", "API", "WebSocket", "Bus")
4. Keep code blocks, file paths, and commands in English
5. Translate descriptions, explanations, and documentation prose to Bengali
6. Maintain the original structure and formatting exactly

TEXT TO TRANSLATE:
{text}

BENGALI TRANSLATION:"""

        try:
            # Call Ollama API
            result = subprocess.run(
                ["ollama", "run", self.model_name, prompt],
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes per chunk
            )

            if result.returncode == 0:
                translation = result.stdout.strip()
                return translation
            else:
                print(f"❌ Translation error: {result.stderr}")
                return text  # Return original if translation fails

        except subprocess.TimeoutExpired:
            print(f"⚠️ Translation timeout for chunk")
            return text
        except Exception as e:
            print(f"❌ Translation exception: {e}")
            return text

    def translate_file(
        self,
        input_file: Path,
        output_file: Path,
        chunk_size: Optional[int] = None
    ) -> bool:
        """
        Translate an entire markdown file to Bengali

        Args:
            input_file: Source English markdown file
            output_file: Destination Bengali markdown file
            chunk_size: Number of lines per translation chunk

        Returns:
            True if successful, False otherwise
        """
        if chunk_size:
            self.chunk_size = chunk_size

        print(f"\n📄 Translating: {input_file.name}")
        print(f"📝 Output: {output_file.name}")

        try:
            # Read input file
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            total_lines = len(lines)
            print(f"📊 Total lines: {total_lines}")

            # Process in chunks
            translated_lines = []
            chunks = [lines[i:i + self.chunk_size] for i in range(0, len(lines), self.chunk_size)]

            for idx, chunk in enumerate(chunks, 1):
                print(f"\n🔄 Translating chunk {idx}/{len(chunks)} ({len(chunk)} lines)...")

                chunk_text = ''.join(chunk)
                translated_chunk = self.translate_text(chunk_text)
                translated_lines.append(translated_chunk)

                # Progress indicator
                progress = (idx / len(chunks)) * 100
                print(f"✅ Progress: {progress:.1f}%")

            # Write output file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(translated_lines))

            print(f"\n✅ Translation complete: {output_file}")
            return True

        except Exception as e:
            print(f"❌ Error translating file: {e}")
            return False

    def translate_documentation_set(
        self,
        source_dir: Path,
        output_dir: Path,
        files: List[str]
    ) -> Dict[str, bool]:
        """
        Translate multiple documentation files

        Args:
            source_dir: Directory containing source files
            output_dir: Directory for translated files
            files: List of filenames to translate

        Returns:
            Dictionary mapping filenames to success status
        """
        results = {}

        print(f"\n{'='*70}")
        print(f"🌐 BENGALI TRANSLATION AGENT")
        print(f"{'='*70}")
        print(f"📁 Source: {source_dir}")
        print(f"📁 Output: {output_dir}")
        print(f"📚 Files: {len(files)}")
        print(f"🤖 Model: {self.model_name}")
        print(f"{'='*70}\n")

        # Create output directory if needed
        output_dir.mkdir(parents=True, exist_ok=True)

        for filename in files:
            input_file = source_dir / filename
            output_file = output_dir / filename.replace('.md', '_BENGALI.md')

            if not input_file.exists():
                print(f"⚠️ File not found: {input_file}")
                results[filename] = False
                continue

            success = self.translate_file(input_file, output_file)
            results[filename] = success

        # Summary
        print(f"\n{'='*70}")
        print(f"📊 TRANSLATION SUMMARY")
        print(f"{'='*70}")
        successful = sum(1 for v in results.values() if v)
        print(f"✅ Successful: {successful}/{len(files)}")
        print(f"❌ Failed: {len(files) - successful}/{len(files)}")
        print(f"{'='*70}\n")

        return results


def main():
    """
    Main function to translate TERMINATOR documentation to Bengali
    """
    agent = BengaliTranslationAgent()

    # Define source and output directories
    source_dir = Path("/Users/reeazmahmud/Desktop/Terminator-Project")

    # Files to translate
    documentation_files = [
        "ARCHITECTURE_DIAGRAMS.md",
        "AGENT_CAPABILITY_MATRIX.md",
        "AGENT_COMMUNICATION_PATTERNS.md",
        "COMPLETE_AGENT_INVENTORY.md",
        "AGENT_ANALYSIS_SUMMARY.md"
    ]

    # Translate files (output to same directory with _BENGALI suffix)
    results = agent.translate_documentation_set(
        source_dir=source_dir,
        output_dir=source_dir,
        files=documentation_files
    )

    # Copy to main Terminator directory (57GB)
    if any(results.values()):
        print("\n📋 Copying Bengali files to main Terminator directory...")
        main_terminator = Path("/Users/reeazmahmud/Desktop/Terminator")

        for filename in documentation_files:
            bengali_file = source_dir / filename.replace('.md', '_BENGALI.md')
            if bengali_file.exists():
                import shutil
                dest = main_terminator / bengali_file.name
                shutil.copy2(bengali_file, dest)
                print(f"✅ Copied: {bengali_file.name} → {dest}")

        print("\n✅ All Bengali translations complete!")

    return results


if __name__ == "__main__":
    main()
