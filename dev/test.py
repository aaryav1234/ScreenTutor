import os
from openai import OpenAI

# OpenRouter Configuration
MODEL = "google/gemini-2.0-flash-001" 
API_KEY = os.environ.get("OPENROUTER_API_KEY")

if not API_KEY:
    print("Error: Set OPENROUTER_API_KEY environment variable")
    exit(1)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)

response = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "Explain photosynthesis in 2 lines"}]
)

print(response.choices[0].message.content)
