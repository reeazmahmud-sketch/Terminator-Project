import sys
import os
import time
from modules.core.module_loader import ModuleLoader

# Mock CLI
class MockCLI:
    def __init__(self):
        self.commands = {}
        from rich.console import Console
        self.console = Console()
    def register_module_command(self, cmd, handler, name):
        self.commands[cmd] = handler

# Load Module
cli = MockCLI()
loader = ModuleLoader(cli)
loader.load_module("smart_home")
mod = loader.loaded_modules["smart_home"]["instance"]

# Helper
def run(cmd):
    print(f"\n> /iot {cmd}")
    mod.cmd_iot(cmd.split())

# Reset Data
mod.data["devices"] = {
    "lamp": {"type": "light", "state": "off"},
    "ac": {"type": "thermostat", "state": "off"},
    "thermometer": {"type": "sensor", "value": 70}
}
mod.data["scenes"] = {}
mod.data["automations"] = []

print("--- 🧪 Testing Advanced IoT Features ---")

# 1. SCENES
print("\n[Test 1: Scenes]")
# Set state
run("set lamp on")
# Capture
run("scene capture relaxing")
# Change state
run("set lamp off")
print(f"Lamp is now: {mod.data['devices']['lamp']['state']}")
# Restore
run("scene run relaxing")
print(f"Lamp restored to: {mod.data['devices']['lamp']['state']}")

# 2. SENSOR LOGIC
print("\n[Test 2: Sensor Logic]")
# Rule: If temp > 75 then ac on
run("rule add if thermometer > 75 then ac on")
# Update sensor (should trigger)
run("sensor thermometer 80")
# Check AC
print(f"AC State: {mod.data['devices']['ac']['state']}")

# 3. GHOST MODE
print("\n[Test 3: Ghost Mode]")
run("ghost on")
print("Waiting 6s for ghost action...")
time.sleep(6)
run("ghost off")
