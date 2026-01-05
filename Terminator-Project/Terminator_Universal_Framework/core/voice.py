#!/usr/bin/env python3

# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
Voice Module - Bengali & English TTS/STT
Supports text-to-speech and speech-to-text in multiple languages
"""

import asyncio
import os
import tempfile
import subprocess
import sys

# TTS imports
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# STT imports
try:
    import speech_recognition as sr
    STT_AVAILABLE = True
except ImportError:
    STT_AVAILABLE = False

# === VOICE CONFIGURATIONS ===

VOICES = {
    'bn': {
        'edge': 'bn-BD-NabanitaNeural',  # Bengali female
        'edge_male': 'bn-BD-PradeepNeural',  # Bengali male
        'gtts': 'bn'
    },
    'en': {
        'edge': 'en-US-JennyNeural',  # English female
        'edge_male': 'en-US-GuyNeural',  # English male
        'gtts': 'en'
    },
    'terminator': {
        'edge': 'en-GB-RyanNeural',  # British male - Terminator style
        'gtts': 'en'
    }
}

# === TEXT TO SPEECH ===

async def speak_edge(text: str, lang: str = 'en', voice: str = None) -> str:
    """Generate speech using Edge TTS (Microsoft)."""
    if not EDGE_TTS_AVAILABLE:
        raise ImportError("edge-tts not installed. Run: pip install edge-tts")

    # Get voice
    if voice is None:
        voice = VOICES.get(lang, VOICES['en'])['edge']

    # Generate audio
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
        output_file = f.name

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

    return output_file

def speak_gtts(text: str, lang: str = 'en') -> str:
    """Generate speech using Google TTS."""
    if not GTTS_AVAILABLE:
        raise ImportError("gTTS not installed. Run: pip install gtts")

    lang_code = VOICES.get(lang, VOICES['en'])['gtts']

    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
        output_file = f.name

    tts = gTTS(text=text, lang=lang_code)
    tts.save(output_file)

    return output_file

def play_audio(filepath: str):
    """Play audio file using system player."""
    if sys.platform == 'darwin':  # macOS
        subprocess.run(['afplay', filepath], check=True)
    elif sys.platform == 'linux':
        subprocess.run(['mpg123', '-q', filepath], check=True)
    else:
        subprocess.run(['start', filepath], shell=True, check=True)

    # Cleanup
    os.unlink(filepath)

def speak(text: str, lang: str = 'en', engine: str = 'edge'):
    """
    Speak text in specified language.

    Args:
        text: Text to speak
        lang: Language code ('en', 'bn', 'hi')
        engine: TTS engine ('edge' or 'gtts')
    """
    try:
        if engine == 'edge' and EDGE_TTS_AVAILABLE:
            audio_file = asyncio.run(speak_edge(text, lang))
        elif GTTS_AVAILABLE:
            audio_file = speak_gtts(text, lang)
        else:
            print("No TTS engine available. Install: pip install edge-tts gtts")
            return

        play_audio(audio_file)

    except Exception as e:
        print(f"TTS Error: {e}")

# === SPEECH TO TEXT ===

def listen(lang: str = 'en-US', timeout: int = 5) -> str:
    """
    Listen for speech and convert to text.

    Args:
        lang: Language code for recognition
        timeout: Seconds to wait for speech

    Returns:
        Recognized text or empty string
    """
    if not STT_AVAILABLE:
        print("SpeechRecognition not installed. Run: pip install SpeechRecognition")
        return ""

    recognizer = sr.Recognizer()

    # Map simple codes to recognition codes
    lang_map = {
        'bn': 'bn-BD',
        'en': 'en-US'
    }
    recognition_lang = lang_map.get(lang, lang)

    try:
        with sr.Microphone() as source:
            print(f"🎤 Listening ({recognition_lang})...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=timeout)

        print("Processing...")
        text = recognizer.recognize_google(audio, language=recognition_lang)
        return text

    except sr.WaitTimeoutError:
        print("No speech detected")
        return ""
    except sr.UnknownValueError:
        print("Could not understand audio")
        return ""
    except sr.RequestError as e:
        print(f"Recognition error: {e}")
        return ""

# === FILE OPERATIONS ===

def read_bengali_file(filepath: str) -> str:
    """Read a file with Bengali text."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_bengali_file(filepath: str, text: str):
    """Write Bengali text to a file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)

# === CLI INTERFACE ===

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Voice TTS/STT for Bengali & English')
    subparsers = parser.add_subparsers(dest='command')

    # Speak command
    speak_parser = subparsers.add_parser('speak', help='Text to speech')
    speak_parser.add_argument('text', help='Text to speak')
    speak_parser.add_argument('-l', '--lang', default='en', help='Language (en, bn, hi)')
    speak_parser.add_argument('-e', '--engine', default='edge', help='TTS engine (edge, gtts)')

    # Listen command
    listen_parser = subparsers.add_parser('listen', help='Speech to text')
    listen_parser.add_argument('-l', '--lang', default='en', help='Language (en, bn, hi)')
    listen_parser.add_argument('-t', '--timeout', type=int, default=5, help='Timeout seconds')

    # List voices command
    subparsers.add_parser('voices', help='List available voices')

    args = parser.parse_args()

    if args.command == 'speak':
        speak(args.text, args.lang, args.engine)

    elif args.command == 'listen':
        text = listen(args.lang, args.timeout)
        if text:
            print(f"You said: {text}")

    elif args.command == 'voices':
        print("\nAvailable voices:")
        for lang, voices in VOICES.items():
            print(f"\n{lang.upper()}:")
            for engine, voice in voices.items():
                print(f"  {engine}: {voice}")

    else:
        parser.print_help()

if __name__ == '__main__':
    main()
