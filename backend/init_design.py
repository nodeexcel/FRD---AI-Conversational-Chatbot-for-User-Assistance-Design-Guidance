#!/usr/bin/env python3
"""
Initialize the design sessions tables for Guided Design Flow.
Run: python init_design.py
"""
import asyncio
import asyncpg


async def init_design():
    """Initialize design tables."""
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='chatbot',
        password='chatbot_secret',
        database='chatbot_db'
    )
    
    try:
        print("Creating design tables...")
        
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
        print("✅ Created design_sessions table")
        
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
        print("✅ Created design_feedback table")
        
        # Create indexes
        try:
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_design_sessions_status 
                ON design_sessions(status)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_design_sessions_user 
                ON design_sessions(created_by)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_design_feedback_session 
                ON design_feedback(design_session_id)
            """)
            print("✅ Created indexes")
        except Exception as e:
            print(f"⚠️ Index creation skipped: {e}")
        
        # Count records
        session_count = await conn.fetchval("SELECT COUNT(*) FROM design_sessions")
        feedback_count = await conn.fetchval("SELECT COUNT(*) FROM design_feedback")
        print(f"✅ Total design sessions: {session_count}")
        print(f"✅ Total feedback records: {feedback_count}")
        
        print("\n🎉 Design tables initialization complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(init_design())
