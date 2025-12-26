#!/usr/bin/env python3

# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
TERMINATOR SDK
==============

Unified SDK for TERMINATOR ecosystem providing easy access to:
- Gemini CLI Tools (12 tools)
- MCP Creative Servers (5 servers)
- Agent Communication Bus
- Infrastructure Services

Usage:
    from core.terminator_sdk import TerminatorSDK

    sdk = TerminatorSDK()
    await sdk.initialize()

    # Use tools
    result = await sdk.tools.find_files("**/*.py")

    # Use MCP
    image = await sdk.mcp.generate_image("prompt")

    # Use agents
    await sdk.agents.send_message("agent_name", "message")

Created: December 17, 2025
Version: 1.0.0
"""

import os
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


# ============================================================================
# SDK Configuration
# ============================================================================

@dataclass
class SDKConfig:
    """SDK Configuration"""
    project_root: Path = field(default_factory=lambda: Path("/Users/reeazmahmud/Desktop/Terminator-Project"))
    google_project_id: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    ollama_host: str = "http://localhost:11434"
    enable_logging: bool = True
    enable_metrics: bool = True
    auto_connect_mcp: bool = False
    auto_start_agents: bool = False

    def __post_init__(self):
        # Load from environment if not set
        if not self.google_project_id:
            self.google_project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        if not self.anthropic_api_key:
            self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.google_api_key:
            self.google_api_key = os.environ.get("GOOGLE_API_KEY")


class SDKStatus(Enum):
    """SDK Status"""
    NOT_INITIALIZED = "not_initialized"
    INITIALIZING = "initializing"
    READY = "ready"
    ERROR = "error"


# ============================================================================
# SDK Result Types
# ============================================================================

@dataclass
class SDKResult:
    """Unified result type for SDK operations"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


# ============================================================================
# Tools Namespace
# ============================================================================

class ToolsNamespace:
    """
    Namespace for Gemini CLI Tools.
    Provides access to all 12 Gemini tools.
    """

    def __init__(self, sdk: 'TerminatorSDK'):
        self._sdk = sdk
        self._manager = None

    async def _ensure_initialized(self):
        if self._manager is None:
            from terminator_gemini_tools import get_gemini_tools
            self._manager = get_gemini_tools()

    # Codebase Investigator
    async def investigate(self, query: str, path: str = None, depth: str = "medium") -> SDKResult:
        """Investigate codebase with AI analysis"""
        await self._ensure_initialized()
        result = await self._manager.investigate_codebase(query, path, depth)
        return SDKResult(
            success=result.success,
            data=result.data,
            error=result.error,
            execution_time=result.execution_time or 0
        )

    # Edit
    async def edit(self, file_path: str, old: str, new: str, replace_all: bool = False) -> SDKResult:
        """Edit file content"""
        await self._ensure_initialized()
        result = await self._manager.edit_file(file_path, old, new, replace_all)
        return SDKResult(
            success=result.success,
            data=result.data,
            error=result.error,
            execution_time=result.execution_time or 0
        )

    # FindFiles
    async def find_files(self, pattern: str, path: str = None, limit: int = 100) -> SDKResult:
        """Find files by glob pattern"""
        await self._ensure_initialized()
        result = await self._manager.find_files(pattern, path, limit)
        return SDKResult(
            success=result.success,
            data=result.data,
            error=result.error,
            execution_time=result.execution_time or 0
        )

    # GoogleSearch
    async def search_web(self, query: str, num_results: int = 10) -> SDKResult:
        """Search the web via Google"""
        await self._ensure_initialized()
        result = await self._manager.google_search(query, num_results)
        return SDKResult(
            success=result.success,
            data=result.data,
            error=result.error,
            execution_time=result.execution_time or 0
        )

    # ReadFile
    async def read_file(self, file_path: str, offset: int = 0, limit: int = None) -> SDKResult:
        """Read file contents"""
        await self._ensure_initialized()
        result = await self._manager.read_file(file_path, offset, limit)
        return SDKResult(
            success=result.success,
            data=result.data,
            error=result.error,
            execution_time=result.execution_time or 0
        )

    # ReadFolder
    async def list_directory(self, path: str, recursive: bool = False) -> SDKResult:
        """List directory contents"""
        await self._ensure_initialized()
        result = await self._manager.read_folder(path, recursive)
        return SDKResult(
            success=result.success,
            data=result.data,
            error=result.error,
            execution_time=result.execution_time or 0
        )

    # SaveMemory
    async def save_memory(self, key: str, value: Any, context: str = None) -> SDKResult:
        """Save to persistent memory"""
        await self._ensure_initialized()
        result = await self._manager.save_memory(key, value, context)
        return SDKResult(
            success=result.success,
            data=result.data,
            error=result.error,
            execution_time=result.execution_time or 0
        )

    async def get_memory(self, key: str = None) -> Dict:
        """Get from persistent memory"""
        await self._ensure_initialized()
        return await self._manager.get_memory(key)

    # SearchText
    async def search_text(self, pattern: str, path: str = None, file_type: str = None) -> SDKResult:
        """Search for text in files"""
        await self._ensure_initialized()
        result = await self._manager.search_text(pattern, path, file_type)
        return SDKResult(
            success=result.success,
            data=result.data,
            error=result.error,
            execution_time=result.execution_time or 0
        )

    # Shell
    async def shell(self, command: str, timeout: int = 30) -> SDKResult:
        """Execute shell command"""
        await self._ensure_initialized()
        result = await self._manager.run_shell(command, timeout)
        return SDKResult(
            success=result.success,
            data=result.data,
            error=result.error,
            execution_time=result.execution_time or 0
        )

    # WebFetch
    async def fetch_url(self, url: str, timeout: int = 10) -> SDKResult:
        """Fetch web content"""
        await self._ensure_initialized()
        result = await self._manager.web_fetch(url, timeout)
        return SDKResult(
            success=result.success,
            data=result.data,
            error=result.error,
            execution_time=result.execution_time or 0
        )

    # WriteFile
    async def write_file(self, file_path: str, content: str, append: bool = False) -> SDKResult:
        """Write content to file"""
        await self._ensure_initialized()
        result = await self._manager.write_file(file_path, content, append)
        return SDKResult(
            success=result.success,
            data=result.data,
            error=result.error,
            execution_time=result.execution_time or 0
        )

    # WriteTodos
    async def write_todos(self, todos: List[Dict]) -> SDKResult:
        """Write todo list"""
        await self._ensure_initialized()
        result = await self._manager.write_todos(todos)
        return SDKResult(
            success=result.success,
            data=result.data,
            error=result.error,
            execution_time=result.execution_time or 0
        )

    async def get_todos(self) -> List[Dict]:
        """Get todo list"""
        await self._ensure_initialized()
        return await self._manager.get_todos()

    def get_available(self) -> List[Dict]:
        """Get list of available tools"""
        if self._manager:
            return self._manager.get_available_tools()
        return []


# ============================================================================
# MCP Namespace
# ============================================================================

class MCPNamespace:
    """
    Namespace for MCP Creative Servers.
    Provides access to Imagen, Veo, Chirp, Lyria, AVTool.
    """

    def __init__(self, sdk: 'TerminatorSDK'):
        self._sdk = sdk
        self._client = None

    async def _ensure_initialized(self):
        if self._client is None:
            from terminator_mcp_integration import get_mcp_client
            self._client = get_mcp_client(self._sdk.config.google_project_id)

    # Connection
    async def connect_all(self) -> Dict[str, bool]:
        """Connect to all MCP servers"""
        await self._ensure_initialized()
        return await self._client.connect_all()

    async def connect_imagen(self) -> bool:
        """Connect to Imagen server"""
        await self._ensure_initialized()
        return await self._client.connect_imagen()

    async def connect_veo(self) -> bool:
        """Connect to Veo server"""
        await self._ensure_initialized()
        return await self._client.connect_veo()

    async def connect_chirp(self) -> bool:
        """Connect to Chirp server"""
        await self._ensure_initialized()
        return await self._client.connect_chirp()

    async def connect_lyria(self) -> bool:
        """Connect to Lyria server"""
        await self._ensure_initialized()
        return await self._client.connect_lyria()

    async def connect_avtool(self) -> bool:
        """Connect to AVTool server"""
        await self._ensure_initialized()
        return await self._client.connect_avtool()

    # Imagen - Image Generation
    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        style: str = None,
        count: int = 1
    ) -> SDKResult:
        """Generate image from prompt"""
        await self._ensure_initialized()
        result = await self._client.generate_image(prompt, size, style, count)
        return SDKResult(
            success=result.success,
            data=result.data,
            error=result.error,
            execution_time=result.execution_time or 0,
            metadata={"server": "imagen"}
        )

    async def edit_image(self, image_path: str, prompt: str, mask: str = None) -> SDKResult:
        """Edit existing image"""
        await self._ensure_initialized()
        result = await self._client.edit_image(image_path, prompt, mask)
        return SDKResult(
            success=result.success,
            data=result.data,
            error=result.error,
            execution_time=result.execution_time or 0,
            metadata={"server": "imagen"}
        )

    # Veo - Video Generation
    async def generate_video(
        self,
        prompt: str,
        duration: str = "5s",
        resolution: str = "1920x1080",
        fps: int = 30
    ) -> SDKResult:
        """Generate video from prompt"""
        await self._ensure_initialized()
        result = await self._client.generate_video(prompt, duration, resolution, fps)
        return SDKResult(
            success=result.success,
            data=result.data,
            error=result.error,
            execution_time=result.execution_time or 0,
            metadata={"server": "veo"}
        )

    # Chirp - Speech Synthesis
    async def text_to_speech(
        self,
        text: str,
        voice: str = "en-US-Neural2-A",
        speed: float = 1.0,
        emotion: str = None
    ) -> SDKResult:
        """Convert text to speech"""
        await self._ensure_initialized()
        result = await self._client.text_to_speech(text, voice, speed, 0, emotion)
        return SDKResult(
            success=result.success,
            data=result.data,
            error=result.error,
            execution_time=result.execution_time or 0,
            metadata={"server": "chirp"}
        )

    async def clone_voice(self, reference_audio: str, text: str) -> SDKResult:
        """Clone voice from reference"""
        await self._ensure_initialized()
        result = await self._client.clone_voice(reference_audio, text)
        return SDKResult(
            success=result.success,
            data=result.data,
            error=result.error,
            execution_time=result.execution_time or 0,
            metadata={"server": "chirp"}
        )

    # Lyria - Music Generation
    async def generate_music(
        self,
        prompt: str,
        duration: str = "30s",
        style: str = None,
        tempo: int = None
    ) -> SDKResult:
        """Generate music from prompt"""
        await self._ensure_initialized()
        result = await self._client.generate_music(prompt, duration, style, tempo)
        return SDKResult(
            success=result.success,
            data=result.data,
            error=result.error,
            execution_time=result.execution_time or 0,
            metadata={"server": "lyria"}
        )

    # AVTool - Compositing
    async def composite(
        self,
        video_tracks: List[str] = None,
        audio_tracks: List[str] = None,
        effects: List[str] = None,
        format: str = "mp4"
    ) -> SDKResult:
        """Composite audio and video"""
        await self._ensure_initialized()
        result = await self._client.composite_media(video_tracks, audio_tracks, effects, format)
        return SDKResult(
            success=result.success,
            data=result.data,
            error=result.error,
            execution_time=result.execution_time or 0,
            metadata={"server": "avtool"}
        )

    async def convert(self, input_file: str, output_format: str, quality: str = "high") -> SDKResult:
        """Convert media format"""
        await self._ensure_initialized()
        result = await self._client.convert_format(input_file, output_format, quality)
        return SDKResult(
            success=result.success,
            data=result.data,
            error=result.error,
            execution_time=result.execution_time or 0,
            metadata={"server": "avtool"}
        )

    async def get_status(self) -> Dict:
        """Get MCP servers status"""
        await self._ensure_initialized()
        return await self._client.get_status()

    def get_available(self) -> List[Dict]:
        """Get available MCP servers"""
        if self._client:
            return self._client.get_available_servers()
        return []


# ============================================================================
# Agents Namespace
# ============================================================================

class AgentsNamespace:
    """
    Namespace for Agent Communication.
    Provides access to agent bus and messaging.
    """

    def __init__(self, sdk: 'TerminatorSDK'):
        self._sdk = sdk
        self._bus = None

    async def _ensure_initialized(self):
        if self._bus is None:
            try:
                from core.terminator_agent_communication_bus import get_communication_bus
                self._bus = get_communication_bus()
            except ImportError:
                pass

    async def register(self, agent_name: str) -> bool:
        """Register an agent with the bus"""
        await self._ensure_initialized()
        if self._bus:
            await self._bus.register_agent_async(agent_name)
            return True
        return False

    async def send_message(
        self,
        recipient: str,
        subject: str,
        content: Dict,
        sender: str = "sdk",
        priority: str = "NORMAL"
    ) -> bool:
        """Send message to an agent"""
        await self._ensure_initialized()
        if self._bus:
            await self._bus.send_message_async(
                sender_agent=sender,
                recipient_agent=recipient,
                subject=subject,
                content=content
            )
            return True
        return False

    async def broadcast(self, subject: str, content: Dict, sender: str = "sdk") -> bool:
        """Broadcast message to all agents"""
        await self._ensure_initialized()
        if self._bus:
            await self._bus.broadcast_async(
                sender_agent=sender,
                subject=subject,
                content=content
            )
            return True
        return False

    async def get_message(self, agent_name: str, timeout: float = 0.1) -> Optional[Dict]:
        """Get next message for an agent"""
        await self._ensure_initialized()
        if self._bus:
            return await self._bus.get_message_async(agent_name, timeout)
        return None

    async def list_agents(self) -> List[str]:
        """List registered agents"""
        await self._ensure_initialized()
        if self._bus:
            return list(self._bus.agents.keys())
        return []


# ============================================================================
# Infrastructure Namespace
# ============================================================================

class InfrastructureNamespace:
    """
    Namespace for Infrastructure Services.
    Provides access to health, logging, protection systems.
    """

    def __init__(self, sdk: 'TerminatorSDK'):
        self._sdk = sdk
        self._coordinator = None

    async def _ensure_initialized(self):
        if self._coordinator is None:
            try:
                from terminator_infrastructure_coordinator import get_coordinator
                self._coordinator = get_coordinator()
            except ImportError:
                pass

    async def start_infrastructure(self) -> bool:
        """Start all infrastructure agents"""
        await self._ensure_initialized()
        if self._coordinator:
            self._coordinator.start_all()
            return True
        return False

    async def stop_infrastructure(self) -> bool:
        """Stop all infrastructure agents"""
        await self._ensure_initialized()
        if self._coordinator:
            self._coordinator.stop_all()
            return True
        return False

    async def get_health_report(self) -> str:
        """Get infrastructure health report"""
        await self._ensure_initialized()
        if self._coordinator:
            return self._coordinator.get_full_report()
        return "Infrastructure not initialized"

    async def check_disk(self) -> Dict:
        """Check disk status"""
        import shutil
        disk = shutil.disk_usage("/")
        return {
            "free_gb": disk.free / (1024**3),
            "total_gb": disk.total / (1024**3),
            "used_percent": ((disk.total - disk.free) / disk.total) * 100
        }


# ============================================================================
# LLM Namespace
# ============================================================================

class LLMNamespace:
    """
    Namespace for LLM backends.
    Provides access to Ollama, Gemini, Claude.
    """

    def __init__(self, sdk: 'TerminatorSDK'):
        self._sdk = sdk

    async def chat_ollama(self, prompt: str, model: str = "llama3") -> SDKResult:
        """Chat with Ollama model"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self._sdk.config.ollama_host}/api/generate",
                    json={"model": model, "prompt": prompt, "stream": False}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return SDKResult(success=True, data={"response": data.get("response", "")})
                    else:
                        return SDKResult(success=False, error=f"HTTP {response.status}")
        except Exception as e:
            return SDKResult(success=False, error=str(e))

    async def chat_gemini(self, prompt: str, model: str = "gemini-pro") -> SDKResult:
        """Chat with Gemini model"""
        if not self._sdk.config.google_api_key:
            return SDKResult(success=False, error="GOOGLE_API_KEY not set")

        try:
            import google.generativeai as genai
            genai.configure(api_key=self._sdk.config.google_api_key)
            model_instance = genai.GenerativeModel(model)
            response = model_instance.generate_content(prompt)
            return SDKResult(success=True, data={"response": response.text})
        except Exception as e:
            return SDKResult(success=False, error=str(e))

    async def chat_claude(self, prompt: str, model: str = "claude-3-sonnet-20240229") -> SDKResult:
        """Chat with Claude model"""
        if not self._sdk.config.anthropic_api_key:
            return SDKResult(success=False, error="ANTHROPIC_API_KEY not set")

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self._sdk.config.anthropic_api_key)
            response = client.messages.create(
                model=model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return SDKResult(success=True, data={"response": response.content[0].text})
        except Exception as e:
            return SDKResult(success=False, error=str(e))

    async def auto_chat(self, prompt: str) -> SDKResult:
        """Automatically select best available LLM"""
        # Try in order: Claude > Gemini > Ollama
        if self._sdk.config.anthropic_api_key:
            return await self.chat_claude(prompt)
        elif self._sdk.config.google_api_key:
            return await self.chat_gemini(prompt)
        else:
            return await self.chat_ollama(prompt)


# ============================================================================
# Main SDK Class
# ============================================================================

class TerminatorSDK:
    """
    TERMINATOR SDK - Unified interface for the entire ecosystem.

    Usage:
        sdk = TerminatorSDK()
        await sdk.initialize()

        # Tools
        files = await sdk.tools.find_files("**/*.py")

        # MCP
        image = await sdk.mcp.generate_image("A robot")

        # Agents
        await sdk.agents.send_message("task_executor", "Run task", {})

        # Infrastructure
        health = await sdk.infrastructure.get_health_report()

        # LLM
        response = await sdk.llm.auto_chat("Hello!")
    """

    VERSION = "1.0.0"

    def __init__(self, config: SDKConfig = None):
        """Initialize SDK with configuration"""
        self.config = config or SDKConfig()
        self.status = SDKStatus.NOT_INITIALIZED

        # Namespaces
        self.tools = ToolsNamespace(self)
        self.mcp = MCPNamespace(self)
        self.agents = AgentsNamespace(self)
        self.infrastructure = InfrastructureNamespace(self)
        self.llm = LLMNamespace(self)

        # Statistics
        self._stats = {
            "initialized_at": None,
            "total_operations": 0,
            "errors": 0
        }

    async def initialize(self) -> bool:
        """Initialize the SDK and all services"""
        try:
            self.status = SDKStatus.INITIALIZING
            print(f"\n🚀 Initializing TERMINATOR SDK v{self.VERSION}...\n")

            # Initialize tools
            print("  📦 Loading Gemini Tools...")
            await self.tools._ensure_initialized()
            print("     ✅ 12 tools ready")

            # Initialize MCP (optional)
            if self.config.auto_connect_mcp:
                print("  🎨 Connecting MCP servers...")
                await self.mcp.connect_all()

            # Initialize agents (optional)
            if self.config.auto_start_agents:
                print("  🤖 Starting agents...")
                await self.agents._ensure_initialized()

            # Initialize infrastructure
            print("  🏗️  Loading infrastructure...")
            await self.infrastructure._ensure_initialized()
            print("     ✅ Infrastructure ready")

            self.status = SDKStatus.READY
            self._stats["initialized_at"] = datetime.now().isoformat()

            print(f"\n✅ TERMINATOR SDK ready!\n")
            return True

        except Exception as e:
            self.status = SDKStatus.ERROR
            print(f"\n❌ SDK initialization failed: {e}\n")
            return False

    def get_status(self) -> Dict:
        """Get SDK status"""
        return {
            "version": self.VERSION,
            "status": self.status.value,
            "config": {
                "project_root": str(self.config.project_root),
                "google_project": self.config.google_project_id,
                "ollama_host": self.config.ollama_host,
                "has_anthropic_key": bool(self.config.anthropic_api_key),
                "has_google_key": bool(self.config.google_api_key)
            },
            "stats": self._stats
        }

    def get_available_services(self) -> Dict:
        """Get all available services"""
        return {
            "tools": {
                "count": 12,
                "items": [
                    "investigate", "edit", "find_files", "search_web",
                    "read_file", "list_directory", "save_memory", "search_text",
                    "shell", "fetch_url", "write_file", "write_todos"
                ]
            },
            "mcp": {
                "count": 5,
                "items": ["imagen", "veo", "chirp", "lyria", "avtool"]
            },
            "llm": {
                "count": 3,
                "items": ["ollama", "gemini", "claude"]
            },
            "infrastructure": {
                "count": 6,
                "items": [
                    "activity_logger", "file_guardian", "change_propagation",
                    "knowledge_base", "loop_guardian", "self_healing"
                ]
            }
        }


# ============================================================================
# Module Interface
# ============================================================================

_sdk_instance = None

def get_sdk(config: SDKConfig = None) -> TerminatorSDK:
    """Get SDK singleton instance"""
    global _sdk_instance
    if _sdk_instance is None:
        _sdk_instance = TerminatorSDK(config)
    return _sdk_instance


async def quick_start() -> TerminatorSDK:
    """Quick start SDK with defaults"""
    sdk = get_sdk()
    await sdk.initialize()
    return sdk


# ============================================================================
# CLI Interface
# ============================================================================

def print_sdk_info():
    """Print SDK information"""
    print(f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                        TERMINATOR SDK v1.0.0                             ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  📦 TOOLS (12)                    🎨 MCP SERVERS (5)                    ║
║  ─────────────                    ──────────────────                     ║
║  • investigate                    • Imagen (9000) - Images              ║
║  • edit                           • Veo (9001) - Video                  ║
║  • find_files                     • Chirp (9002) - Speech               ║
║  • search_web                     • Lyria (9003) - Music                ║
║  • read_file                      • AVTool (9004) - Compositing         ║
║  • list_directory                                                        ║
║  • save_memory                    🤖 LLM BACKENDS (3)                   ║
║  • search_text                    ─────────────────                      ║
║  • shell                          • Ollama (local)                       ║
║  • fetch_url                      • Gemini (cloud)                       ║
║  • write_file                     • Claude (cloud)                       ║
║  • write_todos                                                           ║
║                                                                          ║
║  🏗️  INFRASTRUCTURE (6)                                                  ║
║  ───────────────────                                                     ║
║  • Activity Logger  • File Guardian  • Change Propagation               ║
║  • Knowledge Base   • Loop Guardian  • Self-Healing                     ║
║                                                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  Usage:                                                                  ║
║    from core.terminator_sdk import TerminatorSDK                        ║
║                                                                          ║
║    sdk = TerminatorSDK()                                                ║
║    await sdk.initialize()                                               ║
║                                                                          ║
║    # Use tools                                                          ║
║    result = await sdk.tools.find_files("**/*.py")                       ║
║                                                                          ║
║    # Use MCP                                                            ║
║    image = await sdk.mcp.generate_image("prompt")                       ║
║                                                                          ║
║    # Use LLM                                                            ║
║    response = await sdk.llm.auto_chat("Hello!")                         ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
""")


# ============================================================================
# Testing
# ============================================================================

if __name__ == "__main__":
    async def test_sdk():
        """Test SDK functionality"""
        print_sdk_info()

        print("\n🔧 Testing TERMINATOR SDK\n")

        sdk = get_sdk()
        await sdk.initialize()

        # Test tools
        print("\n1. Testing Tools...")
        result = await sdk.tools.find_files("*.py", limit=5)
        print(f"   Found {len(result.data['matches']) if result.data else 0} Python files")

        # Test disk check
        print("\n2. Testing Infrastructure...")
        disk = await sdk.infrastructure.check_disk()
        print(f"   Disk: {disk['used_percent']:.1f}% used, {disk['free_gb']:.1f}GB free")

        # Show status
        print("\n3. SDK Status:")
        status = sdk.get_status()
        print(f"   Version: {status['version']}")
        print(f"   Status: {status['status']}")

        # Show services
        print("\n4. Available Services:")
        services = sdk.get_available_services()
        print(f"   Tools: {services['tools']['count']}")
        print(f"   MCP Servers: {services['mcp']['count']}")
        print(f"   LLM Backends: {services['llm']['count']}")
        print(f"   Infrastructure: {services['infrastructure']['count']}")

        print("\n✅ SDK test completed!")

    asyncio.run(test_sdk())
