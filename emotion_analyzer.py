import json
from story_schemas import EMOTION_SCHEMA

BATCH_SIZE = 15


def analyze_emotions(gemini_client, narration_script):

    scenes = narration_script.get("scenes", [])

    if not scenes:
        raise ValueError("Narration script contains no scenes.")

    analyzed_scenes = []

    for start in range(0, len(scenes), BATCH_SIZE):

        batch = scenes[start : start + BATCH_SIZE]

        analyzed_batch = analyze_batch(gemini_client, batch, start)

        analyzed_scenes.extend(analyzed_batch)

    return {"scenes": analyzed_scenes}


def analyze_batch(gemini_client, scenes, start_index):

    scenes_text = []

    for index, scene in enumerate(scenes):

        actual_index = start_index + index

        scenes_text.append(f"""
SCENE {actual_index}:

Scene type: {scene["scene_type"]}
Speaker: {scene["speaker"]}
Text: {scene["text"]}
""")

    prompt = f"""
Analyze the emotional state of each scene below.

You MUST return exactly one emotion analysis
for every scene.

There are {len(scenes)} scenes in this batch.

{''.join(scenes_text)}

Rules:

- Do not rewrite the scenes.
- Do not modify the scene text.
- Do not add events.
- Analyze only the emotion expressed or implied.
- Choose one dominant emotion per scene.
- Intensity must be between 0 and 1.
- Choose an appropriate speaking pace.
- Choose an appropriate pause after the scene.
- Preserve the scene order.
- Return one result for every scene.
"""

    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": {"type": "ARRAY", "items": EMOTION_SCHEMA},
        },
    )

    if not response.text:
        raise ValueError(
            f"Emotion Analyzer returned empty response "
            f"for batch starting at scene {start_index}."
        )

    emotions = json.loads(response.text)

    if len(emotions) != len(scenes):
        raise ValueError(
            f"Expected {len(scenes)} emotion results, " f"but received {len(emotions)}."
        )

    analyzed_scenes = []

    for scene, emotion in zip(scenes, emotions):

        required_fields = [
            "emotion",
            "intensity",
            "pace",
            "pause_after",
        ]

        if not all(field in emotion for field in required_fields):
            raise ValueError("Emotion Analyzer returned incomplete scene analysis.")

        if not 0 <= emotion["intensity"] <= 1:
            raise ValueError("Emotion intensity must be between 0 and 1.")

        if not 0 <= emotion["pause_after"] <= 3:
            raise ValueError("pause_after must be between 0 and 3.")

        analyzed_scenes.append({**scene, **emotion})

    return analyzed_scenes
