"""
IBM Watson Text-to-Speech Integration
Generates voice responses in Indian languages
"""

import httpx
import logging
from config.settings import settings
from utils.watson_stt import _get_iam_token

logger = logging.getLogger(__name__)

# Watson TTS voice models for Indian languages
LANGUAGE_VOICES = {
    "hi": "hi-IN_MeeraV3Voice",        # Hindi female
    "ta": "en-US_MichaelV3Voice",      # Fallback to English (Tamil TTS limited)
    "te": "en-US_MichaelV3Voice",      # Fallback
    "mr": "en-US_MichaelV3Voice",      # Fallback
    "kn": "en-US_MichaelV3Voice",      # Fallback
    "bn": "en-US_MichaelV3Voice",      # Fallback
    "gu": "en-US_MichaelV3Voice",      # Fallback
    "pa": "en-US_MichaelV3Voice",      # Fallback
    "en": "en-US_MichaelV3Voice",      # English
}

# Preferred: hi-IN_MeeraV3Voice, hi-IN_KavyaV3Voice for Hindi
# When more IBM regional voices are available, update this map


async def synthesize_speech(text: str, language: str = "hi") -> bytes:
    """
    Convert text to speech using IBM Watson TTS.
    Returns audio bytes (mp3).
    """
    try:
        voice = LANGUAGE_VOICES.get(language, "en-US_MichaelV3Voice")

        # Truncate for TTS (Watson limit is 5000 chars)
        text_to_speak = text[:4900] if len(text) > 4900 else text

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.IBM_TTS_URL}/v1/synthesize",
                headers={
                    "Authorization": f"Bearer {_get_iam_token(settings.IBM_TTS_API_KEY)}",
                    "Content-Type": "application/json",
                    "Accept": "audio/mp3"
                },
                json={
                    "text": text_to_speak,
                    "voice": voice
                },
                timeout=30
            )

            if response.status_code == 200:
                logger.info(f"TTS generated {len(response.content)} bytes for [{language}]")
                return response.content

    except Exception as e:
        logger.error(f"TTS failed: {e}")

    return b""
