"""NLU (Natural Language Understanding) agent using OpenAI."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json
import logging

from app.core.llm.openai_client_v3 import openai_client_v3 as openai_client

logger = logging.getLogger(__name__)


@dataclass
class Intent:
    """Detected intent."""
    name: str
    confidence: float
    description: str


@dataclass
class Entity:
    """Extracted entity."""
    type: str
    value: str
    confidence: float


class NLUMessage:
    """Conversation message for history."""
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content


class NLUAgent:
    """Natural Language Understanding agent using OpenAI."""
    
    # Intent descriptions for reference
    INTENTS = {
        "greeting": "User is greeting the bot",
        "farewell": "User is ending the conversation",
        "knowledge_query": "User is asking for information about dresses/products",
        "design_help": "User wants dress design assistance",
        "comparison": "User is comparing options",
        "pricing": "User is asking about prices",
        "care": "User is asking about product care",
        "recommendation": "User wants personalized recommendations",
        "feedback": "User is providing feedback",
        "help": "User is asking for help",
        "general": "General conversation"
    }
    
    # Common entity types for dress domain
    ENTITY_TYPES = [
        "dress_type",      # evening gown, saree, kurta, etc.
        "fabric",          # silk, cotton, chiffon, etc.
        "color",           # red, blue, black, etc.
        "occasion",        # wedding, party, office, etc.
        "body_type",       # hourglass, pear, apple, etc.
        "size",            # S, M, L, XL, etc.
        "budget",          # price range
        "season",          # summer, winter, monsoon
        "style",           # traditional, modern, casual
        "length",          # knee-length, floor-length, etc.
        "neckline",        # round, v-neck, sweetheart
        "sleeve_type",     # sleeveless, full sleeves, etc.
    ]
    
    def __init__(self):
        """Initialize the NLU agent."""
        logger.info("NLU agent initialized with OpenAI")
    
    async def process(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Process a message and extract intent and entities using OpenAI."""
        try:
            # Convert history to NLUMessage objects
            history = []
            if conversation_history:
                for msg in conversation_history[-10:]:  # Last 10 messages
                    history.append(NLUMessage(
                        role=msg.get("role", "user"),
                        content=msg.get("content", "")
                    ))
            
            # Use OpenAI for intent/entity extraction
            nlu_result = await openai_client.extract_intent_and_entities(
                user_message=message,
                conversation_history=history
            )
            
            # Get intent description
            intent_name = nlu_result.get("intent", "general")
            intent_description = self.INTENTS.get(intent_name, "General conversation")
            
            return {
                "intent": intent_name,
                "intent_description": intent_description,
                "confidence": nlu_result.get("confidence", 0.5),
                "entities": nlu_result.get("entities", []),
                "context": nlu_result.get("context", ""),
                "language": "en"  # Can be extended for language detection
            }
        except Exception as e:
            logger.error(f"NLU processing error: {e}")
            # Fallback to basic extraction
            return self._basic_extraction(message)
    
    async def detect_intent(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Intent:
        """Detect the intent of a message."""
        result = await self.process(message, conversation_history)
        return Intent(
            name=result.get("intent", "general"),
            confidence=result.get("confidence", 0.5),
            description=result.get("intent_description", "General conversation")
        )
    
    async def extract_entities(
        self,
        message: str
    ) -> List[Entity]:
        """Extract entities from a message."""
        result = await self.process(message)
        entities = []
        for entity_data in result.get("entities", []):
            entities.append(Entity(
                type=entity_data.get("type", "unknown"),
                value=entity_data.get("value", ""),
                confidence=entity_data.get("confidence", 0.5)
            ))
        return entities
    
    async def handle_followup(
        self,
        message: str,
        previous_intent: str,
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Handle follow-up questions with context."""
        # Build context from previous interactions
        context = f"Previous intent: {previous_intent}\n"
        context += "Conversation:\n"
        for msg in conversation_history[-5:]:
            context += f"- {msg.get('role', 'user')}: {msg.get('content', '')[:100]}\n"
        
        result = await self.process(message, conversation_history)
        result["followup_context"] = context
        return result
    
    async def detect_language(self, message: str) -> Dict[str, Any]:
        """Detect the language of a message."""
        # Simple keyword-based detection
        # Can be enhanced with language detection libraries
        languages = {
            "hi": ["हिन्दी", "नमस्ते", "धन्यवाद", "भारत"],
            "es": ["hola", "gracias", "cómo", "españa"],
            "fr": ["bonjour", "merci", "comment", "france"],
            "de": ["hallo", "danke", "wie", "deutschland"]
        }
        
        message_lower = message.lower()
        for lang, keywords in languages.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return {"language": lang, "confidence": 0.9}
        
        return {"language": "en", "confidence": 0.95}
    
    def _basic_extraction(self, message: str) -> Dict[str, Any]:
        """Basic fallback extraction when OpenAI fails."""
        message_lower = message.lower()
        
        # Simple keyword matching for intent
        intent = "general"
        for intent_name, keywords in {
            "greeting": ["hello", "hi", "hey", "good morning", "good afternoon"],
            "farewell": ["bye", "goodbye", "see you", "later", "stop"],
            "knowledge_query": ["what is", "how does", "explain", "tell me about", "information"],
            "design_help": ["design", "create", "make", "customize", "create a"],
            "pricing": ["price", "cost", "how much", "budget", "under", "less than"],
            "care": ["wash", "clean", "care", "maintain", "store"],
            "recommendation": ["recommend", "suggest", "which", "best for"],
            "comparison": ["compare", "difference", "versus", "vs"],
        }.items():
            for keyword in keywords:
                if keyword in message_lower:
                    intent = intent_name
                    break
        
        # Extract entities using keyword matching
        entities = []
        
        # Colors
        colors = ["red", "blue", "green", "yellow", "black", "white", "pink", "purple", "orange", "brown", "gray", "grey", "navy", "beige", "maroon", "wine"]
        for color in colors:
            if color in message_lower:
                entities.append({
                    "type": "color",
                    "value": color,
                    "confidence": 0.8
                })
                break
        
        # Fabrics
        fabrics = ["cotton", "silk", "rayon", "linen", "wool", "polyester", "chiffon", "velvet", "denim", "satin", "georgette", "crepe"]
        for fabric in fabrics:
            if fabric in message_lower:
                entities.append({
                    "type": "fabric",
                    "value": fabric,
                    "confidence": 0.8
                })
                break
        
        # Occasions
        occasions = ["wedding", "party", "office", "casual", "formal", "festive", "date", "engagement", "reception"]
        for occasion in occasions:
            if occasion in message_lower:
                entities.append({
                    "type": "occasion",
                    "value": occasion,
                    "confidence": 0.8
                })
                break
        
        # Dress types
        dress_types = ["saree", "kurta", "gown", "dress", "suit", "lehenga", "palazzo", "anorak", "jumpsuit", "top"]
        for dress_type in dress_types:
            if dress_type in message_lower:
                entities.append({
                    "type": "dress_type",
                    "value": dress_type,
                    "confidence": 0.8
                })
                break
        
        # Price range
        if "under" in message_lower or "less than" in message_lower:
            import re
            match = re.search(r'\$?(\d+)', message_lower)
            if match:
                entities.append({
                    "type": "budget",
                    "value": match.group(1),
                    "confidence": 0.8
                })
        
        return {
            "intent": intent,
            "intent_description": self.INTENTS.get(intent, "General conversation"),
            "confidence": 0.3,
            "entities": entities,
            "context": ""
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check NLU service health."""
        return {
            "status": "healthy",
            "service": "openai",
            "model": "gpt-3.5-turbo",
            "supported_intents": list(self.INTENTS.keys()),
            "entity_types": self.ENTITY_TYPES
        }


# Export agent instance
nlu_agent = NLUAgent()
