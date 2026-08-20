import json


def generate_story(client, story_plan, characters, memory: list | None = None):

    story_plan_json = json.dumps(story_plan, indent=2)
    characters_json = json.dumps(characters, indent=2)
    if memory:
        memory_json = json.dumps(memory, indent=2)
    else:
        memory_json = "No previous story memory. This is the beginning of the story."

    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {
                "role": "system",
                "content": """
                    You are a professional horror story writer.

                    Write a complete, immersive horror story using the provided story plan.

                    Rules:
                    - Follow the story plan.
                    - Keep character details consistent.
                    - Do not mention the story plan.
                    - Do not add explanations or notes after the story.
                    - Use suspense, atmosphere and vivid descriptions.
                    """,
            },
            {
                "role": "user",
                "content": f"""
                    Here is the story plan:

                    {story_plan_json}

                    Here are the characters that must remain consistent:

                    {characters_json}

                    Write the complete story.
                """,
            },
        ],
    )

    return response.choices[0].message.content
