# 🚀 API Keys Setup Instructions

## Step 1: Get API Keys

### DeepSeek (UNLIMITED FREE!) ⭐
1. Go to: https://platform.deepseek.com/api_keys
2. Sign up with Google/GitHub
3. Create API Key
4. Copy the key (starts with sk-)

### OpenRouter (1000/day FREE)
1. Go to: https://openrouter.ai/keys
2. Sign up for free
3. Create API Key  
4. Copy the key (starts with sk-)

## Step 2: Add Keys to .env File

Open the `.env` file in your project and add:

```
# DeepSeek API (Unlimited free!)
DEEPSEEK_API_KEY=sk-your-deepseek-key-here

# OpenRouter API (1000/day free)
OPENROUTER_API_KEY=sk-your-openrouter-key-here
```

## Step 3: Restart App

After adding keys, restart your Streamlit app:
- Stop current app (Ctrl+C)
- Run: `streamlit run app.py`

## What You'll Get:

✅ **DeepSeek**: Unlimited free requests per day
✅ **OpenRouter**: 1000+ free requests per day  
✅ **Smart Fallback**: If one fails, tries the other
✅ **No More Quota Issues**: Never run out of requests!

## Current Status:
Your app is running at: http://localhost:8501
Just add the API keys and enjoy unlimited AI chatbot!