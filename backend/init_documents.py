#!/usr/bin/env python3
"""
Initialize the documents table for RAG Knowledge Base.
Run: python init_documents.py
"""
import asyncio
import asyncpg


async def init_documents():
    """Initialize documents table."""
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='chatbot',
        password='chatbot_secret',
        database='chatbot_db'
    )
    
    try:
        print("Creating documents table...")
        
        # Create rag_documents table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS rag_documents (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                title VARCHAR(500) NOT NULL,
                document_type VARCHAR(50) NOT NULL,
                file_path VARCHAR(1000),
                file_size INTEGER,
                content_hash VARCHAR(64),
                status VARCHAR(50) DEFAULT 'processing',
                chunk_count INTEGER DEFAULT 0,
                metadata JSONB DEFAULT '{}'::jsonb,
                created_by UUID,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                indexed_at TIMESTAMP
            )
        """)
        print("✅ Created rag_documents table")
        
        # Create indexes
        try:
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_rag_documents_type 
                ON rag_documents(document_type)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_rag_documents_status 
                ON rag_documents(status)
            """)
            print("✅ Created indexes")
        except Exception as e:
            print(f"⚠️ Index creation skipped: {e}")
        
        # Count documents
        count = await conn.fetchval("SELECT COUNT(*) FROM rag_documents")
        print(f"✅ Total documents in database: {count}")
        
        print("\n🎉 Documents table initialization complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(init_documents())
