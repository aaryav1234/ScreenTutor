import os
import requests

API_KEY = os.environ.get("OPENROUTER_API_KEY")

if not API_KEY:
    print("❌ Error: OPENROUTER_API_KEY not found in environment variables.")
    print("Please run: export OPENROUTER_API_KEY='your_key_here'")
    exit(1)

print("Checking OpenRouter connection...")

try:
    response = requests.get(
        url="https://openrouter.ai/api/v1/models",
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    
    if response.status_code == 200:
        models = response.json().get('data', [])
        print(f"✅ Success! Your key is valid. Found {len(models)} available models.")
        print("\nTop recommended models for ScreenTutor:")
        # List a few popular ones
        featured = ["google/gemini-2.0-flash-001", "anthropic/claude-3.5-sonnet", "openai/gpt-4o-mini"]
        for m in models:
            if m['id'] in featured:
                print(f"- {m['id']}")
    else:
        print(f"❌ API Error: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"❌ Connection Error: {e}")
