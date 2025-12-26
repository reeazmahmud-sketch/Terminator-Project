#!/usr/bin/env python3
"""
TERMINATOR - Local LLM Activation
==================================
Command: /activateLocalLLM

Activates local Ollama LLM (works offline, completely free)
"""

import subprocess
import sys
import time

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(
            ["which", "ollama"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False

def check_ollama_running():
    """Check if Ollama server is running"""
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/tags"],
            capture_output=True,
            text=True,
            timeout=2
        )
        return result.returncode == 0
    except:
        return False

def list_ollama_models():
    """List installed Ollama models"""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True
        )
        return result.stdout
    except:
        return None

def start_ollama():
    """Start Ollama server"""
    try:
        print("🚀 Starting Ollama server...")
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(3)  # Wait for server to start
        return True
    except:
        return False

def install_default_model():
    """Install llama3.2 model"""
    print("📦 Installing llama3.2 model (this may take a few minutes)...")
    try:
        result = subprocess.run(
            ["ollama", "pull", "llama3.2"],
            capture_output=False
        )
        return result.returncode == 0
    except:
        return False

def test_ollama():
    """Test Ollama with a simple query"""
    print("🧪 Testing Ollama...")
    try:
        result = subprocess.run(
            ["ollama", "run", "llama3.2", "Say hello in one sentence"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print("✅ Ollama Response:")
            print(f"   {result.stdout.strip()}")
            return True
        return False
    except:
        return False

def main():
    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║         TERMINATOR - LOCAL LLM ACTIVATION                    ║")
    print("║              Ollama (FREE, OFFLINE, UNLIMITED)               ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

    # Check if Ollama is installed
    if not check_ollama_installed():
        print("❌ Ollama is not installed")
        print()
        print("📦 Install Ollama:")
        print("   brew install ollama")
        print()
        print("   OR download from: https://ollama.com")
        print()
        return 1

    print("✅ Ollama is installed")
    print()

    # Check if Ollama is running
    if not check_ollama_running():
        print("⏳ Ollama server is not running, starting it...")
        if not start_ollama():
            print("❌ Failed to start Ollama server")
            print()
            print("Try manually:")
            print("   ollama serve")
            print()
            return 1
        print("✅ Ollama server started")
    else:
        print("✅ Ollama server is running")

    print()

    # List installed models
    print("📋 Checking installed models...")
    models_output = list_ollama_models()

    if models_output and "llama3.2" in models_output:
        print("✅ llama3.2 model is installed")
        print()
        print(models_output)
    else:
        print("⚠️  llama3.2 model not found")
        print()
        install_default_model()

    print()

    # Test Ollama
    if test_ollama():
        print()
        print("🎉 LOCAL LLM IS ACTIVE!")
        print()
        print("━" * 60)
        print("📊 LOCAL LLM STATUS")
        print("━" * 60)
        print("Provider:    Ollama")
        print("Model:       llama3.2 (3B parameters)")
        print("Speed:       100-2000ms")
        print("Cost:        FREE (completely local)")
        print("Internet:    NOT REQUIRED")
        print("Limit:       UNLIMITED")
        print("Privacy:     100% (never leaves your Mac)")
        print("━" * 60)
        print()
        print("✅ You can now use local LLM in TERMINATOR!")
        print()
        print("Usage:")
        print("   • TERMINATOR will use local LLM by default")
        print("   • No API keys needed")
        print("   • Works offline")
        print("   • Completely private")
        print()
        return 0
    else:
        print()
        print("❌ Ollama test failed")
        print()
        print("Troubleshooting:")
        print("1. Make sure Ollama is running: ollama serve")
        print("2. Test manually: ollama run llama3.2 'hello'")
        print("3. Check logs: tail -f ~/.ollama/logs/server.log")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
