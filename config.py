import os
from dotenv import load_dotenv
from openai import OpenAI
from google import genai

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

gemini_client = genai.Client(api_key=gemini_api_key)


if not groq_api_key:
    raise ValueError("GROQ_API_KEY was not found in the .env file.")

groq_client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=groq_api_key)
