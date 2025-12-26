#!/usr/bin/env python3

# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""Model switcher for TERMINATOR CLI - switch between Ollama models"""

import json
import os
import subprocess
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / ".terminator_model_config.json"

def load_config():
    """Load model config"""
    with open(CONFIG_PATH) as f:
        return json.load(f)

def save_config(config):
    """Save model config"""
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

def get_current_model():
    """Get currently active model"""
    config = load_config()
    return config.get("current_model", "codestral")

def switch_model(model_name):
    """Switch to a different model"""
    config = load_config()

    # Check if model is available
    if model_name not in config["available_models"]:
        return f"❌ Model '{model_name}' not available. Use /models to list."

    config["current_model"] = model_name
    save_config(config)

    details = config["model_details"].get(model_name, {})
    name = details.get("name", model_name)
    return f"✅ Switched to {name}"

def list_models():
    """List all available models with details"""
    config = load_config()
    current = config.get("current_model", "gemini")

    output = f"🔄 Current model: {current}\n\n"
    output += "Available Cloud Models:\n"

    for model in config["available_models"]:
        marker = "→" if model == current else " "
        details = config["model_details"].get(model, {})
        name = details.get("name", model)
        free = "FREE ✓" if details.get("free") else "PAID"
        speed = details.get("speed", "N/A")
        output += f"  {marker} {model:10} | {name:25} | {free:10} | {speed}\n"

    return output

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(list_models())
    else:
        cmd = sys.argv[1]
        if cmd == "current":
            print(f"Current model: {get_current_model()}")
        elif cmd == "list":
            print(list_models())
        else:
            print(switch_model(cmd))
