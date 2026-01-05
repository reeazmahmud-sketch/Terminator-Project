import sys
import os
from pathlib import Path

sys.path.append(os.getcwd())

# Mock CLI
class MockCLI:
    def __init__(self):
        self.commands = {}
        from rich.console import Console
        self.console = Console()
        self.module_loader = None
    
    def register_module_command(self, cmd, handler, name):
        self.commands[cmd] = handler

# Load
from modules.core.module_loader import ModuleLoader
cli = MockCLI()
loader = ModuleLoader(cli)
cli.module_loader = loader

print("--- Testing System Utils Module ---")
if loader.load_module("system_utils"):
    print("\n> /doctor")
    cli.commands["/doctor"]([])
    print("\n> /init")
    cli.commands["/init"]([])
else:
    print("❌ Failed to load system_utils")
