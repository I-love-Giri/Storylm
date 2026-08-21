import json
import time
from openai import RateLimitError


def update_memory(client, story, characters, previous_memory: list | None = None):
    characters_json = json.dumps(characters, indent=2)

    if previous_memory is not None:
        previous_memory_json = json.dumps(previous_memory, indent=2)
    else:
        previous_memory_json = "No previous memory. This is the beginning of the story."

    max_attempts = 3

    for attempt in range(1, max_attempts + 1):
        try:
            response = client.chat.completions.create(
                model="openrouter/free",
                max_tokens=2500,
                messages=[
                    {
                        "role": "system",
                        "content": """
                            You are a story continuity manager.

                            Analyze the provided story and update the character memory.

                            For each character, maintain:
                            - name
                            - role
                            - description
                            - current_state
                            - important_events
                            - relationships_changes

                            Important rules:
                            - Preserve existing character information.
                            - Preserve important facts, but keep the memory compact.
                            - Keep only the 8 most relevant important_events for each character.
                            - Remove old minor events when newer events make them less relevant.
                            - Keep current_state under 60 words.
                            - relationships_changes must always be a list with at most 7 relevant changes.
                            - Preserve name, role, and description exactly as they are.
                            - Return exactly one memory object for every original character.
                            - Add new events from the latest story.
                            - Update current_state based on the latest events.
                            - Keep relationships_changes updated.
                            - Do not use markdown.
                            - Do not add explanations.

                            Return only valid JSON.
                        """,
                    },
                    {
                        "role": "user",
                        "content": f"""
                            Here are the existing characters:

                            {characters_json}

                            Here is the previous story memory:

                            {previous_memory_json}

                            Here is the newly generated story:

                            {story}

                            Update the character memory based on what happened
                            in the story.
                        """,
                    },
                ],
            )

            memory_text = response.choices[0].message.content

            if not memory_text:
                raise ValueError("Model returned an empty response.")

            return json.loads(memory_text)

        except RateLimitError as error:
            error_text = str(error)

            # This is a daily quota exhaustion.
            # Retrying will not help.
            if "free-models-per-day" in error_text:
                raise RuntimeError(
                    "free-model daily limit has been exhausted. "
                    "Wait for the daily reset or add credits to your account."
                ) from error

            # A normal/temporary 429 can be retried.
            if attempt < max_attempts:
                wait_seconds = 2**attempt
                print(f"Rate limited. Retrying in {wait_seconds} seconds...")
                time.sleep(wait_seconds)
            else:
                raise RuntimeError("Rate limit persisted after 3 attempts.") from error

        except json.JSONDecodeError as error:
            # The request succeeded, but the model returned invalid JSON.
            if attempt < max_attempts:
                wait_seconds = 2**attempt
                print(
                    f"Model returned invalid JSON. "
                    f"Retrying in {wait_seconds} seconds..."
                )
                time.sleep(wait_seconds)
            else:
                raise RuntimeError("Model repeatedly returned invalid JSON.") from error

        except Exception as error:
            # Other temporary failures can be retried.
            if attempt < max_attempts:
                wait_seconds = 2**attempt
                # print(f"Request failed: {error}")
                print(f"Retrying in {wait_seconds} seconds...")
                time.sleep(wait_seconds)
            else:
                raise RuntimeError(
                    "Could not update the memory after 3 attempts."
                ) from error
