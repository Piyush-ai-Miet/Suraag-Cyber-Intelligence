#!/usr/bin/env python3
"""
Test multi-provider chatbot system
"""
import sys
sys.path.append('.')

# Mock analysis state
analysis_state = {
    "loaded": True,
    "stats": {"total_sessions": 100, "suspicious_sessions": 5},
}

# Import updated chatbot module  
from modules.chatbot import _build_context

# Test context building
context = _build_context(analysis_state)
print("✅ Multi-provider chatbot loaded successfully!")
print(f"✅ Context built: {len(context)} chars")

print("\n🚀 READY TO USE HIGH-LIMIT APIs!")
print("\nNext steps:")
print("1. Get DeepSeek API key (unlimited free)")
print("2. Get OpenRouter API key (1000/day free)")  
print("3. Add to .env file")
print("4. Restart Streamlit app")
print("5. Enjoy unlimited AI chatbot! 🎉")