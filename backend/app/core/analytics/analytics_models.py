"""
Analytics and Learning Loop Models
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

class AgentType(str, Enum):
    NLU = "nlu"
    RAG = "rag"
    SQL = "sql"
    DESIGN = "design"
    VOICE = "voice"
    TRANSLATION = "translation"
    FEEDBACK = "feedback"

# Chat Message Schema
class ChatMessageCreate(BaseModel):
    session_id: str
    user_message: str
    ai_response: str
    agent_used: AgentType
    response_time_ms: int
    tokens_used: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    user_message: str
    ai_response: str
    agent_used: AgentType
    response_time_ms: int
    tokens_used: Optional[int]
    was_helpful: Optional[bool]
    feedback: Optional[str]
    created_at: datetime

# Session Analytics Schema
class SessionAnalytics(BaseModel):
    session_id: str
    user_id: str
    started_at: datetime
    ended_at: Optional[datetime]
    message_count: int
    total_response_time_ms: int
    agents_used: List[str]
    topics_discussed: List[str]

# User Analytics Summary
class UserAnalyticsSummary(BaseModel):
    total_sessions: int
    total_messages: int
    average_response_time_ms: float
    favorite_agents: List[Dict[str, int]]
    daily_message_counts: List[Dict[str, int]]
    weekly_activity: Dict[str, int]
    top_topics: List[Dict[str, int]]
    average_rating: float
    total_designs_created: int
    documents_uploaded: int

# Learning Feedback Schema
class LearningFeedbackCreate(BaseModel):
    session_id: str
    category: str  # "response_quality", "response_time", "agent_selection", "personalization"
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None
    suggested_improvement: Optional[str] = None

class LearningFeedbackResponse(BaseModel):
    id: str
    session_id: str
    category: str
    rating: int
    comment: Optional[str]
    suggested_improvement: Optional[str]
    created_by: Optional[str]
    created_at: datetime

# Agent Performance Metrics
class AgentPerformance(BaseModel):
    agent_type: str
    total_requests: int
    average_response_time_ms: float
    average_rating: float
    success_rate: float
    daily_counts: List[Dict[str, int]]

# System Analytics (Admin)
class SystemAnalytics(BaseModel):
    total_users: int
    active_users_today: int
    active_users_week: int
    total_messages: int
    messages_today: int
    messages_this_week: int
    total_sessions: int
    average_session_length_ms: float
    agent_usage_stats: Dict[str, int]
    database_size_mb: float
    uptime_seconds: float
