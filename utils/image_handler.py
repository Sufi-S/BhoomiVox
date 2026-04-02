# utils/image_handler.py
import requests
import os
import uuid
from requests.auth import HTTPBasicAuth
from PIL import Image
import io
import config
import logging

logger = logging.getLogger(__name__)

def download_image(media_url, account_sid, auth_token):
    """Download image from Twilio media URL"""
    try:
        os.makedirs("tmp/uploads", exist_ok=True)
        filename = f"tmp/uploads/{uuid.uuid4().hex}.jpg"
        
        response = requests.get(
            media_url,
            auth=HTTPBasicAuth(account_sid, auth_token),
            timeout=30
        )
        
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            logger.info(f"✅ Image saved: {filename}")
            return filename
        return None
    except Exception as e:
        logger.error(f"Image download error: {e}")
        return None

def preprocess_image(image_path):
    """Preprocess image for model prediction"""
    try:
        img = Image.open(image_path).convert('RGB')
        # Resize to standard size
        img = img.resize((224, 224))
        # Save processed image
        processed_path = image_path.replace('.jpg', '_processed.jpg')
        img.save(processed_path)
        return processed_path
    except Exception as e:
        logger.error(f"Preprocess error: {e}")
        return image_path

def get_image_info(image_path):
    """Get image metadata"""
    try:
        img = Image.open(image_path)
        return {
            "width": img.width,
            "height": img.height,
            "format": img.format,
            "size_kb": os.path.getsize(image_path) / 1024
        }
    except:
        return {}