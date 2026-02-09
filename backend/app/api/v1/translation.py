"""Translation API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import logging

from app.core.auth.jwt_handler import get_current_user
from app.agents.translation.translation_agent import TranslationAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/translate", tags=["Translation"])

# Initialize translation agent
translation_agent = TranslationAgent()


# Request/Response Models
class TranslateRequest(BaseModel):
    text: str
    target_lang: str = "en"
    source_lang: Optional[str] = None


class TranslateResponse(BaseModel):
    original_text: str
    translated_text: str
    source_lang: str
    source_lang_name: str
    target_lang: str
    target_lang_name: str
    success: bool
    error: Optional[str] = None


class DetectLanguageRequest(BaseModel):
    text: str


class DetectLanguageResponse(BaseModel):
    detected: str
    code: str
    confidence: float


class TranslateConversationRequest(BaseModel):
    messages: List[dict]
    target_lang: str


class SupportedLanguagesResponse(BaseModel):
    languages: dict


@router.get("/languages", response_model=SupportedLanguagesResponse)
async def get_supported_languages():
    """Get list of supported languages."""
    return {
        "languages": translation_agent.SUPPORTED_LANGUAGES
    }


@router.post("/detect", response_model=DetectLanguageResponse)
async def detect_language(request: DetectLanguageRequest):
    """
    Detect the language of the given text.
    
    Example:
        Input: {"text": "नमस्ते, आप कैसे हैं?"}
        Output: {"detected": "Hindi", "code": "hi", "confidence": 0.9}
    """
    try:
        result = await translation_agent.detect_language(request.text)
        return result
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=TranslateResponse)
async def translate_text(
    request: TranslateRequest,
    current_user = Depends(get_current_user)
):
    """
    Translate text from one language to another.
    
    Supported languages: en (English), es (Spanish), hi (Hindi), te (Telugu),
    fr (French), de (German), zh (Chinese), ja (Japanese), ko (Korean),
    pt (Portuguese), ar (Arabic), ru (Russian)
    
    Example:
        Input: {"text": "Hello, how are you?", "target_lang": "hi"}
        Output: {"translated_text": "नमस्ते, आप कैसे हैं?"}
    """
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if request.target_lang not in translation_agent.SUPPORTED_LANGUAGES:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported language. Supported: {list(translation_agent.SUPPORTED_LANGUAGES.keys())}"
            )
        
        result = await translation_agent.translate(
            text=request.text,
            target_lang=request.target_lang,
            source_lang=request.source_lang
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Translation failed"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversation")
async def translate_conversation(
    request: TranslateConversationRequest,
    current_user = Depends(get_current_user)
):
    """
    Translate a conversation history to the target language.
    
    Useful for translating chat history when user changes language preference.
    """
    try:
        if not request.messages:
            raise HTTPException(status_code=400, detail="Messages cannot be empty")
        
        if request.target_lang not in translation_agent.SUPPORTED_LANGUAGES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported language. Supported: {list(translation_agent.SUPPORTED_LANGUAGES.keys())}"
            )
        
        translated = await translation_agent.translate_conversation(
            messages=request.messages,
            target_lang=request.target_lang
        )
        
        return {
            "original_messages": request.messages,
            "translated_messages": translated,
            "target_lang": request.target_lang,
            "target_lang_name": translation_agent.SUPPORTED_LANGUAGES.get(request.target_lang, "Unknown")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Conversation translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
