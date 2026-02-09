"""OpenAI LLM client using requests library for better compatibility."""
import os
import json
import logging
import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import requests

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


class OpenAIClientV3:
    """OpenAI client using requests library."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens
        self.temperature = settings.openai_temperature
        # Strip any whitespace/newlines from API key
        self.api_key = settings.openai_api_key.strip() if settings.openai_api_key else ""
        self.base_url = "https://api.openai.com/v1"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API request."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> ChatCompletion:
        """Send chat completion request using requests (sync, then convert to async)."""
        
        # Build message list
        chat_messages = []
        if system_prompt:
            chat_messages.append({"role": "system", "content": system_prompt})
        chat_messages.extend(messages)
        
        payload = {
            "model": self.model,
            "messages": chat_messages,
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": temperature or self.temperature
        }
        
        try:
            # Use requests library directly (sync)
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self._get_headers(),
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            
            data = response.json()
            choice = data["choices"][0]["message"]
            
            return ChatCompletion(
                text=choice["content"],
                usage={
                    "prompt_tokens": data["usage"]["prompt_tokens"],
                    "completion_tokens": data["usage"]["completion_tokens"],
                    "total_tokens": data["usage"]["total_tokens"]
                },
                model=data["model"]
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
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for texts using OpenAI text-embedding-3-small."""
        import numpy as np
        
        logger.info(f"Creating embeddings for {len(texts)} texts using OpenAI")
        
        # Use text-embedding-3-small for efficiency
        embeddings = []
        
        try:
            for i, text in enumerate(texts):
                payload = {
                    "model": "text-embedding-3-small",
                    "input": text[:8000]  # Truncate to avoid token limits
                }
                
                response = requests.post(
                    f"{self.base_url}/embeddings",
                    headers=self._get_headers(),
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                
                data = response.json()
                embedding = data["data"][0]["embedding"]
                embeddings.append(embedding)
                
                logger.debug(f"Created embedding {i+1}/{len(texts)} with {len(embedding)} dimensions")
            
            logger.info(f"Successfully created {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to create embeddings: {e}")
            # Return zero embeddings as fallback
            return [[0.0] * 1536 for _ in texts]


# Export singleton instance
openai_client_v3 = OpenAIClientV3()


def get_openai_client() -> OpenAIClientV3:
    """Get the OpenAI client singleton."""
    return openai_client_v3


def create_embeddings(texts: List[str]) -> List[List[float]]:
    """Create embeddings for texts."""
    return openai_client_v3.create_embeddings(texts)
