"""Token blacklist for JWT logout using Redis."""
import redis
import json
from datetime import datetime
from typing import Optional, Dict, Any
from app.config import settings

# Redis client
redis_client = None


def get_redis_client() -> redis.Redis:
    """Get or create Redis client."""
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis(
            host=settings.redis.host,
            port=settings.redis.port,
            db=settings.redis.db,
            decode_responses=True
        )
    return redis_client


def add_to_blacklist(token: str, expires_in: int = 86400) -> bool:
    """
    Add token to blacklist.
    
    Args:
        token: JWT token to blacklist
        expires_in: Seconds until token naturally expires
    
    Returns:
        True if added successfully
    """
    try:
        client = get_redis_client()
        # Store token with expiry
        client.setex(
            f"blacklist:{token}",
            expires_in,
            json.dumps({
                "blacklisted_at": datetime.utcnow().isoformat(),
                "expires_at": expires_in
            })
        )
        return True
    except Exception as e:
        print(f"Error adding to blacklist: {e}")
        return False


def is_blacklisted(token: str) -> bool:
    """
    Check if token is blacklisted.
    
    Args:
        token: JWT token to check
    
    Returns:
        True if token is blacklisted
    """
    try:
        client = get_redis_client()
        result = client.get(f"blacklist:{token}")
        return result is not None
    except Exception as e:
        print(f"Error checking blacklist: {e}")
        return False


def remove_from_blacklist(token: str) -> bool:
    """
    Remove token from blacklist.
    
    Args:
        token: JWT token to remove
    
    Returns:
        True if removed successfully
    """
    try:
        client = get_redis_client()
        client.delete(f"blacklist:{token}")
        return True
    except Exception as e:
        print(f"Error removing from blacklist: {e}")
        return False


def check_token_status(token: str) -> Dict[str, Any]:
    """
    Check token status (blacklisted, expired, etc.).
    
    Args:
        token: JWT token to check
    
    Returns:
        Dict with status info
    """
    from app.core.auth.jwt_handler import verify_token
    
    if is_blacklisted(token):
        return {
            "valid": False,
            "status": "blacklisted",
            "message": "Token has been revoked"
        }
    
    payload = verify_token(token)
    if payload is None:
        return {
            "valid": False,
            "status": "expired",
            "message": "Token has expired"
        }
    
    return {
        "valid": True,
        "status": "active",
        "message": "Token is valid"
    }


def close():
    """Close Redis connection."""
    global redis_client
    if redis_client:
        redis_client.close()
        redis_client = None
