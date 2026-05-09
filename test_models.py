from google import genai
import os

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY", ""))
try:
    for model in client.models.list():
        print(model.name)
except Exception as e:
    print(e)
