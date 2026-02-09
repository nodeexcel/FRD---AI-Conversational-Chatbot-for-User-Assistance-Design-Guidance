#!/usr/bin/env python3
"""
Database initialization script for User Preferences.
Run: python init_db.py
"""
import asyncpg
import asyncio


async def init_user_preferences():
    """Initialize user preferences table."""
    print("Initializing user preferences table...")
    
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='chatbot',
        password='chatbot_secret',
        database='chatbot_db'
    )
    
    try:
        # Create user_preferences table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                preferred_colors TEXT[] DEFAULT '{}',
                preferred_fabrics TEXT[] DEFAULT '{}',
                preferred_styles TEXT[] DEFAULT '{}',
                preferred_occasions TEXT[] DEFAULT '{}',
                body_type VARCHAR(50),
                fit_preference VARCHAR(50),
                size_preference VARCHAR(10),
                budget_min DECIMAL(10, 2),
                budget_max DECIMAL(10, 2),
                budget_currency VARCHAR(3) DEFAULT 'USD',
                language_preference VARCHAR(10) DEFAULT 'en',
                notification_preferences JSONB DEFAULT '{}',
                preferred_brands TEXT[] DEFAULT '{}',
                avoid_colors TEXT[] DEFAULT '{}',
                avoid_fabrics TEXT[] DEFAULT '{}',
                interaction_count INTEGER DEFAULT 0,
                last_interaction TIMESTAMP,
                preference_confidence FLOAT DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ user_preferences table created")
        
        # Create index
        try:
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id 
                ON user_preferences(user_id)
            """)
            print("✅ Index created")
        except Exception as e:
            print(f"⚠️ Index creation skipped: {e}")
        
        # Create trigger function
        await conn.execute("""
            CREATE OR REPLACE FUNCTION update_user_preferences_timestamp()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql
        """)
        
        # Drop and recreate trigger
        await conn.execute("""
            DROP TRIGGER IF EXISTS trigger_user_preferences_updated ON user_preferences
        """)
        await conn.execute("""
            CREATE TRIGGER trigger_user_preferences_updated
                BEFORE UPDATE ON user_preferences
                FOR EACH ROW
                EXECUTE FUNCTION update_user_preferences_timestamp()
        """)
        print("✅ Trigger created")
        
        # Initialize preferences for existing users
        result = await conn.execute("""
            INSERT INTO user_preferences (user_id)
            SELECT id FROM users
            WHERE NOT EXISTS (
                SELECT 1 FROM user_preferences 
                WHERE user_preferences.user_id = users.id
            )
            ON CONFLICT DO NOTHING
        """)
        
        # Count users with preferences
        count = await conn.fetchval("SELECT COUNT(*) FROM user_preferences")
        print(f"✅ User preferences initialized. Total users with preferences: {count}")
        
        print("\n🎉 Database initialization complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(init_user_preferences())
