#!/usr/bin/env python3
"""
Create users table in PostgreSQL
Run: python create_users_table.py
"""

import asyncpg
import asyncio


async def create_users_table():
    """Create the users table."""
    conn = None
    try:
        # Connect to PostgreSQL
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='chatbot',
            password='chatbot_secret',
            database='chatbot_db'
        )
        
        # Drop existing table
        await conn.execute("DROP TABLE IF EXISTS users CASCADE")
        print("✅ Dropped existing users table")
        
        # Create users table
        await conn.execute("""
            CREATE TABLE users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(255) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Created users table")
        
        # Create index
        await conn.execute("""
            CREATE INDEX idx_users_email ON users(email)
        """)
        print("✅ Created email index")
        
        # Verify table
        row = await conn.fetchrow("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'users' ORDER BY ordinal_position")
        print(f"✅ Table structure: {dict(row)}")
        
        # Insert a test user
        from app.core.auth.jwt_handler import hash_password
        hashed = hash_password("TestPass123")
        await conn.execute("""
            INSERT INTO users (email, name, hashed_password)
            VALUES ($1, $2, $3)
        """, "test@example.com", "Test User", hashed)
        print("✅ Inserted test user (test@example.com)")
        
        # Query the user
        user = await conn.fetchrow("SELECT id, email, name FROM users WHERE email = $1", "test@example.com")
        print(f"✅ Test user created: {dict(user)}")
        
        print("\n✅ Users table setup complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        if conn:
            await conn.close()


if __name__ == "__main__":
    asyncio.run(create_users_table())
