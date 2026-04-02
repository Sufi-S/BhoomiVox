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

# Language codes for responses
LANGUAGE_NAMES = {
    'kn': 'Kannada',
    'hi': 'Hindi', 
    'ta': 'Tamil',
    'te': 'Telugu',
    'mr': 'Marathi',
    'en': 'English'
}

async def analyze(image_path, question_text, language, farmer_profile):
    """
    Complete crop doctor analysis with:
    - Disease detection
    - Remedy (chemical + organic)
    - Community intelligence from Neo4j
    - Personalized response using Groq
    """
    
    try:
        # Step 1: Detect disease from image
        logger.info("🔬 Step 1: Detecting disease from image...")
        prediction = disease_model.predict(image_path)
        
        disease_name = prediction["name"]
        crop = prediction["crop"]
        symptoms = prediction["symptoms"]
        remedy_chemical = prediction["remedy"]
        remedy_organic = prediction["organic"]
        confidence = prediction["confidence"]
        severity = prediction["severity"]
        
        logger.info(f"✅ Disease detected: {disease_name} ({confidence:.0%} confidence)")
        
        # Step 2: Get farmer's crop preference from memory
        primary_crop = farmer_profile.get("primary_crop", crop)
        if primary_crop != crop:
            # Update farmer's crop if detected
            sqlite_db.update_farmer_crop(farmer_profile.get("phone_number"), crop)
        
        # Step 3: Get community intelligence from Neo4j
        logger.info("🌍 Step 2: Getting community intelligence...")
        try:
            community_data = await community_agent.get_nearby_count(
                disease_name, 
                config.DEMO_LAT, 
                config.DEMO_LNG
            )
            nearby_count = community_data.get("count", 0)
            trend = community_data.get("trend", "stable")
            affected_districts = community_data.get("districts", [config.DEMO_DISTRICT])
        except Exception as e:
            logger.error(f"Community agent failed: {e}")
            nearby_count = 0
            trend = "unknown"
            affected_districts = [config.DEMO_DISTRICT]
        
        # Step 4: Log this disease detection to database
        sqlite_db.log_disease(
            farmer_profile.get("phone_number"),
            disease_name,
            crop,
            confidence,
            config.DEMO_LAT,
            config.DEMO_LNG
        )
        
        # Step 5: Record in Neo4j for future community data
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
        
        # Step 6: Generate response using Groq
        logger.info("🤖 Step 3: Generating response with Groq...")
        
        lang_name = LANGUAGE_NAMES.get(language, 'Kannada')
        
        # Build the prompt for Groq
        prompt = f"""You are BhoomiVox, a friendly and practical farming AI assistant. 
Reply in {lang_name} language only.

DETECTION RESULTS:
- Disease: {disease_name}
- Crop: {crop}
- Confidence: {confidence:.0%}
- Severity: {severity}

SYMPTOMS:
{symptoms}

REMEDIES:
Chemical: {remedy_chemical}
Organic: {remedy_organic}

COMMUNITY INTELLIGENCE:
- {nearby_count} farmers near {config.DEMO_DISTRICT} reported the same disease
- Trend: {trend}
- Affected areas: {', '.join(affected_districts)}

YOUR RESPONSE MUST:
1. Start with a warm greeting in {lang_name}
2. Clearly state the disease name and confidence
3. Give the chemical remedy in simple steps
4. Give the organic alternative
5. Mention the community alert ({nearby_count} farmers nearby)
6. End with ONE relevant follow-up question (about mandi price or weather)
7. Keep under 120 words
8. Be practical and encouraging

Generate the response now:"""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7
        )
        
        reply_text = response.choices[0].message.content
        
        # Step 7: Add a helpful footer
        footer = f"\n\n📸 Send another leaf photo | 💰 Ask 'price' | 🌤️ Ask 'weather'"
        reply_text += footer
        
        logger.info(f"✅ Response generated successfully")
        
        return {
            "disease": disease_name,
            "crop": crop,
            "confidence": confidence,
            "severity": severity,
            "remedy_chemical": remedy_chemical,
            "remedy_organic": remedy_organic,
            "nearby_count": nearby_count,
            "trend": trend,
            "reply_text": reply_text,
            "symptoms": symptoms
        }
        
    except Exception as e:
        logger.error(f"❌ Crop doctor error: {e}")
        return {
            "disease": "Unknown",
            "crop": "Unknown", 
            "confidence": 0,
            "severity": "Unknown",
            "remedy_chemical": None,
            "remedy_organic": None,
            "nearby_count": 0,
            "trend": "unknown",
            "reply_text": "🌿 I received your photo but couldn't analyze it clearly. Please:\n\n1. Take a clearer photo of the affected leaf\n2. Tell me your crop name\n3. Describe what you're seeing\n\nI'm here to help you, farmer! 🌾",
            "symptoms": None
        }

async def analyze_batch(image_paths, language, farmer_profile):
    """Analyze multiple images and return combined result"""
    results = []
    for path in image_paths:
        result = await analyze(path, "", language, farmer_profile)
        results.append(result)
    return results

def get_quick_advice(crop_name, problem):
    """Quick advice without image"""
    crop_lower = crop_name.lower()
    problem_lower = problem.lower()
    
    # Find matching disease
    all_diseases = disease_model.get_all_diseases()
    matching = [d for d in all_diseases if d["crop"].lower() == crop_lower]
    
    if matching:
        disease_info = disease_model.get_disease_by_name(matching[0]["name"])
        return f"""🌿 *Quick Advice for {crop_name.title()}*

Based on your description of "{problem}":

📋 {disease_info['symptoms'][:150]}

💊 Remedy: {disease_info['remedy'][:200]}

Send a photo of the affected leaf for accurate diagnosis! 📸"""
    else:
        return f"""🌿 *Advice for {crop_name.title()}*

For accurate diagnosis, please:
1. Send a CLEAR PHOTO of the affected leaf
2. Tell me how long you've seen the problem
3. Describe any pests you see

I'll identify the disease and give you the exact remedy! 🌾"""