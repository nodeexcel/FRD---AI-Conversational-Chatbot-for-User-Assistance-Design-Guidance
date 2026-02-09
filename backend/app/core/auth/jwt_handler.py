"""JWT Authentication utilities."""
import jwt
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import bcrypt
from app.config import settings

# Password hashing with bcrypt
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    try:
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


# JWT Configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


def create_access_token(
    user_id: str,
    email: str = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(user_id),
        "email": email,
        "jti": str(uuid.uuid4()),
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.session.secret_key,
        algorithm=ALGORITHM
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and verify a JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.session.secret_key,
            algorithms=[ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify token and return payload if valid."""
    # Check if token is blacklisted (for logout)
    from app.core.auth.token_blacklist import is_blacklisted
    if is_blacklisted(token):
        return None
    
    payload = decode_access_token(token)
    if payload is None:
        return None
    
    # Check expiration
    exp = payload.get("exp")
    if exp:
        exp_dt = datetime.fromtimestamp(exp)
        if datetime.utcnow() > exp_dt:
            return None
    
    return payload


def get_user_id_from_token(token: str) -> Optional[str]:
    """Extract user ID from JWT token."""
    payload = verify_token(token)
    if payload:
        return payload.get("sub")
    return None


def get_email_from_token(token: str) -> Optional[str]:
    """Extract email from JWT token."""
    payload = verify_token(token)
    if payload:
        return payload.get("email")
    return None


# FastAPI Dependency for getting current user
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    FastAPI dependency to get the current authenticated user.
    Returns a dict with user info or raises HTTPException.
    """
    token = credentials.credentials
    
    # Verify token
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Return user info
    return {
        "id": payload.get("sub"),
        "email": payload.get("email"),
        "name": payload.get("name"),
        "token": token,
    }
