import sys
import os
import json
from pathlib import Path

sys.path.append(os.getcwd())

# Mock CLI
class MockCLI:
    def __init__(self):
        self.commands = {}
        from rich.console import Console
        self.console = Console()
    
    def register_module_command(self, cmd, handler, name):
        self.commands[cmd] = handler

# Load
from modules.core.module_loader import ModuleLoader
cli = MockCLI()
loader = ModuleLoader(cli)
loader.load_module("smart_home")
module = loader.loaded_modules["smart_home"]["instance"]

# Helper to run cmd
def run(cmd_str):
    print(f"> /iot {cmd_str}")
    module.cmd_iot(cmd_str.split())

# Reset state
module.data = {"devices": {}, "automations": []}

print("--- 🧪 Testing IoT Logic Engine ---")

# 1. Add Devices
run("add my_btn button")
run("add my_lamp light")

# 2. Add Rule
# "if my_btn pressed then my_lamp toggle"
run("rule add if my_btn pressed then my_lamp toggle")

# 3. Check Initial State
print(f"Lamp State Before: {module.data['devices']['my_lamp']['state']}")

# 4. Press Button
run("press my_btn")

# 5. Check Result
print(f"Lamp State After:  {module.data['devices']['my_lamp']['state']}")

if module.data['devices']['my_lamp']['state'] == 'on':
    print("\n✅ SUCCESS: Logic rule worked!")
else:
    print("\n❌ FAILURE: Lamp did not turn on.")
