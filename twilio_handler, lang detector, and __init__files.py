"""
KisanVaani — Twilio WhatsApp Handler
Sends text and voice responses back to farmers
"""

import httpx
import base64
import logging
import tempfile
import os
from twilio.rest import Client
from config.settings import settings

logger = logging.getLogger(__name__)

_twilio_client = None


def get_twilio() -> Client:
    global _twilio_client
    if _twilio_client is None:
        _twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    return _twilio_client


async def send_whatsapp_message(to: str, message: str):
    """Send text message via WhatsApp"""
    try:
        client = get_twilio()
        msg = client.messages.create(
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to if to.startswith("whatsapp:") else f"whatsapp:{to}",
            body=message[:1600]  # WhatsApp limit
        )
        logger.info(f"Message sent to {to}: {msg.sid}")
        return msg.sid
    except Exception as e:
        logger.error(f"Failed to send WhatsApp message: {e}")


async def send_whatsapp_voice(to: str, text_fallback: str, audio_bytes: bytes):
    """Send voice note + text fallback via WhatsApp"""
    try:
        client = get_twilio()

        # If audio bytes available, we send text (Twilio sandbox has limited media support)
        # In production: upload audio to S3/Cloudflare R2 and send media_url
        # For hackathon: send text response (voice handled client-side)
        msg = client.messages.create(
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to if to.startswith("whatsapp:") else f"whatsapp:{to}",
            body=f"🎙️ {text_fallback[:1500]}"
        )
        logger.info(f"Voice response sent to {to}: {msg.sid}")
        return msg.sid
    except Exception as e:
        logger.error(f"Failed to send voice response: {e}")
