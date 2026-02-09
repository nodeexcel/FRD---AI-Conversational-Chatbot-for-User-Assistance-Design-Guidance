"""User model and database operations."""
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass
import asyncpg
import logging
from app.config import settings
from app.core.auth.jwt_handler import hash_password, verify_password

logger = logging.getLogger(__name__)


@dataclass
class User:
    """User model."""
    id: str
    email: str
    name: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True


class UserDB:
    """User database operations."""
    
    def __init__(self):
        """Initialize user database."""
        self.pool: Optional[asyncpg.Pool] = None
    
    async def initialize(self):
        """Initialize connection pool."""
        if self.pool:
            return
        
        try:
            self.pool = await asyncpg.create_pool(
                host=settings.postgres_host,
                port=settings.postgres_port,
                user=settings.postgres_user,
                password=settings.postgres_password,
                database=settings.postgres_db,
                min_size=2,
                max_size=10
            )
            logger.info("UserDB connected to PostgreSQL")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    async def create_table(self):
        """Create users table if not exists."""
        if not self.pool:
            await self.initialize()
        
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    email VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    hashed_password VARCHAR(255) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index on email
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
            """)
            
            logger.info("Users table created/verified")
    
    async def create_user(
        self,
        email: str,
        name: str,
        password: str
    ) -> User:
        """Create a new user."""
        if not self.pool:
            await self.initialize()
        
        hashed_password = hash_password(password)
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO users (email, name, hashed_password)
                VALUES ($1, $2, $3)
                RETURNING id, email, name, hashed_password, created_at, updated_at, is_active
            """, email.lower(), name, hashed_password)
            
            return User(
                id=str(row["id"]),
                email=row["email"],
                name=row["name"],
                hashed_password=row["hashed_password"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                is_active=row["is_active"]
            )
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        if not self.pool:
            await self.initialize()
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT id, email, name, hashed_password, created_at, updated_at, is_active
                FROM users
                WHERE email = $1
            """, email.lower())
            
            if not row:
                return None
            
            return User(
                id=str(row["id"]),
                email=row["email"],
                name=row["name"],
                hashed_password=row["hashed_password"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                is_active=row["is_active"]
            )
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        if not self.pool:
            await self.initialize()
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT id, email, name, hashed_password, created_at, updated_at, is_active
                FROM users
                WHERE id = $1::uuid
            """, user_id)
            
            if not row:
                return None
            
            return User(
                id=str(row["id"]),
                email=row["email"],
                name=row["name"],
                hashed_password=row["hashed_password"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                is_active=row["is_active"]
            )
    
    async def verify_password(self, email: str, password: str) -> Optional[User]:
        """Verify user credentials."""
        user = await self.get_user_by_email(email)
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        return user
    
    async def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """Update user fields."""
        if not self.pool:
            await self.initialize()
        
        allowed_fields = ["name", "is_active"]
        update_parts = []
        values = []
        
        for key, value in kwargs.items():
            if key in allowed_fields:
                update_parts.append(f"{key} = ${len(values) + 1}")
                values.append(value)
        
        if not update_parts:
            return await self.get_user_by_id(user_id)
        
        update_parts.append("updated_at = CURRENT_TIMESTAMP")
        values.append(user_id)
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(f"""
                UPDATE users
                SET {', '.join(update_parts)}
                WHERE id = ${len(values)}::uuid
                RETURNING id, email, name, hashed_password, created_at, updated_at, is_active
            """, *values)
            
            if not row:
                return None
            
            return User(
                id=str(row["id"]),
                email=row["email"],
                name=row["name"],
                hashed_password=row["hashed_password"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                is_active=row["is_active"]
            )
    
    async def delete_user(self, user_id: str) -> bool:
        """Soft delete a user."""
        return await self.update_user(user_id, is_active=False)


# Export singleton
user_db = UserDB()
