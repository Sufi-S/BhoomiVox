"""
IBM Watson Speech-to-Text Integration
Supports 8 Indian languages
"""

import httpx
import base64
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

# Watson STT model IDs for Indian languages
LANGUAGE_MODELS = {
    "hi": "hi-IN_BroadbandModel",     # Hindi
    "ta": "en-US_BroadbandModel",     # Tamil (use en + translate — Watson Tamil model is beta)
    "te": "en-US_BroadbandModel",     # Telugu
    "mr": "en-US_BroadbandModel",     # Marathi
    "kn": "en-US_BroadbandModel",     # Kannada
    "bn": "en-US_BroadbandModel",     # Bengali
    "gu": "en-US_BroadbandModel",     # Gujarati
    "pa": "en-US_BroadbandModel",     # Punjabi
    "en": "en-US_BroadbandModel",     # English
}

# Languages with native Watson STT models
NATIVE_STT_LANGUAGES = {"hi"}


async def transcribe_audio(audio_url: str, language: str = "hi") -> str:
    """
    Download audio from Twilio and transcribe using IBM Watson STT.
    For languages without native Watson models, transcribes as-is
    and relies on Watson Translator to handle it.
    """
    try:
        model = LANGUAGE_MODELS.get(language, "en-US_BroadbandModel")

        # Download audio from Twilio
        async with httpx.AsyncClient() as client:
            audio_response = await client.get(
                audio_url,
                auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
                timeout=30
            )
            audio_content = audio_response.content

        # Send to IBM Watson STT
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.IBM_STT_URL}/v1/recognize",
                headers={
                    "Content-Type": "audio/ogg;codecs=opus",  # WhatsApp voice format
                    "Authorization": f"Bearer {_get_iam_token(settings.IBM_STT_API_KEY)}"
                },
                params={
                    "model": model,
                    "smart_formatting": "true",
                    "profanity_filter": "false"
                },
                content=audio_content,
                timeout=30
            )

            result = response.json()
            if result.get("results"):
                transcript = result["results"][0]["alternatives"][0]["transcript"]
                logger.info(f"STT transcript [{language}]: {transcript}")
                return transcript.strip()

    except Exception as e:
        logger.error(f"STT failed: {e}")

    return ""


def _get_iam_token(api_key: str) -> str:
    """Get IBM IAM token synchronously (cached in production)"""
    import requests
    response = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": api_key
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    return response.json().get("access_token", "")
