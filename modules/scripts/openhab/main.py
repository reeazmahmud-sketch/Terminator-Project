import json
import os
import requests
from pathlib import Path
from modules.core.module_loader import TerminatorModule

class OpenHABModule(TerminatorModule):
    def on_load(self):
        self.context.log("🏠 OpenHAB Integration Loaded")
        self.context.register_command("openhab", self.cmd_openhab)
        
        # specific config file for this module
        self.config_file = Path(__file__).parent / "config.json"
        self.config = self.load_config()

    def load_config(self):
        if self.config_file.exists():
            try:
                return json.loads(self.config_file.read_text())
            except:
                pass
        return {
            "url": "http://localhost:8080",
            "token": "",
            "demo_mode": True 
        }

    def save_config(self):
        self.config_file.write_text(json.dumps(self.config, indent=2))

    def get_headers(self):
        headers = {"Content-Type": "text/plain", "Accept": "application/json"}
        if self.config.get("token"):
            headers["Authorization"] = f"Bearer {self.config['token']}"
        return headers

    def cmd_openhab(self, args):
        """
        Interact with OpenHAB.
        Usage:
          /openhab config <url> [token]  - Configure connection
          /openhab status                - Check connection
          /openhab items [filter]        - List items
          /openhab get <item>            - Get item state
          /openhab send <item> <cmd>     - Send command (ON, OFF, 50, etc.)
          /openhab demo <on/off>         - Toggle simulation mode
        """
        if not args:
            self.print_help()
            return

        subcmd = args[0].lower()

        if subcmd == "config":
            if len(args) < 2:
                self.context.log("[red]Usage: /openhab config <url> [token][/red]")
                return
            
            self.config["url"] = args[1].rstrip("/")
            if len(args) > 2:
                self.config["token"] = args[2]
            
            self.config["demo_mode"] = False
            self.save_config()
            self.context.log(f"[green]✅ Configuration saved. URL: {self.config['url']}[/green]")
            self.check_connection()

        elif subcmd == "demo":
            if len(args) < 2:
                self.context.log(f"Demo mode is: {self.config.get('demo_mode')}")
                return
            state = args[1].lower() == "on"
            self.config["demo_mode"] = state
            self.save_config()
            self.context.log(f"[yellow]Simulation Mode: {'ON' if state else 'OFF'}[/yellow]")

        elif subcmd == "status":
            self.check_connection()

        elif subcmd == "items":
            self.list_items(filter_str=args[1] if len(args) > 1 else None)

        elif subcmd == "get":
            if len(args) < 2:
                self.context.log("[red]Usage: /openhab get <item_name>[/red]")
                return
            self.get_item(args[1])

        elif subcmd == "send":
            if len(args) < 3:
                self.context.log("[red]Usage: /openhab send <item_name> <command>[/red]")
                return
            self.send_command(args[1], " ".join(args[2:]))

        else:
            self.print_help()

    def check_connection(self):
        if self.config.get("demo_mode"):
            self.context.log("[yellow]⚠ Running in DEMO MODE (Simulated)[/yellow]")
            return True

        url = f"{self.config['url']}/rest/"
        try:
            r = requests.get(url, headers=self.get_headers(), timeout=2)
            if r.status_code == 200:
                self.context.log(f"[green]✅ Connected to OpenHAB at {self.config['url']}[/green]")
                return True
            else:
                self.context.log(f"[red]❌ Connection failed: HTTP {r.status_code}[/red]")
        except Exception as e:
            self.context.log(f"[red]❌ Connection error: {e}[/red]")
        return False

    def list_items(self, filter_str=None):
        if self.config.get("demo_mode"):
            # Mock Data
            items = [
                {"name": "Kitchen_Light", "label": "Kitchen Ceiling", "type": "Switch", "state": "OFF"},
                {"name": "LivingRoom_Temp", "label": "Living Room Thermostat", "type": "Number:Temperature", "state": "21.5 °C"},
                {"name": "Garage_Door", "label": "Main Garage", "type": "Contact", "state": "CLOSED"},
                {"name": "Garden_Sprinkler", "label": "Backyard Water", "type": "Switch", "state": "ON"}
            ]
        else:
            url = f"{self.config['url']}/rest/items?recursive=false"
            try:
                r = requests.get(url, headers=self.get_headers(), timeout=5)
                if r.status_code != 200:
                    self.context.log(f"[red]Error: HTTP {r.status_code}[/red]")
                    return
                items = r.json()
            except Exception as e:
                self.context.log(f"[red]Error fetching items: {e}[/red]")
                return

        # Display
        from rich.table import Table
        from rich.console import Console
        console = Console()
        
        table = Table(title="🏠 OpenHAB Items")
        table.add_column("Name", style="cyan")
        table.add_column("Label", style="yellow")
        table.add_column("Type", style="dim")
        table.add_column("State", style="green")

        count = 0
        for item in items:
            name = item.get("name", "Unknown")
            if filter_str and filter_str.lower() not in name.lower():
                continue
            
            table.add_row(
                name,
                item.get("label", "-"),
                item.get("type", "-"),
                str(item.get("state", "NULL"))
            )
            count += 1
        
        console.print(table)
        self.context.log(f"[dim]Showing {count} items[/dim]")

    def get_item(self, item_name):
        if self.config.get("demo_mode"):
            self.context.log(f"[cyan]{item_name}[/cyan] state is [green]SIMULATED_ON[/green]")
            return

        url = f"{self.config['url']}/rest/items/{item_name}"
        try:
            r = requests.get(url, headers=self.get_headers(), timeout=2)
            if r.status_code == 200:
                data = r.json()
                self.context.log(f"Item: [bold]{data.get('label')}[/bold] ({data.get('name')})")
                self.context.log(f"State: [green]{data.get('state')}[/green]")
            else:
                self.context.log(f"[red]Item not found or error: {r.status_code}[/red]")
        except Exception as e:
            self.context.log(f"[red]Error: {e}[/red]")

    def send_command(self, item_name, command):
        self.context.log(f"Sending [bold]{command}[/bold] to [cyan]{item_name}[/cyan]...")
        
        if self.config.get("demo_mode"):
            self.context.log("[green]✅ Command sent (Simulated)[/green]")
            return

        url = f"{self.config['url']}/rest/items/{item_name}"
        try:
            r = requests.post(url, data=str(command), headers=self.get_headers(), timeout=2)
            if r.status_code in [200, 202]:
                self.context.log("[green]✅ Command sent successfully[/green]")
            else:
                self.context.log(f"[red]Failed to send command: HTTP {r.status_code}[/red]")
        except Exception as e:
            self.context.log(f"[red]Error sending command: {e}[/red]")

    def print_help(self):
        self.context.log("\n[bold]OpenHAB Commands:[/bold]")
        self.context.log("  /openhab config <url> [token]  - Connect to server")
        self.context.log("  /openhab items [filter]        - List available items")
        self.context.log("  /openhab send <item> <cmd>     - Control an item")
        self.context.log("  /openhab demo on/off           - Toggle simulation")
