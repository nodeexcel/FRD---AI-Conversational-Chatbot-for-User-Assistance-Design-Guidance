# Analytics Agent for learning, knowledge gaps, and completion tracking
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from uuid import uuid4

logger = logging.getLogger(__name__)


class AnalyticsAgent:
    """Handles analytics, learning loops, knowledge gaps, and completion tracking"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def track_question(
        self,
        user_id: str,
        session_id: str,
        question: str,
        intent: str,
        confidence: float,
        response_time: float,
        was_helpful: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Track user questions for analytics and learning"""
        
        # Log the question for analytics
        analytics_entry = {
            "id": str(uuid4()),
            "user_id": user_id,
            "session_id": session_id,
            "question": question,
            "intent": intent,
            "confidence": confidence,
            "response_time_ms": response_time * 1000,
            "was_helpful": was_helpful,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        logger.info(f"Tracked question: {question[:50]}... (intent: {intent}, confidence: {confidence})")
        
        return analytics_entry
    
    async def identify_knowledge_gaps(
        self,
        user_id: str,
        question: str,
        intent: str,
        confidence: float,
        sources_checked: List[str]
    ) -> Dict[str, Any]:
        """
        Identify knowledge gaps when:
        - Confidence is low (< 0.7)
        - No sources found
        - User asks follow-up questions on same topic
        """
        
        gap_analysis = {
            "has_gap": False,
            "gap_type": None,
            "suggested_action": None,
            "priority": "low"
        }
        
        # Check if this is a knowledge gap scenario
        if confidence < 0.7:
            gap_analysis["has_gap"] = True
            gap_analysis["gap_type"] = "low_confidence"
            gap_analysis["suggested_action"] = "human_review"
            gap_analysis["priority"] = "high"
            gap_analysis["reason"] = f"Low confidence ({confidence}) for intent: {intent}"
            
        # Check if no sources were found
        if not sources_checked or len(sources_checked) == 0:
            gap_analysis["has_gap"] = True
            gap_analysis["gap_type"] = "no_sources"
            gap_analysis["suggested_action"] = "content_creation"
            gap_analysis["priority"] = "medium"
            gap_analysis["reason"] = f"No sources found for question about: {intent}"
            
        if gap_analysis["has_gap"]:
            logger.warning(f"Knowledge gap identified: {gap_analysis}")
        
        return gap_analysis
    
    async def should_human_handoff(
        self,
        confidence: float,
        intent: str,
        has_sources: bool,
        user_feedback: Optional[bool] = None,
        consecutive_unanswered: int = 0
    ) -> Dict[str, Any]:
        """
        Determine if query should be handed off to human support
        based on FRD requirements for low-confidence answers
        """
        
        handoff = {
            "should_handoff": False,
            "reason": None,
            "priority": None,
            "escalation_level": None
        }
        
        # Criteria for human handoff
        if confidence < 0.5:
            handoff["should_handoff"] = True
            handoff["reason"] = f"Very low confidence ({confidence})"
            handoff["priority"] = "urgent"
            handoff["escalation_level"] = 3
        
        elif confidence < 0.7:
            if consecutive_unanswered >= 2:
                handoff["should_handoff"] = True
                handoff["reason"] = "Multiple consecutive low-confidence responses"
                handoff["priority"] = "high"
                handoff["escalation_level"] = 2
            elif not has_sources and user_feedback is False:
                handoff["should_handoff"] = True
                handoff["reason"] = "Low confidence with negative user feedback"
                handoff["priority"] = "high"
                handoff["escalation_level"] = 2
        
        elif user_feedback is False and consecutive_unanswered >= 1:
            handoff["should_handoff"] = True
            handoff["reason"] = "Negative user feedback received"
            handoff["priority"] = "medium"
            handoff["escalation_level"] = 1
        
        if handoff["should_handoff"]:
            logger.info(f"Human handoff triggered: {handoff}")
        
        return handoff
    
    async def track_design_completion(
        self,
        user_id: str,
        session_id: str,
        design_session_id: str,
        current_step: int,
        total_steps: int,
        completed_steps: List[int],
        abandoned: bool = False,
        completion_time_seconds: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Track design workflow completion rates
        as per FRD analytics requirements
        """
        
        completion_data = {
            "user_id": user_id,
            "session_id": session_id,
            "design_session_id": design_session_id,
            "current_step": current_step,
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "progress_percentage": len(completed_steps) / total_steps * 100 if total_steps > 0 else 0,
            "abandoned": abandoned,
            "completed": len(completed_steps) >= total_steps,
            "completion_time_seconds": completion_time_seconds,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if completion_data["completed"]:
            logger.info(f"Design completed! Session: {design_session_id}, Time: {completion_time_seconds}s")
        elif completion_data["abandoned"]:
            logger.warning(f"Design abandoned at step {current_step}")
        
        return completion_data
    
    async def get_most_asked_questions(
        self,
        days: int = 7,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get most frequently asked questions for analytics
        """
        # This would query the database in a real implementation
        # For now, return structure
        return [
            {
                "question": "Sample question",
                "count": 10,
                "common_intent": "product_inquiry",
                "avg_confidence": 0.85
            }
        ]
    
    async def get_unanswered_queries(
        self,
        days: int = 7,
        confidence_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Get poorly answered queries that need attention
        as per FRD analytics requirements
        """
        return [
            {
                "question": "Sample unanswered query",
                "times_asked": 3,
                "avg_confidence": 0.65,
                "last_asked": datetime.utcnow().isoformat(),
                "suggested_action": "content_creation"
            }
        ]
    
    async def get_language_usage_trends(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get language usage trends for analytics
        """
        return {
            "languages": {
                "en": {"count": 150, "percentage": 60},
                "es": {"count": 40, "percentage": 16},
                "hi": {"count": 30, "percentage": 12},
                "other": {"count": 30, "percentage": 12}
            },
            "period": f"last_{days}_days",
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def get_user_satisfaction_signals(
        self,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get user satisfaction signals for analytics
        """
        return {
            "total_feedback": 100,
            "positive": 75,
            "negative": 15,
            "neutral": 10,
            "satisfaction_rate": 0.75,
            "nps_score": 50
        }
