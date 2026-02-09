"""FastAPI application for AI Chatbot."""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path

# Load environment variables from .env file FIRST, before any other imports
# This ensures environment variables are available when config is loaded
dotenv_path = Path(__file__).parent.parent / ".env"
from dotenv import load_dotenv
load_dotenv(dotenv_path=dotenv_path)

from app.config import settings
from app.api.router import api_router
from app.api.websocket import router as ws_router

# Configure logging
log_level = getattr(logging, settings.logging.level, logging.INFO)
logging.basicConfig(
    level=log_level,
    format=settings.logging.format
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting AI Chatbot Application...")
    logger.info(f"Environment: {settings.app.environment}")
    logger.info(f"OpenAI API Key: {'Set' if settings.openai_api_key else 'NOT SET'}")
    
    # Initialize document database table
    try:
        from app.core.documents.document_model import document_db
        await document_db.initialize()
        logger.info("Document database initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize document database: {e}")
    
    # Initialize ChromaDB vector store
    try:
        from app.agents.knowledge.vector_store import vector_store
        await vector_store.initialize()
        logger.info("ChromaDB vector store initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize ChromaDB: {e}")
    
    yield
    # Shutdown
    logger.info("Shutting down AI Chatbot Application...")


# Create FastAPI application
app = FastAPI(
    title=settings.app.app_name,
    version=settings.app.version,
    lifespan=lifespan
)

# Add CORS middleware (allow all for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")

# Include voice router directly
from app.api.v1 import voice
app.include_router(voice.router, prefix="/api", tags=["Voice"])

# Include WebSocket router (at root level)
app.include_router(ws_router)


# CORS middleware handles OPTIONS preflight automatically
# No need for manual OPTIONS handler


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app.app_name,
        "version": settings.app.version,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app.version
    }


if __name__ == "__main__":
    # Run the application with uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
