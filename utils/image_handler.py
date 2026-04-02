# utils/image_handler.py
import requests
import os
import uuid
from requests.auth import HTTPBasicAuth
from PIL import Image, ImageEnhance
import config
import logging

logger = logging.getLogger(__name__)

def download_image(media_url, account_sid, auth_token):
    """Download image from Twilio media URL"""
    try:
        # Create uploads directory if it doesn't exist
        os.makedirs("tmp/uploads", exist_ok=True)
        
        # Generate unique filename
        filename = f"tmp/uploads/{uuid.uuid4().hex}.jpg"
        
        logger.info(f"📥 Downloading image from: {media_url}")
        
        # Download image from Twilio
        response = requests.get(
            media_url,
            auth=HTTPBasicAuth(account_sid, auth_token),
            timeout=30
        )
        
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            # Enhance image quality for better detection
            enhance_image(filename)
            
            file_size = os.path.getsize(filename) / 1024
            logger.info(f"✅ Image saved: {filename} ({file_size:.1f} KB)")
            return filename
        else:
            logger.error(f"Failed to download image. Status: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Image download error: {e}")
        return None

def enhance_image(image_path):
    """Enhance image quality for better disease detection"""
    try:
        img = Image.open(image_path)
        
        # Enhance contrast (makes spots more visible)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        
        # Enhance sharpness (clearer edges)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.3)
        
        # Enhance color (better disease color detection)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.2)
        
        # Save enhanced image
        img.save(image_path, quality=95)
        logger.info(f"✅ Image enhanced: {image_path}")
        
    except Exception as e:
        logger.error(f"Image enhancement error: {e}")

def get_image_info(image_path):
    """Get image metadata for logging"""
    try:
        img = Image.open(image_path)
        return {
            "width": img.width,
            "height": img.height,
            "format": img.format,
            "mode": img.mode,
            "size_kb": os.path.getsize(image_path) / 1024
        }
    except Exception as e:
        logger.error(f"Image info error: {e}")
        return {}

def delete_image(image_path):
    """Delete image after processing to save space"""
    try:
        if os.path.exists(image_path):
            os.remove(image_path)
            logger.info(f"🗑️ Deleted: {image_path}")
            return True
    except Exception as e:
        logger.error(f"Delete error: {e}")
    return False

def validate_image(image_path):
    """Check if image is valid and readable"""
    try:
        img = Image.open(image_path)
        img.verify()  # Verify integrity
        return True
    except Exception as e:
        logger.error(f"Invalid image: {e}")
        return False