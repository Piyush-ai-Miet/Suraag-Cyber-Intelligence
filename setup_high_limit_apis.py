#!/usr/bin/env python3
"""
Setup Guide for High Limit Free AI APIs
"""

print("🚀 HIGH LIMIT AI API SETUP GUIDE")
print("=" * 50)

print("\n1️⃣ DEEPSEEK API (UNLIMITED FREE!) ⭐")
print("   Website: https://platform.deepseek.com/api_keys")
print("   Steps:")
print("   - Sign up with Google/GitHub")
print("   - Go to API Keys section") 
print("   - Create new API key")
print("   - Copy key to .env file as: DEEPSEEK_API_KEY=sk-xxx")
print("   - UNLIMITED requests per day!")

print("\n2️⃣ OPENROUTER API (1000+ FREE/DAY)")
print("   Website: https://openrouter.ai/keys")
print("   Steps:")
print("   - Sign up for free account")
print("   - Go to Keys section")
print("   - Create new API key") 
print("   - Copy key to .env file as: OPENROUTER_API_KEY=sk-xxx")
print("   - 1000+ requests per day on free models!")

print("\n3️⃣ CURRENT STATUS:")
print("   Checking your .env file...")

# Check current API keys
try:
    from config import DEEPSEEK_API_KEY, OPENROUTER_API_KEY, GEMINI_API_KEY
    
    if DEEPSEEK_API_KEY:
        print("   ✅ DeepSeek API key configured")
    else:
        print("   ❌ DeepSeek API key MISSING")
        
    if OPENROUTER_API_KEY:
        print("   ✅ OpenRouter API key configured") 
    else:
        print("   ❌ OpenRouter API key MISSING")
        
    if GEMINI_API_KEY:
        print("   ✅ Gemini API key configured")
    else:
        print("   ❌ Gemini API key MISSING")
        
except ImportError:
    print("   ❌ Config import failed")

print("\n4️⃣ RECOMMENDED ACTION:")
print("   Get DeepSeek API key first (unlimited free!)")
print("   Then get OpenRouter as backup (1000/day free)")
print("   Your chatbot will work perfectly with these!")

print("\n🎯 After adding keys, restart your Streamlit app!")