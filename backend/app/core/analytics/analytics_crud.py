"""
Analytics Database Operations
"""
import asyncpg
from datetime import datetime, timedelta, date as dt
from typing import Optional, List, Dict, Any
from .analytics_models import AgentType

DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "chatbot",
    "password": "chatbot_secret",
    "database": "chatbot_db",
}

async def get_db_connection():
    return await asyncpg.connect(**DATABASE_CONFIG)

async def init_analytics_tables():
    """Initialize analytics and learning tables."""
    conn = await get_db_connection()
    try:
        print("Creating analytics tables...")
        
        # Chat messages table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                session_id VARCHAR(100) NOT NULL,
                user_id UUID NOT NULL,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                agent_used VARCHAR(50) NOT NULL,
                response_time_ms INTEGER NOT NULL,
                tokens_used INTEGER,
                was_helpful BOOLEAN,
                feedback TEXT,
                metadata JSONB DEFAULT '{}'::jsonb,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Created chat_messages table")
        
        # Chat sessions table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id VARCHAR(100) PRIMARY KEY,
                user_id UUID NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                message_count INTEGER DEFAULT 0,
                total_response_time_ms INTEGER DEFAULT 0,
                agents_used TEXT[] DEFAULT '{}',
                topics_discussed TEXT[] DEFAULT '{}'
            )
        """)
        print("✅ Created chat_sessions table")
        
        # Learning feedback table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS learning_feedback (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                session_id VARCHAR(100),
                user_id UUID NOT NULL,
                category VARCHAR(100) NOT NULL,
                rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
                comment TEXT,
                suggested_improvement TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Created learning_feedback table")
        
        # Daily analytics summary table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_analytics (
                date DATE PRIMARY KEY,
                total_messages INTEGER DEFAULT 0,
                total_users INTEGER DEFAULT 0,
                active_users INTEGER DEFAULT 0,
                total_sessions INTEGER DEFAULT 0,
                average_response_time_ms FLOAT DEFAULT 0,
                agent_usage JSONB DEFAULT '{}'::jsonb,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Created daily_analytics table")
        
        # Create indexes
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_messages_user 
            ON chat_messages(user_id)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_messages_session 
            ON chat_messages(session_id)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_messages_created 
            ON chat_messages(created_at)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_sessions_user 
            ON chat_sessions(user_id)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_learning_feedback_user 
            ON learning_feedback(user_id)
        """)
        print("✅ Created indexes")
        
        print("\n🎉 Analytics tables initialized successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await conn.close()

class AnalyticsCRUD:
    """CRUD operations for analytics."""
    
    @staticmethod
    async def log_message(
        session_id: str,
        user_id: str,
        user_message: str,
        ai_response: str,
        agent_used: str,
        response_time_ms: int,
        tokens_used: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        conn = await get_db_connection()
        try:
            row = await conn.fetchrow("""
                INSERT INTO chat_messages 
                (session_id, user_id, user_message, ai_response, agent_used, response_time_ms, tokens_used, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING *
            """, session_id, user_id, user_message, ai_response, agent_used, response_time_ms, tokens_used, metadata)
            
            # Update session
            await conn.execute("""
                UPDATE chat_sessions
                SET message_count = message_count + 1,
                    total_response_time_ms = total_response_time_ms + $1,
                    agents_used = array_append(agents_used, $2)
                WHERE id = $3
            """, response_time_ms, agent_used, session_id)
            
            return dict(row)
        finally:
            await conn.close()
    
    @staticmethod
    async def start_session(session_id: str, user_id: str) -> None:
        conn = await get_db_connection()
        try:
            await conn.execute("""
                INSERT INTO chat_sessions (id, user_id)
                VALUES ($1, $2)
                ON CONFLICT (id) DO NOTHING
            """, session_id, user_id)
        finally:
            await conn.close()
    
    @staticmethod
    async def end_session(session_id: str) -> None:
        conn = await get_db_connection()
        try:
            await conn.execute("""
                UPDATE chat_sessions
                SET ended_at = CURRENT_TIMESTAMP
                WHERE id = $1
            """, session_id)
        finally:
            await conn.close()
    
    @staticmethod
    async def get_user_messages(user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        conn = await get_db_connection()
        try:
            rows = await conn.fetch("""
                SELECT * FROM chat_messages
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT $2
            """, user_id, limit)
            return [dict(row) for row in rows]
        finally:
            await conn.close()
    
    @staticmethod
    async def get_user_sessions(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        conn = await get_db_connection()
        try:
            rows = await conn.fetch("""
                SELECT * FROM chat_sessions
                WHERE user_id = $1
                ORDER BY started_at DESC
                LIMIT $2
            """, user_id, limit)
            return [dict(row) for row in rows]
        finally:
            await conn.close()
    
    @staticmethod
    async def update_feedback(message_id: str, was_helpful: bool, feedback: Optional[str] = None) -> None:
        conn = await get_db_connection()
        try:
            await conn.execute("""
                UPDATE chat_messages
                SET was_helpful = $1, feedback = $2
                WHERE id = $3
            """, was_helpful, feedback, message_id)
        finally:
            await conn.close()
    
    @staticmethod
    async def log_learning_feedback(
        session_id: Optional[str],
        user_id: str,
        category: str,
        rating: int,
        comment: Optional[str] = None,
        suggested_improvement: Optional[str] = None
    ) -> Dict[str, Any]:
        conn = await get_db_connection()
        try:
            row = await conn.fetchrow("""
                INSERT INTO learning_feedback (session_id, user_id, category, rating, comment, suggested_improvement)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
            """, session_id, user_id, category, rating, comment, suggested_improvement)
            return dict(row)
        finally:
            await conn.close()
    
    @staticmethod
    async def get_user_analytics(user_id: str) -> Dict[str, Any]:
        conn = await get_db_connection()
        try:
            # Get message stats
            msg_stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_messages,
                    AVG(response_time_ms) as avg_response_time,
                    COUNT(DISTINCT session_id) as total_sessions
                FROM chat_messages
                WHERE user_id = $1
            """, user_id)
            
            # Get agent usage
            agent_usage = await conn.fetch("""
                SELECT agent_used, COUNT(*) as count
                FROM chat_messages
                WHERE user_id = $1
                GROUP BY agent_used
                ORDER BY count DESC
            """, user_id)
            
            # Get daily message counts (last 7 days)
            daily_counts = await conn.fetch("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM chat_messages
                WHERE user_id = $1 AND created_at >= CURRENT_DATE - INTERVAL '7 days'
                GROUP BY DATE(created_at)
                ORDER BY date
            """, user_id)
            
            # Get learning feedback
            feedback = await conn.fetchrow("""
                SELECT AVG(rating) as avg_rating, COUNT(*) as total_feedback
                FROM learning_feedback
                WHERE user_id = $1
            """, user_id)
            
            # Get design sessions count
            design_count = await conn.fetchval("""
                SELECT COUNT(*) FROM design_sessions WHERE created_by = $1
            """, user_id)
            
            # Get documents count
            doc_count = await conn.fetchval("""
                SELECT COUNT(*) FROM rag_documents WHERE created_by = $1
            """, user_id)
            
            return {
                "total_messages": msg_stats['total_messages'] or 0,
                "average_response_time_ms": round(msg_stats['avg_response_time'] or 0, 2),
                "total_sessions": msg_stats['total_sessions'] or 0,
                "agent_usage": [{"agent": row['agent_used'], "count": row['count']} for row in agent_usage],
                "daily_counts": [{"date": str(row['date']), "count": row['count']} for row in daily_counts],
                "average_rating": round(feedback['avg_rating'] or 0, 2),
                "total_feedback": feedback['total_feedback'] or 0,
                "designs_created": design_count or 0,
                "documents_uploaded": doc_count or 0,
            }
        finally:
            await conn.close()
    
    @staticmethod
    async def update_daily_analytics(date: dt) -> None:
        conn = await get_db_connection()
        try:
            stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_messages,
                    COUNT(DISTINCT user_id) as active_users,
                    COUNT(DISTINCT session_id) as total_sessions,
                    AVG(response_time_ms) as avg_response_time
                FROM chat_messages
                WHERE DATE(created_at) = $1
            """, date)
            
            agent_usage = await conn.fetch("""
                SELECT agent_used, COUNT(*) as count
                FROM chat_messages
                WHERE DATE(created_at) = $1
                GROUP BY agent_used
            """, date)
            
            await conn.execute("""
                INSERT INTO daily_analytics (date, total_messages, active_users, total_sessions, average_response_time_ms, agent_usage)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (date) DO UPDATE SET
                    total_messages = EXCLUDED.total_messages,
                    active_users = EXCLUDED.active_users,
                    total_sessions = EXCLUDED.total_sessions,
                    average_response_time_ms = EXCLUDED.average_response_time_ms,
                    agent_usage = EXCLUDED.agent_usage,
                    updated_at = CURRENT_TIMESTAMP
            """, date, stats['total_messages'] or 0, stats['active_users'] or 0, 
                stats['total_sessions'] or 0, stats['avg_response_time'] or 0,
                {row['agent_used']: row['count'] for row in agent_usage})
        finally:
            await conn.close()
