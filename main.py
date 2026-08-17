from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

story_idea = input("What kind of story do you want? ")

response = client.chat.completions.create(
    model="openrouter/free",
    messages=[
        {
            "role": "user",
            "content": f"Write a short and scary story based on this idea: {story_idea}",
        }
    ],
)

print("\n--- YOUR STORY ---\n")
print(response.choices[0].message.content)
