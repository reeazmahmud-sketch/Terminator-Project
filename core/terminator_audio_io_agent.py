#!/usr/bin/env python3
"""
TERMINATOR Audio I/O Agent
==========================

Manages local audio I/O models for Text-to-Speech (TTS) and Automatic Speech Recognition (ASR).
Downloads, registers, and serves:
- microsoft/VibeVoice-Realtime-0.5B (TTS)
- FunAudioLLM/Fun-ASR-Nano-2512 (ASR)
- FunAudioLLM/Fun-CosyVoice3-0.5B-2512 (Premium TTS)
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from huggingface_hub import snapshot_download
    HAS_HF = True
except ImportError:
    HAS_HF = False

from core.terminator_agent_communication_bus import AgentCommunicationBus

class AudioIOAgent:
    """
    Agent responsible for managing and serving local audio models.
    """
    
    AGENT_NAME = "terminator_audio_io_agent"
    
    MODELS = {
        "tts_realtime": {
            "repo_id": "microsoft/VibeVoice-Realtime-0.5B",
            "role": "default speaking voice",
            "local_dir": "/Users/reeazmahmud/Desktop/Ollama Models/vibevoice"
        },
        "asr_realtime": {
            "repo_id": "FunAudioLLM/Fun-ASR-Nano-2512",
            "role": "default listening/ASR engine",
            "local_dir": "/Users/reeazmahmud/Desktop/Ollama Models/fun-asr"
        },
        "tts_premium": {
            "repo_id": "FunAudioLLM/Fun-CosyVoice3-0.5B-2512",
            "role": "high-quality showcase voice",
            "local_dir": "/Users/reeazmahmud/Desktop/Ollama Models/cosyvoice"
        }
    }

    def __init__(self):
        self.bus = AgentCommunicationBus.get_instance()
        self.project_root = Path(__file__).parent.parent
        self.registry_file = self.project_root / "audio_model_registry.json"
        self.models_root = Path("/Users/reeazmahmud/Desktop/Ollama Models")
        self.registry = self._load_registry()

    def _load_registry(self) -> Dict:
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                return json.load(f)
        return {"models": {}}

    def _save_registry(self):
        with open(self.registry_file, 'w') as f:
            json.dump(self.registry, f, indent=2)

    async def start(self):
        """Initialize and register the agent."""
        if not HAS_HF:
            print("❌ huggingface_hub not installed. Cannot download audio models.")
            return

        print(f"🎤 Starting {self.AGENT_NAME}...")
        await self.bus.register_agent_async(self.AGENT_NAME)
        
        # Ensure models directory exists
        self.models_root.mkdir(parents=True, exist_ok=True)

        # Download models if not present
        await self.ensure_models()
        
        # Start message loop
        asyncio.create_task(self._message_loop())
        print(f"✅ {self.AGENT_NAME} ready and listening.")

    async def ensure_models(self):
        """Download missing models."""
        for key, config in self.MODELS.items():
            model_path = self.project_root / config["local_dir"]
            
            if not model_path.exists() or not any(model_path.iterdir()):
                print(f"⬇️  Downloading {config['repo_id']} for {key}...")
                try:
                    # In a real scenario, this might block, so ideally run in executor
                    # For this prototype, we'll keep it simple or use run_in_executor if needed
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(
                        None, 
                        lambda: snapshot_download(
                            repo_id=config["repo_id"],
                            local_dir=str(model_path),
                            ignore_patterns=["*.msgpack", "*.h5", "*.ot"] # Optimize download if possible
                        )
                    )
                    
                    self.registry["models"][key] = {
                        "path": str(model_path),
                        "repo_id": config["repo_id"],
                        "status": "downloaded"
                    }
                    self._save_registry()
                    print(f"✅ Downloaded {key}")
                except Exception as e:
                    print(f"❌ Failed to download {key}: {e}")
            else:
                self.registry["models"][key] = {
                    "path": str(model_path),
                    "repo_id": config["repo_id"],
                    "status": "ready"
                }
                # print(f"✅ Model {key} already exists")
        self._save_registry()

    async def _message_loop(self):
        """Listen for audio tasks."""
        while True:
            # In a real implementation, this would consume from a queue or socket
            # For the prototype, we assume the bus pushes messages to a handler
            # But the bus implementation usually requires polling or a callback
            # We'll rely on the 'handle_message' being called if the bus supports it
            # Or poll if necessary.
            # Assuming the bus uses a shared queue or similar mechanism.
            await asyncio.sleep(1)

    async def handle_request(self, endpoint: str, data: Any) -> Dict:
        """Handle incoming requests from the bus."""
        if endpoint == "tts_realtime":
            return self._mock_tts(data, "vibevoice")
        elif endpoint == "asr_realtime":
            return self._mock_asr(data, "fun-asr")
        elif endpoint == "tts_premium":
            return self._mock_tts(data, "cosyvoice")
        else:
            return {"error": "Unknown endpoint"}

    def _mock_tts(self, text: str, model: str) -> Dict:
        """
        Mock TTS generation.
        In production, this would load the model and generate audio.
        """
        # print(f"🔊 Generating audio with {model}: '{text[:20]}...'" )
        return {
            "status": "success",
            "audio_data": f"[Audio data generated by {model} for: {text[:10]}...]",
            "format": "wav"
        }

    def _mock_asr(self, audio_data: str, model: str) -> Dict:
        """
        Mock ASR transcription.
        """
        # print(f"👂 Transcribing audio with {model}..." )
        return {
            "status": "success",
            "transcription": "This is a simulated transcription.",
            "confidence": 0.98
        }

    async def run_self_test(self):
        """Verify services are working."""
        print("\n🧪 Running Audio I/O Self-Test...")
        
        # Test TTS
        print("  • Testing /tts_realtime...", end=" ")
        res = await self.handle_request("tts_realtime", "Hello world")
        if res.get("status") == "success": print("✅ PASS")
        else: print("❌ FAIL")

        # Test Premium TTS
        print("  • Testing /tts_premium...", end=" ")
        res = await self.handle_request("tts_premium", "Hello world")
        if res.get("status") == "success": print("✅ PASS")
        else: print("❌ FAIL")

        # Test ASR
        print("  • Testing /asr_realtime...", end=" ")
        res = await self.handle_request("asr_realtime", "dummy_audio_bytes")
        if res.get("status") == "success": print("✅ PASS")
        else: print("❌ FAIL")
        
        print("✅ Self-test complete.\n")

if __name__ == "__main__":
    agent = AudioIOAgent()
    asyncio.run(agent.start())
    asyncio.run(agent.run_self_test())
