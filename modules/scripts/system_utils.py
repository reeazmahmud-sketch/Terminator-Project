import os
import sys
import subprocess
import platform
import json
from pathlib import Path
from modules.core.module_loader import TerminatorModule

class SystemUtilsModule(TerminatorModule):
    def on_load(self):
        self.context.log("🛠️ System Utilities Loaded (/init, /doctor)")
        self.context.register_command("init", self.cmd_init)
        self.context.register_command("doctor", self.cmd_doctor)

    def cmd_init(self, args):
        """Initialize the Terminator System and check environment."""
        self.context.log("\n[bold cyan]🚀 Initializing TERMINATOR System...[/bold cyan]\n")
        
        # 1. Check/Create Directories
        dirs = [".logs", "modules/scripts", "modules/prebuilt", "core", "logs"]
        for d in dirs:
            p = Path(d)
            if not p.exists():
                p.mkdir(parents=True)
                self.context.log(f"  [green]✓[/green] Created directory: {d}")
            else:
                self.context.log(f"  [dim]✓ Directory exists: {d}[/dim]")

        # 2. Check for LLM
        self.context.log("  [cyan]Checking for Local LLM (Ollama)...[/cyan]")
        try:
            import requests
            r = requests.get("http://localhost:11434/api/tags", timeout=2)
            if r.status_code == 200:
                self.context.log("  [green]✓ Ollama is online.[/green]")
            else:
                self.context.log("  [yellow]⚠ Ollama responded with error. Is it running?[/yellow]")
        except:
            self.context.log("  [red]✗ Ollama is offline. Run 'ollama serve' for local intelligence.[/red]")

        # 3. Create placeholder .env if missing
        env_file = Path(".env")
        if not env_file.exists():
            env_file.write_text("GOOGLE_API_KEY=\nANTHROPIC_API_KEY=\nOPENAI_API_KEY=\n")
            self.context.log("  [green]✓ Created template .env file.[/green]")

        self.context.log("\n[bold green]✅ Initialization complete![/bold green]")
        self.context.log("[dim]Run /doctor to see detailed diagnostics.[/dim]\n")

    def cmd_doctor(self, args):
        """Run system diagnostics and check health."""
        self.context.log("\n[bold cyan]🩺 TERMINATOR System Doctor[/bold cyan]\n")
        
        from rich.table import Table
        from rich.console import Console
        console = Console()
        
        table = Table(title="System Health Report")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="dim")

        # Check Python
        table.add_row("Python", "[green]OK[/green]", sys.version.split()[0])

        # Check OS
        table.add_row("OS", "[green]OK[/green]", f"{platform.system()} {platform.release()}")

        # Check Dependencies
        try:
            import psutil
            table.add_row("psutil", "[green]OK[/green]", "Installed")
        except:
            table.add_row("psutil", "[red]Missing[/red]", "Run: pip install psutil")

        try:
            import rich
            table.add_row("rich", "[green]OK[/green]", "Installed")
        except:
            table.add_row("rich", "[red]Missing[/red]", "Run: pip install rich")

        # Check Modules
        if self.context._cli.module_loader:
            mod_count = len(self.context._cli.module_loader.loaded_modules)
            table.add_row("Module Loader", "[green]OK[/green]", f"{mod_count} active modules")
        else:
            table.add_row("Module Loader", "[red]Error[/red]", "Not initialized")

        # Check File Integrity
        critical_files = ["terminator_universal_cli.py", "TERMINATOR.md", "requirements.txt"]
        for f in critical_files:
            status = "[green]✓[/green]" if Path(f).exists() else "[red]✗[/red]"
            table.add_row(f"File: {f}", status, "")

        console.print(table)
        
        # Recommendations
        self.context.log("\n[bold]Recommendations:[/bold]")
        if not Path(".env").exists():
            self.context.log("  • Create a .env file with your API keys.")
        self.context.log("  • Keep Ollama running in the background for local LLM features.")
        self.context.log("  • Check /modules list regularly for updates.")
        self.context.log("\n[dim]Doctor session complete.[/dim]\n")
