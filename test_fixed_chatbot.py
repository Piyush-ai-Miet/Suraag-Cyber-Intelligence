#!/usr/bin/env python3
"""
Test the fixed chatbot logic
"""
import sys
sys.path.append('.')

# Mock analysis state
analysis_state = {
    "loaded": True,
    "stats": {"total_sessions": 100},
}

# Import chatbot module
from modules.chatbot import _build_context

# Test context building
context = _build_context(analysis_state)
print("Context built successfully!")
print("Context length:", len(context))

# Test model fallback
api_key = "AQ.Ab8RN6Jz62xrnUISZ02gKoSlnJXWhvAJnO-5e1iLoz3-yQCP2Q"

try:
    from google import genai as google_genai
    client = google_genai.Client(api_key=api_key)
    
    models_to_try = [
        "gemini-2.5-flash-lite",  
        "gemini-3.5-flash",       
        "gemini-2.5-flash",       
        "gemini-2.5-pro"          
    ]
    
    answer = None
    
    for model_name in models_to_try:
        try:
            print(f"Trying {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents="Hello, just testing the model!",
            )
            answer = response.text.strip()
            print(f"✅ SUCCESS with {model_name}: {answer[:50]}...")
            break
        except Exception as e:
            error_msg = str(e)
            if ("503" in error_msg or "UNAVAILABLE" in error_msg):
                print(f"❌ {model_name}: High demand, trying next...")
                continue
            elif ("429" in error_msg or "quota" in error_msg.lower()):
                print(f"❌ {model_name}: Quota exceeded, trying next...")
                continue
            else:
                print(f"❌ {model_name}: Other error - {error_msg[:100]}")
                continue
    
    if answer is None:
        print("❌ All models failed")
    else:
        print("🎉 Chatbot logic working correctly!")

except Exception as e:
    print(f"Import error: {e}")