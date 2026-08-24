import time
import json

from story_schemas import NARRATOR_SCHEMA
from google.genai import types


def create_narration_script(client, story):
    max_attempts = 3
    wait_times = [15, 30, 60]

    system_instruction = """
    You are a professional story narrator.

    Convert the provided story chapter into a narration script.

    Rules:
    - Preserve the original story events and order.
    - Do not add new characters, events, or dialogue.
    - Split narration and character dialogue into scenes.
    - Use NARRATOR as the speaker for narration.
    - Use the character's name as the speaker for dialogue.
    - Copy story narration and dialogue faithfully.
    - Do not paraphrase any sentence.
    - Do not add descriptions, imagery, emotions, or new details.
    - Every "text" value must come directly from the provided story chapter.
    """

    for attempt in range(1, max_attempts + 1):
        try:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"""
                Convert this story chapter into a narration script:

                {story}
                """,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    max_output_tokens=6000,
                    response_mime_type="application/json",
                    response_schema=NARRATOR_SCHEMA,
                ),
            )

            narration_text = response.text

            if not narration_text:
                raise ValueError("Narrator Agent returned an empty response.")

            narration_script = json.loads(narration_text)

            if not narration_script.get("scenes"):
                raise ValueError("Narrator Agent returned no scenes.")

            return narration_script

        except Exception as e:

            print(
                f"\nNarrator Agent failed " f"(attempt {attempt}/{max_attempts}): {e}"
            )

            if attempt < max_attempts:
                wait_seconds = wait_times[attempt - 1]

                print(f"Retrying in {wait_seconds} seconds...")

                time.sleep(wait_seconds)

            else:
                raise RuntimeError(
                    "Narrator Agent could not create a valid script."
                ) from e


"""
response_format={
                    "type": "json_schema",
                    "json_schema": NARRATOR_SCHEMA,
                },

"""
