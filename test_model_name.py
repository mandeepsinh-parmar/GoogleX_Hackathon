from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY", ""))
try:
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="Hello"
    )
    print("Response for gemini-1.5-flash:", response.text)
except Exception as e:
    print("Error 1.5-flash:", e)

try:
    response = client.models.generate_content(
        model="gemini-1.5-pro",
        contents="Hello"
    )
    print("Response for gemini-1.5-pro:", response.text)
except Exception as e:
    print("Error 1.5-pro:", e)
