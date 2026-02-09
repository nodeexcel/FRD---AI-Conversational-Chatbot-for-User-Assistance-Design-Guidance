"""Master orchestrator agent that coordinates all specialized agents with enhanced error handling."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AgentType(str, Enum):
    """Types of specialized agents."""
    NLU = "nlu"
    KNOWLEDGE = "knowledge"
    SQL = "sql"
    DESIGN = "design"
    VOICE = "voice"
    TRANSLATION = "translation"
    FEEDBACK = "feedback"
    LLM = "llm"


@dataclass
class AgentResult:
    """Result from an agent operation."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    agent_type: Optional[AgentType] = None
    needs_clarification: bool = False
    clarifying_question: Optional[str] = None
    handoff_required: bool = False
    confidence: float = 1.0


# Clarifying questions based on intent patterns
CLARIFYING_QUESTIONS = {
    "dress_design": [
        "What occasion are you designing for? (wedding, party, casual, office)",
        "Do you have a fabric preference? (silk, cotton, chiffon, georgette)",
        "What color scheme are you considering?",
        "What's your budget range for this design?",
        "Do you have any specific body type considerations?"
    ],
    "product_search": [
        "What type of product are you looking for? (dress, top, bottom, accessory)",
        "What's your size requirement?",
        "Do you have a price range in mind?",
        "Any specific color or style preferences?"
    ],
    "fabric_care": [
        "What type of fabric is the garment made of?",
        "Is this for regular wear or special occasion?",
        "Do you have any specific concerns about the fabric?"
    ],
    "pricing": [
        "Which specific product are you asking about?",
        "Are you looking for something in a particular price range?",
        "Do you want to know about current offers or discounts?"
    ],
    "general": [
        "Could you please provide more details about what you're looking for?",
        "Would you like me to help you with dress design, product search, or something else?",
        "Can you rephrase your question so I can better assist you?"
    ]
}


class OrchestratorAgent:
    """Master orchestrator that routes requests to appropriate agents with enhanced error handling."""
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.agents: Dict[AgentType, Any] = {}
        self.low_confidence_threshold = 0.6
        logger.info("Orchestrator agent initialized")
    
    def register_agent(self, agent_type: AgentType, agent: Any):
        """Register a specialized agent."""
        self.agents[agent_type] = agent
        logger.info(f"Registered agent: {agent_type.value}")
    
    async def process_request(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        language: str = "en"
    ) -> AgentResult:
        """
        Process a user request and route to appropriate agents.
        
        Enhanced with:
        - Low confidence detection
        - Clarifying question flows
        - Human handoff for uncertain queries
        """
        try:
            # Step 1: NLU - Detect intent and entities with confidence
            nlu_result = await self._process_nlu(message)
            
            # Handle NLU failure
            if not nlu_result.success:
                return self._generate_clarifying_response(
                    "general",
                    "I'm having trouble understanding your message. Could you please rephrase it?"
                )
            
            intent = nlu_result.data.get("intent", "general")
            entities = nlu_result.data.get("entities", [])
            confidence = nlu_result.data.get("confidence", 1.0)
            
            # Step 2: Check confidence and handle low confidence
            if confidence < self.low_confidence_threshold:
                return self._handle_low_confidence(intent, message, context)
            
            # Step 3: Route based on intent
            if intent == "knowledge_query":
                return await self._process_knowledge_query(message, entities)
            elif intent == "sql_query":
                return await self._process_sql_query(message, entities)
            elif intent == "design_request":
                return await self._process_design_request(message, entities)
            elif intent == "voice_input":
                return await self._process_voice_input(message)
            elif intent == "translation_request":
                target_lang = context.get("target_language", "en") if context else "en"
                return await self._process_translation(message, target_lang)
            else:
                # Default: Use LLM for general response
                return await self._process_llm(message, context)
                
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            return self._handle_error(e)
    
    def _handle_low_confidence(
        self,
        intent: str,
        message: str,
        context: Optional[Dict[str, Any]]
    ) -> AgentResult:
        """Handle low confidence scenarios with clarifying questions or handoff."""
        # Try to generate a clarifying question first
        clarifying_question = self._get_clarifying_question(intent)
        
        if clarifying_question:
            return AgentResult(
                success=True,
                data={
                    "response": clarifying_question,
                    "requires_clarification": True
                },
                agent_type=AgentType.NLU,
                needs_clarification=True,
                clarifying_question=clarifying_question,
                confidence=0.5
            )
        else:
            # Offer human handoff for truly uncertain queries
            return AgentResult(
                success=True,
                data={
                    "response": (
                        "I'm not entirely confident about this answer. "
                        "Would you like me to connect you with a human expert who can better assist you?"
                    ),
                    "requires_clarification": False,
                    "handoff_available": True
                },
                agent_type=AgentType.NLU,
                handoff_required=True,
                confidence=0.4
            )
    
    def _get_clarifying_question(self, intent: str) -> Optional[str]:
        """Get a clarifying question based on detected intent."""
        import random
        
        questions = CLARIFYING_QUESTIONS.get(intent, CLARIFYING_QUESTIONS["general"])
        if questions:
            return random.choice(questions)
        return None
    
    def _generate_clarifying_response(self, intent: str, default_message: str) -> AgentResult:
        """Generate a clarifying response for unclear requests."""
        clarifying_question = self._get_clarifying_question(intent)
        
        if clarifying_question:
            return AgentResult(
                success=True,
                data={
                    "response": f"{default_message} {clarifying_question}",
                    "requires_clarification": True
                },
                agent_type=AgentType.NLU,
                needs_clarification=True,
                clarifying_question=clarifying_question,
                confidence=0.5
            )
        
        return AgentResult(
            success=True,
            data={
                "response": default_message,
                "requires_clarification": True
            },
            agent_type=AgentType.NLU,
            needs_clarification=True,
            confidence=0.5
        )
    
    def _handle_error(self, error: Exception) -> AgentResult:
        """Handle errors gracefully with helpful suggestions."""
        error_str = str(error).lower()
        
        # Check for specific error types
        if "database" in error_str or "sql" in error_str:
            response = (
                "I'm having trouble accessing the database right now. "
                "Let me try a different approach to help you."
            )
        elif "openai" in error_str or "api" in error_str:
            response = (
                "I'm having trouble connecting to the AI service. "
                "Please try again in a moment."
            )
        elif "timeout" in error_str:
            response = (
                "The request is taking longer than expected. "
                "Would you like to rephrase your question?"
            )
        else:
            response = (
                "I apologize, but I encountered an unexpected issue. "
                "Could you please try again or rephrase your question?"
            )
        
        return AgentResult(
            success=False,
            error=str(error),
            data={"response": response},
            agent_type=AgentType.LLM,
            needs_clarification=True,
            clarifying_question="Would you like to rephrase your question?"
        )
    
    async def _process_nlu(self, message: str) -> AgentResult:
        """Process with NLU agent."""
        if AgentType.NLU in self.agents:
            return await self.agents[AgentType.NLU].process(message)
        # Fallback: Basic intent detection
        return AgentResult(
            success=True,
            data={"intent": "general", "entities": []},
            agent_type=AgentType.NLU
        )
    
    async def _process_knowledge_query(
        self,
        message: str,
        entities: List[Dict]
    ) -> AgentResult:
        """Process knowledge query."""
        if AgentType.KNOWLEDGE in self.agents:
            result = await self.agents[AgentType.KNOWLEDGE].query(message, entities)
            
            # Check if knowledge query returned no results
            if result.success and not result.data.get("results"):
                return self._generate_clarifying_response(
                    "general",
                    "I couldn't find specific information about that in my knowledge base. "
                )
            
            return result
        
        return AgentResult(
            success=False,
            error="Knowledge agent not registered"
        )
    
    async def _process_sql_query(
        self,
        message: str,
        entities: List[Dict]
    ) -> AgentResult:
        """Process SQL query."""
        if AgentType.SQL in self.agents:
            return await self.agents[AgentType.SQL].execute(message, entities)
        return AgentResult(
            success=False,
            error="SQL agent not registered"
        )
    
    async def _process_design_request(
        self,
        message: str,
        entities: List[Dict]
    ) -> AgentResult:
        """Process design request."""
        if AgentType.DESIGN in self.agents:
            return await self.agents[AgentType.DESIGN].process(message, entities)
        return AgentResult(
            success=False,
            error="Design agent not registered"
        )
    
    async def _process_voice_input(self, message: str) -> AgentResult:
        """Process voice input."""
        if AgentType.VOICE in self.agents:
            return await self.agents[AgentType.VOICE].process(message)
        return AgentResult(
            success=False,
            error="Voice agent not registered"
        )
    
    async def _process_translation(
        self,
        message: str,
        target_language: str
    ) -> AgentResult:
        """Process translation request."""
        if AgentType.TRANSLATION in self.agents:
            return await self.agents[AgentType.TRANSLATION].translate(
                message, target_language
            )
        return AgentResult(
            success=False,
            error="Translation agent not registered"
        )
    
    async def _process_llm(
        self,
        message: str,
        context: Optional[Dict[str, Any]]
    ) -> AgentResult:
        """Process with LLM agent."""
        if AgentType.LLM in self.agents:
            return await self.agents[AgentType.LLM].generate(message, context)
        return AgentResult(
            success=False,
            error="LLM agent not registered"
        )
    
    def set_confidence_threshold(self, threshold: float):
        """Set the confidence threshold for low confidence detection."""
        self.low_confidence_threshold = max(0.0, min(1.0, threshold))
        logger.info(f"Confidence threshold set to {self.low_confidence_threshold}")


# Global orchestrator instance
orchestrator = OrchestratorAgent()
