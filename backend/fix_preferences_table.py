#!/usr/bin/env python3
"""
Fix the user_preferences table by dropping and recreating it.
Run: python fix_preferences_table.py
"""
import asyncpg
import asyncio


async def fix_table():
    """Drop and recreate user_preferences table."""
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='chatbot',
        password='chatbot_secret',
        database='chatbot_db'
    )
    
    try:
        print("Dropping user_preferences table...")
        await conn.execute("DROP TABLE IF EXISTS user_preferences CASCADE")
        print("✅ Dropped table")
        
        print("Creating user_preferences table...")
        await conn.execute("""
            CREATE TABLE user_preferences (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                preferred_colors TEXT[] DEFAULT '{}'::text[],
                preferred_fabrics TEXT[] DEFAULT '{}'::text[],
                preferred_styles TEXT[] DEFAULT '{}'::text[],
                preferred_occasions TEXT[] DEFAULT '{}'::text[],
                body_type VARCHAR(50) DEFAULT NULL,
                fit_preference VARCHAR(50) DEFAULT NULL,
                size_preference VARCHAR(10) DEFAULT NULL,
                budget_min DECIMAL(10, 2) DEFAULT NULL,
                budget_max DECIMAL(10, 2) DEFAULT NULL,
                budget_currency VARCHAR(3) DEFAULT 'USD',
                language_preference VARCHAR(10) DEFAULT 'en',
                notification_preferences JSONB DEFAULT '{}'::jsonb,
                preferred_brands TEXT[] DEFAULT '{}'::text[],
                avoid_colors TEXT[] DEFAULT '{}'::text[],
                avoid_fabrics TEXT[] DEFAULT '{}'::text[],
                interaction_count INTEGER DEFAULT 0,
                last_interaction TIMESTAMP DEFAULT NULL,
                preference_confidence FLOAT DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Created table")
        
        print("Creating index...")
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id 
            ON user_preferences(user_id)
        """)
        print("✅ Created index")
        
        print("Creating trigger...")
        await conn.execute("""
            CREATE OR REPLACE FUNCTION update_user_preferences_timestamp()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql
        """)
        
        await conn.execute("""
            DROP TRIGGER IF EXISTS trigger_user_preferences_updated ON user_preferences
        """)
        await conn.execute("""
            CREATE TRIGGER trigger_user_preferences_updated
                BEFORE UPDATE ON user_preferences
                FOR EACH ROW
                EXECUTE FUNCTION update_user_preferences_timestamp()
        """)
        print("✅ Created trigger")
        
        print("Initializing preferences for existing users...")
        result = await conn.execute("""
            INSERT INTO user_preferences (user_id)
            SELECT id FROM users
            WHERE NOT EXISTS (
                SELECT 1 FROM user_preferences 
                WHERE user_preferences.user_id = users.id
            )
            ON CONFLICT DO NOTHING
        """)
        
        count = await conn.fetchval("SELECT COUNT(*) FROM user_preferences")
        print(f"✅ Users with preferences: {count}")
        
        print("\n🎉 Table fixed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(fix_table())
