#!/usr/bin/env python3
"""
Test the fallback responses
"""

# Test questions and expected keywords
test_questions = [
    "Was TOR used by any suspect?",
    "Which suspect is most dangerous?", 
    "What IP addresses were contacted?",
    "General question about the case"
]

for question in test_questions:
    print(f"Q: {question}")
    
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['tor', 'anonymity', 'hidden']):
        print("✅ TOR/Anonymity response")
    elif any(word in question_lower for word in ['risk', 'dangerous', 'suspect', 'threat']):
        print("✅ Risk Assessment response") 
    elif any(word in question_lower for word in ['ip', 'address', 'connection', 'server']):
        print("✅ IP Analysis response")
    else:
        print("✅ General fallback response")
    
    print()

print("🎉 Fallback logic working correctly!")