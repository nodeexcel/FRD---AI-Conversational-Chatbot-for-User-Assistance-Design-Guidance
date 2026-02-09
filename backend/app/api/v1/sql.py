"""SQL Database API endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

from app.agents.sql.text2sql_agent import sql_agent

logger = logging.getLogger(__name__)

router = APIRouter()


class SQLQuery(BaseModel):
    """Natural language SQL query."""
    query: str
    entities: Optional[List[Dict[str, str]]] = None
    user_id: Optional[str] = None


class ProductFilter(BaseModel):
    """Product filter model."""
    category: Optional[str] = None
    color: Optional[str] = None
    fabric: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    occasion: Optional[str] = None
    limit: int = 10


@router.post("/query")
async def execute_natural_language_query(request: SQLQuery):
    """Execute a natural language query against the database."""
    try:
        result = await sql_agent.execute(
            natural_query=request.query,
            entities=request.entities,
            user_id=request.user_id
        )
        
        if "error" in result:
            return {
                "status": "error",
                "message": result["error"],
                "sql_query": result.get("sql_query"),
                "results": []
            }
        
        return {
            "status": "success",
            "sql_query": result["sql_query"],
            "results": result["results"],
            "columns": result["columns"],
            "row_count": result["row_count"],
            "intent": result["intent"]
        }
        
    except Exception as e:
        logger.error(f"SQL query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/products")
async def get_products(filter: ProductFilter):
    """Get products with filters from database."""
    try:
        result = await sql_agent.get_products(
            category=filter.category,
            color=filter.color,
            fabric=filter.fabric,
            min_price=filter.min_price,
            max_price=filter.max_price,
            occasion=filter.occasion,
            limit=filter.limit
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "status": "success",
            "products": result["results"],
            "row_count": result["row_count"]
        }
        
    except Exception as e:
        logger.error(f"Get products error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products/count")
async def get_product_count(category: Optional[str] = None):
    """Get total product count."""
    try:
        count = await sql_agent.get_product_count(category)
        return {
            "status": "success",
            "count": count,
            "category": category
        }
    except Exception as e:
        logger.error(f"Get count error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/inventory")
async def get_inventory_status():
    """Get inventory status summary."""
    try:
        result = await sql_agent.get_inventory_status()
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "status": "success",
            "inventory": result
        }
        
    except Exception as e:
        logger.error(f"Inventory status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def sql_health_check():
    """Check SQL agent health."""
    health = sql_agent.health_check()
    return health


@router.get("/schema")
async def get_database_schema():
    """Get database schema information."""
    if not sql_agent._initialized:
        await sql_agent.initialize()
    
    return {
        "status": "success",
        "schema": sql_agent.schema_info
    }
