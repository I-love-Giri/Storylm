import json
import time


def generate_story(client, story_plan, characters, chapter, memory: list | None = None):

    story_plan_json = json.dumps(story_plan, indent=2)
    characters_json = json.dumps(characters, indent=2)

    if memory is not None:
        memory_json = json.dumps(memory, indent=2)
        story_instruction = f"""
            This is Chapter {chapter}.

            Continue directly from the previous chapter.

            Use the current memory to maintain continuity.
            Develop the existing conflict.

            Do NOT restart the story.
            Do NOT repeat previous events.
            Do NOT resolve the overall story unless the story
            has naturally reached its final stage.

            End with a meaningful development or hook.
        """
    else:
        memory_json = "No previous story memory. This is the beginning of the story."
        story_instruction = """
            This is Chapter 1.

            Establish the setting, characters and main conflict.

            Do NOT resolve the main conflict.
            Do NOT end the overall story.

            End this chapter with a strong hook, discovery,
            danger, revelation, or unanswered question.
        """

    max_attempt = 3

    for attempt in range(1, max_attempt + 1):
        try:
            response = client.chat.completions.create(
                model="openrouter/free",
                max_tokens=2000,
                messages=[
                    {
                        "role": "system",
                        "content": """
                            You are a professional horror story writer.

                            Write an immersive horror story.

                            Rules:
                            - Write between 500 and 700 words. Do not exceed 700 words.
                            - Use the story plan as the original direction of the story.
                            - Prioritize the current story memory when it conflicts with the original plan.
                            - Keep character details consistent.
                            - Use the current story memory to maintain continuity.
                            - Do not restart the story when previous memory is provided.
                            - Do not mention the story plan or memory.
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

                            Here is the current story memory:

                            {memory_json}

                            {story_instruction}

                        """,
                    },
                ],
            )

            story = response.choices[0].message.content

            if not story or story.strip().lower().startswith("user safety"):
                raise ValueError("Story generation failed. Please try again.")

            return story

        except Exception as error:

            if attempt < max_attempt:

                wait_seconds = attempt * 2
                print(f"Retrying in {wait_seconds} seconds...")
                time.sleep(wait_seconds)
            else:
                raise RuntimeError("Could not generate the chapter after 3 attempts.")


"""Write the next part of the story.
Maintain continuity with everything that has already happened."""

"""
if memory is not None:
        memory_json = json.dumps(memory, indent=2)
        story_instruction = "Continue the story from where it left off. You may either continue the current storyline or, when it feels natural, conclude it and start a fresh story or chapter from the point where it ended, while maintaining continuity."
    else:
        memory_json = "No previous story memory. This is the beginning of the story."
        story_instruction = "Start the story and end it at an interesting point that allows for future continuity or a new chapter."


"""

"Write the complete story."
