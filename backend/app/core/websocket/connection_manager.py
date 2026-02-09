"""
WebSocket Connection Manager for Real-time Chat
"""
from typing import Dict, Set
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class WebSocketConnection:
    """Represents a WebSocket connection."""
    user_id: str
    websocket: any
    session_id: str = ""
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)

class ConnectionManager:
    """Manages WebSocket connections for real-time chat."""
    
    def __init__(self):
        # user_id -> connection mapping (one connection per user)
        self._connections: Dict[str, WebSocketConnection] = {}
        # websocket -> user_id mapping
        self._websocket_to_user: Dict[str, str] = {}
        # session_id -> set of user_ids
        self._sessions: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket, user_id: str, session_id: str = ""):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        
        connection = WebSocketConnection(
            user_id=user_id,
            websocket=websocket,
            session_id=session_id
        )
        
        self._connections[user_id] = connection
        self._websocket_to_user[str(id(websocket))] = user_id
        
        if session_id:
            if session_id not in self._sessions:
                self._sessions[session_id] = set()
            self._sessions[session_id].add(user_id)
        
        print(f"✅ WebSocket connected: user_id={user_id}, session_id={session_id}")
        return connection
    
    async def disconnect(self, websocket, user_id: str):
        """Close and cleanup a WebSocket connection."""
        ws_id = str(id(websocket))
        
        if ws_id in self._websocket_to_user:
            del self._websocket_to_user[ws_id]
        
        if user_id in self._connections:
            connection = self._connections[user_id]
            session_id = connection.session_id
            
            if session_id and session_id in self._sessions:
                self._sessions[session_id].discard(user_id)
                if not self._sessions[session_id]:
                    del self._sessions[session_id]
            
            del self._connections[user_id]
        
        print(f"❌ WebSocket disconnected: user_id={user_id}")
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Send a message to a specific user."""
        connection = self._connections.get(user_id)
        if connection:
            try:
                await connection.websocket.send_json(message)
            except Exception as e:
                print(f"Error sending message to {user_id}: {e}")
    
    async def broadcast_to_session(self, message: dict, session_id: str, exclude_user: str = None):
        """Broadcast a message to all users in a session."""
        if session_id not in self._sessions:
            return
        
        for user_id in self._sessions[session_id]:
            if exclude_user and user_id == exclude_user:
                continue
            await self.send_personal_message(message, user_id)
    
    async def broadcast_to_all(self, message: dict, exclude_user: str = None):
        """Broadcast a message to all connected users."""
        for user_id in self._connections:
            if exclude_user and user_id == exclude_user:
                continue
            await self.send_personal_message(message, user_id)
    
    def get_online_users(self, session_id: str = None) -> list:
        """Get list of online users, optionally filtered by session."""
        if session_id:
            return list(self._sessions.get(session_id, set()))
        return list(self._connections.keys())
    
    def is_online(self, user_id: str) -> bool:
        """Check if a user is online."""
        return user_id in self._connections
    
    def get_connection_count(self) -> int:
        """Get total number of connections."""
        return len(self._connections)
    
    async def send_typing_indicator(self, user_id: str, session_id: str, is_typing: bool):
        """Send typing indicator to session participants."""
        await self.broadcast_to_session({
            "type": "typing",
            "user_id": user_id,
            "is_typing": is_typing,
            "timestamp": datetime.utcnow().isoformat()
        }, session_id, exclude_user=user_id)

# Global connection manager instance
ws_manager = ConnectionManager()
