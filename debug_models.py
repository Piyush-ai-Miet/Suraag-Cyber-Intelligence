#!/usr/bin/env python3
"""
Debug script to test individual Gemini models
"""

api_key = "AQ.Ab8RN6Jz62xrnUISZ02gKoSlnJXWhvAJnO-5e1iLoz3-yQCP2Q"

models_to_test = [
    "gemini-2.5-flash-lite",
    "gemini-3.5-flash", 
    "gemini-2.5-flash",
    "gemini-2.5-pro"
]

print("Testing Gemini Models...")
print("=" * 50)

try:
    from google import genai as google_genai
    client = google_genai.Client(api_key=api_key)
    
    for model_name in models_to_test:
        print(f"\n🧪 Testing: {model_name}")
        try:
            response = client.models.generate_content(
                model=model_name,
                contents="Say 'Hello from " + model_name + "'",
            )
            print(f"✅ SUCCESS: {response.text.strip()}")
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower() or "RESOURCE_EXHAUSTED" in error_msg:
                print(f"❌ QUOTA EXCEEDED: {model_name}")
            elif "503" in error_msg or "UNAVAILABLE" in error_msg:
                print(f"⚠️  HIGH DEMAND: {model_name}")
            elif "404" in error_msg or "not found" in error_msg.lower():
                print(f"🚫 MODEL NOT FOUND: {model_name}")
            else:
                print(f"❓ OTHER ERROR: {error_msg[:100]}")

except ImportError:
    print("❌ Google Genai package not available")
except Exception as e:
    print(f"❌ General error: {e}")