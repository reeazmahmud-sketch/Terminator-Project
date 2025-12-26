# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

import asyncio
import os
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass

# Try to import wasmtime, handle missing dependency gracefully
try:
    from wasmtime import Store, Module, Instance, Func, Engine, Linker
    WASM_AVAILABLE = True
except ImportError:
    WASM_AVAILABLE = False

from core.agent_framework import BaseAgent
from core.terminator_agent_communication_bus import Message, MessageType

class WasmAgent(BaseAgent):
    """
    A Universal Agent that runs WebAssembly (Wasm) binaries.
    This allows agents written in Rust, C++, or Go to run safely within the Terminator ecosystem.
    """
    AGENT_NAME = "WasmAgent" # Placeholder, usually set per instance
    
    def __init__(self, name: str, wasm_file_path: str, description: str = "A WebAssembly powered agent"):
        capabilities = ["wasm_execution", "high_performance", "sandboxed"]
        super().__init__(name=name, description=description, capabilities=capabilities)
        
        self.wasm_path = wasm_file_path
        self.store = None
        self.module = None
        self.instance = None
        self.engine = None
        self.linker = None
        self._is_loaded = False

    async def start(self):
        """Start the agent and load the Wasm binary."""
        if not WASM_AVAILABLE:
            print(f"⚠️  WasmAgent '{self.name}': 'wasmtime' library not found. Install via: pip install wasmtime")
            self._status_obj.status = "error"
            return

        if not os.path.exists(self.wasm_path):
            print(f"⚠️  WasmAgent '{self.name}': Binary not found at {self.wasm_path}")
            self._status_obj.status = "error"
            return

        try:
            print(f"⚙️  Initializing Wasm Runtime for '{self.name}'...")
            self.engine = Engine()
            self.store = Store(self.engine)
            self.linker = Linker(self.engine)
            
            # Allow Wasm to print to stdout (WASI)
            # In a real impl, we might capture this to logs
            # self.linker.define_wasi() 
            # self.store.set_wasi(WasiConfig())

            self.module = Module.from_file(self.engine, self.wasm_path)
            self.instance = self.linker.instantiate(self.store, self.module)
            
            self._is_loaded = True
            print(f"✅ Wasm Binary Loaded: {os.path.basename(self.wasm_path)}")
            
            # Standard BaseAgent start
            await super().start()
            
        except Exception as e:
            print(f"❌ Wasm Load Error for '{self.name}': {e}")
            self._status_obj.status = "error"

    async def handle_message(self, message: Message) -> Optional[Dict[str, Any]]:
        """
        Handle messages by calling exported functions in the Wasm module.
        Expected Message Content:
        {
            "function": "add",
            "args": [1, 2]
        }
        """
        if not self._is_loaded:
            return {"error": "Wasm module not loaded"}

        func_name = message.content.get("function")
        args = message.content.get("args", [])

        if not func_name:
            return {"error": "No 'function' specified in message content"}

        return await self._execute_wasm_function(func_name, args)

    async def _execute_wasm_function(self, func_name: str, args: List[Any]) -> Dict[str, Any]:
        """Execute a specific exported function from the Wasm module."""
        try:
            # Get the export
            exports = self.instance.exports(self.store)
            if func_name not in exports:
                return {"error": f"Function '{func_name}' not exported by Wasm module"}

            func = exports[func_name]
            
            # Wasm functions are synchronous cpu-bound, so we run them in a thread
            # to avoid blocking the asyncio loop if they take time.
            # For simple tasks, direct call is fine.
            
            # Need to handle type conversion carefully here. 
            # Wasm usually exports int32/int64/float32/float64.
            # Complex types (strings) require memory access (WASM memory model).
            # For this MVP, we support numeric args only.
            
            import time
            start_time = time.time()
            
            result = func(self.store, *args)
            
            duration = time.time() - start_time
            
            return {
                "result": result,
                "execution_time": f"{duration:.4f}s",
                "status": "success"
            }

        except Exception as e:
            return {"error": f"Wasm Execution Failed: {str(e)}"}
