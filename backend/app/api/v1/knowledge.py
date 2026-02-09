"""Knowledge base API endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

from app.agents.knowledge.rag_agent import knowledge_agent

logger = logging.getLogger(__name__)

router = APIRouter()


class KnowledgeQuery(BaseModel):
    """Knowledge base query model."""
    question: str
    entities: Optional[List[Dict[str, str]]] = None
    num_results: int = 5


class AddDocumentsRequest(BaseModel):
    """Add documents request model."""
    documents: List[Dict[str, str]]


class SearchRequest(BaseModel):
    """Search request model."""
    query: str
    num_results: int = 10


@router.post("/query")
async def query_knowledge_base(request: KnowledgeQuery):
    """Query the knowledge base with RAG."""
    try:
        result = await knowledge_agent.query(
            question=request.question,
            entities=request.entities,
            num_results=request.num_results
        )
        return result
    except Exception as e:
        logger.error(f"Knowledge query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_knowledge_base(request: SearchRequest):
    """Search the knowledge base."""
    try:
        results = await knowledge_agent.search(
            query=request.query,
            num_results=request.num_results
        )
        return {
            "query": request.query,
            "results": results,
            "total_count": len(results)
        }
    except Exception as e:
        logger.error(f"Knowledge search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents")
async def add_documents(request: AddDocumentsRequest):
    """Add documents to the knowledge base."""
    try:
        await knowledge_agent.add_documents(request.documents)
        return {
            "status": "success",
            "message": f"Added {len(request.documents)} documents"
        }
    except Exception as e:
        logger.error(f"Add documents error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from the knowledge base."""
    try:
        await knowledge_agent.delete_documents([document_id])
        return {
            "status": "success",
            "message": f"Deleted document {document_id}"
        }
    except Exception as e:
        logger.error(f"Delete document error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def knowledge_health_check():
    """Check knowledge base health."""
    health = knowledge_agent.health_check()
    return health


@router.get("/stats")
async def get_knowledge_stats():
    """Get knowledge base statistics."""
    health = knowledge_agent.health_check()
    return {
        "status": health.get("status"),
        "total_documents": health.get("documents_count"),
        "categories": [
            "evening_gown", "summer_dress", "cocktail_dress", "saree",
            "maxi_dress", "kurti", "party_dress", "shift_dress",
            "anarkali", "summer_suit", "size_guide", "care_guide",
            "style_guide", "policy"
        ]
    }
