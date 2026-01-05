import os
import sys
import json
import importlib.util
import threading
import time
from pathlib import Path
from typing import Dict, Any, Callable, List, Optional

# Try to import watchdog for hot-reloading
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False

class ModuleContext:
    """Interface exposed to modules for interacting with the system"""
    def __init__(self, cli_instance, module_name: str):
        self._cli = cli_instance
        self._name = module_name
        self.bus = None # To be connected to the agent bus

    def register_command(self, command: str, handler: Callable):
        """Register a CLI command (e.g., /mycmd)"""
        full_cmd = f"/{command.lstrip('/')}"
        self._cli.register_module_command(full_cmd, handler, self._name)

    def register_event_handler(self, event_name: str, handler: Callable):
        """Subscribe to system events"""
        # Placeholder for bus integration
        if self.bus:
            # self.bus.subscribe(event_name, handler)
            pass
        print(f"[{self._name}] Registered handler for '{event_name}'")

    def log(self, message: str, level: str = "info"):
        """Log a message via the CLI console"""
        if hasattr(self._cli, "console"):
            color = "cyan" if level == "info" else "red" if level == "error" else "yellow"
            self._cli.console.print(f"[{color}][{self._name}] {message}[/{color}]")
        else:
            print(f"[{self._name}] {message}")

class TerminatorModule:
    """Base class for all Terminator modules"""
    def __init__(self, context: ModuleContext):
        self.context = context
        self.metadata = {}

    def on_load(self):
        """Called when module is loaded"""
        pass

    def on_unload(self):
        """Called when module is unloaded"""
        pass

    def on_enable(self):
        """Called when module is enabled"""
        pass

    def on_disable(self):
        """Called when module is disabled"""
        pass

class ModuleLoader:
    def __init__(self, cli_instance, modules_dir: str = "modules"):
        self.cli = cli_instance
        self.root_dir = Path(modules_dir)
        self.scripts_dir = self.root_dir / "scripts"
        self.prebuilt_dir = self.root_dir / "prebuilt"
        
        # Registry: name -> {instance: TerminatorModule, path: Path, commands: []}
        self.loaded_modules: Dict[str, Any] = {}
        
        # Hot reload observer
        self.observer = None
        if HAS_WATCHDOG:
            self.setup_file_watcher()

    def discover_modules(self) -> List[Dict]:
        """Scan directories for module.json or .py files"""
        found = []
        for d in [self.scripts_dir, self.prebuilt_dir]:
            if not d.exists(): continue
            
            # 1. Folder-based modules (must have module.json)
            for item in d.iterdir():
                if item.is_dir() and (item / "module.json").exists():
                    try:
                        meta = json.loads((item / "module.json").read_text())
                        found.append({
                            "name": meta.get("name", item.name),
                            "type": "folder",
                            "path": item,
                            "metadata": meta
                        })
                    except Exception as e:
                        print(f"Error reading module.json in {item}: {e}")

            # 2. Single script modules (.py)
            for item in d.glob("*.py"):
                if item.name.startswith("_"): continue
                found.append({
                    "name": item.stem,
                    "type": "script",
                    "path": item,
                    "metadata": {"version": "1.0", "author": "User"}
                })
        return found

    def load_module(self, module_name: str) -> bool:
        """Load a specific module by name"""
        discovery = self.discover_modules()
        target = next((m for m in discovery if m["name"] == module_name), None)
        
        if not target:
            return False

        try:
            # Unload if exists
            if module_name in self.loaded_modules:
                self.unload_module(module_name)

            path = target["path"]
            spec = None
            
            if target["type"] == "folder":
                entry_point = target["metadata"].get("entry", "main.py")
                script_path = path / entry_point
                spec = importlib.util.spec_from_file_location(module_name, script_path)
            else:
                spec = importlib.util.spec_from_file_location(module_name, path)

            if not spec or not spec.loader:
                raise ImportError(f"Could not load spec for {path}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Instantiate the main class
            # Look for a class inheriting from TerminatorModule
            module_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                try:
                    if issubclass(attr, TerminatorModule) and attr is not TerminatorModule:
                        module_class = attr
                        break
                except TypeError:
                    continue

            if not module_class:
                # Fallback: look for simple 'setup(context)' function
                if hasattr(module, "setup"):
                    ctx = ModuleContext(self.cli, module_name)
                    module.setup(ctx)
                    self.loaded_modules[module_name] = {
                        "instance": None, 
                        "type": "functional",
                        "path": path,
                        "commands": [] # Populated by register_module_command callback
                    }
                    return True
                raise ImportError(f"No TerminatorModule subclass or setup() found in {module_name}")

            # Instantiate
            ctx = ModuleContext(self.cli, module_name)
            instance = module_class(ctx)
            instance.metadata = target["metadata"]
            instance.on_load()
            instance.on_enable()

            self.loaded_modules[module_name] = {
                "instance": instance,
                "type": "class",
                "path": path,
                "commands": []
            }
            return True

        except Exception as e:
            if hasattr(self.cli, "console"):
                self.cli.console.print(f"[red]Failed to load module {module_name}: {e}[/red]")
            else:
                print(f"Failed to load module {module_name}: {e}")
            return False

    def unload_module(self, module_name: str):
        """Unload a module and cleanup commands"""
        if module_name not in self.loaded_modules:
            return

        mod_data = self.loaded_modules[module_name]
        instance = mod_data.get("instance")
        
        # 1. Call lifecycle hook
        if instance:
            try:
                instance.on_disable()
                instance.on_unload()
            except Exception as e:
                print(f"Error unloading {module_name}: {e}")

        # 2. Unregister commands
        for cmd in mod_data.get("commands", []):
            self.cli.unregister_module_command(cmd)

        del self.loaded_modules[module_name]
        
        # Remove from sys.modules to ensure fresh reload
        if module_name in sys.modules:
            del sys.modules[module_name]

    def reload_all(self):
        """Reload all currently loaded modules"""
        current_names = list(self.loaded_modules.keys())
        for name in current_names:
            self.load_module(name)

    # --- Hot Reloading ---
    def setup_file_watcher(self):
        class ModuleHandler(FileSystemEventHandler):
            def __init__(self, loader):
                self.loader = loader
            
            def on_modified(self, event):
                if event.is_directory: return
                if not event.src_path.endswith(".py"): return
                
                # Determine which module this file belongs to
                path = Path(event.src_path)
                for name, data in self.loader.loaded_modules.items():
                    mod_path = data["path"]
                    # Check if file is the script itself or inside the module folder
                    if mod_path == path or (mod_path.is_dir() and mod_path in path.parents):
                        print(f"[HotReload] Change detected in {name}. Reloading...")
                        self.loader.cli.console.print(f"[yellow]⚡ Reloading module: {name}[/yellow]")
                        # Add slight delay to ensure write is complete
                        threading.Timer(0.5, self.loader.load_module, args=[name]).start()
                        return

        self.observer = Observer()
        if self.scripts_dir.exists():
            self.observer.schedule(ModuleHandler(self), str(self.scripts_dir), recursive=True)
        self.observer.start()

    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
