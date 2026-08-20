import json


def update_memory(client, story, characters):
    characters_json = json.dumps(characters, indent=2)

    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {
                "role": "system",
                "content": """
                    You are a story continuity manager.

                    Analyze the provided story and update the character memory.

                    For each character, identify:
                    - Current state
                    - Important events that happened to them
                    - Important relationships or changes

                    Return only valid JSON.
                """,
            },
            {
                "role": "user",
                "content": f"""
                    Here are the existing characters:

                    {characters_json}

                    Here is the newly generated story:

                    {story}

                    Update the character memory based on what happened
                    in the story.
                """,
            },
        ],
    )

    return response.choices[0].message.content
