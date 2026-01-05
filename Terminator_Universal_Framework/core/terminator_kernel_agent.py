# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

import os
import struct
import fcntl
import asyncio
from typing import Dict, Any, Optional

from core.agent_framework import BaseAgent
from core.terminator_agent_communication_bus import Message, MessageType

# Define IOCTL constants matching ai_agent_ioctl.h
# AI_IOC_MAGIC = 'k' (0x6b)
# PREDICT = 1, UPDATE = 2
# Structure: op_code(i), input_val(i), param2(i) -> 3 ints = 12 bytes
AI_IOC_MAGIC = 0x6b
AI_IOC_PREDICT = 0xc00c6b01 # _IOWR('k', 1, struct) approximation
AI_IOC_UPDATE  = 0xc00c6b02 # _IOWR('k', 2, struct) approximation

# Note: Python's ioctl encoding is complex. 
# We need to accurately calculate the IOWR value based on struct size (12 bytes).
# _IOWR(type, nr, size)
# type=0x6b, nr=1, size=12
# Direction: Read/Write = 3 (binary 11) -> shifted.
# This often varies by arch. For this PoC, we will try to use the raw numbers 
# or a helper if available. 
# Better yet, let's trust the C client for now or implement a robust struct packer.

class KernelProxyAgent(BaseAgent):
    """
    A Python wrapper acting as a proxy for the Linux Kernel Module AI Agent.
    This allows the high-level Python orchestrator to dispatch tasks to the 
    kernel for ultra-low latency processing.
    """
    AGENT_NAME = "KernelAI"
    
    def __init__(self, device_path: str = "/dev/ai_agent"):
        super().__init__(
            name=self.AGENT_NAME, 
            description="Proxy for Kernel-Space AI Agent (LKM)",
            capabilities=["low_latency_inference", "kernel_task_offload"]
        )
        self.device_path = device_path
        self.fd = None

    async def start(self):
        """Connect to the Kernel Character Device."""
        if not os.path.exists(self.device_path):
            print(f"⚠️  Kernel Agent: Device {self.device_path} not found. Is the module loaded?")
            self._status_obj.status = "offline"
            return

        try:
            self.fd = os.open(self.device_path, os.O_RDWR)
            print(f"✅ Connected to Kernel Agent at {self.device_path}")
            await super().start()
        except Exception as e:
            print(f"❌ Kernel Agent Connection Failed: {e}")
            self._status_obj.status = "error"

    async def stop(self):
        """Close connection."""
        if self.fd:
            os.close(self.fd)
        await super().stop()

    async def handle_message(self, message: Message) -> Optional[Dict[str, Any]]:
        """
        Dispatch requests to the Kernel via ioctl.
        """
        if not self.fd:
            return {"error": "Kernel device not connected"}

        cmd = message.content.get("command")
        
        if cmd == "predict":
            val = message.content.get("input", 0)
            return self._ioctl_predict(val)
        
        elif cmd == "update":
            weight = message.content.get("weight", 0)
            bias = message.content.get("bias", 0)
            return self._ioctl_update(weight, bias)

        return {"error": f"Unknown kernel command: {cmd}"}

    def _ioctl_predict(self, input_val: int) -> Dict[str, Any]:
        """Perform sync ioctl call (fast enough to be blocking)"""
        try:
            # struct ai_request { int op; int input; int param2; }
            # Pack: i i i (3 integers)
            data = struct.pack('iii', 0, input_val, 0)
            
            # Perform IOCTL (using a computed constant for x86_64 usually)
            # Linux x86_64 _IOWR('k', 1, 12) -> 0xc00c6b01
            # We use the raw number derived from C macros.
            AI_PREDICT_CMD = 0xc00c6b01 
            
            # Mutate data in place
            res_data = fcntl.ioctl(self.fd, AI_PREDICT_CMD, data)
            
            # Unpack result
            # The kernel writes result into input_val (2nd int)
            _, result, _ = struct.unpack('iii', res_data)
            
            return {"input": input_val, "prediction": result, "source": "kernel_space"}
            
        except Exception as e:
            return {"error": f"IOCTL Failed: {e}"}

    def _ioctl_update(self, weight: int, bias: int) -> Dict[str, Any]:
        """Update model weights"""
        try:
            # OpCode 1 = Update
            data = struct.pack('iii', 1, weight, bias)
            AI_UPDATE_CMD = 0xc00c6b02
            
            fcntl.ioctl(self.fd, AI_UPDATE_CMD, data)
            return {"status": "weights_updated"}
        except Exception as e:
            return {"error": f"Update Failed: {e}"}

# Factory for Loader
def create_agent():
    return KernelProxyAgent()
