"""User Preferences API endpoints."""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import json

from app.core.auth.user_preferences_model import user_preferences_db
from app.core.auth.user_model import user_db

router = APIRouter(prefix="/preferences", tags=["Preferences"])


# Root handler - redirect to /me or return default preferences
@router.get("/")
async def get_preferences_root(request: Request):
    """Get preferences (root endpoint)."""
    user = await get_current_user(request)
    if not user:
        # Return default preferences for unauthenticated users
        return {
            "id": "default",
            "user_id": "guest",
            "preferred_colors": ["blue", "black", "white"],
            "preferred_fabrics": ["cotton", "silk"],
            "preferred_styles": ["casual", "modern"],
            "preferred_occasions": ["work", "casual outing"],
            "body_type": None,
            "fit_preference": None,
            "size_preference": None,
            "budget_min": None,
            "budget_max": None,
            "budget_currency": "USD",
            "language_preference": "en",
            "notification_preferences": {},
            "preferred_brands": [],
            "avoid_colors": [],
            "avoid_fabrics": [],
            "interaction_count": 0,
            "preference_confidence": 0.0,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    
    await user_db.initialize()
    prefs = await user_preferences_db.get_preferences(user.id)
    if not prefs:
        prefs_id = await user_preferences_db.create_preferences(user.id)
        prefs = await user_preferences_db.get_preferences(user.id)
    
    if not prefs:
        return {
            "id": "default",
            "user_id": user.id,
            "preferred_colors": [],
            "preferred_fabrics": [],
            "preferred_styles": [],
            "preferred_occasions": [],
            "body_type": None,
            "fit_preference": None,
            "size_preference": None,
            "budget_min": None,
            "budget_max": None,
            "budget_currency": "USD",
            "language_preference": "en",
            "notification_preferences": {},
            "preferred_brands": [],
            "avoid_colors": [],
            "avoid_fabrics": [],
            "interaction_count": 0,
            "preference_confidence": 0.0,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    
    return convert_prefs_for_response(prefs)


# Pydantic Models
class PreferencesUpdate(BaseModel):
    """User preferences update request."""
    preferred_colors: Optional[List[str]] = Field(default=None, max_length=20)
    preferred_fabrics: Optional[List[str]] = Field(default=None, max_length=20)
    preferred_styles: Optional[List[str]] = Field(default=None, max_length=20)
    preferred_occasions: Optional[List[str]] = Field(default=None, max_length=20)
    body_type: Optional[str] = Field(default=None, max_length=50)
    fit_preference: Optional[str] = Field(default=None, max_length=50)
    size_preference: Optional[str] = Field(default=None, max_length=10)
    budget_min: Optional[float] = Field(default=None, ge=0)
    budget_max: Optional[float] = Field(default=None, ge=0)
    budget_currency: Optional[str] = Field(default=None, max_length=3, min_length=3)
    language_preference: Optional[str] = Field(default=None, max_length=10)
    preferred_brands: Optional[List[str]] = Field(default=None, max_length=20)
    avoid_colors: Optional[List[str]] = Field(default=None, max_length=20)
    avoid_fabrics: Optional[List[str]] = Field(default=None, max_length=20)
    notification_preferences: Optional[Dict[str, Any]] = None


class PreferencesResponse(BaseModel):
    """User preferences response."""
    id: str
    user_id: str
    preferred_colors: List[str]
    preferred_fabrics: List[str]
    preferred_styles: List[str]
    preferred_occasions: List[str]
    body_type: Optional[str] = None
    fit_preference: Optional[str] = None
    size_preference: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    budget_currency: str
    language_preference: str
    notification_preferences: Dict[str, Any]
    preferred_brands: List[str]
    avoid_colors: List[str]
    avoid_fabrics: List[str]
    interaction_count: int
    preference_confidence: float
    created_at: datetime
    updated_at: datetime


class RecommendationFiltersResponse(BaseModel):
    """Filters for product recommendations."""
    colors: Optional[List[str]] = None
    fabrics: Optional[List[str]] = None
    styles: Optional[List[str]] = None
    occasions: Optional[List[str]] = None
    brands: Optional[List[str]] = None
    exclude_colors: Optional[List[str]] = None
    exclude_fabrics: Optional[List[str]] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    body_type: Optional[str] = None
    fit: Optional[str] = None


def convert_prefs_for_response(prefs: Dict[str, Any]) -> Dict[str, Any]:
    """Convert database row to API response format."""
    # Convert UUIDs to strings
    if 'id' in prefs and isinstance(prefs['id'], uuid.UUID):
        prefs['id'] = str(prefs['id'])
    if 'user_id' in prefs and isinstance(prefs['user_id'], uuid.UUID):
        prefs['user_id'] = str(prefs['user_id'])
    
    # Convert arrays (handle None -> empty list)
    for field in ['preferred_colors', 'preferred_fabrics', 'preferred_styles', 
                  'preferred_occasions', 'preferred_brands', 'avoid_colors', 'avoid_fabrics']:
        if prefs.get(field) is None:
            prefs[field] = []
    
    # Convert Decimals to floats
    for field in ['budget_min', 'budget_max']:
        if prefs.get(field) is not None:
            prefs[field] = float(prefs[field])
    
    # Handle JSONB field (may come as string)
    if 'notification_preferences' in prefs:
        np = prefs['notification_preferences']
        if np is None:
            prefs['notification_preferences'] = {}
        elif isinstance(np, str):
            try:
                prefs['notification_preferences'] = json.loads(np)
            except:
                prefs['notification_preferences'] = {}
    
    return prefs


# Dependency to get current user
async def get_current_user(request: Request):
    """Extract user from JWT token in Authorization header."""
    from app.core.auth.jwt_handler import verify_token
    
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
    if not user_id:
        return None
    
    await user_db.initialize()
    user = await user_db.get_user_by_id(user_id)
    return user


# Available options constants
AVAILABLE_COLORS = [
    "red", "blue", "green", "yellow", "black", "white", "pink", 
    "purple", "orange", "brown", "gray", "navy", "beige", "burgundy",
    "teal", "mint", "coral", "gold", "silver"
]

AVAILABLE_FABRICS = [
    "cotton", "silk", "linen", "wool", "polyester", "rayon", 
    "chiffon", "velvet", "denim", "leather", "satin", "organza",
    "tulle", "jersey", "knit", "crepe", "georgette", "satin"
]

AVAILABLE_STYLES = [
    "casual", "formal", "bohemian", "vintage", "modern", "classic",
    "minimalist", "maximalist", "streetwear", "elegant", "romantic",
    "sporty", "business", "party", "beach"
]

AVAILABLE_OCCASIONS = [
    "work", "wedding", "party", "date night", "casual outing", 
    "formal event", "beach vacation", "holiday", "festive", 
    "workout", "home", "travel"
]

AVAILABLE_BODY_TYPES = [
    "hourglass", "pear", "apple", "rectangle", "inverted triangle",
    "petite", "tall", "plus size", "curvy"
]

AVAILABLE_FITS = [
    "loose", "regular", "slim", "fit", "oversized", "tailored"
]

AVAILABLE_SIZES = ["XS", "S", "M", "L", "XL", "XXL", "3XL"]


@router.get("/me", response_model=PreferencesResponse)
async def get_my_preferences(user = Depends(get_current_user)):
    """Get current user's preferences."""
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Initialize database
    await user_db.initialize()
    
    # Get or create preferences
    prefs = await user_preferences_db.get_preferences(user.id)
    
    if not prefs:
        # Create default preferences
        prefs_id = await user_preferences_db.create_preferences(user.id)
        prefs = await user_preferences_db.get_preferences(user.id)
    
    if not prefs:
        raise HTTPException(
            status_code=500,
            detail="Failed to load preferences"
        )
    
    # Convert for response
    prefs = convert_prefs_for_response(prefs)
    
    return PreferencesResponse(**prefs)


@router.get("/options")
async def get_preferences_options():
    """Get available options for preferences."""
    return {
        "colors": AVAILABLE_COLORS,
        "fabrics": AVAILABLE_FABRICS,
        "styles": AVAILABLE_STYLES,
        "occasions": AVAILABLE_OCCASIONS,
        "body_types": AVAILABLE_BODY_TYPES,
        "fits": AVAILABLE_FITS,
        "sizes": AVAILABLE_SIZES
    }


@router.put("/me", response_model=PreferencesResponse)
async def update_my_preferences(
    update: PreferencesUpdate, 
    user = Depends(get_current_user)
):
    """Update current user's preferences."""
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Initialize database
    await user_db.initialize()
    
    # Get or create preferences
    prefs = await user_preferences_db.get_preferences(user.id)
    if not prefs:
        await user_preferences_db.create_preferences(user.id)
    
    # Update preferences
    updated = await user_preferences_db.update_preferences(
        user_id=user.id,
        preferred_colors=update.preferred_colors,
        preferred_fabrics=update.preferred_fabrics,
        preferred_styles=update.preferred_styles,
        preferred_occasions=update.preferred_occasions,
        body_type=update.body_type,
        fit_preference=update.fit_preference,
        size_preference=update.size_preference,
        budget_min=update.budget_min,
        budget_max=update.budget_max,
        budget_currency=update.budget_currency,
        language_preference=update.language_preference,
        preferred_brands=update.preferred_brands,
        avoid_colors=update.avoid_colors,
        avoid_fabrics=update.avoid_fabrics,
        notification_preferences=update.notification_preferences
    )
    
    if not updated:
        raise HTTPException(
            status_code=500,
            detail="Failed to update preferences"
        )
    
    # Convert for response
    updated = convert_prefs_for_response(updated)
    
    return PreferencesResponse(**updated)


@router.get("/recommendations", response_model=RecommendationFiltersResponse)
async def get_recommendation_filters(user = Depends(get_current_user)):
    """Get filters for product recommendations based on user preferences."""
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    filters = await user_preferences_db.get_recommendation_filters(user.id)
    return RecommendationFiltersResponse(**filters)


@router.delete("/me")
async def delete_preferences(user = Depends(get_current_user)):
    """Reset preferences to defaults."""
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    success = await user_preferences_db.delete_preferences(user.id)
    
    if success:
        # Recreate default preferences
        await user_preferences_db.create_preferences(user.id)
    
    return {"message": "Preferences reset to defaults", "success": True}


@router.post("/initialize")
async def initialize_preferences():
    """Initialize preferences table (admin endpoint)."""
    await user_preferences_db.initialize()
    return {"message": "Preferences table initialized", "success": True}
