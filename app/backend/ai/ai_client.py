import os
from openai import OpenAI
from dotenv import load_dotenv
from app.backend.ai.prompts import solve_prompt, hint_prompt

# Load .env file if it exists
load_dotenv()

# You can change this to any OpenRouter model ID
MODEL = "google/gemini-2.0-flash-001" 

API_KEY = os.environ.get("OPENROUTER_API_KEY")

# Create client only if key exists, otherwise it will be handled in the functions
client = None
if API_KEY:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=API_KEY,
    )


def ask_solution(question: str) -> str:
    if not client:
        raise Exception("API Key Missing: Please set OPENROUTER_API_KEY environment variable.")
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": solve_prompt(question)}]
    )
    return response.choices[0].message.content.strip()


def ask_hint(question: str) -> str:
    if not client:
        raise Exception("API Key Missing: Please set OPENROUTER_API_KEY environment variable.")
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": hint_prompt(question)}]
    )
    return response.choices[0].message.content.strip()


def generate_practice_questions(history: list, count=10) -> str:
    if not client:
        raise Exception("API Key Missing: Please set OPENROUTER_API_KEY environment variable.")
    history_text = "\n".join([f"- {q}" for q in history])
    
    prompt = f"""
    You are an expert educational content creator.
    
    USER HISTORY:
    {history_text}
    
    TASK:
    Generate exactly {count} practice questions similar in difficulty and topic to the history above.
    
    RULES:
    1. Do not provide answers.
    2. Format as a clean numbered list.
    3. Ensure variety.
    4. Topic should be strictly related to the history.
    """
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
