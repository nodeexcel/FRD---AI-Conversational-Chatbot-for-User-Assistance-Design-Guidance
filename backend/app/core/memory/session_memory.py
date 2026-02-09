"""Session memory management using Redis."""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class SessionMemory:
    """Session memory manager using Redis."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """Initialize session memory."""
        self.redis_url = redis_url
        self.redis_client = None
        logger.info("Session memory initialized")
    
    async def connect(self):
        """Connect to Redis."""
        try:
            import redis.asyncio as redis
            self.redis_client = redis.from_url(self.redis_url)
            logger.info("Connected to Redis")
        except Exception as e:
            logger.error(f"Redis connection error: {e}")
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data."""
        try:
            if self.redis_client:
                data = await self.redis_client.get(f"session:{session_id}")
                if data:
                    return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Get session error: {e}")
            return None
    
    async def save_session(
        self,
        session_id: str,
        data: Dict,
        expire_minutes: int = 1440  # 24 hours
    ):
        """Save session data."""
        try:
            if self.redis_client:
                await self.redis_client.set(
                    f"session:{session_id}",
                    json.dumps(data, default=str),
                    ex=expire_minutes * 60
                )
                logger.info(f"Session saved: {session_id}")
        except Exception as e:
            logger.error(f"Save session error: {e}")
    
    async def add_message(
        self,
        session_id: str,
        message: Dict
    ):
        """Add message to conversation history."""
        try:
            session = await self.get_session(session_id) or {"messages": []}
            session["messages"].append({
                **message,
                "timestamp": datetime.utcnow().isoformat()
            })
            await self.save_session(session_id, session)
        except Exception as e:
            logger.error(f"Add message error: {e}")
    
    async def get_messages(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[Dict]:
        """Get conversation messages."""
        session = await self.get_session(session_id)
        if session:
            return session.get("messages", [])[-limit:]
        return []
    
    async def clear_session(self, session_id: str):
        """Clear session data."""
        try:
            if self.redis_client:
                await self.redis_client.delete(f"session:{session_id}")
                logger.info(f"Session cleared: {session_id}")
        except Exception as e:
            logger.error(f"Clear session error: {e}")
    
    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")


# Export memory instance
session_memory = SessionMemory()
