import os

from dotenv import load_dotenv
from google import genai

load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY")

print("Key found:", bool(api_key))
print("Key length:", len(api_key) if api_key else 0)

if not api_key:
    raise RuntimeError("GEMINI_API_KEY not found")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="Reply with exactly: GEMINI TEST OK"
)

print("\nSUCCESS!")
print(response.text)