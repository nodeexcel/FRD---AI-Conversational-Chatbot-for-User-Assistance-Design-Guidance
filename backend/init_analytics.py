#!/usr/bin/env python3
"""
Initialize the analytics tables for Learning Loop.
Run: python init_analytics.py
"""
import asyncio
import asyncpg


async def init_analytics():
    """Initialize analytics tables."""
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='chatbot',
        password='chatbot_secret',
        database='chatbot_db'
    )
    
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
        
        # Count records
        msg_count = await conn.fetchval("SELECT COUNT(*) FROM chat_messages")
        session_count = await conn.fetchval("SELECT COUNT(*) FROM chat_sessions")
        feedback_count = await conn.fetchval("SELECT COUNT(*) FROM learning_feedback")
        
        print(f"✅ Total chat messages: {msg_count}")
        print(f"✅ Total chat sessions: {session_count}")
        print(f"✅ Total learning feedback: {feedback_count}")
        
        print("\n🎉 Analytics tables initialization complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(init_analytics())
