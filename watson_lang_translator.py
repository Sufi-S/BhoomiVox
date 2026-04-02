"""
IBM Watson Language Translator Integration
Bidirectional translation: regional ↔ English
"""

import httpx
import logging
from config.settings import settings
from utils.watson_stt import _get_iam_token

logger = logging.getLogger(__name__)

# IBM Watson Language Translator model IDs
TO_ENGLISH = {
    "hi": "hi-en",   # Hindi → English
    "ta": "ta-en",   # Tamil → English
    "te": "te-en",   # Telugu → English
    "mr": "mr-en",   # Marathi → English
    "kn": "kn-en",   # Kannada → English
    "bn": "bn-en",   # Bengali → English
    "gu": "gu-en",   # Gujarati → English
    "pa": "pa-en",   # Punjabi → English
    "en": None,      # Already English
}

FROM_ENGLISH = {
    "hi": "en-hi",
    "ta": "en-ta",
    "te": "en-te",
    "mr": "en-mr",
    "kn": "en-kn",
    "bn": "en-bn",
    "gu": "en-gu",
    "pa": "en-pa",
    "en": None,
}


async def _translate(text: str, model_id: str) -> str:
    """Core translation function using IBM Watson Language Translator"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.IBM_TRANSLATOR_URL}/v3/translate",
                params={"version": "2018-05-01"},
                headers={
                    "Authorization": f"Bearer {_get_iam_token(settings.IBM_TRANSLATOR_API_KEY)}",
                    "Content-Type": "application/json"
                },
                json={
                    "text": [text],
                    "model_id": model_id
                },
                timeout=15
            )
            result = response.json()
            translated = result["translations"][0]["translation"]
            return translated.strip()
    except Exception as e:
        logger.error(f"Translation failed [{model_id}]: {e}")
        return text  # Return original if translation fails


async def translate_to_english(text: str, language: str) -> str:
    """Translate regional language text to English for AI processing"""
    if language == "en" or not text:
        return text
    model_id = TO_ENGLISH.get(language)
    if not model_id:
        return text
    return await _translate(text, model_id)


async def translate_from_english(text: str, language: str) -> str:
    """Translate English AI response back to farmer's regional language"""
    if language == "en" or not text:
        return text
    model_id = FROM_ENGLISH.get(language)
    if not model_id:
        return text
    return await _translate(text, model_id)
