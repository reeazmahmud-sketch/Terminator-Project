from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Log, Sparkline, Label, Static
from textual.containers import Container, Horizontal, Vertical
from textual.binding import Binding
from textual import work
import asyncio
import psutil
import time
from datetime import datetime

# Import Core Systems
from core.agent_framework import AgentLoader
from core.terminator_agent_communication_bus import AgentCommunicationBus

class AgentStatusWidget(Static):
    """Display individual agent status."""
    def __init__(self, name, status, **kwargs):
        super().__init__(**kwargs)
        self.agent_name = name
        self.status = status
        self.update_render()

    def update_status(self, new_status):
        self.status = new_status
        self.update_render()

    def update_render(self):
        icon = "🟢" if self.status == "idle" else "🟡" if "working" in self.status else "🔴"
        self.update(f"{icon} {self.agent_name}\n   [{self.status}]")

class TerminatorTUI(App):
    """The Terminator Live Dashboard."""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 3; /* Increased for Claude section */
        grid-columns: 1fr 2fr 1fr; /* Col 3 for Claude */
        grid-rows: 60% 40%;
    }
    
    .box {
        border: solid green;
        padding: 1;
        margin: 1;
    }
    
    #agent-grid {
        row-span: 2;
        layout: grid;
        grid-size: 2;
        border-title: "Active Agents";
    }
    
    #traffic-log {
        border-title: "Neural Traffic Stream";
        background: $surface;
    }
    
    #system-stats {
        border-title: "System Vitals";
        height: 100%;
    }
    
    #claude-activity {
        border-title: "Claude Activity Report";
        background: $surface;
        row-span: 2; /* Spans full height on right */
    }
    
    AgentStatusWidget {
        border: solid gray;
        height: 3;
        padding: 0 1;
        margin: 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh_agents", "Refresh Agents"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        # Left Col: Agent Grid
        yield Container(id="agent-grid", classes="box")
        
        # Middle Top: Traffic Log
        yield Log(id="traffic-log", classes="box")
        
        # Right Col: Claude Activity (New)
        yield Log(id="claude-activity", classes="box")
        
        # Middle Bottom: System Stats
        with Container(id="system-stats", classes="box"):
            yield Label("CPU Usage")
            yield Sparkline(id="cpu-spark", summary_function=max)
            yield Label("Memory Usage")
            yield Sparkline(id="mem-spark", summary_function=max)

        yield Footer()

    def on_mount(self):
        self.bus = AgentCommunicationBus.get_instance()
        self.loader = AgentLoader(agent_dir="core", plugin_dirs=["Terminator_Agent_Pack/core_logic", "Terminator_Agent_Pack/ops", "Terminator_Agent_Pack/security"]) # Added security path
        
        self.agent_widgets = {}
        self.log_widget = self.query_one("#traffic-log", Log)
        self.claude_log_widget = self.query_one("#claude-activity", Log)
        self.claude_logger_agent = None
        
        # Start System
        self.start_system()
        
        # Start UI Updaters
        self.set_interval(1.0, self.update_metrics)
        self.set_interval(0.5, self.update_traffic)
        self.set_interval(1.0, self.update_agent_statuses)
        self.set_interval(5.0, self.update_claude_activity_report) # Update Claude report every 5 seconds

    @work(exclusive=True)
    async def start_system(self):
        self.log_widget.write_line("🚀 Initializing Terminator Core...")
        agents = await self.loader.load_and_start_agents()
        self.log_widget.write_line(f"✅ Loaded {len(agents)} Agents.")
        
        grid = self.query_one("#agent-grid")
        for name, agent in agents.items():
            widget = AgentStatusWidget(name, "init")
            self.agent_widgets[name] = widget
            grid.mount(widget)
            if name == "ClaudeActivityLogger":
                self.claude_logger_agent = agent # Store reference to the agent

    def update_metrics(self):
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        
        self.query_one("#cpu-spark", Sparkline).data = (self.query_one("#cpu-spark", Sparkline).data or [])[-40:] + [cpu]
        self.query_one("#mem-spark", Sparkline).data = (self.query_one("#mem-spark", Sparkline).data or [])[-40:] + [mem]

    def update_traffic(self):
        # Poll bus history for new messages
        # In a real event-driven UI, we'd subscribe. polling is safer for TUI main thread.
        # Ideally, Bus should have a 'get_recent_messages(since_timestamp)'
        pass 
        # For MVP, we just show that we are monitoring.
        # self.log_widget.write_line("... scanning neural bus ...")

    def update_agent_statuses(self):
        statuses = self.bus.get_all_agent_statuses()
        for name, status in statuses.items():
            if name in self.agent_widgets:
                self.agent_widgets[name].update_status(status.status)

    @work(exclusive=True)
    async def update_claude_activity_report(self):
        if self.claude_logger_agent:
            # Query the ClaudeActivityLogger for its report
            # The agent's handle_message is async, so we send a message to it
            response_message = await self.bus.send_message_async(
                sender_agent="TerminatorTUI", # TUI identifies itself as an agent
                recipient_agent="ClaudeActivityLogger",
                subject="get_session_report",
                content={},
                requires_response=True
            )
            # Retrieve the response
            # In a real app, the TUI would have its own message queue and listen for 'response_to_get_session_report'
            # For this demo, we can just query the agent directly IF it has a sync method
            
            # The ClaudeActivityLogger.get_session_report() method is currently sync.
            # We can call it directly for now.
            if hasattr(self.claude_logger_agent, 'get_session_report'):
                report_content = self.claude_logger_agent.get_session_report()
                self.claude_log_widget.clear()
                self.claude_log_widget.write(report_content)
        else:
            self.claude_log_widget.write_line("Claude Activity Logger not active.")

    async def on_quit(self):
        await self.loader.stop_all_agents()

if __name__ == "__main__":
    app = TerminatorTUI()
    app.run()
