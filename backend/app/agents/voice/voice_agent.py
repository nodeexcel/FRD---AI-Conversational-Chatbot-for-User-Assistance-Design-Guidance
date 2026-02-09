# Voice Agent for Speech-to-Text and Text-to-Speech
import os
import base64
import logging
from typing import Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


# Avatar to Voice Mapping
AVATAR_VOICE_MAP = {
    "sophia": "alloy",
    "emma": "echo", 
    "james": "fable",
    "aria": "nova",
    "default": "shimmer",
    "alloy": "alloy",
    "echo": "echo",
    "fable": "fable",
    "onyx": "onyx",
    "nova": "nova",
    "shimmer": "shimmer",
}

# Voice Style Recommendations
VOICE_RECOMMENDATIONS = {
    "professional": "alloy",
    "casual": "nova", 
    "friendly": "shimmer",
    "authoritative": "onyx",
    "storytelling": "fable",
    "elegant": "nova",
    "default": "shimmer",
}

# Supported Voices
SUPPORTED_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]


class VoiceAgent:
    """Handles speech-to-text (STT) and text-to-speech (TTS) operations"""
    
    def __init__(self, openai_client: OpenAI):
        self.client = openai_client
        self.stt_model = "whisper-1"
        self.tts_model = "tts-1"
        self.default_voice = "alloy"
    
    def get_voice_for_avatar(self, avatar_id: Optional[str] = None) -> str:
        """
        Get the appropriate TTS voice for a given avatar
        
        Args:
            avatar_id: The avatar ID selected by the user
            
        Returns:
            The OpenAI TTS voice to use
        """
        if not avatar_id:
            return self.default_voice
        
        # Check if it's a direct voice ID
        if avatar_id in SUPPORTED_VOICES:
            return avatar_id
        
        # Map avatar to voice
        return AVATAR_VOICE_MAP.get(avatar_id, self.default_voice)
    
    def get_avatar_for_voice(self, voice_id: str) -> Optional[str]:
        """Reverse lookup: get avatar ID for a voice"""
        for avatar, voice in AVATAR_VOICE_MAP.items():
            if voice == voice_id and avatar not in SUPPORTED_VOICES:
                return avatar
        return None
    
    async def transcribe_audio(self, audio_data: str) -> str:
        """
        Convert audio to text using OpenAI Whisper
        
        Args:
            audio_data: Base64 encoded audio data or file path
        
        Returns:
            Transcribed text
        """
        try:
            # Handle base64 audio data
            if audio_data.startswith("data:audio"):
                # Extract base64 portion
                audio_data = audio_data.split(",")[1]
                audio_bytes = base64.b64decode(audio_data)
                
                # Save to temporary file
                temp_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "temp")
                os.makedirs(temp_dir, exist_ok=True)
                audio_path = os.path.join(temp_dir, "audio_input.wav")
                
                with open(audio_path, "wb") as f:
                    f.write(audio_bytes)
            else:
                audio_path = audio_data
            
            # Transcribe using Whisper
            with open(audio_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model=self.stt_model,
                    file=audio_file
                )
            
            transcribed_text = response.text
            logger.info(f"Transcribed audio to text: {transcribed_text}")
            
            # Clean up temp file
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            return transcribed_text
            
        except Exception as e:
            logger.error(f"Speech-to-text error: {e}")
            raise Exception(f"Failed to transcribe audio: {str(e)}")
    
    async def text_to_speech(
        self, 
        text: str, 
        voice: Optional[str] = None,
        speed: float = 1.0,
        avatar_id: Optional[str] = None
    ) -> str:
        """
        Convert text to speech using OpenAI TTS
        
        Args:
            text: Text to convert to speech
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            speed: Speech speed (0.25 to 4.0)
            avatar_id: Avatar ID to get voice for (overrides voice param)
        
        Returns:
            Base64 encoded audio data
        """
        try:
            # Get voice from avatar if provided
            if avatar_id:
                voice = self.get_voice_for_avatar(avatar_id)
            elif not voice:
                voice = self.default_voice
            
            # Validate voice
            if voice not in SUPPORTED_VOICES:
                voice = self.default_voice
            
            response = self.client.audio.speech.create(
                model=self.tts_model,
                voice=voice,
                input=text,
                speed=speed
            )
            
            # Get audio content
            audio_content = response.content
            
            # Convert to base64
            audio_base64 = base64.b64encode(audio_content).decode('utf-8')
            
            logger.info(f"Generated speech with voice '{voice}' for text: {text[:50]}...")
            
            return audio_base64
            
        except Exception as e:
            logger.error(f"Text-to-speech error: {e}")
            raise Exception(f"Failed to generate speech: {str(e)}")
    
    def get_supported_voices(self) -> list:
        """Get list of supported TTS voices"""
        return SUPPORTED_VOICES
    
    def get_voice_recommendations(self, use_case: str) -> str:
        """Get recommended voice based on use case"""
        return VOICE_RECOMMENDATIONS.get(use_case, VOICE_RECOMMENDATIONS["default"])
    
    def get_avatar_voice_pairs(self) -> list:
        """Get all avatar-voice pairs for frontend selection"""
        return [
            {"avatar_id": "sophia", "avatar_name": "Sophia", "voice": "alloy", "style": "professional"},
            {"avatar_id": "emma", "avatar_name": "Emma", "voice": "echo", "style": "friendly"},
            {"avatar_id": "james", "avatar_name": "James", "voice": "fable", "style": "professional"},
            {"avatar_id": "aria", "avatar_name": "Aria", "voice": "nova", "style": "elegant"},
            {"avatar_id": "default", "avatar_name": "Default", "voice": "shimmer", "style": "casual"},
        ]
