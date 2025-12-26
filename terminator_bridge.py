import os
import sys
import asyncio
import json
import logging
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List

# Ensure we can import core modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.terminator_agent_communication_bus import get_communication_bus, MessageType, Message

# Import guardian agent
from core.terminator_infinite_loop_guardian_agent import start_guardian

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TerminatorBridge")

app = FastAPI()

# Connection Manager for WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()
bus = get_communication_bus()

# --- Bus Listener ---
# We need to listen to the bus and forward messages to the websocket
async def bus_listener():
    # Register as a listener agent
    await bus.register_agent_async("web_bridge")
    logger.info("✅ Connected to Terminator Bus")

    while True:
        # Poll for messages for 'web_bridge' or broadcasts
        msg = await bus.get_message_async("web_bridge", timeout=0.1)
        if msg:
            # Forward to Frontend
            payload = {
                "type": msg.message_type.value if hasattr(msg.message_type, 'value') else str(msg.message_type),
                "sender": msg.sender_agent,
                "content": msg.content,
                "subject": msg.subject
            }
            await manager.broadcast(json.dumps(payload))

        await asyncio.sleep(0.1)

# --- Metrics Broadcaster ---
async def metrics_broadcaster():
    """Broadcast agent metrics every 2 seconds"""
    logger.info("📊 Starting metrics broadcaster (2s interval)")

    while True:
        try:
            # Gather metrics
            top_agents = bus.get_top_active_agents(limit=10)
            bus_status = bus.get_bus_status()

            # Format payload
            metrics_payload = {
                "type": "metrics_update",
                "content": {
                    "agents": top_agents,
                    "system": {
                        "total_agents": bus_status["total_agents"],
                        "agents_online": bus_status["agents_online"],
                        "total_messages": sum(s.messages_processed for s in bus.agent_registry.values()),
                        "total_queue_size": sum(bus_status["queues"].values()),
                    },
                    "timestamp": datetime.now().isoformat()
                }
            }

            await manager.broadcast(json.dumps(metrics_payload))
        except Exception as e:
            logger.error(f"Metrics broadcast error: {e}")

        await asyncio.sleep(2)  # 2-second interval

# --- WebSocket Endpoint ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Parse command from Frontend
            try:
                command_data = json.loads(data)
                command = command_data.get("command")
                
                if command:
                    # Send to Terminator Bus (to Master Agent)
                    # We send to 'terminator_master' usually
                    await bus.send_message_async(
                        sender_agent="web_bridge",
                        recipient_agent="terminator_master",
                        subject="Web Command",
                        content={"command": command},
                        message_type=MessageType.REQUEST
                    )
                    
                    # Ack
                    await websocket.send_text(json.dumps({
                        "type": "system",
                        "content": f"Command '{command}' sent to neural net."
                    }))
            except Exception as e:
                logger.error(f"Error processing command: {e}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# --- Static Files (The React App) ---
# Serve the React build directory
react_dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), "terminator-web-terminal/dist")

if os.path.exists(react_dist):
    app.mount("/assets", StaticFiles(directory=f"{react_dist}/assets"), name="assets")
    
    @app.get("/")
    async def serve_react_app():
        return FileResponse(f"{react_dist}/index.html")
    
    # Catch-all for React Router (if used in future)
    @app.exception_handler(404)
    async def not_found(request, exc):
        return FileResponse(f"{react_dist}/index.html")
else:
    logger.warning("⚠️ React build not found. Run 'npm run build' in terminator-web-terminal/")

# --- Startup Event ---
@app.on_event("startup")
async def startup_event():
    # Start the bus listener in background
    asyncio.create_task(bus_listener())

    # Start metrics broadcaster
    asyncio.create_task(metrics_broadcaster())
    logger.info("✅ Metrics broadcaster scheduled")

    # Start the Infinite Loop Guardian Agent
    logger.info("🛡️  Starting Infinite Loop Guardian...")
    guardian = start_guardian()
    logger.info("✅ Infinite Loop Guardian is now protecting your system")

if __name__ == "__main__":
    import uvicorn
    # Run on 0.0.0.0 to allow access from local network (mobile/tablet)
    print("🚀 Terminator Bridge Active on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
