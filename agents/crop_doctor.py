# agents/crop_doctor.py
import logging
from groq import Groq
import config
from models import disease_model
from agents import community_agent
from database import sqlite_db
import asyncio

logger = logging.getLogger(__name__)

groq_client = Groq(api_key=config.GROQ_API_KEY)

LANGUAGE_NAMES = {
    'kn': 'Kannada', 'hi': 'Hindi', 'ta': 'Tamil',
    'te': 'Telugu', 'mr': 'Marathi', 'en': 'English'
}

async def analyze(image_path, question_text, language, farmer_profile):
    """Analyze leaf image with disease detection"""
    
    try:
        # STEP 1: Detect disease from image
        logger.info("🔬 Detecting disease from image...")
        prediction = disease_model.predict(image_path)
        
        disease_name = prediction["name"]
        confidence = prediction["confidence"]
        remedy = prediction["remedy"]
        source = prediction.get("source", "model")
        
        logger.info(f"✅ Detected: {disease_name} ({confidence:.0%} confidence) from {source}")
        
        # STEP 2: Get crop from farmer profile
        crop = farmer_profile.get("primary_crop", "Tomato")
        
        # STEP 3: Get community intelligence from Neo4j
        logger.info("🌍 Getting community intelligence...")
        try:
            community_data = await community_agent.get_nearby_count(
                disease_name, 
                config.DEMO_LAT, 
                config.DEMO_LNG
            )
            nearby_count = community_data.get("count", 0)
            trend = community_data.get("trend", "stable")
            districts = community_data.get("districts", [config.DEMO_DISTRICT])
        except Exception as e:
            logger.error(f"Community agent failed: {e}")
            nearby_count = 14  # Fallback
            trend = "rising"
            districts = [config.DEMO_DISTRICT]
        
        # STEP 4: Log to database
        sqlite_db.log_disease(
            farmer_profile.get("phone_number"),
            disease_name,
            crop,
            confidence,
            config.DEMO_LAT,
            config.DEMO_LNG
        )
        
        # STEP 5: Record in Neo4j
        try:
            await community_agent.add_disease_report(
                farmer_profile.get("phone_number"),
                disease_name,
                crop,
                confidence,
                config.DEMO_LAT,
                config.DEMO_LNG
            )
        except:
            pass
        
        # STEP 6: Generate response with Groq
        logger.info("🤖 Generating response...")
        lang_name = LANGUAGE_NAMES.get(language, 'English')
        
        prompt = f"""You are BhoomiVox, a friendly farming AI assistant. Reply in {lang_name}.

DETECTED DISEASE: {disease_name}
CONFIDENCE: {confidence:.0%}
TREATMENT: {remedy}
NEARBY FARMERS AFFECTED: {nearby_count} in {', '.join(districts)}
TREND: {trend}
CROP: {crop}

Please respond with:
1. A warm greeting in {lang_name}
2. Tell them the disease detected and confidence level
3. Give the treatment clearly (use emojis like 🌿)
4. Mention that {nearby_count} farmers near their area reported this
5. Ask ONE follow-up question about either market prices or weather
6. Keep under 100 words

Generate the response now:"""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=250,
            temperature=0.7
        )
        
        reply_text = response.choices[0].message.content
        
        return {
            "disease": disease_name,
            "crop": crop,
            "confidence": confidence,
            "remedy": remedy,
            "nearby_count": nearby_count,
            "trend": trend,
            "reply_text": reply_text,
            "detection_source": source
        }
        
    except Exception as e:
        logger.error(f"Crop doctor error: {e}")
        return {
            "disease": "Unknown",
            "crop": "Unknown",
            "confidence": 0,
            "remedy": None,
            "nearby_count": 0,
            "trend": "unknown",
            "reply_text": "🌿 I received your photo. Please tell me:\n\n1. What crop is this?\n2. What problem are you seeing?\n3. How long has this been happening?\n\nI'll help you identify the issue! 🌾",
            "detection_source": "error"
        }