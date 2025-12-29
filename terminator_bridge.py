import os
import sys
import asyncio
import json
import logging
import secrets
from datetime import datetime, timedelta
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional

# Ensure we can import core modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.terminator_agent_communication_bus import get_communication_bus, MessageType, Message

# Import guardian agent
from core.terminator_infinite_loop_guardian_agent import start_guardian

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TerminatorBridge")

app = FastAPI()

# SECURITY: Configure CORS with restricted origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:8000",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# SECURITY: Session/Token Management
class SessionManager:
    """Manages authentication tokens for WebSocket connections"""

    def __init__(self):
        self.sessions: Dict[str, dict] = {}
        self.session_timeout = 3600  # 1 hour in seconds

    def create_session(self, user_id: str = "default_user") -> str:
        """Create a new session token"""
        token = secrets.token_urlsafe(32)  # 256 bits of entropy
        self.sessions[token] = {
            'user_id': user_id,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(seconds=self.session_timeout),
            'last_activity': datetime.now()
        }
        logger.info(f"🔐 New session created for {user_id}")
        return token

    def verify_token(self, token: Optional[str]) -> bool:
        """Verify if a token is valid and not expired"""
        if not token or token not in self.sessions:
            return False

        session = self.sessions[token]

        # Check if expired
        if datetime.now() > session['expires_at']:
            del self.sessions[token]
            logger.warning(f"⚠️  Session expired and removed")
            return False

        # Update last activity
        session['last_activity'] = datetime.now()
        return True

    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        now = datetime.now()
        expired = [token for token, session in self.sessions.items()
                  if now > session['expires_at']]

        for token in expired:
            del self.sessions[token]

        if expired:
            logger.info(f"🧹 Cleaned up {len(expired)} expired sessions")

session_manager = SessionManager()

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

# SECURITY: Authentication Endpoint
@app.post("/api/auth/session")
async def create_session():
    """Create a new authenticated session token"""
    try:
        # In production, you would validate credentials here
        # For now, we create a session for local access
        token = session_manager.create_session("local_user")
        return JSONResponse({
            "token": token,
            "expires_in": session_manager.session_timeout
        })
    except Exception as e:
        logger.error(f"Session creation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create session")

# SECURITY: Secured WebSocket Endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: Optional[str] = Query(None)):
    """
    Secure WebSocket endpoint with token authentication

    Usage: ws://localhost:8000/ws?token=YOUR_TOKEN_HERE
    """
    # SECURITY: Verify token before accepting connection
    if not session_manager.verify_token(token):
        logger.warning(f"⚠️  Unauthorized WebSocket connection attempt")
        await websocket.close(code=4001, reason="Unauthorized - Invalid or missing token")
        return

    logger.info(f"✅ Authenticated WebSocket connection established")
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()

            # SECURITY: Re-verify token on each message (prevents token reuse after expiry)
            if not session_manager.verify_token(token):
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "content": "Session expired. Please reconnect."
                }))
                break

            # Parse command from Frontend
            try:
                command_data = json.loads(data)
                command = command_data.get("command")

                # SECURITY: Validate command length
                if command and len(command) > 10000:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "content": "Command too long (max 10KB)"
                    }))
                    continue

                if command:
                    # Send to Terminator Bus (to Master Agent)
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
                        "content": f"Command '{command[:100]}...' sent to neural net."
                    }))
            except json.JSONDecodeError:
                logger.error("Invalid JSON received")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "content": "Invalid JSON format"
                }))
            except Exception as e:
                logger.error(f"Error processing command: {e}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket disconnected")

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

# --- Session Cleanup Task ---
async def session_cleanup_task():
    """Periodically cleanup expired sessions"""
    while True:
        await asyncio.sleep(300)  # Every 5 minutes
        session_manager.cleanup_expired_sessions()

# --- Startup Event ---
@app.on_event("startup")
async def startup_event():
    # Start the bus listener in background
    asyncio.create_task(bus_listener())

    # Start metrics broadcaster
    asyncio.create_task(metrics_broadcaster())
    logger.info("✅ Metrics broadcaster scheduled")

    # SECURITY: Start session cleanup task
    asyncio.create_task(session_cleanup_task())
    logger.info("✅ Session cleanup task scheduled")

    # Start the Infinite Loop Guardian Agent
    logger.info("🛡️  Starting Infinite Loop Guardian...")
    guardian = start_guardian()
    logger.info("✅ Infinite Loop Guardian is now protecting your system")

if __name__ == "__main__":
    import uvicorn
    # Run on 0.0.0.0 to allow access from local network (mobile/tablet)
    print("🚀 Terminator Bridge Active on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
