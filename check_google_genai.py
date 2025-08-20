import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

if os.environ["GEMINI_API_KEY"] is None:
    raise ValueError("GEMINI_API_KEY not found")

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash", contents="Explain how AI works in a few words"
)
print(response.text)
