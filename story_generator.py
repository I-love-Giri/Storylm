import json


def generate_story(client, story_plan):

    story_plan_json = json.dumps(story_plan, indent=2)

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
                "content": f"Here is the story plan:\n\n{story_plan_json}",
            },
        ],
    )

    return response.choices[0].message.content
