# Voice API endpoints - simplified for testing
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["Voice"])


class AvatarVoicePair(BaseModel):
    avatar_id: str
    avatar_name: str
    voice: str
    style: str


class GetVoicesResponse(BaseModel):
    voices: List[str]
    avatar_pairs: List[AvatarVoicePair]
    recommendations: dict


class VoiceForAvatarResponse(BaseModel):
    avatar_id: str
    voice_id: str
    audio_url: Optional[str] = None
    audio_data: Optional[str] = None


# Avatar to Voice Mapping
AVATAR_VOICE_MAP = {
    "sophia": "alloy",
    "emma": "echo", 
    "james": "fable",
    "aria": "nova",
    "default": "shimmer",
    "female": "alloy",
    "male": "fable",
    "friendly": "shimmer",
    "professional": "alloy",
}

VOICE_RECOMMENDATIONS = {
    "professional": "alloy",
    "casual": "nova", 
    "friendly": "shimmer",
    "authoritative": "onyx",
    "storytelling": "fable",
    "elegant": "nova",
}

SUPPORTED_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]


# Simple test endpoint
@router.get("/test")
async def voice_test():
    """Test endpoint to verify voice router is working"""
    return {"status": "voice router is working"}


@router.get("/voices", response_model=GetVoicesResponse)
async def get_supported_voices():
    """Get list of supported TTS voices and avatar-voice pairs - no auth required"""
    return GetVoicesResponse(
        voices=SUPPORTED_VOICES,
        avatar_pairs=[
            AvatarVoicePair(avatar_id="sophia", avatar_name="Sophia", voice="alloy", style="professional"),
            AvatarVoicePair(avatar_id="emma", avatar_name="Emma", voice="echo", style="friendly"),
            AvatarVoicePair(avatar_id="james", avatar_name="James", voice="fable", style="professional"),
            AvatarVoicePair(avatar_id="aria", avatar_name="Aria", voice="nova", style="elegant"),
            AvatarVoicePair(avatar_id="default", avatar_name="Default", voice="shimmer", style="casual"),
        ],
        recommendations=VOICE_RECOMMENDATIONS
    )


@router.get("/avatar/{avatar_id}", response_model=VoiceForAvatarResponse)
async def get_voice_for_avatar(avatar_id: str):
    """Get the voice configuration for a specific avatar"""
    avatar_id_lower = avatar_id.lower()
    voice_id = AVATAR_VOICE_MAP.get(avatar_id_lower, "alloy")
    
    return VoiceForAvatarResponse(
        avatar_id=avatar_id_lower,
        voice_id=voice_id
    )


@router.get("/health")
async def voice_health():
    """Voice service health check"""
    return {"status": "healthy", "service": "voice", "supported_voices": SUPPORTED_VOICES}
