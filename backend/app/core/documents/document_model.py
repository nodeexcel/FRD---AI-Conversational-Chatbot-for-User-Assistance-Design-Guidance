"""Document Model for RAG Knowledge Base."""
import asyncpg
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.config import settings


class DocumentModel:
    """Database model for RAG documents."""
    
    def __init__(self):
        self.table_name = "rag_documents"
    
    async def get_connection(self):
        """Get database connection."""
        return await asyncpg.connect(settings.postgres.url)
    
    async def initialize(self):
        """Initialize the documents table."""
        conn = await self.get_connection()
        try:
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    title VARCHAR(500) NOT NULL,
                    document_type VARCHAR(50) NOT NULL, -- faq, manual, guide, process_map, policy
                    file_path VARCHAR(1000),
                    file_size INTEGER,
                    content_hash VARCHAR(64),
                    status VARCHAR(50) DEFAULT 'processing', -- processing, indexed, failed
                    chunk_count INTEGER DEFAULT 0,
                    metadata JSONB DEFAULT '{{}}'::jsonb,
                    created_by UUID,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    indexed_at TIMESTAMP
                )
            """)
            
            # Create index
            try:
                await conn.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_{self.table_name}_type 
                    ON {self.table_name}(document_type)
                """)
                await conn.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_{self.table_name}_status 
                    ON {self.table_name}(status)
                """)
            except Exception:
                pass
                
        finally:
            await conn.close()
    
    async def create_document(
        self,
        title: str,
        document_type: str,
        file_path: Optional[str] = None,
        file_size: Optional[int] = None,
        content_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None
    ) -> str:
        """Create a new document record."""
        conn = await self.get_connection()
        try:
            # Convert metadata dict to JSON string
            metadata_value = json.dumps(metadata) if metadata is not None else None
            
            result = await conn.fetchval(
                f"""
                INSERT INTO {self.table_name} 
                (title, document_type, file_path, file_size, content_hash, metadata, created_by)
                VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7)
                RETURNING id
                """,
                title, document_type, file_path, file_size, content_hash, 
                metadata_value,
                created_by
            )
            return str(result)
        finally:
            await conn.close()
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        conn = await self.get_connection()
        try:
            row = await conn.fetchrow(
                f"SELECT * FROM {self.table_name} WHERE id = $1",
                document_id
            )
            return dict(row) if row else None
        finally:
            await conn.close()
    
    async def get_all_documents(
        self, 
        document_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get all documents with optional filters."""
        conn = await self.get_connection()
        try:
            query = f"SELECT * FROM {self.table_name} WHERE 1=1"
            params = []
            param_count = 0
            
            if document_type:
                param_count += 1
                query += f" AND document_type = ${param_count}"
                params.append(document_type)
            
            if status:
                param_count += 1
                query += f" AND status = ${param_count}"
                params.append(status)
            
            query += f" ORDER BY created_at DESC LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
            params.extend([limit, offset])
            
            rows = await conn.fetch(query, *params)
            # Convert UUID fields to strings for Pydantic validation
            result = []
            for row in rows:
                row_dict = dict(row)
                # Convert UUID to string
                if 'id' in row_dict and row_dict['id']:
                    row_dict['id'] = str(row_dict['id'])
                # Convert datetime to ISO format strings
                for key in ['created_at', 'updated_at', 'indexed_at']:
                    if key in row_dict and row_dict[key]:
                        row_dict[key] = row_dict[key].isoformat()
                result.append(row_dict)
            return result
        finally:
            await conn.close()
    
    async def update_document(
        self,
        document_id: str,
        status: Optional[str] = None,
        chunk_count: Optional[int] = None,
        indexed_at: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """Update a document."""
        conn = await self.get_connection()
        try:
            updates = []
            values = []
            param_count = 0
            
            if status:
                param_count += 1
                updates.append(f"status = ${param_count}")
                values.append(status)
            
            if chunk_count is not None:
                param_count += 1
                updates.append(f"chunk_count = ${param_count}")
                values.append(chunk_count)
            
            if indexed_at:
                param_count += 1
                updates.append(f"indexed_at = ${param_count}")
                values.append(indexed_at)
            
            if not updates:
                return await self.get_document(document_id)
            
            param_count += 1
            updates.append(f"updated_at = CURRENT_TIMESTAMP")
            values.append(document_id)
            
            query = f"""
                UPDATE {self.table_name}
                SET {', '.join(updates)}
                WHERE id = ${param_count}
                RETURNING *
            """
            
            row = await conn.fetchrow(query, *values)
            return dict(row) if row else None
        finally:
            await conn.close()
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document."""
        conn = await self.get_connection()
        try:
            result = await conn.execute(
                f"DELETE FROM {self.table_name} WHERE id = $1",
                document_id
            )
            return result != "DELETE 0"
        finally:
            await conn.close()
    
    async def get_indexed_documents(self) -> List[Dict[str, Any]]:
        """Get all successfully indexed documents."""
        return await self.get_all_documents(status='indexed')
    
    async def get_document_count(self, document_type: Optional[str] = None) -> int:
        """Get document count."""
        conn = await self.get_connection()
        try:
            query = f"SELECT COUNT(*) FROM {self.table_name} WHERE status = 'indexed'"
            params = []
            
            if document_type:
                query += " AND document_type = $1"
                params.append(document_type)
            
            return await conn.fetchval(query, *params)
        finally:
            await conn.close()


# Singleton instance
document_db = DocumentModel()
