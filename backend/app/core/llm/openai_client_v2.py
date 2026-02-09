"""OpenAI LLM client using direct HTTP connection."""
import os
import json
import logging
from typing import Dict, Any, Optional, List
from openai import AsyncOpenAI
from pydantic import BaseModel

from app.config import settings

logger = logging.getLogger(__name__)


class Message(BaseModel):
    """Chat message."""
    role: str
    content: str


class ChatCompletion(BaseModel):
    """Chat completion response."""
    text: str
    usage: Dict[str, int]
    model: str


class OpenAIClientV2:
    """OpenAI client using direct HTTP connection."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        self._client = None
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens
        self.temperature = settings.openai_temperature
    
    def _get_client(self) -> AsyncOpenAI:
        """Get or create OpenAI client."""
        if self._client is None:
            # Create client with no automatic environment reading
            self._client = AsyncOpenAI(
                api_key=settings.openai_api_key,
            )
        
        return self._client
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> ChatCompletion:
        """Send chat completion request."""
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        client = self._get_client()
        
        chat_messages = []
        if system_prompt:
            chat_messages.append({"role": "system", "content": system_prompt})
        chat_messages.extend(messages)
        
        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=chat_messages,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature
            )
            
            return ChatCompletion(
                text=response.choices[0].message.content,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                model=response.model
            )
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def extract_intent_and_entities(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Extract intent and entities using OpenAI."""
        
        system_prompt = """You are an expert NLU system for a dress design chatbot.
        
        Your task is to analyze user messages and extract:
        1. INTENT: The user's intention (greeting, farewell, database_query, knowledge_query, design_help, comparison, pricing, care, recommendation, feedback, general)
        2. ENTITIES: List of extracted entities (dress types, fabrics, colors, occasions, body types, budgets, etc.)
        3. CONFIDENCE: Your confidence score (0-1)
        4. CONTEXT: Any follow-up or contextual information
        
        Respond ONLY with valid JSON:
        {"intent": "intent_name", "confidence": 0.95, "entities": [{"type": "color", "value": "red", "confidence": 0.9}], "context": ""}
        """
        
        messages = []
        if conversation_history:
            for msg in conversation_history[-5:]:
                if hasattr(msg, 'role'):
                    messages.append({"role": msg.role, "content": msg.content})
                else:
                    messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = await self.chat(messages, system_prompt, max_tokens=300)
            result = json.loads(response.text)
        except json.JSONDecodeError:
            result = {
                "intent": "general",
                "confidence": 0.5,
                "entities": [],
                "context": ""
            }
        
        return result
    
    async def generate_response(
        self,
        user_message: str,
        intent: str,
        entities: List[Dict],
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """Generate contextual response based on intent and entities."""
        
        system_prompt = f"""You are a helpful dress design assistant.
        
        Current context:
        - User intent: {intent}
        - Entities: {json.dumps(entities)}
        - Context: {context or 'First interaction'}
        
        Guidelines:
        - Be conversational and friendly
        - Provide helpful dress design advice
        - If user asks about products, mention them naturally
        - Keep responses concise but informative
        
        Respond to: {user_message}
        """
        
        messages = []
        if conversation_history:
            for msg in conversation_history[-5:]:
                if hasattr(msg, 'role'):
                    messages.append({"role": msg.role, "content": msg.content})
                else:
                    messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        
        try:
            response = await self.chat(messages, system_prompt, max_tokens=300)
            return response.text
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return f"I understand you're asking about '{user_message}'. For detailed information, please try asking about specific products."


# Export singleton instance
openai_client_v2 = OpenAIClientV2()
