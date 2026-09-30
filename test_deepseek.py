#!/usr/bin/env python3
"""
Test DeepSeek API directly
"""

import requests
import json

api_key = "sk-205827c8d8cd415285d0b71187760177"

print("🚀 Testing DeepSeek API...")
print("API Key:", api_key[:20] + "...")

try:
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "Hello! Test message from Suराग IPDR Investigation Tool."}],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    print("Making API request...")
    response = requests.post(url, headers=headers, json=data, timeout=30)
    
    print("Response Status:", response.status_code)
    
    if response.status_code == 200:
        result = response.json()
        answer = result["choices"][0]["message"]["content"]
        print("✅ SUCCESS!")
        print("Response:", answer)
        print("\n🎉 DeepSeek API is working! Your chatbot now has UNLIMITED requests!")
    else:
        print("❌ ERROR:", response.status_code)
        print("Response:", response.text)
        
except Exception as e:
    print("❌ Exception:", str(e))