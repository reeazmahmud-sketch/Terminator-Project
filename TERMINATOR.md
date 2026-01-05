# 🤖 TERMINATOR AI Agent System

Welcome to the **TERMINATOR** Master Manual. This system is a multi-interface AI orchestrator combining local LLMs, specialized agents, and a universal control interface.

## 🚀 Quick Start
Run `./start_cli.sh` to enter the Universal CLI.

## 📋 Core Commands
- `/help` - Show all available commands.
- `/status` - Check system health and service availability.
- `/doctor` - Run full system diagnostics and fix common issues.
- `/init` - Initialize the system, check dependencies, and onboard.
- `/modules` - Manage the dynamic module system.
- `/iot` - Control smart home devices (Simulated or OpenHAB).

## 📦 Module System
Terminator supports a modular architecture. You can find modules in `modules/scripts/`.
- **IoT Module:** `/iot` - Smart home control and logic engine.
- **OpenHAB:** `/openhab` - Integration with OpenHAB servers.
- **NotebookLLM:** `/notebook` - Local code analysis and podcast generation.

## 🛠️ Architecture
- **Core:** `terminator_universal_cli.py` (Main entry)
- **Engine:** `modules/core/module_loader.py` (Dynamic extension)
- **Intelligence:** Ollama (Local LLM) or Google Gemini (Cloud)

## 🩺 System Diagnostics (/doctor)
The doctor command checks:
1. Python version and dependencies.
2. Local LLM (Ollama) availability.
3. Directory structure integrity.
4. Module loading status.

## 🏗️ Initialization (/init)
The init command:
1. Creates missing directories (`.logs`, `modules/scripts`).
2. Validates API keys in `.env`.
3. Sets up the default configuration.

---
*Generated on 2026-01-05*
