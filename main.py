from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

# story_idea = input("What kind of story do you want? ")


def get_story_idea():
    story_idea = input("What kind of story do you want? ")
    return story_idea


def generate_story(story_idea):
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {
                "role": "system",
                "content": "You are a professional horror story writer. Write atmospheric and suspenseful stories.",
            },
            {
                "role": "user",
                "content": f"Write a short and scary story based on this idea: {story_idea}",
            },
        ],
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    story_idea = get_story_idea()
    story = generate_story(story_idea)

    print("\n--- YOUR STORY ---\n")
    print(story)
