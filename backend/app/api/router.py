"""API router configuration."""
from fastapi import APIRouter

from app.api.v1 import chat, design, feedback, knowledge, sql, auth, preferences, documents, analytics, voice

api_router = APIRouter()

# Include API version routers
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(design.router, tags=["Design"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["Knowledge"])
api_router.include_router(sql.router, prefix="/database", tags=["Database"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(preferences.router, tags=["Preferences"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

# Voice router
api_router.include_router(voice.router, prefix="/voice", tags=["Voice"])

# Translation router (lazy loading to avoid circular imports)
try:
    from app.api.v1 import translation
    api_router.include_router(translation.router, prefix="/translate", tags=["Translation"])
except Exception as e:
    print(f"Warning: Could not load translation router: {e}")
