# config.py
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# ============= MODE =============
MODE = os.getenv('MODE', 'groq')

# ============= DEMO LOCATION =============
DEMO_LAT = 13.1357
DEMO_LNG = 78.1326
DEMO_DISTRICT = 'Kolar'
DEMO_STATE = 'Karnataka'

# ============= APP SETTINGS =============
SUPPORTED_LANGUAGES = ['ta', 'kn', 'hi', 'te', 'mr', 'en']
MAX_RESPONSE_SECONDS = 8
COMMUNITY_RADIUS_KM = 50
DISEASE_CONFIDENCE_THRESHOLD = 0.50

# ============= API KEYS =============
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')

# HuggingFace (for disease detection)
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY', '')

# OpenWeatherMap
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', '')

# Twilio
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')

# Neo4j
NEO4J_URI = os.getenv('NEO4J_URI', '')
NEO4J_USERNAME = os.getenv('NEO4J_USERNAME', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', '')

# ============= VALIDATION =============
def validate_config():
    """Check if required keys are present"""
    missing = []
    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY")
    if not TWILIO_ACCOUNT_SID:
        missing.append("TWILIO_ACCOUNT_SID")
    if not OPENWEATHER_API_KEY:
        missing.append("OPENWEATHER_API_KEY")
    
    if missing:
        print(f"⚠️ Missing API keys: {', '.join(missing)}")
        return False
    return True

# Print status on import
print("📋 Config loaded:")
print(f"   Mode: {MODE}")
print(f"   Location: {DEMO_DISTRICT}, {DEMO_STATE}")
print(f"   Groq API: {'✅' if GROQ_API_KEY else '❌'}")
print(f"   HuggingFace: {'✅' if HUGGINGFACE_API_KEY else '⚠️ (optional)'}")
print(f"   Twilio: {'✅' if TWILIO_ACCOUNT_SID else '❌'}")
print(f"   OpenWeather: {'✅' if OPENWEATHER_API_KEY else '❌'}")
print(f"   Neo4j: {'✅' if NEO4J_URI else '⚠️ (optional)'}")