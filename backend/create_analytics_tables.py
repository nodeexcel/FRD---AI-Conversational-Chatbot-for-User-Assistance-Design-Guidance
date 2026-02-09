"""
Create analytics tables in PostgreSQL
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def create_analytics_tables():
    """Create analytics tables in PostgreSQL."""
    
    # Get database connection parameters from environment
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/chatbot_db"
    )
    
    # SQL to create analytics tables
    sql = """
    -- Drop existing tables if exists (for fresh setup)
    DROP TABLE IF EXISTS chat_messages CASCADE;
    DROP TABLE IF EXISTS chat_sessions CASCADE;
    DROP TABLE IF EXISTS learning_feedback CASCADE;
    
    -- Create chat_sessions table
    CREATE TABLE chat_sessions (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ended_at TIMESTAMP,
        session_type VARCHAR(50) DEFAULT 'general',
        metadata JSONB DEFAULT '{}'
    );
    
    -- Create index on user_id and started_at
    CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
    CREATE INDEX idx_chat_sessions_started_at ON chat_sessions(started_at);
    
    -- Create chat_messages table
    CREATE TABLE chat_messages (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        user_message TEXT NOT NULL,
        ai_response TEXT NOT NULL,
        agent_used VARCHAR(50) NOT NULL DEFAULT 'general',
        response_time_ms INTEGER DEFAULT 0,
        tokens_used INTEGER DEFAULT 0,
        was_helpful BOOLEAN,
        user_feedback TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        metadata JSONB DEFAULT '{}'
    );
    
    -- Create indexes on chat_messages
    CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
    CREATE INDEX idx_chat_messages_user_id ON chat_messages(user_id);
    CREATE INDEX idx_chat_messages_created_at ON chat_messages(created_at);
    CREATE INDEX idx_chat_messages_agent_used ON chat_messages(agent_used);
    
    -- Create learning_feedback table
    CREATE TABLE learning_feedback (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        session_id UUID REFERENCES chat_sessions(id) ON DELETE SET NULL,
        category VARCHAR(100) NOT NULL,
        rating INTEGER CHECK (rating >= 1 AND rating <= 5),
        comment TEXT,
        suggested_improvement TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Create indexes on learning_feedback
    CREATE INDEX idx_learning_feedback_user_id ON learning_feedback(user_id);
    CREATE INDEX idx_learning_feedback_category ON learning_feedback(category);
    """
    
    try:
        await conn.execute(sql)
        print("✅ Analytics tables created successfully!")
        
        # Verify tables exist
        tables = await conn.fetch("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name LIKE 'chat_%' OR table_name = 'learning_feedback'
            ORDER BY table_name
        """)
        print("\nCreated tables:")
        for table in tables:
            print(f"  - {table['table_name']}")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(create_analytics_tables())
