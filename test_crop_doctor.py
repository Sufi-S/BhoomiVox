# test_crop_doctor.py
import asyncio
import os
from models import disease_model
from agents import crop_doctor

async def test():
    print("=" * 50)
    print("🧪 TESTING CROP DOCTOR SYSTEM")
    print("=" * 50)
    
    # Test 1: Model loading
    print("\n1. Testing disease model...")
    disease_model.load_model()
    print("   ✅ Model ready")
    
    # Test 2: Create a test image (if you don't have one)
    print("\n2. Creating test image...")
    from PIL import Image, ImageDraw
    
    # Create a simple test image with brown spots (simulating disease)
    img = Image.new('RGB', (224, 224), color='green')
    draw = ImageDraw.Draw(img)
    
    # Draw some brown spots (simulating disease symptoms)
    for _ in range(30):
        x = 50 + (hash(str(_)) % 150)
        y = 50 + (hash(str(_ + 10)) % 150)
        draw.ellipse([x, y, x+15, y+15], fill='brown')
    
    # Draw yellow edges (simulating nutrient deficiency)
    for _ in range(20):
        x = 10 + (hash(str(_ + 20)) % 200)
        y = 10 + (hash(str(_ + 30)) % 200)
        draw.ellipse([x, y, x+10, y+10], fill='yellow')
    
    test_image_path = "tmp/test_image.jpg"
    os.makedirs("tmp", exist_ok=True)
    img.save(test_image_path)
    print(f"   ✅ Test image created: {test_image_path}")
    
    # Test 3: Predict disease
    print("\n3. Testing disease prediction...")
    result = disease_model.predict(test_image_path)
    print(f"   ✅ Disease: {result['name']}")
    print(f"   ✅ Confidence: {result['confidence']:.0%}")
    print(f"   ✅ Remedy: {result['remedy'][:50]}...")
    
    # Test 4: Test full crop doctor (if Groq API key is set)
    print("\n4. Testing Crop Doctor with Groq AI...")
    
    farmer_profile = {
        "phone_number": "+919876543210",
        "primary_crop": "Tomato",
        "district": "Kolar"
    }
    
    try:
        response = await crop_doctor.analyze(
            test_image_path,
            "",
            "en",
            farmer_profile
        )
        
        print("\n" + "=" * 50)
        print("📋 CROP DOCTOR RESPONSE:")
        print("=" * 50)
        print(f"🌿 Disease: {response['disease']}")
        print(f"📊 Confidence: {response['confidence']:.0%}")
        print(f"💊 Remedy: {response['remedy']}")
        print(f"👥 Nearby affected: {response['nearby_count']} farmers")
        print(f"📈 Trend: {response['trend']}")
        print("\n🤖 AI Response:")
        print("-" * 50)
        print(response['reply_text'])
        print("-" * 50)
        
    except Exception as e:
        print(f"   ⚠️ Groq test failed: {e}")
        print("   (This is fine if GROQ_API_KEY is not set yet)")
    
    # Test 5: Clean up
    print("\n5. Cleaning up...")
    if os.path.exists(test_image_path):
        os.remove(test_image_path)
    print("   ✅ Test image deleted")
    
    print("\n" + "=" * 50)
    print("✅ TEST COMPLETE!")
    print("=" * 50)
    
    if not os.getenv("GROQ_API_KEY"):
        print("\n⚠️ Note: GROQ_API_KEY not found in environment")
        print("   The disease detection works, but AI responses need Groq API key")
        print("   Add it to .env file: GROQ_API_KEY=your_key_here")

if __name__ == "__main__":
    asyncio.run(test())