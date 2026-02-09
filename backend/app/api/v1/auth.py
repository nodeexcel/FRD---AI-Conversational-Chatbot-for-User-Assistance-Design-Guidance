"""Authentication API endpoints with JWT."""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import re
import logging

from app.core.auth.user_model import user_db, User
from app.core.auth.jwt_handler import create_access_token, verify_password

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models
class UserCreate(BaseModel):
    """User registration request."""
    email: EmailStr
    name: str
    password: str
    confirm_password: str


class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class UserResponse(BaseModel):
    """User response model."""
    id: str
    email: str
    name: str
    is_active: bool


class MessageResponse(BaseModel):
    """Message response."""
    message: str
    success: bool


# Password validation
def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number"
    return True, ""


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    """Register a new user."""
    # Validate passwords match
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Validate password strength
    valid, error = validate_password(user_data.password)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    # Initialize database
    await user_db.initialize()
    await user_db.create_table()
    
    # Check if user already exists
    existing = await user_db.get_user_by_email(user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    try:
        # Create user
        user = await user_db.create_user(
            email=user_data.email,
            name=user_data.name,
            password=user_data.password
        )
        
        # Generate token
        access_token = create_access_token(
            user_id=user.id,
            email=user.email
        )
        
        logger.info(f"User registered: {user.email}")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=86400,
            user={
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "is_active": user.is_active
            }
        )
    
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login user and return JWT token."""
    # Initialize database
    await user_db.initialize()
    
    # Verify credentials
    user = await user_db.verify_password(
        email=credentials.email,
        password=credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Generate token
    access_token = create_access_token(
        user_id=user.id,
        email=user.email
    )
    
    logger.info(f"User logged in: {user.email}")
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=86400,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "is_active": user.is_active
        }
    )


@router.post("/logout")
async def logout(authorization: str = None):
    """Logout user and invalidate token (server-side blacklist)."""
    from app.core.auth.jwt_handler import decode_access_token
    from app.core.auth.token_blacklist import add_to_blacklist
    
    token = None
    
    # Get token from Authorization header
    if authorization:
        if authorization.startswith("Bearer "):
            token = authorization[7:]
        else:
            token = authorization
    
    # Calculate token TTL for blacklist
    expires_in = 86400  # Default 24 hours
    if token:
        payload = decode_access_token(token)
        if payload:
            exp = payload.get("exp")
            if exp:
                # Calculate remaining seconds until expiry
                remaining = int(exp) - int(datetime.utcnow().timestamp())
                if remaining > 0:
                    expires_in = min(remaining, 86400)  # Max 24 hours
        
        # Add to blacklist
        add_to_blacklist(token, expires_in)
    
    return MessageResponse(
        message="Successfully logged out",
        success=True
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str = Depends(lambda x: None)):
    """Get current user profile (requires authentication)."""
    # This is a placeholder - actual implementation uses Depends with OAuth2
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"}
    )


@router.post("/refresh")
async def refresh_token(token: str):
    """Refresh access token."""
    from app.core.auth.jwt_handler import verify_token
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("sub")
    email = payload.get("email")
    
    # Generate new token
    access_token = create_access_token(
        user_id=user_id,
        email=email
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=86400,
        user={"id": user_id, "email": email}
    )


# Dependency for authentication
async def get_current_user_from_token(token: str) -> Optional[User]:
    """Extract user from JWT token."""
    from app.core.auth.jwt_handler import verify_token
    
    if not token:
        return None
    
    # Remove 'Bearer ' prefix if present
    if token.startswith("Bearer "):
        token = token[7:]
    
    payload = verify_token(token)
    if not payload:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    await user_db.initialize()
    user = await user_db.get_user_by_id(user_id)
    return user


class AuthMiddleware:
    """Auth middleware for protecting routes."""
    
    @staticmethod
    async def verify_token(request, token: str = None):
        """Verify JWT token from Authorization header."""
        if not token:
            token = request.headers.get("Authorization")
        
        if not token:
            return None
        
        if token.startswith("Bearer "):
            token = token[7:]
        
        payload = verify_token(token)
        if not payload:
            return None
        
        return payload
