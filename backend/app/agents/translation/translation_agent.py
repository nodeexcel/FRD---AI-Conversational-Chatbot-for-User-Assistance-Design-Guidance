"""Translation Agent for multilingual support using OpenAI."""
from typing import Dict, Any, Optional
import logging

from app.core.llm.openai_client_v3 import openai_client_v3 as openai_client

logger = logging.getLogger(__name__)


class TranslationAgent:
    """Agent for translating text between languages while preserving meaning."""
    
    # Supported languages with their codes
    SUPPORTED_LANGUAGES = {
        "en": "English",
        "es": "Spanish", 
        "hi": "Hindi",
        "te": "Telugu",
        "fr": "French",
        "de": "German",
        "zh": "Chinese",
        "ja": "Japanese",
        "ko": "Korean",
        "pt": "Portuguese",
        "ar": "Arabic",
        "ru": "Russian"
    }
    
    def __init__(self):
        """Initialize the translation agent."""
        logger.info("Translation agent initialized")
    
    async def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect the language of the input text.
        
        Args:
            text: Input text to detect language for
            
        Returns:
            Dict with detected language code and confidence
        """
        try:
            prompt = f"""Detect the language of the following text. 
Return ONLY the language name (e.g., "English", "Spanish", "Hindi").
Do not include any explanation.

Text: "{text}"

Language:"""
            
            response = await openai_client.chat(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="You are a language detection expert.",
                max_tokens=20
            )
            
            detected_lang = response.text.strip()
            
            # Try to match with supported languages
            lang_code = None
            for code, name in self.SUPPORTED_LANGUAGES.items():
                if name.lower() in detected_lang.lower() or detected_lang.lower() in name.lower():
                    lang_code = code
                    break
            
            return {
                "detected": detected_lang,
                "code": lang_code or "en",
                "confidence": 0.9
            }
            
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return {
                "detected": "English",
                "code": "en",
                "confidence": 0.5
            }
    
    async def translate(
        self, 
        text: str, 
        target_lang: str = "en",
        source_lang: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Translate text from source language to target language.
        
        Args:
            text: Text to translate
            target_lang: Target language code (e.g., "hi" for Hindi)
            source_lang: Source language code (optional, auto-detect if not provided)
            
        Returns:
            Dict with translated text and language info
        """
        try:
            # Get language names
            target_name = self.SUPPORTED_LANGUAGES.get(target_lang, "English")
            
            # Detect source language if not provided
            if not source_lang:
                detection = await self.detect_language(text)
                source_lang = detection["code"]
            
            source_name = self.SUPPORTED_LANGUAGES.get(source_lang, "English")
            
            # Generate translation prompt
            prompt = f"""You are a professional translator. Translate the following text from {source_name} to {target_name}.
IMPORTANT: Preserve the meaning, tone, and context of the original text.
Keep any product names, technical terms, or proper nouns in their original form if they should not be translated.
Return ONLY the translated text, no explanations.

Text ({source_name}): "{text}"

Translation ({target_name}):"""
            
            response = await openai_client.chat(
                messages=[{"role": "user", "content": prompt}],
                system_prompt=f"You are a professional translator. Translate from {source_name} to {target_name} while preserving meaning.",
                max_tokens=1000
            )
            
            translated_text = response.text.strip()
            
            # Remove quotes if present
            if translated_text.startswith('"') and translated_text.endswith('"'):
                translated_text = translated_text[1:-1]
            
            logger.info(f"Translated text from {source_name} to {target_name}")
            
            return {
                "original_text": text,
                "translated_text": translated_text,
                "source_lang": source_lang,
                "source_lang_name": source_name,
                "target_lang": target_lang,
                "target_lang_name": target_name,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return {
                "original_text": text,
                "translated_text": text,  # Return original on error
                "source_lang": source_lang or "unknown",
                "target_lang": target_lang,
                "error": str(e),
                "success": False
            }
    
    async def translate_chat_message(
        self,
        message: Dict[str, Any],
        target_lang: str
    ) -> Dict[str, Any]:
        """
        Translate a chat message (with role and content) to target language.
        
        Args:
            message: Chat message dict with 'role' and 'content'
            target_lang: Target language code
            
        Returns:
            Translated message dict
        """
        if target_lang == "en":
            return message  # No translation needed
        
        result = await self.translate(message["content"], target_lang)
        
        return {
            "role": message["role"],
            "content": result["translated_text"],
            "original_content": message["content"],
            "translated": True,
            "target_lang": target_lang
        }
    
    async def translate_conversation(
        self,
        messages: list,
        target_lang: str
    ) -> list:
        """
        Translate a conversation history to target language.
        
        Args:
            messages: List of chat message dicts
            target_lang: Target language code
            
        Returns:
            List of translated messages
        """
        if target_lang == "en":
            return messages
        
        translated_messages = []
        for msg in messages:
            if msg.get("content"):
                result = await self.translate(msg["content"], target_lang)
                translated_messages.append({
                    "role": msg["role"],
                    "content": result["translated_text"],
                    "original_content": msg.get("content"),
                    "translated": True,
                    "target_lang": target_lang
                })
            else:
                translated_messages.append(msg)
        
        return translated_messages
