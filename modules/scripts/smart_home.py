import json
import time
import threading
import random
from pathlib import Path
from modules.core.module_loader import TerminatorModule

class SmartHomeModule(TerminatorModule):
    def on_load(self):
        self.context.log("🏠 Smart Home Module Loaded (Enhanced)")
        self.context.register_command("iot", self.cmd_iot)
        
        self.state_file = Path("modules/scripts/smart_home_state.json")
        self.data = self.load_state()
        
        # Ghost Mode Control
        self.ghost_active = False
        self.stop_ghost = threading.Event()

    def on_unload(self):
        self.stop_ghost.set()

    def load_state(self):
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text())
                # Ensure structure
                for key in ["devices", "automations", "scenes"]:
                    if key not in data: data[key] = {} if key != "automations" else []
                return data
            except:
                pass
        return {
            "devices": {
                "living_room_light": {"type": "light", "state": "off", "brightness": 100},
                "porch_light": {"type": "light", "state": "off"},
                "temp_sensor": {"type": "sensor", "value": 70}, # Simulated sensor
                "ac_unit": {"type": "thermostat", "state": "off"}
            },
            "automations": [
                # {"trigger": "temp_sensor", "condition": ">", "threshold": 75, "action": "ac_unit", "value": "on"}
            ],
            "scenes": {
                "movie_night": {
                    "living_room_light": {"state": "on", "brightness": 20, "color": "blue"},
                    "porch_light": {"state": "off"}
                }
            }
        }

    def save_state(self):
        self.state_file.write_text(json.dumps(self.data, indent=2))

    def cmd_iot(self, args):
        """
        Advanced IoT Controller.
        Usage: /iot <cmd> [args]
        """
        if not args:
            self.print_help()
            return

        subcmd = args[0].lower()
        devices = self.data["devices"]

        # --- EXISTING COMMANDS ---
        if subcmd in ["list", "add", "remove", "set", "press"]:
            self.handle_basic_commands(subcmd, args)
        
        # --- NEW: SCENES ---
        elif subcmd == "scene":
            self.handle_scenes(args)

        # --- NEW: GHOST MODE ---
        elif subcmd == "ghost":
            if len(args) < 2:
                self.context.log(f"Ghost Mode is: {'ON' if self.ghost_active else 'OFF'}")
                return
            
            if args[1] == "on":
                if not self.ghost_active:
                    self.ghost_active = True
                    self.stop_ghost.clear()
                    threading.Thread(target=self.ghost_loop, daemon=True).start()
                    self.context.log("[cyan]👻 Ghost Mode ACTIVATED. Simulating presence...[/cyan]")
            else:
                self.ghost_active = False
                self.stop_ghost.set()
                self.context.log("[cyan]👻 Ghost Mode DEACTIVATED.[/cyan]")

        # --- NEW: SENSOR SIMULATION ---
        elif subcmd == "sensor":
            # /iot sensor temp_sensor 80
            if len(args) < 3: return
            s_id = args[1]
            val = args[2]
            
            if s_id in devices and devices[s_id]["type"] == "sensor":
                devices[s_id]["value"] = float(val)
                self.context.log(f"[blue]📡 Sensor '{s_id}' reported: {val}[/blue]")
                self.save_state()
                self.check_sensor_automations(s_id, float(val))
            else:
                self.context.log(f"[red]❌ '{s_id}' is not a sensor[/red]")
        
        # --- NEW: AUTOMATION LOGIC (Updated for sensors) ---
        elif subcmd == "rule":
            self.handle_rules(args)

        else:
            self.print_help()

    def handle_basic_commands(self, subcmd, args):
        devices = self.data["devices"]
        
        if subcmd == "list":
            self.list_all()

        elif subcmd == "set":
            if len(args) < 3: return
            self.control_device(args[1], args[2], " ".join(args[3:]) if len(args) > 3 else None)
        
        elif subcmd == "add" and len(args) >= 3:
            d_id, d_type = args[1], args[2]
            defaults = {"type": d_type, "state": "off"}
            if d_type == "sensor": defaults = {"type": "sensor", "value": 0}
            devices[d_id] = defaults
            self.save_state()
            self.context.log(f"[green]✅ Added {d_id}[/green]")

    def handle_scenes(self, args):
        # /iot scene create night_mode
        # /iot scene capture night_mode (Saves current state of all devs to scene)
        # /iot scene run night_mode
        if len(args) < 2: return
        action = args[1]
        scenes = self.data["scenes"]

        if action == "run" and len(args) >= 3:
            s_name = args[2]
            if s_name in scenes:
                self.context.log(f"[magenta]🎬 Activating Scene: {s_name}[/magenta]")
                for d_id, state in scenes[s_name].items():
                    # Apply state
                    if d_id in self.data["devices"]:
                        for k, v in state.items():
                            self.control_device(d_id, k, v, verbose=False)
            else:
                self.context.log(f"[red]Scene '{s_name}' not found[/red]")

        elif action == "capture" and len(args) >= 3:
            s_name = args[2]
            # Snapshots current state of ALL lights/locks
            snapshot = {}
            for d_id, d_data in self.data["devices"].items():
                if d_data["type"] in ["light", "lock", "thermostat"]:
                    snapshot[d_id] = d_data.copy()
                    del snapshot[d_id]["type"] # Don't store type
            scenes[s_name] = snapshot
            self.save_state()
            self.context.log(f"[green]✅ Scene '{s_name}' captured from current state[/green]")

    def handle_rules(self, args):
        # /iot rule add if temp_sensor > 75 then ac_unit on
        if len(args) < 8:
            self.context.log("Usage: /iot rule add if <id> <cond> <val> then <id> <action>")
            return
        
        # 0    1   2  3            4      5     6    7       8
        # rule add if temp_sensor  >      75    then ac_unit on
        rule = {
            "trigger": args[3],
            "condition": args[4], # >, <, =, pressed
            "threshold": args[5],
            "action": args[7],
            "value": args[8]
        }
        self.data["automations"].append(rule)
        self.save_state()
        self.context.log("[green]✅ Sensor Rule Added[/green]")

    def check_sensor_automations(self, s_id, val):
        for rule in self.data["automations"]:
            if rule["trigger"] == s_id:
                cond = rule["condition"]
                thresh = float(rule["threshold"])
                match = False
                
                if cond == ">" and val > thresh: match = True
                elif cond == "<" and val < thresh: match = True
                elif cond == "=" and val == thresh: match = True
                
                if match:
                    self.context.log(f"[yellow]⚡ Sensor Trigger:[/yellow] {s_id} {cond} {thresh} -> {rule['action']} {rule['value']}")
                    self.control_device(rule["action"], rule["value"])

    def control_device(self, d_id, param, value=None, verbose=True):
        if d_id not in self.data["devices"]: return
        dev = self.data["devices"][d_id]
        
        # Simple update logic
        if param == "on": dev["state"] = "on"
        elif param == "off": dev["state"] = "off"
        elif value: dev[param] = value
        else: dev[param] = value # generic set

        self.save_state()
        if verbose:
            self.context.log(f"💡 {d_id} updated: {param}={value if value else 'set'}")

    def ghost_loop(self):
        """Randomly toggles lights to simulate presence"""
        while not self.stop_ghost.is_set():
            delay = random.randint(5, 15) # Fast for demo, normally mins
            time.sleep(delay)
            if self.stop_ghost.is_set(): break
            
            # Find a light
            lights = [d for d, v in self.data["devices"].items() if v["type"] == "light"]
            if lights:
                target = random.choice(lights)
                action = random.choice(["on", "off"])
                self.context.log(f"[dim]👻 Ghost Mode: Turning {target} {action}[/dim]")
                self.control_device(target, action)

    def list_all(self):
        from rich.console import Console
        from rich.table import Table
        console = Console()
        
        # Devices Table
        table = Table(title="Devices")
        table.add_column("ID", style="cyan")
        table.add_column("State", style="green")
        for k, v in self.data["devices"].items():
            state = v.get("state", str(v.get("value", "")))
            table.add_row(k, state)
        console.print(table)
        
        # Scenes Table
        if self.data["scenes"]:
            stable = Table(title="Scenes", show_header=False)
            for k in self.data["scenes"]:
                stable.add_row(f"🎬 {k}")
            console.print(stable)

    def print_help(self):
        self.context.log("\n[bold]Enhanced IoT Commands:[/bold]")
        self.context.log("  /iot list")
        self.context.log("  /iot scene capture <name>   - Save current state as scene")
        self.context.log("  /iot scene run <name>       - Activate scene")
        self.context.log("  /iot ghost on/off           - Simulate presence")
        self.context.log("  /iot sensor <id> <val>      - Update sensor reading")
        self.context.log("  /iot rule add if <id> > <val> then <id> <action>")
