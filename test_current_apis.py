#!/usr/bin/env python3
"""
Test current API configuration
"""
import sys
sys.path.append('.')

from config import GEMINI_API_KEY, DEEPSEEK_API_KEY, OPENROUTER_API_KEY

print("🔍 CURRENT API STATUS CHECK")
print("=" * 40)

print(f"\n✅ Gemini API Key: {GEMINI_API_KEY[:20]}..." if GEMINI_API_KEY else "❌ Gemini API Key: Missing")
print(f"✅ DeepSeek API Key: {DEEPSEEK_API_KEY[:20]}..." if DEEPSEEK_API_KEY else "❌ DeepSeek API Key: Missing")  
print(f"✅ OpenRouter API Key: {OPENROUTER_API_KEY[:20]}..." if OPENROUTER_API_KEY else "❌ OpenRouter API Key: Missing")

print(f"\n🧪 TESTING GEMINI API...")

try:
    from google import genai as google_genai
    client = google_genai.Client(api_key=GEMINI_API_KEY)
    
    # Try different models
    models_to_test = [
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash", 
        "gemini-3.5-flash"
    ]
    
    for model in models_to_test:
        try:
            print(f"   Testing {model}...")
            response = client.models.generate_content(
                model=model,
                contents="Hello! Test from Suराग IPDR tool.",
            )
            answer = response.text.strip()
            print(f"   ✅ {model}: Working! Response: {answer[:50]}...")
            break
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                print(f"   ⚠️ {model}: Quota exceeded")
            elif "503" in error_msg or "UNAVAILABLE" in error_msg:
                print(f"   ⚠️ {model}: High demand")
            else:
                print(f"   ❌ {model}: {error_msg[:50]}...")
    else:
        print("   ❌ All Gemini models failed")
        
except Exception as e:
    print(f"   ❌ Gemini import error: {e}")

print(f"\n💡 RECOMMENDATION:")
print(f"   Your Gemini API should work with fallback system!")
print(f"   App URL: http://localhost:8501")
print(f"   Upload IPDR file और AI chatbot try करें!")