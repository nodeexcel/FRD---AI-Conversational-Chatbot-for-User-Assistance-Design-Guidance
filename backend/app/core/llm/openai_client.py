"""OpenAI LLM client for GPT models."""
from typing import Dict, Any, Optional, AsyncGenerator, List
from openai import AsyncOpenAI
from pydantic import BaseModel
import json
import logging

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


class OpenAIClient:
    """OpenAI client for chat completions."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        self.client = None
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens
        self.temperature = settings.openai_temperature
        
    def _get_client(self) -> AsyncOpenAI:
        """Get or create OpenAI client with proper settings."""
        if self.client is None:
            import os
            # Clear proxy settings to ensure direct connection
            proxy_keys = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']
            saved_proxies = {}
            for key in proxy_keys:
                if key in os.environ:
                    saved_proxies[key] = os.environ.pop(key)
            
            # Set NO_PROXY for OpenAI
            os.environ['NO_PROXY'] = 'api.openai.com'
            
            self.client = AsyncOpenAI(
                api_key=settings.openai_api_key,
                http_client=None  # Use default client
            )
            
            # Restore proxy settings if they were there
            os.environ.update(saved_proxies)
            
        return self.client
    
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
        
        # Build message list
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
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion."""
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
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=True
            )
            
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for texts using OpenAI text-embedding-3-small."""
        import openai
        
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        try:
            client = openai.OpenAI(api_key=settings.openai_api_key)
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            # Extract embedding vectors
            embeddings = [data.embedding for data in response.data]
            return embeddings
        except Exception as e:
            logger.error(f"OpenAI embeddings error: {e}")
            raise
    
    async def extract_intent_and_entities(
        self,
        user_message: str,
        conversation_history: Optional[List[Message]] = None
    ) -> Dict[str, Any]:
        """Extract intent and entities using OpenAI."""
        
        system_prompt = """You are an expert NLU (Natural Language Understanding) system for a dress design chatbot.
        
Your task is to analyze user messages and extract:
1. INTENT: The user's intention (one of):
    - greeting: User is greeting
    - farewell: User is ending conversation
    - database_query: User asking about inventory, product count, or database-specific questions (e.g., "how many dresses do you have?", "show me all red dresses", "what products are available?", "list all products", "count summer dresses")
    - knowledge_query: User asking for product information or dress details (not count/inventory)
    - design_help: User wants dress design assistance
    - comparison: User comparing options
    - pricing: User asking about prices
    - care: User asking about product care
    - recommendation: User wants recommendations
    - feedback: User giving feedback
    - general: General conversation
    
2. ENTITIES: List of extracted entities (dress types, fabrics, colors, occasions, body types, etc.)
    - Each entity should have: type, value, confidence

3. CONFIDENCE: Your confidence score (0-1)

4. CONTEXT: Any follow-up or contextual information

Respond ONLY with valid JSON in this format:
{
    "intent": "intent_name",
    "confidence": 0.95,
    "entities": [
        {"type": "dress_type", "value": "evening gown", "confidence": 0.9}
    ],
    "context": "follow-up question about fabric"
}
"""
        
        messages = []
        if conversation_history:
            # Add recent history (last 5 messages)
            for msg in conversation_history[-5:]:
                # Handle both dict and Message object
                if hasattr(msg, 'role'):
                    messages.append({"role": msg.role, "content": msg.content})
                else:
                    messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        
        messages.append({"role": "user", "content": user_message})
        
        response = await self.chat(messages, system_prompt, max_tokens=500)
        
        try:
            result = json.loads(response.text)
        except json.JSONDecodeError:
            # Fallback parsing
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
        conversation_history: Optional[List[Message]] = None
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
- Use emojis sparingly but appropriately
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
        
        response = await self.chat(messages, system_prompt, max_tokens=500)
        
        return response.text


# Export singleton instance
openai_client = OpenAIClient()
