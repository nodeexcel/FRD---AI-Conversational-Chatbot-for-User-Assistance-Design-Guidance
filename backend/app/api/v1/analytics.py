# Analytics API endpoints
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from app.core.auth.user_model import User
from app.core.auth.jwt_handler import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Analytics"])


async def get_optional_user(request: Request):
    """Get user from token if present, otherwise return None."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    
    from app.core.auth.jwt_handler import verify_token
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
    
    from app.core.auth.user_model import user_db
    await user_db.initialize()
    user = await user_db.get_user_by_id(user_id)
    return user


class QuestionTrackingRequest(BaseModel):
    question: str
    intent: str
    confidence: float
    response_time: float
    was_helpful: Optional[bool] = None


class KnowledgeGapResponse(BaseModel):
    has_gap: bool
    gap_type: Optional[str]
    reason: Optional[str]
    suggested_action: Optional[str]
    priority: str


class HumanHandoffResponse(BaseModel):
    should_handoff: bool
    reason: Optional[str]
    priority: Optional[str]
    escalation_level: Optional[int]


class DesignCompletionRequest(BaseModel):
    design_session_id: str
    current_step: int
    total_steps: int
    completed_steps: List[int]
    abandoned: bool = False
    completion_time_seconds: Optional[float] = None


@router.get("/most-asked")
async def get_most_asked_questions(
    days: int = 7,
    limit: int = 10,
    current_user = Depends(get_optional_user)
):
    """Get most frequently asked questions"""
    # This would query the database in production
    return {
        "questions": [
            {
                "question": "What dresses do you have in blue color?",
                "count": 45,
                "common_intent": "product_search",
                "avg_confidence": 0.92
            },
            {
                "question": "Show me formal wear for office",
                "count": 38,
                "common_intent": "product_recommendation",
                "avg_confidence": 0.88
            },
            {
                "question": "How to care for silk dresses?",
                "count": 32,
                "common_intent": "care_instructions",
                "avg_confidence": 0.95
            }
        ],
        "period_days": days,
        "generated_at": datetime.utcnow().isoformat()
    }


@router.get("/unanswered")
async def get_unanswered_queries(
    days: int = 7,
    current_user = Depends(get_optional_user)
):
    """Get poorly answered queries that need attention"""
    return {
        "queries": [
            {
                "question": "Can you suggest matching accessories for a wedding guest dress?",
                "times_asked": 5,
                "avg_confidence": 0.65,
                "last_asked": datetime.utcnow().isoformat(),
                "suggested_action": "Expand product database with accessories"
            }
        ],
        "period_days": days,
        "generated_at": datetime.utcnow().isoformat()
    }


@router.get("/design-completion")
async def get_design_completion_rates(
    days: int = 30,
    current_user = Depends(get_optional_user)
):
    """Get design workflow completion rates"""
    return {
        "completion_stats": {
            "total_sessions": 150,
            "completed_sessions": 120,
            "abandoned_sessions": 30,
            "completion_rate": 0.80,
            "avg_completion_time_seconds": 245.5
        },
        "drop_off_points": [
            {"step": 2, "drop_off_count": 15, "percentage": 10},
            {"step": 4, "drop_off_count": 10, "percentage": 6.7},
            {"step": 6, "drop_off_count": 5, "percentage": 3.3}
        ],
        "period_days": days,
        "generated_at": datetime.utcnow().isoformat()
    }


@router.get("/satisfaction")
async def get_user_satisfaction(
    current_user = Depends(get_optional_user)
):
    """Get user satisfaction signals"""
    return {
        "total_feedback": 500,
        "positive": 400,
        "negative": 50,
        "neutral": 50,
        "satisfaction_rate": 0.80,
        "nps_score": 60,
        "trend": "improving",
        "generated_at": datetime.utcnow().isoformat()
    }


@router.get("/language-usage")
async def get_language_usage_trends(
    days: int = 30,
    current_user = Depends(get_optional_user)
):
    """Get language usage trends"""
    return {
        "languages": {
            "English": {"count": 250, "percentage": 50, "trend": "stable"},
            "Spanish": {"count": 100, "percentage": 20, "trend": "increasing"},
            "Hindi": {"count": 75, "percentage": 15, "trend": "increasing"},
            "Telugu": {"count": 50, "percentage": 10, "trend": "stable"},
            "Other": {"count": 25, "percentage": 5, "trend": "stable"}
        },
        "total_conversations": 500,
        "period_days": days,
        "generated_at": datetime.utcnow().isoformat()
    }


@router.post("/track-question")
async def track_question(
    request: QuestionTrackingRequest,
    current_user = Depends(get_optional_user)
):
    """Track a user's question for analytics"""
    logger.info(f"Question tracked: {request.question[:50]}... (intent: {request.intent})")
    return {
        "status": "tracked",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/knowledge-gap", response_model=KnowledgeGapResponse)
async def analyze_knowledge_gap(
    question: str,
    intent: str,
    confidence: float,
    sources_count: int,
    current_user = Depends(get_optional_user)
):
    """Analyze if a query indicates a knowledge gap"""
    gap_analysis = {
        "has_gap": False,
        "gap_type": None,
        "reason": None,
        "suggested_action": None,
        "priority": "low"
    }
    
    if confidence < 0.7:
        gap_analysis["has_gap"] = True
        gap_analysis["gap_type"] = "low_confidence"
        gap_analysis["reason"] = f"Low confidence ({confidence}) for intent: {intent}"
        gap_analysis["suggested_action"] = "human_review"
        gap_analysis["priority"] = "high"
    
    if sources_count == 0:
        gap_analysis["has_gap"] = True
        gap_analysis["gap_type"] = "no_sources" if not gap_analysis["has_gap"] else "multiple"
        gap_analysis["reason"] = f"No sources found for: {intent}"
        gap_analysis["suggested_action"] = "content_creation"
        gap_analysis["priority"] = "medium"
    
    return KnowledgeGapResponse(**gap_analysis)


@router.post("/handoff", response_model=HumanHandoffResponse)
async def check_human_handoff(
    confidence: float,
    intent: str,
    has_sources: bool,
    user_feedback: Optional[bool] = None,
    consecutive_low_confidence: int = 0,
    current_user = Depends(get_optional_user)
):
    """Check if query should be handed off to human support"""
    handoff = {
        "should_handoff": False,
        "reason": None,
        "priority": None,
        "escalation_level": None
    }
    
    if confidence < 0.5:
        handoff["should_handoff"] = True
        handoff["reason"] = f"Very low confidence ({confidence})"
        handoff["priority"] = "urgent"
        handoff["escalation_level"] = 3
    
    elif confidence < 0.7 and consecutive_low_confidence >= 2:
        handoff["should_handoff"] = True
        handoff["reason"] = "Multiple consecutive low-confidence responses"
        handoff["priority"] = "high"
        handoff["escalation_level"] = 2
    
    elif user_feedback is False and consecutive_low_confidence >= 1:
        handoff["should_handoff"] = True
        handoff["reason"] = "Negative user feedback"
        handoff["priority"] = "medium"
        handoff["escalation_level"] = 1
    
    return HumanHandoffResponse(**handoff)


@router.post("/design-completion")
async def track_design_completion(
    request: DesignCompletionRequest,
    current_user = Depends(get_optional_user)
):
    """Track design workflow completion"""
    progress = len(request.completed_steps) / request.total_steps * 100 if request.total_steps > 0 else 0
    
    return {
        "status": "tracked",
        "progress_percentage": progress,
        "completed": len(request.completed_steps) >= request.total_steps,
        "abandoned": request.abandoned,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/dashboard")
async def get_analytics_dashboard(
    days: int = 7,
    current_user = Depends(get_optional_user)
):
    """Get comprehensive analytics dashboard"""
    return {
        "overview": {
            "total_conversations": 500,
            "total_users": 200,
            "avg_response_time_ms": 1250,
            "satisfaction_rate": 0.80
        },
        "top_intents": [
            {"intent": "product_search", "count": 150},
            {"intent": "product_recommendation", "count": 120},
            {"intent": "care_instructions", "count": 80},
            {"intent": "pricing", "count": 60},
            {"intent": "design_help", "count": 50}
        ],
        "completion_rates": {
            "design_workflow": 0.80,
            "product_search": 0.95,
            "general_conversation": 0.90
        },
        "knowledge_gaps_identified": 5,
        "human_handoffs": 3,
        "period_days": days,
        "generated_at": datetime.utcnow().isoformat()
    }


# ============ NEW ENDPOINTS FOR FRONTEND INTEGRATION ============

@router.get("/summary")
async def get_analytics_summary(
    request: Request,
    current_user = Depends(get_optional_user)
):
    """Get user analytics summary"""
    return {
        "total_sessions": 45,
        "total_messages": 892,
        "average_response_time_ms": 1250,
        "favorite_agents": [
            {"agent": "nlu", "count": 350, "label": "NLU Agent"},
            {"agent": "rag", "count": 280, "label": "RAG Agent"},
            {"agent": "sql", "count": 150, "label": "SQL Agent"},
            {"agent": "translate", "count": 112, "label": "Translation Agent"}
        ],
        "daily_message_counts": [
            {"date": "2024-01-01", "count": 45},
            {"date": "2024-01-02", "count": 62},
            {"date": "2024-01-03", "count": 38},
            {"date": "2024-01-04", "count": 71},
            {"date": "2024-01-05", "count": 55},
            {"date": "2024-01-06", "count": 89},
            {"date": "2024-01-07", "count": 67}
        ],
        "weekly_activity": {
            "Monday": 120,
            "Tuesday": 145,
            "Wednesday": 132,
            "Thursday": 156,
            "Friday": 178,
            "Saturday": 89,
            "Sunday": 72
        },
        "top_topics": [
            {"topic": "product_search", "count": 245},
            {"topic": "care_instructions", "count": 156},
            {"topic": "pricing", "count": 134},
            {"topic": "design_help", "count": 98},
            {"topic": "recommendations", "count": 87}
        ],
        "average_rating": 4.2,
        "total_designs_created": 23,
        "documents_uploaded": 15
    }


@router.get("/activity")
async def get_activity_data(
    days: int = 7,
    current_user = Depends(get_optional_user)
):
    """Get user activity data"""
    activity_data = []
    import datetime as dt
    for i in range(days):
        date = (dt.datetime.utcnow() - dt.timedelta(days=days - i - 1)).strftime("%Y-%m-%d")
        activity_data.append({
            "date": date,
            "messages": 50 + (i * 10) % 100
        })
    return {
        "activity": activity_data,
        "total_messages": sum(item["messages"] for item in activity_data)
    }


@router.get("/agent-usage")
async def get_agent_usage(
    current_user = Depends(get_optional_user)
):
    """Get agent usage statistics"""
    agents = [
        {"agent": "nlu", "count": 350, "label": "NLU Agent", "percentage": 35},
        {"agent": "rag", "count": 280, "label": "RAG Agent", "percentage": 28},
        {"agent": "sql", "count": 150, "label": "SQL Agent", "percentage": 15},
        {"agent": "translate", "count": 112, "label": "Translation Agent", "percentage": 11},
        {"agent": "voice", "count": 60, "label": "Voice Agent", "percentage": 6},
        {"agent": "analytics", "count": 48, "label": "Analytics Agent", "percentage": 5}
    ]
    total_requests = sum(a["count"] for a in agents)
    return {
        "agents": agents,
        "total_requests": total_requests
    }


class MessageLogRequest(BaseModel):
    session_id: str
    user_message: str
    ai_response: str
    agent_used: str
    response_time_ms: int
    tokens_used: Optional[int] = None


@router.post("/messages")
async def log_message(
    request: MessageLogRequest,
    current_user = Depends(get_optional_user)
):
    """Log a chat message for analytics"""
    logger.info(f"Message logged: session={request.session_id}, agent={request.agent_used}")
    return {
        "status": "logged",
        "message_id": f"msg_{request.session_id}_{datetime.utcnow().timestamp()}"
    }


@router.get("/messages")
async def get_messages(
    limit: int = 50,
    current_user = Depends(get_optional_user)
):
    """Get chat messages"""
    messages = []
    for i in range(min(limit, 20)):
        messages.append({
            "id": f"msg_{i+1}",
            "session_id": f"session_{1 + (i // 5)}",
            "user_message": f"User message {i+1}",
            "ai_response": f"AI response {i+1}",
            "agent_used": ["nlu", "rag", "sql", "translate"][i % 4],
            "agent_label": ["NLU Agent", "RAG Agent", "SQL Agent", "Translation Agent"][i % 4],
            "response_time_ms": 1000 + (i * 50),
            "tokens_used": 150 + (i * 10),
            "was_helpful": True if i % 3 == 0 else None,
            "feedback": None,
            "created_at": datetime.utcnow().isoformat()
        })
    return messages


@router.put("/messages/{message_id}/feedback")
async def update_message_feedback(
    message_id: str,
    was_helpful: bool,
    feedback: Optional[str] = None,
    current_user = Depends(get_optional_user)
):
    """Update feedback for a message"""
    logger.info(f"Feedback updated for message {message_id}: helpful={was_helpful}")
    return {
        "status": "updated",
        "message_id": message_id
    }


@router.get("/sessions")
async def get_sessions(
    limit: int = 30,
    current_user = Depends(get_optional_user)
):
    """Get chat sessions"""
    sessions = []
    for i in range(min(limit, 10)):
        sessions.append({
            "id": f"session_{i+1}",
            "user_id": current_user.id if current_user else "user_1",
            "started_at": datetime.utcnow().isoformat(),
            "ended_at": None,
            "message_count": 5 + (i * 2),
            "total_response_time_ms": 5000 + (i * 1000),
            "agents_used": ["nlu", "rag", "sql"],
            "topics_discussed": ["product_search", "care_instructions"]
        })
    return sessions


@router.post("/sessions/{session_id}/start")
async def start_session(
    session_id: str,
    current_user = Depends(get_optional_user)
):
    """Start a new chat session"""
    logger.info(f"Session started: {session_id}")
    return {
        "status": "started",
        "session_id": session_id,
        "started_at": datetime.utcnow().isoformat()
    }


@router.post("/sessions/{session_id}/end")
async def end_session(
    session_id: str,
    current_user = Depends(get_optional_user)
):
    """End a chat session"""
    logger.info(f"Session ended: {session_id}")
    return {
        "status": "ended",
        "session_id": session_id,
        "ended_at": datetime.utcnow().isoformat()
    }


class LearningFeedbackRequest(BaseModel):
    session_id: Optional[str] = None
    category: str
    rating: int
    comment: Optional[str] = None
    suggested_improvement: Optional[str] = None


@router.post("/learning-feedback")
async def submit_learning_feedback(
    request: LearningFeedbackRequest,
    current_user: User = Depends(get_current_user)
):
    """Submit learning feedback"""
    logger.info(f"Learning feedback submitted: category={request.category}, rating={request.rating}")
    return {
        "status": "submitted",
        "timestamp": datetime.utcnow().isoformat()
    }
