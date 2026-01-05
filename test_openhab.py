import sys
import os
from pathlib import Path

sys.path.append(os.getcwd())

# Mock CLI
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

print("--- Loading OpenHAB Module ---")
# The loader scans folders in modules/scripts/
# It should find 'openhab' because it has a module.json
loader.discover_modules()
if loader.load_module("openhab"):
    print("--- Executing /openhab items (Demo Mode) ---")
    loader.loaded_modules["openhab"]["instance"].cmd_openhab(["items"])
else:
    print("❌ Failed to load OpenHAB module")
