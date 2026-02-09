"""Feedback agent for collecting and analyzing user feedback."""
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """Feedback type options."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    SUGGESTION = "suggestion"
    BUG_REPORT = "bug_report"


@dataclass
class Feedback:
    """Feedback data structure."""
    id: str
    session_id: str
    message_id: str
    feedback_type: str
    rating: Optional[int]
    comment: Optional[str]
    tags: List[str]
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class FeedbackAgent:
    """Feedback agent for collecting and analyzing user feedback."""
    
    def __init__(self):
        """Initialize the feedback agent."""
        self.feedback_store = []
        logger.info("Feedback agent initialized")
    
    async def submit(
        self,
        session_id: str,
        message_id: str,
        feedback_type: str,
        rating: Optional[int] = None,
        comment: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Submit user feedback."""
        try:
            feedback = Feedback(
                id=f"fb-{datetime.utcnow().timestamp()}",
                session_id=session_id,
                message_id=message_id,
                feedback_type=feedback_type,
                rating=rating,
                comment=comment,
                tags=tags or [],
                timestamp=datetime.utcnow()
            )
            
            self.feedback_store.append(feedback)
            
            logger.info(f"Feedback submitted: {feedback.id}")
            
            return {
                "id": feedback.id,
                "status": "submitted",
                "timestamp": feedback.timestamp.isoformat()
            }
        except Exception as e:
            logger.error(f"Feedback submission error: {e}")
            return {"error": str(e)}
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get feedback statistics."""
        total = len(self.feedback_store)
        
        if total == 0:
            return {
                "total_feedback": 0,
                "average_rating": 0.0,
                "positive_percentage": 0.0,
                "by_type": {}
            }
        
        positive = sum(1 for f in self.feedback_store if f.feedback_type == "positive")
        ratings = [f.rating for f in self.feedback_store if f.rating is not None]
        
        return {
            "total_feedback": total,
            "average_rating": sum(ratings) / len(ratings) if ratings else 0.0,
            "positive_percentage": (positive / total) * 100,
            "by_type": {
                "positive": sum(1 for f in self.feedback_store if f.feedback_type == "positive"),
                "negative": sum(1 for f in self.feedback_store if f.feedback_type == "negative"),
                "suggestion": sum(1 for f in self.feedback_store if f.feedback_type == "suggestion"),
                "bug_report": sum(1 for f in self.feedback_store if f.feedback_type == "bug_report")
            }
        }
    
    async def analyze_sentiment(self) -> Dict[str, Any]:
        """Analyze sentiment of feedback comments."""
        # TODO: Implement sentiment analysis
        return {
            "overall_sentiment": "neutral",
            "positive_count": 0,
            "negative_count": 0,
            "neutral_count": 0,
            "trend": "stable"
        }
    
    async def get_recent_feedback(
        self,
        limit: int = 10
    ) -> List[Dict]:
        """Get recent feedback entries."""
        recent = sorted(
            self.feedback_store,
            key=lambda x: x.timestamp,
            reverse=True
        )[:limit]
        
        return [f.to_dict() for f in recent]
    
    async def get_trends(
        self,
        period: str = "week"
    ) -> Dict[str, Any]:
        """Get feedback trends over time."""
        # TODO: Calculate trends
        return {
            "period": period,
            "daily": [],
            "weekly": [],
            "monthly": []
        }
    
    async def delete_feedback(self, feedback_id: str) -> Dict[str, Any]:
        """Delete a feedback entry."""
        for i, f in enumerate(self.feedback_store):
            if f.id == feedback_id:
                del self.feedback_store[i]
                return {"status": "deleted", "id": feedback_id}
        return {"error": "Feedback not found"}
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of feedback service."""
        return {
            "status": "healthy",
            "feedback_count": len(self.feedback_store),
            "storage": "in-memory"
        }


# Export agent instance
feedback_agent = FeedbackAgent()
