# Terminator System Testing Guide

This guide outlines the steps to verify all features of the Terminator AI System, ensuring independence, modularity, and functionality.

## 1. Portability & Independence
**Goal:** Verify the system runs without hardcoded paths.
1. Run the verification script: `python3 verify_portability.py`
2. **Success Criteria:** 
   - "Root matches current directory"
   - No errors during module loading.

## 2. System Initialization
**Goal:** Verify onboarding (`/init`) and diagnostics (`/doctor`).
1. Start CLI: `./start_cli.sh` (or `python3 terminator_universal_cli.py`)
2. Run `/doctor`
   - **Expect:** All checks "OK" or "✓".
3. Run `/init`
   - **Expect:** "Initialization complete" message.

## 3. Core Commands
**Goal:** Verify aliases and basic tools.
- `/directory` -> Lists files.
- `/ide` -> Tries to open a file (e.g., `/ide README.md`).
- `/quit` -> Exits the CLI.

## 4. Module System
**Goal:** Verify dynamic extension loading.
1. `/modules list` -> Should show `smart_home`, `openhab`, `system_utils`.
2. `/modules reload` -> Should refresh modules.

## 5. IoT & Smart Home
**Goal:** Verify device control and logic.
1. `/iot scan` -> Find simulated devices.
2. `/iot list` -> Show status.
3. `/iot add test_light light` -> Create a device.
4. `/iot rule add if test_light on then ac_unit on` -> Create logic.
5. `/iot set test_light on` -> Trigger logic.
   - **Expect:** AC unit turns ON automatically.
6. `/iot scene capture test_scene` -> Save state.

## 6. OpenHAB Integration
**Goal:** Verify external hub connection.
1. `/openhab demo on` -> Enable simulation.
2. `/openhab items` -> List items.
3. `/openhab send Kitchen_Light ON` -> Control item.

## 7. AI & NotebookLLM
**Goal:** Verify local intelligence.
1. `/notebook add terminator_universal_cli.py`
2. `/notebook summary` -> Generates summary using local LLM.
3. `/notebook podcast` -> Generates audio script.

## 8. Coding Agent
**Goal:** Verify autonomous solving.
1. `/solve "Create a hello world python file"`
   - **Expect:** Agent plans, writes file, and reports success.

## 9. Provider Switching
**Goal:** Verify cloud integration.
1. `/provider` -> Shows current (e.g., ollama).
2. `/provider gemini` -> Switches to Gemini (requires API key).
