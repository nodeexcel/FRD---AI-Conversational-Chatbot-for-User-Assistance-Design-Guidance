"""
Design Session Models for Guided Design Flow
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class DesignStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    COMPLETED = "completed"
    APPROVED = "approved"

class DesignStep(str, Enum):
    CONCEPT = "concept"
    MEASUREMENTS = "measurements"
    FABRIC = "fabric"
    STYLE = "style"
    DETAILS = "details"
    REVIEW = "review"

# Design Session Schema
class DesignSessionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    design_type: str = Field(..., description="Type of design (dress, shirt, pants, etc.)")

class DesignSessionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    current_step: Optional[DesignStep] = None
    status: Optional[DesignStatus] = None
    ai_suggestions: Optional[Dict[str, Any]] = None

class DesignSessionResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    design_type: str
    current_step: DesignStep
    status: DesignStatus
    progress: int = Field(..., description="Progress percentage (0-100)")
    ai_suggestions: Optional[Dict[str, Any]] = None
    user_inputs: Optional[Dict[str, Any]] = None
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

# Design Step Input Schema
class DesignStepInput(BaseModel):
    step: DesignStep
    data: Dict[str, Any]
    save_suggestions: bool = True

# Design Feedback Schema
class DesignFeedbackCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    what_liked: Optional[str] = None
    what_to_improve: Optional[str] = None

class DesignFeedbackResponse(BaseModel):
    id: str
    design_session_id: str
    rating: int
    comment: Optional[str]
    what_liked: Optional[str]
    what_to_improve: Optional[str]
    created_by: Optional[str]
    created_at: datetime

# Design Summary Schema
class DesignSummaryResponse(BaseModel):
    session_id: str
    name: str
    design_type: str
    total_steps: int
    completed_steps: List[str]
    progress: int
    final_design: Optional[Dict[str, Any]]
    next_step: Optional[str]
    feedback_submitted: bool
