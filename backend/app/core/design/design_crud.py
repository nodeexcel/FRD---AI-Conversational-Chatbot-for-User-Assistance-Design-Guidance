"""
Design Session Database Operations
"""
import asyncpg
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from .design_models import DesignStatus, DesignStep

DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "chatbot",
    "password": "chatbot_secret",
    "database": "chatbot_db",
}

async def get_db_connection():
    return await asyncpg.connect(**DATABASE_CONFIG)

async def init_design_tables():
    """Initialize design session and feedback tables."""
    conn = await get_db_connection()
    try:
        # Create design_sessions table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS design_sessions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(200) NOT NULL,
                description TEXT,
                design_type VARCHAR(100) NOT NULL,
                current_step VARCHAR(50) DEFAULT 'concept',
                status VARCHAR(50) DEFAULT 'draft',
                progress INTEGER DEFAULT 0,
                ai_suggestions JSONB DEFAULT '{}'::jsonb,
                user_inputs JSONB DEFAULT '{}'::jsonb,
                created_by UUID,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        
        # Create design_feedback table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS design_feedback (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                design_session_id UUID REFERENCES design_sessions(id) ON DELETE CASCADE,
                rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
                comment TEXT,
                what_liked TEXT,
                what_to_improve TEXT,
                created_by UUID,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_design_sessions_status 
            ON design_sessions(status)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_design_sessions_user 
            ON design_sessions(created_by)
        """)
        
        print("✅ Design tables initialized successfully")
    finally:
        await conn.close()

class DesignCRUD:
    """CRUD operations for design sessions."""
    
    @staticmethod
    async def create(user_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        conn = await get_db_connection()
        try:
            row = await conn.fetchrow("""
                INSERT INTO design_sessions (name, description, design_type, created_by)
                VALUES ($1, $2, $3, $4)
                RETURNING *
            """, kwargs.get('name'), kwargs.get('description'), 
                kwargs.get('design_type'), user_id)
            return dict(row)
        finally:
            await conn.close()
    
    @staticmethod
    async def get_by_id(session_id: str) -> Optional[Dict[str, Any]]:
        conn = await get_db_connection()
        try:
            row = await conn.fetchrow("SELECT * FROM design_sessions WHERE id = $1", session_id)
            return dict(row) if row else None
        finally:
            await conn.close()
    
    @staticmethod
    async def get_all(user_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = await get_db_connection()
        try:
            if status:
                rows = await conn.fetch("""
                    SELECT * FROM design_sessions 
                    WHERE created_by = $1 AND status = $2
                    ORDER BY created_at DESC
                """, user_id, status)
            else:
                rows = await conn.fetch("""
                    SELECT * FROM design_sessions 
                    WHERE created_by = $1
                    ORDER BY created_at DESC
                """, user_id)
            return [dict(row) for row in rows]
        finally:
            await conn.close()
    
    @staticmethod
    async def update(session_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        conn = await get_db_connection()
        try:
            # Build dynamic update query
            updates = []
            values = []
            param_count = 1
            
            for key, value in kwargs.items():
                if value is not None and key not in ['id', 'created_at', 'created_by']:
                    updates.append(f"{key} = ${param_count}")
                    values.append(value)
                    param_count += 1
            
            if not updates:
                return await DesignCRUD.get_by_id(session_id)
            
            updates.append(f"updated_at = ${param_count}")
            values.append(datetime.now())
            param_count += 1
            values.append(session_id)
            
            query = f"""
                UPDATE design_sessions 
                SET {', '.join(updates)}
                WHERE id = ${param_count}
                RETURNING *
            """
            
            row = await conn.fetchrow(query, *values)
            return dict(row) if row else None
        finally:
            await conn.close()
    
    @staticmethod
    async def update_step(session_id: str, step: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user inputs for a specific step and advance to next step."""
        conn = await get_db_connection()
        try:
            # Get current session
            session = await DesignCRUD.get_by_id(session_id)
            if not session:
                return None
            
            # Calculate progress
            steps_order = ['concept', 'measurements', 'fabric', 'style', 'details', 'review']
            current_idx = steps_order.index(step) if step in steps_order else 0
            progress = int(((current_idx + 1) / len(steps_order)) * 100)
            
            # Update user_inputs
            current_inputs = session.get('user_inputs', {}) or {}
            current_inputs[step] = data
            
            # Determine next step
            next_step = steps_order[current_idx + 1] if current_idx < len(steps_order) - 1 else None
            new_status = DesignStatus.IN_PROGRESS.value if progress < 100 else DesignStatus.PENDING_REVIEW.value
            
            row = await conn.fetchrow("""
                UPDATE design_sessions 
                SET user_inputs = $1, current_step = $2, progress = $3, status = $4, updated_at = $5
                WHERE id = $6
                RETURNING *
            """, current_inputs, next_step or step, progress, new_status, datetime.now(), session_id)
            
            return dict(row) if row else None
        finally:
            await conn.close()
    
    @staticmethod
    async def complete(session_id: str) -> Optional[Dict[str, Any]]:
        conn = await get_db_connection()
        try:
            row = await conn.fetchrow("""
                UPDATE design_sessions 
                SET status = $1, progress = 100, completed_at = $2, updated_at = $2
                WHERE id = $3
                RETURNING *
            """, DesignStatus.COMPLETED.value, datetime.now(), session_id)
            return dict(row) if row else None
        finally:
            await conn.close()
    
    @staticmethod
    async def delete(session_id: str) -> bool:
        conn = await get_db_connection()
        try:
            result = await conn.execute("DELETE FROM design_sessions WHERE id = $1", session_id)
            return result != "DELETE 0"
        finally:
            await conn.close()

class DesignFeedbackCRUD:
    """CRUD operations for design feedback."""
    
    @staticmethod
    async def create(design_session_id: str, user_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        conn = await get_db_connection()
        try:
            row = await conn.fetchrow("""
                INSERT INTO design_feedback (design_session_id, rating, comment, what_liked, what_to_improve, created_by)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
            """, design_session_id, kwargs.get('rating'), kwargs.get('comment'),
                kwargs.get('what_liked'), kwargs.get('what_to_improve'), user_id)
            return dict(row)
        finally:
            await conn.close()
    
    @staticmethod
    async def get_by_session_id(design_session_id: str) -> Optional[Dict[str, Any]]:
        conn = await get_db_connection()
        try:
            row = await conn.fetchrow("SELECT * FROM design_feedback WHERE design_session_id = $1", design_session_id)
            return dict(row) if row else None
        finally:
            await conn.close()
    
    @staticmethod
    async def get_average_rating(design_session_id: str) -> float:
        conn = await get_db_connection()
        try:
            avg = await conn.fetchval("SELECT AVG(rating) FROM design_feedback WHERE design_session_id = $1", design_session_id)
            return round(avg, 2) if avg else 0.0
        finally:
            await conn.close()
