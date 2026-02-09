"""Documents API for RAG Knowledge Base."""
import os
import uuid
import hashlib
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, status, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

from app.core.documents.document_model import document_db
from app.core.documents.document_processor import document_processor
from app.agents.knowledge.vector_store import vector_store

router = APIRouter()

# Configuration
UPLOAD_DIR = "./data/documents"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.md', '.html', '.csv'}

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Pydantic Models
class DocumentCreate(BaseModel):
    """Create document from text content."""
    title: str = Field(..., min_length=1, max_length=500)
    document_type: str = Field(..., description="faq, manual, guide, process_map, policy")
    content: str
    metadata: Optional[Dict[str, Any]] = None


class DocumentResponse(BaseModel):
    """Document response model."""
    id: str
    title: str
    document_type: str
    file_path: Optional[str]
    file_size: Optional[int]
    status: str
    chunk_count: int
    created_at: datetime
    updated_at: datetime
    indexed_at: Optional[datetime]


class DocumentListResponse(BaseModel):
    """List documents response."""
    documents: List[DocumentResponse]
    total: int


class DocumentUploadResponse(BaseModel):
    """Document upload response."""
    id: str
    title: str
    document_type: str
    chunk_count: int
    status: str
    message: str


class ChunkResponse(BaseModel):
    """Document chunk response."""
    document_id: str
    chunk_index: int
    content: str


# Document types
DOCUMENT_TYPES = [
    "faq",
    "manual", 
    "guide",
    "process_map",
    "policy",
    "product_guide",
    "training_material",
    "other"
]


async def get_current_user(request):
    """Extract user from JWT token."""
    from app.core.auth.jwt_handler import verify_token
    from app.core.auth.user_model import user_db
    
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        return None
    
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
    else:
        token = auth_header
    
    payload = verify_token(token)
    if not payload:
        return None
    
    user_id = payload.get("sub")
    return user_id


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    title: str = Form(...),
    document_type: str = Form(...)
):
    """
    Upload a document file for RAG knowledge base.
    
    Supports: PDF, DOCX, TXT, MD, HTML, CSV
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Validate document type
    if document_type not in DOCUMENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document_type. Must be one of: {DOCUMENT_TYPES}"
        )
    
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format. Must be one of: {list(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    content = await file.read()
    
    # Check file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    safe_filename = f"{file_id}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    document_id = None
    
    try:
        # Save file
        with open(file_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"Saved file to {file_path}")
        
        # Create document record
        document_id = await document_db.create_document(
            title=title,
            document_type=document_type,
            file_path=file_path,
            file_size=len(content),
            created_by=None  # Can be set from auth
        )
        
        logger.info(f"Created document record: {document_id}")
        
        # Process document
        result = await document_processor.process_document(
            file_path=file_path,
            document_id=document_id,
            document_type=document_type
        )
        
        if result['success']:
            # Index chunks into ChromaDB
            try:
                logger.info(f"[DOC] Indexing {result['chunk_count']} chunks into ChromaDB...")
                
                # Create Document objects for each chunk
                from app.agents.knowledge.vector_store import Document
                chroma_documents = []
                for chunk in result['chunks']:
                    chroma_doc = Document(
                        id=f"{document_id}_chunk_{chunk['chunk_index']}",
                        content=chunk['content'],
                        metadata={
                            "document_id": document_id,
                            "document_type": document_type,
                            "chunk_index": chunk['chunk_index'],
                            "title": title
                        }
                    )
                    chroma_documents.append(chroma_doc)
                
                # Add to ChromaDB
                await vector_store.add_documents(chroma_documents)
                logger.info(f"[DOC] Successfully indexed {len(chroma_documents)} chunks into ChromaDB")
                
            except Exception as chroma_error:
                logger.error(f"[DOC] Failed to index to ChromaDB: {chroma_error}")
                # Continue anyway - document is still stored in PostgreSQL
            
            # Update document with chunk count
            await document_db.update_document(
                document_id=document_id,
                status='indexed',
                chunk_count=result['chunk_count'],
                indexed_at=datetime.utcnow()
            )
            
            message = f"Document indexed successfully with {result['chunk_count']} chunks"
        else:
            # Mark as failed
            if document_id:
                await document_db.update_document(
                    document_id=document_id,
                    status='failed'
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result['error']
            )
        
        return DocumentUploadResponse(
            id=document_id,
            title=title,
            document_type=document_type,
            chunk_count=result['chunk_count'],
            status='indexed',
            message=message
        )
        
    except Exception as e:
        logger.error(f"Document upload error: {e}")
        # Clean up file on error
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )


@router.post("/create", response_model=DocumentResponse)
async def create_document(
    request: Request,
    doc: DocumentCreate
):
    """Create a document from text content."""
    # Create document record
    document_id = await document_db.create_document(
        title=doc.title,
        document_type=doc.document_type,
        created_by=None
    )
    
    # Process content
    result = await document_processor.process_text_content(
        content=doc.content,
        document_id=document_id,
        document_type=doc.document_type,
        title=doc.title
    )
    
    if result['success']:
        await document_db.update_document(
            document_id=document_id,
            status='indexed',
            chunk_count=result['chunk_count'],
            indexed_at=datetime.utcnow()
        )
    else:
        await document_db.update_document(
            document_id=document_id,
            status='failed'
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result['error']
        )
    
    # Get updated document
    doc_data = await document_db.get_document(document_id)
    return DocumentResponse(**doc_data)


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    document_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """List all documents in the knowledge base."""
    documents = await document_db.get_all_documents(
        document_type=document_type,
        status=status,
        limit=limit,
        offset=offset
    )
    
    total = await document_db.get_document_count(document_type)
    
    return DocumentListResponse(
        documents=[DocumentResponse(**doc) for doc in documents],
        total=total
    )


@router.get("/types")
async def get_document_types():
    """Get list of supported document types."""
    return {
        "types": DOCUMENT_TYPES,
        "descriptions": {
            "faq": "Frequently Asked Questions",
            "manual": "Product/Service Manuals",
            "guide": "How-to Guides",
            "process_map": "Process Documentation",
            "policy": "Company Policies",
            "product_guide": "Product Specifications",
            "training_material": "Training Content",
            "other": "Other Documents"
        }
    }


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    """Get document details by ID."""
    doc = await document_db.get_document(document_id)
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return DocumentResponse(**doc)


@router.get("/{document_id}/chunks")
async def get_document_chunks(document_id: str):
    """Get chunks for a document (for debugging/verification)."""
    doc = await document_db.get_document(document_id)
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # This would typically query the vector store
    # For now, return document info
    return {
        "document_id": document_id,
        "title": doc['title'],
        "chunk_count": doc['chunk_count'],
        "status": doc['status'],
        "message": "Chunks are stored in vector database. Use RAG retrieval to access."
    }


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from the knowledge base."""
    doc = await document_db.get_document(document_id)
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete file if exists
    if doc.get('file_path') and os.path.exists(doc['file_path']):
        os.remove(doc['file_path'])
    
    # Delete from database
    await document_db.delete_document(document_id)
    
    return {"message": "Document deleted successfully", "success": True}


@router.post("/initialize")
async def initialize_documents():
    """Initialize documents table (admin endpoint)."""
    await document_db.initialize()
    return {"message": "Documents table initialized", "success": True}


@router.get("/stats")
async def get_document_stats():
    """Get statistics about the knowledge base."""
    total = await document_db.get_document_count()
    indexed = await document_db.get_document_count(status='indexed')
    
    # Get count by type
    type_counts = {}
    for doc_type in DOCUMENT_TYPES:
        count = await document_db.get_document_count(document_type=doc_type)
        type_counts[doc_type] = count
    
    return {
        "total_documents": total,
        "indexed_documents": indexed,
        "by_type": type_counts,
        "supported_formats": list(ALLOWED_EXTENSIONS),
        "chunk_size": document_processor.chunk_size
    }
