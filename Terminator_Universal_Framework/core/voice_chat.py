#!/usr/bin/env python3

# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
Voice Chat - Voice input with Bengali/English output
Listens → Sends to Ollama → Speaks response
"""

import subprocess
import sys
import os

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(__file__))

from voice import speak, listen

def chat_with_ollama(prompt: str, model: str = "qwen2", system_instruction: str = "") -> str:
    """Send prompt to Ollama and get response."""
    try:
        full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt

        result = subprocess.run(
            ["ollama", "run", model, full_prompt],
            capture_output=True,
            text=True,
            timeout=60
        )

        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "সময় শেষ হয়ে গেছে। আবার চেষ্টা করুন।"
    except Exception as e:
        return f"Error: {str(e)}"

def voice_chat(input_lang: str = "en", output_lang: str = "bn", model: str = "qwen2"):
    """
    Voice chat loop.

    Args:
        input_lang: Language for speech recognition ('en' or 'bn')
        output_lang: Language for TTS output ('en' or 'bn')
        model: Ollama model to use
    """

    # System instructions based on output language
    if output_lang == "bn":
        system_instruction = "তুমি একজন সহায়ক AI। সবসময় বাংলায় উত্তর দাও। উত্তর সংক্ষিপ্ত এবং স্পষ্ট রাখো।"
    else:
        system_instruction = "You are a helpful AI assistant. Keep responses concise and clear."

    print("\n" + "="*50)
    print(f"  🎤 Voice Chat ({input_lang.upper()} → {output_lang.upper()})")
    print(f"  Model: {model}")
    print("="*50)
    print("\nSay 'quit' or 'exit' to stop.\n")

    while True:
        # Listen for input
        print(f"🎤 Listening ({input_lang})...")
        user_input = listen(input_lang, timeout=10)

        if not user_input:
            print("No speech detected. Try again.\n")
            continue

        print(f"You: {user_input}\n")

        # Check for exit commands
        if user_input.lower() in ['quit', 'exit', 'stop', 'বন্ধ', 'থামো']:
            print("👋 Goodbye!")
            speak("বিদায়!" if output_lang == "bn" else "Goodbye!", output_lang)
            break

        # Get AI response
        print("🤖 Thinking...")
        response = chat_with_ollama(user_input, model, system_instruction)

        print(f"AI: {response}\n")

        # Speak response
        speak(response, output_lang)
        print()

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Voice Chat with Bengali/English')
    parser.add_argument('-i', '--input', default='en', choices=['en', 'bn'],
                        help='Input language (default: en)')
    parser.add_argument('-o', '--output', default='bn', choices=['en', 'bn'],
                        help='Output language (default: bn)')
    parser.add_argument('-m', '--model', default='qwen2',
                        help='Ollama model (default: qwen2)')
    parser.add_argument('--once', action='store_true',
                        help='Single query mode (no loop)')

    args = parser.parse_args()

    if args.once:
        # Single query mode
        print(f"🎤 Listening ({args.input})...")
        user_input = listen(args.input, timeout=10)

        if user_input:
            print(f"You: {user_input}")

            if args.output == "bn":
                system = "তুমি একজন সহায়ক AI। সবসময় বাংলায় উত্তর দাও।"
            else:
                system = "You are a helpful AI."

            response = chat_with_ollama(user_input, args.model, system)
            print(f"AI: {response}")
            speak(response, args.output)
    else:
        # Continuous chat mode
        voice_chat(args.input, args.output, args.model)

if __name__ == '__main__':
    main()
