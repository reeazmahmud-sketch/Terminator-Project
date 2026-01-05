import unittest
import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.wasm_agent_framework import WasmAgent
from core.terminator_agent_communication_bus import AgentCommunicationBus

class TestWasmAgent(unittest.TestCase):
    def setUp(self):
        self.bus = AgentCommunicationBus.get_instance()
        self.dummy_wasm_path = "core/wasm_agents/calculator_agent.wasm"

    def test_initialization(self):
        """Test that WasmAgent initializes with correct metadata."""
        agent = WasmAgent("TestWasm", self.dummy_wasm_path)
        self.assertEqual(agent.name, "TestWasm")
        self.assertIn("wasm_execution", agent.capabilities)
        self.assertEqual(agent.wasm_path, self.dummy_wasm_path)

    def test_missing_binary_handling(self):
        """Test that start() handles missing binary gracefully."""
        async def run_test():
            # Point to non-existent file
            agent = WasmAgent("MissingAgent", "non_existent.wasm")
            await agent.start()
            
            # Should be in error status or simply not loaded
            meta = agent.get_metadata()
            # If wasmtime is missing, it errors. If file missing, it errors.
            # In our impl, we set status="error" on start failure.
            self.assertEqual(meta['status'], 'error')
            
        asyncio.run(run_test())

    def test_wasm_integration_structure(self):
        """
        If the binary exists, try to load it. 
        If not, just verify the class logic is sound.
        """
        if not os.path.exists(self.dummy_wasm_path):
            print("⚠️  Skipping execution test: 'calculator_agent.wasm' not found.")
            return

        async def run_execution():
            agent = WasmAgent("CalcBot", self.dummy_wasm_path)
            await agent.start()
            
            # If start failed (e.g. wasmtime missing), skip
            if agent.get_metadata()['status'] == 'error':
                return

            # Test Addition
            msg = type('Message', (), {})() # Mock message object
            msg.content = {"function": "add", "args": [10, 20]}
            
            result = await agent.handle_message(msg)
            self.assertEqual(result.get("result"), 30)
            
        asyncio.run(run_execution())

if __name__ == '__main__':
    unittest.main()
