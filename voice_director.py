import json

from story_schemas import VOICE_DIRECTOR_SCHEMA

VOICE_FIELDS = (
    "voice_style",
    "pitch",
    "speed",
    "energy",
    "breathiness",
)


def direct_voices(client, narration_script):
    scenes = narration_script.get("scenes", [])

    if not scenes:
        raise ValueError("Narration script contains no scenes.")

    scenes_for_analysis = []

    for index, scene in enumerate(scenes):
        scenes_for_analysis.append(
            {
                "scene_index": index,
                "scene_type": scene["scene_type"],
                "speaker": scene["speaker"],
                "emotion": scene["emotion"],
                "intensity": scene["intensity"],
                "pace": scene["pace"],
                "pause_after": scene["pause_after"],
            }
        )

    prompt = f"""
You are a Voice Director for an AI audio story.

Your job is to convert the emotion analysis of EACH scene
into voice performance instructions for a TTS engine.

IMPORTANT RULES:

- Return exactly one voice direction for every scene.
- Preserve every scene_index exactly as provided.
- Do not remove or add scenes.
- Do not rewrite the story text.
- Do not modify the emotion, intensity, or pace.
- Do not invent new emotions.
- Match the voice direction to the emotion and intensity.
- Consider whether the speaker is NARRATOR or a character.
- Keep the voice direction consistent with the scene's context.

For each scene, return:

- scene_index
- voice_style
- pitch
- speed
- energy
- breathiness

Numeric constraints:

- speed must be between 0.5 and 2.0
- energy must be between 0 and 1
- breathiness must be between 0 and 1

The Emotion Analyzer is the source of truth.

Scenes:

{json.dumps(scenes_for_analysis, indent=2)}
"""

    response = client.models.generate_content(
        model="gemini-3.7-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": VOICE_DIRECTOR_SCHEMA,
        },
    )

    if not response.text:
        raise ValueError("Voice Director returned an empty response.")

    try:
        voice_directions = json.loads(response.text)
    except json.JSONDecodeError as exc:
        raise ValueError("Voice Director returned invalid JSON.") from exc

    if not isinstance(voice_directions, dict):
        raise ValueError("Voice Director response must be a JSON object.")

    returned_scenes = voice_directions.get("scenes")

    if not isinstance(returned_scenes, list):
        raise ValueError("Voice Director response must contain a scenes list.")

    if len(returned_scenes) != len(scenes):
        raise ValueError(
            f"Expected {len(scenes)} voice directions, "
            f"but received {len(returned_scenes)}."
        )

    directions_by_index = {}

    for direction in returned_scenes:
        if not isinstance(direction, dict):
            raise ValueError("Each voice direction must be a JSON object.")

        scene_index = direction.get("scene_index")

        if type(scene_index) is not int:
            raise ValueError("Every voice direction must have an integer scene_index.")

        if not 0 <= scene_index < len(scenes):
            raise ValueError(f"Invalid scene_index returned: {scene_index}.")

        if scene_index in directions_by_index:
            raise ValueError(f"Duplicate scene_index returned: {scene_index}.")

        directions_by_index[scene_index] = direction

    expected_indexes = set(range(len(scenes)))
    returned_indexes = set(directions_by_index)

    if returned_indexes != expected_indexes:
        missing_indexes = sorted(expected_indexes - returned_indexes)

        raise ValueError(
            f"Voice Director did not return directions for "
            f"all scenes. Missing indexes: {missing_indexes}."
        )

    analyzed_scenes = []

    for index, scene in enumerate(scenes):
        direction = directions_by_index[index]

        missing_fields = [field for field in VOICE_FIELDS if field not in direction]

        if missing_fields:
            raise ValueError(
                f"Voice direction for scene {index} is missing "
                f"fields: {missing_fields}."
            )

        speed = direction["speed"]
        energy = direction["energy"]
        breathiness = direction["breathiness"]

        if (
            isinstance(speed, bool)
            or not isinstance(speed, (int, float))
            or not 0.5 <= speed <= 2.0
        ):
            raise ValueError(f"Invalid speed for scene {index}: {speed}.")

        for field, value in (
            ("energy", energy),
            ("breathiness", breathiness),
        ):
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not 0 <= value <= 1
            ):
                raise ValueError(f"Invalid {field} for scene {index}: {value}.")

        voice_settings = {field: direction[field] for field in VOICE_FIELDS}

        analyzed_scenes.append(
            {
                **scene,
                **voice_settings,
            }
        )

    return {"scenes": analyzed_scenes}
