import sys
import os
sys.path.append(os.getcwd())

# Mock CLI class
class MockCLI:
    def __init__(self):
        self.commands = {}
        self.module_commands = {}
        from rich.console import Console
        self.console = Console()
    
    def register_module_command(self, cmd, handler, name):
        print(f"✅ Registered command: {cmd} for {name}")
        self.commands[cmd] = handler

# Test Loader
from modules.core.module_loader import ModuleLoader
cli = MockCLI()
loader = ModuleLoader(cli)

print("--- Loading Smart Home Module ---")
if loader.load_module("smart_home"):
    print("--- Executing /iot list ---")
    # Simulate command execution
    loader.loaded_modules["smart_home"]["instance"].cmd_iot(["list"])
else:
    print("❌ Failed to load")
