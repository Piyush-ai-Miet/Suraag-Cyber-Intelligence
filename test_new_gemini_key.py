#!/usr/bin/env python3
"""
Test new Gemini API key
"""

api_key = "AQ.Ab8RN6JRcMt2JtaGc_FNsTeuKIzpDqljfhYNT2HB3q3BdSXWoQ"

print("🧪 Testing New Gemini API Key...")
print(f"API Key: {api_key[:20]}...")

try:
    from google import genai as google_genai
    client = google_genai.Client(api_key=api_key)
    
    # Try different models
    models_to_test = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-3.5-flash"
    ]
    
    for model in models_to_test:
        try:
            print(f"\n   Testing {model}...")
            response = client.models.generate_content(
                model=model,
                contents="Hello! Test message from Suराग IPDR tool. Please respond with 'Working!'",
            )
            answer = response.text.strip()
            print(f"   ✅ SUCCESS: {answer[:80]}...")
            print(f"\n🎉 {model} is working perfectly!")
            break
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                print(f"   ⚠️ Quota exceeded for {model}")
            elif "503" in error_msg or "UNAVAILABLE" in error_msg:
                print(f"   ⚠️ High demand for {model}")
            else:
                print(f"   ❌ Error: {error_msg[:100]}")
    else:
        print("\n❌ All models failed")
        
except Exception as e:
    print(f"❌ Import error: {e}")