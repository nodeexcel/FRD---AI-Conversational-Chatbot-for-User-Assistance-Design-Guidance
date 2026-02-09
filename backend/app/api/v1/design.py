"""
Design Session API Routes
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from ...core.auth.jwt_handler import get_current_user
from ...core.design.design_models import (
    DesignSessionCreate, DesignSessionUpdate, DesignSessionResponse,
    DesignStepInput, DesignFeedbackCreate, DesignFeedbackResponse,
    DesignSummaryResponse, DesignStep, DesignStatus
)
from ...core.design.design_crud import DesignCRUD, DesignFeedbackCRUD

router = APIRouter(prefix="/design", tags=["Design"])

# Design types options
DESIGN_TYPES = [
    {"value": "dress", "label": "Dress", "icon": "👗"},
    {"value": "tops", "label": "Tops", "icon": "👚"},
    {"value": "pants", "label": "Pants", "icon": "👖"},
    {"value": "jacket", "label": "Jacket", "icon": "🧥"},
    {"value": "skirt", "label": "Skirt", "icon": "🎀"},
    {"value": "saree", "label": "Saree", "icon": "🥻"},
    {"value": "lehenga", "label": "Lehenga", "icon": "💃"},
    {"value": "suit", "label": "Suit", "icon": "👔"},
    {"value": "other", "label": "Other", "icon": "✨"},
]

# Steps configuration with descriptions
DESIGN_STEPS = [
    {
        "id": "concept",
        "title": "Concept",
        "description": "Define your design vision and inspiration",
        "questions": [
            "What's the occasion or purpose for this design?",
            "Do you have any specific style preferences (casual, formal, party)?",
            "Any color preferences or palette in mind?",
            "Any inspiration images or references?"
        ]
    },
    {
        "id": "measurements",
        "title": "Measurements",
        "description": "Provide body measurements or sizing details",
        "questions": [
            "What size would you like to create?",
            "Do you have specific body measurements?",
            "Preferred fit (tight, regular, loose)?",
            "Any specific length requirements?"
        ]
    },
    {
        "id": "fabric",
        "title": "Fabric Selection",
        "description": "Choose materials and textures",
        "questions": [
            "What type of fabric are you considering?",
            "Do you prefer natural or synthetic materials?",
            "Any specific color or pattern requirements?",
            "What's your budget for fabric?"
        ]
    },
    {
        "id": "style",
        "title": "Style Details",
        "description": "Refine the style elements",
        "questions": [
            "What neckline style do you prefer?",
            "Sleeve type preference ( sleeveless, short, long)?",
            "Any specific embellishments or decorations?",
            "Preferred silhouette or cut?"
        ]
    },
    {
        "id": "details",
        "title": "Finishing Details",
        "description": "Add final touches and special requirements",
        "questions": [
            "Any specific stitching or finishing requirements?",
            "Button, zipper, or closure preferences?",
            "Lining requirements?",
            "Any additional features or customizations?"
        ]
    },
    {
        "id": "review",
        "title": "Review & Submit",
        "description": "Review your design and submit for creation",
        "questions": [
            "Review all your choices above",
            "Any final modifications needed?",
            "Ready to submit for AI suggestions?"
        ]
    },
]

def convert_session_response(session: dict) -> DesignSessionResponse:
    """Convert database session to API response."""
    # Handle JSONB fields that may come as strings from PostgreSQL
    ai_suggestions = session.get('ai_suggestions')
    user_inputs = session.get('user_inputs')
    
    # Convert string to dict if needed
    if isinstance(ai_suggestions, str):
        import json
        try:
            ai_suggestions = json.loads(ai_suggestions)
        except:
            ai_suggestions = {}
    
    if isinstance(user_inputs, str):
        import json
        try:
            user_inputs = json.loads(user_inputs)
        except:
            user_inputs = {}
    
    return DesignSessionResponse(
        id=str(session['id']),
        name=session['name'],
        description=session.get('description'),
        design_type=session['design_type'],
        current_step=DesignStep(session['current_step']),
        status=DesignStatus(session['status']),
        progress=session.get('progress', 0),
        ai_suggestions=ai_suggestions,
        user_inputs=user_inputs,
        created_by=str(session.get('created_by')) if session.get('created_by') else None,
        created_at=session['created_at'],
        updated_at=session['updated_at'],
        completed_at=session.get('completed_at'),
    )

@router.get("/types", response_model=dict)
async def get_design_types():
    """Get available design types."""
    return {"types": DESIGN_TYPES}

@router.get("/steps", response_model=list)
async def get_design_steps():
    """Get all design workflow steps."""
    return DESIGN_STEPS

@router.post("/sessions", response_model=DesignSessionResponse)
async def create_design_session(
    data: DesignSessionCreate,
    current_user = Depends(get_current_user)
):
    """Create a new design session."""
    session = await DesignCRUD.create(
        name=data.name,
        description=data.description,
        design_type=data.design_type,
        user_id=current_user["id"]
    )
    return convert_session_response(session)

@router.get("/sessions", response_model=list)
async def list_design_sessions(
    status: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """List all design sessions for current user."""
    sessions = await DesignCRUD.get_all(
        user_id=current_user["id"],
        status=status
    )
    return [convert_session_response(s) for s in sessions]

@router.get("/sessions/{session_id}", response_model=DesignSessionResponse)
async def get_design_session(session_id: str):
    """Get a specific design session."""
    session = await DesignCRUD.get_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Design session not found")
    return convert_session_response(session)

@router.put("/sessions/{session_id}", response_model=DesignSessionResponse)
async def update_design_session(
    session_id: str,
    data: DesignSessionUpdate,
    current_user = Depends(get_current_user)
):
    """Update a design session."""
    session = await DesignCRUD.get_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Design session not found")
    
    update_data = {}
    if data.name is not None:
        update_data['name'] = data.name
    if data.description is not None:
        update_data['description'] = data.description
    if data.current_step is not None:
        update_data['current_step'] = data.current_step.value
    if data.status is not None:
        update_data['status'] = data.status.value
    if data.ai_suggestions is not None:
        update_data['ai_suggestions'] = data.ai_suggestions
    
    updated = await DesignCRUD.update(session_id, **update_data)
    return convert_session_response(updated)

@router.post("/sessions/{session_id}/step", response_model=DesignSessionResponse)
async def submit_design_step(
    session_id: str,
    data: DesignStepInput,
    current_user = Depends(get_current_user)
):
    """Submit data for a specific design step."""
    session = await DesignCRUD.get_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Design session not found")
    
    updated = await DesignCRUD.update_step(session_id, data.step.value, data.data)
    if not updated:
        raise HTTPException(status_code=400, detail="Failed to update step")
    
    return convert_session_response(updated)

@router.post("/sessions/{session_id}/complete", response_model=DesignSessionResponse)
async def complete_design_session(session_id: str):
    """Mark a design session as completed."""
    session = await DesignCRUD.get_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Design session not found")
    
    completed = await DesignCRUD.complete(session_id)
    if not completed:
        raise HTTPException(status_code=400, detail="Failed to complete session")
    
    return convert_session_response(completed)

@router.delete("/sessions/{session_id}")
async def delete_design_session(session_id: str):
    """Delete a design session."""
    deleted = await DesignCRUD.delete(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Design session not found")
    return {"message": "Design session deleted successfully"}

@router.get("/sessions/{session_id}/summary", response_model=DesignSummaryResponse)
async def get_design_summary(session_id: str):
    """Get a summary of the design session."""
    session = await DesignCRUD.get_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Design session not found")
    
    # Get feedback status
    feedback = await DesignFeedbackCRUD.get_by_session_id(session_id)
    
    steps_order = ['concept', 'measurements', 'fabric', 'style', 'details', 'review']
    completed_steps = [s for s in steps_order if s in (session.get('user_inputs', {}) or {})]
    
    return DesignSummaryResponse(
        session_id=session_id,
        name=session['name'],
        design_type=session['design_type'],
        total_steps=len(steps_order),
        completed_steps=completed_steps,
        progress=session.get('progress', 0),
        final_design=session.get('user_inputs'),
        next_step=steps_order[len(completed_steps)] if len(completed_steps) < len(steps_order) else None,
        feedback_submitted=feedback is not None
    )

# Feedback endpoints
@router.post("/sessions/{session_id}/feedback", response_model=DesignFeedbackResponse)
async def submit_feedback(
    session_id: str,
    data: DesignFeedbackCreate,
    current_user = Depends(get_current_user)
):
    """Submit feedback for a design session."""
    session = await DesignCRUD.get_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Design session not found")
    
    # Check if feedback already exists
    existing = await DesignFeedbackCRUD.get_by_session_id(session_id)
    if existing:
        raise HTTPException(status_code=400, detail="Feedback already submitted for this session")
    
    feedback = await DesignFeedbackCRUD.create(
        design_session_id=session_id,
        user_id=current_user["id"],
        rating=data.rating,
        comment=data.comment,
        what_liked=data.what_liked,
        what_to_improve=data.what_to_improve
    )
    
    return DesignFeedbackResponse(
        id=str(feedback['id']),
        design_session_id=str(feedback['design_session_id']),
        rating=feedback['rating'],
        comment=feedback.get('comment'),
        what_liked=feedback.get('what_liked'),
        what_to_improve=feedback.get('what_to_improve'),
        created_by=str(feedback.get('created_by')) if feedback.get('created_by') else None,
        created_at=feedback['created_at'],
    )

@router.get("/sessions/{session_id}/feedback")
async def get_feedback(session_id: str):
    """Get feedback for a design session."""
    feedback = await DesignFeedbackCRUD.get_by_session_id(session_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    return DesignFeedbackResponse(
        id=str(feedback['id']),
        design_session_id=str(feedback['design_session_id']),
        rating=feedback['rating'],
        comment=feedback.get('comment'),
        what_liked=feedback.get('what_liked'),
        what_to_improve=feedback.get('what_to_improve'),
        created_by=str(feedback.get('created_by')) if feedback.get('created_by') else None,
        created_at=feedback['created_at'],
    )
