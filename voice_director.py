import json

from story_schemas import VOICE_DIRECTOR_SCHEMA


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

You will receive multiple analyzed scenes.

Your job is to convert the emotion analysis of EACH scene
into voice performance instructions for a TTS engine.

IMPORTANT:

- Return exactly one voice direction for every scene.
- Preserve the scene_index.
- Do not remove any scene.
- Do not add any scene.
- Do not rewrite the story text.
- Do not modify the emotion.
- Do not change the intensity.
- Do not change the pace.
- Do not invent new emotions.

The Emotion Analyzer is the source of truth.

For each scene choose:

- voice_style
- pitch
- speed
- energy
- breathiness

Rules:

- speed must be between 0.5 and 2.0
- energy must be between 0 and 1
- breathiness must be between 0 and 1
- Match the voice direction to the given emotion and intensity.
- Consider whether the speaker is NARRATOR or a character.
- Keep voice direction consistent with the emotional context.

Scenes:

{json.dumps(scenes_for_analysis, indent=2)}
"""

    response = client.models.generate_content(
        model="gemini-3.7-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": {
                "type": "OBJECT",
                "properties": {
                    "scenes": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "scene_index": {"type": "INTEGER"},
                                "voice_style": {
                                    "type": "STRING",
                                    "enum": [
                                        "neutral",
                                        "warm",
                                        "calm",
                                        "serious",
                                        "dramatic",
                                        "breathy",
                                        "whisper",
                                        "angry",
                                        "excited",
                                    ],
                                },
                                "pitch": {
                                    "type": "STRING",
                                    "enum": [
                                        "low",
                                        "slightly_low",
                                        "normal",
                                        "slightly_high",
                                        "high",
                                    ],
                                },
                                "speed": {
                                    "type": "NUMBER",
                                    "minimum": 0.5,
                                    "maximum": 2.0,
                                },
                                "energy": {
                                    "type": "NUMBER",
                                    "minimum": 0,
                                    "maximum": 1,
                                },
                                "breathiness": {
                                    "type": "NUMBER",
                                    "minimum": 0,
                                    "maximum": 1,
                                },
                            },
                            "required": [
                                "scene_index",
                                "voice_style",
                                "pitch",
                                "speed",
                                "energy",
                                "breathiness",
                            ],
                        },
                    }
                },
                "required": ["scenes"],
            },
        },
    )

    if not response.text:
        raise ValueError("Voice Director returned an empty response.")

    voice_directions = json.loads(response.text)

    returned_scenes = voice_directions.get("scenes", [])

    if len(returned_scenes) != len(scenes):
        raise ValueError("Voice Director returned a different number of scenes.")

    analyzed_script = []

    for scene, direction in zip(scenes, returned_scenes):
        analyzed_script.append(
            {
                **scene,
                **{
                    key: value
                    for key, value in direction.items()
                    if key != "scene_index"
                },
            }
        )

    return {"scenes": analyzed_script}
